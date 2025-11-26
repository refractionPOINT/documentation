---
name: mssp-reporting
description: Generate comprehensive multi-tenant MSSP security and operational reports from LimaCharlie. Provides billing summaries, usage analytics, detection trends, sensor health monitoring, and configuration audits across multiple customer organizations. Built with strict data accuracy guardrails to prevent fabricated metrics. Supports partial report generation when some organizations fail, with transparent error documentation. Time windows always displayed, detection limits clearly flagged, zero cost calculations.
allowed-tools:
  - mcp__plugin_lc-essentials_limacharlie__lc_call_tool
  - Read
  - Write
  - Bash
---

# LimaCharlie MSSP Reporting Skill

## Overview

This skill enables AI-assisted generation of comprehensive security and operational reports for MSSPs managing multiple LimaCharlie organizations. It provides structured access to billing data, usage statistics, detection summaries, sensor health, and configuration audits across customer tenants.

**Core Philosophy**: Accuracy over completeness. This skill prioritizes data accuracy with strict guardrails that make fabricated metrics impossible. Reports clearly document what data is available, what failed, and what limits were applied.

## Purpose

- Generate multi-tenant MSSP reports across 50+ customer organizations
- Provide billing and usage summaries for customer invoicing
- Analyze security detection trends across customer base
- Monitor sensor health and deployment status
- Audit organizational configurations
- Track operational metrics for capacity planning
- Support partial report generation with clear error documentation

## When to Use This Skill

Use this skill when you need to:

### Multi-Tenant MSSP Reports
- **"Generate monthly report for all my customers"** - Comprehensive overview across all organizations
- **"Billing summary for November 2025"** - Usage and billing data for invoicing period
- **"Show me customer health dashboard"** - Sensor status and detection trends across clients
- **"Which customers had the most detections this month?"** - Security activity ranking
- **"Export usage data for all organizations"** - Bulk data extraction for analysis

### Single Organization Deep Dives
- **"Detailed report for Client ABC"** - Complete organizational analysis
- **"Security posture for organization XYZ"** - Detection and rule effectiveness
- **"Sensor health for customer PDQ"** - Endpoint deployment and status

### Billing and Usage Analysis
- **"Usage trends across all customers"** - Comparative analysis for capacity planning
- **"Which orgs are using the most data?"** - Resource consumption identification
- **"Show subscription status for all clients"** - Billing health check

### Operational Monitoring
- **"How many sensors are offline across all orgs?"** - Fleet health monitoring
- **"Detection volume trends this month"** - Security activity patterns
- **"Which customers need attention?"** - Issue identification and prioritization

## Critical Prerequisites

### Authentication
Ensure you are authenticated to LimaCharlie with access to target organizations:
- User must have permissions across multiple organizations (MSSP/partner account)
- Billing data requires admin/owner role per organization
- Usage statistics accessible with standard read permissions

### Understanding Organization IDs (OIDs)
**⚠️ CRITICAL**: Organization ID (OID) is a **UUID** (like `c7e8f940-1234-5678-abcd-1234567890ab`), **NOT** the organization name.

- Use `list-user-orgs` function to get OID from organization name
- All API calls require the UUID, not the friendly name
- OIDs are permanent identifiers (names can change)

### Time Range Requirements
- All reports MUST specify explicit time ranges
- Time windows MUST be displayed in every report section
- Default to last 30 days if not specified (but always confirm with user)
- Maximum recommended range: 90 days (API limitations)

## Data Accuracy Guardrails

### Principle 1: NEVER Fabricate Data

**Absolute Rules:**
- ❌ NEVER estimate, infer, or extrapolate data not in API responses
- ❌ NEVER calculate costs (no pricing data in API)
- ❌ NEVER guess at missing fields
- ❌ NEVER assume "standard" values
- ❌ NEVER substitute placeholder data for errors

**Always:**
- ✅ Show "N/A" or "Data unavailable" for missing fields
- ✅ Display explicit warnings when limits reached
- ✅ Document all errors and failures prominently
- ✅ State "Retrieved X of potentially more" when truncated
- ✅ Link to invoice URLs for billing details

### Principle 2: Detection Limit Handling

**Default Limit**: 5,000 detections per organization

**Required Workflow:**
```
1. Query with limit=5000
2. Track retrieved_count
3. Check: limit_reached = (retrieved_count >= 5000)
4. If limit_reached:
   ⚠️ DISPLAY PROMINENT WARNING
   "DETECTION LIMIT REACHED
    Retrieved: 5,000 detections
    Actual count: May be significantly higher

    For complete data:
      - Narrow time range
      - Query specific date ranges
      - Filter by category or sensor"
```

**Never Say:**
- ❌ "Total detections: 5,000" (implies this is complete)
- ❌ "Approximately 5,000 detections" (ambiguous)

**Always Say:**
- ✅ "Retrieved 5,000 detections (limit reached - actual count may be higher)"
- ✅ "Detection sample: First 5,000 of potentially more"

### Principle 3: Pricing and Billing

**Absolute Rule: ZERO Cost Calculations**

**What You CAN Show:**
- ✅ Usage metrics: events, data output (GB), evaluations, peak sensors
- ✅ Billing metadata: plan name, status, next billing date
- ✅ Invoice links: get-org-invoice-url for actual costs

**What You CANNOT Do:**
- ❌ Calculate costs based on usage
- ❌ Estimate bills
- ❌ Multiply usage by assumed rates
- ❌ Project future costs
- ❌ Compare plan pricing

