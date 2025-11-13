---
name: dismiss-org-error
description: Dismiss a specific error from a LimaCharlie organization's error log by component name. Use this skill after resolving configuration issues, fixing integration problems, or acknowledging known errors. This clears the error from the org error list to maintain clean error tracking.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Dismiss Organization Error

Remove a specific error from the organization's error log after it has been resolved or acknowledged.

## When to Use

Use this skill when the user needs to:
- Clear resolved errors from the error log
- Acknowledge known issues that don't require immediate action
- Clean up the error list after fixing configurations
- Remove false positive error alerts
- Maintain clean error tracking and monitoring

Common scenarios:
- After fixing output configuration issues
- After correcting D&R rule syntax errors
- After resolving integration authentication failures
- When acknowledging temporary service disruptions
- During error log cleanup and maintenance

## What This Skill Does

This skill dismisses a specific error from a LimaCharlie organization's error log. It calls the LimaCharlie API to remove the error identified by its component name. This is typically done after the underlying issue has been resolved or when the error is acknowledged and doesn't require further action.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **component**: Component name of the error to dismiss (required)
  - Format: "component-type:component-name"
  - Examples: "output:syslog-prod", "rule:malware-detection", "extension:threat-intel"
  - Obtain from get-org-errors skill

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Correct component name from error log
3. Confirmation that the issue is resolved or acknowledged
4. Understanding that dismissal removes the error from tracking

**IMPORTANT**: Always verify the error is resolved before dismissing!

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="DELETE",
  path="/errors/[oid]/[component-name]"
)
```

**API Details:**
- Endpoint: `api`
- Method: `DELETE`
- Path: `/errors/{oid}/{component}` (component should be URL-encoded)
- Query parameters: None
- Body fields: None

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
- Empty or minimal response indicates successful dismissal
- Error is immediately removed from org error log
- Error will not appear in future get-org-errors calls
- Dismissal is permanent unless error recurs

**Common Errors:**
- **400 Bad Request**: Invalid component name format
- **403 Forbidden**: Insufficient permissions to dismiss errors
- **404 Not Found**: Component name doesn't match any existing error or org not found
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm successful dismissal
- Remind user what was dismissed (component name)
- Note that error is removed from tracking
- Suggest monitoring to ensure issue doesn't recur
- If error recurs, it will reappear in error log

## Example Usage

### Example 1: Dismiss a resolved output error

User request: "I fixed the Splunk connection. Can you clear that error?"

Steps:
1. First verify error is in org errors (use get-org-errors)
2. Confirm component name
3. Dismiss the error:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/errors/c7e8f940-1234-5678-abcd-1234567890ab/output:splunk-integration"
)
```

Expected response:
```json
{
  "status_code": 200,
  "body": {}
}
```

Present to user:
```
✅ Error Dismissed Successfully

Component: output:splunk-integration
Status: Removed from error log

The Splunk integration error has been cleared from your organization's error tracking.

Next steps:
✓ Monitor output logs to verify data flow
✓ Check that events are reaching Splunk
✓ If issue recurs, error will reappear automatically

The error log is now clean for this component.
```

### Example 2: Acknowledge a known non-critical issue

User request: "I know about that rate limit warning. Can we dismiss it?"

Steps:
1. Verify component name from error log
2. Confirm user understands impact
3. Dismiss the warning:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="DELETE",
  path="/errors/c7e8f940-1234-5678-abcd-1234567890ab/extension:threat-intel"
)
```

Present to user:
```
✅ Warning Acknowledged and Dismissed

Component: extension:threat-intel
Issue: API rate limit exceeded
Action: Acknowledged (non-critical)

The rate limit warning has been removed from your error log.

Note: If you continue to hit rate limits, consider:
- Reducing query frequency
- Upgrading your threat intel plan
- Implementing caching strategies

The warning will reappear if rate limiting continues.
```

### Example 3: Clean up multiple resolved errors

User request: "I fixed all the issues. Clear the error log."

Steps:
1. Get current errors to see what needs dismissal
2. Dismiss each resolved error individually
3. Verify error log is clean

Present summary:
```
🧹 Error Log Cleanup Complete

Dismissed 3 resolved errors:

✓ output:syslog-prod (connection timeout - fixed)
✓ rule:malware-detection (syntax error - corrected)
✓ extension:threat-intel (rate limit - acknowledged)

Current error status:
- Active errors: 0
- Organization health: Clean ✅

All known issues have been resolved and cleared from tracking.
Run get-org-errors anytime to check for new issues.
```

## Additional Notes

- Only dismiss errors after verifying the issue is resolved
- Dismissed errors will reappear if the problem recurs
- Some errors may auto-dismiss when underlying issue is fixed
- Component names must match exactly (case-sensitive)
- URL-encode component names with special characters
- Dismissal is a privileged operation requiring appropriate access
- Regular error log cleanup maintains clear visibility
- Consider documenting why errors were dismissed
- Monitor for recurring errors after dismissal
- Dismissal doesn't fix the underlying issue - it only clears the notification

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `go-limacharlie/limacharlie/organization_ext.go` (DismissOrgError function)
For the MCP tool implementation, check: `lc-mcp-server/internal/tools/admin/admin.go` (RegisterDismissOrgError)
