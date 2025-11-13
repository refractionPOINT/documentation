---
name: batch-search-iocs
description: Search for multiple Indicators of Compromise (IOCs) simultaneously in a single API call. Supports mixed IOC types (hashes, domains, IPs, paths). More efficient than individual searches. Use for bulk threat hunting, processing IOC feeds, compromise assessment campaigns, and investigating related indicators together.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Batch Search IOCs

Search for multiple IOCs simultaneously in a single efficient API call.

## When to Use

Use this skill when the user needs to:
- Search for multiple IOCs at once
- Process threat intelligence feeds
- Hunt for related indicators together
- Assess compromise scope with multiple indicators
- Efficiently check IOC lists
- Correlate multiple threat indicators

Common scenarios:
- "Check these 10 file hashes against our environment"
- "Search for all IOCs from this threat report"
- "Hunt for this list of C2 domains and IPs"
- "Process this IOC feed across all sensors"
- "Check if any of these indicators are present"

## What This Skill Does

This skill searches for multiple IOCs in parallel, supporting mixed types (hashes, domains, IPs, etc.) in a single API call.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID
- **iocs**: JSON array of IOC objects with `type` and `value` fields
- **info_type**: "summary" or "locations"

## How to Use

### Step 1: Prepare IOC List

Format IOCs as JSON array:
```json
[
  {"type": "file_hash", "value": "abc123..."},
  {"type": "domain", "value": "evil.com"},
  {"type": "ip", "value": "203.0.113.50"}
]
```

### Step 2: Call API

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/search/batch",
  body={
    "objects": {
      "file_hash": ["abc123...", "def456..."],
      "domain": ["evil.com", "malware.net"],
      "ip": ["203.0.113.50"]
    },
    "case_sensitive": false
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/insight/{oid}/search/batch`
- Body: Groups IOCs by type for efficient batch processing

### Step 3: Handle Response

Response contains results for each IOC:
```json
{
  "status_code": 200,
  "body": {
    "results": {
      "file_hash": {
        "abc123...": {
          "last_1_days": 5,
          "last_7_days": 10
        },
        "def456...": {
          "last_1_days": 0,
          "last_7_days": 0
        }
      },
      "domain": {
        "evil.com": {
          "last_1_days": 12,
          "locations": {...}
        }
      }
    }
  }
}
```

### Step 4: Format Response

Display results grouped or as summary:

```
Batch IOC Search Results (5 indicators)

FOUND (2):
- abc123... (file_hash): 10 occurrences in last 7 days
- evil.com (domain): 12 occurrences in last 24 hours
  Locations: SERVER01, WORKSTATION-05

NOT FOUND (3):
- def456... (file_hash)
- malware.net (domain)
- 203.0.113.50 (ip)
```

## Example Usage

### Example 1: Threat report IOCs

User: "Check these IOCs from the threat report"

Parse IOC list, group by type, call batch API.

### Example 2: IOC feed processing

User: "Process this daily IOC feed"

Read feed, convert to batch format, search all at once.

## Additional Notes

- Much more efficient than individual searches
- Supports mixed IOC types in one call
- Results are per-IOC, individually detailed
- Maximum batch size may be limited (typically 100-1000)
- Consider breaking very large lists into multiple batches

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/insight.go`
MCP: `../lc-mcp-server/internal/tools/historical/historical.go`
