
# List YARA Rules

Retrieve all YARA rules configured in the organization for malware detection and file scanning.

## When to Use

Use this skill when the user needs to:
- List all YARA rules in the organization
- View YARA rule inventory
- Audit YARA-based detection capabilities
- Review malware detection rules
- Check what YARA rules are deployed

Common scenarios:
- Inventory: "Show me all my YARA rules"
- Audit: "What YARA rules are configured for malware detection?"
- Review: "List YARA signatures I'm using"
- Management: "Display all YARA rule sources"

## What This Skill Does

This skill retrieves all YARA rules configured in the organization. YARA rules are used for malware detection, file scanning, and pattern matching across files and processes on sensors. It calls the LimaCharlie YARA service API to list all rule sources and their metadata.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are required.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server to call the YARA service:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_yara_rules",
  parameters={
    "oid": "[organization-id]"
  }
)
```

**API Details:**
- Tool: `list_yara_rules`
- Required parameters:
  - `oid`: Organization ID

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "rule-source-1": {
    "by": "user@example.com",
    "filters": {
      "tags": ["windows", "malware"],
      "platforms": ["windows"]
    },
    "sources": ["source-name-1"],
    "updated": 1234567890
  },
  "rule-source-2": {
    "by": "admin@example.com",
    "filters": {
      "tags": [],
      "platforms": ["linux", "macos"]
    },
    "sources": ["source-name-2"],
    "updated": 1234567899
  }
}
```

**Success (200-299):**
- The response contains a map of YARA rule sources indexed by name
- Each entry includes:
  - `by`: Author/creator email
  - `filters`: Tags and platforms the rule applies to
  - `sources`: Source file names
  - `updated`: Unix timestamp of last update
- Count the number of rules and present to user
- Display rule names, platforms, and update times

**Common Errors:**
- **400 Bad Request**: Invalid request format or missing parameters
- **403 Forbidden**: Insufficient permissions to view YARA rules
- **404 Not Found**: Organization ID does not exist
- **500 Server Error**: YARA service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show total count of YARA rule sources
- List rule names with metadata
- Display platform filters (which OS the rules apply to)
- Show tag filters if any
- Include last updated timestamps
- Note if no YARA rules are configured

## Example Usage

### Example 1: List all YARA rules

User request: "Show me all my YARA rules"

Steps:
1. Get organization ID from context
2. Call YARA service API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_yara_rules",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

Expected response:
```json
{
  "malware_detection": {
    "by": "security@company.com",
    "filters": {
      "tags": ["production"],
      "platforms": ["windows", "linux"]
    },
    "sources": ["malware_sigs"],
    "updated": 1705000000
  },
  "ransomware_signatures": {
    "by": "threat-intel@company.com",
    "filters": {
      "tags": [],
      "platforms": ["windows"]
    },
    "sources": ["ransomware_rules"],
    "updated": 1705000100
  }
}
```

User message: "You have 2 YARA rule sources configured:
1. malware_detection (Windows, Linux) - Updated: Jan 11, 2024
2. ransomware_signatures (Windows only) - Updated: Jan 11, 2024"

### Example 2: No YARA rules configured

User request: "List my YARA rules"

Steps:
1. Call API
2. Response body is empty object: {}
3. Inform user: "You have no YARA rules configured. Use set-yara-rule to add malware detection rules."

## Additional Notes

- YARA rules are used for malware detection and file/memory scanning
- Each rule source can contain multiple YARA rule definitions
- Platform filters determine which sensors the rules apply to (windows, linux, macos)
- Tag filters restrict rules to sensors with specific tags
- Empty filters mean the rule applies to all sensors
- To view the actual YARA rule content, use get-yara-rule with the rule name
- To add or update YARA rules, use set-yara-rule
- To remove YARA rules, use delete-yara-rule
- YARA rules are evaluated during file operations and can be triggered manually
- Rules are distributed to sensors based on their platform and tag filters

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/yara.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go`
For YARA documentation, see: https://yara.readthedocs.io/
