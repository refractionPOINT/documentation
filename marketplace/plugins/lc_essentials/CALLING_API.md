# Generic LimaCharlie API Access

The `lc_api_call` tool provides direct HTTP access to LimaCharlie's API and billing endpoints. This document explains how to use it effectively from within skills.

## Basic Parameters

- **endpoint**: Target endpoint type:
  - `"api"` - Standard API endpoint (api.limacharlie.io)
  - `"billing"` - Billing endpoint (billing.limacharlie.io)
  - `"replay"` - Replay/LCQL endpoint (automatically resolves per-org replay instance URL)
- **method**: HTTP method - GET, POST, PUT, DELETE, or PATCH
- **path**: API path starting with "/" (e.g., "/rules/{oid}" or "/outputs/{oid}")
  - For `"replay"` endpoint, use "/" as the path (root path on replay instance)
- **query_params** (optional): URL query parameters as key-value object
- **headers** (optional): Custom HTTP headers as key-value object
- **body** (optional): Request body as object (will be JSON-serialized) - typically used with POST/PUT/PATCH
  - For `"replay"` endpoint, body must include `"oid"` field
- **timeout** (optional): Request timeout in seconds (default: 30)
- **oid**: Organization ID - required for most calls, but **omit this parameter** for user-level and global operations (see below)

## User-Level and Global Operations

Some API operations don't require a specific organization context and the **`oid` parameter should be omitted**:

**User-level operations** (use `/user/*` paths):
- `/user/orgs` (GET) - List organizations accessible to the user
  - Used by: `list-user-orgs` skill
  - Omit the `oid` parameter

**Global operations** (don't include `{oid}` in path):
- `/orgs` (POST) - Create new organization
  - Used by: `create-org` skill
  - Omit the `oid` parameter
- `/ontology` (GET) - Get platform names from global ontology
  - Used by: `get-platform-names` skill
  - Omit the `oid` parameter

**All other operations require a valid, specific organization ID.**

For organization-specific operations, the path typically includes `{oid}` as a variable:
- `/rules/{oid}` - Requires specific organization ID
- `/sensors/{oid}` - Requires specific organization ID
- `/outputs/{oid}` - Requires specific organization ID

## Authentication

Authentication is handled automatically using the MCP server's auth context. You don't need to provide API keys or JWT tokens.

## Path Variables

Always replace path variables with actual values:
- `{oid}` → Actual organization ID (from user context or parameter)
- Example: `/rules/{oid}` → `/rules/c7e8f940-1234-5678-abcd-1234567890ab`

## Response Structure

All responses include:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "headers": {...},
  "body": {...}
}
```

When status_code ≥ 400, an `error` field with human-readable message is included.

Success: 200-299 range
Client errors: 400-499
Server errors: 500-599

## Common Patterns

### Pattern 1: Simple GET Request (List Resources)
```
Use lc_api_call with:
- endpoint: "api"
- method: "GET"
- path: "/outputs/{oid}"
- oid: [organization-id]

No body needed for GET requests.
Response will contain list of resources in body.
```

### Pattern 2: GET with Query Parameters (Filtered List)
```
Use lc_api_call with:
- endpoint: "api"
- method: "GET"
- path: "/rules/{oid}"
- query_params: {"namespace": "general"}
- oid: [organization-id]

Query params appear in URL: /rules/{oid}?namespace=general
```

### Pattern 3: GET Single Resource by Name/ID
```
Some endpoints require name/ID in query params:

Use lc_api_call with:
- endpoint: "api"
- method: "GET"
- path: "/rules/{oid}"
- query_params: {"name": "rule-name", "namespace": "general"}
- oid: [organization-id]

The API will filter and return the specific resource.
```

### Pattern 4: POST to Create Resource
```
Use lc_api_call with:
- endpoint: "api"
- method: "POST"
- path: "/outputs/{oid}"
- body: {
    "name": "my-output",
    "module": "syslog",
    "type": "event",
    "dest_host": "syslog.example.com",
    "dest_port": 514
  }