**Even if user provides rates:**
- ❌ Don't perform calculations
- ✅ Show usage metrics
- ✅ Provide invoice link
- ✅ State: "For billing details, see invoice: [URL]"

### Principle 4: Time Window Display

**MANDATORY in Every Report:**

```
Header (always visible):
  Generated: 2025-11-20 14:45:30 UTC
  Time Window: 2025-11-01 00:00:00 UTC to 2025-11-30 23:59:59 UTC (30 days)
  Organizations: 45 of 50 processed successfully

Per Section:
  ── Usage Statistics ──
  Data Retrieved: 2025-11-20 14:45:35 UTC
  Coverage Period: Nov 1-30, 2025 (30 days)
  Source: get-usage-stats API
  Data Freshness: Daily updates (24hr delay typical)
```

### Principle 5: Error Transparency

**Partial Reports Are Acceptable:**
- Generate reports even if some organizations fail
- Clearly document which organizations failed and why
- Never silently skip failed organizations
- Provide actionable remediation steps

**Error Documentation Template:**
```
⚠️ FAILED ORGANIZATIONS (3 of 50)

Client ABC (oid: c7e8f940-...)
  Status: ❌ Failed
  Error: 403 Forbidden
  Endpoint: get-billing-details
  Reason: Insufficient permissions
  Impact: Billing data unavailable
  Action: Grant billing:read permission
  Timestamp: 2025-11-20 14:32:15 UTC
```

## Available Data Sources

### 1. Multi-Tenant Discovery
**Function**: `list-user-orgs`
- **Endpoint**: GET /v1/user/orgs
- **OID Required**: NO (user-level operation)
- **Returns**: List of accessible organizations with OIDs and names
- **Usage**: Starting point for all multi-tenant operations
- **Data Freshness**: Real-time

**Response Structure:**
```json
{
  "orgs": [
    {
      "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
      "name": "Client ABC Production",
      "role": "owner"
    },
    {
      "oid": "c7e8f940-5678-1234-dcba-0987654321ab",
      "name": "Client XYZ Security",
      "role": "admin"
    }
  ],
  "total": 2
}
```

**Validation:**
- Check `orgs` array exists and not empty
- Verify each OID is valid UUID format
- Confirm role is "owner", "admin", or "user"

### 2. Organization Metadata
**Function**: `get-org-info`
- **Endpoint**: GET /v1/orgs/{oid}
- **OID Required**: YES
- **Returns**: Organization details, creation date, settings
- **Data Freshness**: Real-time

**Response Structure:**
```json
{
  "oid": "c7e8f940-...",
  "name": "Client ABC",
  "created": 1672531200,
  "creator": "user@example.com"
}
```

### 3. Usage Statistics
**Function**: `get-usage-stats`
- **Endpoint**: GET /v1/usage/{oid}
- **OID Required**: YES
- **Returns**: Daily usage metrics (~90 days historical)
- **Data Freshness**: Daily aggregation, 24-hour delay typical

**Response Structure:**
```json
{
  "usage": {
    "2025-11-06": {
      "sensor_events": 131206,
      "output_bytes_tx": 500123456,
      "replay_num_evals": 435847,
      "peak_sensors": 4
    },
    "2025-11-07": {
      "sensor_events": 145821,
      "output_bytes_tx": 523456789,
      "replay_num_evals": 478932,
      "peak_sensors": 4
    }
  }
}
```

**Field Definitions:**
- `sensor_events`: Total events ingested from sensors
- `output_bytes_tx`: Data transmitted to outputs (in bytes)
- `replay_num_evals`: D&R rule evaluations performed
- `peak_sensors`: Maximum concurrent sensors online

**Critical Notes:**
- API returns ~90 days of data
- **MUST filter to requested time range** - don't use all 90 days
- Dates are in YYYY-MM-DD format
- `output_bytes_tx` is in BYTES - convert to GB: divide by 1,073,741,824
- ALWAYS show both: "450 GB (483,183,820,800 bytes)"

**Aggregation Rules:**
```
For time range Nov 1-30, 2025:
  1. Filter usage dict to only dates in range
  2. Sum daily values:
     total_events = sum(usage[date]['sensor_events'] for date in range)
  3. Document calculation:
     "Total Events: 1,250,432,100
      Calculation: Sum of daily sensor_events from Nov 1-30, 2025
      Source: get-usage-stats"
```

### 4. Billing Details
**Function**: `get-billing-details`
- **Endpoint**: GET /orgs/{oid}/details (billing endpoint)
- **OID Required**: YES
- **Permissions**: Requires admin/owner role
- **Returns**: Subscription info, payment status, billing contact
- **Data Freshness**: Updated on changes, ~1hr delay

**Response Structure:**
```json
{
  "plan": "enterprise",
  "status": "active",
  "billing_email": "billing@example.com",
  "payment_method": "card",
  "last_four": "4242",
  "next_billing_date": 1672531200,
  "auto_renew": true
}
```

**Common Error**: 403 Forbidden (insufficient permissions)
- Expected for user-role accounts
- Document in failures section
- Continue with partial data

### 5. Invoice URLs
**Function**: `get-org-invoice-url`
- **Endpoint**: GET /orgs/{oid}/invoice
- **OID Required**: YES
- **Returns**: Direct URL to organization's invoice
- **Usage**: For actual billing amounts (no cost calculations in reports)

