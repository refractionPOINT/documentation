# Events

Understanding LimaCharlie's event types and telemetry is essential for building effective detection rules and analyzing security data.

## Overview

LimaCharlie sensors generate a wide variety of events representing system activity:

- Process lifecycle events
- Network connections
- File operations
- Registry modifications (Windows)
- DNS queries
- User authentication
- And many more...

## Event Categories

### Process Events
- NEW_PROCESS
- TERMINATE_PROCESS
- MODULE_LOAD
- CODE_IDENTITY

### Network Events
- NETWORK_CONNECTIONS
- DNS_REQUEST
- HTTP_REQUEST

### File Events
- FILE_CREATE
- FILE_DELETE
- FILE_MODIFIED
- FILE_READ

### Windows-Specific Events
- REGISTRY_CREATE
- REGISTRY_DELETE
- REGISTRY_WRITE
- WMI_ACTIVITY
- SERVICE_CHANGE

## Event Structure

All events share a common structure:

```json
{
  "routing": {
    "sid": "sensor-id",
    "oid": "organization-id",
    "event_type": "EVENT_TYPE",
    "event_time": 1234567890
  },
  "event": {
    // Event-specific fields
  }
}
```

## Telemetry

For detailed event schemas and field definitions, see the [Telemetry documentation](../Telemetry/index.md).
