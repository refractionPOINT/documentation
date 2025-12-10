---
name: reporting
description: Generate template-based reports from LimaCharlie. Uses JSON templates to define report structure and calls MCP tools directly for data collection. Supports billing reports with single-tenant or multi-tenant scope. Never fabricates data.
allowed-tools:
  - mcp__plugin_lc-essentials_limacharlie__lc_call_tool
  - Read
  - Bash
  - Task
---

# LimaCharlie Reporting

Template-driven reporting system for LimaCharlie data. Each report type has a JSON template defining inputs, outputs, and data sources.

---

## Available Report Templates

| Template | Description | Scope |
|----------|-------------|-------|
| `billing-report` | Invoice-focused billing data | single / all |

Templates are located in `skills/reporting/templates/`.

---

## Billing Report

Generate invoice-based billing reports for one or all organizations.

### Required Input

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | integer | Invoice year (e.g., 2025) |
| `month` | integer | Invoice month (1-12) |

### Optional Input

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scope` | string | `all` | `single` = one org, `all` = all accessible orgs |
| `oid` | uuid | - | Organization ID (required when scope=single) |
| `format` | string | `markdown` | Output format: `json` or `markdown` |

### Usage Examples

**All organizations:**
```
"Generate billing report for November 2025"
"Billing summary for all orgs, month 11 year 2025"
```

**Single organization:**
```
"Billing report for Acme Corp, November 2025"
"Invoice details for org c7e8f940-..., month 11, year 2025"
```

---

## Workflow: Single Organization

When `scope=single` or user specifies a single org:

### Step 1: Resolve OID

If user provides org name instead of OID:

```
tool: list_user_orgs
parameters: {}
```

Match org name to get OID.

### Step 2: Fetch Invoice Data

```
tool: get_org_invoice_url
parameters:
  oid: [uuid]
  year: [year]
  month: [month]
  format: simple_json
```

**Response:**
```json
{
  "lines": [
    { "description": "Enterprise Plan", "amount": 400000, "quantity": 1 },
    { "description": "Sensors (2500)", "amount": 150000, "quantity": 2500 }
  ],
  "total": 550000
}
```

### Step 3: Fetch Invoice URL (Optional)

```
tool: get_org_invoice_url
parameters:
  oid: [uuid]
  year: [year]
  month: [month]
```

Returns PDF download URL.

### Step 4: Transform Data

1. **Convert amounts from cents to dollars**: `amount / 100`
2. **Map to output schema**:

```json
{
  "metadata": {
    "generated_at": "2025-12-09T10:30:00Z",
    "period": "November 2025",
    "scope": "single"
  },
  "data": {
    "tenants": [
      {
        "name": "Acme Corp",
        "oid": "c7e8f940-...",
        "status": "success",
        "cost": 5500.00,
        "currency": "usd",
        "skus": [
          { "description": "Enterprise Plan", "amount": 4000.00, "quantity": 1 },
          { "description": "Sensors (2500)", "amount": 1500.00, "quantity": 2500 }
        ],
        "invoice_url": "https://..."
      }
    ]
  },
  "warnings": [],
  "errors": []
}
```

### Step 5: Output Report

Format as JSON or Markdown based on user preference.

---

## Workflow: All Organizations

When `scope=all` or user asks for "all orgs":

### Step 1: Get Organization List

```
tool: list_user_orgs
parameters: {}
```

### Step 2: Spawn Parallel Collectors

For EACH organization, spawn a `billing-collector` agent IN PARALLEL using a single message with multiple Task calls:

```
Task(subagent_type="lc-essentials:billing-collector", prompt="
  Collect billing data for org 'Acme Corp' (OID: uuid-1)
  Year: 2025, Month: 11
  Return JSON matching billing-report template schema
")

Task(subagent_type="lc-essentials:billing-collector", prompt="
  Collect billing data for org 'Beta Inc' (OID: uuid-2)
  Year: 2025, Month: 11
  Return JSON matching billing-report template schema
")

// ... all orgs in ONE message for parallel execution
```

### Step 3: Aggregate Results

Collect JSON responses from all agents:

1. **Combine tenant data** into `data.tenants` array
2. **Separate errors** into `errors` array
3. **Calculate rollup**:
   - `total_cost`: Sum of all successful tenant costs
   - `total_tenants`: Count of all tenants
   - `successful_count`: Tenants with status=success
   - `failed_count`: Tenants with status=error or no_invoice

### Step 4: Output Report

**JSON Output:**
```json
{
  "metadata": {
    "generated_at": "2025-12-09T10:30:00Z",
    "period": "November 2025",
    "scope": "all",
    "tenant_count": 5
  },
  "data": {
    "tenants": [...],
    "rollup": {
      "total_cost": 25500.00,
      "total_tenants": 5,
      "successful_count": 4,
      "failed_count": 1
    }
  },
  "warnings": [],
  "errors": [
    {
      "org_name": "Failed Corp",
      "oid": "...",
      "error_message": "403 Forbidden - Insufficient permissions"
    }
  ]
}
```

**Markdown Output:**
```markdown
## Billing Report - November 2025

**Generated:** 2025-12-09 10:30:00 UTC
**Scope:** All Organizations (5 total)

### Summary

| Metric | Value |
|--------|-------|
| Total Cost | $25,500.00 |
| Successful | 4 |
| Failed | 1 |

### Per-Tenant Breakdown

| Tenant | Status | Cost | Line Items |
|--------|--------|------|------------|
| Acme Corp | success | $5,500.00 | 2 |
| Beta Inc | success | $8,000.00 | 3 |
| Gamma LLC | success | $7,000.00 | 2 |
| Delta Co | success | $5,000.00 | 2 |
| Failed Corp | error | - | - |

### Errors

| Tenant | Error |
|--------|-------|
| Failed Corp | 403 Forbidden - Insufficient permissions |
```

---

## Data Integrity Rules

### NEVER Fabricate Data

- Only report data returned by APIs
- Missing data = `null` or `"N/A"`
- Failed calls = documented in `errors` array
- NEVER estimate, infer, or guess values

### Currency Conversion

API returns amounts in **cents**. Always convert:

```
amount_dollars = amount_cents / 100
```

Example: `550000` cents → `$5,500.00`

### Error Handling

| Error | Status | Action |
|-------|--------|--------|
| 403 Forbidden | `error` | "Insufficient permissions - requires admin/owner role" |
| 404 Not Found | `no_invoice` | "No invoice exists for this period" |
| Other | `error` | Include error details |

Partial success is valid - report what succeeded, document what failed.

---

## Output Formats

### JSON

Raw structured data matching template schema. Use for:
- Programmatic consumption
- Piping to other tools
- Further processing

### Markdown

Formatted tables for terminal display. Use for:
- Human review
- Quick summaries
- Copy/paste to reports

---

## Template Reference

Template file: `skills/reporting/templates/billing-report.json`

The template defines:
- **Input schema**: Required and optional parameters
- **Output schema**: Expected JSON structure
- **Data sources**: Which API calls populate each field

Read the template for full schema details.
