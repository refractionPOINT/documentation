# API Reference

!!! warning "Not a stable public API yet"
    These routes are the interface that the [console](console.md), the [CLI](cli.md)
    and the [MCP tools](mcp.md) use. They are **not part of the public OpenAPI
    specification** and carry no stability promise yet: routes, fields and limits can
    change before general availability.

The routes are served by the LimaCharlie API gateway under

```text
https://api.limacharlie.io/v1/investigate/{oid}/...
```

`{oid}` is the organization's UUID. Requests are authenticated with a LimaCharlie
JWT, like the rest of the API (see [API keys](../7-administration/access/api-keys.md)).
The gateway checks the [permissions](permissions.md), forwards the request to the
engine in the organization's datacenter, and relays its answer. The routes exist only
where the Investigation Engine is enabled; elsewhere every route is the same `404` as
an unknown path. For a guided tour of these calls, see the [Walkthrough](walkthrough.md).

Templates and policies are not written here: they are the `investigation_plan` and
`investigation_policy` records of the [Config Hive](../7-administration/config-hive/index.md)
(`/v1/hive/investigation_plan/{oid}/{name}/data` and
`/v1/hive/investigation_policy/{oid}/{name}/data`).

## Conventions

- Bodies are `application/json`, uncompressed, at most 8 MiB, and must be a JSON
  object. A query string is at most 8 KiB.
- Run, action and test ids are 1 to 128 characters of letters, digits, `.`, `_`, `:`
  and `-`.
- Times in a run (`created`, `updated`, action times) are RFC 3339 in UTC with
  millisecond precision. Other timestamps can have more precision: parse them as
  dates, do not sort them as text.
- **Reads** are retried by the gateway. **Writes are sent exactly once**: a write that
  times out may or may not have happened, so look before you repeat it, or use an
  `idempotency_key`. The two long-polls (`GET /runs/{id}/events` and
  `GET /test-plan/{test_id}`) are also sent once; just poll again.
- Pages are `limit` (1 to 200, default 50) and an opaque `cursor`; send the cursor back
  with the same filters. A cursor names a position, not an offset, so runs started
  between pages never repeat or hide one. Run events take `limit` up to 500 (default
  200); the run's graph pages with `offset` (`limit` up to 1000, default 200).
- An API key must have a key id; a key without one is refused on every route.
- Errors are `{"error", "error_code", "http_status", ...}`. Every code, and every
  `reason_code` of a refused start, is in [Troubleshooting](troubleshooting.md).

**Rate limits**, per caller and organization, per hour: 300 run starts, 600 waves,
300 tests and 600 comparisons.

## Routes

Permission shorthand: **read** is `investigation.get` + `insight.evt.get`; **write**
is `investigation.set` + `insight.evt.get`. See [Permissions](permissions.md).

### Runs

