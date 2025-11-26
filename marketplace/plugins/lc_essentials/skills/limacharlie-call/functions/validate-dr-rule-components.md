
# Validate D&R Rule Components

Validate Detection & Response (D&R) rule detection and response components using server-side validation via the Replay service.

## When to Use

Use this skill when the user needs to:
- Verify D&R rule syntax before deploying
- Check if detection logic is properly formatted
- Validate response actions before creating rules
- Debug syntax errors in D&R rules
- Validate existing rules by name
- Test rule components against the organization's D&R schema
- Catch errors early before deployment
- Ensure rule components are valid for server-side execution

Common scenarios:
- "Validate this D&R detection component before I deploy it"
- "Check if my response actions are formatted correctly"
- "Is this detection logic valid?"
- "Verify my D&R rule syntax"
- "Validate my existing rule 'detect-powershell'"
- "Check this rule for errors before deploying"

## What This Skill Does

This skill performs server-side validation of D&R rule components using the LimaCharlie Replay service. It validates detection and response components against your organization's D&R rule schema, checking for valid event types, operators, field paths, and response actions. This is more comprehensive than basic syntax checking - it validates against the actual platform schema used for rule execution.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first.

- **oid**: Organization ID (required for server-side validation)
- **detect**: Detection component object (required if `rule_name` not provided)
- **rule_name**: Name of existing rule to validate (required if `detect` not provided)

Optional parameters:
- **namespace**: Rule namespace - 'general', 'managed', or 'service' (default: 'general')
- **respond**: Response component array to validate

**Validation Rules:**
- Either `rule_name` OR `detect` must be provided

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Either detection component in object/dictionary format OR existing rule name
3. Optional response component in array format

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="validate_dr_rule_components",
  parameters={
    "oid": "[organization-id]",
    "detect": {"event": "NEW_PROCESS", "op": "contains", "path": "event/COMMAND_LINE", "value": "powershell"},
    "respond": [{"action": "report", "name": "powershell_detected"}]
  }
)
```

**Tool Details:**
- Tool name: `validate_dr_rule_components`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - Either `rule_name` OR `detect`
- Optional parameters:
  - `namespace`: 'general', 'managed', or 'service' (default: 'general')
  - `respond`: Response actions array

**How it works:**
- Sends components to the LimaCharlie Replay service for validation
- Validates detection component against org's D&R rule schema
- Checks event types, operators, field paths are valid
- Validates response actions and their parameters
- Returns validation result with detailed error messages

**Valid Operators:**
- `and`, `or` - Boolean logic
- `exists` - Field existence check
- `is` - Exact match
- `contains` - Substring match
- `starts with`, `ends with` - Prefix/suffix match
- `matches` - Regex match
- `is greater than`, `is less than` - Numeric comparison
- `length is` - String length check
- `lookup` - Lookup table match

**Valid Actions:**
- `report` - Create detection report
- `task` - Execute sensor task
- `add tag`, `remove tag` - Sensor tagging
- `isolate network`, `rejoin network` - Network isolation
- `service request` - Service integration

### Step 3: Handle the Response

**Validation Success:**
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

**Validation Success (existing rule):**
```json
{
  "valid": true,
  "message": "Rule 'detect-powershell' in namespace 'general' is valid",
  "rule_name": "detect-powershell",
  "namespace": "general"
}
```

**Validation Failure:**
```json
{
  "valid": false,
  "error": "Invalid operator 'equals' in detection component. Valid operators are: and, or, exists, is, contains, starts with, ends with, matches, is greater than, is less than, length is, lookup"
}
```

**Common Errors:**
- Missing 'op' field in detection component
- Invalid operator in detection logic
- Invalid event type for the organization
- Invalid field path
- Missing 'action' field in response component
- Invalid action type in response
- Rule not found (when using `rule_name`)

### Step 4: Format the Response

Present the result to the user:
- Clearly indicate if validation passed or failed
- Display specific error messages if validation failed
- Explain what needs to be fixed
- Suggest corrections for common errors
- For existing rules, show the rule name and namespace validated

## Example Usage

### Example 1: Validate Detection Component

User request: "Validate this detection logic before I deploy it"

Steps:
1. Get organization ID
2. Get detection component from user
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="validate_dr_rule_components",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "powershell"
    }
  }
)
```

Expected response:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

### Example 2: Validate Detection and Response

User request: "Check if my complete D&R rule is valid"

```
mcp__limacharlie__lc_call_tool(
  tool_name="validate_dr_rule_components",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "and",
      "rules": [
        {"op": "contains", "path": "event/FILE_PATH", "value": "powershell"},
        {"op": "contains", "path": "event/COMMAND_LINE", "value": "-enc"}
      ]
    },
    "respond": [
      {"action": "report", "name": "encoded_powershell"},
      {"action": "isolate network"}
    ]
  }
)
```

### Example 3: Validate Existing Rule by Name

User request: "Is my 'detect-ransomware' rule valid?"

```
mcp__limacharlie__lc_call_tool(
  tool_name="validate_dr_rule_components",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "rule_name": "detect-ransomware",
    "namespace": "general"
  }
)
```

Expected response:
```json
{
  "valid": true,
  "message": "Rule 'detect-ransomware' in namespace 'general' is valid",
  "rule_name": "detect-ransomware",
  "namespace": "general"
}
```

### Example 4: Catch Invalid Operator

User request: "Is this detection valid?"

```
mcp__limacharlie__lc_call_tool(
  tool_name="validate_dr_rule_components",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "equals",
      "path": "event/COMMAND_LINE",
      "value": "powershell"
    }
  }
)
```

Expected response:
```json
{
  "valid": false,
  "error": "Invalid operator 'equals'. Valid operators are: and, or, exists, is, contains, starts with, ends with, matches, is greater than, is less than, length is, lookup"
}
```

## Additional Notes

- **Server-Side Validation**: Uses LimaCharlie Replay service for accurate validation
- **OID Required**: Validation runs against your organization's schema
- **Comprehensive Checks**: Validates event types, operators, paths, and actions
- **Existing Rules**: Can validate deployed rules by name
- **Namespace Support**: Validate rules from general, managed, or service namespaces
- **Schema Validation**: Checks against the actual D&R schema used for execution
- **Error Details**: Provides specific error messages for debugging
- **Detection Validation**:
  - Validates 'op' field is present and valid
  - Checks operator against known valid operators
  - Validates nested rules for 'and'/'or' operators
  - Checks field paths are valid
- **Response Validation**:
  - Validates 'action' field is present and valid
  - Checks action types against known valid actions
  - Validates action parameters
- **Use Before Deployment**: Catch errors before deploying to production
- **Combine with Testing**: Follow with `test_dr_rule_events` or `replay_dr_rule` for functional testing
- **AI Integration**: Use after `generate_dr_rule_detection` to validate generated rules

## Related Functions

- `test_dr_rule_events` - Test rules against inline events
- `replay_dr_rule` - Test rules against historical data
- `generate_dr_rule_detection` - AI-generate detection logic
- `generate_dr_rule_respond` - AI-generate response actions
- `set_dr_general_rule` - Deploy validated rules

## Reference

For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/validation.go`

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
