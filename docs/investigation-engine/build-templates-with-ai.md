# Build and Tune Templates with an AI Agent

An AI agent is good at the mechanical part of writing a plan template: reading the
operator catalog, drafting YAML, fixing validation errors and reading test results.
It is a poor judge of whether a plan is *right* for your environment. This guide
splits the work accordingly: **the agent drafts, validates, tests and saves a draft;
a person reads the evidence and promotes it.**

The workflow:

1. Read the authoring kit.
2. Look at real alerts of the kind you are covering.
3. Draft a small template.
4. Validate until there are no errors, then read the warnings.
5. Test on past alerts.
6. Refine and test again.
7. Save as a draft.
8. A person reviews and promotes it.

The agent cannot promote a template. The save tool always writes `status: draft` and
refuses to overwrite an active template, and the Hive refuses an `active` write that
comes from an API key (unless the organization opted out; see
[Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)).

## Set up the agent

The agent needs the engine's tools and a credential that can use them.

**With the MCP server.** Use the `investigation_engine` profile, which holds the
ten investigation tools, or `investigation_engine_readonly` if the agent should only
read, validate and look up (no start, wave, test or save). See [MCP Tools](mcp.md)
for the tool list and how to connect.

**With the CLI.** The `limacharlie investigate` command group offers the same
operations. See [CLI](cli.md).

Give the agent's API key only what the workflow needs:

| To do this | The key needs |
|---|---|
| Read the kit, operators, packs and templates, validate a template | `investigation.get`, `insight.evt.get` |
| Test a template on past alerts, start a run or a wave | `investigation.set`, `insight.evt.get` |
| Save a draft | `investigation_plan.get`, `investigation_plan.set`, and `investigation.get`, `insight.evt.get` |