**Response Structure:**
```json
{
  "url": "https://billing.limacharlie.io/invoice/..."
}
```

**Usage in Reports:**
```
For billing details and charges:
→ View Invoice: https://billing.limacharlie.io/invoice/...
```

### 6. Sensor Inventory
**Function**: `list-sensors`
- **Endpoint**: GET /v1/sensors/{oid}
- **OID Required**: YES
- **Returns**: All sensors with metadata
- **Data Freshness**: Real-time snapshot
- **Large Result Handling**: May return `resource_link` if >100KB

**Response Structure (normal):**
```json
{
  "sensors": {
    "sensor-id-1": {
      "sid": "sensor-id-1",
      "hostname": "SERVER01",
      "plat": 268435456,
      "arch": 1,
      "enroll": "2024-01-15T10:30:00Z",
      "alive": "2024-11-20 14:22:13",
      "int_ip": "10.0.1.50",
      "ext_ip": "203.0.113.45",
      "oid": "c7e8f940-..."
    }
  },
  "continuation_token": ""
}
```

**Large Result Handling:**
If API returns `resource_link` instead of inline data:

```json
{
  "success": true,
  "resource_link": "https://storage.googleapis.com/...",
  "resource_size": 234329,
  "reason": "results too large, see resource_link"
}
```

**REQUIRED Workflow for resource_link:**
```bash
# Step 1: Download and analyze schema (MANDATORY - do not skip)
bash ./marketplace/plugins/lc-essentials/scripts/analyze-lc-result.sh "https://storage.googleapis.com/..."

# Output shows schema and file path:
# (stdout) {"sensors": {"sensor-id": {"sid": "string", "hostname": "string", ...}}}
# (stderr) ---FILE_PATH---
# (stderr) /tmp/lc-result-1234567890.json

# Step 2: Review schema output BEFORE writing jq queries

# Step 3: Extract only needed fields with jq
jq '.sensors | length' /tmp/lc-result-1234567890.json  # Count
jq '.sensors | to_entries | .[].value.hostname' /tmp/lc-result-1234567890.json | head -20  # Sample hostnames

# Step 4: Clean up
rm /tmp/lc-result-1234567890.json
```

**NEVER:**
- Assume JSON structure without analyzing schema
- Write jq queries before seeing schema output
- Skip the analyze-lc-result.sh step
- Load entire large file into context

**Field Validation - CRITICAL:**

**CORRECT Fields to Use:**
- ✅ `alive`: "2025-11-20 14:22:13" (datetime string for last seen)
- ✅ `plat`: Platform code (int or string)
- ✅ `hostname`: Sensor hostname
- ✅ `sid`: Sensor ID
- ✅ `int_ip`: Internal IP address
- ✅ `ext_ip`: External IP address

**INCORRECT Fields (Common Mistakes):**
- ❌ `last_seen`: Often 0 or missing - DO NOT USE
- ❌ Use `alive` field instead for offline detection

**Offline Sensor Detection:**
```python
# Parse alive field (datetime string format: "YYYY-MM-DD HH:MM:SS")
from datetime import datetime, timezone

alive_str = sensor_info.get('alive', '')
if alive_str:
    # Parse: "2025-10-01 17:08:10"
    alive_dt = datetime.strptime(alive_str, '%Y-%m-%d %H:%M:%S')
    alive_dt = alive_dt.replace(tzinfo=timezone.utc)
    last_seen_timestamp = alive_dt.timestamp()

    hours_offline = (current_time - last_seen_timestamp) / 3600

    # Categorize with explicit thresholds:
    if hours_offline < 24:
        category = "Recently offline (< 24 hours)"
    elif hours_offline < 168:  # 7 days
        category = "Offline short term (1-7 days)"
    elif hours_offline < 720:  # 30 days
        category = "Offline medium term (7-30 days)"
    else:
        category = "Offline long term (30+ days)"
```

**Platform Code Translation:**

Traditional OS platforms (strings):
- "windows" → Windows
- "linux" → Linux
- "macos" → macOS
- "chrome" → Chrome OS

Numeric platform codes (extensions/adapters):
- Use two-pass pattern analysis
- Collect hostname samples
- Match patterns: ext-, test-, slack-, office365-
- ALWAYS show sample hostnames in report

**Example:**
```
Platform: LimaCharlie Extensions (code: 2415919104)
Sample hostnames: ext-strelka-01, ext-hayabusa-02, ext-secureannex-01
Sensor count: 30
```

### 7. Online Sensors
**Function**: `get-online-sensors`
- **Endpoint**: GET /v1/sensors/online/{oid}
- **OID Required**: YES
- **Returns**: List of currently online sensor IDs
- **Data Freshness**: Real-time

**Response Structure:**
```json
{
  "sensors": [
    "sensor-id-1",
    "sensor-id-2",
    "sensor-id-3"
  ]
}
```

**Usage:**
```python
# Convert to set for O(1) lookup
online_sids = set(response['sensors'])

# Check if sensor is online
is_online = sensor_id in online_sids

# Calculate offline count
total_sensors = 2500
online_count = len(online_sids)
offline_count = total_sensors - online_count
```

### 8. Historic Detections
**Function**: `get-historic-detections`
- **Endpoint**: GET /v1/insight/{oid}/detections
- **OID Required**: YES
- **Returns**: Security detections within time range
- **Data Freshness**: Near real-time (5-minute delay typical)
- **Default Limit**: 5,000 per query

