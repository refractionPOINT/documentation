
# Generate D&R Rule Respond Component

Generate Detection & Response (D&R) rule response components from natural language descriptions using AI-powered assistance.

## When to Use

Use this skill when the user needs to:
- Create response actions for D&R rules from natural language
- Generate automated response logic without memorizing YAML syntax
- Define what actions to take when threats are detected
- Convert response requirements into proper action syntax
- Learn D&R response syntax through examples
- Build multi-step automated responses
- Create response workflows for security incidents

Common scenarios:
- "Create response actions to isolate the sensor and report"
- "Generate response to kill the process and alert security team"
- "Build response actions for ransomware detection"
- "Create automated containment response"
- "Generate response to tag the sensor and create a ticket"

## What This Skill Does

This skill uses AI (Gemini) to generate D&R rule response components from natural language descriptions. It validates the generated response logic against your organization's D&R rule schema through an iterative process (up to 10 retries) to ensure the component uses valid action types and proper syntax. The skill returns validated YAML response actions ready to use in a D&R rule.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for validation against org's D&R rule schema)
- **query**: Natural language description of how to respond when detection triggers

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Clear natural language description of desired response actions
3. Understanding of available response actions (report, isolate, task, webhook, etc.)

### Step 2: Call the Tool

Use the `generate_dr_rule_respond` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="isolate the sensor and send a report with high severity"
)
```

**Tool Details:**
- Tool: `mcp__limacharlie__generate_dr_rule_respond`
- Parameters:
  - `oid` (string, required): Organization ID for validation
  - `query` (string, required): Natural language description of how to respond

**How it works:**
- Sends the natural language query to Gemini AI with D&R response prompt template
- Generates YAML response component with action array
- Validates using a dummy detection component and the generated response
- Retries up to 10 times if validation fails, refining the actions each iteration
- Cleans markdown formatting and returns pure YAML

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "respond": "- action: isolate network\n- action: report\n  name: suspicious_activity\n  metadata:\n    severity: high"
}
```

**Success:**
- `respond`: YAML string containing validated response actions ready to use in a D&R rule

**Possible Issues:**
- If validation fails after 10 retries, the tool returns an error indicating the AI couldn't generate valid response actions
- Complex or ambiguous descriptions may produce unexpected actions - review carefully
- Some actions may require additional parameters (e.g., webhook URLs)
- Generated responses may be too aggressive or too passive - adjust for your environment

### Step 4: Format the Response

Present the result to the user:
- Show the generated response YAML in a code block
- Explain what each action does
- Highlight the sequence of actions (they execute in order)
- Mention any metadata or parameters included
- Suggest testing the response actions in a safe environment first
- Remind them to pair with appropriate detection logic

## Example Usage

### Example 1: Report and Isolate

User request: "Create response actions to isolate the sensor and send a report"

Steps:
1. Get organization ID from context
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="isolate the sensor and send a report"
)
```
3. Present the generated response logic

Expected response:
```json
{
  "respond": "- action: report\n  name: threat_detected\n- action: isolate network"
}
```

### Example 2: Kill Process and Alert

User request: "Generate response to kill the malicious process and alert the security team via webhook"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="kill the process tree and send a webhook alert"
)
```

Expected response:
```json
{
  "respond": "- action: task\n  command: deny_tree\n- action: report\n  name: malware_killed\n- action: webhook\n  url: https://hooks.example.com/security-alerts"
}
```

### Example 3: Multi-Step Containment

User request: "Create comprehensive response: kill process, isolate sensor, tag as compromised, and create high-priority report"

Steps:
1. Get organization ID
2. Call tool:
```
mcp__limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="kill the process, isolate the sensor, tag as compromised, and create a high-priority report"
)
```

Expected response:
```json
{
  "respond": "- action: task\n  command: deny_tree\n- action: isolate network\n- action: add tag\n  tag: compromised\n  ttl: 86400\n- action: report\n  name: security_incident\n  metadata:\n    priority: high\n    response: automated_containment"
}
```

## Additional Notes

- **AI-Powered**: Uses Gemini AI with D&R response-specific prompt templates
- **Validated**: Automatically validates against your organization's D&R rule schema
- **Iterative**: Retries up to 10 times to generate valid response actions
- **Requires OID**: Validation needs organization context for schema compatibility
- **YAML Format**: Returns pure YAML array of actions (markdown formatting is cleaned)
- **Sequential Execution**: Actions execute in the order they appear in the array
- **Available Actions**:
  - `report` - Create detection report with name and optional metadata
  - `task` - Execute sensor task (deny_tree, remediate, etc.)
  - `isolate network` / `rejoin network` - Network isolation control
  - `add tag` / `remove tag` - Sensor tagging with optional TTL
  - `webhook` - Send HTTP webhook to external systems
  - `service request` - Trigger service integrations
- **Action Parameters**: Each action type has specific parameters (name, command, url, etc.)
- **Metadata**: Can include custom metadata in reports for enrichment
- **TTL**: Tags can have time-to-live for automatic removal
- **Testing**: Always test response actions in a safe environment first
- **Impact**: Consider operational impact (network isolation, process termination)
- **Reversibility**: Some actions (like deny_tree) cannot be undone
- **Detection Required**: Response component must be paired with detection logic
- **Best Practice**: Start with reporting, then add automated responses gradually
- **Combine with Detection**: Use with `generate_dr_rule_detection` to create complete rules
- **Prompt Template**: Uses `prompts/gen_dr_respond.txt` from the MCP server

## See Also

- **detection-engineering skill**: For end-to-end detection development workflow (understand → research → build → test → deploy). This function is used in **Phase 3.2 (Generate Response)** of that workflow.

## Reference

For more details on the MCP tool implementation, check: `../lc-mcp-server/internal/tools/ai/ai.go` (generate_dr_rule_respond function)

For D&R rule response actions and syntax, see LimaCharlie's Detection & Response documentation.
