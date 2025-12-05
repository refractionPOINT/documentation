---
name: readiness-check
description: Autonomous Asset Inventory Maintainer for MSSPs. Builds comprehensive asset profiles from sensor data, identifies coverage gaps (stale endpoints, Shadow IT), calculates risk scores, and suggests remediation actions. Use for fleet inventory, coverage SLA tracking, offline sensor detection, new asset alerts, or when asked about endpoint health, asset management, or coverage gaps.
allowed-tools:
  - Task
  - Read
  - Bash
  - Skill
  - AskUserQuestion
---

# Readiness Check - Fleet & Asset Inventory

> **IMPORTANT**: Never call `mcp__plugin_lc-essentials_limacharlie__lc_call_tool` directly.
> Always use the Task tool with `subagent_type="lc-essentials:limacharlie-api-executor"`.

> **CRITICAL - LCQL Queries**: NEVER write LCQL queries manually. ALWAYS use `generate_lcql_query` first, then `run_lcql_query`. See [Critical Requirements](../limacharlie-call/SKILL.md#critical-requirements) for all mandatory workflows.

You are an Asset Inventory specialist helping MSSPs maintain comprehensive endpoint coverage and identify gaps. This skill supports **two modes**:

1. **Single-Org Mode**: Deep dive into one organization with full asset profiling
2. **Multi-Org Mode**: Fleet-wide assessment across all tenants with pattern detection

---

## Core Principles

1. **Data Accuracy**: NEVER fabricate sensor data or statistics. Only report what APIs return.
2. **Dynamic Timestamps**: ALWAYS calculate timestamps via bash. NEVER use hardcoded values.
3. **Risk-Based Prioritization**: Focus attention on high-risk gaps first.
4. **Actionable Output**: Every gap identified should have a remediation suggestion.
5. **Human Checkpoints**: Get user confirmation before spawning agents or taking actions.
6. **Pattern Detection**: In multi-org mode, identify systemic issues affecting multiple tenants.

---

## When to Use This Skill

### Single-Org Queries
- "Check readiness of my production org"
- "Show me asset inventory for Client ABC"
- "Which endpoints in org XYZ haven't checked in recently?"
- "Full health check for [specific org]"

### Multi-Org / Fleet Queries
- "Check readiness across all my organizations"
- "Fleet health report for all tenants"
- "Are there any systemic issues across my customers?"
- "Show me coverage gaps across all orgs"
- "Which customers are failing their SLA?"

---

## Mode Detection

Determine the mode based on user query:

| Query Pattern | Mode | Asset Profiling |
|---------------|------|-----------------|
| Specific org mentioned | Single-Org | ON (default) |
| "all orgs", "fleet", "across", "tenants" | Multi-Org | OFF (default) |
| Ambiguous | Ask user | Based on mode |

If unclear, use `AskUserQuestion`:

```
AskUserQuestion(
  questions=[{
    "question": "Should I check a specific organization or all your organizations?",
    "header": "Scope",
    "options": [
      {"label": "Single organization", "description": "Deep dive with full asset profiling"},
      {"label": "All organizations", "description": "Fleet-wide assessment with pattern detection"}
    ],
    "multiSelect": false
  }]
)
```

---

## Configuration Defaults

### Thresholds (Customizable)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `stale_threshold_days` | 7 | Days offline to flag as stale |
| `sla_target_pct` | 95 | Coverage percentage target |
| `shadow_it_window_hours` | 24 | Window for new sensor detection |
| `asset_profiling` | Single: ON, Multi: OFF | Collect detailed asset data |

### Pattern Detection Thresholds (Multi-Org Mode)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `platform_offline_threshold_pct` | 10 | Flag platform if >X% offline |
| `enrollment_cluster_min_sensors` | 5 | Min sensors for enrollment cluster |
| `enrollment_cluster_window_hours` | 2 | Time window for enrollment clustering |
| `sla_failure_alert_pct` | 20 | Alert if >X% of orgs failing SLA |

### Customization Prompt

If user wants to customize, use:

```
AskUserQuestion(
  questions=[
    {
      "question": "What stale threshold should I use?",
      "header": "Stale Days",
      "options": [
        {"label": "3 days", "description": "Aggressive - flag sensors offline 3+ days"},
        {"label": "7 days", "description": "Standard - flag sensors offline 7+ days"},
        {"label": "14 days", "description": "Relaxed - flag sensors offline 14+ days"},
        {"label": "30 days", "description": "Minimal - only flag very stale sensors"}
      ],
      "multiSelect": false
    },
    {
      "question": "What SLA coverage target?",
      "header": "SLA Target",
      "options": [
        {"label": "99%", "description": "Very strict coverage requirement"},
        {"label": "95%", "description": "Standard enterprise target"},
        {"label": "90%", "description": "Relaxed coverage requirement"}
      ],
      "multiSelect": false
    }
  ]
)
```

---

## Workflow: Single-Org Mode

```
Phase 1: Initialization
    │
    ▼
Phase 2: Sensor Discovery & Classification
    │
    ▼
Phase 3: Asset Profiling (Online Sensors) ← ENABLED BY DEFAULT
    │
    ▼
Phase 4: Gap Detection & Risk Scoring
    │
    ▼
Phase 5: Report Generation & Remediation
```

### Phase 1: Initialization

#### 1.1 Get Organization

If OID not provided, get the user's organizations:

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_user_orgs
    - Parameters: {}
    - Return: RAW"
)
```

If multiple orgs, use `AskUserQuestion` to let user select one.

#### 1.2 Calculate Timestamps

**CRITICAL**: Always calculate timestamps dynamically via bash:

```bash
NOW=$(date +%s)
THRESHOLD_24H=$((NOW - 86400))      # 24 hours ago
THRESHOLD_7D=$((NOW - 604800))      # 7 days ago
THRESHOLD_30D=$((NOW - 2592000))    # 30 days ago
echo "Now: $NOW, 24h: $THRESHOLD_24H, 7d: $THRESHOLD_7D, 30d: $THRESHOLD_30D"
```

#### 1.3 User Confirmation

Before proceeding, confirm scope with user:

```
Organization: {org_name}
Mode: Single-Org (Deep Dive)
Asset Profiling: Enabled (OS, packages, users, services, autoruns, connections)
Stale Threshold: 7 days
SLA Target: 95%

