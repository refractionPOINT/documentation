
# Search IOCs

Search for Indicators of Compromise (IOCs) across your organization's historical data.

## When to Use

Use this skill when the user needs to:
- Search for specific IOCs across all sensors
- Track prevalence of file hashes, domains, or IPs
- Find which sensors have seen an indicator
- Pivot from one indicator to related activity
- Assess scope of compromise
- Hunt for threats across the environment

Common scenarios:
- "Has any sensor seen this malicious hash: abc123..."
- "Which hosts connected to domain evil.com?"
- "Find all sensors with IP address 203.0.113.50"
- "Search for file path C:\\malware.exe across the fleet"
- "Show me all systems where user 'hacker' appeared"

## What This Skill Does

This skill searches for IOCs across all sensor telemetry, returning either summary counts or specific sensor locations with timestamps.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID
- **ioc_type**: Type of IOC (file_hash, domain, ip, file_path, file_name, user, service_name, package_name, hostname)
- **ioc_value**: The IOC value to search (supports % wildcard)
- **info_type**: "summary" for counts or "locations" for sensor details

Optional:
- **case_sensitive**: Boolean (default false)

## How to Use

### Step 1: Validate Parameters

Ensure valid IOC type and value format.

### Step 2: Call the Tool

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="search_iocs",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "ioc_type": "file_hash",
    "ioc_value": "abc123def456...",
    "info_type": "summary",
    "case_sensitive": false
  }
)
```

**Tool Details:**
- Tool name: `search_iocs`
- Parameters:
  - `oid`: Organization ID (required)
  - `ioc_type`: Type of IOC (required)
  - `ioc_value`: The IOC value to search (required)
  - `info_type`: "summary" or "locations" (required)
  - `case_sensitive`: Boolean (optional, default false)

**IOC Types:**
- file_hash: SHA256 file hashes
- domain: DNS domain names
- ip: IP addresses
- file_path: Full file paths
- file_name: File names
- user: Usernames
- service_name: Service names
- package_name: Package names
- hostname: Hostnames

### Step 3: Handle Response

**Summary response:**
```json
{
  "type": "file_hash",
  "name": "abc123...",
  "last_1_days": 5,
  "last_7_days": 23,
  "last_30_days": 45,
  "last_365_days": 120,
  "from_cache": true
}
```

**Locations response:**
```json
{
  "type": "file_hash",
  "name": "abc123...",
  "locations": {
    "sensor-1": {
      "hostname": "SERVER01",
      "first_ts": 1705761234,
      "last_ts": 1705847634
    }
  }
}
```

### Step 4: Format Response

Display summary counts or sensor list with timestamps.

**Example output:**
```
IOC Search Results: abc123def456... (file_hash)

Prevalence:
- Last 24 hours: 5 occurrences
- Last 7 days: 23 occurrences
- Last 30 days: 45 occurrences
- Last year: 120 occurrences

Sensor Locations (3):
- SERVER01: First seen 2024-01-15, Last seen 2024-01-20
- WORKSTATION-05: First seen 2024-01-18, Last seen 2024-01-20
- DB-01: First seen 2024-01-10, Last seen 2024-01-19
```

## Example Usage

### Example 1: Search file hash

User: "Has any sensor seen this hash: abc123...?"

Request summary first, then locations if found.

### Example 2: Wildcard search

User: "Find all .exe files with 'malware' in the name"

Use `ioc_type="file_name"` and `ioc_value="%malware%.exe"`.

## Additional Notes

- Wildcards use % character
- Summary is cached for performance
- Locations show first and last seen timestamps
- Use batch-search-iocs for multiple IOCs
- Hostname searches use different endpoint

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/insight.go`
MCP: `../lc-mcp-server/internal/tools/historical/historical.go`
