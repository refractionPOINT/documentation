# WEL Monitoring

Windows Event Logs (WEL) are a critical source of security and operational data on Windows systems. LimaCharlie provides comprehensive WEL monitoring capabilities to help you detect threats, troubleshoot issues, and maintain compliance.

## Overview

WEL monitoring in LimaCharlie allows you to:

- Collect and analyze Windows Event Logs in real-time
- Create detection rules based on event patterns
- Forward events to external systems
- Investigate security incidents using event data

## Enabling WEL Collection

To enable WEL collection on your Windows sensors:

1. Navigate to your organization in the LimaCharlie web interface
2. Go to **Sensors** and select the target sensor or sensor group
3. Enable WEL collection in the sensor configuration
4. Specify which event log channels to monitor

## Event Log Channels

Common Windows Event Log channels include:

- **Security**: Authentication, authorization, and security events
- **System**: System component events, driver issues
- **Application**: Application-specific events
- **Windows PowerShell**: PowerShell execution events
- **Microsoft-Windows-Sysmon/Operational**: Sysmon events (if installed)

## Creating Detection Rules

You can create D&R (Detection & Response) rules based on WEL events. Rules can match on:

- Event IDs
- Event sources
- Event data fields
- Patterns across multiple events

## Best Practices

- Focus on high-value security events (e.g., Event ID 4624, 4625, 4688)
- Use filtering to reduce noise and storage costs
- Combine WEL monitoring with other telemetry sources
- Regularly review and tune your detection rules

## Example Use Cases

- **Failed Login Detection**: Monitor Event ID 4625 for failed authentication attempts
- **Privilege Escalation**: Track Event ID 4672 for special privilege assignments
- **Process Creation**: Use Event ID 4688 to track new process creation
- **Service Installation**: Monitor Event ID 7045 for new service installations

## Related Resources

- [Detection & Response Rules](/docs/en/detection-and-response-rules)
- [Windows Sensor Configuration](/docs/en/windows-sensor-configuration)
- [Event Forwarding](/docs/en/event-forwarding)