Proceed with readiness check?
```

### Phase 2: Sensor Discovery & Classification

#### 2.1 Get All Sensors

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_sensors
    - Parameters: {\"oid\": \"[org-id]\"}
    - Return: RAW"
)
```

#### 2.2 Get Online Sensors

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: get_online_sensors
    - Parameters: {\"oid\": \"[org-id]\"}
    - Return: RAW"
)
```

**TIP**: Spawn both API calls in parallel (single message with multiple Task blocks).

#### 2.3 Classify by Offline Duration

Parse the `alive` field (format: "YYYY-MM-DD HH:MM:SS") and calculate hours offline:

| Category | Hours Offline | Description |
|----------|---------------|-------------|
| `online` | 0 | Currently connected |
| `recent_24h` | 1-24 | Recently offline |
| `short_1_7d` | 24-168 | Short-term offline |
| `medium_7_30d` | 168-720 | Medium-term offline |
| `critical_30d_plus` | 720+ | Critical coverage gap |

#### 2.4 Identify New Assets

Check `enroll` timestamp for sensors enrolled in last 24 hours - potential Shadow IT.

### Phase 3: Asset Profiling (Single-Org Default: ENABLED)

For each **online** sensor, spawn `asset-profiler` agents to collect detailed information.

#### 3.1 Spawn Asset Profiler Agents

Batch sensors (5-10 at a time) and spawn agents in parallel:

```
Task(
  subagent_type="lc-essentials:asset-profiler",
  model="haiku",
  prompt="Collect asset profile for sensor:
    - Organization: {org_name} (OID: {oid})
    - Sensor ID: {sid}
    - Hostname: {hostname}

    Collect: OS version, packages, users, services, autoruns, network connections.
    Return structured JSON profile."
)
```

**CRITICAL**: Spawn ALL agents in a SINGLE message to run in parallel.

#### 3.2 Asset Profile Data Collected

Each agent collects:
- `get_os_version` - OS name, version, build, architecture
- `get_packages` - Installed software inventory
- `get_users` - User accounts (flag admin users)
- `get_services` - Running services
- `get_autoruns` - Persistence mechanisms
- `get_network_connections` - Active connections

### Phase 4: Gap Detection & Risk Scoring

#### 4.1 Spawn Gap Analyzer Agent

```
Task(
  subagent_type="lc-essentials:gap-analyzer",
  model="haiku",
  prompt="Analyze gaps and calculate risk scores:
    - Organization: {org_name} (OID: {oid})
    - Total sensors: {count}
    - Online: {online_count}
    - Offline by category: {offline_breakdown}
    - New sensors (24h): {new_sensors}

    Calculate risk scores and identify remediation priorities."
)
```

#### 4.2 Risk Scoring Formula (0-100)

| Factor | Points | Condition |
|--------|--------|-----------|
| Offline 30+ days | +40 | Critical coverage gap |
| Offline 7-30 days | +25 | Medium-term offline |
| Offline 1-7 days | +15 | Short-term offline |
| Offline < 24h | +5 | Recently offline |
| No telemetry 24h | +20 | Online but no data |
| Untagged sensor | +10 | Missing metadata |
| New asset 24h | +15 | Potential Shadow IT |
| Network isolated | +15 | Contained endpoint |

**Severity Thresholds**:
- **Critical**: 60-100 points
- **High**: 40-59 points
- **Medium**: 20-39 points
- **Low**: 0-19 points

### Phase 5: Single-Org Report Generation

```
═══════════════════════════════════════════════════════════
          READINESS CHECK - ASSET INVENTORY REPORT
