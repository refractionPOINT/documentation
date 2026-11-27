# Custom Code and AI Agents

A template can call your own code and your own AI agents, in two places:

- **as a step** in `gather`, which only reads and returns data the rules read;
- **as an action** in `act`, which changes something, with the same `approval`, lease,
  record and undo as every other action.

`gather` only reads and `act` is the only place that changes things. That rule holds for
custom code too: a step's Playbook or agent must be marked read-only by its owner.

!!! warning "Experimental, and not enabled everywhere"
    - Playbook steps and actions need the Playbook extension to run Playbooks as the run's
      identity. Where that is not switched on, a Playbook step is
      `unknown(playbook_identity_disabled)` and a Playbook action fails without running
      (nothing ran, nothing was billed).
    - An AI agent step and a hand-off complete only when the agent's session can answer: it
      needs the `investigate_answer` MCP tool, or a CLI release that includes
      `limacharlie investigate answer` (not in 5.14.0).
    - An AI agent cannot be an action.

## A template that uses all of them

```yaml
# investigation_plan/banned-binary-custom
status: draft
version: 1
description: "A banned binary on a host: ask our asset inventory who owns the host, block the hash at the firewall, page the owner's team, and let an AI agent look for persistence on hosts that matter."
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
  asset:
    why: "Who owns this host, and is it business critical?"
    op: playbook
    args:
      name: asset-inventory-lookup
      data: {hostname: '$trigger.hostname'}
      returns: {critical: bool, owner_team: string}
    deadline: 30s
  persistence:
    why: "Did the binary set up persistence on this host?"
    op: ai_agent
    args:
      agent: host-triage
      prompt: "Decide whether the process in the detection set up persistence on its host. Use the run's evidence first."
      sees: [trigger]
      returns: {persistence: bool, mechanism: string}
      budget: 1.50
    deadline: 8m
    only_if: 'banned.found and asset.critical'
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary {trigger.hash} is on our banned software list."
    - id: banned_and_persistent
      when: ['banned.found', 'persistence.persistence']
      say: "The banned binary set up persistence: {persistence.mechanism}."
act:
  - do: playbook:firewall-block-hash
    target: '$trigger.hash'
    attrs: {reason: banned_software}
    undo: playbook:firewall-unblock-hash
    on_rules: [banned_binary]
    approval: none
    lease: 4h
    on_lease_end: release
  - do: extension:ext-example-pager/page
    target: '$asset.owner_team'
    attrs: {team: '$asset.owner_team', severity: high}
    on_rules: [banned_binary]
    approval: none
hand_off:
  agent: ie-distiller
  when: [couldnt_tell, conflict]
  prompt: "Work out what this run could not decide. If a template change would have decided it, save it as a draft."
  budget: 3.00
  deadline: 45m
case:
  mode: create
  severity: {escalated_by_rule: high, escalated_by_ai: high, default: medium}
```

`asset-inventory-lookup`, `firewall-block-hash`, `firewall-unblock-hash`, `host-triage`,
`ie-distiller` and `ext-example-pager` stand for your own records; validation offline warns
that it could not read them (`playbook_unreadable`, `agent_unreadable`), and validation in
your organization checks them.

## Playbook steps

A `playbook` step runs a [Playbook](../5-integrations/extensions/limacharlie/playbook.md)
that only reads and returns fields the rules read.

| Argument | Meaning |
|---|---|
| `name` | The Playbook record, written literally (a reference is `bad_playbook_step`). |
| `data` | What the Playbook receives in `data`. The engine adds `data.ie` = `{oid, run_id, step, kind: step}`. |
| `returns` | Required. The fields rules may read, each `bool`, `int`, `number`, `string`, `list` or `object`. |

The step's `deadline` is 1s to 5m (default 60s).

**The record must say `read_only: true` and `sdk_version: "5"`.** `read_only` is the code
owner's promise that it changes nothing: the engine cannot verify Python, and an AI that
writes templates cannot set it. The engine runs the Playbook as the run's identity, sending
that identity's short-lived token, never an API key or a secret reference; the Playbook
extension accepts that only for SDK v5 Playbooks, which run isolated. Before every call the
engine reads the record again with the run's identity: one that is gone, unreadable or no
longer read-only gets no call. The extension checks it again, for that exact revision,
before any Python runs.

The Playbook answers `{"data": {...}}`. The declared fields are kept (extra ones dropped);
one missing or of another type makes the step unknown (`invalid_output`). Two reserved keys
are read: `status: unknown` (the step is unknown, `playbook_said_unknown`) and
`complete: false` (a positive stands, an absence is unknown). Nothing the Playbook writes,
prints or raises is kept in the run.

