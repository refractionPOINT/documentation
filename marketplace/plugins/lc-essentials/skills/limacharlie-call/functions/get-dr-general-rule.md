
# Get D&R General Rule

Retrieve a specific custom Detection and Response (D&R) rule by name from the general namespace.

## When to Use

Use this skill when the user needs to:
- View the complete configuration of a specific custom rule
- Inspect detection logic and response actions for a rule
- Debug why a rule is or isn't triggering
- Review a rule before modifying it
- Document existing rule configurations
- Verify a rule exists with specific settings
- Export a single rule for sharing or backup

Common scenarios:
- "Show me the configuration for rule 'detect-ransomware'"
- "What does the 'suspicious-powershell' rule detect?"
- "Display the full details of my custom rule"
- "I need to see what actions this rule takes"

## What This Skill Does

This skill retrieves the complete configuration of a specific D&R rule from the general namespace (custom rules). It returns the full rule definition including detection logic, response actions, targeting criteria, enabled status, and all metadata. This is useful for inspecting, documenting, or preparing to modify a rule.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the rule to retrieve (exact match, case-sensitive)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact rule name (case-sensitive, must exist in general namespace)
3. Consider using `list_dr_general_rules` first if unsure of the exact name

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_dr_general_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]"
  }
)
```

**Tool Details:**
- Tool name: `get_dr_general_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `name`: The exact rule name to retrieve

### Step 3: Handle the Response

The tool returns data directly:
```json
{
  "rule-name": {
    "name": "rule-name",
    "namespace": "general",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "powershell -enc"
    },
    "respond": [
      {
        "action": "report",
        "name": "encoded_powershell"
      },
      {
        "action": "add tag",
        "tag": "suspicious",
        "ttl": 86400
      }
    ],
    "is_enabled": true,
    "target": "tag=production"
  }
}
```

**Success:**
- Response contains a single rule object (keyed by rule name)
- Rule object includes:
  - `name`: Rule identifier
  - `namespace`: "general"
  - `detect`: Complete detection logic
  - `respond`: Array of response actions
  - `is_enabled`: Whether rule is active
  - `target`: Sensor targeting (optional)
  - `tags`: Rule categorization (optional)
  - `ttl`: Auto-deletion time (optional)
- Extract the rule object from the dictionary for display

**Common Errors:**
- **404 Not Found**: Rule doesn't exist in general namespace - verify name is correct
- **403 Forbidden**: Insufficient permissions - requires rule read permissions
- **400 Bad Request**: Invalid parameters - verify rule_name format
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Display rule name and namespace
- Show detection logic clearly:
  - Event type being monitored
  - Matching criteria and operators
  - Paths and values checked
- List all response actions with details
- Show targeting criteria if present
- Display enabled/disabled status
- Include any tags, TTL, or metadata
- Format for readability (consider JSON or structured text)

## Example Usage

### Example 1: Inspect Suspicious PowerShell Rule

User request: "Show me the configuration for 'detect-suspicious-powershell' rule"

Steps:
1. Validate the rule name
2. Call tool to retrieve specific rule:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "detect-suspicious-powershell"
  }
)
```

Expected response:
```json
{
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
      {
        "action": "report",
        "name": "encoded_powershell",
        "metadata": {
          "severity": "high"
        }
      },
      {
        "action": "add tag",
        "tag": "suspicious-activity",
        "ttl": 86400
      }
    ],
    "is_enabled": true,
    "target": "platform=windows"
  }
}
```

Response to user:
"**Rule: detect-suspicious-powershell**

Namespace: general (custom rule)
Status: Enabled
Target: Windows platforms only

**Detection Logic:**
- Event: NEW_PROCESS
- Condition: Command line CONTAINS 'powershell -enc'
- Description: Detects encoded PowerShell commands often used by attackers

**Response Actions:**
1. Report detection as 'encoded_powershell' with high severity
2. Tag the sensor with 'suspicious-activity' for 24 hours

This rule monitors for encoded PowerShell execution, a common technique for obfuscating malicious commands."

### Example 2: Rule Not Found

User request: "Show me the 'malware-detection' rule"

Steps:
1. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "malware-detection"
  }
)
```

Expected response:
```json
{
  "error": "Rule not found"
}
```

Response to user:
"The rule 'malware-detection' was not found in the general namespace. It may not exist, could be in a different namespace (managed or service), or the name might be spelled differently. Use list-dr-general-rules to see all available custom rules."

## Additional Notes

- Rule names are case-sensitive - "Rule-Name" and "rule-name" are different
- This only searches the general namespace (custom rules)
- For managed or service rules, use `get_detection_rules` and filter results
- The detection logic uses event types like NEW_PROCESS, DNS_REQUEST, NETWORK_CONNECTIONS
- Operators include: is, contains, starts_with, ends_with, matches (regex), and more
- Response actions can be: report, task, isolate, add tag, webhook, and others
- Multiple response actions execute in sequence when rule triggers
- The `target` field limits which sensors the rule applies to
- `is_enabled: false` means the rule exists but won't trigger
- TTL (time-to-live) causes rules to auto-delete after specified seconds
- Use this before updating a rule to see current configuration
- This is read-only - use `set_dr_general_rule` to modify
- Empty body or 404 means the rule doesn't exist in general namespace
- Consider the rule's target field when troubleshooting why it's not triggering

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRules method with name filter)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (get_dr_general_rule)
