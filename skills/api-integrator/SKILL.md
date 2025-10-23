---
name: api-integrator
description: Help users integrate with LimaCharlie using the REST API, Python SDK, or Go SDK for programmatic access to sensors, detection rules, events, and platform features.
---

# LimaCharlie API Integrator

This skill provides comprehensive guidance for integrating with LimaCharlie programmatically using the REST API, Python SDK, or Go SDK. Use this skill when users need help with API authentication, SDK usage, event streaming, programmatic sensor management, or building custom integrations.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Python SDK](#python-sdk)
4. [Go SDK](#go-sdk)
5. [REST API](#rest-api)
6. [Common Operations](#common-operations)
7. [Event Streaming](#event-streaming)
8. [Best Practices](#best-practices)
9. [Error Handling](#error-handling)
10. [Complete Examples](#complete-examples)

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

### API Documentation

- REST API OpenAPI Spec: https://api.limacharlie.io/openapi
- Python SDK: https://github.com/refractionPOINT/python-limacharlie
- Go SDK: https://github.com/refractionPOINT/go-limacharlie

---

## Authentication

### Authentication Concepts

LimaCharlie uses JWT (JSON Web Tokens) for API authentication. There are two types of API keys:

1. **Organization API Keys**: Scoped to a specific organization (recommended)
2. **User API Keys**: Scoped to a user across all their organizations (powerful but riskier)

### Organization API Keys

Organization API keys are the recommended authentication method for most use cases.

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

### User API Keys

User API keys provide access across all organizations associated with a user account.

#### Getting a User JWT

```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "uid=YOUR_USER_ID&secret=YOUR_USER_API_KEY"
```

#### Scoping to Specific Organization

If the JWT is too large (HTTP 413 error), scope it to a specific organization:

```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "oid=YOUR_ORG_ID&uid=YOUR_USER_ID&secret=YOUR_USER_API_KEY"
```

### API Key Permissions

API keys have granular permissions. Common permissions include:

- `sensor.get`: Read sensor information
- `sensor.task`: Send tasks to sensors
- `sensor.tag`: Add/remove sensor tags
- `dr.list`: List detection rules
- `dr.set`: Create/update detection rules
- `dr.del`: Delete detection rules
- `output.*`: Manage outputs (required for Firehose/Spout)
- `ingestkey.ctrl`: Manage ingestion keys

View all available permissions:
```
https://app.limacharlie.io/owner_permissions
```

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

## Python SDK

### Installation

**Via pip:**
```bash
pip install limacharlie
```

**From source:**
```bash
git clone https://github.com/refractionPOINT/python-limacharlie.git
cd python-limacharlie
pip install -r requirements.txt
python setup.py install
```

**Requirements:**
- Python 3.6 or higher
- Dependencies: pyyaml>=5.1, requests>=2.20.0, python-dateutil>=2.8.0

### Authentication

#### Direct API Key Authentication

```python
import limacharlie

manager = limacharlie.Manager(
    oid='YOUR_ORGANIZATION_ID',
    secret_api_key='YOUR_API_KEY'
)
```

#### Environment Variables

```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

```python
import limacharlie

# Uses environment variables automatically
manager = limacharlie.Manager()
```

#### Configuration File

Create `~/.limacharlie`:

```yaml
# Default credentials
oid: "12345678-1234-1234-1234-123456789012"
api_key: "87654321-4321-4321-4321-210987654321"

# Named environments
env:
  production:
    oid: "prod-org-id"
    api_key: "prod-api-key"

  staging:
    oid: "staging-org-id"
    api_key: "staging-api-key"
```

```python
# Use specific environment
manager = limacharlie.Manager(environment='production')
```

### Core Manager Operations

#### Organization Information

```python
# Get organization info
org_info = manager.getOrgInfo()
print(f"Organization: {org_info['name']}")

# Get online sensor count
online_count = manager.getOnlineHosts()
print(f"Online sensors: {online_count}")
```

#### Listing Sensors

```python
# Get all sensors
sensors = manager.sensors()
for sid, info in sensors.items():
    print(f"Sensor: {sid} - {info['hostname']}")

# Get sensors with details
detailed_sensors = manager.sensors(with_details=True)

# Get sensors by tag
tagged_sensors = manager.getSensorsWithTag('production')

# Search by hostname
matching = manager.getHostnames(['web-*', 'db-*'])
```

#### Working with Individual Sensors

```python
# Get sensor object
sensor = manager.sensor('SENSOR_ID')

# Check if online
if sensor.isOnline():
    print(f"Sensor {sensor.getHostname()} is online")

# Get sensor information
platform = sensor.getPlatform()  # windows, linux, macos
architecture = sensor.getArchitecture()  # x64, x86, arm64
tags = sensor.getTags()

# Tag management
sensor.addTag('critical', ttl=3600)  # TTL in seconds
sensor.removeTag('old-tag')
```

#### Tasking Sensors

```python
# Simple task (fire and forget)
sensor.task('os_processes')

# Multiple tasks
sensor.task(['os_processes', 'os_services', 'netstat'])

# Task with investigation ID
sensor.setInvId('investigation-123')
sensor.task('history_dump')
```

#### Interactive Tasking (with responses)

```python
# Enable interactive mode
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    is_interactive=True,
    inv_id='investigation-123'
)

sensor = manager.sensor('SENSOR_ID')

# Simple request (blocking, waits for response)
result = sensor.simpleRequest('os_info', timeout=30)
print(result)

# Request with callback
def process_response(event):
    print(f"Received: {event}")

sensor.simpleRequest(
    'os_processes',
    timeout=30,
    until_completion=process_response
)
```

#### Sensor Isolation

```python
# Isolate sensor from network
sensor.isolate()

# Check isolation status
is_isolated = sensor.isIsolated()

# Rejoin network
sensor.rejoin()
```

### Detection & Response Rules (via Hive)

D&R rules are managed through the Hive key-value storage system.

```python
from limacharlie import Hive, HiveRecord

# Initialize Hive
hive = Hive(manager)

# Create a detection rule
rule_data = {
    'detect': {
        'event': 'NEW_PROCESS',
        'op': 'and',
        'rules': [
            {
                'op': 'contains',
                'path': 'event/COMMAND_LINE',
                'value': 'mimikatz'
            }
        ]
    },
    'respond': [
        {
            'action': 'report',
            'name': 'credential-theft-attempt'
        }
    ]
}

# Store rule in Hive
record = HiveRecord(
    hive_name='dr-general',
    partition_key=manager.oid,
    key='detect-mimikatz',
    data=rule_data,
    enabled=True
)
hive.set(record)

# List all D&R rules
rules = hive.list(
    hive_name='dr-general',
    partition_key=manager.oid
)

# Get specific rule
rule = hive.get('dr-general', manager.oid, 'detect-mimikatz')

# Delete rule
hive.delete('dr-general', manager.oid, 'detect-mimikatz')
```

### Event Streaming

#### Spout (Pull-based streaming)

```python
# Create a Spout for detections
spout = limacharlie.Spout(
    manager,
    data_type='detect',  # event, detect, audit, or tailored
    is_parse=True,
    tag='production',    # Optional: filter by tag
    cat='malware'        # Optional: filter by category
)

# Process detections
for detection in spout:
    print(f"Detection: {detection['detect_name']}")
    print(f"Sensor: {detection['sid']}")

    # Take automated action
    if detection['priority'] >= 4:
        sensor = manager.sensor(detection['sid'])
        sensor.isolate()

# Cleanup
spout.shutdown()
```

#### Firehose (Push-based streaming)

```python
# Create a Firehose (requires accessible port)
firehose = limacharlie.Firehose(
    manager,
    listen_on='0.0.0.0:4443',
    data_type='event',
    name='my_firehose',
    public_dest='YOUR_PUBLIC_IP:4443',
    is_parse=True,
    tag='production'  # Optional filter
)

firehose.start()

# Process events
while True:
    event = firehose.queue.get()
    if event.get('event_type') == 'NETWORK_CONNECT':
        dst = event.get('event', {}).get('DESTINATION')
        print(f"Connection to: {dst}")

firehose.shutdown()
```

### Artifact Management

```python
# Initialize Artifacts manager
artifacts = limacharlie.Artifacts(manager)

# List artifacts
artifact_list = artifacts.listArtifacts(
    start_time=1234567890,
    end_time=1234567999,
    sid='SENSOR_ID'
)

# Get artifact
artifact_data = artifacts.getArtifact('ARTIFACT_ID')

# Upload artifact
with open('evidence.txt', 'rb') as f:
    artifact_id = manager.createArtifact(
        name='evidence.txt',
        data=f.read(),
        ttl=86400  # 24 hours
    )
```

### Complete Python Example

```python
import limacharlie
import time

# Initialize
manager = limacharlie.Manager(
    oid='YOUR_ORG_ID',
    secret_api_key='YOUR_API_KEY'
)

# List all Windows sensors
sensors = manager.sensors()
windows_sensors = [
    sid for sid, info in sensors.items()
    if info.get('platform') == 'windows'
]

print(f"Found {len(windows_sensors)} Windows sensors")

# Check for suspicious processes
for sid in windows_sensors:
    sensor = manager.sensor(sid)
    if not sensor.isOnline():
        continue

    print(f"Scanning {sensor.getHostname()}...")

    # Task sensor for process list
    try:
        result = sensor.simpleRequest('os_processes', timeout=30)

        if result and 'processes' in result:
            for proc in result['processes']:
                name = proc.get('name', '').lower()
                if 'mimikatz' in name or 'lazagne' in name:
                    print(f"  [!] Suspicious process: {name}")
                    sensor.addTag('suspicious')
    except Exception as e:
        print(f"  Error: {e}")

    time.sleep(1)  # Rate limiting
```

---

## Go SDK

### Installation

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

For Firehose streaming:
```bash
go get github.com/refractionPOINT/go-limacharlie/firehose
```

### Authentication

#### Environment Variables

```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Uses environment variables
client := limacharlie.NewClient()
```

#### Direct Initialization

```go
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "your-organization-id",
        APIKey: "your-api-key",
    },
)
```

#### Configuration File

Create `.limacharlie.yaml`:

```yaml
environments:
  production:
    oid: "prod-org-id"
    api_key: "prod-api-key"

  development:
    oid: "dev-org-id"
    api_key: "dev-api-key"
```

```go
// Set environment
os.Setenv("LC_ENVIRONMENT", "production")
client := limacharlie.NewClient()
```

### Core Operations

#### Organization Management

```go
// Get organization handle
org := client.Organization(limacharlie.ClientOptions{
    OID: "target-org-id",
})

// Get organization info
info, err := org.GetInfo()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Organization: %s\n", info.Name)

// Get online sensor count
count, err := org.GetOnlineCount()
fmt.Printf("Online sensors: %d\n", count)
```

#### Sensor Management

```go
// List all sensors
sensors, err := org.ListSensors()
if err != nil {
    log.Fatal(err)
}

for _, sensor := range sensors {
    fmt.Printf("Sensor: %s - %s\n", sensor.SID, sensor.Hostname)
}

// Get specific sensor
sensor, err := org.GetSensor("sensor-id")
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Platform: %s\n", sensor.Platform)
fmt.Printf("Architecture: %s\n", sensor.Architecture)
fmt.Printf("Last Seen: %v\n", sensor.LastSeen)
```

#### Sensor Tagging

```go
// Get tags
tags, err := sensor.GetTags()

// Add tag
err = sensor.AddTag("production", 3600) // TTL in seconds (0 = permanent)

// Remove tag
err = sensor.RemoveTag("old-tag")
```

#### Sensor Actions

```go
// Isolate from network
err := sensor.IsolateFromNetwork()

// Rejoin network
err = sensor.RejoinNetwork()

// Delete sensor
err = sensor.Delete()
```

#### Tasking Sensors

```go
// Execute task
investigation := "investigation-id"
response, err := sensor.Task([]byte(`{
    "action": "os_processes"
}`), &investigation)

if err != nil {
    log.Fatal(err)
}
fmt.Printf("Response: %s\n", response)
```

### Detection & Response Rules

```go
// Define rule structure
rule := limacharlie.CoreDRRule{
    Name:      "suspicious-powershell",
    Namespace: "threats",
    Detect: map[string]interface{}{
        "event": "NEW_PROCESS",
        "op":    "and",
        "rules": []map[string]interface{}{
            {
                "op":    "contains",
                "path":  "event/COMMAND_LINE",
                "value": "powershell",
            },
            {
                "op":    "contains",
                "path":  "event/COMMAND_LINE",
                "value": "-encodedcommand",
            },
        },
    },
    Response: []map[string]interface{}{
        {
            "action": "report",
            "name":   "encoded-powershell-execution",
        },
    },
    IsEnabled: true,
}

// Add rule
err := org.DRRuleAdd(rule, false) // false = don't replace if exists

// List rules
rules, err := org.DRRules()
for name, rule := range rules {
    fmt.Printf("Rule: %s (Enabled: %v)\n", name, rule.IsEnabled)
}

// Delete rule
err = org.DRRuleDelete("suspicious-powershell", "threats")
```

### Artifact Management

```go
// Upload from bytes
artifactID, err := org.CreateArtifactFromBytes(
    []byte("artifact content"),
    "evidence.txt",
    "Investigation evidence",
    86400,        // TTL in seconds
    "text/plain", // Content type
)

// Upload from file
artifactID, err = org.CreateArtifactFromFile(
    "/path/to/file.bin",
    "binary-evidence.bin",
    "Binary evidence file",
    0, // No expiration
    "application/octet-stream",
)

// Download artifact
data, err := org.ExportArtifact("artifact-id")
```

### Complete Go Example

```go
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    // Initialize client
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})

    // Get all sensors
    sensors, err := org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Total sensors: %d\n", len(sensors))

    // Check each sensor
    offlineSensors := []string{}
    for _, sensor := range sensors {
        if time.Since(sensor.LastSeen) > 5*time.Minute {
            offlineSensors = append(offlineSensors, sensor.Hostname)
        }
    }

    if len(offlineSensors) > 0 {
        fmt.Printf("Offline sensors: %v\n", offlineSensors)
    }

    // Create detection rule
    rule := limacharlie.CoreDRRule{
        Name:      "ransomware-detection",
        Namespace: "threats",
        Detect: map[string]interface{}{
            "event": "FILE_CREATE",
            "op":    "matches",
            "path":  "event/FILE_PATH",
            "re":    ".*\\.(locked|encrypted)$",
        },
        Response: []map[string]interface{}{
            {
                "action":   "report",
                "name":     "potential-ransomware",
                "priority": 10,
            },
        },
        IsEnabled: true,
    }

    err = org.DRRuleAdd(rule, true)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("Rule added successfully")
}
```

---

## REST API

### Making Direct REST API Calls

All SDK operations ultimately use the REST API. You can make direct HTTP requests when needed.

### Authentication Header

```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Common Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sensors/{oid}` | GET | List all sensors |
| `/sensor/{oid}/{sid}` | GET | Get specific sensor |
| `/sensor/{oid}/{sid}/task` | POST | Task a sensor |
| `/sensor/{oid}/{sid}/tag` | POST | Add sensor tag |
| `/sensor/{oid}/{sid}/tag` | DELETE | Remove sensor tag |
| `/rules/{oid}` | GET | List detection rules |
| `/rules/{oid}` | POST | Create/update rule |
| `/rules/{oid}/{rule_name}` | DELETE | Delete rule |
| `/artifacts/{oid}` | POST | Upload artifact |
| `/artifacts/{oid}/{aid}` | GET | Download artifact |
| `/orgs/{oid}` | GET | Get organization info |

### Example: List Sensors

```bash
# Get JWT
JWT=$(curl -s -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "oid=YOUR_OID&secret=YOUR_API_KEY" | jq -r '.jwt')

# List sensors
curl -X GET "https://api.limacharlie.io/sensors/YOUR_OID" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json"
```

### Example: Task Sensor

```bash
curl -X POST "https://api.limacharlie.io/sensor/YOUR_OID/SENSOR_ID/task" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "command": "os_processes"
      }
    ]
  }'
