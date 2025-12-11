---
description: Pre-defined report templates combining data collection and visualization. Usage: /lc-essentials:reporting-templates
---

# Reporting Templates

Present the user with a menu of pre-defined report templates. Each template combines the `reporting` skill (data collection) with the `graphic-output` skill (HTML visualization).

## Instructions

Use the `AskUserQuestion` tool to present the template menu:

```
AskUserQuestion(
  questions=[{
    "question": "Which report template would you like to generate?",
    "header": "Template",
    "options": [
      {"label": "Monthly Billing Report", "description": "Usage statistics and billing data for customer invoicing with roll-up totals"},
      {"label": "MSSP Executive Report", "description": "High-level fleet health overview with sensor status and detection activity"},
      {"label": "Detection Analytics Report", "description": "Detection volume, categories, severity breakdown across tenants"},
      {"label": "Customer Health Report", "description": "Comprehensive customer health with sensor coverage and attention items"}
    ],
    "multiSelect": false
  }]
)
```

## Template Definitions

### Template: Monthly Billing Report

**Purpose**: Comprehensive billing data with roll-up totals and per-tenant SKU breakdown for customer invoicing.

**Data Collection** (reporting skill):
- List all organizations
- Per-org:
  - Invoice line items via `get_org_invoice_url` with `format: "simple_json"`
  - SKU names, quantities, and amounts (converted from cents to dollars)
  - Subscription status and billing details
  - Sensor counts for context
- Aggregate roll-up:
  - Total cost across all tenants
  - Total sensors across all tenants
  - Average cost per sensor (blended rate)

**Visualization** (graphic-output skill):
- **Executive Summary Roll-Up Cards**:
  - Total Monthly Billing (all tenants combined)
  - Total Sensors (all tenants)
  - Average Cost/Sensor (blended rate)
  - Active Tenant Count
- **Distribution Charts**:
  - Pie chart: Cost distribution by tenant
  - Pie chart: Sensor distribution by tenant
- **Per-Tenant Breakdown Table**:
  - Organization name
  - Region
  - Sensor count
  - Monthly cost
  - Cost per sensor
  - Percentage of total
  - Status (active/draft/no usage)
- **Detailed SKU Breakdown by Tenant**:
  - Expandable cards for each tenant
  - Each SKU line item with name, quantity, amount
  - Progress bar showing percentage of total cost
- **Cost by Category** (if SKUs can be categorized):
  - Bar chart of spending by SKU category

**Time Range**: Prompt user for billing period (year and month). This is passed to `get_org_invoice_url` to retrieve the correct invoice.

**Output**: `/tmp/billing-report-{month}-{year}.html`

**Template Used**: `billing-summary` (uses billing-summary.html.j2)

**JSON Schema**: `billing-summary.json`

---

### Template: MSSP Executive Report

**Purpose**: High-level fleet health overview for MSSP leadership - sensor status, detection activity, and per-org health.

**Data Collection** (reporting skill):
- Use template: `mssp-executive-report.json`
- List all organizations
- Per-org:
  - Sensor inventory via `list_sensors`
  - Detection counts via `get_historic_detections` (last N days)
  - Calculate online/offline counts from last_seen timestamps
- Aggregate roll-up:
  - Total sensors (online/offline)
  - Fleet health percentage
  - Total detections
  - Detection limit flags

**Visualization** (graphic-output skill):
- **Summary Cards**:
  - Total Sensors
  - Online Sensors
  - Fleet Health %
  - Total Detections
- **Distribution Charts**:
  - Platform distribution donut chart
  - Organization health bar chart
- **Top Categories**: Bar chart of top detection categories
- **Per-Organization Table**:
  - Organization name, sensors, online, offline, health %, detections, status
  - LIMIT badge for orgs at detection limit

**Time Range**: Prompt user for time window (7, 14, or 30 days).

**Output**: `/tmp/fleet-health-{days}d.html`

**Template Used**: `fleet-health` (uses fleet-health.html.j2)

**JSON Schema**: `fleet-health.json`

---

### Template: Detection Analytics Report

**Purpose**: Detection volume, categories, severity breakdown, and trends across tenants for security analysis.

**Data Collection** (reporting skill):
- Use template: `detection-analytics-report.json`
- List all organizations
- Per-org:
  - Detection data via `get_historic_detections` (last N days)
  - Extract categories from source_rule or cat field
  - Extract severity from detection metadata
  - Identify top hosts by detection count
- Aggregate roll-up:
  - Total detections across all tenants
  - Severity breakdown (critical/high/medium/low/info)
  - Top categories across all tenants
  - Detection limit tracking

**Visualization** (graphic-output skill):
- **Summary Cards**:
  - Total Detections
  - Tenants with Detections
  - Tenants at Limit
  - Critical Severity Count
