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
      {"label": "Billing Report", "description": "Invoice details, SKU breakdown, and cost analysis for a billing period"}
    ],
    "multiSelect": false
  }]
)
```

## Template Definitions

### Billing Report

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

**Time Range**: Prompt user for billing period (current month, last month, or custom year/month).

**Output**: `/tmp/billing-report-{month}-{year}.html`

**Template Used**: `billing-summary` (uses billing-summary.html.j2)

---

## Execution Flow

Once the user selects a template:

1. **Confirm Time Range**: Use `AskUserQuestion` to confirm or customize the time period

   ```
   AskUserQuestion(
     questions=[{
       "question": "Which billing period should I generate the report for?",
       "header": "Period",
       "options": [
         {"label": "Current month", "description": "Current billing period (may be incomplete)"},
         {"label": "Last month", "description": "Most recent completed billing cycle (Recommended)"},
         {"label": "Custom date range", "description": "I'll specify the year and month"}
       ],
       "multiSelect": false
     }]
   )
   ```

   If user selects "Custom date range", follow up with:
   ```
   AskUserQuestion(
     questions=[{
       "question": "Which year?",
       "header": "Year",
       "options": [
         {"label": "2025", "description": "Current year"},
         {"label": "2024", "description": "Previous year"}
       ],
       "multiSelect": false
     },
     {
       "question": "Which month?",
       "header": "Month",
       "options": [
         {"label": "January", "description": "Month 1"},
         {"label": "February", "description": "Month 2"},
         {"label": "March", "description": "Month 3"},
         {"label": "April", "description": "Month 4"}
       ],
       "multiSelect": false
     }]
   )
   ```
   Note: For months May-December, present a second question with remaining months.

2. **Confirm Scope**: Ask if they want all orgs or a specific subset
3. **Collect Data**: Spawn `org-reporter` agents in parallel to collect data from each organization
   - Include billing period (year, month) in the prompt so agents call `get_org_invoice_url` with `format: "simple_json"`
4. **Aggregate Results**:
   - Calculate roll-up totals (total cost, total sensors, avg cost/sensor)
   - Structure data per the `billing-summary.json` schema
5. **Generate HTML**: Spawn `html-renderer` agent to create the visualization dashboard
   - Use template `billing-summary`
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
Assistant: [Asks about billing period: Current month, Last month (Recommended), or Custom date range]

User: Last month

Assistant: [Collects billing data via reporting skill, generates HTML via graphic-output skill]

Assistant: Your November 2025 Billing Report is ready! Opening in browser...

[Browser opens with the report at http://localhost:9876/billing-report-11-2025.html]
```
