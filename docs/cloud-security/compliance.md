# Compliance

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Cloud Security evaluates compliance frameworks continuously against the live
estate: each control maps to detection rules, and a control fails when open
findings prove the violation — so the compliance report is always as fresh
as the last sweep, with finding-level evidence per control.

## The report

```bash
# Whole-estate assessment against a framework (default: cis-gcp).
limacharlie cloudsec compliance report --framework cis-gcp

# Which frameworks are available?
limacharlie cloudsec compliance frameworks
```

Ten frameworks ship today — `cis-aws`, `cis-azure`, `cis-gcp` (the default),
`soc2`, `pci-dss`, `hipaa`, `iso-27001`, `nist-csf`, `nist-ai-rmf`, and
`owasp-llm`. The last two are AI frameworks: they assess the OpenAI and
Anthropic estate connected through the
[AI providers](providers.md#ai-security-aispm). The set
grows over time, so `limacharlie cloudsec compliance frameworks`
(`GET /compliance/frameworks`) — which carries each framework's `id`, `name`,
`version`, and control counts — is the source of truth for valid
`--framework` values.

The report is per-control, and each control lands in one of four states:

- **PASS** — no open finding proves a violation of the control.
- **FAIL** — one or more open findings prove it; their `finding_id`s are
  attached as evidence.
- **NOT_ASSESSED** — the control has no mapped rule yet, so nothing was
  evaluated.
- **NOT_APPLICABLE** — the control maps to resource types that are not in
  scope for this assessment.

A framework scoped to a single cloud assesses only that cloud's findings —
`cis-aws` looks at AWS findings, `cis-gcp` at GCP. A framework with no
in-scope resource types comes back **NOT_APPLICABLE** rather than a vacuous
PASS, so an empty estate never reads as compliant. Alongside the controls the
report carries a summary score.

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
and `name_glob`; an empty scope means the whole estate.

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
