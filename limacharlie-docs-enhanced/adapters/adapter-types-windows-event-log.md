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
```

### XPath Filter Examples

Security Events (High Priority):

```
  Security:'*[System[(Level=1 or Level=2 or Level=3)]]'
```

Logon Events Only:

```
  Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'
```

System Errors:

```
  System:'*[System[(Level=1 or Level=2)]]'
```

Specific Provider:

```
  Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'
```

## API Doc

See the [official documentation](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.