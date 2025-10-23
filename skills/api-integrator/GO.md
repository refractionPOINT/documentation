# Go SDK Reference

Complete reference for the LimaCharlie Go SDK.

## Installation

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

**For Firehose streaming:**
```bash
go get github.com/refractionPOINT/go-limacharlie/firehose
```

---

## Authentication

### Environment Variables

```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Uses environment variables
client := limacharlie.NewClient()
```

### Direct Initialization

```go
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "your-organization-id",
        APIKey: "your-api-key",
    },
)
```

### Configuration File

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
import "os"

// Set environment
os.Setenv("LC_ENVIRONMENT", "production")
client := limacharlie.NewClient()
```

---

## Client

The client is the main entry point for the SDK.

### Initialize Client

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// From environment variables
client := limacharlie.NewClient()

// With explicit credentials
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "org-id",
        APIKey: "api-key",
    },
)
```

### Get Organization Handle

```go
// Use credentials from client
org := client.Organization(limacharlie.ClientOptions{})

// Or use different organization
org := client.Organization(limacharlie.ClientOptions{
    OID: "different-org-id",
})
```

---

## Organization

The `Organization` struct provides organization-level operations.

### Organization Information

```go
// Get organization info
info, err := org.GetInfo()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Organization: %s\n", info.Name)
fmt.Printf("Owner: %s\n", info.Owner)

// Get online sensor count
count, err := org.GetOnlineCount()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Online sensors: %d\n", count)
```

---

## Sensor Management

### List All Sensors

```go
sensors, err := org.ListSensors()
if err != nil {
    log.Fatal(err)
}

for _, sensor := range sensors {
    fmt.Printf("Sensor: %s\n", sensor.SID)
    fmt.Printf("  Hostname: %s\n", sensor.Hostname)
    fmt.Printf("  Platform: %s\n", sensor.Platform)
    fmt.Printf("  Architecture: %s\n", sensor.Architecture)
    fmt.Printf("  Last Seen: %v\n", sensor.LastSeen)
}
```

### Get Specific Sensor

```go
sensor, err := org.GetSensor("sensor-id")
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Hostname: %s\n", sensor.Hostname)
fmt.Printf("Platform: %s\n", sensor.Platform)
fmt.Printf("Internal IP: %s\n", sensor.InternalIP)
fmt.Printf("External IP: %s\n", sensor.ExternalIP)
```

### Get Sensors by Tag

```go
sensors, err := org.GetSensorsWithTag("production")
if err != nil {
    log.Fatal(err)
}

for _, sensor := range sensors {
    fmt.Printf("%s: %s\n", sensor.SID, sensor.Hostname)
}
```

---

## Sensor Operations

### Tag Management

```go
// Get tags
tags, err := sensor.GetTags()
if err != nil {
    log.Fatal(err)
}

for tagName, ttl := range tags {
    fmt.Printf("Tag: %s (TTL: %d)\n", tagName, ttl)
}

// Add tag (TTL in seconds, 0 = permanent)
err = sensor.AddTag("production", 3600)
if err != nil {
    log.Fatal(err)
}

// Add permanent tag
err = sensor.AddTag("critical", 0)

// Remove tag
err = sensor.RemoveTag("old-tag")
```

### Network Isolation

```go
// Isolate from network
err := sensor.IsolateFromNetwork()
if err != nil {
    log.Fatal(err)
}

// Rejoin network
err = sensor.RejoinNetwork()
if err != nil {
    log.Fatal(err)
}
```

### Sensor Deletion

```go
err := sensor.Delete()
if err != nil {
    log.Fatal(err)
}
```

### Tasking Sensors

```go
// Execute task
investigation := "investigation-id"
response, err := sensor.Task([]byte(`{
    "action": "os_processes"
}`), &investigation)

if err != nil {
    log.Fatal(err)
}

// Parse response
fmt.Printf("Response: %s\n", response)
```

#### Common Task Examples

