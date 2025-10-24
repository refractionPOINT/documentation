# Python SDK Reference

Complete reference for the LimaCharlie Python SDK.

## Installation

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

---

## Authentication

### Direct API Key Authentication

```python
import limacharlie

manager = limacharlie.Manager(
    oid='YOUR_ORGANIZATION_ID',
    secret_api_key='YOUR_API_KEY'
)
```

### Environment Variables

```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

```python
import limacharlie

# Uses environment variables automatically
manager = limacharlie.Manager()
```

### Configuration File

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

---

## Manager Class

The `Manager` class is the main entry point for the SDK.

### Initialization

```python
manager = limacharlie.Manager(
    oid='org-id',                    # Organization ID
    secret_api_key='api-key',        # API Key
    environment='production',         # Named environment from config
    is_interactive=False,             # Enable interactive tasking
    inv_id='investigation-id',        # Investigation ID for tracking
    print_debug_fn=None,              # Debug logging function
    isRetryQuotaErrors=False          # Auto-retry on rate limits
)
```

### Organization Operations

#### Get Organization Information

```python
org_info = manager.getOrgInfo()
print(f"Organization: {org_info['name']}")
print(f"Owner: {org_info['owner']}")
```

#### Get Online Sensor Count

```python
online_count = manager.getOnlineHosts()
print(f"Online sensors: {online_count}")
```

### Sensor Operations

#### List All Sensors

```python
# Basic listing
sensors = manager.sensors()
for sid, info in sensors.items():
    print(f"Sensor: {sid}")
    print(f"  Hostname: {info['hostname']}")
    print(f"  Platform: {info['platform']}")
    print(f"  Online: {info.get('online', False)}")

# With detailed information
detailed_sensors = manager.sensors(with_details=True)
```

#### Get Sensors by Tag

```python
production_sensors = manager.getSensorsWithTag('production')
for sid, info in production_sensors.items():
    print(f"{sid}: {info['hostname']}")
```

#### Search by Hostname Pattern

```python
# Supports wildcards
web_servers = manager.getHostnames(['web-*', 'app-*'])
for hostname, sensors in web_servers.items():
    print(f"{hostname}: {sensors}")
```

#### Get Specific Sensor

```python
sensor = manager.sensor('SENSOR_ID')
```

---

## Sensor Class

The `Sensor` class represents an individual endpoint sensor.

### Get Sensor Information

```python
sensor = manager.sensor('SENSOR_ID')

# Basic information
hostname = sensor.getHostname()
platform = sensor.getPlatform()        # windows, linux, macos, chrome
architecture = sensor.getArchitecture() # x64, x86, arm64
sid = sensor.getSid()

# Detailed information
info = sensor.getInfo()
```

### Check Sensor Status

```python
is_online = sensor.isOnline()
is_isolated = sensor.isIsolated()

if is_online:
    print(f"{hostname} is online")
```

### Tag Management

```python
# Get current tags
tags = sensor.getTags()

# Add tag (TTL in seconds, 0 = permanent)
sensor.addTag('critical', ttl=3600)
sensor.addTag('production', ttl=0)

# Remove tag
sensor.removeTag('old-tag')
```

### Tasking Sensors

#### Simple Task (Fire and Forget)

```python
# Single task
sensor.task('os_processes')

# Multiple tasks
sensor.task(['os_processes', 'os_services', 'netstat'])

# Task with investigation ID
sensor.setInvId('investigation-123')
sensor.task('history_dump')
```

#### Interactive Tasking (Get Responses)

For interactive tasking, initialize Manager with `is_interactive=True`:

```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    is_interactive=True,
    inv_id='investigation-123'
)

sensor = manager.sensor('SENSOR_ID')

# Simple blocking request (waits for response)
result = sensor.simpleRequest('os_info', timeout=30)
print(result)

# Request with callback for each response
def process_response(event):
    print(f"Received: {event}")

sensor.simpleRequest(
    'os_processes',
    timeout=30,
    until_completion=process_response
)
```

### Network Isolation

```python
# Isolate sensor from network
sensor.isolate()

# Check isolation status
if sensor.isIsolated():
    print("Sensor is isolated")

# Rejoin network
sensor.rejoin()
```

### Sensor Deletion

```python
sensor.delete()
```

---

## Hive (Key-Value Storage)

The Hive system is used for storing D&R rules, configurations, and other data.

### Initialize Hive

```python
from limacharlie import Hive, HiveRecord

hive = Hive(manager)
```

### Create/Update Records

```python
# Detection rule example
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

# Create record
record = HiveRecord(
    hive_name='dr-general',
    partition_key=manager.oid,
    key='detect-mimikatz',
    data=rule_data,
    enabled=True,
    ttl=0  # 0 = permanent
)

hive.set(record)
```

### List Records

```python
# List all D&R rules
rules = hive.list(
    hive_name='dr-general',
    partition_key=manager.oid
)

for rule in rules:
    print(f"Rule: {rule['key']}")
    print(f"  Enabled: {rule.get('enabled', False)}")
    print(f"  Data: {rule['data']}")
