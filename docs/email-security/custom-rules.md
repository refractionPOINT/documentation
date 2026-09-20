# Mail Rules

--8<-- "includes/email-security-beta.md"

Every mail detection rule lives in your organization's **`dr-mail` Hive**, one rule
per record. **Email Security → Rules** shows the complete set: search and filter,
inspect the full YAML/JSON, edit, enable, disable or delete any rule. Reading takes
`mailsec.get`; changing or deleting takes `mailsec.set`.

## Default rules and ownership

The first subscription installs LimaCharlie's defaults as ordinary enabled records.
After installation they are yours. There is no hidden pack, reserved record-name
prefix, global managed-detection switch, or per-rule policy override. The record
key is the rule ID. Default keys such as `ms-link-credentials-in-url` are ordinary
keys with exactly the same permissions and behavior as names you choose.

Only enabled records run. With no enabled `pre_verdict` rules, messages remain
`unknown`. When scoring rules run but none matches, the verdict can be `benign`.
Rule changes normally apply on the next rule reload, within ten minutes. If a
reload fails, the collector keeps the last successfully loaded set and reports
the failure. Existing verdicts are not rewritten by a configuration edit.

The subscription's one-time installation marker survives unsubscribe/resubscribe.
Deleted rules never return on a background refresh or a later subscription callback.
If the initial installation was interrupted or partially failed, use **Restore
defaults** to complete it.

## Restore defaults

**Restore defaults** creates missing default records and leaves every existing
record untouched, including disabled or edited defaults. Select **Also reset
existing default rules** to replace default-keyed records with the shipped body,
enabled state, tags and comment. ACL tags are preserved. Keys outside the default
set are never changed. Reset discards edits, and requires confirmation in the UI.

The action is `ext-email-security` → `restore_default_rules`, with optional
`overwrite` (default `false`). It returns `total`, `created`, `overwritten`,
`skipped`, `failed`, and up to 50 `{key, error}` failures. A partial result is not
success for every record. Retry the explicit restore to recover.

The extension performs writes with its own identity. `ext.request` authorizes
calling the action; the console additionally requires `mailsec.set`. Records
outside the extension's segment cannot be overwritten and are reported as failed.

## Infrastructure as code

The UI, Hive API and CLI edit the same records. Use `limacharlie hive list`,
`get`, `set`, `enable`, `disable`, `delete` or `validate` with `--hive-name dr-mail`.
The record body is a single rule, not a `rules:` wrapper and not an `id` field.
Pass `--enabled` when creating a rule that should run.

`limacharlie sync pull` and `sync push` support `--hive-dr-mail` and
`--hive-mailsec-policy`, and include both with `--all`. This lets version-controlled
configuration own the exact same execution set visible in the console.

## A rule

```yaml
# hive: dr-mail, record name: vendor-bank-change
name: Payment-detail change from a first-contact sender
phase: pre_verdict
class: signal
weight: 70
confidence: 75
tags: [bec, finance]
attack_types: [bec]
fp_notes: >
  Fires on genuine new vendors during onboarding. Intended to compound with
  auth failures rather than to stand alone.
detect:
  op: and
  rules:
    - op: is
      path: enrichments/sender_profile/prevalence
      value: none
    - op: matches
      path: body/current_thread/text
      re: "(?i)(bank details|remittance|update our account)"
```

```bash
limacharlie hive set --hive-name dr-mail --key vendor-bank-change \
  --input-file rule.yaml --enabled --oid $OID
```

### Fields

| Field | Required | Meaning |
|---|:--:|---|
| *(record name)* | ✅ | **The record name is the rule ID.** Any non-empty Hive key up to 64 characters; no prefix is reserved. Exclusions and verdict signals name this key. |
| `phase` | ✅ | `pre_verdict` or `post_verdict` — see below |
| `detect` | ✅ | A standard D&R detect block over the MDM |
| `class` | — | `signal` (default), `detection` or `graymail` |
| `weight` | ✅ for `signal` and `detection` | 0–100. Must be **0** for `graymail`, because the graymail lane bypasses the score entirely and a weight there would never be read |
| `confidence` | — | 0–100, **default 100**. An author who does not express a confidence means "when this fires, it is right" |
| `shared_fact` | — | Optional group for overlapping scoring signals. Only the strongest weighted contribution in the group counts; not allowed on graymail or response rules |
| `respond` | — | `post_verdict` only |
| `name`, `fp_notes` | ✅ | Human-readable label and expected false positives |
| `tags`, `attack_types` | — | Documentation and grouping |

### The two phases

| Phase | Sees | May do |
|---|---|---|
| `pre_verdict` | The message and its enrichments, before the verdict exists | Contribute weighted evidence to the verdict. **No `respond` block** — there is no verdict yet to respond to, and a rule with one is refused |
| `post_verdict` | The whole message *and* its verdict | `respond` — dispatch a mail action, or raise a detection |

### What a `post_verdict` rule may respond with

