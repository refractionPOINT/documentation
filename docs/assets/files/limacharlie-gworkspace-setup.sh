#!/usr/bin/env bash
#
# LimaCharlie Email Security: Google Workspace setup in one run.
#
# Creates everything a Google Workspace connection needs in your Google Cloud
# project, then (optionally) saves the credential and the connection in
# LimaCharlie and runs the connection test:
#
#   1. Enables the Gmail, Admin SDK, Pub/Sub and IAM APIs.
#   2. Creates a service account and a JSON key for it.
#   3. Creates the Pub/Sub topic Gmail publishes to, and lets Gmail publish.
#   4. Creates the pull subscription LimaCharlie reads, and lets the service
#      account read it.
#   5. Prints a pre-filled Google Admin link for domain-wide delegation (the one
#      step Google only allows in the browser), then checks that it worked.
#   6. With a LimaCharlie organization ID and API key: stores the credential as
#      a secret, creates the connection, and runs the connection test.
#
# Safe to re-run: existing resources are reused, and a key saved by an earlier
# run is reused. When a new key is needed, the older keys are offered for
# deletion once LimaCharlie works with the new one.
#
# Easiest place to run it is Google Cloud Shell, which already has gcloud and is
# signed in:
#
#   curl -fsSLO https://docs.limacharlie.io/assets/files/limacharlie-gworkspace-setup.sh
#   bash limacharlie-gworkspace-setup.sh
#
# Run with --help for options.

set -euo pipefail
trap 'printf "\n\033[31mERROR:\033[0m the script stopped unexpectedly at line %s. Please report this with the output above.\n" "$LINENO" >&2' ERR

SCRIPT_NAME="limacharlie-gworkspace-setup.sh"

SCOPE_DIRECTORY="https://www.googleapis.com/auth/admin.directory.user.readonly"
SCOPE_MAIL_MODIFY="https://www.googleapis.com/auth/gmail.modify"
SCOPE_MAIL_FULL="https://mail.google.com/"
GMAIL_PUSH_SA="gmail-api-push@system.gserviceaccount.com"

PROJECT=""
ADMIN_EMAIL=""
SA_NAME="limacharlie-mail"
TOPIC="mailsec-gmail-push"
SUBSCRIPTION="mailsec-gmail-push-sub"
BANNERS=""
KEY_FILE="limacharlie-gworkspace-credential.json"
OID="${LC_OID:-}"
SECRET_NAME="gws-mail"
CONNECTION_NAME="gworkspace"
MAILBOXES=""
MAILBOXES_SET=""
BACKFILL_DAYS="14"
BACKFILL_SET=""
DELETE_OLD_KEYS=""
ALLOW_POLICY_EXCEPTION=""
SKIP_LC=""
ASSUME_YES=""

usage() {
  cat <<EOF
Usage: bash $SCRIPT_NAME [options]

Google Cloud:
  --project ID           Google Cloud project to use (default: gcloud's current project)
  --admin-email EMAIL    Workspace administrator the service account acts as
  --sa-name NAME         Service account name (default: $SA_NAME)
  --topic NAME           Pub/Sub topic (default: $TOPIC)
  --subscription NAME    Pub/Sub pull subscription (default: $SUBSCRIPTION)
  --banners              Also request https://mail.google.com/ (warning banners
                         and reporter replies). Broader access; optional.
  --key-file PATH        Where the credential JSON is written
                         (default: ./$KEY_FILE)
  --allow-policy-exception
                         If an organization policy blocks a step, apply a
                         temporary exception on this project only, then put
                         the policy back. Asked interactively otherwise.
                         Needs the Organization Policy Administrator role.

LimaCharlie (optional; without these the script stops after the Google side
and tells you what to paste into the web app):
  --oid UUID             Organization ID (or set LC_OID)
                         The API key is read from LC_API_KEY, or prompted for.
                         It needs secret.get, secret.set, mailsec_provider.get,
                         mailsec_provider.set and mailsec.act. (secret.get lets
                         it check an existing secret before replacing it.)
  --secret-name NAME     Secret to store the credential in (default: $SECRET_NAME)
  --connection NAME      Connection record name (default: $CONNECTION_NAME)
  --mailboxes LIST       Comma-separated mailboxes to protect. Empty means every
                         mailbox in the domain.
  --backfill-days N      Days of existing mail to scan at setup, 0-90 (default: $BACKFILL_DAYS)
  --skip-limacharlie     Only do the Google side.
  --delete-old-keys      After the connection test passes, delete this service
                         account's other keys without asking. Without a
                         terminal they are otherwise only listed.

Other:
  --yes                  Do not ask questions; use flags and defaults.
  -h, --help             Show this help.
EOF
}

die() { printf '\n\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
step() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
ok() { printf '    \033[32mOK\033[0m %s\n' "$*"; }
info() { printf '    %s\n' "$*"; }
warn() { printf '    \033[33mWARNING:\033[0m %s\n' "$*"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --admin-email) ADMIN_EMAIL="${2:-}"; shift 2 ;;
    --sa-name) SA_NAME="${2:-}"; shift 2 ;;
    --topic) TOPIC="${2:-}"; shift 2 ;;
    --subscription) SUBSCRIPTION="${2:-}"; shift 2 ;;
    --banners) BANNERS=1; shift ;;
    --key-file) KEY_FILE="${2:-}"; shift 2 ;;
    --oid) OID="${2:-}"; shift 2 ;;
    --secret-name) SECRET_NAME="${2:-}"; shift 2 ;;
    --connection) CONNECTION_NAME="${2:-}"; shift 2 ;;
    --mailboxes) MAILBOXES="${2:-}"; MAILBOXES_SET=1; shift 2 ;;
    --backfill-days) BACKFILL_DAYS="${2:-}"; BACKFILL_SET=1; shift 2 ;;
    --delete-old-keys) DELETE_OLD_KEYS=1; shift ;;
    --allow-policy-exception) ALLOW_POLICY_EXCEPTION=1; shift ;;
    --skip-limacharlie) SKIP_LC=1; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage; die "Unknown option: $1" ;;
  esac
