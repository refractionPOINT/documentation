
# Query Lookup

This skill queries a specific key in a lookup table to retrieve its associated value. Useful for testing lookups before using them in D&R rules.

## When to Use

Use this skill when the user needs to:
- Check if a specific key exists in a lookup table
- Test lookup functionality before using in D&R rules
- Verify if an IP/domain/hash is in threat intelligence
- Check if an asset is in an allowlist
- Retrieve enrichment data for a specific key
- Validate lookup table contents
- Troubleshoot lookup-based detections

Common scenarios:
- "Is 192.0.2.1 in the malicious-ips lookup?"
- "Check if example.com is in the allowed-domains table"
- "What data is associated with this hash in the threat-hashes lookup?"
- "Test if lookup('user-mapping', 'john.doe') works"
- "Verify the threat intelligence for this IP before creating a rule"

## What This Skill Does

This skill retrieves a lookup table and searches for a specific key, returning the associated value if found or indicating if the key doesn't exist. This simulates the `lookup()` function used in D&R rules.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **lookup_name**: Name of the lookup table to query
- **key**: The key to search for in the lookup table

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact lookup table name (case-sensitive)
3. Key to search for (as string)

### Step 2: Call the API

First, get the lookup table, then extract the key:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/v1/hive/lookup/[oid]/[lookup-name]/data"
)
```

Then search the returned data for the specified key.

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/v1/hive/lookup/{oid}/{lookup_name}/data` (replace placeholders)
- Query parameters: None
- Body: None (GET request)
- Post-processing: Extract key from `body.data[key]`

### Step 3: Handle the Response

The API returns the full lookup table:
```json
{
  "status_code": 200,
  "body": {
    "data": {
      "key1": "value1",
      "key2": {"nested": "data"},
      "searched-key": "found-value"
    }
  }
}
```

Check if the key exists in `body.data`:
- If key exists: Return `body.data[key]`
- If key doesn't exist: Return null/not found

**Success (200-299):**
- Lookup table retrieved successfully
- Search for key in the data dictionary
- Return value if found, null if not found
- Present results clearly

**Common Errors:**
- **404 Not Found**: Lookup table doesn't exist - verify table name
- **403 Forbidden**: Insufficient permissions - user needs read access to lookups
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Show lookup table name and key searched
- If found:
  - Display the value (simple or nested)
  - Show how this would be used in D&R rules
  - Explain accessing nested fields
- If not found:
  - Indicate key doesn't exist
  - Explain this means lookup() would return null
  - Suggest checking the key spelling or table contents

## Example Usage

### Example 1: Query malicious IP

User request: "Is 192.0.2.1 in the malicious-ips lookup?"

Steps:
1. Get lookup table:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/hive/lookup/c7e8f940-1234-5678-abcd-1234567890ab/malicious-ips/data"
)
```

2. Check if "192.0.2.1" exists in data

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "data": {
      "192.0.2.1": {
        "severity": "critical",
        "category": "c2",
        "source": "threat-feed-1"
      },
      "198.51.100.5": {
        "severity": "high",
        "category": "phishing"
      }
    }
  }
}
```

Format output:
```
Query Result: lookup('malicious-ips', '192.0.2.1')

Found: Yes

Value:
{
  "severity": "critical",
  "category": "c2",
  "source": "threat-feed-1"
}

In D&R rules, you can use:
- lookup('malicious-ips', event/IP_ADDRESS) != null  # Check if IP is malicious
- lookup('malicious-ips', event/IP_ADDRESS).severity  # Access severity field
- lookup('malicious-ips', event/IP_ADDRESS).category  # Access category field

Example D&R rule:
  detect:
    event: NETWORK_CONNECTION
    op: is not
    path: lookup('malicious-ips', event/IP_ADDRESS)
    value: null
  respond:
    - action: report
      name: Connection to malicious IP ({{ lookup('malicious-ips', event/IP_ADDRESS).severity }})
```

### Example 2: Query allowlist (key not found)

User request: "Check if suspicious.com is in the allowed-domains lookup"

Steps:
1. Get lookup table
2. Check if "suspicious.com" exists

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "data": {
      "example.com": true,
      "trusted.org": true,
      "corporate.net": true
    }
  }
}
```

Format output:
```
Query Result: lookup('allowed-domains', 'suspicious.com')

Found: No

The domain "suspicious.com" is NOT in the allowed-domains lookup table.

In D&R rules:
- lookup('allowed-domains', 'suspicious.com') returns null
- This means the domain is not allowlisted

To detect domains NOT in allowlist:
  detect:
    event: DNS_REQUEST
    op: is
    path: lookup('allowed-domains', event/DOMAIN_NAME)
    value: null
  respond:
    - action: report

This will trigger for any domain not in the allowlist.
```

### Example 3: Query with nested data

User request: "What data do we have for user john.doe in the user-mapping lookup?"

Steps:
1. Get lookup table
2. Check for "john.doe" key

Expected response with nested data:
```json
{
  "status_code": 200,
  "body": {
    "data": {
      "john.doe": {
        "department": "Engineering",
        "location": "San Francisco",
        "level": "Senior",
        "manager": "jane.smith"
      }
    }
  }
}
```

Format output:
```
Query Result: lookup('user-mapping', 'john.doe')

Found: Yes

Value:
{
  "department": "Engineering",
  "location": "San Francisco",
  "level": "Senior",
  "manager": "jane.smith"
}

In D&R rules, you can access nested fields:
- lookup('user-mapping', event/USER_NAME).department  # Returns "Engineering"
- lookup('user-mapping', event/USER_NAME).location    # Returns "San Francisco"
- lookup('user-mapping', event/USER_NAME).manager     # Returns "jane.smith"

Example enrichment in detection:
  respond:
    - action: report
      name: Suspicious Activity
      metadata:
        user_dept: '{{ lookup("user-mapping", event/USER_NAME).department }}'
        user_location: '{{ lookup("user-mapping", event/USER_NAME).location }}'
```

### Example 4: Lookup table not found

User request: "Query 'test-key' in 'nonexistent-lookup'"

Steps:
1. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/hive/lookup/c7e8f940-1234-5678-abcd-1234567890ab/nonexistent-lookup/data"
)
```

Expected response:
```json
{
  "status_code": 404,
  "error": "Lookup not found"
}
```

Format output:
```
Error: Lookup table "nonexistent-lookup" not found.

The lookup table doesn't exist. Cannot query the key.

Would you like me to:
1. List all available lookup tables?
2. Create this lookup table?
```

## Additional Notes

- This skill simulates the `lookup()` function used in D&R rules
- Lookup keys are case-sensitive
- If key not found, `lookup()` returns null in D&R rules
- Use null checks in D&R rules:
  - `lookup('table', key) != null` checks if key exists
  - `lookup('table', key) = null` checks if key doesn't exist
- Access nested values with dot notation: `lookup('table', key).field`
- Lookups are exact match only (no wildcards or regex)
- Common query patterns:
  - **Threat intel check**: Is this indicator (IP/domain/hash) malicious?
  - **Allowlist check**: Is this asset trusted?
  - **Enrichment**: What metadata exists for this entity?
- Query results help validate lookup tables before using in production rules
- Test different keys to ensure lookup data is complete
- Verify nested structure matches what rules expect
- Related skills: `get-lookup` to see all data, `list-lookups` to see all tables, `set-lookup` to modify data

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/lookups.go`
