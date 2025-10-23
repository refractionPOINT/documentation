---
name: playbook-automator
description: Use this skill when the user needs help designing, implementing, testing, or troubleshooting automated response playbooks using LimaCharlie's Playbook extension.
---

# LimaCharlie Playbook Automator

This skill helps you design and implement automated response playbooks using LimaCharlie's Playbook extension. Use this when users need assistance creating Python-based automation workflows, integrating with external systems, orchestrating complex responses, or building custom detection logic.

## What are Playbooks?

Playbooks are Python scripts that execute within LimaCharlie's cloud infrastructure to automate security operations tasks. They provide a programmable way to:

- Orchestrate complex multi-step response workflows
- Integrate with external security tools and services
- Implement custom detection and enrichment logic
- Automate investigation procedures
- Perform batch operations across sensors
- Generate custom reports and notifications
- Execute scheduled maintenance tasks

### Key Benefits

1. **Serverless Execution**: Run in LimaCharlie's cloud without managing infrastructure
2. **Full SDK Access**: Complete access to LimaCharlie's Python SDK for all operations
3. **Secure Credential Management**: Store secrets safely in Hive for use in playbooks
4. **Multiple Trigger Methods**: Manual, D&R rule-based, API-triggered, or scheduled execution
5. **Rich Execution Environment**: Pre-installed packages including ML libraries, AI CLI tools, and more
6. **Organization Isolation**: Each organization's playbooks run in dedicated containers

## Playbook Structure

Every playbook is a Python script with a required top-level function:

```python
import limacharlie
import json

def playbook(sdk, data):
    """
    Required entry point for all playbooks.

    Args:
        sdk: Pre-authenticated limacharlie.Manager() instance (or None if no credentials provided)
        data: Dictionary of input parameters passed to the playbook

    Returns:
        Dictionary with optional keys:
            - data: Dictionary to return to caller
            - error: Error message string
            - detection: Dictionary to use as a detection
            - cat: String category for the detection
    """

    # Your automation logic here

    return {
        "data": {"result": "success"},
        # "error": "error message if failed",
        # "detection": {...},
        # "cat": "detection-category"
    }
```

### Return Values

The `playbook()` function must return a dictionary with one or more of these optional keys:

1. **data**: Return data to the caller or LimaCharlie
   ```python
   return {"data": {"sensors": [s.getInfo() for s in sdk.sensors()]}}
   ```

2. **error**: Report an error condition
   ```python
   return {"error": "Failed to connect to external API"}
   ```

3. **detection**: Generate a detection report
   ```python
   return {
       "detection": {
           "title": "Suspicious Activity Detected",
           "content": event_details
       },
       "cat": "suspicious-behavior"
   }
   ```

## Triggering Playbooks

### 1. Via D&R Rules (Automated)

The most powerful way to use playbooks is triggering them automatically from D&R rules:

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/COMMAND_LINE
  value: mimikatz
  case sensitive: false

respond:
  - action: report
    name: Mimikatz Detected
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
        file_path: "{{ .event.FILE_PATH }}"
        command_line: "{{ .event.COMMAND_LINE }}"
```

**Key Points:**
- Use `extension request` action in D&R rules
- Pass detection context via the `data` parameter
- Reference credentials using `hive://secret/` syntax
- Use Go template syntax to inject event data

### 2. Via Python SDK

Invoke playbooks programmatically from your own scripts:

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

### 3. Via API

Make direct REST API calls to execute playbooks:

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
        "param1": "value1"
      }
    }
  }'
```

### 4. Interactive Execution

Run playbooks manually from the LimaCharlie web interface:

1. Navigate to **Extensions** > **Playbook**
2. Select the playbook to execute
3. Optionally provide input data as JSON
4. Click **Run Playbook**
5. View results in the interface

## Common Playbook Patterns

### Pattern 1: Webhook Notification

Send security events to external systems:

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Send detection to external webhook."""

    # Get webhook URL from LimaCharlie secrets
    if not sdk:
        return {"error": "API credentials required"}

    webhook_secret = limacharlie.Hive(sdk, "secret").get("webhook-url").data["secret"]

    # Prepare payload
    payload = {
        "timestamp": data.get("timestamp"),
        "hostname": data.get("hostname"),
        "severity": data.get("severity", "medium"),
        "details": data
    }

    # Send webhook
    try:
        request = urllib.request.Request(
            webhook_secret,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode('utf-8')

        return {
            "data": {
                "status": "sent",
                "response": response_body
            }
        }
    except Exception as e:
        return {"error": f"Webhook failed: {str(e)}"}
```

