# LimaCharlie Python SDK Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Authentication](#authentication)
4. [Core Classes](#core-classes)
5. [Organization](#organization)
6. [Sensor Management](#sensor-management)
7. [Detection and Response Rules](#detection-and-response-rules)
8. [Real-time Data Streaming](#real-time-data-streaming)
9. [Artifacts](#artifacts)
10. [Hive Operations](#hive-operations)
11. [Search (LCQL)](#search-lcql)
12. [Extensions](#extensions)
13. [Infrastructure as Code](#infrastructure-as-code)
14. [Error Handling](#error-handling)
15. [Complete Examples](#complete-examples)

## Overview

The LimaCharlie Python SDK provides a comprehensive interface for interacting with the LimaCharlie SecOps Cloud Platform. This SDK enables programmatic access to all platform features including sensor management, detection and response rules, real-time event streaming, and artifact collection.

### Key Features
- **Organization Management**: Create, configure, and manage LimaCharlie organizations
- **Sensor Operations**: Deploy, monitor, and control endpoint sensors
- **Detection & Response**: Create and manage detection rules with automated response actions
- **Real-time Streaming**: Receive events, detections, and audit logs in real-time
- **Artifact Management**: Collect and manage forensic artifacts
- **LCQL Queries**: Execute, validate, and save search queries
- **Hive Storage**: Key-value configuration store for rules, secrets, playbooks, and more
- **Infrastructure as Code**: Pull/push org configuration as version-controlled YAML files

### SDK Version
Current version: 5.0.0

## Installation

### Requirements
- Python 3.9 or higher
- pip package manager

### Install via pip
```bash
pip install limacharlie
```

### Install from source
```bash
git clone https://github.com/refractionPOINT/python-limacharlie.git
cd python-limacharlie
pip install -e ".[dev]"
```

### Dependencies
Core dependencies (automatically installed):

- `requests` - HTTP client
- `click` - CLI framework
- `pyyaml` - YAML parsing
- `jmespath` - Data filtering
- `rich` - Terminal output formatting
- `cryptography` - Encryption

## Authentication

### Authentication Methods

The LimaCharlie SDK supports multiple authentication methods:

1. **API Key Authentication** (Recommended for automation)
2. **OAuth Authentication** (For user-based access)
3. **Environment-based Authentication** (Using configuration files)

### Credential Resolution Order

Credentials are resolved in priority order (highest first):

1. Explicit parameters passed to `Client()`
2. `LC_OID`, `LC_API_KEY`, `LC_UID` environment variables
3. Named environment from `LC_CURRENT_ENV` (or 'default')
4. Default credentials in `~/.limacharlie` config file

### API Key Authentication

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization

# Direct API key authentication
client = Client(
    oid='YOUR_ORGANIZATION_ID',  # UUID format
    api_key='YOUR_API_KEY'       # UUID format
)
org = Organization(client)
```

### Environment-based Authentication

The SDK can read credentials from environment variables or configuration files:

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization

# Using environment variables
# Set: LC_OID="your-org-id"
# Set: LC_API_KEY="your-api-key"
client = Client()
org = Organization(client)

# Using a specific environment from config file
client = Client(environment='production')
org = Organization(client)
```

### Configuration File Format

Create a file at `~/.limacharlie` or specify with `LC_CREDS_FILE` environment variable:

```yaml
# Default credentials
oid: "12345678-1234-1234-1234-123456789012"
api_key: "87654321-4321-4321-4321-210987654321"

# Named environments
env:
  production:
    oid: "12345678-1234-1234-1234-123456789012"
    api_key: "87654321-4321-4321-4321-210987654321"

  staging:
    oid: "87654321-4321-4321-4321-210987654321"
    api_key: "12345678-1234-1234-1234-123456789012"
```

### User-based Authentication

```python
from limacharlie.client import Client

# Authenticate as a user instead of organization
client = Client(
    uid='USER_ID',
    api_key='USER_API_KEY'
)
```

## Core Classes

### Architecture

```
limacharlie
├── client.Client              # HTTP client with JWT and retry logic
├── sdk/
│   ├── organization.Organization  # Main entry point for org operations
│   ├── sensor.Sensor             # Individual sensor management
│   ├── hive.Hive                 # Key-value configuration store
│   ├── hive.HiveRecord           # Individual hive record
│   ├── dr_rules.DRRules          # D&R rule management
│   ├── fp_rules.FPRules          # False positive rule management
│   ├── search.Search             # LCQL query execution
│   ├── firehose.Firehose         # Real-time push streaming
│   ├── spout.Spout               # Real-time pull streaming
│   ├── extensions.Extensions     # Extension management
│   ├── artifacts.Artifacts       # Artifact collection/retrieval
│   ├── payloads.Payloads         # Payload management
│   ├── replay.Replay             # Rule replay
│   ├── configs.Configs           # Infrastructure as Code
│   └── ...                       # Additional modules
└── errors                        # Custom exception hierarchy
```

### Client

The `Client` handles HTTP communication, JWT generation/refresh, retry with exponential backoff, and rate limit awareness.

```python
from limacharlie.client import Client

# Basic usage
client = Client(oid='ORG_ID', api_key='API_KEY')

# As context manager
with Client(oid='ORG_ID', api_key='API_KEY') as client:
    data = client.request("GET", "sensors")
```

## Organization

The `Organization` class is the primary entry point for interacting with a LimaCharlie organization.

### Core Methods

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization

client = Client(oid='ORG_ID', api_key='API_KEY')
org = Organization(client)

# Get organization information
org_info = org.get_info()
# Returns: {'oid': '...', 'name': '...', ...}

# Get organization URLs
urls = org.get_urls()
# Returns: {'webapp': 'https://...', 'api': 'https://...', 'hooks': '...', ...}

# Get usage statistics
stats = org.get_stats()

# Get organization configuration
value = org.get_config('config_name')

# Set organization configuration
org.set_config('config_name', 'new_value')

# Get organization errors
errors = org.get_errors()

# Dismiss an error
org.dismiss_error('component_name')

# Get MITRE ATT&CK coverage report
mitre = org.get_mitre_report()

# Get event schemas
schemas = org.get_schemas(platform='windows')
schema = org.get_schema('NEW_PROCESS')

# Current identity and permissions
identity = org.who_am_i()
```

### User Management

```python
# List organization users
users = org.get_users()
# Returns: ['user1@example.com', 'user2@example.com', ...]

# Add a user
org.add_user('new_user@example.com')

# Remove a user
org.remove_user('user@example.com')

# Get user permissions
permissions = org.get_user_permissions()

# Grant a permission
org.add_user_permission('user@example.com', 'dr.set')

# Revoke a permission
org.remove_user_permission('user@example.com', 'dr.set')

# Set a predefined role (Owner, Administrator, Operator, Viewer, Basic)
org.set_user_role('user@example.com', 'Operator')
```

### Organization Lifecycle

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization

client = Client(uid='USER_ID', api_key='USER_API_KEY')
org = Organization(client)

# List accessible organizations
orgs = org.list_accessible_orgs()

# Check name availability
availability = Organization.check_name(client, 'my-new-org')

# Create a new organization
new_org = Organization.create_org(client, 'my-new-org', location='us')
```

## Sensor Management

The `Sensor` class provides detailed control over individual sensors.

### Listing and Getting Sensors

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor

client = Client()
org = Organization(client)

# List all sensors (returns generator of dicts)
for sensor_info in org.list_sensors():
    print(sensor_info['sid'], sensor_info.get('hostname'))

# List with a selector filter
for sensor_info in org.list_sensors(selector='plat == windows'):
    print(sensor_info['sid'])

# Get list of online sensor IDs
online_sids = org.get_online_sensors()
for sid in online_sids:
    print(sid)

# Get a specific sensor object
sensor = Sensor(org, 'SENSOR_ID')
```

### Sensor Properties and Methods

```python
sensor = Sensor(org, 'SENSOR_ID')

# Get full sensor information
info = sensor.get_info()
# Returns: {'hostname': '...', 'plat': ..., 'arch': ..., ...}

# Check platform
if sensor.is_windows:
    print("Windows sensor")
elif sensor.is_linux:
    print("Linux sensor")
elif sensor.is_macos:
    print("macOS sensor")

# Get hostname
hostname = sensor.hostname

# Check if sensor is online
is_online = sensor.is_online()

# Wait for sensor to come online (blocking)
came_online = sensor.wait_online(timeout=300)  # 5 minutes
```

### Sending Tasks to Sensors

```python
# Send a single task (fire-and-forget)
sensor.task('os_processes')

# Send multiple tasks
sensor.task(['os_info', 'os_processes', 'os_services'])

# Task with investigation ID
sensor.task('os_processes', inv_id='investigation-123')
```

### Tag Management

```python
# Get sensor tags
tags = sensor.get_tags()
# Returns: ['production', 'web-server', ...]

# Add a tag
sensor.add_tag('critical')

# Add a tag with TTL (auto-removed after N seconds)
sensor.add_tag('investigating', ttl=3600)

# Remove a tag
sensor.remove_tag('test')
```

### Network Isolation

```python
# Isolate sensor from network
sensor.isolate()

# Re-join sensor to network
sensor.rejoin()

# Check isolation status
is_isolated = sensor.is_isolated()
```

### Sensor Events

```python
import time

# Get historical events for a sensor
end = int(time.time())
start = end - 3600  # 1 hour ago

for event in sensor.get_events(start=start, end=end, event_type='NEW_PROCESS', limit=100):
    print(event)

# Get event overview/timeline
overview = sensor.get_overview(start=start, end=end)
```

### Sensor Lifecycle

```python
# Delete sensor permanently
sensor.delete()
```

## Detection and Response Rules

D&R rules can be managed through the Hive system or the `DRRules` convenience class.

### Using Hive (Recommended)

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client()
org = Organization(client)

# Access D&R rules hive
hive = Hive(org, "dr-general")

# List all rules
rules = hive.list()
for name, record in rules.items():
    print(name, record.enabled)

# Get a specific rule
record = hive.get("my-detection-rule")
print(record.data)  # {'detect': {...}, 'respond': [...]}

# Create or update a rule
new_rule = HiveRecord(
    name="my-new-rule",
    data={
        "detect": {
            "event": "NEW_PROCESS",
            "op": "contains",
            "path": "event/COMMAND_LINE",
            "value": "mimikatz"
        },
        "respond": [
            {"action": "report", "name": "mimikatz-detected"}
        ]
    }
)
hive.set(new_rule)

# Delete a rule
hive.delete("my-old-rule")
```

### Using DRRules Convenience Class

```python
from limacharlie.sdk.dr_rules import DRRules

dr = DRRules(org)

# List rules (general namespace)
rules = dr.list()

# Get a rule
rule = dr.get("my-rule")

# Create a rule
dr.create("my-rule", {
    "detect": {"event": "NEW_PROCESS", "op": "exists", "path": "event/FILE_PATH"},
    "respond": [{"action": "report", "name": "process-detected"}]
})

# Delete a rule
dr.delete("my-rule")
```

### False Positive Rules

```python
from limacharlie.sdk.fp_rules import FPRules

fp = FPRules(org)

# List FP rules
fp_rules = fp.list()

# Create an FP rule
fp.create("my-fp-rule", {
    "op": "is",
    "path": "detect/event/FILE_PATH",
    "value": "C:\\Windows\\System32\\svchost.exe"
})
```

### Replay (Testing Rules Against Historical Data)

```python
from limacharlie.sdk.replay import Replay

replay = Replay(org)

# Run a rule against historical data
result = replay.run(
    rule_name="my-rule",
    start=1700000000,
    end=1700100000,
)

# Test a rule against sample events
events = [{"routing": {...}, "event": {...}}]
result = replay.scan_events(
    events,
    rule_content={"detect": {...}, "respond": [...]},
)
```

## Real-time Data Streaming

### Spout (Pull-based Streaming)

The `Spout` pulls data from `stream.limacharlie.io` over HTTPS. Works through NATs and proxies. Best for short-term ad-hoc streaming.

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.spout import Spout

client = Client()
org = Organization(client)

# Stream events
spout = Spout(org, "my-spout", data_type="event", tag="production")

try:
    while True:
        data = spout.pull(timeout=5)
        if data is not None:
            print(data)
finally:
    spout.shutdown()
```

### Firehose (Push-based Streaming)

The `Firehose` creates a TLS server that LimaCharlie connects to and pushes data. Best for large-scale, long-running streaming.

```python
from limacharlie.sdk.firehose import Firehose

# Create a firehose listener
fh = Firehose(
    org,
    listen_on="0.0.0.0:4443",
    data_type="event",
    name="my-firehose",
    public_dest="1.2.3.4:4443",
    max_buffer=1024,
    tag="production",
)

try:
    while True:
        data = fh.get(timeout=5)
        if data is not None:
            print(data)
finally:
    fh.shutdown()
```

## Artifacts

```python
from limacharlie.sdk.artifacts import Artifacts

artifacts = Artifacts(org)

# List artifacts
for artifact in artifacts.list(sensor='SENSOR_ID', start=start_time, end=end_time):
    print(artifact)

# Get download URL for an artifact
url = artifacts.get_download_url('ARTIFACT_ID')

# Download an artifact to a local file
artifacts.download('ARTIFACT_ID', '/path/to/output')
```

## Hive Operations

The Hive is LimaCharlie's key-value storage system used for D&R rules, secrets, playbooks, SOPs, lookups, and more.

```python
from limacharlie.sdk.hive import Hive, HiveRecord

# Access a hive (e.g., secrets)
hive = Hive(org, "secret")

# List all records
records = hive.list()
for name, record in records.items():
    print(name, record.data)

# Get a specific record
record = hive.get("my-secret")
print(record.data)

# Get metadata only (without data payload)
metadata = hive.get_metadata("my-secret")

# Create or update a record
new_record = HiveRecord(
    name="my-secret",
    data={"secret": "my-secret-value"},
    enabled=True,
    tags=["automation"],
    comment="API key for external service",
)
hive.set(new_record)

# Delete a record
hive.delete("old-record")
```

## Search (LCQL)

```python
from limacharlie.sdk.search import Search
import time

search = Search(org)

end = int(time.time())
start = end - 3600  # 1 hour ago

# Execute a query (returns generator)
for result in search.execute(
    query="event.FILE_PATH ends with .exe",
    start_time=start,
    end_time=end,
    stream="event",
    limit=100,
):
    print(result)

# Validate a query
validation = search.validate(
    query="event.FILE_PATH ends with .exe",
    start_time=start,
    end_time=end,
    stream="event",
)

# Estimate query cost
estimate = search.estimate(
    query="event.FILE_PATH ends with .exe",
    start_time=start,
    end_time=end,
    stream="event",
)

# Saved queries are managed through Hive
from limacharlie.sdk.hive import Hive, HiveRecord
query_hive = Hive(org, "query")
query_hive.set(HiveRecord(
    name="my-query",
    data={"query": "event.FILE_PATH ends with .exe", "stream": "event"},
    enabled=True,
))
saved = query_hive.list()
query_hive.delete("my-query")
```

## Extensions

```python
from limacharlie.sdk.extensions import Extensions

ext = Extensions(org)

# List subscribed extensions
subscribed = ext.list_subscribed()

# List all available extensions
available = ext.get_all()

# Subscribe to an extension
ext.subscribe('ext-reliable-tasking')

# Unsubscribe from an extension
ext.unsubscribe('ext-reliable-tasking')

# Get extension schema
schema = ext.get_schema('ext-reliable-tasking')

# Make a request to an extension
response = ext.request(
    extension_name='ext-reliable-tasking',
    action='task',
    data={
        'task': 'os_version',
        'selector': 'plat == windows',
        'ttl': 3600,
    },
)
```

## Infrastructure as Code

```python
from limacharlie.sdk.configs import Configs

configs = Configs(org)

# Pull organization configuration to a local file
configs.pull(config_file='lc_conf.yaml')

# Push configuration from a local file
configs.push(config_file='lc_conf.yaml', dry_run=True)

# Push with force (remove resources not in config)
configs.push(config_file='lc_conf.yaml', is_force=True)
```

## Error Handling

### Exception Hierarchy

The SDK uses a structured exception hierarchy with actionable suggestions:

```python
from limacharlie.errors import (
    LimaCharlieError,       # Base exception (exit code 1)
    AuthenticationError,     # Auth failures (exit code 2)
    NotFoundError,           # Resource not found (exit code 3)
    ValidationError,         # Input validation (exit code 4)
    RateLimitError,          # Rate limit hit (exit code 5)
    PermissionDeniedError,   # Permission denied (exit code 2)
    ApiError,                # General API errors (exit code 1)
    ConfigError,             # Configuration errors (exit code 1)
)
```

### Usage

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor
from limacharlie.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    LimaCharlieError,
)

try:
    client = Client(oid='ORG_ID', api_key='API_KEY')
    org = Organization(client)
    sensor = Sensor(org, 'SENSOR_ID')
    sensor.task('os_info')
except AuthenticationError as e:
    print(f"Auth failed: {e}")
    # Suggestion: Run 'limacharlie auth login' to configure credentials
except NotFoundError as e:
    print(f"Not found: {e}")
except RateLimitError as e:
    print(f"Rate limited, retry after: {e.retry_after}s")
except LimaCharlieError as e:
    print(f"Error: {e}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
```

### Built-in Retry Logic

The `Client` automatically retries on HTTP 429 (rate limit) and 504 (gateway timeout) with exponential backoff. No manual retry logic is needed for transient errors.

## Complete Examples

### Example 1: Automated Sensor Inventory

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor

client = Client()
org = Organization(client)

# Build a sensor inventory
inventory = {}
for sensor_info in org.list_sensors():
    sid = sensor_info['sid']
    sensor = Sensor(org, sid)
    info = sensor.get_info()
    tags = sensor.get_tags()

    inventory[sid] = {
        'hostname': info.get('hostname', 'unknown'),
        'platform': info.get('plat', 'unknown'),
        'tags': tags,
        'online': sensor.is_online(),
    }

print(f"Total sensors: {len(inventory)}")
for sid, data in inventory.items():
    print(f"  {data['hostname']} ({sid[:8]}...) - {data['platform']} - tags: {data['tags']}")
```

### Example 2: D&R Rule Deployment

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client()
org = Organization(client)
hive = Hive(org, "dr-general")

# Deploy a detection rule
rule = HiveRecord(
    name="detect-mimikatz",
    data={
        "detect": {
            "op": "and",
            "event": "NEW_PROCESS",
            "rules": [
                {"op": "is windows"},
                {
                    "op": "contains",
                    "path": "event/COMMAND_LINE",
                    "value": "mimikatz",
                    "case sensitive": False,
                }
            ]
        },
        "respond": [
            {"action": "report", "name": "mimikatz-detected"},
            {"action": "task", "command": "history_dump"},
        ]
    },
    enabled=True,
    tags=["threat-hunting"],
    comment="Detect mimikatz execution",
)
hive.set(rule)
print("Rule deployed successfully")
```

### Example 3: Real-time Detection Monitoring

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor
from limacharlie.sdk.spout import Spout

client = Client()
org = Organization(client)

# Stream detections in real-time
spout = Spout(org, "detection-monitor", data_type="detect")

try:
    while True:
        detection = spout.pull(timeout=10)
        if detection is not None:
            routing = detection.get('routing', {})
            print(f"Detection: {detection.get('cat', 'unknown')}")
            print(f"  Sensor: {routing.get('hostname', 'unknown')} ({routing.get('sid', 'unknown')})")

            # Auto-isolate on critical detections
            if 'ransomware' in detection.get('cat', '').lower():
                sid = routing.get('sid')
                if sid:
                    sensor = Sensor(org, sid)
                    sensor.isolate()
                    print(f"  [!] Sensor isolated due to ransomware detection")
finally:
    spout.shutdown()
```

### Example 4: Extension Request (Playbook Execution)

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.extensions import Extensions

client = Client()
org = Organization(client)
ext = Extensions(org)

# Trigger a playbook via the ext-playbook extension
response = ext.request("ext-playbook", "run_playbook", {
    "name": "my-playbook",
    "credentials": "hive://secret/my-api-key",
    "data": {
        "target_sensor": "SENSOR_ID",
        "action": "investigate",
    }
})

print(response)
```