═══════════════════════════════════════════════════════════

Organization: {org_name}
Generated: {timestamp}

── COVERAGE SUMMARY ──
  Total Sensors:      {total}
  Online:             {online} ({online_pct}%)
  Offline:            {offline} ({offline_pct}%)

  Coverage SLA:       {sla_status} (Target: 95%)

── OFFLINE BREAKDOWN ──
  Critical (30+ days):  {critical_count}
  Medium (7-30 days):   {medium_count}
  Short (1-7 days):     {short_count}
  Recent (< 24h):       {recent_count}

── RISK DISTRIBUTION ──
  Critical Risk:   {risk_critical}
  High Risk:       {risk_high}
  Medium Risk:     {risk_medium}
  Low Risk:        {risk_low}

── NEW ASSETS (24h) ──
  Detected:        {new_count}
  Shadow IT Risk:  {shadow_it_risk}

── TOP ISSUES ──
1. {issue_1}
2. {issue_2}
3. {issue_3}
```

---

## Workflow: Multi-Org Mode (Fleet Assessment)

```
Phase 1: Discovery & Configuration
    │
    ▼
Phase 2: Parallel Per-Org Assessment (N agents)
    │
    ▼
Phase 3: Cross-Tenant Pattern Analysis
    │
    ▼
Phase 4: Fleet Report Generation
```

### Phase 1: Discovery & Configuration

#### 1.1 Get All Organizations

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_user_orgs
    - Parameters: {}
    - Return: RAW"
)
```

#### 1.2 Calculate Timestamps

```bash
NOW=$(date +%s)
THRESHOLD_24H=$((NOW - 86400))
THRESHOLD_7D=$((NOW - 604800))
THRESHOLD_30D=$((NOW - 2592000))
echo "Now: $NOW, 24h: $THRESHOLD_24H, 7d: $THRESHOLD_7D, 30d: $THRESHOLD_30D"
```

#### 1.3 User Confirmation

For large org counts, confirm before proceeding:

```
Fleet Readiness Check

Organizations Found: 47
Mode: Multi-Org (Fleet Assessment)
Asset Profiling: Disabled (enable with "include asset profiling")
Stale Threshold: 7 days
SLA Target: 95%

Pattern Detection Enabled:
  • Platform health degradation (>10% offline)
  • Coordinated enrollment detection (>5 sensors in 2h)
  • SLA compliance analysis
  • Risk concentration detection

Proceed with fleet assessment?
```

