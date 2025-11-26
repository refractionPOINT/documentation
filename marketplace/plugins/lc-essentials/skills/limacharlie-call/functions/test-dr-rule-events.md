
# Test D&R Rule Against Events

Test a Detection & Response (D&R) rule against inline events for unit testing and validation before deployment.

## When to Use

Use this skill when the user needs to:
- Unit test a D&R rule against sample events before deploying
- Validate detection logic works as expected
- Debug why a rule isn't matching expected events
- Test existing rules against specific event patterns
- Develop and iterate on detection logic quickly
- Verify rule behavior without waiting for live events
- Test response actions in a controlled environment

Common scenarios:
- "Test this detection rule against these sample events"
- "Does my rule match this NEW_PROCESS event?"
- "Debug why my rule isn't triggering on this event"
- "Test my detection against various attack patterns"
- "Validate my rule before deploying to production"

## What This Skill Does

This skill uses the LimaCharlie Replay service to test D&R rules against inline events you provide. It's like unit testing for detection rules - you provide sample events and the rule, and it tells you whether the rule would match and what response actions would trigger. This allows rapid iteration on detection logic without deploying rules to production or waiting for real events.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first.

- **oid**: Organization ID (required for server-side validation)
- **events**: Array of event objects to test against (required)
- **detect**: Detection component (required if `rule_name` not provided)
- **rule_name**: Name of existing rule to test (required if `detect` not provided)

Optional parameters:
- **namespace**: Rule namespace - 'general', 'managed', or 'service' (default: 'general')
- **respond**: Response actions array (defaults to a single report action)
- **trace**: Enable trace output for debugging (default: false)

**Validation Rules:**
- Either `rule_name` OR `detect` must be provided (not both empty)
- `events` array cannot be empty
- Each event should have 'routing' and 'event' keys

## How to Use

### Step 1: Prepare Test Events

Create event objects that simulate the telemetry you want to test. Each event should match LimaCharlie's event structure:

```json
{
  "routing": {
    "event_type": "NEW_PROCESS",
    "hostname": "test-host",
    "sid": "test-sensor-id"
  },
  "event": {
    "COMMAND_LINE": "powershell.exe -enc SGVsbG8gV29ybGQ=",
    "FILE_PATH": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
    "PARENT": {
      "FILE_PATH": "C:\\Windows\\explorer.exe"
    }
  }
}
```

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="test_dr_rule_events",
  parameters={
    "oid": "[organization-id]",
    "detect": {...detection logic...},
    "events": [...event objects...],
    "trace": true
  }
)
```

**Tool Details:**
- Tool name: `test_dr_rule_events`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `events`: Array of event objects to test
  - Either `rule_name` OR `detect`
- Optional parameters:
  - `namespace`: 'general', 'managed', or 'service' (default: 'general')
  - `respond`: Response actions array
  - `trace`: Enable debug tracing (default: false)

### Step 3: Handle the Response

The tool returns:
```json
{
  "matched": true,
  "stats": {
    "events_processed": 3,
    "events_matched": 1,
    "evaluations": 5,
    "events_scanned": 3,
    "bytes_scanned": 1024,
    "shards": 1,
    "wall_time": 15,
    "billed_events": 0,
    "free_events": 3
  },
  "is_dry_run": false,
  "results": [
    {
      "action": "report",
      "data": {
        "name": "encoded_powershell",
        "event": {...}
      }
    }
  ],
  "traces": [...]
}
```

**Success Indicators:**
- `matched`: true/false - whether any events matched the rule
- `stats.events_matched`: Number of events that triggered the rule
- `results`: Array of response actions that would execute

**Common Errors:**
- **Missing rule source**: Neither `rule_name` nor `detect` provided
- **Empty events**: Events array is empty
- **Invalid rule syntax**: Detection component has syntax errors
- **Rule not found**: `rule_name` doesn't exist in the specified namespace

### Step 4: Format the Response

Present results to the user:
- Clearly indicate if the rule matched (true/false)
- Show match statistics (events processed vs matched)
- Display what response actions would trigger
- If trace enabled, show evaluation details for debugging
- Suggest improvements if rule didn't match as expected

## Example Usage

### Example 1: Test Detection Against Sample Event

User request: "Test this PowerShell detection against a sample event"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="test_dr_rule_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "-enc"
    },
    "events": [
      {
        "routing": {
          "event_type": "NEW_PROCESS",
          "hostname": "workstation-1"
        },
        "event": {
          "COMMAND_LINE": "powershell.exe -enc SGVsbG8=",
          "FILE_PATH": "C:\\Windows\\System32\\powershell.exe"
        }
      }
    ]
  }
)
```

Expected response:
```json
{
  "matched": true,
  "stats": {
    "events_processed": 1,
    "events_matched": 1
  },
  "results": [
    {
      "action": "report",
      "data": {"name": "test_detection"}
    }
  ]
}
```

### Example 2: Test Existing Rule by Name

User request: "Test my 'detect-ransomware' rule against these events"

```
mcp__limacharlie__lc_call_tool(
  tool_name="test_dr_rule_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "rule_name": "detect-ransomware",
    "namespace": "general",
    "events": [
      {
        "routing": {"event_type": "NEW_PROCESS"},
        "event": {
          "COMMAND_LINE": "vssadmin.exe delete shadows /all",
          "FILE_PATH": "C:\\Windows\\System32\\vssadmin.exe"
        }
      }
    ]
  }
)
```

### Example 3: Debug with Trace Enabled

User request: "Why isn't my rule matching? Show me the trace"

```
mcp__limacharlie__lc_call_tool(
  tool_name="test_dr_rule_events",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "and",
      "rules": [
        {"op": "contains", "path": "event/FILE_PATH", "value": "powershell"},
        {"op": "contains", "path": "event/COMMAND_LINE", "value": "-enc"}
      ]
    },
    "events": [
      {
        "routing": {"event_type": "NEW_PROCESS"},
        "event": {
          "COMMAND_LINE": "powershell.exe -ExecutionPolicy Bypass",
          "FILE_PATH": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        }
      }
    ],
    "trace": true
  }
)
```

Response will include detailed trace showing which conditions passed/failed.

## Additional Notes

- **Unit Testing**: Think of this as unit tests for your detection rules
- **Fast Iteration**: Test quickly without waiting for live events
- **Server-Side**: Uses LimaCharlie Replay service for accurate validation
- **Event Format**: Events must match LimaCharlie's telemetry structure
- **Routing Required**: Each event needs a `routing` object with `event_type`
- **Free Testing**: No cost for testing with inline events
- **Trace Mode**: Enable `trace` for debugging rule logic
- **Response Actions**: Provide custom `respond` array to test specific actions
- **Default Response**: If `respond` not provided, defaults to a report action
- **Namespace Support**: Test rules from general, managed, or service namespaces
- **Rule Validation**: Also validates rule syntax as part of testing
- **Multiple Events**: Test against multiple events in one call
- **No Side Effects**: Testing doesn't execute actual response actions

## Related Functions

- `replay_dr_rule` - Test rules against historical sensor data
- `validate_dr_rule_components` - Validate rule syntax
- `generate_dr_rule_detection` - AI-generate detection logic
- `generate_dr_rule_respond` - AI-generate response actions
- `set_dr_general_rule` - Deploy validated rules

## See Also

- **detection-engineering skill**: For end-to-end detection development workflow (understand → research → build → test → deploy). This function is used in **Phase 4.1 (Unit Testing)** of that workflow.

## Reference

For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/replay/replay.go`

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
