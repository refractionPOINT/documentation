---
name: set-playbook
description: Create or update an automation playbook in a LimaCharlie organization. Use this skill when users need to configure, modify, or update automated response workflows. Playbooks define multi-step automation with triggers, conditions, and actions. Creates a new playbook if it doesn't exist, or updates an existing one. Essential for implementing automated incident response, threat hunting, and workflow automation.
allowed-tools: mcp__limacharlie__lc_api_call, Read
---

# Set Playbook

Creates or updates an automation playbook in the LimaCharlie Hive.

## When to Use

Use this skill when the user needs to:
- Create a new automation playbook
- Update an existing playbook workflow
- Modify playbook steps or conditions
- Configure automated incident response
- Set up threat hunting automation
- Define multi-step workflows

Common scenarios:
- "Create a playbook to auto-isolate critical threats"
- "Update the incident-response playbook to also create a case"
- "Set up a playbook that scans suspicious files with YARA"
- "Configure automated threat hunting on network connections"

## What This Skill Does

This skill creates or updates an automation playbook in the LimaCharlie Hive system. It POSTs playbook workflow data to the Hive API using the "playbook" hive name with the "global" partition. The playbook is automatically enabled and includes the provided workflow definition (steps, triggers, conditions, actions). If a playbook with the same name already exists, it will be updated.

## Required Information

Before calling this skill, gather:
- **oid**: Organization ID (required for all API calls)
- **playbook_name**: The name for the playbook (required)
- **playbook_data**: The workflow definition object (required, must be valid structure)
  - `steps`: Array of actions to execute
  - `trigger`: What triggers the playbook
  - `filter`: Optional conditional logic
  - `description`: Optional human-readable explanation

Optional parameters:
- **tags**: Array of tags to categorize the playbook
- **comment**: Description or notes about this playbook
- **enabled**: Whether the playbook is enabled (defaults to true)

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Playbook name (string, will become the playbook key)
3. Playbook data (object with workflow definition)
4. Validate that playbook structure is correct:
   - steps array is valid
   - trigger is specified
   - actions are supported

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/hive/playbook/global/[playbook-name]/data",
  body={
    "gzdata": "[base64-gzipped-json-data]",
    "usr_mtd": {
      "enabled": true,
      "tags": ["incident-response"],
      "comment": "Playbook description"
    }
  }
)
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/hive/playbook/global/{playbook_name}/data`
- Body fields:
  - `gzdata`: Playbook workflow encoded as base64(gzip(json))
  - `usr_mtd`: User metadata object

### Step 3: Handle the Response

The API returns:
```json
{
  "status_code": 200,
  "body": {
    "guid": "unique-record-id",
    "name": "playbook-name"
  }
}
```

**Success (200-299):**
- Playbook has been created or updated successfully
- Inform the user that the playbook is now active

**Common Errors:**
- **400 Bad Request**: Invalid playbook structure - check the workflow definition
- **403 Forbidden**: Insufficient permissions
- **500 Server Error**: Backend issue - advise retry

### Step 4: Format the Response

Present the result to the user:
- Confirm the playbook was created/updated
- Show the playbook name
- Summarize what the playbook does
- Note that it's enabled and ready to execute
- Suggest testing the playbook carefully before production use

## Example Usage

### Example 1: Create auto-isolation playbook

User request: "Create a playbook to automatically isolate sensors on critical detections"

Steps:
1. Get the organization ID
2. Prepare playbook data:
```json
{
  "steps": [
    {"action": "isolate_sensor"},
    {"action": "create_case", "params": {"priority": "high"}}
  ],
  "trigger": "detection",
  "filter": "cat == 'CRITICAL'",
  "description": "Auto-isolate critical threats and create case"
}
```
3. Call API with playbook name "critical-auto-isolation"

Expected response confirms creation.

Inform user: "Successfully created the critical-auto-isolation playbook. It will automatically isolate sensors and create cases when critical detections occur. The playbook is enabled and active."

## Additional Notes

- **Creating vs Updating**: This operation performs an "upsert" - creates if doesn't exist, updates if it does
- **Playbook Structure**: Include required fields (steps, trigger) and optional fields (filter, description)
- **Enabled by Default**: New playbooks are enabled by default - be careful with potentially disruptive actions
- **Test First**: Consider testing playbooks in a non-production environment before enabling
- **Destructive Actions**: Some playbook actions (isolate, delete) are irreversible - review carefully
- Use `get-playbook` to verify the playbook was set correctly
- Playbooks execute automatically when triggered - ensure conditions are correct

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `../go-limacharlie/limacharlie/hive.go` (Add method)
For the MCP tool implementation, check: `../lc-mcp-server/internal/tools/hive/playbooks.go`
