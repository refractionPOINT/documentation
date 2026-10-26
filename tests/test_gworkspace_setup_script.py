"""Tests for the Google Workspace setup script (docs/assets/files/limacharlie-gworkspace-setup.sh).

The script is a public download that customers run with their own Google Cloud
and LimaCharlie credentials. It creates IAM grants and keys, can temporarily
override organization policies on their project, can delete old service
account keys, and writes LimaCharlie secrets and connections. These tests run
it end to end against stateful stand-ins for gcloud, the limacharlie CLI and
the Google token endpoint (tests/fixtures/gworkspace_setup/), so a change to
any of those paths is checked before it reaches customers.

The paths that change a customer's security settings get the most attention:
an overridden organization policy must always be put back exactly as it was,
and a key or secret a working connection may still use must never be removed.
"""

import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "docs" / "assets" / "files" / "limacharlie-gworkspace-setup.sh"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "gworkspace_setup"
OID = "11111111-2222-3333-4444-555555555555"

class Env:
    def __init__(self, tmp_path):
        self.bin = tmp_path / "bin"
        self.state = tmp_path / "state"
        self.cwd = tmp_path / "run"
        for d in (self.bin, self.state, self.cwd):
            d.mkdir()
        for f in FIXTURES.iterdir():
            dst = self.bin / f.name
            shutil.copy(f, dst)
            dst.chmod(0o755)

    def environ(self, **flags):
        env = {k: v for k, v in os.environ.items() if not k.startswith("LC_")}
        env["PATH"] = f"{self.bin}{os.pathsep}{env['PATH']}"
        env["STUB_STATE"] = str(self.state)
        env.update({k: str(v) for k, v in flags.items()})
        return env

    def run(self, *args, lc=False, **flags):
        """Run the script without a terminal, as in CI or a piped run."""
        argv = ["bash", str(SCRIPT), "--yes", "--project", "demo-proj", *args]
        if lc:
            argv += ["--oid", OID]
            flags.setdefault("LC_API_KEY", "test-key")
        else:
            argv += ["--skip-limacharlie"]
        proc = subprocess.run(
            argv, cwd=self.cwd, env=self.environ(**flags), stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=120,
            start_new_session=True,  # no controlling terminal: never prompts
        )
        proc.output = proc.stdout + proc.stderr
        return proc

    def has(self, name):
        return (self.state / name).exists()

    def read(self, name):
        return (self.state / name).read_text()

    def log(self):
        return self.read("log") if self.has("log") else ""

    def key_ids(self):
        if not self.has("kids"):
            return []
        return [line.split()[0] for line in self.read("kids").splitlines() if line.strip()]

    def policy_calls(self):
        return [line for line in self.log().splitlines() if "org-policies set-policy" in line or "org-policies delete" in line]

    @property
    def key_file(self):
        return self.cwd / "limacharlie-gworkspace-credential.json"


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


ADMIN = ["--admin-email", "admin@example.com"]


# --- Inputs -----------------------------------------------------------------

def test_service_account_admin_is_refused(env):
    proc = env.run("--admin-email", "someone@demo-proj.iam.gserviceaccount.com")
    assert proc.returncode == 1
    assert "is a service account" in proc.output
    assert not env.has("sa"), "nothing may be created with a bad administrator"


def test_admin_is_never_picked_silently_without_a_terminal(env):
    proc = env.run()
    assert proc.returncode == 1
    assert "A Workspace administrator email is required" in proc.output


@pytest.mark.parametrize("value", ["91", "-1", "abc", ""])
def test_backfill_days_is_validated_up_front(env, value):
    proc = env.run(*ADMIN, "--backfill-days", value)
    assert proc.returncode == 1
    assert "0 to 90" in proc.output
    assert not env.has("log")


# --- Google Cloud side ----------------------------------------------------------

def test_google_side_creates_everything_and_writes_the_credential(env):
    proc = env.run(*ADMIN)
    assert proc.returncode == 0, proc.output
    for name in ("sa", "topic", "pub", "sub", "subr"):
        assert env.has(name), name
    cred = json.loads(env.key_file.read_text())
    assert cred["admin_email"] == "admin@example.com"
    assert cred["client_email"] == "limacharlie-mail@demo-proj.iam.gserviceaccount.com"
    assert oct(env.key_file.stat().st_mode & 0o777) == "0o600"
    assert "Client ID 112233445566778899 is already authorized" in proc.output


def test_rerun_reuses_the_saved_key(env):
    assert env.run(*ADMIN).returncode == 0
    proc = env.run(*ADMIN)
    assert proc.returncode == 0, proc.output
    assert "Reusing the key" in proc.output
    assert len(env.key_ids()) == 1


def test_missing_delegation_prints_the_prefilled_link(env):
    proc = env.run(*ADMIN, DWD_FAIL=1)
    assert proc.returncode == 0, proc.output
    assert "admin.google.com/ac/owl/domainwidedelegation?overwriteClientId=true&clientIdToAdd=112233445566778899" in proc.output
    assert "not waiting for authorization" in proc.output


