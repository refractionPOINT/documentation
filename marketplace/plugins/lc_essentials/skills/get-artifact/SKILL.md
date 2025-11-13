---
name: get-artifact
description: Download or get signed URL for a specific artifact from LimaCharlie including memory dumps, pcap files, collected files, and forensic evidence. Supports either retrieving base64-encoded artifact data directly or getting a temporary download URL. Use this skill when downloading forensic evidence, retrieving collected samples, or analyzing artifacts.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

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

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **artifact_id**: Unique identifier for the artifact (required)
  - Obtain from list-artifacts skill
  - Format: string identifier (e.g., "artifact-abc123")

Optional parameters:
- **get_url_only**: Return signed URL instead of downloading (optional, default: false)
  - `true` = Get temporary download URL only
  - `false` = Download artifact data directly (base64-encoded)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Valid artifact ID from list-artifacts
3. Decision on retrieval method (URL vs direct download)
4. For large artifacts (>100MB), prefer URL method

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

**For Direct Download:**
```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/insight/[oid]/artifacts/originals/[artifact-id]"
)
```

**For URL Only:**
```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/insight/[oid]/artifacts/[artifact-id]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST` (direct download) or `GET` (metadata/URL)
- Path: `/insight/{oid}/artifacts/originals/{artifact_id}` or `/insight/{oid}/artifacts/{artifact_id}`
- Query parameters: None
- Body fields: None

### Step 3: Handle the Response

The API returns different structures based on method:

**Direct Download (POST to /originals/):**
```json
{
  "status_code": 200,
  "body": {
    "payload": "base64-encoded-data...",
    "size": 52428800,
    "type": "memory_dump"
  }
}
```

**URL/Metadata (GET):**
```json
{
  "status_code": 200,
  "body": {
    "id": "artifact-abc123",
    "url": "https://storage.googleapis.com/...",
    "size": 52428800,
    "type": "memory_dump",
    "expires": 1672531200
  }
}
```

**Success (200-299):**
- Direct download returns base64-encoded artifact data
- URL method returns signed download link (expires)
- Response includes artifact size and type
- Data is compressed/encoded for transfer

**Common Errors:**
- **400 Bad Request**: Invalid artifact ID format
- **403 Forbidden**: Insufficient permissions to download artifacts
- **404 Not Found**: Artifact ID does not exist or has expired
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- For direct download: Save decoded data to file
- For URL method: Provide download link with expiration
- Show artifact metadata (size, type)
- Include instructions for handling the artifact
- Warn about expiration for URL method
- Suggest analysis tools for artifact type

## Example Usage

### Example 1: Get download URL for large memory dump

User request: "Get me the download link for artifact art-mem-123"

Steps:
1. Extract organization ID and artifact ID
2. Request artifact metadata with URL:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/artifacts/art-mem-123"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "id": "art-mem-123",
    "url": "https://storage.googleapis.com/lc-artifacts/.../memory.dmp?signature=...",
    "size": 524288000,
    "type": "memory_dump",
    "expires": 1672534800
  }
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
🔗 https://storage.googleapis.com/lc-artifacts/.../memory.dmp?signature=...

Important Notes:
⚠️ This URL expires at 2:00 PM (1 hour from now)
⚠️ Download the file before it expires
⚠️ Large file - may take several minutes to download

Recommended Analysis Tools:
- Volatility Framework for memory analysis
- Rekall for memory forensics
- WinDbg for Windows memory dumps
```

### Example 2: Download small artifact directly

User request: "Download the collected file artifact-file-456"

Steps:
1. Request direct download:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/artifacts/originals/artifact-file-456"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "payload": "H4sIAAAAAAAA/+y9B5gkSXYn...",
    "size": 2048576,
    "type": "file"
  }
}
```

Present to user:
```
✅ Artifact Downloaded

Artifact ID: artifact-file-456
Type: Collected File
Size: 2 MB
Format: Base64-encoded (gzip compressed)

The artifact has been downloaded and decoded.
Saved to: /downloads/artifact-file-456.bin

File Information:
- Original size: 2 MB
- Compressed for transfer
- Decompressed and ready for analysis

Next Steps:
1. Scan file with antivirus/sandbox
2. Perform static analysis
3. Extract IOCs (hashes, strings, etc.)
4. Submit to threat intelligence platforms

⚠️ Handle with care - may contain malicious content
```

### Example 3: Download network capture for analysis

User request: "I need the pcap file from that suspicious traffic alert"

Steps:
1. First list artifacts to find the pcap
2. Get artifact URL:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/artifacts/art-pcap-789"
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
🔗 https://storage.googleapis.com/lc-artifacts/.../capture.pcap?sig=...

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
- Direct download better for automation and small artifacts
- Artifact data is compressed and may need decompression
- Handle artifacts securely - may contain malicious content
- Base64 encoding increases data size by ~33%
- URLs are single-use and time-limited
- Artifacts may be deleted after retention period
- Consider storage when downloading many/large artifacts
- Always verify artifact integrity (checksums)
- Use appropriate analysis tools for artifact type
- Maintain chain of custody for forensic evidence

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/artifact.go` (ExportArtifact function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/artifacts/artifacts.go` (RegisterGetArtifact)
