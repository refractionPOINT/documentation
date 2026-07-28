# Compliance

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and
    configuration formats on this page can change before general
    availability. Contact LimaCharlie to request access.

Cloud Security evaluates compliance frameworks continuously against the live
estate. Each control maps to detection rules, and a control fails when open
findings prove the violation. The compliance report is thus as fresh as the
last sweep, with evidence at the finding level for each control.

## The report

```bash
# Whole-estate assessment against a framework (default: cis-gcp).
limacharlie cloudsec compliance report --framework cis-gcp

# Which frameworks are available?
limacharlie cloudsec compliance frameworks
```

Ten frameworks are available today — `cis-aws`, `cis-azure`, `cis-gcp` (the
default), `soc2`, `pci-dss`, `hipaa`, `iso-27001`, `nist-csf`,
`nist-ai-rmf`, and `owasp-llm`. The last two are AI frameworks: they assess
the OpenAI and Anthropic estate that you connect through the
[AI providers](providers.md#ai-security-aispm). The set grows over time, so
`limacharlie cloudsec compliance frameworks` (`GET /compliance/frameworks`)
is the source of truth for valid `--framework` values. It carries the `id`,
`name`, `version`, and control counts of each framework.

The report gives one result for each control, and each control has one of
four states:

- **PASS** — no open finding proves a violation of the control.
- **FAIL** — one or more open findings prove it; the report attaches their
  `finding_id`s as evidence.
- **NOT_ASSESSED** — the control has no mapped rule yet, so nothing was
  evaluated.
- **NOT_APPLICABLE** — the control maps to resource types that are not in
  scope for this assessment.

A framework scoped to a single cloud assesses only the findings of that
cloud — `cis-aws` looks at AWS findings, `cis-gcp` at GCP. A framework with
no in-scope resource types returns **NOT_APPLICABLE** instead of an empty
PASS, so an empty estate never reads as compliant. With the controls, the
report also carries a summary score.

For auditors, the same report exports as CSV with the `?format=csv`
parameter of the API — one row for each control, including the evidence
finding ids (see [Automation & IaC](automation.md#csv-export)).

## Scoped assignments

A score for the whole estate is often too coarse: production must obey the
framework, the sandbox does not. A `compliance`-typed `cloudsec_policy`
record creates a **named, scoped assignment** — a framework evaluated over a
subset of the estate:

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
and `name_glob`. Globs use the shared dialect, including leading-`!`
negation — see [Glob syntax](configuration.md#glob-syntax). An empty scope
means the whole estate.

List assignments (each with its own scoped score) and evaluate one:

```bash
limacharlie cloudsec compliance assignments
limacharlie cloudsec compliance report --assignment prod-cis
```

If you set `--assignment`, the command uses its framework and ignores
`--framework`.

!!! info "Permissions"
    To read compliance, you need `cloudsec.get`. Assignments are Hive policy
    records, so their creation obeys the `cloudsec_policy` hive permissions.
