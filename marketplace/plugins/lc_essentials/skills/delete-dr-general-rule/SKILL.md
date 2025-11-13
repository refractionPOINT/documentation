---
name: delete-dr-general-rule
description: Delete a custom Detection and Response (D&R) rule from the general namespace. Permanently removes the rule and stops all detection and response actions. Use for cleaning up obsolete rules, removing test rules, disabling unwanted detections, or during rule maintenance. Deletion is immediate and irreversible.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Delete D&R General Rule

Delete a custom Detection and Response (D&R) rule from the general namespace to remove unwanted or obsolete detections.

## When to Use

Use this skill when the user needs to:
- Remove obsolete or outdated detection rules
- Delete test rules after development
- Clean up duplicate rules
- Disable rules that generate false positives
- Remove rules that are no longer needed
- Reduce rule count for performance optimization
- Clean up the rule inventory

Common scenarios:
- "Delete the test rule we created"
- "Remove the 'old-malware-detection' rule"
- "Clean up the ransomware rule that's causing false positives"
- "Delete all the POC rules we created"

## What This Skill Does

This skill permanently deletes a D&R rule from the general namespace (custom rules). Once deleted, the rule immediately stops evaluating events and no longer triggers detections or response actions. This is irreversible - the rule configuration is permanently removed and cannot be recovered. Consider exporting the rule first if you may need it later.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **rule_name**: Exact name of the rule to delete (case-sensitive)

**IMPORTANT WARNINGS:**
- Deletion is PERMANENT and IRREVERSIBLE
- The rule configuration cannot be recovered after deletion
- All detection and response actions stop immediately
- Consider exporting or backing up the rule first
- Verify you have the correct rule name before deleting

## How to Use

### Step 1: Validate Parameters and Confirm

Ensure you have:
1. Valid organization ID (oid)
2. Exact rule name (case-sensitive)
3. **CRITICAL**: Confirm with the user that they want to permanently delete this rule
4. Consider viewing the rule first with `get-dr-general-rule`
5. Optionally export/backup the rule configuration before deletion

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/rules/[organization-id]",
  body={
    "name": "[rule-name]",
    "namespace": "general"
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/rules/{oid}` where `{oid}` is the organization ID
- No query parameters needed
- Body fields:
  - `name`: String - exact rule name to delete (required)
  - `namespace`: "general" (specifies custom rules namespace)

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
- Status code 200 indicates the rule was successfully deleted
- The rule immediately stops evaluating events
- No more detections or response actions will trigger
- The rule configuration is permanently removed
- The rule name becomes available for reuse

**Common Errors:**
- **404 Not Found**: Rule doesn't exist - verify the rule name and namespace
- **403 Forbidden**: Insufficient permissions - requires rule management permissions
- **400 Bad Request**: Invalid parameters - verify rule name format
- **500 Server Error**: Rare server issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the rule was permanently deleted
- Warn that this action is irreversible
- Mention that detection and response actions have stopped
- Remind that the rule cannot be recovered
- Suggest verifying with `list-dr-general-rules` if needed
- Note the rule name is now available for reuse

## Example Usage

### Example 1: Delete Test Rule

User request: "Delete the 'test-powershell-detection' rule, we're done testing"

Steps:
1. Validate the rule name
2. Optionally view the rule first to confirm it's the right one
3. **Confirm with user**: "This will permanently delete rule 'test-powershell-detection'. The rule configuration cannot be recovered. Are you sure?"
4. If confirmed, call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "test-powershell-detection",
    "namespace": "general"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"Successfully deleted D&R rule 'test-powershell-detection' from the general namespace. The rule has been permanently removed and is no longer monitoring for detections. All associated detection and response actions have stopped immediately. This action is irreversible."

### Example 2: Delete Obsolete Rule

User request: "Remove the old malware detection rule, we have a better one now"

Steps:
1. Identify the exact rule name
2. Confirm deletion intent
3. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/rules/c7e8f940-1234-5678-abcd-1234567890ab",
  body={
    "name": "old-malware-detection",
    "namespace": "general"
  }
)
```

Expected response:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {}
}
```

Response to user:
"The obsolete rule 'old-malware-detection' has been successfully removed from your detection stack. The rule is no longer active and your improved detection rule will handle this threat vector."

## Additional Notes

- **This operation is PERMANENT and IRREVERSIBLE** - there is no undo
- Always confirm with the user before deleting a rule
- Consider exporting the rule with `get-dr-general-rule` before deletion
- Deleted rules cannot be recovered - they must be recreated from scratch
- The rule name becomes available for reuse after deletion
- Deletion is immediate - all detection activity stops instantly
- This only affects the general namespace (custom rules)
- Cannot delete managed or service rules (those are controlled by LC/extensions)
- If the rule doesn't exist, you'll receive a 404 error
- Consider disabling the rule first (update with `is_enabled: false`) to test impact
- Deletion doesn't affect historical detections - those remain in logs
- This is useful for rule lifecycle management and cleanup
- Use caution in production - verify the rule name carefully
- Audit and compliance teams may require documenting rule deletions
- Related response actions (isolations, tags) remain on sensors after rule deletion
- Consider the security impact of removing detection coverage
- Review dependencies - other systems may rely on this rule's detections

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRuleDelete method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (delete_dr_general_rule)