### Pattern 2: Enrichment from External API

Enhance detections with threat intelligence:

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Enrich IP address with threat intel."""

    ip_address = data.get("ip_address")
    if not ip_address:
        return {"error": "ip_address parameter required"}

    # Get API key from secrets
    if not sdk:
        return {"error": "API credentials required"}

    api_key = limacharlie.Hive(sdk, "secret").get("virustotal-api-key").data["secret"]

    # Query VirusTotal
    try:
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}"
        request = urllib.request.Request(url, headers={"x-apikey": api_key})

        with urllib.request.urlopen(request) as response:
            vt_data = json.loads(response.read().decode('utf-8'))

        # Extract relevant information
        attributes = vt_data.get("data", {}).get("attributes", {})
        last_analysis = attributes.get("last_analysis_stats", {})

        malicious_count = last_analysis.get("malicious", 0)

        # Generate detection if malicious
        if malicious_count > 0:
            return {
                "detection": {
                    "ip_address": ip_address,
                    "malicious_votes": malicious_count,
                    "country": attributes.get("country"),
                    "as_owner": attributes.get("as_owner")
                },
                "cat": "malicious-ip-detected",
                "data": {"enriched": True, "malicious": True}
            }

        return {
            "data": {
                "enriched": True,
                "malicious": False,
                "vt_stats": last_analysis
            }
        }

    except Exception as e:
        return {"error": f"VT lookup failed: {str(e)}"}
```

### Pattern 3: Multi-Sensor Investigation

Perform coordinated investigation across multiple endpoints:

```python
import limacharlie
import time

def playbook(sdk, data):
    """Search for indicator across all Windows sensors."""

    if not sdk:
        return {"error": "API credentials required"}

    ioc_hash = data.get("hash")
    if not ioc_hash:
        return {"error": "hash parameter required"}

    results = []

    # Iterate through all Windows sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()

        # Skip non-Windows sensors
        if info.get("plat") != "windows":
            continue

        # Check if sensor is online
        if not info.get("is_online"):
            continue

        try:
            # Search for hash on sensor
            task_result = sensor.task(
                f"dir_find_hash C:\\ --hash {ioc_hash}",
                investigationId="playbook-hash-search"
            )

            # Wait for response (simplified - production should be more robust)
            time.sleep(2)

            # Check if hash was found (would need to query timeline in real implementation)
            results.append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "searched": True
            })

        except Exception as e:
            results.append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "error": str(e)
            })

    return {
        "data": {
            "ioc": ioc_hash,
            "sensors_searched": len(results),
            "results": results
        }
    }
```

### Pattern 4: Automated Triage and Response

Implement automated decision-making based on context:

```python
import limacharlie

def playbook(sdk, data):
    """Automatically triage and respond to suspicious process."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    pid = data.get("process_id")
    file_path = data.get("file_path", "").lower()

    if not sid or not pid:
        return {"error": "sid and process_id required"}

    # Get sensor
    sensor = sdk.sensor(sid)
    info = sensor.getInfo()

    # Decision logic
    actions_taken = []
    severity = "low"

    # Check if sensor is tagged as VIP
    tags = info.get("tags", [])
    is_vip = "vip" in tags

    # Check if process is in suspicious location
    suspicious_paths = ["\\temp\\", "\\downloads\\", "\\appdata\\local\\temp\\"]
    is_suspicious_location = any(path in file_path for path in suspicious_paths)

    try:
        if is_suspicious_location:
            # Collect process memory dump
            sensor.task(
                f"mem_map --pid {pid}",
                investigationId=f"triage-{pid}"
            )
            actions_taken.append("memory_map_collected")
            severity = "medium"

            # Kill process if on VIP system
            if is_vip:
                sensor.task(f"deny_tree {pid}")
                actions_taken.append("process_killed")
                severity = "high"

                # Isolate VIP system
                sensor.task("segregate_network")
                actions_taken.append("network_isolated")

        # Always collect history
        sensor.task("history_dump", investigationId=f"triage-{pid}")
        actions_taken.append("history_collected")

    except Exception as e:
        return {"error": f"Response actions failed: {str(e)}"}

    # Generate detection
    return {
        "detection": {
            "sensor_id": sid,
            "hostname": info.get("hostname"),
            "process_id": pid,
            "file_path": file_path,
            "is_vip": is_vip,
            "actions_taken": actions_taken
        },
        "cat": f"automated-triage-{severity}",
        "data": {
            "actions": actions_taken,
            "severity": severity
        }
    }
