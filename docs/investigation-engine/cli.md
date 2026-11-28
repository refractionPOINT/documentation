# Command Line Interface

The `limacharlie investigate` command group builds and tests templates, starts and follows
runs, works the approvals inbox, and reads the settings, the queue and the stats. Install or
upgrade with `python -m pip install --upgrade limacharlie`.

!!! info "Versions"
    The commands on this page are in CLI **5.14.0**, except `investigate queue`,
    `investigate queue flush` and `investigate answer`, which are in the CLI's source but
    not in a release on PyPI yet. Until then use their [API routes](api-reference.md) or
    [MCP tools](mcp.md). Check what your CLI has with `limacharlie investigate --help`;
    every command also answers `--ai-help`.

Commands take the global options (`--oid`, `--output json|yaml|table|csv|jsonl`,
`--filter`, `--fields`). Use the organization's UUID for `--oid`. The permissions each
command needs are those of its [API route](api-reference.md).

A command that completes but says "no" (an invalid template or wave, a save the CLI refuses)
prints the engine's coded answer and exits with code **4**. Other failures keep the CLI's
codes: **2** for an HTTP 401 or 403, **3** for something that does not exist, **5** for a
rate limit, **1** for anything else. Read the `error_code`, not the exit code, to tell
causes apart. A 404 with no `error_code` means the Investigation Engine is not enabled on
that API host.

## Reference data

```bash
limacharlie investigate kit [--section guide|schema|operators|examples|settings|codes|packs|library]...
limacharlie investigate operators [--brief] [--name OP]... [--match TEXT]
limacharlie investigate packs [--brief] [--name PACK]
limacharlie investigate pack get NAME                    # an organization's own fact pack
limacharlie investigate pack save NAME --file pack.yaml [--etag ETAG]
limacharlie investigate pack delete NAME --confirm
```

Organization packs are `investigation_pack` records. Writing one needs `investigation_plan.set`
and a person (or an API key when the settings record is tagged `allow-api-key-promotion`).

The whole kit is large: read it in sections (`--section guide --section codes` first).

## Templates

```bash
limacharlie investigate templates list [--status draft|active]
limacharlie investigate templates get NAME [--yaml]
limacharlie investigate templates validate --file plan.yaml           # '-' reads stdin; exit 4 when invalid
limacharlie investigate templates test [NAME | --file plan.yaml] [samples] [options]
limacharlie investigate templates save NAME --file plan.yaml [--overwrite] [--status draft|active] [--comment TEXT] [--tag T]...
limacharlie investigate templates promote NAME --confirm
limacharlie investigate templates delete NAME --confirm
limacharlie investigate templates install-defaults [--name NAME]... [--overwrite] [--status draft|active]
```

Rules the CLI enforces:

- `save` writes a **draft** unless a person passes `--status active`. A source that says
  `status: active` is refused. An AI agent never passes `--status active` and never runs
  `promote`.
- A record is never overwritten without `--overwrite`, and a draft never replaces an active
  template.
- Every `act` entry is checked before saving: `approval` is required (`missing_approval`),
  a leased action needs `lease` and `on_lease_end`, and `class` is refused
  (`act_class_renamed`). Nothing is saved when validation reports an error.
- The CLI never rewrites a template's content beyond `status`, and converts nothing from an
  earlier format.
- `install-defaults` skips existing records, with their installed and library versions,
  unless `--overwrite`. Library templates are installed as drafts.

### Test on past alerts

| Flag | Sample |
|---|---|
| `--detection-id ID` | a stored detection (repeatable) |
| `--case-id ID` | a case; a closed case's classification is the expected answer |
| `--detect-cat CATEGORY --last N` | the newest N alerts of a category (N 1 to 25) |
| `--sample '{"inputs": {...}, "expected": "false_positive"}'` | free inputs |
| `--samples-file FILE` | a list of samples |

At most 25 samples in all. Other options: `--mode triage|full`, `--overrides-json`
(tighten-only budgets), `--strict` (refuse instead of ignoring a loosening), `--timeout` (default 600 s), `--no-wait`, `--test-id` (keep waiting
on a test started earlier), `--include-steps`. Exit codes: 0 done, 4 the template is
invalid, 1 the test failed.

