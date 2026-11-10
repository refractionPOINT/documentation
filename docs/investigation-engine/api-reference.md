# API Reference

!!! warning "Not a public API yet"
    These routes are the interface that the [console](console.md), the [CLI](cli.md)
    and the [MCP tools](mcp.md) use. They are an experimental, versioned surface:
    they are **not part of the public OpenAPI specification** and carry no stability
    promise yet. Routes, fields and limits can change before general availability.
    Prefer the CLI or the MCP tools unless you need to call the routes directly.

The routes are served by the LimaCharlie API gateway under

```text
https://api.limacharlie.io/v1/investigate/{oid}/...
```

`{oid}` is the organization's UUID. Requests are authenticated with a LimaCharlie
JWT, like the rest of the API (see [Authentication Resource
Locator](../8-reference/authentication-resource-locator.md) and
[API keys](../7-administration/access/api-keys.md)). The gateway checks the
[permissions](permissions.md), forwards the request to the engine in the
organization's datacenter, and relays the engine's answer.

!!! info "Pre-release"
    The routes exist only on gateways where the Investigation Engine is enabled, and
    they work only for organizations in a datacenter where the engine is enabled too.
    Anywhere else they return the same "not found" as any unknown path.

## Conventions

- Bodies are `application/json`, uncompressed, at most 8 MiB, and must be a JSON
  object. A query string is at most 8 KiB.
- Run, action and test ids are 1 to 128 characters of letters, digits, `.`, `_`, `:`
  and `-`.
- Times in a run are RFC 3339 in UTC with millisecond precision. Other timestamps can
  have more precision: parse them as dates, do not sort them as text.
- Ordinary **reads** are retried by the gateway. **Writes are sent exactly once**: a
  write that times out may or may not have happened, so look before you repeat it, or
  use an `idempotency_key`. The two long-polls (`GET /runs/{id}/events` and
  `GET /test-plan/{test_id}`) are also sent exactly once; just poll again.
- Pages are `limit` (1 to 200, default 50) and an opaque `cursor`. A cursor names a
  position, not an offset, so runs started between pages never repeat or hide one.
  Send the cursor back with the same filters. Run events use `limit` up to 500 (default
  200), and the evidence graph pages with `offset` (`limit` up to 1000).
- An API key must have a key id; a key without one is refused on every route, reads
  included, with `403`.

### Errors

A failed call returns an HTTP status and `{"error": "<message>"}`. When the **engine**
refused the call, the body also has `"error_code": "<code>"` from the table below; a
failure of the gateway itself has only `error`. A refused template or wave also
carries `errors` and `warnings` arrays (each with `code`, `path`, `message` and often
`suggestion`).

Failures that only the gateway can produce, with no `error_code`:

| Status | When |
|---|---|
| `401` | A required permission is missing (the message names it). Note: the gateway answers `401`, not the engine's `403`, for a missing permission. |
| `400` | A malformed id, query string, body or long-poll parameter. |
| `403` | The API key has no key id. |
| `413`, `414` | The body is over 8 MiB, or the query string over 8 KiB. |
| `415` | The body is not uncompressed `application/json`. |

| `error_code` | Status | Meaning |
|---|---|---|
| `bad_request` | 400 | Malformed or invalid arguments. |
| `forbidden` | 403 | Not allowed by the engine: for example adding inputs to a run you did not start, or approving or denying as a user who is not on an action class's approver list. |
| `not_found` | 404 | The run, action or test does not exist (or the retention removed it). |
| `conflict` | 409 | The state does not allow it: the run has finished, or the action is not in the right state. |
| `too_many_runs` | 429 | The organization's concurrent run cap is reached. Retry later. |
| `unavailable` | 503 | Storage or a dependency is unavailable. Retry. |
| `not_implemented` | 501 | The feature is not enabled. |

The gateway adds `503 the investigation engine is not available for this
organization`, `504 investigation engine timed out` and `502 investigation engine
unavailable`.

Start, wave, test and compare routes are rate limited (per hour: 300 starts, 600
waves, 300 tests, 600 comparisons).

## Routes

Permission shorthand: **read** is `investigation.get` + `insight.evt.get`; **write** is
`investigation.set` + `insight.evt.get`. See [Permissions](permissions.md).

### Runs

