
# Set YARA Rule

Create a new YARA rule or update an existing one for malware detection and file scanning.

## When to Use

Use this skill when the user needs to:
- Create a new YARA rule
- Update an existing YARA rule
- Deploy malware detection signatures
- Add threat hunting rules
- Configure file scanning patterns

Common scenarios:
- Rule creation: "Create a YARA rule to detect ransomware"
- Update: "Update the 'malware_detection' YARA rule with new signatures"
- Deployment: "Add this YARA rule for threat hunting"
- Import: "Upload YARA signatures from threat intelligence"

## What This Skill Does

This skill creates or updates a YARA rule source in the organization. YARA rules are used for malware detection, file scanning, and pattern matching across files and processes. The rule content must be valid YARA syntax. If a rule with the same name exists, it will be replaced.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Name for the YARA rule source (unique identifier)
- **rule_content**: YARA rule source code (must be valid YARA syntax)

Optional parameters:
- **tags**: Array of sensor tags to apply the rule to (empty = all sensors)
- **platforms**: Array of platforms (windows, linux, macos) to apply the rule to (empty = all platforms)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Unique rule name (alphanumeric with underscores recommended)
3. Valid YARA rule content (proper syntax)
4. Optional: tag and platform filters

### Step 2: Validate YARA Syntax

Before uploading, validate the YARA rule syntax using validate-yara-rule skill to ensure it's correct.

### Step 3: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/service/yara",
  body={
    "oid": "[organization-id]",
    "action": "add_source",
    "name": "[rule-name]",
    "source": "",
    "content": "[yara-rule-content]"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/service/yara` (YARA service endpoint)
- Body fields:
  - `oid`: Organization ID
  - `action`: Must be "add_source"
  - `name`: Rule source name
  - `source`: Empty string (for literal rules) or URL (for remote sources)
  - `content`: YARA rule source code (complete YARA syntax)

### Step 4: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Rule successfully created or updated
- Rule is now active and will be used for scanning
- Confirm to user that rule is deployed

**Common Errors:**
- **400 Bad Request**: Invalid YARA syntax, malformed rule, or missing required fields
- **403 Forbidden**: Insufficient permissions to create YARA rules
- **500 Server Error**: YARA service issue - retry or contact support

### Step 5: Format the Response

Present the result to the user:
- Confirm rule was created or updated successfully
- Show rule name
- Summarize what the rule detects (from meta or description)
- Note that the rule is now active across sensors
- Suggest testing the rule with yara-scan commands

## Example Usage

### Example 1: Create ransomware detection rule

User request: "Create a YARA rule to detect ransomware behavior"

Steps:
1. Prepare YARA rule content:
```yara
rule ransomware_behavior {
  meta:
    author = "security-team"
    description = "Detects common ransomware patterns"
    severity = "high"
  strings:
    $encrypt1 = "CryptEncrypt" nocase
    $encrypt2 = "AES" nocase
    $ransom = "YOUR FILES HAVE BEEN ENCRYPTED" nocase
    $bitcoin = /bitcoin|btc/i
  condition:
    2 of ($encrypt*) and ($ransom or $bitcoin)
}
```

2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/service/yara",
  body={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "action": "add_source",
    "name": "ransomware_detection",
    "source": "",
    "content": "rule ransomware_behavior {\n  meta:\n    author = \"security-team\"\n    description = \"Detects common ransomware patterns\"\n    severity = \"high\"\n  strings:\n    $encrypt1 = \"CryptEncrypt\" nocase\n    $encrypt2 = \"AES\" nocase\n    $ransom = \"YOUR FILES HAVE BEEN ENCRYPTED\" nocase\n    $bitcoin = /bitcoin|btc/i\n  condition:\n    2 of ($encrypt*) and ($ransom or $bitcoin)\n}\n"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

User message: "Successfully created YARA rule 'ransomware_detection'. The rule is now active and will scan for ransomware patterns across your sensors."

### Example 2: Update existing rule

User request: "Update the 'malware_detection' rule with additional signatures"

Steps:
1. Get current rule content (optional, to preserve existing rules)
2. Prepare updated YARA content with additional rules
3. Call API with same name to replace
4. Confirm update successful

## Additional Notes

- Rule names must be unique within the organization
- Uploading a rule with an existing name replaces the old rule completely
- YARA rule syntax must be valid or the API will reject it
- Use validate-yara-rule before uploading to catch syntax errors
- YARA rules can contain multiple rule definitions in a single source
- Common YARA rule structure:
  ```yara
  rule rule_name {
    meta:
      // Metadata fields
    strings:
      // String patterns to match
    condition:
      // Logic for when rule triggers
  }
  ```
- The `source` field should be empty string for literal rules
- For rules from remote repos, `source` can be a URL and `content` can be empty
- Tags and platforms filters are not yet fully supported in the SDK
- Rules are distributed to sensors automatically
- Changes take effect immediately
- Test rules with `yara_scan_file` or `yara_scan_process` commands

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/yara.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go`
For YARA syntax documentation, see: https://yara.readthedocs.io/en/stable/writingrules.html
