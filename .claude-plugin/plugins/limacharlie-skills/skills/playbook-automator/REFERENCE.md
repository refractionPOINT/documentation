# Playbook Reference Documentation

Complete technical reference for LimaCharlie Playbook extension.

## Table of Contents

- [Triggering Methods](#triggering-methods)
- [SDK Reference](#sdk-reference)
- [Advanced Patterns](#advanced-patterns)
- [Infrastructure as Code](#infrastructure-as-code)

## Triggering Methods

### D&R Rule Triggers (Detailed)

The most powerful way to use playbooks is triggering them from D&R rules. This allows automated response to detections.

#### Basic D&R Trigger

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: mimikatz
  case sensitive: false

respond:
  - action: extension request
    extension name: ext-playbook
    extension action: run_playbook
    extension request:
      name: '{{ "investigate-mimikatz" }}'
      credentials: '{{ "hive://secret/lc-api-key" }}'
      data:
        sid: "{{ .routing.sid }}"
        hostname: "{{ .routing.hostname }}"
        process_id: "{{ .event.PROCESS_ID }}"
        command_line: "{{ .event.COMMAND_LINE }}"
```

#### Passing Event Context

Use Go template syntax to pass event data to playbooks:

```yaml
data:
  # Routing information
  sid: "{{ .routing.sid }}"
  hostname: "{{ .routing.hostname }}"
  platform: "{{ .routing.plat }}"

  # Event data
  event_type: "{{ .routing.event_type }}"
  timestamp: "{{ .routing.event_time }}"

  # Process information
  process_id: "{{ .event.PROCESS_ID }}"
  parent_process_id: "{{ .event.PARENT_PROCESS_ID }}"
  file_path: "{{ .event.FILE_PATH }}"
  command_line: "{{ .event.COMMAND_LINE }}"
  hash: "{{ .event.HASH }}"

  # Network information (if applicable)
  ip_address: "{{ .event.IP_ADDRESS }}"
  port: "{{ .event.NETWORK_ACTIVITY.PORT }}"
  domain: "{{ .event.DOMAIN_NAME }}"

  # User information
  user_name: "{{ .event.USER_NAME }}"
```

#### Conditional Playbook Execution

Only trigger playbooks for specific conditions:

```yaml
respond:
  - action: extension request
    extension name: ext-playbook
    extension action: run_playbook
    extension request:
      name: '{{ if eq .routing.plat "windows" }}windows-playbook{{ else }}linux-playbook{{ end }}'
      credentials: '{{ "hive://secret/lc-api-key" }}'
      data:
        sid: "{{ .routing.sid }}"
```

### Python SDK Triggers (Detailed)

#### Basic SDK Invocation

```python
import limacharlie

# Authenticate to your organization
lc = limacharlie.Manager()

# Get extension manager
ext = limacharlie.Extension(lc)

# Execute playbook
response = ext.request("ext-playbook", "run_playbook", {
    "name": "my-playbook",
    "credentials": "hive://secret/my-api-key",
    "data": {
        "target_host": "server-123",
        "incident_id": "INC-2024-001"
    }
})

print(response)
```

#### Error Handling

```python
import limacharlie

try:
    lc = limacharlie.Manager()
    ext = limacharlie.Extension(lc)

    response = ext.request("ext-playbook", "run_playbook", {
        "name": "my-playbook",
        "credentials": "hive://secret/my-api-key",
        "data": {"param": "value"}
    })

    # Check for playbook errors
    if "error" in response:
        print(f"Playbook error: {response['error']}")
    else:
        print(f"Playbook success: {response.get('data', {})}")

except limacharlie.LcApiException as e:
    print(f"API error: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

#### Batch Playbook Execution

```python
import limacharlie
import concurrent.futures

lc = limacharlie.Manager()
ext = limacharlie.Extension(lc)

# List of hosts to investigate
hosts = ["host-1", "host-2", "host-3", "host-4"]

def run_playbook_for_host(hostname):
    """Run playbook for a single host."""
    try:
        response = ext.request("ext-playbook", "run_playbook", {
            "name": "investigate-host",
            "credentials": "hive://secret/my-api-key",
            "data": {"hostname": hostname}
        })
        return {"hostname": hostname, "response": response}
    except Exception as e:
        return {"hostname": hostname, "error": str(e)}

# Execute playbooks in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(run_playbook_for_host, hosts))

for result in results:
    print(f"{result['hostname']}: {result.get('response', result.get('error'))}")
```

### REST API Triggers (Detailed)

#### Basic API Call

```bash
curl -X POST https://api.limacharlie.io/v1/orgs/YOUR_OID/extension \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ext-playbook",
    "action": "run_playbook",
    "request": {
      "name": "my-playbook",
      "credentials": "hive://secret/my-api-key",
      "data": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  }'
```

#### With Python Requests Library

```python
import requests
import json

oid = "your-org-id"
api_key = "your-api-key"

url = f"https://api.limacharlie.io/v1/orgs/{oid}/extension"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "name": "ext-playbook",
    "action": "run_playbook",
    "request": {
        "name": "my-playbook",
        "credentials": "hive://secret/my-api-key",
        "data": {
            "incident_id": "INC-001",
            "severity": "high"
        }
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    print(f"Success: {result}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

#### Webhook Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Receive webhook and trigger playbook."""

    webhook_data = request.json

    # Extract relevant information
    alert_type = webhook_data.get("type")
    severity = webhook_data.get("severity")

    # Trigger LimaCharlie playbook
    lc_url = "https://api.limacharlie.io/v1/orgs/YOUR_OID/extension"

    response = requests.post(lc_url, headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }, json={
        "name": "ext-playbook",
        "action": "run_playbook",
        "request": {
            "name": "process-external-alert",
            "credentials": "hive://secret/my-api-key",
            "data": {
                "alert_type": alert_type,
                "severity": severity,
                "raw_data": webhook_data
            }
        }
    })

    return jsonify({"status": "playbook_triggered", "response": response.json()})

if __name__ == '__main__':
    app.run(port=5000)
```

## SDK Reference

Complete reference for the LimaCharlie Python SDK within playbooks.

### Manager Operations

The `sdk` object is a pre-authenticated `limacharlie.Manager()` instance.

#### Organization Information

```python
def playbook(sdk, data):
    # Get organization info
    org_info = sdk.getOrgInfo()
    # Returns: {'name': 'org-name', 'id': 'oid', ...}

    # Get organization outputs
    outputs = sdk.getOutputs()
    # Returns list of configured outputs

    # Get organization quota
    quota = sdk.getOrgQuota()

    return {"data": {"org": org_info}}
```

### Sensor Operations

#### Listing Sensors

```python
def playbook(sdk, data):
    all_sensors = []

    # Iterate through all sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()
        all_sensors.append({
            "sid": info.get("sid"),
            "hostname": info.get("hostname"),
            "platform": info.get("plat"),
            "online": info.get("is_online"),
            "tags": info.get("tags", []),
            "last_seen": info.get("last_seen")
        })

    return {"data": {"sensors": all_sensors}}
```

#### Getting Specific Sensor

```python
def playbook(sdk, data):
    sid = data.get("sid")

    # Get sensor by ID
    sensor = sdk.sensor(sid)

    # Get sensor information
    info = sensor.getInfo()

    return {"data": {
        "sid": info.get("sid"),
        "hostname": info.get("hostname"),
        "platform": info.get("plat"),
        "architecture": info.get("arch"),
        "online": info.get("is_online"),
        "last_seen": info.get("last_seen"),
        "tags": info.get("tags", []),
        "ip_addresses": info.get("ip_addresses", []),
        "external_ip": info.get("external_ip"),
        "agent_version": info.get("agent_version")
    }}
```

#### Tasking Sensors

Available sensor tasks:

```python
def playbook(sdk, data):
    sid = data.get("sid")
    sensor = sdk.sensor(sid)

    # History dump
    sensor.task("history_dump", investigationId="investigation-123")

    # Process listing
    sensor.task("os_processes", investigationId="investigation-123")

    # Network connections
    sensor.task("os_network_connections", investigationId="investigation-123")

    # File system operations
    sensor.task("os_dir_list C:\\Users\\", investigationId="investigation-123")
    sensor.task("dir_find_hash C:\\ --hash HASH_VALUE", investigationId="investigation-123")

    # Memory operations
    sensor.task("mem_map --pid 1234", investigationId="investigation-123")
    sensor.task("mem_strings --pid 1234", investigationId="investigation-123")
    sensor.task("mem_dump --pid 1234", investigationId="investigation-123")

    # Process control
    sensor.task("deny_tree 1234")  # Kill process tree
    sensor.task("suspend 1234")    # Suspend process
    sensor.task("resume 1234")     # Resume process

    # Network isolation
    sensor.task("segregate_network")     # Isolate network
    sensor.task("rejoin_network")        # Restore network

    # Registry operations (Windows)
    sensor.task("reg_list HKEY_LOCAL_MACHINE\\SOFTWARE\\", investigationId="investigation-123")

    # Document collection
    sensor.task("doc_cache_get --hash DOC_HASH", investigationId="investigation-123")

    # Yara scanning
    sensor.task("yara_scan --pid 1234 --rule-name my-rule", investigationId="investigation-123")

    return {"data": {"tasks_issued": True}}
```

#### Tagging Sensors

```python
def playbook(sdk, data):
    sid = data.get("sid")
    sensor = sdk.sensor(sid)

    # Add tag (permanent)
    sensor.tag("compromised")

    # Add tag with TTL (seconds)
    sensor.tag("investigating", ttl=3600)  # Expires in 1 hour

    # Remove tag
    sensor.untag("investigating")

    return {"data": {"tagged": True}}
```

### Hive Operations

Hive is LimaCharlie's key-value store for configuration, secrets, and data.

#### Hive Types

- `secret`: Sensitive credentials
- `lookup`: Lists and lookup tables
- `playbook`: Playbook code
- `dr-general`: D&R rules (general)
- `dr-managed`: D&R rules (managed)
- `artifact-collection`: Artifact collection rules
- `fp`: False positive rules
- `exfil`: Exfil rules

#### Secret Management

```python
def playbook(sdk, data):
    # Access secrets
    secret_hive = limacharlie.Hive(sdk, "secret")

    # Get secret
    api_key = secret_hive.get("my-api-key").data["secret"]

    # Set secret (requires proper credentials)
    # secret_hive.set("new-secret", {"secret": "secret-value"})

    # List all secret keys
    all_secrets = secret_hive.list()

    return {"data": {"secret_keys": list(all_secrets.keys())}}
```

#### Lookup Tables

```python
def playbook(sdk, data):
    # Access lookups
    lookup_hive = limacharlie.Hive(sdk, "lookup")

    # Get lookup
    malicious_ips = lookup_hive.get("malicious-ip-list").data

    # Check if IP is in list
    ip_to_check = data.get("ip_address")
    is_malicious = ip_to_check in malicious_ips.get("ips", [])

    # Set lookup (requires proper credentials)
    # lookup_hive.set("my-lookup", {"ips": ["1.2.3.4", "5.6.7.8"]})

    return {"data": {"is_malicious": is_malicious}}
```

#### Playbook Storage

```python
def playbook(sdk, data):
    # Access playbook hive
    playbook_hive = limacharlie.Hive(sdk, "playbook")

    # Store data for later use
    playbook_hive.set("investigation-data", {
        "timestamp": data.get("timestamp"),
        "findings": data.get("findings")
    })

    # Retrieve stored data
    previous_data = playbook_hive.get("investigation-data").data

    return {"data": {"stored": True, "previous": previous_data}}
```

#### D&R Rules

```python
def playbook(sdk, data):
    # Access D&R rules
    dr_hive = limacharlie.Hive(sdk, "dr-general")

    # Get specific rule
    rule = dr_hive.get("my-rule-name")

    # List all rules
    all_rules = dr_hive.list()

    # Set/update rule (requires proper credentials)
    # dr_hive.set("new-rule", {
    #     "detect": {...},
    #     "respond": [...]
    # })

    return {"data": {"rules": list(all_rules.keys())}}
```

### Detection Operations

```python
def playbook(sdk, data):
    # Get recent detections
    detections = sdk.getDetections(limit=100)

    # Filter detections
    high_severity = []
    for det in detections:
        category = det.get("detect", {}).get("cat", "")
        if "critical" in category or "high" in category:
            high_severity.append({
                "category": category,
                "hostname": det.get("routing", {}).get("hostname"),
                "timestamp": det.get("routing", {}).get("event_time")
            })

    return {"data": {"high_severity_detections": high_severity}}
```

### Timeline Operations

```python
def playbook(sdk, data):
    sid = data.get("sid")

    # Get sensor timeline
    sensor = sdk.sensor(sid)

    # Query timeline (requires specific time range and event types)
    # Note: This is a simplified example - production use requires LCQL

    return {"data": {"timeline_query": "Use LCQL for timeline queries"}}
```

### Extension Operations

```python
def playbook(sdk, data):
    # Call other extensions
    ext = limacharlie.Extension(sdk)

    # Trigger another playbook
    response = ext.request("ext-playbook", "run_playbook", {
        "name": "another-playbook",
        "credentials": "hive://secret/api-key",
        "data": {"param": "value"}
    })

    # Call other extensions (e.g., PagerDuty)
    pagerduty_response = ext.request("pagerduty", "trigger", {
        "severity": "critical",
        "summary": "Security incident detected",
        "source": "limacharlie-playbook"
    })

    return {"data": {"extension_responses": [response, pagerduty_response]}}
```

## Advanced Patterns

### Conditional Logic and Workflows

Build complex decision trees:

```python
import limacharlie

def playbook(sdk, data):
    """Multi-stage investigation workflow with conditional logic."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    file_hash = data.get("hash")

    workflow_state = {
        "stage": "initial",
        "actions": [],
        "findings": []
    }

    # Stage 1: Verify sensor status
    workflow_state["stage"] = "sensor_verification"
    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()

        if not info.get("is_online"):
            workflow_state["findings"].append("sensor_offline")
            return {
                "data": workflow_state,
                "error": "Cannot proceed - sensor offline"
            }

        workflow_state["actions"].append("sensor_verified")

    except Exception as e:
        return {"error": f"Sensor verification failed: {str(e)}"}

    # Stage 2: Check if hash is known malicious
    workflow_state["stage"] = "threat_intel_check"
    try:
        lookup_hive = limacharlie.Hive(sdk, "lookup")
        malware_hashes = lookup_hive.get("known-malware-hashes").data

        is_known_malware = file_hash in malware_hashes.get("hashes", [])
        workflow_state["findings"].append(f"known_malware: {is_known_malware}")

        if is_known_malware:
            # Fast path: immediate containment
            workflow_state["stage"] = "immediate_containment"
            sensor.task("segregate_network")
            workflow_state["actions"].append("network_isolated")

            return {
                "detection": {
                    "hash": file_hash,
                    "sensor": info.get("hostname"),
                    "workflow": workflow_state
                },
                "cat": "known-malware-detected",
                "data": workflow_state
            }

    except Exception as e:
        workflow_state["findings"].append(f"threat_intel_error: {str(e)}")

    # Stage 3: Deep investigation for unknown files
    workflow_state["stage"] = "deep_investigation"

    # Check sensor tags for special handling
    tags = info.get("tags", [])

    if "vip" in tags:
        # Enhanced investigation for VIP systems
        workflow_state["actions"].extend([
            "memory_dump_collected",
            "full_history_collected",
            "network_connections_logged"
        ])
        severity = "high"
    elif "dev" in tags:
        # Relaxed handling for dev systems
        workflow_state["actions"].append("basic_telemetry_collected")
        severity = "low"
    else:
        # Standard investigation
        workflow_state["actions"].append("standard_investigation")
        severity = "medium"

    workflow_state["stage"] = "complete"

    return {
        "detection": {
            "hash": file_hash,
            "sensor": info.get("hostname"),
            "severity": severity,
            "workflow": workflow_state
        },
        "cat": f"unknown-file-{severity}",
        "data": workflow_state
    }
```

### Looping and Iteration

Process multiple items efficiently:

```python
import limacharlie

def playbook(sdk, data):
    """Process multiple IoCs across sensors."""

    if not sdk:
        return {"error": "API credentials required"}

    iocs = data.get("iocs", [])
    if not iocs:
        return {"error": "No IoCs provided"}

    results = {
        "processed": 0,
        "matches_found": 0,
        "sensors_affected": [],
        "errors": []
    }

    # Iterate through IoCs
    for ioc in iocs:
        ioc_type = ioc.get("type")
        ioc_value = ioc.get("value")

        results["processed"] += 1

        try:
            # Search across all sensors
            for sensor in sdk.sensors():
                info = sensor.getInfo()

                # Skip offline sensors
                if not info.get("is_online"):
                    continue

                # Type-specific search
                if ioc_type == "hash":
                    # Search for file hash
                    sensor.task(
                        f"dir_find_hash C:\\ --hash {ioc_value}",
                        investigationId=f"ioc-sweep-{ioc_value[:8]}"
                    )
                elif ioc_type == "domain":
                    # Search timeline for DNS requests (would need LCQL in production)
                    pass
                elif ioc_type == "ip":
                    # Search timeline for network connections
                    pass

                results["sensors_affected"].append({
                    "sid": info.get("sid"),
                    "hostname": info.get("hostname"),
                    "ioc": ioc_value
                })
                results["matches_found"] += 1

        except Exception as e:
            results["errors"].append({
                "ioc": ioc_value,
                "error": str(e)
            })

    return {"data": results}
```

### Error Handling Patterns

Comprehensive error handling:

```python
import limacharlie

def playbook(sdk, data):
    """Playbook with comprehensive error handling."""

    # Validate inputs
    if not sdk:
        return {"error": "API credentials required for this playbook"}

    required_fields = ["sid", "process_id"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required parameter: {field}"}

    try:
        sensor = sdk.sensor(data["sid"])

        # Verify sensor is online before tasking
        info = sensor.getInfo()
        if not info.get("is_online"):
            return {
                "error": f"Sensor {data['sid']} is offline",
                "data": {"sensor_status": "offline"}
            }

        # Execute task with timeout consideration
        sensor.task(f"history_dump", investigationId="error-handling-example")

        return {
            "data": {
                "success": True,
                "sensor": info.get("hostname")
            }
        }

    except limacharlie.LcApiException as e:
        # Handle LC API errors
        return {
            "error": f"LimaCharlie API error: {str(e)}",
            "data": {"error_type": "api_error"}
        }

    except Exception as e:
        # Handle unexpected errors
        return {
            "error": f"Unexpected error: {str(e)}",
            "data": {"error_type": "unknown"}
        }
```

## Infrastructure as Code

Store playbooks in version control and deploy via Infrastructure as Code.

### YAML Configuration Format

```yaml
# limacharlie-config.yaml
hives:
  playbook:
    investigate-mimikatz:
      data:
        python: |-
          import limacharlie

          def playbook(sdk, data):
              """Investigate Mimikatz detection."""

              if not sdk:
                  return {"error": "API credentials required"}

              sid = data.get("sid")
              pid = data.get("process_id")

              if not sid or not pid:
                  return {"error": "Missing required parameters"}

              # Get sensor
              sensor = sdk.sensor(sid)

              # Collect evidence
              sensor.task("history_dump", investigationId=f"mimikatz-{pid}")
              sensor.task(f"mem_map --pid {pid}", investigationId=f"mimikatz-{pid}")

              # Tag sensor
              sensor.tag("mimikatz-detected", ttl=86400)

              # Network isolate
              sensor.task("segregate_network")

              return {
                  "detection": {
                      "investigation_id": f"mimikatz-{pid}",
                      "actions_taken": [
                          "history_collected",
                          "memory_mapped",
                          "sensor_tagged",
                          "network_isolated"
                      ]
                  },
                  "cat": "mimikatz-investigation-complete",
                  "data": {
                      "sensor": sid,
                      "process": pid
                  }
              }
      usr_mtd:
        enabled: true
        expiry: 0
        tags: []
        comment: "Automated Mimikatz investigation and containment"

    scheduled-health-check:
      data:
        python: |-
          import limacharlie
          from datetime import datetime

          def playbook(sdk, data):
              """Generate fleet health report."""

              if not sdk:
                  return {"error": "API credentials required"}

              stats = {
                  "total_sensors": 0,
                  "online_sensors": 0,
                  "offline_sensors": 0
              }

              for sensor in sdk.sensors():
                  info = sensor.getInfo()
                  stats["total_sensors"] += 1

                  if info.get("is_online"):
                      stats["online_sensors"] += 1
                  else:
                      stats["offline_sensors"] += 1

              report = {
                  "report_date": datetime.now().isoformat(),
                  "fleet_summary": stats
              }

              return {"data": report}
      usr_mtd:
        enabled: true
        expiry: 0
        tags: ["scheduled", "reporting"]
        comment: "Daily fleet health check"
```

### Deployment

Deploy using the LimaCharlie CLI:

```bash
# Push configuration to organization
limacharlie configs push limacharlie-config.yaml

# Pull current configuration
limacharlie configs pull > current-config.yaml

# Validate configuration
limacharlie configs validate limacharlie-config.yaml
```

### Version Control Integration

```bash
# .gitignore
secrets.yaml
*.key
*.pem

# Store playbooks in git
git add limacharlie-config.yaml
git commit -m "Add mimikatz investigation playbook"
git push

# Deploy via CI/CD
# .github/workflows/deploy-playbooks.yml
name: Deploy Playbooks
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install LimaCharlie CLI
        run: pip install limacharlie

      - name: Configure credentials
        env:
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
        run: |
          echo "$LC_API_KEY" > ~/.limacharlie

      - name: Deploy playbooks
        run: limacharlie configs push limacharlie-config.yaml
```

### Multi-Environment Management

```yaml
# config/production.yaml
organization: prod-org-id
hives:
  playbook:
    critical-response:
      data:
        python: |
          # Production playbook with strict checks
          ...

# config/staging.yaml
organization: staging-org-id
hives:
  playbook:
    critical-response:
      data:
        python: |
          # Staging playbook with debug logging
          ...
```

Deploy to specific environment:

```bash
# Deploy to staging
limacharlie -o staging-org-id configs push config/staging.yaml

# Deploy to production
limacharlie -o prod-org-id configs push config/production.yaml
```

---

For practical examples, see [EXAMPLES.md](./EXAMPLES.md).

For debugging and testing, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
