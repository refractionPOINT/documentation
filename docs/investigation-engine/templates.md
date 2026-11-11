# Plan Templates

A plan template tells the Investigation Engine how to investigate one kind of
alert. This page covers where templates live, the default library, the structure
of a template, how to validate and test one, and how a template becomes active.
For a guided workflow with an AI agent, see
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

LimaCharlie provides a **default library** of templates for common detection
classes. It is content you choose to install. Nothing in the library reaches your
organization until a person installs it, and an installed copy is yours to edit.

| Template | Version | Picked for | What it does |
|---|---|---|---|
| `endpoint-detection-triage` | 3 | any detection category (`detect_cat: ['*']`) | Generic fallback for a detection on a sensor: the triggering process and its parent, its network activity, the binary's prevalence, the host and its user, related detections and what is true on the host now. Proposes `contain.network` on a confirmed true positive. |
| `suspicious-process` | 3 | `encoded-powershell`, `lolbin-*` | Judges the command line of a trusted system binary, then checks the process tree, connections, user and whether the process is still active or persisted. Proposes `contain.network` on a confirmed true positive. |
| `mailsec-suspicious-message` | 5 | `mailsec-ai-triage` | Triage of a message the Email Security AI judge rated suspicious: explains each signal that fired, checks the sender's real history and corroborating mail. Proposes `contain.email` on a confirmed true positive. |
| `phishing-campaign` | 4 | `mailsec-ai-triage` | Investigates a malicious message several people received: where its link goes, who else received it, who clicked, whether a payload ran. Proposes `contain.email` and `contain.network` on a confirmed true positive. |

