---
name: list-artifacts
description: List collected artifacts and forensic data from a LimaCharlie organization with optional filtering by sensor, type, and time range. Use this skill when reviewing collected evidence, finding forensic artifacts, tracking memory dumps, locating pcap files, or auditing artifact collection. Returns artifact metadata including IDs, types, sizes, and timestamps.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Artifacts

Retrieve a list of collected artifacts and forensic data from a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Review collected artifacts and forensic evidence
- Find memory dumps from specific sensors or time periods
- Locate captured network traffic (pcap files)
- Track collected files and executables
- Audit artifact collection activities
- Search for artifacts by type or sensor

Common scenarios:
- Incident response artifact collection review
- Finding evidence for security investigations
- Auditing forensic data collection
- Locating specific dumps or captures
- Reviewing artifact storage and retention
- Tracking artifact collection over time

## What This Skill Does

This skill lists artifacts collected by LimaCharlie from sensors and other sources. It calls the LimaCharlie API to retrieve artifact metadata including artifact IDs, types, collection timestamps, sensor sources, and sizes. Results can be filtered by sensor, artifact type, and time range.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

Optional parameters:
- **sid**: Sensor ID to filter artifacts (optional)
- **artifact_type**: Type of artifact to filter (optional)
  - Examples: "memory_dump", "pcap", "file", "registry"
- **start**: Start timestamp for time range filter (Unix seconds, optional)
- **end**: End timestamp for time range filter (Unix seconds, optional)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Optional: Sensor ID if filtering by sensor
3. Optional: Artifact type if filtering by type
4. Optional: Time range for temporal filtering

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/insight/[oid]/artifacts",
  query_params={
    "sid": "[sensor-id]",        # Optional
    "type": "[artifact-type]",   # Optional
    "start": [start-timestamp],  # Optional
    "end": [end-timestamp]       # Optional
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/insight/{oid}/artifacts`
- Query parameters (all optional):
  - `sid`: Filter by sensor ID
  - `type`: Filter by artifact type
  - `start`: Start timestamp (Unix seconds)
  - `end`: End timestamp (Unix seconds)
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "artifacts": [
      {
        "id": "artifact-123abc",
        "sid": "sensor-456def",
        "type": "memory_dump",
        "size": 52428800,
        "timestamp": 1640995200,
        "source": "manual_collection"
      },
      {
        "id": "artifact-789ghi",
        "sid": "sensor-456def",
        "type": "pcap",
        "size": 10485760,
        "timestamp": 1640995300,
        "source": "automatic_capture"
      }
    ],
    "total": 2
  }
}
```

**Success (200-299):**
- Response contains array of artifact objects
- Each artifact includes ID, type, size, timestamp, and source
- Artifacts sorted by timestamp (most recent first typically)
- Empty array means no artifacts match filters
- Size in bytes, timestamp in Unix seconds

**Common Errors:**
- **400 Bad Request**: Invalid parameters (malformed timestamps, invalid type)
- **403 Forbidden**: Insufficient permissions to view artifacts
- **404 Not Found**: Organization or sensor not found
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- List artifacts with readable timestamps
- Show artifact types and sizes (convert to MB/GB)
- Group by sensor or type if helpful
- Include artifact IDs for retrieval
- Show collection source (manual, automatic)
- Sort by most recent or relevance
- Provide guidance on retrieving specific artifacts

## Example Usage

### Example 1: List all recent artifacts

User request: "Show me all artifacts collected in the last 24 hours"

Steps:
1. Calculate timestamp for 24 hours ago
2. Call API with time filter:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/artifacts",
  query_params={
    "start": 1672444800,
    "end": 1672531200
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "artifacts": [
      {
        "id": "art-abc123",
        "sid": "sensor-001",
        "type": "memory_dump",
        "size": 104857600,
        "timestamp": 1672520000
      },
      {
        "id": "art-def456",
        "sid": "sensor-002",
        "type": "pcap",
        "size": 20971520,
        "timestamp": 1672510000
      }
    ]
  }
}
```

Present to user:
```
Recent Artifacts (Last 24 Hours)

Found 2 artifacts:

1. Memory Dump
   Artifact ID: art-abc123
   Sensor: sensor-001
   Size: 100 MB
   Collected: January 1, 2023 3:20 AM
   Source: Manual collection

2. Network Capture (PCAP)
   Artifact ID: art-def456
   Sensor: sensor-002
   Size: 20 MB
   Collected: January 1, 2023 12:33 AM
   Source: Automatic capture

Use get-artifact skill with artifact ID to download.
```

### Example 2: Find artifacts from specific sensor

User request: "Show me all memory dumps from sensor sensor-abc123"

Steps:
1. Filter by sensor ID and artifact type:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/artifacts",
  query_params={
    "sid": "sensor-abc123",
    "type": "memory_dump"
  }
)
```

Present to user:
```
Memory Dumps from sensor-abc123

Found 3 memory dumps:

1. art-mem-001
   Size: 512 MB
   Collected: December 28, 2023 2:15 PM

2. art-mem-002
   Size: 498 MB
   Collected: December 30, 2023 8:45 AM

3. art-mem-003
   Size: 515 MB
   Collected: January 1, 2024 11:00 PM

Total size: ~1.5 GB
All dumps available for download and analysis.
```

### Example 3: Audit artifact collection

User request: "What types of artifacts have been collected this month?"

Steps:
1. Get artifacts for current month
2. Analyze and group by type

Present summary:
```
Artifact Collection Summary - January 2024

Total Artifacts: 47

By Type:
- Memory Dumps: 12 (1.8 GB)
- Network Captures (PCAP): 18 (450 MB)
- Files/Executables: 15 (120 MB)
- Registry Exports: 2 (5 MB)

By Source:
- Automatic Collection: 35 (74%)
- Manual Collection: 12 (26%)

Top Sensors by Artifact Count:
1. webserver-01: 8 artifacts
2. workstation-42: 7 artifacts
3. database-03: 6 artifacts

Total Storage Used: ~2.4 GB

Artifacts are retained according to your data retention policy.
```

## Additional Notes

- Artifacts are stored based on organization retention policy
- Large artifacts (memory dumps) consume significant storage
- Artifact collection may be automatic (rule-based) or manual
- Artifact IDs are required to download/retrieve artifact data
- Timestamps reflect when artifact was collected, not created
- Size in bytes - consider converting for readability
- Some artifact types: memory_dump, pcap, file, registry, event_log
- Artifacts may expire based on retention settings
- Use get-artifact skill to download specific artifacts
- Monitor storage usage as artifacts accumulate
- Consider cleanup policies for old/large artifacts

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/artifact.go` (via GenericGETRequest)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/artifacts/artifacts.go` (RegisterListArtifacts)
