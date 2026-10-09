# Events & Automation

--8<-- "includes/email-security-availability.md"

Email Security is not a side-car product with its own event bus. Everything it
sees becomes ordinary LimaCharlie telemetry, in the same lake as your endpoint,
cloud and identity data — which is what makes "a phish was delivered, and then
that user's endpoint ran a new binary" one rule instead of two products and a
spreadsheet.

## The sensors

Every protected mailbox is its own sensor on platform `email`. The sensor's
hostname is the mailbox's primary address, and it appears in the sensor list the
first time the mailbox produces an event. A ten-thousand-mailbox tenant is ten
thousand sensors; the `email` platform does not count against your sensor quota.

Each mailbox sensor declares its mailbox address as its identity, so with Cloud
Security it appears as a telemetry source on the matching User in
[Entity Pivot](../cloud-security/entity-pivot.md#adapter-identities-and-external-actors).

Events that are not about one mailbox land on the connection's own sensor,
`mailsec-<connection name>`. That is where a tenant-level event such as a
tenant data deletion request goes, and where everything the connection produced
before per-mailbox sensors existed still lives. The connection sensor shows as
online only while such an event is flowing, so do not use its online state to
judge whether mail is being ingested. Watch `EMAIL_INGEST_ERROR` and the
[coverage](getting-started.md#6-watch-coverage-fill-in) numbers for that.

!!! warning "If you already have rules or queries that select the connection sensor"
    Before per-mailbox sensors, every mail event came from the connection sensor
    (`mailsec-<connection name>`). A sensor selector that names it by hostname or
    sensor id, or a D&R rule scoped to it, no longer matches mailbox events; it
    matches only the tenant-level events described above. Select on
    `plat == email` instead. Per-sensor suppression and threshold state also
    starts fresh and is now kept per mailbox, so a counter that used to be shared
    by the whole tenant is now one counter per mailbox.

Two things follow from mailboxes being sensors:

- **Per-sensor state is per mailbox.** A D&R `suppression` that is not global
  counts per sensor, so a rule that fires "once per sender per day" does so per
  recipient without any extra key. See [State per mailbox](#state-per-mailbox).
- **A mailbox's sensor is fixed by its provider id, not its address.** If a user
  is renamed, the same sensor keeps receiving events and its hostname stays the
  address it was created with. A mailbox deleted and re-created is a new
  mailbox, with a new sensor.

### The `mailbox` object

Every event that concerns a mailbox carries the same top-level object, so a rule
can key on it whichever event it reads:

| Path | Holds |
|---|---|
| `event/mailbox/id` | The provider's stable handle for the mailbox: the user's object id on Microsoft 365, the address on Google Workspace. It is what the sensor is keyed on, and it is lower-case |
| `event/mailbox/address` | The mailbox's primary SMTP address, lower-case. The sensor's hostname |
| `event/mailbox/upn` | The user principal name, which is the sign-in identity that Entra ID and Okta events name the same person by. Google Workspace has no separate one, so it is the address. Absent until discovery has recorded it, which happens on the first discovery pass after a connection starts |

`EMAIL_MESSAGE`, `EMAIL_VERDICT`, `EMAIL_ACTION`, `EMAIL_USER_REPORT` and
`EMAIL_INGEST_ERROR` all carry it. An event that names no mailbox has no `mailbox`
object and goes to the connection sensor: a tenant data deletion request, or a
raw-message download attempt for a message that does not exist.

On `EMAIL_USER_REPORT`, `mailbox` is the mailbox the report **arrived in**, which
is your abuse mailbox. The person who sent the report is `event/reporter`.

!!! tip "Joining mail to sign-ins"
    `event/mailbox/upn` is indexed as a `user`, so an IOC search for a person's
    UPN finds their mail events next to their identity telemetry, and a rule can
    correlate a delivered phish with that user's next sign-in.

## The events

| Event | Emitted when |
|---|---|
| `EMAIL_MESSAGE` | Once per message, at ingest. Carries the whole parsed model — headers, sender, recipients, body, links, attachments, authentication, hops — plus the enrichments and the verdict. It is the record that this mail arrived |
| `EMAIL_VERDICT` | On **every** verdict decision: the rule pack's own, at ingest right after the `EMAIL_MESSAGE` (`revision/seq: 0`, `revision/mode: auto`), and then once per override afterwards (`seq: 1…`, mode `analyst`, `api` or `detonation`, and `ai` on older records) |
| `EMAIL_ANALYSIS_COMPLETE` | When the initial analysis window closes, including messages with nothing pending. Carries terminal outcomes, final verdict snapshot and timing |
| `EMAIL_ACTION` | On every remediation outcome, including failures and skips, **and on every raw-message download** (`action: get_eml`), served or refused. Who asked, what was attempted, what happened |
| `EMAIL_USER_REPORT` | When a message reaches the abuse mailbox and becomes a report |
| `EMAIL_PROVIDER_QUARANTINE` | Microsoft reports a quarantined, spam-filtered or failed delivery. `provider_status` distinguishes them; this is provider delivery metadata, not an engine verdict |
| `EMAIL_RELEASE_REQUEST` | An end user requests release from Microsoft hosted quarantine. Releases/denials are retained as history and do not emit this event |
| `EMAIL_DISPOSITION` | Independent analyst/SOAR disposition changed or cleared; carries actor, source, note, server timestamp, prior value, and sequence |
| `EMAIL_REPORT_RESOLVED` | Report resolved; carries report/message identities, recorded disposition and resolver, and mailbox when available |
| `EMAIL_INGEST_ERROR` | When a message could not be fetched or processed. Coverage honesty: failures are visible, never silent |

`EMAIL_MESSAGE` is emitted once and is immutable. When a verdict changes, the
original event is never rewritten — a new `EMAIL_VERDICT` is emitted instead, so
the verdict history is the sequence of those events and a replay can reconstruct
what was known at any point in time.

### Provider visibility events

See [Provider Quarantine](provider-quarantine.md#events-and-identity) for the
payload fields, mailbox identity, retry deduplication and correlation limits.
Match `routing/event_type` and `event/provider_status` to distinguish quarantined
mail from delivery failures. `EMAIL_RELEASE_REQUEST` observes a user's request;
it does not grant approval or execute a release.

### `EMAIL_VERDICT`

The body carries the message's identity plus one `revision` block, and it is the
same shape whichever decision it reports — which is the point: one rule reads all
of them.

| Path | |
|---|---|
| `event/msg_uuid` | The durable handle every typed action takes. A provider message id is folder-scoped and stops resolving the moment the message is quarantined; this does not |
| `event/mailbox/{id,address,upn}`, `event/provider` | Whose mail, from where. See [the mailbox object](#the-mailbox-object) |
| `event/internet_message_id` | The cross-mailbox join key: one message sent to forty people is forty `msg_uuid`s and one of these |
| `event/sender_email`, `event/sender_root_domain`, `event/subject` | Enough to match on without a lookup |
| `event/ts` | The message's delivery time. The **event's own** timestamp is when the decision was made, so a hunt can window on either |
| `event/campaign_id` | The campaign, if the message clustered into one |
| `event/campaign_joined_late` | Present and `true` only when this event exists *because* the campaign above was identified after the message had already been delivered and reported. See [A message that joins a campaign late](#a-message-that-joins-a-campaign-late) |
| `event/cluster_reason` | The cluster keys that agreed — why this message is in that campaign. Carried on a late join, which is the event the question gets asked about |
| `event/revision/seq` | `0` for the rule pack's verdict, `1…` for each override |
| `event/revision/mode` | `auto`, `analyst`, `api` or `detonation`. Older records can also read `ai`. See [Who is recorded](#who-is-recorded) |
| `event/revision/verdict`, `event/revision/score` | The decision |
| `event/revision/rationale` | The reasons, strongest first. For an override these are what the analyst or agent wrote; for `seq 0` they are the names of the signals that fired — so it is **absent** on a benign message that matched nothing, which is the common case |
| `event/revision/top_signals`, `event/revision/engine_version` | `seq 0` only — the rule ids that fired and the engine that decided (rule-pack version plus the library build it ran with). An override has neither: nothing *matched*, somebody decided |
| `event/revision/actor` | Who decided. Empty on `seq 0`: the rule pack is not a person, and `engine_version` is what identifies it |
| `event/revision/prior` | What the override displaced — verdict, score, mode and engine version. On `seq 0` it is present but empty (`verdict: ""`, `score: 0`), because the engine's first call displaced nothing — so match on `revision/seq` or `revision/mode` to tell the two apart, not on `prior` |

The MDM is deliberately *not* repeated here: it is already in the immutable
`EMAIL_MESSAGE`, and copying it into every verdict change would multiply a year
of telemetry by how often people change their minds.

### `EMAIL_ANALYSIS_COMPLETE`

This event uses the same identity and `revision` paths as `EMAIL_VERDICT`, so
triage reads `event/revision/verdict`, not the MDM's `event/verdict/verdict`.
`event/results` maps each armed analysis (`detonation`, `attachment_scan`) to
`completed`, `changed_verdict`, `skipped`, `shed`, `failed`, or `timed_out`.
`event/completed_at` and `event/timing` describe the completed window. Empty
results mean no delayed work was needed. The completion payload does not include
the seq-0 `analysis` snapshot or `after_complete`.

Start an AI or analyst triage workflow on this event when it needs the initial
analysis results. Continue handling later `EMAIL_VERDICT` escalations: analyses
that finish beyond the deadline carry `event/after_complete: true`. Completion
never means that a failed or timed-out analysis cleared the message.

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

## State per mailbox

Because each mailbox is a sensor, D&R state that is scoped to the sensor is scoped
to the mailbox. The [suppression](../8-reference/response-actions.md#suppression)
action is per-sensor unless you set `is_global: true`, so the recipient does not
have to appear in the key.

### Example: one detection per recipient per sender domain per day

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
  suppression:
    max_count: 1
    period: 24h
    keys:
      - 'email-malicious-delivered'
      - '{{ .event.sender.email.domain.root }}'
```

A sender domain that mails forty people produces forty detections, one per
mailbox, and each mailbox is reported once for that domain in a day. Without the
per-mailbox sensor the same rule would report the domain once for the whole
organization and hide the other thirty-nine recipients.

### Example: three malicious messages to one mailbox in an hour

```yaml
# Respond (same detect as above)
- action: report
  name: email-mailbox-malicious-burst
  priority: 3
  suppression:
    min_count: 3
    max_count: 3
    period: 1h
    keys:
      - 'email-mailbox-malicious-burst'
```

The counter is per sensor, so it counts per mailbox. The action is skipped until
the third event inside the hour and fires on it, then stays quiet for the rest of
the window. The window is fixed: it starts at the first counted event and the
counter resets when it expires.

### Finding one mailbox's events

Any field that takes a [sensor selector](../8-reference/sensor-selector-expressions.md),
such as the Query Console's sensor field, can name a mailbox directly:

```text
plat == email and hostname == "alice@example.com"
```

`limacharlie sensor list` shows the mailbox sensors beside your other sensors.

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
`restore_message`, `release_message`, `banner_message`, `unbanner_message`. They route to the same
executor, so the organization's `alert_only` / `enforce` mode, the audit row and
idempotency all apply unchanged — there is exactly one remediation path in this
product.

A rule may act even when the organization is in alert-only mode by adding
`force: true` to its `extension request`. Only a real boolean `true` forces. The
action is recorded as forced, on its audit row and as `forced: true` on its
`EMAIL_ACTION` — see
[Forcing an action in alert-only mode](remediation.md#forcing-an-action-in-alert-only-mode):

```yaml
- action: extension request
  extension name: ext-email-security
  extension action: quarantine_message
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
    force: true
```

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
the warning. The `enabled` switch on the
[`banners` record](policy.md#banners) does **not** gate a `banner_message` sent
this way. That switch covers bannering that Email Security decides on its own:
policy automations and `dr-mail` rules. A rule here acts through the API like the
console or the CLI, so its banner is performed whenever the organization is
enforcing, or when the request is forced. The audit row records it with
`source: api`. If you don't want a rule to banner, leave
`banner_message` out of it.

**How the action is attributed.** A rule in the `dr-general` Hive acts with the
Email Security extension's own credential: the organization authorized it by
writing the rule. The audit row's `reason` starts with `D&R rule <rule name>`
(followed by your `reason`, if the rule sets one), so you can tell which rule to
edit. The row's `actor` is the extension's own key and its `source` is `api`,
not `DR:<rule>` / `dr`. Rules in `dr-mail` are different: the mail engine runs
them itself and records `source: dr` with the rule as the actor.

The same actions requested by a person or an API key through
`extension request` run with **that caller's own permissions**: they need
`mailsec.act` (in addition to `ext.request`), and the audit row names them.
Campaign actions (`quarantine_campaign`, `trash_campaign`, `restore_campaign`)
need a person and cannot be driven by a rule. In a rule, write a `reason` as a
template. A plain string is read as a path into the event and dropped unless it
matches one, so a fixed reason is written `'{{ "Reviewed by rule" }}'`. See
[Writing the request](#writing-the-request).

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

## Triage after initial analysis

This platform D&R detection reports suspicious or malicious messages after the
initial evidence window closes. The final verdict is a snapshot at completion;
read `results` when your triage needs to distinguish an examined message from a
deadline, capacity refusal or analysis failure. Completion delivery is at least
once. Use `completion_id` as the workflow's idempotency key when dispatching
external work. Initial historical backfill emits no completion event.

```yaml
# Detect
event: EMAIL_ANALYSIS_COMPLETE
op: and
rules:
- op: exists
  path: event/revision/verdict
  truthy: true
- op: or
  rules:
  - op: is
    path: event/revision/verdict
    value: malicious
    case sensitive: false
  - op: is
    path: event/revision/verdict
    value: suspicious
    case sensitive: false
```

```yaml
# Respond
- action: report
  name: email-analysis-triage
  suppression:
    max_count: 1
    period: 720h
    is_global: true
    keys:
      - email-analysis-triage
      - '{{ .event.completion_id }}'
```

The example suppresses repeated reports for the same completion for 30 days
across sensors within the organization. After the suppression period expires,
the same identity can report again. External workflows that require durable
idempotency should retain their own completion identities for their retry horizon.

The initial `EMAIL_MESSAGE` remains useful for immediate containment and
content rules. Waiting for completion is a workflow choice; it does not prevent
the existing ingest-time automations from containing an already malicious message.

## Alerting on provider delivery delays

This example reports a provider notification lag over five minutes. The
existence guard excludes messages whose notification time is unknown. Adjust
the threshold to your own operating expectations; this is an example rule,
not a built-in alert.

```yaml
# Detect
op: and
rules:
- op: is
  path: routing/event_type
  value: EMAIL_ANALYSIS_COMPLETE
- op: exists
  path: event/timing/provider_lag_ms
- op: is greater than
  path: event/timing/provider_lag_ms
  value: 300000
```

```yaml
# Respond
- action: report
  name: email-analysis-provider-lag
```

Compare `provider_lag_ms` with `queue_ms` and `processing_ms` to separate delay
before notification from delay inside processing. The same pattern can alarm
on another present timing field. `analysis_ms` includes the delayed analysis
window; `end_to_end_ms` ends at the initial verdict. Check `clock_skew` before
interpreting clamped measurements.

### Feedback events and typed actions

`EMAIL_DISPOSITION` and `EMAIL_REPORT_RESOLVED` carry `group_id` when the indexed original has a message group, alongside top-level `disposition`,
`actor`, `source`, and `ts`. Disposition events also carry `seq` and `prior`.
Resolution events carry `report_id`. Both carry `msg_uuid`, provider, and mailbox
when an indexed message supplies it. An unlinked resolution retains its explicit
report identity; it never invents a mailbox. Durable retries retain `job_id`.

The Email Security extension has four typed actions that write feedback back to a message or report:

| Action | What it does | Permission | From a D&R rule |
|---|---|---|---|
| `revise_verdict` | Replaces the engine's verdict with yours and appends the change to the message's [revision history](detections.md#revising-a-verdict) | `mailsec.act` | Yes |
| `set_disposition` | Records, or clears, an independent [disposition](messages.md#analyst-disposition). The engine verdict is untouched and no automation runs | `mailsec.set` | Yes |
| `release_message` | Restores the message and records a benign verdict revision and a benign disposition. See [Release a message](messages.md#release-a-message) | `mailsec.act` | Yes |
| `resolve_report` | Closes a [user report](user-reports.md) with a disposition, with optional remediation | `mailsec.set`, plus `mailsec.act` when it remediates | No, interactive only |

None of them takes a `mode`. A rule that still sends one is rejected as an
unknown parameter, so remove it from any rule written for an earlier version.

#### Who is recorded

The decision mode on a revision or release comes from the credential that made
the call. You cannot declare it.

| Caller | Recorded mode | Recorded as the actor |
|---|---|---|
| A person signed in (the console, or the CLI after `limacharlie auth login`) | `analyst` | That person |
| Any API key, including a script, or the CLI configured with an API key | `api` | The key |
| A D&R rule | `api` | The extension's own key. The rule name is recorded in the text, see below |

Older records can read `ai`, from the time callers chose a mode. `auto` and
`detonation` are written only by the engine and no caller can claim them.

Every caller that holds the permission gets the same effect. A revision or a
release credits or repairs the sender's history the same way for a person, a key
and a rule, and counts the same as a decision on a message that was flagged only
because a user reported it. The mode is provenance for audit, not a different
level of authority.

Run interactively, an action uses your permissions (plus `ext.request` to call the
extension) and your identity, and the
audit names you. Run from a rule in the `dr-general` Hive, it uses the Email
Security extension's own credential, because the organization authorized it by
writing the rule. The rule name goes into the record as the first rationale
bullet of a revision, and as a prefix (`D&R rule <name>:`) on the reason of a
release or the note of a disposition. The name includes the Hive, so a rule saved
as `my-rule` in `dr-general` appears as `general.my-rule`. Reading the revision
history or the audit row tells you which rule to edit.

#### Writing the request

The `extension request` block of a rule is a template, and one detail of it
causes silent failures. This is how every `extension request` works, and the
[general rule](../8-reference/response-actions.md#writing-the-request-values) is
documented with the action. For these actions it matters most, because a dropped
`verdict` or `disposition` is the difference between a working rule and one that
does nothing. A top-level string value that has no `{{ }}` in it is
read as a path into the event, not as text. If the path matches nothing, the key
is silently left out of the request. `verdict: malicious` therefore does not send
the word `malicious`. It looks for a field named `malicious` in the event, finds
none, and sends no verdict at all. The platform then refuses the request because
`verdict` is missing. See [Errors show up when the rule runs](#errors-show-up-when-the-rule-runs).

To send a fixed string, write it as a template literal:

```yaml
extension request:
  msg_uuid: '{{ .event.msg_uuid }}'   # a value from the event
  verdict: '{{ "malicious" }}'        # a fixed string
  score: 90                           # numbers and booleans are always literal
  rationale:
    - Matched my phishing rule        # strings inside a list are literal
    - '{{ .event.sender_email }}'     # unless they contain {{ }}
```

Numbers and booleans (`score: 90`, `clear: true`, `force: true`) are literal.
Strings inside a list, which is where the rationale bullets live, are also
literal unless they contain `{{ }}`. A template that names a field the event does
not have is not an error. It renders as the text `<no value>` and is recorded
that way. Use the template literal form for every
top-level fixed string: `verdict`, `disposition`, `note` and `reason`.

#### Values and limits

| Field | Allowed values and limits |
|---|---|
| `msg_uuid` | Required on every action except `resolve_report`. At most 36 characters |
| `verdict` | Required on `revise_verdict`. `benign`, `graymail`, `suspicious`, `malicious` or `unknown`. `unknown` is an honest abstention that escalates to a human queue. `error` is not accepted, because it means the engine failed to judge |
| `rationale` | Required on `revise_verdict`. A list of short strings, at least one non-blank. A person gets up to 10 bullets of 280 characters, and more is refused. A rule gets 9 of its own, because the rule name takes the first of the 10. A rule that goes over is not refused: extra bullets and extra characters are clipped, and the revision is marked `rationale_truncated` |
| `score` | Optional integer from 0 to 100. Leave it out to keep the engine's score beside the new verdict |
| `disposition` | `malicious`, `spam`, `graymail`, `benign` or `simulation`. Leave it out when clearing |
| `clear` | `true` removes the current disposition. Send it instead of `disposition`, never with it |
| `note` | Text, at most 1024 characters including the rule prefix. A person who goes over is refused. A rule's note is clipped and ends in `[truncated]` |
| `reason`, `force` | On `release_message`. `force: true` performs the release in an organization that is in [alert-only mode](remediation.md#forcing-an-action-in-alert-only-mode); without it the release is recorded as `alert_only` and nothing changes. Only a real boolean `true` forces. If the message was never moved, the restore is `skipped` and the benign verdict and disposition are still recorded |

`resolve_report` takes `report_id`, `disposition` and an optional remediation
(`scope` of `message`, `group` or `campaign`, and an `action` from the
[remediation actions](#acting-on-mail-from-a-dr-rule)). Closing a report is a
decision someone has to own, so it runs only interactively. A rule that calls it
is refused.

#### Errors show up when the rule runs

Saving a rule does not check the request against the extension. A rule with
`verdict: '{{ "malcious" }}'`, with a `mode` field, or with a required field
missing, saves without complaint. The request is checked each time the rule
fires, and a bad one is refused and writes nothing. The refusal is recorded as an
organization error. Look at it right after the rule fires:

```bash
limacharlie org errors --oid $OID
```

A plain-string `verdict: malicious`, the trap described above, produces this:

```text
request 'revise_verdict' from DR:general.my-rule failed: lc_error_code:INVALID_PARAMETER - missing one of verdict
```

A misspelled value reads `invalid value for verdict: value not in enum`, and a
leftover `mode` reads `unknown parameter name: mode`. The error always names the
action. A refusal by the platform, as in these examples, also names the rule.

Three things limit what you see there:

- All errors from rule-driven Email Security requests go to one entry, labeled
  `extensions/ext-email-security`. A newer error from any rule or action replaces
  the previous one, so you see the latest error only.
- An identical message is recorded once per 15 minutes. Firing the same broken
  rule again right away does not add anything.
- A refusal that comes from the extension itself reads `EXTENSION_ERROR`
  followed by the extension's message. If the entry does not say which rule
  fired, match its time against your rules' reports.

So test one rule at a time and read the error straight after it fires. To
confirm what a rule did, or that it did nothing, check the message itself:
`limacharlie mailsec message revisions <msg_uuid>` for a revision, or the
`actions` and `disposition_info` fields of `limacharlie mailsec message get
<msg_uuid>` for a release or a disposition. Try a new rule on a message you can
afford to change before you rely on it.

#### Examples

Revise the verdict of mail the engine rated suspicious when it belongs to a
campaign. The detect matches `revision/seq: 0`, the engine's own verdict, so the
revision this rule writes (at `seq 1`) does not trigger it again.

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_VERDICT
  - op: is
    path: event/revision/seq
    value: 0
  - op: is
    path: event/revision/verdict
    value: suspicious
  - op: exists
    path: event/campaign_id
```

```yaml
# Respond
- action: report
  name: email-suspicious-campaign-escalated
- action: extension request
  extension name: ext-email-security
  extension action: revise_verdict
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
    verdict: '{{ "malicious" }}'
    rationale:
      - Engine rated the message suspicious
      - 'Member of campaign {{ .event.campaign_id }}'
```

The revision is recorded with mode `api`, names the rule in its first rationale
bullet, and emits an `EMAIL_VERDICT` at the next `revision/seq`.

Record a disposition on mail from a sender you know is your own phishing
simulation:

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_MESSAGE
  - op: is
    path: event/sender/email/domain/root
    value: phish-sim.example.com
```

```yaml
# Respond
- action: extension request
  extension name: ext-email-security
  extension action: set_disposition
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
    disposition: '{{ "simulation" }}'
    note: '{{ "Known phishing simulation sender" }}'
```

Clear a disposition when link detonation later finds the message malicious, so
that the verdict is no longer overruled by an earlier "benign":

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_VERDICT
  - op: is
    path: event/revision/mode
    value: detonation
  - op: is
    path: event/revision/verdict
    value: malicious
```

```yaml
# Respond
- action: extension request
  extension name: ext-email-security
  extension action: set_disposition
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
    clear: true
```

Release mail from a vetted partner that the engine rated suspicious. The example
sets `force: true` so it also works in an organization in alert-only mode, which
would otherwise record the release and withhold it:

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_VERDICT
  - op: is
    path: event/revision/seq
    value: 0
  - op: is
    path: event/revision/verdict
    value: suspicious
  - op: is
    path: event/sender_root_domain
    value: partner.example.com
```

```yaml
# Respond
- action: extension request
  extension name: ext-email-security
  extension action: release_message
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
    reason: '{{ "Vetted partner sender" }}'
    force: true   # remove this line if your organization is in enforce mode
```

A rule acts with the extension's own credential, so whoever can save rules in
`dr-general` can cause these writes. Keep that in mind when you decide who gets
that permission.
