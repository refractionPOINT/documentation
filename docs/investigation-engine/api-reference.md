# API Reference

!!! warning "Not a stable public API yet"
    These routes are what the [console](console.md), the [CLI](cli.md) and the
    [MCP tools](mcp.md) use. They are not part of the public OpenAPI specification and
    carry no stability promise: routes, fields and limits can change before general
    availability.

The routes are served by the LimaCharlie API gateway under

```text
https://api.limacharlie.io/v1/investigate/{oid}/...
```

`{oid}` is the organization's UUID. Requests are authenticated with a LimaCharlie JWT (see
[API keys](../7-administration/access/api-keys.md)). The gateway checks the
[permissions](permissions.md), forwards the request to the engine in the organization's
region and relays its answer. The routes exist only where the Investigation Engine is
enabled; elsewhere every route is a `404` with no `error_code`.

Templates, checks, fact packs and the settings are not written here: they are records of
the [Config Hive](../7-administration/config-hive/index.md): `investigation_plan`,
`investigation_pack` and `investigation_policy` (`/v1/hive/<hive>/{oid}/<name>/data`).

## Conventions

- Bodies are JSON objects, at most 8 MiB. A query string is at most 8 KiB.
- Run, action and test ids are 1 to 128 characters of letters, digits, `.`, `_`, `:` and
  `-`.
- Times are RFC 3339 in UTC.
- **Writes are sent once.** A write that times out may or may not have happened: look
  before you repeat it, or start runs with an `idempotency_key`.
- Pages are `limit` (1 to 200, default 50) and an opaque `cursor`; send the cursor back with
  the same filters.
- Errors are `{"error", "error_code", "http_status", ...}`; a refused start may add a
  `reason_code` and a refusal its `details`. Every code is in
  [Troubleshooting](troubleshooting.md). Read the codes, never the message text.
- **Rate limits** per caller and organization, per hour: 300 run starts, 600 waves, 300
  tests, 600 single comparisons and 30 batch comparisons. Starts from D&R rules do not go
  through the gateway and are not counted here.

Permission shorthand: **read** is `investigation.get` + `insight.evt.get`; **write** is
`investigation.set` + `insight.evt.get`.

## Runs

| Method and route | Permission | Purpose |
|---|---|---|
| `POST /runs` | write | Start a run. `201` for a new run, `200` when it joined one. |
| `GET /runs` | read | One page of runs. |
| `GET /runs/{id}` | read | The run: state, outcome and what decided it, actions, queue times, usage, case. |
| `DELETE /runs/{id}` | write | Delete a run for good. `409` while it runs or has an action in effect. |
| `GET /runs/{id}/steps` | read | The step log with timing, cost, reasons and each step's `narrative` (`why`, `found`, `used`). `values=true` includes customer values. |
| `GET /runs/{id}/graph` | read | The run's entity graph, paged with `limit` and `offset`. |
| `GET /runs/{id}/events` | read | Run events by long-poll: `after`, `wait` (0 to 10 s), `limit`. Stop when `done`. Events carry structure only. |
| `GET /runs/{id}/case` | read | The case document the run wrote, with `case_error` when it could not. |
| `GET /runs/{id}/trace` | read | An anonymized trace. |
| `GET /runs/{id}/labels`, `POST /runs/{id}/labels` | read, write | People's labels on a run (`benign`, `threat`, `disputed`, `unlabeled`, with a `revision`). Stored and read back; no decision reads them. |
| `POST /runs/{id}/inputs` | write | Add `inputs` or a `detection_id` to a running run. Only its starter may. |
| `POST /runs/{id}/cancel` | write | Cancel. `revert_leases: true` also undoes its actions in effect that you may undo. |
| `POST /runs/{id}/compare` | write | Replay the run's recorded answers under an edited template, offline: no operator call, nothing written. |
| `POST /compare` | write | The same against up to 50 finished runs (`run_ids`, or `last: {template, limit}`). |
| `GET /runs/{id}/check-source` | read + `investigation_plan.get` | A check's source exactly as the run froze it. |
| `POST /runs/{id}/agent-answers/{request_id}` | `investigation.get` + the answer token | An AI agent's answer. See [Custom Code](custom-code.md#how-the-agent-answers). |
| `GET /stats` | read + `investigation_policy.set` | The performance report. |