**Query Parameters:**
- `start`: Unix epoch timestamp (seconds)
- `end`: Unix epoch timestamp (seconds)
- `limit`: Maximum detections to retrieve (default: 5000)
- `sid`: Filter by sensor ID (optional)
- `cat`: Filter by category (optional)

**Response Structure:**
```json
{
  "detects": [
    {
      "detect_id": "detect-uuid-123",
      "cat": "suspicious_process",
      "source_rule": "general.encoded-powershell",
      "namespace": "general",
      "ts": 1732108934567,
      "sid": "sensor-xyz-123",
      "detect": {
        "event": {
          "TIMESTAMP": 1732108934567,
          "COMMAND_LINE": "powershell.exe -encodedCommand ...",
          "FILE_PATH": "C:\\Windows\\System32\\..."
        },
        "routing": {
          "sid": "sensor-xyz-123",
          "hostname": "SERVER01"
        }
      }
    }
  ],
  "next_cursor": ""
}
```

**Field Validation - CRITICAL:**

**CORRECT Fields:**
- ✅ `source_rule`: "namespace.rule-name" (actual rule identifier)
- ✅ `cat`: Category name
- ✅ `ts`: Timestamp (MAY be seconds or milliseconds - normalize!)
- ✅ `sid`: Sensor ID (may be "N/A" for some detections)
- ✅ `detect_id`: Unique detection identifier

**INCORRECT Fields (Common Mistakes):**
- ❌ `rule_name`: Doesn't exist - use `source_rule` instead
- ❌ `severity`: NOT in detection records (only in D&R rule config)

**Timestamp Normalization (MANDATORY):**
```python
ts = detection.get('ts', 0)

# Check magnitude to determine units
if ts > 10000000000:
    # Milliseconds - convert to seconds
    ts = ts / 1000

# Sanity check result
if ts < 1577836800:  # Before 2020-01-01
    # Invalid timestamp
    display = "Invalid timestamp"
elif ts > time.time() + 86400:  # More than 1 day in future
    # Invalid timestamp
    display = "Invalid timestamp"
else:
    # Valid - format for display
    display = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
```

**Detection Limit Tracking (MANDATORY):**
```python
retrieved_count = 0
for detection in detections:
    retrieved_count += 1

limit_reached = (retrieved_count >= query_limit)

if limit_reached:
    # MUST display prominent warning
    warning = f"""
    ⚠️ DETECTION LIMIT REACHED
    Retrieved: {retrieved_count:,} detections
    Actual count: May be significantly higher

    This organization has more detections than retrieved.
    For complete data:
      - Narrow time range (currently: {days} days)
      - Query specific date ranges separately
      - Filter by category or sensor
    """
```

### 9. D&R Rules Inventory
**Function**: `list-dr-general-rules`
- **Endpoint**: GET /v1/rules/{oid}?namespace=general
- **OID Required**: YES
- **Returns**: Custom D&R rules in general namespace
- **Data Freshness**: Real-time

**Response Structure:**
```json
{
  "custom-rule-1": {
    "name": "custom-rule-1",
    "namespace": "general",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "powershell"
    },
    "respond": [
      {
        "action": "report",
        "name": "suspicious_powershell"
      }
    ],
    "is_enabled": true
  }
}
```

**Usage:**
- Count total rules: Object.keys(response).length
- Count enabled: Filter where is_enabled === true
- List detection types: Extract event types from detect blocks

### 10. Outputs Configuration
**Function**: `list-outputs`
- **Endpoint**: GET /v1/outputs/{oid}
- **OID Required**: YES
- **Returns**: Configured data outputs (SIEM, storage, webhooks)
- **Data Freshness**: Real-time

**Usage in Reports:**
- Count total outputs
- List destination types
- Note any disabled outputs

## Workflow Patterns

### Pattern 1: Multi-Tenant MSSP Comprehensive Report

**User Request Examples:**
- "Generate monthly MSSP report for all my customers"
- "Show me comprehensive overview across all organizations"
- "Create security and billing summary for November 2025"

**Step-by-Step Execution:**

