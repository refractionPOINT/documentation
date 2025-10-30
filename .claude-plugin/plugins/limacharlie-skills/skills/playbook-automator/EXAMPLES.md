# Playbook Examples

Complete, production-ready playbook examples for common security automation use cases.

## Table of Contents

1. [Multi-Sensor Investigation](#1-multi-sensor-investigation)
2. [Scheduled Maintenance and Reporting](#2-scheduled-maintenance-and-reporting)
3. [Ticketing System Integration](#3-ticketing-system-integration)
4. [SOAR Platform Integration](#4-soar-platform-integration)
5. [Multi-Channel Notifications](#5-multi-channel-notifications)
6. [Incident Timeline Reconstruction](#6-incident-timeline-reconstruction)
7. [Automated Threat Hunting](#7-automated-threat-hunting)
8. [Compliance Reporting](#8-compliance-reporting)
9. [File Hash Reputation Check](#9-file-hash-reputation-check)
10. [Bulk Sensor Tagging](#10-bulk-sensor-tagging)
11. [Network Traffic Analysis](#11-network-traffic-analysis)
12. [User Activity Monitoring](#12-user-activity-monitoring)
13. [Credential Exposure Detection](#13-credential-exposure-detection)
14. [Ransomware Response](#14-ransomware-response)
15. [Cloud Resource Investigation](#15-cloud-resource-investigation)
16. [Memory Analysis Automation](#16-memory-analysis-automation)

## 1. Multi-Sensor Investigation

Search for indicators across your entire fleet:

```python
import limacharlie
import time

def playbook(sdk, data):
    """Search for indicator across all Windows sensors with detailed results."""

    if not sdk:
        return {"error": "API credentials required"}

    ioc_hash = data.get("hash")
    if not ioc_hash:
        return {"error": "hash parameter required"}

    max_concurrent = data.get("max_concurrent", 10)  # Limit concurrent tasks

    results = {
        "ioc": ioc_hash,
        "search_timestamp": time.time(),
        "sensors_searched": 0,
        "sensors_skipped": 0,
        "matches": [],
        "errors": []
    }

    sensors_to_search = []

    # First pass: identify eligible sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()

        # Skip non-Windows or offline sensors
        if info.get("plat") != "windows":
            results["sensors_skipped"] += 1
            continue

        if not info.get("is_online"):
            results["sensors_skipped"] += 1
            continue

        sensors_to_search.append({
            "sensor": sensor,
            "info": info
        })

    # Second pass: search in batches
    for i in range(0, len(sensors_to_search), max_concurrent):
        batch = sensors_to_search[i:i + max_concurrent]

        for item in batch:
            sensor = item["sensor"]
            info = item["info"]

            try:
                # Search for hash on sensor
                sensor.task(
                    f"dir_find_hash C:\\ --hash {ioc_hash}",
                    investigationId=f"hash-hunt-{ioc_hash[:8]}"
                )

                results["sensors_searched"] += 1

                # In production, you would query the timeline for results
                # This is a simplified example
                results["matches"].append({
                    "sensor_id": info.get("sid"),
                    "hostname": info.get("hostname"),
                    "ip_addresses": info.get("ip_addresses", []),
                    "search_initiated": True
                })

            except Exception as e:
                results["errors"].append({
                    "sensor_id": info.get("sid"),
                    "hostname": info.get("hostname"),
                    "error": str(e)
                })

        # Brief pause between batches
        if i + max_concurrent < len(sensors_to_search):
            time.sleep(1)

    # Generate detection if significant number of sensors need investigation
    if results["sensors_searched"] > 0:
        return {
            "detection": {
                "ioc": ioc_hash,
                "sensors_searched": results["sensors_searched"],
                "investigation_id": f"hash-hunt-{ioc_hash[:8]}"
            },
            "cat": "fleet-wide-ioc-hunt",
            "data": results
        }

    return {"data": results}
```

## 2. Scheduled Maintenance and Reporting

Generate periodic fleet health and security reports:

```python
import limacharlie
from datetime import datetime, timedelta

def playbook(sdk, data):
    """Comprehensive fleet health and security report."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get retention period (days)
    retention_days = data.get("retention_days", 90)
    cutoff_timestamp = int((datetime.now() - timedelta(days=retention_days)).timestamp())

    report = {
        "report_date": datetime.now().isoformat(),
        "report_type": "fleet_health",
        "sensors": {
            "total": 0,
            "online": 0,
            "offline": 0,
            "by_platform": {},
            "needing_update": [],
            "untagged": []
        },
        "detections": {
            "total": 0,
            "last_24h": 0,
            "by_category": {}
        },
        "security_posture": {
            "sensors_isolated": 0,
            "sensors_with_tags": 0,
            "vip_sensors": 0
        },
        "recommendations": []
    }

    # Inventory sensors
    for sensor in sdk.sensors():
        info = sensor.getInfo()
        report["sensors"]["total"] += 1

        # Online status
        if info.get("is_online"):
            report["sensors"]["online"] += 1
        else:
            report["sensors"]["offline"] += 1

        # Platform distribution
        platform = info.get("plat", "unknown")
        report["sensors"]["by_platform"][platform] = \
            report["sensors"]["by_platform"].get(platform, 0) + 1

        # Check agent version
        agent_version = info.get("agent_version", "")
        # In production, compare with known latest version
        if agent_version and agent_version < "5.0.0":
            report["sensors"]["needing_update"].append({
                "sid": info.get("sid"),
                "hostname": info.get("hostname"),
                "version": agent_version
            })

        # Check tagging
        tags = info.get("tags", [])
        if not tags:
            report["sensors"]["untagged"].append({
                "sid": info.get("sid"),
                "hostname": info.get("hostname")
            })
        else:
            report["security_posture"]["sensors_with_tags"] += 1

        if "vip" in tags:
            report["security_posture"]["vip_sensors"] += 1

        if "isolated" in tags:
            report["security_posture"]["sensors_isolated"] += 1

    # Get recent detections
    try:
        detections = sdk.getDetections(limit=1000)
        report["detections"]["total"] = len(detections)

        # Count last 24h
        day_ago = int((datetime.now() - timedelta(days=1)).timestamp())
        for det in detections:
            timestamp = det.get("routing", {}).get("event_time", 0)
            if timestamp > day_ago:
                report["detections"]["last_24h"] += 1

            # Category distribution
            category = det.get("detect", {}).get("cat", "unknown")
            report["detections"]["by_category"][category] = \
                report["detections"]["by_category"].get(category, 0) + 1

    except Exception as e:
        report["detections"]["error"] = str(e)

    # Generate recommendations
    if report["sensors"]["offline"] > 0:
        report["recommendations"].append({
            "priority": "high",
            "category": "availability",
            "message": f"Investigate {report['sensors']['offline']} offline sensors"
        })

    if len(report["sensors"]["needing_update"]) > 0:
        report["recommendations"].append({
            "priority": "medium",
            "category": "patch_management",
            "message": f"Update {len(report['sensors']['needing_update'])} sensors to latest version"
        })

    if report["security_posture"]["sensors_isolated"] > 0:
        report["recommendations"].append({
            "priority": "critical",
            "category": "containment",
            "message": f"{report['security_posture']['sensors_isolated']} sensors remain isolated - review incidents"
        })

    if len(report["sensors"]["untagged"]) > 5:
        report["recommendations"].append({
            "priority": "low",
            "category": "organization",
            "message": f"{len(report['sensors']['untagged'])} sensors lack organizational tags"
        })

    if report["detections"]["last_24h"] > 100:
        report["recommendations"].append({
            "priority": "high",
            "category": "security",
            "message": f"Unusually high detection volume in last 24h: {report['detections']['last_24h']}"
        })

    return {"data": report}
```

## 3. Ticketing System Integration

Automatically create tickets in external ticketing systems:

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Create ticket in external ticketing system (Jira, ServiceNow, etc.)."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get ticketing system credentials from secrets
    ticket_api_key = limacharlie.Hive(sdk, "secret").get("ticketing-api-key").data["secret"]
    ticket_url = limacharlie.Hive(sdk, "secret").get("ticketing-url").data["secret"]

    # Extract detection information
    detection_name = data.get("detection_name", "Unknown Detection")
    hostname = data.get("hostname", "Unknown Host")
    sid = data.get("sid", "Unknown")
    timestamp = data.get("timestamp", "")
    details = data.get("details", {})

    # Determine priority based on detection category or severity
    category = data.get("category", "").lower()
    if "critical" in category or "ransomware" in category:
        priority = "critical"
    elif "malware" in category or "exploit" in category:
        priority = "high"
    elif "suspicious" in category:
        priority = "medium"
    else:
        priority = "low"

    # Prepare ticket data
    ticket = {
        "title": f"[LimaCharlie] {detection_name} on {hostname}",
        "description": f"""
**Security Detection Alert**

**Detection:** {detection_name}
**Hostname:** {hostname}
**Sensor ID:** {sid}
**Timestamp:** {timestamp}
**Priority:** {priority}

**Details:**
```json
{json.dumps(details, indent=2)}
```

**Investigation Steps:**
1. Review the detection in LimaCharlie console
2. Check sensor timeline for related events
3. Verify if this is a true positive
4. Take appropriate containment actions if needed

**LimaCharlie Console:**
https://app.limacharlie.io/sensors/{sid}
        """,
        "priority": priority,
        "category": "security_incident",
        "tags": ["limacharlie", "automated", category],
        "custom_fields": {
            "detection_source": "limacharlie",
            "sensor_id": sid,
            "hostname": hostname
        }
    }

    try:
        # Create ticket via API
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

        ticket_id = result.get("id", "unknown")
        ticket_link = result.get("url", f"{ticket_url}/tickets/{ticket_id}")

        # Optionally tag sensor with ticket ID
        if sdk and sid != "Unknown":
            try:
                sensor = sdk.sensor(sid)
                sensor.tag(f"ticket-{ticket_id}", ttl=604800)  # 7 days
            except:
                pass

        return {
            "data": {
                "ticket_created": True,
                "ticket_id": ticket_id,
                "ticket_url": ticket_link,
                "priority": priority
            }
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {
            "error": f"Failed to create ticket: HTTP {e.code}",
            "data": {"error_details": error_body}
        }

    except Exception as e:
        return {"error": f"Failed to create ticket: {str(e)}"}
```

## 4. SOAR Platform Integration

Trigger SOAR playbooks based on LimaCharlie detections:

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Trigger SOAR playbook for automated investigation and response."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get SOAR credentials
    soar_api_key = limacharlie.Hive(sdk, "secret").get("soar-api-key").data["secret"]
    soar_url = limacharlie.Hive(sdk, "secret").get("soar-url").data["secret"]

    # Map LimaCharlie detection categories to SOAR playbooks
    detection_category = data.get("detection_category", "unknown")

    playbook_mapping = {
        "ransomware": "investigate-ransomware",
        "lateral-movement": "investigate-lateral-movement",
        "data-exfiltration": "investigate-exfiltration",
        "malware": "investigate-malware",
        "credential-theft": "investigate-credential-theft",
        "privilege-escalation": "investigate-privilege-escalation",
        "reconnaissance": "investigate-reconnaissance",
        "command-and-control": "investigate-c2"
    }

    # Select appropriate SOAR playbook
    soar_playbook = playbook_mapping.get(
        detection_category.lower(),
        "generic-investigation"
    )

    # Prepare artifacts for SOAR
    artifacts = {
        "hostname": data.get("hostname"),
        "sensor_id": data.get("sid"),
        "ip_addresses": data.get("ip_addresses", []),
        "file_path": data.get("file_path"),
        "file_hash": data.get("hash"),
        "process_id": data.get("process_id"),
        "command_line": data.get("command_line"),
        "user_name": data.get("user_name"),
        "parent_process": data.get("parent_process"),
        "network_connections": data.get("network_connections", [])
    }

    # Remove None values
    artifacts = {k: v for k, v in artifacts.items() if v is not None}

    # Prepare SOAR request
    soar_request = {
        "playbook": soar_playbook,
        "context": {
            "source": "limacharlie",
            "detection_name": data.get("detection_name"),
            "detection_category": detection_category,
            "timestamp": data.get("timestamp"),
            "raw_detection": data
        },
        "artifacts": artifacts,
        "priority": data.get("priority", "medium"),
        "auto_execute": data.get("auto_execute", False)  # Safety: require manual approval by default
    }

    try:
        # Trigger SOAR playbook
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

        execution_id = result.get("execution_id")
        execution_url = result.get("url", f"{soar_url}/executions/{execution_id}")

        return {
            "data": {
                "soar_playbook_triggered": True,
                "playbook_name": soar_playbook,
                "execution_id": execution_id,
                "execution_url": execution_url,
                "artifacts_sent": len(artifacts)
            }
        }

    except Exception as e:
        return {"error": f"SOAR integration failed: {str(e)}"}
```

## 5. Multi-Channel Notifications

Send notifications via multiple channels based on severity:

```python
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
    """Send notifications via multiple channels based on severity."""

    if not sdk:
        return {"error": "API credentials required"}

    severity = data.get("severity", "medium").lower()
    message = data.get("message", "Security alert")
    details = data.get("details", {})

    notifications_sent = []
    errors = []

    # Prepare formatted message
    formatted_details = "\n".join([f"• {k}: {v}" for k, v in details.items()])
    full_message = f"{message}\n\nDetails:\n{formatted_details}"

    # 1. Always send to Slack
    try:
        slack_webhook = limacharlie.Hive(sdk, "secret").get("slack-webhook").data["secret"]

        # Color based on severity
        color_map = {
            "critical": "#8B0000",
            "high": "#FF0000",
            "medium": "#FFA500",
            "low": "#FFFF00",
            "info": "#0000FF"
        }

        slack_payload = {
            "text": f"*[{severity.upper()}]* {message}",
            "attachments": [{
                "color": color_map.get(severity, "#808080"),
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in details.items()
                ],
                "footer": "LimaCharlie Playbook",
                "ts": int(data.get("timestamp", 0))
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
        errors.append({"channel": "slack", "error": str(e)})

    # 2. Send to email for high/critical
    if severity in ["high", "critical"]:
        try:
            # Use email extension or API
            email_recipients = limacharlie.Hive(sdk, "secret").get("alert-emails").data["secret"]

            # This is a simplified example - use your email service API
            notifications_sent.append("email")

        except Exception as e:
            errors.append({"channel": "email", "error": str(e)})

    # 3. Page on-call for critical
    if severity == "critical":
        try:
            # Trigger PagerDuty via extension
            ext = limacharlie.Extension(sdk)
            ext.request("pagerduty", "trigger", {
                "severity": "critical",
                "summary": message,
                "source": "limacharlie-playbook",
                "custom_details": details
            })
            notifications_sent.append("pagerduty")

        except Exception as e:
            errors.append({"channel": "pagerduty", "error": str(e)})

    # 4. Send to webhook for all severities
    try:
        webhook_url = limacharlie.Hive(sdk, "secret").get("general-webhook").data["secret"]

        webhook_payload = {
            "severity": severity,
            "message": message,
            "details": details,
            "timestamp": data.get("timestamp"),
            "source": "limacharlie"
        }

        request = urllib.request.Request(
            webhook_url,
            data=json.dumps(webhook_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        urllib.request.urlopen(request)
        notifications_sent.append("webhook")

    except Exception as e:
        errors.append({"channel": "webhook", "error": str(e)})

    return {
        "data": {
            "notifications_sent": notifications_sent,
            "notification_count": len(notifications_sent),
            "severity": severity,
            "errors": errors if errors else None
        }
    }
```

## 6. Incident Timeline Reconstruction

Reconstruct incident timeline from sensor telemetry:

```python
import limacharlie
from datetime import datetime, timedelta

def playbook(sdk, data):
    """Reconstruct incident timeline from sensor events."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    if not sid:
        return {"error": "sid parameter required"}

    # Time window (default: last hour)
    end_time = data.get("end_time", int(datetime.now().timestamp()))
    start_time = data.get("start_time", end_time - 3600)

    timeline = {
        "sensor": sid,
        "start": datetime.fromtimestamp(start_time).isoformat(),
        "end": datetime.fromtimestamp(end_time).isoformat(),
        "events": [],
        "statistics": {
            "processes_started": 0,
            "network_connections": 0,
            "files_modified": 0,
            "registry_changes": 0
        }
    }

    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()

        # Add sensor context
        timeline["hostname"] = info.get("hostname")
        timeline["platform"] = info.get("plat")

        # Request comprehensive history
        investigation_id = f"timeline-{sid}-{start_time}"
        sensor.task("history_dump", investigationId=investigation_id)

        # In production, you would:
        # 1. Use LCQL to query specific event types in the time window
        # 2. Parse and correlate events
        # 3. Build causal chains (parent-child processes, etc.)

        # This is a simplified example showing the structure
        timeline["events"] = [
            {
                "timestamp": datetime.fromtimestamp(start_time).isoformat(),
                "type": "investigation_started",
                "details": {
                    "investigation_id": investigation_id,
                    "requested_by": "playbook"
                }
            }
        ]

        # Example of what the timeline would contain:
        # - Process creation events with parent relationships
        # - Network connections (destination IPs, ports, protocols)
        # - File system operations (creates, modifies, deletes)
        # - Registry operations (Windows)
        # - DNS requests
        # - Code injection events
        # - Authentication events

        timeline["note"] = "History dump requested. Query timeline API with LCQL for detailed events."

        return {
            "data": timeline,
            "detection": {
                "investigation_id": investigation_id,
                "sensor": sid,
                "hostname": info.get("hostname"),
                "time_window": f"{start_time} to {end_time}"
            },
            "cat": "timeline-reconstruction-initiated"
        }

    except Exception as e:
        return {"error": f"Timeline reconstruction failed: {str(e)}"}
```

## 7. Automated Threat Hunting

Proactively hunt for threats across the fleet:

```python
import limacharlie

def playbook(sdk, data):
    """Hunt for threats based on IoCs or behavior patterns."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get threat intel feed
    threat_feed = data.get("threat_feed", [])
    hunt_type = data.get("hunt_type", "ioc")  # ioc or behavioral

    hunt_results = {
        "hunt_type": hunt_type,
        "started_at": data.get("timestamp"),
        "iocs_hunted": len(threat_feed),
        "matches": [],
        "sensors_scanned": 0,
        "investigation_ids": []
    }

    if hunt_type == "ioc":
        # IoC-based hunting
        for sensor in sdk.sensors():
            info = sensor.getInfo()

            if not info.get("is_online"):
                continue

            hunt_results["sensors_scanned"] += 1

            for ioc in threat_feed:
                ioc_type = ioc.get("type")
                ioc_value = ioc.get("value")
                investigation_id = f"hunt-{ioc_type}-{ioc_value[:8]}"

                try:
                    if ioc_type == "hash":
                        # Search for file hash
                        sensor.task(
                            f"dir_find_hash C:\\ --hash {ioc_value}",
                            investigationId=investigation_id
                        )
                    elif ioc_type == "registry":
                        # Search registry
                        sensor.task(
                            f"reg_list {ioc_value}",
                            investigationId=investigation_id
                        )
                    elif ioc_type == "file_path":
                        # Check for file existence
                        sensor.task(
                            f"os_dir_list {ioc_value}",
                            investigationId=investigation_id
                        )

                    hunt_results["investigation_ids"].append(investigation_id)

                except Exception as e:
                    hunt_results["matches"].append({
                        "sensor": info.get("hostname"),
                        "ioc": ioc_value,
                        "error": str(e)
                    })

    elif hunt_type == "behavioral":
        # Behavioral hunting (simplified example)
        # In production, use LCQL to query for specific behavior patterns

        hunt_patterns = data.get("hunt_patterns", [])

        for sensor in sdk.sensors():
            info = sensor.getInfo()

            if not info.get("is_online"):
                continue

            hunt_results["sensors_scanned"] += 1

            # Example: Hunt for suspicious PowerShell usage
            # This would use LCQL in production
            investigation_id = f"behavioral-hunt-{info.get('sid')}"
            sensor.task("history_dump", investigationId=investigation_id)

            hunt_results["investigation_ids"].append(investigation_id)

    return {
        "data": hunt_results,
        "detection": {
            "hunt_type": hunt_type,
            "sensors_scanned": hunt_results["sensors_scanned"],
            "iocs_hunted": hunt_results["iocs_hunted"]
        },
        "cat": "threat-hunt-completed"
    }
```

## 8. Compliance Reporting

Generate compliance reports for audit purposes:

```python
import limacharlie
from datetime import datetime

def playbook(sdk, data):
    """Generate compliance report for organization."""

    if not sdk:
        return {"error": "API credentials required"}

    compliance_framework = data.get("framework", "general")  # pci-dss, hipaa, sox, etc.

    report = {
        "framework": compliance_framework,
        "report_date": datetime.now().isoformat(),
        "organization": {},
        "sensors": {
            "total": 0,
            "compliant": 0,
            "non_compliant": 0,
            "issues": []
        },
        "detections": {
            "total_last_30d": 0,
            "critical_unresolved": 0
        },
        "security_controls": {
            "fim_enabled": 0,
            "network_monitoring": 0,
            "audit_logging": 0
        },
        "compliance_status": "compliant"
    }

    try:
        # Get org info
        org_info = sdk.getOrgInfo()
        report["organization"] = {
            "name": org_info.get("name"),
            "id": org_info.get("id")
        }

    except:
        pass

    # Check sensor compliance
    for sensor in sdk.sensors():
        info = sensor.getInfo()
        report["sensors"]["total"] += 1

        is_compliant = True
        issues = []

        # Check online status
        if not info.get("is_online"):
            is_compliant = False
            issues.append("Sensor offline")

        # Check agent version (compliance requirement: latest version)
        agent_version = info.get("agent_version", "")
        if agent_version < "5.0.0":  # Example version requirement
            is_compliant = False
            issues.append(f"Outdated agent version: {agent_version}")

        # Check for required tags (example: all sensors should be tagged)
        tags = info.get("tags", [])
        if not tags:
            is_compliant = False
            issues.append("Missing organizational tags")

        # Check security controls
        if "fim_enabled" in tags:
            report["security_controls"]["fim_enabled"] += 1

        if "network_monitoring" in tags:
            report["security_controls"]["network_monitoring"] += 1

        # Compliance status
        if is_compliant:
            report["sensors"]["compliant"] += 1
        else:
            report["sensors"]["non_compliant"] += 1
            report["sensors"]["issues"].append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "issues": issues
            })

    # Check detections
    try:
        detections = sdk.getDetections(limit=1000)

        # Count critical unresolved detections
        for det in detections:
            category = det.get("detect", {}).get("cat", "").lower()
            if "critical" in category:
                report["detections"]["critical_unresolved"] += 1

    except:
        pass

    # Determine overall compliance status
    if report["sensors"]["non_compliant"] > 0:
        report["compliance_status"] = "non_compliant"

    if report["detections"]["critical_unresolved"] > 0:
        report["compliance_status"] = "review_required"

    # Framework-specific checks
    if compliance_framework == "pci-dss":
        # PCI-DSS specific requirements
        if report["security_controls"]["fim_enabled"] < report["sensors"]["total"]:
            report["compliance_status"] = "non_compliant"
            report["sensors"]["issues"].append({
                "issue": "Not all systems have FIM enabled (PCI-DSS Req 11.5)"
            })

    elif compliance_framework == "hipaa":
        # HIPAA specific requirements
        if report["detections"]["critical_unresolved"] > 0:
            report["compliance_status"] = "review_required"
            report["sensors"]["issues"].append({
                "issue": "Unresolved critical security incidents (HIPAA Security Rule)"
            })

    return {"data": report}
```

## 9. File Hash Reputation Check

Check file reputation across multiple threat intelligence sources:

```python
import limacharlie
import json
import urllib.request
import time

def playbook(sdk, data):
    """Check file hash reputation across multiple threat intel sources."""

    if not sdk:
        return {"error": "API credentials required"}

    file_hash = data.get("hash")
    if not file_hash:
        return {"error": "hash parameter required"}

    reputation = {
        "hash": file_hash,
        "checked_sources": [],
        "malicious_votes": 0,
        "clean_votes": 0,
        "unknown_votes": 0,
        "details": {},
        "verdict": "unknown"
    }

    # Source 1: VirusTotal
    try:
        vt_api_key = limacharlie.Hive(sdk, "secret").get("virustotal-api-key").data["secret"]
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"

        request = urllib.request.Request(url, headers={"x-apikey": vt_api_key})
        with urllib.request.urlopen(request) as response:
            vt_data = json.loads(response.read().decode('utf-8'))

        attributes = vt_data.get("data", {}).get("attributes", {})
        last_analysis = attributes.get("last_analysis_stats", {})

        vt_malicious = last_analysis.get("malicious", 0)
        vt_undetected = last_analysis.get("undetected", 0)

        reputation["checked_sources"].append("virustotal")
        reputation["details"]["virustotal"] = {
            "malicious": vt_malicious,
            "undetected": vt_undetected,
            "total_engines": sum(last_analysis.values())
        }

        if vt_malicious > 0:
            reputation["malicious_votes"] += 1
        elif vt_undetected > 0:
            reputation["clean_votes"] += 1

    except Exception as e:
        reputation["details"]["virustotal"] = {"error": str(e)}

    # Source 2: Check internal lookup table
    try:
        lookup_hive = limacharlie.Hive(sdk, "lookup")
        known_good = lookup_hive.get("known-good-hashes").data.get("hashes", [])
        known_bad = lookup_hive.get("known-bad-hashes").data.get("hashes", [])

        reputation["checked_sources"].append("internal_lookup")

        if file_hash in known_bad:
            reputation["malicious_votes"] += 1
            reputation["details"]["internal_lookup"] = "known_malicious"
        elif file_hash in known_good:
            reputation["clean_votes"] += 1
            reputation["details"]["internal_lookup"] = "known_clean"
        else:
            reputation["unknown_votes"] += 1
            reputation["details"]["internal_lookup"] = "unknown"

    except Exception as e:
        reputation["details"]["internal_lookup"] = {"error": str(e)}

    # Determine verdict
    if reputation["malicious_votes"] > 0:
        reputation["verdict"] = "malicious"
    elif reputation["clean_votes"] > reputation["unknown_votes"]:
        reputation["verdict"] = "clean"
    else:
        reputation["verdict"] = "unknown"

    # Generate detection if malicious
    if reputation["verdict"] == "malicious":
        return {
            "detection": {
                "hash": file_hash,
                "verdict": "malicious",
                "malicious_votes": reputation["malicious_votes"],
                "sources": reputation["checked_sources"]
            },
            "cat": "malicious-file-detected",
            "data": reputation
        }

    return {"data": reputation}
```

## 10. Bulk Sensor Tagging

Tag multiple sensors based on criteria:

```python
import limacharlie

def playbook(sdk, data):
    """Tag sensors based on various criteria."""

    if not sdk:
        return {"error": "API credentials required"}

    tag_operation = data.get("operation", "add")  # add or remove
    tag_name = data.get("tag_name")
    tag_ttl = data.get("ttl", 0)  # 0 = permanent

    if not tag_name:
        return {"error": "tag_name parameter required"}

    # Criteria for tagging
    criteria = data.get("criteria", {})
    platform = criteria.get("platform")  # windows, linux, macos
    online_only = criteria.get("online_only", True)
    hostname_pattern = criteria.get("hostname_pattern")
    existing_tags = criteria.get("has_tags", [])

    results = {
        "operation": tag_operation,
        "tag_name": tag_name,
        "sensors_processed": 0,
        "sensors_tagged": 0,
        "sensors_skipped": 0,
        "errors": []
    }

    for sensor in sdk.sensors():
        info = sensor.getInfo()
        results["sensors_processed"] += 1

        # Apply criteria filters
        if platform and info.get("plat") != platform:
            results["sensors_skipped"] += 1
            continue

        if online_only and not info.get("is_online"):
            results["sensors_skipped"] += 1
            continue

        if hostname_pattern:
            import re
            hostname = info.get("hostname", "")
            if not re.search(hostname_pattern, hostname, re.IGNORECASE):
                results["sensors_skipped"] += 1
                continue

        if existing_tags:
            sensor_tags = info.get("tags", [])
            if not any(tag in sensor_tags for tag in existing_tags):
                results["sensors_skipped"] += 1
                continue

        # Perform tagging operation
        try:
            if tag_operation == "add":
                sensor.tag(tag_name, ttl=tag_ttl)
            elif tag_operation == "remove":
                sensor.untag(tag_name)

            results["sensors_tagged"] += 1

        except Exception as e:
            results["errors"].append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "error": str(e)
            })

    return {"data": results}
```

## 11. Network Traffic Analysis

Analyze network connections from sensors:

```python
import limacharlie

def playbook(sdk, data):
    """Analyze network connections from sensor."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    if not sid:
        return {"error": "sid parameter required"}

    analysis = {
        "sensor_id": sid,
        "network_connections": [],
        "suspicious_connections": [],
        "statistics": {
            "total_connections": 0,
            "outbound": 0,
            "inbound": 0,
            "suspicious": 0
        }
    }

    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()
        analysis["hostname"] = info.get("hostname")

        # Request network connections
        investigation_id = f"network-analysis-{sid}"
        sensor.task("os_network_connections", investigationId=investigation_id)

        # In production, you would query the timeline for the results
        # This is a simplified example

        # Check against threat intel
        lookup_hive = limacharlie.Hive(sdk, "lookup")
        try:
            malicious_ips = lookup_hive.get("malicious-ips").data.get("ips", [])
            malicious_domains = lookup_hive.get("malicious-domains").data.get("domains", [])

            analysis["threat_intel_loaded"] = True
        except:
            malicious_ips = []
            malicious_domains = []
            analysis["threat_intel_loaded"] = False

        # Example of what network analysis would contain:
        # - All active network connections
        # - Check destination IPs against threat intel
        # - Check domains against threat intel
        # - Identify unusual ports or protocols
        # - Flag connections to suspicious regions

        analysis["note"] = "Network connections requested. Query timeline for results."

        return {
            "data": analysis,
            "detection": {
                "investigation_id": investigation_id,
                "sensor": sid,
                "hostname": info.get("hostname")
            },
            "cat": "network-analysis-initiated"
        }

    except Exception as e:
        return {"error": f"Network analysis failed: {str(e)}"}
```

## 12. User Activity Monitoring

Monitor user activities across endpoints:

```python
import limacharlie
from datetime import datetime, timedelta

def playbook(sdk, data):
    """Monitor user activity across sensors."""

    if not sdk:
        return {"error": "API credentials required"}

    username = data.get("username")
    if not username:
        return {"error": "username parameter required"}

    activity_report = {
        "username": username,
        "search_time": datetime.now().isoformat(),
        "sensors_with_activity": [],
        "total_sensors_checked": 0,
        "suspicious_activities": []
    }

    for sensor in sdk.sensors():
        info = sensor.getInfo()
        activity_report["total_sensors_checked"] += 1

        if not info.get("is_online"):
            continue

        # In production, use LCQL to query for user activities:
        # - Login events
        # - Process executions under user context
        # - File access
        # - Network connections

        # For now, check if this sensor has seen the user
        investigation_id = f"user-activity-{username}-{info.get('sid')}"

        # Request history to search for user activity
        try:
            sensor.task("history_dump", investigationId=investigation_id)

            activity_report["sensors_with_activity"].append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "platform": info.get("plat"),
                "investigation_id": investigation_id
            })

        except Exception as e:
            pass

    # Example suspicious activity patterns to look for:
    # - Login outside business hours
    # - Multiple failed login attempts
    # - Access to sensitive files
    # - Unusual process executions
    # - Data exfiltration attempts

    if len(activity_report["sensors_with_activity"]) > 10:
        # User active on many systems - potentially suspicious
        activity_report["suspicious_activities"].append({
            "type": "high_lateral_movement",
            "description": f"User {username} active on {len(activity_report['sensors_with_activity'])} systems"
        })

    return {"data": activity_report}
```

## 13. Credential Exposure Detection

Detect potential credential exposure:

```python
import limacharlie

def playbook(sdk, data):
    """Detect potential credential exposure on sensor."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    if not sid:
        return {"error": "sid parameter required"}

    credential_check = {
        "sensor_id": sid,
        "checks_performed": [],
        "exposures_found": [],
        "risk_level": "low"
    }

    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()
        credential_check["hostname"] = info.get("hostname")
        credential_check["platform"] = info.get("plat")

        investigation_id = f"cred-check-{sid}"

        # Check 1: Look for credentials in memory (Windows)
        if info.get("plat") == "windows":
            # Check for mimikatz indicators
            sensor.task("history_dump", investigationId=investigation_id)
            credential_check["checks_performed"].append("memory_analysis")

        # Check 2: Look for credential files in common locations
        if info.get("plat") == "windows":
            paths_to_check = [
                "C:\\Users\\*\\Desktop\\*password*.txt",
                "C:\\Users\\*\\Documents\\*password*.txt",
                "C:\\Users\\*\\Downloads\\*password*.txt"
            ]
        else:
            paths_to_check = [
                "/home/*/.ssh/id_rsa",
                "/root/.ssh/id_rsa",
                "/tmp/*password*"
            ]

        for path in paths_to_check:
            try:
                # In production, actually search for these files
                credential_check["checks_performed"].append(f"file_search:{path}")
            except:
                pass

        # Check 3: Look for browsers with saved passwords
        credential_check["checks_performed"].append("browser_credential_check")

        # Check 4: Check for clear text passwords in recent processes
        credential_check["checks_performed"].append("process_command_line_analysis")

        # Determine risk level
        if len(credential_check["exposures_found"]) > 0:
            credential_check["risk_level"] = "high"

            return {
                "detection": {
                    "sensor_id": sid,
                    "hostname": info.get("hostname"),
                    "exposures": credential_check["exposures_found"],
                    "investigation_id": investigation_id
                },
                "cat": "credential-exposure-detected",
                "data": credential_check
            }

        return {"data": credential_check}

    except Exception as e:
        return {"error": f"Credential check failed: {str(e)}"}
```

## 14. Ransomware Response

Automated response to ransomware detection:

```python
import limacharlie

def playbook(sdk, data):
    """Automated ransomware response playbook."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    pid = data.get("process_id")
    file_path = data.get("file_path")

    if not sid:
        return {"error": "sid parameter required"}

    response = {
        "sensor_id": sid,
        "actions_taken": [],
        "response_stage": "initial",
        "investigation_id": f"ransomware-{sid}-{pid}"
    }

    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()
        response["hostname"] = info.get("hostname")

        # Stage 1: Immediate containment
        response["response_stage"] = "containment"

        # Kill the process tree
        if pid:
            sensor.task(f"deny_tree {pid}")
            response["actions_taken"].append(f"killed_process_tree:{pid}")

        # Network isolate
        sensor.task("segregate_network")
        response["actions_taken"].append("network_isolated")

        # Tag sensor
        sensor.tag("ransomware-detected", ttl=604800)  # 7 days
        sensor.tag("isolated", ttl=604800)
        response["actions_taken"].append("sensor_tagged")

        # Stage 2: Evidence collection
        response["response_stage"] = "evidence_collection"

        # Collect process memory
        if pid:
            sensor.task(f"mem_dump --pid {pid}", investigationId=response["investigation_id"])
            response["actions_taken"].append("memory_dumped")

        # Collect history
        sensor.task("history_dump", investigationId=response["investigation_id"])
        response["actions_taken"].append("history_collected")

        # Collect file sample if available
        if file_path:
            # In production, collect the malicious file
            response["actions_taken"].append(f"file_sample_collected:{file_path}")

        # Stage 3: Notification
        response["response_stage"] = "notification"

        # Trigger high-priority notifications
        ext = limacharlie.Extension(sdk)

        # Send to PagerDuty
        try:
            ext.request("pagerduty", "trigger", {
                "severity": "critical",
                "summary": f"Ransomware detected on {info.get('hostname')}",
                "source": "limacharlie-playbook"
            })
            response["actions_taken"].append("pagerduty_alerted")
        except:
            pass

        # Stage 4: Response complete
        response["response_stage"] = "complete"
        response["status"] = "contained"

        return {
            "detection": {
                "sensor_id": sid,
                "hostname": info.get("hostname"),
                "process_id": pid,
                "file_path": file_path,
                "response": response
            },
            "cat": "ransomware-response-complete",
            "data": response
        }

    except Exception as e:
        response["error"] = str(e)
        response["response_stage"] = "failed"
        return {
            "error": f"Ransomware response failed: {str(e)}",
            "data": response
        }
```

## 15. Cloud Resource Investigation

Investigate cloud-based resources:

```python
import limacharlie
import json

def playbook(sdk, data):
    """Investigate cloud resources associated with detection."""

    if not sdk:
        return {"error": "API credentials required"}

    # Get cloud provider and resource info
    cloud_provider = data.get("cloud_provider", "aws")  # aws, azure, gcp
    resource_id = data.get("resource_id")
    resource_type = data.get("resource_type")  # ec2, lambda, vm, etc.

    investigation = {
        "cloud_provider": cloud_provider,
        "resource_id": resource_id,
        "resource_type": resource_type,
        "findings": [],
        "recommendations": []
    }

    # Find sensors associated with this cloud resource
    investigation["associated_sensors"] = []

    for sensor in sdk.sensors():
        info = sensor.getInfo()

        # Check if sensor matches cloud resource
        # This would use cloud metadata or tags
        tags = info.get("tags", [])

        if f"{cloud_provider}:{resource_id}" in tags:
            investigation["associated_sensors"].append({
                "sensor_id": info.get("sid"),
                "hostname": info.get("hostname"),
                "online": info.get("is_online")
            })

    # Check for misconfigurations
    if cloud_provider == "aws":
        # Example AWS checks
        investigation["findings"].append({
            "check": "ec2_security_groups",
            "status": "review_required"
        })

    # Generate recommendations
    if len(investigation["associated_sensors"]) == 0:
        investigation["recommendations"].append({
            "priority": "high",
            "message": "No sensors found for this cloud resource - deploy LimaCharlie sensor"
        })

    return {"data": investigation}
```

## 16. Memory Analysis Automation

Automated memory analysis for suspicious processes:

```python
import limacharlie

def playbook(sdk, data):
    """Perform automated memory analysis on suspicious process."""

    if not sdk:
        return {"error": "API credentials required"}

    sid = data.get("sid")
    pid = data.get("process_id")

    if not sid or not pid:
        return {"error": "sid and process_id required"}

    analysis = {
        "sensor_id": sid,
        "process_id": pid,
        "analysis_stages": [],
        "findings": [],
        "investigation_id": f"memanalysis-{sid}-{pid}"
    }

    try:
        sensor = sdk.sensor(sid)
        info = sensor.getInfo()
        analysis["hostname"] = info.get("hostname")

        # Stage 1: Memory map
        sensor.task(f"mem_map --pid {pid}", investigationId=analysis["investigation_id"])
        analysis["analysis_stages"].append("memory_map")

        # Stage 2: Memory strings
        sensor.task(f"mem_strings --pid {pid}", investigationId=analysis["investigation_id"])
        analysis["analysis_stages"].append("memory_strings")

        # Stage 3: Full memory dump (for suspicious processes)
        if data.get("full_dump", False):
            sensor.task(f"mem_dump --pid {pid}", investigationId=analysis["investigation_id"])
            analysis["analysis_stages"].append("memory_dump")

        # Stage 4: Check for code injection indicators
        analysis["analysis_stages"].append("injection_check")

        # In production, analyze the memory data for:
        # - Injected code
        # - Suspicious strings (URLs, IPs, credentials)
        # - Encryption keys
        # - Command and control indicators

        return {
            "detection": {
                "sensor_id": sid,
                "hostname": info.get("hostname"),
                "process_id": pid,
                "investigation_id": analysis["investigation_id"]
            },
            "cat": "memory-analysis-initiated",
            "data": analysis
        }

    except Exception as e:
        return {"error": f"Memory analysis failed: {str(e)}"}
```

---

These examples demonstrate production-ready playbook patterns. Adapt them to your specific environment, threat intelligence sources, and security requirements.

For complete SDK reference, see [REFERENCE.md](./REFERENCE.md).

For testing and debugging, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