- **Severity Distribution**: Stacked bar showing severity breakdown
- **Top Categories**: Horizontal bar chart
- **Top Tenants**: Horizontal bar chart by detection volume
- **Per-Tenant Table**:
  - Tenant name, detection count, critical, high, medium counts
  - Category pills, LIMIT badges
  - Status column

**Time Range**: Prompt user for time window (7, 14, or 30 days).

**Output**: `/tmp/detection-analytics-{days}d.html`

**Template Used**: `detection-analytics` (uses detection-analytics.html.j2)

**JSON Schema**: `detection-analytics.json`

---

### Template: Customer Health Report

**Purpose**: Comprehensive customer health combining sensor coverage, detection activity, and health metrics for customer success tracking.

**Data Collection** (reporting skill):
- Use template: `customer-health-report.json`
- List all organizations
- Per-org:
  - Sensor inventory via `list_sensors`
  - Detection data via `get_historic_detections` (last N days)
  - Calculate health score (online/total * 100)
  - Classify health status (healthy ≥90%, warning 70-89%, critical <70%)
  - Identify attention items:
    - Offline sensors
    - Stale sensors (offline > 7 days)
    - High severity detections
    - Detection limit reached
- Aggregate roll-up:
  - Health distribution (healthy/warning/critical/inactive counts)
  - Fleet-wide health percentage
  - Attention summary

**Visualization** (graphic-output skill):
- **Attention Banner**: Critical/warning items summary
- **Summary Cards**:
  - Total Customers
  - Total Sensors (online count)
  - Fleet Health %
  - Total Detections
- **Health Distribution**: Grid showing healthy/warning/critical/inactive counts
- **Charts**:
  - Health distribution donut chart
  - Platform distribution donut chart
  - Top detection categories bar chart
- **Per-Customer Table**:
  - Customer name, health score, sensors, online, offline, detections
  - Attention badges (critical/warning)
  - Health status
- **Customers Needing Attention**: Expanded cards for flagged customers

**Time Range**: Prompt user for time window (7, 14, or 30 days).

**Output**: `/tmp/customer-health-{days}d.html`

**Template Used**: `customer-health` (uses customer-health.html.j2)

**JSON Schema**: `customer-health.json`

---

## Execution Flow

Once the user selects a template:

### For Monthly Billing Report:

1. **Confirm Billing Period**: Use `AskUserQuestion` to get the billing period
   ```
   AskUserQuestion(
     questions=[{
       "question": "Which billing period should I generate the report for?",
       "header": "Period",
       "options": [
         {"label": "Previous month", "description": "Most recent completed billing cycle"},
         {"label": "Current month", "description": "Current billing period (may be incomplete)"},
         {"label": "Specific month", "description": "I'll specify the year and month"}
       ],
       "multiSelect": false
     }]
   )
   ```
2. **Confirm Scope**: Ask if they want all orgs or a specific subset
3. **Collect Data**: Spawn `org-reporter` agents in parallel to collect billing data
4. **Aggregate Results**: Calculate roll-up totals per `billing-summary.json` schema
5. **Generate HTML**: Spawn `html-renderer` with template `billing-summary`
6. **Open in Browser**: Automatically open the generated HTML file

### For MSSP Executive, Detection Analytics, or Customer Health Reports:

1. **Confirm Time Window**: Use `AskUserQuestion` to get the time window
   ```
   AskUserQuestion(
     questions=[{
       "question": "What time window should the report cover?",
       "header": "Time Window",
       "options": [
         {"label": "Last 7 days", "description": "Recent activity overview"},
         {"label": "Last 14 days", "description": "Two-week analysis"},
         {"label": "Last 30 days", "description": "Monthly comprehensive view (Recommended)"}
       ],
       "multiSelect": false
     }]
   )
   ```
2. **Confirm Scope**: Ask if they want all orgs or a specific subset
3. **Calculate Timestamps**: Use bash to get accurate Unix timestamps
   ```bash
   date +%s                      # Current time (end)
   date -d '7 days ago' +%s      # 7 days ago (start)
   ```
4. **Collect Data**: Spawn parallel agents (one per org) to collect:
   - For MSSP Executive: sensors + detections
   - For Detection Analytics: detections with categories/severity
   - For Customer Health: sensors + detections + health metrics
5. **Aggregate Results**: Structure data per the appropriate schema:
   - MSSP Executive → `fleet-health.json`
   - Detection Analytics → `detection-analytics.json`
   - Customer Health → `customer-health.json`
6. **Generate HTML**: Spawn `html-renderer` with the appropriate template
7. **Open in Browser**: Automatically open the generated HTML file

**Browser Launch Command:**
```bash
# Option 1: Direct file open
xdg-open /tmp/{report-file}.html

# Option 2: HTTP server (if direct open fails)
cd /tmp && python3 -m http.server 8765 &
xdg-open http://localhost:8765/{report-file}.html
```

## Example Conversation Flow

```
User: /lc-essentials:reporting-templates