```
┌─ PHASE 1: DISCOVERY ──────────────────────────────┐
│ 1. Call: list-user-orgs (no OID required)        │
│    MCP Tool: mcp__plugin_lc-essentials_limacharlie__lc_call_tool
│    Params: {
│      endpoint: "api",
│      method: "GET",
│      path: "/v1/user/orgs"
│    }
│                                                    │
│ 2. Validation:                                    │
│    ✓ Check response.body.orgs exists              │
│    ✓ Verify orgs array not empty                  │
│    ✓ Validate each OID is UUID format             │
│    ✓ Count total organizations                    │
│                                                    │
│ 3. User Confirmation (if >20 orgs):              │
│    "Found 50 organizations. Generate report for   │
│     all 50? This will take approximately 5-10     │
│     minutes and make ~300 API calls."             │
│                                                    │
│    Options to present:                            │
│    - Yes, process all 50                          │
│    - No, let me filter first                      │
│    - Show me the organization list                │
└────────────────────────────────────────────────────┘

┌─ PHASE 2: TIME RANGE VALIDATION ──────────────────┐
│ 4. Parse time range from user request:           │
│    - "monthly" → Last 30 days from today          │
│    - "November" → Nov 1-30, 2025 (full month)     │
│    - "last week" → 7 days from today              │
│    - Specific dates → Parse and validate          │
│                                                    │
│ 5. Validation Checks:                             │
│    ✓ Start timestamp < End timestamp              │
│    ✓ End timestamp <= Current time                │
│    ✓ Range is reasonable (<= 90 days)            │
│    ✓ Convert to Unix epoch (seconds)              │
│                                                    │
│ 6. Display for user confirmation:                 │
│    "Time Range:                                    │
│     - Start: Nov 1, 2025 00:00:00 UTC             │
│     - End: Nov 30, 2025 23:59:59 UTC              │
│     - Duration: 30 days                           │
│     - Unix: 1730419200 to 1733011199"             │
└────────────────────────────────────────────────────┘

┌─ PHASE 3: PARALLEL DATA COLLECTION ───────────────┐
│ For each organization (process in parallel):      │
│                                                    │
│ 7. Organization Info:                             │
│    Call: get-org-info                             │
│    Validate: Status 200, extract name/oid         │
│    On error: Record failure, continue             │
│                                                    │
│ 8. Usage Statistics:                              │
│    Call: get-usage-stats                          │
│    Filter: Only dates in time range               │
│    Validate: 'usage' key exists                   │
│    Extract: Daily metrics for period              │
│    On error: Record failure, continue             │
│                                                    │
│ 9. Billing Details:                               │
│    Call: get-billing-details                      │
│    Validate: Status 200 (403 expected for some)   │
│    Extract: plan, status, next billing date       │
│    On 403: Note permission issue, continue        │
│    On other error: Record failure, continue       │
│                                                    │
│ 10. Sensor Inventory:                             │
│     Call: list-sensors                            │
│     Check for: resource_link (large result)       │
│     If resource_link:                             │
│       a. Download: analyze-lc-result.sh [URL]     │
│       b. Review schema output                     │
│       c. Extract: count, sample hostnames         │
│     Validate: Response structure                  │
│     On error: Record failure, continue            │
│                                                    │
│ 11. Online Sensor Status:                         │
│     Call: get-online-sensors                      │
│     Validate: Returns SID string array            │
│     Calculate: online count, offline count        │
│     On error: Mark status unavailable             │
│                                                    │
│ 12. Detection Summary:                            │
│     Call: get-historic-detections                 │
│     Params: {                                     │
│       start: [unix_timestamp],                    │
│       end: [unix_timestamp],                      │
│       limit: 5000                                 │
│     }                                             │
│     Track: retrieved_count                        │
│     Check: limit_reached = (count >= 5000)        │
│     Extract: Categories, timestamps               │
│     On error: Record failure, continue            │
│                                                    │
│ 13. D&R Rules Count:                              │
│     Call: list-dr-general-rules                   │
│     Count: Total and enabled rules                │
│     On error: Record failure, continue            │
│                                                    │
│ 14. Categorize Results:                           │
│     success_orgs = [] (all APIs succeeded)        │
│     partial_orgs = [] (some APIs failed)          │
│     failed_orgs = [] (all critical APIs failed)   │
└────────────────────────────────────────────────────┘

┌─ PHASE 4: VALIDATION & AGGREGATION ───────────────┐
│ 15. Per-Organization Data Validation:            │
│     For each successful/partial org:              │
│       ✓ Normalize all timestamps                  │
│       ✓ Verify no negative values                 │
│       ✓ Confirm dates within time range           │
│       ✓ Validate units (bytes, counts)            │
│       ✓ Check for missing critical fields         │
│                                                    │
│ 16. Multi-Org Aggregation:                       │
│     Aggregate across SUCCESSFUL orgs only:        │
│     - Sum sensor_events (from usage stats)        │
│     - Sum output_bytes_tx (convert to GB)         │
│     - Sum replay_num_evals                        │
│     - Sum peak_sensors                            │
│     - Count total sensors                         │
│     - Count total detections (track limits)       │
│                                                    │
│     Document for each aggregate:                  │
│     - Formula used                                │
│     - Orgs included count                         │
│     - Orgs excluded (and why)                     │
│     - Time range covered                          │
└────────────────────────────────────────────────────┘

┌─ PHASE 5: REPORT GENERATION ──────────────────────┐
│ 17. Report Structure:                             │
│                                                    │
│     A. HEADER (mandatory metadata)                │
│        ═══════════════════════════════════════    │
│        MSSP Comprehensive Report                  │
│        Generated: 2025-11-20 14:45:30 UTC         │
│        Time Window: Nov 1-30, 2025 (30 days)      │
│        Organizations: 45 of 50 successful         │
│        ═══════════════════════════════════════    │
│                                                    │
│     B. EXECUTIVE SUMMARY                          │
│        - High-level metrics (successful orgs)     │
│        - Critical warnings and alerts             │
│        - Failed organization count                │
│        - Detection limit warnings                 │
│                                                    │
│     C. AGGREGATE METRICS                          │
│        Total Across 45 Organizations              │
│        (Excluded: 5 orgs - see failures section)  │
│                                                    │
│        - Total Sensor Events: 1,250,432,100       │
│          Calculation: Sum of daily sensor_events  │
│          from Nov 1-30, 2025                      │
│                                                    │
│        - Total Data Output: 3,847 GB              │
│          (4,128,394,752,000 bytes)                │
│          Calculation: Sum of daily output_bytes_tx│
│          ÷ 1,073,741,824                          │
│                                                    │
│        - Peak Sensors: 12,450                     │
│          Calculation: Sum of max peak_sensors     │
│                                                    │
│     D. PER-ORGANIZATION DETAILS                   │
│        For each successful organization:          │
│                                                    │
│        ── Client ABC ─────────────────────────    │
│        OID: c7e8f940-1234-5678-abcd-...           │
│        Data Retrieved: 2025-11-20 14:45:35 UTC    │
│                                                    │
│        Usage Statistics (Nov 1-30, 2025):         │
│          - Sensor Events: 42,150,000              │
│          - Data Output: 125 GB (134,217,728,000 B)│
│          - D&R Evaluations: 1,200,450             │
│          - Peak Sensors: 250                      │
│                                                    │
│        Sensor Inventory:                          │
│          - Total Sensors: 250                     │
│          - Online: 245 (98%)                      │
│          - Offline: 5 (2%)                        │
│          - Platforms: Windows (150), Linux (100)  │
│                                                    │
│        Detection Summary:                         │
│          Retrieved: 5,000 detections              │
│          ⚠️ LIMIT REACHED - actual count higher   │
│          Top Categories:                          │
│            - suspicious_process: 1,250            │
│            - network_threat: 890                  │
│            - malware: 450                         │
│                                                    │
│        Billing Status:                            │
│          - Plan: Enterprise                       │
│          - Status: Active ✓                       │
│          - Next Billing: Dec 1, 2025              │
│          - Invoice: [URL]                         │
│                                                    │
│     E. FAILED ORGANIZATIONS SECTION               │
│        ⚠️ FAILED ORGANIZATIONS (5 of 50)          │
│                                                    │
│        Client XYZ (oid: c7e8f940-...)             │
│          Status: ❌ Failed                        │
│          Error: 403 Forbidden                     │
│          Endpoint: get-billing-details            │
│          Reason: Insufficient billing permissions │
│          Impact: Billing data unavailable         │
│          Available: Usage stats, sensor inventory │
│          Action: Grant billing:read permission    │
│          Timestamp: 2025-11-20 14:32:15 UTC       │
│                                                    │
│     F. DETECTION LIMIT WARNINGS                   │
│        ⚠️ Organizations at Detection Limit:       │
│                                                    │
│        15 of 45 organizations exceeded the 5,000  │
│        detection limit. Actual counts are higher. │
│                                                    │
│        Organizations affected:                    │
│          - Client A: 5,000 retrieved ⚠️           │
│          - Client B: 5,000 retrieved ⚠️           │
│          - [... 13 more]                          │
│                                                    │
│        Recommendation: For complete detection     │
│        data, narrow time ranges or query specific │
│        date ranges for these organizations.       │
│                                                    │
│     G. METHODOLOGY SECTION                        │
│        Data Sources:                              │
│          - list-user-orgs: Organization discovery │
│          - get-usage-stats: Daily metrics         │
│          - get-billing-details: Subscription info │
│          - list-sensors: Endpoint inventory       │
│          - get-online-sensors: Real-time status   │
│          - get-historic-detections: Security data │
│          - list-dr-general-rules: Custom rules    │
│                                                    │
│        Query Parameters:                          │
│          - Detection limit: 5,000 per org         │
│          - Time range: Nov 1-30, 2025             │
│          - Date filtering: Applied to usage stats │
│                                                    │
│        Calculations:                              │
│          - Bytes to GB: value ÷ 1,073,741,824     │
│          - Aggregations: Sum across successful    │
│            organizations only                     │
│          - Timestamps: Normalized from mixed      │
│            seconds/milliseconds format            │
│                                                    │
│        Data Freshness:                            │
│          - Usage stats: Daily (24hr delay)        │
│          - Detections: Near real-time (5min)      │
│          - Sensor status: Real-time               │
│          - Billing: Updated on changes (~1hr)     │
│                                                    │
│     H. FOOTER                                     │
│        ═══════════════════════════════════════    │
│        Report completed: 2025-11-20 14:50:15 UTC  │
│        Execution time: 4 minutes 45 seconds       │
│                                                    │
│        For questions or issues:                   │
│        Contact: support@limacharlie.io            │
│                                                    │
│        Disclaimer: Usage metrics shown are from   │
│        LimaCharlie APIs. For billing and pricing, │
│        refer to individual organization invoices. │
│        ═══════════════════════════════════════    │
└────────────────────────────────────────────────────┘

Progress Reporting During Execution:
  Display progress as orgs are processed:

  "Generating MSSP Report for 50 Organizations...

   [1/50] Client ABC... ✓ Success (2.3s)
   [2/50] Client XYZ... ✓ Success (1.8s)
   [3/50] Client PDQ... ⚠️ Billing permission denied
   [4/50] Client RST... ✓ Success (2.1s)
   [5/50] Client MNO... ❌ Failed: 500 Server Error
   ...
   [50/50] Client ZZZ... ✓ Success (1.9s)

   Collection Complete:
     ✓ Successful: 45 organizations
     ⚠️ Partial: 2 organizations (some data unavailable)
     ❌ Failed: 3 organizations

   Generating report structure..."
```

