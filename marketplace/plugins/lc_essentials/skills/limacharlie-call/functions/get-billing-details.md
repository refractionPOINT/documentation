
# Get Billing Details

Retrieve comprehensive billing information and configuration for a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Review billing and subscription information
- Check payment method and billing contact
- Verify subscription plan and status
- Troubleshoot billing or payment issues
- Prepare for plan changes or upgrades
- Audit billing configuration

Common scenarios:
- Reviewing billing before plan upgrades
- Troubleshooting failed payments
- Verifying billing contact information
- Checking subscription renewal dates
- Preparing for budget planning
- Auditing organization costs

## What This Skill Does

This skill retrieves detailed billing information for a LimaCharlie organization. It calls the LimaCharlie billing API to get subscription details, payment method information, billing contact, and account status.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are required.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Appropriate permissions (billing access typically requires admin/owner role)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="billing",
  method="GET",
  path="/orgs/[oid]/details"
)
```

**API Details:**
- Endpoint: `billing` (uses billing.limacharlie.io)
- Method: `GET`
- Path: `/orgs/{oid}/details`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "plan": "enterprise",
    "status": "active",
    "billing_email": "billing@example.com",
    "payment_method": "card",
    "next_billing_date": 1640995200,
    "subscription_id": "sub_1234567890"
  }
}
```

**Success (200-299):**
- Response contains comprehensive billing details
- Includes plan type, subscription status, and payment info
- Shows billing contact and next billing date
- May include payment method details (card, invoice, etc.)

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view billing details - requires admin/owner access
- **404 Not Found**: Organization or billing details not found
- **500 Server Error**: Billing API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display subscription plan and status
- Show billing contact information
- Include next billing/renewal date
- Highlight payment method (without sensitive details)
- Note any billing warnings or issues
- Suggest actions if status is not active

## Example Usage

### Example 1: Review billing configuration

User request: "Show me our billing details"

Steps:
1. Extract organization ID from context
2. Call billing API to get details:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="billing",
  method="GET",
  path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/details"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "plan": "enterprise",
    "status": "active",
    "billing_email": "billing@acme.com",
    "payment_method": "card",
    "last_four": "4242",
    "next_billing_date": 1672531200,
    "auto_renew": true
  }
}
```

Present to user:
```
Billing Details

Subscription:
- Plan: Enterprise
- Status: Active ✓
- Auto-renewal: Enabled

Billing Contact:
- Email: billing@acme.com

Payment Method:
- Type: Credit Card
- Last 4 digits: 4242
- Status: Valid ✓

Next Billing:
- Date: January 1, 2023
- Auto-payment: Enabled

Everything looks good! Your subscription is active and configured correctly.
```

### Example 2: Troubleshoot billing issue

User request: "Why did our payment fail?"

Steps:
1. Get billing details to check status
2. Identify any issues or warnings
3. Provide troubleshooting guidance

Present findings:
```
Billing Status Check

⚠️ Issue Detected

Subscription: Enterprise
Status: Payment Failed
Error: Card declined

Last Attempted Payment:
- Date: December 15, 2023
- Amount: $5,000
- Result: Failed

Recommended Actions:
1. Update payment method with valid card
2. Verify billing email is correct
3. Check with your bank for card issues
4. Contact support if problem persists

Current Access:
- Services remain active for 7 days grace period
- Update payment by December 22 to avoid interruption
```

## Additional Notes

- Billing details require admin or owner permissions
- Sensitive payment information (full card numbers) is never returned
- Billing API uses separate endpoint (billing.limacharlie.io)
- Subscription status affects service availability
- Grace periods may apply for failed payments
- Contact LimaCharlie support for billing changes
- Payment method updates must be done through web console
- This is a read-only operation - no billing changes made
- Always verify billing contact email for important notifications

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/billing.go` (GetBillingOrgDetails function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterGetBillingDetails)
