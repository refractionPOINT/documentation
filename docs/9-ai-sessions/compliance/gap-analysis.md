# Gap Analysis

The [`compliance-gap`](skills.md#compliance-gap) skill makes a markdown report on demand. The report compares the deployed configuration of an organization against the recommended baseline of the framework. This page explains how to read the report, what each section means, and how to act on the findings.

Gap analysis is the main way to assess the compliance posture in `lc-compliance`. There is no gap-analyzer agent in the cloud. Gap reports are engineering punch lists, not audit evidence. The skill therefore makes them interactively, and they stay only in your Claude Code chat.

## When to run a gap analysis

Common occasions:

- **Before an audit window opens.** The best time is three to six weeks before an external assessor starts fieldwork. You then still have time to remediate.
- **After onboarding a new tenant or new scope.** Run a gap analysis when you first tag sensors into scope, for example when the endpoints of a new acquisition get the `cde` tag. The analysis confirms that the organization meets the expectations of the framework.
- **After a plugin update.** When the bundled recommended baseline changes, the gap analysis shows the new rules that you should deploy.
- **As a regular cadence.** A gap analysis each quarter or each month shows drift before it becomes an audit finding. Drift includes disabled rules, offline sensors, and unsubscribed extensions.

## Running the skill

```text
/lc-compliance:compliance-gap pci-dss --oid <your-oid>
```

The skill queries the organization through the standard LimaCharlie CLI session. It compares the deployed configuration against the `recommended-rules.yaml` baseline of the framework, and it prints the report to your chat. It writes nothing to the organization.

For NIST 800-53, scope the analysis to a FIPS 199 baseline:

```text
/lc-compliance:compliance-gap nist --oid <your-oid> --baseline moderate
```

For CIS v8, scope to an Implementation Group:

```text
/lc-compliance:compliance-gap cis --oid <your-oid> --ig 2
```

## Anatomy of a gap report

The structure of the report is the same for all frameworks. This is a sample run against a PCI DSS organization:

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

The header carries the **organization name and UUID**, so that each report has a clear owner. It gives the **timestamp** of the report, always in UTC. It gives the **recommended set version**: a date string that shows which bundled baseline the analysis used. It gives the **verification level** of the framework, so that readers know how much to trust the content. It gives the **scope**: the sensors that the analysis treated as in scope, from the tag convention of the framework.

### Summary

A count of the issues in six categories. The counts have no weight for severity. A missing D&R rule with low priority and a missing critical exfil event each add one to the count. Use the Prioritized Remediation section for priority.

### A. Telemetry Gaps

The events that the recommended baseline of the framework expects from the in-scope sensors, but that the deployed exfil profile of the organization does not collect. The report groups them by sensor platform (Windows, Linux, macOS), because an exfil profile is specific to one platform.

A telemetry gap means that the downstream rule cannot fire, because the sensor does not collect the event. This is true even if you deploy the rule. **Correct these gaps before you deploy the related D&R rules.**

### B. Artifact Collection Gaps

Rules from the recommended baseline that collect specific artifacts and that are not deployed. Examples are PowerShell Operational logs, Windows Defender logs, and Task Scheduler logs. These rules subscribe the sensor to more log sources than standard exfil.

### C. FIM Gaps

File-integrity-monitoring rules that are not deployed. The `ext-integrity` extension supplies FIM in LimaCharlie. The gap report states if the organization has a subscription to `ext-integrity`. If it does not, the report shows all FIM rules in the baseline as gaps, and the first remediation step is to subscribe to the extension.

See the [Integrity extension](../../5-integrations/extensions/limacharlie/integrity.md).

### D. D&R Rule Gaps

D&R rule names from the recommended baseline that are not in the deployed rule set of the organization. By default, the report shows the top 10 and a count of the others. To get the full list, ask the skill in an interactive follow-up.

Each entry carries the control citation of the framework. If the bundled implementation document includes it, the entry also carries the MITRE ATT&CK technique that the rule targets. Use the technique to cross-reference an existing roadmap for detection engineering.

### E. Name Drift

Deployed rules with names that are *close to but not identical to* a name in the recommended baseline. There are two usual causes:

- The organization deployed a rule manually with a different name that misses the canonical convention for names by some characters
- A previous version of the baseline used a different name, and nobody renamed the rule to match the current bundled name

The report shows name-drift candidates for **manual review**, not for automatic remediation. It does not try to merge them with their canonical equivalents. To remediate, rename the deployed rule to the canonical name, or accept the drift and treat both names as in scope.

### F. Sensor Coverage

In-scope sensors that sent no report for more than 7 days. The skill uses the same threshold of 7 days for all frameworks. Each row carries the citations of the framework. These citations show the controls that the offline sensor can fail, for example PCI DSS Req 10.7.x for cardholder-data environments, or HIPAA §164.312(b) for ePHI systems.

In audit terms, a sensor in this section shows an organization that stopped the collection of necessary telemetry from an in-scope system. Investigate the sensor before the auditor finds it.

### G. Deployed Extras (informational)

Rules that are deployed in the organization but are **not** part of the recommended baseline. The report never shows them as gaps. Extras are usually intentional: custom detections, rules from threat intelligence, and tuning for the organization. The list is informational, so that operators can confirm that the deployed set is intentional.

### Prioritized Remediation

A short ordered list, usually 4–6 items, with the actions that close the most important gaps. The order accounts for dependencies, for example a subscription to `ext-integrity` *before* the deployment of FIM rules. It also accounts for the criticality of the control. Sensor coverage and controls for authentication logging usually rank highest.

## Acting on the report

The report is a punch list. The usual next actions:

| Section | Remediation skill or action |
|---|---|
| A. Telemetry gaps | Edit the exfil profile of the organization — see [Exfil extension](../../5-integrations/extensions/limacharlie/exfil.md) |
| B. Artifact collection gaps | Run [`compliance-baseline-deploy --apply --kinds artifact`](skills.md#compliance-baseline-deploy) |
| C. FIM gaps | Subscribe to the [Integrity extension](../../5-integrations/extensions/limacharlie/integrity.md), then use `--kinds fim` |
| D. D&R rule gaps | Run [`compliance-baseline-deploy --apply --kinds dr`](skills.md#compliance-baseline-deploy) for the full set, or write or import targeted rules |
| E. Name-drift candidates | Rename the deployed rules manually, or accept the drift |
| F. Sensor-coverage issues | Investigate the offline sensors. If a sensor is decommissioned, remove it from scope |
| G. Deployed extras | No action — informational only |

## Persisting a gap report

The skill writes the report to your Claude Code chat. It does not write to the LimaCharlie organization. To keep the report for an auditor, paste the markdown into a [Case](../../5-integrations/extensions/limacharlie/cases.md) note, or store it in your GRC system.

This separation is deliberate. Gap reports are engineering punch lists that become old quickly. The case-reviewer agent produces the audit evidence continuously inside the case queue. If you mix the two, auditors can treat a snapshot punch list as compliance evidence, and it is not compliance evidence.

## Multi-tenant gap analysis

The skill operates on one organization for each call. For a portfolio of organizations, such as an MSSP book of business or a parent organization with subsidiaries, call the skill one time for each `--oid`. Each report is independent, and you can send it to the customer, business unit, or compliance team.

If you run the same gap analysis across many organizations at regular times, write a script around the call to the skill, or send a feature request. A roll-up across organizations is not a built-in capability of the plugin.

## See also

- [Skills Reference](skills.md#compliance-gap) — full argument reference for the gap-analysis skill
- [Frameworks](frameworks.md) — recommended scope tags and verification levels for each framework
- [Case-Reviewer Agent](case-reviewer-agent.md) — the continuous production of evidence that completes ad-hoc gap analysis