### Pattern 2: Billing-Focused Summary Report

**User Request Examples:**
- "Billing summary for all customers this month"
- "Show me subscription status across organizations"
- "Usage report for invoicing"

**Focused Data Collection:**
```
1. list-user-orgs
2. For each org (parallel):
   - get-org-info (metadata)
   - get-usage-stats (filter to month)
   - get-billing-details (plan, status)
   - get-org-invoice-url (direct link)

3. Skip (not billing-relevant):
   - Historic detections
   - D&R rules
   - Detailed sensor list

4. Report Focus:
   - Usage metrics per org (NO cost calculations)
   - Subscription status
   - Invoice links
   - Billing issues flagged
```

### Pattern 3: Single Organization Deep Dive

**User Request Examples:**
- "Detailed report for Client ABC"
- "Complete security analysis for organization XYZ"
- "Show me everything for [org name]"

**Enhanced Data Collection:**
```
1. Get OID from name (list-user-orgs + filter)
2. Collect comprehensive data:
   - All standard metrics
   - Individual sensor details (not just count)
   - Detection breakdown by rule
   - Sensor health by platform
   - Offline sensor investigation
   - Output configuration details

3. Deep analysis:
   - Per-platform sensor statistics
   - Top detection categories with context
   - Stale sensor identification
   - D&R rule coverage analysis

4. More detailed sections:
   - Individual sensor list
   - Detection timeline
   - Rule effectiveness metrics
```