**Listing runs.** Filters: `state` (`queued`, `running`, `decided`, `completed`,
`cancelled`, `failed`, `budget_exhausted`, `flushed`, `capped`), `outcome` (an
[outcome](concepts.md#outcomes) or `undecided`; needs `investigation_policy.set`),
`verdict`, `template`, `trigger`, `entity`, `started_by`, `idempotency_key`,
`detection_id`, `case_id`, `message_id`, `sid`, `needs_person`, `kind` (`template`, `wave`
or `lease_check`), `since`, `until`, and `sort` (`-created` default, `created`,
`time_to_verdict`, `-time_to_verdict`). Each at most once. Answer:
`{"runs": [...], "next_cursor": ""}`.

### Starting a run

```json
{
  "trigger": {"detection_id": "...", "category": "rare-process"},
  "plan": {"template": "rare-process"},
  "inputs": {},
  "urgency": "high",
  "case": "create",
  "idempotency_key": "...",
  "identity": "caller",
  "wait_seconds": 0
}
```

| Field | Meaning |
|---|---|
| `trigger` | What the run is about: `detection_id`, `case_id`, `entity_id` or `question`, with `category`, `priority`, `severity`, `tags` describing what fired. |
| `plan` | `{"template": "<name>"}`, `{"inline": "<YAML>"}` (always a draft: it only suggests), or no `plan` to get the active template whose `applies_to` matches the trigger. |
| `inputs` | Values the template's steps may read as `$?name`. |
| `urgency` | `low`, `medium`, `high`, `critical`; derived from priority or severity when absent. It is the run's [queue band](run-queue.md#fairness-and-order). |
| `case` | `create`, `none` or `attach:<case number>`. See [Case](templates.md#case). |
| `coalesce_key`, `idempotency_key` | Join an open run with the same key; return the same run for a repeated key. |
| `identity` | `caller` or `hive://secret/<name>`, only if the settings allow it for the template. |
| `overrides`, `strict` | Tighten `budgets` or `speculation` for this run (never loosen). |
| `notify` | `output:<name>` destinations for this run's events. |
| `wait_seconds` | Block up to this long for the outcome. |
| `parent_run` | Sent by an AI agent's session: the run that started it. A run with a parent asks no AI agent. |

The answer is `{"run": {...}, "queued": true, "joined": false}`. A run, abbreviated:

```json
{
  "run_id": "...",
  "state": "decided",
  "template": "banned-binary",
  "template_version": 1,
  "template_by": "request",
  "identity": {"kind": "secret", "secret_name": "ie-runner"},
  "ai_may_decide": "off",
  "verdict": {
    "outcome": "escalated_by_rule",
    "label": "true_positive",
    "decided": true,
    "decided_by": {"kind": "rule", "rule": "banned_binary", "say": "The binary ... is on our banned software list."},
    "missing": []
  },
  "actions": [{"id": "...", "class": "contain.network", "target": "...", "target_kind": "sensor",
               "target_label": "host-01", "state": "active", "automatic": true,
               "approval": {"form": "none"}, "lease_until": "...",
               "eligibility": {"approve": false, "deny": false, "extend": true, "confirm": true, "revert": true}}],
  "queued_at": "...", "started_at": "...", "queue_wait_ms": 4, "queue_band": "high", "queue_path": "fast",
  "settings_etag": "...", "clamped": [], "lookback_days": 30,
  "usage": {"steps": 3, "cancelled": 0, "llm_usd": 0, "wall_ms": 900},
  "case_id": "...", "case_final": true, "case_mode_from": "template",
  "started_by": {"identity": "trigger:dr-rule", "actor": "dr-rule:general.banned-binary-exec"}
}
```

A `conflict` verdict names both rules (`"conflict": {"escalate": "...", "close": "..."}`).
`also_held` and `contradicted_by` are set only after a decision. Wait for `case_final` when
you need the finished case.

## Actions

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /actions` | read | The approvals inbox across runs: `state`, `approval_reason`, `class`, `template`, `target`, `run_id`, `automatic`, `sort` (`updated` or `deadline`), paging. What needs a person first. |
| `POST /runs/{id}/actions/{aid}/{verb}` | write + the action's permission | `approve`, `deny`, `revert`, `extend` or `confirm`. Body: `note` (deny, revert), `seconds` (extend). Answers with the action. |
| `GET /actions/automatic` | read | The log of what the engine did on its own. |
| `GET /actions/automatic/{aid}` | read | One entry. |
| `POST /actions/automatic/undo` | write + each action's permission | Bulk undo: `ids` (1 to 100), per-item `items`, or a `selector` (needs `investigation_policy.set`). Per-item results. |
| `POST /actions/automatic/{aid}/undo` | write + the action's permission | Undo one. Body `run_id`. |

States, reasons, eligibility and the audit entries are in
[Actions, Approvals and Undo](actions.md).

## The run queue

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /queue` | read | Counts by state, band, rule and template, the hour's cap and recent flushes. |
| `POST /queue/flush` | write | Exactly one of `rule`, `template` or `all: true`, optional `note` (at most 1,024 characters). |

See [The Run Queue](run-queue.md).

## Settings

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /settings` | read | The settings as the engine enforces them: pause, circuit breaker with its live count, identity and readiness per template, notifications, AI agent, limits, budgets, case, warnings. |

The settings record itself is written through the Hive. See [Settings](settings.md).

## Templates and authoring

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /templates` | read | The templates the engine has loaded. `stored=true` lists every stored record, with `load_error` for one that does not load; `validation=true` adds each one's validation summary. |
| `GET /templates/coverage` | read | Which template a trigger picks (`category`, `rule`, `severity`, `source`, `tags`) and which others apply; `as_active=<draft>` previews a draft taking over. |
| `POST /plans/validate` | read | Body `{"yaml": "...", "name": "<record name>"}`. The validation report; for a check, `used_by` validates every caller against your draft. |
| `GET /operators` | read | The typed operator catalog. |
| `GET /packs` | read | The fact packs; `name` for one. |
| `GET /authoring-kit` | read | Everything needed to write a template; `sections` (`guide`, `schema`, `operators`, `examples`, `settings`, `codes`, `packs`, `library`). |
| `POST /test-plan` | write | A dry run on past alerts. `202` with a `test_id` while it runs. |
| `GET /test-plan/{test_id}` | read | Poll a test: `after`, `wait` (0 to 10 s). |
| `POST /waves` | write | A batch of questions with no template. See [Waves](concepts.md#waves-and-fact-packs). |

**Validate** answers `valid`, `errors` and `warnings` (each `{code, path, message,
suggestion?}`), `ai_rules`, an `estimate` of the worst case, and `actions` (per entry
`do`, `approval`, `lease`, `on_lease_end`, `acts_alone_possible`).

**Test** takes exactly one of `template` and `inline`, and `samples`:
`{"detection_id"}`, `{"case_id"}`, `{"detect_cat", "last"}` (at most 25 in all), or
`{"inputs", "expected"}`; a check takes `{"params", "expected": {"outcome"}}` samples. Each
result has `verdict`, `steps`, `cost`, `wall_ms`, `would_propose` (with `approval` and
`would_wait`) and, for a closed case, `expected` and `agreement`. The `summary` counts
per rule how many samples it decided and how many agree or disagree with your analysts.

**Compare** replays recorded facts: per run whether the outcome `changed`, the `diff`
(outcome, deciding rule, actions), and what the edit needs that the run never fetched
(`not_recorded`).

## Stats

`GET /stats?template=&since=&until=` (read + `investigation_policy.set`) aggregates the most
recent matching runs: runs by state and outcome, time to verdict, AI spend, operators, the
actions per template, and three per-template lists:

- `by_template[]`: runs, outcomes, states, median time to verdict, detection-to-verdict and
  detection-to-action times (`p50`, `p95`), AI spend, hand-offs, answered hand-offs and
  drafts proposed;
- `deciding_rules[]`: how many runs each rule decided;
- `missing_reasons[]`: which step's evidence was missing, and why, how often.

The report says what the engine did. It never scores whether an outcome was right, and it
changes nothing.
