# The Run Queue

Every start of a run goes through a durable queue in the organization's region. A start is
**never dropped and never refused for load** (unless you set an hourly cap, `limits.runs_per_hour`): above the organization's limit it waits, and
it starts as soon as a slot frees. The queue is what lets a burst of alerts (a noisy rule,
a worm) be investigated in order without losing any of them, and what lets you see and
clear what waits.

!!! warning "Experimental"
    Billing per run is not on. This page states no price.

## What happens to a start

1. A D&R rule (or a person, or the API) starts a run. The start is recorded in the queue in
   one transaction and answered at once with `queued: true`. From that moment the platform
   has the alert.
2. If the alert belongs to a run that is already open, it **joins** that run instead (see
   [Coalescing](#coalescing)).
3. A replica with a free slot claims the start, pins the template as it is **now** (a
   template fixed while runs wait helps them), resolves the identity and starts the run.
4. On an idle organization the queue and the start are one step: a run starts without
   waiting.

A run that went through the queue shows `queued_at` (when the platform had the alert),
`started_at`, `queue_wait_ms`, `queue_band` and `queue_path` (`fast` on an idle
organization, `claimed` otherwise). The time to verdict and the run's wall budget start
when the run starts, not when it was queued.

Waves, template tests and "check again" runs are not queued.

## Coalescing

A template says how its alerts group into runs with the top-level key `coalesce`:

| `coalesce` | Alerts |
|---|---|
| `sensor` (the default) | Alerts on the same sensor, while a run of the same template is open for it, join that run. |
| `off` | One run per alert. |

A joined alert is added to the run's inputs and its case; it never changes the alert the run
is about. A queued run receives the alerts that joined it when it starts, oldest first; a
running one receives each within about a second. Once a run's investigation ended (it
decided, even if an action still waits for a person), it takes no more alerts: the next
alert on that sensor starts one new run, which the later ones join. The first 1,000 alerts
of a run are fed to it; later ones are counted (`coalesced_alerts`) but not fed.

A D&R rule's `coalesce_key` (default `sid:<sensor id>`) says which alerts belong together;
an alert joins only an open run of the same template. A template that says `coalesce: off`
wins: one run per alert and rule, whatever key the rule sends. A repeated start of the same detection by the same rule returns the run it
already has (`joined_by: idempotency_key`).

## Fairness and order

- **Per organization.** Each organization has its own slots
  (`limits.max_parallel_runs`) and claims are shared fairly between organizations, so one
  organization's flood does not take another's slots.
- **By urgency.** Within an organization, starts are claimed by band: `interactive` (a
  person's start) first, then the rule's `urgency`: `critical`, `high`, `medium`, `low`.
  Within a band, oldest first.
- A run waiting for a person's approval holds no slot, and neither does a run parked on an
  [AI agent's answer](custom-code.md#ai-agent-steps).

## The limits

Both are in the [settings record](settings.md#limits):

| Field | Default | Meaning |
|---|---|---|
| `limits.max_parallel_runs` | 100 (1 to 2000) | How many runs of the organization execute at once, region-wide. The rest wait. |
| `limits.runs_per_hour` | none | How many runs may start in a UTC clock hour. Above it a new start is not queued: it is recorded as a terminal **`capped`** run (its alert shows as not investigated, it is not billed, kept 7 days). Starts already queued wait for the next hour. |

At most 5 times `max_parallel_runs` (and never more than 2,000) of an organization's runs
can be parked on AI agents at once; past that a run waits for its agent while holding its
slot. A parked run that resumes counts again without waiting, so the organization can run
above its limit by at most the runs that resumed.

## The queue display

```bash
limacharlie investigate queue --oid "$OID"
```

```json
{"queued": 1240, "claimed": 12, "running": 25, "parked": 3, "max_parallel_runs": 100,
 "oldest_enqueued_at": "2026-11-25T18:02:11.120Z", "oldest_wait_ms": 184000,
 "by_band": {"interactive": 0, "critical": 0, "high": 40, "medium": 1200, "low": 0},
 "by_rule": [{"rule": "general.fictional-noisy-rule", "queued": 1200, "oldest_enqueued_at": "..."}],
 "by_template": [{"template": "suspicious-process", "queued": 1200, "oldest_enqueued_at": "..."}],
 "hour": {"started": 812, "runs_per_hour": 2000, "flushed": 0, "capped": 0, "start_failed": 0,
          "resets_at": "2026-11-25T19:00:00Z"},
 "flushes": [],
 "as_of": "2026-11-25T18:05:15.000Z"}
```

- `queued` waits for a slot, `claimed` is being started, `running` holds a slot, `parked`
  waits on an AI agent and holds none.
- The counts are exact at `as_of` (at most 5 seconds old). `by_band`, `by_rule` and
  `by_template` each add up to `queued` and list **every** rule and template with waiting
  starts, never a page. A person's start has no rule.
- `hour` is the current UTC hour: runs started, the cap (`null` without one), and the starts
  flushed, capped and failed before starting. `flushes` are the 10 most recent.

`limacharlie investigate runs list --state queued` (or `flushed`, `capped`) lists the runs
themselves. The console shows the same panel.

## Flush

A flush removes queued starts that have not started yet: those of one rule, one template, or
all of them. Use it when a rule fired thousands of times by mistake: fix the rule, then
flush what it queued.

```bash
limacharlie investigate queue flush --rule fictional-noisy-rule --note "rule fixed" --oid "$OID"
```

- Name exactly one scope: `--rule`, `--template` or `--all`. A rule can be named as the
  queue shows it (`general.<name>`) or by its bare name; a bare name queued under several
  namespaces is refused (`rule_ambiguous`, with the candidates). A name with nothing queued
  flushes nothing and says so (`rule_not_queued`, with the rules that are queued).
- Each flushed start becomes a terminal **`flushed`** run that records who flushed it, when
  and the note. Its alert shows as not investigated. It is not billed.
- Only starts queued before the flush began are taken; alerts that arrive during it queue
  as usual. Running runs are never touched (cancel them instead). **A flush cannot be
  undone.**
- The command shows how many starts it will take and asks first (`--yes` skips the
  question). The answer has `flush_id`, `flushed` and `done`; a large flush goes on in the
  engine and the queue display shows its progress.
- The same flush repeated within a minute (a retry) is answered by the first one with
  `replayed: true`: it flushed nothing itself.
- Every flush is in the organization's audit log (`ie_queue_flushed`), filed under who
  flushed.

API: `GET /v1/investigate/{oid}/queue`, `POST /v1/investigate/{oid}/queue/flush` with
exactly one of `rule`, `template` or `all: true`, and an optional `note`.

## States of a start that never ran

| State | Why |
|---|---|
| `queued` | Waiting for a slot. |
| `flushed` | Removed by a flush. Not investigated. |
| `capped` | Recorded at the hourly cap. Not investigated. |
| `failed` | It could not start: the template was deleted or no longer applies (`template_gone`), became a draft (`template_draft`), the identity is not allowed (`identity_not_allowed`), or it was claimed three times without starting (`start_failed`). |

## Billing

A run is counted once, when it starts. Joined alerts, `flushed` and `capped` starts, starts
that failed before starting, waves, tests and "check again" runs are not counted. Billing
per run is not on.

## Not available yet

`limacharlie investigate queue` and `queue flush` are not in the CLI release on PyPI yet
(5.14.0). Use the API routes above or the MCP tools `investigate_queue` and
`investigate_flush_queue`.
