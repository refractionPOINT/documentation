# Concepts

This page defines the words the rest of the Investigation Engine documentation
uses.

## The pieces

| Object | Stored as | What it is |
|---|---|---|
| **Plan template** | Hive record `investigation_plan/<name>` | How to investigate one kind of alert: the steps to gather, the rules that decide, an optional AI review, and the actions to propose. See [Plan Templates](templates.md) and [How to Think About Templates](how-to-think-about-templates.md). |
| **Policy** | Hive record `investigation_policy/<name>` | What the engine may do: budgets, allowed operators, autonomy per action class, what the AI may decide per template, approvers, the identity runs execute as. See [Policies and Autonomy](policies.md). |
| **Run** | Engine store | One investigation: its inputs, the effective policy, state, steps, actions and outcome. |
| **Step** | Part of a run | One operator call (or one fact pack), with its timing, cost, status and three sentences: why it ran, what it found and what used it. |
| **Rule** | Part of a template | A condition over steps that decides: an `escalate` rule or a `close` rule, with an id and a sentence for the case. |
| **Action** | Part of a run | A containment, eradication, tagging or close step with a target, a class, a state and, for reversible ones, a lease. |
| **Operator** | Built into the engine | One way to obtain an answer or perform an action: an entity lookup, a search, a Lookup read, a sensor read, a threat-intel lookup, an AI question. The org's operator list shows which ones your policy allows. |

## Gather, rules and the AI

A template lists the steps to **gather**. Each step is one operator call whose
arguments can read the run's inputs and other steps. A step that reads another waits
for it. Every other step starts at once, in parallel.

```yaml
starts_from: detection
gather:
  trigger:                    # the detection record itself
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:                     # waits for `trigger`, reads its hash
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
  related:                    # also waits for `trigger`; runs in parallel with `banned`
    op: detection.list
    args: {sids: ['$trigger.sid'], window: [-7d, now]}
    only_if: 'not banned.found'   # only worth a search when the binary is not banned
```

**Rules** decide. An `escalate` rule decides as soon as it holds. A `close` rule
decides once it holds on complete answers and nothing blocks a close. Each rule has
an `id`, a condition (`when`) and a sentence (`say`) the case leads with:

```yaml
rules:
  escalate:
    - {id: banned_binary, when: 'banned.found', say: "The binary is on our banned software list."}
  close:
    - id: approved_and_signed
      when: ['approved.found', 'file_on_host.matches', 'file_on_host.verified']
      say: "The binary is on our approved list, and the file on the host is that file, signed and verified."
```

As soon as a rule decides, the engine **cancels every step that can no longer
change the outcome or an action that can still fire** and records why. This is where most of the time saved comes
from.

**The AI** takes part in two ways, and by default both only recommend:

- An **`ask_ai` step** asks one focused question about what other steps gathered
  ("is this command line malicious?"). Its answer is `yes`, `no` or `unclear`, with a
  self-rated confidence and a short rationale. A rule that reads it, directly or
  through another step, is **AI-assisted**.
- The **AI review** (`ai_review`) is the fallback. It runs only when no rule decided
  and nothing relevant is left to gather. It reads the steps it is given and answers
  malicious, benign or unclear, citing what it used.

