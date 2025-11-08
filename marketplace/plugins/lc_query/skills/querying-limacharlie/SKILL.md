---
name: querying-limacharlie
description: Query and analyze LimaCharlie telemetry data using LCQL (LimaCharlie Query Language). Use when users ask about searching events, analyzing telemetry, hunting for threats, investigating incidents, or examining historical security data across endpoints and cloud sources.
allowed_tools:
  - Read
  - mcp__limacharlie__run_lcql_query
  - mcp__limacharlie__get_historic_events
  - mcp__limacharlie__get_historic_detections
  - mcp__limacharlie__search_iocs
  - mcp__limacharlie__batch_search_iocs
  - mcp__limacharlie__get_time_when_sensor_has_data
  - mcp__limacharlie__list_saved_queries
  - mcp__limacharlie__get_saved_query
  - mcp__limacharlie__run_saved_query
  - mcp__limacharlie__set_saved_query
  - mcp__limacharlie__delete_saved_query
  - mcp__limacharlie__get_event_schema
  - mcp__limacharlie__get_event_schemas_batch
  - mcp__limacharlie__get_event_types_with_schemas
  - mcp__limacharlie__get_event_types_with_schemas_for_platform
  - mcp__limacharlie__get_platform_names
  - mcp__limacharlie__list_with_platform
  - mcp__limacharlie__generate_lcql_query
  - mcp__limacharlie__generate_sensor_selector
  - mcp__limacharlie__get_sensor_info
  - mcp__limacharlie__list_sensors
---

# Querying LimaCharlie Telemetry

Use this skill when users need to search, analyze, or investigate security telemetry in LimaCharlie. This includes threat hunting, incident investigation, compliance reporting, and general data exploration across endpoints, cloud adapters, and detection streams.

## When to Use This Skill

Invoke this skill autonomously when the user's request involves:

- **Searching for specific events** - "Show me PowerShell activity", "Find DNS queries to suspicious domains"
- **Threat hunting** - "Look for unsigned executables", "Find unusual parent-child process relationships"
- **Incident investigation** - "What happened on host X?", "Timeline of activities"
- **Compliance and reporting** - "Count logon types", "Network connections over time"
- **IOC searches** - "Has IP 1.2.3.4 appeared?", "Search for this hash across the fleet"
- **Understanding available data** - "What event types are available?", "What fields does NEW_PROCESS have?"

## Available Tools

You have access to the **limacharlie** MCP server with these tool categories:

### Historical Data Tools

**Primary querying tool:**
- `run_lcql_query` - Execute LCQL queries against event, detection, or audit streams
  - Parameters: `query` (LCQL string), `limit` (optional), `stream` (event/detect/audit)
  - Use for: Most searches and investigations

**IOC search tools:**
- `search_iocs` - Search for a single IOC (IP, domain, hash, etc.)
  - Parameters: `indicator`, `indicator_type`, `days`
- `batch_search_iocs` - Search for multiple IOCs in parallel
  - Parameters: `iocs` (array of {indicator, type}), `days`

### Schema Discovery Tools

Use these to understand available data **before** building queries:

- `get_platform_names` - List available platforms (windows, linux, macos, etc.)
- `get_event_types_with_schemas_for_platform` - Get event types for a specific platform
- `get_event_schema` - Get field definitions for a specific event type (prefix with "evt:")
- `get_event_types_with_schemas` - List all available event types

### AI-Powered Generation Tools

- `generate_lcql_query` - Generate LCQL from natural language
  - Use when: User request is complex or you're unsure of syntax
  - Returns: Validated LCQL query + explanation
- `generate_sensor_selector` - Generate sensor selection expressions
  - Use when: Complex sensor filtering needed

### Core Tools (Context)

- `get_sensor_info` - Get details about a specific sensor (hostname, platform, tags, IPs)
- `list_sensors` - List all sensors with optional filtering

## Query Workflow

### Standard Workflow

```
1. Understand user's question
   ↓
2. Check if schema lookup needed (unfamiliar event types)
   - Use get_event_types_with_schemas_for_platform
   - Use get_event_schema for field details
   ↓
3. Build or generate the query
   - Simple queries: Build LCQL directly
   - Complex queries: Use generate_lcql_query
   ↓
4. Execute with run_lcql_query
   - Set appropriate limit (default: unlimited)
   - Choose correct stream (event/detect/audit)
   ↓
5. Interpret and present results
   - Explain findings in plain language
   - Highlight anomalies or key findings
   - Suggest follow-up actions
```

### IOC Search Workflow

```
1. User provides IOC(s)
   ↓
2. Determine search type
   - Single IOC → search_iocs
   - Multiple IOCs → batch_search_iocs
   ↓
3. Execute with appropriate timeframe
   ↓
4. Report matches with context
```