| Method and route | Permission | Purpose |
|---|---|---|
| `POST /runs` | write | Start a run. `201` for a new run, `200` when it joined an existing one. |
| `GET /runs` | read | One page of the organization's runs, newest first. |
| `GET /runs/{id}` | read | State, phase, verdict, proof, effective policy, usage, critical path. |
| `GET /runs/{id}/steps` | read | The step log with timing, cost, cancellations, the plan graph edges, the belief curve and the critical path. Query `values=true` includes values. |
| `GET /runs/{id}/graph` | read | The evidence graph, paged (`limit` up to 1000, `offset`). |
| `GET /runs/{id}/events` | read | Run events by long-poll. |
| `GET /runs/{id}/case` | read | The case document the run wrote. `404` until it has one. |
| `GET /runs/{id}/trace` | read | An anonymized trace of the run. |
| `GET /runs/{id}/labels` | read | Feedback labels recorded against the run. Query `fact`, `kind`, `all`. |
| `POST /runs/{id}/inputs` | write | Add evidence or a new alert to a running run (`inputs`, `detection_id`). Only the identity that started the run may. |
| `POST /runs/{id}/cancel` | write | Cancel. In-flight steps are cancelled. Body `revert_leases` reverts active leases. |
| `POST /runs/{id}/compare` | write | Re-evaluate the run's recorded facts under another template or a tighter policy. Calls no operator. The run must have finished (`409` otherwise). |
| `GET /stats` | read | Aggregates over the most recent runs of a window (`since`, `until`, `template`). |

**Listing runs.** Filters are combined with AND and evaluated by the engine: `state`
(`queued`, `running`, `decided`, `completed`, `cancelled`, `failed`, `budget_exhausted`),
`verdict` (`true_positive`, `false_positive`, `inconclusive`, or `undecided`),
`template` (`inline` for an inline plan), `trigger` (`detection`, `entity`, `case`,
`question` or `message`), `entity`, `started_by`, `idempotency_key`, `since` and
`until`. A bad value is `400` with a message naming the parameter.

**Events.** `GET /runs/{id}/events?after=N&wait=S&limit=L` returns as soon as an event
with `seq > after` exists, or after `wait` seconds (0 to 10) with none. The answer is
`{"events": [{"seq", "at", "type", "data"}], "next": N, "done": false}`: pass `next` as
the next `after`, and stop when `done` is true. Event data carries structure only, never
customer values. A client that needs only the final answer can instead set
`wait_seconds` on the start request.

### Starting a run

```json
{
  "trigger": {"detection_id": "...", "case_id": "...", "entity_id": "...", "question": "..."},
  "plan": {"template": "suspicious-process"},
  "urgency": "high",
  "mode": "full",
  "overrides": {},
  "strict": false,
  "case": "create",
  "coalesce_key": "sid:abc",
  "idempotency_key": "...",
  "notify": ["output:slack-soc"],
  "wait_seconds": 0
}
```

