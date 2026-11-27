# Settings

An organization's Investigation Engine settings are **one record**:
`investigation_policy/default`. It holds only what belongs to no single template:

- an emergency **pause**;
- a **circuit breaker** on automatic containments;
- the **identity** (the key) runs execute as;
- where **notifications** go, which **AI agent** answers, run **budgets**, run **limits**,
  and the default **case** mode.

Whether an action acts on its own or waits for a person, how long it lasts, what happens
when its lease ends and whether the AI may decide are written in each template, never
here. The record cannot turn a template's action on, off or into a suggestion.

The hive keeps its historical name, `investigation_policy`. The console calls it
Settings. The field reference is the
[settings record page](../7-administration/config-hive/investigation-policy.md).

## The record

```yaml
# investigation_policy/default
paused: false
circuit_breaker:
  per_hour: 20
  per_run: 5
identity:
  default: hive://secret/ie-runner
  allow: [caller, hive://secret/ie-runner]
  templates:
    mailsec-message: {default: hive://secret/ie-mail}
notify:
  action.needs_approval: [output:soc-slack]
  action.held: [output:soc-slack]
  action.executed: [output:soc-audit]
llm:
  agent: soc-agent
limits:
  max_parallel_runs: 100
  runs_per_hour: 5000
budgets:
  max_wall_seconds: 600
  max_steps_per_run: 200
  max_llm_usd_per_run: 0.5
  max_agent_usd_per_run: 5.0
  search_slot_share: 0.5
  lookback_days: 30
case: create
```

Every field is optional; a missing one takes its default. With no record at all the
engine runs the organization on the defaults, with no identity, so runs started by a
D&R rule are refused until you name one.

## Pause

`paused: true` is the organization's emergency stop. While it is true:

- **nothing acts alone**: every action that would have acted on its own waits for a person
  (`approval_reason: paused`);
- runs still investigate, and approvals, denials, undos, lease ends and "check again" runs
  still work (they are the safe direction);
