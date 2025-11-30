# set_dr_managed_rule

Enable or disable a D&R rule in the managed namespace.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |
| name | string | Yes | Rule name (case-sensitive) |
| is_enabled | boolean | Yes | true to enable, false to disable |

## Returns

```json
{}
```

Empty response indicates success. Status is immediately updated.

## Example

**Enable a rule:**
```
lc_call_tool(tool_name="set_dr_managed_rule", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "name": "credential_access_detection",
  "is_enabled": true
})
```

**Disable a rule:**
```
lc_call_tool(tool_name="set_dr_managed_rule", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "name": "lateral_movement_smb",
  "is_enabled": false
})
```

## Notes

- Only toggles enabled status; does not modify detection logic
- Changes take effect immediately
- Related: `get_dr_managed_rule`, `list_dr_managed_rules`, `delete_dr_managed_rule`
