
# Upgrade Sensors

Update the sensor version for a LimaCharlie organization - upgrade to specific versions, downgrade to previous version, or set sensors to dormant mode.

## When to Use

Use this skill when the user needs to:
- Update sensors to a specific version (semantic version or label)
- Downgrade sensors to the previous version (rollback)
- Move sensors to dormant mode (sleep)
- Pin an organization to a specific tested sensor version
- Upgrade to stable, latest, or experimental versions
- Deploy a specific version across multiple organizations consistently

Common scenarios:
- "Update all sensors to version 4.33.20"
- "Upgrade the organization to the latest sensor version"
- "Downgrade to the previous version"
- "Roll back the sensor upgrade"
- "Put sensors in dormant mode"
- "Upgrade to the experimental version for testing"

## What This Skill Does

This skill updates the organization-level sensor version setting using the `/v1/modules/{oid}` API endpoint. All sensors in the organization will update within approximately 20 minutes. The update only affects the over-the-air core component (approximately 3-5 MB), not the on-disk agent. Individual sensors with version tags (`lc:latest`, `lc:stable`, `lc:experimental`) will override this organization-level setting.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list_user_orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required)
- **Exactly ONE of the following** (mutually exclusive):
  - **version**: Target sensor version or label (string)
  - **is_fallback**: Downgrade to previous version (boolean)
  - **is_sleep**: Move sensors to dormant mode (boolean)

### Option 1: Specific Version (`version` parameter)
- **Semantic version**: Specific version like `4.33.20` (format: MAJOR.MINOR.PATCH)
- **Version labels**: `latest`, `stable`, or `experimental`

Version label meanings:
- `latest`: Most recent release with new fixes and features
- `stable`: Less frequently updated, ideal for slower update cadences
- `experimental`: Beta version of the next "latest" release

### Option 2: Downgrade to Previous (`is_fallback` parameter)
Set to `true` to downgrade all sensors to the previous version (rollback functionality).

### Option 3: Dormant Mode (`is_sleep` parameter)
Set to `true` to move all sensors to dormant/sleep mode.

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Exactly ONE of:
   - Valid version string (semantic version or label)
   - `is_fallback=true` for downgrade
   - `is_sleep=true` for dormant mode

### Step 2: Call the Tool

Use the `lc_call_tool` MCP tool from the `limacharlie` server:

**Option 1: Upgrade to specific version**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "version": "4.33.20"
  }
)
```

**Option 2: Downgrade to previous version**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "is_fallback": true
  }
)
```

**Option 3: Move to dormant mode**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "is_sleep": true
  }
)
```

**Tool Details:**
- Tool name: `upgrade_sensors`
- Required parameters:
  - `oid` (string): Organization ID
  - ONE of: `version` (string) OR `is_fallback` (boolean) OR `is_sleep` (boolean)
- API endpoint: `POST /v1/modules/{oid}`
- Query parameters:
  - `specific_version={value}`: For semantic versions or labels (latest/stable/experimental)
  - `is_fallback=true`: To downgrade to previous version
  - `is_sleep=true`: To move sensors to dormant mode

### Step 3: Handle the Response

The tool returns a response with:
```json
{
  "success": true
}
```

**Success:**
- Response indicates the upgrade was successfully initiated
- Sensors will update within approximately 20 minutes
- Only the over-the-air core component is updated (3-5 MB)
- Sensors with version tags will override this setting
- No reinstallation or redeployment is required

**Common Errors:**
- **400 Bad Request**: Invalid version format or unavailable version
- **403 Forbidden**: Insufficient permissions to upgrade sensors
- **404 Not Found**: Organization does not exist
- **500 Server Error**: API service issue - retry or contact support

### Step 4: Format the Response

Present the result to the user:
- Confirm the upgrade was successfully initiated
- State the target version or label
- Mention the 20-minute update window
- Note that sensors with version tags will override this setting
- Recommend monitoring sensor versions after the update window
- Suggest best practices like staged deployments for production

## Example Usage

### Example 1: Upgrade to specific version

User request: "Update all sensors in lc-demo to version 4.33.20"

Steps:
1. Get organization ID for lc-demo using `list_user_orgs`
2. Call tool to upgrade sensors:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "8cbe27f4-bfa1-4afb-ba19-138cd51389cd",
    "version": "4.33.20"
  }
)
```

Expected response:
```json
{
  "success": true
}
```

