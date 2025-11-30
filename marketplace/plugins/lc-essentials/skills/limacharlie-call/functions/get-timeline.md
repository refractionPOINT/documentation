
# Get Timeline

Retrieve a specific timeline from LimaCharlie's Timeline Hive by name.

## When to Use

Use this skill when the user needs to:
- Retrieve a saved investigation timeline
- Review timeline data before updating
- Check the current state of an investigation
- Export timeline data for reporting
- Merge new findings with existing timeline data

Common scenarios:
- "Get the timeline for incident-2024-001"
- "Show me the ransomware investigation timeline"
- "Retrieve the current state of this investigation"
- "What's in the timeline named 'phishing-attack'?"

## What This Skill Does

This skill retrieves a timeline record from LimaCharlie's Timeline Hive by its name. It returns the complete timeline data including events, detections, entities, notes, and metadata.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.

- **oid**: Organization ID (required)
- **timeline_name**: Name of the timeline to retrieve (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact timeline name

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "incident-2024-001"
  }
)
```

**Tool Details:**
- Tool name: `get_timeline`
- Parameters:
  - `oid`: Organization ID (required)
  - `timeline_name`: Name of the timeline to retrieve (required)

### Step 3: Handle the Response

The tool returns:
```json
{
  "timeline": {
    "name": "incident-2024-001",
    "data": {
      "name": "Ransomware Investigation",
      "description": "...",
      "status": "in_progress",
      "priority": "critical",
      "events": [...],
      "detections": [...],
      "entities": [...],
      "notes": [...],
      "summary": "..."
    },
    "enabled": true,
    "tags": ["ransomware", "critical"],
    "comment": "Active investigation",
    "metadata": {
      "created_at": 1700000000,
      "created_by": "user@example.com",
      "last_mod": 1700100000,
      "last_author": "analyst@example.com",
      "guid": "abc-123-def"
    }
  }
}
```

**Success:**
- Returns complete timeline with data and metadata
- Includes creation and modification timestamps
- Shows who created and last modified the timeline

**Common Errors:**
- **404 Not Found**: Timeline with the specified name does not exist
- **403 Forbidden**: Insufficient permissions
- **400 Bad Request**: Invalid parameters

### Step 4: Format the Response

Present the result to the user:
- Display timeline name and status
- Show summary if available
- List event, detection, and entity counts
- Show investigation notes
- Display metadata (created/modified timestamps)

**Example output:**
```
Timeline: incident-2024-001
Status: in_progress | Priority: critical

Summary: Ransomware attack detected on DESKTOP-001. Initial access via phishing.

Contents:
- Events: 5
- Detections: 3
- Entities: 4
- Notes: 7

Created: 2024-01-20 by user@example.com
Last Modified: 2024-01-21 by analyst@example.com
```

## Example Usage

### Example 1: Retrieve investigation timeline

User request: "Get the timeline for the ransomware investigation"

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "ransomware-investigation-2024"
  }
)
```

### Example 2: Get timeline before updating

User request: "I need to add new findings to the existing timeline"

Steps:
1. Get the existing timeline
2. Merge new data with existing
3. Use `set_timeline` to save combined data

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="get_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "existing-incident"
  }
)
```

Then merge the returned data with new findings and call `set_timeline`.

## Additional Notes

- Timeline names are case-sensitive
- Use `list_timelines` first if you don't know the exact name
- The returned data contains references (atoms, detection IDs), not full event data
- Use `expand_timeline` to get full event and detection data hydrated
- Metadata shows audit trail (who created/modified and when)
- Related skills: `list_timelines` to find timelines, `set_timeline` to update, `expand_timeline` to hydrate

## Related Functions

- `list_timelines` - List all timelines in the organization
- `set_timeline` - Create or update a timeline
- `delete_timeline` - Delete a timeline
- `expand_timeline` - Hydrate timeline with full event/detection data

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

- **Config Hive Documentation**: [Config Hive: Timeline](../../../../../docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-timeline.md)
- **MCP Implementation**: `../lc-mcp-server/internal/tools/hive/timelines.go`
