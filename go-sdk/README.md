# LimaCharlie Go SDK Documentation

## Overview

The LimaCharlie Go SDK provides a comprehensive client library for interacting with the LimaCharlie security platform API. This SDK enables developers to programmatically manage sensors, detection rules, artifacts, and organizational configurations within the LimaCharlie ecosystem.

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Client Initialization](#client-initialization)
- [Core Components](#core-components)
  - [Sensor Management](#sensor-management)
  - [Detection Rules](#detection-rules)
  - [Artifacts](#artifacts)
  - [Events and Data Streaming](#events-and-data-streaming)
  - [Organization Management](#organization-management)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)
- [Advanced Features](#advanced-features)
- [Examples](#examples)

## Installation

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

For the firehose streaming client:
```bash
go get github.com/refractionPOINT/go-limacharlie/firehose
```

## Authentication

The SDK supports multiple authentication methods:

### API Key Authentication
The most common authentication method uses an Organization ID (OID) and API Key:

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Using environment variables
// Set LC_OID and LC_API_KEY environment variables
client := limacharlie.NewClient()

// Direct initialization
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "your-organization-id",
        APIKey: "your-api-key",
    },
)
```

### JWT Authentication
For user-based authentication:

```go
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID: "your-organization-id",
        JWT: "your-jwt-token",
    },
)
```

### Configuration File
Create a YAML configuration file:

```yaml
environments:
  production:
    oid: "your-production-oid"
    api_key: "your-production-api-key"
  
  development:
    oid: "your-dev-oid"
    api_key: "your-dev-api-key"
```

Load configuration:
```go
// Loads from default locations (~/.limacharlie, ./.limacharlie.yaml)
client := limacharlie.NewClient()

// Or specify environment
os.Setenv("LC_ENVIRONMENT", "production")
client := limacharlie.NewClient()
```

## Client Initialization

### Basic Client Creation

```go
package main

import (
    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    // Initialize client with environment variables
    client := limacharlie.NewClient()
    
    // Or with explicit options
    client := limacharlie.NewClientFromLoader(
        limacharlie.ClientOptions{
            OID:    "your-oid",
            APIKey: "your-api-key",
        },
    )
    
    // Get organization handle
    org := client.Organization(limacharlie.ClientOptions{
        OID: "target-organization-id",
    })
}
```

### Advanced Client Options

```go
options := limacharlie.ClientOptions{
    OID:         "organization-id",
    APIKey:      "api-key",
    UID:         "user-id",        // Optional
    JWT:         "jwt-token",       // Alternative to API key
    Permissions: []string{"sensor.get", "sensor.task"}, // Specific permissions
}

client := limacharlie.NewClientFromLoader(options)
```

## Core Components

### Sensor Management

#### Listing Sensors

```go
// Get all sensors
sensors, err := org.ListSensors()
if err != nil {
    log.Fatal(err)
}

for _, sensor := range sensors {
    fmt.Printf("Sensor: %s - %s\n", sensor.SID, sensor.Hostname)
}

// Get sensors with specific tag
taggedSensors, err := org.GetSensorsWithTag("production")
```

#### Getting Specific Sensor

```go
// Get sensor by SID (Sensor ID)
sensor, err := org.GetSensor("sensor-id-here")
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Sensor %s:\n", sensor.SID)
fmt.Printf("  Hostname: %s\n", sensor.Hostname)
fmt.Printf("  Platform: %s\n", sensor.Platform)
fmt.Printf("  Architecture: %s\n", sensor.Architecture)
fmt.Printf("  Last Seen: %v\n", sensor.LastSeen)
```

#### Sensor Actions

```go
// Isolate sensor from network
err := sensor.IsolateFromNetwork()
if err != nil {
    log.Fatal(err)
}

// Rejoin network
err = sensor.RejoinNetwork()

// Delete sensor
err = sensor.Delete()
```

#### Sensor Tagging

```go
// Get current tags
tags, err := sensor.GetTags()
if err != nil {
    log.Fatal(err)
}

// Add a tag
err = sensor.AddTag("critical-asset", 3600) // TTL in seconds (0 for permanent)

// Remove a tag
err = sensor.RemoveTag("old-tag")
```

#### Tasking Sensors

```go
// Execute a task on sensor
investigation := "investigation-id" // Optional
response, err := sensor.Task([]byte(`{
    "action": "os_processes"
}`), &investigation)

if err != nil {
    log.Fatal(err)
}

// Process response
fmt.Printf("Task response: %s\n", response)
```

### Detection Rules

#### Rule Structure

```go
type CoreDRRule struct {
    Name      string                 `json:"name"`
    Namespace string                 `json:"namespace,omitempty"`
    Detect    map[string]interface{} `json:"detect"`
    Response  []map[string]interface{} `json:"respond"`
    IsEnabled bool                   `json:"is_enabled"`
    TTL       int                    `json:"ttl,omitempty"`
}
```

#### Adding Detection Rules

```go
rule := limacharlie.CoreDRRule{
    Name: "suspicious-process",
    Namespace: "custom",
    Detect: map[string]interface{}{
        "event": "NEW_PROCESS",
        "op": "and",
        "rules": []map[string]interface{}{
            {
                "op": "is",
                "path": "event/FILE_PATH",
                "value": "C:\\Windows\\Temp\\*.exe",
            },
        },
    },
    Response: []map[string]interface{}{
        {
            "action": "report",
            "name": "suspicious-temp-execution",
        },
    },
    IsEnabled: true,
    TTL: 86400, // 24 hours
}

err := org.DRRuleAdd(rule, false) // false = don't replace if exists
```

#### Listing Detection Rules

```go
// Get all rules
rules, err := org.DRRules()
if err != nil {
    log.Fatal(err)
}

for name, rule := range rules {
    fmt.Printf("Rule: %s (Enabled: %v)\n", name, rule.IsEnabled)
}

// Get rules in specific namespace
rules, err = org.DRRulesInNamespace("custom")
```

#### Deleting Detection Rules

```go
// Delete a specific rule
err := org.DRRuleDelete("suspicious-process", "custom")
```

### Artifacts

#### Creating Artifacts

```go
// Upload from bytes
artifactID, err := org.CreateArtifactFromBytes(
    []byte("artifact content"),
    "artifact-name.txt",
    "description of artifact",
    3600, // TTL in seconds
    "text/plain", // Content type
)

// Upload from file
artifactID, err = org.CreateArtifactFromFile(
    "/path/to/file.txt",
    "artifact-name.txt",
    "file artifact",
    7200,
    "text/plain",
)
```

#### Uploading Large Artifacts

```go
// For large files, use chunked upload
file, err := os.Open("/path/to/large/file.bin")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

artifactID, err := org.UploadArtifact(
    file,
    "large-file.bin",
    "Large binary artifact",
    0, // No TTL
    "application/octet-stream",
)
```

#### Exporting Artifacts

```go
// Direct export
data, err := org.ExportArtifact("artifact-id")
if err != nil {
    log.Fatal(err)
}

// Export to Google Cloud Storage
gcsURL, err := org.ExportArtifactToGCS(
    "artifact-id",
    "gs://bucket/path/to/artifact",
)

// Export through GCS (gets temporary URL)
tempURL, err := org.ExportArtifactThroughGCS("artifact-id")
```

### Events and Data Streaming

#### Webhook Sender

```go
// Create webhook sender for real-time events
webhookSender := limacharlie.WebhookSender{
    URL: "https://your-endpoint.com/webhook",
    Headers: map[string]string{
        "Authorization": "Bearer token",
    },
    CompressData: true, // Enable gzip compression
}

// Send event
err := webhookSender.Send(eventData)
```

#### Historical Event Retrieval

```go
// Use the REST API through request method
response, err := client.Request(
    "GET",
    fmt.Sprintf("/insight/%s/%s", org.GetOID(), sensorID),
    map[string]string{
        "start": "1609459200", // Unix timestamp
        "end":   "1609545600",
        "event_type": "NEW_PROCESS",
    },
    nil,
)
```

### Organization Management

#### Organization Information

```go
// Get organization info
info, err := org.GetInfo()
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Organization: %s\n", info.Name)
fmt.Printf("Created: %v\n", info.CreatedAt)

// Get online sensor count
count, err := org.GetOnlineCount()
fmt.Printf("Online sensors: %d\n", count)
```

#### Quota Management

```go
// Set organization quota
err := org.SetQuota(map[string]interface{}{
    "max_sensors": 1000,
    "max_retention_days": 30,
})
```

#### Authorization and JWT Management

```go
// Check current authorization
authInfo, err := client.WhoAmI()
fmt.Printf("Authorized as: %s\n", authInfo.UserID)

// Get current JWT
jwt, err := client.GetCurrentJWT()

// Refresh JWT
newJWT, err := client.RefreshJWT()
```

#### Organization Deletion

```go
// Get deletion confirmation token
token, err := org.GetDeleteConfirmationToken()

// Delete organization (requires confirmation token)
err = org.DeleteOrganization(token)
```

## Data Structures

### Sensor Structure

```go
type Sensor struct {
    SID          string    `json:"sid"`           // Sensor ID
    Hostname     string    `json:"hostname"`      // Sensor hostname
    Platform     string    `json:"platform"`      // OS platform
    Architecture string    `json:"architecture"`  // CPU architecture
    LastSeen     time.Time `json:"last_seen"`     // Last activity time
    EnrollmentTime time.Time `json:"enrollment"`  // First enrollment
    Tags         []string  `json:"tags"`          // Applied tags
    IsolationStatus string `json:"isolation"`    // Network isolation status
    Organization string    `json:"oid"`           // Organization ID
}
```

### Detection Rule Components

```go
// Detection criteria structure
detect := map[string]interface{}{
    "event": "DNS_REQUEST",
    "op": "and",
    "rules": []map[string]interface{}{
        {
            "op": "contains",
            "path": "event/DOMAIN_NAME",
            "value": "malicious.com",
        },
    },
}

// Response action structure
response := []map[string]interface{}{
    {
        "action": "report",
        "name": "malicious-dns-query",
        "priority": 5,
    },
    {
        "action": "task",
        "command": map[string]interface{}{
            "action": "os_kill_process",
            "pid": "<<event/PROCESS_ID>>",
        },
    },
}
```

### Artifact Rule Structure

```go
type ArtifactRule struct {
    Name        string   `json:"name"`
    Patterns    []string `json:"patterns"`      // File patterns to match
    Platforms   []string `json:"platforms"`     // Target platforms
    Tags        []string `json:"tags"`          // Required sensor tags
    RetentionDays int    `json:"retention"`    // Artifact retention period
}
```

## Error Handling

### Error Types and Patterns

```go
// Check for specific error types
response, err := org.GetSensor("invalid-id")
if err != nil {
    // Check if it's a 404 error
    if strings.Contains(err.Error(), "404") {
        fmt.Println("Sensor not found")
    } else if strings.Contains(err.Error(), "401") {
        fmt.Println("Authentication failed")
    } else {
        // General error handling
        log.Fatal(err)
    }
}
```

### Retry Logic

```go
// The SDK includes automatic retry for transient failures
// You can implement additional retry logic:

var sensor *limacharlie.Sensor
maxRetries := 3

for i := 0; i < maxRetries; i++ {
    sensor, err = org.GetSensor(sensorID)
    if err == nil {
        break
    }
    
    if i < maxRetries-1 {
        time.Sleep(time.Second * time.Duration(i+1))
    }
}

if err != nil {
    log.Fatal("Failed after retries:", err)
}
```

### Validation

```go
// Validate UUIDs before use
import "github.com/google/uuid"

func validateOID(oid string) error {
    _, err := uuid.Parse(oid)
    if err != nil {
        return fmt.Errorf("invalid OID format: %v", err)
    }
    return nil
}

// Validate configuration
if err := validateOID(options.OID); err != nil {
    log.Fatal(err)
}
```

## Advanced Features

### Investigation Context

When tasking sensors, you can maintain investigation context:

```go
investigationID := uuid.New().String()

// Task multiple sensors with same investigation
for _, sensor := range suspiciousSensors {
    response, err := sensor.Task([]byte(`{
        "action": "os_processes"
    }`), &investigationID)
    
    if err != nil {
        log.Printf("Failed to task sensor %s: %v", sensor.SID, err)
        continue
    }
    
    // Process responses within investigation context
}
```

### Concurrent Operations

```go
// Process multiple sensors concurrently
var wg sync.WaitGroup
results := make(chan SensorResult, len(sensors))

for _, sensor := range sensors {
    wg.Add(1)
    go func(s *limacharlie.Sensor) {
        defer wg.Done()
        
        tags, err := s.GetTags()
        results <- SensorResult{
            SID: s.SID,
            Tags: tags,
            Error: err,
        }
    }(sensor)
}

wg.Wait()
close(results)

// Process results
for result := range results {
    if result.Error != nil {
        log.Printf("Error for %s: %v", result.SID, result.Error)
    } else {
        fmt.Printf("Sensor %s has tags: %v\n", result.SID, result.Tags)
    }
}
```

### Custom HTTP Client

```go
// Use custom HTTP client for advanced networking needs
httpClient := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:       10,
        IdleConnTimeout:    30 * time.Second,
        DisableCompression: false,
    },
}

// Set custom HTTP client in options
options := limacharlie.ClientOptions{
    OID:        "your-oid",
    APIKey:     "your-api-key",
    HTTPClient: httpClient,
}
```

### Logging

```go
import "github.com/rs/zerolog"

// Configure logging
logger := zerolog.New(os.Stdout).With().Timestamp().Logger()

// The SDK uses zerolog internally
// Set log level via environment
os.Setenv("LOG_LEVEL", "debug")
```

## Examples

### Complete Sensor Monitoring Example

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
    
    // Monitor sensors
    for {
        sensors, err := org.ListSensors()
        if err != nil {
            log.Printf("Error listing sensors: %v", err)
            time.Sleep(30 * time.Second)
            continue
        }
        
        offlineSensors := []string{}
        for _, sensor := range sensors {
            if time.Since(sensor.LastSeen) > 5*time.Minute {
                offlineSensors = append(offlineSensors, sensor.Hostname)
            }
        }
        
        if len(offlineSensors) > 0 {
            fmt.Printf("Offline sensors detected: %v\n", offlineSensors)
            // Send alert or take action
        }
        
        time.Sleep(60 * time.Second)
    }
}
```

### Threat Detection Rule Example

```go
package main

import (
    "log"
    
    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})
    
    // Create ransomware detection rule
    rule := limacharlie.CoreDRRule{
        Name:      "ransomware-file-encryption",
        Namespace: "threats",
        Detect: map[string]interface{}{
            "event": "FILE_CREATE",
            "op": "and",
            "rules": []map[string]interface{}{
                {
                    "op": "matches",
                    "path": "event/FILE_PATH",
                    "re": ".*\\.(locked|encrypted|enc|cry)$",
                },
                {
                    "op": "greater than",
                    "path": "event/SIZE",
                    "value": 100,
                },
            },
        },
        Response: []map[string]interface{}{
            {
                "action": "report",
                "name": "potential-ransomware-activity",
                "priority": 10,
            },
            {
                "action": "task",
                "command": map[string]interface{}{
                    "action": "os_kill_process",
                    "pid": "<<event/PROCESS_ID>>",
                },
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
    
    err := org.DRRuleAdd(rule, true)
    if err != nil {
        log.Fatal("Failed to add rule:", err)
    }
    
    fmt.Println("Ransomware detection rule added successfully")
}
```

### Artifact Collection Example

```go
package main

import (
    "fmt"
    "io/ioutil"
    "log"
    
    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func collectSuspiciousFile(org *limacharlie.Organization, sensor *limacharlie.Sensor, filePath string) {
    // Task sensor to retrieve file
    investigation := "suspicious-file-investigation"
    response, err := sensor.Task([]byte(fmt.Sprintf(`{
        "action": "file_get",
        "path": "%s"
    }`, filePath)), &investigation)
    
    if err != nil {
        log.Printf("Failed to retrieve file: %v", err)
        return
    }
    
    // Save as artifact
    artifactID, err := org.CreateArtifactFromBytes(
        response,
        fmt.Sprintf("suspicious_%s_%s", sensor.Hostname, filePath),
        fmt.Sprintf("Suspicious file from %s", sensor.Hostname),
        86400*7, // Keep for 7 days
        "application/octet-stream",
    )
    
    if err != nil {
        log.Printf("Failed to create artifact: %v", err)
        return
    }
    
    fmt.Printf("Artifact created: %s\n", artifactID)
}
```

### Batch Sensor Operations Example

```go
package main

import (
    "fmt"
    "log"
    "sync"
    
    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client := limacharlie.NewClient()
    org := client.Organization(limacharlie.ClientOptions{})
    
    // Get all Windows sensors
    sensors, _ := org.ListSensors()
    windowsSensors := []*limacharlie.Sensor{}
    
    for _, sensor := range sensors {
        if sensor.Platform == "windows" {
            windowsSensors = append(windowsSensors, sensor)
        }
    }
    
    // Apply security patch check concurrently
    var wg sync.WaitGroup
    results := make(map[string]bool)
    var mu sync.Mutex
    
    for _, sensor := range windowsSensors {
        wg.Add(1)
        go func(s *limacharlie.Sensor) {
            defer wg.Done()
            
            // Check for specific security patch
            response, err := s.Task([]byte(`{
                "action": "os_packages",
                "filter": "KB5005565"
            }`), nil)
            
            mu.Lock()
            if err == nil && len(response) > 0 {
                results[s.Hostname] = true
            } else {
                results[s.Hostname] = false
            }
            mu.Unlock()
        }(sensor)
    }
    
    wg.Wait()
    
    // Report results
    unpatched := []string{}
    for hostname, patched := range results {
        if !patched {
            unpatched = append(unpatched, hostname)
        }
    }
    
    if len(unpatched) > 0 {
        fmt.Printf("Unpatched systems: %v\n", unpatched)
        
        // Tag unpatched systems
        for _, sensor := range windowsSensors {
            for _, hostname := range unpatched {
                if sensor.Hostname == hostname {
                    sensor.AddTag("needs-patch-KB5005565", 0)
                }
            }
        }
    }
}
```

## Best Practices

### 1. Authentication Security
- Store API keys in environment variables or secure vaults
- Use JWT tokens with minimal required permissions
- Rotate API keys regularly
- Never commit credentials to version control

### 2. Error Handling
- Always check for errors from SDK methods
- Implement retry logic for transient failures
- Log errors appropriately for debugging
- Handle specific error cases (404, 401, 403, 500)

### 3. Performance Optimization
- Use concurrent operations for batch processing
- Implement caching for frequently accessed data
- Use pagination for large result sets
- Set appropriate timeouts for long-running operations

### 4. Resource Management
- Close connections properly
- Use context for cancellation
- Monitor memory usage with large datasets
- Implement rate limiting for API calls

### 5. Detection Rules
- Test rules in a non-production namespace first
- Use TTL for experimental rules
- Document rule logic and purpose
- Version control rule definitions

### 6. Sensor Management
- Tag sensors appropriately for organization
- Monitor sensor health regularly
- Implement automated response to offline sensors
- Use investigation IDs for related tasks

## Troubleshooting

### Common Issues

#### Authentication Failures
```go
// Check API key format
if len(apiKey) != 36 {
    log.Fatal("Invalid API key format")
}

// Verify organization ID
if _, err := uuid.Parse(oid); err != nil {
    log.Fatal("Invalid OID format:", err)
}
```

#### Connection Issues
```go
// Set custom timeout
client.SetTimeout(60 * time.Second)

// Check connectivity
_, err := client.WhoAmI()
if err != nil {
    log.Fatal("Cannot connect to LimaCharlie API:", err)
}
```

#### Rate Limiting
```go
// Implement exponential backoff
backoff := 1 * time.Second
for attempts := 0; attempts < 5; attempts++ {
    err := operation()
    if err == nil {
        break
    }
    
    if strings.Contains(err.Error(), "429") {
        time.Sleep(backoff)
        backoff *= 2
    } else {
        return err
    }
}
```

## API Endpoints Reference

The SDK interacts with the following main API endpoints:

- **Base URL**: `https://api.limacharlie.io`
- **Authentication**: Bearer token in Authorization header
- **Content-Type**: `application/json`

### Key Endpoints Used by SDK

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sensors/{oid}` | GET | List all sensors |
| `/sensor/{oid}/{sid}` | GET | Get specific sensor |
| `/sensor/{oid}/{sid}/task` | POST | Task a sensor |
| `/sensor/{oid}/{sid}/tag` | POST/DELETE | Manage sensor tags |
| `/rules/{oid}` | GET/POST/DELETE | Manage detection rules |
| `/artifacts/{oid}` | POST | Upload artifacts |
| `/artifacts/{oid}/{aid}` | GET | Download artifacts |
| `/orgs/{oid}` | GET/DELETE | Organization management |

## SDK Versioning

The SDK follows semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Check the latest version:
```bash
go list -m -versions github.com/refractionPOINT/go-limacharlie/limacharlie
```

Update to latest:
```bash
go get -u github.com/refractionPOINT/go-limacharlie/limacharlie
```

## Additional Resources

- **GitHub Repository**: https://github.com/refractionPOINT/go-limacharlie
- **API Documentation**: https://api.limacharlie.io/openapi
- **LimaCharlie Documentation**: https://docs.limacharlie.io
- **Support**: support@limacharlie.io

## License

The LimaCharlie Go SDK is licensed under the Apache License 2.0. See the LICENSE file in the repository for full details.