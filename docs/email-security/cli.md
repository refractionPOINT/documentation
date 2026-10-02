# Command Line Interface

--8<-- "includes/email-security-beta.md"

The `limacharlie mailsec` command group covers the Email Security API surface:
the coverage screen, the message index and drawer, the audited raw-EML download,
verdict revisions, campaigns and campaign-wide sweeps, bulk remediation over a
selection you name, sender profiles, the action audit trail, the abuse-mailbox
report queue, sample submission, custom-rule validation and backtest, the connection preflight, the
served onboarding guide, and the tenant purge.

Commands take the global options (`--oid`,
`--output json|yaml|toon|csv|table|jsonl`, `--filter <jmespath>`,
`--fields <names>`), and every command and subgroup answers `--ai-help` with
task-oriented guidance.

```bash
limacharlie mailsec --help
```

Every command requires the org to be subscribed to the extension:

```bash
limacharlie extension subscribe --name ext-email-security --oid $OID
```

Provider connections and policy are Hive records — manage them with the
standard `limacharlie hive` commands (`mailsec_provider`, `mailsec_policy`,
`dr-mail`). This group is the query, triage and remediation surface. See
[Policy Reference](policy.md) for the record contracts and
[API Reference](api-reference.md) for the routes these commands call.

## Actions in alert-only mode

An action in an alert-only organization is audited but withheld, with
`force_required: true`. The CLI prints a notice on stderr. Repeat with `--force`
to perform it deliberately:

```bash
limacharlie mailsec message action <msg_uuid> --action quarantine_message --force
```

