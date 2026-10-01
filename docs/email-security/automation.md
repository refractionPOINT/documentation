# Events & Automation

--8<-- "includes/email-security-beta.md"

Email Security is not a side-car product with its own event bus. Everything it
sees becomes ordinary LimaCharlie telemetry, in the same lake as your endpoint,
cloud and identity data — which is what makes "a phish was delivered, and then
that user's endpoint ran a new binary" one rule instead of two products and a
spreadsheet.

## The sensors

Each protected mailbox appears as its own sensor on platform `email`, keyed by
the provider's stable mailbox id and named by its normalized primary address.
Mailbox-scoped events carry `mailbox: {id, address, upn}`; `upn` is present when
known and can differ from the address on Microsoft 365. Events without a mailbox
use the connection's sensor (`mailsec-<connection name>`). The `email` platform
does not count against the sensor quota. Watch coverage and `EMAIL_INGEST_ERROR`
to assess ingestion health; the connection sensor's online state reflects only
its own events.

## The events

| Event | Emitted when |
|---|---|
| `EMAIL_MESSAGE` | Once per message, at ingest. Carries the whole parsed model — headers, sender, recipients, body, links, attachments, authentication, hops — plus the enrichments and the verdict. It is the record that this mail arrived |
| `EMAIL_VERDICT` | On **every** verdict decision: the rule pack's own, at ingest right after the `EMAIL_MESSAGE` (`revision/seq: 0`, `revision/mode: auto`), and then once per override afterwards (`seq: 1…`, mode `analyst`, `ai` or `detonation`) |
| `EMAIL_ACTION` | On every remediation outcome, including failures and skips, **and on every raw-message download** (`action: get_eml`), served or refused. Who asked, what was attempted, what happened |
| `EMAIL_USER_REPORT` | When a message reaches the abuse mailbox and becomes a report |
| `EMAIL_INGEST_ERROR` | When a message could not be fetched or processed. Coverage honesty: failures are visible, never silent |

`EMAIL_MESSAGE` is emitted once and is immutable. When a verdict changes, the
original event is never rewritten — a new `EMAIL_VERDICT` is emitted instead, so
the verdict history is the sequence of those events and a replay can reconstruct
what was known at any point in time.

### `EMAIL_VERDICT`

The body carries the message's identity plus one `revision` block, and it is the
same shape whichever decision it reports — which is the point: one rule reads all
of them.