## LCQL Query Structure

Every LCQL query follows this structure:

```
TIMEFRAME | SENSOR_SELECTOR | EVENT_TYPE | FILTER | PROJECTION
```

### Quick Reference

**Timeframe** (required):
```
-24h    Last 24 hours
-7d     Last 7 days
-30m    Last 30 minutes
```

**Sensor Selector** (filter by platform/tags):
```
plat == windows                     Windows endpoints
plat == linux and tag == production Linux production hosts
hostname contains "server"          Specific hostname pattern
```

**Event Types** (what to search):
```
NEW_PROCESS              Process creation
DNS_REQUEST              DNS queries
NETWORK_CONNECTIONS      Network activity
CODE_IDENTITY            Binary signatures
WEL                      Windows Event Logs
FILE_CREATE              File operations
*                        All events (expensive - use sparingly)
```

**Filters** (boolean expressions):
```
event/COMMAND_LINE contains "powershell"
event/DOMAIN_NAME contains "google"
routing/hostname == "server-01"
event/FILE_IS_SIGNED != 1
event/COMMAND_LINE contains "psexec" and event/FILE_PATH not contains "windows"
```

**Projections** (output formatting):
```
event/DOMAIN_NAME as domain routing/hostname as host
COUNT(event) as count GROUP BY(domain)
COUNT_UNIQUE(routing/sid) as unique_hosts
ORDER BY(count) DESC
```

For detailed syntax, see [LCQL_SYNTAX.md](./LCQL_SYNTAX.md).

## Event Structure

All LimaCharlie events have two top-level objects:

**`routing`** - Metadata (consistent across all events):
- `routing/sid` - Sensor ID (unique endpoint)
- `routing/hostname` - Hostname
- `routing/event_type` - Event type (NEW_PROCESS, DNS_REQUEST, etc.)
- `routing/event_time` - Unix timestamp (milliseconds)
- `routing/plat` - Platform identifier
- `routing/int_ip` / `routing/ext_ip` - IP addresses
- `routing/this` / `routing/parent` / `routing/target` - Process correlation hashes
- `routing/tags` - Sensor tags

**`event`** - Event-specific data (varies by type):
- NEW_PROCESS: `event/FILE_PATH`, `event/COMMAND_LINE`, `event/PROCESS_ID`
- DNS_REQUEST: `event/DOMAIN_NAME`, `event/IP_ADDRESS`, `event/DNS_TYPE`
- WEL: `event/EVENT/System/EventID`, `event/EVENT/EventData/*`
- CODE_IDENTITY: `event/FILE_PATH`, `event/HASH`, `event/SIGNATURE/FILE_IS_SIGNED`

For complete event type details, see [EVENT_TYPES.md](./EVENT_TYPES.md).

## Common Query Patterns

### Process Hunting
```lcql
-24h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "powershell" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

### DNS Analysis
```lcql
-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "google" | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

### Unsigned Binaries
```lcql
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as path event/HASH as hash COUNT_UNIQUE(hash) as count GROUP BY(path hash)
```

### Windows Event Logs
```lcql
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as srcip event/EVENT/EventData/TargetUserName as username
```

For more examples organized by use case, see [QUERY_EXAMPLES.md](./QUERY_EXAMPLES.md).

## Best Practices

### Query Optimization