#### 1.4 Optional: Enable Asset Profiling

If user requests detailed profiling in multi-org mode:

```
AskUserQuestion(
  questions=[{
    "question": "Asset profiling across all orgs will take longer. Continue?",
    "header": "Asset Profiling",
    "options": [
      {"label": "Yes, full profiling", "description": "Collect OS, packages, services for all online sensors"},
      {"label": "No, metadata only", "description": "Faster - just sensor status and coverage metrics"}
    ],
    "multiSelect": false
  }]
)
```

### Phase 2: Parallel Per-Org Assessment

#### 2.1 Spawn org-readiness-reporter Agents

**CRITICAL**: Spawn ALL agents in a SINGLE message for true parallelism.

```
Task(
  subagent_type="lc-essentials:org-readiness-reporter",
  model="haiku",
  prompt="Collect readiness data for organization:
    - Organization: Client ABC (OID: uuid-1)
    - Timestamps: NOW={now}, 24H={t24h}, 7D={t7d}, 30D={t30d}
    - Stale Threshold: 7 days
    - SLA Target: 95%
    - Asset Profiling: false

    Return structured JSON with coverage, offline breakdown, risk distribution,
    platform breakdown, tag breakdown, new sensors, and top issues."
)

Task(
  subagent_type="lc-essentials:org-readiness-reporter",
  model="haiku",
  prompt="Collect readiness data for organization:
    - Organization: Client XYZ (OID: uuid-2)
    ..."
)

... (one Task per organization, all in same message)
```

#### 2.2 Expected Agent Response Format

Each `org-readiness-reporter` returns:

```json
{
  "org_name": "Client ABC",
  "oid": "uuid",
  "status": "success|partial|failed",
  "collected_at": "2025-12-05T16:30:00Z",
  "coverage": {
    "total_sensors": 150,
    "online": 142,
    "offline": 8,
    "coverage_pct": 94.7,
    "sla_target": 95,
    "sla_status": "FAILING"
  },
  "offline_breakdown": {
    "recent_24h": 3,
    "short_1_7d": 2,
    "medium_7_30d": 2,
    "critical_30d_plus": 1
  },
  "risk_distribution": {
    "critical": 1,
    "high": 3,
    "medium": 4,
    "low": 142
  },
  "platforms": {
    "windows": {"total": 100, "online": 95, "offline": 5, "offline_pct": 5.0},
    "linux": {"total": 50, "online": 47, "offline": 3, "offline_pct": 6.0}
  },
  "tags": {
    "production": {"total": 80, "online": 76, "offline": 4},
    "dev": {"total": 30, "online": 30, "offline": 0}
  },
  "new_sensors_24h": [
    {"sid": "...", "hostname": "test-vm-01", "enrolled_at": "2025-12-05T08:15:00Z"}
  ],
  "critical_sensors": [
    {"sid": "...", "hostname": "SERVER01", "risk_score": 65, "risk_factors": ["offline_30d_plus", "untagged"]}
  ],
  "top_issues": [
    "1 sensor offline 30+ days (critical)",
    "2 sensors offline 7-30 days",
    "1 new untagged sensor (Shadow IT risk)"
  ],
  "errors": []
}
```

#### 2.3 Handle Partial Failures

If some orgs fail, continue with successful ones:

```python
successful_results = [r for r in results if r['status'] in ['success', 'partial']]
failed_results = [r for r in results if r['status'] == 'failed']

# Continue analysis with successful results
# Document failures in report
```

### Phase 3: Cross-Tenant Pattern Analysis

#### 3.1 Spawn Fleet Pattern Analyzer

After collecting all per-org results:

