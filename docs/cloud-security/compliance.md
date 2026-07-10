# Compliance

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

The report is per-control pass/fail with the proving finding ids as
evidence, plus a summary score. The frameworks list carries `id`, `name`,
`version`, and control counts — treat it as the source of truth for valid
`--framework` values.

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
