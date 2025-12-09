---
name: fleet-dashboard
description: Generate comprehensive multi-org fleet dashboards with sensors, detections, health metrics, and anomaly detection. Spawns parallel agents for fast data collection across dozens of organizations, then renders interactive HTML dashboards with charts, tables, and actionable insights.
skills:
  - lc-essentials:limacharlie-call
  - lc-essentials:graphic-output
---

# Fleet Dashboard Skill

## Purpose

Generate comprehensive, interactive HTML dashboards showing fleet status, sensor health, detection trends, and anomalies across **all** LimaCharlie organizations in your account. Designed for MSSPs, security teams, and platform administrators managing multiple organizations.

## What This Skill Does

1. **Multi-Org Data Collection** - Spawns parallel `fleet-dashboard-collector` agents (one per org) to gather:
   - Sensor inventory (total, online, offline, by platform)
   - Recent detection volume and top categories
   - D&R rule counts
   - Output configurations
   - Adapter status
   - Organizational metadata

2. **Anomaly Detection** - Automatically identifies:
   - Organizations with no sensors deployed
   - Organizations with zero detections (possible blind spots)
   - Organizations with excessive detection volume (tuning needed)
   - Organizations with offline sensors > 50%
   - Organizations with no D&R rules configured
   - Organizations with no outputs configured (detections not routed)

3. **Interactive Dashboard** - Generates HTML with:
   - Executive summary with key metrics
   - Organization comparison tables (sortable, filterable)
   - Sensor distribution charts (by platform, by org)
   - Detection volume trends
   - Health score calculations
   - Anomaly alerts with severity levels
   - Exportable data in JSON/CSV formats

4. **Parallel Execution** - Uses agent orchestration pattern:
   - Spawns one `fleet-dashboard-collector` agent per organization
   - All agents run **in parallel** for maximum speed
   - Aggregates results into unified dashboard
   - Typical execution: 10-15 seconds for 10+ organizations

## Use Cases

**MSSP Operations:**
- "Generate a fleet dashboard for all my customer organizations"
- "Show me health metrics across my entire MSSP platform"
- "Which organizations need attention this week?"

**Security Team Management:**
- "Dashboard showing sensor coverage across all business units"
- "Compare detection volume across development, staging, and production orgs"
- "Show me which orgs have configuration gaps"

**Executive Reporting:**
- "Create a monthly status report for all security monitoring"
- "Generate dashboard showing platform adoption metrics"
- "Weekly security posture report across all organizations"

**Troubleshooting:**
- "Which organizations have the most offline sensors?"
- "Show me orgs with no detections in the last 24 hours"
- "Find orgs missing critical configurations"

## How It Works

### Architecture

```
User Request
    ↓
fleet-dashboard (Sonnet) - Orchestration skill
    ↓
├── Get list of all user organizations (via limacharlie-call)
├── Spawn N parallel agents (one per org)
│   ├── fleet-dashboard-collector (Haiku) - Org 1
│   ├── fleet-dashboard-collector (Haiku) - Org 2
│   ├── fleet-dashboard-collector (Haiku) - Org 3
│   └── ... (N agents running simultaneously)
├── Collect and aggregate results
├── Calculate health scores and detect anomalies
├── Generate structured JSON for dashboard
└── Invoke graphic-output skill → Interactive HTML Dashboard
```

### Data Collection Per Organization

Each `fleet-dashboard-collector` agent gathers:

**Sensor Metrics:**
- Total sensor count
- Online vs offline breakdown
- Platform distribution (Windows, Linux, macOS, Chrome, Cloud, etc.)
- Sensors with no recent events

**Detection Metrics:**
- Total detections (configurable time window, default 24h)
- Top 5 detection categories
- Detection rate trends

**Configuration Metrics:**
- D&R rule count (general + managed)
- Output count
- External adapter count
- Installation key count

**Health Indicators:**
- Sensor uptime percentage
- Detection velocity (detections per hour)
- Configuration completeness score

