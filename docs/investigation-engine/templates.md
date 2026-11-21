# Plan Templates

A plan template tells the Investigation Engine how to investigate one kind of
alert. This page is the reference: where templates live, the default library, every
section of a template, and how to validate, test and promote one. For the method
(what to write first, and why), read
[How to Think About Templates](how-to-think-about-templates.md). For a guided
workflow with an AI agent, see
[Build and Tune Templates with an AI Agent](build-templates-with-ai.md).

## Where templates live

Templates are [Config Hive](../7-administration/config-hive/index.md) records of
the `investigation_plan` type, named by the record key. **An organization's
templates are exactly its `investigation_plan` records.** The engine adds none and
hides none. A template you did not write, edit or install does not exist for your
organization.

Reading and writing these records needs the `investigation_plan.get` and
`investigation_plan.set` permissions, which are **granted explicitly** and are not
part of the Owner role. See [Permissions](permissions.md).

## The default library

LimaCharlie provides a **default library**, one template per kind of alert. It is
content you choose to install. Nothing in the library reaches your organization until
a person installs it, and an installed copy is yours to edit.

| Template | Picked for (`applies_to`) | Starts from | How it decides | Proposes |
|---|---|---|---|---|
| `endpoint-detection` | any detection category (`detect_cat: ['*']`) | detection | Your banned and approved software Lookups and what is true on the host now (running, connected, set to start on its own, the file signed and verified) decide; AI-assisted rules on a judged command line; otherwise one AI review of the stored event, lineage, workload, host and exposure recommends. | `contain.network`, `tag.add` |
| `suspicious-process` | `encoded-powershell`, `lolbin-*`, `suspicious-process`, `rare-process` | detection | The same model, for a trusted system binary used in a suspicious way. | `contain.network`, `tag.add` |
| `mailsec-message` | `mailsec-ai-triage` | message | Every reason Email Security flagged is explained; where the links land, attachments, the sender's history and clicks decide harm; a known sender whose reasons are all explained closes; otherwise the AI recommends. | `contain.email` (with a registered authorization) |
| `phishing-campaign` | `mailsec-ai-triage` | message | A malicious message many people received: where its link goes, who got it, who clicked, whether a payload ran. | `contain.email` (with a registered authorization), `contain.network` |
| `identity-sign-in` | `identity-suspicious-sign-in` | none (the caller gives the provider, sensor and principal) | The account's exact native activity and directory context; an AI-assisted rule; nothing closes on an empty search. | |
| `saas-admin-action` | `saas-risky-admin-action` | none (as above) | The actor's exact native activity and directory context; admin activity alone never establishes abuse. | |
| `cloud-exposure-finding` | `cloud-exposure-finding` | none (the caller gives `finding_id`) | Established reachability escalates; abuse beyond exposure is judged by the AI. | |
| `code-finding` | `code-security-finding` | none (the caller gives `finding_id`) | A live exposed secret escalates by rule; the AI reviews dependency and infrastructure-as-code findings. | |
| `appcontrol` | `app-control-policy-refused`, `app-control-break-glass`, `app-control-enforced-block`, `app-control-resident-terminated` | detection | One AI review of the stored event, lineage, workload, host, exposure and the application's record recommends. | |

