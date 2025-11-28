
# Expand Timeline

Expand a timeline by fetching full event and detection data for all references, transforming a lightweight timeline with atom/detection IDs into a fully hydrated timeline with complete event and detection details.

## When to Use

Use this skill when the user needs to:
- Get full event details for events referenced in a timeline
- Retrieve complete detection data for detections in a timeline
- Export a timeline with all associated data
- Review an investigation timeline with full context
- Generate reports from timeline data
- Analyze events and detections in an investigation

Common scenarios:
- "Expand the timeline to show full event details"
- "Get the complete data for all events in my investigation timeline"
- "Fetch full detection information for this timeline"
- "Hydrate timeline 'ransomware-incident-2024' with event data"
- "Show me the expanded timeline with all event and detection details"

## What This Skill Does

This skill expands a timeline by:
1. Taking either a timeline object or the name of a stored timeline
2. Fetching full event data for each event reference (using atom IDs)
3. Fetching complete detection data for each detection reference
4. Returning the timeline with all data hydrated

Timelines are investigation records that reference events and detections by ID. This function resolves those references to provide complete data.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required)

One of the following (mutually exclusive):
- **timeline**: A timeline object to expand directly
- **timeline_name**: Name of a timeline stored in Hive to fetch and expand

## Timeline Structure

For the complete timeline schema reference, see [Config Hive: Timeline](../../../../../docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-timeline.md).

Timelines can contain:
- **name**: Timeline name (required, max 256 chars)
- **description**: Timeline description (max 4096 chars)
- **status**: Investigation status (new, in_progress, pending_review, escalated, closed_false_positive, closed_true_positive)
- **priority**: Priority level (critical, high, medium, low, informational)
- **events**: Array of event references with atom, sid, tags, comments, relevance, verdict
- **detections**: Array of detection references with detection_id, tags, comments, false_positive info
- **entities**: IOCs of interest (type, value, first_seen, last_seen, verdict, comments)
- **notes**: Investigation notes (type, content, author, timestamp)
- **summary**: Executive summary (max 16384 chars)
- **conclusion**: Final conclusion (max 16384 chars)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Either a timeline object OR a timeline name (not both)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

**Option A: Expand a stored timeline by name**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="expand_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "ransomware-investigation-2024"
  }
)
```

**Option B: Expand a timeline object directly**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="expand_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline": {
      "name": "My Investigation",
      "events": [
        {"atom": "abc123", "sid": "sensor-001"}
      ],
      "detections": [
        {"detection_id": "det-456"}
      ]
    }
  }
)
```

**Tool Details:**
- Tool name: `expand_timeline`
- Parameters:
  - `oid`: Organization ID (required)
  - `timeline_name`: Name of stored timeline (mutually exclusive with timeline)
  - `timeline`: Timeline object to expand (mutually exclusive with timeline_name)

### Step 3: Handle the Response

The tool returns an expanded timeline with full event and detection data:

```json
{
  "name": "ransomware-investigation-2024",
  "status": "in_progress",
  "priority": "critical",
  "events": [
    {
      "atom": "abc123",
      "sid": "sensor-001",
      "event": {
        "TIMESTAMP": 1705761234567,
        "EVENT_TYPE": "NEW_PROCESS",
        "COMMAND_LINE": "powershell.exe -encodedCommand ...",
        "FILE_PATH": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "PARENT_PROCESS_ID": 1234
      },
      "routing": {
        "hostname": "SERVER01",
        "arch": "x64",
        "plat": "windows"
      },
      "tags": ["initial_access"],
      "relevance": "First suspicious process execution",
      "verdict": "malicious"
    }
  ],
  "detections": [
    {
      "detection_id": "det-456",
      "detect": {
        "event": {...},
        "routing": {...}
      },
      "detect_mtd": {
        "rule_name": "Encoded PowerShell Command",
        "severity": 8
      },
      "tags": ["ransomware"]
    }
  ],
  "entities": [...],
  "notes": [...],
  "summary": "Investigating potential ransomware activity..."
}
```

**Success:**
- Returns timeline with full event data hydrated for all event references
- Detections include complete detection data with event context and metadata
- All other timeline fields (entities, notes, summary, etc.) preserved

**Common Errors:**
- **400 Bad Request**: Both timeline and timeline_name provided, or neither provided
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Timeline name not found in Hive

### Step 4: Format the Response

Present the expanded timeline to the user:
- Show event details with timestamps, command lines, file paths
- Display detection context with rule names and severity
- Highlight high-priority or malicious items
- Group by entity or chronologically

**Example output:**
```
Expanded Timeline: ransomware-investigation-2024
Status: in_progress | Priority: critical

EVENTS (3):
[2024-01-20 14:22:15] SERVER01 - NEW_PROCESS
  Atom: abc123
  Command: powershell.exe -encodedCommand ...
  Verdict: malicious
  Relevance: First suspicious process execution

[2024-01-20 14:25:30] SERVER01 - NETWORK_CONNECTION
  Atom: def456
  Destination: 203.0.113.50:443
  Verdict: suspicious

DETECTIONS (2):
[2024-01-20 14:22:16] Encoded PowerShell Command (severity 8)
  Detection ID: det-456
  Host: SERVER01
  Rule matched encoded PowerShell execution pattern

ENTITIES (1):
- IP: 203.0.113.50 (malicious) - C2 infrastructure
  First seen: 2024-01-20 14:25:30
```

## Example Usage

### Example 1: Expand stored timeline

User: "Show me the full details for timeline 'incident-2024-01-20'"

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="expand_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline_name": "incident-2024-01-20"
  }
)
```

### Example 2: Expand timeline object

User: "Get full event data for these timeline events"

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="expand_timeline",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "timeline": {
      "name": "Quick Investigation",
      "events": [
        {"atom": "event-atom-1", "sid": "sensor-001"},
        {"atom": "event-atom-2", "sid": "sensor-001"}
      ]
    }
  }
)
```

## Additional Notes

- Timelines store references (atoms, detection IDs), not full event data
- Expanding hydrates all references with complete data
- Use `timeline_name` for stored timelines in Hive
- Use `timeline` object for ad-hoc expansion of timeline data
- Parameters are mutually exclusive - provide one or the other
- Event data includes full telemetry from the sensor
- Detection data includes rule metadata and matched event context

## Related Functions

- `get_historic_events` - Get events directly by time range
- `get_historic_detections` - Get detections directly by time range
- `run_lcql_query` - Query events using LCQL

## Reference

See [CALLING_API.md](../../CALLING_API.md) for details on using `lc_call_tool`.

- **Config Hive Documentation**: [Config Hive: Timeline](../../../../../docs/limacharlie/doc/Platform_Management/Config_Hive/config-hive-timeline.md)
- **MCP Implementation**: `../lc-mcp-server/internal/tools/historical/timeline.go`
- **Hive Schema**: `../legion_config_hive/hives/def_timeline.go`
