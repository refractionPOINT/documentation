# get_time_when_sensor_has_data

Get the time range when a sensor has telemetry data available.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |
| sid | UUID | Yes | Sensor ID |
| start | integer | Yes | Start timestamp (Unix epoch seconds) |
| end | integer | Yes | End timestamp (Unix epoch seconds) |

## Returns

```json
{
  "sid": "xyz-sensor-id",
  "start": 1705000000,
  "end": 1705086400,
  "timestamps": [1705000000, 1705003600, 1705007200]
}
```

`timestamps` array contains time batches where data exists. Empty array means no data in range.

## Example

```
lc_call_tool(tool_name="get_time_when_sensor_has_data", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "sid": "xyz-sensor-id",
  "start": 1705000000,
  "end": 1705086400
})
```

## Notes

- Time range must be less than 30 days
- Useful before running expensive historical queries
- Data retention depends on org tier/policy
- Sensors may have gaps in their timeline
