# Investigation Guide

This guide provides opinionated best practices for SOC analysts using LimaCharlie Investigations to document and encode security investigations. By following these conventions, you enable attack chain visualization, cross-investigation analysis, and consistent reporting.

## Tag Format Specification

Use colon-separated tags to categorize events, detections, and entities within your timeline. This section defines the format patterns - actual values are either format-based (you define them) or fetched dynamically from authoritative sources.

### MITRE ATT&CK Tags (Dynamic)

MITRE ATT&CK tags should be validated against the authoritative MITRE STIX data rather than hardcoded lists.

**Authoritative Source:** https://github.com/mitre-attack/attack-stix-data

**Tag Formats:**

| Format | Description | Example |
|--------|-------------|---------|
| `phase:{tactic-name}` | Attack phase aligned with MITRE tactic | `phase:initial-access` |
| `mitre:{technique-id}` | Specific MITRE ATT&CK technique | `mitre:T1566` |

**Fetching Valid Values at Runtime:**

```
URL: https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json

Parsing:
1. Tactics: Filter objects where type="x-mitre-tactic"
   - Use x_mitre_shortname for phase tag values

2. Techniques: Filter objects where type="attack-pattern"
   - Extract external_references[] where source_name="mitre-attack"
   - Use external_id for mitre: tag values (e.g., T1566)
```

### Operational Tags (Format-Based)

These tags follow a consistent format pattern. You define the values based on your investigation context.

| Category | Format | Description | Examples |
|----------|--------|-------------|----------|
| **Timing** | `timing:{marker}` | Investigation timing markers | `timing:first-observed`, `timing:pivot-point`, `timing:detection-trigger` |
| **Confidence** | `confidence:{level}` | Analyst confidence in findings | `confidence:high`, `confidence:medium`, `confidence:low` |
| **Actor** | `actor:{identifier}` | Threat actor attribution | `actor:apt-29`, `actor:ransomware-lockbit`, `actor:nation-state` |
| **Tool** | `tool:{name}` | Identified attack tools | `tool:cobalt-strike`, `tool:mimikatz`, `tool:psexec` |
| **Impact** | `impact:{type}` | Observed or potential impact | `impact:data-exfiltration`, `impact:ransomware`, `impact:credential-compromise` |
| **Scope** | `scope:{extent}` | Attack scope | `scope:single-host`, `scope:subnet`, `scope:domain-wide` |
| **Root Cause** | `root-cause:{cause}` | Initial access method | `root-cause:phishing`, `root-cause:vuln-exploit`, `root-cause:credential-reuse` |
| **Defense Gap** | `gap:{deficiency}` | Security control failures | `gap:no-mfa`, `gap:missing-detection`, `gap:no-segmentation` |
| **Asset** | `asset:{classification}` | Business asset classification | `asset:crown-jewels`, `asset:pci-scope`, `asset:external-facing` |
| **Customer** | `customer:{name}` | MSSP customer identifier | `customer:acme-corp` |

---

## Attack Chain Visualization

Use `phase:` tags chronologically to visualize attack progression through MITRE ATT&CK tactics:

```
[phase:initial-access] → [phase:execution] → [phase:persistence] → [phase:credential-access] → [phase:lateral-movement] → [phase:exfiltration]
```

### Timing Markers

Apply timing tags to key events:

| Tag | When to Apply |
|-----|---------------|
| `timing:first-observed` | Earliest confirmed malicious activity |
| `timing:pivot-point` | Critical decision points in the attack chain |
| `timing:detection-trigger` | Event/detection that initiated the investigation |

### Example: Attack Chain Tags

```json
{
  "events": [
    {
      "atom": "evt-001",
      "tags": ["phase:initial-access", "mitre:T1566", "timing:first-observed"],
      "relevance": "User opened phishing attachment"
    },
    {
      "atom": "evt-002",
      "tags": ["phase:execution", "mitre:T1059", "timing:pivot-point"],
      "relevance": "Encoded PowerShell executed from macro"
    },
    {
      "atom": "evt-003",
      "tags": ["phase:credential-access", "mitre:T1003", "tool:mimikatz"],
      "relevance": "LSASS memory access detected"
    }
  ]
}
```

---

## Entity Enrichment Best Practices

### IOC Provenance

Document how entities were discovered and validated in the `context` field:

**Pattern:** `Provenance: [how discovered]. Validation: [how confirmed]. Attribution: [threat intel correlation].`