The organization's policy says, per template, whether the AI may decide alone
(`ai_may_decide`: `off`, `escalate` or `close_and_escalate`). It is `off` by default.
An AI-assisted rule or the review then produces a **recommendation**, and a person
decides. See [What the AI may decide](policies.md#what-the-ai-may-decide).

**Signals** apply to detections that carry several reasons for firing, such as an
Email Security detection. `explain_signals` gives each reason a question, a condition
under which it is benign (`benign_when`) and one under which it is malicious
(`malicious_when`). Every reason that fired must be explained benign before anything
closes, and a reason whose malicious condition holds blocks every close.

## Outcomes

Every run ends with one outcome. It is the run's `verdict.outcome`; `verdict.label`
is derived from it.

| Outcome | Meaning | `label` |
|---|---|---|
| `closed_by_rule` | A close rule decided. | `false_positive` |
| `escalated_by_rule` | An escalate rule decided. | `true_positive` |
| `closed_by_ai` | An AI-assisted close rule or the AI review decided, because the policy lets the AI close for this template. | `false_positive` |
| `escalated_by_ai` | An AI-assisted escalate rule or the AI review decided, because the policy lets the AI escalate for this template. | `true_positive` |
| `ai_recommends_benign` | The AI recommends closing. Nothing is acted on; a person decides. | `inconclusive` |
| `ai_recommends_malicious` | The AI recommends escalating. Nothing is acted on; a person decides. | `inconclusive` |
| `couldnt_tell` | No rule decided and the AI did not answer either way. The run lists what was missing and why. | `inconclusive` |
| `conflict` | An escalate rule and a close rule hold at once, or an AI-assisted rule recommends against a deterministic rule of the other side. A person decides; fix the rules. | `inconclusive` |

The outcome travels with what is behind it:

```json
"verdict": {
  "outcome": "closed_by_rule",
  "label": "false_positive",
  "decided": true,
  "decided_by": {"kind": "rule", "rule": "approved_and_signed", "say": "The binary is on our approved list, and the file on the host is that file, signed and verified."},
  "recommendation": null,
  "missing": [],
  "unknowns": []
}
```

- `decided_by` names what decided: `kind` is `rule`, `ai_rule` (an AI-assisted rule)
  or `ai_review`, with the rule id and its rendered sentence.
- `recommendation` is set when the AI recommends: `label` (`benign`, `malicious` or
  `unclear`), `self_rated_confidence` (shown, never used), `rationale`, `citations`
  (the step fields it used) and `by` (the rule id or `ai_review`).
- `also_held` (omitted when empty) lists the other escalate rules that held after an
  escalation. The first escalate rule that held decides and never moves; each rule in
  `also_held` fires its own `act` entries.
- `missing` lists, when nothing decided, each step that stayed unknown: `step`,
  `reason`, `needed_by` (the rules or the review that needed it) and `ask` (the
  question for a person, from the step's `ask:`).

**`couldnt_tell` is a good answer when data is missing.** The case says what could
not be established and why, and asks the question a person can answer.

## Unknown is never false

A step ends in one of four states:

| Status | Meaning |
|---|---|
| `ok` | The operator answered. The answer is **complete**, or **incomplete** when it may be missing data: a truncated list, a search over the last few minutes (`index_lag`), a lower bound. |
| `unknown` | There is no answer. The step has a `reason` such as `timeout`, `forbidden`, `not_found`, `policy_denied`, `llm_agent_not_found` or `outside_free_window`. |
| `skipped` | Its `only_if` was false (`only_if_false`), a step its condition reads failed (`condition_unknown`), or it reads a skipped step (`dependency_skipped`). A skipped step reads as unknown. |
| `cancelled` | A rule decided and the step could no longer change the outcome, or the run was cancelled. |

The engine uses three-valued (Kleene) logic, and this is the rule behind every
decision:

- A comparison on an unknown step is **unknown, never false**. `not unknown` is
  unknown. `unknown and false` is false, and `unknown or true` is true.
- A rule decides only when its condition is **true**. An unknown answer can never
  make a rule hold.
- An **escalate** rule reads an incomplete answer for what it shows: `count > 0`,
  `found`, `x in list` are true as soon as the data shows them. A claim of absence
  (`found == false`, `count == 0`) on an incomplete answer is unknown.
- A **close** rule decides only on complete answers. A lower bound ("seen on 50+
  hosts") or a derived value never closes anything.

So "no click was seen" proves nothing until the data it rests on is complete. See
[How to Think About Templates](how-to-think-about-templates.md) for how to write rules
that respect this.

## Runs

### States and phases

A run is `queued`, `running`, `decided`, `completed`, `cancelled`, `failed` or
`budget_exhausted`. While it runs it moves through phases that overlap:

1. **Triage** gathers what the rules read, and stops as soon as one decides.
2. **Scoping** gathers the steps the template lists under `scope.from` (who else,
   what else). It starts only once a rule, or the AI where the policy allows it,
   escalated. The template names every step: the engine does not discover new
   entities or generate searches of its own.
3. **Containment** proposes the `act` entries of the rule that decided and executes
   them according to policy. A recommendation proposes nothing but the case close
   a person can confirm. See [Act](templates.md#act).

`decided` means the outcome is final while scoping or actions may still be running.
A run is `completed` when its steps are done and every action is settled.

### Modes and urgency

A run starts in one of three modes: `triage` (stop at the outcome), `full` (triage,
scoping and containment) or `scope` (skip triage, for a confirmed incident).
`urgency` (`low`, `medium`, `high`, `critical`) selects how aggressively the engine
spends parallel work: a *speculation profile* of `conservative`, `balanced` or
`aggressive`. The platform default, which a policy's `speculation` section can change,
maps `low` to conservative, `medium` to balanced and `high` and `critical` to aggressive. If you do not set an urgency, the engine
derives it from the detection priority and the severity (priority 8 or more, or severity `critical`, is `critical`; 6 or more, or `high`, is `high`; 3 or more, or `medium`, is `medium`; anything lower is `low`) and falls back to `medium` when the start carries neither. Tags do not change the urgency; the trigger's tags can match a run-scoped [policy record](policies.md#two-match-scopes) that tightens the run.

### Coalescing and idempotency

A start that carries a `coalesce_key` **joins the open run that has the same key**
instead of starting a second run, and its inputs are added to that run. Nothing joins
runs merely because they concern the same entity: without a `coalesce_key` every start
is its own run. The key only matches within the same organization, the same starter
and the same run identity, so a start by a person and a start by a D&R rule never join
each other, and a request that executes as a different identity never joins a run
executing as this one. All D&R rules on detections share one starter per organization,
so alerts from different rules with the same key do join; rules on cases have a starter
of their own.

An `idempotency_key` makes a repeated start with the same starter return the same run.
A D&R rule sets both keys for you: on a detection the idempotency key is the detection
id and the coalesce key defaults to `sid:<sensor id>`; on a case they are
`case:<number>:<rule>` and `case:<number>`. See [Automatic Starts](automation.md).

### Identity

Every read a run makes and every action it takes is authorized as the run's
identity, so a run can never read or do what its identity cannot.

- A run started by a person or an API key uses the identity the policy names
  (`identity.default`), unless the request picks `caller` and the policy allows it. With
  no policy identity, it uses that person's (or API key's) token. **A policy secret can
  hold more permissions than the person who starts the run.**
- A run started by a D&R rule (on a detection or on a new case) has no person. It needs an identity
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
- **AI calls** (`ask_ai` steps and the AI review) run on the organization's
  `ai_agent` record that the policy's `llm.agent` names, or the record named
  `investigation-judge` when the policy names none. The record decides the model and
  the provider credentials: your provider bills those tokens. The usage is also
  reported with the organization's other AI usage, under the feature
  `investigation_engine`, with the run id as the reference. The policy's
  `max_llm_usd_per_run` budget **stops the run from launching further AI calls** once
  the cost already recorded reaches it. It is not a hard cap: a call already in
  flight (or several launched together) can take the run past it, and a call with no
  known price adds nothing to the recorded cost.
- **Operators that bill per use**, such as artifact collection and some extensions, are
  off in the default policy. An organization enables them by policy.

### The case

Each run writes a [case](../5-integrations/extensions/limacharlie/cases.md) by
default. An engine-written case leads with the outcome sentence: the deciding
rule's `say`, or the AI's recommendation and what was missing. It then lists the
fired signals and how each was answered, the triggering detections, the evidence
(each step a rule or the review read that answered, with its sentence), what stayed
unknown and why, the open question for a person (a missing step's `ask`), the actions
proposed, approved, executed and reverted with who decided, severity (by outcome, as
the template's `case.severity` says), status, tags and a classification, and a link
back to the run.

People's edits of an engine case (closing it, changing its classification, a note)
are not read by the engine and change nothing it does. A person can submit an explicit
label on a run (`POST /runs/{id}/labels`); labels are stored with the run and read back,
and no decision reads them.

## Waves and fact packs

A template is for an alert that comes back. A one-off question ("what did this host
do after that download?", "who else received this message?") does not need one.

A **wave** is a batch of operator calls, or fact packs, that the engine runs now,
in parallel, and returns compact answers for. It has no rules and no outcome, but
the engine still batches, caches, enforces the free time range and applies policy.
A wave can reference earlier steps of the same wave, can `select` just the fields
you need, and can stop early with `stop_when` conditions that follow the same
unknown-is-never-false rule as rules.

A **fact pack** is a named, tested bundle of steps with parameters and described
exports. The engine has these built in: `app_control_context`, `cloud_audit_context`,
`cloud_exposure_path`, `cloud_finding_context`, `cloud_resource_exposure`,
`container_context`, `detection_context`, `domain_reputation`, `hash_spread`,
`host_context`, `host_vulnerability_exposure`, `identity_signins`, `message_outcome`,
`org_roster`, `process_lineage`, `process_tree`, `saas_admin_actions`,
`sender_reputation` and `user_activity`. `GET /packs` (or `investigate_packs`) lists
them with their parameters and exports. An organization can add its own packs as
`investigation_pack` Hive records; templates and waves `use:` them like the built-in
ones. Like an active template, an organization pack can only be written by a person
(or by an API key when the organization opted out), so an AI agent's key cannot change
what an active template runs by replacing a pack. A pack can be used in a wave or as a step
(`use:` instead of `op:`) in a template, where it expands into ordinary steps named
`<id>__<step>` (`host__card`), which rules read like any other step.

Waves are what an AI agent uses to answer a question in three or four calls instead
of thirty. See [MCP Tools](mcp.md) and [API Reference](api-reference.md#waves).

## Draft and active templates

A template carries `status: draft` (the default) or `status: active`.

| | Draft | Active |
|---|---|---|
| Can a person start a run on it? | Yes | Yes |
| Autonomy | Capped at `suggest` for every action class | As the policy says |
| Can a D&R rule start it? | No | Yes |
| Picked automatically by `applies_to`? | No | Yes |

**A person promotes a draft** by setting `status: active` in the Hive record. None of
the AI-agent tools can do it, and by default the Hive refuses it from an API key (see
[Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)).