| Action | |
|---|---|
| `extension request` naming `ext-email-security` | The way a rule reaches remediation. The typed action goes to the same executor every other action uses, which is where `alert_only` / `enforce` is decided |
| `report` | Raise a detection into the platform's detection stream |

```yaml
name: Quarantine malicious mail sent to the CFO
fp_notes: A false malicious verdict can quarantine legitimate mail.
phase: post_verdict
class: signal
weight: 1
detect:
  op: and
  rules:
    - op: is
      path: verdict/verdict
      value: malicious
    - op: is
      path: mailbox/address
      value: cfo@corp.example
respond:
  - action: extension request
    extension name: ext-email-security
    extension action: quarantine_message
    extension request:
      msg_uuid: "{{ .msg_uuid }}"
```

Everything sensor-shaped — task, tag, isolate, seal, re-enroll, set variable —
**fails loudly** in a mail rule with a message saying so. There is no sensor
behind a message, and remediation goes through `extension request`.

!!! note "This is the same machinery your automations compile to"
    A `mailsec_policy/automations` rule is compiled into exactly this shape: a
    `post_verdict` rule whose respond block is an `extension request` naming the
    action, bound to the message that matched. Policy is the easy path; a
    `dr-mail` rule is the escape hatch when your condition does not fit the
    match fields.

## Matching one link, not any two links

A mail rule reads the message as JSON, and the paths it writes are the emitted
event's own field names. Two constructs walk a list, and confusing them is the
most common way a mail rule quietly matches the wrong thing.

### `?` walks a list and compares values

`?` is a **path segment**. It stands for "every element", and the condition
matches if **any** element satisfies it.

```yaml
# Any link whose registrable domain is evil.example
op: is
path: links/?/href_url/domain/root
value: evil.example
```

Cheap, and right most of the time. But two conditions using `?` can be satisfied
by **two different elements**:

```yaml
# WRONG if you meant "one link that is both"
op: and
rules:
  - op: is
    path: links/?/href_url/domain/root
    value: evil.example
  - op: is
    path: links/?/mismatched
    value: true
```

That fires on a message with a perfectly ordinary link to `evil.example` *and* a
separate, unrelated link whose visible text disagrees with its destination.
Nothing in it says "the same link" — and a phishing message that carries a
tracking pixel and a footer link will satisfy pairs like this by accident.

### `scope` re-roots a whole sub-rule onto one element

`scope` is an **operator**. It takes a `path` and a `rule`, and evaluates that
whole sub-rule against **each element in turn**, with the element as the root —
so every condition inside is about the *same* one.

```yaml
# ONE link that both points at evil.example and lies about where it goes
op: scope
path: links
rule:
  op: and
  rules:
    - op: is
      path: href_url/domain/root
      value: evil.example
    - op: is
      path: mismatched
      value: true
```

Paths inside a `scope` are **relative to the element** — `href_url/domain/root`
and `mismatched`, not `links/?/href_url/domain/root`. That is the other half of
the trap: a rule that keeps the full path inside a `scope` block looks correct
and matches nothing.

| | `?` | `scope` |
|---|---|---|
| What it is | A segment in a `path` | An operator with `path` and `rule` |
| Correlates fields of one element | **No** | **Yes** |
| Paths inside | Full, from the message root | Relative to the element |
| Cost | One extraction | The sub-rule, once per element |

### `scope` is capped, and nesting is refused

Use `?` unless you actually need the correlation, because `scope` is the one
allowed operator whose cost the rule's own size does not describe: the element
counts — links, attachments, headers, hops — come from **the message**, not from
your rule.

- At most **two** `scope` operators per rule.
- A `scope` inside another `scope` is **refused at save**, not merely
  discouraged. Nesting multiplies: elements to the power of the depth.

Both refusals name the reason rather than reporting a generic validation error.

## Validation

A `dr-mail` record is validated at **write time** by compiling it on the real
engine, so a record that exists has already been proven to compile. Validate a
candidate before you save it — the check calls the *same* function the Hive runs
on save, so "valid here" means "savable there":

```bash
limacharlie mailsec rule validate --file rule.json --rule-id vendor-bank-change --oid $OID
```

An invalid rule is a **200 carrying `valid: false` and the reason**, not an error
response: you asked whether the rule is valid and found out that it is not. The
reason is the validator's own wording, because an author acts on the message and
not on a status code.

Omitting `--rule-id` validates against the placeholder `unnamed`,
so a rule you have not named yet does not fail on its name.

`limacharlie hive validate --hive-name dr-mail --key <name> --input-file rule.yaml`
performs the same check through the generic Hive path.

### Rules fail loudly, never quietly

A `dr-mail` record that cannot be decoded or converted **fails the whole rule
load** for that organization rather than being skipped. That is the opposite of
how a bad *policy* record is handled, and deliberately so: a dropped policy record
costs one setting, while a dropped rule is a detection the organization believes
exists and does not — silently reduced protection, which no report after the fact
undoes.

Records are loaded in record-name order so the rule set is assembled identically
on every pass, and a **disabled** record is honoured as your own off switch.

## Backtesting

