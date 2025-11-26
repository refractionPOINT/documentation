
# Get Artifact

Download artifact data or retrieve a signed download URL for a specific artifact from LimaCharlie.

## When to Use

Use this skill when the user needs to:
- Download collected artifacts for analysis
- Retrieve memory dumps from sensors
- Get network capture (pcap) files
- Download collected files or executables
- Access forensic evidence for investigations
- Export artifacts for offline analysis

Common scenarios:
- Incident response evidence collection
- Malware analysis and reverse engineering
- Network traffic investigation
- Memory forensics and analysis
- File extraction for sandboxing
- Evidence preservation and archiving

## What This Skill Does

This skill retrieves a specific artifact from LimaCharlie by its artifact ID. It calls the LimaCharlie API to either download the artifact data directly (base64-encoded) or obtain a signed URL for download. The choice depends on artifact size and use case - URLs are better for large artifacts, while direct download works for smaller files.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **artifact_id**: Unique identifier for the artifact (required)
  - Obtain from list-artifacts skill
  - Format: string identifier (e.g., "artifact-abc123")

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid artifact ID from list-artifacts
3. For large artifacts (>100MB), prefer URL method

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="get_artifact",
  parameters={
    "oid": "[organization-id]",
    "artifact_id": "[artifact-id]"
  }
)
```

**API Details:**
- Tool: `get_artifact`
- Required parameters:
  - `oid`: Organization ID
  - `artifact_id`: Artifact ID to retrieve

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "id": "artifact-abc123",
  "url": "https://storage.googleapis.com/...",
  "size": 52428800,
  "type": "memory_dump",
  "expires": 1672531200
}
```

**Success (200-299):**
- Response includes signed download link (expires)
- Response includes artifact size and type
- URL is temporary and time-limited

**Common Errors:**
- **400 Bad Request**: Invalid artifact ID format
- **403 Forbidden**: Insufficient permissions to download artifacts
- **404 Not Found**: Artifact ID does not exist or has expired
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Provide download link with expiration
- Show artifact metadata (size, type)
- Include instructions for handling the artifact
- Warn about expiration for URL method
- Suggest analysis tools for artifact type

## Example Usage

### Example 1: Get download URL for large memory dump

User request: "Get me the download link for artifact art-mem-123"

Steps:
1. Extract organization ID and artifact ID
2. Request artifact:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_artifact",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "artifact_id": "art-mem-123"
  }
)
```

Expected response:
```json
{
  "id": "art-mem-123",
  "url": "https://storage.googleapis.com/lc-artifacts/.../memory.dmp?signature=...",
  "size": 524288000,
  "type": "memory_dump",
  "expires": 1672534800
}
```

Present to user:
```
Artifact Download Ready

Artifact ID: art-mem-123
Type: Memory Dump
Size: 500 MB
Status: Available

Download URL (expires in 1 hour):
https://storage.googleapis.com/lc-artifacts/.../memory.dmp?signature=...

Important Notes:
- This URL expires at 2:00 PM (1 hour from now)
- Download the file before it expires
- Large file - may take several minutes to download

Recommended Analysis Tools:
- Volatility Framework for memory analysis
- Rekall for memory forensics
- WinDbg for Windows memory dumps
```

### Example 2: Download network capture for analysis

User request: "I need the pcap file from that suspicious traffic alert"

Steps:
1. First list artifacts to find the pcap
2. Get artifact:
```
mcp__limacharlie__lc_call_tool(
  tool_name="get_artifact",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "artifact_id": "art-pcap-789"
  }
)
```

Present to user:
```
Network Capture Ready for Analysis

Artifact ID: art-pcap-789
Type: Packet Capture (PCAP)
Size: 15 MB
Capture Duration: 5 minutes
Sensor: webserver-prod-01

Download Link:
https://storage.googleapis.com/lc-artifacts/.../capture.pcap?sig=...

Analysis Suggestions:
1. Open in Wireshark for packet-level analysis
2. Use tcpdump for command-line inspection
3. Check for suspicious connections/protocols
4. Extract IOCs (IPs, domains, patterns)
5. Look for protocol anomalies

Common Wireshark Filters:
- Suspicious IPs: ip.addr == x.x.x.x
- HTTP traffic: http
- DNS queries: dns
- TLS/SSL: ssl or tls

The capture contains traffic from the time of the alert.
```

## Additional Notes

- Signed URLs expire quickly (typically 1 hour) for security
- Download artifacts promptly when using URL method
- Large artifacts (>100MB) should use URL method
- Handle artifacts securely - may contain malicious content
- URLs are single-use and time-limited
- Artifacts may be deleted after retention period
- Consider storage when downloading many/large artifacts
- Always verify artifact integrity (checksums)
- Use appropriate analysis tools for artifact type
- Maintain chain of custody for forensic evidence

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/artifact.go` (ExportArtifact function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/artifacts/artifacts.go` (RegisterGetArtifact)
