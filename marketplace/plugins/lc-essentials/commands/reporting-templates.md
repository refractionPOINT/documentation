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
      {"label": "MSSP Executive Summary", "description": "High-level metrics across all customers: sensor counts, detection volumes, SLA status"},
      {"label": "Customer Health Dashboard", "description": "Per-org health scores, offline sensors, detection trends with drill-down"},
      {"label": "Monthly Billing Report", "description": "Usage statistics and billing data for customer invoicing"},
      {"label": "Detection Analytics", "description": "Security activity breakdown: top categories, trends, alert volumes by org"}
    ],
    "multiSelect": false
  }]
)
```

## Template Definitions

### Template 1: MSSP Executive Summary

**Purpose**: High-level overview for MSSP leadership - quick health check across all customers.

**Data Collection** (reporting skill):
- List all organizations
- Per-org: sensor count (online/offline), detection count (7 days), SLA status
- Aggregate totals across fleet

**Visualization** (graphic-output skill):
- Summary cards: Total sensors, Total detections, Fleet coverage %, Orgs passing SLA
- Pie chart: Platform distribution (Windows/Linux/macOS)
- Bar chart: Top 10 orgs by detection volume
- Table: All orgs with health indicators (green/yellow/red)

**Time Range**: Default last 7 days, prompt user to confirm.

**Output**: `/tmp/mssp-executive-summary-{date}.html`

---

### Template 2: Customer Health Dashboard

**Purpose**: Operational dashboard for SOC teams - identify customers needing attention.

**Data Collection** (reporting skill):
- List all organizations
- Per-org: sensor inventory with online/offline status, detection counts by category
- Identify: offline sensors >24h, orgs below SLA, detection spikes

**Visualization** (graphic-output skill):
- Health gauge: Fleet-wide coverage percentage
- Heatmap: Org health matrix (rows=orgs, columns=metrics, color=status)
- Bar chart: Offline sensors by org
- Line chart: Detection trend (daily, last 7 days) if data available
- Alert list: Orgs requiring immediate attention

**Time Range**: Default last 7 days, prompt user to confirm.

**Output**: `/tmp/customer-health-dashboard-{date}.html`

---

### Template 3: Monthly Billing Report

**Purpose**: Comprehensive billing data with roll-up totals and per-tenant SKU breakdown for customer invoicing.

**Data Collection** (reporting skill - direct MCP calls):
- List all organizations via `list_user_orgs`
- Per-org: Invoice data via `get_org_invoice_url` with `format: "simple_json"`
- Extract: SKU names, quantities, amounts (convert cents to dollars)
- Calculate roll-ups: total cost, total sensors, avg cost/sensor

**MANDATORY Transformations**:
- Currency: API returns cents → ALWAYS divide by 100
- Region detection: Check SKU names for "CANADA", "EU", etc.
- Roll-up: Sum only from orgs with billing data available

**Visualization** (graphic-output skill):
- Summary cards: Total Monthly Billing, Total Sensors, Avg Cost/Sensor, Active Tenants
- Pie chart: Cost distribution by tenant
- Pie chart: Sensor distribution by tenant
- Table: Per-tenant breakdown (org, region, sensors, cost, cost/sensor, % of total)
- SKU cards: Detailed line items per tenant

**Time Range**: Prompt user for billing period (year and month).

**Output**: `/tmp/billing-report-{month}-{year}.html`

**Template Used**: `billing-summary` (uses billing-summary.html.j2)

---

### Template 4: Detection Analytics

**Purpose**: Security activity analysis for threat intelligence and tuning.

**Data Collection** (reporting skill):
- List all organizations
- Per-org: detections by category, top detection rules triggered
- Aggregate: fleet-wide detection categories, rule effectiveness

**Visualization** (graphic-output skill):
- Summary cards: Total detections, Unique categories, Orgs with alerts
- Pie chart: Detection categories (top 10)
- Bar chart: Detections by organization
- Table: Top triggered rules with counts
- Warning banner: Detection limits reached (if applicable)

**Time Range**: Default last 30 days, prompt user to confirm.

**Output**: `/tmp/detection-analytics-{date}.html`

---

## Execution Flow

Once the user selects a template:

1. **Confirm Time Range**: Use `AskUserQuestion` to confirm or customize the time period
   - For billing reports: Ask for specific billing period (year and month)
2. **Confirm Scope**: Ask if they want all orgs or a specific subset
3. **Collect Data**: Use direct MCP calls via `lc_call_tool` to collect data from each organization
   - For billing: `list_user_orgs` then `get_org_invoice_url` per org
   - Apply MANDATORY transformations (currency conversion, roll-ups)
4. **Build JSON**: Structure data to match the template's expected schema
5. **Generate HTML**: Spawn `html-renderer` agent to create the visualization dashboard
   - For billing reports: Use template `billing-summary`
6. **Open in Browser**: Start HTTP server and open the generated HTML file

**Browser Launch Commands:**
```bash
# Start HTTP server in /tmp (if not already running)
lsof -i :9876 || (cd /tmp && python3 -m http.server 9876 &)

# Open report in browser
xdg-open "http://localhost:9876/{report-file}.html"  # Linux
# or: open "http://localhost:9876/{report-file}.html"  # macOS
```

**Why HTTP server instead of file:// URLs:**
- Some browsers block `file://` URLs for security reasons
- Chart.js CDN loads reliably over HTTP
- Consistent behavior across all browser configurations

## Example Conversation Flow

```
User: /lc-essentials:reporting-templates

Assistant: [Presents template menu]

User: MSSP Executive Summary

Assistant: [Confirms time range, collects data via reporting skill, generates HTML via graphic-output skill]

Assistant: Your MSSP Executive Summary is ready! Opening in browser...

[Browser opens with the report at http://localhost:8765/mssp-executive-summary-2025-12-06.html]
```
