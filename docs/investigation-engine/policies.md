# Policies and Autonomy

A policy decides **what the engine may do**: how much it may spend, which operators
it may use, which actions it may propose or take on its own, who approves, and which
identity runs execute as. Templates say what to investigate; policies say how far the
engine may go.

Policies are `investigation_policy` [Hive](../7-administration/config-hive/index.md)
records. They are managed with the Hive API, the CLI or infrastructure-as-code, and
need the `investigation_policy.*` permissions, which are granted explicitly (see
[Permissions](permissions.md)). The console shows the **effective** policy and the
pause switch, but does not edit records. See [Console](console.md#policy).

!!! tip "Start in `suggest`"
    With every action class in `suggest`, the engine investigates, writes cases and
    proposes actions, but never executes anything. Run that way for a while, read what
    it proposes, and raise classes one at a time.

## How policy records combine

One record named **`default`** applies to everything. Other records carry a `match`
and apply only where they match. The effective policy for a run or an action is built
from the widest to the narrowest:

1. The built-in safe defaults (below) for every field you did not set.
2. The `default` record.
3. Every matching override record. When records disagree, **the strictest value wins**
   for each field.
4. The per-run `overrides` of the request. They can only make the policy stricter.
5. The permissions of the run's identity. A run can never read or do anything its
   identity cannot.

*Strictest* means a lower autonomy mode, a higher confidence bar, a shorter lease, a
smaller cap, a smaller budget, or fewer allowed operators. Autonomy modes rank
`off < suggest < approve < auto`.

The `default` record therefore describes what the organization allows for ordinary
endpoints, and overrides tighten it for servers, crown jewels, executives or particular
detection categories.

### Two match scopes

A `match` has two scopes because two decisions are made at different times:

| Scope | Decides | Evaluated | Against |
|---|---|---|---|
| `run` | Budgets, speculation, allowed operators, LLM settings | Once, when the run starts | The trigger: detection category, priority, rule tags, case severity |
| `target` | Autonomy of an action | For each action | The action's target: sensor selector, sensor tags, entity attributes such as `human`, `external` or department |

### Built-in defaults

An unset field never means "unlimited" or "allowed". The safe baseline is: an
unconfigured action class is **only suggested**; `min_confidence` is 0.85; a lease is
2 hours; the approval timeout is 15 minutes; automatic containment is capped at 3
targets per run and 10 per hour; and eradication is capped at `approve` unless a record
explicitly sets `auto`. Per-run overrides apply on top of that, so an override can
never enable an action class the organization left off.

If a policy record cannot be parsed, it never loosens anything: the previous good set
stays, and with none the engine falls back to suggest-only.

## A default policy

This example lets network isolation run by itself (`auto`). For a first policy, copy the
cautious one below it instead.

```yaml
# investigation_policy/default
case: create
budgets:
  max_concurrent_runs: 20
  max_wall_seconds: 900
  max_steps_per_run: 400
  max_llm_usd_per_run: 0.50
  search_slot_share: 0.5        # the most of the org's concurrent LCQL slots the engine may hold
  lookback_days: 30             # 1 to 30
operators:
  allow: [plan.*, entity.*, org.roster, endpoint.*, ioc.*, detection.*, event.*, search.*, sensor.read.*, ti.*, mailsec.*, case.*, lookup.*, llm.judge]
  deny: [sensor.collect.*]
speculation:                    # urgency -> profile
  low: conservative
  medium: balanced
  high: aggressive
  critical: aggressive
decision:
  escalate_at: 0.90             # P(true positive) that decides a true positive on evidence alone
  dismiss_at: 0.03              # P(true positive) at or below which a false positive is dismissed
  scope_at: 0.40                # P(true positive) at which scoping starts
  ask_approval_at: 0.60         # P(true positive) at which approvals are requested
autonomy:
  contain.network:  {mode: auto,    min_confidence: 0.85, lease: 2h, max_targets_per_run: 3, max_targets_per_hour: 10}
  contain.email:    {mode: approve, approvers: ['group:soc-leads'], approval_timeout: 15m, lease: 24h}
```

Only `contain.network` and `contain.email` can be carried out today (see [Action
classes](#action-classes)), so those are the only classes this example sets.

A cautious first policy has every class in `suggest`:

```yaml
# investigation_policy/default
case: create
autonomy:
  contain.network: {mode: suggest}
  contain.email:   {mode: suggest}
```

Override records tighten the default where they match:

```yaml
# investigation_policy/servers
match:
  target: '"server" in tags or "dc" in tags'
autonomy:
  contain.network: {mode: approve}
```

```yaml
# investigation_policy/low-priority-detections
match:
  run: 'priority < 3'
speculation: {low: conservative, medium: conservative}
budgets: {max_wall_seconds: 300}
```

### Record sections

| Section | What it sets |
|---|---|
| `match` | `run` and/or `target` expressions. Absent on the `default` record. |
| `budgets` | `max_concurrent_runs`, `max_wall_seconds`, `max_steps_per_run`, `max_llm_usd_per_run`, `search_slot_share` (above 0 up to 1) and `lookback_days` (1 to 30, never more). |
| `operators` | `allow` and `deny` patterns over operator names (`entity.*`). Allow lists intersect across records. `extension_requests` is a list of exact `<extension>/<action>` pairs that the `extension.request` operator may call. It is **denied by default**, only the `default` record grants it, and every other record only narrows it. |
| `speculation` | Urgency (`low`, `medium`, `high`, `critical`) to profile (`conservative`, `balanced`, `aggressive`). |
| `decision` | `escalate_at`, `dismiss_at`, `scope_at`, `ask_approval_at` (each from 0 to 1) and `mandatory_checks` per urgency. |
| `autonomy` | Per action class (or pattern such as `eradicate.*`): `mode`, `min_confidence`, `lease`, `max_targets_per_run`, `max_targets_per_hour`, `approvers`, `approval_timeout`. |
| `identity` | Which credentials runs execute with. **Default record only.** See below. |
| `case` | `create` or `none`: whether runs write a case by default. **Default record only.** |
| `notify` | Events to destinations. **Default record only.** See below. |
| `triggers` | Runs without a person, such as `case_created`. See [Automatic Starts](automation.md#the-case-trigger). |
| `llm` | Settings for `llm.judge`; the model and credentials come from the organization's `ai_agent` record. |

A record is **enabled by default** when saved, unlike most Hive types. A record with
`usr_mtd.enabled: false` is invisible to the engine.

The billable and costly operators, such as artifact collection (`sensor.collect.*`),
extensions that bill per use and detonation, are off in the default policy. An
organization enables them by policy.

## Autonomy modes

Autonomy is set **per action class**.

| Mode | Behavior |
|---|---|
| `off` | The action class is never proposed. |
| `suggest` | Proposed with its reasoning, never executed, **not even if a person approves it**: approving a suggest-mode proposal is refused with "this action class is in suggest mode". Also a dry run when rolling out a new policy. |
| `approve` | Executed after a person with `investigation.set` and the underlying permission approves. The request goes out as soon as P(true positive) passes `ask_approval_at`, so the human's response time overlaps the investigation, and it can be before the verdict is final. |
| `auto` | Executed once `min_confidence` is met, within the caps. This does not wait for the final verdict: the bar is the confidence, and the template's `when`. |

### Action classes

| Action class | Available | What it does | Reversible |
|---|---|---|---|
| `contain.network` | **Yes** | Sensor network isolation, plus a lease expiry. A sensor that was already isolated is left isolated at undo. | Yes |
| `contain.email` | **Yes** | Email Security message quarantine, including the other recipient copies of the message's group. Each copy is checked before and after. | Where the provider supports release |
| `contain.process` | Not yet | Suspend and resume a process | Yes |
| `contain.identity` | Not yet | The organization's identity response extensions | Yes, by re-enabling |
| `tag` | Not yet | Sensor tags | Yes |
| `eradicate.process`, `eradicate.file` | Not yet | Kill a process, delete a file | No |
| `collect.memory`, `collect.file`, `collect.artifact` | Not yet | Evidence collection | No effect on the host |

The policy and templates accept every class, but **only the two available classes can act**. A proposal of
any other class can be shown, and approved or executed automatically, but the attempt
fails with "action class ... is not wired" and the action ends `failed` with nothing done
on the target. Leave the others at `suggest` or `off`, and do not write templates that
propose them.

### Rules no policy can change

- **Reversible actions run as leases.** A lease undoes itself at expiry unless the
  verdict or a person confirms it.
- **Irreversible actions never run before the evidence-preserving collection** that
  the template lists with `before:`, when collection is allowed. (No irreversible class
  is available yet.)
- **The pause switch stops all automatic actions** in the organization at once.
  Proposals and approvals continue. See [Console](console.md#pause-automatic-actions).
- **Every action transition is recorded** in the run's event log with the run, the
  proof and the approver. The ones a person acts on reach the organization's audit
  log when the policy asks for notifications.
- **Nothing waits forever.** Every open action state has a deadline: a proposal
  waiting for confidence or a prerequisite, an approval (the class's
  `approval_timeout`, default 15 minutes, after which it expires and is treated as
  denied), an execution, and a lease.
- **Unknown outcomes are not failures.** If a call to execute an action times out, the
  action becomes *uncertain*. A late success makes it active, a late failure makes it
  failed, and if nothing answers a reversible action is undone to be safe. An
  irreversible action in this state is escalated to a person.

### Approvals

An action in `approve` mode appears in the [approvals inbox](console.md#approvals) and,
if the policy asks for it, as a notification. Approving needs `investigation.set`,
`insight.evt.get` and the permission of the action's class, and membership of the
`approvers` list when the class has one. **Deny** is checked against the `approvers`
list the same way. Revert, extend (the lease) and confirm (keep it) are the other
decisions: they need the same permissions but do not check the `approvers` list.
Each decision, with the person and the optional note, is recorded in the action's
history.

## Run identity

A run executes as one of two identities:

- **The caller**: the token of the person or API key that started it. This is the
  default when the policy names nothing.
- **A secret**: the API key stored in an organization Hive secret, exchanged for a
  short-lived token. Only an **organization API key** works; a user API key is refused.

```yaml
# investigation_policy/default
identity:
  default: hive://secret/investigation-engine-key   # or "caller"
  allow: [caller]                                   # what a request may name besides the default
  templates:                                        # per-template overrides
    mailsec-suspicious-message: {default: hive://secret/mail-key, allow: [caller]}
```

- A request that names an identity is accepted only if it is the template's default or
  in its `allow` list; otherwise it is refused with the allowed identities in the
  message.
- **A run with no person** (a D&R rule or the case trigger) **needs a policy
  identity.** The simplest setup is `identity.default`. A named template can instead
  carry its own `identity.templates.<name>.default` and need no org-wide default; a
  template-level entry inherits any field it leaves unset. Without an identity for the
  template, the start is refused with a message that names both settings. The case trigger, when it
  leaves the template to `auto`, reads the case with the org-wide identity before a
  template is chosen, so keep `identity.default` set for that.
- An inline plan never inherits the organization-wide identity.
- A secret that is rotated, disabled or deleted stops being used within ten minutes,
  or at once when the Hive's change broadcast announces it.
- When a run uses the caller's token, the engine never schedules work that outlives it.
  A reversible action needs about 17 minutes of token left to execute, settle and be
  undone; its lease is shortened to fit, and an action that cannot hold a lease of at
  least a minute is refused. A run that must act for hours should use a secret identity.
- The key and its token never appear in a run, a log, an event, an error or a response.

!!! warning "A policy secret can be wider than the person who starts a run"
    When the policy names a secret as `identity.default`, a run started by a person
    with `investigation.set` and `insight.evt.get` executes with the **secret's**
    permissions, not the person's, unless they pick `caller` and the policy allows it.
    The person's own permissions do not limit what that run reads or does. Give the
    identity key only what the runs need, and keep `identity.allow` and the per-template
    `identity` entries as narrow as the policy allows. The console shows who a run
    **Runs as**.

Give the identity key the least it needs: it reads telemetry for every run started by a
rule, and takes the actions the policy allows. Saving a policy that names a **new**
secret requires read access to that secret. See [Permissions](permissions.md).

## Notifications

The engine writes events to the organization's **audit log**, and your Outputs on the
audit stream deliver them like any other audit entry. Nothing is written unless the
policy's `notify` (or the request's own `notify` list) asks for it.

```yaml
notify:
  action.needs_approval: ['output:slack-soc', 'output:pagerduty']
  run.decided: ['output:slack-soc']
```

| Event | Audit event type | When |
|---|---|---|
| `run.decided` | `ie_run_decided` | The run reached a verdict (once per run). |
| `action.needs_approval` | `ie_action_needs_approval` | An action entered *awaiting approval*. |
| `action.executed` | `ie_action_executed` | An action executed and became active or confirmed. |
| `action.reverted` | `ie_action_reverted` | An action was reverted by a person or by its lease ending. |
| `run.completed` | `ie_run_completed` | The run ended, with its final state. |

`approval_needed` and `decided` are accepted as aliases of the first two events.
Destinations are written `output:<name>` and travel in the record's metadata
(`mtd.destinations`). To make `output:slack-soc` a real, named Output, route on them
with a D&R rule on the audit target that matches `mtd.destinations` and the event type
and uses the `output` action. Without such a rule, every Output on the audit stream
receives the events.

Notifications carry identifiers, states and what a person needs to act, including the
**action target** (a person cannot approve a containment of "something"). They never
carry evidence values. Delivery is best effort, and a lost notification never loses an
approval, since the action stays in the approvals inbox.

## Per-run overrides

A request can narrow the policy for one run:

```json
"overrides": {
  "speculation": "conservative",
  "budgets": {"max_wall_seconds": 120},
  "autonomy": {"contain.network": {"mode": "suggest"}}
}
```

Overrides can only make the policy stricter: lower the mode, raise confidence, shorten
leases and timeouts, lower caps and budgets, raise the decision thresholds `escalate_at`,
`scope_at` and `ask_approval_at` and **lower** `dismiss_at` (a lower bar to dismiss is
the riskier direction, so a higher `dismiss_at` is the looser value), add operator
denies. A looser value is **clamped** to the policy value, and the run lists the clamped
fields in `policy.clamped`. With `"strict": true` the request fails with a `400`
instead.

## See what applies

The effective-policy view answers "what would the engine do for this alert or this
host?" record by record. In the console it is the **Policy** tab; over the API it is
`GET /v1/investigate/{oid}/policy/effective` with a category, priority, severity and
target tags. See [API Reference](api-reference.md).
