
# Run LCQL Query

Execute LCQL (LimaCharlie Query Language) queries against your organization's historical data.

## ⚠️ CRITICAL: LCQL Syntax Required

**This function requires ACTUAL LCQL syntax - NOT SQL, NOT English, NOT natural language.**

LCQL uses a pipe-based syntax like: `-24h | * | DNS_REQUEST | event.DOMAIN_NAME = 'suspicious-domain.com'`

**WRONG:** `SELECT DISTINCT event.FILE_PATH FROM events WHERE sid = 'abc' AND event_type = 'NEW_PROCESS'` (This is SQL)
**WRONG:** `find all PowerShell executions` (This is English)
**RIGHT:** `-24h | sid = 'abc' | NEW_PROCESS | event.FILE_PATH contains 'powershell'`

## Required Workflow

**ALWAYS use this two-step workflow:**

1. **FIRST**: Use `generate_lcql_query` to convert natural language to LCQL syntax
2. **THEN**: Use `run_lcql_query` with the generated LCQL query

**DO NOT** skip step 1 and try to write LCQL manually unless you are certain of the correct syntax.

## When to Use

Use this skill when the user needs to:
- Search historical events, detections, or audit logs
- Perform threat hunting across sensor telemetry
- Investigate security incidents
- Analyze patterns in event data
- Extract insights from historical data

Common scenarios:
- "Search for all DNS requests to suspicious-domain.com in the last 24 hours"
- "Find all process executions of powershell.exe"
- "Show me all network connections to IP 203.0.113.50"
- "Query detections from the last week"

**If a query covers time outside of the last 30 days, you are _REQUIRED_ to ask the user for confirmation as it may incur costs.**

## What This Skill Does

Executes LCQL queries against LimaCharlie's replay service, supporting complex filtering, timeframes, and pagination for events, detections, or audit logs.

## Recommended Workflow: AI-Assisted Query Generation

**For reliable query creation, use this workflow:**

1. **Gather Documentation** (if needed)
   Use `lookup-lc-doc` skill to search for LCQL syntax, operators, and event types.

2. **Generate Query from Natural Language**
   ```
   mcp__plugin_lc-essentials_limacharlie__generate_lcql_query(
     oid="[your-oid]",
     query="find all PowerShell executions in the last 24 hours"
   )
   ```
   Returns validated LCQL query with explanation.

3. **Execute Query** (this API call)

## Required Information

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list_user_orgs` first.

- **oid**: Organization ID (UUID)
- **query**: LCQL query string (generate using `generate_lcql_query`)

Optional:
- **limit**: Max events to return (default: 1000)
- **stream**: "event" (default), "detect", or "audit"

## How to Use

### Step 1: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="run_lcql_query",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "query": "[your-lcql-query]",
    "limit": 1000,
    "stream": "event"
  }
)
```

### Step 2: Handle the Response

**Success:**
```json
{
  "results": [...],
  "cursor": "next-page-cursor",
  "stats": {
    "events_searched": 50000,
    "results_returned": 100
  }
}
```
- Non-empty `cursor` means more results available (pagination)
- Empty `cursor` means all results retrieved

**Common Errors:**
- **400 Bad Request**: Invalid LCQL syntax - use `generate_lcql_query` first
- **403 Forbidden**: Insufficient permissions
- **413 Request Too Large**: Add filters or limits
- **500 Server Error**: Query timeout, simplify query

## Example Usage

### Complete AI-Assisted Workflow

User request: "Search for all DNS requests to suspicious-domain.com in the last 24 hours"

**Step 1: Generate query**
```
mcp__plugin_lc-essentials_limacharlie__generate_lcql_query(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="DNS requests to suspicious-domain.com in the last 24 hours"
)
// Returns: {"query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME = 'suspicious-domain.com'", "explanation": "..."}
```

**Step 2: Execute query**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="run_lcql_query",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME = 'suspicious-domain.com'",
    "limit": 1000,
    "stream": "event"
  }
)
```

**Step 3: Present results**
```
Query Results: 45 events found

1. [2024-01-20 14:22:15] DNS_REQUEST on SERVER01
   - Domain: suspicious-domain.com
   - IP: 203.0.113.50
   ...
```

## Related Functions

- `generate_lcql_query` - AI-assisted query generation from natural language
- `list_saved_queries` - List saved queries
- `set_saved_query` - Save a query for reuse
- `run_saved_query` - Execute a saved query
- Use `lookup-lc-doc` skill for LCQL syntax reference

## See Also

- **detection-engineering skill**: For end-to-end detection development workflow (understand → research → build → test → deploy). This function is used in **Phase 2.2 (LCQL Exploration)** of that workflow.

## Reference

For the API implementation, see [CALLING_API.md](../../CALLING_API.md).

For LCQL syntax and operators, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