## Runs

```bash
limacharlie investigate runs start (--template NAME | --file plan.yaml | --auto) \
    (--detection-id ID | --case-id ID | --entity-id ID | --question TEXT) \
    [--category C] [--severity S] [--priority N] [--tag T]... \
    [--input K=V]... [--inputs-json JSON] [--urgency low|medium|high|critical] [--mode triage|full|scope] \
    [--case-mode create|none|attach:ID] [--idempotency-key KEY] [--wait SECONDS] [--follow [--timeout S]] \
    [--trust-lookup NAME]... [--trust-value VALUE]...
limacharlie investigate runs get RUN_ID
limacharlie investigate runs list [--state S] [--outcome O] [--verdict V] [--template T] [--trigger T] \
    [--entity E] [--started-by ID] [--idempotency-key K] [--since TIME] [--until TIME] [--limit N] [--cursor C | --all]
limacharlie investigate runs events RUN_ID [--after SEQ] [--wait S] [--limit N] [--follow [--timeout S]]
limacharlie investigate runs steps RUN_ID [--values]
limacharlie investigate runs case RUN_ID
limacharlie investigate runs cancel RUN_ID [--revert-leases]
limacharlie investigate runs delete RUN_ID --confirm
limacharlie investigate wave --file wave.yaml [--validate-only] [--full] [--stop-when EXPR]... [--deadline-ms N] [--input K=V]...
```

- `--auto` sends no plan: the engine picks the active template whose `applies_to` matches
  `--category`, `--severity` and `--tag` (`source` is `api`).
- A start is sent once and never retried; `--idempotency-key` makes a repeat return the
  same run.
- `runs list --state` takes `queued`, `running`, `decided`, `completed`, `cancelled`,
  `failed`, `budget_exhausted`, `flushed`, `capped`.
- `runs events --follow` writes one JSON event per line until the run is over (exit 0) or
  `--timeout` passes (exit 1).

## Actions, settings and stats

```bash
limacharlie investigate actions list [--state awaiting_approval,held] [--class C] [--run-id ID] [--limit N] [--cursor C | --all]
limacharlie investigate actions approve RUN_ID ACTION_ID
limacharlie investigate actions deny RUN_ID ACTION_ID [--note TEXT]
limacharlie investigate settings get
limacharlie investigate settings pause
limacharlie investigate settings resume
limacharlie investigate stats [--template T] [--since TIME] [--until TIME]
```

- There is no `revert`, `extend` or `confirm` command: use the
  [API](actions.md#deciding-an-action), for example
  `limacharlie api "investigate/$OID/runs/<run>/actions/<action>/revert" -X POST`.
- `settings pause` and `resume` change only `paused` in `investigation_policy/default`,
  with a write conditional on the version read. They need `investigation_policy.get` and
  `investigation_policy.set`. If Git Sync manages that hive, set the pause in git.
- `settings get` shows what the engine enforces, including `warnings` (a record that does
  not parse is `settings_rejected`).
- `stats` and `runs list --outcome` / `--verdict` are reads like the others (`investigation.get` + `insight.evt.get`). The 5.14.0 help text still says they need `investigation_policy.set`; the engine does not ask for it.

## In the next release

```bash
limacharlie investigate queue
limacharlie investigate queue flush (--rule NAME | --template NAME | --all) [--note TEXT] [--yes]
limacharlie investigate answer (--answer JSON | --answer-file PATH|-) [--run-id ID] [--request-id ID] [--token TOKEN]
```

`queue` and `queue flush` are described in [The Run Queue](run-queue.md); `answer` is how an
AI agent's session answers a step (its ids and token default from `LC_IE_RUN_ID`,
`LC_IE_REQUEST_ID` and `LC_IE_ANSWER_TOKEN`; see
[Custom Code](custom-code.md#how-the-agent-answers)). Inside such a session, `runs start`
sends `parent_run`, so a run an agent starts asks no other agent.
