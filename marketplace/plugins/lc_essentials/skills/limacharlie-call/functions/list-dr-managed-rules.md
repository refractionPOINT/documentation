
# List Managed D&R Rules

Retrieve all managed Detection & Response rules from the organization. Managed rules are detection rules stored in the 'managed' namespace.

## When to Use

Use this skill when the user needs to:
- List all managed D&R rules in the organization
- View detection rules from the managed namespace
- Audit or inventory managed detection rules
- Review automated or imported detection rules
- Check what managed detections are currently active

Common scenarios:
- Security audit: "Show me all my managed detection rules"
- Detection review: "What managed D&R rules do I have?"
- Coverage analysis: "List all detection rules in the managed namespace"
- Compliance check: "Display managed detection rules for review"

## What This Skill Does

This skill retrieves all Detection & Response rules from the 'managed' namespace in the organization. Managed rules are typically created through automation, imported from rule packs, or managed by extensions. It calls the LimaCharlie API to fetch these rules and returns a complete list with their configurations.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are required.

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
  path="/v1/rules/[organization-id]",
  query_params={"namespace": "managed"}
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/rules/{oid}`
- Query parameters: `namespace=managed` (filters to managed namespace only)
- Body fields: None (GET request)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "rule-name-1": {
      "name": "rule-name-1",
      "namespace": "managed",
      "detect": {...},
      "respond": [...],
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
- The response body contains a map/dictionary of rules indexed by rule name
- Each rule object includes: name, namespace, detect component, respond actions, and enabled status
- Count the number of rules and present to user
- Display rule names and key information (enabled status, detection types)

**Common Errors:**
- **400 Bad Request**: Invalid organization ID format
- **403 Forbidden**: Insufficient permissions to view rules - user needs detection engineering permissions
- **404 Not Found**: Organization ID does not exist
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show total count of managed rules
- List rule names with their enabled/disabled status
- Optionally summarize detection types or rule purposes
- Highlight any disabled rules that might need attention
- Note if no managed rules exist (empty list is valid)

## Example Usage

### Example 1: List all managed rules

User request: "Show me all my managed detection rules"

Steps:
1. Get organization ID from context
2. Call API with managed namespace filter
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  query_params={"namespace": "managed"}
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "credential_access_detection": {
      "name": "credential_access_detection",
      "namespace": "managed",
      "detect": {"op": "and", "rules": [...]},
      "respond": [{"action": "report", "name": "credential_access"}],
      "is_enabled": true
    },
    "lateral_movement_smb": {
      "name": "lateral_movement_smb",
      "namespace": "managed",
      "detect": {"op": "is", "path": "event/EVENT_TYPE", "value": "NETWORK_CONNECTIONS"},
      "respond": [{"action": "report", "name": "lateral_movement"}],
      "is_enabled": true
    }
  }
}
```

### Example 2: Check managed rule count

User request: "How many managed D&R rules do I have?"

Steps:
1. Call API to list managed rules
2. Count the number of rules in response
3. Report count and optionally show rule names
4. If count is 0, inform user they have no managed rules

## Additional Notes

- Managed namespace rules are separate from general namespace rules
- Managed rules are typically created by extensions, automation, or rule imports
- To see all rules across all namespaces, use the get-detection-rules skill instead
- To view a specific managed rule's full configuration, use the get-dr-managed-rule skill
- To modify managed rules, use set-dr-managed-rule and delete-dr-managed-rule skills
- The response includes both enabled and disabled rules
- Rule names must be unique within the managed namespace

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go`
