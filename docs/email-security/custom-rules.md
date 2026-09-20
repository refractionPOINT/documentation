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

## Choose where the rule runs

| Goal | Configuration | Detection paths |
|---|---|---|
| Add evidence to a message verdict | `dr-mail`, `phase: pre_verdict`, class `signal` or `detection` | Message root: `sender/email/domain/root` |
| Classify bulk mail | `dr-mail`, `phase: pre_verdict`, class `graymail` | Message root; omit `weight` |
| Act after the initial verdict | `mailsec_policy` automations, or `dr-mail` with `phase: post_verdict` | Message root, including `verdict/verdict` |
| React to later verdict revisions or correlate mail with other telemetry | `dr-general` on `EMAIL_*` events | `routing/event_type` and `event/...` |
| Detect risky mailbox or domain configuration | `cloudsec_policy` posture rules | Resource properties under `event/...`; see [Mail Posture Rules](../cloud-security/mail-posture-rules.md) |

See the [Rule Reference](rule-reference.md) for supported operators, limits, and
message fields. A `dr-mail` rule has no `event/` or `mdm/` prefix. Its record body
contains the fields below directly, without a `rule:` or `data:` wrapper.

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
| *(record name)* | ✅ | **The record name is the rule ID.** Any non-empty Hive key up to 64 bytes; no prefix is reserved. Exclusions and verdict signals name this key. |
| `phase` | ✅ | `pre_verdict` or `post_verdict` — see below |
| `detect` | ✅ | A standard D&R detect block over the MDM |
| `class` | — | `signal` (default), `detection` or `graymail` |
| `weight` | ✅ for `signal` and `detection` | 1–100 for `signal` and `detection`. **Omit the field for `graymail`**, including an explicit zero; the Hive rejects any supplied weight for that class |
| `confidence` | — | 0–100, **default 100**. An author who does not express a confidence means "when this fires, it is right" |
| `shared_fact` | — | Optional group for overlapping scoring signals. Only the strongest weighted contribution in the group counts; not allowed on graymail or response rules |
| `respond` | — | `post_verdict` only |
| `name` | ✅ | Non-empty human-readable label, up to 256 bytes |
| `fp_notes` | ✅ | Non-empty explanation of the benign mail that might match |
| `tags`, `attack_types` | — | Grouping and authoring metadata; entries must not be empty |

### Signal, detection, or graymail?

