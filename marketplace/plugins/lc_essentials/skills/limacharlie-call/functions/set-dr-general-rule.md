
# Set D&R General Rule

Create or update a custom Detection and Response (D&R) rule in the general namespace.

## When to Use

Use this skill when the user needs to:
- Create a new custom detection rule
- Update an existing custom rule
- Implement organization-specific detection logic
- Define automated response actions for threats
- Target rules to specific sensors or sensor groups

Common scenarios:
- "Create a rule to detect suspicious PowerShell activity"
- "Update the ransomware detection rule with new IOCs"
- "Add a detection for unauthorized network connections"
- "Build a rule that isolates sensors when malware is detected"

## What This Skill Does

Creates a new D&R rule or updates an existing one in the general namespace (custom rules). Rules become active immediately unless explicitly disabled.

## Recommended Workflow: AI-Assisted Generation

**For reliable rule creation, use this workflow:**

1. **Gather Documentation** (if needed)
   Use `lookup-lc-doc` skill to search for D&R rule syntax, event types, operators, and response actions.

2. **Generate Detection Component**
   ```
   mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
     oid="[your-oid]",
     query="detect encoded PowerShell commands"
   )
   ```

3. **Generate Response Component**
   ```
   mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
     oid="[your-oid]",
     query="report the detection and isolate the sensor"
   )
   ```

4. **Validate Components**
   ```
   mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
     detect={...generated detection...},
     respond=[...generated response...]
   )
   ```

5. **Deploy Rule** (this API call)

## Required Information

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list-user-orgs` first.

- **oid**: Organization ID (UUID)
- **rule_name**: Unique name for the rule (alphanumeric, hyphens, underscores)
- **detection**: Detection logic (generate using `generate-dr-rule-detection`)
- **response**: Response actions (generate using `generate-dr-rule-respond`)

Optional:
- **is_replace**: true to update existing rule (default: true)
- **is_enabled**: true/false to enable/disable rule (default: true)
- **expire_on**: Unix timestamp for auto-deletion

## How to Use

### Step 1: Call the API

Use the `lc_api_call` MCP tool:

```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/rules/[organization-id]",
  body={
    "name": "[rule-name]",
    "namespace": "general",
    "is_replace": true,
    "is_enabled": true,
    "detection": "[json-string-of-detect-logic]",
    "response": "[json-string-of-respond-actions]"
  }
)
```

**Important**: The `detection` and `response` fields must be JSON-encoded strings, not objects.

### Step 2: Handle the Response

**Success (200):**
```json
{
  "status_code": 200,
  "body": {}
}
```
Rule is immediately active.

**Common Errors:**
- **400 Bad Request**: Invalid syntax - use `validate-dr-rule-components` first
- **403 Forbidden**: Insufficient permissions
- **422 Unprocessable Entity**: Validation failed - check event types and operators

## Example Usage

### Complete AI-Assisted Workflow

User request: "Create a rule to detect and report encoded PowerShell commands"

**Step 1: Generate detection**
```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="detect encoded PowerShell commands"
)
// Returns YAML detection component
```

**Step 2: Generate response**
```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="report as encoded_powershell"
)
// Returns YAML response component
```

**Step 3: Validate**
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={...generated detection...},
  respond=[...generated response...]
)
// Returns {"valid": true, "message": "..."}
```

**Step 4: Deploy**
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "detect-encoded-powershell",
    "namespace": "general",
    "is_replace": true,
    "is_enabled": true,
    "detection": "{...validated detection JSON string...}",
    "response": "[...validated response JSON string...]"
  }
)
```

## Related Functions

- `generate-dr-rule-detection` - AI-assisted detection component generation
- `generate-dr-rule-respond` - AI-assisted response actions generation
- `validate-dr-rule-components` - Validate syntax before deployment
- `generate-sensor-selector` - Generate sensor targeting expressions
- `get-dr-general-rule` - Verify rule after creation
- `delete-dr-general-rule` - Remove rules
- Use `lookup-lc-doc` skill for D&R syntax reference and event types

## Reference

For the API implementation, see [CALLING_API.md](../../CALLING_API.md).

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
