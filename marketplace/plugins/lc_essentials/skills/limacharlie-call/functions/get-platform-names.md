
# Get Platform Names

Retrieve the official list of platform names from LimaCharlie's ontology, providing the canonical identifiers for all supported platforms.

## When to Use

Use this skill when the user needs to:
- Get the correct platform identifier for API calls
- Discover what platforms LimaCharlie supports
- Validate platform names before filtering operations
- Build cross-platform detection logic
- Understand platform taxonomy

Common scenarios:
- "What platforms does LimaCharlie support?"
- "What's the correct name for Windows in the API?"
- "Show me all available platform identifiers"
- "I need to filter by platform - what are the valid names?"

## What This Skill Does

This skill retrieves the authoritative list of platform names from LimaCharlie's ontology endpoint. These are the canonical platform identifiers used throughout the LimaCharlie API for filtering sensors, event types, and building platform-specific rules. Note that this returns the platform ontology, not necessarily platforms with active sensors in the organization.

## Required Information

Before calling this skill, gather:

**⚠️ NOTE**: This is a **global operation** that queries the platform ontology and does not require a specific organization ID. When calling the API, **omit the `oid` parameter** entirely.

No specific parameters required (global ontology query)

Note: The ontology endpoint returns the global platform list, not organization-specific platforms.

## How to Use

### Step 1: Validate Parameters

This is a global query - no specific validation required.

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  endpoint="api",
  method="GET",
  path="/v1/ontology"
  # Note: oid parameter omitted - not required for global operations
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/ontology`
- No query parameters
- No request body
- Global endpoint - does not require organization context

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "platforms": {
      "windows": 1,
      "linux": 2,
      "macos": 3,
      "chrome": 4,
      "android": 5,
      "ios": 6,
      ...
    }
  }
}
```

**Success (200-299):**
- Body contains `platforms` object mapping platform names to numeric IDs
- Platform names are lowercase strings (e.g., "windows", "linux", "macos")
- Numeric values are internal platform identifiers
- Keys (platform names) are what you use in other API calls
- This is the authoritative source for platform naming

**Common Errors:**
- **500 Server Error**: Temporary API issue - retry after a short delay

### Step 4: Format the Response

Present the result to the user:
- Extract platform names from the response object keys
- List platforms in a logical order (common platforms first)
- Group by category if helpful (desktop, mobile, cloud)
- Indicate which platforms are most commonly used
- Note that this is the global list, not org-specific

## Example Usage

### Example 1: Getting all platform names

User request: "What platforms does LimaCharlie support?"

Steps:
1. Call API:
```
mcp__limacharlie__lc_api_call(
  endpoint="api",
  method="GET",
  path="/v1/ontology"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "platforms": {
      "windows": 1,
      "linux": 2,
      "macos": 3,
      "chrome": 4,
      "android": 5,
      "ios": 6
    }
  }
}
```

Present to user: "LimaCharlie supports the following platforms: Windows, Linux, macOS, Chrome OS, Android, and iOS. Use these lowercase names (windows, linux, macos, chrome, android, ios) when filtering by platform in API calls."

### Example 2: Validating platform name before filtering

User request: "I want to filter events for Mac computers"

Steps:
1. Get platform names
2. Identify that "macos" is the correct platform identifier (not "mac" or "osx")
3. Inform user of the correct name: "macos"
4. Use this in subsequent platform filtering operations

## Additional Notes

- **This is a global operation that does not require a specific organization ID**
- When calling the API, omit the `oid` parameter entirely
- This endpoint returns the global platform ontology, not org-specific data
- Platform names are always lowercase in the API
- Use exactly these names when filtering (e.g., "windows" not "Windows" or "win")
- The numeric platform IDs are for internal use - use the string names in API calls
- Just because a platform is listed doesn't mean the organization has sensors on it
- Use `list-with-platform` to see which platforms have active sensors
- Common platforms: windows, linux, macos, chrome
- Mobile platforms: android, ios
- Platform names are stable and rarely change
- These same platform names are used in sensor selectors and D&R rules

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/go-limacharlie/limacharlie/schemas.go`
For the MCP tool implementation, check: `/lc-mcp-server/internal/tools/schemas/schemas.go`
