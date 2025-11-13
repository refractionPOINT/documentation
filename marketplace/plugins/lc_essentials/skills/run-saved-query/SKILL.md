---
name: run-saved-query
description: Execute a saved LCQL query by name and return results. Automatically retrieves query definition from hive storage and runs it against historical data. Supports result limiting and pagination. Use to run pre-built queries, execute scheduled searches, run validated hunting queries, and perform repeated investigations.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Run Saved Query

Execute a saved LCQL query by name and return the results.

## When to Use

Use this skill when the user needs to:
- Run a pre-built saved query
- Execute validated hunting queries
- Perform repeated investigations
- Run scheduled or routine searches
- Use organization-standard queries
- Execute queries by name without knowing LCQL

Common scenarios:
- "Run the suspicious-dns query"
- "Execute the threat-hunting query"
- "Run saved query 'malware-detection'"
- "Search using the powershell-encoded query"
- "Run our standard compliance query"

## What This Skill Does

This skill retrieves a saved query by name from hive storage and executes it, returning the query results.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **query_name**: Name of the saved query to execute

Optional:
- **limit**: Maximum number of results to return

## How to Use

### Step 1: Retrieve Query

First, get the saved query:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/query/global/suspicious-dns/data"
)
```

### Step 2: Execute Query

Then execute the LCQL query string from the saved query:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="https://replay.limacharlie.io/",
  body={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'",
    "limit_event": 1000,
    "event_source": {"stream": "event", "sensor_events": {"cursor": "-"}}
  }
)
```

**API Details:**
- First GET from `/hive/query/global/{query_name}/data`
- Then POST to replay service with query string
- Combines hive storage retrieval with LCQL execution

### Step 3: Handle Response

Query results follow standard LCQL response format:
```json
{
  "status_code": 200,
  "body": {
    "results": [
      {
        "event": {...},
        "routing": {...}
      }
    ],
    "cursor": "",
    "stats": {...}
  }
}
```

### Step 4: Format Response

```
Executed Query: suspicious-dns
Description: Find DNS requests to Russian domains

Results: 12 events found

1. [2024-01-20 14:22:15] DNS_REQUEST on SERVER01
   Domain: malware.ru
   Response: 203.0.113.50

2. [2024-01-20 14:45:30] DNS_REQUEST on WORKSTATION-05
   Domain: phishing.ru
   Response: 203.0.113.51

...

Query Stats:
- Events searched: 50,000
- Results returned: 12
- Execution time: 1.5s
```

## Example Usage

### Example 1: Run threat hunting query

User: "Run the suspicious-dns query"

Steps:
1. Get query definition from hive
2. Execute LCQL query
3. Format and display results

### Example 2: Run with limit

User: "Run the malware-detection query, show top 20 results"

Add limit parameter when executing query.

## Additional Notes

- Query must exist in hive storage
- Uses query's LCQL string directly
- Respects query metadata (tags, description)
- Can apply additional limits at runtime
- Returns standard LCQL results
- Query definition is not modified
- Use set-saved-query to create new queries
- Use delete-saved-query to remove queries

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/hive.go` and `query.go`
MCP: `../lc-mcp-server/internal/tools/hive/saved_queries.go`
