
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

**WARNING**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **name**: Exact name of the rule to delete (case-sensitive)

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

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_dr_general_rule",
  parameters={
    "oid": "[organization-id]",
    "name": "[rule-name]"
  }
)
```

**Tool Details:**
- Tool name: `delete_dr_general_rule`
- Required parameters:
  - `oid`: Organization ID (UUID)
  - `name`: Exact rule name to delete (string)

### Step 3: Handle the Response

The tool returns data directly:
```json
{}
```

**Success:**
- Empty object indicates the rule was successfully deleted
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
4. If confirmed, call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "test-powershell-detection"
  }
)
```

Expected response:
```json
{}
```

Response to user:
"Successfully deleted D&R rule 'test-powershell-detection' from the general namespace. The rule has been permanently removed and is no longer monitoring for detections. All associated detection and response actions have stopped immediately. This action is irreversible."

### Example 2: Delete Obsolete Rule

User request: "Remove the old malware detection rule, we have a better one now"

Steps:
1. Identify the exact rule name
2. Confirm deletion intent
3. Call tool:
```
mcp__limacharlie__lc_call_tool(
  tool_name="delete_dr_general_rule",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "name": "old-malware-detection"
  }
)
```

Expected response:
```json
{}
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

For more details on using `lc_call_tool`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/dr_rule.go` (DRRuleDelete method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/rules/dr_rules.go` (delete_dr_general_rule)