| Method and route | Permission | Purpose |
|---|---|---|
| `POST /runs` | write | Start a run. `201` for a new run, `200` when it joined an open one. |
| `GET /runs` | read | One page of the organization's runs, newest first. |
| `GET /runs/{id}` | read | State, phase, outcome and what decided it, actions, effective policy, `ai_may_decide`, `ai_agent`, usage, critical path. |
| `DELETE /runs/{id}` | write | Delete a run for good: `{"deleted": true, "run_id": ...}`. `409` while it is running, writing its case, or has actions waiting, executing or holding an effect. |
| `GET /runs/{id}/steps` | read | The step log with timing, cost, cancellations and each step's `narrative` (`why`, `found`, `used`), the plan graph edges, the outcome `timeline`, the run's `ai_may_decide` and the critical path. `values=true` includes customer values (the narratives are rendered with them). |
| `GET /runs/{id}/graph` | read | The run's entity graph, paged. |
| `GET /runs/{id}/events` | read | Run events by long-poll. |
| `GET /runs/{id}/case` | read | The case document the run wrote, with `written`, `case_id` and `case_error`. `404` until it has one. |
| `GET /runs/{id}/trace` | read | An anonymized trace of the run. |
| `GET /runs/{id}/labels` | read | Labels recorded against the run. Query `fact` (a step), `kind`, `all`. |
| `POST /runs/{id}/labels` | write | Submit your assessment of a run: `{"assessment": "benign" \| "threat" \| "disputed" \| "unlabeled", "revision": <positive integer>}`. A label is stored and read back; no decision reads it. Use a higher `revision` to correct one. |
| `POST /runs/{id}/inputs` | write | Add an input or a new alert to a running run: `inputs` (object) and/or `detection_id`. Only the identity that started the run may. |
| `POST /runs/{id}/cancel` | write | Cancel. Body `revert_leases` (boolean). |
| `POST /runs/{id}/compare` | write | Re-evaluate the run's recorded answers under another template or a tighter policy, including a lower `ai_may_decide`. Each side carries `outcome` and `decided_by`; diff kinds include `outcome`, `decided_by` and `ai_may_decide`. Calls no operator. The run must have finished (`409` otherwise). |
| `GET /stats` | read + `investigation_policy.set` | The performance report. See [Stats](#stats). |

**Listing runs.** Filters are combined with AND and evaluated by the engine, so they
cover every run: `state` (`queued`, `running`, `decided`, `completed`, `cancelled`,
`failed`, `budget_exhausted`), `outcome` (one of the eight
[outcomes](concepts.md#outcomes), or `undecided`; needs `investigation_policy.set`),
`verdict` (the label: `true_positive`, `false_positive`,
`inconclusive` (any recommendation, `couldnt_tell` or `conflict`) or `undecided`;
needs `investigation_policy.set`), `template`
(`inline` for an inline plan), `trigger` (`detection`, `entity`, `case`, `question` or
`message`), `entity`, `started_by` (an identity such as `user:<uid>`, or a user's
email or key name), `idempotency_key`, `kind` (`template` or `wave`), `session`,
`since` and `until` (RFC 3339, on the creation time). A bad value is `400` naming the
parameter. The answer is `{"runs": [...], "next_cursor": ""}`.

**Events.** `GET /runs/{id}/events?after=N&wait=S&limit=L` returns as soon as an event
with `seq > after` exists, or after `wait` seconds (0 to 10) with none. The answer is
`{"events": [{"seq", "at", "type", "data"}], "next": N, "done": false}`: pass `next` as
the next `after`, and stop when `done` is true. Event data carries structure only,
never customer values.

**Cancel.** In-flight steps stop. Every action still waiting for a person expires at
once (`expired`, by `run_end`) and can no longer be approved. Active leases are kept,
or reverted with `revert_leases: true`; a lease of a class whose permission the caller
does not hold is kept and listed in `skipped_reverts` (`[{action_id, class}]`).
Cancelling a run that already ended leaves it as it ended, but `revert_leases: true`
still undoes what it left in place.

### Starting a run

```json
{
  "trigger": {"detection_id": "...", "case_id": "...", "entity_id": "...", "question": "..."},
  "plan": {"template": "suspicious-process"},
  "inputs": {},
  "urgency": "high",
  "mode": "full",
  "overrides": {},
  "strict": false,
  "case": "create",
  "coalesce_key": "sid:abc",
  "idempotency_key": "...",
  "identity": "caller",
  "notify": ["output:slack-soc"],
  "wait_seconds": 0
}
```

| Field | Meaning |
|---|---|
| `trigger` | At least one of `detection_id`, `case_id`, `entity_id` or `question`, or a non-empty `inputs` with a named template. `category`, `priority`, `severity` and `tags` describe what fired: they select the policy records and, with no `plan`, the template. |
| `plan` | `{"template": "<name>"}` for a stored template, or `{"inline": "<template YAML>"}` for a template you supply (always a draft; refused for a start without a person). **Leave `plan` out** to let the engine choose the active template whose `applies_to` matches the trigger (`no_template_applies` when none does). A person's start is matched on the request's own `trigger`, not on the detection's record: `detect_cat` matches `trigger.category`, `tag` matches `tags`, `severity` matches `severity`, and `source` is `api`. Without `category`, no `detect_cat` matches, not even `*`. `{"auto": true}` is refused for a person. |
| `inputs` | Named values the template's steps may read as optional inputs (`$?name`). A template reads `$name` only for the ids its `starts_from` provides. |
| `urgency` | `low`, `medium`, `high` or `critical`. Without it: derived from the priority or the severity (8 or more, or `critical`, is `critical`; 6 or more, or `high`, is `high`; 3 or more, or `medium`, is `medium`; otherwise `low`), and `medium` when the trigger carries neither. |
| `mode` | `full` (the default: triage, scoping and containment), `triage` (stop at the outcome) or `scope` (skip triage). |
| `overrides`, `strict` | Tighten the policy for this run. See [Per-run overrides](policies.md#per-run-overrides). |
| `case` | `create`, `attach:<case number>` or `none`. Without it, a run on a detection or a case writes a **new** case unless the policy's `case` is `none`; to write into an existing case, send `attach:<case number>`. |
| `coalesce_key` | A start with the same key joins the open run of the same organization, starter and run identity. Without a key nothing joins. |
| `idempotency_key` | A repeated start with the same key returns the same run. Scoped to your identity. |
| `identity` | `caller`, or `hive://secret/<name>`; accepted only if the policy allows it for the template. |
| `notify` | `output:<name>` destinations for this run's events. |
| `wait_seconds` | Block up to this long for the outcome, for a synchronous caller. |
| `serial` | `true` starts the serial baseline used to measure the speed-up: one step at a time, no speculation, forced to `case: none` and `suggest`. |

The response is `{"run": {...}, "joined": false}`. A run object, abbreviated:

```json
{
  "run_id": "...",
  "state": "decided",
  "phase": ["triage", "scoping", "containment"],
  "template": "suspicious-process",
  "template_version": 1,
  "template_by": "request",
  "identity": {"kind": "secret", "secret_name": "investigation-engine-key"},
  "verdict": {
    "outcome": "escalated_by_rule",
    "label": "true_positive",
    "decided": true,
    "decided_by": {"kind": "rule", "rule": "banned_binary", "say": "The binary ... is on our banned software list."},
    "recommendation": null,
    "missing": [],
    "unknowns": [{"fact": "f40", "key": "live_net", "reason": "timeout"}]
  },
  "ai_may_decide": "off",
  "ai_agent": "investigation-judge",
  "actions": [{"id": "a1", "class": "contain.network", "target": "...", "state": "awaiting_approval", "mode": "approve",
               "eligibility": {"approve": true, "deny": true, "extend": true, "confirm": true, "revert": true, "approvers_required": false}}],
  "policy": {"applied": ["builtin", "default"], "clamped": []},
  "usage": {"steps": 61, "cancelled": 14, "llm_usd": 0.08, "wall_ms": 41000},
  "case_id": "...",
  "case_final": false,
  "started_by": {"identity": "user:...", "actor": "alice@example.com"}
}
```

`template_by` is `request` or `applies_to`. Wait for `case_final` (not just `case_id`)
when you need the finished case: `case_id` appears with the first write, `case_final`
once the write made after the run ended has landed.

### Actions

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /actions` | read | The approvals inbox: one page of actions across all runs, `awaiting_approval` first. Query `state` (one or a comma-separated list), `class`, `run_id`, `limit`, `cursor`. |
| `POST /runs/{id}/actions/{aid}/{verb}` | write + the action class's permission | `verb` is `approve`, `deny`, `revert`, `extend` or `confirm`. Body: `note` (deny, revert), `seconds` (extend). Answers with the action. |

Action states, in the order the inbox lists them: `awaiting_approval`, `proposed`,
`uncertain`, `executing`, `reverting`, `active`, `confirmed`, `reverted`, `failed`,
`denied`, `expired`. Within a state the most recently changed action is first. Each
item is the action plus `run` (`run_id`, `template`, `urgency`, `outcome`, `verdict` (its
label, `""` while there is none), `decided`, `state`, `case_id`, `created`). `approve`/`deny` apply to `awaiting_approval`,
`extend`/`confirm` to `active`, `revert` to `active` or `confirmed`. The approvers rule
is in [Approvals](policies.md#approvals).

### Templates, policy and authoring

| Method and route | Permission | Purpose |
|---|---|---|
| `GET /templates` | read | The organization's templates: `name`, `version`, `description`, `applies_to`, `status`. |
| `POST /plans/validate` | read | Body `{"yaml": "..."}`. Type-checks a template against the organization's operator catalog. |
| `GET /operators` | read | The operator catalog: typed `args` and `output`, and availability under your policy. |
| `GET /packs` | read | The fact packs: tested bundles of steps. Query `name` for one. |
| `GET /authoring-kit` | read | Everything needed to write a template. Query `sections`. |
| `POST /test-plan` | write | Dry run of a template on past alerts. |
| `GET /test-plan/{test_id}` | read | Poll a test. Query `after`, `wait` (0 to 10). |
| `GET /policy/effective` | read | The effective policy, record by record. Query `category`, `priority`, `severity`, `target_tags`, `class`, `template`. See [See what applies](policies.md#see-what-applies). |
| `GET /autonomy` | read | Deprecated. Answers `{"deprecated": true, "replacement": "investigation_policy", ...}`. |
| `POST /autonomy/{verb}` | `org.conf.set` | Retired: `410 route_control_retired`. Pause with the [`autonomy-manual-pause` record](../7-administration/config-hive/investigation-policy.md#emergency-pause-and-resume). |

#### Validate

`POST /plans/validate` answers with `valid`, `errors[]` and `warnings[]` (each
`{code, path, message, suggestion?}`), `worst_case_steps`, `cost_class`,
`free_window_compliant`, `steps_by_class`, `ai_rules` (the ids of the AI-assisted
rules, which decide only where `ai_may_decide` allows) and an `estimate` of the worst
case of one run:

```json
"estimate": {"steps": 14, "search_steps": 3, "llm_steps": 1, "billed_steps": 0, "wall_seconds": 95, "exceeds": ["max_steps_per_run"]}
```

#### Authoring kit

`GET /authoring-kit?sections=guide,schema,codes` returns the parts you ask for. Without
`sections`, everything except `library` (about 33,000 tokens). The answer reports its
own size.

| Section | Content |
|---|---|
| `schema` | The JSON Schema of the template YAML. |
| `guide` | The authoring guide. |
| `operators` | The typed operator catalog and what your policy allows. |
| `examples` | Templates of the default library, as models (at most 8). |
| `policy` | The policy as it shapes a plan: budgets, denied operators, allowed extension requests, each action class's resolved policy. |
| `codes` | Every validation code with its meaning and fix. |
| `packs` | The fact packs. |
| `library` | The whole [default library](templates.md#the-default-library): per template `name`, `description`, `version`, `status`, `applies_to` and the `yaml` to store, and under `rules` the library's D&R rules (`name`, `description`, `hive`, `yaml`). Only when asked for by name. |

Every answer also has `kit_version` (6) and `capabilities`: the only template format
the engine accepts (`v5`), the outcomes a run can end with, the step statuses (`ok`,
`unknown`, `skipped`, `cancelled`) and the positions of `ai_may_decide`.

#### Test a template on past alerts

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

Give **exactly one** of `template` (stored, draft or active) and `inline` (YAML).
`mode` is `triage` (default) or `full`; `wait_seconds` is 0 to 10. It answers `202`
with a `test_id` while the test runs, and `200` when it is over or the template is
invalid (`state: "invalid"` with the validation report, nothing started). Poll
`GET /test-plan/{test_id}?after=<samples seen>&wait=10` until `done`. Each result has
`verdict` (the outcome, `decided_by`, `recommendation`, `missing`, `unknowns`),
`steps`, `cost`, `wall_ms`, `would_propose` and, for an alert in a closed classified
case, `expected` and `agreement` (`{"rule": "agree", "ai": "none"}`). The `summary`
has `decided_by_rules`, `rules` (per rule id: `decided`, `agree`, `disagree`), `ai`
(`recommended`, `agree`, `disagree`, `unclear`), `by_outcome`, `unknown_reasons`,
`cost_per_sample` and `wall_ms`:

```json
"summary": {"samples": 10, "ran": 10, "errors": 0,
            "decided_by_rules": 8,
            "rules": {"known_sender": {"decided": 5, "agree": 4, "disagree": 1},
                      "clicked_credential_harvest": {"decided": 3, "agree": 3, "disagree": 0}},
            "ai": {"recommended": 1, "agree": 1, "disagree": 0, "unclear": 0},
            "by_outcome": {"closed_by_rule": 5, "escalated_by_rule": 3, "ai_recommends_benign": 1, "couldnt_tell": 1},
            "with_expected": 6, "expected_complete": true,
            "unknown_reasons": {"index_lag": 2},
            "cost_per_sample": {"steps": 6.5, "llm_usd": 0.002, "wall_ms": 2400}}
```

These numbers are informational: nothing at run time reads them. See
[Test on past alerts](templates.md#test-on-past-alerts).

### Stats

`GET /stats?since=&until=&template=` needs **read** plus `investigation_policy.set`.
`since` and `until` are RFC 3339 times on the runs' creation; `template` is a template
name. It aggregates at most the 2,000 most recent matching runs (`window.truncated`
says more matched), and a result can be up to 5 seconds old.

```json
{
  "window": {"template": "mailsec-message", "runs_considered": 41, "truncated": false},
  "runs": {"total": 41, "by_state": {"completed": 30, "decided": 8, "cancelled": 3},
           "by_verdict": {"true_positive": 9, "false_positive": 28, "inconclusive": 2, "undecided": 2},
           "by_outcome": {"escalated_by_rule": 9, "closed_by_rule": 26, "closed_by_ai": 2, "couldnt_tell": 2, "": 2}},
  "time_to_verdict_ms": {"p50": 410, "p95": 2300, "samples": 39},
  "speedup": {"p50": 2.4, "p95": 4.1, "samples": 6},
  "llm": {"usd": 0.31, "tokens": 91000},
  "operators": [{"op": "search.exists", "calls": 77, "p50_ms": 120.5, "p95_ms": 480, "errors": 2}],
  "feedback": {"labels": 12, "corrections": 3},
  "actions": {
    "by_class_state": {"close.false_positive": {"proposed": 5, "confirmed": 7, "reverted": 1, "denied": 1, "expired": 1}},
    "by_template_class": [
      {"template": "mailsec-message", "action_class": "close.false_positive", "total": 15,
       "suggested": 3, "approved": 3, "denied": 1, "expired": 1, "auto_executed": 5, "failed": 0, "undone": 1,
       "held": 2, "held_by_reason": {"policy_no_approvers": 2},
       "by_state": {"proposed": 5, "confirmed": 7, "reverted": 1, "denied": 1, "expired": 1}}
    ]
  }
}
```

The answer also has `concurrency`, `steps`, `speculation_efficiency` and `search`.

- **`runs.by_outcome`** counts runs per outcome; runs nothing settled yet count under
  `""`, and runs recorded before outcomes existed under their label.
  `time_to_verdict_ms` is the time to the first decision.
- **`speedup`** compares a run with a serial baseline of the same investigation (start
  one with `serial: true`); without a baseline it has `samples: 0`.
- **`actions.by_template_class`** has one row per template and action class with at
  least one action in the window. The counters are **not** a partition of `total`: an
  approved action can later be undone. Only `by_state` adds up to `total`.
  `suggested`: rested as a suggestion. `approved` / `denied`: a person decided.
  `expired`: nobody decided within `approval_timeout` (an expiry because the run ended
  is not counted). `auto_executed`: executed under `auto` with no person. `failed`: the
  execution was attempted and failed. `undone`: reverted at a person's request; a lease
  that simply expires shows as `reverted` in `by_state` and is not counted. `held`: it
  would have run automatically but was held, counted once, and once under each reason
  in `held_by_reason`.
- **`feedback`** counts the labels stored for the runs in the window. `corrections`
  can only be non-zero for runs labelled by earlier versions.
- The report says what the engine did. It never scores whether an outcome was right,
  and it changes nothing.

### Waves

`POST /waves` (write) runs a batch of operator calls now and returns compact answers.
There is no template, no outcome and no case. It runs with **your** token, counts
against the organization's concurrent run cap, and is kept as a run of `kind: wave`.

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
| `stop_when` | Up to 8 conditions with the same rules as a template's rules. The first one that is true cancels the steps still running. An unknown step never makes one true. |
| `deadline_ms` | Default 30000, capped by the policy's wall-time budget. |
| `inputs` | Named values steps and conditions may read as `$name`. |
| `full` | `true` returns raw values instead of compact ones. |
| `validate_only` | Validate and return the expanded steps without running anything. |
| `title`, `session`, `correlation_id` | Optional labels (at most 256 bytes each) to group the waves of one conversation; `GET /runs?kind=wave&session=` finds them. |

The answer has `run_id`, one result per step (`id`, `op` or `pack`, `status`, `reason`,
`complete`, `ms`, `value`), `stopped_by`, `usage` and `compact`. A step's `status` is
`ok`, `unknown` (with a `reason` such as `timeout`, `forbidden`, `dependency_unknown`,
`missing_input` or `policy_denied`), `cancelled` (only because `stop_when` fired) or,
for a pack, `partial`. A list cut at `limit` is `complete: false` (`truncated`): a
lower bound, never a count or a proof of absence. An invalid wave is refused before
anything runs, with `400` and the coded `errors`.
