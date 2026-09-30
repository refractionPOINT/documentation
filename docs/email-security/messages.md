# Messages & Triage

--8<-- "includes/email-security-beta.md"

**Messages** is the queue: every message the product has seen, filtered down to
the ones that need a person. This page covers the queue, the drawer, the actions
and the audit trail they leave.

Where classification is available, the queue and drawer show the message's
apparent purpose, such as **Correspondence**, **Transactional**, or **Marketing**.
This is separate from its security verdict: a transactional message can still be
malicious. **Not classified** means no classification is stored; **Unknown** means
the classifier abstained. The drawer explains the reasons when present. Inspect
the `mail_type` object, including its classifier version, with
`limacharlie mailsec message get MESSAGE_UUID --output yaml --oid $OID`,
`mailsec message list --output yaml`, or an `analyze` result. See the
[purpose fields](rule-reference.md#mailtypeinfo) for API and rule paths; purpose is
not a message-list filter.

## The queue

Filtering is **entirely server-side** — every filter below narrows the query in
the backend, so a filtered page is a statement about your whole mail history, not
about the rows a browser happened to have loaded.

| Filter | Notes |
|---|---|
| `verdict` | Repeatable: `malicious`, `suspicious`, `graymail`, `benign`, `unknown` |
| `state` | Repeatable: `delivered`, `quarantined`, `trashed`, `restored`, `bannered`, `spam` |
| `direction` | Repeatable: `inbound`, `outbound`, `internal` |
| `lane` | `live` for ordinary incoming mail or `backfill` for the initial history walk; omit for either |
| `mailbox` | One protected mailbox address |
| `sender_email` | One sender address |
| `sender_root_domain` | One sender registrable domain |
| `campaign_id` | The members of one campaign |
| `link_domain` | Messages linking to this **registrable root** domain (`evil.example`, not `login.evil.example`) |
| `attachment_sha256` | Messages carrying an attachment with this hash |
| `user_reported` | Tri-state — see below |
| `min_score` | Messages scoring at least this much |
| `q` | Free-text over the message's subject and sender address, up to 512 characters. The subject is matched in both its raw and its normalized form, so a hit can be on text the row does not display. It is matched row by row rather than looked up, so it must be accompanied by something that bounds the read: a `since`, or one of `mailbox` / `sender_email` / `campaign_id` / `link_domain` / `attachment_sha256`, or a **single** `verdict`. On its own it is refused — see [Free text needs a window](#free-text-needs-a-window) |
| `since` / `until` | RFC3339 or unix seconds |

Repeatable filters **OR within a key and AND across keys**: `verdict=suspicious`
plus `verdict=malicious` plus `mailbox=cfo@corp.example` means "suspicious or
malicious, delivered to that mailbox".

The processing-lane filter is available on time-window, verdict, IOC-pivot and
`sender_root_domain` queries. It cannot be combined with `mailbox`,
`sender_email`, or `campaign_id` because those indexes do not carry the lane
dimension. The API refuses such a
combination with the typed, non-retryable `lane_unsupported` error and names the
conflicting dimension; the console clears and disables the lane control while
one of those filters is active.

```bash
limacharlie mailsec message list --verdict suspicious --verdict malicious \
  --mailbox cfo@corp.example --since "$(date -d '7 days ago' +%s)" --oid $OID
```

To inspect historical analysis separately:

```bash
limacharlie mailsec message list --lane backfill --limit 10 --oid "$OID" --output yaml
```

Historical messages are scored but do not trigger live-mail telemetry or
automatic responses; an empty action history on one is expected.

!!! warning "Tri-state booleans: absent is not `false`"
    Omitting `user_reported` means the dimension is *unconstrained*. Setting it
    to `false` selects mail **nobody reported**, which is a different and much
    larger set than "all mail".

### Free text needs a window

Most of the filters in the table above are a **lookup**: `mailbox`,
`sender_email`, `campaign_id`, `link_domain`, `attachment_sha256` and a *single*
`verdict` each pick the read index, so the backend seeks straight to the matching
rows. `q` is not one of them. It is matched literally and case-insensitively
against each candidate row's sender address and subject as the index is walked,
so its cost follows how much of the index gets read rather than how many rows
come back — and the most expensive `q` is the one that matches **nothing**, because
nothing fills the page and the walk runs to the end of your retention.

So a `q` on its own is refused, and it has to name something that bounds the
walk:

- a **`since`** — an `until` alone does not count, because the walk is
  newest-first, so `until` moves where it starts and `since` is where it stops;
- or one of **`mailbox`**, **`sender_email`**, **`campaign_id`**,
  **`link_domain`**, **`attachment_sha256`**;
- or a **single** `verdict`. Two or more verdicts is not a lookup either, so it
  does not count.

`state`, `direction`, `user_reported`, `min_score` and `sender_root_domain`
narrow the *answer* rather than the *scan*, so they do not satisfy the
requirement.

```http
# refused
GET /v1/mailsec/$OID/messages?q=invoice

# bounded by time
GET /v1/mailsec/$OID/messages?q=invoice&since=1757116800

# bounded by a lookup, any time
GET /v1/mailsec/$OID/messages?q=invoice&mailbox=cfo@corp.example
```

The subject is matched in two forms: as received, and in the normalized form
campaign clustering derives from it — reply and forward prefixes stripped, digit
runs collapsed. A row can therefore match on a subject that is not the one shown
in the result.

`q` is also capped at **512 characters**. A search bounded only by time is
counted against a per-organization
[read budget](api-reference.md#read-budgets); one carrying a `mailbox`,
`sender_email`, `campaign_id`, `link_domain` or `attachment_sha256` is an index
lookup and is not counted at all. A single `verdict` satisfies the requirement
above but does **not** exempt the search: the verdict index is keyed by verdict
and then time, so `verdict=benign` seeks into what is, for most organizations,
all of their mail.

In the web console the search box supplies the bound for you: searching without
any other filter searches everything retained, and the result summary says so.

### The two IOC pivots

`link_domain` and `attachment_sha256` are the incident-response pivots, and they
are the reason the queue is not just a mailbox view. Given one confirmed phish,
they answer **"who else received this"** across every protected mailbox — which
is the question that decides whether you are handling one message or an incident.

```bash
limacharlie mailsec message list --link-domain evil.example --oid $OID
limacharlie mailsec message list --attachment-sha256 <sha256> --oid $OID
```

### Pagination

Pages are keyset-paginated. `next_cursor` is opaque and is passed back verbatim;
an empty one is the last page.

A message cursor is **bound to the complete filter set that minted it**: the
token carries the chosen read index and a digest of your organization, the sort
order and *every* filter — `q`, verdict, state, direction, lane, mailbox,
sender address, sender root domain, campaign, user-reported, score floor, time
window, link domain and attachment hash — so changing any of them mid-walk fails
the next page (`400`, `error_code: cursor_filter_changed`, `restart_walk: true`)
rather than silently resuming at the previous search's position. Filter *values*
are not readable from the token; it is a hash, not a serialization. Restart the
walk from the first page instead; a cursor minted before this binding existed is
refused the same way once. A token that is structurally invalid — truncated,
edited, from another endpoint — answers `error_code: cursor_malformed` with the
same `restart_walk: true`, and the repair is identical.

### Retention

The searchable message index keeps **35 days** by default; flagged messages and
their stored evidence are kept up to **400 days**. Both are *maxima* you can
lower — `message_days` and `flagged_days` in
[`mailsec_policy/retention`](policy.md#retention) — and data past whichever
horizon you set is deleted rather than merely hidden. A miss on an older id is a
normal outcome and returns a null message rather than an error.

## The drawer

Opening a row shows what the engine decided and why:

- **Why this verdict** — the top signals with their weights, from the same
  `top_signals` the API returns.
- **The message itself** — a sanitized rendering plus the parsed model: sender
  and recipients, authentication results, the links table with display/href
  mismatches highlighted, attachments and their explosion tree, and the thread
  segmentation.
- **The sender profile card** — this organization's history with the sender.
- **The action timeline** — every audited action on this message.
- **Remediation controls**, driven by the message's current placement: the
  actions offered are the ones that make sense for where the message actually is.

### Which model you are looking at

The detail response labels its source, because the two are not equivalent:

| `mdm_source` | What it is |
|---|---|
| `stored` | The model the collector actually judged with — the enrichments it resolved at ingest (sender prevalence, lookalike distances, link features, domain age) and the verdict as stamped |
| `eml_reparse` | Today's parser reading the original bytes. The same message, a different parse, and **no enrichments at all** |

`stored` is served when it exists; `eml_reparse` is the fallback for mail
ingested before stored models existed. An analyst deciding whether the engine was
right needs to know which one they are reading, so the field is always present.

Neither requires a justification. The model is the product's own structured view;
the *original bytes* are what is gated.

### Which lane judged it

`judged_via` says whether this message's verdict came from live ingestion or
from the connection's historical backfill.

| `judged_via` | What it means |
|---|---|
| `live` | An ordinary ingest. The `EMAIL_MESSAGE` and `EMAIL_VERDICT` events shipped, and any policy automation that matched has run |
| `backfill` | The message was already in the mailbox when the connection was made. It is judged with the same rules, and **nothing was emitted and nothing acted on it** |
| absent / `null` | The read did not carry the field. Treat it as unknown — never as `live` |

The distinction matters on exactly one screen, and it is worth stating plainly:
a backfilled message can show a `malicious` verdict beside an empty action
timeline and no telemetry. That is the lane working as designed, not a broken
connection and not somebody suppressing an alert. See
[the ingest pipeline](pipeline.md#the-historical-backfill).

### Similar messages

`GET /messages/{id}/similar` (`limacharlie mailsec message similar <msg_uuid>`)
returns recent messages sharing at least one
[clustering key](campaigns.md#how-clustering-works) with this one, each row
carrying the `matched_keys` that matched. These are **candidates, not a
cluster** — deciding that two messages are the same attack belongs to the
clustering engine. The response echoes the lookback window, because "no similar
messages" only means something alongside the window it looked at.

## Actions

Six typed actions apply to a single message. Each is idempotent, performed at the
provider, and audited.

| Action | Effect |
|---|---|
| `quarantine_message` | Out of the inbox into a product-owned quarantine location, restorable. On Microsoft 365 the location is a hidden folder, so the user does not see the message. On Google Workspace it is a visible `LC Quarantine` label, so the user can still find the message under that label |
| `trash_message` | To the provider's recoverable trash |
| `move_to_spam` | To the provider's junk/spam location |
| `restore_message` | Back to where it was before we moved it, falling back to the Inbox when that is unknown |
| `banner_message` | Prepend the organization's warning banner. Its wording comes from the `banners` [policy record](policy.md#banners) and is escaped into a fixed template — no caller supplies HTML |
| `unbanner_message` | Remove it |

The per-provider mechanics differ and are documented in
[Connecting Providers](providers.md#capability-differences-between-providers).

!!! warning "Quarantine is hidden from the user on Microsoft 365 only"
    On Microsoft 365 the message moves to a hidden `LC Quarantine` folder that
    the user does not see in Outlook. On Google Workspace, quarantine removes
    the message from the inbox and adds an `LC Quarantine` label that is shown
    in the label list and in message lists, so the user can open the label and
    read the message. If your process assumes the recipient cannot reach a
    quarantined message, that holds for Microsoft 365 mailboxes only. On
    Workspace, treat quarantine as "out of the inbox", and use `trash_message`
    if you need the message out of the user's normal view.

```bash
limacharlie mailsec message action <msg_uuid> \
  --action quarantine_message --reason "confirmed credential phish" --oid $OID
```

Actions require `mailsec.act`.

To act on many messages at once — a filtered page of this queue, or a selection
you built elsewhere — see [Bulk Remediation](remediation.md). It is the same
executor and the same audit trail, with a preview and a confirmation over the set
you named.

### Outcomes are reported honestly

| `result` | Meaning |
|---|---|
| `ok` | The provider was changed |
| `skipped` | The desired state already held, so nothing was written. Recording this as success would make the audit claim a provider write that never happened |
| `alert_only` | The action was **decided and deliberately not performed**, because the organization is not in enforce mode. Not an error |
| `failed` | The provider refused or errored; `error` carries the reason |
| `pending` | In flight |

!!! note "`unbanner_message` does not change placement"
    A message's `state` is a **placement**. Bannering is a modification, so a
    message that was quarantined and then un-bannered is still quarantined —
    writing `delivered` there would move it back in the UI without moving it at
    the provider.

### Idempotency

Repeating an action collapses onto the existing attempt, so a redelivery, a
double-click or a rule firing twice on one event is a no-op rather than two
quarantines. To deliberately act *again* — re-running a quarantine after a
provider outage — pass a new `attempt` token.

### Enforcement

In an alert-only organization, actions from **every source**, including analysts,
are recorded but withheld. The response reports `force_required: true`.
To perform that action deliberately, repeat the request with JSON `force: true`,
use the console's explicit override confirmation, or pass `--force` in the CLI:

```bash
limacharlie mailsec message action <msg_uuid> --action quarantine_message --force
```

Only a JSON boolean `true` overrides the mode; strings such as `"true"` do not.
The override applies to this action, does not enable organization-wide automation,
and is recorded separately from the withheld attempt in the audit trail. It
still requires `mailsec.act` and the provider's required capabilities.

Automated actions are governed by [policy](policy.md#automations).

## The audit trail

Every action writes an audit row — including failures and skips, because
"quarantined 412 of 418, 6 failed" is only answerable if the six are recorded —
and emits an `EMAIL_ACTION` event.

| Field | Meaning |
|---|---|
| `action_id` | The row's identity and its idempotency key |
| `action`, `ts`, `result`, `error` | What was attempted, when, and what happened |
| `actor` | **Who asked** — stamped by the server from the caller's authenticated claims. A request body cannot supply it |
| `source` | `analyst`, `automation`, `ai`, `api` or `dr` |
| `provider` | Which mail tenant it hit |

The per-message timeline is deliberately narrow and does **not** carry the action's
request payload. Expand one row to read it:

```bash
limacharlie mailsec action get <action_id> --oid $OID --output yaml
```

A `null` request on a timeline row means **"not read"**, never "no parameters
recorded" — an auditor asking whether a justification exists must expand the row
rather than infer absence from the list.

## Downloading the original message

This is a privileged read of a person's mail, and it is gated separately from the
rest of the product. It requires **both** `mailsec.get` and `mailsec.get.eml`,
plus a justification.

```bash
limacharlie mailsec message eml <msg_uuid> \
  --justification "INC-4471, user reported credential harvest" \
  --out-file suspect.eml --oid $OID
```

- The justification is **required**. A blank or whitespace-only reason is
  refused.
- It is recorded against your authenticated identity in the organization's action
  audit and retained for 400 days. **A failed attempt is recorded too.**
- It is stored verbatim. The backend enforces a minimum and a maximum length, and
  refuses an over-long reason rather than truncating — silently clipping the
  record the gate exists to produce would corrupt it.
- Raw copies expire 35 days after delivery (longer for flagged messages), after
  which this returns a typed expiry error while the index row stays readable.

Read a justification back with `mailsec action get <action_id>`.

## Who read a message: the content-read audit event

Reading a message's content is recorded, not only downloading it. Each time
someone reads the body of a message, Email Security writes one
**`mailsec_message_content_read`** event to the organization's
[audit log](../7-administration/access/user-access.md#4-what-access-related-changes-have-been-made-and-by-whom),
the same log that records configuration and user changes across the platform. It
answers "who read this person's mail", which the action audit above does not: that
trail records what was *done* to a message and who took the original bytes out, not
who looked at the text.

This is an audit log event, not an `EMAIL_*` event. It is not emitted on the mail
connection's sensor, it does not reach D&R rules as a sensor event, and it is
not part of the message index. You read it through the audit log, and you can
forward the whole `audit` stream with an
[Output](../5-integrations/outputs/stream-structures.md#3-audit-stream-structure).

### What counts as a read

There is one event type, and the `content` field says which kind of content was read.

| `content` | What was served | Needs |
|---|---|---|
| `mdm` | The parsed message, including its HTML and plain-text body. This is what the drawer shows, and what `mailsec message get` and the matching API route return | `mailsec.get` |
| `eml` | The original message bytes, through the [justified download](#downloading-the-original-message) | `mailsec.get` and `mailsec.get.eml`, plus a justification |

Only a read that actually served content is recorded. A message whose raw copy has
expired, an unknown `msg_uuid` and a refused download serve nothing and write
nothing here. A refused download is still recorded in the action audit and as an
`EMAIL_ACTION` event, as before.

### Fields

| Field | Meaning |
|---|---|
| `etype` | Always `mailsec_message_content_read` |
| `ident` | Who read it: the authenticated identity the request ran as. `origin` carries the same value |
| `time`, `ts` | When the read was recorded |
| `msg` | A human-readable sentence naming the message and the mailbox |
| `entity.msg_uuid` | The message that was read |
| `entity.mailbox_address` | The mailbox the message was read from |
| `mtd.content` | `mdm` or `eml` |
| `mtd.actor_kind` | The kind of credential behind `ident`: `user` for an interactive session, `user_api_key` for a user's personal API key, `org_api_key` for an organization API key, or `unknown` when the request carried no identity |
| `mtd.provider` | `m365` or `gworkspace`, as indexed for the message |
| `mtd.verdict` | The message's verdict at the time of the read |
| `mtd.mdm_source` | `mdm` reads only: `stored` for the model the engine judged with, `eml_reparse` for a fresh parse of the raw copy. See [Which model you are looking at](#which-model-you-are-looking-at) |
| `mtd.bytes` | `eml` reads only: the size of the download |
| `mtd.justification` | `eml` reads only: the justification that was supplied |

The event never carries the subject, the sender or any of the message body. A
record of who read mail must not become a second copy of it in a stream you may
forward to a SIEM with its own retention. `ident` and `mtd.actor_kind` are what
tell an analyst's console session apart from an automation or an
[AI triage](ai-triage.md) agent working through an API key.

### Finding the events

Reading the audit log needs the `audit.get` permission. In the web console, open
**Audit Logs** in the organization and filter on the event type. From the CLI:

```bash
limacharlie audit list --event-type mailsec_message_content_read \
  --start $(date -d '7 days ago' +%s) --end $(date +%s) --oid $OID
```

An entry for a person reading a message in the console looks like this:

```json
{
  "oid": "<your org id>",
  "etype": "mailsec_message_content_read",
  "msg": "read the parsed content of message 4f0c2b1e-9d7a-4c55-8a3e-6b1f2d9e7a10 in mailbox alice@example.com",
  "ident": "analyst@example.com",
  "origin": "analyst@example.com",
  "time": 1790000000000,
  "entity": {
    "msg_uuid": "4f0c2b1e-9d7a-4c55-8a3e-6b1f2d9e7a10",
    "mailbox_address": "alice@example.com"
  },
  "mtd": {
    "content": "mdm",
    "actor_kind": "user",
    "provider": "m365",
    "verdict": "suspicious",
    "mdm_source": "stored"
  }
}
```

A download has `content: eml` and adds `bytes` and `justification` to `mtd`.

### What to rely on

- **One event per reader, message and kind, per hour.** The drawer re-fetches the
  message on tab switches, and several screens open the same drawer, so recording
  every request would report one analyst reading one message ten times. A second
  read of the same message by the same identity inside the hour is not recorded
  again. A different identity, including the same person through a personal API
  key, is a different reader. A download with a different justification is
  recorded separately, and so is an `eml` read after an `mdm` read of the same
  message. This limits how often the event is written and never limits access:
  nothing is refused because it was already recorded.
- **The event is best effort.** If the audit log cannot be written at that moment,
  the read is still served and the gap is recorded in the service's own logs. The
  drawer must stay usable while the audit service restarts, so a failed audit write
  does not block an `mdm` read.
- **A download fails closed, on the action audit.** This is separate from the event
  above. Before any byte of the original message is read, its record in the action
  audit must be written. If it cannot be, the download is refused and recorded as
  `refused_reason: audit_write_failed`; nothing is served. So a raw download never
  happens without an audit record, even if the `mailsec_message_content_read` event
  for it could not be written.

## Sender profiles

```bash
limacharlie mailsec sender get cfo@corp.example --oid $OID
limacharlie mailsec sender get domain:corp.example --oid $OID
```

A key with no profile means **no history at all**, and the response says so
explicitly rather than returning a zeroed profile that would read as a
known-but-quiet sender. Keys are lowercased, and a bare address or domain is
resolved for you.