### Anomaly Detection Rules

**Critical Anomalies** (🔴):
- No sensors deployed
- No D&R rules configured
- No outputs configured (detections not routed)
- >80% sensors offline

**Warning Anomalies** (🟡):
- Zero detections in time window (possible blind spot)
- >50% sensors offline
- Detection volume >10,000/day (tuning needed)
- <5 D&R rules (minimal coverage)

**Informational** (🔵):
- New organization (created <7 days ago)
- Low sensor count (<5 sensors)
- Single platform deployment only

### Dashboard Components

**Executive Summary:**
- Total organizations monitored
- Total sensors across fleet
- Fleet-wide online percentage
- Total detections in time window
- Critical anomalies requiring action

**Organization Comparison Table:**
| Org Name | Sensors | Online % | Detections (24h) | Rules | Outputs | Health Score | Anomalies |
|----------|---------|----------|------------------|-------|---------|--------------|-----------|
| ... | ... | ... | ... | ... | ... | ... | ... |

**Visual Charts:**
- Sensor distribution by platform (pie chart)
- Sensor distribution by organization (bar chart)
- Detection volume by organization (bar chart)
- Health score distribution (histogram)

**Anomaly Alerts Section:**
- Grouped by severity (Critical → Warning → Info)
- Actionable recommendations for each anomaly
- Quick links to address issues

## Parameters

**Optional Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_window_hours` | integer | 24 | Hours to look back for detection metrics |
| `include_platform_breakdown` | boolean | true | Include detailed platform distribution |
| `health_score_weights` | object | See below | Custom weights for health score calculation |
| `export_format` | string | "html" | Output format: "html", "json", "both" |

**Default Health Score Weights:**
```json
{
  "sensor_uptime": 0.40,        // 40% weight
  "detection_activity": 0.20,   // 20% weight
  "rule_coverage": 0.20,        // 20% weight
  "output_configured": 0.10,    // 10% weight
  "adapter_health": 0.10        // 10% weight
}
```

## Example Usage

### Basic Fleet Dashboard

**User:** "Generate a fleet dashboard for all my organizations"

**Skill Actions:**
1. Lists all user organizations (e.g., 12 orgs)
2. Spawns 12 parallel `fleet-dashboard-collector` agents
3. Each agent collects data from one organization
4. Aggregates results and calculates health scores
5. Detects anomalies across the fleet
6. Invokes `graphic-output` skill to render HTML dashboard
7. Saves dashboard to `fleet-dashboard-<timestamp>.html`
8. Presents summary and anomaly highlights to user

### Custom Time Window

**User:** "Show me a fleet dashboard with detection data from the last 7 days"

**Skill Actions:**
- Sets `time_window_hours: 168` (7 days)
- Adjusts detection metrics collection accordingly
- Generates dashboard with weekly detection trends

### Targeted Subset

**User:** "Generate dashboard for only production organizations"

**Skill Actions:**
- Filters organization list by name pattern (e.g., contains "prod")
- Spawns agents only for matching orgs
- Generates focused dashboard

## Output Examples

### Console Summary

```
Fleet Dashboard Generated Successfully
=====================================

📊 Executive Summary:
- Organizations Monitored: 12
- Total Sensors: 487
- Fleet Online Rate: 78.2% (381 online, 106 offline)
- Detections (24h): 15,247
- Average Health Score: 82/100

🔴 Critical Anomalies (3):
- Org "dev-sandbox": No D&R rules configured
- Org "legacy-infra": 92% sensors offline (23/25)
- Org "test-env": No outputs configured

🟡 Warnings (5):
- Org "customer-acme": Zero detections in 24h
- Org "customer-contoso": 67% sensors offline
- Org "staging": Detection volume 12,500/day (tuning recommended)
- Org "iot-devices": Only 3 D&R rules
- Org "partner-xyz": Only 3 D&R rules

