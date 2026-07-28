# Windows Event Log

## Overview

This Adapter connects to the local Windows Event Logs API on Windows. The Adapter is available only in Windows builds, and it works only locally. It does not connect to remote Windows instances.

## Configurations

Adapter Type: `wel`

- `client_options`: see [common adapter configuration](../usage.md).
- `evt_sources`: a comma separated list of elements in the format `SOURCE:FILTER`. `SOURCE` is an Event Source name, such as `Application`, `System`, or `Security`. `FILTER` is an `XPath` filter value, as described in the documentation linked below.
- `write_timeout_sec`: number of seconds before a write to LimaCharlie times out (default: 600).

### Configuration File Example

```yaml
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
    platform: "wel"
    sensor_seed_key: "wel-collector"
  write_timeout_sec: 30
```

### XPath Filter Examples

Security Events (High Priority):

```text
  Security:'*[System[(Level=1 or Level=2 or Level=3)]]'
```

Logon Events Only:

```text
  Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'
```

System Errors:

```text
  System:'*[System[(Level=1 or Level=2)]]'
```

Specific Provider:

```text
  Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'
```

## API Doc

See the [Microsoft documentation for consuming events](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).