```

### Example: Create Detection Rule (via Hive)

```bash
curl -X POST "https://api.limacharlie.io/hive/dr-general/YOUR_OID/my-rule" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "data": {
      "detect": {
        "event": "NEW_PROCESS",
        "op": "contains",
        "path": "event/FILE_PATH",
        "value": "malware.exe"
      },
      "respond": [
        {
          "action": "report",
          "name": "malware-execution"
        }
      ]
    }
  }'
```

---

## Common Operations

### Sensor Operations

#### List All Online Sensors

**Python:**
```python
sensors = manager.sensors()
online = [sid for sid, info in sensors.items() if info.get('online')]
```

**Go:**
```go
sensors, _ := org.ListSensors()
online := []string{}
for _, sensor := range sensors {
    if time.Since(sensor.LastSeen) < 5*time.Minute {
        online = append(online, sensor.SID)
    }
}
```

#### Get Sensors by Tag

**Python:**
```python
production_sensors = manager.getSensorsWithTag('production')
```

**Go:**
```go
taggedSensors, err := org.GetSensorsWithTag("production")
```

#### Search by Hostname Pattern

**Python:**
```python
web_servers = manager.getHostnames(['web-*', 'app-*'])
```

### Task Operations

Common sensor tasks:

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

### Detection Rule Patterns

#### Process-based Detection

```python
{
    'detect': {
        'event': 'NEW_PROCESS',
        'op': 'and',
        'rules': [
            {
                'op': 'contains',
                'path': 'event/FILE_PATH',
                'value': 'powershell.exe'
            },
            {
                'op': 'contains',
                'path': 'event/COMMAND_LINE',
                'value': '-enc'
            }
        ]
    },
    'respond': [
        {
            'action': 'report',
            'name': 'encoded-powershell'
        }
    ]
}
```

#### Network-based Detection

```python
{
    'detect': {
        'event': 'NETWORK_CONNECT',
        'op': 'and',
        'rules': [
            {
                'op': 'is',
                'path': 'event/DESTINATION/PORT',
                'value': 4444
            }
        ]
    },
    'respond': [
        {
            'action': 'report',
            'name': 'suspicious-port'
        },
        {
            'action': 'task',
            'command': {
                'action': 'isolate_network'
            }
        }
    ]
}
```

#### File-based Detection

```python
{
    'detect': {
        'event': 'FILE_CREATE',
        'op': 'matches',
        'path': 'event/FILE_PATH',
        're': '.*\\.(locked|encrypted|cry)$'
    },
    'respond': [
        {
            'action': 'report',
            'name': 'ransomware-indicator',
            'priority': 10
        }
    ]
}
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

