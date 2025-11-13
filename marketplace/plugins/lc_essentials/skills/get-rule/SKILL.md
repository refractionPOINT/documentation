---
name: get-rule
description: Get a specific rule by name from a Hive in a LimaCharlie organization. Use this skill when users need to view, inspect, or retrieve detailed rule definition from any Hive like D&R rules (dr-general, dr-managed), false positive rules (fp), or other custom Hive types. Generic Hive operation that works with any Hive name and rule name. Returns complete rule definition, enabled status, tags, comments, and metadata.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get Rule from Hive

Retrieves a specific rule by name from a Hive in a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Get detailed definition for a specific D&R rule
- View a false positive rule's filter logic
- Inspect rule configuration from any Hive
- Check if a specific rule exists
- Review rule metadata (creation date, last author, etc.)
- Understand what a rule does

Common scenarios:
- "Show me the 'suspicious-dns' D&R rule from general namespace"
- "What does the 'chrome-fp' false positive rule do?"
- "Get the rule named 'malware-detection' from dr-general"
- "Is the 'ransomware-behavior' rule configured?"

## What This Skill Does

This skill retrieves a single rule record from a specified Hive in the LimaCharlie Hive system by its name. It's a generic operation that works with any Hive name and rule name. The skill calls the Hive API with the specified Hive name, "global" partition, and rule name as the key. The response includes the complete rule definition, user metadata (enabled, tags, comments), and system metadata (audit trail).

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **hive_name**: The name of the Hive containing the rule (required)
  - Common values: `dr-general`, `dr-managed`, `fp`
- **rule_name**: The name of the rule to retrieve (required)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Hive name (string, determines which Hive to query)
3. Rule name (string, must be exact match)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/hive/[hive-name]/global/[rule-name]/data"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/{hive_name}/global/{rule_name}/data`
  - Replace `{hive_name}` with the Hive name
  - Replace `{rule_name}` with the URL-encoded rule name
  - The `/data` suffix retrieves both data and metadata
- Query parameters: None
- Body: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "data": {
      "detect": {
        "event": "DNS_REQUEST",
        "op": "and",
        "rules": [
          {"op": "contains", "path": "event/DOMAIN_NAME", "value": "malicious"}
        ]
      },
      "respond": [
        {"action": "report", "name": "malicious_dns"}
      ]
    },
    "sys_mtd": {
      "etag": "abc123...",
      "created_by": "user@example.com",
      "created_at": 1234567890,
      "last_author": "admin@example.com",
      "last_mod": 1234567899,
      "guid": "unique-id-123"
    },
    "usr_mtd": {
      "enabled": true,
      "expiry": 0,
      "tags": ["network", "dns", "threat"],
      "comment": "Detects malicious DNS requests"
    }
  }
}
```

**Success (200-299):**
- The `data` field contains the complete rule definition
- For D&R rules: includes `detect` and `respond` sections
- For FP rules: includes filter/match logic
- The `usr_mtd` field shows user-controlled metadata
- The `sys_mtd` field shows system metadata
- Present the rule details to the user in a readable format

**Common Errors:**
- **400 Bad Request**: Invalid rule name format
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: The rule doesn't exist in this Hive
- **500 Server Error**: Backend issue - advise retry

### Step 4: Format the Response

Present the result to the user:
- Show the rule name, Hive name, and enabled status prominently
- For D&R rules: explain the detection logic and response actions
- For FP rules: explain what false positives are being filtered
- Display relevant metadata like creation date and last modification
- Note any tags or comments
- Explain what the rule does in simple terms

## Example Usage

### Example 1: Get a D&R rule

User request: "Show me the 'suspicious-dns' D&R rule from general namespace"

Steps:
1. Get the organization ID from context
2. Use hive_name "dr-general" and rule_name "suspicious-dns"
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/dr-general/global/suspicious-dns/data"
)
```

Expected response contains the D&R rule definition with detect and respond sections.

Format the output explaining:
- Rule: suspicious-dns (Enabled)
- Hive: dr-general
- Detects: DNS requests containing "malicious" in domain name
- Responds: Reports as "malicious_dns" detection
- Last Modified: [date] by admin@example.com

### Example 2: Get a false positive rule

User request: "What does the 'chrome-fp' false positive rule do?"

Steps:
1. Get organization ID
2. Use hive_name "fp" and rule_name "chrome-fp"
3. Call API with path "/hive/fp/global/chrome-fp/data"

Expected response shows the FP rule filter logic.

## Additional Notes

- **Hive Types**: Different Hives store different types of rules
- **Rule Structure**: The `data` field structure varies by Hive type
- Rule names are case-sensitive - use exact name from list-rules
- The `enabled` field controls whether the rule is active
- Use `list-rules` first if you don't know the exact rule name
- Managed rules (dr-managed) are typically read-only
- Some rules may have complex nested logic in the detect section

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go` (Get method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/generic_hive.go`
