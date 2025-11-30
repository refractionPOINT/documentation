# get_online_sensors

Retrieve all sensors currently online and connected to the LimaCharlie platform.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |

## Returns

```json
{
  "sensor-id-1": true,
  "sensor-id-2": true,
  "sensor-id-3": true
}
```

Returns a map of all online sensor IDs with `true` values. Empty map means no sensors online.

## Example

```
lc_call_tool(tool_name="get_online_sensors", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
})
```

## Notes

- Efficient single call to check all sensors
- For individual sensor status, use `is_online`
- For detailed sensor info with hostnames, use `list_sensors` with `online_only: true`
