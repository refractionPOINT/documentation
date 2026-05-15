# Frameworks

`lc-compliance` ships reference content and a case-reviewer agent for seven compliance frameworks. Each framework's coverage is bundled inside the plugin under `${CLAUDE_PLUGIN_ROOT}/compliance/<framework>/`, where the skills resolve it at runtime.

## Verification levels

Every framework carries a declared **verification level** that describes how its control IDs have been reconciled against the standard's authoritative publisher:

| Level | Meaning |
|---|---|
| **MACHINE_VERIFIED** | Every control ID in the mapping has been programmatically reconciled against the standard's authoritative source (e.g., an OSCAL catalog, the eCFR XML, a published API). |
| **ATTESTATION_ONLY** | The format and structure of the citations have been validated, but the wording has not been reconciled programmatically because the authoritative source is a PDF that cannot be parsed reliably. A QSA / ISSO / certified assessor should review citations against the official document before relying on them in an external audit. |
| **UNVERIFIED** | The authoritative source is paywalled or otherwise inaccessible, and the mapping is based on publicly-available summaries. Each affected framework's attribution document explains how to upgrade the level if a licensed source extract is available. |

The level is declared in each framework's `attribution.md` file inside the plugin and is reported in the output of the `compliance-lookup` skill for every control queried.

| Framework | Level | Authoritative source |
|---|---|---|
| NIST SP 800-53 Rev 5 | **MACHINE_VERIFIED** | NIST OSCAL catalog |
| HIPAA Security Rule | **MACHINE_VERIFIED** | eCFR 45 CFR §164 |
| CMMC v2 | ATTESTATION_ONLY | NIST SP 800-171 Rev 2 PDF |
| PCI DSS v4.0 | ATTESTATION_ONLY | PCI SSC v4.0 PDF |
| SOC 2 | ATTESTATION_ONLY | AICPA Trust Services Criteria PDF |
| CIS Critical Security Controls v8 | ATTESTATION_ONLY | CIS Controls v8 PDF |
| ISO/IEC 27001:2022 | UNVERIFIED | ISO/IEC 27002:2022 (paywalled) |

## Per-framework details

The sections below summarize each framework's scope, recommended scope-tag convention, and any framework-specific arguments that the skills accept.

### CMMC v2

| Property | Value |
|---|---|
| Citation format | `AU.L2-3.3.1`, `AC.L1-3.1.1`, etc. |
| Reviewer agent | `cmmc-compliance-reviewer` |
| Accepted scope tags | `cui`, `cui-host`, `cmmc-scope`, `dib-host` |
| Verification level | ATTESTATION_ONLY (review against NIST SP 800-171 Rev 2) |
| Framework-specific skill args | None |

CMMC v2 inherits its Level 2 control set from NIST SP 800-171 Rev 2. Citations in the bundled mapping and implementation documents use the standard CMMC short-form (`<DOMAIN>.L<LEVEL>-3.x.x`). The reviewer agent is intended for systems handling Controlled Unclassified Information (CUI).

### NIST SP 800-53 Rev 5

| Property | Value |
|---|---|
| Citation format | `AC-2`, `AU-2`, `SI-4`, etc. |
| Reviewer agent | `nist-800-53-compliance-reviewer` |
| Accepted scope tags | `fisma-scope`, `fedramp-scope`, `federal-system`, `nist-scope` |
| Verification level | **MACHINE_VERIFIED** (NIST OSCAL catalog, 1,196 control IDs) |
| Framework-specific skill args | `--baseline <low\|moderate\|high>` on `compliance-gap` |

NIST 800-53 supports the FIPS 199 Low / Moderate / High baselines. The `compliance-gap` skill accepts a `--baseline` argument to scope the analysis to controls applicable at a given baseline level. The skill itself does not declare a default — if omitted, behaviour is to evaluate all controls in the bundled implementation document. Specify `--baseline` explicitly when the analysis should follow a single FIPS 199 tier.

### PCI DSS v4.0

| Property | Value |
|---|---|
| Citation format | `Req 10.2.1.4`, `Req 7.2.x`, etc. |
| Reviewer agent | `pci-compliance-reviewer` |
| Accepted scope tags | `cde`, `pci-scope`, `card-data`, `pci-dss` |
| Verification level | ATTESTATION_ONLY (review against PCI SSC v4.0 PDF — license restricts redistribution) |
| Framework-specific skill args | None |

The reviewer agent scopes itself to sensors tagged `cde` (cardholder data environment). PCI DSS v4.0 distinguishes between Requirement (top-level) and Sub-requirement (e.g., `10.2.1.4`). The lookup skill accepts both `pci` and `pci-dss` as the framework shorthand.

### HIPAA Security Rule

| Property | Value |
|---|---|
| Citation format | `§164.312(b)`, `§164.308(a)(1)(ii)(D)`, etc. |
| Reviewer agent | `hipaa-compliance-reviewer` |
| Accepted scope tags | `ephi-host`, `hipaa-scope`, `phi-host`, `covered-entity` |
| Verification level | **MACHINE_VERIFIED** (eCFR 45 CFR §164, 1,036 subsection IDs) |
| Framework-specific skill args | None |

