
# Remove Tag

Remove a tag from a sensor to update categorization, end investigation tracking, or clean up labels.

## When to Use

Use this skill when the user needs to:
- Remove a tag that is no longer relevant
- End investigation tracking after incident resolution
- Change sensor categorization or grouping
- Remove temporary tags before TTL expiration
- Clean up incorrect or obsolete tags
- Re-categorize sensors for different D&R rule targeting

Common scenarios:
- "Remove the 'compromised' tag from this sensor"
- "Clean up the investigation tag now that we're done"
- "Remove the 'production' tag, this server is being decommissioned"
- "Delete the temporary tag before it expires"

## What This Skill Does

This skill removes a specific tag from a sensor immediately. The tag is deleted regardless of its TTL setting, and any D&R rules or outputs that filter by this tag will no longer apply to the sensor. This is useful for updating sensor categorization and managing tag lifecycle manually rather than waiting for TTL expiration.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to remove the tag from
- **tag**: Tag name/label to remove (must match exactly, case-sensitive)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. Exact tag name to remove (case-sensitive, must match existing tag)
4. Confirm the tag currently exists on the sensor (optional but recommended)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="remove_tag",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012",
    "tag": "compromised"
  }
)
```

**Tool Details:**
- Tool name: `remove_tag`
- Required parameters:
  - `oid`: Organization ID
  - `sid`: Sensor ID
  - `tag`: Tag name to remove (case-sensitive)

### Step 3: Handle the Response

The tool returns data directly:
```json
{}
```

**Success:**
- Empty response indicates the tag was successfully removed
- The tag is immediately deleted and no longer associated with the sensor
- D&R rules targeting this tag will no longer apply to this sensor
- Outputs filtering by this tag will no longer include this sensor

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format - verify the sid is a valid UUID
- **404 Not Found**: Sensor does not exist or tag not found - verify both sid and tag name
- **403 Forbidden**: Insufficient permissions - requires sensor tag management permissions
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the tag was successfully removed from the sensor
- Explain that D&R rules targeting this tag no longer apply to the sensor
- If the tag was used for investigation tracking, note that tracking has ended
- Suggest verifying the sensor's current tags if needed
- Mention any implications for monitoring or response actions

## Example Usage

### Example 1: Remove Investigation Tag

User request: "Remove the 'compromised' tag from sensor abc12345-6789-0123-4567-890abcdef012, investigation is complete"

Steps:
1. Validate the sensor ID format (UUID)
2. Confirm the tag name is correct
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="remove_tag",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "abc12345-6789-0123-4567-890abcdef012",
    "tag": "compromised"
  }
)
```

Expected response:
```json
{}
```

Response to user:
"Successfully removed tag 'compromised' from sensor abc12345-6789-0123-4567-890abcdef012. The sensor is no longer marked as compromised, and any special monitoring or response rules targeting this tag will no longer apply. Investigation tracking for this sensor has ended."

### Example 2: Clean Up Incorrect Tag

User request: "That 'production' tag was added by mistake, remove it"

Steps:
1. Identify the sensor ID
2. Verify the tag exists on the sensor
3. Call tool to remove:
```
mcp__limacharlie__lc_call_tool(
  tool_name="remove_tag",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "sid": "def45678-90ab-cdef-0123-456789abcdef",
    "tag": "production"
  }
)
```

Expected response:
```json
{}
```

Response to user:
"The 'production' tag has been removed from sensor def45678-90ab-cdef-0123-456789abcdef. The sensor will no longer be targeted by D&R rules or outputs configured for production systems. Make sure to add the correct tag if this sensor should have a different categorization."

## Additional Notes

- Tag removal is immediate and irreversible
- Tags are case-sensitive - "Production" and "production" are different tags
- Removing a non-existent tag typically returns a 404 or succeeds silently
- This operation does not affect other tags on the sensor
- Use this to manually remove tags before their TTL expires
- D&R rules with sensor selectors using this tag will immediately stop applying to this sensor
- Outputs filtered by this tag will immediately stop including this sensor's events
- Consider the implications before removing tags used by active D&R rules
- You can verify current tags by querying sensor metadata
- This is useful for dynamic sensor categorization and fleet management
- Multiple tags can be managed independently on a single sensor
- Removing a tag does not affect historical events that were tagged

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (RemoveTag method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/response.go` (remove_tag)
