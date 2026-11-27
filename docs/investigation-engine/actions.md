# Actions, Approvals and Undo

A template's `act` entries say what the engine does about a decision. What an entry says is
what the engine does: nothing above the template turns an action on, off or into a
suggestion, and an action the template does not list is never taken. Only three things
can still make an action that would act alone wait for a person: the organization's
[pause](settings.md#pause), its [circuit breaker](settings.md#circuit-breaker), and
settings that cannot be read. The key the run executes as limits what any action can do.

## An `act` entry

```yaml
act:
  - do: contain.network                 # what the action does
    target: '$trigger.sid'              # what it applies to
    on_rules: [banned_binary]           # the rules (or ai_review) whose decision fires it
    approval: {when: '"server" in host.tags'}   # REQUIRED: none | required | {when: <condition>}
    approval_timeout: 1h                # how long it waits for a person (1m to 7d, default 1h)
    lease: 2h                           # how long it stays in effect (reversible actions only)
    on_lease_end: release               # REQUIRED with a lease: release | hold | {check ...}
```

| Key | Required | Meaning |
|---|---|---|
| `do` | yes | The action. See [the list](#what-an-action-can-do). The key used to be `class`, which is now refused (`act_class_renamed`). |
| `target` | yes, except for the close | A step path (`'$trigger.sid'`) or a literal. Never a caller's optional input (`$?name`): a caller never chooses what is acted on. |
| `attrs` | no | An object of literals or step paths: the action's parameters (a tag's name and `ttl`, a Playbook's or an extension's data). |
| `on_rules` | yes | The rule ids, or `ai_review`, whose decision fires the entry. |
| `approval` | yes | `none`, `required` or `{when: <condition>}`. There is no default. |
| `approval_timeout` | no | 1m to 7d, default 1h. |
| `lease`, `on_lease_end` | for leased actions | See [Leases](#leases-and-what-happens-when-they-end). |
| `undo` | no | For a Playbook or extension action: what undoes it. See [Custom Code](custom-code.md#playbook-and-extension-actions). |

## `approval`

`approval` is required on every entry, so no action acts on its own by omission and a
reader always sees which ones do.

| Form | The action |
|---|---|
| `none` | acts on its own when its rule decides |
| `required` | always waits for a person |
| `{when: <condition>}` | waits for a person when the condition holds **or is unknown**; acts on its own only when it is false |

The condition is written like a rule's `when` (an expression, a list for "all of",
`{all: [...]}` or `{any: [...]}`) and reads what a rule reads: the template's steps, the
starting inputs, `org.*` and `signals.*`. It may read an AI answer: "a person approves when
the AI is unsure" is a legitimate thing to say. It is read once, when the action is
proposed, with incomplete data read as unknown. A step the condition reads is gathered
even after the decision, and the action is proposed once that step settled, so a fast
decision never reads the condition before its evidence. A step that makes a side-effecting
request is never gathered for a condition: read alone by it, it stays unknown and the
action waits.

Protected hosts are written this way: a condition on the host's tags, or a shared
[check](templates.md#checks-templates-other-templates-call) the condition reads. There is
no organization-side deny list.

## How an action is decided

When an entry fires, the engine proposes its action, then:

1. **Suggest only.** A draft template, an inline plan, a run whose template is no longer
   the active one it started with: the action is recorded `suggested`. It is never executed
   and never approvable. A person promotes the template to let it act.
2. **An AI recommendation.** When an AI-assisted rule or the review only recommends (the
   template's `ai_may_decide` does not let the AI decide that side), the entries that name
   it wait for a person whatever their `approval` says (`ai_recommendation`). The person
   gets the one-click action the AI recommends.
3. **The entry's approval.** `required`, or a `when` that holds or is unknown: it waits.
4. **The organization's controls**, for an action that would act alone: the pause
   (`paused`), settings that cannot be read (`settings_unavailable`) and, for a
   containment-family action, the circuit breaker (`circuit_breaker`).

When the AI decides (`escalated_by_ai`, `closed_by_ai`), the entries that name the deciding
rule fire with their own `approval`, like any other.

## Action states

| State | Meaning |
|---|---|
| `proposed` | The engine is deciding (milliseconds). |
| `suggested` | A draft's or inline plan's action. Never executed, never approvable. Final. |
| `awaiting_approval` | Waits for a person. `approval_reason` says why; `deadline` is when it expires. |
| `executing` | The call is in flight. |
| `active` | In effect, with a lease (`lease_until`). |
| `held` | In effect, lease over, kept until a person confirms, extends or undoes it. `held_reason` says why. |
| `confirmed` | In effect and kept: a tag, an irreversible action that ran, a confirmed close, or a person confirmed it. |
| `reverting` | The undo is in flight. |
| `reverted` | Undone. `undo_cause` says why (`lease_expiry`, `lease_check`, a person). |
| `uncertain` | The outcome is not known (a timeout, a lost answer). An action with an undo is undone to be safe; one without goes to a person. |
| `failed` | It did not run (refused, an error), or its undo failed (`undo_error_code`). |
| `denied` | A person denied it. |
| `expired` | Nobody decided by its deadline (`expired_reason: approval_timeout`), or the run ended abnormally. |
| `withheld` | The product declined on purpose, for example a case a person already decided (`withheld_reason: already_decided`). Nothing changed. |

Why an action waits, `approval_reason`: `approval_required`, `approval_condition`,
`ai_recommendation`, `paused`, `circuit_breaker`, `settings_unavailable`. It is set when the
action starts waiting and never changes.

Every open state has a deadline, so nothing waits forever. A run is complete only when none
of its actions is open; a `held` action is a person's queue, not an open state.

## Leases and what happens when they end

These actions hold a lease: `contain.network`, `contain.seal`, `contain.email`, and a
Playbook or extension action that names its `undo`. Each must say `lease` (1m to 7d) and
`on_lease_end`:

| `on_lease_end` | At the end of the lease |
|---|---|
| `release` | It is undone (`undo_cause: lease_expiry`). |
| `hold` | It stays in effect and becomes `held` (`held_reason: on_lease_end_hold`), the `action.held` notification goes out, and a person confirms, extends or undoes it. |
| `{check, args, extend, max, at_max}` | **Check again**: see below. |

No other action takes a lease (`lease_not_allowed`): a tag lasts its `ttl`, an irreversible
action (`eradicate.file`, `tag.remove`, a custom action without `undo`) and the close cannot
be released.

A run that executes with the caller's own token (a person's run with `identity: caller`)
cannot keep anything past that token: its lease is cut to end before the token, and `hold`
and checking again release instead (`lease_end_note: caller_token`). Runs started by a D&R
rule always use a secret identity.

### Check again: the automatic rollback of a false positive

At the end of the lease the engine runs a [check](templates.md#checks-templates-other-templates-call)
(a `kind: check` template). If it now says benign, the action is undone. Otherwise the
lease is extended, up to a maximum you state.

```yaml
# investigation_plan/hash-still-banned
kind: check
description: "Is this hash still banned, or has it been approved since?"
params:
  hash: {type: string, required: true, description: "The SHA-256 to check."}
gather:
  approved:
    op: lookup.get
    args: {name: approved-software, keys: [$hash]}
  banned:
    op: lookup.get
    args: {name: banned-software, keys: [$hash]}
rules:
  escalate:
    - {id: still_banned, when: 'banned.found', say: "{hash} is still on the banned list."}
  close:
    - {id: now_approved, when: ['approved.found', 'not banned.found'], say: "{hash} is now approved and no longer banned."}
```

```yaml
# investigation_plan/banned-binary-held
status: draft
version: 1
description: "Isolate a host that ran a banned binary; release it on its own once the hash is approved, otherwise keep it up to a day, then keep it for a person."
applies_to:
  rule: ['general.banned-binary-exec']
starts_from: detection
gather:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
rules:
  escalate:
    - {id: banned_binary, when: 'banned.found', say: "The binary {trigger.hash} is on our banned software list."}
act:
  - do: contain.network
    target: '$trigger.sid'
    on_rules: [banned_binary]
    approval: none
    lease: 1h
    on_lease_end:
      check: template:hash-still-banned
      args: {hash: '$trigger.hash'}
      extend: 1h
      max: 24h
      at_max: hold
case:
  mode: create
  severity: {escalated_by_rule: high, default: medium}
```

| Key | Meaning |
|---|---|
| `check` | `template:<name>` of a `kind: check` template (`lease_check_not_check` otherwise). |
| `args` | The check's params, checked like a call's. Resolved when the action is proposed and stored with the action; the check always runs with those values. |
| `extend` | How much longer the action stays when the check is not benign (1m to 7d, default the lease). |
| `max` | The longest the action stays in effect in all, counted from when it took effect (1h to 30d, at least the lease). Required. |
| `at_max` | `hold` (keep it for a person, `held_reason: lease_check_max`) or `release` (undo it). Required. |

- **Benign** means the check closed, in a run that completed, on complete evidence. An AI
  close counts only when the original template's `ai_may_decide` is `close_and_escalate`
  and the AI saw complete evidence.
- **Anything else is not benign**: escalated, could not tell, a conflict, a run that
  failed, and no answer within the check's 10-minute grace.
- An argument read from evidence the run did not finish reading (partial data, a step
  that did not answer, an AI answer) can never let the check say benign: the action says so
  (`on_lease_end.args_incomplete`) and every lease end extends.
- Each check is a run of its own (`kind: lease_check`) with the original run's identity,
  no case and no actions. The action lists each one in `lease_checks` (`outcome`: `benign`,
  `not_benign`, `no_result` or `superseded`). Find a check's run with
  `list_runs kind=lease_check`.
- A person's decision while a check runs wins (the check is `superseded`). A person may
  extend past `max`; at the end of that extension `at_max` applies.
- The pause and the circuit breaker never block a check or the release it leads to.

## What an action can do

| `do` | Effect | Lease | Run key needs |
|---|---|---|---|
| `contain.network` | Isolates the sensor from the network | yes | `sensor.task` |
| `contain.seal` | Seals the sensor | yes | `sensor.task` |
| `contain.email` | Quarantines the message's copies | yes | `mailsec.act` |
| `tag`, `tag.add` | Adds a sensor tag for `attrs.ttl` seconds (or until removed) | no | `sensor.tag` |
| `tag.remove` | Removes a sensor tag (irreversible) | no | `sensor.tag` |
| `eradicate.file` | Deletes a file on the sensor (irreversible) | no | `sensor.task`, `output.set` |
| `close.false_positive` | Closes the run's case (and the message the run started from) as a false positive | no | `investigation.get`, `investigation.set` (`mailsec.set` for a message) |
| `playbook:<name>` | Runs a Python Playbook | with `undo` | `ext.request`, `playbook.get` |
| `extension:<name>/<action>` | Sends one extension request | with `undo` | `ext.request` and what the extension needs |

`contain.process`, `contain.identity`, `eradicate.process` and `collect.*` are not
supported (`action_not_supported`). An action a person approves still executes as the run
identity, so the key needs the action's permission even when a person decides.

A tag holds no lease: write `attrs.ttl` (whole seconds) or it stays until someone removes it
(warning `auto_tag_permanent`). A tag the host already carried changes nothing
(`already_in_place: true`, nothing to undo).

### The close

`do: close.false_positive` closes the run's case when a close rule (or the review) it names
decides. It takes no `target`, `attrs` or lease, fires only on close rules or `ai_review`,
and a template has at most one. Without it, a close verdict writes the case's conclusion and
closes nothing (warning `close_rule_without_close_entry`).

A person's decision on the case always wins: a close on a case a person already decided is
`withheld` (`already_decided`) and nothing is sent. A close the product confirmed is
`confirmed`; one it did not confirm is `held` for a person (`close_unconfirmed`). An
approval of a close on a case a person decided shows that decision first
(`prior_decision`).

## The approvals inbox

Everything that waits for a person, across all runs:

```bash
limacharlie investigate actions list --state awaiting_approval,held --oid "$OID"
```

API: `GET /v1/investigate/{oid}/actions` with `state`, `approval_reason`, `class`,
`template`, `target`, `run_id`, `automatic` (only what the engine ran on its own, or only
the rest), `sort` (`updated`, or `deadline` for what expires next) and paging. What needs a
person comes first. Each action carries `eligibility`, what a person may decide on it now:

```json
"eligibility": {"approve": true, "deny": true, "extend": false, "confirm": false, "revert": false}
```

There are no approver lists: anyone with `investigation.set`, `insight.evt.get` and the
action's own permission (for example `sensor.task` for isolation) may decide it.

## Deciding an action

| Verb | When | Effect |
|---|---|---|
| `approve` | `awaiting_approval` | It executes, as the run identity. |
| `deny` | `awaiting_approval` | It never executes. Optional `note`. |
| `revert` | `active`, `held`, `confirmed`, or a failed undo | Undo it now. Optional `note`. |
| `extend` | `active` or `held` (leased actions) | Keep it `seconds` more. |
| `confirm` | `active` or `held` (leased actions) | Keep it; no lease end applies any more. |

```bash
limacharlie investigate actions approve <run_id> <action_id> --oid "$OID"
limacharlie investigate actions deny <run_id> <action_id> --note "known admin tool" --oid "$OID"
```

`revert`, `extend` and `confirm` have no CLI command yet. Use the API:

```bash
curl -s -X POST "$API/investigate/$OID/runs/<run_id>/actions/<action_id>/revert" \
  -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
  -d '{"note": "false positive"}'
curl -s -X POST "$API/investigate/$OID/runs/<run_id>/actions/<action_id>/extend" \
  -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
  -d '{"seconds": 3600}'
```

A wrong state answers `409` naming the state. An undo whose outcome is not known is never
sent again by itself: at its deadline it is `failed`, and a person can retry it.

## Undoing what the engine did on its own

The log of automatic actions, and a bulk undo:

```bash
curl -s "$API/investigate/$OID/actions/automatic?limit=50" -H "Authorization: Bearer $LC_JWT"
curl -s -X POST "$API/investigate/$OID/actions/automatic/undo" \
  -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
  -d '{"ids": ["<action id>", "<action id>"]}'
```

A bulk undo takes 1 to 100 explicit ids, or a selector (`route_id` and a time range; it
needs `investigation_policy.set`). Results keep the input order and report each item's
state, error code and whether a retry can work. Retry failed ids explicitly. Each undo still
needs the action's own permission.

Cancelling a run with `revert_leases` also undoes its actions that are in effect and that
you may undo (the others are listed in `skipped_reverts`):

```bash
limacharlie investigate runs cancel <run_id> --revert-leases --oid "$OID"
```

## The audit log

Every decision a person or a key makes is one entry in the organization's
audit log (`GET /v1/insight/{oid}/audit`, `limacharlie audit list`), filed under who decided (`ident` is
the person or key):

| `etype` | Decision |
|---|---|
| `ie_action_approved`, `ie_action_denied` | approve, deny |
| `ie_action_undone` | revert, a bulk undo (`via: bulk_undo`), a cancel that undid it (`via: cancel_run`): one entry per action |
| `ie_action_extended`, `ie_action_confirmed` | extend, confirm |
| `ie_run_cancelled` | cancel |
| `ie_run_started` | a start by a person or a key (not by a D&R rule or a case) |
| `ie_run_inputs_added` | inputs added to a run (the names, never the values) |
| `ie_run_labelled` | a label on a run |
| `ie_agent_answered` | an AI agent's answer (never the answer itself) |
| `ie_queue_flushed` | a [queue flush](run-queue.md#flush) |

- A refused decision is recorded `outcome: refused` with its error code.
- A decision that changes nothing (undo of what is already undone, a retried start) records
  nothing.
- What the engine does on its own (an action that acts alone, a release at lease end, an
  expiry) is not a person's decision and has no audit entry: it is in the action's
  `history`, the run's log and the stats.
- No entry carries a token, a note, an input value or an answer.
- An entry is written in the same transaction as the decision, then delivered; receivers
  can deduplicate on its `event_id`.

Settings, pause and template edits are Hive writes, audited by the Hive.

## What an action records

Every action keeps: `do` (`class`), `target` with `target_kind` and a readable
`target_label` (the hostname, the message subject), `approval` as written, `approval_reason`,
`deadline`, `lease_until`, `in_effect_since`, `automatic`, `decided_by`, every transition in
`history` (who, when, from which state), `undo_cause`, `undo_error_code`, and for "check
again" its `lease_checks`. A custom action also records which version of the code ran and
the seconds it was billed.
