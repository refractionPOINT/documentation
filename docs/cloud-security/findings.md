# Findings & Triage

Everything Cloud Security detects lands in one place: a merged, risk-ranked
findings worklist. CSPM misconfigurations, graph-derived attack paths, and
identity (CIEM) risks are all findings with the same shape, the same triage
verbs, and the same automation events.

## The worklist

Findings are ordered by `lc_risk` — a 0–1000 composite that weighs severity,
exposure, reachability, exploit intelligence (KEV / EPSS), and whether the
resource is sensitive. Each finding carries:

- `finding_id` (stable, prefixed `fnd_`) and `fingerprint` — the identity of
  the *condition*; the same misconfiguration on the same resource keeps the
  same fingerprint across sweeps.
- `finding_class` — one of `toxic_combination`, `public_exposure`,
  `ciem_risk`, `privilege_escalation`, `vulnerability`, `misconfig`,
  `malware`, `secret`, `scan_finding`, `coverage_gap`.
- `severity` (`CRITICAL` … `INFO`), `lc_risk`, and a `risk_breakdown`
  explaining the score.
- The affected resource (`resource_urn`, `resource_name`, `resource_type`,
  `account`, `region`), related resources, and — for path findings — the
  full `path` of hops.
- `evidence` (the offending configuration) and `remediation` (what to
  change).
- Vulnerability context where applicable: `vulns` (CVEs with fix versions),
  `epss`, `in_kev`.
- Runtime context: `runtime_sids` — the LimaCharlie sensors running on the
  affected asset, when the fusion mapping resolves any.

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
counts that drive the console's filter rail, and `finding get <id>` returns
one finding in full.

## Dispositions

A finding is `open` until the sweep observes the condition gone (automatic
close) or an operator dispositions it:

| Kind | Meaning |
|---|---|
| `mitigated` | The risk was fixed operator-side; treated as closed. |
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

Ownership and ticket linkage are separate, lighter-weight fields:

```bash
limacharlie cloudsec finding set-owner fnd_0a1b... --owner alice@acme.com
limacharlie cloudsec finding set-ticket fnd_0a1b... --ticket JIRA-1234
```

Dispositions can also be applied *as policy* — a `suppression`-typed
`cloudsec_policy` record auto-dispositions matching findings (see
[Automation & IaC](automation.md#suppression-rules-finding-disposition-policy)).
An operator's explicit disposition always wins over policy.

!!! info "Permissions"
    Reading findings requires `cloudsec.get`; every disposition, owner,
    ticket, and chokepoint write requires `cloudsec.set`.

## Chokepoints — fix one thing

Attack paths tend to share hops. The chokepoint view ranks resources by how
many distinct attack paths each one sits on, so remediation can be framed as
"fixing this one security group closes 41 of 63 paths":

```bash
limacharlie cloudsec chokepoint list
```

A chokepoint that is understood and tolerated (e.g. a bastion by design) can
be dismissed from the risk overview — and restored later:

```bash
limacharlie cloudsec chokepoint dismiss "lcrn:..." --reason "bastion by design"
limacharlie cloudsec chokepoint restore "lcrn:..."
```

## Overview, changes, and trend

Three read endpoints power the at-a-glance layer:

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
stream: `cloud_finding.created`, `cloud_finding.closed`, and a daily
`cloud_finding.still_open` for open findings with a linked ticket. D&R rules
match them like any other event — see
[Automation & IaC](automation.md#findings-cases-automation) for the
ready-made Cases loop.
