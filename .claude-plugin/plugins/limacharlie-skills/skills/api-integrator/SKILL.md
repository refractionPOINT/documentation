---
name: api-integrator
description: Help users integrate with LimaCharlie using the REST API, Python SDK, or Go SDK for programmatic access to sensors, detection rules, events, and platform features.
---

# LimaCharlie API Integrator

This skill provides comprehensive guidance for integrating with LimaCharlie programmatically using the REST API, Python SDK, or Go SDK. Use this skill when users need help with API authentication, SDK usage, event streaming, programmatic sensor management, or building custom integrations.

## Quick Navigation

- **Python SDK Details**: See [PYTHON.md](PYTHON.md) for complete Python SDK reference
- **Go SDK Details**: See [GO.md](GO.md) for complete Go SDK reference
- **Complete Examples**: See [EXAMPLES.md](EXAMPLES.md) for working code examples
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for error handling and common issues

---

## Overview

### API Access Methods

LimaCharlie provides three primary methods for programmatic access:

1. **Python SDK**: Full-featured SDK with high-level abstractions for Python applications
2. **Go SDK**: Native Go client library for Go applications and services
3. **REST API**: Direct HTTP/HTTPS access for any programming language

### Key Capabilities

- **Sensor Management**: List, query, task, tag, and control endpoint sensors
- **Detection & Response**: Create, update, and manage D&R rules programmatically
- **Event Streaming**: Receive real-time events, detections, and audit logs
- **Artifact Collection**: Upload, download, and manage forensic artifacts
- **Organization Management**: Configure organizations, users, and permissions
- **Query & Search**: Execute LCQL queries and search historical data

### Base API URL

```
https://api.limacharlie.io
```

### Documentation Links

- REST API OpenAPI Spec: https://api.limacharlie.io/openapi
- Python SDK: https://github.com/refractionPOINT/python-limacharlie
- Go SDK: https://github.com/refractionPOINT/go-limacharlie

---

## Authentication

### Authentication Concepts

LimaCharlie uses JWT (JSON Web Tokens) for API authentication. There are two types of API keys:

1. **Organization API Keys**: Scoped to a specific organization (recommended)
2. **User API Keys**: Scoped to a user across all their organizations

### Organization API Keys (Recommended)

#### Components
- **OID (Organization ID)**: UUID format identifier for your organization
- **API Key**: UUID format secret key with specific permissions

#### Getting a JWT Token

**Using curl:**
```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "oid=YOUR_ORG_ID&secret=YOUR_API_KEY"
```

**Response:**
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

The JWT token is valid for **1 hour** and must be refreshed after expiration.

### API Key Permissions

API keys have granular permissions. Common permissions include:

- `sensor.get`: Read sensor information
- `sensor.task`: Send tasks to sensors
- `sensor.tag`: Add/remove sensor tags
- `dr.list`: List detection rules
- `dr.set`: Create/update detection rules
- `dr.del`: Delete detection rules
- `output.*`: Manage outputs (required for Firehose/Spout)

View all available permissions: https://app.limacharlie.io/owner_permissions

### API Key Flair

API keys support "flair" tags to modify behavior:

- `[bulk]`: Optimizes rate limits for high-volume API usage
  - Example: `automation-key[bulk]`
- `[segment]`: Limits visibility to resources created by this key only
  - Example: `third-party-integration[segment]`

### Managing API Keys

API keys are managed in the web interface:
**Organization > Access Management > REST API**

---

## Quick Start

### Python SDK

```bash
pip install limacharlie
```

```python
import limacharlie

manager = limacharlie.Manager(oid='YOUR_ORG_ID', secret_api_key='YOUR_API_KEY')
sensors = manager.sensors()
sensor = manager.sensor('SENSOR_ID')
sensor.task('os_processes')
```

See [PYTHON.md](PYTHON.md) for complete documentation.

### Go SDK

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

client := limacharlie.NewClient()
org := client.Organization(limacharlie.ClientOptions{})
sensors, err := org.ListSensors()
```

See [GO.md](GO.md) for complete documentation.

---

## Working with Timestamps

**IMPORTANT**: When users provide relative time offsets (e.g., "last hour", "past 24 hours", "last week"), you MUST dynamically compute the current epoch timestamp based on the actual current time. Never use hardcoded or placeholder timestamps.

### Computing Current Epoch

```python
import time

# Compute current time dynamically
current_epoch_seconds = int(time.time())
current_epoch_milliseconds = int(time.time() * 1000)
```

**The granularity (seconds vs milliseconds) depends on the specific API or MCP tool**. Always check the tool signature or API documentation to determine which unit to use.

### Common Relative Time Calculations

**Example: "List artifacts from the last hour"**
```python
end_time = int(time.time())  # Current time
start_time = end_time - 3600  # 1 hour ago

