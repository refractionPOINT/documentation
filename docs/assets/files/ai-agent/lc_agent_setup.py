#!/usr/bin/env python3
"""Helper for https://docs.limacharlie.io/secure-my-agent/

Runs the steps of that setup that handle a secret, so the secret never
passes through the AI agent's chat, a command line or the shell's output
encoding. It only calls the `limacharlie` command-line tool, and never
prints a secret.

  keys           Create the installation key and save its two values in
                 FOLDER/key and FOLDER/json_key, readable by you only.
  imap-password  Ask for a mailbox app password without showing it and
                 store it as a LimaCharlie secret.
  alert-output   Ask for a webhook address or bot token without showing
                 it, put it into an output configuration and create the
                 output.

Add --env NAME before the command to use a named LimaCharlie environment,
for example: python3 lc_agent_setup.py --env agent keys --folder DIR
"""

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys

PLACEHOLDER = "__SECRET__"


def cli(env):
    exe = shutil.which("limacharlie")
    if exe is None:
        sys.exit("The limacharlie command-line tool was not found on PATH. Open a new terminal and try again.")
    return [exe] + (["--env", env] if env else [])


def write_private(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(value)


def first_json_object(text):
    # The tool can print a status line before the JSON.
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in the output")
    return json.loads(text[start:])


def cmd_keys(args):
    os.makedirs(args.folder, mode=0o700, exist_ok=True)
    done = subprocess.run(
        cli(args.env) + ["installation-key", "create", "--description", args.description,
                         "--tags", args.tags, "--get", "--output", "json"],
        capture_output=True)
    if done.returncode != 0:
        sys.exit("Creating the installation key failed:\n" + done.stderr.decode("utf-8", "replace"))
    try:
        key = first_json_object(done.stdout.decode("utf-8"))
        values = (("key", key["key"]), ("json_key", key["json_key"]))
    except (ValueError, KeyError, UnicodeDecodeError) as e:
        sys.exit("The installation key could not be read from the tool's output (%s)." % e)
    for name, value in values:
        write_private(os.path.join(args.folder, name), value)
    print("keys saved")


def ask(prompt):
    value = getpass.getpass(prompt + " (nothing will show as you type or paste), then press Enter: ")
    return value


def cmd_imap_password(args):
    password = ask("Paste the app password")
    if args.gmail:
        password = "".join(password.split())
        if len(password) != 16:
            sys.exit("That is not a 16-letter app password (%d characters). Run this again." % len(password))
    else:
        password = password.strip("\r\n")
    if not password:
        sys.exit("Nothing was entered. Run this again.")
    record = json.dumps({"data": {"secret": json.dumps({"password": password})}})
    done = subprocess.run(cli(args.env) + ["secret", "set", "--key", args.key, "--enabled", "--output", "yaml"],
                          input=record.encode("utf-8"), capture_output=True)
    if done.returncode != 0:
        sys.exit("Saving the password failed:\n" + done.stderr.decode("utf-8", "replace"))
    print("Saved in LimaCharlie as secret %r. You can close this window." % args.key)


def cmd_alert_output(args):
    with open(args.config, encoding="utf-8") as f:
        template = f.read()
    if template.count(PLACEHOLDER) != 1:
        sys.exit("The configuration must contain %s exactly once." % PLACEHOLDER)
    secret = ask("Paste the " + args.what).strip()
    if not secret:
        sys.exit("Nothing was entered. Run this again.")
    # json.dumps gives a double-quoted, escaped string, which YAML reads as is.
    config = template.replace(PLACEHOLDER, json.dumps(secret))
    path = args.config + ".private"
    try:
        write_private(path, config)
        done = subprocess.run(cli(args.env) + ["output", "create", "--name", args.name, "--module", args.module,
                                               "--type", "detect", "--input-file", path, "--output", "yaml"],
                              capture_output=True)
    finally:
        if os.path.exists(path):
            os.remove(path)
    if done.returncode != 0:
        # The error comes from LimaCharlie and does not repeat the secret.
        sys.exit("Creating the alert output failed:\n" + done.stderr.decode("utf-8", "replace"))
    print("Alerts are set up. You can close this window.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", help="named LimaCharlie environment")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("keys")
    p.add_argument("--folder", required=True)
    p.add_argument("--description", default="AI agent computer")
    p.add_argument("--tags", default="ai-agent")
    p.set_defaults(run=cmd_keys)

    p = sub.add_parser("imap-password")
    p.add_argument("--key", required=True, help="secret name, for example agent-imap-1")
    p.add_argument("--gmail", action="store_true", help="remove spaces and expect 16 letters")
    p.set_defaults(run=cmd_imap_password)

    p = sub.add_parser("alert-output")
    p.add_argument("--config", required=True, help="output configuration containing " + PLACEHOLDER)
    p.add_argument("--name", required=True)
    p.add_argument("--module", required=True)
    p.add_argument("--what", default="webhook address", help="what to ask for, for example 'bot token'")
    p.set_defaults(run=cmd_alert_output)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
