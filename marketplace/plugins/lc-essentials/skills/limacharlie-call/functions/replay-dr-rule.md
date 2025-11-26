
# Replay D&R Rule Against Historical Data

Test a Detection & Response (D&R) rule against historical sensor data to validate detection logic on real telemetry.

## When to Use

Use this skill when the user needs to:
- Test a D&R rule against real historical telemetry data
- Validate detection logic works in production-like conditions
- Backtest rules against past incidents or time periods
- Verify rules would have caught known malicious activity
- Test rules against specific sensors or sensor groups
- Estimate rule performance and match rates before deployment
- Debug rules using actual event data from their environment

Common scenarios:
- "Test this rule against the last hour of data"
- "Would this rule have detected yesterday's incident?"
- "Replay my detection against all Windows sensors from last week"
- "How many events would this rule match in production?"
- "Test this rule against sensor XYZ's data"
- "Estimate the cost of running this rule against 24 hours of data"

## What This Skill Does

This skill uses the LimaCharlie Replay service to test D&R rules against historical telemetry data stored in your organization. Unlike `test_dr_rule_events` which uses inline events, this function replays actual sensor data from a specified time range. This is the closest you can get to testing rules in production without actually deploying them.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first.

- **oid**: Organization ID (required)
- **detect**: Detection component (required if `rule_name` not provided)
- **rule_name**: Name of existing rule to test (required if `detect` not provided)

**Time Range** (one of these is required):
- **last_seconds**: Replay last N seconds (e.g., 3600 for last hour)
- OR both **start_time** and **end_time**: Epoch timestamps in seconds

Optional parameters:
- **namespace**: Rule namespace - 'general', 'managed', or 'service' (default: 'general')
- **respond**: Response actions array (defaults to a single report action)
- **sid**: Specific sensor ID to replay from
- **selector**: Sensor selector expression using bexpr syntax (e.g., `plat == "windows"`)
- **limit_event**: Maximum events to process (default: 10000)
- **limit_eval**: Maximum evaluations to perform
- **trace**: Enable trace output for debugging (default: false)
- **dry_run**: Estimate cost only without processing (default: false)
- **stream**: Data stream - 'event', 'audit', or 'detect' (default: 'event')

**Validation Rules:**
- Either `rule_name` OR `detect` must be provided
- Either `last_seconds` OR both `start_time` and `end_time` must be provided

## How to Use

### Step 1: Determine Time Range

Choose how to specify the time range:

**Option A: Last N seconds**
```json
"last_seconds": 3600  // Last hour
```

**Option B: Specific time range**
```json
"start_time": 1700000000,  // Epoch timestamp
"end_time": 1700003600     // Epoch timestamp
```

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "[organization-id]",
    "detect": {...detection logic...},
    "last_seconds": 3600,
    "selector": "plat == \"windows\""
  }
)
```

**Tool Details:**
- Tool name: `replay_dr_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - Either `rule_name` OR `detect`
  - Either `last_seconds` OR both `start_time`/`end_time`
- Optional parameters:
  - `namespace`: 'general', 'managed', or 'service'
  - `respond`: Response actions array
  - `sid`: Specific sensor ID
  - `selector`: Sensor selector (bexpr syntax)
  - `limit_event`: Max events (default: 10000)
  - `limit_eval`: Max evaluations
  - `trace`: Enable tracing (default: false)
  - `dry_run`: Cost estimate only (default: false)
  - `stream`: 'event', 'audit', or 'detect' (default: 'event')

### Step 3: Handle the Response

The tool returns:
```json
{
  "matched": true,
  "stats": {
    "events_processed": 50000,
    "events_matched": 127,
    "evaluations": 150000,
    "events_scanned": 50000,
    "bytes_scanned": 52428800,
    "shards": 5,
    "wall_time": 3500,
    "billed_events": 50000,
    "free_events": 0
  },
  "is_dry_run": false,
  "results": [
    {
      "action": "report",
      "data": {
        "name": "suspicious_activity",
        "event": {...}
      }
    }
  ],
  "traces": [...]
}
```

