---
name: get-org-invoice-url
description: Get downloadable invoice URL or detailed invoice data for a specific month from a LimaCharlie organization. Supports multiple formats including PDF download URLs, JSON invoice objects, CSV data, or simplified JSON. Use this skill when retrieving billing invoices, preparing financial reports, or auditing monthly charges.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get Organization Invoice URL

Retrieve invoice information or download URL for a specific billing period from a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Download invoices for accounting or record-keeping
- Review detailed billing line items for a specific month
- Prepare financial reports or expense summaries
- Audit monthly charges and usage-based billing
- Export invoice data for accounting systems
- Verify billing amounts and breakdowns

Common scenarios:
- Monthly financial closing and reporting
- Expense tracking and budget reconciliation
- Tax preparation and documentation
- Audit trails for billing history
- Dispute resolution for billing questions
- Integration with accounting software

## What This Skill Does

This skill retrieves invoice information for a specific billing period from a LimaCharlie organization. It calls the LimaCharlie billing API to get either a download URL for the invoice PDF or detailed invoice data in various formats (JSON, CSV). The response format depends on the optional format parameter.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **year**: Invoice year (required, e.g., 2023)
- **month**: Invoice month (required, 1-12)

Optional parameters:
- **format**: Response format (optional)
  - Omit or empty string = PDF download URL (default)
  - "json" = Full Stripe Invoice object with all details
  - "simple_json" = Simplified line items array
  - "simple_csv" = CSV format invoice data

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid year (2000-3000 range)
3. Valid month (1-12)
4. Optional format choice based on need

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="billing",
  method="GET",
  path="/orgs/[oid]/invoice_url/[year]/[month]?format=[format]"
)
```

**API Details:**
- Endpoint: `billing` (uses billing.limacharlie.io)
- Method: `GET`
- Path: `/orgs/{oid}/invoice_url/{year}/{month}` (month zero-padded to 2 digits)
- Query parameters:
  - `format` (optional): "json", "simple_json", "simple_csv", or omit for URL
- Body fields: None

### Step 3: Handle the Response

The API returns different structures based on format:

**Default (URL format):**
```json
{
  "status_code": 200,
  "body": {
    "url": "https://invoice-download-url.stripe.com/..."
  }
}
```

**JSON format:**
```json
{
  "status_code": 200,
  "body": {
    "invoice": {
      "id": "in_1234567890",
      "amount_due": 500000,
      "currency": "usd",
      "lines": [...],
      "period_start": 1640995200,
      "period_end": 1643673600
    }
  }
}
```

**Simple JSON format:**
```json
{
  "status_code": 200,
  "body": {
    "lines": [
      {
        "description": "Enterprise Plan",
        "amount": 400000,
        "quantity": 1
      },
      {
        "description": "Additional Sensors",
        "amount": 100000,
        "quantity": 500
      }
    ]
  }
}
```

**Success (200-299):**
- URL format returns downloadable link (expires after time)
- JSON formats return detailed invoice structure
- Amounts are typically in cents (divide by 100 for dollars)
- Simple formats easier to parse and display

**Common Errors:**
- **400 Bad Request**: Invalid year/month values
- **403 Forbidden**: Insufficient permissions - requires admin/owner access
- **404 Not Found**: No invoice exists for specified month (org may not have been billed yet)
- **500 Server Error**: Billing API issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- For URL format: Provide download link with expiration note
- For JSON formats: Parse and display line items clearly
- Convert amounts from cents to dollars
- Show billing period and total amount
- Format dates in readable format
- Highlight any credits or adjustments

## Example Usage

### Example 1: Get invoice download link

User request: "Get me the invoice for January 2023"

Steps:
1. Extract organization ID
2. Call API for invoice URL:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="billing",
  method="GET",
  path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/invoice_url/2023/01"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "url": "https://pay.stripe.com/invoice/acct_123/invst_456/pdf?s=ap"
  }
}
```

Present to user:
```
Invoice Download Link - January 2023

Your invoice is ready for download:
🔗 https://pay.stripe.com/invoice/acct_123/invst_456/pdf?s=ap

Note: This link expires after a few hours for security.
Download the PDF now for your records.

Organization: c7e8f940-1234-5678-abcd-1234567890ab
Period: January 2023
```

### Example 2: Get detailed invoice breakdown

User request: "Show me the detailed charges for December 2023"

Steps:
1. Call API with simple_json format:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="billing",
  method="GET",
  path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/invoice_url/2023/12?format=simple_json"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "lines": [
      {
        "description": "Enterprise Plan - Base",
        "amount": 400000,
        "quantity": 1
      },
      {
        "description": "Sensors (2,500 sensors)",
        "amount": 150000,
        "quantity": 2500
      },
      {
        "description": "Data Storage (800 GB)",
        "amount": 50000,
        "quantity": 800
      }
    ],
    "total": 600000
  }
}
```

Present to user:
```
Invoice Details - December 2023

Line Items:
1. Enterprise Plan - Base
   Quantity: 1
   Amount: $4,000.00

2. Sensors (2,500 sensors)
   Quantity: 2,500
   Amount: $1,500.00

3. Data Storage (800 GB)
   Quantity: 800 GB
   Amount: $500.00

Total Amount: $6,000.00

This invoice reflects your usage during December 2023.
```

### Example 3: Export for accounting system

User request: "Export the last 3 months of invoices in CSV format"

Steps:
1. Loop through last 3 months
2. Get each invoice in CSV format
3. Combine or present separately

Present summary:
```
Invoice Export Complete

Exported 3 months of billing data:

✓ October 2023 - $5,800.00
✓ November 2023 - $6,100.00
✓ December 2023 - $6,000.00

Total (Q4 2023): $17,900.00

CSV data is ready for import into your accounting system.
Each file contains itemized line items with descriptions, quantities, and amounts.
```

## Additional Notes

- Invoice URLs expire after a short period (hours) for security
- Download PDFs immediately if needed for records
- Invoices are typically available 2-3 days after month end
- Amounts in API responses are usually in cents (USD)
- JSON format provides full Stripe invoice object with all metadata
- Simple formats are easier to parse for custom reporting
- CSV format is ideal for spreadsheet imports
- No invoice exists for current/future months
- Contact support for billing adjustments or corrections
- This is a read-only operation - no billing changes made

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/billing.go` (GetBillingInvoiceURL function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterGetOrgInvoiceURL)
