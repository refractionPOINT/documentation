# LimaCharlie Python SDK Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Authentication](#authentication)
4. [Core Classes](#core-classes)
5. [Manager Class](#manager-class)
6. [Sensor Management](#sensor-management)
7. [Detection and Response Rules](#detection-and-response-rules)
8. [Real-time Data Streaming](#real-time-data-streaming)
9. [Artifacts and Payloads](#artifacts-and-payloads)
10. [Event Ingestion](#event-ingestion)
11. [Advanced Features](#advanced-features)
12. [Error Handling](#error-handling)
13. [Complete Examples](#complete-examples)

## Overview

The LimaCharlie Python SDK provides a comprehensive interface for interacting with the LimaCharlie SecOps Cloud Platform. This SDK enables programmatic access to all platform features including sensor management, detection and response rules, real-time event streaming, and artifact collection.

### Key Features
- **Organization Management**: Create, configure, and manage LimaCharlie organizations
- **Sensor Operations**: Deploy, monitor, and control endpoint sensors
- **Detection & Response**: Create and manage detection rules with automated response actions
- **Real-time Streaming**: Receive events, detections, and audit logs in real-time
- **Artifact Management**: Collect and manage forensic artifacts
- **Event Processing**: Ingest and query historical events
- **API Integration**: Full access to LimaCharlie REST API endpoints

### SDK Version
Current version: 4.9.24

## Installation

### Requirements
- Python 3.6 or higher
- pip package manager

### Install via pip
```bash
pip install limacharlie
```

### Install from source
```bash
git clone https://github.com/refractionPOINT/python-limacharlie.git
cd python-limacharlie
pip install -r requirements.txt
python setup.py install
```

### Dependencies
```python
# Core dependencies
pyyaml>=5.1
requests>=2.20.0
python-dateutil>=2.8.0
```

## Authentication

### Authentication Methods

The LimaCharlie SDK supports multiple authentication methods:

1. **API Key Authentication** (Recommended for automation)
2. **OAuth Authentication** (For user-based access)
3. **JWT Token Authentication** (For temporary access)
4. **Environment-based Authentication** (Using configuration files)

### API Key Authentication

```python
import limacharlie

# Direct API key authentication
manager = limacharlie.Manager(
    oid='YOUR_ORGANIZATION_ID',  # UUID format
    secret_api_key='YOUR_API_KEY'  # UUID format
)
```

### Environment-based Authentication

The SDK can read credentials from environment variables or configuration files:

```python
# Using environment variables
# Set: LC_OID="your-org-id"
# Set: LC_API_KEY="your-api-key"
manager = limacharlie.Manager()

# Using a specific environment from config file
manager = limacharlie.Manager(environment='production')
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
  
  dev:
    oid: "11111111-1111-1111-1111-111111111111"
    api_key: "22222222-2222-2222-2222-222222222222"
```

### OAuth Authentication

```python
# OAuth configuration in ~/.limacharlie
oauth:
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  refresh_token: "your-refresh-token"
  id_token: "your-id-token"
```

### User-based Authentication

```python
# Authenticate as a user instead of organization
manager = limacharlie.Manager(
    uid='USER_ID',
    secret_api_key='USER_API_KEY'
)
```

## Core Classes

### Class Hierarchy

```
limacharlie
├── Manager           # Main entry point for API operations
├── Sensor           # Individual sensor management
├── Firehose         # Real-time data streaming (push)
├── Spout            # Real-time data streaming (pull)
├── Configs          # Configuration management
├── Payloads         # Artifact and payload management
├── Logs/Artifacts   # Log and artifact retrieval
├── Hive             # Hive data storage
├── Extensions       # Add-on extensions
├── Billing          # Billing and usage information
├── User             # User management
├── UserPreferences  # User preferences
├── Webhook          # Webhook management
├── WebhookSender    # Send data to webhooks
├── Jobs             # Background job management
├── Query            # Query builder for LCQL
├── Replay           # Event replay functionality
├── Search           # Search operations
├── SpotCheck        # Spot check operations
└── Replicants       # Service replicants (external services)
```

## Manager Class

The `Manager` class is the primary entry point for interacting with LimaCharlie.

### Initialization

```python
import limacharlie

# Basic initialization
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY'
)

# Advanced initialization with all parameters
manager = limacharlie.Manager(
    oid='ORG_ID',                    # Organization ID (UUID)
    secret_api_key='API_KEY',        # API Key (UUID)
    environment='production',        # Named environment from config
    inv_id='investigation-123',      # Investigation ID for tracking
    print_debug_fn=print,            # Debug output function
    is_interactive=True,             # Enable interactive mode
    extra_params={'key': 'value'},   # Additional parameters
    jwt='existing-jwt-token',        # Use existing JWT
    uid='USER_ID',                   # User ID for user-based auth
    onRefreshAuth=callback_func,     # Callback on auth refresh
    isRetryQuotaErrors=True         # Auto-retry on quota errors
)
```

### Core Manager Methods

#### Organization Management

```python
# Get organization information
org_info = manager.getOrgInfo()
# Returns: {'oid': '...', 'name': '...', 'tier': '...', ...}

# Get organization URLs
urls = manager.getOrgURLs()
# Returns: {'webapp': 'https://...', 'api': 'https://...', ...}

# Get organization configuration
config = manager.getOrgConfig()
# Returns: {'sensor_quota': 100, 'retention': 30, ...}

# Update organization configuration
manager.setOrgConfig({
    'sensor_quota': 200,
    'retention': 60
})

# Get billing information
billing = limacharlie.Billing(manager)
billing_info = billing.getInfo()
```

#### Sensor Listing and Search

```python
# List all sensors
sensors = manager.sensors()
# Returns: {'sensor-id-1': {...}, 'sensor-id-2': {...}, ...}

# List sensors with details
detailed_sensors = manager.sensors(with_details=True)

# Get sensor count
online_count = manager.getOnlineHosts()
# Returns: 42

# Search sensors by hostname
matching_sensors = manager.getHostnames(['web-server-*', 'db-*'])
# Returns: {'web-server-01': 'sensor-id-1', ...}

# Get sensors by tag
tagged_sensors = manager.getSensorsWithTag('production')
# Returns: ['sensor-id-1', 'sensor-id-2', ...]

# Get sensor information
sensor_info = manager.getSensorInfo('SENSOR_ID')
# Returns: {'hostname': '...', 'platform': '...', 'architecture': '...', ...}
```

#### Installation Keys

```python
# List installation keys
keys = manager.getInstallationKeys()
# Returns: [{'key': '...', 'tags': [...], 'desc': '...', ...}, ...]

# Create new installation key
new_key = manager.setInstallationKey(
    key_name='prod-servers',
    tags=['production', 'server'],
    desc='Production server deployment key'
)
# Returns: 'INSTALLATION_KEY_STRING'

# Delete installation key
manager.delInstallationKey('INSTALLATION_KEY_ID')
```

#### Outputs Management

```python
# List all outputs
outputs = manager.outputs()
# Returns: {'output1': {...}, 'output2': {...}, ...}

# Add new output
manager.add_output(
    name='siem_output',
    module='syslog',
    type='detect',
    config={
        'dest_host': 'siem.example.com',
        'dest_port': 514,
        'protocol': 'tcp'
    }
)

# Delete output
manager.del_output('siem_output')
```

#### Artifact Collection

```python
# List available artifacts
artifacts = manager.getArtifacts(
    start_time=1234567890,  # Unix timestamp
    end_time=1234567999
)

# Get specific artifact
artifact_data = manager.getArtifact('ARTIFACT_ID')

# Get artifact as JSON
artifact_json = manager.getArtifactAsJson('ARTIFACT_ID')
```

#### Service Management

```python
# List services
services = manager.getServices()

# Subscribe to a service
manager.subscribeToService('virustotal')

# Unsubscribe from service
manager.unsubscribeFromService('virustotal')

# Get service configuration
service_config = manager.getServiceConfig('virustotal')

# Update service configuration
manager.setServiceConfig('virustotal', {
    'api_key': 'YOUR_VT_API_KEY'
})
```

## Sensor Management

The `Sensor` class provides detailed control over individual sensors.

### Creating a Sensor Object

```python
# Create from Manager
sensor = manager.sensor('SENSOR_ID')

# Direct instantiation
from limacharlie import Sensor
sensor = Sensor(manager, 'SENSOR_ID')

# With detailed info pre-loaded
sensor = Sensor(manager, 'SENSOR_ID', detailedInfo={...})
```

### Sensor Properties and Methods

#### Getting Sensor Information

```python
# Check if sensor is online
is_online = sensor.isOnline()
# Returns: True/False

# Get sensor hostname
hostname = sensor.getHostname()
# Returns: 'web-server-01'

# Get platform information
platform = sensor.getPlatform()
# Returns: 'windows', 'linux', 'macos', etc.

# Get architecture
architecture = sensor.getArchitecture()
# Returns: 'x64', 'x86', 'arm64', etc.

# Get full sensor information
info = sensor.getInfo()
# Returns: {'hostname': '...', 'platform': '...', 'last_seen': ..., ...}

# Get sensor tags
tags = sensor.getTags()
# Returns: ['production', 'web-server', ...]
```

#### Sending Tasks to Sensors

```python
# Send a single task
response = sensor.task('os_info')

# Send multiple tasks
responses = sensor.task([
    'os_info',
    'os_packages',
    'os_services'
])

# Task with investigation ID
sensor.setInvId('investigation-123')
response = sensor.task('os_processes')

# Direct task with inv_id
response = sensor.task('os_processes', inv_id='investigation-456')
```

#### Interactive Task Execution

```python
# Manager must be in interactive mode
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    is_interactive=True,
    inv_id='investigation-123'
)

sensor = manager.sensor('SENSOR_ID')

# Request with future results
future = sensor.request('os_info')

# Wait for results
result = future.getNewResponses(timeout=30)

# Simple request (blocking)
result = sensor.simpleRequest('os_info', timeout=30)

# Request with completion tracking
results = sensor.simpleRequest(
    ['os_info', 'os_processes'],
    timeout=60,
    until_completion=True  # Wait for all tasks to complete
)

# Request with callback
def process_response(event):
    print(f"Received: {event}")

sensor.simpleRequest(
    'os_processes',
    timeout=30,
    until_completion=process_response  # Called for each response
)
```

#### Sensor Isolation

```python
# Isolate sensor from network
sensor.isolate()

# Re-join sensor to network
sensor.rejoin()

# Check isolation status
is_isolated = sensor.isIsolated()
```

#### Sensor Management

```python
# Tag management
sensor.addTag('critical')
sensor.removeTag('test')

# Wait for sensor to come online
came_online = sensor.waitToComeOnline(timeout=300)  # 5 minutes
# Returns: True if online, False if timeout

# Delete sensor
sensor.delete()

# Drain sensor (mark for deletion after offline)
sensor.drain()
```

### Available Sensor Tasks

Common tasks that can be sent to sensors:

```python
# System Information
'os_info'           # Get OS information
'os_packages'       # List installed packages
'os_services'       # List running services
'os_processes'      # List running processes
'os_autoruns'       # List autorun entries
'os_drivers'        # List loaded drivers

# File Operations
'file_info <path>'  # Get file information
'file_get <path>'   # Retrieve file content
'file_del <path>'   # Delete file
'file_mov <src> <dst>'  # Move file
'file_hash <path>'  # Get file hash

# Process Operations
'mem_map <pid>'     # Get process memory map
'mem_read <pid> <address> <size>'  # Read process memory
'mem_strings <pid>' # Get process strings
'kill <pid>'        # Kill process

# Network Operations
'netstat'           # Get network connections
'dns_resolve <domain>'  # Resolve DNS

# Registry Operations (Windows)
'reg_list <path>'   # List registry keys
'reg_get <path>'    # Get registry value

# History and Forensics
'history_dump'      # Dump sensor history
'hidden_module_scan'  # Scan for hidden modules
'exec_oob_scan'     # Out-of-band executable scan
```

## Detection and Response Rules

**Note**: The direct D&R rule methods (`rules()`, `add_rule()`, `del_rule()`, `add_fp()`, `del_fp()`) are deprecated. Please use the Hive accessors instead for managing Detection & Response rules. See the Hive Operations section for details on using the key-value storage system for rule management.

## Real-time Data Streaming

### Firehose (Push-based Streaming)

The Firehose class receives data pushed from LimaCharlie:

```python
import limacharlie

manager = limacharlie.Manager('ORG_ID', 'API_KEY')

# Create a Firehose for events
firehose = limacharlie.Firehose(
    manager,
    listen_on='0.0.0.0:4443',  # Listen interface and port
    data_type='event',          # event, detect, or audit
    name='my_firehose',         # Output name in LC
    public_dest='1.2.3.4:4443', # Public IP:port for LC to connect
    ssl_cert='/path/to/cert.pem',  # Optional SSL cert
    ssl_key='/path/to/key.pem',    # Optional SSL key
    is_parse=True,              # Parse JSON automatically
    max_buffer=1024,            # Max messages to buffer
    inv_id='investigation-123', # Filter by investigation ID
    tag='production',           # Filter by sensor tag
    sid='SENSOR_ID'            # Filter by sensor ID
)

# Start receiving data
firehose.start()

# Process events
while True:
    event = firehose.queue.get()
    print(f"Received event: {event}")
    
    # Process event
    if event.get('event_type') == 'PROCESS_START':
        process_path = event.get('event', {}).get('FILE_PATH')
        print(f"Process started: {process_path}")

# Shutdown
firehose.shutdown()
```

### Spout (Pull-based Streaming)

The Spout class pulls data from LimaCharlie:

```python
# Create a Spout for detections
spout = limacharlie.Spout(
    manager,
    data_type='detect',      # event, detect, audit, or tailored
    is_parse=True,           # Parse JSON
    inv_id='investigation-123',
    tag='critical',
    cat='malware',           # Detection category filter
    sid='SENSOR_ID',
    is_compressed=True,      # Use compression
    rel_parent_events=True,  # Include parent events
    rel_child_events=True    # Include child events
)

# Process detections
for detection in spout:
    print(f"Detection: {detection['detect_name']}")
    print(f"Sensor: {detection['sid']}")
    print(f"Event: {detection['event']}")
    
    # Take action based on detection
    if detection['detect_name'] == 'ransomware_behavior':
        sensor = manager.sensor(detection['sid'])
        sensor.isolate()

# Shutdown
spout.shutdown()
```

### Tailored Event Streaming

```python
# Stream specific event types
spout = limacharlie.Spout(
    manager,
    data_type='tailored',
    event_type=['PROCESS_START', 'NETWORK_CONNECT'],
    is_parse=True
)

for event in spout:
    if event['event_type'] == 'PROCESS_START':
        print(f"Process: {event['event']['FILE_PATH']}")
    elif event['event_type'] == 'NETWORK_CONNECT':
        print(f"Connection: {event['event']['DESTINATION']}")
```

## Artifacts and Payloads

### Managing Artifacts

```python
# Initialize Artifacts/Logs manager
artifacts = limacharlie.Artifacts(manager)

# List artifacts in time range
artifact_list = artifacts.listArtifacts(
    start_time=1234567890,
    end_time=1234567999,
    sid='SENSOR_ID',  # Optional: filter by sensor
    type='log'        # Optional: filter by type
)

# Get specific artifact
artifact_data = artifacts.getArtifact('ARTIFACT_ID')

# Get artifact metadata
metadata = artifacts.getArtifactMetadata('ARTIFACT_ID')

# Delete artifact
artifacts.deleteArtifact('ARTIFACT_ID')
```

### Payloads Management

```python
# Initialize Payloads manager
payloads = limacharlie.Payloads(manager)

# List available payloads
payload_list = payloads.list()

# Create a new payload
payload_id = payloads.create(
    name='custom_script',
    data=b'#!/bin/bash\necho "Hello World"',
    description='Custom bash script'
)

# Get payload
payload_data = payloads.get('PAYLOAD_ID')

# Delete payload
payloads.delete('PAYLOAD_ID')

# Use payload in a task
sensor.task(f'run_payload {payload_id}')
```

## Event Ingestion

### Ingesting Custom Events

```python
# Ingest a single event
manager.ingestEvent({
    'event_type': 'CUSTOM_EVENT',
    'timestamp': 1234567890,
    'data': {
        'key': 'value',
        'severity': 'high'
    }
})

# Batch ingestion
events = [
    {
        'event_type': 'CUSTOM_LOGIN',
        'timestamp': 1234567890,
        'user': 'admin',
        'source_ip': '192.168.1.100'
    },
    {
        'event_type': 'CUSTOM_FILE_ACCESS',
        'timestamp': 1234567891,
        'file': '/etc/passwd',
        'user': 'admin'
    }
]

for event in events:
    manager.ingestEvent(event)
```

### Ingesting Third-party Logs

```python
# Ingest syslog events
def ingest_syslog(syslog_line):
    # Parse syslog format
    parsed = parse_syslog(syslog_line)
    
    manager.ingestEvent({
        'event_type': 'SYSLOG',
        'timestamp': parsed['timestamp'],
        'hostname': parsed['hostname'],
        'facility': parsed['facility'],
        'severity': parsed['severity'],
        'message': parsed['message']
    })

# Ingest Windows Event Logs
def ingest_windows_event(event_xml):
    # Parse Windows Event XML
    parsed = parse_windows_event(event_xml)
    
    manager.ingestEvent({
        'event_type': 'WINDOWS_EVENT',
        'timestamp': parsed['TimeCreated'],
        'event_id': parsed['EventID'],
        'provider': parsed['Provider'],
        'level': parsed['Level'],
        'data': parsed['EventData']
    })
```

## Advanced Features

### Hive Operations

The Hive is LimaCharlie's key-value storage system:

```python
# Initialize Hive
hive = limacharlie.Hive(manager)

# Store data
hive_record = limacharlie.HiveRecord(
    hive_name='threat_intel',
    key='malware_hash_123',
    data={
        'hash': 'abc123...',
        'type': 'ransomware',
        'first_seen': 1234567890
    },
    ttl=86400  # TTL in seconds
)
hive.set(hive_record)

# Get data
record = hive.get('threat_intel', 'malware_hash_123')
print(record.data)

# List keys
keys = hive.list('threat_intel')

# Delete data
hive.delete('threat_intel', 'malware_hash_123')

# Bulk operations
records = [
    limacharlie.HiveRecord('intel', f'hash_{i}', {'value': i})
    for i in range(100)
]
hive.setBulk(records)
```

### Query Language (LCQL)

```python
from limacharlie import Query

# Build queries programmatically
query = Query()

# Simple query
results = manager.query(
    query='event_type == "PROCESS_START" AND event.FILE_PATH contains "powershell"',
    limit=100
)

# Complex query with time range
results = manager.query(
    query='''
        event_type == "NETWORK_CONNECT" 
        AND event.DESTINATION contains "suspicious.com"
        AND timestamp > now() - 86400
    ''',
    start_time=time.time() - 86400,
    end_time=time.time(),
    limit=1000
)

# Query with aggregation
results = manager.query(
    query='event_type == "PROCESS_START"',
    select=['event.FILE_PATH', 'count()'],
    group_by=['event.FILE_PATH'],
    order_by='count() DESC'
)
```

### Replay Functionality

```python
# Initialize Replay
replay = limacharlie.Replay(manager)

# Start replay of historical events
replay.start(
    start_time=time.time() - 3600,  # 1 hour ago
    end_time=time.time(),
    filters={
        'event_type': ['PROCESS_START', 'FILE_CREATE'],
        'sid': 'SENSOR_ID'
    },
    rules=['suspicious_process', 'ransomware_behavior']  # Test specific rules
)

# Get replay results
results = replay.getResults()
for result in results:
    print(f"Rule triggered: {result['rule_name']}")
    print(f"Event: {result['event']}")
```

### Jobs Management

```python
# Create a job
job = limacharlie.Job(manager)

job_id = job.create(
    name='daily_scan',
    schedule='0 2 * * *',  # Cron format
    task='full_scan',
    sensors=['SENSOR_ID_1', 'SENSOR_ID_2']
)

# List jobs
jobs = job.list()

# Get job status
status = job.getStatus('JOB_ID')

# Cancel job
job.cancel('JOB_ID')
```

### Extensions Management

```python
# Initialize Extensions
extensions = limacharlie.Extension(manager)

# List available extensions
available = extensions.list()

# Install extension
extensions.install('velociraptor')

# Configure extension
extensions.configure('velociraptor', {
    'api_key': 'YOUR_API_KEY',
    'server_url': 'https://velociraptor.example.com'
})

# Uninstall extension
extensions.uninstall('velociraptor')
```


## Error Handling

### Exception Types

```python
from limacharlie.utils import LcApiException

try:
    manager = limacharlie.Manager('INVALID_OID', 'INVALID_KEY')
except LcApiException as e:
    print(f"API Error: {e}")
    # Handle authentication error

try:
    sensor = manager.sensor('INVALID_SENSOR_ID')
    sensor.task('os_info')
except LcApiException as e:
    if 'not found' in str(e):
        print("Sensor not found")
    elif 'offline' in str(e):
        print("Sensor is offline")
    else:
        print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import time
from limacharlie.utils import LcApiException

def retry_operation(func, max_retries=3, delay=1):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except LcApiException as e:
            if 'rate limit' in str(e).lower():
                wait_time = delay * (2 ** attempt)
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} attempts")

# Usage
result = retry_operation(lambda: manager.sensors())
```

### Handling Quota Errors

```python
# Enable automatic retry on quota errors
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    isRetryQuotaErrors=True  # Auto-retry on HTTP 429
)

# Manual handling
try:
    sensors = manager.sensors()
except LcApiException as e:
    if e.http_code == 429:  # Too Many Requests
        retry_after = e.headers.get('Retry-After', 60)
        print(f"Quota exceeded, retry after {retry_after}s")
        time.sleep(int(retry_after))
        sensors = manager.sensors()  # Retry
```

## Complete Examples

### Example 1: Automated Threat Hunting

```python
import limacharlie
import time
from datetime import datetime, timedelta

class ThreatHunter:
    def __init__(self, org_id, api_key):
        self.manager = limacharlie.Manager(org_id, api_key)
        self.suspicious_processes = [
            'mimikatz.exe',
            'lazagne.exe',
            'pwdump.exe',
            'procdump.exe'
        ]
    
    def hunt_suspicious_processes(self):
        """Hunt for suspicious processes across all sensors"""
        print("Starting threat hunt...")
        
        # Get all online sensors
        sensors = self.manager.sensors()
        online_sensors = [
            sid for sid, info in sensors.items()
            if info.get('online', False)
        ]
        
        print(f"Found {len(online_sensors)} online sensors")
        
        findings = []
        
        for sid in online_sensors:
            sensor = self.manager.sensor(sid)
            hostname = sensor.getHostname()
            
            print(f"Scanning {hostname}...")
            
            # Get running processes
            try:
                result = sensor.simpleRequest('os_processes', timeout=30)
                if result and 'processes' in result:
                    for process in result['processes']:
                        process_name = process.get('name', '').lower()
                        for suspicious in self.suspicious_processes:
                            if suspicious.lower() in process_name:
                                findings.append({
                                    'sensor': sid,
                                    'hostname': hostname,
                                    'process': process_name,
                                    'pid': process.get('pid'),
                                    'path': process.get('path')
                                })
                                print(f"  [!] Found suspicious process: {process_name}")
            except Exception as e:
                print(f"  Error scanning {hostname}: {e}")
        
        return findings
    
    def monitor_detections(self, duration=3600):
        """Monitor for detections in real-time"""
        print(f"Monitoring detections for {duration} seconds...")
        
        spout = limacharlie.Spout(
            self.manager,
            data_type='detect',
            is_parse=True
        )
        
        start_time = time.time()
        
        try:
            for detection in spout:
                if time.time() - start_time > duration:
                    break
                
                print(f"\n[DETECTION] {detection['detect_name']}")
                print(f"  Sensor: {detection['hostname']} ({detection['sid']})")
                print(f"  Time: {datetime.fromtimestamp(detection['ts'])}")
                
                # Auto-respond to critical detections
                if detection.get('priority', 0) >= 4:
                    sensor = self.manager.sensor(detection['sid'])
                    print(f"  [!] High priority detection - isolating sensor")
                    sensor.isolate()
                    
                    # Collect forensics
                    sensor.task([
                        'history_dump',
                        'os_processes',
                        'netstat'
                    ])
        finally:
            spout.shutdown()
    
    def generate_hunt_report(self, findings):
        """Generate a hunting report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_sensors': len(self.manager.sensors()),
            'findings_count': len(findings),
            'findings': findings,
            'recommendations': []
        }
        
        if findings:
            report['recommendations'].append(
                "Suspicious processes detected - investigate immediately"
            )
            report['recommendations'].append(
                "Consider isolating affected systems"
            )
            report['recommendations'].append(
                "Review process execution history on affected systems"
            )
        
        return report

# Usage
if __name__ == "__main__":
    hunter = ThreatHunter('ORG_ID', 'API_KEY')
    
    # Hunt for suspicious processes
    findings = hunter.hunt_suspicious_processes()
    
    # Generate report
    report = hunter.generate_hunt_report(findings)
    print(f"\nHunt Report: {report}")
    
    # Monitor for new detections
    hunter.monitor_detections(duration=3600)
```

### Example 2: Incident Response Automation

```python
import limacharlie
import json
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
        self.artifacts = limacharlie.Artifacts(self.manager)
        self.hive = limacharlie.Hive(self.manager)
    
    def respond_to_incident(self, sensor_id, incident_type):
        """Orchestrate incident response"""
        print(f"Responding to {incident_type} on sensor {sensor_id}")
        
        sensor = self.manager.sensor(sensor_id)
        hostname = sensor.getHostname()
        
        # Create incident record
        incident = {
            'id': hashlib.md5(f"{sensor_id}{datetime.now()}".encode()).hexdigest(),
            'type': incident_type,
            'sensor': sensor_id,
            'hostname': hostname,
            'timestamp': datetime.now().isoformat(),
            'status': 'investigating',
            'artifacts': [],
            'actions': []
        }
        
        # Step 1: Isolate if critical
        if incident_type in ['ransomware', 'data_theft', 'backdoor']:
            print(f"  Isolating {hostname}...")
            sensor.isolate()
            incident['actions'].append({
                'action': 'isolate',
                'timestamp': datetime.now().isoformat()
            })
        
        # Step 2: Collect forensics
        print("  Collecting forensic data...")
        forensics_tasks = [
            'os_processes',
            'netstat',
            'os_autoruns',
            'history_dump'
        ]
        
        for task in forensics_tasks:
            try:
                result = sensor.simpleRequest(task, timeout=60)
                if result:
                    # Store in Hive for analysis
                    self.hive.set(limacharlie.HiveRecord(
                        hive_name='incidents',
                        key=f"{incident['id']}_{task}",
                        data=result,
                        ttl=2592000  # 30 days
                    ))
                    incident['artifacts'].append(task)
            except Exception as e:
                print(f"    Failed to collect {task}: {e}")
        
        # Step 3: Collect memory dump for critical incidents
        if incident_type in ['ransomware', 'backdoor']:
            print("  Collecting memory dump...")
            try:
                sensor.task('os_memory_dump')
                incident['actions'].append({
                    'action': 'memory_dump',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"    Memory dump failed: {e}")
        
        # Step 4: Kill malicious processes
        if incident_type == 'malware':
            self.kill_malicious_processes(sensor)
            incident['actions'].append({
                'action': 'kill_processes',
                'timestamp': datetime.now().isoformat()
            })
        
        # Step 5: Update incident status
        incident['status'] = 'contained'
        self.hive.set(limacharlie.HiveRecord(
            hive_name='incidents',
            key=incident['id'],
            data=incident,
            ttl=7776000  # 90 days
        ))
        
        return incident
    
    def kill_malicious_processes(self, sensor):
        """Kill known malicious processes"""
        malicious_patterns = [
            'mimikatz',
            'cobalt',
            'empire',
            'meterpreter'
        ]
        
        try:
            result = sensor.simpleRequest('os_processes', timeout=30)
            if result and 'processes' in result:
                for process in result['processes']:
                    process_name = process.get('name', '').lower()
                    for pattern in malicious_patterns:
                        if pattern in process_name:
                            print(f"    Killing {process_name} (PID: {process['pid']})")
                            sensor.task(f"kill {process['pid']}")
        except Exception as e:
            print(f"    Error killing processes: {e}")
    
    def analyze_network_connections(self, sensor_id):
        """Analyze network connections for IOCs"""
        sensor = self.manager.sensor(sensor_id)
        
        try:
            result = sensor.simpleRequest('netstat', timeout=30)
            suspicious_connections = []
            
            if result and 'connections' in result:
                for conn in result['connections']:
                    # Check for suspicious ports
                    if conn.get('dst_port') in [4444, 5555, 31337, 1337]:
                        suspicious_connections.append(conn)
                    
                    # Check for known C2 IPs (would come from threat intel)
                    # This is a placeholder - real implementation would check against threat intel
                    if conn.get('dst_ip') in ['1.2.3.4', '5.6.7.8']:
                        suspicious_connections.append(conn)
            
            return suspicious_connections
        except Exception as e:
            print(f"Error analyzing network: {e}")
            return []
    
    def generate_incident_timeline(self, incident_id):
        """Generate timeline of incident events"""
        timeline = []
        
        # Get incident data from Hive
        incident = self.hive.get('incidents', incident_id)
        
        if incident:
            # Query events around incident time
            results = self.manager.query(
                query=f"sid == '{incident.data['sensor']}'",
                start_time=datetime.fromisoformat(incident.data['timestamp']).timestamp() - 3600,
                end_time=datetime.fromisoformat(incident.data['timestamp']).timestamp() + 3600,
                limit=1000
            )
            
            for event in results:
                timeline.append({
                    'timestamp': event['ts'],
                    'event_type': event['event_type'],
                    'summary': self.summarize_event(event)
                })
        
        return sorted(timeline, key=lambda x: x['timestamp'])
    
    def summarize_event(self, event):
        """Create human-readable event summary"""
        event_type = event.get('event_type')
        
        if event_type == 'PROCESS_START':
            return f"Process started: {event.get('event', {}).get('FILE_PATH', 'unknown')}"
        elif event_type == 'NETWORK_CONNECT':
            return f"Network connection to {event.get('event', {}).get('DESTINATION', 'unknown')}"
        elif event_type == 'FILE_CREATE':
            return f"File created: {event.get('event', {}).get('FILE_PATH', 'unknown')}"
        else:
            return f"Event: {event_type}"

# Usage
if __name__ == "__main__":
    responder = IncidentResponder('ORG_ID', 'API_KEY')
    
    # Respond to a ransomware incident
    incident = responder.respond_to_incident(
        sensor_id='SENSOR_ID',
        incident_type='ransomware'
    )
    
    print(f"\nIncident Response Complete:")
    print(json.dumps(incident, indent=2))
    
    # Generate timeline
    timeline = responder.generate_incident_timeline(incident['id'])
    print(f"\nIncident Timeline: {len(timeline)} events")
```

### Example 3: Compliance and Audit Automation

```python
import limacharlie
import csv
from datetime import datetime, timedelta
import json

class ComplianceAuditor:
    def __init__(self, org_id, api_key):
        self.manager = limacharlie.Manager(org_id, api_key)
        self.required_software = {
            'windows': ['Windows Defender', 'BitLocker'],
            'linux': ['auditd', 'aide'],
            'macos': ['XProtect', 'Gatekeeper']
        }
    
    def audit_sensor_compliance(self, sensor_id):
        """Audit individual sensor for compliance"""
        sensor = self.manager.sensor(sensor_id)
        
        compliance_report = {
            'sensor_id': sensor_id,
            'hostname': sensor.getHostname(),
            'platform': sensor.getPlatform(),
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'compliant': True
        }
        
        # Check 1: Sensor online status
        compliance_report['checks']['sensor_online'] = {
            'status': sensor.isOnline(),
            'required': True
        }
        if not sensor.isOnline():
            compliance_report['compliant'] = False
        
        # Check 2: Required software installed
        if sensor.isOnline():
            platform = sensor.getPlatform()
            required = self.required_software.get(platform, [])
            
            try:
                result = sensor.simpleRequest('os_packages', timeout=60)
                installed_packages = []
                
                if result and 'packages' in result:
                    installed_packages = [p.get('name', '') for p in result['packages']]
                
                for software in required:
                    found = any(software.lower() in pkg.lower() for pkg in installed_packages)
                    compliance_report['checks'][f'software_{software}'] = {
                        'status': found,
                        'required': True
                    }
                    if not found:
                        compliance_report['compliant'] = False
            except Exception as e:
                compliance_report['checks']['software_audit'] = {
                    'status': False,
                    'error': str(e)
                }
                compliance_report['compliant'] = False
        
        # Check 3: Security patches
        if sensor.isOnline():
            try:
                # Check for critical patches (platform-specific)
                if platform == 'windows':
                    result = sensor.simpleRequest('os_patches', timeout=60)
                    if result:
                        missing_critical = [
                            p for p in result.get('missing', [])
                            if p.get('severity') == 'Critical'
                        ]
                        compliance_report['checks']['critical_patches'] = {
                            'status': len(missing_critical) == 0,
                            'missing_count': len(missing_critical),
                            'required': True
                        }
                        if missing_critical:
                            compliance_report['compliant'] = False
            except Exception as e:
                pass  # Not all platforms support patch checking
        
        return compliance_report
    
    def audit_organization_compliance(self):
        """Audit entire organization for compliance"""
        print("Starting organization-wide compliance audit...")
        
        sensors = self.manager.sensors()
        audit_results = []
        
        for sid in sensors:
            print(f"Auditing sensor {sid}...")
            report = self.audit_sensor_compliance(sid)
            audit_results.append(report)
        
        # Generate summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_sensors': len(sensors),
            'compliant_sensors': sum(1 for r in audit_results if r['compliant']),
            'non_compliant_sensors': sum(1 for r in audit_results if not r['compliant']),
            'compliance_rate': 0,
            'details': audit_results
        }
        
        if summary['total_sensors'] > 0:
            summary['compliance_rate'] = (
                summary['compliant_sensors'] / summary['total_sensors'] * 100
            )
        
        return summary
    
    def generate_audit_log(self, days=30):
        """Generate audit log for compliance reporting"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Query audit events
        audit_events = self.manager.query(
            query='event_type == "AUDIT"',
            start_time=start_time.timestamp(),
            end_time=end_time.timestamp(),
            limit=10000
        )
        
        # Process and categorize audit events
        audit_log = {
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'events': {
                'authentication': [],
                'authorization': [],
                'configuration_changes': [],
                'data_access': []
            },
            'summary': {}
        }
        
        for event in audit_events:
            event_data = event.get('event', {})
            audit_type = event_data.get('type', 'unknown')
            
            if 'auth' in audit_type.lower():
                audit_log['events']['authentication'].append(event)
            elif 'config' in audit_type.lower():
                audit_log['events']['configuration_changes'].append(event)
            elif 'access' in audit_type.lower():
                audit_log['events']['data_access'].append(event)
            else:
                audit_log['events']['authorization'].append(event)
        
        # Generate summary statistics
        audit_log['summary'] = {
            'total_events': len(audit_events),
            'authentication_events': len(audit_log['events']['authentication']),
            'configuration_changes': len(audit_log['events']['configuration_changes']),
            'data_access_events': len(audit_log['events']['data_access'])
        }
        
        return audit_log
    
    def export_compliance_report(self, audit_results, filename='compliance_report.csv'):
        """Export compliance audit results to CSV"""
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'sensor_id', 'hostname', 'platform', 
                'compliant', 'timestamp', 'issues'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in audit_results['details']:
                issues = []
                for check, status in result['checks'].items():
                    if not status.get('status', False):
                        issues.append(check)
                
                writer.writerow({
                    'sensor_id': result['sensor_id'],
                    'hostname': result['hostname'],
                    'platform': result['platform'],
                    'compliant': result['compliant'],
                    'timestamp': result['timestamp'],
                    'issues': ', '.join(issues)
                })
        
        print(f"Compliance report exported to {filename}")

# Usage
if __name__ == "__main__":
    auditor = ComplianceAuditor('ORG_ID', 'API_KEY')
    
    # Perform organization-wide audit
    audit_results = auditor.audit_organization_compliance()
    
    print(f"\nCompliance Audit Summary:")
    print(f"  Total Sensors: {audit_results['total_sensors']}")
    print(f"  Compliant: {audit_results['compliant_sensors']}")
    print(f"  Non-Compliant: {audit_results['non_compliant_sensors']}")
    print(f"  Compliance Rate: {audit_results['compliance_rate']:.1f}%")
    
    # Export results
    auditor.export_compliance_report(audit_results)
    
    # Generate audit log
    audit_log = auditor.generate_audit_log(days=30)
    print(f"\nAudit Log Summary (Last 30 days):")
    print(json.dumps(audit_log['summary'], indent=2))
```

## Best Practices

### Performance Optimization

1. **Batch Operations**
```python
# Good: Batch sensor queries
sensors = manager.sensors(with_details=True)

# Bad: Individual queries for each sensor
for sid in sensor_ids:
    sensor = manager.sensor(sid)
    info = sensor.getInfo()
```

2. **Use Streaming for Large Datasets**
```python
# Good: Stream events
spout = limacharlie.Spout(manager, 'event')
for event in spout:
    process_event(event)

# Bad: Query all events at once
events = manager.query('*', limit=1000000)
```

3. **Connection Pooling**
```python
# Reuse Manager instance
manager = limacharlie.Manager('ORG_ID', 'API_KEY')
# Use this manager instance throughout your application
```

### Security Best Practices

1. **Credential Management**
```python
# Good: Use environment variables or secure vaults
import os
api_key = os.environ.get('LC_API_KEY')

# Bad: Hardcode credentials
api_key = 'hardcoded-api-key'
```

2. **Least Privilege**
```python
# Create API keys with minimal required permissions
# Use read-only keys when write access isn't needed
```

3. **Audit Logging**
```python
# Enable audit logging for all operations
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    print_debug_fn=audit_logger.log
)
```

### Error Handling Best Practices

1. **Graceful Degradation**
```python
def get_sensor_info_safe(sensor_id):
    try:
        sensor = manager.sensor(sensor_id)
        return sensor.getInfo()
    except LcApiException:
        return {'error': 'Unable to retrieve sensor info'}
```

2. **Retry with Backoff**
```python
@retry(max_attempts=3, backoff_factor=2)
def reliable_task(sensor, command):
    return sensor.task(command)
```

3. **Timeout Handling**
```python
# Always set reasonable timeouts
result = sensor.simpleRequest('os_processes', timeout=60)
```

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failures**
```python
# Check API key format
assert len(api_key) == 36  # UUID format
assert api_key.count('-') == 4

# Verify organization ID
assert len(oid) == 36  # UUID format
```

2. **Sensor Offline**
```python
# Wait for sensor to come online
if not sensor.isOnline():
    came_online = sensor.waitToComeOnline(timeout=300)
    if not came_online:
        print("Sensor did not come online")
```

3. **Rate Limiting**
```python
# Handle rate limits
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    isRetryQuotaErrors=True
)
```

4. **Network Issues**
```python
# Check connectivity
import requests
try:
    response = requests.get('https://api.limacharlie.io/health')
    assert response.status_code == 200
except:
    print("Cannot reach LimaCharlie API")
```

## API Reference Links

- [LimaCharlie REST API Documentation](https://api.limacharlie.io/openapi)
- [LimaCharlie Python SDK GitHub](https://github.com/refractionPOINT/python-limacharlie)
- [LimaCharlie Documentation](https://docs.limacharlie.io)
- [LimaCharlie Web Console](https://app.limacharlie.io)

## Support

For SDK issues or questions:
- GitHub Issues: https://github.com/refractionPOINT/python-limacharlie/issues
- LimaCharlie Support: support@limacharlie.io
- Community Slack: https://slack.limacharlie.io

---

## See Also

- [SDK Overview](index.md)
- [Go SDK](go-sdk.md)
- [API Keys](../../7-administration/access/api-keys.md)
