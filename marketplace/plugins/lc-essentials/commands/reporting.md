---
description: Generate reports from LimaCharlie data with visualization. Usage: /lc-essentials:reporting
---

# Report Generation Wizard

You MUST complete all 3 steps in order before generating any report:
1. **Report Type** - Ask which report to generate
2. **Time Period** - Ask which period (NEVER assume a default)
3. **Scope** - Ask which organizations to include

Do NOT skip any step. Do NOT assume defaults for time period.

---

## Step 1: Report Type (MANDATORY)

IMMEDIATELY call AskUserQuestion - do NOT output any text first:

questions=[{"question": "Which report would you like to generate?", "header": "Report", "options": [{"label": "Billing Summary", "description": "Monthly billing with roll-up totals and per-tenant SKU breakdown (Recommended)"}, {"label": "Fleet Health", "description": "Sensor status, platform distribution, and detection activity"}, {"label": "Detection Analytics", "description": "Detection volume, severity breakdown, and category analysis"}, {"label": "Customer Health", "description": "Health scores with sensor coverage and attention items"}], "multiSelect": false}]

## Step 2: Time Period (MANDATORY - DO NOT SKIP)

After Step 1 response, you MUST call AskUserQuestion for time period. Never assume a default period:

questions=[{"question": "What time period should the report cover?", "header": "Period", "options": [{"label": "Previous month", "description": "Most recent completed month (Recommended for billing)"}, {"label": "Current month", "description": "Current month to date (may be incomplete)"}, {"label": "Custom date range", "description": "I'll specify the year and month"}], "multiSelect": false}]

IMPORTANT: You must wait for the user to select a time period before proceeding. Do NOT assume "current billing period" or any default.

If "Custom date range" is selected, call AskUserQuestion with year and month questions:

questions=[{"question": "Which year?", "header": "Year", "options": [{"label": "2025", "description": "Current year"}, {"label": "2024", "description": "Previous year"}], "multiSelect": false}, {"question": "Which month?", "header": "Month", "options": [{"label": "January", "description": "Month 1"}, {"label": "February", "description": "Month 2"}, {"label": "March", "description": "Month 3"}, {"label": "April", "description": "Month 4"}, {"label": "May", "description": "Month 5"}, {"label": "June", "description": "Month 6"}, {"label": "July", "description": "Month 7"}, {"label": "August", "description": "Month 8"}, {"label": "September", "description": "Month 9"}, {"label": "October", "description": "Month 10"}, {"label": "November", "description": "Month 11"}, {"label": "December", "description": "Month 12"}], "multiSelect": false}]

## Step 3: Scope (MANDATORY)

After Step 2 response (and custom date if applicable), call AskUserQuestion for scope:

questions=[{"question": "Which organizations should be included?", "header": "Scope", "options": [{"label": "All organizations", "description": "Generate report for all accessible orgs (Recommended)"}, {"label": "Specific organizations", "description": "I'll select which orgs to include"}], "multiSelect": false}]

If "Specific organizations" is selected:
1. Load the lc-essentials:limacharlie-call skill
2. Call list_user_orgs to get available organizations
3. Present a multi-select AskUserQuestion with the org names and OIDs

After all selections are complete, display this summary:

## Report Configuration

| Setting | Value |
|---------|-------|
| **Report** | {selected_report} |
| **Period** | {selected_period} |
| **Scope** | {scope_description} |

Then execute the report based on the selected type:

## Billing Summary Report Execution

1. Calculate billing period using bash:
   - Previous month: YEAR=$(date -d "last month" +%Y) MONTH=$(date -d "last month" +%-m)
   - Current month: YEAR=$(date +%Y) MONTH=$(date +%-m)

2. Load the lc-essentials:limacharlie-call skill

3. Call list_user_orgs to get all organizations

4. For each organization, call get_org_invoice_url with parameters:
   - oid: the organization's OID
   - year: the billing year
   - month: the billing month
   - format: "simple_json"

5. Aggregate results into billing-summary.json schema:
   - report_metadata: title, generated_at, period (month_name, year, display)
   - summary: total_billing, total_sensors, avg_cost_per_sensor, active_tenants
   - tenants: array with name, oid, region, sensors, monthly_cost, cost_per_sensor, percentage_of_total, status, line_items

6. Load the lc-essentials:graphic-output skill and render using template "billing-summary"

7. Open the generated HTML file with: xdg-open /tmp/billing-report-{month}-{year}.html

## Fleet Health Report Execution

1. Calculate timestamps using bash:
   - END_TS=$(date +%s)
   - START_TS based on selected period

2. Load the lc-essentials:limacharlie-call skill

3. Call list_user_orgs

4. For each organization:
   - Call list_sensors to get sensor inventory
   - Call get_historic_detections with start/end timestamps
   - Calculate online/offline from last_seen timestamps

5. Aggregate into fleet-health.json schema

6. Load lc-essentials:graphic-output skill and render using template "fleet-health"

7. Open: xdg-open /tmp/fleet-health-{days}d.html

## Detection Analytics Report Execution

1. Calculate timestamps using bash

2. Load lc-essentials:limacharlie-call skill

3. Call list_user_orgs

4. For each organization:
   - Call get_historic_detections
   - Extract categories and severity from detection metadata

5. Aggregate into detection-analytics.json schema

6. Load lc-essentials:graphic-output skill and render using template "detection-analytics"

7. Open: xdg-open /tmp/detection-analytics-{days}d.html

## Customer Health Report Execution

1. Calculate timestamps using bash

2. Load lc-essentials:limacharlie-call skill

3. Call list_user_orgs

4. For each organization:
   - Call list_sensors
   - Call get_historic_detections
   - Calculate health score (online/total * 100)
   - Classify: healthy >= 90%, warning 70-89%, critical < 70%

5. Aggregate into customer-health.json schema

6. Load lc-essentials:graphic-output skill and render using template "customer-health"

7. Open: xdg-open /tmp/customer-health-{days}d.html