**Example:**
```json
{
  "type": "ip",
  "value": "203.0.113.50",
  "context": "Provenance: Extracted from C2 beacon traffic. Validation: Cross-referenced with TI feed (58/72 VirusTotal). Attribution: Matches APT29 infrastructure per CISA AA24-001.",
  "verdict": "malicious"
}
```

### Verdict Assignment

| Verdict | Criteria |
|---------|----------|
| `malicious` | Confirmed IOC match, known-bad behavior, validated threat |
| `suspicious` | Anomalous but not definitively malicious, requires review |
| `benign` | Cleared by investigation, legitimate activity |
| `unknown` | Insufficient context, further analysis needed |

### Entity Context Templates

**For IPs:**
```
Provenance: [discovered in which event type]. Geo: [country/ASN]. TI: [threat intel match]. Historical: [seen before in org?].
```

**For Hashes:**
```
Provenance: [file name and path]. AV: [detection ratio]. Sandbox: [behavior summary]. First seen: [date].
```

**For Domains:**
```
Provenance: [DNS query or URL]. Registration: [age, registrar]. TI: [threat intel match]. Resolution: [IP addresses].
```

---

## Note-Taking Templates

Use structured note types for consistent documentation:

### Observation Notes
Record raw facts without interpretation:
```
[TIMESTAMP] [HOST] [EVENT_TYPE]
Observed: [description of what was seen]
Key data: [relevant field values]
Related atoms: [list of event atoms]
```

### Hypothesis Notes
Document working theories:
```
HYPOTHESIS: [statement]

Supporting evidence:
- [evidence 1]
- [evidence 2]

Tests to validate:
1. [query or action to confirm/refute]
2. [additional validation step]

Alternative explanations:
- [alternative 1]
```

### Finding Notes
Document confirmed discoveries:
```
FINDING: [definitive statement]

Evidence:
- [primary evidence]
- [corroborating evidence]

Impact:
- Affected systems: [list]
- Data at risk: [description]

Confidence: [high/medium/low]
```

### Attack Chain Summary Note
Document the full attack narrative:
```
ATTACK CHAIN:
[Phase 1] → [Phase 2] → [Phase 3] → ...

Techniques: [T1566] → [T1059] → [T1003] → ...
Dwell time: [hours/days from first access to detection]

Root cause: [initial access method]
Defense gaps: [what failed]
```

---

## Investigation Workflow

### Status Transitions

| Status | When to Use |
|--------|-------------|
| `new` | Timeline just created, investigation not started |
| `in_progress` | Active investigation underway |
| `pending_review` | Analyst completed, awaiting peer review |
| `escalated` | Requires senior analyst or management attention |
| `closed_false_positive` | Confirmed benign, documented rationale |
| `closed_true_positive` | Confirmed incident, remediation complete |

### Closure Criteria

**For `closed_false_positive`:**
- [ ] Benign explanation documented in conclusion
- [ ] Finding note with FP rationale
- [ ] Consider FP rule if pattern is common

**For `closed_true_positive`:**
- [ ] All action item notes resolved
- [ ] Containment/eradication verified
- [ ] Root cause identified
- [ ] Summary field completed
- [ ] Conclusion field completed
- [ ] All entities have verdicts assigned

---

## Summary and Conclusion Fields

### Summary Field (Executive Audience)

Write for non-technical stakeholders:
```
On [date], [attack type] was detected on [target]. The attacker [brief action summary].
Impact: [what was affected]. Status: [current state]. Attribution: [if known].
```

**Example:**
```
On November 15, 2024, a targeted spearphishing attack compromised a Finance department workstation.
The attacker harvested credentials and moved laterally to 15 servers, exfiltrating approximately 50GB
of financial data over 72 hours. Containment was achieved by isolating affected systems.
Attribution: Financially-motivated actor (medium confidence).
```

### Conclusion Field (Technical Closure)

Document technical determination:
```
CLASSIFICATION: [true positive/false positive] - [incident type]
ROOT CAUSE: [initial access method]
ATTRIBUTION: [threat actor/campaign] ([confidence level])
IMPACT: [data affected], [systems affected]
DWELL TIME: [duration from first access to detection]
CONTAINMENT: [status and date]
```

---

## Example: Complete Tagged Timeline

*Note: MITRE technique IDs shown are illustrative. Validate against the authoritative STIX source.*

