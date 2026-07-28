# Frameworks

`lc-compliance` supplies reference content and a case-reviewer agent for seven compliance frameworks. The plugin holds the coverage for each framework under `${CLAUDE_PLUGIN_ROOT}/compliance/<framework>/`. The skills read it from that location when they run.

## Verification levels

Every framework has a declared **verification level**. The level describes how the control IDs of the framework were reconciled against the authoritative publisher of the standard:

| Level | Meaning |
|---|---|
| **MACHINE_VERIFIED** | A program reconciled every control ID in the mapping against the authoritative source of the standard (for example, an OSCAL catalog, the eCFR XML, or a published API). |
| **ATTESTATION_ONLY** | The format and the structure of the citations are validated, but no program reconciled the wording, because the authoritative source is a PDF that cannot be parsed reliably. A QSA, ISSO, or certified assessor should review the citations against the official document before you use them in an external audit. |
| **UNVERIFIED** | The authoritative source is paywalled or is not accessible, and the mapping is based on publicly available summaries. The attribution document of each affected framework explains how to upgrade the level if a licensed extract of the source is available. |

The `attribution.md` file of each framework inside the plugin declares the level. The `compliance-lookup` skill reports the level in its output for every control that you query.

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

The sections below summarize the scope of each framework, the recommended convention for scope tags, and the framework-specific arguments that the skills accept.

### CMMC v2

| Property | Value |
|---|---|
| Citation format | `AU.L2-3.3.1`, `AC.L1-3.1.1`, etc. |
| Reviewer agent | `cmmc-compliance-reviewer` |
| Accepted scope tags | `cui`, `cui-host`, `cmmc-scope`, `dib-host` |
| Verification level | ATTESTATION_ONLY (review against NIST SP 800-171 Rev 2) |
| Framework-specific skill args | None |

CMMC v2 takes its Level 2 control set from NIST SP 800-171 Rev 2. The citations in the bundled mapping and implementation documents use the standard CMMC short form (`<DOMAIN>.L<LEVEL>-3.x.x`). The reviewer agent is for systems that handle Controlled Unclassified Information (CUI).

### NIST SP 800-53 Rev 5

| Property | Value |
|---|---|
| Citation format | `AC-2`, `AU-2`, `SI-4`, etc. |
| Reviewer agent | `nist-800-53-compliance-reviewer` |
| Accepted scope tags | `fisma-scope`, `fedramp-scope`, `federal-system`, `nist-scope` |
| Verification level | **MACHINE_VERIFIED** (NIST OSCAL catalog, 1,196 control IDs) |
| Framework-specific skill args | `--baseline <low\|moderate\|high>` on `compliance-gap` |

NIST 800-53 supports the FIPS 199 Low, Moderate, and High baselines. The `compliance-gap` skill accepts a `--baseline` argument that scopes the analysis to the controls that apply at one baseline level. The skill declares no default. If you omit the argument, the skill evaluates all controls in the bundled implementation document. Give `--baseline` when the analysis must use one FIPS 199 tier.

### PCI DSS v4.0

| Property | Value |
|---|---|
| Citation format | `Req 10.2.1.4`, `Req 7.2.x`, etc. |
| Reviewer agent | `pci-compliance-reviewer` |
| Accepted scope tags | `cde`, `pci-scope`, `card-data`, `pci-dss` |
| Verification level | ATTESTATION_ONLY (review against PCI SSC v4.0 PDF — license restricts redistribution) |
| Framework-specific skill args | None |

The reviewer agent scopes itself to sensors with the `cde` tag (cardholder data environment). PCI DSS v4.0 separates the Requirement (top level) from the Sub-requirement (for example, `10.2.1.4`). The lookup skill accepts `pci` and `pci-dss` as the short name of the framework.

### HIPAA Security Rule

| Property | Value |
|---|---|
| Citation format | `§164.312(b)`, `§164.308(a)(1)(ii)(D)`, etc. |
| Reviewer agent | `hipaa-compliance-reviewer` |
| Accepted scope tags | `ephi-host`, `hipaa-scope`, `phi-host`, `covered-entity` |
| Verification level | **MACHINE_VERIFIED** (eCFR 45 CFR §164, 1,036 subsection IDs) |
| Framework-specific skill args | None |

HIPAA citations use the section-and-subsection notation of the eCFR. The reviewer agent scopes itself to sensors with the `phi` tag (protected health information). The skill accepts `§164.312(b)` and `164.312(b)` as the control ID.

### SOC 2 (Trust Services Criteria)

