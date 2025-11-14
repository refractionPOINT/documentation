
# Delete Sensor

Permanently delete a sensor from your organization, removing all associated data and configuration.

## When to Use

Use this skill when the user needs to:
- Remove sensors from decommissioned systems
- Clean up test or temporary sensors
- Delete sensors that will never come back online
- Remove duplicate sensor entries
- Permanently remove compromised sensors that are being replaced
- Clean up the sensor inventory

Common scenarios:
- "Delete this decommissioned server from the system"
- "Remove the test sensor, we're done with it"
- "Permanently delete this sensor and all its data"
- "Clean up old sensors that are no longer in use"

## What This Skill Does

This skill permanently deletes a sensor from your LimaCharlie organization. All sensor data, configuration, tags, and history are removed. This is an irreversible operation - once deleted, the sensor cannot be recovered and would need to be re-enrolled if the endpoint should be managed again. Use this carefully for true decommissioning or cleanup scenarios.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sid**: Sensor ID (UUID format) - the sensor to permanently delete

**IMPORTANT WARNINGS:**
- This operation is PERMANENT and IRREVERSIBLE
- All sensor data, history, and configuration will be deleted
- The sensor cannot be recovered after deletion
- If the sensor comes online again, it will be treated as a new enrollment
- Confirm with the user before proceeding with deletion

## How to Use

### Step 1: Validate Parameters and Confirm

Ensure you have:
1. Valid organization ID (oid)
2. Valid sensor ID (sid) in UUID format
3. **CRITICAL**: Confirm with the user that they want to permanently delete this sensor
4. Verify you have the correct sensor (check hostname, IP, etc.)
5. Consider backing up any important data from the sensor first

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/[sensor-id]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/{sid}` where `{sid}` is the sensor UUID
- No query parameters needed
- No request body needed

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Status code 200 indicates the sensor was successfully deleted
- All sensor data, history, and configuration are permanently removed
- The sensor ID is no longer valid in the organization
- If the endpoint comes online, it will need to be re-enrolled as a new sensor

**Common Errors:**
- **400 Bad Request**: Invalid sensor ID format - verify the sid is a valid UUID
- **404 Not Found**: Sensor does not exist - may already be deleted or never existed
- **403 Forbidden**: Insufficient permissions - requires sensor deletion permissions
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the sensor was permanently deleted
- Warn that this action is irreversible
- Explain that all data and history have been removed
- Mention that re-enrollment would be required if the endpoint should be managed again
- Suggest documenting the deletion for audit purposes

## Example Usage

### Example 1: Delete Decommissioned Server

User request: "Delete sensor abc12345-6789-0123-4567-890abcdef012, the server has been decommissioned"

Steps:
1. Validate the sensor ID format (UUID)
2. Verify the sensor exists and get its details (hostname, etc.)
3. **Confirm with user**: "This will permanently delete sensor abc12345-6789-0123-4567-890abcdef012 (hostname: SERVER01). All data and history will be lost. Are you sure?"
4. If confirmed, call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/abc12345-6789-0123-4567-890abcdef012"
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Sensor abc12345-6789-0123-4567-890abcdef012 (SERVER01) has been permanently deleted from your organization. All sensor data, configuration, tags, and history have been removed. This action is irreversible. If the endpoint comes online again, it would need to be re-enrolled as a new sensor."

### Example 2: Clean Up Test Sensor

User request: "Remove the test sensor we used for POC"

Steps:
1. Identify the sensor ID for the test sensor
2. Verify it's the correct sensor to delete
3. Confirm deletion intent
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/def45678-90ab-cdef-0123-456789abcdef"
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"The test sensor has been successfully deleted from your organization. All associated data has been permanently removed. Your sensor inventory is now cleaned up."

## Additional Notes

- **This operation is PERMANENT and IRREVERSIBLE** - there is no undo
- Always confirm with the user before deleting a sensor
- Consider exporting or archiving important data before deletion
- Deleted sensors cannot be recovered - they would need complete re-enrollment
- The sensor ID becomes invalid and cannot be reused
- If the physical endpoint is still running the LC sensor, it will lose connection
- The endpoint can be re-enrolled with a new installation key if needed
- Tags, custom metadata, and all historical telemetry are permanently deleted
- This does not uninstall the sensor software from the endpoint
- Consider using isolation or tags instead of deletion for temporary removal needs
- Deletion is immediate and takes effect within seconds
- This is useful for true decommissioning, not for temporary offline sensors
- Review billing impact - deleted sensors no longer count toward your license
- Audit and compliance teams may require documenting sensor deletions
- Use caution in production environments - verify the sensor identity carefully

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/sensor.go` (Delete method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/response/tasking.go` (delete_sensor)
