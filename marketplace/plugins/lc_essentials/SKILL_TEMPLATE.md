# SKILL TEMPLATE - DO NOT USE DIRECTLY

This is a template for creating new skills. Copy this structure and fill in the specific details for each MCP tool.

## SKILL.md Structure

```yaml
---
name: tool-name-in-kebab-case
description: Clear, concise description of what this skill does and when Claude should use it. Include key trigger words and use cases. Maximum 1024 characters.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# [Tool Name in Title Case]

Brief overview of what this skill does (1-2 sentences).

## When to Use

Use this skill when the user needs to:
- [Specific use case 1]
- [Specific use case 2]
- [Specific use case 3]

Common scenarios:
- [Scenario 1 with context]
- [Scenario 2 with context]

## What This Skill Does

This skill [detailed explanation of functionality]. It calls the LimaCharlie API to [specific operation].

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **[param1]**: [Description and format]
- **[param2]**: [Description and format]

Optional parameters:
- **[optional-param]**: [Description and when to use]

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. [Other required parameters]
3. [Validation checks if needed]

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="[GET|POST|PUT|DELETE]",
  path="/[api-path]/[oid]",
  [query_params={"param": "value"}]  # if needed
  [body={"field": "value"}]  # if needed for POST/PUT
)
```

**API Details:**
- Endpoint: `api` (or `billing` if billing-related)
- Method: `[HTTP-METHOD]`
- Path: `/[exact-api-path]/[oid-placeholder]`
- Query parameters: [Describe query params if any]
- Body fields: [Describe body structure if POST/PUT]

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    // Response structure specific to this endpoint
  }
}
```

**Success (200-299):**
- [What the response contains]
- [How to interpret the data]
- [What to do with the result]

**Common Errors:**
- **400 Bad Request**: [What causes this and how to fix]
- **404 Not Found**: [What causes this and how to fix]
- **403 Forbidden**: [Insufficient permissions - what's needed]
- **500 Server Error**: [Rare, but what to tell user]

### Step 4: Format the Response

Present the result to the user:
- [How to format the output]
- [What information to highlight]
- [Any warnings or notes to include]

## Example Usage

### Example 1: [Common scenario]

User request: "[Example user request]"

Steps:
1. [Step 1]
2. [Step 2]
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="abc123...",
  endpoint="api",
  method="GET",
  path="/example/abc123..."
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    // Example response
  }
}
```

### Example 2: [Edge case or complex scenario]

User request: "[Another example]"

[Similar structure as Example 1]

## Additional Notes

- [Any special considerations]
- [Related skills that might be useful]
- [Common gotchas or limitations]
- [Best practices specific to this operation]

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/[relevant-file].go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/[category]/[tool-file].go`
```

## Key Points for Skill Creation

1. **Name**: Use kebab-case matching the snake_case MCP tool name
2. **Description**: Rich with keywords, use cases, and trigger words (max 1024 chars)
3. **Allowed Tools**: Always include the lc_api_call tool and Read tool
4. **Structure**: Follow the template structure for consistency
5. **Examples**: Include at least 2 concrete examples
6. **Error Handling**: Document common error codes and how to handle them
7. **API Details**: Be specific about endpoint, method, path, parameters
8. **Response Handling**: Explain what comes back and how to use it

## Common Patterns by Operation Type

### List Operations (GET with no params)
- Method: GET
- Path usually ends with /{oid}
- No body, no query params usually
- Returns array or object of resources

### Get Single Resource (GET with identifier)
- Method: GET
- Path includes resource identifier or uses query params
- Returns single resource object

### Create Operations (POST)
- Method: POST
- Body contains resource configuration
- Path usually ends with /{oid}
- Returns created resource

### Update Operations (POST/PUT)
- Method: POST or PUT
- Body contains updated configuration
- May include resource name/id in body or path
- Returns updated resource

### Delete Operations (DELETE)
- Method: DELETE
- Resource identifier in body or path
- Returns success confirmation

## Discovery Optimization

To make skills easily discoverable:
- Include action verbs in description (list, get, create, delete, update, search, scan, etc.)
- Include domain keywords (sensor, rule, detection, output, secret, etc.)
- Include use case keywords (security, investigation, incident response, compliance, etc.)
- Include related concepts (YARA for malware, LCQL for querying, etc.)
- Mention common user intents (troubleshoot, investigate, monitor, alert, etc.)