```
Task(
  subagent_type="lc-essentials:fleet-pattern-analyzer",
  model="sonnet",  # Use sonnet for complex pattern analysis
  prompt="Analyze fleet-wide patterns from readiness data:

    Configuration:
    - Platform offline threshold: 10%
    - Enrollment cluster minimum: 5 sensors
    - Enrollment cluster window: 2 hours
    - SLA failure alert threshold: 20%

    Per-Org Results:
    {json_array_of_all_org_results}

    Analyze for:
    1. Platform health degradation (any platform with >10% offline rate)
    2. Coordinated enrollment patterns (sensors enrolled within 2h across orgs)
    3. SLA compliance patterns (group failures by org characteristics)
    4. Risk concentration (are critical risks clustered in specific orgs?)
    5. Temporal correlations (did sensors go offline at similar times?)

    Return structured JSON with:
    - fleet_summary (totals across all orgs)
    - systemic_issues (array of detected patterns)
    - platform_health (per-platform stats)
    - sla_compliance (orgs meeting/failing)
    - recommendations (prioritized actions)"
)
```

#### 3.2 Pattern Detection Details

The `fleet-pattern-analyzer` agent detects:

**Pattern 1: Platform Health Degradation**
- Calculate offline % per platform across all orgs
- Flag if any platform exceeds threshold (default: 10%)
- Identify affected orgs and sensor counts

**Pattern 2: Coordinated Enrollment (Shadow IT)**
- Aggregate all new_sensors_24h across orgs
- Detect time clusters (>N sensors within X hours)
- Check for common hostname patterns
- Flag cross-org enrollment spikes

**Pattern 3: SLA Compliance Patterns**
- Group orgs by size, platform mix, or tags
- Calculate SLA compliance rate per group
- Identify if specific org types are struggling

**Pattern 4: Risk Concentration**
- Check if critical risks are concentrated vs distributed
- Alert if few orgs have majority of critical sensors

**Pattern 5: Temporal Correlation**
- Check if offline events cluster around specific times
- Could indicate infrastructure issues or attacks

### Phase 4: Fleet Report Generation

