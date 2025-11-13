---
name: delete-saved-query
description: Delete a saved LCQL query from the organization's hive storage by name. Permanently removes the query definition. Use to clean up query library, remove obsolete queries, fix naming mistakes, or manage query inventory.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Delete Saved Query

Delete a saved LCQL query from the organization's hive storage.

## When to Use

Use this skill when the user needs to:
- Remove obsolete queries
- Clean up query library
- Fix naming mistakes
- Delete duplicate queries
- Manage query inventory
- Remove unused saved searches

Common scenarios:
- "Delete the old-query saved query"
- "Remove the test-query query"
- "Clean up obsolete saved queries"
- "Delete query 'duplicate-search'"
- "Remove the broken query"

## What This Skill Does

This skill permanently deletes a saved query from hive storage by name.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID
- **query_name**: Name of the saved query to delete

## How to Use

### Step 1: Confirm Query Exists

Optionally, verify query exists first:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="GET",
  path="/hive/query/global/old-query/data"
)
```

### Step 2: Delete Query

```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/hive/query/global",
  body={
    "key": "old-query"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/hive/query/global`
- Body: `{"key": "query-name"}`

### Step 3: Handle Response

```json
{
  "status_code": 200,
  "body": {
    "success": true,
    "message": "Successfully deleted saved query 'old-query'"
  }
}
```

**Success (200):**
- Query is permanently deleted
- Cannot be recovered
- Returns confirmation message

**Common Errors:**
- **404 Not Found**: Query with that name doesn't exist
- **403 Forbidden**: Insufficient permissions to delete queries

### Step 4: Format Response

```
Query Deleted Successfully!

Deleted: old-query

The query has been permanently removed from your saved queries.
```

## Example Usage

### Example 1: Delete obsolete query

User: "Delete the old-query saved query"

Steps:
1. Confirm with user if deletion is intentional
2. Call DELETE API
3. Confirm deletion

### Example 2: Clean up test queries

User: "Remove all test queries"

Steps:
1. List saved queries
2. Filter for test queries
3. Delete each one (confirm first)

## Additional Notes

- Deletion is permanent and cannot be undone
- Query name is case-sensitive
- No confirmation prompt in API (implement in UI/skill logic)
- Consider backing up query LCQL before deletion
- Use list-saved-queries to verify deletion
- Deletion only affects saved queries, not historical data
- Does not affect query execution history
- Team members will immediately lose access to deleted query

## Reference

See [CALLING_API.md](../../CALLING_API.md).

SDK: `../go-limacharlie/limacharlie/hive.go`
MCP: `../lc-mcp-server/internal/tools/hive/saved_queries.go`
