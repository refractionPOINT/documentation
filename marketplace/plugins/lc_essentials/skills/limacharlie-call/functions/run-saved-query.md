
# Run Saved Query

Execute a saved LCQL query by name and return the results.

## When to Use

Use this skill when the user needs to:
- Run a pre-built saved query
- Execute validated hunting queries
- Perform repeated investigations
- Use organization-standard queries

Common scenarios:
- "Run the suspicious-dns query"
- "Execute the threat-hunting query"
- "Run saved query 'malware-detection'"

## What This Skill Does

Retrieves a saved query by name from hive storage and executes it, returning the query results.

## When to Create vs Run Queries

**Use this function** for running existing saved queries.

**Use `generate-lcql-query`** to create new queries from natural language:
```
mcp__plugin_lc-essentials_limacharlie__generate_lcql_query(
  oid="[your-oid]",
  query="find suspicious PowerShell executions"
)
```
Then save it with `set-saved-query` for reuse.

## Required Information

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list-user-orgs` first.

- **oid**: Organization ID (UUID)
- **query_name**: Name of the saved query to execute

Optional:
- **limit**: Maximum results to return

## How to Use

### Step 1: Retrieve Query

Get the saved query definition:
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/hive/query/[oid]/[query-name]/data"
)
```

### Step 2: Execute Query

Execute the LCQL query string:
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="replay",
  method="POST",
  path="/",
  body={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "query": "[lcql-from-saved-query]",
    "limit_event": 1000,
    "event_source": {"stream": "event", "sensor_events": {"cursor": "-"}}
  }
)
```

### Step 3: Handle Response

**Success (200):**
```json
{
  "status_code": 200,
  "body": {
    "results": [...],
    "cursor": "",
    "stats": {...}
  }
}
```

**Common Errors:**
- **404 Not Found**: Query doesn't exist
- **400 Bad Request**: Invalid LCQL syntax in saved query
- **403 Forbidden**: Insufficient permissions

## Example Usage

User: "Run the suspicious-dns query"

**Step 1: Get query**
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="...",
  endpoint="api",
  method="GET",
  path="/v1/hive/query/{oid}/suspicious-dns/data"
)
// Returns: {"query": "-24h | * | DNS_REQUEST | ..."}
```

**Step 2: Execute**
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="...",
  endpoint="replay",
  method="POST",
  path="/",
  body={...}
)
```

**Step 3: Present results**
```
Executed Query: suspicious-dns
Results: 12 events found
...
```

## Related Functions

- `generate-lcql-query` - AI-assisted query generation for new queries
- `list-saved-queries` - List available saved queries
- `get-saved-query` - Get query definition without executing
- `set-saved-query` - Save a new query for reuse
- `delete-saved-query` - Remove a saved query
- `run-lcql-query` - Execute ad-hoc LCQL queries

## Reference

For the API implementation, see [CALLING_API.md](../../CALLING_API.md).

For LCQL syntax, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
