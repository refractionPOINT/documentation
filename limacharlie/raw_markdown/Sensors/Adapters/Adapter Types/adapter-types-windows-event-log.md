# Windows Event Log

## Overview

This Adapter allows you to connect to the local Windows Event Logs API on Windows. This means this Adapter is only available from Windows builds and only works locally (will not connect to remote Windows instances).

## Configurations

Adapter Type: `wel`

  * `client_options`: common configuration for adapter as defined [here](../adapter-usage.md).

  * `evt_sources`: a comma separated list of elements in the format `SOURCE:FILTER`, where `SOURCE` is an Event Source name like `Application`, `System` or `Security` and `FILTER` is an `XPath` filter value as described in the documentation linked below.

### Infrastructure as Code Deployment

    # Windows Event Log (WEL) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-windows-event-log

    # Basic Event Sources:
    # evt_sources: "Security,System,Application"

    # With XPath Filters:
    # evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System:'*[System[Provider[@Name=\"Microsoft-Windows-Kernel-General\"]]]'"

    # File-Based Sources:
    # evt_sources: "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx:'*[System[(EventID=4624)]]'"

      wel:
        evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System,Application"
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_WEL"
          hostname: "prod-dc01.example.local"
          platform: "windows"
          sensor_seed_key: "wel-collector"
        write_timeout_sec: 30


### XPath Filter Examples

Security Events (High Priority):

      Security:'*[System[(Level=1 or Level=2 or Level=3)]]'

Logon Events Only:

      Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'

System Errors:

      System:'*[System[(Level=1 or Level=2)]]'

Specific Provider:

      Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'

## API Doc

See the [official documentation](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).
