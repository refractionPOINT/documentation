# Command Line Interface

The `limacharlie mailsec` command group covers the whole Email Security API
surface: the coverage screen, the message index and drawer, the audited raw-EML
download, campaigns and campaign-wide sweeps, sender profiles, the action audit
trail, the abuse-mailbox report queue, retro-hunts, custom-rule validation and
backtest, the connection preflight, and the served onboarding guide.

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
`dr-mail`). This group is the query, triage and remediation surface.

## Permissions

Four, rather than the usual get/set pair, because Email Security asks to be
trusted with four separable things:

| Permission | Covers |
|---|---|
| `mailsec.get` | Read the product's own view: queue, drawer, campaigns, senders, audit trail |
| `mailsec.set` | Change detection behaviour and triage state |
| `mailsec.act` | Remediate live mail at the provider |
| `mailsec.get.eml` | Download the original bytes of a message; requires a logged justification |

`mailsec.get.eml` is separate on purpose: opening the drawer shows you the
product's structured view of a message, while downloading the EML takes a
person's actual mail out of your tenant. Gating them identically would mean
typing a justification to look at the queue.

## At a glance

```bash
# Coverage
limacharlie mailsec coverage --window-days 30

# The triage queue
limacharlie mailsec message list --verdict suspicious --verdict malicious
limacharlie mailsec message list --mailbox cfo@corp.example --since 2026-08-01
limacharlie mailsec message list --user-reported            # a human flagged these
limacharlie mailsec message list --link-domain evil.example # IOC pivot
limacharlie mailsec message list --attachment-sha256 <sha>  # IOC pivot
limacharlie mailsec message get <msg_uuid>
limacharlie mailsec message similar <msg_uuid>              # who else got it
limacharlie mailsec message eml <msg_uuid> --justification "INC-4471"

# Remediation
limacharlie mailsec message action <msg_uuid> --action quarantine_message --reason "confirmed phish"
limacharlie mailsec message action <msg_uuid> --action restore_message

# Campaigns: one attack, triaged once
limacharlie mailsec campaign list --min-members 3
limacharlie mailsec campaign get <campaign_id>
limacharlie mailsec campaign action <campaign_id> --action quarantine_message           # preview
limacharlie mailsec campaign action <campaign_id> --action quarantine_message --confirm <campaign_id>

# Senders and the audit trail
limacharlie mailsec sender get cfo@corp.example
limacharlie mailsec sender get domain:corp.example
limacharlie mailsec action get <action_id>

# Abuse-mailbox reports
limacharlie mailsec report list --status open --oldest-first
limacharlie mailsec report get <report_id>
limacharlie mailsec report resolve <report_id> --disposition true_positive

# Custom rules
limacharlie mailsec rule validate --file rule.json --rule-id custom-lookalike
limacharlie mailsec rule backtest --file rule.json --since 2026-08-01

# Hunts
limacharlie mailsec hunt create --detect-file detect.json --since 2026-07-01
limacharlie mailsec hunt get <hunt_id>
limacharlie mailsec hunt remediate <hunt_id> --action quarantine_message --confirm <hunt_id>

# Analysis and setup
limacharlie mailsec analyze --file suspect.eml --org-domain corp.example
limacharlie mailsec connection test gws-exp
limacharlie mailsec onboarding --provider gworkspace
```

## Things worth knowing before you script this

### Actions preview by default

`campaign action` and `hunt remediate` report what they *would* do and change
nothing unless you pass `--confirm`. That is deliberate for an operation whose
blast radius is every mailbox that received an attack.

```bash
limacharlie mailsec campaign action <campaign_id> --action quarantine_message            # dry run
limacharlie mailsec campaign action <campaign_id> --action quarantine_message --confirm <campaign_id>
```

### `alert_only` is a success, not a failure

An action's `result` can come back as `alert_only`, meaning the action was
**decided and deliberately not performed** because your organization is not in
enforce mode. Do not treat it as an error — it is the product doing what you
configured, reported honestly rather than dressed up as `ok`.

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
limacharlie mailsec campaign action "$CAMPAIGN" --action quarantine_message --output yaml
limacharlie mailsec campaign action "$CAMPAIGN" --action quarantine_message --confirm "$CAMPAIGN"

# Resolve the oldest open report
REPORT=$(limacharlie mailsec report list --status open --oldest-first --limit 1 \
  --output json | jq -r '.reports[0].report_id')
limacharlie mailsec report resolve "$REPORT" --disposition true_positive
```

Because the CLI is the whole surface, it is also how an
[AI triage agent](ai-triage.md) reaches Email Security — there is no separate
integration for agents to learn.
