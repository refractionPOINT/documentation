---
name: validate-dr-rule-components
description: Validate Detection & Response rule detection and response components for syntax correctness before creating or updating rules. Perform client-side validation of D&R rule structure, operators, paths, and actions. Use when users need to test, validate, check, or verify rule syntax, troubleshoot rule creation errors, or ensure rule correctness before deployment.
allowed-tools: Read
---

# Validate D&R Rule Components

Validate the syntax and structure of Detection & Response rule detection and response components before creating or updating rules.

## When to Use

Use this skill when the user needs to:
- Validate D&R rule syntax before creating a rule
- Test detection logic for correctness
- Troubleshoot rule creation errors
- Verify response action structure
- Check rule components before deployment

Common scenarios:
- Pre-deployment validation: "Validate this D&R rule before I create it"
- Troubleshooting: "Check if my detection logic is valid"
- Development: "Test this rule syntax for errors"
- Quality assurance: "Verify this rule configuration is correct"

## What This Skill Does

This skill performs client-side validation of D&R rule components. It checks the detection component for required fields, valid operators, proper structure, and the response component for valid actions and required parameters. This validation happens locally without calling the LimaCharlie API, making it fast and useful for iterative rule development.

## Required Information

Before calling this skill, gather:
- **detect**: Detection component object (required)
- **respond**: Response component array or object (optional)

No organization ID (oid) is required as this is client-side validation.

### Detection Component Requirements

Must contain:
- **op**: Operation type (string)
- Valid operators: and, or, exists, is, contains, starts with, ends with, matches, is greater than, is less than, length is, lookup
- For 'and'/'or': **rules** array with sub-rules
- For field operations: **path** or **event** field

### Response Component Requirements

Can be array or single object, each action needs:
- **action**: Action type (string)
- Valid actions: report, task, add tag, remove tag, isolate network, rejoin network, service request
- Action-specific fields (e.g., 'name' for report, 'command' for task)

## How to Use

### Step 1: Prepare Rule Components

Structure your detect and respond components:

Detect example:
```json
{
  "op": "and",
  "rules": [
    {"op": "is", "path": "event/EVENT_TYPE", "value": "NEW_PROCESS"},
    {"op": "contains", "path": "event/COMMAND_LINE", "value": "malware"}
  ]
}
```

Respond example:
```json
[
  {"action": "report", "name": "malware_detection"},
  {"action": "isolate network"}
]
```

### Step 2: Validate

This is a client-side validation tool. The MCP tool implementation performs:

1. **Detection validation**:
   - Checks 'op' field exists and is a string
   - Validates operator type against known operators
   - For 'and'/'or': verifies 'rules' array exists and is non-empty
   - For field operations: checks 'path' or 'event' field presence

2. **Response validation** (if provided):
   - Checks each action is an object
   - Verifies 'action' field exists and is a string
   - Validates action type against known actions
   - For 'report': checks 'name' field exists
   - For 'task': checks 'command' field exists

### Step 3: Handle Results

Validation returns:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

Or if invalid:
```json
{
  "valid": false,
  "error": "Invalid detect component: detect must have 'op' field"
}
```

**Valid result:**
- Proceed with creating or updating the rule
- Rule structure is syntactically correct
- Note: This does not guarantee the rule will work as expected, only that syntax is correct

**Invalid result:**
- Review the error message
- Fix the indicated issue in the rule structure
- Re-validate before attempting to create the rule
- Common issues: missing 'op' field, empty 'rules' array, missing action 'name'

## Example Usage

### Example 1: Validate correct rule

User request: "Validate this detection rule before I create it"

Rule components:
```json
{
  "detect": {
    "op": "is",
    "path": "event/EVENT_TYPE",
    "value": "NETWORK_CONNECTIONS"
  },
  "respond": [
    {"action": "report", "name": "network_activity"}
  ]
}
```

Result:
```json
{
  "valid": true,
  "message": "D&R rule components are valid"
}
```

User message: "Rule components are valid. You can proceed with creating the rule."

### Example 2: Detect missing field

User request: "Check if this rule is valid"

Rule components:
```json
{
  "detect": {
    "rules": [
      {"op": "is", "path": "event/EVENT_TYPE", "value": "NEW_PROCESS"}
    ]
  }
}
```

Result:
```json
{
  "valid": false,
  "error": "Invalid detect component: detect must have 'op' field"
}
```

User message: "Rule validation failed: Invalid detect component - detect must have 'op' field. Please add the 'op' field to your detection logic."

### Example 3: Invalid response action

User request: "Validate this rule with response actions"

Rule components:
```json
{
  "detect": {
    "op": "is",
    "path": "event/EVENT_TYPE",
    "value": "FILE_CREATE"
  },
  "respond": [
    {"action": "report"}
  ]
}
```

Result:
```json
{
  "valid": false,
  "error": "Invalid respond component: 'report' action requires 'name' field"
}
```

## Additional Notes

- This is client-side validation only - it checks structure, not semantic correctness
- Valid syntax does not guarantee the rule will work as intended
- The rule may still fail when created if:
  - Field paths don't exist for the event type
  - Values are incorrect type (e.g., string vs number)
  - Logic doesn't match any events
- Unknown operators or actions will pass validation (they might be valid in the API)
- This validation is fast and doesn't require API calls
- Use this before calling set-dr-general-rule or set-dr-managed-rule
- For testing rule logic against actual data, create the rule and test with historical events
- The validation checks common D&R rule patterns but may not catch all edge cases

## Reference

For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/validation.go`
For D&R rule syntax documentation, see: https://doc.limacharlie.io/docs/documentation/docs/detection-and-response