| Path | |
|---|---|
| `event/msg_uuid` | The durable handle every typed action takes. A provider message id is folder-scoped and stops resolving the moment the message is quarantined; this does not |
| `event/mailbox/address`, `event/provider` | Whose mail, from where |
| `event/internet_message_id` | The cross-mailbox join key: one message sent to forty people is forty `msg_uuid`s and one of these |
| `event/sender_email`, `event/sender_root_domain`, `event/subject` | Enough to match on without a lookup |
| `event/ts` | The message's delivery time. The **event's own** timestamp is when the decision was made, so a hunt can window on either |
| `event/campaign_id` | The campaign, if the message clustered into one |
| `event/campaign_joined_late` | Present and `true` only when this event exists *because* the campaign above was identified after the message had already been delivered and reported. See [A message that joins a campaign late](#a-message-that-joins-a-campaign-late) |
| `event/cluster_reason` | The cluster keys that agreed — why this message is in that campaign. Carried on a late join, which is the event the question gets asked about |
| `event/revision/seq` | `0` for the rule pack's verdict, `1…` for each override |
| `event/revision/mode` | `auto`, `analyst`, `ai` or `detonation` |
| `event/revision/verdict`, `event/revision/score` | The decision |
| `event/revision/rationale` | The reasons, strongest first. For an override these are what the analyst or agent wrote; for `seq 0` they are the names of the signals that fired — so it is **absent** on a benign message that matched nothing, which is the common case |
| `event/revision/top_signals`, `event/revision/engine_version` | `seq 0` only — the rule ids that fired and the engine that decided (rule-pack version plus the library build it ran with). An override has neither: nothing *matched*, somebody decided |
| `event/revision/actor` | Who decided. Empty on `seq 0`: the rule pack is not a person, and `engine_version` is what identifies it |
| `event/revision/prior` | What the override displaced — verdict, score, mode and engine version. On `seq 0` it is present but empty (`verdict: ""`, `score: 0`), because the engine's first call displaced nothing — so match on `revision/seq` or `revision/mode` to tell the two apart, not on `prior` |

The MDM is deliberately *not* repeated here: it is already in the immutable
`EMAIL_MESSAGE`, and copying it into every verdict change would multiply a year
of telemetry by how often people change their minds.

### A message that joins a campaign late

Clustering runs while a message is being ingested, so two copies of one attack
that arrive in the same instant each look for a campaign-mate before the other
has been written down — and both are stored attributed to nothing. When a
campaign one of them belongs to is identified afterwards, its membership is
recorded and an `EMAIL_VERDICT` is emitted carrying
**`campaign_joined_late: true`**.

```yaml
# Detect: mail we already delivered has been shown to be part of a campaign.
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_VERDICT
  - op: is
    path: event/campaign_joined_late
    value: true
```

It is a flag on the existing event rather than an event type of its own,
deliberately: a rule already written against `EMAIL_VERDICT` keeps working and
simply starts seeing the campaign, which is the one fact a campaign-wide response
needs.

**The `revision` block on this event is a restatement, not a new decision.**
Nothing was re-judged — the verdict is exactly what it was — so:

| Path | On a late join |
|---|---|
| `revision/seq` | The message's *current* revision sequence: `0` when the engine's verdict has never been overridden, which is the usual case, and `1…` when it has. A consumer de-duplicating on `(msg_uuid, seq)` therefore reads this as a decision it already holds, now carrying a campaign |
| `revision/decided_at` | The clock of the decision being restated. On a message whose engine verdict was never overridden — the usual case — that is when the **join** happened, because the join is the only thing this event reports as new. On an already-overridden message it is the timestamp of the override being restated — the message's **current** one, which is the original when there has only ever been one — because restating an analyst's decision under a clock they did not choose would be worse. So match late joins on `campaign_joined_late`, never on a time window |
| `revision/verdict`, `revision/mode`, `revision/actor` | Whatever the message already carried. An overridden message restates its analyst's or agent's decision verbatim, attribution included |

The original `EMAIL_MESSAGE` is never rewritten, here as everywhere: it stands as
the record of what was known at ingest, and this is the record of what was learned
afterwards.

!!! tip "Why you want to act on this"
    A campaign-wide quarantine reaches the members the product knows about. A
    message that was never attributed to its campaign is one the sweep does not
    touch and one the campaign's member count does not include — so this event is
    how a response you have already run learns that it missed something.

    Match on the flag rather than on a time window, per the `decided_at` note
    above: on an already-overridden message the event carries the original
    decision's timestamp, so a rule scoped to "the last hour" would miss it.

!!! warning "It roughly doubles your mail event volume"
    `EMAIL_VERDICT` at `seq 0` is emitted for **every** ingested message, not only
    for flagged ones, so a protected mailbox now produces about two events per
    message instead of one. These are ordinary telemetry: they are evaluated by
    your D&R rules and they land in your retention like any other event. The
    bodies are small — identity plus a verdict, never the parsed message — so the
    byte volume moves far less than the count.

!!! info "Everything the rule needs is in the event"
    The verdict, the top signals and the enrichments the pipeline resolved are
    all *in* `EMAIL_MESSAGE`. A rule never has to call back for enrichment, and a
    replay of the event sees exactly what the pipeline saw.

Events arrive on the **default D&R target**, so a rule matching them needs no
`target:` line.

## Acting on mail from a D&R rule

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_MESSAGE
  - op: is
    path: event/verdict/verdict
    value: malicious
  - op: is
    path: event/direction
    value: inbound
```

```yaml
# Respond
- action: report
  name: email-malicious-delivered
- action: extension request
  extension name: ext-email-security
  extension action: quarantine_message
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
```

The typed actions available to `extension request` are the same six the console
and the CLI use: `quarantine_message`, `trash_message`, `move_to_spam`,
`restore_message`, `banner_message`, `unbanner_message`. They route to the same
executor, so the organization's `alert_only` / `enforce` mode, the audit row and
idempotency all apply unchanged — there is exactly one remediation path in this
product.

A rule does not supply banner HTML: `banner_message` uses the organization's own
banner from its [`banners` policy record](policy.md#banners) (title, colour,
logo and the wording for the message's verdict), rendered server-side into a
fixed escaped template. A rule may add one plain-text `text` (at most 512
characters, no `<` or `>`) that replaces the wording for that banner only, for
example to name the reason the rule fired:

```yaml
respond:
  - action: extension request
    extension name: ext-email-security
    extension action: banner_message
    extension request:
      msg_uuid: '{{ .event.msg_uuid }}'
      text: "Payment details changed in this message. Confirm by phone before paying."
```

A `text` that contains markup, control characters or is over 512 characters is
**dropped** and the banner goes out with the organization's own wording, because
a rule's values are usually templated from the message and a sender must not be
able to decide whether the warning appears. `text` on any action other than
`banner_message` is ignored. Because `text` replaces the organization's
wording, avoid templating sender-controlled fields (the display name, the
subject) into it: whatever you put there is shown to the recipient as part of
the warning. Automated bannering also requires
`enabled` on the [`banners` record](policy.md#banners); without it a rule's
`banner_message` is decided and audited but the mailbox is not touched
(`alert_only`). Bannering asked for by a person — console, API, CLI — is not
gated by that switch.

Actions dispatched this way are attributed with `source: dr` in the audit trail.

!!! tip "Which seat should this rule sit in?"
    A rule that should **change the verdict** belongs in `dr-mail` as a
    `pre_verdict` signal — see [Custom Rules](custom-rules.md). A rule that
    should **do something once the verdict exists** can sit in either seat: in
    `dr-mail` as `post_verdict` if it only needs mail actions, or here as an
    ordinary D&R rule if it needs the platform's full response arsenal, Outputs,
    Cases, or correlation with non-mail telemetry.

## Reacting to a user report

```yaml
# Detect
op: is
path: routing/event_type
value: EMAIL_USER_REPORT
```

```yaml
# Respond
- action: report
  name: user-reported-phish
  priority: 3
```

From there the detection flows into Cases, Outputs and everything else that
consumes detections. A report is the highest-signal thing your users will ever
hand you, so treating it as a first-class detection is usually right.

## Counting events per mailbox or per user

A rule that fires on one event is often not what you want. "One malicious message
landed in a mailbox" is routine; "the same mailbox received five in an hour" is an
attack on a person. LimaCharlie's D&R [suppression](../8-reference/response-actions.md#suppression)
does the counting, and Email Security events carry the identity to count by, so no
mail-specific feature is needed.

The pattern is a `report` action whose suppression is **global** and whose `keys`
include the mailbox or user. Global means the counter is shared across the
organization, so it is scoped by the key alone. The action is skipped until the
count reaches `min_count`, and then fires up to `max_count` times in the `period`.
Setting both to the same number fires once, on the Nth event, and stays quiet for
the rest of the window.

| Parameter | Use for per-user counters |
|---|---|
| `is_global` | `true`. The counter is organization-wide and the key decides what is counted together |
| `keys` | A constant label, so two rules never share a counter, then the field to count by, for example `'{{ .event.mailbox.address }}'` |
| `min_count`, `max_count` | The threshold. Set both to `N` to fire once when the Nth event arrives |
| `period` | The window: `s`, `m` or `h`, from 1 second to 720 hours |

The window is fixed, not sliding: it starts at the first counted event for a key and
the counter resets when it expires. See the platform's
[Behavioral Detection](../3-detection-response/behavioral-detection.md) page for the
full set of patterns and its limitations.

The field to count by depends on the event:

| Event | Field | Holds |
|---|---|---|
| Any event about a mailbox (`EMAIL_MESSAGE`, `EMAIL_VERDICT`, `EMAIL_ACTION`, and the other mailbox-scoped events) | `event/mailbox/address` (template `{{ .event.mailbox.address }}`) | The protected mailbox the event is about. The same `mailbox` object also carries `id` (the provider's stable handle) and `upn` (the sign-in name, which can differ from the address on Microsoft 365), so `{{ .event.mailbox.upn }}` can key a counter by sign-in identity |
| `EMAIL_USER_REPORT` | `event/reporter` (template `{{ .event.reporter }}`) | The address that sent the report to the abuse mailbox, or `unknown` when the report had no usable sender. Its `mailbox` is the abuse mailbox the report arrived in, not the person who reported, so count reports per person with `reporter` |

### Example: five malicious messages to one mailbox in an hour

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_MESSAGE
  - op: is
    path: event/verdict/verdict
    value: malicious
  - op: is
    path: event/direction
    value: inbound
```

```yaml
# Respond
- action: report
  name: email-mailbox-malicious-burst
  priority: 3
  suppression:
    is_global: true
    min_count: 5
    max_count: 5
    period: 1h
    keys:
      - 'email-malicious-per-mailbox'
      - '{{ .event.mailbox.address }}'
```

The detection fires once, when a mailbox receives its fifth malicious inbound
message inside the hour, and carries the triggering `EMAIL_MESSAGE` so the
responder can see the mailbox and the message. It counts the verdict the rule pack
gave at ingest. A message that only becomes malicious later, through an analyst, AI
or detonation revision, arrives as an `EMAIL_VERDICT` and is not counted by this
rule.

### Example: three user reports from one person in a day

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_USER_REPORT
  - op: exists
    path: event/automated_sender
    not: true
```

```yaml
# Respond
- action: report
  name: email-reporter-repeat
  priority: 2
  suppression:
    is_global: true
    min_count: 3
    max_count: 3
    period: 24h
    keys:
      - 'email-reports-per-reporter'
      - '{{ .event.reporter }}'
```

`automated_sender` is present, and `true`, only on reports that came from a
machine, so the second condition leaves those out of the count. A person who
reports three messages in a day is either being targeted or is the most alert
member of your staff, and in both cases an analyst wants to know.

!!! tip "Chain a counter onto a detection"
    The same suppression can count detections instead of events, using the
    `target: detection` chaining described in
    [Behavioral Detection](../3-detection-response/behavioral-detection.md#cardinality-detection).
    That is how you count *distinct* values, for example the number of different
    senders that hit one mailbox, rather than the number of events.

## Watching your own coverage

`EMAIL_INGEST_ERROR` is the event to alert on. A mail security product that
quietly stops seeing a mailbox is worse than one that is visibly down, so
failures are emitted rather than swallowed:

```yaml
op: is
path: routing/event_type
value: EMAIL_INGEST_ERROR
```

Pair it with the `coverage` call, which reports mailboxes in `error`, the
parse-degradation rate and the emission backlog. See
[Getting Started](getting-started.md#6-watch-coverage-fill-in).

Poll it **without a window**. With no `since`/`until`/`window_days` the answer is
eligible for a short-lived server-side memo and is **not** counted against the
[read budget](api-reference.md#read-budgets); naming a window recomputes the
period on every call and is counted. The memo lives 60 seconds, so polling faster
than once a minute buys you nothing — and a once-a-minute poll lands on the
expiry most times, so it is not free either. It is simply not budgeted.

## Querying mail with LCQL

The **Email Security → Hunt** screen runs ordinary LCQL search over
`EMAIL_MESSAGE` events under your own organization permissions. Its guided
filters can also be opened in the Query Console. Other emitted `EMAIL_*` events
are searchable in the Query Console and through `limacharlie search`.

**Body contains** matches a case-insensitive phrase in any of the message's
current authored thread, visible HTML text or plain-text part. The phrase is
limited to 256 characters and cannot contain control characters or line breaks.
It searches the body text retained in the event, subject to ingestion limits;
it does not fetch the original EML. Narrow the time window and other filters
before searching bodies, because the search reads message text across the window.

Before running, Hunt estimates the search cost. Small priced searches can start
immediately; larger searches ask you to confirm. If the estimate is unavailable
or unpriced, Hunt says so and asks before running, rather than treating the
search as free. The estimate is a guide; the final charge can differ.

These searches cover retained telemetry, independently of the Email Security
message index and raw-message retention. They can find older emitted messages
when telemetry is retained longer than the index. Initial historical backfill
rows do not emit `EMAIL_MESSAGE` and are not included; inspect those through the
message index. Search coverage is bounded by the organization's actual telemetry
retention, not a promise that every organization has a year of searchable mail.

To act on matches, select the messages and use
[bulk remediation](remediation.md). Review its read-only preview and confirm the
exact selection. The preview uses current indexed state, so an event that is
still searchable may no longer have a retained message available for action.

Use `limacharlie ai generate-query` to build the query and
`limacharlie search validate` before running it — LCQL is validated against
org-specific schemas and hand-written queries fail or mislead. See
[Data & Queries](../4-data-queries/index.md).

For the everyday "who else got this" question, the
[message index pivots](messages.md#the-two-ioc-pivots) are faster and are
purpose-built.

## Outputs

Because the events are ordinary telemetry, every
[Output](../5-integrations/outputs/index.md) works without any mail-specific
configuration: stream `EMAIL_MESSAGE` to a data lake, forward detections to a
SIEM, or push `EMAIL_ACTION` into an audit pipeline.

## Configuration as code

Every piece of Email Security configuration is a Hive record, so a tenant's whole
mail posture is a directory of YAML:

| Hive | Holds |
|---|---|
| `secret` | The provider credential |
| `mailsec_provider` | The connection |
| `mailsec_policy` | Automations, exclusions, VIPs, thresholds, banners, retention, reporter replies |
| `dr-mail` | Custom mail rules |
| `lookup` | VIP lists referenced by `vips.list_refs` |
| `dr-general` | The D&R rules on `EMAIL_*` events |

```bash
limacharlie hive set --hive-name mailsec_policy --key 50-finance-vips \
  --input-file policy/50-finance-vips.yaml --enabled --oid $OID

limacharlie hive list --hive-name mailsec_policy --oid $OID --output yaml
limacharlie hive get  --hive-name mailsec_policy --key 50-finance-vips --oid $OID
```

Two conventions make this pleasant to keep in git:

- **Records compose in name order**, so number your records (`00-baseline`,
  `50-team-x`, `99-override`) when precedence matters.
- **Unknown fields are refused**, so a typo fails the write rather than silently
  disabling a control. Validate a rule with `limacharlie hive validate` or
  `limacharlie mailsec rule validate` before committing it.

Onboarding a new tenant is then: subscribe the extension, write the secret, write
the provider record, apply the policy directory, run the connection test.
