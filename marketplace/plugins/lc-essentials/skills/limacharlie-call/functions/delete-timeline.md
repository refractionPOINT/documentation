
# Delete Timeline

Delete a timeline from LimaCharlie's Timeline Hive.

## When to Use

Use this skill when the user needs to:
- Remove an old or completed investigation timeline
- Delete a test timeline
- Clean up duplicate timelines
- Remove a timeline created in error

Common scenarios:
- "Delete the timeline named 'test-investigation'"
- "Remove the old incident timeline"
- "Clean up the duplicate timeline"
- "Delete timeline 'incident-2024-001'"

## What This Skill Does

This skill permanently deletes a timeline record from LimaCharlie's Timeline Hive. This action cannot be undone - the timeline and all its data (events, detections, entities, notes) will be permanently removed.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.

- **oid**: Organization ID (required)
- **timeline_name**: Name of the timeline to delete (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact timeline name to delete
3. **Confirm with user** before deleting - this action is irreversible

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="delete_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "test-timeline"
  }
)
```

**Tool Details:**
- Tool name: `delete_timeline`
- Parameters:
  - `oid`: Organization ID (required)
  - `timeline_name`: Name of the timeline to delete (required)

### Step 3: Handle the Response

The tool returns:
```json
{
  "success": true,
  "message": "Successfully deleted timeline 'test-timeline'"
}
```

**Success:**
- Timeline is permanently deleted
- Cannot be recovered after deletion

**Common Errors:**
- **404 Not Found**: Timeline with the specified name does not exist
- **403 Forbidden**: Insufficient permissions
- **400 Bad Request**: Invalid parameters

### Step 4: Format the Response

Present the result to the user:
- Confirm successful deletion
- Remind that this action was permanent

**Example output:**
```
Successfully deleted timeline 'test-timeline'.

Note: This action is permanent. The timeline and all associated data have been removed.
```

## Example Usage

### Example 1: Delete test timeline

User request: "Delete the test timeline I created"

Steps:
1. **Confirm with user**: "Are you sure you want to delete timeline 'test-timeline'? This cannot be undone."
2. After confirmation, call the API:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="delete_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "test-timeline"
  }
)
```

### Example 2: Clean up old investigation

User request: "Remove the closed investigation timeline from last month"

Steps:
1. Use `list_timelines` to find the exact name
2. Confirm with user before deletion
3. Delete the timeline

## Additional Notes

- **Deletion is permanent** - there is no undo or recovery
- Always confirm with user before deleting
- Consider exporting timeline data before deletion if needed for records
- Timeline names are case-sensitive
- Use `list_timelines` to verify the exact name before deleting
- The underlying events and detections in LimaCharlie are NOT deleted - only the timeline record
- Related skills: `list_timelines` to find timelines, `get_timeline` to review before deleting

## Related Functions

- `list_timelines` - List all timelines in the organization
- `get_timeline` - Get a specific timeline by name
- `set_timeline` - Create or update a timeline
- `expand_timeline` - Hydrate timeline with full event/detection data

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../../CALLING_API.md).

- **Config Hive Documentation**: [Config Hive: Timeline](../../../../../docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-timeline.md)
- **MCP Implementation**: `../lc-mcp-server/internal/tools/hive/timelines.go`
