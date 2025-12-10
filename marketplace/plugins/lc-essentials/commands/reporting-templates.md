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
      {"label": "Monthly Billing Report", "description": "Usage statistics and billing data for customer invoicing with roll-up totals"}
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

## Execution Flow

Once the user selects a template:

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
3. **Collect Data**: Spawn `org-reporter` agents in parallel to collect data from each organization
   - Include billing period (year, month) in the prompt so agents call `get_org_invoice_url` with `format: "simple_json"`
4. **Aggregate Results**:
   - Calculate roll-up totals (total cost, total sensors, avg cost/sensor)
   - Structure data per the `billing-summary.json` schema
5. **Generate HTML**: Spawn `html-renderer` agent to create the visualization dashboard
   - Use template `billing-summary`
6. **Open in Browser**: Automatically open the generated HTML file

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