### Spout Usage

**Python - Event Stream:**
```python
spout = limacharlie.Spout(
    manager,
    data_type='event',
    is_parse=True
)

for event in spout:
    event_type = event.get('event_type')
    if event_type == 'NEW_PROCESS':
        path = event['event']['FILE_PATH']
        print(f"Process started: {path}")

spout.shutdown()
```

**Python - Detection Stream:**
```python
spout = limacharlie.Spout(
    manager,
    data_type='detect',
    is_parse=True,
    cat='malware'  # Filter by category
)

for detection in spout:
    print(f"Detection: {detection['detect_name']}")
    print(f"Sensor: {detection['sid']}")
    print(f"Priority: {detection.get('priority', 0)}")

spout.shutdown()
```

**Python - Tailored Events:**
```python
spout = limacharlie.Spout(
    manager,
    data_type='tailored',
    event_type=['PROCESS_START', 'NETWORK_CONNECT'],
    is_parse=True
)

for event in spout:
    if event['event_type'] == 'NETWORK_CONNECT':
        dst = event['event']['DESTINATION']
        print(f"Connection to: {dst}")

spout.shutdown()
```

### Firehose Usage

```python
firehose = limacharlie.Firehose(
    manager,
    listen_on='0.0.0.0:4443',
    data_type='event',
    name='production_firehose',
    public_dest='YOUR_PUBLIC_IP:4443',
    is_parse=True,
    tag='production',  # Optional filter
    inv_id='inv-123'   # Optional investigation filter
)

firehose.start()

while True:
    event = firehose.queue.get()
    # Process event
    process_event(event)

firehose.shutdown()
```