done

case "$BACKFILL_DAYS" in
  ''|*[!0-9]*) die "--backfill-days must be a whole number from 0 to 90." ;;
esac
[ "$BACKFILL_DAYS" -le 90 ] || die "--backfill-days must be a whole number from 0 to 90."

# Questions are read from the terminal, so the script also works when piped.
INTERACTIVE=""
if [ -z "$ASSUME_YES" ] && { exec 3</dev/tty; } 2>/dev/null; then
  INTERACTIVE=1
fi

ask() { # ask VAR "Question" [default]
  local __var="$1" __q="$2" __def="${3:-}" __ans=""
  if [ -z "$INTERACTIVE" ]; then
    printf -v "$__var" '%s' "$__def"
    return
  fi
  if [ -n "$__def" ]; then
    printf '%s [%s]: ' "$__q" "$__def" >&2
  else
    printf '%s: ' "$__q" >&2
  fi
  IFS= read -r __ans <&3 || true
  printf -v "$__var" '%s' "${__ans:-$__def}"
}

ask_secret() { # ask_secret VAR "Question"
  local __var="$1" __ans=""
  [ -n "$INTERACTIVE" ] || { printf -v "$__var" '%s' ""; return; }
  printf '%s: ' "$2" >&2
  IFS= read -rs __ans <&3 || true
  printf '\n' >&2
  printf -v "$__var" '%s' "$__ans"
}

confirm() { # confirm "Question" -> 0 for yes. Defaults to yes without a terminal.
  local ans=""
  [ -n "$INTERACTIVE" ] || return 0
  printf '%s [Y/n]: ' "$1" >&2
  IFS= read -r ans <&3 || true
  case "$ans" in [nN]*) return 1 ;; *) return 0 ;; esac
}

PAUSE_ANSWER=""
confirm_no() { # confirm_no "Question" -> 0 only for an explicit yes.
  local ans=""
  [ -n "$INTERACTIVE" ] || return 1
  printf '%s [y/N]: ' "$1" >&2
  IFS= read -r ans <&3 || true
  case "$ans" in [yY]*) return 0 ;; *) return 1 ;; esac
}

pause() {
  PAUSE_ANSWER=""
  [ -n "$INTERACTIVE" ] || return 0
  printf '%s' "$1" >&2
  IFS= read -r PAUSE_ANSWER <&3 || true
}

# ---------------------------------------------------------------------------
step "Checking prerequisites"

for tool in gcloud python3 openssl curl; do
  command -v "$tool" >/dev/null 2>&1 || {
    if [ "$tool" = gcloud ]; then
      die "gcloud is not installed. Run this script in Google Cloud Shell (https://shell.cloud.google.com), or install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install"
    fi
    die "$tool is required but not installed."
  }
done
ok "gcloud, python3, openssl and curl are available"

GCLOUD_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n1 || true)"
[ -n "$GCLOUD_ACCOUNT" ] || die "gcloud is not signed in. Run: gcloud auth login"
ok "Signed in to Google Cloud as $GCLOUD_ACCOUNT"

if [ -z "$PROJECT" ]; then
  PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
  ask PROJECT "Google Cloud project ID to use" "$PROJECT"
fi
[ -n "$PROJECT" ] || die "No project. Pass --project <PROJECT_ID>. List yours with: gcloud projects list"
gcloud projects describe "$PROJECT" --format='value(projectId)' >/dev/null 2>&1 \
  || die "Project '$PROJECT' does not exist or $GCLOUD_ACCOUNT cannot access it. List yours with: gcloud projects list"
ok "Using project $PROJECT"

if [ -z "$ADMIN_EMAIL" ]; then
  admin_default=""
  case "$GCLOUD_ACCOUNT" in
    *.gserviceaccount.com|*@gmail.com|*@googlemail.com) ;;
    *@*) admin_default="$GCLOUD_ACCOUNT" ;;
  esac
  info "Enter a Workspace user with admin rights (a person's account like admin@yourdomain.com,"
  info "not a service account). LimaCharlie acts as this user to list your domain's mailboxes."
  ask ADMIN_EMAIL "Workspace administrator email" "$admin_default"
fi
case "$ADMIN_EMAIL" in
  *.gserviceaccount.com)
    die "$ADMIN_EMAIL is a service account. The administrator must be a Workspace user with admin rights, such as admin@yourdomain.com (often the account you sign in to admin.google.com with)." ;;
  *@*.*) ;;
  *) die "A Workspace administrator email is required (--admin-email admin@yourdomain.com)." ;;
esac
ok "Workspace administrator: $ADMIN_EMAIL"

if [ -z "$BANNERS" ] && [ -n "$INTERACTIVE" ]; then
  if ! confirm "Leave out the optional https://mail.google.com/ scope (no warning banners or reporter replies)?"; then
    BANNERS=1
  fi
fi

SA_EMAIL="$SA_NAME@$PROJECT.iam.gserviceaccount.com"
TOPIC_PATH="projects/$PROJECT/topics/$TOPIC"
SUB_PATH="projects/$PROJECT/subscriptions/$SUBSCRIPTION"
SCOPES="$SCOPE_DIRECTORY,$SCOPE_MAIL_MODIFY"
[ -n "$BANNERS" ] && SCOPES="$SCOPES,$SCOPE_MAIL_FULL"

WORKDIR="$(mktemp -d)"

