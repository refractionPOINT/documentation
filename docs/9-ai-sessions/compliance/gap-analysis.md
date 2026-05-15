# Gap Analysis

The [`compliance-gap`](skills.md#compliance-gap) skill produces an on-demand markdown report comparing an organization's currently-deployed configuration against the framework's recommended baseline. This page explains how to read the report, what each section means, and how to act on the findings.

Gap analysis is the primary way to assess compliance posture in `lc-compliance`. There is no backend gap-analyzer agent — gap reports are engineering punch lists, not audit evidence, and so they are produced interactively and live only in your Claude Code chat.

## When to run a gap analysis

Common occasions:

- **Before an audit window opens.** Three to six weeks before an external assessor begins fieldwork is the most valuable moment — there is still time to remediate.
- **After onboarding a new tenant or new scope.** When sensors are first tagged into scope (e.g., a new acquisition's endpoints get the `cde` tag), run a gap analysis to confirm the framework's expectations are met.
- **After a plugin update.** When the bundled recommended baseline changes, the gap analysis identifies any new rules that should be deployed.
- **As a regular cadence.** Quarterly or monthly gap analyses surface drift (rules disabled, sensors offline, extensions unsubscribed) before they become audit findings.

## Running the skill

```text
/lc-compliance:compliance-gap pci-dss --oid <your-oid>
```

The skill queries the organization through the standard LimaCharlie CLI session, diffs the deployed configuration against the framework's `recommended-rules.yaml` baseline, and prints the report to your chat. Nothing is written to the organization.

For NIST 800-53, scope the analysis to a FIPS 199 baseline:

```text
/lc-compliance:compliance-gap nist --oid <your-oid> --baseline moderate
```

For CIS v8, scope to an Implementation Group:

```text
/lc-compliance:compliance-gap cis --oid <your-oid> --ig 2
```

## Anatomy of a gap report

The report has a consistent structure across frameworks. A sample run against a PCI DSS org looks like this:

````text
# PCI DSS v4.0 Gap Analysis (Interactive)

**Org:** c1ffedc0-ffee-4a1e-b1a5-abc123def456 (example-org)
**Generated:** 2026-04-17T18:42:03Z
**Recommended set version:** 2026-04-17
**Verification level:** ATTESTATION_ONLY
**Scope:** sensors tagged `cde` (3 found; 2 online / 1 offline > 7d)

## Summary
- Telemetry gaps: 7 events across windows, linux
- Artifact collection gaps: 9 rules missing
- FIM gaps: 23 rules (ext-integrity not subscribed — see Section C)
- D&R rule gaps: 42 of 57 recommended missing
- Sensor-coverage issues: 1 CDE sensor offline > 7d (Req 10.7.x)
- Name-drift candidates: 2 (manual review)
- Deployed extras: 11 (informational)

## A. Telemetry Gaps
### Windows
| Missing event | PCI requirement |
|---|---|
| THREAD_INJECTION | Req 10.2.x |
| SENSITIVE_PROCESS_ACCESS | Req 10.2.1.2 |
| NEW_NAMED_PIPE | Req 10.2.x |

## D. D&R Rule Gaps (top 10 of 42)
| Canonical rule name | PCI requirement | MITRE ATT&CK |
|---|---|---|
| pci-10-failed-logon-windows    | Req 10.2.1.4 | T1078 |
| pci-10-brute-force-windows     | Req 10.2.1.4 | T1110 |
| pci-10-event-log-cleared       | Req 10.2.1.6 | T1070.001 |

## F. Sensor Coverage
| Sensor | Hostname | Last seen | PCI requirement |
|---|---|---|---|
| aaaabbbb...11 | web-prod-04 | 11 days ago | Req 10.7.x — critical security control failure |

## Prioritized Remediation
1. Subscribe ext-integrity and deploy the 23 FIM rules — addresses Req 11.5.1 + 11.5.2
2. Investigate offline CDE sensor web-prod-04 (Req 10.7.x)
3. Deploy the 10 highest-priority D&R rules (Req 10.2.x failed-logon cluster first)
4. Enable missing exfil events on Windows CDE fleet
5. Add 9 missing artifact-collection rules (PowerShell Operational, Defender, Task Scheduler)
````

The sections in the report:

### Header

The header carries the **organization name and UUID** so reports can be attributed unambiguously, the **timestamp** the report was generated (always UTC), the **recommended set version** (a date string indicating which bundled baseline the analysis ran against), the framework's **verification level** (so readers can calibrate trust appropriately), and the **scope** (which sensors were considered in-scope based on the framework's tag convention).

### Summary

A one-glance count of issues across six categories. The counts are not weighted by severity — a missing low-priority D&R rule and a missing critical exfil event each contribute one to the count. Use the Prioritized Remediation section for priority.

### A. Telemetry Gaps

Events the framework's recommended baseline expects the in-scope sensors to be collecting, that are absent from the org's deployed exfil profile. Broken down by sensor platform (Windows, Linux, macOS) because exfil profiles are platform-specific.

A telemetry gap means the rule downstream cannot fire even if deployed, because the underlying event isn't being collected. **Fix these before deploying the corresponding D&R rules.**

### B. Artifact Collection Gaps

Rules from the recommended baseline that collect specific artifacts (PowerShell Operational logs, Windows Defender logs, Task Scheduler logs, etc.) which are not deployed. These rules subscribe the sensor to additional log sources that go beyond standard exfil.

### C. FIM Gaps

File-integrity-monitoring rules that are not deployed. FIM in LimaCharlie is provided by the `ext-integrity` extension. The gap report explicitly flags whether `ext-integrity` is subscribed to the organization — if it is not, all FIM rules in the baseline will be reported as gaps, and subscribing the extension is the first remediation step.

See the [Integrity extension](../../5-integrations/extensions/limacharlie/integrity.md).

### D. D&R Rule Gaps

D&R rule names from the recommended baseline that are not present in the org's deployed rule set. The report shows the top 10 by default with a count of the remainder; the full list is accessible via the skill's interactive follow-up.

Each entry carries the framework's control citation and, where the bundled implementation document includes it, the MITRE ATT&CK technique the rule targets. The latter is useful for cross-referencing against an existing detection engineering roadmap.

### E. Name Drift

Deployed rules whose names are *close to but not identical to* a recommended-baseline name. This usually indicates one of two things:

- The org deployed a rule manually with a slightly different name, missing the canonical naming convention by a few characters
- A previous version of the baseline used a different name, and the rule has not been renamed to match the current bundled name

Name-drift candidates are surfaced for **manual review**, not auto-remediation — the report does not attempt to merge them with their canonical counterparts. To remediate, either rename the deployed rule to match the canonical name, or accept the drift and treat both as in-scope.

### F. Sensor Coverage

In-scope sensors that have not reported in more than 7 days. The skill uses a uniform 7-day threshold across all frameworks; per-framework citations attached to each row identify which control(s) the offline sensor risks failing (e.g., PCI DSS Req 10.7.x for cardholder-data environments, HIPAA §164.312(b) for ePHI systems).

A sensor showing here is, in audit terms, an organization that has stopped collecting required telemetry from an in-scope system. Investigate before the auditor finds it.

### G. Deployed Extras (informational)

Rules deployed in the org that are **not** part of the recommended baseline. These are never flagged as gaps — extras are usually intentional (custom detections, threat-intel-driven rules, organization-specific tuning). The list is informational so operators can confirm the deployed set is intentional.

### Prioritized Remediation

A short ordered list, typically 4–6 items, reflecting the most impactful gap-closing actions. The ordering takes into account dependencies (e.g., subscribe `ext-integrity` *before* deploying FIM rules) and control criticality (sensor coverage and authentication-logging controls usually rank highest).

## Acting on the report

The report is a punch list. Typical follow-up paths:

| Section | Remediation skill or action |
|---|---|
| A. Telemetry gaps | Edit the org's exfil profile — see [Exfil extension](../../5-integrations/extensions/limacharlie/exfil.md) |
| B. Artifact collection gaps | Run [`compliance-baseline-deploy --apply --kinds artifact`](skills.md#compliance-baseline-deploy) |
| C. FIM gaps | Subscribe [Integrity extension](../../5-integrations/extensions/limacharlie/integrity.md), then `--kinds fim` |
| D. D&R rule gaps | Run [`compliance-baseline-deploy --apply --kinds dr`](skills.md#compliance-baseline-deploy) for the full set, or write/import targeted rules |
| E. Name-drift candidates | Manual rename of deployed rules, or accept the drift |
| F. Sensor-coverage issues | Investigate the offline sensors; if decommissioned, remove from scope |
| G. Deployed extras | No action — informational only |

## Persisting a gap report

The skill writes the report to your Claude Code chat. It does not write to the LimaCharlie organization. If you want the report persisted for an auditor to reference, paste the markdown into a [Case](../../5-integrations/extensions/limacharlie/cases.md) note, or store it in your GRC platform of choice.

This separation is deliberate: gap reports are engineering punch lists with a short half-life. Audit evidence is what the case-reviewer agent produces continuously inside the case queue. Conflating the two would invite auditors to treat a snapshot punch list as compliance evidence, which it is not.

## Multi-tenant gap analysis

The skill operates on a single organization per invocation. For a portfolio of organizations (an MSSP book of business, a parent organization with multiple subsidiaries), invoke the skill once per `--oid`. Each report is independent and can be sent to the relevant customer, business unit, or compliance team.

If you find yourself running the same gap analysis across many orgs on a regular cadence, consider scripting the iteration around the skill invocation, or surface a feature request — a multi-org roll-up is not currently a built-in capability of the plugin.

## See also

- [Skills Reference](skills.md#compliance-gap) — full argument reference for the gap-analysis skill
- [Frameworks](frameworks.md) — per-framework recommended scope tags and verification levels
- [Case-Reviewer Agent](case-reviewer-agent.md) — the continuous evidence-production complement to ad-hoc gap analysis