---

## Best Practices

### 1. Authentication Security

**Store credentials securely:**
```python
# Good: Use environment variables
import os
api_key = os.environ.get('LC_API_KEY')

# Bad: Hardcode credentials
api_key = 'hardcoded-key'  # Never do this!
```

**Rotate API keys regularly:**
- Create new keys periodically
- Delete unused keys
- Use least-privilege permissions

### 2. Rate Limiting

**Implement backoff:**
```python
import time
from limacharlie.utils import LcApiException

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except LcApiException as e:
            if 'rate limit' in str(e).lower():
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

**Use bulk flair for high-volume:**
```
automation-key[bulk]
```

### 3. Error Handling

**Always handle errors:**
```python
try:
    sensor = manager.sensor('SENSOR_ID')
    result = sensor.task('os_processes')
except LcApiException as e:
    if 'not found' in str(e):
        print("Sensor not found")
    elif 'offline' in str(e):
        print("Sensor is offline")
    else:
        log.error(f"Unexpected error: {e}")
```

**Check sensor status before tasking:**
```python
if sensor.isOnline():
    result = sensor.task('os_processes')
else:
    print("Sensor is offline, queuing for later")
```

### 4. Performance Optimization

**Batch operations:**
```python
# Good: Get all sensors at once
sensors = manager.sensors(with_details=True)