```go
// OS information
response, _ := sensor.Task([]byte(`{"action": "os_info"}`), nil)

// Process list
response, _ := sensor.Task([]byte(`{"action": "os_processes"}`), nil)

// Network connections
response, _ := sensor.Task([]byte(`{"action": "netstat"}`), nil)

// File information
response, _ := sensor.Task([]byte(`{
    "action": "file_info",
    "file": "/path/to/file"
}`), nil)

// Kill process
response, _ := sensor.Task([]byte(`{
    "action": "kill",
    "pid": 1234
}`), nil)
```

---

## Detection & Response Rules

### Rule Structure

```go
type CoreDRRule struct {
    Name      string                   // Rule name
    Namespace string                   // Rule namespace (e.g., "threats")
    Detect    map[string]interface{}   // Detection logic
    Response  []map[string]interface{} // Response actions
    IsEnabled bool                     // Whether rule is enabled
}
```

### Create Detection Rule

```go
rule := limacharlie.CoreDRRule{
    Name:      "suspicious-powershell",
    Namespace: "threats",
    Detect: map[string]interface{}{
        "event": "NEW_PROCESS",
        "op":    "and",
        "rules": []map[string]interface{}{
            {
                "op":    "contains",
                "path":  "event/FILE_PATH",
                "value": "powershell.exe",
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

// Add rule (false = don't replace if exists)
err := org.DRRuleAdd(rule, false)
if err != nil {
    log.Fatal(err)
}
```

### List Detection Rules

```go
rules, err := org.DRRules()
if err != nil {
    log.Fatal(err)
}

for name, rule := range rules {
    fmt.Printf("Rule: %s\n", name)
    fmt.Printf("  Namespace: %s\n", rule.Namespace)
    fmt.Printf("  Enabled: %v\n", rule.IsEnabled)
}
```

### Delete Detection Rule

```go
err := org.DRRuleDelete("suspicious-powershell", "threats")
if err != nil {
    log.Fatal(err)
}
```

---

## Artifact Management

### Upload Artifact from Bytes

```go
artifactID, err := org.CreateArtifactFromBytes(
    []byte("artifact content"),
    "evidence.txt",           // Name
    "Investigation evidence", // Description
    86400,                    // TTL in seconds (24 hours)
    "text/plain",             // Content type
)

if err != nil {
    log.Fatal(err)
}

fmt.Printf("Artifact ID: %s\n", artifactID)
```

### Upload Artifact from File

```go
artifactID, err := org.CreateArtifactFromFile(
    "/path/to/file.bin",
    "binary-evidence.bin",
    "Binary evidence file",
    0,                          // No expiration
    "application/octet-stream",
)

if err != nil {
    log.Fatal(err)
}
```

### Download Artifact

```go
data, err := org.ExportArtifact("artifact-id")
if err != nil {
    log.Fatal(err)
}

// Save to file
err = os.WriteFile("downloaded-artifact.bin", data, 0644)
```

---

## Complete Example: Security Scanner