- oid: [organization-id]

Body contains the resource configuration.
```

### Pattern 5: POST with Form Data (Legacy Endpoints)
```
Some older endpoints expect form-encoded data. Use body object:

Use lc_api_call with:
- endpoint: "api"
- method: "POST"
- path: "/rules/{oid}"
- body: {
    "name": "rule-name",
    "namespace": "general",
    "detect": {...},
    "respond": [...]
  }
- oid: [organization-id]

The tool will serialize as JSON (most endpoints now accept JSON).
```

### Pattern 6: PUT to Update Resource
```
Use lc_api_call with:
- endpoint: "api"
- method: "PUT"
- path: "/configs/extension/{oid}"
- body: {
    "name": "extension-name",
    "config": {...}
  }
- oid: [organization-id]

PUT typically replaces the entire resource.
```

### Pattern 7: DELETE with Parameters
```
Use lc_api_call with:
- endpoint: "api"
- method: "DELETE"
- path: "/outputs/{oid}"
- body: {"name": "output-name"}
- oid: [organization-id]

DELETE may require identifying which resource to delete via body or query params.
```

### Pattern 8: PATCH for Partial Updates
```
Use lc_api_call with:
- endpoint: "api"
- method: "PATCH"
- path: "/some-resource/{oid}"
- body: {
    "field_to_update": "new_value"
  }
- oid: [organization-id]

PATCH updates only specified fields (less common in LC API).
```

## Handling Large Results

When API responses exceed approximately 100KB, the `lc_api_call` tool returns a special response format instead of the full data:

```json
{
  "is_temp_file": false,
  "reason": "results too large, see resource_link for content",
  "resource_link": "https://storage.googleapis.com/lc-tmp-mcp-export/lc_api_call_20251114_142154_73e57517.json.gz?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=...",
  "resource_size": 34329,
  "success": true
}
```

### Understanding the Response

- **is_temp_file**: `false` indicates data is at a remote URL
- **reason**: Explains why the full data wasn't returned inline
- **resource_link**: Signed Google Cloud Storage URL containing the data
- **resource_size**: Size of the compressed file in bytes
- **success**: `true` indicates the API call succeeded

### Resource Link Details

The `resource_link` URL:
- Contains gzip-compressed JSON data (`.json.gz` extension)
- Is time-limited (typically expires in 24 hours)
- Includes GCP authentication tokens in the URL parameters
- Can be downloaded directly with tools like `curl` or `WebFetch`

### Handling Large Results with analyze-lc-result.sh Script

**CRITICAL REQUIREMENT**: When `lc_api_call` returns a `resource_link`, you **MUST** follow this exact workflow. DO NOT attempt to guess the JSON structure or write jq queries before analyzing the schema.

**Why this is mandatory**: Skipping the analysis step results in incorrect queries, wasted tokens, and frustration. The schema reveals the actual structure, which may differ from what you expect.

**Step 1: Download and Analyze (REQUIRED)**

**You MUST run the analyze script first. DO NOT skip this step.**

Run the analyze script with the `resource_link` URL directly:

```bash
bash ./marketplace/plugins/lc_essentials/scripts/analyze-lc-result.sh "https://storage.googleapis.com/lc-tmp-mcp-export/..."
```

Replace the URL with the actual `resource_link` value from the API response.

**What this script does:**
1. Downloads the file to `/tmp/lc-result-{timestamp}.json`
2. Outputs the JSON schema to stdout showing object keys, array patterns, and data types
3. Prints the file path to stderr (after `---FILE_PATH---`)

**Example output:**
```
(stdout) {"sensors": [{"sid": "string", "hostname": "string", "platform": "string"}]}
(stderr) ---FILE_PATH---
(stderr) /tmp/lc-result-1731633216789456123.json
```

**Before proceeding to Step 2**, you MUST review the schema output to understand:
- Is the top-level structure an object or array?
- What are the available keys/fields?
- How is the data nested?

**Step 2: Extract Specific Data with jq**

**Only after reviewing the schema**, use jq to extract the specific information requested. Use the file path shown in the script output.

Common patterns based on schema:

```bash
# If schema shows top-level array
jq '.[] | select(.hostname == "web-01")' /tmp/lc-result-{timestamp}.json