📈 Dashboard saved to: fleet-dashboard-2025-12-05-143022.html
🌐 Open in browser to view interactive charts and detailed breakdowns
```

### HTML Dashboard Features

**Interactive Elements:**
- Sortable tables (click column headers)
- Filterable by anomaly severity
- Hover tooltips with detailed metrics
- Drill-down links to specific organizations (if web console integration available)
- Export data buttons (JSON, CSV)
- Refresh metadata with generation timestamp

**Responsive Design:**
- Mobile-friendly layout
- Print-optimized view
- Dark/light theme toggle

## Performance Characteristics

**Parallel Execution Efficiency:**
- 1 organization: ~3-5 seconds
- 10 organizations: ~8-12 seconds (vs. ~30-50 seconds sequential)
- 50 organizations: ~15-25 seconds (vs. ~150-250 seconds sequential)
- 100 organizations: ~20-35 seconds (vs. ~300-500 seconds sequential)

**Agent Model Selection:**
- Orchestration: Sonnet (complex aggregation and analysis)
- Data collection: Haiku (fast, cost-effective API calls)
- HTML rendering: Uses existing `html-renderer` agent

## Error Handling

**Partial Failures:**
- If some organizations fail to collect data, continue with others
- Clearly mark failed organizations in dashboard
- Include error details in anomaly section
- Generate dashboard with available data

**Complete Failures:**
- If unable to list organizations, provide clear error message
- If all agents fail, return diagnostic information
- Suggest troubleshooting steps (API key validation, permissions)

## Integration with Other Skills

**Complementary Skills:**
- **sensor-health**: Drill down into specific organization's sensor health
- **reporting**: Generate detailed MSSP billing and usage reports
- **detection-tuner**: Address high-volume detection anomalies
- **limacharlie-call**: Manually investigate specific organizations

**Typical Workflow:**
1. Generate fleet dashboard (this skill) → Identify anomalies
2. Use **sensor-health** for orgs with connectivity issues
3. Use **detection-tuner** for orgs with excessive detections
4. Use **reporting** for monthly executive summaries

## Skill Prompt

You are the **fleet-dashboard** skill orchestrator. Your job is to generate comprehensive, interactive dashboards showing fleet status across all LimaCharlie organizations.

### Step 1: Get Organization List

Use the `limacharlie-call` skill to get all user organizations:

```
Use limacharlie-call skill with function: list-user-orgs
```

This returns a list of organizations with OIDs and names.

### Step 2: Validate Organization Count

- If 0 organizations: Return error "No organizations found in your account"
- If 1 organization: Warn user this is designed for multi-org, but proceed
- If 2-100 organizations: Optimal use case, proceed with parallel collection
- If >100 organizations: Warn about potential rate limits, offer to batch

### Step 3: Spawn Parallel Agents

Use the Task tool to spawn one `fleet-dashboard-collector` agent per organization **IN A SINGLE MESSAGE**.

**CRITICAL**: You MUST spawn all agents in parallel by sending a single message with multiple Task tool calls. DO NOT spawn them sequentially.

Example for 3 organizations:

```
[Single message with 3 Task tool calls]
Task(subagent_type="lc-essentials:fleet-dashboard-collector",
     model="haiku",
     prompt=f"Collect fleet dashboard data for organization '{org1_name}' (OID: {org1_oid}). Time window: 24 hours. Return structured JSON with sensor counts, platform breakdown, detection metrics, rule counts, output counts, and adapter counts.")

Task(subagent_type="lc-essentials:fleet-dashboard-collector",
     model="haiku",
     prompt=f"Collect fleet dashboard data for organization '{org2_name}' (OID: {org2_oid}). Time window: 24 hours. Return structured JSON with sensor counts, platform breakdown, detection metrics, rule counts, output counts, and adapter counts.")

Task(subagent_type="lc-essentials:fleet-dashboard-collector",
     model="haiku",
     prompt=f"Collect fleet dashboard data for organization '{org3_name}' (OID: {org3_oid}). Time window: 24 hours. Return structured JSON with sensor counts, platform breakdown, detection metrics, rule counts, output counts, and adapter counts.")