# ---------------------------------------------------------------------------
# Temporary organization-policy exceptions.
#
# Some organizations block a step with a policy, most often Domain Restricted
# Sharing (Gmail's publisher account is outside the organization) or a ban on
# service account keys. Both only gate the moment a grant or key is CREATED:
# once it exists it keeps working after the policy is restored. So the script
# can override the policy on this project only, do the one step, and put back
# exactly what was there before (the project's own policy, or inheritance).

POLICY_ACTIVE=""   # constraints currently overridden by this script (space separated)

constraint_from_error() { # prints the constraint named in a gcloud error, if any
  printf '%s' "$1" | grep -oE 'constraints/[A-Za-z0-9_.]+' | head -n1 | sed 's#^constraints/##' || true
}

policy_console_url() {
  printf 'https://console.cloud.google.com/iam-admin/orgpolicies/%s?project=%s' "$1" "$PROJECT"
}

policy_manual_help() { # constraint -> how an administrator does it by hand
  local action="Enforcement Off"
  [ "$1" = iam.allowedPolicyMemberDomains ] && action="Allow All"
  cat <<EOF
       To fix it, someone with the Organization Policy Administrator role can either:
         - re-run this script with --allow-policy-exception (it applies the exception
           on this project only and restores the policy right after), or
         - open $(policy_console_url "$1")
           choose Manage policy > Override parent's policy > Add a rule > $action,
           save, wait a few minutes, re-run this script, then set the policy back to
           "Inherit parent's policy" (or its previous setting).
EOF
}

# Puts back every policy this script overrode: the project's own previous
# policy when it had one, otherwise inheritance from the parent.
restore_policy_exception() {
  local c saved restored
  for c in $POLICY_ACTIVE; do
    saved="$WORKDIR/previous-$c.json"
    restored=""
    if [ -s "$saved" ]; then
      python3 -c '
import json, sys
def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in ("etag", "updateTime")}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o
json.dump(strip(json.load(open(sys.argv[1]))), open(sys.argv[2], "w"))
' "$saved" "$WORKDIR/restore-$c.json" \
        && gcloud org-policies set-policy "$WORKDIR/restore-$c.json" --quiet >/dev/null 2>&1 && restored=1
    else
      gcloud org-policies delete "$c" --project="$PROJECT" --quiet >/dev/null 2>&1 && restored=1
    fi
    if [ -n "$restored" ]; then
      ok "Restored the $c policy on $PROJECT"
    elif [ -s "$saved" ]; then
      cp "$saved" "./$c-previous-policy.json" 2>/dev/null || true
      warn "Could not restore the $c policy on $PROJECT. Its previous setting is in ./$c-previous-policy.json;"
      info "put it back with: gcloud org-policies set-policy ./$c-previous-policy.json"
    else
      warn "Could not restore the $c policy on $PROJECT. Put it back with:"
      info "  gcloud org-policies delete $c --project=$PROJECT"
    fi
  done
  POLICY_ACTIVE=""
}

# offer_policy_exception CONSTRAINT "what it unblocks" -> 0 when the exception is in place.
offer_policy_exception() {
  local c="$1" why="$2" rule spec saved out
  case " $POLICY_ACTIVE " in *" $c "*) return 0 ;; esac
  case "$c" in
    iam.allowedPolicyMemberDomains) rule="  - allowAll: true" ;;
    iam.managed.allowedPolicyMembers|iam.disableServiceAccountKeyCreation|iam.managed.disableServiceAccountKeyCreation)
      rule="  - enforce: false" ;;
    *) return 1 ;;
  esac
  cat <<EOF

    The organization policy $c blocks this step.
    The script can override it on project $PROJECT only, $why, and then
    restore the policy exactly as it was. What it creates keeps working after
    the policy is restored. The rest of your organization is not affected.
EOF
  if [ -z "$ALLOW_POLICY_EXCEPTION" ] && ! confirm_no "    Apply this temporary exception now?"; then
    return 1
  fi
  saved="$WORKDIR/previous-$c.json"
  gcloud org-policies describe "$c" --project="$PROJECT" --format=json >"$saved" 2>/dev/null || : >"$saved"
  spec="$WORKDIR/exception-$c.yaml"
  printf 'name: projects/%s/policies/%s\nspec:\n  rules:\n%s\n' "$PROJECT" "$c" "$rule" >"$spec"
  if ! out="$(gcloud org-policies set-policy "$spec" --quiet 2>&1)"; then
    printf '%s\n' "$out" >&2
    warn "Could not change the policy. $GCLOUD_ACCOUNT needs the Organization Policy Administrator role (roles/orgpolicy.policyAdmin) on the organization."
    return 1
  fi
  POLICY_ACTIVE="$POLICY_ACTIVE $c"
  ok "Temporary exception for $c applied to $PROJECT"
}

# retry_until_policy_applies "description" "why" cmd... : policy changes take up
# to 15 minutes to reach every Google service, so retry the blocked step until
# then. If a second policy turns out to block it too, offer an exception for it.
retry_until_policy_applies() {
  local what="$1" why="$2" start=$SECONDS out c last_min=0 min
  shift 2
  info "Waiting for the exception to take effect (usually a minute or two, up to 15)..."
  while :; do
    if out="$("$@" 2>&1)"; then
      return 0
    fi
    c="$(constraint_from_error "$out")"
    if [ -n "$c" ]; then
      case " $POLICY_ACTIVE " in
        *" $c "*) ;;
        *) offer_policy_exception "$c" "$why" || { printf '%s\n' "$out" >&2; return 1; } ;;
      esac
    fi
    if [ $((SECONDS - start)) -ge 900 ]; then
      printf '%s\n' "$out" >&2
      warn "$what still fails after 15 minutes."
      return 1
    fi
    sleep 20
    min=$(( (SECONDS - start) / 60 ))
    if [ "$min" -gt "$last_min" ]; then
      info "  still waiting ($min min)..."
      last_min=$min
    fi
  done
}