```

### Get Specific Record

```python
rule = hive.get(
    hive_name='dr-general',
    partition_key=manager.oid,
    key='detect-mimikatz'
)
```

### Delete Record

```python
hive.delete(
    hive_name='dr-general',
    partition_key=manager.oid,
    key='detect-mimikatz'
)
```

---

## Event Streaming

### Spout (Pull-based Streaming)

Spout pulls events from the LimaCharlie cloud. Good for moderate volume and works through NAT/firewalls.

#### Stream Detections

```python
spout = limacharlie.Spout(
    manager,
    data_type='detect',  # detect, event, audit, or tailored
    is_parse=True,       # Parse JSON automatically
    tag='production',    # Optional: filter by tag
    cat='malware',       # Optional: filter by category
    inv_id='inv-123'     # Optional: filter by investigation
)

try:
    for detection in spout:
        print(f"Detection: {detection['detect_name']}")
        print(f"Sensor: {detection['sid']}")
        print(f"Priority: {detection.get('priority', 0)}")

        # Take action
        if detection['priority'] >= 4:
            sensor = manager.sensor(detection['sid'])
            sensor.isolate()
finally:
    spout.shutdown()
```

#### Stream Events

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
        cmdline = event['event'].get('COMMAND_LINE', '')
        print(f"Process: {path}")
        print(f"Command: {cmdline}")

spout.shutdown()
```

#### Stream Tailored Events

```python
# Only specific event types
spout = limacharlie.Spout(
    manager,
    data_type='tailored',
    event_type=['NEW_PROCESS', 'NETWORK_CONNECT', 'FILE_CREATE'],
    is_parse=True
)

for event in spout:
    print(f"{event['event_type']} on {event['sid']}")

spout.shutdown()
```

#### Stream Audit Logs

```python
spout = limacharlie.Spout(
    manager,
    data_type='audit',
    is_parse=True
)

for audit_event in spout:
    print(f"User: {audit_event['user']}")
    print(f"Action: {audit_event['action']}")
    print(f"Time: {audit_event['ts']}")

spout.shutdown()
```

### Firehose (Push-based Streaming)

Firehose pushes events to your endpoint. Best for high volume but requires an accessible port.

```python
firehose = limacharlie.Firehose(
    manager,
    listen_on='0.0.0.0:4443',         # Local bind address
    data_type='event',                 # event, detect, audit, or tailored
    name='my_firehose',                # Unique name
    public_dest='YOUR_PUBLIC_IP:4443', # Public IP:Port
    is_parse=True,                     # Parse JSON automatically
    tag='production',                  # Optional: filter by tag
    inv_id='inv-123'                   # Optional: investigation filter
)

firehose.start()

try:
    while True:
        event = firehose.queue.get()

        if event.get('event_type') == 'NETWORK_CONNECT':
            dst = event['event']['DESTINATION']
            print(f"Connection to: {dst['IP_ADDRESS']}:{dst['PORT']}")
finally:
    firehose.shutdown()
```

---

## Artifacts

Artifacts are files collected during investigations (memory dumps, executables, etc.).

### Initialize Artifacts Manager

```python
artifacts = limacharlie.Artifacts(manager)
```

### List Artifacts

```python
artifact_list = artifacts.listArtifacts(
    start_time=1234567890,  # Unix timestamp
    end_time=1234567999,
    sid='SENSOR_ID'         # Optional: filter by sensor
)

for artifact in artifact_list:
    print(f"Artifact ID: {artifact['aid']}")
    print(f"Name: {artifact['name']}")
    print(f"Size: {artifact['size']} bytes")
```

### Get Artifact

```python
artifact_data = artifacts.getArtifact('ARTIFACT_ID')
```

### Upload Artifact

```python
# Upload file
with open('evidence.txt', 'rb') as f:
    artifact_id = manager.createArtifact(
        name='evidence.txt',
        data=f.read(),
        ttl=86400,          # TTL in seconds (24 hours)
        source='investigation'
    )

print(f"Uploaded: {artifact_id}")
```

---

## Common Task Commands

### System Information

```python
sensor.task('os_info')           # Operating system details
sensor.task('os_processes')      # Running processes
sensor.task('os_services')       # Installed services
sensor.task('os_packages')       # Installed software
sensor.task('os_autoruns')       # Autostart programs
sensor.task('os_drivers')        # Loaded drivers (Windows)
```

### File Operations

```python
sensor.task('file_info /path/to/file')
sensor.task('file_get /path/to/file')      # Download file
sensor.task('file_hash /path/to/file')     # Calculate hash
sensor.task('file_del /path/to/file')      # Delete file
```

### Network Operations

```python
sensor.task('netstat')                      # Network connections
sensor.task('dns_resolve example.com')      # DNS lookup
```

### Process Operations

```python
sensor.task('mem_map 1234')                 # Memory map of PID 1234
sensor.task('kill 1234')                    # Terminate PID 1234
```

### Forensics

