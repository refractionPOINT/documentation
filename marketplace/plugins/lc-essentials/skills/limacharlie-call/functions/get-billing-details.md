# get_billing_details

Retrieve billing and subscription information for an organization.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |

## Returns

```json
{
  "plan": "enterprise",
  "status": "active",
  "billing_email": "billing@example.com",
  "payment_method": "card",
  "last_four": "4242",
  "next_billing_date": 1640995200,
  "auto_renew": true
}
```

## Example

```
lc_call_tool(tool_name="get_billing_details", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
})
```

## Notes

- Requires admin/owner permissions
- Sensitive payment info (full card numbers) is never returned
- Payment method updates must be done through web console
- Subscription status affects service availability
