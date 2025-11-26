
# Validate YARA Rule

Validate YARA rule syntax for basic correctness using client-side validation.

## When to Use

Use this skill when the user needs to:
- Verify YARA rule syntax before deploying
- Check if YARA rules are properly formatted
- Validate YARA rules during development
- Debug syntax errors in YARA rules
- Learn correct YARA rule structure through validation feedback
- Catch basic errors early before deployment
- Ensure YARA rules meet basic structural requirements
- Test YARA rules before adding to LimaCharlie

Common scenarios:
- "Validate this YARA rule before I deploy it"
- "Check if my YARA rule syntax is correct"
- "Is this YARA rule valid?"
- "Verify my YARA rule for errors"
- "Test this YARA rule syntax"

## What This Skill Does

This skill performs basic client-side validation of YARA rule syntax. It checks for fundamental structural requirements like the presence of the 'rule' keyword, balanced braces, and a condition section. This is NOT a full YARA compiler - it performs basic syntax checks only. No API calls are made, no Organization ID is required, and the rule is not compiled or executed.

## Required Information

Before calling this skill, gather:

**Note**: This skill does NOT require an Organization ID (OID). Validation is performed client-side without API calls.

- **rule_content**: YARA rule content as a string

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. YARA rule content as a string (not a file path)
2. Understanding that this is basic syntax validation only
3. Knowledge that full YARA compilation may catch additional errors

### Step 2: Call the Tool

Use the `validate_yara_rule` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__validate_yara_rule(
  rule_content='rule SuspiciousPowerShell {
    meta:
        description = "Detects encoded PowerShell"
    strings:
        $ps = "powershell" nocase
        $enc = "-enc" nocase
    condition:
        all of them
  }'
)
```

**Tool Details:**
- Tool: `mcp__limacharlie__validate_yara_rule`
- Parameters:
  - `rule_content` (string, required): YARA rule content to validate

**How it works:**
- Performs client-side validation without API calls or compilation
- Checks that content is non-empty
- Verifies presence of 'rule' keyword
- Checks for balanced braces { }
- Validates presence of 'condition:' section
- Returns validation result with error messages if validation fails

**Basic Checks Performed:**
- Non-empty content
- Contains 'rule' keyword
- Balanced opening and closing braces
- Contains 'condition:' section

**NOT Checked (requires full YARA compiler):**
- String pattern syntax
- Condition expression logic
- Import statements
- Regex validity
- Module usage
- Advanced YARA features

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "valid": true,
  "message": "YARA rule passes basic syntax validation"
}
```

**Success:**
- `valid`: true
- `message`: Success message

**Validation Failure:**
```json
{
  "valid": false,
  "message": "YARA rule missing 'condition:' section"
}
```

**Common Error Messages:**
- "YARA rule content is empty"
- "YARA rule missing 'rule' keyword"
- "YARA rule has unbalanced braces"
- "YARA rule missing 'condition:' section"

### Step 4: Format the Response

Present the result to the user:
- Clearly indicate if validation passed or failed
- Display specific error messages if validation failed
- Explain what needs to be fixed
- Remind them this is basic validation only
- Recommend full YARA compilation for comprehensive validation
- Suggest testing the rule with YARA compiler before deployment

## Example Usage

### Example 1: Validate Basic YARA Rule

User request: "Validate this YARA rule"

Steps:
1. Get YARA rule content from user
2. Call tool:
```
mcp__limacharlie__validate_yara_rule(
  rule_content='rule SuspiciousPowerShell {
    strings:
        $ps = "powershell" nocase
        $enc = "-enc" nocase
    condition:
        all of them
  }'
)
```
3. Present validation result

Expected response:
```json
{
  "valid": true,
  "message": "YARA rule passes basic syntax validation"
}
```

### Example 2: Detect Missing Condition

User request: "Is this YARA rule valid?"

Steps:
1. Get YARA rule without condition section
2. Call tool:
```
mcp__limacharlie__validate_yara_rule(
  rule_content='rule MissingCondition {
    strings:
        $pattern = "test"
  }'
)
```

Expected response:
```json
{
  "valid": false,
  "message": "YARA rule missing 'condition:' section"
}
```

### Example 3: Detect Unbalanced Braces

User request: "Check if my YARA rule syntax is correct"

Steps:
1. Get YARA rule with unbalanced braces
2. Call tool:
```
mcp__limacharlie__validate_yara_rule(
  rule_content='rule UnbalancedBraces {
    strings:
        $pattern = "test"
    condition:
        $pattern
  '
)
```

Expected response:
```json
{
  "valid": false,
  "message": "YARA rule has unbalanced braces"
}
```

### Example 4: Validate Complex Rule with Metadata

User request: "Validate this YARA rule before I deploy it"

Steps:
1. Get comprehensive YARA rule
2. Call tool:
```
mcp__limacharlie__validate_yara_rule(
  rule_content='rule MalwareDetection {
    meta:
        description = "Detects specific malware family"
        author = "Security Team"
        date = "2024-01-20"
    strings:
        $mz = "MZ"
        $string1 = "malicious" nocase
        $string2 = { 6A 40 68 00 30 00 00 }
    condition:
        $mz at 0 and any of ($string*)
  }'
)
```

Expected response:
```json
{
  "valid": true,
  "message": "YARA rule passes basic syntax validation"
}
```

## Additional Notes

- **Client-Side**: No API calls made - validation is local
- **No OID Required**: Works without organization context
- **Basic Validation Only**: NOT a full YARA compiler
- **Fast**: Instant validation without network calls or compilation
- **Checks Performed**:
  - Non-empty content
  - Presence of 'rule' keyword
  - Balanced braces { }
  - Presence of 'condition:' section
- **NOT Checked** (requires full YARA compiler):
  - String pattern syntax validity
  - Condition expression correctness
  - Regex pattern validity
  - Import statement correctness
  - Module availability
  - Variable references
  - Operator usage
  - Advanced YARA features (private rules, includes, etc.)
- **Limitations**:
  - Basic structural validation only
  - May pass rules that would fail YARA compilation
  - Cannot catch logical errors
  - Cannot validate pattern syntax
  - Cannot check module dependencies
- **Use Cases**:
  - Quick syntax check during development
  - Catch obvious structural errors
  - Pre-validation before API submission
  - Learning YARA rule structure
- **Recommendation**: Follow up with full YARA compiler validation
- **Testing**: Test rules with actual YARA compiler before production
- **Deployment**: Use LimaCharlie's YARA rule API for final validation and deployment
- **Learning Tool**: Helps understand basic YARA rule structure
- **Development Aid**: Useful during rule creation
- **Complementary**: Use before deploying to LimaCharlie YARA scanning

## Reference

For more details on the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go` (validate_yara_rule function)

For complete YARA syntax and documentation, see the official YARA documentation at: https://yara.readthedocs.io/

For deploying YARA rules in LimaCharlie, see LimaCharlie's documentation on YARA scanning and artifact collection.