cleanup() { restore_policy_exception; rm -rf "$WORKDIR"; }
trap cleanup EXIT
trap 'exit 130' INT TERM

# Runs gcloud, retrying a few times: new service accounts and APIs take a
# moment to become visible to the rest of Google Cloud.
gcloud_retry() {
  local attempt=1 out
  while :; do
    if out="$(gcloud "$@" --quiet 2>&1)"; then
      printf '%s' "$out"
      return 0
    fi
    if [ "$attempt" -ge 6 ]; then
      printf '%s' "$out" >&2
      return 1
    fi
    sleep $((attempt * 5))
    attempt=$((attempt + 1))
  done
}

# Prints "yes" when MEMBER holds ROLE in the IAM policy JSON on stdin.
policy_has() {
  python3 -c '
import json, sys
member, role = sys.argv[1], sys.argv[2]
policy = json.load(sys.stdin)
found = any(b.get("role") == role and member in b.get("members", []) for b in policy.get("bindings", []))
print("yes" if found else "no")
' "$1" "$2"
}

# ---------------------------------------------------------------------------
step "Enabling the Gmail, Admin SDK, Pub/Sub and IAM APIs"
gcloud_retry services enable gmail.googleapis.com admin.googleapis.com \
  pubsub.googleapis.com iam.googleapis.com --project="$PROJECT" >/dev/null \
  || die "Could not enable the APIs. $GCLOUD_ACCOUNT needs permission to enable services (for example the Owner or Service Usage Admin role) on $PROJECT."
ok "APIs enabled"

# ---------------------------------------------------------------------------
step "Service account $SA_EMAIL"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT" >/dev/null 2>&1; then
  ok "Already exists"
else
  gcloud_retry iam service-accounts create "$SA_NAME" --project="$PROJECT" \
    --display-name="LimaCharlie Email Security" >/dev/null \
    || die "Could not create the service account. $GCLOUD_ACCOUNT needs the Service Account Admin role (or Owner) on $PROJECT."
  ok "Created"
fi

# ---------------------------------------------------------------------------
step "Pub/Sub topic $TOPIC"
if gcloud pubsub topics describe "$TOPIC" --project="$PROJECT" >/dev/null 2>&1; then
  ok "Already exists"
else
  gcloud_retry pubsub topics create "$TOPIC" --project="$PROJECT" >/dev/null \
    || die "Could not create the topic. $GCLOUD_ACCOUNT needs the Pub/Sub Admin role (or Owner) on $PROJECT."
  ok "Created"
fi

step "Letting Gmail publish to the topic"
policy="$(gcloud pubsub topics get-iam-policy "$TOPIC" --project="$PROJECT" --format=json)" \
  || die "Could not read the topic's permissions. $GCLOUD_ACCOUNT needs the Pub/Sub Admin role (or Owner) on $PROJECT."
if [ "$(printf '%s' "$policy" | policy_has "serviceAccount:$GMAIL_PUSH_SA" roles/pubsub.publisher)" = yes ]; then
  ok "$GMAIL_PUSH_SA already has Pub/Sub Publisher on the topic"
else
  if ! out="$(gcloud pubsub topics add-iam-policy-binding "$TOPIC" --project="$PROJECT" \
      --member="serviceAccount:$GMAIL_PUSH_SA" --role=roles/pubsub.publisher --quiet 2>&1)"; then
    printf '%s\n' "$out" >&2
    case "$out" in
      *allowedPolicyMember*|*FAILED_PRECONDITION*|*"not in permitted organization"*|*"does not belong to a permitted customer"*)
        c="$(constraint_from_error "$out")"
        c="${c:-iam.allowedPolicyMemberDomains}"
        if offer_policy_exception "$c" "grant Gmail's publisher account ($GMAIL_PUSH_SA) access to the topic" \
           && retry_until_policy_applies "Granting $GMAIL_PUSH_SA" \
                "grant Gmail's publisher account ($GMAIL_PUSH_SA) access to the topic" \
                gcloud pubsub topics add-iam-policy-binding "$TOPIC" --project="$PROJECT" \
                --member="serviceAccount:$GMAIL_PUSH_SA" --role=roles/pubsub.publisher --quiet; then
          restore_policy_exception
        else
          restore_policy_exception
          die "The organization policy $c (Domain Restricted Sharing) blocks granting $GMAIL_PUSH_SA access to the topic.
       This Google-owned account is how Gmail delivers new-mail notifications, and Google Workspace has no polling alternative.
$(policy_manual_help "$c")
       Details: https://developers.google.com/workspace/gmail/api/guides/push"
        fi ;;
      *) die "Could not grant $GMAIL_PUSH_SA the Pub/Sub Publisher role on the topic." ;;
    esac
  fi
  policy="$(gcloud pubsub topics get-iam-policy "$TOPIC" --project="$PROJECT" --format=json)" \
  || die "Could not read the topic's permissions. $GCLOUD_ACCOUNT needs the Pub/Sub Admin role (or Owner) on $PROJECT."
  [ "$(printf '%s' "$policy" | policy_has "serviceAccount:$GMAIL_PUSH_SA" roles/pubsub.publisher)" = yes ] \
    || die "The publisher grant did not appear on the topic. Check the topic's permissions in the Google Cloud console."
  ok "Granted $GMAIL_PUSH_SA the Pub/Sub Publisher role on the topic"
fi

# ---------------------------------------------------------------------------
step "Pub/Sub pull subscription $SUBSCRIPTION"
if sub_json="$(gcloud pubsub subscriptions describe "$SUBSCRIPTION" --project="$PROJECT" --format=json 2>/dev/null)"; then
  problem="$(printf '%s' "$sub_json" | python3 -c '
import json, sys
s = json.load(sys.stdin)
if s.get("topic") != sys.argv[1]:
    print("it is attached to %s, not %s" % (s.get("topic"), sys.argv[1]))