| Field | Meaning |
|---|---|
| `trigger` | At least one of `detection_id`, `case_id`, `entity_id`, `question`. `category`, `priority`, `severity` and `tags` describe what fired, and select the policy records and the template. |
| `plan` | `{"template": name}` to run a stored template, or `{"inline": "<yaml>"}` to run a template you supply (always a draft). Leave it out to let the engine choose by `applies_to`. |
| `inputs` | Named values for the template's facts. |
| `urgency` | `low`, `medium`, `high` or `critical`. Derived from the trigger if you omit it. |
| `mode` | `triage` (stop at the verdict), `full` (default), or `scope` (skip triage). |
| `overrides`, `strict` | Tighten the policy for this run. See [Policies](policies.md#per-run-overrides). |
| `case` | `create`, `attach:<case_id>` or `none`. |
| `coalesce_key` | A start with the same key joins the open run (same organization, same starter and same run identity). Without a key nothing joins. |
| `idempotency_key` | A repeated start with the same key returns the same run. Scoped to your identity. |
| `identity` | `caller`, or `hive://secret/<name>`; accepted only if the policy allows it for the template. |
| `notify` | `output:<name>` destinations for this run's events. |
| `wait_seconds` | Block up to this long for the verdict, for a synchronous caller such as an agent turn. |
| `serial` | `true` starts the serial baseline for speed comparison: one step at a time, no speculation, forced to `case: none` and `suggest` autonomy. |

The response is `{"run": {...}, "joined": false}`. A run object, abbreviated:

```json
{
  "run_id": "...",
  "state": "decided",
  "phase": ["scoping", "containment"],
  "template": "suspicious-process",
  "template_version": 2,
  "template_by": "request",
  "verdict": {
    "label": "true_positive",
    "p": 0.97,
    "proof": {"rule": "cmd_malicious AND rare_egress", "facts": ["f12", "f31"]},
    "unknowns": [{"fact": "f40", "reason": "outside_free_window"}]
  },
  "actions": [{"id": "a1", "class": "contain.network", "target": "...", "state": "active", "lease_until": "2026-11-10T21:00:00.000Z"}],
  "policy": {"applied": ["default"], "clamped": []},
  "usage": {"steps": 61, "cancelled": 14, "search_events": 18200000, "llm_usd": 0.08, "wall_ms": 41000},
  "case_id": "...",
  "case_final": false,
  "started_by": {"identity": "...", "actor": "..."}
}
```

Wait for `case_final` (not just `case_id`) when you need the finished case: `case_id`
appears with the first write, `case_final` once the write made after the run ended has
landed. It stays false when no final write exists, such as with `case: none`.

### Actions and autonomy

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /actions` | read | The approvals inbox: one page of actions across all runs, awaiting approval first. Query `state` (one or a comma-separated list), `class`, `run_id`, `limit`, `cursor`. |
| `POST /runs/{id}/actions/{aid}/{verb}` | write + the action class's permission | `verb` is `approve`, `deny`, `revert`, `extend` or `confirm`. Body: `note` (deny, revert), `seconds` (extend). |
| `GET /autonomy` | read | `{"paused": false}` or `{"paused": true, "by": "...", "at": "..."}`. |
| `POST /autonomy/pause`, `POST /autonomy/resume` | `org.conf.set` only | Stop or allow every automatic action in the organization. Answers with the same shape as the read. |

Action states, in the order the inbox lists them: `awaiting_approval`, `proposed`,
`uncertain`, `executing`, `reverting`, `active`, `confirmed`, `reverted`, `failed`,
`denied`, `expired`. Within a state the most recently changed action is first.

### Templates, policy and authoring

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /templates` | read | The organization's templates: `name`, `version`, `description`, `applies_to`, `status`. |
| `POST /plans/validate` | read | Body `{"yaml": "..."}`. Type-checks a template against the organization's operator catalog. |
| `GET /operators` | read | The operator catalog with metadata, typed `args` and `output`, and availability under your policy. |
| `GET /packs` | read | The fact packs. Query `name` for one. |
| `GET /authoring-kit` | read | Everything needed to write a template. Query `sections`. |
| `POST /test-plan` | write | Dry run of a template on past alerts. |
| `GET /test-plan/{test_id}` | read | Poll a test. Query `after`, `wait` (0 to 10). |
| `GET /policy/effective` | read | The effective policy, record by record. Query `category`, `priority`, `severity`, `target_tags`, `class`. |

Templates and policies themselves are written through the
[Config Hive](../7-administration/config-hive/index.md) routes for the
`investigation_plan` and `investigation_policy` types.

#### Validate

`POST /plans/validate` answers with `valid`, `errors[]` and `warnings[]` (each
`{code, path, message, suggestion?}`), `worst_case_steps`, `cost_class`,
`free_window_compliant`, `steps_by_class`, and an `estimate`:

```json
"estimate": {"steps": 14, "search_steps": 3, "llm_steps": 1, "billed_steps": 0, "wall_seconds": 95, "exceeds": ["max_steps_per_run"]}
```

#### Authoring

`GET /authoring-kit?sections=guide,schema,codes` returns the parts you ask for. Sections
are `schema`, `guide`, `operators`, `examples`, `policy`, `codes`, `packs` and `library`.
Without `sections`, everything except `library` is returned. The answer reports its own
size.

| Section | Content |
|---|---|
| `schema` | The JSON Schema of the template YAML, generated from the engine's types. |
| `guide` | The authoring guide. |
| `operators` | The typed operator catalog and what your policy allows. |
| `examples` | Templates of the default library, as models (at most 8). |
| `policy` | The policy as it shapes a plan: budgets, denied operators, allowed extension requests, each action class's mode. |
| `codes` | Every validation code with its meaning and fix. |
| `packs` | The fact packs. |
| `library` | The whole [default library](templates.md#the-default-library): per entry `name`, `description`, `version`, `status`, `applies_to` and the `yaml` to store. Asked for by name only. |

#### Test a template on past alerts

`POST /test-plan` takes a body like:

```json
{
  "template": "my-plan",
  "samples": [
    {"detection_id": "..."},
    {"case_id": "..."},
    {"detect_cat": "mailsec-ai-triage", "last": 10},
    {"inputs": {"msg_uuid": "..."}, "expected": "false_positive"}
  ],
  "overrides": {"budgets": {"max_wall_seconds": 120}},
  "mode": "triage",
  "wait_seconds": 5
}
```

Give **exactly one** of `template` (a stored template, draft or active) and `inline` (a
template as YAML). It answers `202` with a `test_id` while the test runs, and `200` when
it is over, or when the template is invalid (`state: "invalid"` with the validation
report, and nothing started). Poll `GET /test-plan/{test_id}?after=<samples seen>&wait=10`.
Each sample result has `verdict`, `proof`, `unknowns`, `steps`, `cost`, `wall_ms`,
`would_propose`, and, for an alert in a closed classified case, `expected` and
`agreement` (`agree`, `disagree`, `undecided` or `none`). The summary has the counts, an
`agreement_rate`, the most frequent unknown reasons and the cost. See [Test on past
alerts](templates.md#test-on-past-alerts) for the semantics and limits.

A test never writes a run, case, label, action or audit event; it is not in any run
list, and the result is kept for 24 hours.

### Waves

`POST /waves` runs a batch of operator calls now and returns compact answers. There is
no template, no verdict and no case. It runs with **your** token and counts against the
organization's concurrent run cap, step cap and wall time.

```json
{
  "steps": [
    {"id": "alert", "use": "detection_context", "args": {"detection_id": "<detect id>"},
     "select": ["sid", "atom", "hash", "command_line", "same_rule_count"]},
    {"id": "host",  "use": "host_context", "args": {"sid": "$alert__trigger.sid"}, "select": ["hostname", "owner_name"]},
    {"id": "spread", "use": "hash_spread", "args": {"hash": "$alert__trigger.hash"}, "select": ["hosts_30d", "seen"]}
  ],
  "stop_when": ["spread__prevalence.hosts_30d >= 500 and alert__same_rule.count >= 50"],
  "deadline_ms": 20000
}
```

| Field | Meaning |
|---|---|
| `steps` | Each step has an `id` and exactly one of `op` (an operator) or `use` (a fact pack), plus `args`. A string argument that is a whole reference such as `"$alert__trigger.sid"` reads another step's value and makes the step wait for it. |
| `select` | Field paths of the value to return (`matches[0].entity_id`, `matches[*].entity_id`). For a pack step, the names of exports. |
| `limit` | Per step, 1 to 1000, default 10: the most list elements returned. |
| `stop_when` | Up to 8 conditions with the same rules as proofs. The first one that is true cancels the steps still running. An unknown step never makes one true. An incomplete step can make a condition true when the claim only gets stronger with more data (`machine_count > 3`), but never a claim of absence or of an exact count. Conditions are evaluated on the full results, before the answer is compacted: a step returned as `complete: false` because its list was cut may already have stopped the wave. |
| `deadline_ms` | Default 30000, capped by the policy's wall-time budget. |
| `inputs` | Named values steps and conditions may read as `$name`. |
| `full` | `true` returns raw values instead of compact ones. |
| `validate_only` | Validate and return the expanded steps without running anything. |

The answer has one result per step (`id`, `op` or `pack`, `status`, `reason`,
`complete`, `ms`, `value`), plus `stopped_by`, `usage` and `compact`. A step's `status`
is `ok`, `unknown` (with a `reason` such as `timeout`, `forbidden`, `dependency_unknown`,
`missing_input` or `policy_denied`), `cancelled` (only because `stop_when` fired) or,
for a pack, `partial`.

- **A cut list is not a complete answer.** When a list was cut at `limit`, the step is
  `complete: false` with reason `truncated`: it is a lower bound, so do not count it or
  claim something is absent from it.
- **Unknown is never absence.** An unknown step established nothing.
- An invalid wave is refused before anything runs, with `400` and the coded `errors`.
  Fix them mechanically and send it again.
- Steps of an earlier wave are not available to a later one: copy the values you need.

## See also

- [MCP Tools](mcp.md): the same operations as tools for an AI assistant.
- [CLI](cli.md): the `limacharlie investigate` commands.
- [Concepts](concepts.md) and [Plan Templates](templates.md).
