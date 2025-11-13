---
name: unsubscribe-from-extension
description: Unsubscribe a LimaCharlie organization from an extension to disable its functionality. Use this skill when users need to deactivate, disable, or remove extensions from their organization. Unsubscribing stops the extension from processing data and removes its functionality. Use with caution as this may impact security monitoring, integrations, or data collection.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Unsubscribe from Extension

Unsubscribes a LimaCharlie organization from an extension, disabling its functionality.

## When to Use

Use this skill when the user needs to:
- Unsubscribe from an extension to deactivate it
- Disable an extension in their organization
- Remove an extension capability
- Stop an extension from processing data
- Decommission an extension

Common scenarios:
- "Unsubscribe from the threat-intel extension"
- "Disable the artifact-collection extension"
- "Remove the logging extension from my organization"
- "Deactivate the custom-integration extension"

## What This Skill Does

This skill unsubscribes an organization from a LimaCharlie extension by sending a DELETE request to the subscriptions API. Once unsubscribed, the extension is deactivated and stops processing events, providing integrations, or delivering functionality. The extension configuration (if any) remains in the Hive and can be used if you re-subscribe later.

**Warning:** Unsubscribing may impact security monitoring, data collection, or integrations. Ensure this is the intended action before proceeding.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **extension_name**: The name of the extension to unsubscribe from (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Extension name (string, must match currently subscribed extension)
3. Verify the extension is currently subscribed
4. Consider warning the user about impact of unsubscribing

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/orgs/[organization-id]/subscription/extension/[extension-name]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/orgs/{oid}/subscription/extension/{extension_name}`
  - Replace `{oid}` with the organization ID
  - Replace `{extension_name}` with the URL-encoded extension name
- Query parameters: None
- Body: None (DELETE requests have no body)

**Important:**
- The extension name must be URL-encoded if it contains special characters
- The API may take up to 60 seconds to complete as it deprovisions resources
- Timeout is set to 1 minute for this operation

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Unsubscription was successful
- The extension is now inactive in the organization
- The extension is no longer processing data
- Extension configuration remains in Hive (can be deleted separately if desired)
- Inform the user that unsubscription is complete

**Common Errors:**
- **400 Bad Request**: Invalid extension name
- **403 Forbidden**: Insufficient permissions - user needs platform_admin role
- **404 Not Found**: Extension doesn't exist, not subscribed, or already unsubscribed
- **500 Server Error**: Backend deprovisioning issue - advise user to retry or contact support
- **504 Gateway Timeout**: Extension deprovisioning took too long - check if unsubscription completed

### Step 4: Format the Response

Present the result to the user:
- Confirm the extension unsubscription was successful
- Show the extension name
- Note that the extension is now inactive
- Warn about potential impact (e.g., lost functionality, data collection stopped)
- Note that extension configuration is preserved if they want to re-subscribe
- Suggest using delete-extension-config if they want to remove the configuration too

## Example Usage

### Example 1: Unsubscribe from an extension

User request: "Unsubscribe from the threat-intel extension"

Steps:
1. Get the organization ID from context
2. Use extension name "threat-intel"
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/subscription/extension/threat-intel"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

Inform user: "Successfully unsubscribed from the threat-intel extension. The extension is now inactive and will no longer process threat intelligence data. The extension configuration remains saved if you want to re-subscribe later."

### Example 2: Handle not subscribed

User request: "Unsubscribe from the logging extension"

Steps:
1. Attempt to unsubscribe
2. Receive 404 Not Found error
3. Inform user: "Your organization is not currently subscribed to the logging extension. It may have already been unsubscribed or was never subscribed."

### Example 3: Complete removal

User request: "Completely remove the artifact-collection extension"

Steps:
1. First, unsubscribe from the extension (this skill)
2. Then, delete the configuration with delete-extension-config
3. Confirm both operations completed successfully
4. Inform user that extension is fully removed

## Additional Notes

- **Unsubscription vs Configuration**: These are separate operations:
  - Unsubscription deactivates the extension
  - Configuration remains in Hive unless explicitly deleted
  - Can re-subscribe later and configuration will be reused
- **Impact Assessment**: Consider impact before unsubscribing:
  - Will security detections stop?
  - Will integrations break?
  - Will data collection cease?
- **Immediate Effect**: Once unsubscribed, the extension stops processing immediately
- **Billing**: Unsubscribing may reduce charges for paid extensions
- **No Data Loss**: Historical data collected by extension is preserved
- **Re-subscription**: Can re-subscribe anytime using subscribe-to-extension
- **Configuration Preservation**: Extension configuration in Hive is NOT deleted automatically
- **API Keys**: Extension-specific API keys may be revoked upon unsubscription
- **Deprovisioning Time**: Extension deactivation may take a few seconds to complete
- **Organization Level**: Extensions are unsubscribed at the organization level
- **Audit Trail**: Unsubscription is logged in organization audit logs
- **Related Operations**:
  - To remove configuration too: use delete-extension-config after unsubscribing
  - To re-activate: use subscribe-to-extension
  - To temporarily disable: consider disabling the configuration instead (set enabled: false)

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/extension.go` (UnsubscribeFromExtension method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/extensions.go`