elif (s.get("pushConfig") or {}).get("pushEndpoint"):
    print("it is a push subscription; LimaCharlie needs a pull subscription")
' "$TOPIC_PATH")"
  [ -z "$problem" ] || die "Subscription $SUBSCRIPTION already exists but $problem. Delete it or pass --subscription with another name."
  ok "Already exists"
else
  gcloud_retry pubsub subscriptions create "$SUBSCRIPTION" --topic="$TOPIC" \
    --project="$PROJECT" --ack-deadline=60 >/dev/null \
    || die "Could not create the subscription."
  ok "Created"
fi

step "Letting the service account read the subscription"
policy="$(gcloud pubsub subscriptions get-iam-policy "$SUBSCRIPTION" --project="$PROJECT" --format=json)" \
  || die "Could not read the subscription's permissions. $GCLOUD_ACCOUNT needs the Pub/Sub Admin role (or Owner) on $PROJECT."
if [ "$(printf '%s' "$policy" | policy_has "serviceAccount:$SA_EMAIL" roles/pubsub.subscriber)" = yes ]; then
  ok "Already granted"
else
  gcloud_retry pubsub subscriptions add-iam-policy-binding "$SUBSCRIPTION" --project="$PROJECT" \
    --member="serviceAccount:$SA_EMAIL" --role=roles/pubsub.subscriber >/dev/null \
    || die "Could not grant the service account the Pub/Sub Subscriber role on the subscription."
  ok "Granted $SA_EMAIL the Pub/Sub Subscriber role on the subscription"
fi

# ---------------------------------------------------------------------------
step "Service account key"

# Reuse a key saved by an earlier run when it still exists, so re-running does
# not pile up keys (Google allows 10 per service account).
reuse=""
if [ -f "$KEY_FILE" ]; then
  existing="$(python3 -c '
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get("client_email", ""), d.get("private_key_id", ""))
except Exception:
    print("")
' "$KEY_FILE")"
  existing_email="${existing%% *}"
  existing_kid="${existing#* }"
  if [ "$existing_email" = "$SA_EMAIL" ] && [ -n "$existing_kid" ] && \
     gcloud iam service-accounts keys list --iam-account="$SA_EMAIL" --project="$PROJECT" \
       --managed-by=user --format='value(name.basename())' 2>/dev/null | grep -qx "$existing_kid"; then
    reuse=1
  else
    die "$KEY_FILE exists but does not hold a current key for $SA_EMAIL. Move it away or pass --key-file with another path."
  fi
fi

if [ -n "$reuse" ]; then
  ok "Reusing the key saved in $KEY_FILE"
else
  key_count="$(gcloud iam service-accounts keys list --iam-account="$SA_EMAIL" --project="$PROJECT" \
    --managed-by=user --format='value(name.basename())' 2>/dev/null | grep -c . || true)"
  if [ "${key_count:-0}" -ge 10 ]; then
    die "$SA_EMAIL already has $key_count keys, the most Google allows. Delete the ones nothing uses:
       gcloud iam service-accounts keys list --iam-account=$SA_EMAIL --project=$PROJECT --managed-by=user
       gcloud iam service-accounts keys delete <KEY_ID> --iam-account=$SA_EMAIL --project=$PROJECT
       Keep the key LimaCharlie uses (its private_key_id), then run this script again."
  fi
  if [ "${key_count:-0}" -gt 0 ]; then
    info "This service account already has $key_count key(s). A new one is created; the script offers to delete the old ones once LimaCharlie uses the new one."
  fi
  RAW_KEY="$WORKDIR/raw-key.json"
  if ! out="$(gcloud iam service-accounts keys create "$RAW_KEY" --iam-account="$SA_EMAIL" \
      --project="$PROJECT" --quiet 2>&1)"; then
    printf '%s\n' "$out" >&2
    case "$out" in
      *disableServiceAccountKeyCreation*)
        c="$(constraint_from_error "$out")"
        c="${c:-iam.disableServiceAccountKeyCreation}"
        if offer_policy_exception "$c" "create the one key LimaCharlie needs" \
           && retry_until_policy_applies "Creating the key" "create the one key LimaCharlie needs" \
                gcloud iam service-accounts keys create "$RAW_KEY" --iam-account="$SA_EMAIL" \
                --project="$PROJECT" --quiet; then
          restore_policy_exception
        else
          restore_policy_exception
          die "The organization policy $c blocks creating service account keys in $PROJECT.
       LimaCharlie needs a key to call the Gmail API on your behalf.
$(policy_manual_help "$c")"
        fi ;;
      *[Mm]aximum*|*"limit"*)
        die "Google refused another key for $SA_EMAIL: it has reached its key limit. Delete unused keys (gcloud iam service-accounts keys list --iam-account=$SA_EMAIL --managed-by=user), then run this script again." ;;
      *) die "Could not create a key. $GCLOUD_ACCOUNT needs the Service Account Key Admin role (or Owner) on $PROJECT." ;;
    esac
  fi
  (
    umask 077
    python3 -c '
import json, sys
key = json.load(open(sys.argv[1]))
cred = {"admin_email": sys.argv[2]}
cred.update(key)
json.dump(cred, open(sys.argv[3], "w"), indent=2)
' "$RAW_KEY" "$ADMIN_EMAIL" "$KEY_FILE"
  )
  rm -f "$RAW_KEY"
  ok "Created a key and wrote the credential (key + admin_email) to $KEY_FILE"
fi

# Keep admin_email in step with this run's answer.
python3 -c '
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["admin_email"] = sys.argv[2]
json.dump(d, open(p, "w"), indent=2)
' "$KEY_FILE" "$ADMIN_EMAIL"
chmod 600 "$KEY_FILE"

