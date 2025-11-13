---
name: set-saved-query
description: Create or update a saved LCQL query in the organization's hive storage. Store queries with names, descriptions, tags for organization. Use to save frequently used queries, build query library, standardize investigations, share queries across team, and create reusable hunting logic.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Save LCQL Query

Create or update a saved LCQL query for future use.

## When to Use

Use this skill when the user needs to:
- Save a frequently used query
- Create reusable hunting queries
- Build organization query library
- Standardize investigation procedures
- Share queries with team
- Document validated search logic

Common scenarios:
- "Save this query as 'suspicious-dns'"
- "Create a saved query for PowerShell hunting"
- "Store this query with description"
- "Save this search for later use"
- "Create a query named 'compliance-check'"

## What This Skill Does

This skill saves an LCQL query string to hive storage with a name, optional description, and tags for organization.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **query_name**: Name for the saved query
- **lcql_query**: The LCQL query string to save

Optional:
- **description**: Description of what the query does

## How to Use

### Step 1: Prepare Query Data

Format query data:
```json
{
  "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'",
  "description": "Find DNS requests to Russian domains"
}
```

### Step 2: Call API

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/hive/query/global",
  body={
    "key": "suspicious-dns",
    "data": {
      "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'",
      "description": "Find DNS requests to Russian domains"
    },
    "enabled": true,
    "tags": ["threat-hunting", "dns"],
    "comment": "Monitor for suspicious domains"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/hive/query/global`
- Body:
  - `key`: Query name (unique identifier)
  - `data`: Query object with LCQL and description
  - `enabled`: Boolean (default true)
  - `tags`: Array of tags for organization
  - `comment`: Optional comment

### Step 3: Handle Response

```json
{
  "status_code": 200,
  "body": {
    "success": true,
    "guid": "query-guid-123",
    "message": "Successfully saved query 'suspicious-dns'"
  }
}
```

### Step 4: Format Response

```
Query Saved Successfully!

Name: suspicious-dns
Description: Find DNS requests to Russian domains
Tags: threat-hunting, dns

LCQL:
-24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'

You can now run this query using:
- run-saved-query with name "suspicious-dns"
```

## Example Usage

### Example 1: Save threat hunting query

User: "Save this query as 'powershell-encoded'"

```
LCQL: -7d | * | NEW_PROCESS | event.COMMAND_LINE contains 'encodedCommand'
Description: Detect encoded PowerShell commands
Tags: threat-hunting, powershell
```

Save with name, description, and tags.

### Example 2: Update existing query

User: "Update the suspicious-dns query to include .cn domains"

Same API call with updated LCQL - overwrites existing query.

## Additional Notes

- Query names must be unique within organization
- Overwrites existing query with same name
- LCQL syntax is not validated on save
- Test query with run-lcql-query before saving
- Tags help organize query library
- Description should explain query purpose
- Consider naming conventions for team queries
- Can include timeframes in saved queries
- Query modifications are tracked via metadata

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/hive.go`
MCP: `../lc-mcp-server/internal/tools/hive/saved_queries.go`
