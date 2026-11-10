# MCP Tools

The [LimaCharlie MCP server](https://github.com/refractionPOINT/lc-mcp-server) exposes
the Investigation Engine to AI assistants. The tools are built for an agent that
**writes, tests and saves plan templates**, and that **answers one-off questions** by
driving waves of parallel checks. Saving is always a draft: a person promotes it.

!!! info "Pre-release"
    The `investigate_*` tools exist only when the server is started with
    `INVESTIGATION_ENGINE_ENABLED=true` (or `1`). Without it they are not registered:
    they are absent from the tool list on every endpoint, including `all`, and the two
    profiles below are not defined. The variable is read once at startup.

## Connect

Connect the server as described in [Connecting AI Assistants](../6-developer-guide/mcp-server.md),
with one of two profiles:

| Profile | Tools |
|---|---|
| `investigation_engine` | All ten tools below. |
| `investigation_engine_readonly` | `investigate_operators`, `investigate_authoring_kit`, `investigate_packs`, `investigate_validate_plan`, `investigate_list_templates`, `investigate_get`. No start, wave, test or save. |

For a local client, set `MCP_PROFILE=investigation_engine` in the server's environment.
Give the API key the permissions in the table below, and nothing more. Profiles select
tools; each call still checks the key's permissions at the gateway.

## Tools

| Tool | What it does | Permissions |
|---|---|---|
| `investigate_authoring_kit` | One call for everything needed to write a template: the template JSON Schema, the authoring guide, the organization's typed operator catalog, the default template library, the effective policy and every validation code. `sections` (`schema`, `guide`, `operators`, `examples`, `policy`, `codes`, `packs`, `library`) fetches part of it. The whole kit is large: start with `guide,schema,codes`. | `investigation.get`, `insight.evt.get` |
| `investigate_operators` | The operator catalog, with `filter`, `names` and `brief`. | same |
| `investigate_packs` | The fact packs as a compact index: parameters with types, exports with type, reference form and a short meaning. `name` returns one pack in full. Enough to write waves without the operator catalog. | same |
| `investigate_validate_plan` | Type-checks a template (`yaml`): structure, operators, references, expressions, free time range and budgets. | `investigation.get`, `insight.evt.get` |
| `investigate_test_plan` | Dry run on real past alerts: a stored `template` or `yaml`, plus `samples` (a detection id, a case id, the newest alerts of a category, or free inputs with an expected label). Waits and polls (`wait_seconds` up to 180, default 60) and returns the agreement rate, disagreements, unknowns and costs. `test_id` continues a test that is still running. `include_steps` adds every step. Nothing is written. | `investigation.set`, `insight.evt.get` |
| `investigate_save_plan` | Saves a template to the `investigation_plan` Hive, **always as a draft**. | `investigation_plan.get`, `investigation_plan.set`, `investigation.get`, `insight.evt.get` |
| `investigate_list_templates` | The organization's templates: name, version, description, `applies_to`, status. `status` filters draft or active. | `investigation.get`, `insight.evt.get` |
| `investigate_start` | Starts a run on a `template` for a `detection_id`, `case_id`, `entity_id` or `question`. Optional `inputs`, `urgency`, `mode` (`triage`, `full`, `scope`), `case` (`create`, `none`, `attach:<id>`), `idempotency_key`, and `wait_seconds` (up to 60) to wait for the verdict. A draft template runs with autonomy capped at `suggest`. | `investigation.set`, `insight.evt.get` |
| `investigate_get` | Reads a run. `view` is `run` (default), `steps`, `events` (long-poll: `after`, `wait` up to 10) or `case`. | `investigation.get`, `insight.evt.get` |
| `investigate_wave` | Runs a batch of questions (operators or fact packs) in parallel and returns compact typed answers, stopping as soon as a `stop_when` condition is true. Steps carry `select` and `limit`; `full` returns raw values; `validate_only` checks a wave without running it; `deadline_ms` defaults to 30000. | `investigation.set`, `insight.evt.get` |

All of them work against the organization the session is connected to.

## Templates and the default library

An organization's templates are exactly its `investigation_plan` Hive records. The
engine ships a **default library** of ready-made templates. It is content, not part of
any organization: read it with `investigate_authoring_kit` and `sections: ["library"]`,
and install one by writing it as an `investigation_plan/<name>` record with the Hive
tools. Library entries say `status: active`, and the Hive refuses an `active` write from
an API key, so set `status: draft` in the YAML first and have a person promote it, or
install from the console. Fact packs (`use:` in a fact) are built into the engine, like operators.

## `investigate_save_plan` and what it refuses

A draft never runs on its own. The tool is built so an agent cannot get around that:

- It always writes `status: draft`, adds the tag `ai-draft`, and stores the optional
  `test_summary` (up to 2,000 characters) as the record's comment so the reviewer sees
  what was tested.
- It refuses a template that sets `status: active` or any other status, a `name:` key
  inside the YAML (the name is the tool's `name` argument, 1 to 64 lowercase letters,
  digits, `_` or `-`, starting with a letter or digit), and YAML anchors or aliases.
- It refuses a template that does not validate, returning the full report.
- It never overwrites an **active** template, whether the engine lists it as active or
  the Hive record says so. Save your version under a new name.
- It replaces an existing draft only with `overwrite: true`, and only if the record has
  not changed since it was read.
- It fails closed: when the engine or the Hive cannot say what exists under the name,
  nothing is written.

A successful save answers with the name, the etag, the warnings, and a reminder that a
person reviews the draft in the console and promotes it.

## The authoring loop

See [Build and Tune Templates with an AI Agent](build-templates-with-ai.md) for the
full workflow. In tool terms:

1. `investigate_authoring_kit` with `guide,schema,codes`, then `operators`.
2. Look at the organization's real data: detections and cases with the read tools, and
   `investigate_wave` to see what an operator returns.
3. Draft the YAML.
4. `investigate_validate_plan` until `errors` is empty.
5. `investigate_test_plan` on real past alerts, including known true and false
   positives; read the disagreements and unknowns, refine, test again.
6. `investigate_save_plan` with a `test_summary`.

## Investigating a novel question without a template

For a one-off question, drive waves directly:

1. `investigate_packs` once: the packs, their arguments and exports. For an
   indicator-driven question with no alert, start with the `org_roster` pack: the
   organization's machines (offline ones included) and the people who own them.
2. `investigate_wave` with one step per pack (`use`) or operator (`op`), `select` for
   the fields you will read, and `limit` to cap lists.
3. `stop_when`: the conditions that would settle the question. The engine cancels the
   rest as soon as one is true and reports `stopped_by`. An unknown is never false, so
   an incomplete step cannot stop the wave.
4. Read the compact answer (`status`, `complete`, `value`, `usage`), plan the next wave
   from it, and stop when the question is answered.

Read `unknown` as "not established", never as "no". A step with a cut list is a lower
bound, not a count. See [Waves](api-reference.md#waves).