**Unknown, never false.** An exception, a timeout, a kill or a result over the size cap is
`unknown(error)`, and the step's record names the cause with a fixed code
(`playbook_exception`, `timeout`, `killed`, `invalid_return`, `too_large`). A close never
rests on it.

**Delivered once.** Each call asks the platform for a single delivery, so a Playbook that
fails is run, and billed, once. A call whose answer did not come back is
`unknown(upstream_unavailable)`: it may or may not have run, and nothing sends it again. The
engine itself can call a step again after a takeover by another replica, so a Playbook that
cares deduplicates on `data.ie.run_id` + `data.ie.step`.

The run publishes nothing from a step's Playbook: a detection it returns is never sent, and
no D&R rule sees its run events. The step's fact records which version of the code answered
and the seconds billed (`playbook: {name, etag, billed_seconds}`). A step is a read, so
`templates test` and draft runs call it: test only with Playbooks whose code you trust.

The run identity needs `ext.request` and `playbook.get`.

## Playbook and extension actions

| `do` | Sends |
|---|---|
| `playbook:<name>` | The Playbook gets `{ie: {op: apply, oid, run_id, action_id}, target, attrs}`. Its record must say `sdk_version: "5"`; it need not be read-only. |
| `extension:<name>/<action>` | One extension request with `attrs` as its data. |

They are decided exactly like every action (`approval`, pause, draft only suggests) and
**every automatic one counts in the circuit breaker**, notifications included. If the cap
gets in the way of a paging action, keep `approval: none` knowing that past the cap it waits
for a person, or raise `circuit_breaker.per_hour`.

**Undo.** `undo:` names what reverts it: `playbook:<name>` or `extension:<name>/<action>`.
Without `undo` the action is irreversible and takes no lease. With it, it needs a `lease`
and an `on_lease_end` like a containment.

### The contract with your Playbooks

| The forward Playbook answers | The action |
|---|---|
| `{status: ok, undo: {...}}` | applied; the `undo` object (at most 16 KiB) is kept for the undo |
| `{status: already_in_place}` | changed nothing: confirmed, nothing to undo |
| `{status: withheld}` | declined on purpose: `withheld` |
| `{status: error}` | `failed` |

The undo Playbook gets the forward data plus `ie.op: undo`, `ie.cause` and that `undo`
object (null when the forward answer was lost, so it must handle "maybe applied"). It
answers `ok`, `nothing_to_undo` or `error`. **Both Playbooks must be idempotent on
`ie.action_id`.** An extension action's undo gets the `undo` object the request answered,
else the same `attrs`. An extension that answers without a `status` and without an error is
recorded as applied (`executed_unconfirmed`).

No text your code answers (a reason, an error) is kept in the action, a note or a
notification: it could echo private attrs. Your Playbook's own logs hold it.

### "Not sent" and "outcome unknown"

What the engine knows about a call decides what happens next:

- **Not sent.** The platform proved it refused the request before delivering it: a 401,
  403 or 404 from the gateway, a missing or non-v5 Playbook record, an extension or action
  that does not exist, an undeclared parameter, the Playbook extension not running
  Playbooks as the run's identity. The action is `failed` with `not sent: <why>`. Nothing
  reached your code, nothing is billed, nobody is asked to check an effect that cannot
  exist, and no undo is sent. An undo refused this way leaves the action as it was, with a
  failed-undo reason a person can act on.
- **Outcome unknown.** Anything that does not say what happened: a 5xx, a cut connection, a
  timeout, an error text, an extension that was overloaded or unavailable at that moment, an
  answer outside the contract, or the platform's "no answer came back". The action is
  `uncertain`. One with an undo is undone to be safe (the undo gets `undo: null`); one
  without goes to a person, who checks whether it took effect before retrying.

Each apply and each undo is sent once by the engine and asks every platform hop for a single
delivery. What can still deliver a call twice is a person's retry, which is why both
Playbooks must be idempotent, and an extension action should be a request that is safe to
repeat.

`extension:ext-playbook/...` is never run (warning `playbook_through_extension`): use
`playbook:<name>`, which checks the record and runs as the run's identity.

The action records `call: {name, etag, billed_seconds, undo_name, undo_etag,
undo_billed_seconds}` (which version ran, the seconds billed) and `target_kind: custom`.

## AI agent steps