# Bad: Individual requests
for sid in sensor_ids:
    sensor = manager.sensor(sid)
    info = sensor.getInfo()
```

**Use streaming for large datasets:**
```python
# Good: Stream events
spout = limacharlie.Spout(manager, 'event')
for event in spout:
    process(event)

# Bad: Query all at once (memory intensive)
events = manager.query('*', limit=1000000)
```

**Reuse client connections:**
```python
# Initialize once, reuse throughout application
manager = limacharlie.Manager(oid='ORG_ID', secret_api_key='API_KEY')
```

### 5. Investigation Tracking

**Use investigation IDs:**
```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    inv_id='incident-2024-001'
)

# All operations are now tagged with investigation ID
sensor.task('history_dump')
```

### 6. Logging and Auditing

**Enable audit logging:**
```python
import logging

def audit_log(msg):
    logging.info(f"[AUDIT] {msg}")

manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    print_debug_fn=audit_log
)
```

---

## Error Handling

### Common Error Types

#### Authentication Errors (401)

```python
try:
    manager = limacharlie.Manager('INVALID_OID', 'INVALID_KEY')
except LcApiException as e:
    if '401' in str(e):
        print("Authentication failed - check OID and API key")
```

#### Permission Errors (403)

```python
try:
    manager.add_output('output_name', config)
