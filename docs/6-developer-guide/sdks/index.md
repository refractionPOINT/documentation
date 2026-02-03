# SDK Documentation

Programmatic access to LimaCharlie via official SDKs.

## Overview

LimaCharlie provides official SDKs for Go and Python, enabling complete programmatic control of the platform:

- Sensor management and tasking
- Detection rule deployment
- Artifact collection and export
- Organization administration
- Real-time event streaming

## Available SDKs

### [Go SDK](go-sdk.md)

The Go SDK provides a comprehensive client library for building security automation, integrations, and custom tools.

**Installation:**
```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

**Key Features:**
- Type-safe API client
- Sensor management
- Detection & Response rule management
- Artifact collection
- Real-time event streaming (Firehose)
- Organization administration

### [Python SDK](python-sdk.md)

The Python SDK offers a full-featured interface perfect for security automation, data analysis, and rapid prototyping.

**Installation:**
```bash
pip install limacharlie
```

**Key Features:**
- Manager class for all platform operations
- Sensor tasking and management
- Real-time streaming (Firehose/Spout)
- Detection rule management via Hive
- LCQL query support
- Artifact and payload management

## Quick Start Examples

### Python
```python
import limacharlie

# Initialize the manager
manager = limacharlie.Manager(
    oid='your-org-id',
    secret_api_key='your-api-key'
)

# List all online sensors
sensors = manager.sensors()
for sensor in sensors:
    if sensor.isOnline():
        print(f"Online: {sensor.sid}")
```

### Go
```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Initialize client
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "your-org-id",
        APIKey: "your-api-key",
    },
)

// List sensors
sensors, err := client.GetSensors()
if err != nil {
    log.Fatal(err)
}
```

## Resources

- [API Documentation](https://api.limacharlie.io/openapi)
- [GitHub - Go SDK](https://github.com/refractionPOINT/go-limacharlie)
- [GitHub - Python SDK](https://github.com/refractionPOINT/python-limacharlie)
- [Community Slack](https://slack.limacharlie.io)

## Authentication

Both SDKs support multiple authentication methods:

1. **API Key**: Organization-level API key
2. **JWT**: User-specific JWT tokens
3. **Environment Variables**: Auto-load from `LC_OID` and `LC_API_KEY`

## Support

For SDK-specific questions:

- File issues on the respective GitHub repositories
- Join the [Community Slack](https://slack.limacharlie.io)
- Email [support@limacharlie.io](mailto:support@limacharlie.io)
