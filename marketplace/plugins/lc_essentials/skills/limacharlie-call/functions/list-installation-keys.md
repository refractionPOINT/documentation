
# List Installation Keys

Retrieve all installation keys configured in a LimaCharlie organization, including their properties and metadata.

## When to Use

Use this skill when the user needs to:
- View all available installation keys in the organization
- Check which installation keys exist for sensor deployment
- Audit installation key configurations and tags
- Find a specific installation key by description or tags
- Review key creation dates and associated metadata

Common scenarios:
- Planning new sensor deployments and checking available keys
- Security audits of sensor deployment credentials
- Troubleshooting sensor enrollment issues
- Identifying which keys to use for specific sensor groups
- Managing and organizing installation keys

## What This Skill Does

This skill retrieves a complete list of all installation keys in the organization. Installation keys are credentials used to deploy LimaCharlie sensors to endpoints. Each key can automatically apply tags to sensors that use it for enrollment. The skill calls the LimaCharlie MCP tool to fetch all keys along with their metadata including IID (installation key ID), description, tags, creation timestamp, and the actual key values.

## Required Information

Before calling this skill, gather:

**IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)

No additional parameters are needed.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="list_installation_keys",
  parameters={
    "oid": "[organization-id]"
  }
)
```

**Tool Details:**
- Tool Name: `list_installation_keys`
- Required Parameters:
  - `oid`: Organization ID

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "{oid}": {
    "{iid-1}": {
      "iid": "installation-key-id",
      "desc": "Description of the key",
      "tags": "tag1,tag2,tag3",
      "key": "actual-key-value",
      "json_key": "json-formatted-key",
      "created": 1234567890,
      "use_public_root_ca": false
    },
    "{iid-2}": { ... }
  }
}
```

**Success:**
- The response contains a nested object structure
- Top level key is the organization ID
- Each installation key is keyed by its IID (installation key ID)
- Key properties include:
  - `iid`: Unique identifier for the installation key
  - `desc`: Human-readable description
  - `tags`: Comma-separated list of tags to apply to sensors
  - `key`: The actual installation key value for sensor deployment
  - `json_key`: JSON-formatted version of the key
  - `created`: Unix timestamp of when the key was created
  - `use_public_root_ca`: Boolean indicating if public CA is used

**Common Errors:**
- **Invalid organization ID**: Organization ID format is invalid
- **Unauthorized**: Authentication token is invalid or expired
- **Forbidden**: Insufficient permissions to view installation keys (requires platform_admin role)
- **Not Found**: Organization does not exist

### Step 4: Format the Response

Present the result to the user:
- Display each installation key with its key properties
- Show the IID, description, and associated tags clearly
- Format the creation timestamp as a human-readable date
- If the user is looking for a specific key, filter results by description or tags
- Provide a count of total installation keys found
- Include guidance on which key might be suitable for their use case

## Example Usage

### Example 1: List all installation keys

User request: "Show me all the installation keys"

Steps:
1. Extract the organization ID from context
2. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="list_installation_keys",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab"
  }
)
```

Expected response:
```json
{
  "c7e8f940-1234-5678-abcd-1234567890ab": {
    "prod-windows-key": {
      "iid": "prod-windows-key",
      "desc": "Production Windows Servers",
      "tags": "production,windows,server",
      "key": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
      "json_key": "{\"oid\":\"c7e8f940...\",\"iid\":\"prod-windows-key\"...}",
      "created": 1704067200,
      "use_public_root_ca": false
    },
    "dev-linux-key": {
      "iid": "dev-linux-key",
      "desc": "Development Linux Workstations",
      "tags": "development,linux,workstation",
      "key": "wxyz9876-5432-10ab-cdef-ghijklmnopqr",
      "json_key": "{\"oid\":\"c7e8f940...\",\"iid\":\"dev-linux-key\"...}",
      "created": 1704153600,
      "use_public_root_ca": false
    }
  }
}
```

Present to user:
```
Found 2 installation keys:

1. Production Windows Servers (prod-windows-key)
   - Tags: production, windows, server
   - Created: January 1, 2024
   - Key: abcd1234-5678-90ef-ghij-klmnopqrstuv

2. Development Linux Workstations (dev-linux-key)
   - Tags: development, linux, workstation
   - Created: January 2, 2024
   - Key: wxyz9876-5432-10ab-cdef-ghijklmnopqr
```

### Example 2: Find installation keys for production

User request: "Which installation keys are for production?"

Steps:
1. Call tool to get all keys
2. Filter results for keys with "production" in tags or description
3. Present filtered results:
```
Found 1 installation key for production:

Production Windows Servers (prod-windows-key)
- Tags: production, windows, server
- Created: January 1, 2024
- Key: abcd1234-5678-90ef-ghij-klmnopqrstuv
```

## Additional Notes

- Installation keys are sensitive credentials and should be handled securely
- The `key` field contains the actual credential used for sensor deployment
- Tags specified in an installation key are automatically applied to sensors during enrollment
- Multiple sensors can use the same installation key
- Keys can be identified by their IID (installation key ID)
- The `use_public_root_ca` field indicates certificate validation behavior
- If no installation keys exist, the response will contain an empty object for the organization
- Consider using the create-installation-key skill to create new keys if none exist

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/installation_keys.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/config/installation_keys.go`