Present to user:
```
Sensor Upgrade Initiated

Organization: lc-demo (8cbe27f4-bfa1-4afb-ba19-138cd51389cd)
Target Version: 4.33.20
Status: SUCCESS

All sensors will update to version 4.33.20 within approximately 20 minutes.

Note: Sensors with version tags (lc:latest, lc:stable, lc:experimental)
will override this organization-level setting and maintain their tagged version.

Best Practice: Monitor sensor versions after the update window to ensure
successful deployment across your fleet.
```

### Example 2: Upgrade to latest version label

User request: "Upgrade to the latest sensor version"

Steps:
1. Validate organization ID
2. Use "latest" as the version parameter:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "version": "latest"
  }
)
```

Expected response:
```json
{
  "success": true
}
```

Present to user:
```
Upgraded to Latest Version

Your organization will receive the most recent sensor release within
approximately 20 minutes. The latest version includes new fixes and features.

Recommendation: Consider testing on a subset of sensors first using the
lc:latest tag before organization-wide upgrades.
```

### Example 3: Switch to stable release channel

User request: "Move our production org to the stable release channel"

Steps:
1. Validate organization ID
2. Use "stable" as the version parameter:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-prod-org-abcd-1234567890ab",
    "version": "stable"
  }
)
```

Expected response:
```json
{
  "success": true
}
```

Present to user:
```
Switched to Stable Release Channel

Your production organization is now configured to use the stable release
channel. This version is less frequently updated and ideal for production
environments requiring slower update cadences.

All sensors will update to the current stable version within 20 minutes.

To enable automatic updates when new stable versions are released, tag your
sensors with lc:stable.
```

### Example 4: Rollback to previous version

User request: "Roll back to version 4.32.15 due to compatibility issue"

Steps:
1. Validate organization ID
2. Specify the rollback version:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="upgrade_sensors",
  parameters={
    "oid": "c7e8f940-1234-5678-abcd-1234567890ab",
    "version": "4.32.15"
  }
)
```

Expected response:
```json
{
  "success": true
}
```

Present to user:
```
Sensor Rollback Initiated

Rolling back sensors from current version to 4.32.15 due to compatibility issue.

Rollback will complete within approximately 20 minutes.

After rollback:
1. Verify all sensors are running 4.32.15
2. Test the compatibility issue to confirm it's resolved
3. Monitor sensor health and telemetry quality
4. Document the issue before attempting future upgrades

You can maintain this version by keeping the organization setting or by
applying version tags to individual sensors.
```

## Additional Notes

- **Update time**: Sensors update within approximately 20 minutes
- **Component updated**: Only the over-the-air core component (~3-5 MB)
- **No reinstall required**: Existing installers remain valid
- **Version override**: Individual sensor tags override organization setting
- **Version tags**: `lc:latest`, `lc:stable`, `lc:experimental`
- **Semantic versioning**: Must use format MAJOR.MINOR.PATCH (e.g., 4.33.20)
- **Invalid versions**: API returns error if version doesn't exist
- **Staged deployment best practice**:
  1. Tag a few representative sensors with `lc:latest`
  2. Monitor for 24-48 hours
  3. If stable, upgrade organization-wide
  4. Remove `lc:latest` tags from test sensors
- **Auto-update**: Tag sensors with `lc:stable` to auto-update on new stable releases
- **Rollback plan**: Always maintain ability to rollback to previous version
- **Production recommendation**: Use specific version numbers for production (e.g., `4.33.20`) rather than labels for consistency
- **Testing recommendation**: Use `experimental` label only in dev/test environments
- **API endpoint**: `POST /v1/modules/{oid}`
- **Query parameters** (mutually exclusive):
  - `specific_version={version}`: Upgrade to specific semantic version or label (latest/stable/experimental)
  - `is_fallback=true`: Downgrade to the previous version
  - `is_sleep=true`: Move sensors to dormant mode
- **API reference**: https://api.limacharlie.io/static/swagger/#/Modules/upgradeOrg
- **Dormant mode**: Sensors in sleep mode consume minimal resources but remain manageable
- **Rollback**: `is_fallback=true` downgrades to the immediately previous version, not "stable"

## Reference

For more details on using `lc_call_tool`, see [CALLING_API.md](../../../CALLING_API.md).

For sensor versioning documentation, see: `docs/limacharlie/doc/Sensors/Endpoint_Agent/endpoint-agent-versioning-and-upgrades.md`
For the API reference, see: https://api.limacharlie.io/static/swagger/#/Modules/upgradeOrg
