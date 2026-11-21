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
fourteen investigation tools, or `investigation_engine_readonly` if the agent should only
read, validate and look up (no start, delete, wave, test or save). See [MCP Tools](mcp.md)
for the tool list and how to connect.

**With the CLI.** The `limacharlie investigate` command group offers the same
operations. See [CLI](cli.md).

Give the agent's API key only what the workflow needs:

| To do this | The key needs |
|---|---|
| Read the kit, operators, packs and templates, validate a template | `investigation.get`, `insight.evt.get` |
| Test a template on past alerts | `investigation.set`, `investigation.get`, `insight.evt.get` (starting the test needs the first, polling its result the second) |
| Start a run or a wave | `investigation.set`, `insight.evt.get` |
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
| As needed | `policy` | small | The budgets a plan must fit and each action class's autonomy mode. Worth fetching when you plan `act` entries. |
| For one-off questions, or reusable bundles | `packs` | small | The fact packs. |

Ask the agent to read the guide first. The guide the kit returns is the same text
the engine's tests check its examples against.

## 2. Look at real alerts

Before writing, have the agent list the detections of the category you want to
cover, their cases, and how analysts classified them. A template written from a
handful of real alerts is far better than one written from the category name alone.
Note which fields the detections actually carry.

## 3. Draft a small template

