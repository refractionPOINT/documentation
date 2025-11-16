
# Set Managed D&R Rule

Create or update a Detection & Response rule in the managed namespace.

## When to Use

Use this skill when the user needs to:
- Create a new managed D&R rule
- Update an existing managed rule
- Modify detection logic in a managed rule
- Import detection rules into the managed namespace

Common scenarios:
- "Create a managed rule to detect credential access"
- "Update the 'lateral_movement' managed rule with new detection logic"
- "Import this detection rule as a managed rule"

## What This Skill Does

Creates or updates a D&R rule in the 'managed' namespace. Rules are enabled by default and take effect immediately.

## Recommended Workflow: AI-Assisted Generation

**For reliable rule creation, use this workflow:**

1. **Gather Documentation** (if needed)
   Use `lookup-lc-doc` skill to search for D&R rule syntax, event types, and operators.

2. **Generate Detection Component**
   ```
   mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
     oid="[your-oid]",
     query="detect lateral movement using PsExec"
   )
   ```

3. **Generate Response Component**
   ```
   mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
     oid="[your-oid]",
     query="report and tag sensor as compromised"
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
- **rule_name**: Unique name within managed namespace
- **detection**: Detection logic (generate using `generate-dr-rule-detection`)
- **response**: Response actions (generate using `generate-dr-rule-respond`)

Optional:
- **is_replace**: true to update existing rule (default: true)
- **is_enabled**: true/false (default: true)

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
    "namespace": "managed",
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
- **409 Conflict**: Rule exists and is_replace is false

## Example Usage

### Complete AI-Assisted Workflow

User request: "Create a managed rule to detect suspicious PowerShell execution"

**Step 1: Generate detection**
```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="detect suspicious PowerShell execution"
)
```

**Step 2: Generate response**
```
mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  query="report as suspicious_powershell_execution"
)
```

**Step 3: Validate**
```
mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components(
  detect={...generated detection...},
  respond=[...generated response...]
)
```

**Step 4: Deploy**
```
mcp__plugin_lc-essentials_limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "suspicious_powershell",
    "namespace": "managed",
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
- `get-dr-managed-rule` - Verify rule after creation
- `delete-dr-managed-rule` - Remove rules
- `list-dr-managed-rules` - List all managed rules
- Use `lookup-lc-doc` skill for D&R syntax reference

## Reference

For the API implementation, see [CALLING_API.md](../../CALLING_API.md).

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
