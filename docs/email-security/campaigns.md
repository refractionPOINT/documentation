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
| **Body similarity** | A fuzzy hash (TLSH) of the message body, normalized first — see [Body similarity](#body-similarity) |

A message **joins an open campaign when at least two keys agree** with a
candidate. One key is too easy to hit by accident — two unrelated messages with
the same generic subject are not a campaign — and requiring three would miss real
campaigns that vary one dimension deliberately.

An **empty key never matches**. Two messages with no subject, or with no links,
are not evidence of anything, and treating empty as agreement would cluster the
whole tenant into one campaign.

Candidates are considered newest first, bounded, and the first one reaching the
threshold wins. Joining an existing campaign always beats seeding a new one.

## Body similarity

The first three keys are all things an attacker can randomize. A kit that gives
every recipient a unique subject line and a unique tracking path on every link
defeats all three and sends one attack that looks like forty unrelated messages.

What such a kit cannot randomize is the pitch. The body has to read the same to
every victim, because the body **is** the attack. So the fourth key is a fuzzy
hash of the body — one that gets *closer* the more two texts have in common,
rather than changing completely when one character does.

### The body is normalized first

Hashing the raw body would key on exactly the bytes a kit varies. Before hashing,
the body is reduced to what it actually says:

- the **visible** text is used — text hidden from the reader (zero-height divs,
  white-on-white) is dropped, because planting per-recipient noise there is the
  oldest way to defeat a similarity hash;
- **links** collapse to their scheme and host: the path, query and fragment are
  where the victim's identifier lives, while the host is what the attacker had to
  register;
- **email addresses** collapse to a placeholder — the greeting and the "this was
  sent to …" footer are otherwise a per-recipient signature;
- the **salutation** and the **recipient's own name** collapse, so "Dear Riley,"
  and "Dear Morgan," are the same sentence;
- long **digit, hex and opaque tokens** collapse — invoice numbers, ticket ids,
  unsubscribe and tracking tokens;
- whitespace collapses last.

How much this matters, measured rather than claimed: two copies of one 630-byte
phishing body differing only in the recipient's name and the tracking parameters
on its link are **86 apart before normalization and 0 apart after it**. The
default join distance is 30, so without the normalization this key would not work
at the length of an ordinary email.

### The threshold

Two bodies count as the same body at a **distance of 30 or less**, which is a
policy knob (`clustering` — see the [Policy Reference](policy.md#clustering)).

30 is measured. Across a 404-message corpus of ordinary business mail —
newsletters, invoices, calendar invites, internal notices — the **closest pair of
unrelated messages is 39 apart**, and at 30 the body key produces zero agreements
across all 71,631 pairs. The policy ceiling is 35, below that closest pair on
purpose: a setting above it is one you cannot have measured, and what it buys is
a campaign-wide quarantine reaching mail that was never part of the attack.

!!! warning "It is closer to all-or-nothing than a tolerance"
    At the length of ordinary email, TLSH is very sensitive: two bodies whose
    normalized text is byte-identical score **0**, and a single per-recipient word
    the normalization could not identify — a name in a footer, an amount, a company
    — has been measured at **100**, well past the ceiling. So the threshold is not a
    slider that trades recall for precision in small steps. What it buys is the mass
    case: one pitch, randomized subjects and links. A kit that rewrites a word of
    prose per victim will not group, and that failure is entirely on the recall
    side — it can never merge unrelated mail.

### It still takes two keys

Body similarity does **not** join a campaign on its own. It is the strongest of
the four keys and it is still one key, and a 39-point margin is a margin rather
than a wall — two form letters from different vendors can read alike. What the
key changes is not the threshold but how often it is *reachable*: a message whose
subject and links were randomized now has a second key to agree on.

### Why a message did or did not group

Every message records the keys that agreed when it joined, and the drawer and the
API return them:

```bash
limacharlie mailsec message get <msg_uuid> --oid $OID --output yaml
```

```yaml
campaign_id: <campaign_id>
cluster_reason:
  - subject
  - body_tlsh
body_tlsh: T1A1B2...
```

`cluster_reason` is the answer to the question a campaign-wide quarantine
provokes: *why was my mail in that group?*

`body_tlsh` is the digest itself. It is shareable — it is the standard TLSH form,
so it pastes into other tools — and the "similar messages" view ranges on it:

```bash
limacharlie mailsec message similar <msg_uuid> --oid $OID --output yaml
```

Every candidate carries `matched_keys` and, when both messages have a digest, a
`body_distance` next to the threshold your policy set. That view returns
*candidates*, not campaign members: the "two keys agree" decision belongs to the
clustering engine, and a list presented as "similar" without saying how similar
would be an unexplainable claim.

### The window is wider for bodies

The other three keys look back 72 hours, the open-campaign window. Body
similarity looks back **seven days**, because the attack this key exists to catch
is also the one that trickles: a kit sending a hundred distinct-looking messages
over five days is one campaign, and a 72-hour horizon would split it into two
nobody would ever connect. A body-similar message arriving days later **reopens**
the campaign, because a campaign still receiving mail is still live.

### Messages with no usable body

A body under 50 bytes of normalized text — "ok, thanks" — or one with too little
variety to characterize produces **no digest**, and `body_tlsh` is absent. That is
a fact about the message, not a missing value: an empty key never matches, which
is what stops every short message clustering with every other one.

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
