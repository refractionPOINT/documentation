
# Get SKU Definitions

Retrieve pricing information and SKU definitions for all LimaCharlie services, plans, and features.

## When to Use

Use this skill when the user needs to:
- Review available service plans and pricing
- Understand costs for different features
- Plan budgets for new deployments
- Compare plan tiers and capabilities
- Calculate estimated costs for scaling
- Evaluate add-on services and pricing

Common scenarios:
- Planning new LimaCharlie deployments
- Budgeting for organization expansion
- Comparing plan options before upgrade
- Understanding usage-based pricing
- Evaluating cost of additional features
- Preparing procurement requests

## What This Skill Does

This skill retrieves SKU definitions and pricing information for LimaCharlie services. It calls the LimaCharlie billing API to get the complete catalog of available plans, features, add-ons, and their associated costs. This is a global query that doesn't require a specific organization context.

## Required Information

Before calling this skill, gather:

**⚠️ NOTE**: This is a **global operation** that queries the pricing catalog and does not require a specific organization ID. When calling the API, **omit the `oid` parameter** entirely.

No specific parameters required (global pricing query)

## How to Use

### Step 1: Validate Parameters

This is a global query - no specific validation required.

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  endpoint="billing",
  method="GET",
  path="/sku"
  # Note: oid parameter omitted - not required for global operations
)
```

**API Details:**
- Endpoint: `billing` (uses billing.limacharlie.io)
- Method: `GET`
- Path: `/sku`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "skus": {
      "enterprise_base": {
        "name": "Enterprise Plan - Base",
        "price": 400000,
        "currency": "usd",
        "interval": "month",
        "description": "Enterprise tier base subscription"
      },
      "sensor_unit": {
        "name": "Additional Sensor",
        "price": 60,
        "currency": "usd",
        "interval": "month",
        "description": "Per-sensor monthly charge"
      },
      "storage_gb": {
        "name": "Data Storage",
        "price": 62,
        "currency": "usd",
        "interval": "month",
        "unit": "GB",
        "description": "Per-GB monthly storage"
      }
    }
  }
}
```

**Success (200-299):**
- Response contains comprehensive SKU catalog
- Each SKU includes name, price, currency, billing interval
- Prices typically in cents (divide by 100 for dollars)
- Descriptions explain what each SKU provides
- May include usage-based and subscription-based items

**Common Errors:**
- **403 Forbidden**: Insufficient permissions (rare for this endpoint)
- **500 Server Error**: Billing API issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Group SKUs by category (plans, sensors, storage, features)
- Convert prices from cents to dollars
- Show billing intervals (monthly, annually, usage-based)
- Explain what each SKU includes
- Highlight popular or recommended options
- Provide cost examples for common scenarios

## Example Usage

### Example 1: Review available plans and pricing

User request: "What are the LimaCharlie pricing options?"

Steps:
1. Call API to get SKU definitions:
```
mcp__limacharlie__lc_api_call(
  endpoint="billing",
  method="GET",
  path="/sku"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "skus": {
      "community": {
        "name": "Community Plan",
        "price": 0,
        "interval": "month"
      },
      "enterprise": {
        "name": "Enterprise Plan",
        "price": 400000,
        "interval": "month"
      },
      "sensor": {
        "name": "Sensor Unit",
        "price": 60,
        "interval": "month"
      }
    }
  }
}
```

Present to user:
```
LimaCharlie Pricing Plans

Base Plans:
1. Community Plan
   Cost: Free
   Billing: Monthly
   Best for: Testing and small deployments

2. Enterprise Plan
   Cost: $4,000/month base
   Billing: Monthly
   Best for: Production deployments with full features

Usage-Based Pricing:
- Sensors: $0.60 per sensor/month
- Data Storage: $0.62 per GB/month
- Additional features priced separately

Example Total Cost (1,000 sensors):
- Base Plan: $4,000/month
- 1,000 Sensors: $600/month
- Storage (100GB): $62/month
- Total: ~$4,662/month

Contact sales for volume discounts and custom pricing.
```

### Example 2: Calculate cost for planned expansion

User request: "How much will it cost to add 500 more sensors?"

Steps:
1. Get SKU definitions to find sensor pricing
2. Calculate additional cost
3. Provide breakdown

Present analysis:
```
Expansion Cost Analysis

Current: 1,000 sensors
Planned: 1,500 sensors (+500)

Sensor Pricing:
- Cost per sensor: $0.60/month
- Additional sensors: 500
- Monthly increase: $300

Annual Impact:
- Monthly: +$300
- Annually: +$3,600

This is just the sensor cost. Consider also:
- Additional data storage needs
- Increased API usage
- Any feature add-ons required

Total estimated monthly increase: $300-400
```

## Additional Notes

- **This is a global operation that does not require a specific organization ID**
- When calling the API, omit the `oid` parameter entirely
- This endpoint doesn't require organization context
- SKU prices are in cents (USD typically)
- Pricing may vary by region or contract
- Volume discounts may be available (contact sales)
- Some SKUs are usage-based, others are flat-rate
- Enterprise agreements may have custom pricing
- Prices shown are list prices (before discounts)
- Currency and intervals specified per SKU
- Pricing subject to change - verify with LimaCharlie sales
- Custom plans and features may not appear in standard SKU list

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (GetSKUDefinitions via GenericGETRequest)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterGetSKUDefinitions)
