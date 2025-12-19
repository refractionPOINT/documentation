
# List Timelines

List all timelines in a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- See all investigation timelines in the organization
- Find a specific timeline by browsing available timelines
- Get an overview of ongoing and completed investigations
- Audit timeline usage across the organization
- Find timelines by tags

Common scenarios:
- "Show me all timelines in this organization"
- "List all investigation timelines"
- "What timelines do we have?"
- "Find timelines tagged with 'ransomware'"
- "Show me all active investigations"

## What This Skill Does

This skill retrieves all timeline records from LimaCharlie's Investigation Hive for the specified organization. It returns timeline names along with their metadata (status, tags, creation info).

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.

- **oid**: Organization ID (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_timelines",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

**Tool Details:**
- Tool name: `list_timelines`
- Parameters:
  - `oid`: Organization ID (required)

### Step 3: Handle the Response

The tool returns:
```json
{
  "timelines": {
    "incident-2024-001": {
      "data": {
        "name": "Ransomware Investigation",
        "status": "in_progress",
        "priority": "critical",
        ...
      },
      "enabled": true,
      "tags": ["ransomware", "critical"],
      "comment": "Active investigation",
      "metadata": {
        "created_at": 1700000000,
        "created_by": "user@example.com",
        "last_mod": 1700100000,
        "last_author": "analyst@example.com"
      }
    },
    "phishing-incident-2024": {
      ...
    }
  },
  "count": 2
}
```

**Success:**
- Returns all timelines with their data and metadata
- Count indicates total number of timelines
- Each timeline includes status, priority, tags, and audit info

**Common Errors:**
- **403 Forbidden**: Insufficient permissions
- **500 Server Error**: Service issue

### Step 4: Format the Response

Present the result to the user:
- Show total count of timelines
- List timelines with key info (name, status, priority)
- Group by status if helpful (in_progress, closed, etc.)
- Show tags for filtering

**Example output:**
```
Found 5 timelines in organization:

IN PROGRESS (2):
1. ransomware-server01-2024
   Priority: critical | Tags: ransomware, critical
   Last modified: 2024-01-21 by analyst@example.com

2. phishing-investigation-q1
   Priority: high | Tags: phishing, email
   Last modified: 2024-01-20 by security@example.com

CLOSED (3):
3. malware-desktop05-2024
   Status: closed_true_positive | Priority: medium
   Closed: 2024-01-15

4. false-positive-alert-123
   Status: closed_false_positive | Priority: low
   Closed: 2024-01-10

5. test-timeline
   Status: closed_true_positive | Priority: informational
   Closed: 2024-01-05
```

## Example Usage

### Example 1: List all timelines

User request: "Show me all investigation timelines"

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_timelines",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

### Example 2: Find specific timeline

User request: "I'm looking for the ransomware investigation timeline"

Steps:
1. List all timelines
2. Filter results for ransomware-related names or tags
3. Present matching timelines

## Additional Notes

- Returns all timelines regardless of status
- Filter results client-side by status, priority, or tags
- Timeline data in list is the same as stored (not expanded)
- Use `get_timeline` for a single timeline with full data
- Use `expand_timeline` to hydrate with full event/detection data
- Related skills: `get_timeline` to retrieve one, `set_timeline` to create/update, `delete_timeline` to remove

## Related Functions

- `get_timeline` - Get a specific timeline by name
- `set_timeline` - Create or update a timeline
- `delete_timeline` - Delete a timeline
- `expand_timeline` - Hydrate timeline with full event/detection data

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../../CALLING_API.md).

- **Config Hive Documentation**: [Config Hive: Investigation](../../../../../docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-investigation.md)
- **MCP Implementation**: `../lc-mcp-server/internal/tools/hive/timelines.go`