The library entries are written for production use, but **installing them writes
drafts unless you choose otherwise**: a draft never starts from a D&R rule or the case
trigger, and its actions stay capped at `suggest`. Test an installed copy, then
promote it (see [Draft, active and promotion](#draft-active-and-promotion)).

!!! warning "Installing the generic fallback"
    `endpoint-detection-triage` matches **every** detection category. Once it is
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
  templates**. The dialog starts at **Draft** for every template, whatever the library
  recommends; making a template active is an explicit choice, confirmed separately.
  See [Console](console.md#install-default-templates).
- **CLI:** `limacharlie investigate templates install-defaults`, which writes drafts
  unless you pass `--status`. See [CLI](cli.md#templates).
- **API or AI agent:** fetch the library with the authoring kit section
  `library` (each entry has `name`, `description`, `version`, `status`, `applies_to`
  and the `yaml` to store), then write the record `investigation_plan/<name>` with
  that YAML. The library entries are drafts (`status: draft`); keep that status when
  you store one, and have a person promote it once it is tested. Writing `status: active`
  is refused by default from an API key. Or install from the console. See
  [Permissions](permissions.md#active-templates-can-only-be-written-by-a-person),
  [API Reference](api-reference.md#authoring) and [MCP Tools](mcp.md).

## Anatomy of a template

A template is YAML. Unknown keys are errors, so a typo is never silently ignored.

```yaml
status: draft            # draft (default) or active
version: 1
description: One line shown in lists.
applies_to:              # which detections it is automatically picked for
  detect_cat: ['mailsec-ai-triage']
prior: 0.3               # P(true positive) before any evidence
inputs:                  # names a run may be given (see "Run inputs")
  detection_id: '{{ .detection.detect_id }}'
facts:                   # what to gather: one operator call each
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
signals: {}              # optional: per-signal questions for multi-reason detections
proofs:                  # conditions that settle the verdict
  false_positive: []
  true_positive: []
evidence: []             # weighted conditions used when no proof completes
scope:                   # facts to start scoping from once a true positive is likely
  from: []
respond: []              # actions to propose, each with an optional `when`
report:                  # how the case is written
  case: create
```

This skeleton shows every section. A real template needs at least one fact, and at
least one proof, signal or evidence rule, or it can never reach a verdict.

Top-level keys are `status`, `version`, `description`, `applies_to`, `inputs`,
`prior`, `facts`, `signals`, `signals_from`, `proofs`, `evidence`, `scope`,
`respond` and `report`. The authoring kit returns a JSON Schema listing every key.

### Facts and references

A fact is `{op: <operator>, args: {...}}`, or `{use: <pack>, args: {...}}` for a
[fact pack](concepts.md#waves-and-fact-packs). Arguments are literals or references:

| Form | Meaning |
|---|---|
| `$name` | A run input, or another fact. A fact that reads another waits for it. |
| `$name.path.to.field` | A field of that fact. References are checked against the operator's declared output, so a misspelled field is a validation error with a suggestion. |
| `$list[0].field` | An element of a list. |
| `$?name` | An optional input. If the run was not given it, the value is absent and the step still runs. |
| `$alert_time`, `$now` | Allowed in a `window`. |

A `window` is `[start, end]`. A bound is `-24h`, `+30m` (relative to the alert),
`now`, `now-7d`, an RFC 3339 time, or `{at: '$message.received', offset: -2h}` (a time
read from a fact). Durations accept `s`, `m`, `h` and `d`.

Facts can also carry `deadline: 30s`, `predict: true`, `checks: [tag]`, `case: true`
(the case always needs it) and a `report:` block that describes how the fact appears
in the case.

Prefer indexed reads (entities, detections, email messages) when they answer the
question. Searches and the `llm.judge` operator cost more time and money.

### Expressions

Proofs, evidence rules, signals and `respond.when` use expressions: a path, or a
comparison of paths and literals, combined with `and`, `or`, `not` and parentheses.
Comparison operators are `==`, `!=`, `<`, `<=`, `>`, `>=` and `in`.

```text
related.count >= 5
message.sender_domain in org.trusted_domains
"server" in host.attrs.tags or host.attrs.role == "dc"
judge.label == "yes"
p >= 0.7                 verdict == true_positive
signals.all_explained    signals.any_holds
```

Only numbers are ordered. A string is never equal to a number. `p` is the current
probability of a true positive and `verdict` is the current label.

### Run inputs

The `inputs:` block declares input names and documents what a D&R rule would map
to each one. **The engine never evaluates those expressions.** A run gets only what
its trigger provides:

| Started by | The run has |
|---|---|
| Console on a **detection** | `detection_id` |
| Console on a **case** | `case_id` |
| Console on an **email message** | `msg_uuid` |
| Console on an **entity** | `entity_id` |
| Console launcher, a question | `question` |
| D&R rule, `start investigation` | `detection_id` of the detection that fired, plus exactly the inputs the action lists |
| New case (case trigger) | `case_id`, and `detection_id` of the case's first detection when it has one |
| Test sample `{detection_id}` | `detection_id` |
| Test sample `{case_id}` | `case_id` and `detection_id` (the case's first detection) |
| Test sample `{detect_cat, last}` | `detection_id`, one run per detection |
| Test sample `{inputs: {...}}` | exactly the inputs you give |
| Every one of them | `alert_time`: when the run (or test) started. In a test this is the time of the test, not of the past alert; read the alert's own time from `detection.get`. |

**The recommended pattern: take `detection_id` and derive everything else with
facts.** A template written this way runs unchanged from the console, from a D&R
rule, from the case trigger and from every kind of test sample:

```yaml
inputs:
  detection_id: '{{ .detection.detect_id }}'
facts:
  trigger:
    op: detection.get          # the detection's own record
    args: {detect_id: $detection_id, window: [-29d, now]}
  host:
    op: entity.resolve
    args: {type: sensor_id, value: $trigger.sid}   # a field of the detection, not an input
```

The classic first mistake is copying an `inputs:` block such as
`'{{ .event.HASH }}'` and then reading `$hash`. The trigger does not provide it, the
input does not exist and every fact that reads it is `unknown(missing_input)`. The
validator warns about this with `input_not_provided`. To prefer an explicit input and
fall back to a derived value, read the input with `$?name` and use the `plan.pick`
operator:

```yaml
hash:
  op: plan.pick
  args: {candidates: ['$?hash', '$trigger.hash'], optional: true}
```

### Proofs, evidence and signals

```yaml
proofs:
  true_positive:                  # any ONE alternative completing proves a true positive
    - all: [cmd.label == yes, {any: ['live_net.public_remote_count >= 1', live_autoruns.found]}]
  false_positive:
    - all: [cmd.label == no, 'prev.hosts_30d >= 50']
evidence:
  - {id: common_binary, when: 'prev.hosts_30d >= 50', weight: -0.8}
```

- Each list is a set of alternatives (OR). An alternative is an expression string,
  `{all: [...]}` or `{any: [...]}`. They nest.
- The engine stops as soon as a proof completes and cancels the steps only the other
  alternatives needed. If a true-positive and a false-positive proof both complete,
  the verdict is flagged as a conflict, so avoid overlapping conditions.
- Evidence weights are log-odds. Keep them modest (0.5 to 2). Give each rule a stable
  `id`.
- A proof that depends on an unknown fact never completes. See
  [Unknown, absent and incomplete](concepts.md#unknown-absent-and-incomplete).

Signals (for detections that carry several reasons for firing) are described with a
`question`, a `malicious` condition and a `benign` condition. **Give both**: a signal
with no `benign` can never be explained, so `signals.all_explained` is never true
while it fires (`signal_missing_explanation`). `signals.all_explained` is true only
when every signal that fired is explained, and it is not true when none fired.

### Scope

`scope.from` names the facts the scoping phase starts from, for instance the host and
the user. Scoping does not search for new entities: the engine runs the facts you
listed (and what they depend on) once they become relevant, and a
conservative-profile run waits for a decided true positive before it does. The keys
`follow` and `after` are accepted and not used yet.

### Respond and report

`respond` proposes actions: `{class, target, when, before, attrs}`. The engine
evaluates each step every time new facts arrive, and proposes it as soon as its
`when` is true and its `target` can be resolved. **This can be before the final
verdict.** A step with no `when` is proposed as soon as the target is known. Write
`when: 'verdict == true_positive'` to hold a step until the verdict is a decided true
positive (as the default library does); `p >= 0.7` proposes it while the evidence is
still building. What happens to a proposal then depends on its class's mode:
`approve` asks a person once `P(TP)` passes `ask_approval_at`, and `auto` executes as
soon as the class's `min_confidence` is met, both without waiting for the verdict.

Only two classes can be carried out today:

| Class | What it does |
|---|---|
| `contain.network` | Isolate a sensor from the network (a reversible lease). Needs `sensor.task`. |
| `contain.email` | Quarantine a message, and the other recipient copies of its group, through Email Security (reversible where the provider supports release). Needs `mailsec.act`. |

The other classes the policy and the template format recognize (`contain.process`,
`contain.identity`, `tag`, `eradicate.process`, `eradicate.file`, `collect.memory`,
`collect.file`, `collect.artifact`) are **not available yet**: a template can propose
them, but approving or auto-executing one fails with "action class ... is not
wired", and the action ends `failed`. Do not use them in a template you intend to
run.

**A template only proposes.** The organization's [autonomy policy](policies.md#autonomy-modes)
decides per class whether an action is only suggested, needs approval or runs by
itself. A class whose mode is `off` is never proposed. `before: <class>` on a step
makes **this step a prerequisite** of the steps of the named class on the same
target: those actions wait until this step's action has been carried out. For instance,
`collect.file` with `before: eradicate.file` means the collection comes first and the
eradication waits for it. If this step's class is only suggested or off, or no such
step was proposed, the later action goes ahead with a caveat saying the collection
was not performed; if the collection was allowed but was denied, failed or expired,
the later action needs a person's approval. (The classes in the example are not
available yet, see above.)

`report` shapes the case: `case: create|none`, `severity` by verdict, `kind`,
`attack` (technique tags), `summary` sentences by verdict, and `questions` for the
analyst. A fact's `report:` block (kind `telemetry`, `entity`, `artifact` or
`detection`) says how it appears in the case, with a `note` in which `{fact.path}`
is replaced by values.

## How templates are chosen

A run names its template, or the engine picks one. A run **with no person** (a D&R
rule or the case trigger) that names no template gets the **active** template whose
`applies_to` matches the trigger. A person who starts a run from the console on a
detection or a case gets the same automatic choice.

| `applies_to` key | Matches |
|---|---|
| `detect_cat` | The detection's category. |
| `rule` | The D&R rule, written `general.<rule record name>`. A bare record name never matches. |
| `severity` | The case severity. D&R never sends a severity, so this key only helps the case trigger. |
| `tag` | Any of the trigger's tags. For a D&R rule these are the rule record's tags. |
| `source` | `api`, `dr-rule` or `case`. |

Values are exact (case-insensitive) or `*` globs (`lolbin-*`). A template matches
when **every** key it lists matches. With several matches, the one that lists more
keys wins, then the one with more exact (non-glob) values, then the lower name. If
none matches, the start is refused with a message that names what was tried. A
template with no `applies_to` is never chosen automatically; it can still be named.

## Validate

Validation type-checks a template against the operator catalog of your organization:
operators, argument types, every reference and expression path, and the free time
range. Every issue has a stable `code`, a `path`, a message and often a `suggestion`
that is the replacement to type.

```text
errors:
  - code: window_outside_free_range
    path: facts.related.args.window
    message: window starts earlier than 30 days ago: searches must stay inside the free time range
  - code: unknown_field
    path: proofs.false_positive[1]
    message: 'prev.hosts_30: the fact has no field "hosts_30" (did you mean "hosts_30d"?)'
    suggestion: hosts_30d
```

**Errors** make a template invalid. **Warnings** do not, and are what to fix next:
they are the mistakes that pass validation but make a plan useless. The most useful
ones are listed below; the authoring kit returns the complete list as `codes`.

| Code | Meaning |
|---|---|
| `unknown_field` | A reference reads a field the operator does not return. The suggestion is the field you probably meant. |
| `window_outside_free_range` | A search window starts earlier than 30 days ago. |
| `input_not_provided` | A fact reads an input no trigger provides. Derive it from `detection.get` instead. |
| `unused_fact` | A fact nothing reads. It only costs a step. |
| `operator_denied` | Your policy does not allow the operator, so the fact is always unknown. |
| `proof_never_completes` | A proof reads a fact that is always unknown. |
| `contradictory_proofs` | A proof that can never be true, or one condition proving both sides. |
| `signal_missing_explanation` | A signal lacks its `benign` or `malicious` condition. |
| `respond_class_off` | The policy has this action class `off`; it is never proposed. |
| `applies_to_never_matches` | An `applies_to` key a D&R rule cannot match. |
| `budget_exceeded` | The worst case does not fit your policy's budgets. |

The validation report also carries an `estimate` of the worst case of one run: the
number of steps, search steps, LLM steps, billed steps, the longest chain of step
deadlines in seconds, and which policy budgets it would exceed.

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
never calls `extension.request` (those facts stay unknown with the reason
`policy_denied`). It counts against your organization's concurrent run cap.

For each sample you get:

- the verdict (`label`, `p`, and its basis: a proof or evidence), the proof that
  completed, and what stayed unknown with its reason;
- the steps with status and timing, the cost, and the time;
- the actions the template **would** propose, by target reference only;
- when the detection belongs to a closed case that an analyst classified true
  positive or false positive: the **expected** label and whether the template
  **agreed**, **disagreed** or stayed **undecided**.

The summary gives the counts, an agreement rate, the most frequent unknown reasons
and the cost and time.

| You see | It usually means | Do |
|---|---|---|
| Many `undecided`, reason `not_found` or `forbidden` | The sample's data is not readable by you, or the template reads the wrong field. | Check the sample, then the operator arguments. |
| Many `undecided`, reason `index_lag` or `truncated` | A claim of absence on incomplete data. | Use a positive condition, or end the window before the last few minutes. |
| `disagree` | The proof is too eager, or the evidence weights are wrong. | Read the `proof` and `evidence` of that sample and tighten the alternative. |
| `agree` but always by evidence, never by proof | Slow and weak. | Add a proof alternative on the deciding fact. |
| High `wall_ms` or step count | Too many scans or LLM calls. | Drop facts that only feed unused alternatives, and reorder. |

A sample without an `expected` label may still have a case the engine could not read:
the engine looks at the newest 100 closed cases of the organization, and the result
says when it could not read them all (`expected_complete: false`).

## Draft, active and promotion

New templates, and everything written by an AI agent, are **drafts**. A draft:

- runs only through a test or a run a person starts;
- is capped at `suggest` for every action class, and says so in the run's
  `policy.clamped`;
- cannot be started by a D&R rule or the case trigger, and is never picked by
  `applies_to`.

A person **promotes** a template by setting `status: active` in the Hive record
(in the console, with **Make active** on the template's page). Review what was tested first. Promotion does
not change the autonomy policy: an active template still only does what
[the policy](policies.md) allows.
