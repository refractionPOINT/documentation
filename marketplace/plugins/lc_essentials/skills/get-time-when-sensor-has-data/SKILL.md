---
name: get-time-when-sensor-has-data
description: Get the time range when a sensor has available telemetry data in the historical database. Returns earliest and latest data timestamps. Use to verify data retention, check sensor data availability, determine query boundaries, and troubleshoot missing data issues.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get Sensor Data Timeline

Get the time range when a sensor has telemetry data available.

## When to Use

Use this skill when the user needs to:
- Check if sensor has data in a specific timeframe
- Verify data retention for a sensor
- Determine earliest available data
- Find latest data timestamp
- Troubleshoot missing sensor data
- Plan historical queries

Common scenarios:
- "Does this sensor have data from last week?"
- "When did this sensor start sending telemetry?"
- "What's the earliest data available for this sensor?"
- "Check if we have data for the incident timeframe"
- "Verify sensor data retention"

## What This Skill Does

This skill queries the sensor's data timeline to return the earliest and latest timestamps for which telemetry data is available.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **sid**: Sensor ID

## How to Use

### Step 1: Validate Parameters

Ensure valid org ID and sensor ID.

### Step 2: Call API

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/insight/c7e8f940-1234-5678-abcd-1234567890ab/timeline/xyz-sensor-id"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/insight/{oid}/timeline/{sid}`

### Step 3: Handle Response

```json
{
  "status_code": 200,
  "body": {
    "sid": "xyz-sensor-id",
    "earliest": 1705000000,
    "latest": 1705847634,
    "has_data": true
  }
}
```

**Success (200):**
- `earliest`: Unix timestamp of oldest data
- `latest`: Unix timestamp of newest data
- `has_data`: Boolean indicating data availability

### Step 4: Format Response

```
Sensor Data Availability: xyz-sensor-id

Data Range:
- Earliest: 2024-01-11 12:00:00 UTC
- Latest: 2024-01-21 14:30:34 UTC
- Duration: 10 days

Status: Data available for historical queries
```

## Example Usage

### Example 1: Check data availability

User: "Does sensor xyz-123 have data from last week?"

Compare query timeframe with returned earliest/latest range.

### Example 2: Troubleshoot missing data

User: "Why can't I query events for this sensor?"

Check timeline to verify sensor has any data.

## Additional Notes

- Empty response means no data retained
- Useful before running expensive queries
- Data retention depends on org tier/policy
- Sensors may have gaps in timeline

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/organization.go`
MCP: `../lc-mcp-server/internal/tools/historical/historical.go`
