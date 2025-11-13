---
name: list-extension-configs
description: List all extension configurations in a LimaCharlie organization. Use this skill when users need to view, inventory, audit, or manage extension configurations. Shows configuration data, enabled status, tags, comments, and metadata for all extensions. Essential for understanding what extensions are configured and their current settings.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List Extension Configurations

Lists all extension configurations stored in the Hive for a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- List all extension configurations in their organization
- View what extensions have custom configurations
- Audit extension settings and metadata
- Check which extensions are enabled or disabled
- Review extension configuration details before modifying them

Common scenarios:
- "Show me all my extension configurations"
- "What extensions do I have configured?"
- "List extension configs with their settings"
- "Which extensions are enabled in my organization?"

## What This Skill Does

This skill retrieves all extension configuration records from the LimaCharlie Hive system. It calls the Hive API using the "extension_config" hive name with the "global" partition to list all configurations. Each configuration includes the extension's data, enabled status, tags, comments, and system metadata (creation time, last modification, author, etc.).

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)

No other parameters are required.

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
  path="/hive/extension_config/global"
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/hive/extension_config/global`
- Query parameters: None
- Body: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "extension-name-1": {
      "data": {
        // Extension-specific configuration data
      },
      "sys_mtd": {
        "etag": "...",
        "created_by": "user@example.com",
        "created_at": 1234567890,
        "last_author": "user@example.com",
        "last_mod": 1234567899,
        "guid": "...",
        "last_error": "",
        "last_error_ts": 0
      },
      "usr_mtd": {
        "enabled": true,
        "expiry": 0,
        "tags": ["tag1", "tag2"],
        "comment": "Description of this config"
      }
    },
    "extension-name-2": {
      // ... another extension config
    }
  }
}
```

**Success (200-299):**
- The response body is an object where each key is an extension name
- Each value contains `data` (configuration), `sys_mtd` (system metadata), and `usr_mtd` (user metadata)
- Present the list of extensions with their enabled status and key configuration details
- Count the total number of configured extensions

**Common Errors:**
- **403 Forbidden**: Insufficient permissions - user needs platform_admin or similar role to access Hive
- **404 Not Found**: The hive or partition doesn't exist (unusual, should always exist)
- **500 Server Error**: Rare backend issue - advise user to retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Show a summary count of how many extensions are configured
- List each extension name with its enabled status
- Highlight key configuration details from the data field
- Note any extensions with tags or comments
- Show creation and last modification timestamps for audit purposes

## Example Usage

### Example 1: List all extension configurations

User request: "Show me all my extension configurations"

Steps:
1. Get the organization ID from context
2. Call the Hive API to list extension configs
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/extension_config/global"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "artifact-collection": {
      "data": {
        "retention_days": 90,
        "max_size_mb": 100
      },
      "sys_mtd": {
        "created_at": 1700000000,
        "last_mod": 1700001000,
        "last_author": "admin@example.com"
      },
      "usr_mtd": {
        "enabled": true,
        "tags": ["production"],
        "comment": "Artifact collection config"
      }
    },
    "logging": {
      "data": {
        "destinations": ["s3://bucket/path"]
      },
      "sys_mtd": {
        "created_at": 1699000000,
        "last_mod": 1699000000
      },
      "usr_mtd": {
        "enabled": false,
        "tags": []
      }
    }
  }
}
```

Format the output showing:
- Total: 2 extension configurations
- artifact-collection: Enabled, retention 90 days
- logging: Disabled, S3 destination configured

### Example 2: Check which extensions are enabled

User request: "Which of my extension configs are currently enabled?"

Steps:
1. Get organization ID
2. List all extension configs
3. Filter and present only those with `usr_mtd.enabled = true`

The same API call is used, but the response is filtered to show only enabled extensions.

## Additional Notes

- Extension configurations are stored in the Hive system, separate from extension subscriptions
- An extension subscription must exist for its configuration to be meaningful
- The `enabled` field in `usr_mtd` controls whether the configuration is active
- Tags can be used for filtering and organizing extension configs
- The `data` field structure varies by extension type - each extension defines its own schema
- System metadata is automatically managed and shows audit trail information
- Empty result (no configs) is valid and means no extensions have been configured yet
- Use the `get-extension-config` skill to retrieve a specific extension's full configuration

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/extension_configs.go`