Both `signal` and `detection` contribute `weight × confidence / 100` through the
[scoring formula](detections.md#scoring). A `detection` match also prevents the
graymail lane from winning; it does **not** bypass the malicious threshold.
Use `signal` for evidence intended to compound with other evidence.

Overlapping pre-verdict signals can use `shared_fact` to count only the strongest
contribution for the same fact. The field must have no surrounding whitespace
and cannot be used on graymail or post-verdict rules.

A graymail rule contributes no score. For example:

```yaml
# hive: dr-mail, record name: custom-bulk-precedence
name: Message declares bulk precedence
phase: pre_verdict
class: graymail
fp_notes: Transactional messages can also declare bulk precedence.
detect:
  op: scope
  path: headers/all
  rule:
    op: and
    rules:
      - op: is
        path: name
        value: Precedence
        case sensitive: false
      - op: is
        path: value
        value: bulk
        case sensitive: false
```

The installed defaults already include bulk-mail rules; this illustrates the
record format. Source files for default rules use `id` and `weight: 0` for
graymail. The extension converts those files into ordinary Hive records using
the record key as the ID and omitting graymail `weight`.

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
# hive: dr-mail, record name: custom-quarantine-cfo-malicious
name: Quarantine malicious mail to the CFO
fp_notes: Inherits false positives from the rules that produced the verdict.
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

The `weight: 1` satisfies the shared rule contract; post-verdict rules do not
change the score. Automated remediation still follows the organization's
[automation mode](policy.md#mode). Adding this rule does not itself enable
`enforce`.

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

`dr-mail` rules use `scope` to walk arrays of objects. The Hive rejects paths
containing `?` or `*`, even though those paths work in ordinary platform D&R
rules. This restriction applies to every `dr-mail` record, including defaults.

### `?` walks a list and compares values

In `dr-general`, `?` is a path segment that matches any element. Two conditions
using it may match two different elements. For example, a condition on
`event/links/?/href_url/domain/root` and another on
`event/links/?/mismatched` need not describe the same link. Use `scope` when the
conditions must describe one element. In `dr-mail`, use `scope` for either case.

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
and `mismatched`, not `links/href_url/domain/root`. A rule that keeps the full
path inside a `scope` block addresses fields that are not on that element.

### `scope` is capped, and nesting is refused

At most **two** `scope` operators are allowed in one `dr-mail` rule, and a
`scope` inside another `scope` is rejected. Keep conditions about one attachment,
link, or header in the same scope. Two sibling scopes can match different
elements and do not establish a relationship between them.

For a single-field array test, the same construct applies:

```yaml
op: scope
path: links
rule:
  op: is
  path: href_url/domain/root
  value: evil.example
```

## Validation

A `dr-mail` record is validated at **write time**: required fields, supported
operators, path restrictions, and budgets are checked, and the `detect` block is
compiled on the real engine. The `respond` block is checked for shape and size;
full response compilation happens when the collector loads it. Validation does
not prove that a field will be present or that a response will succeed.

Validate a candidate before saving it. The API calls the same validator as the
Hive, including lookup existence checks when its Hive access is configured.

The `mailsec rule` commands take a **JSON** file containing the rule body. For
the YAML examples on this page, save the equivalent JSON as `rule.json`; generic
`hive` commands also accept YAML through `--input-file`.

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

### What a backtest can evaluate

A `post_verdict` rule is refused: this backtest does not compute a new verdict or
execute responses. Backtest the `pre_verdict` conditions instead.

The service re-parses stored EMLs and restores `direction` and `mailbox/address`
from the index. It does **not** reconstruct the original pipeline's sender
history, VIP matches, domain-age enrichments, attachment scanner results, or
detonation results. Zero matches on a rule that requires those fields does not
prove that the rule would never match live mail. Use representative enriched
message fixtures for those conditions and inspect live matches before relying
on them for remediation.

A `lookup` rule can be backtested when the API service has its Hive resolver
configured. It reads the organization's **current** lookup records, not a
historical snapshot of the feed. If no resolver is configured, the request is
refused with the resource name; it is not reported as zero matches.

`mailsec analyze --file sample.eml` evaluates the organization's enabled scoring
rules and resolved scoring policy without ingesting the sample or executing
responses. It does not accept an unsaved candidate rule. Use `rule validate`
and `rule backtest` to check a candidate before saving it, and read the analyze
response's context limitations when testing rules that need enrichments.

The default window is seven days, the maximum window is 35 days, and a run
examines at most 2,000 messages. Check `coverage_note`, skip counts, and
`truncated` before interpreting the result.

### Rules for `lookup` in a mail rule

| Constraint | Behavior |
|---|---|
| Resource | Only `hive://lookup/<name>` is accepted |
| Count | At most four `lookup` operators per rule |
| Existence | Checked on save and by `rule validate` when the API's Hive metadata access is configured |
| Arrays | Use `scope` and an element-relative path; wildcard paths are rejected in `dr-mail` |

Create and populate the lookup before validating or saving the rule. A missing
record is reported by name when the metadata lookup succeeds. If that lookup
fails, the existence check is skipped; a successful validation therefore does
not prove that the lookup was resolved. Existence validation also does not prove
that the lookup is enabled, populated, or fresh; inspect the record and test a known
indicator. See [IOC & Reputation Feeds](ioc-feeds.md#changing-the-verdict-instead-of-raising-a-detection).

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
| Only a *change* to malicious | `path: event/revision/prior/verdict`, `op: is`, `not: true`, `value: malicious` |
| A specific rule that fired | `op: is`, `path: event/revision/top_signals/?/rule_id`, `value: ms-link-credentials-in-url` — the `?` matches any element of the list (`seq 0` only; an override carries no signals) |

!!! warning "Overrides go both ways"
    An override can also clear a verdict. A rule that quarantines on
    `verdict: malicious` will see the escalation, and a later `benign` revision
    does **not** undo the action it took — write the compensating rule if you
    want one.

## Maintaining the default rule sources

For contributors with access to the product repositories, `mail-rules` contains
the source pack and its sample harness. The shipped default sources live in
`go-mailsec/signals/rules/`. `ext-email-security` converts them into ordinary
Hive records during initial installation or explicit restoration;
`legion_mailsec` evaluates the organization's enabled records. Updating the
source pack does not replace an existing organization's rules.

`go-cloudsec` owns the separate configuration-posture rules described in
[Mail Posture Rules](../cloud-security/mail-posture-rules.md).

Default source files contain a top-level `rules` list. Each rule has a stable `id`,
`name`, `phase: pre_verdict`, `class`, `weight`, `confidence`, `tags`,
`attack_types`, `fp_notes`, and `detect`. Unlike a graymail Hive record,
a source graymail entry uses `weight: 0`. Do not copy a source file directly
into `dr-mail`: remove the list wrapper and body ID, choose the record key,
omit graymail weight, and replace any wildcard paths with supported conditions.

The contribution workflow is:

1. Change the YAML under `mail-rules/rules/`. Preserve rule IDs; retire and add a
   new ID when changing the meaning of a rule. Update false-positive notes.
2. Add positive and near-miss RFC 5322 samples under
   `samples/<rule-id>/positive/` and `samples/<rule-id>/negative/`. Use reserved
   domains such as `.example` and `.invalid` for fixture addresses and URLs.
3. Supply runtime-only enrichment facts in `<sample>.enrich.json` sidecars.
   Authentication results, headers, link mismatches, and other parse-derived
   evidence must come from the EML bytes. The harness runs the real parser and
   pure enrichers before applying sidecars.
4. Run the harness from its module directory:

   ```bash
   cd mail-rules/harness
   go test ./...
   ```

5. Sync approved changes into `go-mailsec/signals/rules/`, update its default-pack
   version, and run the library's rule and corpus tests. Check the extension's
   library pin before expecting an installation or restore to use the new defaults.
   Live verdicts identify the effective rules and policy by their configuration
   fingerprint; existing Hive records change only through an explicit edit or restore.

The harness checks compilation, sample coverage, positive and negative behavior,
fixture hygiene, and the benign-corpus gate. Its current benign-corpus gate
requires zero flagged messages. A change needs both a sample that should match
and a plausible benign sample that should not.
