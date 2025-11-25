
# Delete Output

This skill deletes an output configuration from a LimaCharlie organization. Deleting an output immediately stops data export to that destination.

## When to Use

Use this skill when the user needs to:
- Remove an output configuration
- Stop data export to a destination
- Disable syslog forwarding
- Stop S3 or cloud storage archiving
- Remove webhooks or integrations
- Clean up unused or test outputs
- Reconfigure an output (delete then recreate with new settings)
- Reduce data volume or costs

Common scenarios:
- "Delete the syslog output named prod-syslog"
- "Remove the S3 archive output"
- "Stop sending detections to the webhook"
- "Disable the Slack notification output"
- "I need to reconfigure the output - delete it first"

## What This Skill Does

This skill calls the LimaCharlie API to delete an output configuration. Once deleted, data will no longer be exported to that destination. The deletion is immediate and cannot be undone - the output configuration must be recreated if needed again.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the output to delete

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact output name (case-sensitive)
3. Confirmation that the user wants to delete (data export will stop)

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_output",
  parameters={
    "oid": "[organization-id]",
    "name": "output-name"
  }
)
```

**API Details:**
- Tool: `delete_output`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Name of the output to delete

### Step 3: Handle the Response

The API returns a response with:
```json
{}
```

**Success:**
- Output is deleted immediately
- Data export to this destination stops
- Response body is typically empty or contains a success confirmation
- The output name is now available for reuse

**Common Errors:**
- **404 Not Found**: Output with this name doesn't exist - verify the exact name
- **403 Forbidden**: Insufficient permissions - user needs write access to organization configuration
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Confirm deletion with output name
- Remind user that:
  - Data export has stopped immediately
  - The deletion cannot be undone
  - Output configuration must be recreated if needed again
  - Any buffered data may be lost
- Suggest:
  - Verify data has stopped flowing to the destination
  - Check if a replacement output is needed
  - Monitor for any alerts that depended on this output

## Example Usage

### Example 1: Delete a syslog output

User request: "Delete the syslog output named prod-syslog"

Steps:
1. Confirm output name: "prod-syslog"
2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "prod-syslog"
  }
)
```

Expected response:
```json
{}
```

Format output:
```
Successfully deleted output "prod-syslog"

The syslog output has been removed and data export has stopped.
Events are no longer being forwarded to the syslog destination.

To recreate this output, use the add-output skill with the desired configuration.
```

### Example 2: Delete before reconfiguration

User request: "I need to change the S3 bucket for the archive output. Delete it first."

Steps:
1. Confirm this is the right approach (outputs must be deleted and recreated to modify)
2. Get the output name from user or list-outputs
3. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "s3-archive"
  }
)
```

Expected response:
```json
{}
```

Format output:
```
Successfully deleted output "s3-archive"

The S3 archive output has been removed.
You can now create a new output with the updated bucket configuration.

Would you like me to create the new output with the new bucket?
```

### Example 3: Output not found error

User request: "Delete the output named test-webhook"

Steps:
1. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_output",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "test-webhook"
  }
)
```

Expected response:
```json
{
  "error": "Output not found"
}
```

Format output:
```
Error: Output "test-webhook" not found.

The output may have already been deleted or the name might be incorrect.
Output names are case-sensitive.

Would you like me to list all outputs to see what's configured?
```

## Additional Notes

- Deletion is immediate and cannot be undone
- Data export stops as soon as the output is deleted
- Any buffered or pending data may be lost
- Output names become available for reuse after deletion
- To modify an output configuration, must delete and recreate
- Consider checking list-outputs first to verify the exact output name
- Output names are case-sensitive - must match exactly
- Deleting an output does not delete historical data already exported
- Related skills: `list_outputs` to see configured outputs, `add_output` to create new outputs
- For temporary disabling, consider creating with restrictive filters instead of deleting

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/output.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/outputs.go`