## Validation Checkpoints

AI must validate at these critical points:

### Before API Calls
```
✓ OID is valid UUID format (not org name)
✓ Timestamps are reasonable (start < end, not future)
✓ Limit values are positive integers
✓ Date ranges <= 90 days (warn if larger)
```

### After API Response
```
✓ Status code is 2xx (200-299)
✓ Response body structure matches expected schema
✓ Required fields present
✓ Check for resource_link (large result handling)
```

### Before Calculations
```
✓ Data types correct (numbers are numbers)
✓ Values within expected ranges
✓ No division by zero
✓ No negative values where impossible
✓ Timestamps pass sanity checks
```

### Before Presenting Data
```
✓ All numbers formatted with thousand separators
✓ Units clearly labeled (GB, bytes, count, etc.)
✓ Timestamps in consistent format (UTC)
✓ Warnings included where required
✓ Metadata sections complete
```

## Common Mistakes to Avoid

Based on previous implementation learnings:

### ❌ Detection Data Mistakes
```
WRONG: detection['rule_name']
RIGHT: detection.get('source_rule', detection.get('cat', 'unknown'))

WRONG: detection['severity']
RIGHT: Severity not in detection records - only in D&R rule config
```

### ❌ Timestamp Mistakes
```
WRONG: Assuming all timestamps are seconds
RIGHT: Check magnitude, normalize if > 10000000000 (milliseconds)

WRONG: Ignoring invalid timestamps
RIGHT: Validate range (2020-01-01 to now+1day), flag invalid
```

### ❌ Sensor Status Mistakes
```
WRONG: last_seen field
RIGHT: alive field (datetime string format)

WRONG: Estimating offline duration
RIGHT: Parse alive timestamp, calculate exact hours/days
```

### ❌ Platform Mistakes
```
WRONG: Showing raw numeric codes without context
RIGHT: Pattern analysis + sample hostnames

Example:
  WRONG: "Platform: 2415919104 (30 sensors)"
  RIGHT: "Platform: LimaCharlie Extensions (code: 2415919104)
          Sample hostnames: ext-strelka-01, ext-hayabusa-02
          Sensor count: 30"
```

### ❌ Usage Stats Mistakes
```
WRONG: Using all 90 days from API without filtering
RIGHT: Filter to requested time range only

WRONG: Showing only GB
RIGHT: Show both - "450 GB (483,183,820,800 bytes)"

WRONG: Calculating costs
RIGHT: Show usage only, link to invoice for costs
```

### ❌ Multi-Org Aggregation Mistakes
```
WRONG: Including failed orgs in totals
RIGHT: Sum successful orgs only, document exclusions

WRONG: "Total detections: 75,000"
RIGHT: "Total retrieved: 75,000 (15 orgs hit 5K limit - actual higher)"
```

## Error Handling Reference

### Error Severity Levels

