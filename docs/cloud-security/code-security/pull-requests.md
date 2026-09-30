# Pull-request checks and push rescans

A scheduled scan tells you what a repository contains. On GitHub, Code Security
can also:

- **rescan on every push** to the default branch, so a fix shows as fixed within
  minutes instead of at the next daily pass;
- **check every pull request** and report what the change *introduces*, as a
  GitHub check run you can make required before merging.

Both are GitHub-only. GitLab and Bitbucket repositories are scanned on the
policy's schedule.

## What you need

| Piece | What it does | Already done by **Create a GitHub App for me**? |
|---|---|---|
| **The App's webhook** | GitHub sends push and pull-request events to LimaCharlie | Yes |
| **Three D&R rules** | Turn those events into a rescan or a check | Yes, if you had `dr.list` and `dr.set` |
| **Checks** and **Pull requests: Read and write** on the App | Lets LimaCharlie publish the check | Yes |
| **`pr_checks: true`** in the policy | Turns pull-request checks on | Only with the starter policy |

Push rescans need only the webhook and rules. Use the
[webhook status](#webhook-status) on the **Code security** Overview tab to see
what is missing for your connection.

## How it works

```text
GitHub App webhook ──▶ LimaCharlie webhook adapter ──▶ D&R rule ──▶ rescan or check
```

A GitHub App has **one** webhook, which receives events from every repository
the App is installed on. So each GitHub connection needs one webhook, never one
per repository. The code-scanning policy still decides which repositories are
scanned and checked. Events for other repositories are ignored.

Every delivery is signed with the webhook secret. LimaCharlie rejects a delivery
whose signature does not match, and ignores a redelivery of an event it already
processed.

## Push rescans

When a push lands on a repository's **default branch**, the repository is
rescanned. Pushes within 10 minutes of the first are combined into one scan of
the latest commit. Pushes to other branches are ignored.

The usual rules still apply: the repository must be in the connection's
inventory, not archived, and selected by an enabled policy. Each repository can
have up to 50 triggered scans a day (pushes and manual rescans). Scheduled scans
do not count.

## Turn on pull-request checks

Add to the code-scanning policy, or tick **Publish a check run on pull
requests** in the policy form:

```yaml
pr_checks: true
pr_comments: false   # true posts one summary comment, edited on each push
gating:
  fail_on: HIGH      # CRITICAL, HIGH, MEDIUM, LOW or NONE
```

- `gating.fail_on` sets the lowest severity that fails the check. When it is
  missing, or `NONE`, the check reports but never fails, so turning checks on
  never blocks a merge by surprise.
- `pr_comments` is off by default, because a comment notifies everyone watching
  the pull request. When on, there is one comment per pull request, updated in
  place.

A check runs when a pull request is opened, reopened, receives new commits, or is
retargeted to a different base branch. Draft pull requests are checked too.

To block merges, make **LimaCharlie Code Security** a required status check in
the repository's branch protection rules on GitHub.

### Keeping write access on a separate App

By default, checks, comments and AutoFix write through the connection's own
GitHub App, with a token limited to each action. If you prefer to keep write
access off that App, create a second GitHub App with **Checks**, **Pull
requests** and (for AutoFix) **Contents** set to **Read and write**, install it,
and name it on the provider record:

```yaml
provider_type: github
github_org: "acme"
github_app_id: "1234567"
github_installation_id: "89012345"
credentials: hive://secret/github-app-key
github_actions_app_id: "7654321"
github_actions_installation_id: "54321098"
actions_credentials: hive://secret/github-code-actions-key
```

The three fields are set together. The record is refused if they name the same
App, or the same secret, as the connection. The webhook stays on the
connection's App.

## What the check says

Both the base and head commits are scanned, and findings are compared by
identity, not line number. A finding that moves within a file is not reported as
new. Findings from pull requests are never added to your worklist: the worklist
reflects the default branch.

| Result | Conclusion |
|---|---|
| Nothing new, both scans complete | `success` |
| New findings, none at or above `fail_on` | `neutral` |
| A new finding at or above `fail_on` | `failure` |
| A scan hit a limit | never `success`, because the scan did not see everything |
| The scan could not run | `neutral`, saying the scan did not complete. An outage on our side does not block your merge |

Findings below the policy's `severity_floor` are not counted, and `INFO`
findings never fail a check.

Both commits are checked with the same [code rules](code-rules.md). If the rules
could not be used, or different rules failed to load on the two commits, code
weaknesses are left out and the check cannot be `success`. See
[Pull-request checks](code-rules.md#pull-request-checks) on the Code rules page.

The check shows the full counts and up to 50 annotations, which is GitHub's
limit per update. Pushes within about 20 seconds produce one check, on the
newest commit.

Each check uses 2 of the connection's 500 daily pull-request writes, or 3 with
comments on, so a connection can publish roughly 250 checks a day.

!!! warning "Required checks and declined events"
    If a pull-request event is declined (see [Is it firing?](#is-it-firing)), no
    check is created and a required check stays pending until the next push.
    Push a new commit, or close and reopen the pull request, to try again.

LimaCharlie re-reads the pull request from GitHub before scanning, and uses
GitHub's commits rather than the values in the event.

## Webhook status

The **Code security** Overview tab has a **GitHub webhooks** section. It reads
each connection's App settings from GitHub and shows whether events reach this
organization:

| Status | Meaning | What to do |
|---|---|---|
| **Receiving events** | The webhook points here and sends push and pull-request events. | Nothing. Check that the rules are installed under **Webhook automation**. |
| **Not connected**, no active webhook | The App has no webhook, or it is not active. | [Set up webhook](#set-up-webhook). |
| **Not connected**, points elsewhere | The webhook sends to another address, or is not using JSON with TLS verification. | [Fix webhook](#fix-webhook). |
| **Missing events** | The App is not subscribed to **Push** and/or **Pull request**. | A GitHub organization owner ticks them under the App's **Permissions & events**. GitHub has no API for this. |
| **Not verified** | GitHub could not be read: a timeout, a rate limit or rejected credentials. | It is checked again automatically. If it persists, check that the App and its private key still exist. |
| **Secret not synced** | The App may be signing with a different secret than LimaCharlie verifies. | [Sync webhook secret](#sync-webhook-secret). |
| **Name conflict** | Two connection names differ only by letter case, so they would share one webhook adapter. No webhook actions are offered. | Delete one connection and add it again under a different name. |
| **Needs attention** | GitHub reported something else. | Follow the detail shown. |

A fix made on GitHub shows within about a minute, or choose **Check again**. A
webhook that breaks on GitHub can keep showing **Receiving events** for up to 5
minutes. The status reads the App's settings. It does not prove deliveries
arrive, so use GitHub's **Recent Deliveries** for that.

The **Webhook automation** panel below it shows whether the three rules are
installed. **Install the webhook rules** installs all three, and **Remove the
rules** takes them out. Both need `dr.list` and `dr.set`.

### Set up webhook

For an App with no active webhook. **Set up webhook** creates the connection's
webhook adapter and signing secret if needed, installs missing rules, and shows a
**Payload URL** and **Secret**. It needs `secret.get`, `secret.set`,
`cloudsensor.get`, `cloudsensor.set`, `ikey.list` and `ikey.set`, plus `dr.list`
and `dr.set` for the rules.

GitHub's API cannot create or activate an App webhook, so a GitHub organization
owner finishes on GitHub. Open **Organization → Settings → Developer settings →
GitHub Apps → the App**, then:

1. Under **General → Webhook**, tick **Active**.
2. Paste the **Payload URL** into **Webhook URL**.
3. Set **Content type** to `application/json`.
4. Paste the **Secret** into **Webhook secret**.
5. Keep **SSL verification** enabled.
6. Under **Permissions & events → Subscribe to events**, tick **Push** and
   **Pull request**. GitHub offers **Push** only once the App has **Contents**
   access, and **Pull request** only once it has **Pull requests** access.
7. Save, then choose **Check again** in LimaCharlie.

### Fix webhook

For an App whose webhook points somewhere else. **Fix webhook** prepares the
adapter, secret and rules like **Set up webhook**, then updates the App's
webhook through GitHub's API. It needs `cloudsec.set` in addition to the
permissions above.

A GitHub App has only one webhook. The page asks you to confirm with **Replace
webhook**: whatever receives those events today stops receiving them, and the
old secret cannot be restored. If another tool relies on that webhook, connect
LimaCharlie with its own App instead.

If the webhook already delivers to a **different LimaCharlie organization**,
**Fix webhook** refuses and changes nothing. One App can serve only one
organization. Create a separate App for this one.

### Sync webhook secret

Deliveries fail with `401` in GitHub's **Recent Deliveries** when the App signs
with a different secret than LimaCharlie verifies. **Re-sync webhook secret**
(or **Sync webhook secret** when the status is **Secret not synced**) sets
LimaCharlie's secret on the App through GitHub's API. It asks for confirmation,
because the App's current secret cannot be restored. It needs `cloudsec.set`,
`secret.get` and `cloudsensor.get`, and is not offered while the status is **Not
connected**.

**Secret not synced** appears when a **Create a GitHub App for me** setup could
not confirm the secret. The flag is kept only in the browser that ran the setup.

## Is it firing?

If pushes are not rescanned or pull requests get no check, go through these in
order:

1. **The webhook.** The connection shows **Receiving events**, and **Webhook
   automation** shows all three rules installed.
2. **GitHub delivered the event.** On GitHub, open the App's settings →
   **Advanced → Recent Deliveries**. Look for a `push` or `pull_request`
   delivery answered with `200`. A `401` usually means the secrets differ, so
   use [Re-sync webhook secret](#sync-webhook-secret). It can also mean the
   webhook URL is wrong, so read the response body GitHub shows. No delivery at
   all usually means the App is not installed on that repository. GitHub's
   **Redeliver** of an event already accepted in the last 24 hours does nothing.
3. **The rule matched.** Replay the rule over a few minutes around the delivery.
   `--start` and `--end` are Unix seconds. Replay is billed on the data it reads,
   so keep the window short.

    ```bash
    limacharlie replay run --name cloudsec-code-pr-check \
        --start 1750000000 --end 1750000600
    ```

    Use `cloudsec-code-push-rescan` for a push, or `cloudsec-code-pr-retarget`
    for a base-branch change.

4. **The policy and permissions.** The repository is selected by an enabled
   policy with `pr_checks: true`, and **Protection capabilities** shows
   pull-request checks as available. `limacharlie cloudsec code capabilities
   --repo <owner>/<name>` gives the same answer.
5. **The check.** It appears on the pull request's **Checks** tab as
   **LimaCharlie Code Security**, usually within a minute and completed within a
   few minutes.

A declined check leaves nothing on the pull request, and no event is emitted, so
check each of these:

- both `pr_checks` and `pr_comments` are off for that repository, or no enabled
  policy selects it (with only `pr_comments` on, you get a comment but no check);
- the App lacks **Checks** or **Pull requests: Read and write**, or is not
  installed on that repository;
- the repository is not in the inventory, is archived, is over the free-tier
  repository limit, or exists only through [pushed results](bring-your-own-scanner.md);
- the pull request is not open, its head moved since the event, or its base and
  head are the same commit;
- GitHub could not be read to confirm the pull request;
- the connection used its daily budget of 500 pull-request writes (if the budget
  cannot be read, a `neutral` check saying the scan did not run is published
  instead);
- a retarget event did not actually change the base commit.

## Manual setup

Use this only when you manage your organization entirely as code, or want to
fork a rule. It gives the same result as **Set up webhook**.

### 1. Create the webhook adapter

Create a `cloud_sensor` record named `github-code-webhook-<connection>`, where
`<connection>` is the connection name in lowercase. Its `hostname` must be
exactly `github-code-webhook`, because the rules match on it. It holds two
random secrets: `secret` goes in the URL, and `signature_secret` is the key
GitHub signs with.

```bash
OID=<your organization id>
CONNECTION=<the connection name, lowercased>
# The installation key's ID (a UUID), not the long encoded key.
INSTALLATION_KEY=<an installation key ID for the organization>
SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(32))")
SIGNATURE_SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(32))")
cat > hook.json <<JSON
{
  "sensor_type": "webhook",
  "webhook": {
    "secret": "$SECRET",
    "signature_scheme": "hmac-sha256",
    "signature_header": "X-Hub-Signature-256",
    "signature_secret": "$SIGNATURE_SECRET",
    "client_options": {
      "hostname": "github-code-webhook",
      "identity": {"oid": "$OID", "installation_key": "$INSTALLATION_KEY"},
      "platform": "json",
      "sensor_seed_key": "github-code-webhook-$CONNECTION"
    }
  }
}
JSON
limacharlie hive set --hive-name cloud_sensor --key "github-code-webhook-$CONNECTION" \
    --input-file hook.json --enabled
```

The hook URL is
`https://<hooks domain>/<oid>/github-code-webhook-<connection>/<secret>`. The
hooks domain is the `url.hooks` value of `GET /v1/orgs/{oid}/url`. See the
[webhook adapter tutorial](../../2-sensors-deployment/adapters/tutorials/webhook-adapter.md)
for the adapter format.

An older adapter named just `github-code-webhook` still works for a single
connection, but **Set up webhook**, **Fix webhook** and the API only work with
per-connection names.

### 2. Point the App at it

Follow the [Set up webhook](#set-up-webhook) steps on GitHub with your URL and
`$SIGNATURE_SECRET`. If the App already has an active webhook, you can use
[the API](#the-webhook-api) instead.

### 3. Install the rules

Save each rule below to a file and install it into the `dr-general` hive:

```bash
limacharlie hive set --hive-name dr-general \
    --key cloudsec-code-push-rescan --input-file push-rescan.yaml --enabled
limacharlie hive set --hive-name dr-general \
    --key cloudsec-code-pr-check --input-file pr-check.yaml --enabled
limacharlie hive set --hive-name dr-general \
    --key cloudsec-code-pr-retarget --input-file pr-retarget.yaml --enabled
```

The rules only match deliveries whose signature LimaCharlie verified
(`event/__lc_signature_verified`).

**`cloudsec-code-push-rescan`** rescans a repository after a push:

<!-- generated from the code lane's canonical webhook recipe definition; rule=cloudsec-code-push-rescan; sha256=0fc818b70646d3d42101331dd0011354e0cf14bbd06a8f67d847276873467c9c; do not edit -->

```yaml
detect:
  event: json
  op: and
  rules:
    - op: is
      path: routing/hostname
      value: github-code-webhook
    - op: is
      path: event/__lc_signature_verified
      value: true
    - op: exists
      path: event/head_commit/id
    - op: exists
      path: event/repository/full_name
    - op: starts with
      path: event/ref
      value: refs/heads/
    - op: is
      path: event/deleted
      value: false
respond:
  - action: extension request
    extension name: ext-cloud-security
    extension action: code_scan_now
    extension request:
      repo: '{{ .event.repository.full_name }}'
      ref: '{{ .event.ref }}'
```

<!-- end generated: cloudsec-code-push-rescan -->

**`cloudsec-code-pr-check`** checks a pull request when it is opened, reopened
or updated:

<!-- generated from the code lane's canonical webhook recipe definition; rule=cloudsec-code-pr-check; sha256=d345295d2d6219ac9308b7a033b749ff502483c2b7464da314f60114a785fb57; do not edit -->

```yaml
detect:
  event: json
  op: and
  rules:
    - op: is
      path: routing/hostname
      value: github-code-webhook
    - op: is
      path: event/__lc_signature_verified
      value: true
    - op: exists
      path: event/pull_request/number
    - op: exists
      path: event/repository/full_name
    - op: exists
      path: event/pull_request/head/sha
    - op: exists
      path: event/pull_request/base/sha
    - op: or
      rules:
        - op: is
          path: event/action
          value: opened
        - op: is
          path: event/action
          value: synchronize
        - op: is
          path: event/action
          value: reopened
respond:
  - action: extension request
    extension name: ext-cloud-security
    extension action: code_pr_check
    extension request:
      repo: '{{ .event.repository.full_name }}'
      pr: event.pull_request.number
      base_sha: '{{ .event.pull_request.base.sha }}'
      head_sha: '{{ .event.pull_request.head.sha }}'
      base_ref: '{{ .event.pull_request.base.ref }}'
      head_ref: '{{ .event.pull_request.head.ref }}'
      action: '{{ .event.action }}'
```

<!-- end generated: cloudsec-code-pr-check -->

**`cloudsec-code-pr-retarget`** re-checks a pull request whose base branch
changed. GitHub reports that as an `edited` event with no new commits, so without
this rule a required check would keep a result for a diff that no longer exists:

<!-- generated from the code lane's canonical webhook recipe definition; rule=cloudsec-code-pr-retarget; sha256=031e394f79a92e2ad0d7313d2e19a8f3880bafbf898980c8f114b4b6523a4258; do not edit -->

```yaml
detect:
  event: json
  op: and
  rules:
    - op: is
      path: routing/hostname
      value: github-code-webhook
    - op: is
      path: event/__lc_signature_verified
      value: true
    - op: is
      path: event/action
      value: edited
    - op: exists
      path: event/changes/base/sha/from
    - op: exists
      path: event/pull_request/number
    - op: exists
      path: event/repository/full_name
    - op: exists
      path: event/pull_request/head/sha
    - op: exists
      path: event/pull_request/base/sha
respond:
  - action: extension request
    extension name: ext-cloud-security
    extension action: code_pr_check
    extension request:
      repo: '{{ .event.repository.full_name }}'
      pr: event.pull_request.number
      base_sha: '{{ .event.pull_request.base.sha }}'
      head_sha: '{{ .event.pull_request.head.sha }}'
      base_ref: '{{ .event.pull_request.base.ref }}'
      head_ref: '{{ .event.pull_request.head.ref }}'
      action: '{{ .event.action }}'
      prev_base_sha: '{{ .event.changes.base.sha.from }}'
```

<!-- end generated: cloudsec-code-pr-retarget -->

!!! warning "If you fork these rules"
    - Keep `pr` as a bare path (`event.pull_request.number`), not a
      `{{ ... }}` template. A template turns the number into text, the request is
      rejected with `invalid value for pr: not an integer, a string`, and no check
      appears.
    - Do not add `prev_base_sha` to `cloudsec-code-pr-check`. Those events have
      no such field, so the template renders as `<no value>` and every check is
      rejected.
    - To skip draft pull requests, add a condition that `event/pull_request/draft`
      is `false`. Marking a draft ready for review does not trigger a new check,
      so push a commit afterwards or a required check never arrives.

## The webhook API

**Fix webhook** uses a public route you can also call from automation. Like
**Fix webhook**, it updates an App's **active** webhook. It cannot create or
activate one.

```text
POST https://api.limacharlie.io/v1/cloudsec/{oid}/code/webhook
```

It requires `cloudsec.set`. It does not create the adapter or its secret.

```json
{
  "connection": "<the GitHub connection's cloudsec_provider record name>",
  "url": "https://<hooks domain>/<oid>/github-code-webhook-<connection>/<url secret>",
  "secret": "<the adapter's signature_secret>"
}
```

- `url` must be this organization's hook URL for a per-connection adapter:
  `https`, this organization's hooks domain and ID, three path segments, and no
  port, credentials, query or fragment. Anything else is refused, so the route
  cannot point your App outside LimaCharlie.
- `secret` is 20 to 256 characters with no whitespace.

The response is the connection's re-checked status. The URL and secrets are
never returned:

```json
{"state": "available", "reason": "", "missing_events": [], "detail": ""}
```

`state` is `available`, `unavailable` or `unknown`. `reason` is empty,
`webhook_not_configured`, `webhook_points_elsewhere`, `missing_events` or
`verification_unavailable`. A successful call can still report `missing_events`,
because event subscriptions can only be changed on GitHub.

Errors carry a `reason` at the top level:

| HTTP | `reason` | Meaning |
|---|---|---|
| 400 | `invalid_connection`, `invalid_url`, `invalid_secret` | The body is malformed, or the URL is not this organization's per-connection hook URL. |
| 400 | `connection_not_found`, `provider_not_github` | No such connection, or it is not GitHub. |
| 400 | `credential_unavailable` | The App's credentials are missing or unreadable. |
| 400 | `webhook_not_active` | The App has no active webhook. An owner must enable it on GitHub first. |
| 400 | `webhook_in_use_by_other_org` | The webhook delivers to another LimaCharlie organization. Nothing changed. |
| 500 | `hooks_domain_unavailable` | The organization's hooks domain could not be determined. Nothing changed. |
| 502 | `github_unavailable` | GitHub was unreachable or rate-limited the request. Retry later. |
| 502 | `github_credential_rejected` | GitHub rejected the App's credentials. |
| 502 | `github_rejected` | GitHub refused the update. The message says why. |
| 503 | `host_unavailable` | A temporary LimaCharlie failure. Safe to retry. |
| 504 | `timeout` | The change may already be applied. Re-read the status before retrying. |

Each GitHub connection's current status is also in the `webhook` object of
`GET /v1/cloudsec/{oid}/code/capabilities`.
