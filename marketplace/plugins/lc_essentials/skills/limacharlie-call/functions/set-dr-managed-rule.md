
# Set Managed D&R Rule

Enable or disable a Detection & Response rule in the managed namespace.

## When to Use

Use this skill when the user needs to:
- Enable a managed D&R rule
- Disable a managed D&R rule
- Toggle the active status of a managed rule

Common scenarios:
- "Enable the 'credential_access_detection' managed rule"
- "Disable the 'lateral_movement' managed rule temporarily"
- "Turn on the ransomware detection rule"

## What This Skill Does

Enables or disables a D&R rule in the 'managed' namespace. This changes the rule's `is_enabled` status without modifying the detection logic or response actions.

## Required Information

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use `list-user-orgs` first.

- **oid**: Organization ID (UUID)
- **name**: Name of the rule to enable/disable
- **is_enabled**: true to enable, false to disable

## How to Use

### Step 1: Call the Tool

Use the `lc_call_tool` MCP tool:

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_managed_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]",
    "is_enabled": true
  }
)
```

**Tool Details:**
- Tool name: `set_dr_managed_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `name`: Rule name (string)
  - `is_enabled`: Whether rule is active (boolean)

### Step 2: Handle the Response

**Success:**
```json
{}
```
Rule status is immediately updated.

**Common Errors:**
- **400 Bad Request**: Invalid parameters
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Rule does not exist

## Example Usage

### Enable a managed rule

User request: "Enable the 'credential_access_detection' managed rule"

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_managed_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "credential_access_detection",
    "is_enabled": true
  }
)
```

### Disable a managed rule

User request: "Disable the 'lateral_movement_smb' rule temporarily"

```
mcp__limacharlie__lc_call_tool(
  tool_name="set_dr_managed_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "lateral_movement_smb",
    "is_enabled": false
  }
)
```

## Related Functions

- `get-dr-managed-rule` - View rule configuration before modifying
- `delete-dr-managed-rule` - Remove rules
- `list-dr-managed-rules` - List all managed rules

## Reference

For the tool implementation, see [CALLING_API.md](../../CALLING_API.md).

For D&R rule syntax and event types, use the `lookup-lc-doc` skill to search LimaCharlie documentation.