```python
sensor.task('history_dump')                 # Event history
sensor.task('hidden_module_scan')           # Scan for hidden modules
sensor.task('os_memory_dump')               # Full memory dump
```

---

## Detection Rule Examples

### Process-based Detection

```python
rule_data = {
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
            'name': 'encoded-powershell',
            'priority': 5
        },
        {
            'action': 'task',
            'command': {
                'action': 'mem_map',
                'process_id': '<<routing/parent_atom>>'
            }
        }
    ]
}
```

### Network-based Detection

```python
rule_data = {
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
            'name': 'suspicious-port',
            'priority': 7
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

### File-based Detection

```python
rule_data = {
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
        },
        {
            'action': 'task',
            'command': {
                'action': 'history_dump'
            }
        }
    ]
}
```

---

## Complete Example: Threat Scanner

```python
import limacharlie
import time
from datetime import datetime

class ThreatScanner:
    def __init__(self, org_id, api_key):
        self.manager = limacharlie.Manager(org_id, api_key)
        self.suspicious_processes = [
            'mimikatz.exe',
            'lazagne.exe',
            'pwdump.exe',
            'procdump.exe'
        ]

    def scan_all_sensors(self):
        """Scan all online sensors for suspicious processes"""
        sensors = self.manager.sensors()
        online_sensors = [
            sid for sid, info in sensors.items()
            if info.get('online', False)
        ]

        print(f"Scanning {len(online_sensors)} online sensors...")
        findings = []

        for sid in online_sensors:
            sensor = self.manager.sensor(sid)
            hostname = sensor.getHostname()

            try:
                # Get process list
                result = sensor.simpleRequest('os_processes', timeout=30)

                if result and 'processes' in result:
                    for process in result['processes']:
                        name = process.get('name', '').lower()

                        # Check against suspicious list
                        for suspicious in self.suspicious_processes:
                            if suspicious.lower() in name:
                                finding = {
                                    'sensor': sid,
                                    'hostname': hostname,
                                    'process': name,
                                    'pid': process.get('pid'),
                                    'timestamp': datetime.now().isoformat()
                                }
                                findings.append(finding)

                                print(f"[!] ALERT: {hostname}")
                                print(f"    Process: {name} (PID: {finding['pid']})")

                                # Tag sensor
                                sensor.addTag('suspicious-process')

            except Exception as e:
                print(f"[ERROR] {hostname}: {e}")

            # Rate limiting
            time.sleep(1)

        return findings

    def monitor_detections(self, duration=3600):
        """Monitor for detections in real-time"""
        spout = limacharlie.Spout(
            self.manager,
            data_type='detect',
            is_parse=True
        )

        start = time.time()
        detection_count = 0

        print(f"Monitoring detections for {duration} seconds...")

        try:
            for detection in spout:
                if time.time() - start > duration:
                    break

                detection_count += 1
                detect_name = detection['detect_name']
                priority = detection.get('priority', 0)
                sid = detection['sid']
                hostname = detection.get('hostname', 'unknown')

                print(f"\n[DETECTION #{detection_count}]")
                print(f"  Name: {detect_name}")
                print(f"  Priority: {priority}")
                print(f"  Sensor: {hostname} ({sid})")
                print(f"  Time: {datetime.fromtimestamp(detection['ts'])}")

                # Auto-respond to high-priority detections
                if priority >= 4:
                    print(f"  [ACTION] Isolating sensor due to high priority")
                    sensor = self.manager.sensor(sid)
                    sensor.isolate()
                    sensor.task('history_dump')
                    sensor.addTag('high-priority-detection')

        finally:
            spout.shutdown()
            print(f"\nMonitoring complete. {detection_count} detections processed.")

# Usage
if __name__ == "__main__":
    scanner = ThreatScanner('YOUR_ORG_ID', 'YOUR_API_KEY')

    # Scan for suspicious processes
    findings = scanner.scan_all_sensors()
    print(f"\nScan complete: {len(findings)} suspicious processes found")

    # Monitor detections for 1 hour
    scanner.monitor_detections(duration=3600)
```

---

## Error Handling

### Common Exceptions

```python
from limacharlie.utils import LcApiException

try:
    sensor = manager.sensor('SENSOR_ID')
    result = sensor.task('os_processes')
except LcApiException as e:
    if '401' in str(e):
        print("Authentication failed")
    elif '403' in str(e):
        print("Insufficient permissions")
    elif '404' in str(e):
        print("Sensor not found")
    elif '429' in str(e):
        print("Rate limited")
    else:
        print(f"API error: {e}")
```

### Auto-retry on Rate Limits

```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    isRetryQuotaErrors=True  # Automatically retry on 429
)
```

### Custom Retry Logic

```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except LcApiException as e:
            if 'rate limit' in str(e).lower() and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")

# Usage
result = retry_with_backoff(lambda: sensor.task('os_processes'))
```

---

## Additional Resources

- **GitHub**: https://github.com/refractionPOINT/python-limacharlie
- **PyPI**: https://pypi.org/project/limacharlie/
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