except LcApiException as e:
    if '403' in str(e):
        print("Insufficient permissions - missing 'output.*' permission")
```

#### Not Found Errors (404)

```python
try:
    sensor = manager.sensor('INVALID_SENSOR_ID')
except LcApiException as e:
    if '404' in str(e):
        print("Sensor not found")
```

#### Rate Limiting (429)

```python
try:
    result = manager.sensors()
except LcApiException as e:
    if e.http_code == 429:
        retry_after = e.headers.get('Retry-After', 60)
        print(f"Rate limited - retry after {retry_after}s")
        time.sleep(int(retry_after))
```

### Automatic Retry

**Python - Enable auto-retry:**
```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    isRetryQuotaErrors=True  # Auto-retry on 429
)
```

**Go - Manual retry:**
```go
var sensor *limacharlie.Sensor
maxRetries := 3

for i := 0; i < maxRetries; i++ {
    sensor, err = org.GetSensor(sensorID)
    if err == nil {
        break
    }

    if strings.Contains(err.Error(), "429") {
        time.Sleep(time.Second * time.Duration(i+1))
    } else {
        return err
    }
}
```

### Timeout Handling

**Python:**
```python
# Set timeout for interactive requests
result = sensor.simpleRequest('os_processes', timeout=60)
```

**Go:**
```go
// Use context for timeouts
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
```

---

## Complete Examples

### Example 1: Automated Threat Hunting

```python
import limacharlie
import time
from datetime import datetime

