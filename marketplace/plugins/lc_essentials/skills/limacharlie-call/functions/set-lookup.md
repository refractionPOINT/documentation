
# Set Lookup

This skill creates or updates a lookup table in LimaCharlie. Lookup tables store reference data that can be queried in D&R rules and LCQL queries.

## When to Use

Use this skill when the user needs to:
- Create a new lookup table
- Load threat intelligence data (malicious IPs, domains, hashes)
- Create allowlists or blocklists
- Store asset inventory data
- Load user or device mappings
- Update existing lookup table data
- Add enrichment data for detections
- Create reference data for D&R rules

Common scenarios:
- "Create a lookup table of malicious IPs from this threat feed"
- "Load this allowlist of trusted domains"
- "Create a lookup for our asset inventory"
- "Update the threat-ips table with new indicators"
- "Store this user-to-department mapping"

## What This Skill Does

This skill calls the LimaCharlie API to create or update a lookup table. The lookup data is provided as a key-value dictionary. If a table with the same name exists, it will be replaced with the new data.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **lookup_name**: Name for the lookup table (alphanumeric, hyphens, underscores)
- **lookup_data**: Dictionary of key-value pairs to store

Optional metadata:
- **tags**: Array of tags for organization
- **comment**: Description of the lookup table
- **enabled**: Enable/disable the lookup (default: true)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Descriptive lookup name (indicates purpose)
3. Valid lookup data (JSON object/dictionary)
4. Optional: Tags and comment for organization

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/hive/lookup/[oid]",
  body={
    "hive": {
      "name": "lookup",
      "partition": "[oid]"
    },
    "name": "lookup-name",
    "record": {
      "data": {
        "key1": "value1",
        "key2": {"nested": "data"}
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["threat-intel"],
        "comment": "Description here"
      }
    }
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/hive/lookup/{oid}` (replace `{oid}` with actual organization ID)
- Query parameters: None
- Body structure (Hive record format):
  - `hive`: Identifies the hive type and partition
    - `name`: "lookup" (hive type)
    - `partition`: Organization ID
  - `name`: Lookup table name
  - `record`: The lookup data and metadata
    - `data`: Dictionary of key-value pairs
    - `usr_mtd`: User metadata (enabled, tags, comment)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "guid": "abc123...",
    "hive": {
      "name": "lookup",
      "partition": "oid"
    },
    "name": "lookup-name"
  }
}
```

**Success (200-299):**
- Lookup table is created/updated and immediately available
- Response includes GUID and confirmation
- Can be queried in D&R rules immediately
- If updating, old data is completely replaced

**Common Errors:**
- **400 Bad Request**: Invalid parameters (missing fields, malformed data)
- **403 Forbidden**: Insufficient permissions - user needs write access to lookups
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Confirm lookup creation/update with name
- Show number of entries loaded
- Explain how to use in D&R rules
- Provide example D&R rule usage
- Note if this updated an existing table

## Example Usage

### Example 1: Create malicious IPs lookup

User request: "Create a lookup table of malicious IPs with this data: 192.0.2.1 (critical), 198.51.100.5 (high)"

Steps:
1. Prepare lookup data as dictionary
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/hive/lookup/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "hive": {
      "name": "lookup",
      "partition": "c7e8f940-1234-5678-abcd-1234567890ab"
    },
    "name": "malicious-ips",
    "record": {
      "data": {
        "192.0.2.1": {
          "severity": "critical",
          "category": "c2"
        },
        "198.51.100.5": {
          "severity": "high",
          "category": "phishing"
        }
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["threat-intel", "ips"],
        "comment": "Known malicious IP addresses"
      }
    }
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "abc-123-def",
    "name": "malicious-ips"
  }
}
```

Format output:
```
Successfully created lookup table "malicious-ips"

Loaded 2 entries:
- 192.0.2.1 (severity: critical, category: c2)
- 198.51.100.5 (severity: high, category: phishing)

Tags: threat-intel, ips
Description: Known malicious IP addresses

To use in D&R rules:
  detect:
    event: NETWORK_CONNECTION
    op: and
    rules:
      - op: exists
        path: event/IP_ADDRESS
      - op: is not
        path: lookup('malicious-ips', event/IP_ADDRESS)
        value: null
  respond:
    - action: report
      name: Connection to malicious IP

This will detect connections to IPs in the lookup table.
You can access the severity with: lookup('malicious-ips', event/IP_ADDRESS).severity
```

### Example 2: Create simple allowlist

User request: "Create an allowlist of trusted domains: example.com, trusted.org, corporate.net"

Steps:
1. Create simple boolean lookup
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/hive/lookup/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "hive": {
      "name": "lookup",
      "partition": "c7e8f940-1234-5678-abcd-1234567890ab"
    },
    "name": "allowed-domains",
    "record": {
      "data": {
        "example.com": true,
        "trusted.org": true,
        "corporate.net": true
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["allowlist"],
        "comment": "Trusted domains for suppressing false positives"
      }
    }
  }
)
```

Format output:
```
Successfully created lookup table "allowed-domains"

Loaded 3 trusted domains:
- example.com
- trusted.org
- corporate.net

Tags: allowlist
Description: Trusted domains for suppressing false positives

To suppress detections for trusted domains in D&R rules:
  detect:
    event: DNS_REQUEST
    op: and
    rules:
      - op: contains
        path: event/DOMAIN_NAME
        value: suspicious-string
      - op: is
        path: lookup('allowed-domains', event/DOMAIN_NAME)
        value: null
  respond:
    - action: report

The second rule ensures the domain is NOT in the allowlist (lookup returns null).
```

### Example 3: Update existing lookup

User request: "Update the threat-ips lookup with new indicators"

Steps:
1. Prepare complete updated data (replaces existing)
2. Call API (same as create)
3. Format output:
```
Successfully updated lookup table "threat-ips"

Updated with 5 entries (replaces previous data).

Note: Setting a lookup completely replaces the old data.
To add entries without replacing, first get the existing lookup,
merge with new data, then set the combined result.

The updated lookup is immediately available for D&R rules.
```

## Additional Notes

- Setting a lookup completely replaces any existing data with that name
- To add entries without replacing: get existing → merge → set combined
- Lookup data can be any JSON-serializable structure
- No size limit on lookup tables, but large tables may impact performance
- Common lookup patterns:
  - **Boolean membership**: `{"key": true}` for simple yes/no
  - **Metadata enrichment**: `{"key": {"field1": "val1", "field2": "val2"}}`
  - **Lists**: `{"key": ["item1", "item2"]}`
- Lookup names should be descriptive and indicate purpose
- Use tags to organize lookups (threat-intel, allowlist, asset-data, etc.)
- Comments provide context for future reference
- Lookups are immediately available after creation
- Use in D&R rules: `lookup('table-name', key)`
- Lookup keys are typically strings but can be any JSON type
- Values can be nested objects accessed via dot notation
- Related skills: `list-lookups` to see all tables, `get-lookup` to view data, `delete-lookup` to remove, `query-lookup` to test lookups

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/lookups.go`
