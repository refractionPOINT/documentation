# Campaigns

--8<-- "includes/email-security-beta.md"

An attack that reached forty mailboxes is one thing that happened, not forty. A
campaign is the cluster of messages the engine attributed to one attack, so it is
triaged once and remediated once.

## How clustering works

Every message contributes cluster keys at ingest time:

| Key | How it is built |
|---|---|
| **Normalized subject** | Lowercased, reply/forward prefixes stripped (`Re:`, `Fwd:`, `AW:`, `SV:` …), then the parts an attacker varies per recipient collapsed — runs of two or more digits, UUIDs and long hex tokens all fold to a placeholder. "Invoice 88213" and "Invoice 88214" are one campaign, and a key that distinguished them would defeat the feature |
| **Link root domains** | The sorted, deduplicated set of *registrable* root domains the message links to, fingerprinted. Root domains rather than URLs, because a phishing kit gives every recipient a unique path or tracking parameter while the domain is what the attacker had to register. Sorting means link order, which varies with templating, cannot split one campaign in two |
| **Attachment hashes** | The set of attachment SHA-256s |

A message **joins an open campaign when at least two keys agree** with a
candidate. One key is too easy to hit by accident — two unrelated messages with
the same generic subject are not a campaign — and requiring three would miss real
campaigns that vary one dimension deliberately.

An **empty key never matches**. Two messages with no subject, or with no links,
are not evidence of anything, and treating empty as agreement would cluster the
whole tenant into one campaign.

!!! note "Body similarity is not currently a clustering key"
    Near-identical bodies do not group on their own. Two messages that differ
    only in wording, with different links and no attachments, will not cluster.
    That is the conservative failure and the deliberate one — the alternative
    collapses every body-less message into one cluster.

Candidates are considered newest first, bounded, and the first one reaching the
threshold wins. Joining an existing campaign always beats seeding a new one.

Campaigns close after **72 hours of silence**. Only open campaigns absorb new
members, so an attacker re-using a subject three months later starts a new
campaign rather than resurrecting an old one.

A campaign's verdict is the strongest verdict among its members.

## Working campaigns

```bash
limacharlie mailsec campaign list --min-members 3 --oid $OID
limacharlie mailsec campaign get <campaign_id> --oid $OID
```

Filters: `state` (`open`, `closed`), `verdict`, `min_members`, `since`/`until`,
all repeatable where it makes sense and keyset-paginated like every other list.

The detail view gives the campaign's span, its membership, its verdict and the
keys that bound its messages together. From a message, `campaign_id` is on the
index row; from a campaign, `message list --campaign-id` gives the members.

In the console, **Campaigns** has the list, the detail, and the sweep controls.

## Sweeping a campaign

A campaign-wide action applies a **per-message action** to every member:
`quarantine_message`, `trash_message` or `restore_message`. Three protections
apply, and none of them is optional.

### 1. Preview, then confirm

A sweep with no confirmation token **changes nothing**. It returns exactly what
it would do — the member ids, the distinct mailboxes affected, and the counts —
plus a `confirm` token.

```bash
# Preview. Nothing is touched.
limacharlie mailsec campaign action <campaign_id> \
  --action quarantine_message --oid $OID --output yaml
```

```yaml
preview: true
campaign_id: <campaign_id>
action: quarantine_message
member_count: 38
mailbox_count: 31
confirm: <token>
```

`mailbox_count` is the number that matters. "38 messages" and "31 people's
inboxes" feel very different, and only one of them is the real blast radius.

```bash
# Execute exactly the set the preview described.
limacharlie mailsec campaign action <campaign_id> \
  --action quarantine_message --confirm "<token>" --oid $OID
```

!!! warning "The token is derived from the member set, not from the campaign id"
    Passing the campaign id as `--confirm` is **refused**. The token is a
    function of the exact members the preview showed you, so a campaign that
    absorbed new messages while you were reading the preview fails the
    confirmation rather than sweeping a set nobody approved. Re-run the preview
    and confirm the current set.

### 2. A cap

A sweep refuses outright above **500 members** rather than asking again. An
operator confirming a four-thousand-message sweep from a dialog has not really
consented to four thousand mailboxes changing; that needs a person deciding.

### 3. The executor still decides

Every member goes through the same remediation path as a single-message action,
so `alert_only`, the audit row and idempotency all apply unchanged. A sweep is
many ordinary actions, never a bulk write that skips them.

Members are routed **per message**, so a campaign that spans a Microsoft 365
connection and a Google Workspace connection sweeps correctly across both.

### The result

```yaml
campaign_id: <campaign_id>
action: quarantine_message
attempted: 38
succeeded: 36
alert_only: 0
failed:
  <msg_uuid>: "<provider error>"
```

A sweep does **not** abort on the first error. Stopping halfway leaves a campaign
half-remediated, which is the worst of both states: the attacker still has reach
and the operator believes it is handled. Every member is attempted and every
failure is named.

Re-running a sweep is idempotent per message and action, so clicking twice does
not produce two audit rows claiming two quarantines.

## Permissions

Previewing needs `mailsec.act`, the same as executing — a preview reaches the
collector and enumerates members. Reading campaigns needs only `mailsec.get`.