# Use with API calls
artifacts.listArtifacts(start_time=start_time, end_time=end_time)
```

**Common offsets (in seconds)**:
- 1 hour = 3600
- 24 hours = 86400
- 7 days = 604800
- 30 days = 2592000

**For millisecond-based APIs, multiply by 1000**.

### Critical Rules

**NEVER**:
- Use hardcoded timestamps
- Use placeholder values like `1234567890`
- Assume a specific current time

**ALWAYS**:
- Compute dynamically using `time.time()`
- Check the API/tool signature for correct granularity
- Verify the time range is valid (start < end)

---

## Common Operations

### 1. List Sensors
```python
sensors = manager.sensors()
sensor = manager.sensor('SENSOR_ID')
```

### 2. Tag Sensors
```python
sensor.addTag('production', ttl=3600)
sensor.removeTag('old-tag')
```

### 3. Task Sensors
```python
sensor.task('os_processes')
result = sensor.simpleRequest('os_info', timeout=30)
```

### 4. Isolate Sensors
```python
sensor.isolate()
sensor.rejoin()
```

### 5. Create Detection Rules
```python
from limacharlie import Hive, HiveRecord
hive = Hive(manager)
hive.set(HiveRecord(hive_name='dr-general', key='rule-name', data=rule_data))
```

---

## Event Streaming

### Spout vs Firehose

| Feature | Spout | Firehose |
|---------|-------|----------|
| Connection | Pull (HTTPS) | Push (requires open port) |
| NAT/Proxy | Works through NAT | Requires port forwarding |
| Reliability | Good for moderate volume | Best for high volume |
| Setup | Easier | More complex |
| Use case | Ad-hoc, development | Production, long-term |

### Spout (Pull-based)
```python
spout = limacharlie.Spout(manager, data_type='detect', is_parse=True)
for detection in spout:
    print(detection['detect_name'])
spout.shutdown()
```

### Firehose (Push-based)
```python
firehose = limacharlie.Firehose(manager, listen_on='0.0.0.0:4443', data_type='event')
firehose.start()
```

See [EXAMPLES.md](EXAMPLES.md) and [PYTHON.md](PYTHON.md) for complete examples.

---

## Common Sensor Tasks

```python
# System Information
'os_info'           # Operating system details
'os_processes'      # Running processes
'os_services'       # Installed services
'os_packages'       # Installed software
'os_autoruns'       # Autostart programs
'os_drivers'        # Loaded drivers (Windows)

# File Operations
'file_info PATH'    # File metadata
'file_get PATH'     # Download file
'file_hash PATH'    # Calculate file hash
'file_del PATH'     # Delete file

# Network Operations
'netstat'           # Network connections
'dns_resolve DOMAIN' # DNS lookup

# Process Operations
'mem_map PID'       # Process memory map
'kill PID'          # Terminate process

# Forensics
'history_dump'      # Event history
'hidden_module_scan' # Find hidden modules
```

---

## Best Practices

1. **Authentication**: Use environment variables, never hardcode credentials
2. **Rate Limiting**: Use `[bulk]` flair for high-volume operations
3. **Error Handling**: Always check sensor status before tasking
4. **Performance**: Batch operations, use streaming for large datasets
5. **Tracking**: Use investigation IDs to track related operations

```python
# Use environment variables
manager = limacharlie.Manager()  # Uses LC_OID and LC_API_KEY

# Check sensor status
if sensor.isOnline():
    sensor.task('os_processes')

# Investigation tracking
manager = limacharlie.Manager(inv_id='incident-2024-001')
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed error handling.

---

## Quick Reference

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sensors/{oid}` | GET | List all sensors |
| `/sensor/{oid}/{sid}` | GET | Get specific sensor |
| `/sensor/{oid}/{sid}/task` | POST | Task a sensor |
| `/sensor/{oid}/{sid}/tag` | POST/DELETE | Manage sensor tags |
| `/rules/{oid}` | GET/POST | Manage detection rules |
| `/artifacts/{oid}` | POST | Upload artifact |
| `/artifacts/{oid}/{aid}` | GET | Download artifact |
| `/orgs/{oid}` | GET | Get organization info |

### Python SDK Classes

- `Manager`: Main SDK entry point, organization management
- `Sensor`: Individual sensor operations and tasking
- `Hive`: Key-value storage for D&R rules and data
- `Spout`: Pull-based event streaming
- `Firehose`: Push-based event streaming
- `Artifacts`: Artifact upload/download management

### Go SDK Packages

- `limacharlie.Client`: Main client initialization
- `limacharlie.Organization`: Organization operations
- `limacharlie.Sensor`: Sensor management and tasking
- `limacharlie.CoreDRRule`: Detection rule structure
- `firehose`: Firehose streaming package

---

## Additional Resources

### Documentation
- **REST API Spec**: https://api.limacharlie.io/openapi
- **Python SDK**: https://github.com/refractionPOINT/python-limacharlie
- **Go SDK**: https://github.com/refractionPOINT/go-limacharlie
- **Main Docs**: https://docs.limacharlie.io

### Support
- **Email**: support@limacharlie.io
- **Community Slack**: https://slack.limacharlie.io
- **GitHub Issues**: Report SDK issues on respective GitHub repositories

### Important Notes
- JWT tokens expire after **1 hour**
- Use `[bulk]` flair for high-volume API usage
- Default rate limits apply unless configured otherwise
- Keep SDKs updated to latest versions
- Use least-privilege API keys for security

---

## See Also

- [PYTHON.md](PYTHON.md) - Complete Python SDK reference with all classes and methods
- [GO.md](GO.md) - Complete Go SDK reference with all packages and methods
- [EXAMPLES.md](EXAMPLES.md) - Complete working code examples for common use cases
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error handling, debugging, and common issues