- no [hand-off](custom-code.md#hand-off-to-an-ai-agent) to an AI agent starts.

The engine reads the stored record itself before every automatic action and again right
before it calls the executor, past every cache, so a pause saved a moment ago applies to
the next action. A read that fails makes the action wait (`settings_unavailable`).

When the pause is lifted, the actions that waited **keep waiting** for a person until
their `approval_timeout`. Nothing wakes by itself.

The pause is a field, so you set it the way you set everything else:

```bash
limacharlie investigate settings pause --oid "$OID"
limacharlie investigate settings resume --oid "$OID"
```

These two commands change only `paused`, with a write conditional on the version they
read. If Git Sync manages the `investigation_policy` hive, put the pause in git: the next
sync overwrites a change made outside it. `settings get` shows who last saved the record
and when (`set_by`, `set_at`).

## Circuit breaker

An organization-wide cap on automatic containments, so that one bad template cannot
isolate a fleet.

| Field | Default | Range | Counts |
|---|---|---|---|
| `circuit_breaker.per_hour` | 20 | 1 to 10000 | automatic containment-family executions of the organization in a sliding hour |
| `circuit_breaker.per_run` | 5 | 1 to 1000 | the same, inside one run |

It counts an execution with no person behind it of `contain.*`, `eradicate.*`, and every
[Playbook and extension action](custom-code.md#playbook-and-extension-actions) (the engine
cannot tell a notification from a containment). It does not count a close, a tag, an
undo, a lease extension or an action a person approved.

Over the cap, an action that would have acted alone waits for a person
(`approval_reason: circuit_breaker`; its history note names the cap). The count is shared
by every engine replica of the region, so the cap is the organization's whatever replica
executes. A count that cannot be read makes the action wait. `settings get` shows the live
count (`used_last_hour`, `oldest_in_window`, `tripped`).

Like the pause, the breaker never blocks a release, an undo or a lease check, and actions
that waited stay waiting when the hour frees up.

## Identity

Which credentials runs execute as.

| Field | Meaning |
|---|---|
| `identity.default` | `hive://secret/<name>` (a Hive secret holding an **organization** API key) or `caller` (the token of the person who started the run). A run with no person behind it (a D&R rule, a case) needs a secret. |
| `identity.allow` | The identities a person's start may ask for instead (`request.identity`). Anything else is refused (`identity_not_allowed`), so a caller can never pick a stronger key. |
| `identity.templates.<template>.default` | The key one template's runs use instead of `identity.default`. Give each template a key with only what it needs. |

The key's own platform permissions are the real limit on what a run can read and do:
there is no allow or deny list of operators or actions. A run whose key lacks a grant is
never silently broken: the step is `unknown(forbidden)`, the case write fails with
`cases_access_denied`, an action fails with `permission_denied` naming the grants.
`settings get` checks each template's key before its first run (`template_readiness`,
with `missing_grants` and the [resource-ACL scopes](permissions.md#acl-scoped-sensors)
the key is outside of). See [Permissions](permissions.md).

Writing a record that names a secret the stored record did not already name requires the
writer to be able to read that secret (`secret.get` or `secret.get.<name>`).

A run with the caller's token cannot keep anything past that token: a lease is cut to end
before the token does, and `hold` and "check again" behave as `release`
(`lease_end_note: caller_token`). Runs started by a D&R rule always use a secret.

## Notifications

`notify` maps an event to `output:<name>` destinations:

| Event | When |
|---|---|
| `run.decided` | a rule or the AI decided |
| `action.needs_approval` | an action waits for a person |
| `action.held` | an action is held for a person at the end of its lease |
| `action.executed` | an action took effect |
| `action.reverted` | an action was undone |
| `run.completed` | a run is over |

A notification carries ids, states and what a person needs to act, never evidence values.
It never delays a run, and a lost one never loses an approval: the
[approvals inbox](actions.md#the-approvals-inbox) is the pull side.

## AI agent

`llm.agent` names the `ai_agent` record that answers the templates' `ask_ai` questions
and AI reviews. Set it: without it the deployment's default agent answers, if it has one,
and otherwise every AI question is `unknown(llm_agent_not_found)`. An
[AI agent step](custom-code.md#ai-agent-steps) names its own agent in the template.

## Limits

| Field | Default | Meaning |
|---|---|---|
| `limits.max_parallel_runs` | 100 (1 to 2000) | How many of the organization's runs execute at once, region-wide. Starts above it wait in the [run queue](run-queue.md); a start is never refused for it. |
| `limits.runs_per_hour` | none (no cap) | How many runs may start in a UTC clock hour, region-wide (at least 1). Above it a start is recorded as a terminal `capped` run: not investigated, not billed. |

`budgets.max_concurrent_runs` was replaced by `limits.max_parallel_runs`. A record that
still carries it is refused when saved; a stored one keeps working without it, with the
warning `settings_field_ignored`.

## Budgets

What one run may use. A run's own `overrides` can only tighten them.

| Field | Default | Meaning |
|---|---|---|
| `budgets.max_wall_seconds` | 600 | A run's wall time |
| `budgets.max_steps_per_run` | 200 | Steps per run, packs and checks expanded |
| `budgets.max_llm_usd_per_run` | 0.5 | AI questions and the review, in US dollars |
| `budgets.max_agent_usd_per_run` | 5.0 (0 to 1000) | What one run's AI agent steps and hand-off may reserve together |
| `budgets.search_slot_share` | 0.5 (above 0, at most 1) | The share of the organization's concurrent LCQL search slots the engine may hold, so analysts keep console capacity |
| `budgets.lookback_days` | 30 (1 to 30) | The free search range: no search window starts earlier than now minus this |

## Case

`case` (`create` or `none`, default `create`) is the default for templates that do not
say: whether a run that carries a detection or a case writes a case. A template that
states `case.mode` decides for itself, whatever this says. The library templates state
`mode: create`, so `case: none` here does not stop them; install your copy without
`case.mode` to let the settings decide. A start that names a case always writes into it.
The run says what decided (`case_mode_from`: `request`, `template`, `settings` or
`default`).

## What the engine enforces

- **One record.** Only the enabled record named `default` is read. The hive refuses any
  other name (`policy_record_name`).
- **The hive's rules are the engine's.** A record the hive accepts, the engine reads; one
  the hive refuses, the engine refuses with the same code and path.
- **A record that does not parse never loosens anything.** The engine keeps its last good
  copy (`settings_rejected`). With none, it runs the organization paused with no identity
  until the record is fixed.
- **A misspelled key is an error,** never silently dropped.
- **Removed sections are refused.** The earlier policy format (`autonomy`, `match`,
  `operators`, `ai_may_decide`, `automation_routes`, `auto_investigation`, `triggers`,
  `decision`) is gone. A record that carries one is refused when saved
  (`policy_unknown_field`, with a message naming what replaced it), and a stored one is
  rejected: rewrite it, and write in each template's `act` entries what acts alone.

## Reading them

```bash
limacharlie investigate settings get --oid "$OID"
```

The answer is the settings as the engine enforces them now: `source` (`default`,
`builtin` or `rejected`), `paused`, `circuit_breaker` with its live count, `identity` with
`identity_readiness` and `template_readiness`, `notify`, `llm`, `limits`, `budgets`,
`case` and `warnings`. It never shows a secret value. API: `GET
/v1/investigate/{oid}/settings`.

## Managing them as code

The record is a Hive record like any other: write it with `limacharlie hive set`, Hive
compare-and-swap, or [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md#investigation-engine-records).
An MSSP sets the same record for every tenant, and templates carry the behaviour, so there
is no per-tenant step.
