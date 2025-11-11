# LimaCharlie Go SDK Documentation

## Overview

The LimaCharlie Go SDK provides a comprehensive client library for interacting with the LimaCharlie security platform API. This SDK enables developers to programmatically manage sensors, detection rules, artifacts, organizational configurations, real-time event streaming, and more within the LimaCharlie ecosystem.

**Repository**: [github.com/refractionPOINT/go-limacharlie](https://github.com/refractionPOINT/go-limacharlie)

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Client Initialization](#client-initialization)
- [Core Components](#core-components)
  - [Sensor Management](#sensor-management)
  - [Detection & Response Rules](#detection--response-rules)
  - [Artifacts](#artifacts)
  - [Events and Data Streaming](#events-and-data-streaming)
  - [Organization Management](#organization-management)
  - [Installation Keys](#installation-keys)
  - [Outputs](#outputs)
  - [Billing](#billing)
  - [LCQL Queries](#lcql-queries)
  - [Hive Configuration Management](#hive-configuration-management)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Firehose CLI Tool](#firehose-cli-tool)

## Installation

### Main SDK Package

```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
```

### Firehose CLI Tool

```bash
go get github.com/refractionPOINT/go-limacharlie/firehose
```

**Minimum Go Version**: 1.18 or higher

## Authentication

The SDK supports multiple authentication methods for flexible integration.

### Environment Variables

The SDK automatically loads credentials from environment variables:

```bash
export LC_OID="your-organization-id"
export LC_API_KEY="your-api-key"
export LC_ENVIRONMENT="production"  # Optional: environment name from config file
```

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Automatically loads from environment variables
client, err := limacharlie.NewClient(limacharlie.ClientOptions{}, nil)
if err != nil {
    log.Fatal(err)
}
org, err := limacharlie.NewOrganization(client)
```

### Direct API Key Authentication

```go
client, err := limacharlie.NewClient(limacharlie.ClientOptions{
    OID:    "your-organization-id",
    APIKey: "your-api-key",
}, nil)
if err != nil {
    log.Fatal(err)
}

org, err := limacharlie.NewOrganization(client)
```

### JWT Authentication

For user-based authentication or limited-scope permissions:

```go
client, err := limacharlie.NewClient(limacharlie.ClientOptions{
    OID:         "your-organization-id",
    JWT:         "your-jwt-token",
    Permissions: []string{"sensor.get", "sensor.task"}, // Optional: specific permissions
}, nil)
```

### Configuration File

Create a YAML configuration file at `~/.limacharlie` or specify with `LC_CREDS_FILE`:

```yaml
environments:
  production:
    oid: "your-production-oid"
    api_key: "your-production-api-key"

  development:
    oid: "your-dev-oid"
    api_key: "your-dev-api-key"
    uid: "your-user-id"  # Optional
```

Load configuration:

```go
// Set environment to use (defaults to first in file)
os.Setenv("LC_ENVIRONMENT", "production")

client, err := limacharlie.NewClient(limacharlie.ClientOptions{}, nil)
```

### JWT Refresh

The SDK automatically refreshes JWT tokens when they expire:

```go
// Manual JWT refresh
newJWT, err := client.RefreshJWT(24 * time.Hour) // 24-hour expiry
if err != nil {
    log.Fatal(err)
}

// Get current JWT
currentJWT := client.GetCurrentJWT()
```

## Client Initialization

### Basic Client Creation

```go
package main

import (
    "log"
    "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    // Initialize client (loads from environment or config file)
    client, err := limacharlie.NewClient(limacharlie.ClientOptions{}, nil)
    if err != nil {
        log.Fatal(err)
    }

    // Get organization handle
    org, err := limacharlie.NewOrganization(client)
    if err != nil {
        log.Fatal(err)
    }
    defer org.Close()

    // Verify authentication
    whoami, err := org.WhoAmI()
    if err != nil {
        log.Fatal(err)
    }
    log.Printf("Authenticated as: %v", whoami.Identity)
}
```

### With Custom Logger

```go
import "github.com/rs/zerolog"

logger := &limacharlie.LCLoggerZerolog{}

client, err := limacharlie.NewClient(
    limacharlie.ClientOptions{
        OID:    "your-oid",
        APIKey: "your-api-key",
    },
    logger,
)
```

### Organization from Direct Options

```go
// Create organization directly
org, err := limacharlie.NewOrganizationFromClientOptions(
    limacharlie.ClientOptions{
        OID:    "your-oid",
        APIKey: "your-api-key",
    },
    nil, // logger
)
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

for sid, sensor := range sensors {
    fmt.Printf("Sensor: %s\n", sid)
    fmt.Printf("  Hostname: %s\n", sensor.Hostname)
    fmt.Printf("  Platform: %d\n", sensor.Platform)
    fmt.Printf("  Internal IP: %s\n", sensor.InternalIP)
    fmt.Printf("  Is Isolated: %v\n", sensor.IsIsolated)
}
```

#### List Sensors with Selector

```go
// List sensors matching a selector
sensors, err := org.ListSensorsFromSelector("platform: windows AND tag: production")
if err != nil {
    log.Fatal(err)
}
```

#### List Sensors with Options

```go
// List with limit and selector
sensors, err := org.ListSensors(limacharlie.ListSensorsOptions{
    Selector: "platform: linux",
    Limit:    100,
})
```

#### Iterative Listing (Pagination)

```go
// For very large organizations, use iterative listing
continuationToken := ""
allSensors := make(map[string]*limacharlie.Sensor)

for {
    sensors, nextToken, err := org.ListSensorsFromSelectorIteratively(
        "tag: critical",
        continuationToken,
    )
    if err != nil {
        log.Fatal(err)
    }

    // Merge results
    for sid, sensor := range sensors {
        allSensors[sid] = sensor
    }

    // Check if more results
    if nextToken == "" {
        break
    }
    continuationToken = nextToken
}

fmt.Printf("Total sensors: %d\n", len(allSensors))
```

#### Getting Specific Sensor

```go
// Get sensor by SID
sensor := org.GetSensor("sensor-id-here")
if sensor.LastError != nil {
    log.Fatal(sensor.LastError)
}

fmt.Printf("Sensor %s:\n", sensor.SID)
fmt.Printf("  Hostname: %s\n", sensor.Hostname)
fmt.Printf("  Enrollment: %s\n", sensor.EnrollTS)
fmt.Printf("  Last Alive: %s\n", sensor.AliveTS)
fmt.Printf("  Kernel Available: %v\n", sensor.IsKernelAvailable)
```

#### Get Multiple Sensors

```go
sids := []string{"sid1", "sid2", "sid3"}
sensors := org.GetSensors(sids)

for sid, sensor := range sensors {
    if sensor.LastError != nil {
        log.Printf("Error getting %s: %v", sid, sensor.LastError)
        continue
    }
    fmt.Printf("Sensor: %s - %s\n", sid, sensor.Hostname)
}
```

#### Check Sensor Online Status

```go
// Check single sensor
isOnline, err := sensor.IsOnline()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Sensor is online: %v\n", isOnline)

// Check multiple sensors
sids := []string{"sid1", "sid2", "sid3"}
statuses, err := org.ActiveSensors(sids)
if err != nil {
    log.Fatal(err)
}

for sid, isOnline := range statuses {
    fmt.Printf("Sensor %s online: %v\n", sid, isOnline)
}
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
if err != nil {
    log.Fatal(err)
}

// Delete sensor
err = sensor.Delete()
if err != nil {
    log.Fatal(err)
}
```

#### Sensor Tagging

```go
// Get current tags
tags, err := sensor.GetTags()
if err != nil {
    log.Fatal(err)
}

for _, tag := range tags {
    fmt.Printf("Tag: %s (by %s at %s)\n", tag.Tag, tag.By, tag.AddedTS)
}

// Add a tag (with 1-hour TTL)
err = sensor.AddTag("incident-response", 1*time.Hour)
if err != nil {
    log.Fatal(err)
}

// Add permanent tag (0 TTL)
err = sensor.AddTag("production", 0)

// Remove a tag
err = sensor.RemoveTag("old-tag")
if err != nil {
    log.Fatal(err)
}

// Get all tags in organization
allTags, err := org.GetAllTags()

// Get sensors with specific tag
sensorMap, err := org.GetSensorsWithTag("production")
// Returns map[string][]string - map of SID to list of tags
```

#### Tasking Sensors

##### Simple Task Execution

```go
// Basic task
err := sensor.Task(`{"action": "os_processes"}`)
if err != nil {
    log.Fatal(err)
}

// Task with investigation ID
err = sensor.Task(
    `{"action": "file_get", "path": "C:\\Windows\\System32\\calc.exe"}`,
    limacharlie.TaskingOptions{
        InvestigationID: "investigation-123",
    },
)
```

##### Task with Idempotent Key

```go
// Prevent duplicate task execution
err := sensor.Task(
    `{"action": "os_version"}`,
    limacharlie.TaskingOptions{
        InvestigationID: "inv-001",
        IdempotentKey:   "unique-task-key-12345",
    },
)
```

##### SimpleRequest - Task with Synchronous Response

```go
// Enable interactive mode (creates Spout for receiving responses)
org = org.WithInvestigationID("my-investigation-id")

// Send task and wait for response
response, err := sensor.SimpleRequest(
    `{"action": "os_version"}`,
    limacharlie.SimpleRequestOptions{
        Timeout:         30 * time.Second,
        UntilCompletion: false, // Return after first response
    },
)
if err != nil {
    log.Fatal(err)
}

// Response is map[string]interface{}
if respMap, ok := response.(map[string]interface{}); ok {
    fmt.Printf("OS Version: %v\n", respMap)
}
```

##### SimpleRequest - Multiple Tasks

```go
// Send multiple tasks
tasks := []string{
    `{"action": "os_version"}`,
    `{"action": "os_processes"}`,
}

responses, err := sensor.SimpleRequest(
    tasks,
    limacharlie.SimpleRequestOptions{
        Timeout:         60 * time.Second,
        UntilCompletion: false,
    },
)

// responses is []interface{} containing all responses
if respList, ok := responses.([]interface{}); ok {
    for i, resp := range respList {
        fmt.Printf("Response %d: %v\n", i, resp)
    }
}
```

##### Request - Async Response Handling

```go
// For more control, use Request() to get FutureResults
future, err := sensor.Request(`{"action": "os_processes"}`)
if err != nil {
    log.Fatal(err)
}
defer future.Close()

// Wait for response with timeout
response, err := future.GetWithTimeout(30 * time.Second)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Response: %v\n", response)

// Or get multiple responses as they arrive
for i := 0; i < 3; i++ {
    resp, ok := future.Get()
    if !ok {
        break
    }
    fmt.Printf("Got response %d: %v\n", i, resp)
}

// Batch retrieval with timeout
newResponses := future.GetNewResponses(5 * time.Second)
for _, resp := range newResponses {
    fmt.Printf("Response: %v\n", resp)
}
```

#### Device Association

Sensors may be associated with logical devices (when multiple sensors represent the same device):

```go
sensor := org.GetSensor("sensor-id")
if sensor.Device != nil {
    fmt.Printf("Device ID: %s\n", sensor.Device.DID)
    // Device operations can be performed through sensor.Device
}
```

### Detection & Response Rules

#### Rule Structure

```go
type CoreDRRule struct {
    Name      string                 `json:"name,omitempty"`
    Namespace string                 `json:"namespace,omitempty"` // Default: "general"
    Detect    map[string]interface{} `json:"detect"`
    Response  []map[string]interface{} `json:"respond"`
    IsEnabled *bool                  `json:"is_enabled,omitempty"`
}
```

#### Adding Detection Rules

```go
// Simple detection rule
detection := map[string]interface{}{
    "event": "NEW_PROCESS",
    "op":    "and",
    "rules": []map[string]interface{}{
        {
            "op":    "contains",
            "path":  "event/FILE_PATH",
            "value": "\\Windows\\Temp\\",
        },
    },
}

response := []map[string]interface{}{
    {
        "action": "report",
        "name":   "suspicious-temp-execution",
    },
}

enabled := true
err := org.DRRuleAdd(
    "suspicious-temp-execution",
    detection,
    response,
    limacharlie.NewDRRuleOptions{
        IsEnabled: true,
        Namespace: "custom",
        IsReplace: true, // Replace if exists
        TTL:       86400, // 24 hours in seconds
    },
)
```

#### Advanced Detection Rule with Response Actions

```go
// Ransomware detection with automated response
detection := map[string]interface{}{
    "event": "FILE_CREATE",
    "op":    "and",
    "rules": []map[string]interface{}{
        {
            "op":   "matches",
            "path": "event/FILE_PATH",
            "re":   ".*\\.(locked|encrypted|enc|cry)$",
        },
        {
            "op":    "greater than",
            "path":  "event/SIZE",
            "value": 100,
        },
    },
}

response := []map[string]interface{}{
    {
        "action":   "report",
        "name":     "potential-ransomware",
        "priority": 10,
    },
    {
        "action": "task",
        "command": map[string]interface{}{
            "action": "os_kill_process",
            "pid":    "<<event/PROCESS_ID>>",
        },
    },
    {
        "action": "task",
        "command": map[string]interface{}{
            "action": "isolate_network",
        },
    },
}

enabled := true
err := org.DRRuleAdd(
    "ransomware-file-encryption",
    detection,
    response,
    limacharlie.NewDRRuleOptions{
        IsEnabled: true,
        Namespace: "threats",
        IsReplace: true,
    },
)
```

#### Listing Detection Rules

```go
// Get all rules
rules, err := org.DRRules()
if err != nil {
    log.Fatal(err)
}

for name, rule := range rules {
    fmt.Printf("Rule: %s\n", name)
    fmt.Printf("  Detect: %v\n", rule["detect"])
    fmt.Printf("  Respond: %v\n", rule["respond"])
}

// Get rules in specific namespace
rules, err = org.DRRules(limacharlie.WithNamespace("custom"))
if err != nil {
    log.Fatal(err)
}
```

#### Deleting Detection Rules

```go
// Delete rule from default namespace
err := org.DRRuleDelete("rule-name")
if err != nil {
    log.Fatal(err)
}

// Delete rule from specific namespace
err = org.DRRuleDelete("rule-name", limacharlie.WithNamespace("custom"))
```

### Artifacts

Artifacts are files or data collected from sensors for analysis.

#### Creating Artifacts from Bytes

```go
artifactData := []byte("Suspicious file content...")

err := org.CreateArtifactFromBytes(
    "suspicious-file.txt",         // name
    artifactData,                  // data
    "text/plain",                  // content type
    "artifact-12345",              // artifact ID (or "" for auto-generate)
    7,                             // retention days
    "your-ingestion-key",          // ingestion key
)
if err != nil {
    log.Fatal(err)
}
```

#### Creating Artifacts from File

```go
err := org.CreateArtifactFromFile(
    "collected-malware",           // artifact name
    "/path/to/local/file.exe",     // local file path
    "application/octet-stream",    // content type
    "",                            // auto-generate artifact ID
    30,                            // 30 days retention
    "your-ingestion-key",
)
```

#### Uploading Large Artifacts

For large files, the SDK automatically handles chunked uploads:

```go
file, err := os.Open("/path/to/large/file.bin")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

fileInfo, _ := file.Stat()

err = org.UploadArtifact(
    file,                          // io.Reader
    fileInfo.Size(),               // size
    "application/octet-stream",    // hint (content type)
    "large-memory-dump",           // source name
    "artifact-uuid",               // artifact ID
    "/path/to/large/file.bin",     // original path
    7,                             // retention days
    "your-ingestion-key",
)
```

#### Exporting Artifacts

```go
deadline := time.Now().Add(5 * time.Minute)

// Export artifact
reader, err := org.ExportArtifact("artifact-id", deadline)
if err != nil {
    log.Fatal(err)
}
defer reader.Close()

// Save to file
outFile, _ := os.Create("exported-artifact.bin")
defer outFile.Close()

io.Copy(outFile, reader)
```

#### Exporting Through Google Cloud Storage

```go
import (
    "context"
    "cloud.google.com/go/storage"
)

ctx := context.Background()
deadline := time.Now().Add(10 * time.Minute)

// Setup GCS client
gcsClient, err := storage.NewClient(ctx)
if err != nil {
    log.Fatal(err)
}

// Export artifact through GCS
reader, err := org.ExportArtifactThroughGCS(
    ctx,
    "artifact-id",
    deadline,
    "your-gcs-bucket",
    "gcs-service-account-credentials-json",
    gcsClient,
)
if err != nil {
    log.Fatal(err)
}
defer reader.Close()

// Process the data
data, _ := io.ReadAll(reader)
```

#### Artifact Collection Rules

Define rules for automatic artifact collection:

```go
// Add artifact collection rule
rule := limacharlie.ArtifactRule{
    Patterns: []string{
        "C:\\Windows\\Temp\\*.exe",
        "C:\\Users\\*\\AppData\\Local\\Temp\\*.dll",
    },
    Filters: limacharlie.ArtifactRuleFilter{
        Tags:      []string{"production"},
        Platforms: []string{"windows"},
    },
    DaysRetentions: 30,
    IsDeleteAfter:  false,
    IsIgnoreCert:   false,
}

err := org.ArtifactRuleAdd("collect-temp-executables", rule)
if err != nil {
    log.Fatal(err)
}

// List artifact rules
rules, err := org.ArtifactsRules()
if err != nil {
    log.Fatal(err)
}

for name, rule := range rules {
    fmt.Printf("Rule: %s\n", name)
    fmt.Printf("  Patterns: %v\n", rule.Patterns)
    fmt.Printf("  Retention: %d days\n", rule.DaysRetentions)
}

// Delete artifact rule
err = org.ArtifactRuleDelete("collect-temp-executables")
```

### Events and Data Streaming

The SDK provides powerful real-time event streaming through the **Spout** system.

#### Spout - Real-Time Event Streaming

Spout provides WebSocket-based streaming of events, detections, audit logs, and more:

```go
import "github.com/refractionPOINT/go-limacharlie/limacharlie"

// Create a Spout for events
spout, err := limacharlie.NewSpout(
    org,
    "event", // Type: "event", "detect", "audit", "deployment", "billing"
    limacharlie.WithInvestigationID("my-investigation"),
)
if err != nil {
    log.Fatal(err)
}

// Start receiving data
if err := spout.Start(); err != nil {
    log.Fatal(err)
}
defer spout.Shutdown()

// Process events
for {
    event, ok := <-spout.GetDataChannel()
    if !ok {
        break // Spout closed
    }

    if eventMap, ok := event.(map[string]interface{}); ok {
        fmt.Printf("Event: %v\n", eventMap)
    }
}
```

#### Spout Options

```go
// Filter by tag
spout, err := limacharlie.NewSpout(
    org,
    "event",
    limacharlie.WithTag("production"),
)

// Filter by category (for detections)
spout, err := limacharlie.NewSpout(
    org,
    "detect",
    limacharlie.WithCategory("malware"),
)

// Filter by sensor ID
spout, err := limacharlie.NewSpout(
    org,
    "event",
    limacharlie.WithSensorID("sensor-id"),
)

// Combine multiple options
spout, err := limacharlie.NewSpout(
    org,
    "detect",
    limacharlie.WithTag("critical"),
    limacharlie.WithCategory("ransomware"),
    limacharlie.WithInvestigationID("incident-2024-001"),
)

// Disable auto-reconnect
spout, err := limacharlie.NewSpout(
    org,
    "event",
    limacharlie.WithoutReconnect(),
)
```

#### Using Spout with FutureResults

The Spout system integrates with sensor tasking for request/response workflows:

```go
// Organization with investigation ID enables interactive mode
org = org.WithInvestigationID("investigation-123")

// The organization will create a shared Spout automatically
sensor := org.GetSensor("sensor-id")

// SimpleRequest uses the shared Spout internally
response, err := sensor.SimpleRequest(`{"action": "os_version"}`)

// Or use Request() for manual handling
future, err := sensor.Request(`{"action": "os_processes"}`)
if err != nil {
    log.Fatal(err)
}
defer future.Close()

response, err := future.GetWithTimeout(30 * time.Second)
```

#### Manual Spout Management for Interactive Mode

```go
org := org.WithInvestigationID("my-investigation")

// Manually enable interactive mode (creates shared Spout)
if err := org.MakeInteractive(); err != nil {
    log.Fatal(err)
}

// Now you can use SimpleRequest/Request on sensors
sensor := org.GetSensor("sensor-id")
response, err := sensor.SimpleRequest(`{"action": "os_version"}`)
```

#### Monitoring Dropped Events

```go
spout, err := limacharlie.NewSpout(org, "event")
spout.Start()

// Check dropped count
droppedCount := spout.GetDropped()
fmt.Printf("Dropped events: %d\n", droppedCount)
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
fmt.Printf("OID: %s\n", info.OID)
fmt.Printf("Sensor Version: %s\n", info.SensorVersion)
fmt.Printf("Number of Rules: %d\n", info.NumberRules)
fmt.Printf("Number of Outputs: %d\n", info.NumberOutputs)
fmt.Printf("Sensor Quota: %d\n", info.SensorQuota)
```

#### Online Sensor Count

```go
count, err := org.GetOnlineCount()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Online sensors: %d\n", count.Count)
```

#### Site Connectivity Information

```go
// Get URLs for different services
urls, err := org.GetURLs()
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Artifacts URL: %s\n", urls["artifacts"])
fmt.Printf("Replay URL: %s\n", urls["replay"])
fmt.Printf("Ingestion URL: %s\n", urls["ingestion"])

// Get full site connectivity info (URLs + certificates)
info, err := org.GetSiteConnectivityInfo()
if err != nil {
    log.Fatal(err)
}

for service, url := range info.URLs {
    fmt.Printf("%s: %s\n", service, url)
}

for service, cert := range info.Certs {
    fmt.Printf("%s cert: %s...\n", service, cert[:50])
}
```

#### Quota Management

```go
// Set organization quota
success, err := org.SetQuota(1000) // Max 1000 sensors
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Quota set: %v\n", success)
```

#### Creating Organizations

```go
// Create a new organization
newOrg, err := org.CreateOrganization(
    "us",                    // location
    "New Organization Name", // name
)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Created organization: %s\n", newOrg.Data.Oid)

// Create with template
templateYAML := `
detection:
  - name: "default-rule"
    namespace: "general"
    detect: ...
    respond: ...
`

newOrg, err = org.CreateOrganization(
    "us",
    "Templated Org",
    templateYAML,
)
```

#### Organization Deletion

```go
// Get confirmation token
token, err := org.GetDeleteConfirmationToken()
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Confirmation token: %s\n", token)

// Delete organization (DANGEROUS!)
success, err := org.DeleteOrganization(token)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Deletion successful: %v\n", success)
```

#### Group Management

```go
// Add organization to a group
success, err := org.AddToGroup("group-id")
if err != nil {
    log.Fatal(err)
}
```

#### Authorization and Permissions

```go
// Check who you are
whoami, err := org.WhoAmI()
if err != nil {
    log.Fatal(err)
}

if whoami.Identity != nil {
    fmt.Printf("Identity: %s\n", *whoami.Identity)
}
if whoami.Organizations != nil {
    fmt.Printf("Organizations: %v\n", *whoami.Organizations)
}
if whoami.Permissions != nil {
    fmt.Printf("Permissions: %v\n", *whoami.Permissions)
}

// Check specific permission
hasPermission := whoami.HasPermissionForOrg("org-id", "sensor.task")
fmt.Printf("Has sensor.task permission: %v\n", hasPermission)

// Check access to org
hasAccess := whoami.HasAccessToOrg("org-id")
fmt.Printf("Has access to org: %v\n", hasAccess)

// Authorize with required permissions
identity, perms, err := org.Authorize([]string{"sensor.get", "sensor.task"})
if err != nil {
    log.Fatal("Missing required permissions:", err)
}
fmt.Printf("Authorized as %s with %d permissions\n", identity, len(perms))
```

#### Service and Extension Requests

```go
// Generic service request
var response map[string]interface{}
err := org.ServiceRequest(
    &response,
    "logging", // service name
    limacharlie.Dict{
        "action": "list_rules",
    },
    false, // is_async
)

// Extension request
var extResponse map[string]interface{}
err = org.ExtensionRequest(
    &extResponse,
    "extension-name",
    "action-name",
    limacharlie.Dict{
        "param1": "value1",
    },
    false, // is_impersonate
)
```

### Installation Keys

Installation keys are used for enrolling new sensors.

#### List Installation Keys

```go
keys, err := org.InstallationKeys()
if err != nil {
    log.Fatal(err)
}

for _, key := range keys {
    fmt.Printf("Key ID: %s\n", key.ID)
    fmt.Printf("  Description: %s\n", key.Description)
    fmt.Printf("  Tags: %v\n", key.Tags)
    fmt.Printf("  Created: %d\n", key.CreatedAt)
    fmt.Printf("  Use Public CA: %v\n", key.UsePublicCA)
    fmt.Printf("  Key: %s\n", key.Key)
}
```

#### Get Specific Installation Key

```go
key, err := org.InstallationKey("installation-key-id")
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Key: %s\n", key.Key)
fmt.Printf("JSON Key: %s\n", key.JsonKey)
```

#### Add Installation Key

```go
key := limacharlie.InstallationKey{
    Description: "Production Servers",
    Tags:        []string{"production", "linux"},
    UsePublicCA: false, // Use LimaCharlie's certificate
}

iid, err := org.AddInstallationKey(key)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Created installation key: %s\n", iid)

// With custom ID
key.ID = "custom-key-id"
iid, err = org.AddInstallationKey(key)
```

#### Delete Installation Key

```go
err := org.DelInstallationKey("installation-key-id")
if err != nil {
    log.Fatal(err)
}
```

### Outputs

Outputs define where LimaCharlie sends events, detections, and other data. The SDK provides comprehensive output management through the `output.go` module.

#### Supported Output Modules

The SDK supports numerous output types via the `OutputTypes` struct:

- **Cloud Storage**: `s3`, `gcs`, `azure_storage_blob`
- **Messaging**: `pubsub`, `kafka`, `azure_event_hub`
- **Databases**: `bigquery`, `elastic`, `opensearch`
- **File Transfer**: `scp`, `sftp`
- **Webhooks**: `webhook`, `webhook_bulk`, `websocket`
- **Monitoring/SIEM**: `syslog`, `humio`, `datadog`
- **Orchestration**: `slack`, `smtp`, `tines`, `torq`

### Billing

The SDK provides access to billing information and invoices through the billing service.

#### Get Billing Status

```go
status, err := org.GetBillingOrgStatus()
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Past due: %v\n", status.IsPastDue)
```

#### Get Billing Details

```go
details, err := org.GetBillingOrgDetails()
if err != nil {
    log.Fatal(err)
}

// Customer info (Stripe Customer object)
if customer, ok := details.Customer["email"].(string); ok {
    fmt.Printf("Customer email: %s\n", customer)
}

// Status
if status, ok := details.Status["is_past_due"].(bool); ok {
    fmt.Printf("Is past due: %v\n", status)
}

// Upcoming invoice
if invoice := details.UpcomingInvoice; invoice != nil {
    if amount, ok := invoice["amount_due"].(float64); ok {
        fmt.Printf("Amount due: $%.2f\n", amount/100)
    }
}
```

#### Get Invoice

```go
// Get invoice URL for download
invoice, err := org.GetBillingInvoiceURL(2024, 1, "") // January 2024
if err != nil {
    log.Fatal(err)
}

if url, ok := invoice["url"].(string); ok {
    fmt.Printf("Invoice URL: %s\n", url)
}

// Get invoice as JSON
invoice, err = org.GetBillingInvoiceURL(2024, 1, "json")
if invoiceObj, ok := invoice["invoice"].(map[string]interface{}); ok {
    fmt.Printf("Invoice: %v\n", invoiceObj)
}

// Get simple JSON format
invoice, err = org.GetBillingInvoiceURL(2024, 1, "simple_json")
if lines, ok := invoice["lines"].([]interface{}); ok {
    fmt.Printf("Invoice has %d lines\n", len(lines))
}

// Get CSV format
invoice, err = org.GetBillingInvoiceURL(2024, 1, "simple_csv")
if csv, ok := invoice["csv"].(string); ok {
    fmt.Printf("CSV: %s\n", csv)
}
```

#### Get Available Plans

```go
plans, err := org.GetBillingAvailablePlans()
if err != nil {
    log.Fatal(err)
}

for _, plan := range plans {
    fmt.Printf("Plan: %s\n", plan.Name)
    fmt.Printf("  ID: %s\n", plan.ID)
    fmt.Printf("  Price: $%.2f %s\n", plan.Price, plan.Currency)
    fmt.Printf("  Description: %s\n", plan.Description)
    fmt.Printf("  Features: %v\n", plan.Features)
}
```

#### Get User Auth Requirements

```go
authReqs, err := org.GetBillingUserAuthRequirements()
if err != nil {
    log.Fatal(err)
}

if reqs, ok := authReqs.Requirements["methods"].([]interface{}); ok {
    fmt.Printf("Auth methods: %v\n", reqs)
}
```

### LCQL Queries

LCQL (LimaCharlie Query Language) allows querying historical events and detections.

#### Basic Query

```go
// Query last hour of process creation events
response, err := org.Query(limacharlie.QueryRequest{
    Query:      `-1h | * | * | event.FILE_PATH ends with ".exe"`,
    Stream:     "event",    // "event", "detect", or "audit"
    LimitEvent: 1000,
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Results: %d\n", len(response.Results))
for i, result := range response.Results {
    fmt.Printf("Result %d: %v\n", i, result)
}

// Print stats
if response.Stats != nil {
    fmt.Printf("Stats: %v\n", response.Stats)
}
```

#### Query with Context

```go
import "context"

ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
defer cancel()

response, err := org.QueryWithContext(ctx, limacharlie.QueryRequest{
    Query:  `-24h | platform: windows | event | event.COMMAND_LINE contains "powershell"`,
    Stream: "event",
})
```

#### Paginated Query

```go
// For large result sets, use pagination
response, err := org.Query(limacharlie.QueryRequest{
    Query:      `-7d | * | detect | *`,
    Stream:     "detect",
    Cursor:     "-",  // Start pagination
    LimitEvent: 500,
})

for response.Cursor != "" {
    // Process current page
    for _, result := range response.Results {
        fmt.Printf("Detection: %v\n", result)
    }

    // Get next page
    response, err = org.Query(limacharlie.QueryRequest{
        Query:  `-7d | * | detect | *`,
        Stream: "detect",
        Cursor: response.Cursor,
    })
    if err != nil {
        log.Fatal(err)
    }
}
```

#### Query Iterator

```go
// Use iterator for automatic pagination
iter, err := org.QueryAll(limacharlie.QueryRequest{
    Query:      `-30d | tag: production | event | event.EVENT_TYPE = "NEW_PROCESS"`,
    Stream:     "event",
    LimitEvent: 1000,
})
if err != nil {
    log.Fatal(err)
}

totalResults := 0
for iter.HasMore() {
    response, err := iter.Next()
    if err != nil {
        log.Fatal(err)
    }

    if response == nil {
        break
    }

    totalResults += len(response.Results)
    fmt.Printf("Page results: %d\n", len(response.Results))

    // Process results...
}

fmt.Printf("Total results: %d\n", totalResults)
```

#### Complex LCQL Queries

```go
// Multi-condition query
response, err := org.Query(limacharlie.QueryRequest{
    Query: `-1h | platform: windows AND tag: critical | event | ` +
           `(event.FILE_PATH ends with ".exe" OR event.FILE_PATH ends with ".dll") ` +
           `AND event.FILE_PATH contains "\\Temp\\"`,
    Stream:     "event",
    LimitEvent: 5000,
    LimitEval:  10000,
})

// Detection query with category filter
response, err = org.Query(limacharlie.QueryRequest{
    Query:  `-24h | * | detect | detect.cat = "malware" OR detect.cat = "ransomware"`,
    Stream: "detect",
})

// Audit log query
response, err = org.Query(limacharlie.QueryRequest{
    Query:  `-7d | * | audit | audit.action = "sensor.task"`,
    Stream: "audit",
})
```

### Hive Configuration Management

Hive is LimaCharlie's configuration management system for storing structured data.

#### Initialize Hive Client

```go
hive := limacharlie.NewHiveClient(org)
```

#### List Hive Records

```go
// List all records in a hive partition
records, err := hive.List(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
})
if err != nil {
    log.Fatal(err)
}

for key, record := range records {
    fmt.Printf("Record: %s\n", key)
    fmt.Printf("  Data: %v\n", record.Data)
    fmt.Printf("  Enabled: %v\n", record.UsrMtd.Enabled)
    fmt.Printf("  Tags: %v\n", record.UsrMtd.Tags)
    fmt.Printf("  Last Modified: %d\n", record.SysMtd.LastMod)
    fmt.Printf("  Last Author: %s\n", record.SysMtd.LastAuthor)
    fmt.Printf("  ETag: %s\n", record.SysMtd.Etag)
}
```

#### Get Specific Hive Record

```go
record, err := hive.Get(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
    Key:          "my-config-key",
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Data: %v\n", record.Data)
```

#### Add/Update Hive Record

```go
enabled := true
err := hive.Add(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
    Key:          "my-rule",
    Data: limacharlie.Dict{
        "detect": map[string]interface{}{
            "event": "NEW_PROCESS",
            "op":    "is",
            "path":  "event/FILE_PATH",
            "value": "C:\\malware.exe",
        },
        "respond": []map[string]interface{}{
            {
                "action": "report",
                "name":   "malware-detected",
            },
        },
    },
    Enabled: &enabled,
    Tags:    []string{"malware", "test"},
})
```

#### Delete Hive Record

```go
err := hive.Remove(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
    Key:          "my-rule",
})
```

#### Batch Hive Operations

```go
// Create a batch
batch := hive.NewBatch()

// Add multiple operations
enabled := true
batch.Add(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
    Key:          "rule-1",
    Data:         limacharlie.Dict{/* ... */},
    Enabled:      &enabled,
})

batch.Add(limacharlie.HiveArgs{
    HiveName:     "dr-general",
    PartitionKey: org.GetOID(),
    Key:          "rule-2",
    Data:         limacharlie.Dict{/* ... */},
    Enabled:      &enabled,
})

// Execute batch
responses, err := batch.Execute()
if err != nil {
    log.Fatal(err)
}

for i, resp := range responses {
    if resp.Error != "" {
        fmt.Printf("Operation %d failed: %s\n", i, resp.Error)
    } else {
        fmt.Printf("Operation %d succeeded: %v\n", i, resp.Data)
    }
}
```

## Data Structures

### Sensor Structure

```go
type Sensor struct {
    OID          string // Organization ID
    IID          string // Installation key ID
    SID          string // Sensor ID
    DID          string // Device ID (if associated with device)
    Platform     uint32 // OS platform code
    Architecture uint32 // CPU architecture code

    EnrollTS string // Enrollment timestamp
    AliveTS  string // Last alive timestamp

    InternalIP string // Internal IP address
    ExternalIP string // External IP address
    Hostname   string // Sensor hostname

    IsIsolated        bool // Currently isolated from network
    ShouldIsolate     bool // Should be isolated
    IsKernelAvailable bool // Kernel component available

    Organization    *Organization // Parent organization
    Device          *Device       // Associated device (if any)
    InvestigationID string        // Investigation context
}
```

### Detection Rule Structure

```go
type CoreDRRule struct {
    Name      string                   `json:"name,omitempty"`
    Namespace string                   `json:"namespace,omitempty"`
    Detect    map[string]interface{}   `json:"detect"`
    Response  []map[string]interface{} `json:"respond"`
    IsEnabled *bool                    `json:"is_enabled,omitempty"`
}
```

### Installation Key Structure

```go
type InstallationKey struct {
    CreatedAt   uint64   // Unix timestamp
    Description string   // Human-readable description
    ID          string   // Installation key ID (IID)
    Key         string   // The actual installation key
    JsonKey     string   // JSON-formatted key
    Tags        []string // Tags to auto-apply to sensors
    UsePublicCA bool     // Use public CA vs LimaCharlie CA
}
```

### Query Structures

```go
type QueryRequest struct {
    Query      string // LCQL query string
    Stream     string // "event", "detect", or "audit"
    LimitEvent int    // Max events to process
    LimitEval  int    // Max rule evaluations
    Cursor     string // Pagination cursor
}

type QueryResponse struct {
    Results []map[string]interface{} // Query results
    Cursor  string                   // Next page cursor
    Stats   map[string]interface{}   // Query statistics
}
```

## Error Handling

### Error Types

```go
// REST API errors
if err != nil {
    if strings.Contains(err.Error(), "404") {
        fmt.Println("Resource not found")
    } else if strings.Contains(err.Error(), "401") {
        fmt.Println("Authentication failed - check credentials")
    } else if strings.Contains(err.Error(), "403") {
        fmt.Println("Permission denied")
    } else if strings.Contains(err.Error(), "429") {
        fmt.Println("Rate limited - too many requests")
    } else if strings.Contains(err.Error(), "500") {
        fmt.Println("Server error")
    }
}

// Sensor-specific errors
sensor := org.GetSensor("invalid-sid")
if sensor.LastError != nil {
    log.Printf("Error getting sensor: %v", sensor.LastError)
}
```

### Retry Logic

The SDK includes automatic retry for transient failures (401, 429, 504).

## Best Practices

### 1. Authentication Security

- Store API keys in environment variables or secure vaults, never in code
- Use JWT tokens with minimal required permissions
- Rotate API keys regularly
- Never commit credentials to version control

### 2. Resource Management

- Always call `org.Close()` when done
- Use `defer spout.Shutdown()` to ensure cleanup
- Close FutureResults when done: `defer future.Close()`

### 3. Performance Optimization

- Use concurrent operations for batch processing
- Use pagination for large result sets
- Set appropriate timeouts for long-running operations
- Use selectors to filter sensors server-side

## Firehose CLI Tool

The `firehose` module provides a standalone CLI tool for streaming LimaCharlie data to local applications via TCP.

### Installation

```bash
go install github.com/refractionPOINT/go-limacharlie/firehose@latest
```

### Usage

```bash
# Basic usage (will prompt for API key)
firehose --listen_interface 0.0.0.0:4444 --data_type event --oid your-org-id

# Use environment variables for credentials
export LC_OID=your-org-id
export LC_API_KEY=your-api-key
firehose --listen_interface 0.0.0.0:4444 --data_type event --use-env

# Filter by investigation ID
firehose --listen_interface 0.0.0.0:4444 --data_type event -i investigation-id --use-env

# Filter by sensor tag
firehose --listen_interface 0.0.0.0:4444 --data_type event -t production --use-env

# Filter detections by category
firehose --listen_interface 0.0.0.0:4444 --data_type detect -c malware --use-env

# Named firehose (auto-creates Output configuration)
firehose --listen_interface 0.0.0.0:4444 --data_type event -n my-firehose --use-env
```

### Parameters

- `--listen_interface`: IP:port to listen on (required, e.g., `0.0.0.0:4444`)
- `--data_type`: Type of data to stream (required: `event`, `detect`, `audit`, `deployment`, `artifact`)
- `--oid`: Organization ID (optional, uses environment if not specified)
- `-n, --name`: Unique firehose name (optional, auto-creates Output if specified)
- `-i, --investigation-id`: Filter by investigation ID
- `-t, --tag`: Filter by sensor tag
- `-c, --category`: Filter by detection category
- `--use-env`: Use environment variables for API key instead of prompting

## Additional Resources

- **GitHub Repository**: [github.com/refractionPOINT/go-limacharlie](https://github.com/refractionPOINT/go-limacharlie)
- **API Documentation**: [api.limacharlie.io/openapi](https://api.limacharlie.io/openapi)
- **LimaCharlie Documentation**: [docs.limacharlie.io](https://docs.limacharlie.io)
- **LCQL Query Language**: [docs.limacharlie.io/docs/query-language](https://docs.limacharlie.io/docs/query-language)
- **Detection & Response Rules**: [docs.limacharlie.io/docs/detection-and-response](https://docs.limacharlie.io/docs/detection-and-response)
- **Community Support**: [community.limacharlie.io](https://community.limacharlie.io)
- **Commercial Support**: support@limacharlie.io

## License

The LimaCharlie Go SDK is licensed under the Apache License 2.0. See the LICENSE file in the repository for full details.
