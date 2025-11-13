---
name: list-dr-general-rules
description: List all custom Detection and Response (D&R) rules in the general namespace. View user-created detection rules, audit custom detections, review organization-specific logic, and manage custom rule inventory. General namespace contains all custom rules created by users, not LC-maintained rules.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List D&R General Rules

List all custom Detection and Response (D&R) rules in the general namespace to view user-created detections.

## When to Use

Use this skill when the user needs to:
- View all custom D&R rules created by users
- List organization-specific detection logic
- Audit custom rules separate from managed rules
- Review the general namespace rule inventory
- Find a specific custom rule by browsing
- Export custom rules for backup or migration
- Understand what custom detections are active

Common scenarios:
- "Show me our custom D&R rules"
- "List all rules in the general namespace"
- "What custom detections have we created?"
- "Display user-created detection rules"

## What This Skill Does

This skill retrieves all D&R rules from the general namespace, which contains custom rules created by users in your organization. These are distinct from managed rules (maintained by LimaCharlie) and service rules (provided by extensions). The general namespace is where you create, test, and deploy organization-specific detection logic.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

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
  path="/rules/[organization-id]",
  query_params={
    "namespace": "general"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/rules/{oid}` where `{oid}` is the organization ID
- Query parameters:
  - `namespace`: "general" (filters to general namespace only)
- No request body needed

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "custom-rule-1": {
      "name": "custom-rule-1",
      "namespace": "general",
      "detect": {
        "event": "NEW_PROCESS",
        "op": "contains",
        "path": "event/COMMAND_LINE",
        "value": "powershell"
      },
      "respond": [
        {
          "action": "report",
          "name": "suspicious_powershell"
        }
      ],
      "is_enabled": true
    },
    "custom-rule-2": {
      "name": "custom-rule-2",
      "namespace": "general",
      "detect": {...},
      "respond": [...],
      "is_enabled": false
    }
  }
}
```

**Success (200-299):**
- Status code 200 indicates successful retrieval
- Response is a dictionary keyed by rule name
- Each rule object contains:
  - `name`: Rule identifier
  - `namespace`: "general" for all results
  - `detect`: Detection logic
  - `respond`: Response actions array
  - `is_enabled`: Active status
  - Additional fields: `target`, `tags`, `ttl`, etc.
- Empty object means no custom rules exist

**Common Errors:**
- **403 Forbidden**: Insufficient permissions - requires rule read permissions
- **404 Not Found**: Organization not found - verify OID
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display total count of general namespace rules
- List each rule with key information:
  - Rule name
  - Detection event type and logic
  - Response actions
  - Enabled/disabled status
  - Target sensors (if specified)
- Highlight disabled rules
- Group by detection type or purpose if helpful
- Suggest next actions (view specific rule, create new rule, etc.)

## Example Usage

### Example 1: View All Custom Rules

User request: "Show me all our custom D&R rules"

Steps:
1. Call API to list general namespace rules:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  query_params={
    "namespace": "general"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "detect-suspicious-powershell": {
      "name": "detect-suspicious-powershell",
      "namespace": "general",
      "detect": {
        "event": "NEW_PROCESS",
        "op": "contains",
        "path": "event/COMMAND_LINE",
        "value": "powershell -enc"
      },
      "respond": [
        {"action": "report", "name": "encoded_powershell"}
      ],
      "is_enabled": true
    },
    "block-known-malware": {
      "name": "block-known-malware",
      "namespace": "general",
      "detect": {
        "event": "CODE_IDENTITY",
        "op": "is",
        "path": "event/HASH",
        "value": "abc123..."
      },
      "respond": [
        {"action": "task", "command": "deny_tree"}
      ],
      "is_enabled": true
    }
  }
}
```

Response to user:
"Found 2 custom D&R rules in the general namespace:

1. **detect-suspicious-powershell** (enabled)
   - Detects: Encoded PowerShell commands
   - Event: NEW_PROCESS with 'powershell -enc' in command line
   - Action: Report as 'encoded_powershell'

2. **block-known-malware** (enabled)
   - Detects: Known malware by hash
   - Event: CODE_IDENTITY matching specific hash
   - Action: Kill process tree

Both rules are active and monitoring your environment."

### Example 2: No Custom Rules Configured

User request: "List our custom detection rules"

Steps:
1. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  query_params={
    "namespace": "general"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"No custom D&R rules found in the general namespace. You haven't created any custom detection rules yet. You may be relying on managed rules from LimaCharlie extensions. Use the set-dr-general-rule skill to create your first custom rule."

## Additional Notes

- General namespace contains only custom, user-created rules
- This does NOT include managed rules (from LC) or service rules (from extensions)
- Use `get-detection-rules` to see rules from all namespaces
- Rules in general namespace are fully manageable (create, update, delete)
- Empty response means no custom rules - you may still have managed/service rules
- Rule names must be unique within the general namespace
- `is_enabled: false` means the rule exists but won't trigger detections
- Rules can target specific sensors using the `target` field
- Response actions include: report, task, isolate, add_tag, and more
- Detection logic uses event matching with operators (is, contains, starts_with, etc.)
- This is read-only - use `set-dr-general-rule` to create/update rules
- Use `get-dr-general-rule` to view a specific rule's full configuration
- General namespace rules are included in org exports and backups
- Custom rules persist across sensor deployments and org changes
- Consider organizing rules by purpose (detection, blocking, alerting, etc.)

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRules method with namespace filter)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (list_dr_general_rules)
