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
   has the alert. If the queue cannot accept the start within about 2 seconds, the call is
   answered `unavailable` ("busy, retry"): see [When the engine is busy](#when-the-engine-is-busy).
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

## When the engine is busy

The start call answers within about 2 seconds of store work. If the queue has not accepted
the start in that time, or the engine server is already handling as many start calls as it
bounds, the call is answered `unavailable` (HTTP 503, "busy, retry"). This is about the
call, not the run: nothing was queued, so a D&R rule's `start investigation` action keeps the
start and sends it again for up to 15 minutes, and an API caller should retry.

- **Retry with the same `idempotency_key`.** If the first attempt did commit after all, the
  retry is answered by its run (`joined_by: idempotency_key`), so there is exactly one run.
  A start with no `idempotency_key` is not answered `unavailable` for the 2 seconds alone
  (a retry could not find its run): it waits for its enqueue's outcome.
- **A start that was accepted is never answered `unavailable`.** Past the 2 seconds it is
  answered with the run (`queued: true` until it starts) and goes on in the background. A start
  refused for good after it was accepted (its template became a draft, its identity is
  not allowed) answers that refusal when it comes within the 2 seconds, and otherwise shows
  it on the run (`state: failed`, `error_code`).
- A `wait_seconds` is honoured when the run goes live within the 2 seconds; one that starts
  later is answered queued.
- A start that a server could not start right away is given back to the queue and can be
  claimed again at once by any server.

## Coalescing

A template says how its alerts group into runs with the top-level key `coalesce`:

| `coalesce` | Alerts |
|---|---|
| `sensor` (the default) | Alerts on the same sensor, while a run of the same template is open for it, join that run. |
| `off` | One run per alert. |

**The alert a run started on is its subject for its whole life.** A joined alert is an extra
alert of the run: it is counted (`coalesced_alerts`), listed in the run's `detections` and
attached to its case. It is **not an input**: no step reads it, so it never changes what the
run investigates (its `detection_id`, the detection's document and event, its `entity_id`,
`question`, `case_id` and `alert_time` stay those of the alert that started it) or when
the run says it started. This holds whether the alert joined while the run waited or while
it ran. A queued run receives the alerts that joined it when it starts, oldest first; a
running one receives each within about a second. Once a run's investigation ended (it
decided, even if an action still waits for a person), it takes no more alerts: the next
alert on that sensor starts one new run, which the later ones join. About the first 1,000
alerts of a run are listed with their documents; later ones are counted (`coalesced_alerts`)
and not listed. The bound is about 1,000, not exact: each engine server counts it from its
own reads, so alerts that arrive on several servers in the same second can pass it by a few.

Evidence you add yourself to a running run (`add_run_inputs`, below) is different: it is the
starter's own, and the steps read it, except for what the run started on.

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

About 5 times `max_parallel_runs` (and never more than 2,000) of an organization's runs
can be parked on AI agents at once; past that a run waits for its agent while holding its
slot. The bound is approximate: parks that commit in the same instant can pass it by a few. A parked run that resumes counts again without waiting, so the organization can run
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
- A run that took an alert after the flush began is not the flush's: it runs with that alert
  and the ones it already had. Every engine server learns of a flush within about a second,
  so when a sensor keeps alerting as the flush begins, its queued run usually takes one of
  those alerts and runs instead of being flushed. Nothing is lost and nothing is cancelled
  twice either way.
- The command shows how many starts it will take and asks first (`--yes` skips the
  question). The answer has `flush_id`, `flushed` and `done`; a large flush goes on in the
  engine and the queue display shows its progress.
- The same flush repeated within a minute (a retry: same scope written the same way, same
  note and caller) is answered by the first one with `replayed: true`: it flushed nothing
  itself. A rule named `foo` after `general.foo` (or the reverse) is a new flush, not a
  replay.
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
