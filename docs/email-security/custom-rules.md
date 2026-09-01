# Custom Rules

--8<-- "includes/email-security-beta.md"

Your own mail rules live in the `dr-mail` Hive. They are ordinary D&R detect
blocks evaluated against the [Message Data Model](detections.md#what-the-rules-can-read),
and they compound with the managed pack in the same scoring pass — so a custom
rule is evidence in the same verdict, not a parallel opinion.

## A rule

```yaml
# hive: dr-mail, record name: custom-vendor-bank-change
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
limacharlie hive set --hive-name dr-mail --key custom-vendor-bank-change \
  --input-file rule.yaml --enabled --oid $OID
```

### Fields

| Field | Required | Meaning |
|---|:--:|---|
| *(record name)* | ✅ | **The record name is the rule id.** It must start with `custom-`, which is what keeps your rules from ever colliding with a packaged one. It is also what an exclusion or a rule override names, which is why the id is the name rather than a field inside the body — a body field could be duplicated across two records |
| `phase` | ✅ | `pre_verdict` or `post_verdict` — see below |
| `detect` | ✅ | A standard D&R detect block over the MDM |
| `class` | — | `signal` (default), `detection` or `graymail` |
| `weight` | ✅ for `signal` and `detection` | 0–100. Must be **0** for `graymail`, because the graymail lane bypasses the score entirely and a weight there would never be read |
| `confidence` | — | 0–100, **default 100**. An author who does not express a confidence means "when this fires, it is right" |
| `respond` | — | `post_verdict` only |
| `name`, `tags`, `attack_types`, `fp_notes` | — | Documentation and grouping. `fp_notes` is not required of your own rules — that discipline is ours, for the pack we ship |

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

## Validation

A `dr-mail` record is validated at **write time** by compiling it on the real
engine, so a record that exists has already been proven to compile. Validate a
candidate before you save it — the check calls the *same* function the Hive runs
on save, so "valid here" means "savable there":

```bash
limacharlie mailsec rule validate --file rule.json --rule-id custom-vendor-bank-change --oid $OID
```

An invalid rule is a **200 carrying `valid: false` and the reason**, not an error
response: you asked whether the rule is valid and found out that it is not. The
reason is the validator's own wording, because an author acts on the message and
not on a status code.

Omitting `--rule-id` validates against a placeholder in the `custom-` namespace,
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

## Tuning the managed pack

You do not need a custom rule to change a packaged one. Disable it, or replace
its weight, for your organization:

```yaml
policy_type: thresholds
rule_overrides:
  ms-link-unranked-domain:
    weight: 15
  ms-sender-first-contact:
    disabled: true
```

And to suppress a rule for a specific sender, domain or mailbox rather than
everywhere, use an [exclusion](policy.md#exclusions) — which carries a reason and
an optional expiry, so the hole in detection is reviewable.

## Rules that act on emitted events

A `dr-mail` rule is one of two seats. The other is an ordinary D&R rule in
`dr-general` matching the `EMAIL_*` events, which gets the platform's full
response arsenal and can correlate mail with the rest of your telemetry. See
[Events & Automation](automation.md).
