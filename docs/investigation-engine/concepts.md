# Concepts

This page defines the words the rest of the Investigation Engine documentation
uses.

## The pieces

| Object | Stored as | What it is |
|---|---|---|
| **Plan template** | Hive record `investigation_plan/<name>` | A reusable plan for a class of alerts: the facts to gather, the proofs that settle a verdict, how weaker evidence moves the probability, and the actions to propose. See [Plan Templates](templates.md). |
| **Policy** | Hive record `investigation_policy/<name>` | What the engine may do: budgets, allowed operators, autonomy per action class, approvers, the identity runs execute as. See [Policies and Autonomy](policies.md). |
| **Run** | Engine store | One investigation: its inputs, the effective policy, state, evidence graph, steps, actions and verdict. |
| **Step** | Part of a run | One operator call (one way of obtaining a fact), with its timing, cost and outcome. |
| **Fact** | Part of a run | A typed result of a step, with its provenance. A fact is `ok`, `unknown` (with a reason) or `incomplete`. |
| **Action** | Part of a run | A containment, eradication or collection step with a target, a class, a state and, for reversible ones, a lease. |
| **Operator** | Built into the engine | One way to obtain a fact or perform an action: an entity lookup, a search, a sensor read, a threat-intel lookup, an LLM judgement. The org's operator list shows which ones your policy allows. |

## Facts, signals and proof

A template lists **facts**. Each fact is one operator call whose arguments can
refer to run inputs and to other facts. A fact that reads another fact waits for
it. Every other fact starts immediately, in parallel.

```yaml
facts:
  trigger:                    # the detection record itself
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  host:                       # waits for `trigger`, reads its `sid`
    op: entity.resolve
    args: {type: sensor_id, value: $trigger.sid}
  related:                    # also waits for `trigger`; runs in parallel with `host`
    op: detection.list
    args: {sids: [$trigger.sid], window: [-7d, now]}
```

**Proofs** are conditions over facts that settle the verdict. A proof is a list of
alternatives (any one completing is enough); each alternative is a condition or
an `all` / `any` group of conditions:

```yaml
proofs:
  false_positive:
    - 'related.count <= 1 and judge.label == "no"'
  true_positive:
    - all: ['judge.label == "yes"', 'related.count >= 5']
```

**Evidence** is the softer path. When no proof completes, each `evidence` rule
whose condition is true adds its `weight` (a log-odds value; negative favors a
false positive) to the template's `prior`. The result is the probability of a
true positive, `P(TP)`.

**Signals** apply to detections that carry several reasons for firing, such as an
email detection. Each signal that fired is given a question, a condition under
which it is *malicious* (holds) and one under which it is *benign* (explained).
`signals.all_explained` is a common backbone of a false-positive proof.

### How a verdict is reached

