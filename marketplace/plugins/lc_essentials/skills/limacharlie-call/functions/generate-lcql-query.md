
# Generate LCQL Query

Generate LimaCharlie Query Language (LCQL) queries from natural language descriptions using AI-powered assistance.

## ⚠️ CRITICAL: Use This BEFORE run_lcql_query

**ALWAYS use this function FIRST before calling `run_lcql_query`.**

LCQL is NOT SQL or standard query language - it uses a unique pipe-based syntax. Do not attempt to write LCQL manually.

**Correct workflow:**
1. **FIRST**: Call `generate_lcql_query` with natural language (e.g., "find all PowerShell executions in last 24 hours")
2. **THEN**: Use the generated LCQL query with `run_lcql_query`

**Example LCQL syntax:** `-24h | * | NEW_PROCESS | event.FILE_PATH contains 'powershell'`

## When to Use

**Use this skill EVERY TIME before running an LCQL query, when the user needs to:**
- Create LCQL queries from natural language descriptions
- Convert investigation questions into LCQL syntax
- Learn proper LCQL query syntax through examples
- Generate complex telemetry queries without memorizing syntax
- Search historical event data with precise filters
- Build queries for incident investigation or threat hunting
- Get help with LCQL operators and field paths

Common scenarios:
- "Create a query to find all PowerShell executions in the last 24 hours"
- "Write LCQL to search for network connections to suspicious IPs"
- "Generate a query for file creation events on Windows systems"
- "Help me query DNS requests to specific domains"
- "Build a query to find process executions with specific command line patterns"
- "Get unique file paths that have executed in the last week"

## What This Skill Does

This skill uses AI (Gemini) to generate LCQL queries from natural language descriptions. It validates the generated query against your organization's schema through an iterative process (up to 10 retries) to ensure the query is syntactically correct and uses valid field paths for your events. The skill returns both the validated query and an explanation of what it does.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for query validation against org schema)
- **query**: Natural language description of what you want to search for

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Clear natural language description of the query intent
3. Understand what events or telemetry you're looking for

### Step 2: Call the Tool

Use the `generate_lcql_query` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__generate_lcql_query(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="find all PowerShell executions in the last 24 hours"
)
```

**Tool Details:**
- Tool: `mcp__limacharlie__generate_lcql_query`
- Parameters:
  - `oid` (string, required): Organization ID for validation
  - `query` (string, required): Natural language description

**How it works:**
- Sends the natural language query to Gemini AI with LCQL prompt template
- Validates the generated query against your organization's event schema
- Retries up to 10 times if validation fails, refining the query each iteration
- Returns the validated query and an explanation

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "query": "event_type:NEW_PROCESS file_path:powershell* start_ts:>now-24h",
  "explanation": "This query searches for NEW_PROCESS events where the file path contains 'powershell' and the event occurred within the last 24 hours. The 'start_ts:>now-24h' filter ensures only recent events are returned."
}
```

**Success:**
- `query`: The validated LCQL query string ready to use
- `explanation`: Human-readable explanation of what the query does and how it works

**Possible Issues:**
- If validation fails after 10 retries, the tool returns an error indicating the AI couldn't generate a valid query for your organization's schema
- Complex or ambiguous natural language descriptions may produce unexpected queries - review the explanation
- Some event types or field paths may not be available in your organization

### Step 4: Format the Response

Present the result to the user:
- Show the generated LCQL query in a code block for easy copying
- Display the explanation to help the user understand the query
- Suggest running the query using the LCQL search interface or API
- Mention that they can refine the query manually if needed
- Remind them about query performance considerations for large datasets

## Example Usage

### Example 1: Find Recent PowerShell Executions

User request: "Create a query to find all PowerShell executions in the last 24 hours"

Steps:
1. Get organization ID from context
2. Call tool:
```
mcp__limacharlie__generate_lcql_query(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="find all PowerShell executions in the last 24 hours"
)
```
3. Present the generated query and explanation

Expected response:
```json
{
  "query": "event_type:NEW_PROCESS file_path:powershell* start_ts:>now-24h",
  "explanation": "This query searches for NEW_PROCESS events where the file path contains 'powershell' and the event occurred within the last 24 hours."
}
```

### Example 2: Search for Network Connections

User request: "Write LCQL to find network connections to IP address 192.168.1.100"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__generate_lcql_query(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="network connections to IP address 192.168.1.100"
)
```

Expected response:
```json
{
  "query": "event_type:NETWORK_CONNECTIONS routing/dst_ip:192.168.1.100",
  "explanation": "This query searches for NETWORK_CONNECTIONS events where the destination IP address is 192.168.1.100."
}
```

### Example 3: Complex Query with Multiple Conditions

User request: "Find DNS requests to domains ending in .ru or .cn from Windows systems in the last week"

Steps:
1. Get organization ID
2. Call tool with complex description:
```
mcp__limacharlie__generate_lcql_query(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="DNS requests to domains ending in .ru or .cn from Windows systems in the last week"
)
```

Expected response:
```json
{
  "query": "event_type:DNS_REQUEST (routing/domain:*.ru OR routing/domain:*.cn) routing/plat:windows start_ts:>now-7d",
  "explanation": "This query searches for DNS_REQUEST events where the domain ends in .ru or .cn, from Windows platforms, within the last 7 days. Boolean operators allow combining multiple conditions."
}
```

## Additional Notes

- **AI-Powered**: Uses Gemini AI with LCQL-specific prompt templates
- **Validated**: Automatically validates against your organization's event schema
- **Iterative**: Retries up to 10 times to generate a valid query
- **Requires OID**: Validation needs organization context for field paths
- **Field Paths**: Uses your actual telemetry schema to ensure field paths exist
- **Operators**: Supports LCQL operators like `:`, `>`, `<`, `*` wildcards, `OR`, `AND`, `NOT`
- **Time Filters**: Can generate time-based filters like `start_ts:>now-24h`
- **Event Types**: Validates against available event types (NEW_PROCESS, DNS_REQUEST, etc.)
- **Limitations**: Complex natural language may require multiple attempts or manual refinement
- **Performance**: Consider query performance for broad searches on large datasets
- **Learning Tool**: Great for learning LCQL syntax through examples
- **Refinement**: You can manually edit the generated query if needed
- **Best Practice**: Start with simpler queries and build complexity incrementally
- **Prompt Template**: Uses `prompts/gen_lcql.txt` from the MCP server

## Reference

For more details on the MCP tool implementation, check: `../lc-mcp-server/internal/tools/ai/ai.go` (generate_lcql_query function)

For LCQL syntax and documentation, see LimaCharlie's Query Language documentation.
