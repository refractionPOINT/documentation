# Investigation Engine Settings Record

!!! warning "Experimental"
    The [Investigation Engine](../../investigation-engine/index.md) is experimental and
    reachable only where it has been enabled for your organization.

The `investigation_policy` hive holds the Investigation Engine's settings for an
organization: **one record, named `default`**. A write to any other record name is refused
(`policy_record_name`). New records default to enabled; the engine reads only an enabled
record.

The record holds only what belongs to no single template. What an action does, whether it
acts on its own or waits for a person, its lease and what happens when the lease ends, and
whether the AI may decide are written in each
[template](../../investigation-engine/templates.md#act), never here. How each setting
behaves is explained on the [Settings](../../investigation-engine/settings.md) page.

## Example

```yaml
# investigation_policy/default
paused: false
circuit_breaker:
  per_hour: 20
  per_run: 5
identity:
  default: hive://secret/ie-runner
  allow: [caller, hive://secret/ie-runner]
notify:
  action.needs_approval: [output:soc-slack]
  action.held: [output:soc-slack]
llm:
  agent: soc-agent
limits:
  max_parallel_runs: 100
budgets:
  max_wall_seconds: 600
  max_steps_per_run: 200
  max_llm_usd_per_run: 0.5
  max_agent_usd_per_run: 5.0
  lookback_days: 30
case: create
speculation: {low: conservative, medium: balanced, high: aggressive, critical: aggressive}
```

## Fields

| Field | Type, range | Default | Meaning |
|---|---|---|---|
| `paused` | boolean | `false` | Emergency stop: while true nothing acts alone; every action that would act alone waits for a person. Approvals, undos, lease ends and lease checks still work. |
| `circuit_breaker.per_hour` | integer, 1 to 10000 | 20 | Automatic containment-family executions of the organization in a sliding hour; over it an action waits for a person. |
| `circuit_breaker.per_run` | integer, 1 to 1000 | 5 | The same, inside one run. |
| `identity.default` | `caller` or `hive://secret/<name>` | none | The identity runs execute as. A run started by a D&R rule or a case needs a secret holding an organization API key. |
| `identity.allow` | list of the same | none | Identities a person's start may ask for instead. |
| `identity.templates.<template>.default` | `caller` or `hive://secret/<name>` | none | The identity one template's runs use. |
| `notify.<event>` | list of `output:<name>` | none | Destinations per event: `run.decided`, `action.needs_approval`, `action.held`, `action.executed`, `action.reverted`, `run.completed` (aliases `decided`, `approval_needed`). |
| `llm.agent` | `ai_agent` record name | none | The AI agent that answers `ask_ai` steps and the AI review. |
| `limits.max_parallel_runs` | integer, 1 to 2000 | 100 | Runs executing at once, region-wide; the rest wait in the run queue. |
| `limits.runs_per_hour` | integer, at least 1 | none (no cap) | Runs that may start in a UTC clock hour; above it a start is recorded `capped`. |
| `budgets.max_wall_seconds` | integer, not negative | 600 | A run's wall time. |
| `budgets.max_steps_per_run` | integer, not negative | 200 | Steps per run. |
| `budgets.max_llm_usd_per_run` | number, 0 or more | 0.5 | AI questions and the review, US dollars. |
| `budgets.max_agent_usd_per_run` | number, 0 to 1000 | 5.0 | AI agent steps and hand-off of one run, US dollars. |
| `budgets.search_slot_share` | number, above 0, at most 1 | 0.5 | Share of the organization's concurrent LCQL slots the engine may hold. |
| `budgets.lookback_days` | integer, 1 to 30 | 30 | The free search range. |
| `case` | `create` or `none` | `create` | Default case mode for templates that state no `case.mode`. |
| `speculation.<urgency>` | `conservative`, `balanced` or `aggressive` per `low`, `medium`, `high`, `critical` | as in the example | How eagerly the engine starts steps before they are known to be needed. |

Validation is strict and case-sensitive: an unknown or misspelled key is refused, never
dropped. Introducing a `hive://secret/<name>` reference the stored record does not hold yet
requires the writer to be able to read that secret.

## Removed fields

| Removed | Replaced by |
|---|---|
| `autonomy`, `match`, `operators`, `ai_may_decide`, `automation_routes`, `auto_investigation`, `triggers`, `decision` | The template: each `act` entry's `approval`, `lease` and `on_lease_end`, and its top-level `ai_may_decide`. Starts come from D&R rules (`start investigation`). |
| `budgets.max_concurrent_runs` | `limits.max_parallel_runs` |
| Other records of the hive (for example `autonomy-manual-pause`) | The `paused` field of `default` |

A write that carries a removed field is refused (`policy_unknown_field`, the message names
what replaced it). A stored record that still carries a section of the earlier format is
rejected by the engine (it keeps its last good copy, or runs the organization paused with
no identity) until it is rewritten. A stored record that still carries
`budgets.max_concurrent_runs` keeps working without it, with the warning
`settings_field_ignored`.

## Tags

Tagging the enabled `default` record `allow-api-key-promotion` lets API keys write
`status: active` templates and write fact packs. Without the tag only a person can promote
a template or write a pack. An
infrastructure-as-code pipeline that writes active templates with an API key (Git Sync,
for example) needs the tag; it is a deliberate choice: whoever holds that key can then make
a template act.

## Permissions

| Permission | Allows |
|---|---|
| `investigation_policy.get` | Read the record |
| `investigation_policy.set` | Write it, including the identity runs execute as and the pause |
| `investigation_policy.del` | Delete it |
| `investigation_policy.get.mtd`, `investigation_policy.set.mtd` | Read or write its metadata |

No preset role holds these, not even Owner: grant them explicitly. Reading the settings
**as the engine enforces them** (`limacharlie investigate settings get`) needs only
`investigation.get` and `insight.evt.get`.

## Managing it as code

Write it with `limacharlie hive set --hive-name investigation_policy --key default`, Hive
compare-and-swap, or
[Git Sync](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-engine-records).
Keep the pause in the same source of truth: a sync overwrites a pause set elsewhere.
