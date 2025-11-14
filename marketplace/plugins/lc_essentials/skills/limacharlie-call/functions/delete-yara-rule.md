
# Delete YARA Rule

Delete a specific YARA rule source from the organization by name.

## When to Use

Use this skill when the user needs to:
- Delete a YARA rule
- Remove outdated malware signatures
- Clean up unused YARA rules
- Decommission threat detection rules
- Remove incorrectly configured YARA rules

Common scenarios:
- Cleanup: "Delete the 'old_malware_sigs' YARA rule"
- Decommission: "Remove the 'test_signatures' YARA rule"
- Correction: "Delete the 'broken_rule' YARA rule so I can recreate it"
- Maintenance: "Remove unused YARA rules from my organization"

## What This Skill Does

This skill permanently deletes a YARA rule source from the organization by its name. The rule will no longer be used for file or process scanning across sensors. This operation cannot be undone.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Name of the YARA rule source to delete (must be exact match)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exact YARA rule name to delete (case-sensitive)
3. Confirm user wants to delete the rule (permanent operation)

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/yara_source/global/[rule-name]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/v1/hive/yara_source/global/{rule_name}`
- Body: None (rule name is in the path)

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

**Success (200-299):**
- Rule successfully deleted
- Rule will no longer be used for scanning
- Confirm to user that rule has been removed

**Common Errors:**
- **400 Bad Request**: Invalid request format or missing name parameter
- **403 Forbidden**: Insufficient permissions to delete YARA rules
- **404 Not Found**: Rule with specified name does not exist
- **500 Server Error**: YARA service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm rule was successfully deleted
- Show the rule name that was removed
- Note that deletion is permanent and cannot be undone
- Mention that the rule will no longer scan files/processes
- If rule not found, suggest checking the name with list-yara-rules

## Example Usage

### Example 1: Delete a YARA rule

User request: "Delete the 'old_malware_signatures' YARA rule"

Steps:
1. Get organization ID from context
2. Extract rule name: "old_malware_signatures"
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/v1/hive/yara_source/global/old_malware_signatures"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

User message: "Successfully deleted YARA rule 'old_malware_signatures'. The rule has been permanently removed and will no longer be used for scanning."

### Example 2: Rule not found

User request: "Delete YARA rule 'nonexistent_rule'"

Steps:
1. Call API to delete rule
2. API returns 404 Not Found
3. Inform user: "YARA rule 'nonexistent_rule' not found. The rule may have already been deleted or the name may be incorrect. Use list-yara-rules to see available rules."

## Additional Notes

- Deletion is permanent and cannot be undone
- Rule names are case-sensitive
- The rule must exist in the organization
- Deletion takes effect immediately across all sensors
- No confirmation prompt from the API - ensure user intends to delete
- Consider backing up the rule content before deletion (use get-yara-rule first)
- Deleted rules will not appear in future YARA scans
- Historical detections from this rule may still exist in the timeline
- If you want to temporarily disable a rule, consider using tag or platform filters instead of deleting
- To recreate a deleted rule, use set-yara-rule with the same content
- Deleting a rule source removes all YARA rule definitions contained within it

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/yara.go`
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/yara_rules.go`
