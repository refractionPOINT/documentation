---
name: list-user-orgs
description: List all LimaCharlie organizations accessible to the authenticated user with optional filtering and sorting. Use this skill when viewing available organizations, switching between orgs, managing multi-tenant access, or auditing user permissions across organizations. Returns org IDs, names, and access details.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# List User Organizations

Retrieve all LimaCharlie organizations accessible to the current authenticated user.

## When to Use

Use this skill when the user needs to:
- View all organizations they have access to
- Switch between multiple organizations
- Audit organization access and permissions
- Find organization IDs for API operations
- Manage multi-tenant or MSP deployments
- Review customer organization list

Common scenarios:
- MSPs managing multiple customer organizations
- Users with access to multiple business units
- Finding specific organization by name
- Auditing user access across organizations
- Preparing organization selection menus
- Documenting organization inventory

## What This Skill Does

This skill lists all organizations accessible to the authenticated user. It calls the LimaCharlie API at the user level (not organization-scoped) to retrieve the complete list of orgs the user can access, along with organization names and metadata. Results can be filtered and sorted.

## Required Information

Before calling this skill, gather:

**⚠️ NOTE**: This is a **user-level operation** that does not require a specific organization ID. When calling the API, **omit the `oid` parameter** entirely. This skill is used to discover organization IDs and names.

No required parameters (user-level query)

Optional parameters:
- **filter**: Filter string to match organization names (optional)
- **sort_by**: Field to sort results by (optional)
- **sort_order**: Sort direction "asc" or "desc" (optional)
- **with_names**: Include organization names (default: true)

## How to Use

### Step 1: Validate Parameters

This is a user-level query - minimal validation required.
Optional filters and sorting can refine results.

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  endpoint="api",
  method="GET",
  path="/user/orgs",
  query_params={
    "filter": "[optional-filter]",
    "sort_by": "[optional-field]",
    "sort_order": "[asc|desc]",
    "offset": "[pagination-offset]",
    "limit": "[pagination-limit]"
  }
  # Note: oid parameter omitted - not required for user-level operations
)
```

**API Details:**
- Endpoint: `api`
- Method: `GET`
- Path: `/user/orgs`
- Query parameters (all optional):
  - `filter`: String to filter organization names
  - `sort_by`: Field name to sort by
  - `sort_order`: "asc" or "desc"
  - `offset`: Pagination offset (for large lists)
  - `limit`: Number of results per page
- Body fields: None

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "orgs": [
      {
        "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
        "name": "Production Environment",
        "role": "owner"
      },
      {
        "oid": "c7e8f940-5678-1234-dcba-0987654321ab",
        "name": "Development Environment",
        "role": "admin"
      }
    ],
    "total": 2
  }
}
```

**Success (200-299):**
- Response contains array of organization objects
- Each org includes OID, name, and user's role
- Total count may be included for pagination
- Empty array means user has no organization access
- Results respect filter and sort parameters

**Common Errors:**
- **401 Unauthorized**: Authentication issue
- **403 Forbidden**: User context issue (rare)
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- List organizations with names and IDs
- Show user's role in each organization
- Group by role level if multiple orgs
- Highlight currently active organization
- Format for easy selection or reference
- Show total count if large list

## Example Usage

### Example 1: List all accessible organizations

User request: "Show me all my organizations"

Steps:
1. Call API to list user orgs:
```
mcp__limacharlie__lc_api_call(
  endpoint="api",
  method="GET",
  path="/user/orgs"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "orgs": [
      {
        "oid": "c7e8f940-1111-2222-3333-444455556666",
        "name": "Acme Production",
        "role": "owner"
      },
      {
        "oid": "c7e8f940-7777-8888-9999-aaabbbcccddd",
        "name": "Acme Development",
        "role": "owner"
      },
      {
        "oid": "c7e8f940-eeee-ffff-0000-111122223333",
        "name": "Customer XYZ",
        "role": "admin"
      }
    ],
    "total": 3
  }
}
```

Present to user:
```
Your LimaCharlie Organizations

You have access to 3 organizations:

Organizations You Own:
1. Acme Production
   ID: c7e8f940-1111-2222-3333-444455556666
   Role: Owner

2. Acme Development
   ID: c7e8f940-7777-8888-9999-aaabbbcccddd
   Role: Owner

Organizations with Admin Access:
3. Customer XYZ
   ID: c7e8f940-eeee-ffff-0000-111122223333
   Role: Admin

Use the organization ID for API operations.
```

### Example 2: Find specific organization by name

User request: "What's the org ID for 'Customer XYZ'?"

Steps:
1. List orgs with filter:
```
mcp__limacharlie__lc_api_call(
  endpoint="api",
  method="GET",
  path="/user/orgs",
  query_params={
    "filter": "Customer XYZ"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "orgs": [
      {
        "oid": "c7e8f940-eeee-ffff-0000-111122223333",
        "name": "Customer XYZ",
        "role": "admin"
      }
    ]
  }
}
```

Present to user:
```
Found Organization: Customer XYZ

Organization ID: c7e8f940-eeee-ffff-0000-111122223333
Your Role: Admin
Status: Active

This ID can be used for API calls and CLI operations.
```

### Example 3: List MSP customer organizations

User request: "Show me all our customer organizations"

Steps:
1. List all orgs and filter/group by type
2. Present customer orgs separately

Present to user:
```
MSP Customer Organizations

You manage 15 customer organizations:

Active Customers (12):
1. ABC Corp Security (oid: c7e8f940-aaaa-...)
2. DEF Industries (oid: c7e8f940-bbbb-...)
3. GHI Enterprises (oid: c7e8f940-cccc-...)
...

Trial Customers (3):
13. JKL Startup (oid: c7e8f940-dddd-...)
14. MNO Tech (oid: c7e8f940-eeee-...)
15. PQR Solutions (oid: c7e8f940-ffff-...)

Internal Organizations (2):
- Your Production (oid: c7e8f940-0000-...)
- Your Development (oid: c7e8f940-1111-...)

Total: 17 organizations
```

## Additional Notes

- **This is a user-level operation that does not require a specific organization ID**
- When calling the API, omit the `oid` parameter entirely
- This skill is the starting point for discovering organization IDs
- This is not organization-specific
- Results show only orgs the user has explicit access to
- Role levels: owner, admin, user (permissions vary)
- Large result sets support pagination via offset/limit
- Filtering helps find specific organizations quickly
- Organization names can be changed without affecting OIDs
- OIDs are permanent unique identifiers
- Use OIDs for all API operations and automation
- Some operations require owner or admin role
- For MSPs: This lists all customer organizations
- Consider caching org list for performance in UIs

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (ListUserOrgs function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterListUserOrgs)