HIPAA citations use the eCFR's section-and-subsection notation. The reviewer agent scopes itself to sensors tagged `phi` (protected health information). The skill accepts both `§164.312(b)` and `164.312(b)` as the control ID.

### SOC 2 (Trust Services Criteria)

| Property | Value |
|---|---|
| Citation format | `CC6.1`, `CC7.2`, `A1.2`, etc. |
| Reviewer agent | `soc2-compliance-reviewer` |
| Accepted scope tags | `soc2-scope`, `in-scope-system`, `audit-scope` |
| Verification level | ATTESTATION_ONLY (review against AICPA TSC PDF) |
| Framework-specific skill args | None |

SOC 2 citations follow the AICPA Trust Services Criteria short-form. CC (Common Criteria) controls apply to all SOC 2 Type II engagements; A, C, P, and PI categories apply only when the corresponding trust service is in scope.

### ISO/IEC 27001:2022

| Property | Value |
|---|---|
| Citation format | `A.8.15`, `A.5.10`, etc. |
| Reviewer agent | `iso-27001-compliance-reviewer` |
| Accepted scope tags | `isms-scope`, `iso-scope`, `iso-27001-scope`, `soa-included` |
| Verification level | **UNVERIFIED** (ISO standard is paywalled at ~$215 / ~$395 for combined 27001+27002) |
| Framework-specific skill args | None |

ISO/IEC 27002:2022 control identifiers (`A.x.y`) are used. The mapping is based on publicly-available summaries because the official ISO standard is not redistributable. The attribution document explains how to upgrade this framework to MACHINE_VERIFIED if a licensed extract is staged.

!!! warning "ISO 27001 verification level"
    Unlike the other six frameworks, ISO 27001 citations have not been programmatically reconciled against an authoritative source. A certified ISO 27001 lead auditor should review the citations in the mapping document before relying on them in a certification audit.

### CIS Critical Security Controls v8

| Property | Value |
|---|---|
| Citation format | `8.2`, `4.1`, `13.6`, etc. (Safeguard numbering) |
| Reviewer agent | `cis-v8-compliance-reviewer` |
| Accepted scope tags | `cis-scope`, `cis-v8-scope` (plus optional `cis-ig1`, `cis-ig2`, `cis-ig3` for tier) |
| Verification level | ATTESTATION_ONLY (review against CIS Controls v8 PDF — CC BY-NC-ND license) |
| Framework-specific skill args | `--ig <1\|2\|3>` on `compliance-gap` |

CIS v8 organizes safeguards into Implementation Groups (IG1 / IG2 / IG3) based on enterprise size and risk tolerance. The `compliance-gap` skill accepts an `--ig` argument to scope the analysis to safeguards applicable at a given implementation group. The skill does not declare a hard-coded default; if neither `--ig` is supplied nor a `cis-ig1`/`cis-ig2`/`cis-ig3` tag is set on a sensor, the analysis covers all safeguards in the bundled implementation document.

## Bundled artifacts per framework

For each framework, the plugin ships five artifacts under `${CLAUDE_PLUGIN_ROOT}/compliance/<framework>/`:

| File | Purpose |
|---|---|
| `<framework>-limacharlie-mapping.md` | Control-to-capability mapping. Quoted verbatim by the `compliance-lookup` skill. |
| `<framework>-limacharlie-implementation.md` | Deployable D&R / FIM / artifact-collection / exfil rules in YAML, each with the control citation in its metadata. |
| `<framework>-attribution.md` | Authoritative publisher, citation format, retrieval date, verification level, independent-re-verification procedure. |
| `recommended-rules.yaml` | Canonical rule-name baseline. The `compliance-gap` skill diffs deployed-rule names against this list. |
| `agent/` | Reviewer agent manifest (`<framework>-compliance-reviewer.yaml`) and the hive records (`ai_agent`, `dr-general`, `secret`) that `compliance-deploy` pushes. |

These artifacts are read at skill-invocation time. They are not synced into your organization automatically — synchronisation happens only when you explicitly invoke `compliance-deploy` or `compliance-baseline-deploy`.

## Updating to a newer framework version

When the plugin ships an updated implementation document for a framework (e.g., a new PCI sub-requirement is added), the recommended re-sync sequence is:

```text
/plugin update lc-compliance@lc-marketplace

/lc-compliance:compliance-baseline-deploy <framework> --oid <your-oid>   # dry-run
/lc-compliance:compliance-baseline-deploy <framework> --oid <your-oid> --apply
```

The baseline deploy is idempotent — rules already present under the same name are skipped, so re-running it picks up only the new rules. To replace existing rules with the updated definitions, use `--overwrite`.

To refresh the reviewer agent's prompt and tools after a plugin update:

```text
/lc-compliance:compliance-deploy <framework> --oid <your-oid>
```

## See also

- [Skills Reference](skills.md) — argument syntax for `--baseline`, `--ig`, and other framework-specific flags
- [Case-Reviewer Agent](case-reviewer-agent.md) — how the per-framework reviewer agent classifies cases
- [Gap Analysis](gap-analysis.md) — how the framework's recommended baseline is used to compute gaps