# If schema shows top-level object with named keys
jq '.sensors[] | {id: .sid, name: .hostname}' /tmp/lc-result-{timestamp}.json

# Count items
jq '. | length' /tmp/lc-result-{timestamp}.json
```

**Step 3: Clean Up**

Remove the temporary file when done:

```bash
rm /tmp/lc-result-{timestamp}.json
```

Replace `{timestamp}` with the actual timestamp from Step 1's output.

**When to use this workflow:**
- `lc_api_call` returns a `resource_link` response
- You're asking for specific information (e.g., "find sensors with hostname X", "count enabled rules", "get OID for lc_demo")
- You don't need the complete result set

**When NOT to use this workflow:**
- You explicitly want the full/complete dataset
- Results are small enough to fit in context (no `resource_link`)
- You only need summary metadata (count, structure overview)

### Common Scenarios

**Scenario 1: Large Sensor Lists**
- API: `GET /sensors/{oid}` for organizations with 1000+ sensors
- Returns: `resource_link` with full sensor inventory
- Use jq to: Find specific sensors, filter by platform, check online status

**Scenario 2: Bulk Historical Events**
- API: `POST /insight/{oid}/lcql` with broad time range
- Returns: `resource_link` with thousands of events
- Use jq to: Extract specific event types, count occurrences, find patterns

**Scenario 3: Extensive Rule Lists**
- API: `GET /rules/{oid}` for organizations with many D&R rules
- Returns: `resource_link` with complete rule set
- Use jq to: Find rules by name, check which are enabled, analyze detection logic

### Best Practices

1. **Request specific data**: Be clear about what information you need from large results
2. **Use the analyze script**: The analyze-lc-result.sh script helps you understand the data structure before querying
3. **Be patient**: Large files may take time to download and process
4. **Re-run if expired**: If the signed URL expires (403/404), re-run the original API call for a fresh link
5. **Avoid full dumps**: Don't request the complete dataset unless truly necessary

## Common API Paths

### Detection & Response
- GET `/rules/{oid}` - List D&R rules (add ?namespace=general or ?namespace=managed)
- POST `/rules/{oid}` - Create/update D&R rule
- DELETE `/rules/{oid}` - Delete D&R rule (name in body/query)

### Sensors
- GET `/sensors/{oid}` - List all sensors
- GET `/sensors/{oid}/{sid}` - Get specific sensor
- DELETE `/sensors/{oid}/{sid}` - Delete sensor

### Outputs
- GET `/outputs/{oid}` - List outputs
- POST `/outputs/{oid}` - Create output
- DELETE `/outputs/{oid}` - Delete output (name in body)

### Secrets
- GET `/secret/{oid}` - List secrets (returns names only)
- GET `/secret/{oid}/{secret_name}` - Get secret value
- POST `/secret/{oid}` - Create/update secret
- DELETE `/secret/{oid}/{secret_name}` - Delete secret

### Lookups
- GET `/insight/{oid}/lookup` - List lookups
- GET `/insight/{oid}/lookup/{lookup_name}` - Get lookup
- POST `/insight/{oid}/lookup/{lookup_name}` - Create/update lookup
- DELETE `/insight/{oid}/lookup/{lookup_name}` - Delete lookup

### YARA Rules
- GET `/yara/{oid}` - List YARA rules
- POST `/yara/{oid}` - Create/update YARA rule
- DELETE `/yara/{oid}` - Delete YARA rule (name in body)

### Historical Data
- POST `/` with `endpoint="replay"` - Run LCQL query (requires oid in body, auto-resolves replay URL)
- GET `/insight/{oid}/events` - Get historical events (time range in query params)
- GET `/insight/{oid}/detections` - Get historical detections

**Note:** LCQL queries use the `"replay"` endpoint which automatically resolves the per-organization replay instance URL. The path is always `/` (root) when using this endpoint.

## Error Handling

Always check `status_code` in response:

- **200-299**: Success, proceed with body data
- **400**: Bad request - check parameter format
- **401**: Unauthorized - authentication issue
- **403**: Forbidden - insufficient permissions
- **404**: Not found - resource doesn't exist
- **409**: Conflict - resource already exists or state conflict
- **429**: Rate limited - retry with backoff
- **500-599**: Server error - retry or report issue

## Best Practices

1. **Always validate OID**: Ensure you have a valid organization ID
2. **Check required parameters**: Review which fields are required for each endpoint
3. **Use appropriate HTTP method**: GET for reading, POST for creating, PUT for replacing, DELETE for removing
4. **Parse response body**: Most endpoints return JSON with structured data
5. **Handle errors gracefully**: Provide clear error messages to users based on status code
6. **Reference SDK code**: When unsure, check ../go-limacharlie/limacharlie/ for the Go SDK implementation
7. **Use form data for legacy endpoints**: Some older endpoints expect form-encoded data in body
8. **Include namespaces for rules**: D&R rules require namespace ("general" or "managed") in queries

## Examples by Category

### Example: List D&R Rules in General Namespace
```
lc_api_call(
  oid="abc123...",
  endpoint="api",
  method="GET",
  path="/rules/abc123...",
  query_params={"namespace": "general"}
)
```

### Example: Create Output
```
lc_api_call(
  oid="abc123...",
  endpoint="api",
  method="POST",
  path="/outputs/abc123...",
  body={
    "name": "my-syslog",
    "module": "syslog",
    "type": "event",
    "dest_host": "10.0.0.5",
    "dest_port": 514
  }
)
```

### Example: Get Secret Value
```
lc_api_call(
  oid="abc123...",
  endpoint="api",
  method="GET",
  path="/secret/abc123.../my-api-key"
)
```

### Example: Run LCQL Query
```
lc_api_call(
  oid="abc123...",
  endpoint="replay",
  method="POST",
  path="/",
  body={
    "oid": "abc123...",
    "query": "-24h | * | DNS_REQUEST | event.DOMAIN_NAME contains 'example.com'",
    "limit_event": 1000,
    "limit_eval": 10000,
    "event_source": {
      "stream": "event",
      "sensor_events": {
        "cursor": "-"
      }
    }
  }
)
```

**Note:** The `"replay"` endpoint automatically resolves the per-organization replay instance URL. Always include the `oid` field in the body when using this endpoint.

## When to Use This Tool

Use `lc_api_call` when:
- Implementing a skill that needs to interact with LimaCharlie API
- You know the exact API endpoint and parameters needed
- You want fine-grained control over the HTTP request
- You need to access endpoints not yet covered by dedicated MCP tools

## MCP Server Configuration

The `lc_api_call` tool is provided by the LimaCharlie MCP server configured in this plugin:
- **Server name**: `limacharlie`
- **Profile**: `api_access` (provides only the `lc_api_call` tool)
- **Tool reference**: `mcp__limacharlie__lc_api_call`
- **Server URL**: https://mcp.limacharlie.io/mcp/api_access

This MCP server is configured in `.claude-plugin/servers.json` and provides the minimal toolset needed for API access.

## Additional Resources

- Go SDK source: ../go-limacharlie/limacharlie/
- MCP tool implementations: ../lc-mcp-server/internal/tools/
- LimaCharlie API documentation: https://doc.limacharlie.io/
