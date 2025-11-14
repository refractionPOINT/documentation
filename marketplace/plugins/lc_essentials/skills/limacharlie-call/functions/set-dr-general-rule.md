
# Set D&R General Rule

Create or update a custom Detection and Response (D&R) rule in the general namespace to implement custom detection logic.

## When to Use

Use this skill when the user needs to:
- Create a new custom detection rule
- Update an existing custom rule
- Implement organization-specific detection logic
- Define automated response actions for threats
- Target rules to specific sensors or sensor groups
- Build custom security monitoring policies
- Deploy detection rules from templates or examples

Common scenarios:
- "Create a rule to detect suspicious PowerShell activity"
- "Update the ransomware detection rule with new IOCs"
- "Add a detection for unauthorized network connections"
- "Build a rule that isolates sensors when malware is detected"

## What This Skill Does

This skill creates a new D&R rule or updates an existing one in the general namespace (custom rules). It accepts detection logic (what to look for), response actions (what to do when detected), and optional configuration like sensor targeting. If a rule with the same name exists, it will be replaced. Rules become active immediately unless explicitly disabled.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Unique name for the rule (alphanumeric, hyphens, underscores)
- **rule_content**: Object containing detection and response configuration

The rule_content must include:
- **detect**: Detection logic object (event matching criteria)
- **respond**: Response actions array (optional, can be empty)

Optional fields in rule_content:
- **target**: Sensor selector expression to limit rule scope
- **tags**: Array of tags for rule categorization
- **ttl**: Time-to-live in seconds for auto-deletion

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Descriptive rule name (lowercase, hyphens for spaces)
3. Valid detection logic with proper event type and operators
4. Response actions defined (or empty array for detection-only)
5. Consider testing detection logic before deploying

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/rules/[organization-id]",
  body={
    "name": "[rule-name]",
    "namespace": "general",
    "is_replace": true,
    "is_enabled": true,
    "detection": "[json-string-of-detect-logic]",
    "response": "[json-string-of-respond-actions]"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/rules/{oid}` where `{oid}` is the organization ID
- No query parameters needed
- Body fields:
  - `name`: String - rule name (required)
  - `namespace`: "general" (for custom rules)
  - `is_replace`: true (update if exists, false to error on duplicate)
  - `is_enabled`: true/false (whether rule is active)
  - `detection`: JSON string of detect object (required)
  - `response`: JSON string of respond array (optional, can be empty array)
  - `expire_on`: Unix timestamp for TTL (optional)

**Important**: The `detection` and `response` fields must be JSON-encoded strings, not objects.

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Status code 200 indicates the rule was created or updated successfully
- The rule is immediately active if `is_enabled: true`
- Sensors matching the target criteria will start evaluating the rule
- Response actions will execute when the detection logic matches

**Common Errors:**
- **400 Bad Request**: Invalid detection logic or response actions - check syntax
- **403 Forbidden**: Insufficient permissions - requires rule management permissions
- **409 Conflict**: Rule name already exists and `is_replace` is false
- **422 Unprocessable Entity**: Detection logic validation failed - check event types and operators
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the rule was created or updated
- Summarize the detection criteria
- List the response actions
- Mention sensor targeting if specified
- Remind that the rule is now active
- Suggest testing the rule or monitoring for detections
- Provide the rule name for future reference

## Example Usage

### Example 1: Create Encoded PowerShell Detection

User request: "Create a rule to detect and report encoded PowerShell commands"

Steps:
1. Define detection logic for encoded PowerShell
2. Define response action (report)
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "detect-encoded-powershell",
    "namespace": "general",
    "is_replace": true,
    "is_enabled": true,
    "detection": "{\"event\":\"NEW_PROCESS\",\"op\":\"contains\",\"path\":\"event/COMMAND_LINE\",\"value\":\"powershell -enc\"}",
    "response": "[{\"action\":\"report\",\"name\":\"encoded_powershell\"}]"
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
"Successfully created custom D&R rule 'detect-encoded-powershell'.

**Detection:** Monitors NEW_PROCESS events for PowerShell commands with the '-enc' parameter (encoded commands)

**Response:** Reports detections as 'encoded_powershell'

The rule is now active across all sensors. You'll receive alerts when encoded PowerShell execution is detected, which is often used by attackers to obfuscate malicious commands."

### Example 2: Create Rule with Multiple Actions and Targeting

User request: "Create a rule that detects malware by hash, kills the process, isolates the sensor, and only applies to production systems"

Steps:
1. Define detection logic for known malware hash
2. Define multiple response actions
3. Add sensor targeting
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "block-known-malware-prod",
    "namespace": "general",
    "is_replace": true,
    "is_enabled": true,
    "detection": "{\"event\":\"CODE_IDENTITY\",\"op\":\"is\",\"path\":\"event/HASH\",\"value\":\"abc123def456...\"}",
    "response": "[{\"action\":\"report\",\"name\":\"known_malware_detected\"},{\"action\":\"task\",\"command\":\"deny_tree\"},{\"action\":\"isolate\"}]"
  }
)
```

Note: The SDK may handle the target field through rule_content, so check if you need to include it in the detection string or as a separate field.

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Successfully created custom D&R rule 'block-known-malware-prod'.

**Detection:** Identifies known malware by hash (CODE_IDENTITY event)
**Target:** Production sensors only (tag=production)

**Automated Response:**
1. Report as 'known_malware_detected'
2. Kill the process tree
3. Isolate the sensor from network

This rule provides immediate automated containment when known malware executes on production systems. The sensor will be isolated automatically to prevent lateral movement."

## Additional Notes

- Rule names must be unique within the general namespace
- Use descriptive names that indicate what the rule detects
- Set `is_replace: true` to update existing rules, `false` to error on duplicates
- Detection logic requires valid event types (NEW_PROCESS, DNS_REQUEST, etc.)
- Common operators: is, contains, starts_with, ends_with, matches (regex)
- Response actions execute in array order
- Available actions: report, task, isolate, add tag, webhook, and more
- Empty respond array creates a detection-only rule (no automated response)
- Use `target` field to limit rules to specific sensors (e.g., "tag=production")
- Rules are evaluated in real-time as events occur
- Complex detection logic can use AND/OR operators
- Test detection logic with historical data before deploying
- Consider performance impact of complex rules on high-volume events
- Rules persist until explicitly deleted
- Use TTL (expire_on) for temporary rules during investigations
- This replaces the entire rule - partial updates aren't supported
- Validate detection logic syntax before deployment to avoid errors
- Use `get-dr-general-rule` to verify the rule after creation

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRuleAdd method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (set_dr_general_rule)

For D&R rule syntax and examples, see LimaCharlie documentation on Detection and Response rules.
