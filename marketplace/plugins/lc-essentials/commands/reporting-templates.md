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

**Data Collection** (reporting skill):
- List all organizations
- Per-org:
  - Invoice line items via `get_org_invoice_url` with `format: "simple_json"`
  - SKU names, quantities, and amounts (converted from cents to dollars)
  - Subscription status and billing details
  - Sensor counts for context
- Aggregate roll-up:
  - Total cost across all tenants (only from orgs with billing data)
  - Total sensors across all tenants
  - Average cost per sensor (blended rate)

**CRITICAL: Billing Data Availability**

Organizations may not have billing data available for several reasons:
- **Missing `billing.ctrl` permission**: API key lacks billing access
- **No invoice for period**: Organization has no invoice for the requested month/year
- **API error**: Temporary or permanent API access issue

**NEVER show `$0` for organizations where billing data is unavailable.** This falsely implies zero usage when the actual usage is unknown.

Each tenant in the data structure MUST include:
```json
{
  "name": "<org-name>",
  "sensors": <count>,
  "cost": <amount-or-null>,
  "billing_available": <true|false>,
  "billing_error": "<error-reason-if-unavailable>",
  "status": "active|billing_unavailable|draft"
}
```

**Visualization** (graphic-output skill):
- **Executive Summary Roll-Up Cards**:
  - Total Monthly Billing (only tenants with billing data)
  - Total Sensors (all tenants)
  - Average Cost/Sensor (blended rate from available data)
  - Active Tenant Count (with billing data available)
- **Distribution Charts**:
  - Pie chart: Cost distribution by tenant (only those with data)
  - Pie chart: Sensor distribution by tenant
- **Per-Tenant Breakdown Table**:
  - Organization name
  - Region
  - Sensor count
  - Monthly cost (or "—" if unavailable)
  - Cost per sensor (or "—" if unavailable)
  - Percentage of total (or "—" if unavailable)
  - Status: `Active`, `Billing Unavailable`, `Draft`, or `No Usage`
- **Detailed SKU Breakdown by Tenant**:
  - Cards for tenants WITH billing data showing SKU line items
  - Summary card for tenants WITHOUT billing data listing each org and reason
- **Cost by Category** (if SKUs can be categorized):
  - Bar chart of spending by SKU category

**Time Range**: Prompt user for billing period (year and month). This is passed to `get_org_invoice_url` to retrieve the correct invoice.

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
3. **Collect Data**: Spawn `org-reporter` agents in parallel to collect data from each organization
   - For billing reports: Include billing period (year, month) in the prompt so agents call `get_org_invoice_url` with `format: "simple_json"`
4. **Aggregate Results**:
   - For billing reports: Calculate roll-up totals (total cost, total sensors, avg cost/sensor)
   - Structure data per the `billing-summary.json` schema
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
- Do NOT use `xdg-open` directly on HTML files as it may open in a text editor instead of a browser depending on system configuration

## Example Conversation Flow

```
User: /lc-essentials:reporting-templates

Assistant: [Presents template menu]

User: MSSP Executive Summary

Assistant: [Confirms time range, collects data via reporting skill, generates HTML via graphic-output skill]

Assistant: Your MSSP Executive Summary is ready! Opening in browser...

[Browser opens with the report at http://localhost:<port>/mssp-executive-summary-<YYYY-MM-DD>.html]
```