| Property | Value |
|---|---|
| Citation format | `CC6.1`, `CC7.2`, `A1.2`, etc. |
| Reviewer agent | `soc2-compliance-reviewer` |
| Accepted scope tags | `soc2-scope`, `in-scope-system`, `audit-scope` |
| Verification level | ATTESTATION_ONLY (review against AICPA TSC PDF) |
| Framework-specific skill args | None |

SOC 2 citations use the short form of the AICPA Trust Services Criteria. The CC (Common Criteria) controls apply to all SOC 2 Type II engagements. The A, C, P, and PI categories apply only when the related trust service is in scope.

### ISO/IEC 27001:2022

| Property | Value |
|---|---|
| Citation format | `A.8.15`, `A.5.10`, etc. |
| Reviewer agent | `iso-27001-compliance-reviewer` |
| Accepted scope tags | `isms-scope`, `iso-scope`, `iso-27001-scope`, `soa-included` |
| Verification level | **UNVERIFIED** (ISO standard is paywalled at ~$215 / ~$395 for combined 27001+27002) |
| Framework-specific skill args | None |

The mapping uses the ISO/IEC 27002:2022 control identifiers (`A.x.y`). The mapping is based on publicly available summaries, because the official ISO standard is not redistributable. The attribution document explains how to upgrade this framework to MACHINE_VERIFIED if you stage a licensed extract.

!!! warning "ISO 27001 verification level"
    No program reconciled the ISO 27001 citations against an authoritative source, as it did for the other six frameworks. A certified ISO 27001 lead auditor should review the citations in the mapping document before you use them in a certification audit.

### CIS Critical Security Controls v8

| Property | Value |
|---|---|
| Citation format | `8.2`, `4.1`, `13.6`, etc. (Safeguard numbering) |
| Reviewer agent | `cis-v8-compliance-reviewer` |
| Accepted scope tags | `cis-scope`, `cis-v8-scope` (plus optional `cis-ig1`, `cis-ig2`, `cis-ig3` for tier) |
| Verification level | ATTESTATION_ONLY (review against CIS Controls v8 PDF — CC BY-NC-ND license) |
| Framework-specific skill args | `--ig <1\|2\|3>` on `compliance-gap` |

CIS v8 puts safeguards into Implementation Groups (IG1, IG2, IG3) by the size of the enterprise and its tolerance of risk. The `compliance-gap` skill accepts an `--ig` argument that scopes the analysis to the safeguards that apply at one implementation group. The skill declares no hard-coded default. If you supply no `--ig` argument, and no `cis-ig1`, `cis-ig2`, or `cis-ig3` tag is set on a sensor, the analysis covers all safeguards in the bundled implementation document.

## Bundled artifacts per framework

For each framework, the plugin supplies five artifacts under `${CLAUDE_PLUGIN_ROOT}/compliance/<framework>/`:

| File | Purpose |
|---|---|
| `<framework>-limacharlie-mapping.md` | Mapping of controls to capabilities. The `compliance-lookup` skill quotes it verbatim. |
| `<framework>-limacharlie-implementation.md` | Deployable D&R / FIM / artifact-collection / exfil rules in YAML, each with the control citation in its metadata. |
| `<framework>-attribution.md` | Authoritative publisher, citation format, retrieval date, verification level, procedure for independent re-verification. |
| `recommended-rules.yaml` | Canonical baseline of rule names. The `compliance-gap` skill compares the names of deployed rules against this list. |
| `agent/` | Reviewer agent manifest (`<framework>-compliance-reviewer.yaml`) and the hive records (`ai_agent`, `dr-general`, `secret`) that `compliance-deploy` pushes. |

The skills read these artifacts when you call them. The skills do not sync the artifacts into your organization automatically. A sync happens only when you call `compliance-deploy` or `compliance-baseline-deploy`.

## Updating to a newer framework version

When the plugin supplies a new implementation document for a framework (for example, with a new PCI sub-requirement), use this re-sync sequence:

```text
/plugin update lc-compliance@lc-marketplace

/lc-compliance:compliance-baseline-deploy <framework> --oid <your-oid>   # dry-run
/lc-compliance:compliance-baseline-deploy <framework> --oid <your-oid> --apply
```

The baseline deploy is idempotent. It skips the rules that are already present with the same name, so a second run adds only the new rules. To replace existing rules with the new definitions, use `--overwrite`.

To update the prompt and the tools of the reviewer agent after a plugin update:

```text
/lc-compliance:compliance-deploy <framework> --oid <your-oid>
```

## See also

- [Skills Reference](skills.md) — argument syntax for `--baseline`, `--ig`, and other framework-specific flags
- [Case-Reviewer Agent](case-reviewer-agent.md) — how the reviewer agent for each framework classifies cases
- [Gap Analysis](gap-analysis.md) — how the gap analysis uses the recommended baseline of the framework
