# Compliance

Cloud Security evaluates compliance frameworks continuously against the live
estate. Controls combine observed configuration, findings and, where required,
scoped manual evidence. A finding can prove a violation even when collection is
partial. A clean result receives credit only after the required collection and
assessment finish against the current connection settings. A report is an
assessment of that evidence, not certification of the entire framework.

## The report

```bash
# Whole-estate assessment against a framework (default: cis-gcp).
limacharlie cloudsec compliance report --framework cis-gcp

# Which frameworks are available?
limacharlie cloudsec compliance frameworks
```

Fifteen frameworks ship today: `cis-aws`, `cis-azure`, `cis-gcp` (the
default), `cis-gcp-v5`, `cis-m365`, `cis-m365-v7`, `soc2`, `pci-dss`, `hipaa`,
`iso-27001`, `nist-csf`, `nist-ai-rmf`, `owasp-llm`, `owasp-top10`, and
`cis-supply-chain`. `nist-ai-rmf`
and `owasp-llm` are AI frameworks: they assess the OpenAI and Anthropic estate
connected through the [AI providers](providers.md#ai-security-aispm).
`owasp-top10` (OWASP Top 10:2021, mapped by CWE) and `cis-supply-chain` (the CIS
Software Supply Chain Security Guide's *Source Code* and *Dependencies*
sections) use [Code Security](code-security/results.md#compliance), GitHub
configuration and manual evidence, and apply to connected GitHub organizations.
The Supply Chain dependency scanner checks combine observed settings across active
GitHub repositories with code-scan observations under your selected policy. They
do not certify complete software composition analysis across every repository.
OWASP A06/A08 and CIS Supply Chain 3.1.1 can FAIL from observed code findings;
their clean assessment currently remains unverified because the required code
evaluation completion evidence is unavailable.
The set grows over time, so `limacharlie cloudsec compliance frameworks`
(`GET /compliance/frameworks`) — which carries each framework's `id`, `name`,
`version`, and control counts — is the source of truth for valid
`--framework` values.

### CIS benchmark versions

Two CIS benchmarks ship in two versions, side by side. Each version is its own
framework id, so an assignment or report on the older id keeps working
unchanged, and you move to the newer one when you are ready:

| Framework | Benchmark | Controls |
|---|---|---|
| `cis-gcp` | CIS Google Cloud Platform Foundation Benchmark (v2.0 subset) | 21 |
| `cis-gcp-v5` | CIS Google Cloud Platform Foundation Benchmark v5.0.0 | 93: 76 automated, 8 partly automated, 9 manual |
| `cis-m365` | CIS Microsoft 365 Foundations Benchmark (v4.0 subset) | 26 |
| `cis-m365-v7` | CIS Microsoft 365 Foundations Benchmark v7.0.0 | 160: 143 automated, 17 manual |

The newer catalogs include every benchmark control; collection support and
manual requirements still determine which controls can be assessed. Each control
carries its CIS recommendation number (`external_id`, for example `5.1.2.3`) with a title and a
description of what LimaCharlie checks, written by LimaCharlie. The benchmark
text itself is published by CIS at
[cisecurity.org](https://www.cisecurity.org/cis-benchmarks).

- **`cis-gcp-v5`** reads project and organization configuration (IAM, logging and
  alerting, networking, compute, Cloud SQL, storage, BigQuery). Several of these
  reads need optional roles or APIs on the service account; without them, the
  controls they feed report NOT_ASSESSED and name the missing read. See
  [Google Cloud provider setup](provider-setup/gcp.md). A partly automated control
  can FAIL from what LimaCharlie reads, but a PASS also needs your attestation,
  so without one it reports NOT_ASSESSED.
- **`cis-m365-v7`** covers Entra ID, Exchange Online, Defender for Office 365,
  Purview, SharePoint and OneDrive, Teams, Intune, Microsoft Forms and
  Power BI / Fabric. It applies to a tenant connected as an
  [`entra` provider](provider-setup/entra.md). Its Microsoft Graph reads work with
  either credential type. Exchange Online, Defender for Office 365, Purview and
  the SharePoint advanced settings need the connection's
  [certificate mode](provider-setup/entra.md#authentication-modes). The Entra half of
  an `azure` connection reads the Microsoft Graph settings only; Exchange Online,
  Purview, Teams and Power BI / Fabric are read through an `entra` connection.
- **`cis-m365`** (v4.0) covers a benchmark selection. Its Entra checks apply to
  an `entra` provider or the Entra half of an `azure` connection. An `entra`
  connection also supplies the named v7 reads reused by legacy checks: password
  expiration, common attachment filtering, unified audit logging, privileged-role
  access review definitions, SharePoint external sharing and Teams anonymous
  meetings. The non-Graph reads need certificate mode as described above. This
  reuse does not assess every control in those admin centers or change an
  assignment to the v7 benchmark.

!!! note "Licence-gated Microsoft 365 controls"
    37 `cis-m365-v7` controls grade a feature that exists only with a specific
    Microsoft licence: Entra ID P1 or P2, Entra ID Governance, Intune, Defender for
    Office 365 Plan 1 or 2, Safe Documents, Customer Lockbox, or Purview
    Communications DLP. LimaCharlie reads the tenant's licences. When a tenant does
    not hold the licence a control needs, that control reports **NOT_ASSESSED** and
    its reason names the licence, for example `no licence was observed for the
    feature this control grades: Microsoft Entra ID P1`. It never reports PASS
    for a feature the tenant cannot turn on. It does not report FAIL either,
    because the fix is a purchase, not a setting.

The report is per-control, and each control lands in one of four states:

- **PASS** — every required input was read, the relevant detectors completed,
  no open finding proves a violation, and any required manual evidence is valid
  for the assessed scope.
- **FAIL** — one or more open findings prove it; their `finding_id`s are
  attached as evidence.
- **NOT_ASSESSED** — evidence is missing or unverified. This includes unread,
  denied, capped or stale collection; changed connection settings awaiting a
  successful collection; incomplete assessment; and manual requirements without
  valid scoped evidence. A partly automated control can FAIL from observed
  counterevidence, but needs its manual requirements satisfied to PASS. A control
  also lands here when the detection that would have decided it never ran —
  including when a [`rules` policy](custom-rules.md#compliance-interaction) has **disabled every
  rule the control relies on** and it has no other basis to be graded from. A
  zero-violation result from a detector that did not run is not evidence of
  compliance, so it is never reported as a PASS.
- **NOT_APPLICABLE** — complete observation proves that the control has no
  eligible resources in this scope, or authoritative connection inventory proves
  its provider is absent. A newly connected, unread or failed provider is
  **NOT_ASSESSED**, even if no resources have been inventoried yet.

A framework scoped to a single cloud assesses only that cloud's findings —
`cis-aws` looks at AWS findings, `cis-gcp` at GCP. A framework with no
eligible resources comes back **NOT_APPLICABLE** only when absence is established,
so an unread estate never reads as compliant.

### How the score is computed

The report's summary carries `passed`, `failed`, `not_assessed`,
`not_applicable`, `total`, `score`, and `applicable`. The score is the share of
**assessable** controls that pass:

```text
score = passed / (passed + failed) × 100
```

Only PASS and FAIL are assessable. NOT_ASSESSED and NOT_APPLICABLE controls are
excluded from the denominator entirely, so a manual control you have not
attested does not drag the number down, and a framework you are only partly in
scope for is not penalized for the parts that do not apply.

!!! warning "No assessable controls means `applicable: false`, not 100%"
    When nothing in the framework is assessable against your estate, the report
    comes back with `applicable: false` and a `score` of **0** — never a
    vacuous 100. Read `applicable` before reading `score`: a 0 with
    `applicable: false` means "we could not assess this", not "you failed
    everything".

!!! note "FAIL evidence is capped per control"
    A failing control attaches at most **25** proving `finding_id`s in the JSON
    report, while `evidence_count` reports the true total — so a control with
    900 violations shows 25 examples and `evidence_count: 900`. The CSV export
    raises the cap to 2,000 ids per control for auditors who need the fuller
    list; use the [findings API](findings.md) itself when you need all of them.

### Auditor export

For auditors, the same report exports as CSV — one row per control including
the evidence finding ids — via the API's `?format=csv`
(see [Automation & IaC](automation.md#csv-export)).

## Scoped assignments

A whole-estate score is often the wrong altitude: production must meet the
bar, the sandbox does not. A `compliance`-typed `cloudsec_policy` record
creates a **named, scoped assignment** — a framework evaluated over a subset
of the estate:

```bash
cat > prod-cis.json <<EOF
{
  "policy_type": "compliance",
  "compliance": {
    "framework_id": "cis-gcp",
    "description": "Production accounts only",
    "scope": [
      {"account_glob": ["proj-prod-*"]}
    ]
  }
}
EOF

limacharlie hive set --hive-name cloudsec_policy --key prod-cis \
  --oid $OID --input-file prod-cis.json --enabled
```

Scope matchers support `account_contains`, `account_glob`, `name_contains`,
and `name_glob` (globs use the shared dialect, including leading-`!`
negation — see [Glob syntax](configuration.md#glob-syntax)); an empty scope
means the whole estate.

List assignments (each with its own scoped score) and evaluate one:

```bash
limacharlie cloudsec compliance assignments
limacharlie cloudsec compliance report --assignment prod-cis
```

When `--assignment` is set, its framework is used and `--framework` is
ignored.

!!! info "Permissions"
    Reading compliance requires `cloudsec.get`. Assignments are Hive policy
    records, so creating them follows the `cloudsec_policy` hive
    permissions.
