
# Validate D&R Rule Components

Validate Detection & Response (D&R) rule detection and response components for syntax correctness using client-side validation.

## When to Use

Use this skill when the user needs to:
- Verify D&R rule syntax before deploying
- Check if detection logic is properly formatted
- Validate response actions before creating rules
- Debug syntax errors in D&R rules
- Learn correct D&R rule structure through validation feedback
- Test rule components during development
- Ensure rule components meet structural requirements
- Catch errors early before API deployment

Common scenarios:
- "Validate this D&R detection component before I deploy it"
- "Check if my response actions are formatted correctly"
- "Is this detection logic valid?"
- "Verify my D&R rule syntax"
- "Check this rule for errors before deploying"

## What This Skill Does

This skill performs client-side validation of D&R rule components (detection and response). It checks that the detection component has the required 'op' field and uses valid operators, and that response components have valid 'action' fields. This validation is structural and syntactic only - it doesn't validate against organization-specific schemas or test actual rule execution. No API calls are made, and no Organization ID is required.

## Required Information

Before calling this skill, gather:

**Note**: This skill does NOT require an Organization ID (OID). Validation is performed client-side without API calls.

- **detect**: Detection component object (YAML/JSON structure) to validate
- **respond** (optional): Response component object (YAML/JSON structure) to validate

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Detection component in object/dictionary format (not YAML string)
2. Optional response component in object/dictionary format
3. Understanding that this is basic syntax validation, not full rule testing

### Step 2: Call the Tool

Use the `validate_dr_rule_components` MCP tool from the `limacharlie` server:

```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={"event": "NEW_PROCESS", "op": "contains", "path": "event/COMMAND_LINE", "value": "powershell"},
  respond=[{"action": "report", "name": "powershell_detected"}]
)
```

**Tool Details:**
- Tool: `mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components`
- Parameters:
  - `detect` (object, required): Detection component structure
  - `respond` (object/array, optional): Response component structure

**How it works:**
- Performs client-side validation without API calls
- Checks detection component for required 'op' field
- Validates operator against known valid operators
- Checks response actions for valid 'action' field
- Validates action types against known valid actions
- Returns validation result with errors or success message

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

The tool returns a response with:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

**Success:**
- `valid`: true
- `message`: Success message
- No `error` field

**Validation Failure:**
```json
{
  "valid": false,
  "error": "Detection component missing required 'op' field",
  "message": "Validation failed"
}
```

**Common Errors:**
- Missing 'op' field in detection component
- Invalid operator in detection logic
- Missing 'action' field in response component
- Invalid action type in response
- Malformed structure (not an object/array)

### Step 4: Format the Response

Present the result to the user:
- Clearly indicate if validation passed or failed
- Display specific error messages if validation failed
- Explain what needs to be fixed
- Suggest corrections for common errors
- Remind them this is basic syntax validation only
- Recommend full testing after deployment

**Example formatted output for success:**
```
✓ Validation Passed

Your D&R rule components are syntactically valid:
- Detection component: Valid operator and structure
- Response component: Valid actions

Note: This is basic syntax validation. Test the rule with actual data after deployment to ensure it works as expected.
```

**Example formatted output for failure:**
```
✗ Validation Failed

Error: Detection component missing required 'op' field

Your detection component must include an 'op' field specifying the operator. Valid operators include:
- is, contains, starts with, ends with, matches
- and, or (for combining multiple conditions)
- exists, is greater than, is less than, length is

Example:
{
  "event": "NEW_PROCESS",
  "op": "contains",
  "path": "event/COMMAND_LINE",
  "value": "powershell"
}
```

## Example Usage

### Example 1: Validate Detection Component

User request: "Validate this detection logic before I deploy it"

Steps:
1. Get detection component from user
2. Call tool:
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={
    "event": "NEW_PROCESS",
    "op": "contains",
    "path": "event/COMMAND_LINE",
    "value": "powershell"
  }
)
```
3. Present validation result

Expected response:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

### Example 2: Validate Detection and Response

User request: "Check if my complete D&R rule is valid"

Steps:
1. Get both detection and response components
2. Call tool:
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={
    "event": "NEW_PROCESS",
    "op": "and",
    "rules": [
      {"op": "contains", "path": "event/FILE_PATH", "value": "powershell"},
      {"op": "contains", "path": "event/COMMAND_LINE", "value": "-enc"}
    ]
  },
  respond=[
    {"action": "report", "name": "encoded_powershell"},
    {"action": "isolate network"}
  ]
)
```

Expected response:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

### Example 3: Catch Invalid Operator

User request: "Is this detection valid?"

Steps:
1. Get detection component with invalid operator
2. Call tool:
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={
    "event": "NEW_PROCESS",
    "op": "equals",
    "path": "event/COMMAND_LINE",
    "value": "powershell"
  }
)
```

Expected response:
```json
{
  "valid": false,
  "error": "Invalid operator 'equals'. Valid operators are: and, or, exists, is, contains, starts with, ends with, matches, is greater than, is less than, length is, lookup",
  "message": "Validation failed"
}
```

### Example 4: Missing Required Field

User request: "Validate this detection component"

Steps:
1. Get detection component missing 'op' field
2. Call tool:
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={
    "event": "NEW_PROCESS",
    "path": "event/COMMAND_LINE",
    "value": "powershell"
  }
)
```

Expected response:
```json
{
  "valid": false,
  "error": "Detection component missing required 'op' field",
  "message": "Validation failed"
}
```

## Additional Notes

- **Client-Side**: No API calls made - validation is local
- **No OID Required**: Works without organization context
- **Basic Validation**: Checks syntax and structure only
- **Not Comprehensive**: Doesn't validate against org-specific schemas
- **Fast**: Instant validation without network calls
- **Detection Validation**:
  - Requires 'op' field
  - Validates operator is in known list
  - Checks for proper structure
  - Validates nested rules for 'and'/'or' operators
- **Response Validation**:
  - Requires 'action' field
  - Validates action is in known list
  - Checks for proper array structure
- **Limitations**:
  - Doesn't validate event types against org schema
  - Doesn't validate field paths exist
  - Doesn't test rule execution
  - Doesn't check for logic errors
  - Doesn't validate against LimaCharlie API
- **Use Before Deployment**: Catch basic errors before API calls
- **Combine with Testing**: Follow with actual rule testing
- **Learning Tool**: Helps learn proper D&R syntax
- **Development Aid**: Useful during rule creation and debugging
- **Error Messages**: Provides specific guidance on what's wrong
- **Valid Operators List**: Maintained in MCP server code
- **Valid Actions List**: Maintained in MCP server code
- **Complementary**: Use with AI generation tools to validate generated rules

## Reference

For more details on the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/validation.go` (validate_dr_rule_components function)

For complete D&R rule syntax and validation, see LimaCharlie's Detection & Response documentation and use the API-based validation via `set-dr-general-rule`.
