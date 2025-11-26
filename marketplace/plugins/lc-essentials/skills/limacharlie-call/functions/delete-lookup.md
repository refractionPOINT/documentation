
# Delete Lookup

This skill deletes a lookup table from LimaCharlie. Deletion is immediate and cannot be undone.

## When to Use

Use this skill when the user needs to:
- Remove an outdated or unused lookup table
- Delete test or temporary lookup data
- Clean up old threat intelligence feeds
- Remove deprecated reference data
- Delete lookups before replacing with updated data
- Free up resources from large unused lookups

Common scenarios:
- "Delete the old-threat-ips lookup table"
- "Remove the test-lookup"
- "Clean up unused lookup tables"
- "Delete the deprecated allowlist"
- "I need to replace the lookup completely, delete it first"

## What This Skill Does

This skill calls the LimaCharlie API to permanently delete a lookup table. Any D&R rules or queries that reference the deleted lookup will fail or return null. The deletion is immediate and cannot be reversed.

## Required Information

Before calling this skill, gather:

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Name of the lookup table to delete

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact lookup table name (case-sensitive)
3. Confirmation that the lookup is not being used
4. Understanding that deletion is permanent

### Step 2: Call the API

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_lookup",
  parameters={
    "oid": "[organization-id]",
    "name": "[lookup-name]"
  }
)
```

**API Details:**
- Tool: `delete_lookup`
- Required parameters:
  - `oid`: Organization ID
  - `name`: Name of the lookup table to delete

### Step 3: Handle the Response

The API returns a response with:
```json
{}
```

**Success:**
- Lookup table is deleted immediately
- Response body is typically empty or contains confirmation
- Lookup name is now available for reuse
- D&R rules referencing this lookup will fail

**Common Errors:**
- **404 Not Found**: Lookup table with this name doesn't exist - verify exact name
- **403 Forbidden**: Insufficient permissions - user needs write access to lookups
- **401 Unauthorized**: Authentication issue with API credentials
- **500 Server Error**: LimaCharlie service issue - rare, retry or report

### Step 4: Format the Response

Present the result to the user:
- Confirm deletion with lookup name
- Warn about impact:
  - D&R rules using this lookup will fail
  - LCQL queries referencing it will return null
  - Cannot be undone
- Suggest:
  - Verify no D&R rules are using the lookup
  - Check for any detection failures after deletion
  - Create replacement lookup if data was updated

## Example Usage

### Example 1: Delete unused lookup

User request: "Delete the test-lookup table, we don't need it anymore"

Steps:
1. Confirm lookup name: "test-lookup"
2. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "test-lookup"
  }
)
```

Expected response:
```json
{}
```

Format output:
```
Successfully deleted lookup table "test-lookup"

The lookup table has been permanently removed.
Any D&R rules or queries referencing this lookup will no longer work.

The lookup name is now available for reuse if needed.
```

### Example 2: Delete before updating

User request: "I have updated threat intelligence. Delete the old-threat-ips lookup so I can load the new data"

Steps:
1. Confirm approach (could also just update existing)
2. Delete old lookup:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "old-threat-ips"
  }
)
```

Format output:
```
Successfully deleted lookup table "old-threat-ips"

The old threat intelligence data has been removed.

You can now create a new lookup with updated data using the same name
or a different name. If D&R rules reference "old-threat-ips", you may
want to use the same name for the new lookup.

Note: You can also update lookups without deleting by using set-lookup,
which replaces the data automatically.

Would you like me to create the new lookup table now?
```

### Example 3: Lookup not found

User request: "Delete the nonexistent-lookup"

Steps:
1. Call API:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_lookup",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "nonexistent-lookup"
  }
)
```

Expected response:
```json
{
  "error": "Lookup not found"
}
```

Format output:
```
Error: Lookup table "nonexistent-lookup" not found.

The lookup may have already been deleted or the name might be incorrect.
Lookup names are case-sensitive.

Would you like me to list all lookup tables to see what exists?
```

### Example 4: Check for usage before deletion

User request: "Can I safely delete the malicious-ips lookup?"

Steps:
1. Check D&R rules for references (if possible)
2. Warn user about potential impact
3. Format output:
```
Warning: Before deleting "malicious-ips", check if it's being used.

To check D&R rules:
1. List all D&R rules and search for: lookup('malicious-ips'
2. Review any rules that reference this lookup
3. Update or disable those rules before deleting the lookup

Common usage patterns to search for:
- lookup('malicious-ips', ...)
- Enrichment in respond actions
- Filters in detect conditions

Would you like me to proceed with deletion, or would you like to
review D&R rules first?
```

## Additional Notes

- Deletion is immediate and permanent
- Cannot undo lookup deletion
- D&R rules using deleted lookups will fail:
  - `lookup('deleted-table', key)` returns null
  - Rules may generate errors or unexpected behavior
- Check for lookup usage before deleting:
  - Search D&R rules for `lookup('lookup-name'`
  - Review LCQL queries
  - Check dashboards or reports
- Lookup names are case-sensitive - must match exactly
- Best practices for lookup updates:
  - **Simple update**: Use set-lookup to replace data (no delete needed)
  - **Major change**: Delete old, create new with different name, update rules
  - **Rename**: Create new with new name, update rules, delete old
- After deletion, monitor for:
  - D&R rule errors
  - Unexpected null values in detections
  - Missing enrichment data
- Lookup name becomes available for reuse immediately
- Related skills: `list_lookups` to see all tables, `get_lookup` to view before deleting, `set_lookup` to create replacements

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/config/lookups.go`