Follow [How to Think About Templates](how-to-think-about-templates.md): write the
analyst's questions, then the rules that decide, cheapest first. Start with three to
six steps and one or two rules on each side. Use `starts_from: detection` and derive
everything else with steps (see
[Where a run starts](templates.md#where-a-run-starts-starts_from)).

A first draft for rare processes:

<!-- validate: template -->
```yaml
description: "Rare process: a banned binary escalates; a command the AI judges malicious on a busy host escalates where the policy allows."
version: 1
applies_to:
  detect_cat: ['rare-process']
starts_from: detection
gather:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
  related:
    op: detection.list
    args: {sids: ['$trigger.sid'], window: [-7d, now]}
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [trigger.command_line]
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary is on our banned software list."
    - id: judged_malicious_on_busy_host
      when: ['cmd.label == "yes"', 'related.count >= 5']
      say: "The command was judged malicious on a host that raised {related.count} detections this week."
act:
  - {class: contain.network, target: '$trigger.sid', on: [banned_binary]}
case:
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, default: medium}
```

Why it looks like this:

- `banned` is a Lookup read: exact, cheap, and the organization's own. It is the
  first rule.
- `cmd` is the only AI step, and it sees one field. `judged_malicious_on_busy_host`
  reads it, so it is **AI-assisted**: with the policy's AI switch off for this
  template, it recommends instead of deciding.
- There is no close rule yet. Nothing here is positive benign evidence, and "the AI
  said no" alone should not close an alert. Runs where no rule holds end
  `couldnt_tell` (there is no review yet), which is honest; when the AI-assisted rule
  holds, the run ends `ai_recommends_malicious`.
- `act` proposes isolation only on the deterministic rule. The policy decides whether
  that proposal is only suggested, needs approval or runs.

## 4. Validate

Validation type-checks the template against the organization's real operator
catalog and returns coded issues:

```text
errors:
  - code: window_outside_free_range
    path: gather.related.args.window
    message: window starts earlier than 30 days ago: searches must stay inside the free time range
  - code: unknown_field
    path: rules.escalate[1].when
    message: 'related.cont: the fact has no field "cont" (did you mean "count"?)'
    suggestion: count
```

Fix the errors first. Then read the **warnings**: they pass validation but make a
template useless. Typical ones are `unused_step`, `operator_denied`,
`rule_never_holds` and `act_class_off`. The report lists the AI-assisted rules in
`ai_rules`, and estimates the worst case of one run, so the agent can see before
testing whether the template fits the policy's budgets.

## 5. Test on past alerts

Run the template on 10 to 25 real past alerts, including closed cases classified each
way. A test is read-only and writes nothing but its own result.

The test returns a result per sample (the outcome, the deciding rule or the AI's
recommendation, what was missing, the cost, and whether the rule and the AI agreed
with the analysts) and a summary. Read it like this:

- **`decided_by_rules`** says how much the rules carry. Few means a deciding fact is
  missing from the rules.
- **`rules.<id>.disagree`** is worth reading sample by sample. Which step misled the
  rule? Tighten the rule's condition, or drop the rule.
- **`ai`** says how the AI's recommendation fared on what the rules left open. A
  pattern the AI keeps recommending correctly is a candidate for a rule.
- **`unknown_reasons`** tells you what to fix: `forbidden` is a permission,
  `not_found` on a Lookup is a list that does not exist yet, `index_lag` is a window
  that ends too close to now.

## 6. Refine and test again

Suppose the test shows that most `rare-process` alerts in this organization come from
an approved software updater, and the analysts closed every one of them as a false
positive. The template could not close them. Add the organization's approved software
list, a check of the file on the host, a close rule on both, and an AI review for what
the rules leave open:

<!-- validate: template -->
```yaml
description: "Rare process: our banned and approved lists and the file on the host decide; otherwise the AI review recommends."
version: 2
applies_to:
  detect_cat: ['rare-process']
starts_from: detection
gather:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
  approved:
    why: "Is this binary on our approved software list?"
    op: lookup.get
    args: {name: approved-software, keys: ['$trigger.hash']}
  live_file:
    why: "Is the file on the host the approved one, and is it signed?"
    ask: "Can someone check the file on this host? The sensor could not be read."
    op: sensor.read.file_hash
    args: {sid: '$trigger.sid', path: '$trigger.file_path', hash: '$trigger.hash'}
    only_if: 'approved.found'
  related:
    op: detection.list
    args: {sids: ['$trigger.sid'], window: [-7d, now]}
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [trigger.command_line]
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary is on our banned software list."
    - id: judged_malicious_on_busy_host
      when: ['cmd.label == "yes"', 'related.count >= 5']
      say: "The command was judged malicious on a host that raised {related.count} detections this week."
  close:
    - id: approved_and_signed
      when: ['approved.found', 'live_file.matches', 'live_file.verified']
      say: "The binary is on our approved software list, and the file on the host is that file, signed and verified."
ai_review:
  question: "Is this process activity malicious? Judge the command, the host's other alerts and the parent process; say what in the evidence shows it."
  sees: [trigger, related]
  needs: [trigger]
act:
  - {class: contain.network, target: '$trigger.sid', on: [banned_binary]}
case:
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, closed_by_rule: low, default: medium}
```

Test again on **the same samples**, so the comparison is fair. Most of the updater
alerts should now be `closed_by_rule` by `approved_and_signed`, and the agreement of
that rule with the analysts is the number to check.

General advice for refining:

- Start from the decision, not the data. Ask what would let an analyst close or
  escalate this alert, then gather only that.
- A close rule needs positive benign evidence: a list entry, a verified signature, a
  known sender. "Nothing found" never closes, and the engine enforces it.
- Prevalence ("seen on many hosts") is a lower bound, and the engine never closes on
  it: a worm is on many hosts too. Let the AI review read it instead.
- Drop a step nothing reads (`unused_step`). Put an `only_if` on an expensive step that
  matters only in some cases.
- Ask the AI only what a list or an indexed read cannot answer exactly, and show it
  only the fields it needs.

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
template covers, how many samples it ran on, how many the rules decided and how each
rule agreed with the analysts, how the AI's recommendations fared on the rest, what
stayed unknown and why, what it would propose, and what it costs per run.

## 8. A person promotes

A person opens the draft in the [console](console.md#templates), reads the template
and the test summary, tests it once more if needed, and sets `status: active`. At that
point:

- a D&R rule can start it;
- `applies_to` can pick it automatically;
- it acts within the [autonomy policy](policies.md), which is a separate decision;
- its AI-assisted rules and its AI review still only recommend, until a person turns
  on [AI may decide](policies.md#what-the-ai-may-decide) for it. That is a third
  decision, and the agent never makes it.

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
3. Draft a SMALL template: 3 to 6 steps, starts_from: detection, everything else
   derived with steps. Write the deciding rules first, cheapest first, on the
   organization's own Lookups where you can. Add an ai_review only for what rules
   cannot decide.
4. Validate it until there are no errors, then fix the warnings that matter.
5. Test it on 15 to 25 samples that include closed cases of both classifications.
   Report how many the rules decided, each rule's agree/disagree, the AI's record on
   the rest, the unknown reasons, and cost.
6. Refine at most three times, testing the same samples each time.
7. Save the best version as a draft. You cannot activate it.
8. Finish with a summary for the person who will promote it.

Rules: unknown is never false; a close rule needs positive, complete benign
evidence, never "nothing found"; keep every window within 30 days; never guess a
field name, read it from the operator catalog; never change the policy.
```

## Common mistakes

| Mistake | What happens |
|---|---|
| Reading `$hash` or `$sid` as an input | The starting point does not provide it: validation fails with `unknown_reference`. Derive it from `detection.get`, or read a caller's value as `$?hash` through `plan.pick`. |
| Writing the earlier format (`facts`, `proofs`, `evidence`, `respond`) | Validation fails with `legacy_template_format`. Use `gather`, `rules`, `ai_review` and `act`. |
| A close rule on absence ("nothing found") or on incomplete data | The rule never holds. Use positive benign evidence, or accept `couldnt_tell`. |
| A signal with no `benign_when`, then a close on `signals.all_explained` | The signal can never be explained, so nothing closes while it fires. |
| An `act` entry on a rule that is not first to hold | Only the deciding rule's entries fire. Put the most specific rule first. |
| Guessing a field name | Validation fails with `unknown_field` and a suggestion. |
| A window older than 30 days | Validation fails with `window_outside_free_range`. |
| Proposing a class the policy has `off` | The action is never proposed (`act_class_off`). |
| Writing a template for a one-off question | Use a [wave](concepts.md#waves-and-fact-packs). Write a template only when the same alert comes back. |