**Always include:**
- Specific timeframe (don't use overly broad ranges)
- Platform selector when applicable
- Specific event types (avoid `*` unless necessary)

**Good query:**
```lcql
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "cmd.exe"
```

**Bad query (expensive):**
```lcql
-30d | * | * | event/* contains "cmd"
```

### Schema-First Approach

When working with unfamiliar event types:

1. Use `get_event_types_with_schemas_for_platform` to see available events
2. Use `get_event_schema` to understand field structure
3. Build query based on actual schema

**Example workflow:**
```
User: "Show me Sysmon process creation events on Windows"

1. get_event_types_with_schemas_for_platform(platform="windows")
   → Confirms "evt:NEW_PROCESS" is available

2. get_event_schema(name="evt:NEW_PROCESS")
   → Shows available fields: event/FILE_PATH, event/COMMAND_LINE, etc.

3. Build query:
   -24h | plat == windows | NEW_PROCESS | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

### Iterative Refinement

Start broad, then add specificity:

**Step 1 - Basic query:**
```lcql
-1h | plat == windows | NEW_PROCESS
```

**Step 2 - Add filter:**
```lcql
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "temp"
```

**Step 3 - Add aggregation:**
```lcql
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "temp" | event/FILE_PATH as path COUNT(event) as count GROUP BY(path)
```

### Using AI Generation

For complex natural language requests, leverage `generate_lcql_query`:

**User request:** "Show me all PowerShell commands that downloaded files from the internet in the last week"

**Workflow:**
1. Call `generate_lcql_query(query="Show me all PowerShell commands that downloaded files from the internet in the last week")`
2. Review generated query for correctness
3. Execute with `run_lcql_query`
4. Interpret results

### Stream Selection

Choose the correct stream based on what you're searching:

- **`event`** (default) - Telemetry from sensors and adapters
  - Use for: Process activity, network connections, file operations, logs

- **`detect`** - Detection events from D&R rules
  - Use for: Alerts, rule matches, detection history

- **`audit`** - Platform audit logs
  - Use for: API calls, configuration changes, user actions

### Result Limits

Set appropriate limits to avoid overwhelming results:

```python
# Exploratory query - limit to see sample data
run_lcql_query(query="...", limit=100)

# Full investigation - no limit (default)
run_lcql_query(query="...")

# Known high-volume query - reasonable limit
run_lcql_query(query="...", limit=1000)
```

## Error Handling

If a query fails:

1. **Check syntax** - Verify LCQL structure is correct
2. **Verify event types** - Use schema tools to confirm event type exists
3. **Check field paths** - Use `get_event_schema` to verify field names
4. **Simplify** - Remove filters one at a time to isolate the issue
5. **Check timeframe** - Ensure reasonable time range
6. **Consider AI generation** - Use `generate_lcql_query` for complex queries

## Response Format

When presenting query results to users:

1. **Acknowledge** - Confirm understanding of the question
2. **Explain** - Describe your approach (if complex)
3. **Show query** - Display the LCQL query being executed
4. **Execute** - Run the query with appropriate parameters
5. **Interpret** - Explain results in plain language
6. **Highlight** - Point out anomalies or key findings
7. **Suggest** - Recommend follow-up actions or deeper investigation

**Example:**

User: "Show me PowerShell activity on Windows servers in the last day"

Response:
```
I'll search for PowerShell processes on Windows endpoints from the last 24 hours.

Query:
-24h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "powershell" | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host

[Execute run_lcql_query]

Results show:
- 45 PowerShell executions across 12 Windows hosts
- Most activity from scheduled tasks (legitimate)
- 2 instances with encoded commands on host "ws-finance-05" - potentially suspicious
- Recommendation: Investigate the encoded commands further

Follow-up: Would you like me to examine the encoded PowerShell commands in detail?
```

## Tool Orchestration

### Combining Tools Effectively

**Scenario: Investigate a specific host**

1. Get host info: `get_sensor_info(sid=...)`
2. Search activity: `run_lcql_query(query="-24h | routing/sid == '...' | * | ...")`
3. Check for IOCs: `batch_search_iocs(iocs=[...], days=7)`

**Scenario: Unknown event type**

1. List platforms: `get_platform_names()`
2. Get event types: `get_event_types_with_schemas_for_platform(platform="windows")`
3. Get schema: `get_event_schema(name="evt:NEW_PROCESS")`
4. Build and run query: `run_lcql_query(...)`

**Scenario: Complex hunt**

1. Generate query: `generate_lcql_query(query="natural language description")`
2. Execute: `run_lcql_query(query=generated_query)`
3. Refine if needed: Adjust timeframe, add filters, change projections

## Common Use Cases

### Threat Hunting

- Look for suspicious PowerShell
- Find unsigned executables
- Detect unusual parent-child relationships
- Identify lateral movement indicators
- Search for known IOCs

### Incident Investigation

- Timeline of host activity
- Network connections from specific process
- File operations during timeframe
- Authentication events
- Correlated events across sensors

### Compliance & Reporting

- Logon activity by type and user
- DNS resolution patterns
- Network traffic summaries
- Software inventory (running processes)
- Security control validation

See [QUERY_EXAMPLES.md](./QUERY_EXAMPLES.md) for detailed examples.

## Key Differences from Agents

This is a **Skill**, not an Agent:

- **Autonomous invocation** - Claude invokes this skill automatically when appropriate
- **Tool orchestration focus** - How to combine MCP tools, not just syntax tutorial
- **Concise and actionable** - Quick reference with links to detailed docs
- **Context-aware** - Adapts to user's specific question and available data

## Additional Resources

- [LCQL_SYNTAX.md](./LCQL_SYNTAX.md) - Complete LCQL syntax reference
- [QUERY_EXAMPLES.md](./QUERY_EXAMPLES.md) - Practical examples by use case
- [EVENT_TYPES.md](./EVENT_TYPES.md) - Event type reference guide