```

### Step 4: Aggregate Results

When all agents return:

1. **Parse each agent's JSON response**
2. **Detect failed collections** - Mark orgs with errors
3. **Calculate fleet-wide metrics**:
   - Total sensors (sum across all orgs)
   - Fleet online percentage (weighted average)
   - Total detections (sum)
   - Average health score
4. **Build organization comparison table data**

**CRITICAL**: You MUST build a complete data structure with ALL required keys before proceeding to dashboard generation. The data structure must include:
- `metadata` object (generated_at, time_window_hours, total_orgs, successful_collections, failed_collections)
- `summary` object (total_sensors, online_sensors, offline_sensors, fleet_online_percentage, total_detections, average_health_score, critical_anomalies, warning_anomalies, info_anomalies)
- `organizations` array (REQUIRED - must contain array of organization objects, even if empty)
- `anomalies` array (REQUIRED - must contain array of anomaly objects, even if empty)

### Step 5: Anomaly Detection

For each organization, check:

**Critical (🔴):**
- `sensor_count == 0` → "No sensors deployed"
- `rule_count == 0` → "No D&R rules configured"
- `output_count == 0` → "No outputs configured"
- `online_percentage < 20` → "Critical sensor connectivity issues"

**Warning (🟡):**
- `detection_count == 0` AND `sensor_count > 0` → "No detections (possible blind spot)"
- `online_percentage < 50` → "Poor sensor uptime"
- `detection_count > 10000` → "Excessive detections (tuning needed)"
- `rule_count < 5` → "Minimal detection coverage"

**Info (🔵):**
- `sensor_count < 5` → "Small deployment"
- `platform_count == 1` → "Single platform only"

### Step 6: Calculate Health Scores

For each organization, calculate health score (0-100):

```
health_score = (
    (online_percentage * 0.40) +
    (min(detection_activity_score, 100) * 0.20) +
    (min(rule_count / 50 * 100, 100) * 0.20) +
    (output_count > 0 ? 100 : 0) * 0.10 +
    (adapter_health_score * 0.10)
)