```
═══════════════════════════════════════════════════════════
          FLEET READINESS REPORT - MULTI-TENANT
═══════════════════════════════════════════════════════════

Generated: 2025-12-05 16:30:00 UTC
Organizations: 47 of 50 analyzed successfully
Stale Threshold: 7 days | SLA Target: 95%

══════════════════════════════════════════════════════════
                    EXECUTIVE SUMMARY
══════════════════════════════════════════════════════════

Fleet Health: ⚠️ DEGRADED (2 systemic issues detected)

Key Metrics:
  • Total Sensors: 12,500 (across 47 organizations)
  • Fleet Coverage: 95.0% (11,875 online / 625 offline)
  • SLA Compliance: 89.4% (42 of 47 orgs meeting target)

Risk Overview:
  • Critical Risk Sensors: 12 (across 3 organizations)
  • High Risk Sensors: 45 (across 8 organizations)
  • Total At-Risk: 57 sensors requiring attention

══════════════════════════════════════════════════════════
              ⚠️ SYSTEMIC ISSUES DETECTED ⚠️
══════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│ ISSUE #1: Linux Platform Degradation (HIGH SEVERITY)   │
├─────────────────────────────────────────────────────────┤
│ Pattern: 15.2% offline rate (vs 3.5% fleet baseline)   │
│ Affected: 8 organizations, 125 Linux sensors           │
│                                                         │
│ Organizations Impacted:                                 │
│   • Client ABC - 23/45 Linux sensors offline (51%)     │
│   • Client XYZ - 18/62 Linux sensors offline (29%)     │
│   • Client DEF - 15/40 Linux sensors offline (37%)     │
│   • [5 more organizations...]                          │
│                                                         │
│ Possible Causes:                                        │
│   1. Recent kernel update causing agent crash          │
│   2. Network infrastructure change affecting Linux     │
│   3. Firewall rule blocking agent communication        │
│                                                         │
│ Recommended Actions:                                    │
│   □ Check agent logs on sample affected Linux hosts    │
│   □ Verify network connectivity to LC cloud            │
│   □ Review infrastructure changes (last 48h)           │
│   □ Consider rolling back recent Linux updates         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ISSUE #2: Coordinated Shadow IT (MEDIUM SEVERITY)      │
├─────────────────────────────────────────────────────────┤
│ Pattern: 12 sensors enrolled in 2h window across 4 orgs│
│ Hostname Pattern: "test-vm-*"                          │
│ Time Window: 2025-12-05 08:15 - 10:22 UTC              │
│                                                         │
│ Organizations Impacted:                                 │
│   • Client DEF - 4 new sensors                         │
│   • Client GHI - 3 new sensors                         │
│   • Client JKL - 3 new sensors                         │
│   • Client MNO - 2 new sensors                         │
│                                                         │
│ Recommended Actions:                                    │
│   □ Verify with IT if test deployments were planned    │
│   □ Check automation systems for triggered enrollments │
│   □ Investigate if sensors are legitimate              │
└─────────────────────────────────────────────────────────┘

══════════════════════════════════════════════════════════
                  PLATFORM HEALTH OVERVIEW
══════════════════════════════════════════════════════════

┌──────────┬────────┬────────┬─────────┬─────────────────┐
│ Platform │ Total  │ Online │ Offline │ Status          │
├──────────┼────────┼────────┼─────────┼─────────────────┤
│ Windows  │ 8,000  │ 7,720  │ 280     │ ✓ HEALTHY (3.5%)│
│ Linux    │ 3,500  │ 2,968  │ 532     │ ⚠ DEGRADED (15%)│
│ macOS    │ 1,000  │ 982    │ 18      │ ✓ HEALTHY (1.8%)│
└──────────┴────────┴────────┴─────────┴─────────────────┘

══════════════════════════════════════════════════════════
                    SLA COMPLIANCE
══════════════════════════════════════════════════════════

Target: 95% coverage
Meeting SLA: 42 organizations (89.4%)
Failing SLA: 5 organizations

Organizations Failing SLA (sorted by gap):
┌─────────────┬──────────┬────────┬──────────┐
│ Organization│ Coverage │ Gap    │ Priority │
├─────────────┼──────────┼────────┼──────────┤
│ Client ABC  │ 87.2%    │ -7.8%  │ CRITICAL │
│ Client XYZ  │ 91.5%    │ -3.5%  │ HIGH     │
│ Client DEF  │ 92.1%    │ -2.9%  │ HIGH     │
│ Client GHI  │ 93.8%    │ -1.2%  │ MEDIUM   │
│ Client JKL  │ 94.2%    │ -0.8%  │ MEDIUM   │
└─────────────┴──────────┴────────┴──────────┘

══════════════════════════════════════════════════════════
              PER-ORGANIZATION BREAKDOWN
══════════════════════════════════════════════════════════

[For each organization, show condensed summary:]

── Client ABC ──────────────────────────────────────────
  Coverage: 87.2% (131/150) ⚠️ FAILING SLA
  Risk: 1 critical, 3 high, 4 medium
  Issues: 1 sensor offline 30+ days, 2 untagged sensors
  Platforms: Windows (100), Linux (50)

── Client XYZ ──────────────────────────────────────────
  Coverage: 91.5% (183/200) ⚠️ FAILING SLA
  Risk: 0 critical, 2 high, 5 medium
  Issues: 2 sensors offline 7-30 days
  Platforms: Windows (150), Linux (50)

[... additional orgs ...]

══════════════════════════════════════════════════════════
              FAILED ORGANIZATIONS
══════════════════════════════════════════════════════════

⚠️ 3 organizations could not be assessed:

  • Legacy Corp (OID: abc-123)
    Error: 403 Forbidden on list_sensors
    Impact: No coverage data available
    Action: Check API permissions

  • Test Org (OID: def-456)
    Error: 500 Internal Server Error
    Impact: Partial data only
    Action: Retry or contact support

══════════════════════════════════════════════════════════
              FLEET-WIDE RECOMMENDATIONS
══════════════════════════════════════════════════════════

Priority 1 (Immediate):
  □ Investigate Linux platform degradation affecting 8 orgs
  □ Address 12 critical-risk sensors across 3 orgs

Priority 2 (Within 24h):
  □ Review Shadow IT enrollments across 4 orgs
  □ Remediate 5 orgs failing coverage SLA

Priority 3 (Within 7 days):
  □ Tag 23 unmanaged sensors across fleet
  □ Review 45 high-risk sensors

══════════════════════════════════════════════════════════
                    METHODOLOGY
══════════════════════════════════════════════════════════

Data Sources:
  • list_user_orgs - Organization discovery
  • list_sensors - Sensor inventory per org
  • get_online_sensors - Real-time online status

Pattern Detection:
  • Platform threshold: >10% offline = degraded
  • Enrollment clustering: >5 sensors in 2h window
  • SLA target: 95% coverage

Report Generated: 2025-12-05 16:35:00 UTC
Processing Time: 4 minutes 32 seconds
```

