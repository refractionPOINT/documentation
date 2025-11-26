
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

5. **Deploy Rule** (this tool call)

## Required Information

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list_user_orgs` first.

- **oid**: Organization ID (UUID)
- **name**: Unique name for the rule (alphanumeric, hyphens, underscores)
- **detect**: Detection logic object (generate using `generate_dr_rule_detection`)
- **respond**: Response actions array (generate using `generate_dr_rule_respond`)

Optional:
- **is_enabled**: true/false to enable/disable rule (default: true)

## How to Use

### Step 1: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_general_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]",
    "detect": {...detection logic object...},
    "respond": [...response actions array...],
    "is_enabled": true
  }
)
```

**Tool Details:**
- Tool name: `set_dr_general_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `name`: Rule name (string)
  - `detect`: Detection logic (object)
  - `respond`: Response actions (array)
- Optional parameters:
  - `is_enabled`: Whether rule is active (boolean, default: true)

### Step 2: Handle the Response

**Success:**
```json
{}
```
Rule is immediately active.

**Common Errors:**
- **400 Bad Request**: Invalid syntax - use `validate_dr_rule_components` first
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
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "detect-encoded-powershell",
    "detect": {
      "event": "NEW_PROCESS",
      "op": "contains",
      "path": "event/COMMAND_LINE",
      "value": "powershell -enc"
    },
    "respond": [
      {
        "action": "report",
        "name": "encoded_powershell"
      }
    ],
    "is_enabled": true
  }
)
```

### Example: Lookup-Based Threat Detection

When using lookups for IOC-based detection (e.g., from threat intelligence), use the `op: lookup` operator with the correct resource format.

**Important**: When creating rules via the API (JSON format), use `hive://lookup/` prefix for the resource:

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "detect-malicious-domains",
    "detect": {
      "op": "lookup",
      "path": "event/DOMAIN_NAME",
      "resource": "hive://lookup/threat-intel-domains"
    },
    "respond": [
      {
        "action": "report",
        "name": "malicious-domain-detected"
      }
    ],
    "is_enabled": true
  }
)
```

**Important**: Always use `hive://lookup/lookup-name` format. Never use `lookup://lookup-name`, which will cause an error:
```
error: resource category not allowed here
```

## Related Functions

- `generate_dr_rule_detection` - AI-assisted detection component generation
- `generate_dr_rule_respond` - AI-assisted response actions generation
- `validate_dr_rule_components` - Validate syntax before deployment
- `generate_sensor_selector` - Generate sensor targeting expressions
- `get_dr_general_rule` - Verify rule after creation
- `delete_dr_general_rule` - Remove rules
- `set_lookup` - Create lookup tables for IOC-based detection
- Use `lookup-lc-doc` skill for D&R syntax reference and event types

## See Also

- **detection-engineering skill**: For end-to-end detection development workflow (understand → research → build → test → deploy). This function is used in **Phase 5 (Deploy)** of that workflow.

## Reference

For the tool implementation, see [CALLING_API.md](../../CALLING_API.md).

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
