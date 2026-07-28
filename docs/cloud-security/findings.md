# Findings & Triage

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

Everything that Cloud Security detects goes to one place: a merged,
risk-ranked findings worklist. CSPM misconfigurations, graph-derived attack
paths, and identity (CIEM) risks are all findings with the same shape, the
same triage verbs, and the same automation events.

!!! info "In the console it's called **Risks**"
    The worklist is the **Risks** page. Lens tabs divide it but keep the
    unified ranking: *All risks*, *Public exposure & misconfig*, *Identity*,
    *Vulnerabilities*, and *Data*. Everything below is the same
    data through the CLI/API.

## The worklist

Findings are ordered by `lc_risk` — a 0–1000 composite that weighs severity,
exposure, reachability, exploit intelligence (KEV / EPSS), and whether the
resource is sensitive. Each finding carries:

- `finding_id` (stable, prefixed `fnd_`) and `fingerprint` — the identity of
  the *condition*; the same misconfiguration on the same resource keeps the
  same fingerprint across sweeps.
- `finding_class` — one of `toxic_combination`, `public_exposure`,
  `ciem_risk`, `privilege_escalation`, `vulnerability`, `misconfig`,
  `coverage_gap`, `device_posture`.
- `severity` (`CRITICAL` … `INFO`), `lc_risk`, and a `risk_breakdown` that
  explains the score.
- The affected resource (`resource_urn`, `resource_name`, `resource_type`,
  `account`, `region`), related resources, and — for path findings — the
  full `path` of hops.
- `evidence` (the offending configuration) and `remediation` (what to
  change).
- Vulnerability context where applicable: `vulns` (CVEs with fix versions),
  `epss`, `in_kev`.
- Runtime context: `runtime_sids` — the LimaCharlie sensors that run on the
  affected asset, when the fusion mapping resolves any.

Attack-path and `toxic_combination` findings show the durable **workload
group** instead of a single ephemeral node: a GKE/EKS/AKS node pool, a GCE
managed instance group, an AWS Auto Scaling group, or an Azure VM scale set.
`source_scope` / `target_scope` carry the group, so remediation is one shared
fix for the whole pool instead of one finding for each short-lived VM.

For identity (CIEM) findings, the **capability** that a grant confers scores
the access — `data_admin` › `data_write` › `data_read` › `metadata` › `none`
— not the existence of the grant alone. "Reaches sensitive data" gates on
`data_read` or higher. `metadata`/`none` grants appear as a reconnaissance
signal with lower severity, not as a top data-access risk.

List, filter, and paginate server-side:

```bash
limacharlie cloudsec finding list \
  --severity CRITICAL --severity HIGH \
  --class toxic_combination --status open \
  --kev --limit 50
```

Repeatable filters are OR within a key and AND across keys. Free-text search
is `-q`; pagination is keyset-based (`next_cursor` from one page becomes
`--cursor` for the next). `finding facets` returns the cross-filtered facet
counts that drive the filter rail in the web app, and `finding get <id>`
returns one finding in full.

## Dispositions

A finding is `open` until the sweep sees that the condition is gone
(automatic close), or until an operator dispositions it:

| Kind | Meaning |
|---|---|
| `mitigated` | The operator fixed the risk; the finding counts as closed. |
| `accepted` | Known and accepted, optionally until an expiry (`expires_at`, unix seconds) — after which it reopens. |
| `false_positive` | The finding was wrong. |
| `open` | Clears a previous disposition and reopens the finding (owner and ticket are kept). |

```bash
# Accept a known risk for 90 days.
limacharlie cloudsec finding resolve fnd_0a1b... --kind accepted \
  --reason "sandbox accepted risk (SEC-123)" --expires-at 1767225600

# Reopen it.
limacharlie cloudsec finding resolve fnd_0a1b... --kind open

# Disposition a batch at once.
limacharlie cloudsec finding bulk-resolve \
  --finding-id fnd_0a1b... --finding-id fnd_2c3d... \
  --kind false_positive --reason "scanner artifact"
```