```json
{
  "name": "APT-Investigation-2024-001",
  "description": "Investigation of targeted attack against Finance department",
  "status": "closed_true_positive",
  "priority": "critical",
  "events": [
    {
      "atom": "evt-001",
      "sid": "sensor-001",
      "tags": ["phase:initial-access", "mitre:T1566", "timing:first-observed", "root-cause:phishing"],
      "relevance": "User opened phishing attachment with malicious macro",
      "verdict": "malicious"
    },
    {
      "atom": "evt-002",
      "sid": "sensor-001",
      "tags": ["phase:execution", "mitre:T1059", "timing:pivot-point"],
      "relevance": "Encoded PowerShell executed by Word macro",
      "verdict": "malicious"
    },
    {
      "atom": "evt-003",
      "sid": "sensor-001",
      "tags": ["phase:credential-access", "mitre:T1003", "tool:mimikatz"],
      "relevance": "LSASS memory access - credential harvesting",
      "verdict": "malicious"
    },
    {
      "atom": "evt-004",
      "sid": "sensor-002",
      "tags": ["phase:lateral-movement", "mitre:T1021", "scope:domain-wide"],
      "relevance": "RDP to domain controller with stolen credentials",
      "verdict": "malicious"
    },
    {
      "atom": "evt-005",
      "sid": "sensor-003",
      "tags": ["phase:exfiltration", "mitre:T1041", "impact:data-exfiltration", "timing:detection-trigger"],
      "relevance": "Large HTTPS upload to external IP",
      "verdict": "malicious"
    }
  ],
  "entities": [
    {
      "type": "ip",
      "value": "203.0.113.50",
      "name": "C2 Server",
      "context": "Provenance: Network connection from compromised host. TI: Matches APT29 infrastructure per CISA AA24-001.",
      "verdict": "malicious",
      "related_events": ["evt-005"]
    },
    {
      "type": "hash",
      "value": "d41d8cd98f00b204e9800998ecf8427e",
      "context": "Provenance: Dropped by macro execution. AV: 52/72 detections. Sandbox: Downloads secondary payload.",
      "verdict": "malicious",
      "related_events": ["evt-002"]
    }
  ],
  "notes": [
    {
      "type": "finding",
      "content": "ATTACK CHAIN:\nInitial Access (T1566) → Execution (T1059) → Credential Access (T1003) → Lateral Movement (T1021) → Exfiltration (T1041)\n\nDwell time: 48 hours from first access to detection."
    },
    {
      "type": "finding",
      "content": "DEFENSE GAPS IDENTIFIED:\n- gap:no-mfa on domain admin accounts\n- gap:missing-detection for PowerShell script block logging\n- gap:no-segmentation between workstations and servers"
    },
    {
      "type": "action_item",
      "content": "Rotate all domain admin credentials",
      "resolved": true
    }
  ],
  "summary": "Targeted spearphishing attack compromised Finance workstation. Attacker harvested domain admin credentials within 4 hours, moved laterally to file server, exfiltrated 50GB over 48 hours. Attributed to financially-motivated actor (medium confidence).",
  "conclusion": "CLASSIFICATION: True positive - data breach\nROOT CAUSE: Spearphishing with compromised vendor sender\nATTRIBUTION: Financially-motivated (medium confidence)\nIMPACT: 50GB data exfiltrated, 15 servers accessed\nDWELL TIME: 48 hours\nCONTAINMENT: Complete as of 2024-11-18"
}
```

---

## Cross-Timeline Analysis

Consistent tagging enables searching across multiple investigations:

| Search Goal | Tag Pattern to Query |
|-------------|---------------------|
| All ransomware incidents | `impact:ransomware` |
| APT activity | `actor:apt-*` |
| Critical asset compromises | `asset:crown-jewels` |
| Open investigations | `status:in_progress` |
| Phishing-originated attacks | `root-cause:phishing` |
| MFA gaps | `gap:no-mfa` |
| Specific customer (MSSP) | `customer:acme-corp` |

---

## Related Documentation

- [Config Hive: Investigation](../../Platform_Management/Config_Hive/config-hive-investigation.md) - Investigation schema reference
- [Investigation Creation Skill](https://github.com/refractionPOINT/lc-ai/blob/master/plugins/lc-essentials/skills/investigation-creation/SKILL.md) - Automated investigation creation
- [expand_investigation function](https://github.com/refractionPOINT/lc-ai/blob/master/plugins/lc-essentials/skills/limacharlie-call/functions/expand-investigation.md) - Hydrate investigation with full event data