---

## Remediation Playbooks

### Playbook: Sensor Offline 30+ Days
```
Issue: {hostname} offline for {days} days
Risk Score: {score} (Critical)

Remediation Steps:
1. Verify endpoint status with IT Operations
2. Check if device decommissioned in CMDB
3. If active but offline:
   - Check network connectivity
   - Verify sensor service status
   - Consider sensor reinstallation
4. If decommissioned:
   - Remove sensor: delete_sensor(sid="{sid}")
5. Tag for tracking:
   - add_tag(sid="{sid}", tag="stale-30d-review", ttl=604800)
```

### Playbook: New Asset Detected (Shadow IT)
```
Issue: New sensor {hostname} enrolled {hours}h ago
Risk Score: {score} (High)

Remediation Steps:
1. Cross-reference with IT deployment tickets
2. Verify hostname matches naming convention
3. Check installation key used
4. If legitimate:
   - Apply department tags: add_tag(sid, "{dept}")
5. If unauthorized:
   - Investigate device ownership
   - Consider isolation: isolate_network(sid)
```

### Playbook: Platform Degradation (Multi-Org)
```
Issue: {platform} showing {pct}% offline rate across {org_count} orgs

Remediation Steps:
1. Identify common factors:
   - OS version distribution
   - Network segments
   - Recent changes (patches, configs)
2. Check sample hosts:
   - Agent service status
   - Network connectivity to LC cloud
   - System logs for errors
3. Coordinate fix across affected orgs
4. Consider staggered remediation to track effectiveness
```

---

## Export Options

After generating report, offer export:

```
AskUserQuestion(
  questions=[{
    "question": "How would you like to export this report?",
    "header": "Export",
    "options": [
      {"label": "Markdown", "description": "Human-readable text format"},
      {"label": "JSON", "description": "Structured data for automation"},
      {"label": "HTML Dashboard", "description": "Interactive visual dashboard"}
    ],
    "multiSelect": false
  }]
)
```

### HTML Dashboard Export

For visual output, invoke the `graphic-output` skill:

```
Skill(skill="lc-essentials:graphic-output")
```

Provide structured data:
```json
{
  "report_type": "fleet_readiness",
  "title": "Fleet Readiness Report",
  "mode": "multi_org",
  "generated_at": "2025-12-05T16:35:00Z",
  "fleet_summary": {...},
  "systemic_issues": [...],
  "platform_health": {...},
  "sla_compliance": {...},
  "per_org_breakdown": [...],
  "recommendations": [...]
}
```

---

## Integration with Other Skills

### sensor-health
**Use when**: Detailed telemetry availability checks (online but not sending data).

```
Skill(skill="lc-essentials:sensor-health")
```

### reporting
**Use when**: Billing, usage, and detection summaries across orgs.

```
Skill(skill="lc-essentials:reporting")
```

### timeline-creation
**Use when**: Investigating specific problematic sensors.

```
Skill(skill="lc-essentials:timeline-creation")
```

### detection-engineering
**Use when**: Creating D&R rules for Shadow IT detection.

```
Skill(skill="lc-essentials:detection-engineering")
```

---

## Troubleshooting

### No Sensors Found
- Verify OID is correct
- Check user has permissions for the organization

### Asset Profiling Fails
- Sensor may have gone offline since discovery
- Live commands require online sensors
- Check for permission errors

### Pattern Detection Issues
- Ensure sufficient orgs for meaningful patterns
- Check if thresholds are too aggressive/relaxed
- Review org result quality (partial failures may skew patterns)

### High False Positive Shadow IT
- Review installation key assignments
- Check expected enrollment patterns
- Adjust new asset threshold if needed