CLIENT_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["client_id"])' "$KEY_FILE")"
CURRENT_KID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["private_key_id"])' "$KEY_FILE")"

# The service account's user-managed keys other than the one in $KEY_FILE, as
# "KEY_ID CREATED" lines.
other_keys() {
  gcloud iam service-accounts keys list --iam-account="$SA_EMAIL" --project="$PROJECT" \
    --managed-by=user --format='value(name.basename(),validAfterTime)' 2>/dev/null \
    | awk -v cur="$CURRENT_KID" '$1 != cur' || true
}

# Old keys still carry the same domain-wide access, so once LimaCharlie uses
# the new key, offer to delete them.
retire_old_keys() {
  local old kid
  old="$(other_keys)"
  [ -n "$old" ] || return 0
  step "Older keys on $SA_EMAIL"
  info "LimaCharlie now uses key $CURRENT_KID. These older keys are still valid and carry the same access:"
  printf '%s\n' "$old" | awk '{print "      " $1 "  (created " $2 ")"}'
  if [ -n "$DELETE_OLD_KEYS" ] || confirm_no "    Delete them? Answer no if anything else uses this service account."; then
    for kid in $(printf '%s\n' "$old" | awk '{print $1}'); do
      if gcloud iam service-accounts keys delete "$kid" --iam-account="$SA_EMAIL" \
          --project="$PROJECT" --quiet >/dev/null 2>&1; then
        ok "Deleted key $kid"
      else
        warn "Could not delete key $kid"
      fi
    done
  else
    info "To delete one later: gcloud iam service-accounts keys delete <KEY_ID> --iam-account=$SA_EMAIL --project=$PROJECT"
  fi
}

# ---------------------------------------------------------------------------
# Domain-wide delegation check: ask Google for a token that acts as the admin
# with the given scope. Google refuses it until the Workspace admin has
# authorized the client ID for that scope.

b64url() { openssl base64 -e -A | tr '+/' '-_' | tr -d '='; }

# Prints "ok", or Google's error.
dwd_check() {
  local scope="$1" pem="$WORKDIR/key.pem" now header claims unsigned sig resp
  python3 -c 'import json,sys; sys.stdout.write(json.load(open(sys.argv[1]))["private_key"])' "$KEY_FILE" > "$pem"
  chmod 600 "$pem"
  now="$(date +%s)"
  header="$(printf '%s' '{"alg":"RS256","typ":"JWT"}' | b64url)"
  claims="$(python3 -c '
import json, sys
print(json.dumps({"iss": sys.argv[1], "sub": sys.argv[2], "scope": sys.argv[3],
                  "aud": "https://oauth2.googleapis.com/token",
                  "iat": int(sys.argv[4]), "exp": int(sys.argv[4]) + 600}, separators=(",", ":")), end="")
' "$SA_EMAIL" "$ADMIN_EMAIL" "$scope" "$now" | b64url)"
  unsigned="$header.$claims"
  sig="$(printf '%s' "$unsigned" | openssl dgst -sha256 -sign "$pem" | b64url)"
  rm -f "$pem"
  resp="$(curl -sS --max-time 30 https://oauth2.googleapis.com/token \
    --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
    --data-urlencode "assertion=$unsigned.$sig" 2>&1 || true)"
  printf '%s' "$resp" | python3 -c '
import json, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    print("unexpected response: " + raw[:300]); sys.exit()
if d.get("access_token"):
    print("ok")
else:
    print("%s: %s" % (d.get("error", "error"), d.get("error_description", "")))
'
}

# Prints the scopes that are not yet authorized, one per line.
missing_scopes() {
  local s res
  for s in ${SCOPES//,/ }; do
    res="$(dwd_check "$s")"
    if [ "$res" != ok ]; then
      printf '%s\t%s\n' "$s" "$res"
    fi
  done
}

urlencode() { python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"; }
DWD_URL="https://admin.google.com/ac/owl/domainwidedelegation?overwriteClientId=true&clientIdToAdd=$CLIENT_ID&clientScopeToAdd=$(urlencode "$SCOPES")"

step "Domain-wide delegation (Google Admin console)"
missing="$(missing_scopes)"
if [ -z "$missing" ]; then
  ok "Client ID $CLIENT_ID is already authorized for: $SCOPES"
else
  cat <<EOF

    This is the one step Google only allows in the browser. A Workspace
    Super Admin must open this link, check the values, and click Authorize:

    $DWD_URL

    It pre-fills:
      Client ID:    $CLIENT_ID
      OAuth scopes: $SCOPES

    (Manual path: admin.google.com > Security > Access and data control >
     API controls > Manage Domain Wide Delegation > Add new.)
EOF
  if [ -z "$INTERACTIVE" ]; then
    warn "Running without a terminal: not waiting for authorization. Authorize with the link above."
  else
    while :; do
      pause $'\n    Press Enter once you clicked Authorize (or type s then Enter to skip the check): '
      if [ "$PAUSE_ANSWER" = s ]; then break; fi
      info "Checking (Google can take a few minutes to apply it)..."
      for _try in 1 2 3 4 5 6 7 8 9 10 11 12; do
        missing="$(missing_scopes)"
        [ -z "$missing" ] && break
        sleep 10
      done
      if [ -z "$missing" ]; then
        ok "Domain-wide delegation works for: $SCOPES"
        break
      fi
      warn "Still not authorized:"
      printf '%s\n' "$missing" | sed 's/^/      /'
      case "$missing" in
        *"invalid_grant"*)
          info "invalid_grant usually means $ADMIN_EMAIL is not a valid Workspace user in this domain." ;;
        *)
          info "Check that the entry uses client ID $CLIENT_ID and lists every scope above."
          info "Changes usually apply within minutes but Google allows up to 24 hours." ;;
      esac
      if ! confirm "    Check again?"; then break; fi
    done
  fi
fi

