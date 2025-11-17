
# Create Installation Key

Generate a new installation key for deploying LimaCharlie sensors with automatic tag assignment.

## When to Use

Use this skill when the user needs to:
- Create a new installation key for sensor deployment
- Generate deployment credentials for a specific environment or group
- Set up keys with automatic tagging for organizational structure
- Create keys with descriptions for easy identification
- Establish separate keys for different teams, locations, or purposes

Common scenarios:
- Setting up sensor deployment for a new project or environment
- Creating segregated keys for production vs. development systems
- Generating keys with specific tags for automated sensor organization
- Establishing deployment credentials for different geographic regions
- Creating keys for specific OS platforms or server types

## What This Skill Does

This skill creates a new installation key in the LimaCharlie organization. Installation keys are credentials used to deploy and enroll sensors. When sensors are deployed using a specific key, they automatically receive the tags associated with that key. This enables automatic organizational grouping and policy application. The skill calls the LimaCharlie API to generate the key and returns the new key's IID (installation key ID) and the actual key value for deployment.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **tags**: Array of tags to automatically apply to sensors using this key (required)
- **description**: Human-readable description of the key's purpose (required)

Optional parameters:
- **quota**: Maximum number of sensors that can use this key (optional, not currently supported by SDK)
- **use_public_root_ca**: Whether to use public CA for certificate validation (optional, defaults to false)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. At least one tag in the tags array
3. Meaningful description string
4. Consider what tags best represent the sensor group (e.g., environment, OS, location)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/installationkeys/[oid]",
  body={
    "tags": ["tag1", "tag2", "tag3"],
    "desc": "Description of the installation key",
    "use_public_root_ca": false
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/installationkeys/{oid}`
- Query parameters: None
- Body fields:
  - `tags`: Array of tag strings (required) - can also be comma-separated string
  - `desc`: Description string (required)
  - `use_public_root_ca`: Boolean (optional, defaults to false)
  - `iid`: Installation key ID (optional, auto-generated if not provided)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "iid": "generated-installation-key-id",
    "key": "the-actual-key-value-for-deployment",
    "json_key": "{...json-formatted-key...}"
  }
}
```

**Success (200-299):**
- The response contains the newly created installation key
- `iid`: Unique identifier for this installation key
- `key`: The actual key value to use for sensor deployment
- `json_key`: JSON-formatted version of the key for certain deployment scenarios
- Save the key value securely as it's needed for sensor deployment

**Common Errors:**
- **400 Bad Request**: Missing required fields (tags or desc), invalid tag format, or malformed request body
- **401 Unauthorized**: Authentication token is invalid or expired
- **403 Forbidden**: Insufficient permissions to create installation keys (requires platform_admin role)
- **409 Conflict**: Installation key with the same IID already exists (if IID was provided)
- **500 Server Error**: Internal server error, retry the request

### Step 4: Format the Response

Present the result to the user:
- Display a success message confirming the key was created
- Show the installation key ID (IID)
- Display the actual key value prominently
- Remind the user to save the key securely
- List the tags that will be automatically applied to sensors
- Provide guidance on how to use the key for sensor deployment
- If applicable, mention the deployment documentation or next steps

## Example Usage

### Example 1: Create key for production Windows servers

User request: "Create an installation key for production Windows servers with tags production, windows, and server"

Steps:
1. Extract organization ID from context
2. Prepare tags array: ["production", "windows", "server"]
3. Create descriptive string
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/installationkeys/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "tags": ["production", "windows", "server"],
    "desc": "Production Windows Servers",
    "use_public_root_ca": false
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "iid": "prod-win-server-key",
    "key": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
    "json_key": "{\"oid\":\"c7e8f940-1234-5678-abcd-1234567890ab\",\"iid\":\"prod-win-server-key\",\"key\":\"abcd1234-5678-90ef-ghij-klmnopqrstuv\"}"
  }
}
```

Present to user:
```
Successfully created installation key!

Installation Key ID: prod-win-server-key
Description: Production Windows Servers
Tags: production, windows, server

Installation Key:
abcd1234-5678-90ef-ghij-klmnopqrstuv

Save this key securely. Use it to deploy sensors to your production Windows servers.
All sensors enrolled with this key will automatically receive the tags: production, windows, server
```

### Example 2: Create key for development Linux workstations

User request: "I need a deployment key for our dev team's Linux workstations"

Steps:
1. Extract organization ID
2. Determine appropriate tags: ["development", "linux", "workstation"]
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/v1/installationkeys/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "tags": ["development", "linux", "workstation"],
    "desc": "Development Linux Workstations"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "iid": "dev-linux-ws-key",
    "key": "wxyz9876-5432-10ab-cdef-ghijklmnopqr",
    "json_key": "{\"oid\":\"c7e8f940...\",\"iid\":\"dev-linux-ws-key\"...}"
  }
}
```

Present to user:
```
Installation key created for development Linux workstations!

Key ID: dev-linux-ws-key
Key: wxyz9876-5432-10ab-cdef-ghijklmnopqr
Auto-applied tags: development, linux, workstation

Your dev team can use this key to deploy sensors to their Linux workstations.
```

## Additional Notes

- Installation keys are sensitive credentials - handle them securely and don't expose them in logs or public repositories
- Tags are automatically applied to sensors during enrollment, enabling immediate policy application and organization
- Choose descriptive tag names that align with your organizational structure (environment, OS, location, team, etc.)
- The description field should clearly indicate the key's purpose for easy identification later
- Multiple sensors can use the same installation key
- Consider creating separate keys for different environments (production, staging, development)
- The quota parameter is not currently supported by the SDK but may be added in future versions
- If you specify an IID manually, ensure it's unique within the organization to avoid conflicts
- Use the list-installation-keys skill to view all existing keys
- Use the delete-installation-key skill to remove keys that are no longer needed
- Keep a secure record of installation keys as they may be needed for future deployments

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/installation_keys.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/config/installation_keys.go`