```

### Pattern 5: Scheduled Maintenance

Perform periodic security hygiene tasks:

```python
import limacharlie
from datetime import datetime, timedelta

def playbook(sdk, data):
    """Clean up old detections and generate report."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get retention period (days)
    retention_days = data.get("retention_days", 90)
    cutoff_timestamp = int((datetime.now() - timedelta(days=retention_days)).timestamp())

    stats = {
        "total_sensors": 0,
        "offline_sensors": 0,
        "sensors_needing_update": [],
        "old_detections_found": 0
    }

    # Inventory sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()
        stats["total_sensors"] += 1

        # Check if offline
        if not info.get("is_online"):
            stats["offline_sensors"] += 1

        # Check agent version (example)
        # In production, compare with known latest version
        agent_version = info.get("agent_version", "")
        if agent_version < "5.0.0":  # Example version check
            stats["sensors_needing_update"].append({
                "sid": info.get("sid"),
                "hostname": info.get("hostname"),
                "version": agent_version
            })

    # Generate report
    report = {
        "report_date": datetime.now().isoformat(),
        "fleet_summary": stats,
        "recommendations": []
    }

    if stats["offline_sensors"] > 0:
        report["recommendations"].append(
            f"Investigate {stats['offline_sensors']} offline sensors"
        )

    if len(stats["sensors_needing_update"]) > 0:
        report["recommendations"].append(
            f"Update {len(stats['sensors_needing_update'])} sensors to latest version"
        )

    return {
        "data": report
    }
```

## Working with LimaCharlie SDK

Playbooks receive a pre-authenticated `sdk` object providing full access to the LimaCharlie Python SDK.

### Common SDK Operations

#### Sensor Management

```python
# List all sensors
for sensor in sdk.sensors():
    info = sensor.getInfo()
    print(f"{info['hostname']}: {info['sid']}")

# Get specific sensor
sensor = sdk.sensor("sensor-id-here")

# Task a sensor
sensor.task("history_dump", investigationId="my-investigation")

# Tag a sensor
sensor.tag("compromised", ttl=3600)

# Isolate sensor
sensor.task("segregate_network")
```

#### Hive Operations

```python
# Access secrets
secret_value = limacharlie.Hive(sdk, "secret").get("my-secret").data["secret"]

# Access lookups
lookup = limacharlie.Hive(sdk, "lookup")
domains = lookup.get("malicious-domains").data

# Store data in Hive
playbook_hive = limacharlie.Hive(sdk, "playbook")
playbook_hive.set("my-data", {"results": [1, 2, 3]})

# Access D&R rules
dr_hive = limacharlie.Hive(sdk, "dr-general")
rule = dr_hive.get("my-rule-name")
```

#### Detection Management

```python
# Query detections
detections = sdk.getDetections(limit=100)

for det in detections:
    print(f"{det['detect']['cat']}: {det['routing']['hostname']}")
```

#### Organization Info

```python
# Get org info
org_info = sdk.getOrgInfo()
print(f"Organization: {org_info['name']}")

# Get org outputs
outputs = sdk.getOutputs()
```

## Secret Management

Store sensitive credentials securely in Hive and reference them in playbooks.

### Creating Secrets

Via CLI:
```bash
# Create secret
limacharlie hive set secret --key webhook-url --data "https://hooks.example.com/webhook" --data-key secret

# Create secret from file
echo "my-api-key-value" > api-key.txt
limacharlie hive set secret --key external-api-key --data api-key.txt --data-key secret
```

Via Python SDK:
```python
import limacharlie

lc = limacharlie.Manager()
hive = limacharlie.Hive(lc, "secret")

hive.set("my-secret-name", {
    "secret": "secret-value-here"
})
```

### Using Secrets in Playbooks

```python
def playbook(sdk, data):
    if not sdk:
        return {"error": "API credentials required"}

    # Retrieve secret
    api_key = limacharlie.Hive(sdk, "secret").get("external-api-key").data["secret"]

    # Use in API calls
    # ...
```

### Passing Credentials to Playbooks

When invoking playbooks, pass credentials that the playbook will use:

```yaml
# In D&R rule
- action: extension request
  extension name: ext-playbook
  extension action: run_playbook
  extension request:
    name: '{{ "my-playbook" }}'
    credentials: '{{ "hive://secret/lc-api-key" }}'  # API key for the sdk object
    data:
      webhook_key: '{{ "hive://secret/webhook-url" }}'  # Additional secret for playbook
```

## Error Handling

Implement robust error handling in playbooks:

```python
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

## Conditional Logic and Workflows

Build complex decision trees and workflows:

```python
def playbook(sdk, data):
    """Multi-stage investigation workflow."""

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

## Looping and Iteration

Process multiple items efficiently:

```python
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

## Integration with External Systems

### Ticketing System Integration

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Create ticket in external ticketing system."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get ticketing system credentials
    ticket_api_key = limacharlie.Hive(sdk, "secret").get("ticketing-api-key").data["secret"]
    ticket_url = limacharlie.Hive(sdk, "secret").get("ticketing-url").data["secret"]

    # Prepare ticket data
    ticket = {
        "title": f"Security Incident: {data.get('detection_name')}",
        "description": f"""
        Detection: {data.get('detection_name')}
        Hostname: {data.get('hostname')}
        Sensor ID: {data.get('sid')}
        Timestamp: {data.get('timestamp')}

        Details:
        {json.dumps(data.get('details', {}), indent=2)}
        """,
        "priority": data.get("priority", "medium"),
        "category": "security_incident",
        "tags": data.get("tags", [])
    }

    try:
        request = urllib.request.Request(
            f"{ticket_url}/api/tickets",
            data=json.dumps(ticket).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ticket_api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))

        return {
            "data": {
                "ticket_created": True,
                "ticket_id": result.get("id"),
                "ticket_url": result.get("url")
            }
        }

    except Exception as e:
        return {"error": f"Failed to create ticket: {str(e)}"}
```

### SOAR Integration

```python
def playbook(sdk, data):
    """Trigger SOAR playbook for investigation."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get SOAR credentials
    soar_api_key = limacharlie.Hive(sdk, "secret").get("soar-api-key").data["secret"]
    soar_url = limacharlie.Hive(sdk, "secret").get("soar-url").data["secret"]

    # Map LimaCharlie detection to SOAR playbook
    detection_type = data.get("detection_category")

    playbook_mapping = {
        "ransomware": "investigate-ransomware",
        "lateral-movement": "investigate-lateral-movement",
        "data-exfiltration": "investigate-exfiltration",
        "malware": "investigate-malware"
    }

    soar_playbook = playbook_mapping.get(detection_type, "generic-investigation")

    # Prepare SOAR request
    soar_request = {
        "playbook": soar_playbook,
        "context": {
            "source": "limacharlie",
            "detection": data,
            "artifacts": {
                "hostname": data.get("hostname"),
                "sensor_id": data.get("sid"),
                "file_path": data.get("file_path"),
                "hash": data.get("hash")
            }
        },
        "priority": data.get("priority", "medium")
    }

    try:
        request = urllib.request.Request(
            f"{soar_url}/api/playbooks/execute",
            data=json.dumps(soar_request).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "X-API-Key": soar_api_key
            },
            method="POST"
        )

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))

        return {
            "data": {
                "soar_playbook_triggered": True,
                "playbook_name": soar_playbook,
                "execution_id": result.get("execution_id")
            }
        }

    except Exception as e:
        return {"error": f"SOAR integration failed: {str(e)}"}