**Key Statistics:**
- `events_processed`: Total events scanned
- `events_matched`: Events that triggered the rule
- `billed_events`: Events counted against quota
- `wall_time`: Processing time in milliseconds
- `is_dry_run`: Whether this was a cost estimate only

**Common Errors:**
- **Missing rule source**: Neither `rule_name` nor `detect` provided
- **Missing time range**: Neither `last_seconds` nor `start_time`/`end_time` provided
- **Invalid selector**: Sensor selector syntax error
- **Sensor not found**: Specified `sid` doesn't exist
- **Quota exceeded**: Event limit reached

### Step 4: Interpret Results

Present results to the user:
- Show match rate (events_matched / events_processed)
- Highlight matched events and response actions
- Report processing statistics and cost
- If dry_run, explain this was a cost estimate
- Suggest rule tuning if match rate seems too high/low

## Example Usage

### Example 1: Test Rule Against Last Hour

User request: "Test my PowerShell detection against the last hour of data"

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "-enc"
    },
    "last_seconds": 3600
  }
)
```

### Example 2: Test Existing Rule with Sensor Filter

User request: "Test 'detect-ransomware' against Windows sensors from yesterday"

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "rule_name": "detect-ransomware",
    "namespace": "general",
    "start_time": 1700000000,
    "end_time": 1700086400,
    "selector": "plat == \"windows\"",
    "limit_event": 100000
  }
)
```

### Example 3: Estimate Cost Before Full Replay

User request: "How many events would this rule process over the last 24 hours?"

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "exists",
      "path": "event/COMMAND_LINE"
    },
    "last_seconds": 86400,
    "dry_run": true
  }
)
```

Response shows estimated events without processing:
```json
{
  "matched": false,
  "is_dry_run": true,
  "stats": {
    "events_processed": 0,
    "billed_events": 250000
  }
}
```

### Example 4: Test Against Specific Sensor

User request: "Replay this rule against sensor abc123 from the last 2 hours"

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NETWORK_CONNECTIONS",
      "op": "is",
      "path": "event/NETWORK_ACTIVITY",
      "value": 1
    },
    "sid": "abc123-sensor-id",
    "last_seconds": 7200,
    "trace": true
  }
)
```

### Example 5: Test Against Detection Stream

User request: "Check if this rule would have caught existing detections"

```
mcp__limacharlie__lc_call_tool(
  tool_name="replay_dr_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "detection",
      "op": "contains",
      "path": "event/cat",
      "value": "ransomware"
    },
    "last_seconds": 604800,
    "stream": "detect"
  }
)
```

## Additional Notes

- **Production Testing**: Tests against real historical data from your environment
- **Billable Events**: Replay consumes event quota - use `dry_run` to estimate first
- **Default Limit**: 10,000 events by default; increase with `limit_event`
- **Sensor Selection**: Use `sid` for single sensor, `selector` for groups
- **Selector Syntax**: Uses bexpr syntax (e.g., `plat == "windows"`, `hostname contains "server"`)
- **Time Ranges**: Use `last_seconds` for relative time, epoch timestamps for absolute
- **Streams**: 'event' for telemetry, 'detect' for detections, 'audit' for audit logs
- **Trace Mode**: Enable for debugging but increases response size
- **Performance**: Large time ranges or many sensors take longer to process
- **Cost Control**: Use `dry_run` first, then set appropriate `limit_event`
- **Response Actions**: Actions are simulated, not actually executed
- **Iterative Testing**: Start with small time windows, expand once rule is tuned

## Related Functions

- `test_dr_rule_events` - Test rules against inline events (unit testing)
- `validate_dr_rule_components` - Validate rule syntax
- `generate_dr_rule_detection` - AI-generate detection logic
- `set_dr_general_rule` - Deploy validated rules
- `get_historic_events` - Query raw historical events

## See Also

- **detection-engineering skill**: For end-to-end detection development workflow (understand → research → build → test → deploy). This function is used in **Phase 4.2 (Historical Replay)** of that workflow.
- **dr-replay-tester agent**: For parallel multi-org replay testing, the detection-engineering skill uses this specialized agent to test rules across multiple organizations simultaneously.

## Reference

For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/replay/replay.go`

For D&R rule syntax and sensor selectors, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