def test_existing_push_subscription_is_refused(env):
    env.run(*ADMIN)
    gcloud = env.bin / "gcloud"
    gcloud.write_text(gcloud.read_text().replace('"pushConfig":{}', '"pushConfig":{"pushEndpoint":"https://x"}'))
    env.key_file.unlink()
    proc = env.run(*ADMIN)
    assert proc.returncode == 1
    assert "push subscription" in proc.output


def test_key_limit_is_reported_before_creating_a_key(env):
    (env.state / "sa").touch()
    (env.state / "kids").write_text("".join(f"old{i} 2026-01-01T00:00:00Z\n" for i in range(10)))
    proc = env.run(*ADMIN)
    assert proc.returncode == 1
    assert "the most Google allows" in proc.output
    assert len(env.key_ids()) == 10


# --- Organization policy exceptions -----------------------------------------------

def test_drs_without_consent_changes_no_policy(env):
    proc = env.run(*ADMIN, LEGACY=1)
    assert proc.returncode == 1
    assert "Domain Restricted Sharing" in proc.output
    assert "--allow-policy-exception" in proc.output
    assert env.policy_calls() == []


def test_drs_exception_is_applied_waited_for_and_removed(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1)
    assert proc.returncode == 0, proc.output
    assert env.has("pub"), "the publisher grant must be made"
    assert env.has("deleted_iam.allowedPolicyMemberDomains"), "a project with no policy of its own goes back to inheriting"
    assert not env.has("exc_iam.allowedPolicyMemberDomains")


def test_legacy_and_managed_drs_are_both_handled_and_restored(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1, MANAGED=1)
    assert proc.returncode == 0, proc.output
    for c in ("iam.allowedPolicyMemberDomains", "iam.managed.allowedPolicyMembers"):
        assert env.has(f"deleted_{c}"), c
        assert not env.has(f"exc_{c}"), c


def test_constraint_name_at_end_of_sentence_is_recognised(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", MANAGED=1, DOTERR=1)
    assert proc.returncode == 0, proc.output
    assert env.has("deleted_iam.managed.allowedPolicyMembers")


def test_projects_own_policy_is_restored_not_deleted(env):
    own = {
        "name": "projects/demo-proj/policies/iam.allowedPolicyMemberDomains",
        "etag": "abc",
        "spec": {"etag": "def", "updateTime": "2026-01-01T00:00:00Z",
                 "rules": [{"values": {"allowedValues": ["is:C0abc"]}}]},
    }
    (env.state / "own_iam.allowedPolicyMemberDomains").write_text(json.dumps(own))
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1)
    assert proc.returncode == 0, proc.output
    assert not env.has("deleted_iam.allowedPolicyMemberDomains")
    restored = json.loads(env.read("restored_iam.allowedPolicyMemberDomains"))
    assert restored == {
        "name": "projects/demo-proj/policies/iam.allowedPolicyMemberDomains",
        "spec": {"rules": [{"values": {"allowedValues": ["is:C0abc"]}}]},
    }


def test_unreadable_policy_means_no_change(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1, DESCFAIL=1)
    assert proc.returncode == 1
    assert "No change was made" in proc.output
    assert env.policy_calls() == []


def test_refused_policy_change_points_to_the_role(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1, NOPOLADMIN=1)
    assert proc.returncode == 1
    assert "roles/orgpolicy.policyAdmin" in proc.output
    assert "Could not restore" not in proc.output


