#!/usr/bin/env python3
"""Make Chrome and Chromium load the LimaCharlie browser extension.

Run as root by lc-start.sh. Writes a managed policy file that force-installs the
LimaCharlie Sensor extension and gives it the organization's installation key.
The key is read from /workspace/.limacharlie/chrome_key and is never printed.

Prints "ok" when both policy files were already correct, "changed" when one was
written, or an error message (exit code 1).
"""
import json
import os
import sys

LC_HOME = "/workspace/.limacharlie"
KEY_FILE = os.path.join(LC_HOME, "chrome_key")
EXTENSION_ID = "ljdgkaegafdgakkjekimaehhneieecki"
UPDATE_URL = "https://clients2.google.com/service/update2/crx"
POLICY_FILES = (
    "/etc/opt/chrome/policies/managed/limacharlie.json",
    "/etc/chromium/policies/managed/limacharlie.json",
)
MODE = 0o640


def main():
    try:
        with open(KEY_FILE) as f:
            key = f.read().strip()
    except OSError as e:
        print(f"cannot read {KEY_FILE}: {e.strerror}")
        return 1
    if not key:
        print(f"{KEY_FILE} is empty")
        return 1

    # The browser runs as the user who ran sudo, so that user's group must be
    # able to read the policy. The key only lets a browser enroll into this org.
    gid = int(os.environ.get("SUDO_GID", "0"))
    policy = {
        "ExtensionInstallForcelist": [f"{EXTENSION_ID};{UPDATE_URL}"],
        "3rdparty": {"extensions": {EXTENSION_ID: {"installation_key": key}}},
    }

    changed = False
    for path in POLICY_FILES:
        try:
            st = os.stat(path)
            with open(path) as f:
                current = json.load(f)
            if current == policy and st.st_uid == 0 and st.st_gid == gid and st.st_mode & 0o7777 == MODE:
                continue
        except (OSError, ValueError):
            pass

        os.makedirs(os.path.dirname(path), mode=0o755, exist_ok=True)
        tmp = path + ".tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(policy, f)
        os.chown(tmp, 0, gid)
        os.chmod(tmp, MODE)
        os.replace(tmp, path)
        changed = True

    print("changed" if changed else "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
