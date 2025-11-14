
# Validate YARA Rule

Validate YARA rule syntax and structure before uploading to the organization.

## When to Use

Use this skill when the user needs to:
- Validate YARA rule syntax before creating
- Test YARA rule for syntax errors
- Troubleshoot YARA rule creation errors
- Verify YARA rule structure
- Check rule correctness before deployment

Common scenarios:
- Pre-deployment validation: "Validate this YARA rule before I upload it"
- Troubleshooting: "Check if my YARA rule syntax is correct"
- Development: "Test this YARA rule for errors"
- Quality assurance: "Verify this YARA rule is valid"

## What This Skill Does

This skill performs basic client-side validation of YARA rule syntax. It checks for required keywords (rule, condition), balanced braces, and basic structure. This validation happens locally without calling the LimaCharlie API, making it fast and useful for iterative rule development. Note that this is basic validation only - full YARA compilation happens on the server.

## Required Information

Before calling this skill, gather:
- **rule_content**: YARA rule source code to validate (string)

No organization ID (oid) is required as this is client-side validation.

### YARA Rule Structure

Valid YARA rules must contain:
- `rule` keyword followed by rule name
- Opening and closing braces `{ }`
- `condition:` section (required)
- Optional: `meta:` section for metadata
- Optional: `strings:` section for patterns

## How to Use

### Step 1: Prepare YARA Rule

Example YARA rule structure:
```yara
rule example_malware {
  meta:
    author = "security-team"
    description = "Detects example malware"
  strings:
    $hex1 = { 4D 5A 90 }
    $str1 = "malicious"
  condition:
    $hex1 or $str1
}
```

### Step 2: Validate

This is a client-side validation tool. The MCP tool implementation performs:

1. **Basic structure checks**:
   - Rule content is not empty
   - Contains 'rule' keyword
   - Has opening and closing braces
   - Braces are balanced (same number of { and })

2. **Required sections**:
   - Contains 'condition:' keyword (required in YARA)

3. **Syntax hints**:
   - Checks for common YARA keywords
   - Validates basic structure

Note: This is NOT full YARA compilation. The server will perform complete validation when you upload the rule.

### Step 3: Handle Results

Validation returns:
```json
{
  "valid": true,
  "message": "YARA rule syntax is valid"
}
```

Or if invalid:
```json
{
  "valid": false,
  "message": "Invalid YARA rule: rule content must contain 'condition:' section"
}
```

**Valid result:**
- Basic syntax appears correct
- Proceed with uploading the rule using set-yara-rule
- Note: Server may still reject for semantic errors

**Invalid result:**
- Review the error message
- Fix the indicated issue in the rule
- Common issues: missing 'rule' keyword, missing 'condition:', unbalanced braces
- Re-validate after fixing

## Example Usage

### Example 1: Validate correct YARA rule

User request: "Validate this YARA rule before uploading"

YARA rule content:
```yara
rule ransomware_detection {
  meta:
    severity = "high"
  strings:
    $encrypt = "CryptEncrypt"
    $ransom = "bitcoin"
  condition:
    all of them
}
```

Result:
```json
{
  "valid": true,
  "message": "YARA rule syntax is valid"
}
```

User message: "YARA rule syntax is valid. You can proceed with uploading the rule."

### Example 2: Missing condition section

User request: "Check if this YARA rule is valid"

YARA rule content:
```yara
rule broken_rule {
  strings:
    $pattern = "test"
}
```

Result:
```json
{
  "valid": false,
  "message": "Invalid YARA rule: rule must contain 'condition:' section"
}
```

User message: "YARA rule validation failed: rule must contain 'condition:' section. Please add a condition section to your rule."

### Example 3: Unbalanced braces

User request: "Validate this YARA rule"

YARA rule content:
```yara
rule malformed {
  condition:
    true
```

Result:
```json
{
  "valid": false,
  "message": "Invalid YARA rule: unbalanced braces in rule content"
}
```

## Additional Notes

- This is basic client-side validation only
- Full YARA compilation happens when you upload the rule
- Valid basic syntax does not guarantee the rule will work as intended
- The rule may still fail on the server if:
  - String patterns are malformed
  - Condition logic is invalid
  - References to undefined identifiers
  - Regular expression syntax errors
- This validation is fast and doesn't require API calls
- Use this before calling set-yara-rule to catch obvious errors early
- For complete validation, upload the rule to a test organization first
- Common YARA sections:
  - `meta:` - Metadata (optional)
  - `strings:` - String patterns (optional)
  - `condition:` - Detection logic (required)
- YARA condition examples:
  - `any of them` - Any string matches
  - `all of them` - All strings match
  - `$str1 or $str2` - Specific string logic
  - `filesize < 100KB` - File size checks
  - `pe.number_of_sections > 5` - PE structure checks

## Reference

For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go`
For YARA syntax documentation, see: https://yara.readthedocs.io/en/stable/writingrules.html
For YARA modules, see: https://yara.readthedocs.io/en/stable/modules.html
