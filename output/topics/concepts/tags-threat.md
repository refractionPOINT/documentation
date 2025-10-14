# Threat Hunting

Threat hunting is the practice of proactively searching for cyber threats that may have evaded existing security measures. LimaCharlie provides powerful capabilities for threat hunters to search through telemetry, create detection rules, and investigate potential security incidents.

## Key Capabilities

LimaCharlie enables threat hunting through several core features:

- **Real-time telemetry**: Access to comprehensive endpoint telemetry data
- **Historical search**: Query past events stored in your data retention period
- **Detection & Response (D&R) rules**: Create custom detection logic
- **Artifacts**: Collect and analyze forensic artifacts from endpoints
- **Timelines**: Investigate event sequences across your environment

## Getting Started with Threat Hunting

### Accessing Telemetry

You can access sensor telemetry through:

1. **Live view**: Real-time streaming of events from sensors
2. **Historical search**: Query past events using the search interface
3. **API access**: Programmatic access to telemetry data

### Creating Detection Rules

D&R rules allow you to define custom detection logic:

```yaml
detect:
  event: NEW_PROCESS
  op: starts with
  path: event/FILE_PATH
  value: 'C:\Windows\System32\cmd.exe'
respond:
  - action: report
    name: suspicious_cmd_execution
```

### Hunting with Queries

Use the search interface to hunt for specific indicators:

```
event_type:NEW_PROCESS AND file_path:*\powershell.exe*
```

## Best Practices

1. **Start with a hypothesis**: Define what you're looking for before hunting
2. **Use multiple data sources**: Correlate events across different telemetry types
3. **Document findings**: Keep records of your hunting activities
4. **Automate detections**: Convert successful hunts into D&R rules
5. **Iterate and refine**: Continuously improve your hunting techniques

## Common Hunting Scenarios

### Lateral Movement Detection

Look for unusual network connections or authentication events:

```
event_type:NETWORK_CONNECTIONS AND dst_port:445
```

### Persistence Mechanisms

Search for common persistence techniques:

```
event_type:NEW_REGISTRY_KEY AND registry_path:*\CurrentVersion\Run*
```

### Suspicious Process Execution

Identify unusual process patterns:

```
event_type:NEW_PROCESS AND (parent_process:*\excel.exe* OR parent_process:*\word.exe*)
```