
# Get Event Types With Schemas

Retrieve a complete list of all event types that have schema definitions available in the organization.

## When to Use

Use this skill when the user needs to:
- Discover what event types are available
- List all telemetry types supported
- Find the correct name for a specific event type
- Browse available data sources for detection
- Understand the organization's telemetry coverage

Common scenarios:
- "What event types are available?"
- "Show me all the events LimaCharlie can collect"
- "What's the event type for DNS queries?"
- "List all network-related events"

## What This Skill Does

This skill retrieves the complete list of event type names that have schema definitions in LimaCharlie. It returns a comprehensive array of event type names, allowing users to discover what telemetry is available before diving into specific schemas.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No other parameters are needed - this returns all available event types.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="GET",
  path="/v1/orgs/[organization-id]/schema"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/v1/orgs/{oid}/schema`
- No query parameters
- No request body

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "event_types": [
      "DNS_REQUEST",
      "HTTP_REQUEST",
      "NETWORK_CONNECTIONS",
      "PROCESS_START",
      "FILE_CREATE",
      ...
    ]
  }
}
```

**Success (200-299):**
- Body contains `event_types` array with all available event type names
- Names use LimaCharlie's standard naming convention (UPPERCASE_WITH_UNDERSCORES)
- Array typically contains 50-100+ event types depending on platform support
- These names can be used with `get-event-schema` to get detailed field information

**Common Errors:**
- **403 Forbidden**: Insufficient API permissions to read schemas
- **500 Server Error**: Temporary API issue - retry after a short delay

### Step 4: Format the Response

Present the result to the user:
- List event types in logical groups (network, process, file, registry, etc.)
- Include a count of total event types available
- Highlight commonly used event types
- Provide brief descriptions of event type categories
- If user asked for specific type, filter and highlight matches

## Example Usage

### Example 1: Listing all available event types

User request: "What event types are available in LimaCharlie?"

Steps:
1. Extract oid from context
2. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/v1/orgs/c7e8f940-1234-5678-abcd-1234567890ab/schema"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "event_types": [
      "DNS_REQUEST",
      "HTTP_REQUEST",
      "NETWORK_CONNECTIONS",
      "PROCESS_START",
      "FILE_CREATE",
      "FILE_DELETE",
      "REGISTRY_CREATE",
      ...
    ]
  }
}
```

Present to user grouped by category:
- Network Events: DNS_REQUEST, HTTP_REQUEST, NETWORK_CONNECTIONS...
- Process Events: PROCESS_START, PROCESS_TERMINATE...
- File Events: FILE_CREATE, FILE_DELETE, FILE_OPEN...
- Registry Events: REGISTRY_CREATE, REGISTRY_DELETE...

### Example 2: Finding DNS-related events

User request: "What events are available for DNS monitoring?"

Steps:
1. Get all event types
2. Filter for DNS-related names
3. Present matching event types with brief descriptions

## Additional Notes

- Event type names are platform-agnostic at the schema level
- Not all event types are available on all platforms (Windows, Linux, macOS)
- Use `get-event-types-with-schemas-for-platform` to filter by OS
- The list includes both endpoint and cloud/SaaS event types
- Event types with schemas are those that have been indexed and are queryable
- Use this as a discovery tool before requesting specific schemas
- Names returned here can be directly used with other schema-related skills

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/schemas.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/schemas/schemas.go`