**CRITICAL** (Stop entire report):
- User authentication failure
- list-user-orgs fails (can't discover orgs)
- No organizations accessible

**HIGH** (Skip org, document prominently):
- 403 Forbidden on critical endpoints
- 500 Internal Server Error (after retry)
- Invalid OID format

**MEDIUM** (Use fallback, note in report):
- Sensor list unavailable
- Detection query timeout
- Empty result sets

**LOW** (Note in methodology):
- resource_link handling (normal for large results)
- Pagination required
- Data freshness >24hr

### Error Response Template

```json
{
  "org_oid": "c7e8f940-...",
  "org_name": "Client ABC",
  "endpoint": "get-billing-details",
  "error_type": "403 Forbidden",
  "error_message": "Insufficient permissions",
  "timestamp": "2025-11-20T14:45:30Z",
  "impact": "Billing details unavailable",
  "remediation": "Grant billing:read permission",
  "severity": "HIGH",
  "retry_attempted": false,
  "partial_data_available": true,
  "partial_data_sections": ["usage", "sensors", "detections"]
}
```

## Report Quality Checklist

Before presenting any report, verify:

### ✓ Header Completeness
- [ ] Generation timestamp (UTC)
- [ ] Time window start/end (UTC)
- [ ] Duration in days
- [ ] Success/failure org counts

### ✓ Data Accuracy
- [ ] All timestamps normalized
- [ ] Units clearly labeled
- [ ] No cost calculations
- [ ] Detection limits flagged
- [ ] Aggregations documented

### ✓ Error Transparency
- [ ] Failed orgs listed with details
- [ ] Error codes and messages shown
- [ ] Impact statements clear
- [ ] Remediation actions provided

### ✓ Methodology Documentation
- [ ] API endpoints listed
- [ ] Query parameters documented
- [ ] Calculation formulas shown
- [ ] Data freshness stated
- [ ] Exclusions explained

### ✓ Warnings Present
- [ ] Detection limit warnings
- [ ] Partial data notices
- [ ] Permission issues flagged
- [ ] Data freshness alerts

## Example Output Snippets

### Executive Summary Example
```
═══════════════════════════════════════════════════════════
MSSP Comprehensive Report - November 2025

Generated: 2025-11-20 14:45:30 UTC
Time Window: 2025-11-01 00:00:00 UTC to 2025-11-30 23:59:59 UTC
Duration: 30 days
Organizations Processed: 45 of 50 (90% success rate)
═══════════════════════════════════════════════════════════

EXECUTIVE SUMMARY

Fleet Overview:
  • Total Sensors: 12,450 (across 45 successful organizations)
  • Online: 11,823 (95%)
  • Offline: 627 (5%)

Security Activity:
  • Detections Retrieved: 127,450
  • ⚠️ 15 organizations hit detection limit (actual counts higher)
  • Top Categories: suspicious_process (32%), network_threat (28%)

Usage Metrics (45 organizations):
  • Total Events: 1,250,432,100
  • Data Output: 3,847 GB
  • D&R Evaluations: 45,230,890

Issues Requiring Attention:
  ⚠️ 5 organizations failed (see Failures section)
  ⚠️ 15 organizations exceeded detection limits
  ⚠️ 627 sensors offline (5% of fleet)
```

### Failed Organization Example
```
⚠️ FAILED ORGANIZATIONS (5 of 50)

─────────────────────────────────────────────────────────
Organization: Client XYZ Security Operations
OID: c7e8f940-aaaa-bbbb-cccc-ddddeeeeffffggg
Status: ❌ Partial Failure
─────────────────────────────────────────────────────────

Failed Endpoint: get-billing-details
  Error Code: 403 Forbidden
  Error Message: Insufficient permissions to access billing data
  Timestamp: 2025-11-20 14:32:15 UTC

Impact:
  ✗ Billing details unavailable
  ✗ Subscription status unknown
  ✗ Invoice link unavailable
  ✗ Next billing date unknown

Available Data:
  ✓ Organization metadata
  ✓ Usage statistics (Nov 1-30, 2025)
  ✓ Sensor inventory (125 sensors)
  ✓ Detection summary (1,847 detections)
  ✓ D&R rules configuration

Action Required:
  Grant the following permission to this organization:
  • Permission: billing:read
  • Scope: Organization level
  • Required Role: Admin or Owner

  Without this permission, billing data will remain unavailable
  in future reports for this organization.

Data Inclusion:
  ✓ Usage metrics INCLUDED in aggregate totals
  ✗ Billing status EXCLUDED from billing summaries
─────────────────────────────────────────────────────────
```

### Detection Limit Warning Example
```
⚠️ DETECTION LIMIT WARNINGS

The following organizations exceeded the 5,000 detection retrieval
limit. Actual detection counts are higher than shown.

Organizations Affected (15 of 45):

  Client ABC Corp
    Retrieved: 5,000 detections ⚠️ LIMIT REACHED
    Time Range: Nov 1-30, 2025 (30 days)
    Actual Count: Unknown (exceeds 5,000)
    Recommendation: Query in 7-day increments for complete data

  Client XYZ Industries
    Retrieved: 5,000 detections ⚠️ LIMIT REACHED
    Time Range: Nov 1-30, 2025 (30 days)
    Actual Count: Unknown (exceeds 5,000)
    Recommendation: Query in 7-day increments for complete data

  [... 13 more organizations]

Impact on Report:
  • Detection counts shown are MINIMUM values
  • Actual totals across all organizations are higher
  • Category distributions may be skewed (sample bias)
  • Aggregate detection count is underreported

Recommendations:
  1. For complete data, narrow time ranges:
     - Instead of 30 days, query 7-day periods
     - Aggregate results manually

  2. Filter by category for targeted analysis:
     - Query specific categories separately
     - Combine results for complete picture

  3. Consider increasing limit (max: 50,000):
     - Higher limits increase API response time
     - May hit other infrastructure limits
```

## Support and Troubleshooting

### Common Issues

**Issue**: "Too many organizations to process"
- **Solution**: Filter to subset, or process in batches
- **Workaround**: Generate multiple reports for org groups

**Issue**: "Detection limit hit for all orgs"
- **Solution**: Narrow time range (30 days → 7 days)
- **Workaround**: Query by week, aggregate manually

**Issue**: "Billing permission errors"
- **Solution**: Grant billing:read to organizations
- **Workaround**: Generate usage-only reports

**Issue**: "Large sensor list timing out"
- **Solution**: Use resource_link pattern with analyze script
- **Workaround**: Extract summary only (count, platforms)

### Getting Help

For issues with this skill:
1. Verify authentication and permissions
2. Check API endpoint availability
3. Validate time ranges and parameters
4. Review error messages for specific guidance
5. Contact LimaCharlie support: support@limacharlie.io

## Skill Maintenance

This skill should be updated when:
- New LimaCharlie API endpoints become available
- Data structure changes in API responses
- New reporting requirements emerge
- Additional guardrails needed based on issues

Last Updated: 2025-11-20
Version: 1.0.0