# ---------------------------------------------------------------------------
lc_manual_instructions() {
  cat <<EOF

    Finish in the LimaCharlie web app:
      1. Email Security > Settings > Add connection > Google Workspace.
      2. Credential > Add New, name it $SECRET_NAME, and paste the whole content of:
           $KEY_FILE
         (In Cloud Shell, run: cloudshell download $KEY_FILE)
      3. Topic: $TOPIC   Subscription: $SUBSCRIPTION
      4. Save, then run the connection test with "Verify notification delivery".
    Delete $KEY_FILE once the connection test passes.
EOF
  local old
  old="$(other_keys)"
  if [ -n "$old" ]; then
    cat <<EOF

    $SA_EMAIL also has older keys that are still valid. Once the connection
    test passes with the new key ($CURRENT_KID), delete them unless something
    else uses them:
EOF
    printf '%s\n' "$old" | awk -v sa="$SA_EMAIL" -v p="$PROJECT" '{print "      gcloud iam service-accounts keys delete " $1 " --iam-account=" sa " --project=" p "   # created " $2}'
  fi
}

if [ -n "$SKIP_LC" ]; then
  step "Done with Google Cloud"
  lc_manual_instructions
  exit 0
fi

step "LimaCharlie"
if [ -z "$OID" ]; then
  info "To finish in LimaCharlie from here, enter your organization ID (the UUID shown in the"
  info "web app under Organization Settings > Access Management > REST API)."
  info "Press Enter to skip and finish in the web app instead."
  ask OID "LimaCharlie organization ID" ""
fi
if [ -z "$OID" ]; then
  lc_manual_instructions
  exit 0
fi

LC_API_KEY="${LC_API_KEY:-}"
if [ -z "$LC_API_KEY" ]; then
  info "An organization API key is needed (Organization Settings > Access Management > REST API)"
  info "with secret.get, secret.set, mailsec_provider.get, mailsec_provider.set and mailsec.act."
  info "(secret.get lets the script check an existing secret before replacing it.)"
  ask_secret LC_API_KEY "LimaCharlie API key (input hidden)"
fi
[ -n "$LC_API_KEY" ] || { warn "No API key given."; lc_manual_instructions; exit 0; }
export LC_OID="$OID" LC_API_KEY

# Find or install the LimaCharlie CLI.
LC=()
if command -v limacharlie >/dev/null 2>&1; then
  LC=(limacharlie)
else
  info "Installing the LimaCharlie CLI into a temporary environment..."
  if python3 -m venv "$WORKDIR/venv" >/dev/null 2>&1 && \
     "$WORKDIR/venv/bin/pip" install --quiet --disable-pip-version-check limacharlie >/dev/null 2>&1; then
    LC=("$WORKDIR/venv/bin/limacharlie")
  elif python3 -m pip install --user --quiet --disable-pip-version-check limacharlie >/dev/null 2>&1; then
    LC=(python3 -m limacharlie)
  else
    warn "Could not install the LimaCharlie CLI (pip install limacharlie)."
    lc_manual_instructions
    exit 0
  fi
fi
"${LC[@]}" auth whoami --oid "$OID" >/dev/null 2>&1 \
  || die "LimaCharlie rejected the organization ID / API key pair. Check both and run the script again (everything done so far is reused)."
ok "Authenticated to LimaCharlie organization $OID"

# Listing extensions needs ext.conf.get, which the documented key may lack;
# only warn when the list was readable. The connection test catches it anyway.
if ext_list="$("${LC[@]}" extension list --oid "$OID" --output json 2>/dev/null)" && \
   ! printf '%s' "$ext_list" | grep -q '"ext-email-security"'; then
  warn "Email Security is not enabled in this organization."
  info "Subscribe to it first (Email Security in the web app, or: limacharlie extension subscribe --name ext-email-security --oid $OID)."
  confirm "    Continue anyway?" || exit 1
fi

step "Connection $CONNECTION_NAME"
write_record=1
if "${LC[@]}" hive get --hive-name mailsec_provider --key "$CONNECTION_NAME" --oid "$OID" >/dev/null 2>&1; then
  if [ -n "$INTERACTIVE" ]; then
    confirm "    Connection $CONNECTION_NAME already exists. Replace its settings?" || write_record=""
  elif [ -z "$MAILBOXES_SET" ] && [ -z "$BACKFILL_SET" ]; then
    # Without a terminal, only replace it when the settings were passed explicitly.
    write_record=""
  fi
  if [ -z "$write_record" ]; then
    ok "Keeping the existing connection settings (pass --mailboxes or --backfill-days to replace them)"
  fi
fi

# A kept connection may read another secret. Then the new credential is not
# stored at all, nothing is retired, and the test checks the connection as is.
uses_our_secret=1
if [ -z "$write_record" ]; then
  kept_cred="$("${LC[@]}" hive get --hive-name mailsec_provider --key "$CONNECTION_NAME" \
    --oid "$OID" --output json 2>/dev/null | python3 -c '
import json, sys
def find(o):
    if isinstance(o, dict):
        if isinstance(o.get("credentials"), str):
            return o["credentials"]
        for v in o.values():
            r = find(v)
            if r:
                return r
    return ""
try:
    print(find(json.load(sys.stdin)))
except Exception:
    print("")
' || true)"
  if [ "$kept_cred" != "hive://secret/$SECRET_NAME" ]; then
    uses_our_secret=""
    warn "Connection $CONNECTION_NAME reads '${kept_cred:-an unknown credential}', not hive://secret/$SECRET_NAME."
    info "The new credential is not stored, and the test below checks the connection's own credential."
    info "To switch the connection to the new key, re-run and replace its settings."
  fi
fi

