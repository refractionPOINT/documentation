
# List Saved Queries

List all saved LCQL queries stored in your organization.

## When to Use

Use this skill when the user needs to:
- See all saved queries
- Discover available pre-built queries
- Review query library
- Find specific saved query by name
- Audit saved query inventory
- Browse hunting query collection

Common scenarios:
- "What saved queries do I have?"
- "List all available queries"
- "Show me saved hunting queries"
- "What queries are tagged 'threat-hunting'?"
- "Find queries created by security-team"

## What This Skill Does

This skill lists all LCQL queries saved in the organization's hive storage, including metadata like tags, comments, and creation info.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID

## How to Use

### Step 1: Call API

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/hive/query/global"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/query/global`
- Uses Hive API for persistent storage

### Step 2: Handle Response

```json
{
  "status_code": 200,
  "body": {
    "suspicious-dns": {
      "data": {
        "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'",
        "description": "Find DNS requests to Russian domains"
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["threat-hunting", "dns"],
        "comment": "Monitor for suspicious domains"
      },
      "sys_mtd": {
        "created_at": 1705000000,
        "created_by": "user@example.com",
        "guid": "query-guid-123"
      }
    }
  }
}
```

### Step 3: Format Response

```
Saved Queries (3 total)

1. suspicious-dns
   Description: Find DNS requests to Russian domains
   Query: -24h | * | DNS_REQUEST | event.DOMAIN_NAME ends with '.ru'
   Tags: threat-hunting, dns
   Created: 2024-01-11 by user@example.com

2. powershell-encoded
   Description: Detect encoded PowerShell commands
   Query: -7d | * | NEW_PROCESS | event.COMMAND_LINE contains 'encodedCommand'
   Tags: threat-hunting, powershell
   Created: 2024-01-15 by security-team@example.com

3. network-anomalies
   ...
```

## Example Usage

User: "What saved queries do I have?"

List all with names, descriptions, and tags.

## Additional Notes

- Queries stored in "query" hive, "global" partition
- Can be tagged for organization
- Include comments and metadata
- Use get-saved-query for full details
- Use run-saved-query to execute

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/hive.go`
MCP: `../lc-mcp-server/internal/tools/hive/saved_queries.go`
