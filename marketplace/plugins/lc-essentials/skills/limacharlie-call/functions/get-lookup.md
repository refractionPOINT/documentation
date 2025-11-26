
# Get Lookup

This skill retrieves a specific lookup table with all its data and metadata from a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- View the contents of a specific lookup table
- Inspect threat intelligence data
- Review allowlist or blocklist entries
- Check what keys and values are in a lookup
- Audit enrichment data
- Verify lookup table contents before use
- Export lookup data for analysis

Common scenarios:
- "Show me the malicious-ips lookup table"
- "What's in the allowed-domains lookup?"
- "Get the threat intelligence feed data"
- "Display the contents of the user-mapping lookup"
- "Show me all entries in the blocklist"

## What This Skill Does

This skill calls the LimaCharlie API to retrieve a specific lookup table with its complete data and metadata. The response includes all key-value pairs and associated metadata.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the lookup table to retrieve

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact lookup table name (case-sensitive)

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_lookup",
  parameters={
    "oid": "[organization-id]",
    "name": "[lookup-name]"
  }
)
```

**API Details:**
- Tool: `get_lookup`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Name of the lookup table to retrieve

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "data": {
    "key1": "value1",
    "key2": {"nested": "data"},
    "key3": ["list", "of", "values"]
  },
  "sys_mtd": {
    "created_at": 1234567890,
    "created_by": "user@example.com",
    "last_mod": 1234567890,
    "last_author": "user@example.com",
    "etag": "abc123",
    "guid": "def456"
  },
  "usr_mtd": {
    "enabled": true,
    "tags": ["threat-intel"],
    "comment": "Known malicious IPs",
    "expiry": 0
  }
}
```

**Success:**
- Lookup data is in `data` as key-value pairs
- System metadata in `sys_mtd` (creation, modification times)
- User metadata in `usr_mtd` (enabled status, tags, comments)
- Present data in readable format
- Show metadata for context

**Common Errors:**
- **404 Not Found**: Lookup table with this name doesn't exist - verify exact name
- **403 Forbidden**: Insufficient permissions - user needs read access to lookups
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Show lookup table name and description (from comment)
- Display number of entries
- List all key-value pairs (or sample if very large)
- Include metadata (created, modified, tags, enabled status)
- Explain how to use this lookup in D&R rules
- Note if table is disabled or has expiry set

## Example Usage

### Example 1: Get malicious IPs lookup

User request: "Show me the malicious-ips lookup table"

Steps:
1. Confirm lookup name: "malicious-ips"
2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "malicious-ips"
  }
)
```

Expected response:
```json
{
  "data": {
    "192.0.2.1": {
      "severity": "critical",
      "category": "c2",
      "source": "threat-feed-1",
      "first_seen": 1640000000
    },
    "198.51.100.5": {
      "severity": "high",
      "category": "phishing",
      "source": "threat-feed-2",
      "first_seen": 1641000000
    },
    "203.0.113.10": {
      "severity": "medium",
      "category": "spam",
      "source": "manual",
      "first_seen": 1642000000
    }
  },
  "sys_mtd": {
    "created_at": 1640000000,
    "created_by": "admin@example.com",
    "last_mod": 1642000000,
    "last_author": "admin@example.com",
    "guid": "abc-123-def"
  },
  "usr_mtd": {
    "enabled": true,
    "tags": ["threat-intel", "ips"],
    "comment": "Known malicious IP addresses from threat feeds"
  }
}
```

Format output:
```
Lookup Table: malicious-ips
Description: Known malicious IP addresses from threat feeds
Status: Enabled
Tags: threat-intel, ips

Entries (3 total):

1. 192.0.2.1
   - Severity: critical
   - Category: c2
   - Source: threat-feed-1
   - First seen: 2021-12-20

2. 198.51.100.5
   - Severity: high
   - Category: phishing
   - Source: threat-feed-2
   - First seen: 2022-01-01

3. 203.0.113.10
   - Severity: medium
   - Category: spam
   - Source: manual
   - First seen: 2022-01-12

Metadata:
- Created: 2021-12-20 by admin@example.com
- Last modified: 2022-01-12 by admin@example.com

To use in D&R rules:
  lookup('malicious-ips', event.IP_ADDRESS)

This returns the IP's data (severity, category, etc.) if found, or null if not.
```

### Example 2: Get allowlist lookup

User request: "What's in the allowed-domains lookup?"

Steps:
1. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "allowed-domains"
  }
)
```

Expected response:
```json
{
  "data": {
    "example.com": true,
    "trusted.org": true,
    "corporate.net": true
  },
  "usr_mtd": {
    "enabled": true,
    "tags": ["allowlist"],
    "comment": "Trusted domains for our organization"
  }
}
```

Format output:
```
Lookup Table: allowed-domains
Description: Trusted domains for our organization
Status: Enabled
Tags: allowlist

Trusted Domains (3 total):
- example.com
- trusted.org
- corporate.net

To use in D&R rules to suppress false positives:
  lookup('allowed-domains', event.DOMAIN) = null

This condition is true when the domain is NOT in the allowlist.
```

### Example 3: Lookup not found

User request: "Get the test-lookup table"

Steps:
1. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "test-lookup"
  }
)
```

Expected response:
```json
{
  "error": "Lookup not found"
}
```

Format output:
```
Error: Lookup table "test-lookup" not found.

The lookup may not exist or the name might be incorrect.
Lookup names are case-sensitive.

Would you like me to list all lookup tables to see what's available?
```

## Additional Notes

- Lookup tables can contain any JSON-serializable data
- Values can be simple (strings, numbers, booleans) or complex (objects, arrays)
- Large lookup tables may take time to retrieve
- Common lookup data patterns:
  - **Boolean flags**: `{"key": true}` for simple membership tests
  - **Metadata objects**: `{"key": {"field1": "val1", "field2": "val2"}}`
  - **Arrays**: `{"key": ["item1", "item2"]}`
- Use lookups in D&R rules:
  - `lookup('table-name', key)` returns value or null
  - `lookup('table-name', key) = null` checks if key NOT in table
  - `lookup('table-name', key) != null` checks if key IS in table
  - `lookup('table-name', key).field` accesses nested data
- Lookup table names are case-sensitive
- Disabled lookups can still be retrieved but won't work in queries
- Tags help organize and categorize lookups
- Comments provide description and context
- Related skills: `list_lookups` to see all tables, `set_lookup` to create/update, `query_lookup` to search specific key

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/lookups.go`