`message bulk-action` and `campaign action` also accept `--force`. Their preview
and `--confirm` requirements still apply; `--force` does not bypass selection
confirmation or permissions. The override applies only to the requested action
or job and is audited separately from the withheld attempt. Inspect per-message
outcomes for bulk jobs. See [enforcement](messages.md#enforcement).

## Permissions

Four, rather than the usual get/set pair, because Email Security asks to be
trusted with four separable things — plus one command that is not any of them:

| Permission | Covers |
|---|---|
| `mailsec.get` | Read the product's own view: queue, drawer, campaigns, senders, audit trail |
| `mailsec.set` | Change triage state — resolving a user report |
| `mailsec.act` | Remediate live mail at the provider; submit and withdraw samples |
| `mailsec.get.eml` | Download the original bytes of a message; requires a logged justification |
| `mailsec.act` **and** `billing.ctrl` **and** `user.ctrl` | `tenant purge`, in both its preview and its destructive form. Owner-level authority, the same trio deleting the organization requires — there is no separate "owner" permission |

`mailsec.get.eml` is separate on purpose: opening the drawer shows you the
product's structured view of a message, while downloading the EML takes a
person's actual mail out of your tenant. Gating them identically would mean
typing a justification to look at the queue.

## At a glance

```bash
# Coverage
limacharlie mailsec coverage --window-days 30

# Explicit UTC window instead of window-days (development builds with these flags).
limacharlie mailsec coverage --since "2026-09-01T00:00:00Z" --until "2026-09-02T00:00:00Z"

# The triage queue
limacharlie mailsec message list --verdict suspicious --verdict malicious
limacharlie mailsec message list --mailbox cfo@corp.example --since 2026-08-01
limacharlie mailsec message list --user-reported            # a human flagged these
limacharlie mailsec message list --lane backfill            # historical analysis, not live actions
limacharlie mailsec message list --link-domain evil.example # IOC pivot
limacharlie mailsec message list --attachment-sha256 <sha>  # IOC pivot
limacharlie mailsec message get <msg_uuid>
limacharlie mailsec message similar <msg_uuid>              # who else got it
limacharlie mailsec message eml <msg_uuid> --justification "INC-4471"

# Re-judging a message, and reading how its verdict moved
limacharlie mailsec message revise <msg_uuid> --verdict malicious --rationale "confirmed credential harvest"
limacharlie mailsec message revisions <msg_uuid>

# Remediation
limacharlie mailsec message action <msg_uuid> --action quarantine_message --reason "confirmed phish"
limacharlie mailsec message action <msg_uuid> --action restore_message

# Bulk remediation over a selection you name: previews without --confirm
limacharlie mailsec message bulk-action --action quarantine_message --input-file uuids.txt
limacharlie mailsec message bulk-action --action quarantine_message --input-file uuids.txt --confirm <token> --reason "INC-4471"
limacharlie mailsec message bulk-status <bulk_id>

# Sample submission (opt-in): copy ONE message to LimaCharlie, list it, withdraw it
limacharlie mailsec message submit-sample <msg_uuid> --category missed_threat --reason "credential phish we did not flag"
limacharlie mailsec message withdraw-sample <msg_uuid>
limacharlie mailsec submission list --category false_positive --since 2026-09-01T00:00:00Z
limacharlie mailsec submission get <submission_id>
limacharlie mailsec submission withdraw <submission_id>

# Campaigns: one attack, triaged once
limacharlie mailsec campaign list --min-members 3
limacharlie mailsec campaign get <campaign_id>
limacharlie mailsec campaign action <campaign_id> --action quarantine_message              # preview
limacharlie mailsec campaign action <campaign_id> --action quarantine_message --confirm <token>

# Senders and the audit trail
limacharlie mailsec sender get cfo@corp.example
limacharlie mailsec sender get domain:corp.example
limacharlie mailsec action get <action_id>

# Abuse-mailbox reports
limacharlie mailsec report list --status open --oldest-first
limacharlie mailsec report get <report_id>
limacharlie mailsec report resolve <report_id> --disposition malicious
limacharlie mailsec report reopen <report_id>

# Custom rules
limacharlie mailsec rule validate --file rule.json --rule-id custom-lookalike
limacharlie mailsec rule backtest --file rule.json --since 2026-08-01

# Analysis and setup
limacharlie mailsec analyze --file suspect.eml --org-domain corp.example
limacharlie mailsec connection test gws-exp
limacharlie mailsec onboarding --provider gworkspace
limacharlie mailsec onboarding --provider gworkspace \
  --project-id "$GCP_PROJECT" --sa-email "$SERVICE_ACCOUNT_EMAIL" \
  --topic mailsec-gmail-push --subscription mailsec-gmail-push-sub

# Delete everything Email Security holds for this org — previews without --confirm
limacharlie mailsec tenant purge
```

`--window-days` accepts 1-35 (the platform's maximum message retention) and cannot be combined with an explicit `--since`/`--until`. Out-of-range values for `--limit`, `--min-score` and `--min-members` are refused with an error naming the flag rather than silently clamped or ignored.

The `--lane`, explicit coverage-window and personalized-onboarding flags are
development additions. Check the command's `--help`; an older development
checkout may lack them. They are tracked in the
[public SDK update](https://github.com/refractionPOINT/python-limacharlie/pull/408);
until it is merged, `master` does not include every new flag. Use the equivalent query parameters in the
[API reference](api-reference.md#reads) with `limacharlie api` until you update.
`--lane` cannot be combined with `--mailbox`, `--sender-email` or `--campaign-id`;
it filters where a message was judged, not its threat verdict.

## Things worth knowing before you script this

### Campaign actions preview by default

`campaign action` reports what it *would* do and changes nothing unless you pass
`--confirm`. That is deliberate for an operation whose blast radius is every
mailbox that received an attack.

The preview returns the members, the distinct mailboxes it would touch, and a
`confirm` **token derived from that exact member set**. Pass the token back —
**not** the campaign id, which is refused — so a campaign that absorbed new
members while you were reading the preview fails the confirmation rather than
sweeping a set nobody approved.

```bash
PREVIEW=$(limacharlie mailsec campaign action "$CAMPAIGN" \
  --action quarantine_message --output json)
echo "$PREVIEW" | jq '{member_count, mailbox_count}'

TOKEN=$(echo "$PREVIEW" | jq -r .confirm)
limacharlie mailsec campaign action "$CAMPAIGN" \
  --action quarantine_message --confirm "$TOKEN"
```

Sweeps are capped at 500 members: above that the answer is a person deciding,
not a bigger dialog. See [Campaigns](campaigns.md#sweeping-a-campaign).

`--reason` is recorded on every member's audit row **and** on the sweep's own
row, which comes back as `action_id` and reads through
`limacharlie mailsec action get`. It is bounded at 1024 characters and refused
rather than truncated, and it is not part of the confirmation token — rewording
it after the preview does not invalidate the token.

`--attempt` asks for a **deliberate second run**. Re-running a sweep is
idempotent per member — the per-member audit key is the campaign itself, so a
double click, or a retry of a request whose response you never saw, collapses
onto the row each member already has instead of claiming a move that happened
once as two. A new `--attempt` composes with the campaign, minting a new action
id per member and a new sweep record, so a re-run after a provider outage is
recorded *beside* the run that failed rather than over it; the same value twice
collapses again. It is an opaque handle you mint, not prose: at most 128
characters, refused rather than truncated, because a clipped idempotency token
is a *different* token, and it is checked on the preview leg too.

Like `--reason`, it is **not** part of a campaign sweep's confirmation — unlike a
*bulk* action's `--attempt` [below](#bulk-remediation-previews-by-default-too),
which is. The two tokens answer different questions: a bulk token derives the
job's own identity, so the attempt is part of what it names, while a sweep's
token authorizes a member set and nothing else. Repeat a bulk `--attempt` on the
execute; add or change a sweep's freely.

`--attempt` on a campaign sweep needs the beta CLI from `master`; an older
one refuses the flag as unknown, and the field can be sent directly to the API
in the meantime (see
[Campaigns](campaigns.md#repeating-a-sweep-and-asking-for-a-second-one-on-purpose)).

```bash
limacharlie mailsec campaign action "$CAMPAIGN" \
  --action quarantine_message --confirm "$TOKEN" \
  --reason "re-running after the provider outage" \
  --attempt after-the-outage
```

### `alert_only` is a success, not a failure

An action's `result` can come back as `alert_only`, meaning the action was
**decided and deliberately not performed** because your organization is not in
enforce mode. Do not treat it as an error — it is the product doing what you
configured, reported honestly rather than dressed up as `ok`.

### Windowed coverage is budgeted

`coverage` with no `--window-days` is served from a short-lived server-side memo
and is the right shape for a script that polls it. Naming a window recomputes
the period from scratch, so those calls are counted against a per-organization
[read budget](api-reference.md#read-budgets) — generous (7,200/hour, decaying
every minute), but a tight loop over `--window-days` will reach it and answer
`429`.

### Filters are tri-state

Leaving a boolean filter unset means the dimension is *unconstrained*, which is
not the same as `false`:

```bash
limacharlie mailsec message list                      # every message
limacharlie mailsec message list --user-reported      # only reported mail
limacharlie mailsec message list --no-user-reported   # only unreported mail
```

### The EML download is audited

`message eml` requires `--justification`, and it is written to the access audit
with your identity. There is no way to fetch raw mail without leaving a record
of why.

```bash
limacharlie mailsec message eml <msg_uuid> \
  --justification "INC-4471, user reported credential harvest" \
  --out-file suspect.eml
```

### Reports have an SLA ordering

`--oldest-first` is what makes the report queue an SLA surface rather than a
feed. "The oldest thing nobody has looked at" is the question a queue exists to
answer, and it is not answerable from a newest-first page.

Each report also carries `original_found`. A report whose original was never
indexed is a real state — the mail predates the connection, or landed in a
mailbox outside your scope — and it is shown as a gap rather than as a blank
field.

### Backtest tells you what it could not see

`rule backtest` reports `skipped_no_raw`, `skipped_unparse` and `truncated`
alongside the match count, because a precision figure whose denominator quietly
shrank is a number that looks like a measurement and is not one. Its
`coverage_note` states the window it actually examined.

`precision` comes back as **null**, not `0`, when nothing it matched has an
analyst disposition yet. Zero would read as "everything it matched was wrong"
and would have you discard a good rule.

```bash
limacharlie mailsec rule backtest --file rule.json --output yaml
```

### Backtests are budgeted

`rule backtest` re-reads every stored message in its window, so it is bounded per
organization: **6 backtests per 10 minutes**, decaying every minute, across every
credential in the organization. Past it the command reports a `429` carrying
`rate_bucket: mailsec_post_read` and a `Retry-After`. It is sized for authoring a
rule by hand; a script looping it will reach it. See
[Read budgets](api-reference.md#the-replay-budget).

### Bulk remediation previews by default too

`message bulk-action` is the campaign sweep's discipline over a selection you
name: omit `--confirm` and it previews, pass the token back and it executes. The
selection can come from `--msg-uuids`, `--input-file`, or standard input — which
is what lets the queue pipe into it:

```bash
limacharlie mailsec message list --verdict malicious --output json \
  | jq -r '.messages[].msg_uuid' \
  | limacharlie mailsec message bulk-action --action quarantine_message --input-file -
```

The execute must repeat the **identical** `--action`, `--msg-uuids` and
`--attempt` the preview was minted with — the token is derived from those three,
not issued as a nonce. `--reason` is not one of them, and **is** supported: it is
recorded on the job's audit row and on every message's.

The job runs in the background, `--wait` is the default, and **the exit code
carries the outcome** — `0` only when the job completed and something was acted
on. The full contract, including every `state`, `result` and count, is in
[Bulk Remediation](remediation.md#from-the-cli).

### Submitting a sample sends the message to LimaCharlie

`message submit-sample` copies one message to LimaCharlie, so it is opt-in, explicit and
one message per call. The organization must have opted in with a `sample_sharing`
[policy record](policy.md#sample_sharing); `--category`
(`missed_threat`, `false_positive`, `other`) and `--reason` (1 to 1024 characters) are
both required and are checked before anything is sent. A refusal (not opted in, no store
in the datacenter, raw copy no longer stored) is reported like any other failed action, with the reason in
`error`; the command prints the reason and exits non-zero. `submission list` prints the `enabled` and
`available` flags, so an empty list can be told apart from a feature that is off, and
pages with `--cursor`. `submission get` shows recorded access times for the copy, and
`submission withdraw` (or `message withdraw-sample`) deletes it. An unknown id is not an
error: `submission get` returns `submission: null` and `submission withdraw` returns
`withdrawn: false`, and the command says so on stderr. See
[Sample Submission](sample-submission.md).

### Revising a verdict is `mailsec.act`, not `mailsec.set`

`message revise` records a human verdict revision over the scorer's, appending to the
message's history rather than overwriting it. `--rationale` is required and
audited — at least one, at most ten, each 280 characters or fewer.

```bash
limacharlie mailsec message revise <msg_uuid> \
  --verdict benign --rationale "internal test send" --rationale "sender verified"
limacharlie mailsec message revisions <msg_uuid> --output yaml
```

The CLI always revises as `analyst`, because the operator of a CLI is a person.
An autonomous agent revises with its **own** key and `mode: ai` through the API,
so the audit can always say whether a person or a model decided.

`applied: false` is an honest outcome and not an error: the message already
carried that verdict and nothing changed. See
[Detections & Verdicts](detections.md#revising-a-verdict).

### The tenant purge is irreversible

`tenant purge` permanently deletes everything Email Security holds for the
organization — the message index and the long-term evidence lane, campaigns,
sender profiles, the action audit trail, user reports, stored raw messages and
their parsed copies, and link-detonation results — and removes the provider
connection and policy records, which stops the provider sending any further
notifications. There is no undo and no smaller scope than the whole tenant.

So it is two calls. With **no** `--confirm` the command previews: it prints the
warning and mints a confirmation token, and destroys nothing.

```bash
# 1. Preview. Prints the warning and a single-use token; changes nothing.
PREVIEW=$(limacharlie mailsec tenant purge --oid "$OID" --output json)
echo "$PREVIEW" | jq -r .warning

# 2. Purge, within 5 minutes, quoting that token.
TOKEN=$(echo "$PREVIEW" | jq -r .confirmation)
limacharlie mailsec tenant purge --oid "$OID" \
  --confirm "$TOKEN" \
  --reason "Tenant offboarded"
```

The token is **single-use and expires 5 minutes after it is minted**, so a purge
cannot be replayed and cannot be scripted without someone having been shown the
warning. A purge that comes back with `complete: false` did not finish and is
safe to repeat — but repeating it means starting again at step 1, because step 2
spent the token.

`--reason` is optional, capped at 1024 characters, and written to the
organization's audit log with your identity. Requires Owner-level authority. See
[Data retention and deletion](policy.md#data-retention-and-deletion) for exactly
what a purge removes, and for the deletion that happens on its own 30 days after
an organization unsubscribes.

## Filtering and pagination

Repeatable filters OR within a key and AND across keys:

```bash
# suspicious OR malicious, AND delivered to that mailbox
limacharlie mailsec message list \
  --verdict suspicious --verdict malicious \
  --mailbox cfo@corp.example
```

Cursors are opaque and are passed back verbatim. They encode which index the
walk is pinned to and are bound to the filter set that minted them — changing a
filter mid-walk is an error rather than a page that silently means something
else.

```bash
PAGE=$(limacharlie mailsec message list --limit 100 --output json)
NEXT=$(echo "$PAGE" | jq -r .next_cursor)
[ -n "$NEXT" ] && limacharlie mailsec message list --limit 100 --cursor "$NEXT"
```

An empty `next_cursor` means the last page.

## Scripting

```bash
# Every suspicious message that reached a VIP mailbox in the last day
limacharlie mailsec message list \
  --verdict suspicious \
  --mailbox ceo@corp.example \
  --since "$(date -d '1 day ago' +%s)" \
  --output json --filter 'messages[].{id: msg_uuid, subject: subject}'

# Quarantine every member of a campaign, after reading the preview
PREVIEW=$(limacharlie mailsec campaign action "$CAMPAIGN" --action quarantine_message --output json)
limacharlie mailsec campaign action "$CAMPAIGN" --action quarantine_message \
  --confirm "$(echo "$PREVIEW" | jq -r .confirm)"

# Resolve the oldest open report
REPORT=$(limacharlie mailsec report list --status open --oldest-first --limit 1 \
  --output json | jq -r '.reports[0].report_id')
limacharlie mailsec report resolve "$REPORT" --disposition malicious
```

Because the CLI is the whole surface, it is also how an
[AI triage agent](ai-triage.md) reaches Email Security — there is no separate
integration for agents to learn.

## Provider quarantine and release activity

`mailsec provider-quarantine list` and `mailsec release-request list` observe
Microsoft delivery and hosted-quarantine activity. They support connection,
status, time-window and cursor filters and return independent coverage. They
require a CLI build containing these commands and `mailsec.get`. See
[Provider Quarantine](provider-quarantine.md#cli-and-api) for examples and limits.

## Independent disposition and release

```bash
limacharlie mailsec message disposition <msg_uuid> --disposition benign --note "Reviewed"
limacharlie mailsec message disposition <msg_uuid> --clear
limacharlie mailsec message list --disposition none
limacharlie mailsec message bulk-disposition --msg-uuids <id1> --msg-uuids <id2> --disposition spam
limacharlie mailsec message release <msg_uuid> --reason "Reviewed as safe" --mode analyst
```

Disposition accepts `malicious`, `spam`, `graymail`, `benign`, or `simulation` and
never changes the engine verdict. A bulk selection is limited to 500 unique IDs;
individual failures are reported and cause a nonzero CLI exit. Release restores
placement and records a benign verdict and disposition. It needs `mailsec.act`;
`--force` supplies explicit consent in alert-only mode. See [Messages](messages.md).

For report remediation, first preview:

```bash
limacharlie mailsec report resolve <report_id> --disposition malicious --scope message --action quarantine_message
# all recipient copies of the reported message's group (durable job)
limacharlie mailsec report resolve <report_id> --disposition malicious --scope group --action quarantine_message --attempt $(uuidgen)
```

Read `remediation_preview`, then repeat with `--confirm <token>` and, when needed,
`--force`. Pure resolution uses `mailsec.set`; remediation also needs `mailsec.act`.
The report remains open during preview or when provider remediation fails.

Group report remediation uses `--scope group` with an explicit UUID `--attempt`,
reused through preview, confirmation and polling. Add `--wait` to wait up to
300 seconds for a complete preview or resolution; timeouts exit with code 2 and
the durable job continues. Resume with the same attempt and confirmation.
See [group report remediation](user-reports.md#remediate-the-same-message-across-recipients)
for the complete workflow.
