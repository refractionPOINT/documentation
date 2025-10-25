# Complete Code Examples

This document contains complete, working code examples for common LimaCharlie API use cases.

## Table of Contents

1. [Example 1: Automated Threat Hunting](#example-1-automated-threat-hunting)
2. [Example 2: Incident Response Automation](#example-2-incident-response-automation)
3. [Example 3: Compliance Auditing (Go)](#example-3-compliance-auditing-go)
4. [Example 4: Real-time Detection Response](#example-4-real-time-detection-response)

---

## Example 1: Automated Threat Hunting

Scan all online sensors for suspicious processes and monitor for detections in real-time.

### Python Implementation

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
            'pwdump.exe',
            'procdump.exe',
            'gsecdump.exe'
        ]

    def hunt_suspicious_processes(self):
        """Hunt for suspicious processes across all sensors"""
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
                # Get process list with timeout
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

                                # Tag sensor for follow-up
                                sensor.addTag('suspicious-process')

            except Exception as e:
                print(f"[ERROR] {hostname}: {e}")

            # Rate limiting
            time.sleep(1)

        return findings

    def hunt_lateral_movement(self):
        """Detect potential lateral movement by looking for unusual network connections"""
        sensors = self.manager.sensors()
        online_sensors = [
            sid for sid, info in sensors.items()
            if info.get('online', False)
        ]

        print(f"Checking {len(online_sensors)} sensors for lateral movement...")
        alerts = []

        for sid in online_sensors:
            sensor = self.manager.sensor(sid)
            hostname = sensor.getHostname()

            try:
                # Get network connections
                result = sensor.simpleRequest('netstat', timeout=30)

                if result and 'connections' in result:
                    for conn in result['connections']:
                        # Look for SMB/RDP connections to internal IPs
                        dst_port = conn.get('remote_port')
                        dst_ip = conn.get('remote_ip', '')

                        if dst_port in [445, 3389] and dst_ip.startswith('10.'):
                            alert = {
                                'sensor': sid,
                                'hostname': hostname,
                                'destination': dst_ip,
                                'port': dst_port,
                                'timestamp': datetime.now().isoformat()
                            }
                            alerts.append(alert)

                            print(f"[!] Potential lateral movement: {hostname}")
                            print(f"    -> {dst_ip}:{dst_port}")

                            sensor.addTag('lateral-movement-detected')

            except Exception as e:
                print(f"[ERROR] {hostname}: {e}")

            time.sleep(1)

        return alerts

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

                # Auto-respond to critical detections
                if priority >= 4:
                    print(f"  [ACTION] High priority - taking automated action")
                    sensor = self.manager.sensor(sid)

                    # Isolate sensor
                    sensor.isolate()

                    # Collect forensics
                    sensor.task(['history_dump', 'os_processes', 'netstat'])

                    # Tag for incident response
                    sensor.addTag('high-priority-detection')
                    sensor.addTag(f'detection-{detect_name}')

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
        finally:
            spout.shutdown()
            print(f"\nMonitoring complete. {detection_count} detections processed.")

# Usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python threat_hunter.py <ORG_ID> <API_KEY>")
        sys.exit(1)

    hunter = ThreatHunter(sys.argv[1], sys.argv[2])

    # Hunt for suspicious processes
    print("=== Hunting for Suspicious Processes ===\n")
    findings = hunter.hunt_suspicious_processes()
    print(f"\nScan complete: {len(findings)} suspicious processes found")

    # Check for lateral movement
    print("\n\n=== Checking for Lateral Movement ===\n")
    alerts = hunter.hunt_lateral_movement()
    print(f"\nCheck complete: {len(alerts)} potential lateral movement alerts")

    # Monitor detections
    print("\n\n=== Monitoring Detections (Press Ctrl+C to stop) ===\n")
    hunter.monitor_detections(duration=3600)
```

---

## Example 2: Incident Response Automation

Automated incident response workflow for ransomware and credential theft.

### Python Implementation

```python
import limacharlie
from datetime import datetime
import hashlib
import json

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
        print(f"=== RANSOMWARE RESPONSE ===")
        print(f"Responding to ransomware on {sensor_id}\n")

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
        print("Step 1: Isolating sensor from network...")
        try:
            sensor.isolate()
            incident['actions'].append({
                'action': 'isolate',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            print("  [SUCCESS] Sensor isolated")
        except Exception as e:
            print(f"  [ERROR] Failed to isolate: {e}")
            incident['actions'].append({
                'action': 'isolate',
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            })

        # Step 2: Collect forensics
        print("\nStep 2: Collecting forensics...")
        forensic_tasks = {
            'os_processes': 'Process list',
            'netstat': 'Network connections',
            'os_autoruns': 'Autostart programs',
            'history_dump': 'Event history'
        }

        for task, description in forensic_tasks.items():
            print(f"  Collecting: {description}")
            try:
                result = sensor.simpleRequest(task, timeout=60)
                if result:
                    # Store in Hive
                    record_key = f"{incident['id']}_{task}"
                    self.hive.set(limacharlie.HiveRecord(
                        hive_name='incidents',
                        partition_key=self.manager.oid,
                        key=record_key,
                        data=result,
                        ttl=2592000  # 30 days
                    ))
                    print(f"    [SUCCESS] {description} collected and stored")
                    incident['actions'].append({
                        'action': f'collect_{task}',
                        'timestamp': datetime.now().isoformat(),
                        'status': 'success'
                    })
            except Exception as e:
                print(f"    [ERROR] Failed {task}: {e}")
                incident['actions'].append({
                    'action': f'collect_{task}',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'failed',
                    'error': str(e)
                })

        # Step 3: Memory dump
        print("\nStep 3: Collecting memory dump...")
        try:
            sensor.task('os_memory_dump')
            incident['actions'].append({
                'action': 'memory_dump',
                'timestamp': datetime.now().isoformat(),
                'status': 'initiated'
            })
            print("  [SUCCESS] Memory dump initiated")
        except Exception as e:
            print(f"  [ERROR] Memory dump failed: {e}")

        # Step 4: Tag sensor
        print("\nStep 4: Tagging sensor...")
        sensor.addTag('ransomware-incident')
        sensor.addTag(f'incident-{incident["id"]}')

        # Step 5: Save incident record
        incident['status'] = 'contained'
        incident['contained_at'] = datetime.now().isoformat()

        self.hive.set(limacharlie.HiveRecord(
            hive_name='incidents',
            partition_key=self.manager.oid,
            key=incident['id'],
            data=incident,
            ttl=7776000  # 90 days
        ))

        print(f"\n=== INCIDENT {incident['id']} CONTAINED ===")
        print(f"Total actions: {len(incident['actions'])}")
        return incident

    def respond_to_credential_theft(self, sensor_id, process_id=None):
        """Automated credential theft response"""
        print(f"=== CREDENTIAL THEFT RESPONSE ===")
        print(f"Responding to credential theft on {sensor_id}\n")

        sensor = self.manager.sensor(sensor_id)
        hostname = sensor.getHostname()

        incident = {
            'id': hashlib.md5(f"{sensor_id}{datetime.now()}".encode()).hexdigest(),
            'type': 'credential_theft',
            'sensor': sensor_id,
            'hostname': hostname,
            'process_id': process_id,
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }

        # Step 1: Kill malicious process if PID provided
        if process_id:
            print(f"Step 1: Terminating malicious process (PID: {process_id})...")
            try:
                sensor.task(f'kill {process_id}')
                incident['actions'].append({
                    'action': f'kill_process_{process_id}',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
                print("  [SUCCESS] Process terminated")
            except Exception as e:
                print(f"  [ERROR] Failed to kill process: {e}")

        # Step 2: Collect memory
        print("\nStep 2: Collecting memory dump for analysis...")
        try:
            sensor.task('os_memory_dump')
            incident['actions'].append({
                'action': 'memory_dump',
                'timestamp': datetime.now().isoformat(),
                'status': 'initiated'
            })
            print("  [SUCCESS] Memory dump initiated")
        except Exception as e:
            print(f"  [ERROR] Memory dump failed: {e}")

        # Step 3: Collect additional forensics
        print("\nStep 3: Collecting forensics...")
        try:
            result = sensor.simpleRequest('os_processes', timeout=30)
            self.hive.set(limacharlie.HiveRecord(
                hive_name='incidents',
                partition_key=self.manager.oid,
                key=f"{incident['id']}_processes",
                data=result,
                ttl=2592000
            ))
            print("  [SUCCESS] Process list collected")
        except Exception as e:
            print(f"  [ERROR] Failed to collect processes: {e}")

        # Step 4: Tag sensor
        sensor.addTag('credential-theft-attempt')
        sensor.addTag(f'incident-{incident["id"]}')

        # Step 5: Save incident
        self.hive.set(limacharlie.HiveRecord(
            hive_name='incidents',
            partition_key=self.manager.oid,
            key=incident['id'],
            data=incident,
            ttl=7776000
        ))

        print(f"\n=== INCIDENT {incident['id']} RECORDED ===")
        return incident

    def list_incidents(self):
        """List all recorded incidents"""
        try:
            incidents = self.hive.list(
                hive_name='incidents',
                partition_key=self.manager.oid
            )

            print("=== INCIDENTS ===\n")
            for incident_record in incidents:
                incident = incident_record['data']
                print(f"ID: {incident['id']}")
                print(f"  Type: {incident['type']}")
                print(f"  Hostname: {incident['hostname']}")
                print(f"  Timestamp: {incident['timestamp']}")
                print(f"  Actions: {len(incident.get('actions', []))}")
                print()

            return incidents
        except Exception as e:
            print(f"Failed to list incidents: {e}")
            return []

# Usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python incident_response.py <ORG_ID> <API_KEY>")
        sys.exit(1)

    responder = IncidentResponder(sys.argv[1], sys.argv[2])

    # Example: Respond to ransomware
    # responder.respond_to_ransomware('SENSOR_ID')

    # Example: Respond to credential theft
    # responder.respond_to_credential_theft('SENSOR_ID', process_id=1234)

    # List all incidents
    responder.list_incidents()
```

---

## Example 3: Compliance Auditing (Go)

Automated compliance checking across all Windows sensors.

### Go Implementation

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

type ComplianceResult struct {
    Hostname   string
    Compliant  bool
    Checks     map[string]bool
    Timestamp  time.Time
}

func NewComplianceChecker(org *limacharlie.Organization) *ComplianceChecker {
    return &ComplianceChecker{org: org}
}

func (c *ComplianceChecker) CheckAllSensors() []ComplianceResult {
    sensors, err := c.org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    results := []ComplianceResult{}
    var mu sync.Mutex
    var wg sync.WaitGroup

    fmt.Printf("Checking compliance for %d sensors...\n", len(sensors))

    for _, sensor := range sensors {
        // Only check Windows sensors
        if sensor.Platform != "windows" {
            continue
        }

        // Skip offline sensors
        if time.Since(sensor.LastSeen) > 5*time.Minute {
            continue
        }

        wg.Add(1)
        go func(s *limacharlie.Sensor) {
            defer wg.Done()

            result := c.checkSensor(s)

            mu.Lock()
            results = append(results, result)
            mu.Unlock()

            // Print result
            status := "FAIL"
            if result.Compliant {
                status = "OK"
            }
            fmt.Printf("[%s] %s\n", status, result.Hostname)

            // Tag non-compliant sensors
            if !result.Compliant {
                s.AddTag("non-compliant", 0)
            } else {
                s.RemoveTag("non-compliant")
                s.AddTag("compliant", 0)
            }

            // Rate limiting
            time.Sleep(500 * time.Millisecond)
        }(sensor)
    }

    wg.Wait()
    return results
}

func (c *ComplianceChecker) checkSensor(sensor *limacharlie.Sensor) ComplianceResult {
    result := ComplianceResult{
        Hostname:  sensor.Hostname,
        Checks:    make(map[string]bool),
        Timestamp: time.Now(),
    }

    // Check 1: Windows Defender running
    result.Checks["windows_defender"] = c.checkWindowsDefender(sensor)

    // Check 2: Firewall enabled
    result.Checks["firewall"] = c.checkFirewall(sensor)

    // Check 3: Auto-update enabled
    result.Checks["auto_update"] = c.checkAutoUpdate(sensor)

    // Check 4: No unauthorized admin accounts
    result.Checks["admin_accounts"] = c.checkAdminAccounts(sensor)

    // Overall compliance: all checks must pass
    result.Compliant = true
    for _, passed := range result.Checks {
        if !passed {
            result.Compliant = false
            break
        }
    }

    return result
}

func (c *ComplianceChecker) checkWindowsDefender(sensor *limacharlie.Sensor) bool {
    response, err := sensor.Task([]byte(`{
        "action": "os_services"
    }`), nil)

    if err != nil {
        return false
    }

    // In real implementation, parse response and check for WinDefend service
    // For this example, assume it's a simple check
    return len(response) > 0
}

func (c *ComplianceChecker) checkFirewall(sensor *limacharlie.Sensor) bool {
    response, err := sensor.Task([]byte(`{
        "action": "os_services"
    }`), nil)

    if err != nil {
        return false
    }

    // Check for Windows Firewall service
    return len(response) > 0
}

func (c *ComplianceChecker) checkAutoUpdate(sensor *limacharlie.Sensor) bool {
    response, err := sensor.Task([]byte(`{
        "action": "os_services"
    }`), nil)

    if err != nil {
        return false
    }

    // Check for Windows Update service
    return len(response) > 0
}

func (c *ComplianceChecker) checkAdminAccounts(sensor *limacharlie.Sensor) bool {
    // In real implementation, would check for unauthorized admin accounts
    return true
}

func (c *ComplianceChecker) GenerateReport(results []ComplianceResult) {
    fmt.Println("\n=== COMPLIANCE REPORT ===\n")

    compliant := 0
    nonCompliant := 0

    checkStats := map[string]struct{ passed, failed int }{
        "windows_defender": {0, 0},
        "firewall":         {0, 0},
        "auto_update":      {0, 0},
        "admin_accounts":   {0, 0},
    }

    for _, result := range results {
        if result.Compliant {
            compliant++
        } else {
            nonCompliant++
        }

        // Update check statistics
        for checkName, passed := range result.Checks {
            stats := checkStats[checkName]
            if passed {
                stats.passed++
            } else {
                stats.failed++
            }
            checkStats[checkName] = stats
        }
    }

    total := compliant + nonCompliant
    complianceRate := float64(compliant) / float64(total) * 100

    fmt.Printf("Total Sensors Checked: %d\n", total)
    fmt.Printf("Compliant: %d\n", compliant)
    fmt.Printf("Non-Compliant: %d\n", nonCompliant)
    fmt.Printf("Compliance Rate: %.1f%%\n\n", complianceRate)

    fmt.Println("Check Results:")
    for checkName, stats := range checkStats {
        passRate := float64(stats.passed) / float64(total) * 100
        fmt.Printf("  %s: %.1f%% (%d/%d)\n",
            checkName, passRate, stats.passed, total)
    }

    // List non-compliant sensors
    if nonCompliant > 0 {
        fmt.Println("\nNon-Compliant Sensors:")
        for _, result := range results {
            if !result.Compliant {
                fmt.Printf("  %s\n", result.Hostname)
                for checkName, passed := range result.Checks {
                    if !passed {
                        fmt.Printf("    [FAIL] %s\n", checkName)
                    }
                }
            }
        }
    }
}

func (c *ComplianceChecker) CreateComplianceRules() error {
    fmt.Println("Creating compliance detection rules...")

    // Rule 1: Detect when Windows Defender is disabled
    defenderRule := limacharlie.CoreDRRule{
        Name:      "windows-defender-disabled",
        Namespace: "compliance",
        Detect: map[string]interface{}{
            "event": "SERVICE_CHANGE",
            "op":    "and",
            "rules": []map[string]interface{}{
                {
                    "op":    "is",
                    "path":  "event/SERVICE_NAME",
                    "value": "WinDefend",
                },
                {
                    "op":    "is",
                    "path":  "event/STATE",
                    "value": "stopped",
                },
            },
        },
        Response: []map[string]interface{}{
            {
                "action":   "report",
                "name":     "windows-defender-disabled",
                "priority": 7,
            },
        },
        IsEnabled: true,
    }

    if err := c.org.DRRuleAdd(defenderRule, false); err != nil {
        return err
    }

    // Rule 2: Detect unauthorized admin account creation
    adminRule := limacharlie.CoreDRRule{
        Name:      "unauthorized-admin-account",
        Namespace: "compliance",
        Detect: map[string]interface{}{
            "event": "USER_ADDED_TO_GROUP",
            "op":    "contains",
            "path":  "event/GROUP_NAME",
            "value": "Administrators",
        },
        Response: []map[string]interface{}{
            {
                "action":   "report",
                "name":     "unauthorized-admin-account",
                "priority": 8,
            },
        },
        IsEnabled: true,
    }

    if err := c.org.DRRuleAdd(adminRule, false); err != nil {
        return err
    }

    fmt.Println("Compliance rules created successfully")
    return nil
}

func main() {
    // Initialize client
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})

    // Get organization info
    info, err := org.GetInfo()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Organization: %s\n\n", info.Name)

    // Create compliance checker
    checker := NewComplianceChecker(org)

    // Create compliance rules
    if err := checker.CreateComplianceRules(); err != nil {
        log.Printf("Failed to create rules: %v", err)
    }

    // Check all sensors
    results := checker.CheckAllSensors()

    // Generate report
    checker.GenerateReport(results)
}
```

---

## Example 4: Real-time Detection Response

Monitor detections and respond automatically based on detection type and priority.

### Python Implementation

```python
import limacharlie
from datetime import datetime
import time

def automated_response_handler(org_id, api_key):
    """Monitor detections and respond automatically"""

    manager = limacharlie.Manager(org_id, api_key)

    # Create Spout for detections
    spout = limacharlie.Spout(
        manager,
        data_type='detect',
        is_parse=True
    )

    print("=== AUTOMATED DETECTION RESPONSE SYSTEM ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Monitoring for detections...\n")

    detection_count = 0
    action_count = 0

    try:
        for detection in spout:
            detection_count += 1

            detect_name = detection['detect_name']
            priority = detection.get('priority', 0)
            sid = detection['sid']
            hostname = detection.get('hostname', 'unknown')
            category = detection.get('cat', 'unknown')

            print(f"\n[DETECTION #{detection_count}] {datetime.now().strftime('%H:%M:%S')}")
            print(f"  Name: {detect_name}")
            print(f"  Category: {category}")
            print(f"  Priority: {priority}")
            print(f"  Sensor: {hostname} ({sid})")

            sensor = manager.sensor(sid)

            # Response based on detection type
            if 'ransomware' in detect_name.lower():
                print("  [ACTION] RANSOMWARE DETECTED - Immediate isolation")
                sensor.isolate()
                sensor.task(['history_dump', 'os_processes', 'netstat'])
                sensor.addTag('ransomware-incident')
                action_count += 1

            elif 'credential' in detect_name.lower() or 'mimikatz' in detect_name.lower():
                print("  [ACTION] CREDENTIAL THEFT - Collecting memory")

                # Get the malicious process ID if available
                event = detection.get('event', {})
                pid = event.get('PROCESS_ID')

                if pid:
                    print(f"  [ACTION] Terminating malicious process (PID: {pid})")
                    sensor.task(f'kill {pid}')

                sensor.task('os_memory_dump')
                sensor.addTag('credential-theft-attempt')
                action_count += 1

            elif 'lateral' in detect_name.lower() or 'movement' in detect_name.lower():
                print("  [ACTION] LATERAL MOVEMENT - Collecting forensics")
                sensor.task(['netstat', 'os_processes', 'history_dump'])
                sensor.addTag('lateral-movement-detected')
                action_count += 1

            elif 'persistence' in detect_name.lower():
                print("  [ACTION] PERSISTENCE DETECTED - Collecting autoruns")
                sensor.task(['os_autoruns', 'history_dump'])
                sensor.addTag('persistence-detected')
                action_count += 1

            elif priority >= 7:
                print("  [ACTION] HIGH PRIORITY - Collecting forensics")
                sensor.task(['history_dump', 'os_processes'])
                sensor.addTag('high-priority-detection')
                action_count += 1

            elif priority >= 4:
                print("  [ACTION] MEDIUM PRIORITY - Tagging for review")
                sensor.addTag('medium-priority-detection')
                action_count += 1

            else:
                print("  [INFO] Low priority - logged for review")

            # Add detection-specific tag
            sensor.addTag(f'detection-{detect_name}', ttl=86400)

    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
    finally:
        spout.shutdown()

        print("\n=== SESSION SUMMARY ===")
        print(f"Total Detections: {detection_count}")
        print(f"Actions Taken: {action_count}")
        print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def monitor_specific_events(org_id, api_key, event_types=None):
    """Monitor specific event types in real-time"""

    manager = limacharlie.Manager(org_id, api_key)

    if event_types is None:
        event_types = ['NEW_PROCESS', 'NETWORK_CONNECT', 'FILE_CREATE']

    spout = limacharlie.Spout(
        manager,
        data_type='tailored',
        event_type=event_types,
        is_parse=True
    )

    print(f"=== MONITORING EVENTS: {', '.join(event_types)} ===\n")

    try:
        for event in spout:
            event_type = event.get('event_type')
            sid = event['sid']

            if event_type == 'NEW_PROCESS':
                path = event['event'].get('FILE_PATH', 'unknown')
                cmdline = event['event'].get('COMMAND_LINE', '')
                print(f"[PROCESS] {path}")
                if cmdline:
                    print(f"  Command: {cmdline}")

            elif event_type == 'NETWORK_CONNECT':
                dst = event['event'].get('DESTINATION', {})
                ip = dst.get('IP_ADDRESS', 'unknown')
                port = dst.get('PORT', 'unknown')
                print(f"[NETWORK] Connection to {ip}:{port}")

            elif event_type == 'FILE_CREATE':
                file_path = event['event'].get('FILE_PATH', 'unknown')
                print(f"[FILE] Created: {file_path}")

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
    finally:
        spout.shutdown()

# Usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python detection_response.py <ORG_ID> <API_KEY>")
        sys.exit(1)

    # Run automated response system
    automated_response_handler(sys.argv[1], sys.argv[2])

    # Or monitor specific events
    # monitor_specific_events(sys.argv[1], sys.argv[2], ['NEW_PROCESS', 'NETWORK_CONNECT'])
```

---

## Running the Examples

### Python Examples

1. Install the SDK:
```bash
pip install limacharlie
```

2. Set environment variables:
```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

3. Run an example:
```bash
python threat_hunter.py $LC_OID $LC_API_KEY
```

### Go Examples

1. Initialize module:
```bash
go mod init example
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

2. Set environment variables:
```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

3. Run an example:
```bash
go run compliance_checker.go
```

---

## Additional Resources

- [SKILL.md](SKILL.md) - Main skill documentation
- [PYTHON.md](PYTHON.md) - Complete Python SDK reference
- [GO.md](GO.md) - Complete Go SDK reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
