---
name: get-yara-rule
description: Get a specific YARA rule's content and source code by name. Retrieve the actual YARA rule syntax and signatures for malware detection. Use when users need to view, inspect, review, export, or analyze YARA rule definitions, malware signatures, or detection patterns.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get YARA Rule

Retrieve a specific YARA rule's source content and signatures by name.

## When to Use

Use this skill when the user needs to:
- View a specific YARA rule's content
- Inspect YARA rule signatures
- Review malware detection patterns
- Export YARA rule definitions
- Analyze YARA rule syntax

Common scenarios:
- Rule inspection: "Show me the 'malware_detection' YARA rule"
- Analysis: "What signatures are in the 'ransomware' YARA rule?"
- Export: "Get the YARA rule content for 'apt_signatures'"
- Documentation: "Display the 'trojan_detection' YARA rule source"

## What This Skill Does

This skill retrieves the actual YARA rule source code for a specific rule by name. It returns the complete YARA syntax including rule definitions, strings, conditions, and metadata. This is useful for reviewing detection logic, exporting rules, or troubleshooting signatures.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Name of the YARA rule source to retrieve (must be exact match)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact YARA rule source name (case-sensitive)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/service/yara",
  body={
    "oid": "[organization-id]",
    "action": "get_source",
    "source": "[rule-name]"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/service/yara` (YARA service endpoint)
- Body fields:
  - `oid`: Organization ID
  - `action`: Must be "get_source"
  - `source`: Rule source name to retrieve

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "content": "rule malware_detection {\n  meta:\n    author = \"security\"\n    description = \"Detects malware\"\n  strings:\n    $hex1 = { 4D 5A 90 }\n    $str1 = \"malicious\"\n  condition:\n    $hex1 or $str1\n}\n"
  }
}
```

**Success (200-299):**
- The response body contains a "content" field with the YARA rule source code
- Present the complete YARA rule text to the user
- Format the rule content with proper syntax highlighting if possible

**Common Errors:**
- **400 Bad Request**: Invalid request format or missing source parameter
- **403 Forbidden**: Insufficient permissions to view YARA rules
- **404 Not Found**: Rule with specified name does not exist
- **500 Server Error**: YARA service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show the rule name clearly
- Display the YARA rule source code with proper formatting
- Highlight key sections: meta, strings, condition
- Note the rule complexity (number of strings, conditions)
- If rule not found, suggest checking the name with list-yara-rules

## Example Usage

### Example 1: Get YARA rule content

User request: "Show me the 'malware_detection' YARA rule"

Steps:
1. Get organization ID from context
2. Extract rule name: "malware_detection"
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/service/yara",
  body={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "action": "get_source",
    "source": "malware_detection"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "content": "rule suspicious_pe {\n  meta:\n    author = \"security-team\"\n    description = \"Detects suspicious PE files\"\n  strings:\n    $mz = { 4D 5A }\n    $pe = \"PE\\x00\\x00\"\n    $suspicious = \"malware\" nocase\n  condition:\n    $mz at 0 and $pe and $suspicious\n}\n\nrule ransomware_behavior {\n  meta:\n    severity = \"high\"\n  strings:\n    $encrypt = \"CryptEncrypt\"\n    $delete = \"shadow delete\"\n  condition:\n    all of them\n}\n"
  }
}
```

User message: "YARA Rule: malware_detection\n\n[Display formatted YARA content]"

### Example 2: Rule not found

User request: "Get YARA rule 'nonexistent_rule'"

Steps:
1. Call API
2. API returns 404 Not Found
3. Inform user: "YARA rule 'nonexistent_rule' not found. Use list-yara-rules to see available rules."

## Additional Notes

- Rule names are case-sensitive and must match exactly
- The returned content is the raw YARA rule source code
- YARA rules can contain multiple rule definitions in a single source
- Common YARA sections:
  - `meta:` - Metadata about the rule (author, description, etc.)
  - `strings:` - String and hex patterns to match
  - `condition:` - Logic for when the rule triggers
- YARA syntax supports:
  - Hex patterns: `{ 4D 5A 90 }`
  - Text strings: `"malicious text"`
  - Regular expressions: `/regex pattern/`
  - Wildcards and jumps: `{ 4D 5A [0-10] 90 }`
- To modify this rule, use set-yara-rule with updated content
- To delete this rule, use delete-yara-rule
- To validate YARA syntax before uploading, use validate-yara-rule
- YARA rules are powerful for malware detection and threat hunting

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/yara.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go`
For YARA syntax documentation, see: https://yara.readthedocs.io/en/stable/writingrules.html
