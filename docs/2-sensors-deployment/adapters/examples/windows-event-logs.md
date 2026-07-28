# Windows Event Logs

This example collects Windows Event Logs (`wel`) natively from a Windows machine. Only the Windows Adapter can do this. Use this method to collect WEL without the LimaCharlie Windows Agent.

Note: This example uses PowerShell backtick (`` ` ``) line continuation. On Linux/macOS shells, use backslash (`\`) instead.

```powershell
.\lc_adapter.exe wel client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d `
    client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd `
    client_options.sensor_seed_key=domain-controller1 `
    client_options.hostname=domain-controller1 `
    client_options.platform=wel `
    evt_sources=security:*,application:*,system:*,Microsoft-Windows-Windows Defender/Operational:*
```

The example uses these options:

- `wel`: the method that the Adapter uses to collect data locally. The `wel` value uses a native local subscription to Windows Event Logs.
- `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
- `client_options.identity.oid=....`: the Organization ID in LimaCharlie that owns the installation key above.
- `client_options.platform=wel`: the type of data that this adapter receives. In this example, the data is `wel` events.
- `client_options.sensor_seed_key=....`: the value that identifies this instance of the Adapter. Keep this value. It lets you re-use the Sensor ID of this Adapter if you re-install the Adapter.
- `client_options.hostname=....`: specifies the sensor hostname for the adapter.
- `evt_sources=....`: a comma separated list of event channels to collect, with an XPath filter expression for each channel. The format is `CHANNEL_NAME:FILTER_EXPRESSION`. A filter of `*` selects all events. Common channels: `security`, `system` and `application`.
