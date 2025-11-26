
# Get Managed D&R Rule

Retrieve a specific managed Detection & Response rule by name, including its full configuration and detection logic.

## When to Use

Use this skill when the user needs to:
- View a specific managed D&R rule's configuration
- Inspect detection logic for a managed rule
- Review response actions for a managed rule
- Analyze rule structure for troubleshooting
- Export or document a specific managed rule

Common scenarios:
- Rule inspection: "Show me the 'credential_access_detection' managed rule"
- Troubleshooting: "What does my managed rule 'lateral_movement_smb' detect?"
- Documentation: "Get the configuration for managed rule 'ransomware_behavior'"
- Analysis: "Display the detection logic for managed rule 'suspicious_powershell'"

## What This Skill Does

This skill retrieves a specific Detection & Response rule from the 'managed' namespace by its name. It fetches the complete rule configuration including detection component, response actions, enabled status, and metadata.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the managed rule to retrieve

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Rule name (must be exact match, case-sensitive)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_dr_managed_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]"
  }
)
```

**Tool Details:**
- Tool name: `get_dr_managed_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `name`: The exact rule name to retrieve

### Step 3: Handle the Response

The tool returns data directly:
```json
{
  "requested-rule-name": {
    "name": "requested-rule-name",
    "namespace": "managed",
    "detect": {
      "op": "and",
      "rules": [...]
    },
    "respond": [
      {"action": "report", "name": "detection_name"}
    ],
    "is_enabled": true
  }
}
```

**Success:**
- Parse the response to extract the rule configuration
- Present detection logic, response actions, and metadata
- If rule name not found in results, return "Rule not found" error

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view rules - user needs detection engineering permissions
- **404 Not Found**: Organization ID does not exist or rule name not found
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show rule name and namespace
- Display enabled/disabled status prominently
- Format detection logic in readable structure
- List all response actions clearly
- Include any metadata (author, timestamps if available)
- If rule not found, suggest checking the rule name or listing all managed rules

## Example Usage

### Example 1: Get specific managed rule

User request: "Show me the 'credential_access_detection' managed rule"

Steps:
1. Get organization ID from context
2. Extract rule name: "credential_access_detection"
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_dr_managed_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "credential_access_detection"
  }
)
```

Expected response:
```json
{
  "credential_access_detection": {
    "name": "credential_access_detection",
    "namespace": "managed",
    "detect": {
      "op": "and",
      "rules": [
        {"op": "is", "path": "event/EVENT_TYPE", "value": "CODE_IDENTITY"},
        {"op": "contains", "path": "event/FILE_PATH", "value": "lsass"}
      ]
    },
    "respond": [
      {"action": "report", "name": "credential_access", "metadata": {"severity": "high"}}
    ],
    "is_enabled": true
  }
}
```

### Example 2: Rule not found scenario

User request: "Get managed rule 'nonexistent_rule'"

Steps:
1. Call tool to get managed rule
2. Rule not found in results
3. Return error: "Managed rule 'nonexistent_rule' not found. Use list-dr-managed-rules to see available rules."

## Additional Notes

- Rule names are case-sensitive and must match exactly
- This skill only searches the managed namespace
- For general namespace rules, use the get-dr-general-rule skill instead
- The detection logic uses LimaCharlie's D&R rule syntax with operators like 'and', 'or', 'is', 'contains', etc.
- Response actions can include: report, task, add tag, remove tag, isolate network, etc.
- The is_enabled field indicates if the rule is active
- Some rules may have complex nested detection logic
- To modify this rule, use the set-dr-managed-rule skill
- To delete this rule, use the delete-dr-managed-rule skill

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go`
