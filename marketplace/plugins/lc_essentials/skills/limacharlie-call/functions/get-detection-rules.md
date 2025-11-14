
# Get Detection Rules

Retrieve all Detection and Response (D&R) rules from all namespaces to get a complete view of your detection stack.

## When to Use

Use this skill when the user needs to:
- View all D&R rules across the entire organization
- Audit detection coverage and rule configurations
- Export the complete detection stack for backup
- Review rules from all namespaces (general, managed, service)
- Analyze detection logic and response actions
- Compare rules across different namespaces
- Generate compliance or security reports

Common scenarios:
- "Show me all D&R rules in the organization"
- "Export all detection rules for audit"
- "What detection rules are currently active?"
- "Give me a complete list of rules across all namespaces"

## What This Skill Does

This skill retrieves all D&R rules from every namespace in the organization, including general (custom rules), managed (LC-maintained rules), and service (extension-provided rules). It returns the complete rule configurations including detection logic, response actions, metadata, and status. This provides a comprehensive view of your entire detection stack.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No other parameters needed - this returns all rules from all namespaces.

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
  path="/rules/[organization-id]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/rules/{oid}` where `{oid}` is the organization ID
- No query parameters needed (to get all namespaces)
- No request body needed

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "rule-name-1": {
      "name": "rule-name-1",
      "namespace": "general",
      "detect": {
        "event": "NEW_PROCESS",
        "op": "is",
        "path": "event/FILE_PATH",
        "value": "cmd.exe"
      },
      "respond": [
        {
          "action": "report",
          "name": "suspicious_cmd_execution"
        }
      ],
      "is_enabled": true
    },
    "rule-name-2": {
      "name": "rule-name-2",
      "namespace": "managed",
      "detect": {...},
      "respond": [...],
      "is_enabled": true
    }
  }
}
```

**Success (200-299):**
- Status code 200 indicates successful retrieval
- Response is a dictionary keyed by rule name
- Each rule object contains:
  - `name`: Rule identifier
  - `namespace`: Where the rule lives (general, managed, service)
  - `detect`: Detection logic (event matching criteria)
  - `respond`: Response actions (array of actions)
  - `is_enabled`: Whether the rule is active
  - Other metadata (tags, target, etc.)
- Rules from all namespaces are included in the response
- Empty object means no rules are configured

**Common Errors:**
- **403 Forbidden**: Insufficient permissions - requires rule read permissions
- **404 Not Found**: Organization not found - verify OID
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display total count of rules
- Group rules by namespace for clarity
- For each rule, show:
  - Rule name and namespace
  - Detection event type and logic
  - Response actions
  - Enabled/disabled status
  - Target sensors (if specified)
- Highlight any disabled rules
- Suggest filtering by namespace if the list is large
- Offer to export in different formats if requested

## Example Usage

### Example 1: Audit All Detection Rules

User request: "Show me all D&R rules in the organization"

Steps:
1. Call API to retrieve all rules:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "detect-suspicious-cmd": {
      "name": "detect-suspicious-cmd",
      "namespace": "general",
      "detect": {
        "event": "NEW_PROCESS",
        "op": "is",
        "path": "event/FILE_PATH",
        "value": "cmd.exe"
      },
      "respond": [{"action": "report", "name": "suspicious_cmd"}],
      "is_enabled": true
    },
    "ransomware-behavior": {
      "name": "ransomware-behavior",
      "namespace": "managed",
      "detect": {...},
      "respond": [...],
      "is_enabled": true
    }
  }
}
```

Response to user:
"Found 2 D&R rules in your organization:

**General Namespace (Custom Rules): 1**
1. detect-suspicious-cmd (enabled)
   - Detects: NEW_PROCESS events for cmd.exe
   - Action: Report as 'suspicious_cmd'

**Managed Namespace (LC-Maintained): 1**
1. ransomware-behavior (enabled)
   - Detects: Ransomware-like behaviors
   - Actions: Report and respond

All rules are currently enabled and active."

### Example 2: Export Rules for Compliance

User request: "Export all detection rules for our security audit"

Steps:
1. Call API to get all rules:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab"
)
```

Expected response: (same as above)

Response to user:
"Retrieved all detection rules from your organization. Here's the complete rule configuration for your audit:

[Present full JSON or formatted output]

Summary:
- Total rules: 2
- General namespace: 1 rule
- Managed namespace: 1 rule
- All rules enabled: Yes

This data includes complete detection logic, response actions, and metadata for compliance review."

## Additional Notes

- This retrieves rules from ALL namespaces (general, managed, service, etc.)
- General namespace contains custom rules created by users
- Managed namespace contains LC-maintained detection rules from extensions
- Service namespace contains rules from integrated services
- Rules are returned as a dictionary keyed by rule name (unique within namespace)
- Rule names can be the same across namespaces (namespace + name = unique)
- The `detect` field contains the detection logic (event matching)
- The `respond` field is an array of response actions
- `is_enabled: false` means the rule exists but won't trigger
- Rules with `target` fields only apply to specific sensors
- Use `list-dr-general-rules` to see only custom rules
- This is read-only - it doesn't modify rules
- Large organizations may have hundreds of rules
- Consider filtering by namespace for focused analysis
- This is useful for backup, migration, and compliance purposes
- Rules include metadata like TTL, tags, and targeting information

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRules method without namespace filter)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (get_detection_rules)