where:
- detection_activity_score = has detections ? 100 : 0 (binary)
- adapter_health_score = (online_adapters / total_adapters) * 100 if adapters exist, else 100
```

### Step 7: Generate Dashboard Data Structure

Create JSON structure for dashboard:

```json
{
  "metadata": {
    "generated_at": "2025-12-05T14:30:22Z",
    "time_window_hours": 24,
    "total_orgs": 12,
    "successful_collections": 11,
    "failed_collections": 1
  },
  "summary": {
    "total_sensors": 487,
    "online_sensors": 381,
    "offline_sensors": 106,
    "fleet_online_percentage": 78.2,
    "total_detections": 15247,
    "average_health_score": 82,
    "critical_anomalies": 3,
    "warning_anomalies": 5,
    "info_anomalies": 2
  },
  "organizations": [
    {
      "name": "TPS Reporting Solutions",
      "oid": "aac9c41d-e0a3-4e7e-88b8-33936ab93238",
      "sensors": {
        "total": 60,
        "online": 25,
        "offline": 35,
        "online_percentage": 41.7,
        "platforms": {
          "Windows": 3,
          "Linux": 8,
          "Adapters": 39,
          "Chrome": 1,
          "AWS": 1
        }
      },
      "detections": {
        "total": 5000,
        "top_categories": [
          {"name": "rundll32_Network_Connection", "count": 1179},
          {"name": "SYNC fired", "count": 508},
          {"name": "Non Interactive PowerShell", "count": 220}
        ]
      },
      "configuration": {
        "rules": 68,
        "outputs": 37,
        "adapters": 3,
        "installation_keys": 36
      },
      "health_score": 65,
      "anomalies": [
        {"severity": "warning", "type": "sensor_uptime", "message": "Only 41.7% sensors online"}
      ]
    }
    // ... more orgs
  ],
  "anomalies": [
    {
      "severity": "critical",
      "org_name": "dev-sandbox",
      "oid": "...",
      "type": "no_rules",
      "message": "No D&R rules configured",
      "recommendation": "Deploy baseline detection rules to enable threat detection"
    }
    // ... more anomalies
  ]
}
```

### Step 8: Validate Data Structure

**BEFORE** invoking graphic-output, validate that your data structure has all required keys:

```python
# Required validation checks:
assert 'metadata' in data
assert 'summary' in data
assert 'organizations' in data  # CRITICAL - must be present
assert 'anomalies' in data      # CRITICAL - must be present
assert isinstance(data['organizations'], list)
assert isinstance(data['anomalies'], list)
```

If any key is missing, DO NOT proceed to graphic-output. Fix the data structure first.

### Step 9: Invoke Graphic Output

Use the `graphic-output` skill to render the HTML dashboard:

```
Use graphic-output skill with:
- data: [JSON structure from Step 7]
- template: "fleet-dashboard"
- title: "Multi-Org Fleet Dashboard"
- filename: "fleet-dashboard-<timestamp>.html"
```

The graphic-output skill will:
- Render interactive HTML with charts
- Generate sortable tables
- Add filtering controls
- Include export buttons
- Save to file

### Step 10: Present Summary to User

After dashboard is generated, provide concise summary:

1. **Executive metrics** (orgs, sensors, detections, health score)
2. **Critical anomalies** (with org names)
3. **Warning anomalies** (with org names)
4. **Dashboard file location**
5. **Next steps** (recommend addressing critical anomalies first)

## Important Implementation Notes

**Parallel Agent Spawning:**
- ALWAYS spawn all agents in a SINGLE message with multiple Task calls
- NEVER spawn agents sequentially in a loop
- This is critical for performance (10x+ speedup)

**Error Resilience:**
- Continue if some organizations fail
- Mark failed orgs clearly in dashboard
- Don't let one failure block entire dashboard

**Rate Limiting:**
- For >50 orgs, consider batching in groups of 50
- Add brief delays between batches if needed

**Data Freshness:**
- Include generation timestamp in dashboard
- Note time window for detection metrics
- Indicate if any data is stale (>1 hour old)

**User Experience:**
- Provide progress updates if possible ("Collecting data from 12 organizations...")
- Show summary immediately, dashboard file as artifact
- Highlight actionable items (anomalies requiring attention)

## Expected Agent Response Format

Each `fleet-dashboard-collector` agent should return JSON:

```json
{
  "success": true,
  "org_name": "TPS Reporting Solutions",
  "oid": "aac9c41d-e0a3-4e7e-88b8-33936ab93238",
  "collection_timestamp": "2025-12-05T14:30:22Z",
  "sensors": {
    "total": 60,
    "online": 25,
    "offline": 35,
    "online_percentage": 41.7,
    "platforms": {"Windows": 3, "Linux": 8, "Adapters": 39}
  },
  "detections": {
    "total": 5000,
    "time_window_hours": 24,
    "top_categories": [...]
  },
  "configuration": {
    "rules": 68,
    "outputs": 37,
    "adapters": 3
  },
  "errors": []
}
```

Or if failed:

```json
{
  "success": false,
  "org_name": "Failed Org",
  "oid": "...",
  "errors": ["Failed to list sensors: permission denied"]
}
```

## Common Issues and Solutions

**Issue**: "Too many organizations (>100), slow execution"
**Solution**: Batch in groups of 50, generate multiple dashboards or filter

**Issue**: "Some agents timing out"
**Solution**: Mark as failed, continue with available data, note in anomalies

**Issue**: "Permission errors for some orgs"
**Solution**: User may have read-only access to some orgs, note in dashboard

**Issue**: "Detection count hit limit (5000)"
**Solution**: Note in dashboard that count may be higher, recommend narrower time window

This skill provides critical multi-org visibility that's currently missing from the LimaCharlie platform. Use it for executive reporting, MSSP operations, and proactive fleet management.
