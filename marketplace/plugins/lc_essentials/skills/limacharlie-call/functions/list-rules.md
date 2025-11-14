
# List Rules from Hive

Lists all rules from a specific Hive in a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- List all D&R rules from general or managed namespace
- View false positive rules
- Inventory rules from any Hive
- Audit rule configurations
- Check which rules are enabled or disabled
- Review rule details before modifying them

Common scenarios:
- "Show me all my D&R rules from the general namespace"
- "List my false positive rules"
- "What rules do I have in the dr-managed Hive?"
- "Show all rules from the fp Hive"

## What This Skill Does

This skill retrieves all rule records from a specified Hive in the LimaCharlie Hive system. It's a generic operation that works with any Hive name, commonly used for:
- `dr-general`: General Detection & Response rules
- `dr-managed`: Managed Detection & Response rules
- `fp`: False Positive rules
- Other custom Hive types

The skill calls the Hive API with the specified Hive name and organization ID as the partition to list all rules. Each rule includes its definition, enabled status, tags, comments, and system metadata.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **hive_name**: The name of the Hive to list rules from (required)
  - Common values: `dr-general`, `dr-managed`, `fp`
  - Can be any valid Hive name

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Hive name (string, determines which type of rules to list)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/v1/hive/[hive-name]/{oid}"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/{hive_name}/{oid}`
  - Replace `{hive_name}` with the Hive name (e.g., `dr-general`, `fp`)
  - Replace `{oid}` with the organization ID
- Query parameters: None
- Body: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "rule-name-1": {
      "data": {
        "detect": {
          "event": "DNS_REQUEST",
          "op": "contains",
          "path": "event/DOMAIN_NAME",
          "value": "malicious.com"
        },
        "respond": [
          {"action": "report", "name": "suspicious_dns"}
        ]
      },
      "sys_mtd": {
        "etag": "...",
        "created_by": "user@example.com",
        "created_at": 1234567890,
        "last_author": "user@example.com",
        "last_mod": 1234567899,
        "guid": "..."
      },
      "usr_mtd": {
        "enabled": true,
        "expiry": 0,
        "tags": ["network", "dns"],
        "comment": "Detect malicious DNS queries"
      }
    },
    "rule-name-2": {
      // ... another rule
    }
  }
}
```

**Success (200-299):**
- The response body is an object where each key is a rule name
- Each value contains `data` (rule definition), `sys_mtd` (system metadata), and `usr_mtd` (user metadata)
- For D&R rules: data includes `detect` and `respond` sections
- For FP rules: data includes filter/match conditions
- Present the list of rules with their enabled status and key details
- Count the total number of rules

**Common Errors:**
- **403 Forbidden**: Insufficient permissions - user needs platform_admin or similar role
- **404 Not Found**: The Hive doesn't exist or has no rules
- **500 Server Error**: Rare backend issue - advise user to retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show a summary count of how many rules exist in this Hive
- List each rule name with its enabled status
- Highlight key rule details (detection logic, actions)
- Note any rules with tags or comments
- Show creation and last modification timestamps for audit purposes
- Explain what each rule does in simple terms

## Example Usage

### Example 1: List general D&R rules

User request: "Show me all my D&R rules from the general namespace"

Steps:
1. Get the organization ID from context
2. Use hive_name "dr-general"
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/hive/dr-general/global"
)
```

Expected response contains all general D&R rules.

Format the output showing:
- Total: X D&R rules in general namespace
- List each rule with detection summary and response actions

### Example 2: List false positive rules

User request: "List my false positive rules"

Steps:
1. Get organization ID
2. Use hive_name "fp"
3. Call API with path "/hive/fp/global"

The response shows all FP rules that filter out false detections.

### Example 3: List managed D&R rules

User request: "What managed D&R rules do I have?"

Steps:
1. Get organization ID
2. Use hive_name "dr-managed"
3. Call API with path "/hive/dr-managed/global"

The response shows all managed D&R rules (typically from LC service or subscriptions).

## Additional Notes

- **Hive Types**: Different Hives store different types of rules:
  - `dr-general`: User-created D&R rules
  - `dr-managed`: Managed D&R rules (from LC service)
  - `fp`: False positive filtering rules
  - Custom Hives may exist for specific purposes
- **Rule Structure**: The `data` field structure varies by Hive type:
  - D&R rules have `detect` and `respond` sections
  - FP rules have filter/match logic
  - Other Hives may have custom structures
- The `enabled` field controls whether the rule is active
- Tags can be used for filtering and organizing rules
- System metadata provides audit trail information
- Empty result (no rules) is valid and means no rules have been created in this Hive yet
- Use the `get-rule` skill to retrieve a specific rule's full definition
- Some Hives may be read-only (managed rules typically cannot be modified directly)

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go` (List method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/generic_hive.go`