The two `investigation_plan.*` permissions are not part of the Owner role. Grant them
to the key explicitly. A test reads the data the key can read, so a key that cannot
read a detection or its case reports those samples as unreadable, not as failures. A
run the key starts executes as the policy identity unless it picks `caller` (see [Run
identity](policies.md#run-identity)).

!!! warning "Do not give the agent key any `investigation_policy.*` permission"
    The opt-out tag `allow-api-key-promotion` is set on a policy record with
    `investigation_policy.set.mtd`. A key that holds any broad `investigation_policy.*`
    grant could set it, turn off the promotion gate and then promote its own drafts. The
    agent only needs the `investigation_plan.*` permissions above.

!!! tip "Keep the key away from containment"
    The agent saves and tests templates. It does not need `sensor.task` or
    `mailsec.act`, which approving actions requires. Withholding them does not stop
    a run: a run the key starts on an **active** template acts as the policy identity,
    not as the key. Do not give the key `investigation.set` unless it should be able to
    start runs.

### Or let the console start the agent

The console can start this workflow for you. **Draft with AI** (on the Templates tab,
and on a detection) starts an AI session with the *Investigation plan author* agent from
the AI agent catalog. Describe the alerts in plain words, or start from a detection as
the example alert. The agent follows the steps below and saves a draft that appears in
the Templates list. See [Console](console.md#draft-a-template-with-ai).

## 1. Read the kit, in sections

The authoring kit is the one call that gives an agent everything it needs. It is
large (about 33,000 tokens as a whole), so fetch it in parts:

| Call | Sections | Size | Why |
|---|---|---|---|
| First | `guide`, `schema`, `codes` | about 13k tokens | How to write a plan, the template JSON Schema, every validation code. |
| Second | `operators` | about 14k tokens | What each operator takes and returns, and which ones your policy denies (`available: false`). Never guess a field name. |
| As needed | `examples` or `library` | varies | Real templates to copy a shape from. |
| As needed | `policy` | small | The budgets a plan must fit and each action class's autonomy mode. Worth fetching when you plan `respond` steps. |
| For one-off questions | `packs` | small | The fact packs. |

Ask the agent to read the guide first. The guide the kit returns is the same text
the engine's tests check its examples against.

## 2. Look at real alerts

Before writing, have the agent list the detections of the category you want to
cover, their cases, and how analysts classified them. A template written from a
handful of real alerts is far better than one written from the category name alone.
Note which fields the detections actually carry.

## 3. Draft a small template

Start with three to six facts and one or two proofs on each side. Start from the
`detection_id` input and derive everything else with facts, as described in
[Run inputs](templates.md#run-inputs).

This first draft triages a `rare-process` detection from what else fired on the
same host in the last week and an LLM judgement of that activity:

```yaml
status: draft
version: 1
description: Triage a rare-process detection from what else fired on the host in the last week and a judgement of that activity.
applies_to:
  detect_cat: ['rare-process']
prior: 0.25
inputs:
  detection_id: '{{ .detection.detect_id }}'
facts:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  host:
    op: entity.resolve
    args: {type: sensor_id, value: $trigger.sid}
  related:
    op: detection.list
    args: {sids: [$trigger.sid], window: [-7d, now]}
  judge:
    op: llm.judge
    args: {question: host_activity_malicious, data: {detections_last_week: '$related.count', host: '$host.display_name'}}
proofs:
  false_positive:
    - 'related.count <= 1 and judge.label == "no"'
  true_positive:
    - all: ['judge.label == "yes"', 'related.count >= 5']
evidence:
  - {id: busy_host, when: 'related.count >= 5', weight: 1.0}
respond:
  - {class: contain.network, target: '$trigger.sid', when: 'verdict == true_positive'}
report:
  case: none
```

Things to notice:

- `trigger`, then `host` and `related` run **in parallel** once `trigger` answers.
  `judge` waits for both.
- The `llm.judge` fact is the most expensive step. It gets only the two values it
  needs, not whole records.
- Both proofs need `judge`. If it is unknown, neither completes, and the run can
  only end on evidence or `inconclusive`. That is the safe behavior.
- `respond` only proposes isolating the sensor from the network, and only once the verdict
  is a decided true positive. Because this is a draft, the proposal stays a suggestion.
- `report.case: none` keeps test noise out of your cases while you tune.

## 4. Validate

Validation is cheap and stores nothing. Call it until `errors` is empty. Every issue
has a code, a path and often a suggestion. Here is the report for a copy of the next
version of this template with two mistakes, a misspelled field and a window that
starts 45 days ago:

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

Both are mechanical to fix: use the suggestion, and start the window within 30 days.
Then read the **warnings**: they are what makes a template useless without making it
invalid. Typical ones are `unused_fact`, `operator_denied`, `proof_never_completes`
and `respond_class_off`. The report also estimates the worst case of one run, so
you can see early whether it fits your budgets.

## 5. Test on past alerts

Test with 10 to 25 samples that include closed cases. A good mix is a few
detections whose cases were classified true positive, a few false positive, and a
few with no case at all. Use `{detect_cat, last: N}` to take the newest
detections of the category, and `{case_id}` for specific closed cases.

The test returns a result per sample: the verdict, the proof, what stayed unknown
and why, the cost, the time, and, for detections in a classified closed case, the
expected label and whether the template **agreed**. Then it returns a summary.

Read it with the table in [Test on past alerts](templates.md#test-on-past-alerts).
Do not optimize for agreement alone:

- A template that is `undecided` on a sample where the data is missing is behaving
  correctly. Inconclusive is a good answer.
- Agreement that comes only from evidence, never from a proof, is slow and weak.
- A single `disagree` is worth reading closely. Which fact misled the proof?

## 6. Refine and test again

Say the first test shows the binary is common across the fleet for most
false-positive samples, but the template cannot say so. Add the prevalence fact, a
second false-positive alternative and an evidence rule that favors a false positive
for a common binary:

```yaml
status: draft
version: 2
description: Triage a rare-process detection from what else fired on the host, how common its binary is, and a judgement of that activity.
applies_to:
  detect_cat: ['rare-process']
prior: 0.25
inputs:
  detection_id: '{{ .detection.detect_id }}'
facts:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  host:
    op: entity.resolve
    args: {type: sensor_id, value: $trigger.sid}
  related:
    op: detection.list
    args: {sids: [$trigger.sid], window: [-7d, now]}
  prev:
    op: ioc.prevalence
    args: {file_hash: $trigger.hash}
  judge:
    op: llm.judge
    args: {question: host_activity_malicious, data: {detections_last_week: '$related.count', host: '$host.display_name'}}
proofs:
  false_positive:
    - 'related.count <= 1 and judge.label == "no"'
    - 'prev.hosts_30d >= 50 and judge.label == "no"'
  true_positive:
    - all: ['judge.label == "yes"', 'related.count >= 5']
evidence:
  - {id: busy_host, when: 'related.count >= 5', weight: 1.0}
  - {id: common_binary, when: 'prev.hosts_30d >= 50', weight: -1.0}
respond:
  - {class: contain.network, target: '$trigger.sid', when: 'verdict == true_positive'}
report:
  case: none
```

Bump `version` for each meaningful change so you can tell test runs apart. Validate,
then test the **same samples** again. Comparing the same samples between versions is
what shows whether a change helped.

Keep these in mind while refining:

- Count a claim of absence ("no other detection", "zero hosts") as unknown when the
  window ends in the last few minutes. `ioc.prevalence` is a lagging index: a zero
  there is incomplete, so never let it complete a proof of safety.
- Do not write a proof that turns missing data into a verdict.
- Keep evidence weights modest. A weight so large that it overrides every proof
  defeats the proofs.
- Drop a fact no proof or evidence rule reads (`unused_fact`).
- Judge with `llm.judge` only what an indexed read cannot answer exactly.

## 7. Save as a draft

When the template validates cleanly and the test results are acceptable, the agent
saves it as a draft. The save tool does four things:

- always writes `status: draft` and adds the tag `ai-draft`;
- stores a short test summary (up to 2,000 characters) as the record's comment, so
  the reviewer sees what was tested;
- refuses to save a template that does not validate;
- refuses to overwrite an **active** template. An existing draft is replaced only
  when the agent passes `overwrite`. Save an improved version of an active template
  under a new name.

!!! note "The agent cannot activate"
    A template that says `status: active` is refused by the save tool. Leave
    `status` out.

Ask the agent to end with a summary a reviewer can read in a minute: what the
template covers, how many samples it ran on, how it agreed with analysts, what stayed
unknown and why, what it would propose, and what it costs per run.

## 8. A person promotes

A person opens the draft in the [console](console.md#templates), reads the template
and the test summary, tests it once more if needed, and sets `status: active`. At that
point:

- a D&R rule or the case trigger can start it;
- `applies_to` can pick it automatically;
- it acts within the [autonomy policy](policies.md), which is a separate decision.

Promote in two steps for anything that proposes containment. First activate the
template with the relevant action classes at `suggest` in the policy, and watch what
it proposes. Raise a class to `approve`, and only later to `auto`, when you trust it.

## A prompt to start from

```text
You are writing an Investigation Engine plan template for detections of category
"rare-process" in this organization.

1. Fetch the authoring kit with sections guide, schema and codes, then operators.
2. List recent detections of this category and the cases they ended up in. Tell me
   how many were classified true positive and false positive.
3. Draft a SMALL template: 3 to 6 facts, take detection_id as the only input, and
   derive everything else with facts.
4. Validate it until there are no errors, then fix the warnings that matter.
5. Test it on 15 to 25 samples that include closed cases of both classifications.
   Report agreement, the unknown reasons, and cost.
6. Refine at most three times, testing the same samples each time.
7. Save the best version as a draft. You cannot activate it.
8. Finish with a summary for the person who will promote it.

Rules: unknown is never false; never write a proof that depends on a fact that
can be incomplete to prove an absence; keep every window within 30 days; never
guess a field name, read it from the operator catalog.
```

## Common mistakes

| Mistake | What happens |
|---|---|
| Copying the `inputs:` block of an example and reading `$hash`, `$sid` | The trigger does not provide it. Every fact that reads it is `unknown(missing_input)`. Derive it from `detection.get`. |
| Proving absence on incomplete data | The proof never completes. Use a positive condition, or accept `inconclusive`. |
| A signal with only a `malicious` or only a `benign` condition, then a proof on `signals.all_explained` | The signal can never be explained, so the proof never completes. |
| Guessing a field name | Validation fails with `unknown_field` and a suggestion. |
| A window older than 30 days | Validation fails with `window_outside_free_range`. |
| Proposing a class the policy has `off` | The action is never proposed (`respond_class_off`). |
| Writing a template for a one-off question | Use a [wave](concepts.md#waves-and-fact-packs). Write a template only when the same alert comes back. |
