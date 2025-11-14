
# Run LCQL Query

Execute powerful LCQL (LimaCharlie Query Language) queries against your organization's historical data.

## When to Use

Use this skill when the user needs to:
- Search historical events, detections, or audit logs
- Perform threat hunting across sensor telemetry
- Investigate security incidents using flexible queries
- Analyze patterns in event data
- Filter and aggregate telemetry data
- Search for specific indicators across timeframes
- Perform compliance audits
- Extract insights from historical data

Common scenarios:
- "Search for all DNS requests to suspicious-domain.com in the last 24 hours"
- "Find all process executions of powershell.exe"
- "Show me all network connections to IP 203.0.113.50"
- "Query detections from the last week"
- "Find file modifications in C:\\Windows\\System32"

## What This Skill Does

This skill executes LCQL queries against LimaCharlie's replay service, supporting complex filtering, timeframes, and pagination. It can query events, detections, or audit logs with full LCQL syntax support.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **query**: LCQL query string (e.g., "-1h | * | * | event.FILE_PATH ends with '.exe'")

Optional parameters:
- **limit**: Maximum number of results to return (unlimited if not specified)
- **stream**: Data stream to query - "event" (default), "detect", or "audit"

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid LCQL query with proper syntax
3. Stream type is one of: event, detect, audit
4. Limit is reasonable for performance

### Step 2: Call the API

Use the `lc_api_call` MCP tool to POST to the replay service:

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/insight/c7e8f940-1234-5678-abcd-1234567890ab/lcql",
  body={
    "query": "-1h | * | * | event.FILE_PATH ends with '.exe'",
    "limit_event": 1000,
    "limit_eval": 10000,
    "event_source": {
      "stream": "event",
      "sensor_events": {
        "cursor": "-"
      }
    }
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/insight/{oid}/lcql` (or use replay service URL directly)
- Body fields:
  - `oid`: Organization ID
  - `query`: LCQL query string
  - `limit_event`: Approx max events to process
  - `limit_eval`: Approx max rule evaluations
  - `event_source`: Specifies stream and cursor for pagination

**LCQL Query Format:**
```
timeframe | sensor_selector | event_types | filtering_logic
```

Examples:
- `-24h | * | * | event.FILE_PATH starts with 'C:\\Windows'`
- `-7d | tag:production | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'`
- `-30d | plat:windows | NETWORK_CONNECTIONS | event.IP_ADDRESS = '203.0.113.50'`

**Note:** The SDK method `org.QueryWithContext()` handles authentication and routing to the replay service automatically.

### Step 3: Handle the Response

The API returns paginated results:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "results": [
      {
        "event": {
          "TIMESTAMP": 1705761234567,
          "EVENT_TYPE": "NEW_PROCESS",
          "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
          "COMMAND_LINE": "cmd.exe /c whoami",
          ...
        },
        "routing": {
          "sid": "sensor-xyz-123",
          "hostname": "SERVER01",
          ...
        }
      },
      ...
    ],
    "cursor": "next-page-cursor-token",
    "stats": {
      "events_searched": 50000,
      "results_returned": 100
    }
  }
}
```

**Success (200):**
- `results` array contains matching events/detections
- Each result has `event` data and `routing` metadata
- `cursor` is non-empty if more results available (use for pagination)
- `stats` provides query performance metrics
- Empty `cursor` means all results retrieved

**Common Errors:**
- **400 Bad Request**: Invalid LCQL syntax or malformed query
- **403 Forbidden**: Insufficient permissions or retention policy limits
- **413 Request Too Large**: Query returns too much data, add filters or limits
- **500 Server Error**: Query timeout or service issue, simplify query

### Step 4: Format the Response

Present the result to the user:
- Display count of results and whether more are available
- Format events in readable structure
- Highlight key fields relevant to the query
- Show timestamps in human-readable format
- Group or aggregate results if appropriate
- Indicate if results were truncated due to limits

**Example formatted output:**
```
Query Results: 45 events found (showing all)

1. [2024-01-20 14:22:15] NEW_PROCESS on SERVER01
   - Process: C:\Windows\System32\cmd.exe
   - Command: cmd.exe /c whoami
   - User: DOMAIN\administrator
   - PID: 4567

2. [2024-01-20 14:23:01] NEW_PROCESS on WORKSTATION-05
   - Process: C:\Windows\System32\powershell.exe
   - Command: powershell.exe -ExecutionPolicy Bypass
   - User: LOCAL\user01
   - PID: 8901

...

Query Stats:
- Events searched: 50,000
- Results returned: 45
- Execution time: 1.2s
```

## Example Usage

### Example 1: Search for suspicious DNS requests

User request: "Search for all DNS requests to suspicious-domain.com in the last 24 hours"

LCQL Query: `-24h | * | DNS_REQUEST | event.DOMAIN_NAME = 'suspicious-domain.com'`

Steps:
1. Construct LCQL query with timeframe and filters
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="https://replay.limacharlie.io/",
  body={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME = 'suspicious-domain.com'",
    "event_source": {"stream": "event", "sensor_events": {"cursor": "-"}}
  }
)
```
3. Parse and display matching DNS requests

### Example 2: Find PowerShell executions

User request: "Find all process executions of powershell.exe in the last 7 days"

LCQL Query: `-7d | * | NEW_PROCESS | event.FILE_PATH ends with 'powershell.exe'`

Steps:
1. Build query targeting NEW_PROCESS events
2. Filter by file path ending
3. Execute query and display results with command lines

### Example 3: Query detections

User request: "Show me all detections from the last week"

LCQL Query: `-7d | * | *` with stream="detect"

Steps:
1. Set stream parameter to "detect" instead of "event"
2. Query all detection events
3. Group by detection type and show summary

## Additional Notes

- LCQL supports complex boolean logic: AND, OR, NOT
- Timeframe prefixes: `-1h`, `-24h`, `-7d`, `-30d`, etc.
- Sensor selectors: `*` (all), `sid:xyz`, `tag:production`, `plat:windows`
- Event type filters: `*` (all), `NEW_PROCESS`, `DNS_REQUEST`, `NETWORK_CONNECTIONS`
- Comparison operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `starts with`, `ends with`, `contains`, `matches` (regex)
- Results are paginated automatically using cursors
- Large queries may take longer to execute
- Consider using timeframe limits to improve performance
- For recurring queries, use saved queries feature
- Audit stream requires special permissions
- Detection stream is limited to detection events only
- Cursor-based pagination allows retrieving all results across multiple pages
- The replay service may have different rate limits than REST API

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For LCQL syntax documentation, see: https://doc.limacharlie.io/docs/documentation/docs/lc-query-language.md

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/query.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/historical/historical.go`