```go
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

type SecurityScanner struct {
    org *limacharlie.Organization
}

func NewSecurityScanner(org *limacharlie.Organization) *SecurityScanner {
    return &SecurityScanner{org: org}
}

func (s *SecurityScanner) ScanAllSensors() {
    sensors, err := s.org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Scanning %d sensors...\n", len(sensors))

    for _, sensor := range sensors {
        // Check if sensor is online (seen in last 5 minutes)
        if time.Since(sensor.LastSeen) > 5*time.Minute {
            fmt.Printf("[OFFLINE] %s\n", sensor.Hostname)
            continue
        }

        fmt.Printf("[SCANNING] %s (%s)\n", sensor.Hostname, sensor.Platform)

        // Get process list
        response, err := sensor.Task([]byte(`{"action": "os_processes"}`), nil)
        if err != nil {
            log.Printf("  [ERROR] %v\n", err)
            continue
        }

        // In real implementation, parse response and check for suspicious processes
        fmt.Printf("  [OK] Process scan complete\n")

        // Rate limiting
        time.Sleep(1 * time.Second)
    }
}

func (s *SecurityScanner) CheckCompliance() map[string]bool {
    sensors, err := s.org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    results := make(map[string]bool)

    for _, sensor := range sensors {
        if sensor.Platform != "windows" {
            continue
        }

        // Check for Windows Defender
        response, err := sensor.Task([]byte(`{
            "action": "os_services",
            "filter": "WinDefend"
        }`), nil)

        compliant := err == nil && len(response) > 0
        results[sensor.Hostname] = compliant

        // Tag non-compliant sensors
        if !compliant {
            sensor.AddTag("non-compliant", 0)
        }
    }

    return results
}

func (s *SecurityScanner) CreateDetectionRules() error {
    // Rule 1: Detect mimikatz
    mimikatzRule := limacharlie.CoreDRRule{
        Name:      "detect-mimikatz",
        Namespace: "threats",
        Detect: map[string]interface{}{
            "event": "NEW_PROCESS",
            "op":    "contains",
            "path":  "event/FILE_PATH",
            "value": "mimikatz",
        },
        Response: []map[string]interface{}{
            {
                "action":   "report",
                "name":     "credential-theft-attempt",
                "priority": 10,
            },
            {
                "action": "task",
                "command": map[string]interface{}{
                    "action": "isolate_network",
                },
            },
        },
        IsEnabled: true,
    }

    if err := s.org.DRRuleAdd(mimikatzRule, false); err != nil {
        return err
    }

    // Rule 2: Detect ransomware file extensions
    ransomwareRule := limacharlie.CoreDRRule{
        Name:      "detect-ransomware-files",
        Namespace: "threats",
        Detect: map[string]interface{}{
            "event": "FILE_CREATE",
            "op":    "matches",
            "path":  "event/FILE_PATH",
            "re":    ".*\\.(locked|encrypted|cry)$",
        },
        Response: []map[string]interface{}{
            {
                "action":   "report",
                "name":     "ransomware-indicator",
                "priority": 10,
            },
        },
        IsEnabled: true,
    }

    if err := s.org.DRRuleAdd(ransomwareRule, false); err != nil {
        return err
    }

    fmt.Println("Detection rules created successfully")
    return nil
}

func main() {
    // Initialize client
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})

    // Create scanner
    scanner := NewSecurityScanner(org)

    // Get organization info
    info, err := org.GetInfo()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Organization: %s\n\n", info.Name)

    // Scan all sensors
    scanner.ScanAllSensors()

    // Check compliance
    fmt.Println("\nCompliance Check:")
    results := scanner.CheckCompliance()
    compliant := 0
    for hostname, isCompliant := range results {
        if isCompliant {
            compliant++
            fmt.Printf("[OK] %s\n", hostname)
        } else {
            fmt.Printf("[FAIL] %s\n", hostname)
        }
    }
    fmt.Printf("\nCompliance Rate: %.1f%%\n",
        float64(compliant)/float64(len(results))*100)

    // Create detection rules
    fmt.Println("\nCreating Detection Rules:")
    if err := scanner.CreateDetectionRules(); err != nil {
        log.Fatal(err)
    }
}
```

---

## Detection Rule Examples

### Process-based Detection

```go
rule := limacharlie.CoreDRRule{
    Name:      "suspicious-process",
    Namespace: "threats",
    Detect: map[string]interface{}{
        "event": "NEW_PROCESS",
        "op":    "or",
        "rules": []map[string]interface{}{
            {
                "op":    "contains",
                "path":  "event/FILE_PATH",
                "value": "mimikatz",
            },
            {
                "op":    "contains",
                "path":  "event/FILE_PATH",
                "value": "pwdump",
            },
        },
    },
    Response: []map[string]interface{}{
        {
            "action":   "report",
            "name":     "suspicious-tool-execution",
            "priority": 8,
        },
    },
    IsEnabled: true,
}
```

### Network-based Detection

