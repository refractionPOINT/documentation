# Concepts

## The pieces

| Piece | What it is |
|---|---|
| **Template** | A Hive record (`investigation_plan`) for one kind of alert: steps to gather, rules that decide, optional AI, actions, the case. [Plan Templates](templates.md). |
| **Check** | A template other templates call (`kind: check`) for logic they share. It returns a verdict and never acts. |
| **Fact pack** | A tested bundle of steps (host context, process tree, hash spread, ...) a template or a wave uses with `use:`. |
| **Run** | One investigation of one alert, case, entity or question by one template. |
| **Step** | One operator call, pack, check, Playbook or AI agent inside a run. Its answer is a **fact**. |
| **Action** | What an `act` entry does when its rule decides: isolate, tag, quarantine, close, run a Playbook, send an extension request. [Actions](actions.md). |
| **Settings** | The one record (`investigation_policy/default`) for what belongs to no single template: pause, circuit breaker, identity, budgets, limits. [Settings](settings.md). |
| **Run queue** | Where every start waits for a slot. [The Run Queue](run-queue.md). |

## Gather, decide, act

A run:

1. **gathers**: every step whose inputs are ready starts at once, in parallel; a step that
   reads another waits for it;
2. **decides**: after each answer, the rules are evaluated. An escalate rule decides as soon
   as it holds; a close rule decides once it holds on complete answers. Steps that can no
   longer change the outcome are cancelled;
3. **acts**: the `act` entries that name the deciding rule fire, each acting on its own or
   waiting for a person as its `approval` says;
4. **writes the case** and ends.

The AI answers focused questions (`ask_ai`) and, when no rule decided, reviews the evidence
(`ai_review`). It decides only where the template's `ai_may_decide` lets it; otherwise it
recommends and a person decides. The engine, not the AI, decides what runs next, what can be
skipped and when to stop.

## Outcomes

Every run ends with one outcome (`verdict.outcome`; `verdict.label` follows from it):

| Outcome | Meaning | `label` |
|---|---|---|
| `escalated_by_rule` | an escalate rule decided | `true_positive` |
| `closed_by_rule` | a close rule decided | `false_positive` |
| `escalated_by_ai` | an AI-assisted rule or the review escalated, as `ai_may_decide` allows | `true_positive` |
| `closed_by_ai` | an AI-assisted rule or the review closed, as `ai_may_decide` allows | `false_positive` |
| `ai_recommends_malicious` | the AI recommends escalating; a person decides | `inconclusive` |
| `ai_recommends_benign` | the AI recommends closing; a person decides | `inconclusive` |
| `couldnt_tell` | no rule decided and the AI did not answer either way | `inconclusive` |
| `conflict` | rules on both sides held at once | `inconclusive` |

`verdict.decided_by` names what decided (`{kind: rule | ai_rule | ai_review, rule, say}`).
`verdict.missing` lists the steps that stayed unknown, why, and which rules needed them. A
recommendation carries the AI's `label`, `self_rated_confidence` (shown, never used) and
`rationale`.

## Unknown is never false

A step is **ok**, **unknown** (with a `reason`: `timeout`, `forbidden`, `not_found`,
`acl_restricted`, `only_if_false`, ...) or **incomplete** (ok but possibly missing data:
`truncated`, `index_lag`, a lower bound). An unknown step never reads as "nothing found". An
absence on incomplete data never closes an alert. A close never rests on a step that did not
answer. See [Templates](templates.md#unknown-is-never-false).

## Runs

### How a run starts

| Started by | Has |
|---|---|
| A D&R rule's [`start investigation`](automation.md) | the detection the rule reported, the rule's inputs; no person |
| A D&R rule on a new case | the case; no person |
| A person: console, CLI, API, MCP | a detection, case, entity or question; the person is the caller |
| The engine, at a lease end | a "check again" run (`kind: lease_check`) |

Every start but the last goes through the [run queue](run-queue.md).

### States

`queued` (waiting for a slot), `running`, `decided` (it decided and waits for an action to
settle, for example an approval), `completed`, `cancelled`, `failed`, `budget_exhausted`,
and for a start that never ran, `flushed` and `capped`. `phase` says where a running run is
(gathering, deciding, containment).

### Coalescing and idempotency

Alerts on the same sensor while a run of the same template is open join that run
as extra alerts (`coalesce: sensor`, the default; `off` gives one run per alert). The run keeps
investigating the alert it started on: a joined alert is counted and attached to the case,
and no step reads it. A repeated start with the
same idempotency key returns the run it already has. A D&R rule starts at most one run per
detection and rule.

### Identity

Every read a run makes and every action it takes is authorized as the run's **identity**:
the key the settings name for its template (`identity.default` or a per-template key), or,
for a person's start where the settings allow it, the person's own token. A run with no
person behind it always uses a key. The key's own permissions are the limit on what the run
can do. See [Settings](settings.md#identity) and [Permissions](permissions.md).

### The free time range

No search window of a run starts earlier than now minus 30 days (the settings'
`budgets.lookback_days` can lower it). Validation refuses an older window.

### Time

A run records `detection_to_accepted_ms` (from the detection to the platform having the
start), `queue_wait_ms`, `time_to_verdict_ms` and, for its actions, when each took effect.
A run started by a D&R rule that only needs the detection it was handed decides without
waiting for storage.

### What a run costs

`usage` counts steps, cancelled steps, events scanned, AI questions and their cost
(`llm_usd`), AI agent sessions (`agent_usd`) and wall time. The settings' budgets cap each
run; a run that reaches one ends `budget_exhausted` with what it had. An AI call already sent
is still billed when the run no longer needs it, so a finished run's AI cost can grow for a
short while after it ended (`late_usage`). Billing per run is not on.

### The case

A run that carries a detection or a case writes a case unless its template (or the
settings, when the template says nothing) says `none`. The case leads with the outcome
sentence, then the evidence, what stayed unknown, the open question and the actions. A
person's edits on the case win: the engine never overwrites a person's verdict, status or
classification, and an automatic close never closes a case a person decided. `case_final`
is true once the case written after the run ended has landed.

## Draft and active

A draft template only suggests. Only an active template starts from a D&R rule and acts.
Making a template active is the permission to act. An AI agent saves drafts; a person
promotes them. See [Templates](templates.md#draft-and-active).

## Waves and fact packs

A **wave** is a batch of questions with no template, no rules, no outcome and no case: the
engine answers every step in parallel with your own token and returns compact answers. Use
it for a one-off question ("what did this host do after that download?") and to see what an
operator returns before you write a template around it.

```yaml
# wave.yaml
steps:
  - {id: host, use: host_context, args: {sid: "<SID>"}}
  - {id: prev, op: ioc.prevalence, args: {file_hash: "<SHA256>"}, select: [hosts_30d, seen]}
  - {id: kids, op: event.children, args: {sid: "<SID>", atom: "<ATOM>"}, limit: 5}
stop_when:
  - "prev.hosts_30d >= 50 and kids.count == 0"
deadline_ms: 20000
```

```bash
limacharlie investigate wave --file wave.yaml --oid "$OID"
```

Each step answers `status` (`ok`, `partial`, `unknown` with a `reason`, `cancelled`),
`complete` and the selected `value`. `stop_when` cancels the rest as soon as it is true:
stop on a positive, never on an absence. `limacharlie investigate packs --brief` lists the
packs, their parameters and exports.
