# Adapter Examples

## Stdin

This example is similar to the Syslog example above, except it uses the CLI Adapter and receives the data from the CLI's STDIN interface. This method is perfect for ingesting arbitrary logs on disk or from other applications locally.

```
./lc_adapter stdin client_options...
```

## Stdin JSON

This example is similar to the Stdin example above, except it assumes the data being read is JSON, not just text. If your data source is already JSON, it's much simpler to let LimaCharlie do the JSON parsing directly.

```
./lc_adapter stdin client_options...
```

## Windows Event Logs

This example shows collecting Windows Event Logs (wel) from a Windows box natively (and therefore is only available using the Windows Adapter). This is useful for cases where you'd like to collect WEL without running the LimaCharlie Windows Agent.