
# Generate D&R Rule Detection Component

Generate Detection & Response (D&R) rule detection components from natural language descriptions using AI-powered assistance.

## When to Use

Use this skill when the user needs to:
- Create detection logic for D&R rules from natural language
- Generate detection components without memorizing YAML syntax
- Build custom threat detection rules
- Convert threat descriptions into detection logic
- Learn D&R detection syntax through examples
- Create event matching criteria for security monitoring
- Develop detection logic for specific threat patterns

Common scenarios:
- "Create detection logic for suspicious PowerShell activity"
- "Generate a detection component to identify lateral movement"
- "Build detection for unusual network connections"
- "Create detection logic for ransomware indicators"
- "Generate detection for credential dumping techniques"

## What This Skill Does

This skill uses AI (Gemini) to generate D&R rule detection components from natural language descriptions. It validates the generated detection logic against your organization's D&R rule schema through an iterative process (up to 10 retries) to ensure the component is syntactically correct and uses valid event types, operators, and field paths. The skill returns validated YAML detection logic ready to use in a D&R rule.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for validation against org's D&R rule schema)
- **query**: Natural language description of what threat or behavior to detect

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Clear natural language description of the threat or behavior to detect
3. Understanding of what event types might be relevant (NEW_PROCESS, DNS_REQUEST, etc.)

### Step 2: Call the Tool

Use the `generate_dr_rule_detection` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="detect encoded PowerShell commands"
)
```

**Tool Details:**
- Tool: `mcp__limacharlie__generate_dr_rule_detection`
- Parameters:
  - `oid` (string, required): Organization ID for validation
  - `query` (string, required): Natural language description of what to detect

**How it works:**
- Sends the natural language query to Gemini AI with D&R detection prompt template
- Generates YAML detection component
- Validates using a minimal test D&R rule with the generated detection
- Retries up to 10 times if validation fails, refining the logic each iteration
- Cleans markdown formatting and returns pure YAML

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "detection": "event: NEW_PROCESS\nop: contains\npath: event/COMMAND_LINE\nvalue: ' -enc'\ncase sensitive: false"
}
```

**Success:**
- `detection`: YAML string containing validated detection logic ready to use in a D&R rule

**Possible Issues:**
- If validation fails after 10 retries, the tool returns an error indicating the AI couldn't generate valid detection logic
- Complex or ambiguous descriptions may produce unexpected detection logic - review carefully
- Some event types or operators may not be suitable for the described threat
- Generated detection may be too broad or too narrow - test before deploying

### Step 4: Format the Response

Present the result to the user:
- Show the generated detection YAML in a code block
- Explain what the detection logic does
- Mention which event types it monitors
- Highlight key conditions and operators
- Suggest testing the detection before deploying to production
- Remind them to pair with appropriate response actions

## Example Usage

### Example 1: Detect Encoded PowerShell

User request: "Create detection logic for encoded PowerShell commands"

Steps:
1. Get organization ID from context
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="detect encoded PowerShell commands"
)
```
3. Present the generated detection logic

Expected response:
```json
{
  "detection": "event: NEW_PROCESS\nop: and\nrules:\n  - op: contains\n    path: event/FILE_PATH\n    value: powershell\n    case sensitive: false\n  - op: or\n    rules:\n      - op: contains\n        path: event/COMMAND_LINE\n        value: ' -enc'\n      - op: contains\n        path: event/COMMAND_LINE\n        value: ' -e '\n      - op: contains\n        path: event/COMMAND_LINE\n        value: ' -encodedcommand'"
}
```

### Example 2: Detect Lateral Movement

User request: "Generate detection for lateral movement using PsExec"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="lateral movement using PsExec"
)
```

Expected response:
```json
{
  "detection": "event: NEW_PROCESS\nop: and\nrules:\n  - op: ends with\n    path: event/FILE_PATH\n    value: psexesvc.exe\n    case sensitive: false\n  - op: is\n    path: event/PARENT/FILE_PATH\n    value: C:\\Windows\\system32\\services.exe"
}
```

### Example 3: Detect Suspicious DNS Requests

User request: "Create detection for DNS requests to known malicious domains"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="DNS requests to domains ending in .xyz or .top which are often used for malware C2"
)
```

Expected response:
```json
{
  "detection": "event: DNS_REQUEST\nop: or\nrules:\n  - op: ends with\n    path: event/DOMAIN_NAME\n    value: .xyz\n  - op: ends with\n    path: event/DOMAIN_NAME\n    value: .top"
}
```

## Additional Notes

- **AI-Powered**: Uses Gemini AI with D&R detection-specific prompt templates
- **Validated**: Automatically validates against your organization's D&R rule schema
- **Iterative**: Retries up to 10 times to generate valid detection logic
- **Requires OID**: Validation needs organization context for schema compatibility
- **YAML Format**: Returns pure YAML (markdown formatting is cleaned)
- **Event Types**: Supports all LimaCharlie event types (NEW_PROCESS, DNS_REQUEST, NETWORK_CONNECTIONS, etc.)
- **Operators**: Uses valid D&R operators like `is`, `contains`, `starts with`, `ends with`, `matches`, `and`, `or`
- **Complex Logic**: Can generate nested logic with `and`/`or` operators
- **Path Notation**: Uses event path notation like `event/COMMAND_LINE` or `event/PARENT/FILE_PATH`
- **Detection Only**: This generates only the detection component - pair with response actions to create a complete rule
- **Testing**: Always test detection logic before deploying to production
- **Performance**: Consider performance impact of complex detection on high-volume events
- **False Positives**: Review and refine to minimize false positives
- **Best Practice**: Start with specific detections and broaden if needed
- **Combine with Response**: Use with `generate_dr_rule_respond` to create complete rules
- **Prompt Template**: Uses `prompts/gen_dr_detect.txt` from the MCP server

## Reference

For more details on the MCP tool implementation, check: `../lc-mcp-server/internal/tools/ai/ai.go` (generate_dr_rule_detection function)

For D&R rule syntax and event types, see LimaCharlie's Detection & Response documentation.
