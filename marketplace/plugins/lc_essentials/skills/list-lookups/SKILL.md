---
name: list-lookups
description: List all lookup tables in a LimaCharlie organization with their data and metadata. Use this skill when users need to see enrichment data, threat intelligence feeds, allowlists, blocklists, IP reputation lists, domain lists, hash lists, or any reference data stored in lookup tables. Lookup tables enable D&R rules to make contextual decisions, enrich detections, and correlate events with external data.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Lookups

This skill retrieves all lookup tables in a LimaCharlie organization. Lookup tables store reference data that can be queried in D&R rules, LCQL queries, and other contexts.

## When to Use

Use this skill when the user needs to:
- View all lookup tables and their data
- Audit enrichment data and reference lists
- Check what threat intelligence feeds are loaded
- Review allowlists, blocklists, or reputation lists
- Understand available lookup data for D&R rules
- Verify lookup table names before referencing them
- Inspect lookup table contents

Common scenarios:
- "Show me all lookup tables"
- "What threat intelligence is loaded?"
- "List all allowlists and blocklists"
- "What lookup data is available for enrichment?"
- "Show me the IP reputation lookup table"
- "What reference data can I use in D&R rules?"

## What This Skill Does

This skill calls the LimaCharlie API to retrieve all lookup tables with their complete data and metadata. Lookup tables are key-value stores used for enrichment, correlation, and decision-making in detections and queries.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No other parameters are needed for listing lookup tables.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/hive/lookup/[oid]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/lookup/{oid}` (replace `{oid}` with actual organization ID)
- Query parameters: None
- Body: None (GET request)

Note: Lookup tables are stored in the LimaCharlie Hive system.

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "threat-ips": {
      "data": {
        "1.2.3.4": {"severity": "high", "category": "c2"},
        "5.6.7.8": {"severity": "medium", "category": "spam"}
      },
      "sys_mtd": {
        "created_at": 1234567890,
        "created_by": "user@example.com",
        "last_mod": 1234567890,
        "last_author": "user@example.com",
        "guid": "abc123"
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["threat-intel"],
        "comment": "Known malicious IPs"
      }
    },
    "allowed-domains": {
      "data": {
        "example.com": true,
        "trusted.org": true
      },
      "sys_mtd": {...},
      "usr_mtd": {
        "enabled": true,
        "tags": ["allowlist"],
        "comment": "Trusted domains"
      }
    }
  }
}
```

**Success (200-299):**
- Response body contains a dictionary where keys are lookup table names
- Each lookup table includes:
  - `data`: The actual key-value pairs (lookup data)
  - `sys_mtd`: System metadata (creation, modification, GUID)
  - `usr_mtd`: User metadata (enabled status, tags, comments)
- Present lookup names, sizes, and summaries
- Show sample data if helpful

**Common Errors:**
- **404 Not Found**: Organization doesn't exist or no lookups configured (empty response)
- **403 Forbidden**: Insufficient permissions - user needs read access to lookups
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- List all lookup table names
- Show size (number of entries) for each
- Include metadata (tags, comments, last modified)
- Show sample data or keys for each table
- Group by purpose if tags indicate (threat-intel, allowlist, etc.)
- Note if no lookups are configured (empty result)
- Explain how to use lookups in D&R rules

## Example Usage

### Example 1: List all lookup tables

User request: "Show me all lookup tables in the organization"

Steps:
1. Obtain organization ID
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/lookup/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "malicious-ips": {
      "data": {
        "192.0.2.1": {"severity": "critical", "source": "threat-feed-1"},
        "198.51.100.5": {"severity": "high", "source": "threat-feed-2"},
        "203.0.113.10": {"severity": "medium", "source": "manual"}
      },
      "sys_mtd": {
        "created_at": 1640000000,
        "last_mod": 1641000000
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["threat-intel", "ips"],
        "comment": "Known malicious IP addresses"
      }
    },
    "allowed-hashes": {
      "data": {
        "abc123...": true,
        "def456...": true
      },
      "sys_mtd": {
        "created_at": 1640000000,
        "last_mod": 1640000000
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["allowlist", "hashes"],
        "comment": "Trusted file hashes"
      }
    }
  }
}
```

Format output:
```
Lookup Tables (2 total):

1. malicious-ips (3 entries)
   - Tags: threat-intel, ips
   - Comment: Known malicious IP addresses
   - Last modified: 2022-01-01
   - Status: Enabled
   - Sample entries:
     - 192.0.2.1: severity=critical, source=threat-feed-1
     - 198.51.100.5: severity=high, source=threat-feed-2

2. allowed-hashes (2 entries)
   - Tags: allowlist, hashes
   - Comment: Trusted file hashes
   - Last modified: 2021-12-20
   - Status: Enabled
   - Sample keys: abc123..., def456...

To query these lookups in D&R rules:
  lookup('malicious-ips', event.IP_ADDRESS)
  lookup('allowed-hashes', event.FILE_HASH)
```

### Example 2: No lookups configured

User request: "List lookup tables"

Steps:
1. Call API as above
2. Receive empty response:
```json
{
  "status_code": 200,
  "body": {}
}
```

Format output:
```
No lookup tables are currently configured in this organization.

Lookup tables store reference data for:
- Threat intelligence (malicious IPs, domains, hashes)
- Allowlists and blocklists
- Asset inventories
- User or device metadata
- Any key-value data for enrichment

Lookups can be used in:
- D&R rules: lookup('table-name', key)
- LCQL queries: for enrichment and filtering
- Response actions: for contextual decisions

Create lookup tables using the set-lookup skill.
```

### Example 3: View specific category

User request: "Show me all threat intelligence lookup tables"

Steps:
1. List all lookups
2. Filter by tags or names containing "threat"
3. Format output:
```
Threat Intelligence Lookup Tables (2 found):

1. threat-ips (150 entries)
   - Tags: threat-intel, ips
   - Known malicious IP addresses
   - Updated: 2025-11-12

2. threat-domains (75 entries)
   - Tags: threat-intel, domains
   - Known malicious domains
   - Updated: 2025-11-13

These tables can be used to enrich detections and block known threats.
```

## Additional Notes

- Lookup tables are stored as key-value dictionaries
- Keys and values can be any JSON-serializable data
- Common lookup table uses:
  - **Threat intelligence**: Malicious IPs, domains, hashes, URLs
  - **Allowlists**: Trusted assets, approved software, safe domains
  - **Blocklists**: Banned IPs, blacklisted domains, prohibited apps
  - **Asset data**: Device inventory, user mappings, location data
  - **Enrichment**: GeoIP data, ASN info, domain reputation
- Lookup tables have no size limit but large tables may impact performance
- Use tags to organize lookups by purpose
- Comments provide context for future reference
- Lookups can be enabled/disabled without deletion
- Query lookups in D&R rules: `lookup('table-name', key)`
- Query returns the value if key exists, null if not found
- Lookups are organization-wide (not per-sensor)
- Related skills: `get-lookup` for single table, `set-lookup` to create/update, `delete-lookup` to remove, `query-lookup` to search specific key

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/lookups.go`
