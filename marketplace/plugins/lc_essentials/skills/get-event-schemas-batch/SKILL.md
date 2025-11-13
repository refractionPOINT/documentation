---
name: get-event-schemas-batch
description: Retrieve schema definitions for multiple event types simultaneously in parallel for improved performance. Use when users need schemas for several event types at once (DNS_REQUEST, PROCESS_START, NETWORK_CONNECTIONS, etc.). Essential for bulk analysis, comprehensive rule development, multi-event investigations, and reducing API calls when analyzing multiple telemetry types.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Get Event Schemas Batch

Retrieve schema definitions for multiple event types simultaneously in a single operation, improving performance when working with multiple event structures.

## When to Use

Use this skill when the user needs to:
- Get schemas for multiple event types at once
- Reduce API calls when analyzing several event types
- Build comprehensive detection rules across multiple event types
- Analyze relationships between different event structures
- Document multiple event types for integrations

Common scenarios:
- "Show me schemas for DNS_REQUEST, HTTP_REQUEST, and NETWORK_CONNECTIONS"
- "I need to understand process and network events together"
- "Get schemas for all file-related events"
- "What fields are available across DNS, HTTP, and TLS events?"

## What This Skill Does

This skill retrieves schema definitions for multiple event types in parallel, returning a comprehensive map of event structures. It makes concurrent API calls to fetch each schema efficiently, combining the results into a single response. This is more efficient than calling get-event-schema multiple times sequentially.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **event_names**: Array of event type names (e.g., ['DNS_REQUEST', 'PROCESS_START', 'NETWORK_CONNECTIONS'])

Event type names should match LimaCharlie's naming convention (UPPERCASE_WITH_UNDERSCORES).

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Array of event type names (at least one)
3. Each event type name is valid and case-sensitive
4. No duplicate event types in the array

### Step 2: Call the API for Each Event Type

For each event type in the array, call the API in parallel:

```
For each event_name in event_names:
  mcp__limacharlie__lc_api_call(
    oid="[organization-id]",
    endpoint="api",
    method="GET",
    path="/orgs/[organization-id]/schema/[event-name]"
  )
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/orgs/{oid}/schema/{name}` for each event type
- Calls are made in parallel for performance
- Individual failures don't stop other requests

### Step 3: Handle the Response

The response combines all schemas and errors:
```json
{
  "schemas": {
    "DNS_REQUEST": {
      "event_type": "DNS_REQUEST",
      "elements": ["event/DNS_REQUEST/DOMAIN_NAME", ...]
    },
    "PROCESS_START": {
      "event_type": "PROCESS_START",
      "elements": ["event/PROCESS_START/FILE_PATH", ...]
    }
  },
  "errors": {
    "UNKNOWN_EVENT": "failed to get schema: 404 Not Found"
  }
}
```

**Success (200-299 for each):**
- `schemas` object contains successfully retrieved schemas
- Each schema includes `event_type` and `elements` array
- Partial success is possible (some schemas succeed, others fail)

**Handling Errors:**
- `errors` object contains any failed event types
- Keys are event type names, values are error messages
- Continue processing successful schemas even if some fail
- Common individual errors:
  - **404 Not Found**: Specific event type doesn't exist
  - **400 Bad Request**: Event type name format invalid
  - **403 Forbidden**: Insufficient permissions

### Step 4: Format the Response

Present the result to the user:
- Group schemas by category if appropriate (network, process, file, etc.)
- For each successful schema, list the event type and key fields
- Clearly indicate any failed event types and why
- Summarize common fields across multiple event types
- Highlight unique fields specific to each event type

## Example Usage

### Example 1: Getting multiple network event schemas

User request: "Show me schemas for DNS_REQUEST, HTTP_REQUEST, and NETWORK_CONNECTIONS"

Steps:
1. Extract oid from context
2. Event names array: ['DNS_REQUEST', 'HTTP_REQUEST', 'NETWORK_CONNECTIONS']
3. Call API for each in parallel:
```
For 'DNS_REQUEST':
  mcp__limacharlie__lc_api_call(
    oid="c7e8f940-1234-5678-abcd-1234567890ab",
    endpoint="api",
    method="GET",
    path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/schema/DNS_REQUEST"
  )

For 'HTTP_REQUEST':
  mcp__limacharlie__lc_api_call(
    oid="c7e8f940-1234-5678-abcd-1234567890ab",
    endpoint="api",
    method="GET",
    path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/schema/HTTP_REQUEST"
  )

For 'NETWORK_CONNECTIONS':
  mcp__limacharlie__lc_api_call(
    oid="c7e8f940-1234-5678-abcd-1234567890ab",
    endpoint="api",
    method="GET",
    path="/orgs/c7e8f940-1234-5678-abcd-1234567890ab/schema/NETWORK_CONNECTIONS"
  )
```

Expected combined response showing all three schemas with their respective elements.

### Example 2: Handling partial failures

User request: "Get schemas for PROCESS_START, FAKE_EVENT, and FILE_CREATE"

Steps:
1. Make parallel calls for all three
2. PROCESS_START succeeds
3. FAKE_EVENT returns 404
4. FILE_CREATE succeeds
5. Present successful schemas and note the failure

Result presentation: "Retrieved schemas for PROCESS_START and FILE_CREATE successfully. Note: FAKE_EVENT schema not found - this event type may not exist in LimaCharlie."

## Additional Notes

- This operation is significantly faster than sequential calls for multiple event types
- Partial failures are handled gracefully - successful schemas are still returned
- Useful when building detection logic that spans multiple event types
- Consider requesting related event types together (e.g., all network events, all process events)
- Maximum recommended: 10-15 event types at once for optimal performance
- If you need all event types, use `get-event-types-with-schemas` instead
- Event type names are case-sensitive

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/schemas.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/schemas/schemas.go`