| Outcome | When |
|---|---|
| `true_positive` | A true-positive proof completes, or the evidence alone brings `P(TP)` to the policy's `escalate_at` (0.90 by default). |
| `false_positive` | A false-positive proof completes, or the evidence alone brings `P(TP)` to `dismiss_at` (0.03) or below and nothing is left to run. **Both paths wait for the required checks** (`mandatory_checks` of the run's urgency): while one is unknown or unfinished, the run cannot be dismissed, and if it stays unknown after everything has run, the run ends `inconclusive`. |
| `inconclusive` | Nothing more can be learned and neither side was reached. The case lists what stayed unknown and asks one open question. |

When a proof completes, the engine **cancels every step that can no longer matter**
and records why. This is where most of the time saved comes from.

## Unknown, absent and incomplete

A fact has one of three conditions:

| Condition | Meaning |
|---|---|
| **ok** | The operator answered and the answer is complete. |
| **unknown** | There is no answer. The fact has a `reason` such as `timeout`, `forbidden`, `not_found`, `policy_denied`, `missing_input` or `outside_free_window`. |
| **incomplete** | There is an answer, but it may be missing data: a truncated list, a search over the last few minutes (`index_lag`), a window clamped to the free time range. |

The engine uses three-valued (Kleene) logic, and this is the rule behind every
proof:

- A comparison on an unknown fact is **unknown, never false**. `not unknown` is
  unknown. `unknown and false` is false, and `unknown or true` is true.
- A proof completes only when its expression is **true**. A fact that is unknown
  can never complete a proof.
- An **incomplete** fact supports only answers that can only get stronger with
  more data: `count > 0`, `found`, `x in list`. A claim of absence (`found == false`,
  `count == 0`) on an incomplete fact is unknown.

So "no click was seen" proves nothing until the data it rests on is complete.
**Inconclusive is a good answer when data is missing.** The case says what could not
be established and why. See [Writing templates](templates.md#proofs-evidence-and-signals) for
how to write conditions that respect this.

## Runs

### States and phases

A run is `queued`, `running`, `decided`, `completed`, `cancelled`, `failed` or
`budget_exhausted`. While it runs it moves through phases that overlap:

1. **Triage** looks for the shortest proof of true or false positive.
2. **Scoping** gathers the facts the template lists under `scope` (see
   [Plan Templates](templates.md#scope)). In the `balanced` and `aggressive`
   speculation profiles it starts once `P(TP)` passes the policy's `scope_at` bar, usually
   before the verdict is final. In the `conservative` profile it waits for a decided
   true positive. The template names every fact to gather: the engine does not discover
   new entities or generate searches of its own.
3. **Containment** proposes actions as the facts they depend on arrive and executes
   them according to policy once their confidence bar is met. That can happen before the
   verdict is final: see [Respond](templates.md#respond-and-report).

`decided` means the verdict is final while scoping or actions may still be running.
A run is `completed` when its steps are done and every action is settled.

### Modes and urgency

A run starts in one of three modes: `triage` (stop at the verdict), `full` (triage,
scoping and containment) or `scope` (skip triage, for a confirmed incident).
`urgency` (`low`, `medium`, `high`, `critical`) selects how aggressively the engine
spends parallel work: a *speculation profile* of `conservative`, `balanced` or
`aggressive`. A typical policy, like the example in [Policies and Autonomy](policies.md#a-default-policy),
maps `low` to conservative, `medium` to balanced and `high` and `critical` to aggressive. If you do not set an urgency, the engine
derives it from the detection priority and the severity (priority 8 or more, or severity `critical`, is `critical`; 6 or more, or `high`, is `high`; 3 or more, or `medium`, is `medium`; anything lower is `low`) and falls back to `medium` when the start carries neither. Tags do not change the urgency; the trigger's tags can match a run-scoped [policy record](policies.md#two-match-scopes) that tightens the run.

### Coalescing and idempotency

A start that carries a `coalesce_key` **joins the open run that has the same key**
instead of starting a second run, and its inputs are added to that run. Nothing joins
runs merely because they concern the same entity: without a `coalesce_key` every start
is its own run. The key only matches within the same organization, the same starter
and the same run identity, so a start by a person and a start by a D&R rule never join
each other, and a request that executes as a different identity never joins a run
executing as this one. All D&R rules share one starter per organization, so alerts from different rules
with the same key do join.

An `idempotency_key` makes a repeated start with the same starter return the same run.
For runs started by a D&R rule, the detection id is the idempotency key, so one
detection starts one run, within the retention of the engine's records.

### Identity

Every read a run makes and every action it takes is authorized as the run's
identity, so a run can never read or do what its identity cannot.

- A run started by a person or an API key uses the identity the policy names
  (`identity.default`), unless the request picks `caller` and the policy allows it. With
  no policy identity, it uses that person's (or API key's) token. **A policy secret can
  hold more permissions than the person who starts the run.**
- A run started by a D&R rule or a new case has no person. It needs an identity
  named in the org's policy: an **organization API key** stored as a Hive secret,
  set as `identity.default` or, for one template, as that template's own
  `identity.templates.<name>.default`. Without one, the start is refused with a
  message that names the missing setting.
- A run that must work for hours (a lease, a delayed approval) should use a secret
  identity. A run on a person's token cannot schedule work that outlives that token,
  so its leases are shortened to fit.

See [Policies and Autonomy](policies.md#run-identity).

### The free time range

Every search a run makes must start no earlier than **now minus 30 days**. A
template that asks for older data is rejected when it is validated. A window that
still reaches past the boundary when it runs is clamped to it, and the result is
marked incomplete or unknown (`outside_free_window`), never "nothing found".
A policy can lower the lookback below 30 days, never raise it.
Operators that bill per use, such as artifact collection, are off in the default
policy.

### What a run costs

- **Searches** stay inside the free time range, so they are free of search charges.
- **Language-model judgements** (`llm.judge`) go through your organization's AI agent
  configuration, which decides the model and credentials. The usage is reported as AI
  usage and billed with your other AI usage, under the feature
  `investigation_engine`, with the run id as the reference. The policy's
  `max_llm_usd_per_run` budget **stops the run from launching further judgements** once
  the cost already recorded reaches it. It is not a hard cap on spend: the engine does
  not reserve the cost of a judgement before it runs, so a judgement already in flight
  (or several launched together) can take the run past the budget. The dollar figures
  come from the engine's configured prices, and a judgement billed with no known price
  adds nothing to the dollar total, so it never counts against the budget. The spend a
  run reports is therefore a lower bound, and a judgement cut short by a deadline or a
  cancel can still be billed.
- **Operators that bill per use**, such as artifact collection and some extensions, are
  off in the default policy. An organization enables them by policy.

### The case

Each run writes a [case](../5-integrations/extensions/limacharlie/cases.md) by
default. An engine-written case contains the triggering detections, a plain-language
summary with the verdict and proof (each claim cites a fact), entities and
telemetry with a verdict and a reason each, the unknowns that mattered, the actions
proposed, approved, executed and reverted with who decided, severity, status, tags
and a classification, and a link back to the run.

Because every engine case has the same structure, what people do to it is
**feedback**: closing it unchanged weakly confirms the verdict, changing its
classification or an entity verdict corrects it, and approving or denying an action
labels that action. The engine records these against the run, the template version
and the facts involved.

## Waves and fact packs

A template is for an alert that comes back. A one-off question ("what did this host
do after that download?", "who else received this message?") does not need one.

A **wave** is a batch of operator calls, or fact packs, that the engine runs now,
in parallel, and returns compact answers for. It has no plan and no verdict, but
the engine still batches, caches, enforces the free time range and applies policy.
A wave can reference earlier steps of the same wave, can `select` just the fields
you need, and can stop early with `stop_when` conditions that follow the same
unknown-is-never-false rule as proofs.

A **fact pack** is a named, tested bundle of facts with parameters and described
exports. The engine has these built in: `detection_context`, `domain_reputation`,
`hash_spread`, `host_context`, `message_outcome`, `org_roster`, `process_tree`,
`sender_reputation` and `user_activity`. A pack can be used in a wave or as a fact
(`use:` instead of `op:`) in a template, where it expands into ordinary facts named
`<id>__<fact>`.

Waves are what an AI agent uses to answer a question in three or four calls instead
of thirty. See [MCP Tools](mcp.md) and [API Reference](api-reference.md#waves).

## Draft and active templates

A template carries `status: draft` (the default) or `status: active`.

| | Draft | Active |
|---|---|---|
| Can a person start a run on it? | Yes | Yes |
| Autonomy | Capped at `suggest` for every action class | As the policy says |
| Can a D&R rule or the case trigger start it? | No | Yes |
| Picked automatically by `applies_to`? | No | Yes |

**A person promotes a draft** by setting `status: active` in the Hive record. None of
the AI-agent tools can do it, and by default the Hive refuses it from an API key (see
[Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)).