```

### Notification Services

```python
def playbook(sdk, data):
    """Send notifications via multiple channels."""

    if not sdk:
        return {"error": "API credentials required"}

    severity = data.get("severity", "medium")
    message = data.get("message", "Security alert")

    notifications_sent = []

    # Determine notification channels based on severity
    if severity in ["high", "critical"]:
        # Send to PagerDuty for high severity
        try:
            # Use PagerDuty extension
            ext = limacharlie.Extension(sdk)
            ext.request("pagerduty", "trigger", {
                "severity": "critical",
                "summary": message,
                "source": "limacharlie-playbook"
            })
            notifications_sent.append("pagerduty")
        except Exception as e:
            pass

    # Always send to Slack
    try:
        slack_webhook = limacharlie.Hive(sdk, "secret").get("slack-webhook").data["secret"]

        slack_payload = {
            "text": f"[{severity.upper()}] {message}",
            "attachments": [{
                "color": "danger" if severity in ["high", "critical"] else "warning",
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in data.items()
                    if k not in ["message", "severity"]
                ]
            }]
        }

        request = urllib.request.Request(
            slack_webhook,
            data=json.dumps(slack_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        urllib.request.urlopen(request)
        notifications_sent.append("slack")

    except Exception as e:
        pass

    return {
        "data": {
            "notifications_sent": notifications_sent,
            "severity": severity
        }
    }
```

## Testing Playbooks

### Development and Testing Workflow

1. **Write Playbook Locally**: Develop playbooks in your local Python environment

2. **Store in Hive**: Upload playbook to LimaCharlie Hive
   ```bash
   limacharlie hive set playbook --key my-playbook --data playbook.py --data-key python
   ```

3. **Test Interactively**: Run playbook manually with test data from web interface

4. **Test via API**: Use SDK to test with various inputs
   ```python
   import limacharlie

   lc = limacharlie.Manager()
   ext = limacharlie.Extension(lc)

   # Test with different scenarios
   test_cases = [
       {"sid": "test-sensor-1", "process_id": 1234},
       {"sid": "offline-sensor", "process_id": 5678},
       {"sid": "vip-sensor", "process_id": 9999}
   ]

   for test_data in test_cases:
       result = ext.request("ext-playbook", "run_playbook", {
           "name": "my-playbook",
           "credentials": "hive://secret/test-api-key",
           "data": test_data
       })
       print(f"Test: {test_data} -> {result}")
   ```

5. **Enable in D&R Rules**: Once tested, integrate with D&R rules for automation

### Debugging Techniques

Use return data to log execution steps:

```python
def playbook(sdk, data):
    """Playbook with debug logging."""

    debug_log = []

    debug_log.append(f"Started with data: {data}")

    try:
        if not sdk:
            debug_log.append("No SDK provided")
            return {
                "error": "API credentials required",
                "data": {"debug_log": debug_log}
            }

        debug_log.append("SDK authenticated")

        sid = data.get("sid")
        debug_log.append(f"Looking up sensor: {sid}")

        sensor = sdk.sensor(sid)
        info = sensor.getInfo()
        debug_log.append(f"Sensor found: {info.get('hostname')}")

        # ... rest of logic

        return {
            "data": {
                "success": True,
                "debug_log": debug_log
            }
        }

    except Exception as e:
        debug_log.append(f"Error: {str(e)}")
        return {
            "error": str(e),
            "data": {"debug_log": debug_log}
        }
```

## Execution Environment

### Available Packages

Playbooks run in a Python environment with these pre-installed packages:

**Python Libraries:**
- `limacharlie` - LimaCharlie SDK/CLI
- `lcextension` - LimaCharlie Extension SDK
- `flask`, `gunicorn` - Web framework
- `scikit-learn` - Machine learning
- `jinja2` - Templating
- `markdown` - Markdown processing
- `pillow` - Image processing
- `weasyprint` - PDF generation

**CLI Tools:**
- NodeJS
- `claude` - Claude Code CLI
- `codex` - Codex CLI
- `gemini` - Gemini CLI

### Limitations

- **Execution Time**: Maximum 10 minutes per playbook execution
- **State**: Environment is ephemeral - don't assume persistent state between executions
- **Packages**: Custom packages not available in self-serve mode (contact support)
- **Background Tasks**: Only code in `playbook()` function executes - no persistent background tasks
- **Container Reuse**: Instances may be reused but can be wiped at any time

### Best Practices

1. **Keep Playbooks Focused**: Each playbook should do one thing well
2. **Validate Inputs**: Always check for required parameters
3. **Handle Errors Gracefully**: Return meaningful error messages
4. **Use Secrets**: Never hardcode credentials
5. **Return Structured Data**: Use consistent return formats
6. **Log Important Steps**: Return debug info in development
7. **Test Thoroughly**: Test with edge cases before production
8. **Document Parameters**: Comment expected inputs and outputs
9. **Avoid Long Waits**: Design for async operations when possible
10. **Use Investigation IDs**: Tag sensor tasks for correlation

## Infrastructure as Code

Store playbooks in version control and deploy via Infrastructure as Code:

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
```

Deploy using the LimaCharlie CLI:
```bash
limacharlie configs push limacharlie-config.yaml
```

## Advanced Patterns

### Pattern: Incident Timeline Reconstruction

```python
def playbook(sdk, data):
    """Reconstruct incident timeline from sensor telemetry."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    start_time = data.get("start_time")  # Unix timestamp
    end_time = data.get("end_time")

    # In production, use LCQL or timeline API to query events
    # This is a simplified example

    timeline = {
        "sensor": sid,
        "start": start_time,
        "end": end_time,
        "events": []
    }

    # Collect relevant events
    event_types = [
        "NEW_PROCESS",
        "NETWORK_CONNECTIONS",
        "NEW_DOCUMENT",
        "DNS_REQUEST"
    ]

    # Build timeline (simplified - production would use LCQL)
    sensor = sdk.sensor(sid)

    # Collect comprehensive history
    sensor.task("history_dump", investigationId="timeline-reconstruction")

    # In production, parse timeline and build structured output
    timeline["events"] = [
        {"type": "investigation_started", "timestamp": start_time}
    ]

    return {
        "data": {
            "timeline": timeline,
            "investigation_id": "timeline-reconstruction"
        }
    }
```

### Pattern: Automated Threat Hunting

```python
def playbook(sdk, data):
    """Hunt for threats based on new IoCs."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get latest threat intel
    threat_feed = data.get("threat_feed", [])

    hunt_results = {
        "iocs_hunted": len(threat_feed),
        "matches": [],
        "sensors_scanned": 0
    }

    # Hunt across fleet
    for sensor in sdk.sensors():
        info = sensor.getInfo()

        if not info.get("is_online"):
            continue

        hunt_results["sensors_scanned"] += 1

        for ioc in threat_feed:
            # Search based on IoC type
            if ioc.get("type") == "hash":
                sensor.task(
                    f"dir_find_hash C:\\ --hash {ioc['value']}",
                    investigationId=f"hunt-{ioc['value'][:8]}"
                )
            elif ioc.get("type") == "registry":
                sensor.task(
                    f"reg_list {ioc['value']}",
                    investigationId=f"hunt-registry"
                )

    return {
        "data": hunt_results
    }
```

### Pattern: Compliance Reporting

```python
def playbook(sdk, data):
    """Generate compliance report for organization."""

    if not sdk:
        return {"error": "API credentials required"}

    report = {
        "report_date": data.get("date"),
        "sensors": {
            "total": 0,
            "online": 0,
            "with_fim": 0,
            "isolated": 0
        },
        "detections": {
            "total": 0,
            "by_severity": {}
        },
        "compliance_status": "pass"
    }

    # Inventory sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()
        report["sensors"]["total"] += 1

        if info.get("is_online"):
            report["sensors"]["online"] += 1

        tags = info.get("tags", [])
        if "fim_enabled" in tags:
            report["sensors"]["with_fim"] += 1
        if "isolated" in tags:
            report["sensors"]["isolated"] += 1

    # Check for compliance issues
    if report["sensors"]["isolated"] > 0:
        report["compliance_status"] = "review_required"
        report["issues"] = [
            f"{report['sensors']['isolated']} sensors remain isolated"
        ]

    return {
        "data": report
    }
```

## Key Reminders

1. **Always validate inputs**: Check for required parameters and handle missing data
2. **Use secrets for credentials**: Never hardcode sensitive information
3. **Return structured data**: Use consistent return format with `data`, `error`, `detection`, `cat`
4. **Handle offline sensors**: Check sensor status before tasking
5. **Use investigation IDs**: Tag related sensor tasks for correlation
6. **Test before deploying**: Validate playbooks with test data before automation
7. **Keep executions short**: Design for 10-minute maximum execution time
8. **Don't assume persistence**: Environment is ephemeral between executions
9. **Use proper error handling**: Catch and report errors meaningfully
10. **Document your playbooks**: Comment expected inputs, outputs, and behavior

## Common Use Cases

- **Automated Incident Response**: Execute containment actions based on detections
- **Threat Intelligence Integration**: Enrich detections with external threat data
- **Custom Notifications**: Send alerts to ticketing systems, SOAR platforms, or chat apps
- **Fleet Management**: Perform batch operations across multiple sensors
- **Compliance Automation**: Generate reports and audit logs
- **Scheduled Maintenance**: Periodic security hygiene tasks
- **Investigation Orchestration**: Coordinate multi-step investigation workflows
- **External System Integration**: Connect LimaCharlie with other security tools

This skill provides comprehensive guidance for creating powerful automated response playbooks. When helping users, focus on understanding their automation goals and designing playbooks that are reliable, maintainable, and follow security best practices.