def test_unrelated_precondition_failure_changes_no_policy(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", BAREFP=1)
    assert proc.returncode == 1
    assert env.policy_calls() == []


def test_unsupported_constraint_gets_its_own_help(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", CUSTOM=1)
    assert proc.returncode == 1
    assert "cannot change custom.restrictMembers" in proc.output
    assert env.policy_calls() == []


def test_non_policy_error_while_waiting_stops_and_restores(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", LEGACY=1, TOPICGONE=1)
    assert proc.returncode == 1
    assert "other than the organization policy" in proc.output
    assert env.has("deleted_iam.allowedPolicyMemberDomains")


def test_key_ban_exception_creates_the_key_and_restores(env):
    proc = env.run(*ADMIN, "--allow-policy-exception", NOKEYS=1)
    assert proc.returncode == 0, proc.output
    assert env.key_file.exists()
    assert env.has("deleted_iam.disableServiceAccountKeyCreation")


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
def test_interrupt_while_waiting_restores_the_policy(env, sig):
    (env.state / "prop").write_text("-99999999")  # the exception never takes effect
    argv = ["bash", str(SCRIPT), "--yes", "--project", "demo-proj", "--skip-limacharlie",
            *ADMIN, "--allow-policy-exception"]
    proc = subprocess.Popen(argv, cwd=env.cwd, env=env.environ(LEGACY=1, REAL_SLEEP=1),
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, start_new_session=True)
    try:
        deadline = time.time() + 60
        while not env.has("exc_iam.allowedPolicyMemberDomains"):
            assert time.time() < deadline, "exception was never applied"
            time.sleep(0.1)
        time.sleep(1)
        proc.send_signal(sig)
        out, _ = proc.communicate(timeout=60)
    finally:
        # The script leads its own session; never leave it looping after a failure.
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    assert env.has("deleted_iam.allowedPolicyMemberDomains"), out
    assert not env.has("exc_iam.allowedPolicyMemberDomains")


# --- LimaCharlie side ---------------------------------------------------------------

def test_first_run_stores_secret_creates_connection_and_tests(env):
    proc = env.run(*ADMIN, "--mailboxes", "a@example.com, b@example.com", lc=True)
    assert proc.returncode == 0, proc.output
    secret = json.loads(env.read("secret_in"))
    cred = json.loads(secret["secret"])
    assert cred["admin_email"] == "admin@example.com"
    assert "private_key" in cred
    rec = json.loads(env.read("rec"))
    assert rec == {
        "provider": "gworkspace",
        "credentials": "hive://secret/gws-mail",
        "ingest": {"mode": "push", "backfill_days": 14},
        "features": {
            "outbound_observation": True,
            "pubsub_topic": "projects/demo-proj/topics/mailsec-gmail-push",
            "pubsub_subscription": "projects/demo-proj/subscriptions/mailsec-gmail-push-sub",
        },
        "scope": {"include_addresses": ["a@example.com", "b@example.com"]},
    }
    assert "Connection test passed" in proc.output
    assert not env.key_file.exists(), "the local key is deleted once LimaCharlie holds it"


def test_missing_extension_permission_does_not_warn(env):
    proc = env.run(*ADMIN, lc=True, EXTFAIL=1)
    assert proc.returncode == 0, proc.output
    assert "not enabled" not in proc.output


def test_refused_connection_test_is_not_retried(env):
    proc = env.run(*ADMIN, lc=True, NOEXT=1)
    assert proc.returncode == 1
    assert "Email Security is not enabled" in proc.output
    assert env.read("tests_run").count("x") == 1


def test_rerun_keeps_connection_without_flags_and_offers_nothing_destructive(env):
    assert env.run(*ADMIN, "--mailboxes", "a@example.com", lc=True).returncode == 0
    proc = env.run(*ADMIN, lc=True)
    assert proc.returncode == 0, proc.output
    assert "Keeping the existing connection settings" in proc.output
    assert json.loads(env.read("rec"))["scope"] == {"include_addresses": ["a@example.com"]}
    assert len(env.key_ids()) == 2, "without --delete-old-keys and no terminal, old keys are only listed"


def test_rerun_with_flags_replaces_connection_and_retires_old_keys(env):
    assert env.run(*ADMIN, lc=True).returncode == 0
    proc = env.run(*ADMIN, "--mailboxes", "z@example.com", "--delete-old-keys", lc=True)
    assert proc.returncode == 0, proc.output
    assert json.loads(env.read("rec"))["scope"] == {"include_addresses": ["z@example.com"]}
    assert len(env.key_ids()) == 1
    current = json.loads(json.loads(env.read("secret_in"))["secret"])["private_key_id"]
    assert env.key_ids() == [current], "only the key LimaCharlie now uses may remain"


def test_kept_connection_on_another_secret_is_left_alone(env):
    assert env.run(*ADMIN, lc=True).returncode == 0
    rec = json.loads(env.read("rec"))
    rec["credentials"] = "hive://secret/webapp-cred"
    (env.state / "rec").write_text(json.dumps(rec))
    before = env.read("secret_in")
    proc = env.run(*ADMIN, "--delete-old-keys", lc=True)
    assert proc.returncode == 0, proc.output
    assert env.read("secret_in") == before, "the new key must not be stored where nothing reads it"
    assert len(env.key_ids()) == 2, "no key may be deleted: the connection may use any of them"
    assert env.key_file.exists(), "the unused new key stays tracked for a re-run"


def test_secret_holding_another_service_account_is_not_overwritten(env):
    other = {"secret": json.dumps({"client_email": "other@x.iam.gserviceaccount.com"})}
    (env.state / "secret_in").write_text(json.dumps(other))
    proc = env.run(*ADMIN, lc=True)
    assert proc.returncode == 1
    assert "holds a key for other@x.iam.gserviceaccount.com" in proc.output
    assert json.loads(env.read("secret_in")) == other


def test_unexpected_failure_is_never_silent(env):
    """A failure no check anticipates must still say so (the ERR trap).

    The existing subscription's description is not JSON, which no `|| die`
    guards, so only the trap can explain why the run stopped."""
    (env.state / "sub").touch()
    gcloud = env.bin / "gcloud"
    gcloud.write_text(gcloud.read_text().replace(
        """[ -f "$S/sub" ] || exit 1; echo '{"topic":"projects/demo-proj/topics/mailsec-gmail-push","pushConfig":{}}'""",
        """[ -f "$S/sub" ] || exit 1; echo 'not json'"""))
    proc = env.run(*ADMIN)
    assert proc.returncode != 0
    assert "stopped unexpectedly at line" in proc.output
