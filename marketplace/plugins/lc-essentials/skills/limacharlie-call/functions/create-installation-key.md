
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

This skill creates a new installation key in the LimaCharlie organization. Installation keys are credentials used to deploy and enroll sensors. When sensors are deployed using a specific key, they automatically receive the tags associated with that key. This enables automatic organizational grouping and policy application. The skill calls the LimaCharlie MCP tool to generate the key and returns the new key's IID (installation key ID) and the actual key value for deployment.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **tags**: Array of tags to automatically apply to sensors using this key (required)
- **description**: Human-readable description of the key's purpose (required)

Optional parameters:
- **use_public_root_ca**: Whether to use public CA for certificate validation (optional, defaults to false)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. At least one tag in the tags array
3. Meaningful description string
4. Consider what tags best represent the sensor group (e.g., environment, OS, location)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "[organization-id]",
    "description": "Description of the installation key",
    "tags": ["tag1", "tag2", "tag3"]
  }
)
```

**Tool Details:**
- Tool Name: `create_installation_key`
- Required Parameters:
  - `oid`: Organization ID
  - `description`: Human-readable description of the key's purpose
  - `tags`: Array of tag strings to apply to sensors using this key

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "iid": "generated-installation-key-id",
  "key": "the-actual-key-value-for-deployment",
  "json_key": "{...json-formatted-key...}"
}
```

**Success:**
- The response contains the newly created installation key
- `iid`: Unique identifier for this installation key
- `key`: The actual key value to use for sensor deployment
- `json_key`: JSON-formatted version of the key for certain deployment scenarios
- Save the key value securely as it's needed for sensor deployment

**Common Errors:**
- **Invalid parameters**: Missing required fields (tags or description), invalid tag format, or malformed request
- **Unauthorized**: Authentication token is invalid or expired
- **Forbidden**: Insufficient permissions to create installation keys (requires platform_admin role)
- **Conflict**: Installation key with the same IID already exists (if IID was provided)

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
4. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "description": "Production Windows Servers",
    "tags": ["production", "windows", "server"]
  }
)
```

Expected response:
```json
{
  "iid": "prod-win-server-key",
  "key": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
  "json_key": "{\"oid\":\"c7e8f940-1234-5678-abcd-1234567890ab\",\"iid\":\"prod-win-server-key\",\"key\":\"abcd1234-5678-90ef-ghij-klmnopqrstuv\"}"
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
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "description": "Development Linux Workstations",
    "tags": ["development", "linux", "workstation"]
  }
)
```

Expected response:
```json
{
  "iid": "dev-linux-ws-key",
  "key": "wxyz9876-5432-10ab-cdef-ghijklmnopqr",
  "json_key": "{\"oid\":\"c7e8f940...\",\"iid\":\"dev-linux-ws-key\"...}"
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
- If you specify an IID manually, ensure it's unique within the organization to avoid conflicts
- Use the list-installation-keys skill to view all existing keys
- Use the delete-installation-key skill to remove keys that are no longer needed
- Keep a secure record of installation keys as they may be needed for future deployments

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/installation_keys.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/config/installation_keys.go`