Before you enable a rule, find out what it would have matched.

```bash
limacharlie mailsec rule backtest --file rule.json --since "$(date -d '14 days ago' +%s)" \
  --oid $OID --output yaml
```

The response is deliberately honest about its own limits:

| Field | Meaning |
|---|---|
| `coverage_note` | What was actually examined |
| `skipped_no_raw` | Messages whose raw copy had expired |
| `skipped_unparse` | Messages that could not be re-parsed |
| `truncated` | The run hit its bound |
| `precision` | **`null`, not `0`**, when nothing it matched has an analyst disposition yet |

A precision figure whose denominator quietly shrank is a number that looks like a
measurement and is not one — hence the skip counts. And `0` would read as
"everything it matched was wrong" and would have you discard a good rule, so the
absence of labels is reported as absence.

Backtests are bounded to the window this product retains rather than the full
message history. Both `rule validate` and `rule backtest` are gated on
`mailsec.get`: they reveal only messages you can already read, and a rule author
should be able to check their work with the grant that lets them see what the
rule would be matching.

### Backtests are budgeted, because they re-read your mail

A backtest is not an index query. For every message in the window it fetches the
stored original, decrypts it, decompresses it, parses it and evaluates your rule
against it — so it is the most expensive read on the Email Security surface, and
an organization gets **6 backtests per 10 minutes** across every credential in
it. Past that the call answers `429` with `rate_bucket: mailsec_post_read` and a
`Retry-After`; see [Read budgets](api-reference.md#the-replay-budget).

That is sized for the loop this page describes — write, backtest, read the
report, adjust — and not for a script. Asking for a narrower window does not take
the call out of the budget (the charge is the same whatever window you name), but
it does make the call itself faster, and a backtest over a wide window on a busy
organization can take tens of seconds.

### Response rules cannot be backtested

A `post_verdict` rule is refused: it runs against the verdict a pass would compute,
while a backtest replays a message rather than re-scoring it. Backtest the
`pre_verdict` rules that produce the verdict instead.

Rules using `lookup` can be backtested with your organization's current lookup
records. This tests current lookup content, not a historical snapshot of the
lookup at the time each message arrived. If the API's Hive resolver is unavailable,
the backtest refuses the rule rather than reporting a misleading zero matches.

### Rules for `lookup` in a mail rule

| | |
|---|---|
| Form | The resource must be `hive://lookup/<name>` — nothing else is accepted |
| Count | At most **four** `lookup` operators per rule. Each resolves a whole lookup record for your organization |
| Existence | Checked by both `rule validate` and Hive on save against your organization's lookup metadata |

Create the lookup before validating or saving a rule that names it. A missing
lookup is reported by name. As with any validation preview, a record can change
between validation and save; the save remains authoritative.

## Tuning rules

Edit `weight`, `confidence` or `detect` directly on the rule record. Use the
record's enabled state to turn it off. This applies equally to seeded defaults
and rules you wrote. The YAML and JSON editors preserve the complete rule body.
Saves use the record's etag; a concurrent edit is reported as a conflict rather
than overwritten.

For a scoped suppression, use an [exclusion](policy.md#exclusions) with a reason
and optional expiry. A suppressed match remains in `matched_signals` for auditing;
a disabled rule does not run at all.

## Rules that act on emitted events

A `dr-mail` rule is one of two seats. The other is an ordinary D&R rule in
`dr-general` matching the `EMAIL_*` events, which gets the platform's full
response arsenal and can correlate mail with the rest of your telemetry. See
[Events & Automation](automation.md).

### Acting on a verdict

`EMAIL_VERDICT` carries every verdict decision — the rule pack's own at
`seq: 0`, and each later override — so a rule that should fire whenever a message
is judged malicious is written once, against one path:

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_VERDICT
  - op: is
    path: event/revision/verdict
    value: malicious
```

```yaml
# Respond
- action: report
  name: email-verdict-malicious
- action: extension request
  extension name: ext-email-security
  extension action: quarantine_message
  extension request:
    msg_uuid: '{{ .event.msg_uuid }}'
```

That fires when the pack decides a message is malicious **and** when an analyst,
the AI triage agent or a link detonation later decides so. Narrow it with the
fields that distinguish them:

| To match | Add |
|---|---|
| Only the rule pack's own decision | `path: event/revision/seq`, `value: 0` |
| Only overrides | `op: is greater than`, `path: event/revision/seq`, `value: 0` |
| Only what a human decided | `path: event/revision/mode`, `value: analyst` |
| Only a *change* to malicious | `path: event/revision/prior/verdict`, `op: is not`, `value: malicious` |
| A specific rule that fired | `op: is`, `path: event/revision/top_signals/?/rule_id`, `value: ms-link-credentials-in-url` — the `?` matches any element of the list (`seq 0` only; an override carries no signals) |

!!! warning "Overrides go both ways"
    An override can also clear a verdict. A rule that quarantines on
    `verdict: malicious` will see the escalation, and a later `benign` revision
    does **not** undo the action it took — write the compensating rule if you
    want one.