An `ai_agent` step hands a judgement that needs more than one question (read more
telemetry, follow a lead) to one of your organization's
[AI agents](../9-ai-sessions/index.md): its `ai_agent` record runs as an AI Session with the
record's own key and tools.

| Argument | Meaning |
|---|---|
| `agent` | The `ai_agent` record, written literally. |
| `prompt` | Required. What to decide. |
| `sees` | The steps whose answers the session receives as its data block, each with whether it is complete. |
| `returns` | Required. The fields rules may read, as for a Playbook step. The answer also carries `rationale`, `agent`, `session_id` and `evidence_complete`. |
| `budget` | Required. US dollars the session may spend (never above the record's own). |

The step's `deadline` (1m to 60m, default 10m) is how long the run waits for the answer;
it must fit the run's budget (`agent_wait_exceeds_budget`).

- **Only a read-only agent is a step.** The record must say `read_only: true`
  (`agent_not_read_only`): its owner's promise that its key and tools only read. It is read
  again with the run's identity before every start.
- **A rule that reads it is AI-assisted**, like one that reads an `ask_ai` step: it decides
  only on the sides the template's `ai_may_decide` grants, otherwise it recommends.
- **Unknown, never false.** No answer by the deadline is `unknown(timeout)`, a session that
  ended without one `unknown(agent_ended)`, a start refused `unknown(agent_unavailable)`, a
  budget that does not fit `unknown(agent_budget)`.
- **Money.** Each step reserves its `budget` from the run's `budgets.max_agent_usd_per_run`
  (default 5.00) before its session starts. What the session really cost shows in the run's
  `usage.agent_usd`, and can grow after the run ended.
- **The run holds no worker while it waits.** When nothing else is left to do, the run
  parks in storage, holds no slot of the [run queue](run-queue.md), and resumes when the
  answer (or the deadline) comes.
- A step with no `only_if` warns `agent_step_unconditional`: every run would start a
  session. Template tests and waves start no session (`unknown(agent_dry_run)`).

### How the agent answers

The session gets three environment variables: `LC_IE_RUN_ID`, `LC_IE_REQUEST_ID` and
`LC_IE_ANSWER_TOKEN` (a one-time secret). It answers with the MCP tool
`investigate_answer`, or:

```bash
limacharlie investigate answer --answer '{"persistence": true, "mechanism": "a scheduled task", "rationale": "The task was created one second after the process started."}'
```

API: `POST /v1/investigate/{oid}/runs/{run_id}/agent-answers/{request_id}` with
`{"token": "...", "answer": {...}}` (the session's key needs `investigation.get`). An answer
that does not match `returns` is refused with the fields to fix (`invalid_answer`) and may
be sent again until the deadline; `already_answered`, `deadline_passed` and `not_waiting`
are final. The token is never logged or shown.

**Loop guard.** A run started from an agent's session (it sends `parent_run`) or with a key
that has answered an agent request asks no agent itself (`unknown(agent_depth)`), so an
agent cannot start a chain of agents.

## Hand-off to an AI agent

A run that could not decide can hand itself to an AI agent once it is over. The agent
investigates with its own key, proposes a verdict, and may save a **draft** template that
would have decided it. Once a person promotes that draft, the next alert of that kind is
decided by a rule.

| Key | Meaning |
|---|---|
| `agent` | The `ai_agent` record, literally. It need not be read-only. |
| `when` | The outcomes that hand off: `couldnt_tell`, `conflict` (the default), `ai_recommends_benign`, `ai_recommends_malicious`. |
| `prompt` | What to do. |
| `budget` | Required. US dollars, reserved with the steps' from `budgets.max_agent_usd_per_run`. |
| `deadline` | How long the agent has, from the run's end: 1m to 60m, default 30m. |

- **After the run ended**, never before: the outcome, the case and the actions are what they
  are, and the hand-off never delays them.
- **It proposes and never acts.** The answer is `{verdict: malicious | benign | unclear,
  rationale, draft_template}`. It never changes the run's outcome; the run and its case show
  "The agent proposes: ..." and a person decides. Whatever else the agent writes, it writes
  with its own key, and an API key's template stays a draft unless the settings record is
  tagged `allow-api-key-promotion`.
- **Only runs with no caller hand off**: those a D&R rule or a case started. A run a person,
  a key or an agent started never does (`skipped_reason: has_caller`). No hand-off starts
  while the organization is paused. About 20 hand-off sessions of an organization run at
  once; the next waits.
- The run shows `hand_off` (`state`, `answer`, `draft_exists`, `cost_usd`), and the stats
  count `hand_offs`, `hand_off_answered` and `drafts_proposed` per template.
