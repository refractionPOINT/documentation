# Policies and Autonomy

A policy decides **what the engine may do**: how much it may spend, which operators
it may use, which actions it may propose or take on its own, what the AI may decide
alone, who approves, and which identity runs execute as. Templates say what to investigate; policies say how far the
engine may go. **The policy record is the only thing that decides what the engine may
do**: no history, score or label changes a decision.

Policies are `investigation_policy` [Hive](../7-administration/config-hive/index.md)
records, managed with the Hive API, the CLI, infrastructure-as-code or
[Git Sync](../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans).
They need the `investigation_policy.*` permissions, which no role holds (see
[Permissions](permissions.md)).

This page explains how policies work. The field-by-field reference of the `autonomy`
section, the emergency pause and validation are in
[Investigation Action Policies](../7-administration/config-hive/investigation-policy.md).

!!! tip "Start in `suggest`"
    With every action class in `suggest`, the engine investigates, writes cases and
    proposes actions, but never executes anything. Run that way for a while, read what
    it proposes, and raise classes one at a time. The
    [Walkthrough](walkthrough.md#4-the-policy-start-in-suggest) has a minimal policy.

## How policy records combine

One record named **`default`** applies to everything. Other records carry a `match`
and apply only where they match. The effective policy for a run or an action is built
from the widest to the narrowest:

1. The platform defaults (below).
2. The `default` record, which **replaces** the platform defaults section by section:
   a section it sets (its `autonomy`, its `operators.allow` list) takes the place of
   the platform's.
3. Every matching override record. When records disagree, **the strictest value wins**
   for each field. An override can never loosen the `default` record.
4. The per-run `overrides` of the request. They can only make the policy stricter.
5. The permissions of the run's identity. A run can never read or do anything its
   identity cannot.

*Strictest* means a lower autonomy mode, less that the AI may decide, a shorter
lease, a smaller cap, a smaller budget, fewer allowed operators, and the intersection
of approver lists. Autonomy modes rank `off < suggest < approve < auto`;
`ai_may_decide` ranks `off < escalate < close_and_escalate` and only the `default`
record can grant it.

If a policy record cannot be parsed, it never loosens anything: the engine keeps the
last good set of records, or suggest-only when it has none, and the effective policy
reports `policy_records_rejected`.

### Two match scopes

| Scope | Decides | Evaluated | Against |
|---|---|---|---|
| `run` | Budgets, speculation, allowed operators, LLM settings, and autonomy for the run | Once, when the run starts | The trigger: `category`, `priority`, `severity`, `tags`, and `template` (the template's record name) |
| `target` | Autonomy of an action | For each action | The action's target: sensor tags and attributes |

A match expression that cannot be evaluated, because an attribute is missing, counts
as a match: records only tighten, so "don't know" applies the restriction.

<!-- validate: policy -->
```yaml
# investigation_policy/servers
match:
  target: '"server" in tags or "dc" in tags'
autonomy:
  contain.network: {mode: approve}
```

<!-- validate: policy -->
```yaml
# investigation_policy/low-priority-detections
match:
  run: 'priority < 3'
speculation: {low: conservative, medium: conservative}
budgets: {max_wall_seconds: 300}
```

### Platform defaults

An unset field never means "unlimited" or "allowed".

| Section | Platform default |
|---|---|
| `budgets` | `max_concurrent_runs` 10, `max_wall_seconds` 600, `max_steps_per_run` 200, `max_llm_usd_per_run` 0.50, `search_slot_share` 0.5, `lookback_days` 30 |
| `speculation` | `low` conservative, `medium` balanced, `high` and `critical` aggressive |
| `operators` | The platform's read operators allowed; evidence collection (`sensor.collect.*`) denied |
| `autonomy` | Every class `suggest`. Unset fields: `lease` 2h, `approval_timeout` 15m; containment and eradication capped at 3 targets per run and 10 per hour |
| `ai_may_decide` | `off` for every template: the AI only recommends |
| `case` | `create` |
| `identity` | None: runs use the caller's token, and runs started by rules are refused |

## Record sections

| Section | What it sets |
|---|---|
| `match` | `run` and/or `target` expressions. Absent on the `default` record. |
| `budgets` | `max_concurrent_runs`, `max_wall_seconds`, `max_steps_per_run`, `max_llm_usd_per_run`, `search_slot_share` (above 0, up to 1) and `lookback_days` (1 to 30). |
| `operators` | `allow` and `deny` patterns over operator names (`entity.*`). Allow lists intersect across records. `extension_requests` is a list of exact `<extension>/<action>` pairs the `extension.request` operator may call: denied by default, granted only by the `default` record, narrowed by every other. |
| `speculation` | Urgency (`low`, `medium`, `high`, `critical`) to profile (`conservative`, `balanced`, `aggressive`). |
| `ai_may_decide` | Per template name, or `"*"`: `off`, `escalate` or `close_and_escalate`. **Granted only by the `default` record**; other records narrow it. See [What the AI may decide](#what-the-ai-may-decide). |
| `autonomy` | Per action class or pattern: `mode`, `lease`, `approval_timeout`, `max_targets_per_run`, `max_targets_per_hour`, `approvers`. See the [field reference](../7-administration/config-hive/investigation-policy.md#fields-and-defaults). |
| `identity` | Which credentials runs execute with. **`default` record only.** See [Run identity](#run-identity). |
| `case` | `create` or `none`: whether a run on a detection or a case writes a case by default. **`default` record only.** |
| `notify` | Events to destinations. **`default` record only.** See [Notifications](#notifications). |
| `llm` | `agent`: `hive://ai_agent/<name>`, the AI agent record that `ask_ai` steps and the AI review run with. Without it they use the record named `investigation-judge` (see the [walkthrough](walkthrough.md#2-the-ai-agent-record)). |

A record saved with no `usr_mtd` at all is enabled, unlike most Hive types; a
`usr_mtd` that leaves out `enabled` (as Git Sync and some clients send) creates it
disabled. A disabled record is ignored by the engine, so **always set
`usr_mtd.enabled: true`**, above all on the `autonomy-manual-pause` record. Unknown keys are refused when the
record is saved (`policy_unknown_field`); the removed `triggers` and `decision`
sections and the removed `min_confidence` field are among them. New cases start runs through a [D&R rule](automation.md#dr-rules-on-a-new-case).

## Autonomy modes

Autonomy is set **per action class**.

| Mode | Behavior |
|---|---|
| `off` | The action class is never proposed. |
| `suggest` | Proposed with its reasoning, never executed, **not even if a person approves it**: approving is refused with `this action class is in suggest mode`. A proposal keeps the mode it was made with. |
| `approve` | Executed after a person approves. The request goes out as soon as a rule its `act` entry names decided or also held. |
| `auto` | Executed by itself once a rule its `act` entry names decided or also held, within the caps, **when the action has a registered authorization** (below). |

Two rules hold whatever the policy says:

- **An action with no registered authorization asks for a person.** Under `auto`, an
  action of an active template is executed by itself only when the template binds it
  to an authorization the engine can re-check from the run's evidence (the
  `authorize:` key of an `act` entry), and for the false-positive close the engine
  proposes after a close outcome. Any other action waits in `awaiting_approval` with
  the reason `no_registered_authorization`, and a person decides. An action that fires
  on a decision the AI made never has a registered authorization, and neither has one
  that rests on a [check's](templates.md#checks-templates-other-templates-call) verdict
  (the informational reason `via_check`). There are three: the `contain.email` entries
  that carry `mail.verified_credential_harvest.v1` (in the default library, those of
  `mailsec-message` and `phishing-campaign`), the engine's close of a false positive,
  and the **tag check**, which needs no key in the template. Under `auto`, a `tag`,
  `tag.add` or `tag.remove` entry runs by itself when a rule that does not use the AI
  decided and holds again on the run's own evidence; see
  [Tags](templates.md#tags-run-by-themselves-and-last-their-ttl).
- **An action that cannot be undone runs by itself only when its exact class says
  `auto`.** A pattern such as `eradicate.*` or `*` with `mode: auto` resolves to
  `approve` for `eradicate.file` and `tag.remove`, with the reason
  `irreversible_requires_exact_class`.

A draft template, a [serial](api-reference.md#starting-a-run) run and a test only
ever suggest. A **suggestion** has no Approve button in the console (**Deny** becomes
**Dismiss**) and the engine refuses an approval of it from the API: it is never
executed, whoever asks.

### Pausing automatic actions

The emergency pause is an `investigation_policy` record named `autonomy-manual-pause`
with `autonomy: {"*": {mode: approve}}` (the console's **Pause automatic actions** writes
it). It caps every action class at `approve`, which means:

- nothing runs by itself: an action the policy would have executed automatically waits
  in the [approvals inbox](console.md#approvals) for a person;
- a person can still approve, with the same permissions and approver lists;
- a class the policy already holds at `suggest` or `off` stays there, since a pause only
  lowers a mode, and never turns a suggestion into something that can be approved.

Resuming deletes the record. See the
[record reference](../7-administration/config-hive/investigation-policy.md#emergency-pause-and-resume).

### Action classes

| Action class | Can execute | What it does | Undo |
|---|---|---|---|
| `contain.network` | Yes | Sensor network isolation, as a lease. A sensor that was already isolated is left isolated at undo. | Yes |
| `contain.email` | Yes | Email Security message quarantine, including the other recipient copies of the message's group. Each copy is checked before and after. | Where the provider supports release |
| `contain.seal` | Yes | Seal a Windows sensor (tamper protection), as a lease. | Yes, engine seals only |
| `tag.add` (also `tag`) | Yes | Add a sensor tag, with an optional TTL. It holds **no lease**: it lasts its `ttl` (set by the template) or until removed. | A person's undo removes it, engine additions only; nothing undoes it automatically |
| `tag.remove` | Yes | Remove a sensor tag. | No |
| `eradicate.file` | Yes | Delete one file by absolute path. | No |
| `close.false_positive` | Yes | Close the case the run wrote, or the email message, as a false positive. Proposed by the engine itself, not by templates: under the class's mode after `closed_by_rule` or `closed_by_ai`, and capped at `approve` after `ai_recommends_benign`. | Yes |
| `eradicate.process` | No | Refused (`unsupported_safe_identity`): a process cannot be identified safely by the sensor. | |
| `contain.process`, `contain.identity`, `collect.memory`, `collect.file`, `collect.artifact` | No | Recognized by the policy and templates, but not carried out: the attempt fails with `action class ... is not wired` and the action ends `failed` with nothing done. | |

The run's identity needs the permission of what an action does (for example
`sensor.task` to isolate, `mailsec.act` to quarantine, `sensor.tag` for tags,
`investigation.set` to close a case, `mailsec.set` to close a message). A person who
decides an action needs the class's permission too (see
[Permissions](permissions.md#permission-of-the-action-class)).

### Rules no policy can change

- **Reversible actions run as leases**, except tags. A lease undoes itself at expiry
  unless a person confirms or extends it. A `tag` or `tag.add` holds no lease: it is
  `confirmed` once added and lasts what its template declares (`ttl`, or until
  removed). The policy's `lease` has no effect on a tag class, no lease end or run
  cancel removes the tag, and `extend` and `confirm` are refused for it.
- **Irreversible actions never run before the evidence-preserving collection** that
  the template lists with `before:`, when collection is allowed.
- **Every action transition is recorded** in the run's event log with the run, the
  rule that decided and who decided.
- **Nothing waits forever.** Every open action state has a deadline: a proposal waiting
  for a prerequisite (1 hour), an approval (`approval_timeout`, after
  which it expires and is treated as denied), an execution (5 minutes), and a lease.
- **Unknown outcomes are not failures.** If a call to execute an action times out, the
  action becomes `uncertain`. A late success makes it active, a late failure makes it
  failed, and if nothing answers a reversible action is undone to be safe. An
  irreversible action in this state is escalated to a person.
- **A run that ends early settles its approvals.** When a run is cancelled, fails, or
  runs out of budget before it decided, every action still waiting for a
  person expires at once and can no longer be approved. A run that has decided keeps
  its approvals until their own `approval_timeout`.

### Approvals

An action in `approve` mode appears in the [approvals inbox](console.md#approvals) and,
if the policy asks, as a notification. Deciding needs `investigation.set`,
`insight.evt.get` and the permission of the action's class. Every request has a
deadline, `approval_timeout` (15 minutes unless the policy says otherwise): the inbox
lists the soonest first, and a request nobody decides in time expires and is treated as
denied. A run that is cancelled, fails or runs out of budget before it decided settles
its requests at once.

An action whose outcome is **uncertain** takes no decision from anyone: the engine
settles it by itself (see [Rules no policy can change](#rules-no-policy-can-change)).
The inbox can approve or deny many requests at once. Each is still checked as if decided
on its own, and an action that cannot be undone is never approved in bulk.

When the class's policy names `approvers`, only those people may **approve, deny,
extend or confirm** it; **revert** stays open to anyone with the class permission,
since undoing is the safe direction. `approvers` entries are compared exactly with the
identity of the person deciding: the user's email, or the API key's name. A list that
matches nobody (including `approvers: []`) blocks every decision but revert. Each
action returned by the API carries `eligibility`, what the caller may decide on it.

## What the AI may decide

The AI takes part in a run through `ask_ai` steps (a focused question whose answer
rules read) and the AI review (the fallback when no rule decided). By default it only
**recommends**: the run ends `ai_recommends_benign` or `ai_recommends_malicious`,
nothing is acted on, and a person decides. `ai_may_decide` lets it decide alone, per
template:

<!-- validate: policy -->
```yaml
# investigation_policy/default
ai_may_decide:
  mailsec-message: "close_and_escalate"  # the AI may close and escalate for this template
  suspicious-process: "escalate"         # the AI may escalate; a close stays a recommendation
  "*": "off"                             # every other template: the AI only recommends
```

Quote the values. Some YAML readers, including the one in current `limacharlie hive set` releases,
turn a bare `off` into the boolean false, and the record is then refused
(`policy_type`). The CLI changes one entry without editing YAML:

```bash
limacharlie investigate policy ai --oid "$OID"
limacharlie investigate policy ai-set suspicious-process escalate --confirm --oid "$OID"
```

| Position | An AI-assisted rule or the AI review that... |
|---|---|
| `off` (the default when absent) | ...holds only recommends. |
| `escalate` | ...escalates decides (`escalated_by_ai`); a close stays a recommendation. |
| `close_and_escalate` | ...escalates or closes decides (`escalated_by_ai`, `closed_by_ai`). |

- A template's own entry wins over `"*"`.
- **Only the `default` record grants.** Every other matching record, and a run's
  overrides, can only lower it. A run override that would raise it is clamped
  (`policy.clamped` lists `ai_may_decide.<key>`), or refused with `strict`.
- A run keeps the position it started with (`ai_may_decide` on the run object). The
  engine's close check re-decides with the lower of the run's position and the
  organization's current one, so turning the switch down is obeyed before an
  AI-decided close runs. A policy the engine cannot read lets the AI decide nothing.
- The switch decides the **outcome**, not the actions. An `act` entry that fires on an
  AI decision has no registered authorization, so it waits for a person whatever the
  autonomy mode. The case close (`close.false_positive`) is the one action the switch
  controls: after `closed_by_ai` it runs under the class's mode, so with
  `close_and_escalate` and `close.false_positive: {mode: auto}` the AI closes cases
  with no person.
- The switch is the template a run **starts with**. A template that calls
  [checks](templates.md#checks-templates-other-templates-call) has its switch cover
  the AI-assisted rules of the checks it calls. A key that names a check has no effect
  (the warning `ai_switch_on_check`): set the switch on the templates that call it.
- `"*"` grants every template that has no entry of its own. `"*": "close_and_escalate"`
  lets the AI close alerts for every template the organization has, including ones
  added later.
- There is no prerequisite. Results of a [test on past alerts](templates.md#test-on-past-alerts)
  are shown beside the switch in the console, for information only: nothing checks
  them. You can turn the switch on for many organizations at once.

In the console the switch is **AI may decide** on each template's page. It writes
`ai_may_decide.<template>` in the `default` record.

## Run identity

A run executes as one of two identities, recorded on the run as `identity`:

- **The caller**: the token of the person or API key that started it. This is the
  default when the policy names nothing.
- **A secret**: the API key stored in an organization Hive secret, exchanged for a
  short-lived token. Only an **organization API key** works; a user API key is refused
  when the run starts.

<!-- validate: policy -->
```yaml
# investigation_policy/default
identity:
  default: hive://secret/investigation-engine-key   # or "caller"
  allow: [caller]                                   # what a request may name besides the default
  templates:                                        # per-template overrides
    mailsec-message: {default: hive://secret/mail-key, allow: [caller]}
```

- `identity` is accepted only in the `default` record.
- A request may name `"identity": "caller"` or `"hive://secret/<name>"`. It is accepted
  only if it is the template's default or in its `allow` list (a template's own
  `allow` replaces the organization-wide one); otherwise the start is refused
  (`identity_not_allowed`).
- **A run with no person** (a D&R rule) **needs a policy identity**:
  `identity.default`, or the template's own `identity.templates.<name>.default`.
  Without one the start is refused (`no_policy_identity`).
- An inline plan never inherits the organization-wide identity: it runs with the
  caller's token unless the policy has an `identity.templates.inline` entry.
- A secret that is rotated, disabled or deleted stops being used within ten minutes.
- When a run uses the caller's token, the engine never schedules work that outlives
  it. A reversible action needs about 17 minutes of token left to execute, settle and
  be undone; its lease is shortened to fit, and an action that cannot hold a lease of
  at least a minute is refused. A run that must act for hours should use a secret.
- The key and its token never appear in a run, a log, an event, an error or a response.

!!! warning "A policy secret can be wider than the person who starts a run"
    When the policy names a secret as `identity.default`, a run started by a person
    executes with the **secret's** permissions, not the person's, unless they pick
    `caller` and the policy allows it. Give the identity key only what the runs need.
    Saving a policy that names a **new** secret requires read access to that secret
    (`secret.get`), and the secret must exist.

## Notifications

The engine writes events to the organization's **audit log**, and your Outputs on the
audit stream deliver them like any other audit entry. Nothing is written unless the
policy's `notify` (or the request's own `notify` list) asks for it.

<!-- validate: policy -->
```yaml
notify:
  action.needs_approval: ['output:slack-soc', 'output:pagerduty']
  run.decided: ['output:slack-soc']
```

| Event | Audit event type | When |
|---|---|---|
| `run.decided` | `ie_run_decided` | The run reached its outcome: when a rule or the AI decided, or at the end of the run for any other outcome (once per run). |
| `action.needs_approval` | `ie_action_needs_approval` | An action entered `awaiting_approval`. |
| `action.executed` | `ie_action_executed` | An action executed and became active or confirmed. |
| `action.reverted` | `ie_action_reverted` | An action was reverted by a person or by its lease ending. |
| `run.completed` | `ie_run_completed` | The run ended, with its final state. |

`approval_needed` and `decided` are accepted as aliases of the first two events.
Destinations are written `output:<name>` and travel in the record's metadata
(`mtd.destinations`). To deliver to one named Output only, add a D&R rule on the audit
target that matches `mtd.destinations` and the event type and uses the `output`
action. Without such a rule, every Output on the audit stream receives the events.

Notifications carry identifiers, states and what a person needs to act, including the
action target. They never carry evidence values. Delivery is best effort; a lost
notification never loses an approval, since the action stays in the inbox.

## Per-run overrides

A request can narrow the policy for one run:

```json
"overrides": {
  "speculation": "conservative",
  "budgets": {"max_wall_seconds": 120},
  "autonomy": {"contain.network": {"mode": "suggest"}}
}
```

Overrides can only make the policy stricter: lower the mode, lower what the AI may
decide (`"ai_may_decide": {"*": "off"}`), shorten leases and timeouts, lower caps and
budgets, narrow approvers, add operator denies. A looser
value is **clamped** to the policy value and listed in the run's `policy.clamped`.
With `"strict": true` the request fails with a `400` instead.

## See what applies

`GET /v1/investigate/{oid}/policy/effective` answers "what would the engine do for
this alert or this host?", record by record. Query parameters: `category`, `priority`,
`severity`, `target_tags` (comma separated), `class` and `template` (the template whose
run identity to explain). It returns the records applied, the budgets, what the AI may
decide (`ai_may_decide`) and the speculation, each action class with its mode and the record each value came from, the
run identity (`identity: {default, allowed[], source, configured}`), the extension
requests allowed, and `warnings` (see [Troubleshooting](troubleshooting.md#policy-warnings)).
In the console it is the **Policy** tab.
