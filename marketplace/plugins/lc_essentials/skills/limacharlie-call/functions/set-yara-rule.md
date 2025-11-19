
# Set YARA Rule

Create or update a YARA rule for malware detection and file scanning.

## When to Use

Use this skill when the user needs to:
- Create a new YARA rule
- Update an existing YARA rule
- Deploy malware detection signatures
- Add threat hunting rules
- Configure file scanning patterns

Common scenarios:
- "Create a YARA rule to detect ransomware"
- "Update the 'malware_detection' YARA rule with new signatures"
- "Upload YARA signatures from threat intelligence"

## What This Skill Does

Creates or updates a YARA rule source in the organization. Rules are used for malware detection, file scanning, and pattern matching. The rule content must be valid YARA syntax.

## Recommended Workflow: Validate Before Deployment

**For reliable YARA rule deployment, use this workflow:**

1. **Review YARA Documentation** (if needed)
   Visit https://yara.readthedocs.io/en/stable/writingrules.html for YARA syntax reference.

2. **Validate Rule Syntax**
   ```
   mcp__limacharlie__validate_yara_rule(
     rule_content="rule my_rule { ... }"
   )
   ```
   Returns validation result with any syntax errors.

3. **Deploy Rule** (this API call)

## Required Information

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list-user-orgs` first.

- **oid**: Organization ID (UUID)
- **name**: Unique name for the YARA rule source
- **rule_content**: YARA rule source code (valid YARA syntax)

Optional:
- **tags**: Sensor tags to apply the rule to (empty = all sensors)
- **platforms**: Platforms to target (windows, linux, macos)

## How to Use

### Step 1: Call the API

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_yara_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]",
    "rule_content": "[yara-rule-content]"
  }
)
```

**API Details:**
- Tool: `set_yara_rule`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Rule name
  - `rule_content`: YARA rule source code

### Step 2: Handle the Response

**Success (200):**
```json
{}
```
Rule is immediately active across sensors.

**Common Errors:**
- **400 Bad Request**: Invalid YARA syntax - use `validate-yara-rule` first
- **403 Forbidden**: Insufficient permissions
- **500 Server Error**: YARA service issue

## Example Usage

### Complete Workflow with Validation

User request: "Create a YARA rule to detect ransomware behavior"

**Step 1: Prepare rule content**
```yara
rule ransomware_behavior {
  meta:
    author = "security-team"
    description = "Detects common ransomware patterns"
  strings:
    $encrypt1 = "CryptEncrypt" nocase
    $ransom = "YOUR FILES HAVE BEEN ENCRYPTED" nocase
  condition:
    $encrypt1 and $ransom
}
```

**Step 2: Validate syntax**
```
mcp__limacharlie__validate_yara_rule(
  rule_content="rule ransomware_behavior { ... }"
)
// Returns: {"valid": true, "message": "YARA rule passes basic syntax validation"}
```

**Step 3: Deploy**
```
mcp__limacharlie__lc_call_tool(
  tool_name="set_yara_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "ransomware_detection",
    "rule_content": "rule ransomware_behavior {\n  meta:\n    author = \"security-team\"\n    description = \"Detects common ransomware patterns\"\n  strings:\n    $encrypt1 = \"CryptEncrypt\" nocase\n    $ransom = \"YOUR FILES HAVE BEEN ENCRYPTED\" nocase\n  condition:\n    $encrypt1 and $ransom\n}\n"
  }
)
```

## Related Functions

- `validate-yara-rule` - Validate YARA syntax before deployment
- `list-yara-rules` - List all YARA rules
- `get-yara-rule` - Get specific rule content
- `delete-yara-rule` - Remove a YARA rule
- `yara-scan-file` - Test rule against files
- `yara-scan-process` - Test rule against processes

## Reference

For the API implementation, see [CALLING_API.md](../../CALLING_API.md).

For YARA syntax documentation, see: https://yara.readthedocs.io/en/stable/writingrules.html