Every library entry is a draft (`status: draft`). Read the current list, with each
entry's exact `applies_to` and YAML, from the authoring kit (`sections=library`). The
library also ships one D&R rule, `investigate-high-critical-case` (see
[D&R rules on a new case](automation.md#dr-rules-on-a-new-case)).

The Lookups the library reads (`banned-software` and `approved-software`, keyed by
file hash, in `endpoint-detection` and `suspicious-process`) are yours to create. A Lookup that does not exist answers unknown
(`not_found`), so the rules that read it never hold: nothing closes or escalates on a
list you have not written.

!!! warning "Installing the generic fallback"
    `endpoint-detection` matches **every** detection category. Once it is
    installed and active, a D&R rule that says `start investigation` without a
    `template` can choose it for any detection no more specific template covers.
    Install it deliberately.

!!! note "Versions and updates"
    Each library entry has a `version`. The console compares the library entry's
    version with the installed record's and offers an explicit update. An update
    **replaces your edits**; there is no merge. If you changed a template,
    copy it under another name before updating. The CLI never replaces an active
    template with a draft (move it back to draft first), and the console asks you to
    confirm before it does.

### Install the library

- **Console:** open **Investigations**, then **Templates**, and choose **Install default
  templates**. The dialog starts at **Draft** for every template; making a template
  active is an explicit choice, confirmed separately. See
  [Console](console.md#install-default-templates).
- **CLI:** `limacharlie investigate templates install-defaults`, which writes drafts
  unless you pass `--status`. See [CLI](cli.md#templates).
- **API or AI agent:** fetch the library with the authoring kit section
  `library` (each entry has `name`, `description`, `version`, `status`, `applies_to`
  and the `yaml` to store), then write the record `investigation_plan/<name>` with
  that YAML. Keep `status: draft` when you store one, and have a person promote it
  once it is tested. Writing `status: active` is refused by default from an API key.
  See [Permissions](permissions.md#active-templates-can-only-be-written-by-a-person),
  [API Reference](api-reference.md#authoring-kit) and [MCP Tools](mcp.md).

## Anatomy of a template

A template is YAML. Unknown keys are errors, so a typo is never silently ignored.

<!-- validate: template -->
```yaml
status: draft                      # draft (the default) or active
version: 1
description: "Escalate a message whose link lands on a password page a recipient reached; close one from a sender with history whose flagged reasons are all explained."
applies_to:                        # which alerts it is picked for automatically
  detect_cat: ['mailsec-ai-triage']
starts_from: message               # which ids the run is given (see below)
gather:                            # the steps: what to look at
  message:
    op: mailsec.message_get
    args: {msg_uuid: $msg_uuid}
  sender_history:
    why: "Has this sender written to the org before?"
    op: mailsec.sender_profile
    args: {sender: '$message.sender', domain: '$message.sender_domain', before: '$message.received', exclude_group: '$message.group_id'}
  link_landing:
    op: mailsec.link_resolve
    args: {links: '$message.links', links_complete: '$message.links_complete', sender_domain: '$message.sender_domain', reply_to_domain: '$message.reply_to_domain', detonation: '$message.detonation'}
  recipients:
    op: mailsec.group_recipients
    args: {group_id: '$message.group_id'}
  clicks:
    ask: "Did the recipients whose machines could not be checked open the link?"
    op: endpoint.click_check
    args: {copies: '$recipients.copies', domains: '$link_landing.malicious_domains', window: [{at: '$message.received'}, now]}
    only_if: 'link_landing.credential_harvest'
rules:                             # what decides
  escalate:
    - id: clicked_credential_harvest
      when: ['link_landing.credential_harvest', 'clicks.any_clicked']
      say: "A link lands on a page that asks for a password, and a recipient's machine reached it after delivery."
  close:
    - id: known_sender
      when: [signals.all_explained, 'sender_history.prior_messages_30d > 0']
      say: "The sender wrote {sender_history.prior_messages_30d} message(s) in the last 30 days, and every reason Email Security flagged has a benign explanation."
explain_signals:                   # for alerts that come with reasons
  ms_sender_first_contact:
    question: Is this really the first time this sender wrote to the org?
    malicious_when: 'sender_history.prior_messages_30d == 0'
    benign_when: 'sender_history.prior_messages_30d > 0'
act:                               # what to propose when a rule decides
  - {class: contain.email, target: '$message.msg_id', attrs: {group_id: '$recipients.action_attrs.group_id'}, on_rules: [clicked_credential_harvest]}
case:                              # how the case reads
  mode: create
  severity: {escalated_by_rule: high, closed_by_rule: low, default: medium}
  kind: [phishing]
```

Top-level keys, exactly: `description`, `version`, `status`, `applies_to`,
`starts_from`, `deadline`, `scope`, `trust`, `gather`, `rules`, `explain_signals`,
`ai_review`, `act` and `case`. A template needs at least one step, and at least one
rule or an `ai_review` (`no_verdict_path`). The authoring kit's `schema` section is
the JSON Schema of every key.

A record in the earlier format (`facts`, `inputs`, `proofs`, `evidence`, `prior`,
`signals`, `signals_from`, `respond`, `report`, `decision`...) is refused with
`legacy_template_format`, and the engine does not run it. Rewrite it: facts become
`gather` steps, proofs become rules with ids, `respond` becomes `act` with `on_rules`,
`report` becomes `case`, and evidence, priors and thresholds go.

- `deadline` (`10m`, `2h`, `1d`) caps the run's wall time. It never loosens the
  policy's budget.
- `scope: {from: [step ids]}` names the steps that run only once a rule (or the AI)
  escalated: the scoping of an incident, never part of the decision.
- `trust` declares values and Lookups your organization maintains as trusted for this
  template. A match skips active analysis of an initial target; it never counts as
  verified benign. The run identity needs `lookup.get`.

## Where a run starts: `starts_from`

A run gets very little from what started it: the id of the thing it was started on,
plus `alert_time`. `starts_from` says which of those ids the template reads as
`$name`:

| `starts_from` | Inputs it provides |
|---|---|
| `detection` | `detection_id` |
| `message` | `msg_uuid`, `fired_signals`, `detection_id` |
| `case` | `case_id`, `detection_id` |
| `none` (the default) | none |

Who provides them:

| Started by | The run has |
|---|---|
| Console on a **detection** | `detection_id` |
| Console on a **case** | `case_id` |
| Console on an **email message** | `msg_uuid` |
| D&R rule, `start investigation` | `detection_id` of the detection that fired, plus exactly the inputs the action lists |
| D&R rule `start investigation` with `case` (a new case) | `case_id`, and `detection_id` of the detection the case was opened for, when it has one |
| Test sample `{detection_id}` or `{detect_cat, last}` | `detection_id` |
| Test sample `{case_id}` | `case_id` and `detection_id` (the case's first detection) |
| Test sample `{inputs: {...}}` | exactly the inputs you give |
| Every one of them | `alert_time`: when the run (or test) started. In a test this is the time of the test, not of the past alert; read the alert's own time from `detection.get`. |

Reading `$name` that the starting point does not provide is the error
`unknown_reference`. Any other value a caller may pass (a D&R rule's `inputs`, a test
sample's `inputs`) is an **optional input**, `$?name`, readable in a step's `args`
only: when it was not given, the step reads null. Rules, conditions and `act` entries
never read `$?name`: a caller's value never decides an outcome and never chooses what
is acted on (`bad_reference`).

**The recommended pattern: start from the id and derive everything else with
steps.** A template written this way runs unchanged from the console, from a D&R
rule and from every kind of test sample:

```yaml
starts_from: detection
gather:
  trigger:
    op: detection.get          # the detection's own record: category, sensor, time, hash...
    args: {detect_id: $detection_id, window: [-29d, now]}
  host:
    op: entity.resolve
    args: {type: sensor_id, value: '$trigger.sid'}   # a field of the detection, not an input
```

To prefer a value a caller gave and fall back to the derived one, use `plan.pick`:

```yaml
  hash:
    op: plan.pick
    args: {candidates: ['$?hash', '$trigger.hash'], optional: true}
```

## Gather

A step is `{op: <operator>, args: {...}}`, one operator call, or
`{use: <pack>, args: {...}}`, a [fact pack](concepts.md#waves-and-fact-packs). A step
also takes:

| Key | Meaning |
|---|---|
| `why` | The question the step answers, for the person reading the run. It replaces the operator's default sentence. |
| `ask` | The question for a person when the step stays unknown. The case asks it. |
| `only_if` | Run the step only when this condition is true (below). |
| `always: true` | Gather it for the case even after a rule decided (the triggering detection, who else received it). Without it, a step that can no longer change the outcome is cancelled. |

### References

| Form | Meaning |
|---|---|
| `$name` | A step, or an input the starting point provides. A step that reads another waits for it. |
| `$name.path.to.field` | A field of that step. References are checked against the operator's declared output, so a misspelled field is a validation error with a suggestion. |
| `$list[0].field` | An element of a list. |
| `$?name` | An optional caller input, in a step's `args` only. |

Steps with no dependency start at once, in parallel. A cycle is an error
(`dependency_cycle`).

A `window` is `[start, end]`. A bound is `-24h`, `+30m` (relative to the alert),
`now`, `now-7d`, an RFC 3339 time, or `{at: '$message.received', offset: -2h}` (a time
read from a step). Durations accept `s`, `m`, `h` and `d`. No window may start earlier
than 30 days ago: validation **rejects** an older one (`window_outside_free_range`).

### `only_if`

```yaml
  live_net:
    op: sensor.read.netstat
    args: {sid: $sensor, pid: '$live_process.matches[0].pid'}
    only_if: 'live_process.found'      # only ask the host when the process still runs
```

- The step waits while the steps its condition reads are pending, then runs when the
  condition is true.
- It is **skipped** when the condition is false (reason `only_if_false`), or when a
  step its condition reads failed (`condition_unknown`). Steps that read a skipped step
  are skipped too (`dependency_skipped`).
- **A skipped step reads as unknown** to rules and to the AI review. The condition
  decides cost, never the outcome: it can only ever cost a decision, never make one.
- It reads what a rule may read (see [Expressions](#expressions)). A condition on
  `signals.*` waits for the fired signals and every step the explanations read.

### Packs

`use: <pack>` expands a tested bundle of steps named `<id>__<step>`: `ctx` using
`detection_context` gives `ctx__trigger`, `ctx__host_alerts` and the others. Rules
read those names; the bare pack id is not a value. `GET /packs` (or the kit's
`packs` section) lists each pack's parameters and exports. A pack step takes `use`,
`args`, `only_if`, `why`, `ask`, `always` and an optional pin (`pack_version`,
`pack_digest`).

### Steps that need care

- **`lookup.get`** `{name, keys}` reads one of your organization's
  [Lookups](../7-administration/config-hive/lookups.md): one `{key, found, value}` per
  key, plus `found`, `all_found` and `missing`. A key the Lookup does not list is
  `found: false`, and that answer is complete. A Lookup that does not exist is
  unknown (`not_found`). These are the best rules you can write: exact, cheap, and
  yours.
- **`search.exists`** and **`search.rows`** take an LCQL `filter`. A value read from a
  step never goes into the text: write `:name` in the filter and bind it in
  `params: {name: $step.path}`.
- **`extension.request`** `{extension, action, data}` calls an extension. Its side
  effects are unknown to the engine, so it is denied unless the policy lists the pair
  in `operators.extension_requests`, and a test never calls it.
- **`ask_ai`** asks the AI one question (see [The AI](#the-ai-ask_ai-and-the-review)).
- Actions are never steps (`action_in_gather`): they belong in `act`.

Prefer indexed reads (entities, detections, email messages, Lookups) when they answer
the question. Searches, live sensor reads and AI questions cost more time and money:
put an `only_if` on them when they matter only in some cases.

## Expressions

Rules (`when`, `never_close_when`), `only_if` and signal explanations
(`benign_when`, `malicious_when`) share one expression language: a path, or a
comparison of paths and literals, combined with `and`, `or`, `not` and parentheses.

```text
sender_history.prior_messages_30d > 0
message.sender_domain in org.trusted_domains
link_landing.open_redirect and not message.reply_to_mismatch
cmd.label == "yes"
is_ok(trigger)
signals.all_explained     signals.any_holds     signals.ms_sender_first_contact.explained
```

- Operators are `==`, `!=`, `<`, `<=`, `>`, `>=` and `in`. A bare path is true when
  the value is the boolean true. Only numbers are ordered, and a string is never
  equal to a number.
- `is_ok(step)` is true when the step answered, false when it ran and failed, and
  unknown while it is pending or when its `only_if` skipped it.
- An expression reads exactly: the steps of `gather` (pack steps as `<id>__<step>`),
  the inputs the starting point provides and `alert_time`, and the builtins
  `signals` and `org`. It never reads `$?name` inputs or the AI review.

## Rules

```yaml
rules:
  escalate:
    - {id: banned_binary, when: 'banned.found', say: "The binary is on our banned software list."}
  close:
    - id: approved_and_signed
      when: ['approved.found', 'live_file.matches', 'live_file.verified']   # a list is "all of"
      say: "The binary is on our approved list, and the file on the host is that file, signed and verified."
  never_close_when:
    - 'live_autoruns.found'      # never close while the binary is set to start on its own
```

| Key | Meaning |
|---|---|
| `id` | Required, unique across both sides, lowercase letters, digits and `_`. The case, the run, `act` entries and test results name rules by id. |
| `when` | A string, a list (all of), `{all: [...]}` or `{any: [...]}`, nested as you need. |
| `say` | The sentence the case leads with when the rule decides. `{step.path}` puts a value in. |
| `never_close_when` | Conditions that block every close while one of them is true or unknown. Only a known false lets a close through. |

- **An escalate rule decides as soon as it holds**, and gathering stops, except for
  the steps that other escalate rules with `act` entries, or an `act` entry's target
  or guard, still read (below).
- **A close rule decides once it holds on complete answers** and nothing blocks a
  close (a fired signal not explained, a `never_close_when` condition). It does not
  wait for steps only escalate rules read: those are cancelled.
- **An escalate rule and a close rule that hold at once** end the run `conflict`.
  `contradictory_rules` warns about a rule that can never be true, or the same
  condition on both sides.
- **Which rule decides:** the escalate rule that held **first** (the last of the steps
  it reads arrived first; at the same moment, a deterministic rule before an
  AI-assisted one, then the template's order), or the first close rule in order. The
  decision is written at once and never moves.
- **Other escalate rules keep counting** after an escalation when they have `act`
  entries: the steps they read are not cancelled until each rule is true, false or
  finally unknown, within the run's budgets. One that holds is listed in
  `verdict.also_held` and in the case's decision sentence, and fires its own `act`
  entries under the normal policy and authorization rules (an AI-assisted one only
  where the AI may escalate). The cost: those steps can still run after the
  decision.
- When no rule decides and nothing relevant is left to gather, the run ends
  `couldnt_tell` (or the AI review runs). Never write a rule that turns missing data
  into a decision.

## Signals: `explain_signals`

For alerts that come with reasons, such as an Email Security message's fired
signals, every reason that fired must be answered before anything closes:

```yaml
explain_signals:
  ms_sender_first_contact:
    question: Is this really the first time this sender wrote to the org?
    malicious_when: 'sender_history.prior_messages_30d == 0'
    benign_when: 'sender_history.prior_messages_30d > 0'
```

- The fired set is the run's `fired_signals` input when given, else the
  `fired_signals` field of the template's one `mailsec.message_get` step. Until it
  is read, the fired signals are unknown: no `signals.*` condition is vacuously true.
- Each signal needs a `question` and at least one of `benign_when` and
  `malicious_when`. **Give both**: a signal with no `benign_when` can never be
  explained, so it blocks every close when it fires (`signal_missing_explanation`).
  Names are the detection's reason ids with `-` written `_`.
- A fired signal whose `malicious_when` holds blocks every close; so does a fired
  signal the template does not explain. `signals.all_explained` is true only when
  every fired signal has a benign explanation that holds and no malicious check
  holds.

## The AI: `ask_ai` and the review

**A focused question.** An `ask_ai` step asks one question about what other steps
gathered:

```yaml
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [ctx__trigger]
```

`question` and `sees` (the steps, or `step.path` for one field, whose answers it
reads) are required. The step waits for what it sees; when one of them is unknown,
the question is not asked. The answer is `label` (`yes`, `no` or `unclear`), a
self-rated `confidence` (shown, never used), a short `rationale` and the `agent` that
answered. Write the question so that yes is the risky reading and no the benign one.

**AI-assisted rules.** A rule that reads an `ask_ai` step, directly or through
another step's arguments, is AI-assisted, and `validate_plan` lists it in
`ai_rules`. When a signal explanation or a `never_close_when` condition reads an AI
answer, that answer can lift the veto on every close, so every close rule becomes
AI-assisted. An AI-assisted rule decides only on the sides the policy's
`ai_may_decide` allows for this template. Otherwise, when it holds, it
**recommends**: the outcome is `ai_recommends_malicious` or `ai_recommends_benign`,
nothing is acted on, and a person decides.

**The review.** `ai_review` is the fallback when no rule decided and nothing
relevant is left to gather:

```yaml
ai_review:
  question: "Is this process activity malicious? Say what in the evidence shows it."
  sees: [ctx__trigger, host__card, spread__prevalence]   # the steps it reads
  needs: [ctx__trigger]                                   # it may not answer benign unless these are known
```

- `question` is required. `sees` lists the steps it reads, each whole; the default is
  everything gathered.
- It answers malicious, benign or unclear, and cites the step fields it used. The
  engine checks every claim against what it saw. A benign answer counts only when
  every step it `needs` (by default every step it sees) is known and complete, and
  every claim checks out. Otherwise the answer is unclear.
- Nothing reads the review: it is not a step in `gather`, and no rule or condition
  reads it. `act` entries name it in `on_rules: [ai_review]`.
- It decides only where the policy's `ai_may_decide` allows; otherwise it
  recommends.

Both run on the organization's `ai_agent` record that the policy's `llm.agent` names,
or `investigation-judge` when the policy names none (see the
[walkthrough](walkthrough.md#2-the-ai-agent-record)). Without an agent, `ask_ai`
steps and the review are unknown (`llm_agent_not_found`).

## Act

```yaml
act:
  - {class: contain.network, target: '$ctx__trigger.sid', on_rules: [banned_binary, judged_malicious_on_noisy_host]}
  - {class: tag.add, target: '$ctx__trigger.sid', attrs: {tag: 'ie:banned-binary', ttl: 86400}, on_rules: [banned_binary]}
```

| Key | Meaning |
|---|---|
| `class` | The action class. See [Action classes](policies.md#action-classes). |
| `target` | A step path or a literal. |
| `attrs` | An object of literals or step paths, for the class (a tag and its TTL, a message group). |
| `on_rules` | Required. The rule ids, or `ai_review`, whose decision fires the entry, each named once. A recommendation fires nothing. The key is `on_rules`, not `on`: some YAML readers turn a bare `on` into the boolean true, so `on` is refused as an unknown field. |
| `before` | A class whose actions on the same target must wait for this one: evidence before eradication. |
| `authorize` | A registered authorization the engine re-checks from the run's evidence (below). |

**A template only proposes.** The organization's
[autonomy policy](policies.md#autonomy-modes) decides per class whether an action is
only suggested, needs approval or runs by itself. A class whose mode is `off` is never
proposed (`act_class_off`). A draft template and an inline plan only suggest.

**Nothing runs without a person unless a registered authorization holds**, an engine
check rebuilt from the run's own evidence. There are exactly two:

- `contain.email` with `authorize: mail.verified_credential_harvest.v1`: one message,
  a credential-harvest landing of that message's links that a stored link detonation
  verified, the recipients of that message's group, decided by a deterministic rule
  with no support from the AI or from case history.
- The engine's own close check of `close.false_positive`.

Every other `act` entry, host isolation included, and every entry that fires on a
decision the AI made, waits for a person even under `auto` (the reason
`no_registered_authorization`).

**The case close.** `closed_by_rule` and `closed_by_ai` propose `close.false_positive`
under the policy's mode for that class. `closed_by_ai` closes by itself only while the
policy still lets the AI close for the template. `ai_recommends_benign` proposes the
close of the case and of the message capped at `approve`, whatever the class's mode:
it is the person's **Close as benign** button. `ai_recommends_malicious` proposes no
close.

`before: <class>` makes this entry a prerequisite of the actions of the named class
on the same target: `collect.file` with `before: eradicate.file` means the collection
comes first. If this entry's class is only suggested or off, the later action goes
ahead with a caveat saying the collection was not performed; if the collection was
allowed but was denied, failed or expired, the later action needs a person.

## Case

```yaml
case:
  mode: create                 # create | none: this template's default
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, closed_by_rule: low, default: medium}
  kind: [phishing]
  attack: [T1566.002]
  trigger_step: detection      # the step that holds the detection the run is about
  fp_rule_tag: watch-fp-rule   # a tag the case gets when it is closed
```

`severity` is keyed by outcome (`closed_by_rule`, `escalated_by_rule`,
`closed_by_ai`, `escalated_by_ai`, `ai_recommends_benign`,
`ai_recommends_malicious`, `couldnt_tell`, `conflict`) plus `default`, with values
`low`, `medium`, `high` and `critical`. A close outcome without its own key
(`closed_by_rule`, `closed_by_ai`) is `low`; `default` does not raise it. The case leads with the outcome sentence and
lists the fired signals, the detections, the evidence (each step a rule or the review
read that answered, with its sentence), what stayed unknown, the actions and the open
question. A test writes no case.

## A complete example

A rare-process detection. A banned binary escalates by rule and proposes host
isolation. A command the AI judges malicious, on a host that keeps alerting,
escalates where the policy lets the AI decide, and otherwise recommends. Otherwise
the AI review recommends.

<!-- validate: template -->
```yaml
status: draft
version: 1
description: "Triage a rare-process detection: a banned binary escalates; a command the AI judges malicious on a host that keeps alerting escalates where the policy lets the AI decide; otherwise one AI review recommends."
applies_to:
  detect_cat: ['rare-process']
starts_from: detection
gather:
  ctx:
    use: detection_context
    args: {detection_id: $detection_id}
  host:
    use: host_context
    args: {sid: '$ctx__trigger.sid'}
  spread:
    use: hash_spread
    args: {hash: '$ctx__trigger.hash'}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$ctx__trigger.hash']}
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [ctx__trigger]
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary is on our banned software list."
    - id: judged_malicious_on_noisy_host
      when: ['cmd.label == "yes"', 'ctx__host_alerts.count >= 3']
      say: "The command was judged malicious on a host that raised {ctx__host_alerts.count} detections in the last week."
ai_review:
  question: "Is this process activity malicious? Judge the command, the host and how common the binary is; say what in the evidence shows it."
  sees: [ctx__trigger, host__card, spread__prevalence]
  needs: [ctx__trigger]
act:
  - {class: contain.network, target: '$ctx__trigger.sid', on_rules: [banned_binary]}
case:
  mode: create
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, default: medium}
```

Read it this way. `ctx` answers first; `host`, `spread`, `banned` and the question
wait for the fields of `ctx__trigger` they read, then run in parallel.
`judged_malicious_on_noisy_host` is AI-assisted: with the policy's AI switch off for
this template, it only recommends. There is no close rule: a binary seen on many hosts
is never what closes an alert, so only the review reads the prevalence, and it may
answer benign only with the detection's own record known.

## How templates are chosen

A run names its template, or the engine picks one. A run **with no person** (a D&R
rule) that names no template gets the **active** template whose `applies_to` matches
the trigger. A person who starts a run from the console on a detection or a case gets
the same automatic choice. A person's start through the API is matched on the
request's own `trigger`, so it must carry the detection's `category` (and `tags` or
`severity` when `applies_to` uses them): without a category, no `detect_cat` matches,
not even `*`.

| `applies_to` key | Matches |
|---|---|
| `detect_cat` | The detection's category. |
| `rule` | The D&R rule, written `general.<rule record name>`. A bare record name never matches. |
| `severity` | The case severity, or the severity a person's start carries. A rule on a detection never sends one. |
| `tag` | Any of the trigger's tags. For a D&R rule these are the rule record's tags. |
| `source` | `api` (a person or a script), `dr-rule` (a rule on a detection) or `case` (a rule on a case). |

Values are exact (case-insensitive) or `*` globs (`lolbin-*`). A template matches
when **every** key it lists matches. With several matches, the one that lists more
keys wins, then the one with more exact (non-glob) values, then the lower name. If
none matches, the start is refused with a message that names what was tried. A
template with no `applies_to` is never chosen automatically; it can still be named.

## Validate

Validation type-checks a template against your organization's operator catalog:
operators, argument types, every reference and expression path, and the free time
range. Every issue has a stable `code`, a `path`, a message and often a `suggestion`
that is the replacement to type.

```text
errors:
  - code: window_outside_free_range
    path: gather.related.args.window
    message: window starts earlier than 30 days ago: searches must stay inside the free time range
  - code: unknown_field
    path: rules.escalate[0].when
    message: 'spread__prevalence.hosts_30: the fact has no field "hosts_30" (did you mean "hosts_30d"?)'
    suggestion: hosts_30d
```

**Errors** make a template invalid. **Warnings** do not, and are what to fix next:
they are the mistakes that pass validation but make a template useless. The most
useful ones are below; the authoring kit returns the complete list as `codes`.

| Code | Meaning |
|---|---|
| `legacy_template_format` | The template is in the earlier format. Rewrite it in this one. |
| `unknown_reference` | A reference names something that is neither a step nor an input of the starting point. Derive it with a step, or read a caller's value as `$?name` in a step's args. |
| `unknown_field` | A reference reads a field the operator does not return. The suggestion is the field you probably meant. |
| `window_outside_free_range` | A search window starts earlier than 30 days ago. |
| `no_verdict_path` | No rule and no `ai_review`: the template can never decide or recommend. |
| `unknown_rule` | An `act` entry's `on_rules` names a rule the template does not have. |
| `reads_review` | A rule, a condition or a step reads `ai_review`. |
| `unused_step` | A step nothing reads, and not `always`. It only costs a step. |
| `operator_denied` | Your policy does not allow the operator, so the step is always unknown. |
| `rule_never_holds` | A rule reads a step that is always unknown. |
| `contradictory_rules` | A rule that can never be true, or one condition on both sides. |
| `signal_missing_explanation` | A signal lacks its `benign_when` or `malicious_when`. |
| `act_class_off` | The policy has this action class `off`; it is never proposed. |
| `applies_to_never_matches` | An `applies_to` key a D&R rule cannot match. |
| `budget_exceeded` | The worst case does not fit your policy's budgets. |

The validation report also has `ai_rules`, the ids of the AI-assisted rules, and an
`estimate` of the worst case of one run: the number of steps, search steps, AI steps,
billed steps, the longest chain of step deadlines in seconds, and which policy budgets
it would exceed.

## Test on past alerts

Testing runs a template for real, **read-only**, on past alerts, and shows how it
would have done. Nothing is written: no run, no case, no feedback label, no action,
no audit event. The only thing kept is the test result itself, for 24 hours.

A test takes a stored template (draft or active) or a template you paste, and up to
**25 samples**, each one of:

| Sample | Meaning |
|---|---|
| `{detection_id}` | One past detection. |
| `{case_id}` | A case; the run gets its first detection, and the case's classification is the expected label. |
| `{detect_cat, last: N}` | The newest N stored detections of that category in the free time range (N up to 25). |
| `{inputs: {...}, expected: ...}` | Free run inputs, with an optional expected label. |

Pick a mix: some detections whose cases were classified true positive, some false
positive, some with no case.

A test runs **as you**, with your token and your permissions, whatever identity the
policy configures for real runs. It is forced to autonomy `suggest`, no case, and
never calls `extension.request` (those steps stay unknown with the reason
`policy_denied`). It counts against your organization's concurrent run cap.

For each sample you get:

- `verdict`: the outcome, `decided_by` (`kind` and `rule`), the AI's
  `recommendation`, `missing` and `unknowns`. A test result carries no rendered
  sentences: `decided_by` has no `say` and the recommendation no `rationale`;
- the steps with status, reason and timing, the `cost` and the time;
- the actions the template **would** propose, by target reference only;
- when the detection belongs to a closed case that an analyst classified:
  `expected` (`label`, `source`, `case_id`) and `agreement`. `agreement.rule` is
  `agree`, `disagree` or `none` (no rule decided); `agreement.ai` is `agree`,
  `disagree`, `unclear` or `none` (no recommendation).

The `summary` gives:

| Field | Meaning |
|---|---|
| `decided_by_rules` | How many samples a rule decided. |
| `rules.<rule id>` | For each rule, how many samples it `decided`, and how many of those `agree` or `disagree` with the analysts. |
| `ai` | On the samples no rule decided, how the AI's recommendation fared: `recommended`, `agree`, `disagree`, `unclear`. |
| `by_outcome` | Samples per outcome. |
| `unknown_reasons` | The most frequent reasons steps stayed unknown. |
| `cost_per_sample`, `wall_ms` | Steps, AI cost and time per sample; time percentiles. |
| `expected_complete` | `false` when the engine could not read every closed case (it looks at the newest 100): a sample without `expected` may still have a case. |

**These numbers are informational.** Nothing at run time reads them, and nothing
waits for them before a template is promoted or the AI may decide.

| You see | It usually means | Do |
|---|---|---|
| Steps unknown, reason `llm_agent_not_found` | No AI agent is set for the run. | Set `llm.agent` in the `default` policy, or create the `investigation-judge` record. |
| Many `couldnt_tell`, reason `not_found` or `forbidden` | The sample's data is not readable by you, or a step reads the wrong field. | Check the sample, then the step's args. |
| Many `couldnt_tell`, reason `index_lag` or `truncated` | A claim of absence on incomplete data. | Prefer a positive condition, or end the window before the last few minutes. |
| A rule with `disagree` | The rule is too eager. | Read the samples it decided and tighten its condition. |
| Most samples decided by the AI, few by rules | The rules miss the deciding fact. | Add a rule on that fact, often a Lookup of your own. |
| High `wall_ms` or step count | Too many scans or AI questions. | Drop steps nothing reads, add `only_if`. |

## Draft, active and promotion

New templates, and everything written by an AI agent, are **drafts**. A draft:

- runs only through a test or a run a person starts;
- is capped at `suggest` for every action class, and says so in the run's
  `policy.clamped`;
- cannot be started by a D&R rule, and is never picked by `applies_to`.

A person **promotes** a template by setting `status: active` in the Hive record
(in the console, with **Make active** on the template's page). Read what was tested
first. Promotion does not change the policy: an active template still only does what
[the policy](policies.md) allows, and the AI still only recommends until someone turns
on [AI may decide](policies.md#what-the-ai-may-decide) for it.