The `bulk-resolve` route applies one disposition to many findings at once, but
it does **not** accept `open` — reopen findings one at a time with
`finding resolve <id> --kind open`.

In the web app, the same dispositions are one-click buttons on a finding,
with the workflow actions that are built on them:

| Button | What it does |
|---|---|
| **Mark fixed** | disposition `mitigated` |
| **Accept risk** | disposition `accepted`, with an optional re-surface expiry |
| **Mute** | disposition `false_positive` |
| **Reopen** | clears the disposition |
| **Assign owner** | sets/clears `owner` |
| **Link ticket** | sets/clears `ticket` |
| **Create case** | one-click, idempotent — opens (or updates) the linked case |
| **Create suppression rule** | opens a prefilled `suppression` policy rule |
| **Create D&R rule** | opens a prefilled detection & response rule |

Ownership and ticket linkage are separate, lighter-weight fields:

```bash
limacharlie cloudsec finding set-owner fnd_0a1b... --owner alice@acme.com
limacharlie cloudsec finding set-ticket fnd_0a1b... --ticket JIRA-1234
```

You can also apply dispositions *as policy* — a `suppression`-typed
`cloudsec_policy` record auto-dispositions matching findings (see
[Automation & IaC](automation.md#suppression-rules-finding-disposition-policy)).
The explicit disposition of an operator always wins over policy.

!!! info "Permissions"
    To read findings, you need `cloudsec.get`. Every disposition, owner,
    ticket, and chokepoint write needs `cloudsec.set`.

## Chokepoints — fix one thing

Attack paths often share hops. The chokepoint view ranks resources by the
number of distinct attack paths that each one is on. Remediation then reads
as "a fix to this one security group closes 41 of 63 paths":

```bash
limacharlie cloudsec chokepoint list
```

You can dismiss a chokepoint that you understand and accept (for example, a
bastion by design) from the risk overview, and restore it later:

```bash
limacharlie cloudsec chokepoint dismiss "lcrn:..." --reason "bastion by design"
limacharlie cloudsec chokepoint restore "lcrn:..."
```

## Overview, changes, and trend

Three read endpoints supply the summary layer:

```bash
# Score, severity distribution, top paths, coverage, trend — one call.
limacharlie cloudsec overview --trend-days 90

# The created/closed feed, newest first.
limacharlie cloudsec changes --limit 100

# The risk-score history on its own.
limacharlie cloudsec risk-trend --trend-days 90
```

## Findings are events too

Every lifecycle transition emits an event into the organization's event
stream, so D&R rules, Outputs, and the Cases loop consume findings like any
other telemetry. Two families:

**Detection-truth lifecycle** (emitted by the projector when the sweep
observes the world):

- `cloud_finding.created` — a new finding; the full finding object is under
  `event/finding` (including `runtime_sids`).
- `cloud_finding.updated` — the content of an already-open finding materially
  changed (a severity flip, a changed vuln set); payload names the
  `changed` fields, `old_severity`/`new_severity`, and carries the current
  `finding`.
- `cloud_finding.closed` — the condition is gone; `{finding_id, fingerprint,
  finding_class}`.
- `cloud_finding.still_open` — re-asserted at most once a day for open
  findings that carry a linked ticket, the heartbeat that keeps a Case
  correct when the cloud was not fixed.

**Operator-disposition verbs** (emitted by the write handlers, flat payload
`{finding_id, fingerprint, finding_class, actor, note?}`):
`cloud_finding.resolved`, `cloud_finding.dismissed`, `cloud_finding.reopened`,
`cloud_finding.assigned`.

**Summary:** on the first-ever projection (or a rebuild) the cloud emits a
single `cloudsec.sync_completed` (`{total, by_class, by_severity}`) instead of
a flood of `created` events, one for each finding — first-sync suppression.

See [Automation & IaC](automation.md#findings-cases-automation) for the
ready-made Cases loop that keys on `fingerprint`, and the
[`emission` policy](configuration.md#emission-the-event-feed) for the feed
controls (severity floor, which families are on).