```go
rule := limacharlie.CoreDRRule{
    Name:      "suspicious-port",
    Namespace: "network",
    Detect: map[string]interface{}{
        "event": "NETWORK_CONNECT",
        "op":    "is",
        "path":  "event/DESTINATION/PORT",
        "value": 4444,
    },
    Response: []map[string]interface{}{
        {
            "action":   "report",
            "name":     "connection-to-suspicious-port",
            "priority": 7,
        },
        {
            "action": "task",
            "command": map[string]interface{}{
                "action": "netstat",
            },
        },
    },
    IsEnabled: true,
}
```

### File-based Detection

```go
rule := limacharlie.CoreDRRule{
    Name:      "ransomware-file-extension",
    Namespace: "threats",
    Detect: map[string]interface{}{
        "event": "FILE_CREATE",
        "op":    "matches",
        "path":  "event/FILE_PATH",
        "re":    ".*\\.(locked|encrypted|cry|crypt)$",
    },
    Response: []map[string]interface{}{
        {
            "action":   "report",
            "name":     "potential-ransomware",
            "priority": 10,
        },
        {
            "action": "task",
            "command": map[string]interface{}{
                "action": "history_dump",
            },
        },
    },
    IsEnabled: true,
}
```

### Registry-based Detection (Windows)

```go
rule := limacharlie.CoreDRRule{
    Name:      "registry-persistence",
    Namespace: "persistence",
    Detect: map[string]interface{}{
        "event": "REG_KEY_CREATE",
        "op":    "contains",
        "path":  "event/REGISTRY_KEY",
        "value": "CurrentVersion\\Run",
    },
    Response: []map[string]interface{}{
        {
            "action":   "report",
            "name":     "registry-persistence-attempt",
            "priority": 6,
        },
    },
    IsEnabled: true,
}
```

---

## Advanced Examples

### Concurrent Sensor Scanning

```go
package main

import (
    "fmt"
    "log"
    "sync"
    "time"

    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func scanSensorsConcurrent(org *limacharlie.Organization) {
    sensors, err := org.ListSensors()
    if err != nil {
        log.Fatal(err)
    }

    var wg sync.WaitGroup
    results := make(chan string, len(sensors))

    // Scan sensors concurrently
    for _, sensor := range sensors {
        wg.Add(1)
        go func(s *limacharlie.Sensor) {
            defer wg.Done()

            if time.Since(s.LastSeen) > 5*time.Minute {
                results <- fmt.Sprintf("[OFFLINE] %s", s.Hostname)
                return
            }

            // Task sensor
            _, err := s.Task([]byte(`{"action": "os_processes"}`), nil)
            if err != nil {
                results <- fmt.Sprintf("[ERROR] %s: %v", s.Hostname, err)
                return
            }

            results <- fmt.Sprintf("[OK] %s", s.Hostname)
        }(sensor)
    }

    // Close results channel when all done
    go func() {
        wg.Wait()
        close(results)
    }()

    // Print results
    for result := range results {
        fmt.Println(result)
    }
}
```

### Auto-Response System

```go
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

type AutoResponder struct {
    org *limacharlie.Organization
}

func (ar *AutoResponder) RespondToThreat(sensorID string, threatType string) error {
    sensor, err := ar.org.GetSensor(sensorID)
    if err != nil {
        return err
    }

    switch threatType {
    case "ransomware":
        // Isolate immediately
        if err := sensor.IsolateFromNetwork(); err != nil {
            return err
        }

        // Collect forensics
        sensor.Task([]byte(`{"action": "history_dump"}`), nil)
        sensor.Task([]byte(`{"action": "os_processes"}`), nil)

        // Tag
        sensor.AddTag("ransomware-incident", 0)

        fmt.Printf("Ransomware response executed for %s\n", sensor.Hostname)

    case "credential-theft":
        // Collect memory
        sensor.Task([]byte(`{"action": "os_memory_dump"}`), nil)

        // Tag
        sensor.AddTag("credential-theft-attempt", 86400)

        fmt.Printf("Credential theft response executed for %s\n", sensor.Hostname)

    default:
        // Generic response
        sensor.Task([]byte(`{"action": "history_dump"}`), nil)
        sensor.AddTag("security-incident", 86400)
    }

    return nil
}
```