class ThreatHunter:
    def __init__(self, org_id, api_key):
        self.manager = limacharlie.Manager(org_id, api_key)
        self.suspicious_processes = [
            'mimikatz.exe',
            'lazagne.exe',
            'pwdump.exe'
        ]

    def hunt_suspicious_processes(self):
        """Hunt for suspicious processes across all sensors"""
        sensors = self.manager.sensors()
        online_sensors = [
            sid for sid, info in sensors.items()
            if info.get('online', False)
        ]

        print(f"Scanning {len(online_sensors)} sensors...")
        findings = []

        for sid in online_sensors:
            sensor = self.manager.sensor(sid)
            hostname = sensor.getHostname()

            try:
                result = sensor.simpleRequest('os_processes', timeout=30)
                if result and 'processes' in result:
                    for process in result['processes']:
                        name = process.get('name', '').lower()
                        for suspicious in self.suspicious_processes:
                            if suspicious.lower() in name:
                                findings.append({
                                    'sensor': sid,
                                    'hostname': hostname,
                                    'process': name,
                                    'pid': process.get('pid')
                                })
                                print(f"[!] {hostname}: {name}")
            except Exception as e:
                print(f"Error scanning {hostname}: {e}")

        return findings

    def monitor_detections(self, duration=3600):
        """Monitor for detections in real-time"""
        spout = limacharlie.Spout(
            self.manager,
            data_type='detect',
            is_parse=True
        )

        start = time.time()

        try:
            for detection in spout:
                if time.time() - start > duration:
                    break

                print(f"\n[DETECTION] {detection['detect_name']}")
                print(f"  Sensor: {detection['hostname']}")
                print(f"  Time: {datetime.fromtimestamp(detection['ts'])}")

                # Auto-respond to critical detections
                if detection.get('priority', 0) >= 4:
                    sensor = self.manager.sensor(detection['sid'])
                    print(f"  [!] Isolating sensor")
                    sensor.isolate()
        finally:
            spout.shutdown()

# Usage
hunter = ThreatHunter('YOUR_OID', 'YOUR_API_KEY')
findings = hunter.hunt_suspicious_processes()
print(f"\nFound {len(findings)} suspicious processes")
```

### Example 2: Incident Response Automation

```python
import limacharlie
from datetime import datetime
import hashlib