if [ -n "$uses_our_secret" ]; then
  step "Storing the credential as secret $SECRET_NAME"
  # Do not silently replace a secret that holds another service account's key:
  # a working connection may depend on it. Reading it needs secret.get; when
  # the key cannot be read, the secret is replaced as before.
  prior_email="$("${LC[@]}" secret get --key "$SECRET_NAME" --oid "$OID" --output json 2>/dev/null | python3 -c '
import json, sys
def find(o):
    if isinstance(o, dict):
        v = o.get("secret")
        if isinstance(v, str):
            return v
        for x in o.values():
            r = find(x)
            if r:
                return r
    return ""
try:
    print(json.loads(find(json.load(sys.stdin))).get("client_email", ""))
except Exception:
    print("")
' || true)"
  if [ -n "$prior_email" ] && [ "$prior_email" != "$SA_EMAIL" ]; then
    if ! confirm_no "    Secret $SECRET_NAME holds a key for $prior_email, not $SA_EMAIL. Replace it?"; then
      die "Secret $SECRET_NAME was left unchanged because it holds a key for $prior_email.
       Pass --secret-name <another name> (and --connection <another name>) to set up this service account separately,
       or run the script in a terminal to confirm the replacement."
    fi
  fi
  python3 -c 'import json,sys; print(json.dumps({"secret": open(sys.argv[1]).read()}))' "$KEY_FILE" \
    | "${LC[@]}" secret set --key "$SECRET_NAME" --enabled --oid "$OID" >/dev/null \
    || die "Could not store the secret. The API key needs secret.set."
  ok "Stored"
fi

if [ -n "$write_record" ]; then
  if [ -z "$MAILBOXES_SET" ] && [ -n "$INTERACTIVE" ]; then
    info "Which mailboxes should be protected? Billing is per protected mailbox."
    ask MAILBOXES "Comma-separated addresses for a pilot, or Enter for every mailbox" ""
  fi
  RECORD="$WORKDIR/connection.json"
  python3 -c '
import json, sys
secret, topic, sub, mailboxes, backfill, out = sys.argv[1:7]
rec = {
    "provider": "gworkspace",
    "credentials": "hive://secret/" + secret,
    "ingest": {"mode": "push", "backfill_days": int(backfill)},
    "features": {"outbound_observation": True, "pubsub_topic": topic, "pubsub_subscription": sub},
}
addrs = [a.strip() for a in mailboxes.split(",") if a.strip()]
bad = [a for a in addrs if "@" not in a]
if bad:
    sys.exit("not an email address: " + ", ".join(bad))
if addrs:
    rec["scope"] = {"include_addresses": addrs}
json.dump(rec, open(out, "w"), indent=2)
' "$SECRET_NAME" "$TOPIC_PATH" "$SUB_PATH" "$MAILBOXES" "$BACKFILL_DAYS" "$RECORD" \
    || die "Invalid --mailboxes or --backfill-days."
  if ! out="$("${LC[@]}" hive set --hive-name mailsec_provider --key "$CONNECTION_NAME" \
      --input-file "$RECORD" --enabled --oid "$OID" 2>&1)"; then
    printf '%s\n' "$out" >&2
    die "Could not save the connection. The API key needs mailsec_provider.set."
  fi
  if [ -n "$MAILBOXES" ]; then
    ok "Saved, protecting: $MAILBOXES"
  else
    ok "Saved, protecting every mailbox in the domain"
  fi
fi

step "Connection test (includes a real Gmail notification check)"
test_ok=""
for attempt in 1 2 3 4 5 6; do
  result="$("${LC[@]}" mailsec connection test "$CONNECTION_NAME" --include-watch \
    --oid "$OID" --output json 2>&1 || true)"
  verdict="$(printf '%s' "$result" | python3 -c '
import json, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    print("ERROR"); print(raw.strip()[:2000]); sys.exit()
# Accept the result at the top level or wrapped in one object.
if "checks" not in d:
    for v in d.values():
        if isinstance(v, dict) and "checks" in v:
            d = v; break
print("PASS" if d.get("ok") else "FAIL")
for c in d.get("checks", []):
    line = "  %-14s %-8s%s" % (c.get("id", ""), c.get("status", ""), "" if c.get("required") else " (optional)")
    print(line)
    if c.get("status") == "failed" and c.get("remediation"):
        print("      -> " + c["remediation"])
')"
  first="${verdict%%$'\n'*}"
  printf '%s\n' "${verdict#*$'\n'}" | sed 's/^/  /'
  if [ "$first" = PASS ]; then
    test_ok=1
    break
  fi
  # A refusal (not a test result) will not fix itself by waiting.
  [ "$first" = ERROR ] && break
  [ "$attempt" -lt 6 ] || break
  info "Not passing yet. Google can take a few minutes to apply new permissions; retrying in 30s ($attempt/5)..."
  sleep 30
done

if [ -n "$test_ok" ]; then
  ok "Connection test passed"
  if [ -n "$uses_our_secret" ]; then
    rm -f "$KEY_FILE"
    ok "Deleted $KEY_FILE (LimaCharlie now holds the credential in secret $SECRET_NAME)"
    retire_old_keys
  else
    warn "Connection $CONNECTION_NAME does not use the key in $KEY_FILE ($CURRENT_KID), so it was kept and no keys were deleted."
    info "A re-run reuses it. If you do not need it, delete both the key and the file:"
    info "  gcloud iam service-accounts keys delete $CURRENT_KID --iam-account=$SA_EMAIL --project=$PROJECT && rm -f $KEY_FILE"
  fi
  step "Done"
  info "Mail should start appearing in Email Security within a few minutes."
else
  warn "The connection test has not passed yet. Fix the items above, then re-run this script"
  info "or run: limacharlie mailsec connection test $CONNECTION_NAME --include-watch --oid $OID"
  info "$KEY_FILE was kept so a re-run reuses the same key; delete it once the test passes."
  exit 1
fi