### Batch Tag Management

```go
func tagSensorsByPlatform(org *limacharlie.Organization) error {
    sensors, err := org.ListSensors()
    if err != nil {
        return err
    }

    platformCounts := make(map[string]int)

    for _, sensor := range sensors {
        // Tag by platform
        tag := fmt.Sprintf("platform-%s", sensor.Platform)
        if err := sensor.AddTag(tag, 0); err != nil {
            log.Printf("Failed to tag %s: %v", sensor.Hostname, err)
            continue
        }

        // Tag by architecture
        archTag := fmt.Sprintf("arch-%s", sensor.Architecture)
        sensor.AddTag(archTag, 0)

        platformCounts[sensor.Platform]++

        // Rate limiting
        time.Sleep(100 * time.Millisecond)
    }

    fmt.Println("Platform distribution:")
    for platform, count := range platformCounts {
        fmt.Printf("  %s: %d\n", platform, count)
    }

    return nil
}
```

---

## Error Handling

### Basic Error Handling

```go
sensor, err := org.GetSensor("sensor-id")
if err != nil {
    log.Printf("Failed to get sensor: %v", err)
    return
}
```

### Retry Logic

```go
func taskWithRetry(sensor *limacharlie.Sensor, task []byte, maxRetries int) ([]byte, error) {
    var response []byte
    var err error

    for i := 0; i < maxRetries; i++ {
        response, err = sensor.Task(task, nil)
        if err == nil {
            return response, nil
        }

        // Wait before retry (exponential backoff)
        wait := time.Duration(1<<uint(i)) * time.Second
        log.Printf("Attempt %d failed, retrying in %v: %v", i+1, wait, err)
        time.Sleep(wait)
    }

    return nil, fmt.Errorf("max retries exceeded: %w", err)
}
```

### Context with Timeout

```go
import "context"

func taskWithTimeout(sensor *limacharlie.Sensor, task []byte) ([]byte, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    // Create channel for result
    type result struct {
        response []byte
        err      error
    }
    resultChan := make(chan result, 1)

    // Execute in goroutine
    go func() {
        response, err := sensor.Task(task, nil)
        resultChan <- result{response, err}
    }()

    // Wait for result or timeout
    select {
    case res := <-resultChan:
        return res.response, res.err
    case <-ctx.Done():
        return nil, fmt.Errorf("task timeout: %w", ctx.Err())
    }
}
```

---

## Best Practices

### 1. Connection Reuse

```go
// Good: Reuse client and organization
client := limacharlie.NewClient()
org := client.Organization(limacharlie.ClientOptions{})

for _, sensorID := range sensorIDs {
    sensor, _ := org.GetSensor(sensorID)
    sensor.Task(task, nil)
}

// Bad: Creating new client each time
for _, sensorID := range sensorIDs {
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})
    sensor, _ := org.GetSensor(sensorID)
}
```

### 2. Error Handling

```go
// Always check errors
sensor, err := org.GetSensor(sensorID)
if err != nil {
    return fmt.Errorf("failed to get sensor: %w", err)
}
```

### 3. Rate Limiting

```go
for _, sensor := range sensors {
    sensor.Task(task, nil)
    time.Sleep(100 * time.Millisecond) // Rate limiting
}
```

### 4. Concurrent Operations

```go
// Use goroutines with proper synchronization
var wg sync.WaitGroup
for _, sensor := range sensors {
    wg.Add(1)
    go func(s *limacharlie.Sensor) {
        defer wg.Done()
        s.Task(task, nil)
    }(sensor)
}
wg.Wait()
```

---

## Additional Resources

- **GitHub**: https://github.com/refractionPOINT/go-limacharlie
- **Go Package**: https://pkg.go.dev/github.com/refractionPOINT/go-limacharlie
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