class IncidentResponder:
    def __init__(self, org_id, api_key):
        self.manager = limacharlie.Manager(
            org_id,
            api_key,
            is_interactive=True,
            inv_id=f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.hive = limacharlie.Hive(self.manager)

    def respond_to_ransomware(self, sensor_id):
        """Automated ransomware incident response"""
        print(f"Responding to ransomware on {sensor_id}")

        sensor = self.manager.sensor(sensor_id)
        hostname = sensor.getHostname()

        incident = {
            'id': hashlib.md5(f"{sensor_id}{datetime.now()}".encode()).hexdigest(),
            'type': 'ransomware',
            'sensor': sensor_id,
            'hostname': hostname,
            'timestamp': datetime.now().isoformat(),
            'status': 'investigating',
            'actions': []
        }

        # Step 1: Isolate
        print("  Isolating sensor...")
        sensor.isolate()
        incident['actions'].append({
            'action': 'isolate',
            'timestamp': datetime.now().isoformat()
        })

        # Step 2: Collect forensics
        print("  Collecting forensics...")
        tasks = ['os_processes', 'netstat', 'os_autoruns', 'history_dump']

        for task in tasks:
            try:
                result = sensor.simpleRequest(task, timeout=60)
                if result:
                    # Store in Hive
                    self.hive.set(limacharlie.HiveRecord(
                        hive_name='incidents',
                        key=f"{incident['id']}_{task}",
                        data=result,
                        ttl=2592000  # 30 days
                    ))
            except Exception as e:
                print(f"    Failed {task}: {e}")

        # Step 3: Memory dump
        print("  Collecting memory dump...")
        try:
            sensor.task('os_memory_dump')
            incident['actions'].append({
                'action': 'memory_dump',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"    Memory dump failed: {e}")

        # Step 4: Save incident record
        incident['status'] = 'contained'
        self.hive.set(limacharlie.HiveRecord(
            hive_name='incidents',
            key=incident['id'],
            data=incident,
            ttl=7776000  # 90 days
        ))

        print(f"  Incident {incident['id']} contained")
        return incident

# Usage
responder = IncidentResponder('YOUR_OID', 'YOUR_API_KEY')
incident = responder.respond_to_ransomware('SENSOR_ID')
```

### Example 3: Compliance Auditing (Go)

```go
package main

import (
    "fmt"
    "log"
    "sync"
    "time"

    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

type ComplianceChecker struct {
    org *limacharlie.Organization
}

func NewComplianceChecker(org *limacharlie.Organization) *ComplianceChecker {
    return &ComplianceChecker{org: org}
}

func (c *ComplianceChecker) CheckAllSensors() map[string]bool {
    sensors, err := c.org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    results := make(map[string]bool)
    var mu sync.Mutex
    var wg sync.WaitGroup

    for _, sensor := range sensors {
        if sensor.Platform != "windows" {
            continue
        }

        wg.Add(1)
        go func(s *limacharlie.Sensor) {
            defer wg.Done()

            // Check for required security software
            compliant := c.checkSensor(s)

            mu.Lock()
            results[s.Hostname] = compliant
            mu.Unlock()

            // Tag non-compliant sensors
            if !compliant {
                s.AddTag("non-compliant", 0)
            }
        }(sensor)
    }

    wg.Wait()
    return results
}

func (c *ComplianceChecker) checkSensor(sensor *limacharlie.Sensor) bool {
    // Check if Windows Defender is running
    response, err := sensor.Task([]byte(`{
        "action": "os_services",
        "filter": "WinDefend"
    }`), nil)

    if err != nil || len(response) == 0 {
        return false
    }

    return true
}

func main() {
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})

    checker := NewComplianceChecker(org)
    results := checker.CheckAllSensors()

    compliant := 0
    for hostname, isCompliant := range results {
        if isCompliant {
            compliant++
            fmt.Printf("[OK] %s\n", hostname)
        } else {
            fmt.Printf("[FAIL] %s\n", hostname)
        }
    }

    total := len(results)
    rate := float64(compliant) / float64(total) * 100
    fmt.Printf("\nCompliance Rate: %.1f%% (%d/%d)\n", rate, compliant, total)
}
```

### Example 4: Real-time Detection Response

```python
import limacharlie

def automated_response_handler():
    """Monitor detections and respond automatically"""
    manager = limacharlie.Manager()

    # Create Spout for detections
    spout = limacharlie.Spout(
        manager,
        data_type='detect',
        is_parse=True
    )

    print("Monitoring for detections...")

    try:
        for detection in spout:
            detect_name = detection['detect_name']
            priority = detection.get('priority', 0)
            sid = detection['sid']
            hostname = detection.get('hostname', 'unknown')

            print(f"\n[{priority}] {detect_name} on {hostname}")

            sensor = manager.sensor(sid)

            # Response based on detection type
            if 'ransomware' in detect_name.lower():
                print("  -> Isolating sensor")
                sensor.isolate()
                sensor.task('history_dump')
                sensor.addTag('ransomware-incident')

            elif 'credential' in detect_name.lower():
                print("  -> Killing process and collecting memory")
                event = detection.get('event', {})
                pid = event.get('PROCESS_ID')
                if pid:
                    sensor.task(f'kill {pid}')
                sensor.task('os_memory_dump')

            elif priority >= 4:
                print("  -> High priority - collecting forensics")
                sensor.task(['os_processes', 'netstat', 'history_dump'])
                sensor.addTag('high-priority-detection')

            else:
                print("  -> Logged for review")

    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        spout.shutdown()

# Run
automated_response_handler()
```

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

### API Limits
- JWT tokens expire after **1 hour**
- Rate limits vary by API key flair (use `[bulk]` for high volume)
- Default rate limits apply unless otherwise configured

### Best Practices Summary
1. Use environment variables for credentials
2. Implement proper error handling and retries
3. Use investigation IDs to track related operations
4. Leverage streaming for real-time data
5. Batch operations when possible
6. Monitor API usage and respect rate limits
7. Keep SDKs updated to latest versions
8. Use least-privilege API keys
