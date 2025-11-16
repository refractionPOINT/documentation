
# Set Rule in Hive

Creates or updates a rule in a Hive in a LimaCharlie organization.

## When to Use

Use this skill when the user needs to:
- Create a new D&R rule in general namespace
- Update an existing D&R rule
- Create or modify false positive rules
- Configure rules in any custom Hive
- Modify rule detection logic or response actions
- Enable/disable rules

Common scenarios:
- "Create a D&R rule to detect suspicious DNS queries"
- "Update the ransomware-detection rule to also isolate the sensor"
- "Add a false positive rule to filter out Chrome update noise"
- "Create a rule in dr-general named 'malware-behavior'"

## What This Skill Does

This skill creates or updates a rule in a specified Hive in the LimaCharlie Hive system. It's a generic operation that works with any Hive name, commonly used for:
- `dr-general`: General Detection & Response rules (user-created)
- `fp`: False Positive filtering rules
- Other custom Hives

The skill POSTs rule data to the Hive API using the specified Hive name, "global" partition, and rule name. The rule is automatically enabled and includes the provided definition. If a rule with the same name already exists, it will be updated.

**Note:** `dr-managed` Hive typically contains read-only managed rules and may not allow direct updates.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **hive_name**: The name of the Hive to create/update rule in (required)
  - Common values: `dr-general`, `fp`
- **rule_name**: The name for the rule (required)
- **rule_content**: The rule definition object (required, structure varies by Hive type)
  - For D&R rules: must include `detect` and `respond` sections
  - For FP rules: must include filter/match logic

Optional parameters:
- **tags**: Array of tags to categorize the rule
- **comment**: Description or notes about this rule
- **enabled**: Whether the rule is enabled (defaults to true)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Hive name (string, determines where the rule is stored)
3. Rule name (string, will become the rule key)
4. Rule content (object with valid structure for the Hive type)
5. For D&R rules: validate detect and respond sections are correctly formatted

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/v1/hive/[hive-name]/global/[rule-name]/data",
  body={
    "gzdata": "[base64-gzipped-json-data]",
    "usr_mtd": {
      "enabled": true,
      "tags": ["detection", "network"],
      "comment": "Rule description"
    }
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/v1/hive/{hive_name}/global/{rule_name}/data`
  - Replace `{hive_name}` with the Hive name
  - Replace `{rule_name}` with the URL-encoded rule name
  - The `/data` suffix indicates we're setting the rule data
- Body fields:
  - `gzdata`: Rule content encoded as base64(gzip(json))
  - `usr_mtd`: User metadata object

### Step 3: Handle the Response

The API returns:
```json
{
  "status_code": 200,
  "body": {
    "guid": "unique-record-id",
    "name": "rule-name"
  }
}
```

**Success (200-299):**
- Rule has been created or updated successfully
- Inform the user that the rule is now active

**Common Errors:**
- **400 Bad Request**: Invalid rule structure - check the rule definition format
- **403 Forbidden**: Insufficient permissions or read-only Hive
- **500 Server Error**: Backend issue - advise retry

### Step 4: Format the Response

Present the result to the user:
- Confirm the rule was created/updated
- Show the rule name and Hive
- Summarize what the rule does
- Note that it's enabled and ready to execute
- Suggest testing the rule carefully before production use

## Example Usage

### Example 1: Create a D&R rule

User request: "Create a D&R rule to detect suspicious DNS queries to malicious domains"

Steps:
1. Get the organization ID
2. Prepare rule content:
```json
{
  "detect": {
    "event": "DNS_REQUEST",
    "op": "contains",
    "path": "event/DOMAIN_NAME",
    "value": "malicious.com"
  },
  "respond": [
    {"action": "report", "name": "suspicious_dns"},
    {"action": "add_tag", "tag": "suspicious", "ttl": 900}
  ]
}
```
3. Use hive_name "dr-general" and rule_name "suspicious-dns-detection"
4. Call API

Expected response confirms creation.

Inform user: "Successfully created the suspicious-dns-detection rule in dr-general. It will detect DNS requests to malicious.com and report them as suspicious_dns. The rule is enabled and active."

### Example 2: Create a false positive rule

User request: "Add a false positive rule to filter out Chrome update detections"

Steps:
1. Get organization ID
2. Prepare FP rule content with filter logic
3. Use hive_name "fp" and rule_name "chrome-update-fp"
4. Call API with appropriate FP rule structure

### Example 3: Update existing D&R rule

User request: "Update the ransomware-detection rule to also isolate the sensor"

Steps:
1. Optionally get existing rule first to see current definition
2. Prepare updated rule content with added isolation action
3. POST the updated content (it will replace the existing rule)
4. Confirm the update was successful

## Additional Notes

- **Creating vs Updating**: This operation performs an "upsert" - creates if doesn't exist, updates if it does
- **Rule Structure**: Structure varies by Hive type:
  - D&R rules: require `detect` and `respond` sections
  - FP rules: require filter/match logic
  - Validate structure matches Hive type requirements
- **Enabled by Default**: New rules are enabled by default - test carefully
- **Read-Only Hives**: Some Hives like `dr-managed` may be read-only
- **No Partial Updates**: POST replaces the entire rule - include all fields you want to keep
- **Testing**: Consider testing rules in a non-production environment first
- **Impact**: Rules execute in real-time - ensure detection and response logic is correct
- Use `get-rule` to verify the rule was set correctly
- Use `list-rules` to see the rule in context with other rules

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go` (Add method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/generic_hive.go`
