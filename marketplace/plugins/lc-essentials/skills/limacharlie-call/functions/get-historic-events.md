# get_historic_events

Retrieve historical telemetry events for a specific sensor within a time range.

## CRITICAL: Timestamps in SECONDS

API parameters require Unix epoch in **seconds** (10 digits), NOT milliseconds (13 digits).

Detection/event data contains timestamps in milliseconds → **divide by 1000** before using.

```
Detection timestamp: 1764445150453 (ms)  ÷ 1000  →  API parameter: 1764445150 (seconds)
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |
| sid | UUID | Yes | Sensor ID |
| start | integer | Yes | Start time (Unix epoch **seconds**) |
| end | integer | Yes | End time (Unix epoch **seconds**) |
| limit | integer | No | Max events (default=1000) |
| event_type | string | No | Filter by type (e.g., "NEW_PROCESS", "DNS_REQUEST") |

## Returns

```json
{
  "events": [
    {
      "event": {
        "TIMESTAMP": 1705761234567,
        "EVENT_TYPE": "NEW_PROCESS",
        "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
        "COMMAND_LINE": "cmd.exe /c whoami"
      },
      "routing": {
        "sid": "xyz-sensor-id",
        "hostname": "SERVER01"
      }
    }
  ]
}
```

## Example

```
lc_call_tool(tool_name="get_historic_events", parameters={
  "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
  "sid": "xyz-sensor-id",
  "start": 1705761234,
  "end": 1705764834,
  "event_type": "NEW_PROCESS",
  "limit": 500
})
```

## Common Event Types

`NEW_PROCESS`, `DNS_REQUEST`, `NETWORK_CONNECTIONS`, `FILE_CREATE`, `FILE_DELETE`, `REGISTRY_CREATE`

## Notes

- Use `get_time_when_sensor_has_data` to verify data availability first
- Very large time ranges may timeout - narrow the window
- For cross-sensor queries, use `run_lcql_query` instead
- Related: `get_historic_detections`, `run_lcql_query`
