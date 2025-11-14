
# Set Managed D&R Rule

Create a new managed Detection & Response rule or update an existing one in the managed namespace.

## When to Use

Use this skill when the user needs to:
- Create a new managed D&R rule
- Update an existing managed D&R rule
- Modify detection logic in a managed rule
- Change response actions for a managed rule
- Import detection rules into the managed namespace

Common scenarios:
- Rule creation: "Create a new managed rule to detect credential access"
- Rule update: "Update the 'lateral_movement' managed rule with new detection logic"
- Configuration: "Add a report action to managed rule 'suspicious_activity'"
- Automation: "Import this detection rule as a managed rule"

## What This Skill Does

This skill creates or updates a Detection & Response rule in the 'managed' namespace. It takes a rule name and configuration (detection logic and response actions) and saves it to the organization. If a rule with the same name exists, it will be replaced (updated). The rule is enabled by default.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Name for the rule (unique within managed namespace)
- **rule_content**: Rule configuration object containing:
  - **detect**: Detection component (required) - defines what to detect
  - **respond**: Response actions (optional) - defines what actions to take

### Detection Component Structure

The `detect` field must contain:
- **op**: Operation type (and, or, is, contains, exists, etc.)
- **path**: Event field path (for field operations)
- **value**: Value to match (for comparison operations)
- **rules**: Array of sub-rules (for and/or operations)

### Response Actions Structure

The `respond` field is an array of action objects:
- **action**: Action type (report, task, add tag, remove tag, isolate network, etc.)
- **name**: Detection name (for report action)
- Additional fields depending on action type

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Rule name (alphanumeric with underscores/hyphens recommended)
3. Valid detection component with required fields
4. Optional but recommended: response actions

### Step 2: Prepare Rule Content

Structure the rule_content as:
```json
{
  "detect": {
    "op": "and",
    "rules": [
      {"op": "is", "path": "event/EVENT_TYPE", "value": "NETWORK_CONNECTIONS"},
      {"op": "contains", "path": "event/COMMAND_LINE", "value": "malicious"}
    ]
  },
  "respond": [
    {"action": "report", "name": "detection_name"}
  ]
}
```

### Step 3: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/rules/[organization-id]",
  body={
    "name": "[rule-name]",
    "namespace": "managed",
    "is_replace": true,
    "is_enabled": true,
    "detection": "[JSON-encoded-detect-component]",
    "response": "[JSON-encoded-respond-component]"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/rules/{oid}`
- Body fields:
  - `name`: Rule name (string)
  - `namespace`: Must be "managed"
  - `is_replace`: true (update if exists) or false (fail if exists)
  - `is_enabled`: true (active) or false (disabled)
  - `detection`: JSON-encoded string of detect component
  - `response`: JSON-encoded string of respond component

### Step 4: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Rule successfully created or updated
- Confirm to user that rule is active
- Optionally retrieve and display the rule to verify

**Common Errors:**
- **400 Bad Request**: Invalid rule syntax, malformed detection logic, or missing required fields
- **403 Forbidden**: Insufficient permissions - user needs detection engineering write permissions
- **409 Conflict**: Rule already exists and is_replace is false
- **500 Server Error**: API service issue - retry or contact support

### Step 5: Format the Response

Present the result to the user:
- Confirm rule was created or updated
- Show rule name and namespace
- Summarize detection logic in plain language
- List response actions configured
- Mention that rule is enabled and active
- Suggest testing the rule with historical data

## Example Usage

### Example 1: Create new managed rule

User request: "Create a managed rule to detect suspicious PowerShell execution"

Steps:
1. Design detection logic for PowerShell detection
2. Define response action (report)
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "suspicious_powershell",
    "namespace": "managed",
    "is_replace": true,
    "is_enabled": true,
    "detection": "{\"op\":\"and\",\"rules\":[{\"op\":\"is\",\"path\":\"event/EVENT_TYPE\",\"value\":\"NEW_PROCESS\"},{\"op\":\"contains\",\"path\":\"event/COMMAND_LINE\",\"value\":\"powershell\"}]}",
    "response": "[{\"action\":\"report\",\"name\":\"suspicious_powershell_execution\"}]"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

### Example 2: Update existing managed rule

User request: "Update the 'lateral_movement' managed rule to add network isolation response"

Steps:
1. Get current rule configuration (optional, for merging)
2. Prepare updated rule with new response action
3. Call API with is_replace=true
4. Confirm update successful

## Additional Notes

- Rule names must be unique within the managed namespace
- Setting is_replace=true will overwrite existing rules with the same name
- Rules are enabled by default - set is_enabled=false to create disabled rules
- Detection component must be valid D&R syntax or the API will reject it
- The detection and response fields must be JSON-encoded strings in the API body
- Empty respond array is valid (detection-only rule)
- Use the validate-dr-rule-components skill to test rule syntax before creating
- Managed rules are separate from general namespace rules
- To view the created rule, use get-dr-managed-rule
- To delete the rule, use delete-dr-managed-rule
- Rule changes take effect immediately

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go`
For D&R rule syntax, see: https://doc.limacharlie.io/docs/documentation/docs/detection-and-response
