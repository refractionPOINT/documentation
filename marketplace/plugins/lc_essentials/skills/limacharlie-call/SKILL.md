---
name: limacharlie-call
description: Perform LimaCharlie API operations using MCP tool. Access 125 functions for sensors, rules, outputs, cloud integrations, artifacts, AI-powered generation, and validation. Load function references on-demand from ./functions/ directory.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_call_tool, mcp__plugin_lc-essentials_limacharlie__generate_lcql_query, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection, mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond, mcp__plugin_lc-essentials_limacharlie__generate_sensor_selector, mcp__plugin_lc-essentials_limacharlie__generate_python_playbook, mcp__plugin_lc-essentials_limacharlie__generate_detection_summary, mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components, mcp__plugin_lc-essentials_limacharlie__validate_yara_rule, Read, Bash
---

# LimaCharlie API Operations

Perform any LimaCharlie operation by dynamically loading function references.

## Core Concepts

**⚠️ CRITICAL**: The Organization ID (OID) is a **UUID** (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name.
- If you don't have the OID, use `list-user-orgs` function first to get the UUID from the org name
- All operations use the MCP tool: `mcp__plugin_lc-essentials_limacharlie__lc_call_tool`

**⚠️ CRITICAL: JSON Processing with jq**
When using jq to process JSON files, call jq directly:
```bash
jq '<expression>' <file>
```

## How to Use

1. Find the function you need in the index below
2. Read the function's reference file: `./functions/{function-name}.md`
3. Follow the instructions in that file to make the API call
4. If an OID is needed, get it first with `list-user-orgs`

## Functions by Use Case

Quick reference to find functions by common task:

### Timeline & Data Availability
- `get-time-when-sensor-has-data` - Check when sensor has data, data availability timeline, sensor overview
- `get-historic-events` - Query historical telemetry events
- `get-historic-detections` - Query historical detection alerts

### Sensor Status & Health
- `is-online` - Check if sensor is currently online
- `get-online-sensors` - List all online sensors
- `get-sensor-info` - Get detailed sensor information
- `list-sensors` - List all sensors in organization
- `list-with-platform` - Filter sensors by OS platform
- `upgrade-sensors` - Upgrade all sensors to specific version

### Threat Hunting & Investigation
- `run-lcql-query` - Search historical data with LCQL
- `search-iocs` - Search for indicators of compromise
- `batch-search-iocs` - Bulk IOC search
- `search-hosts` - Search for hosts by criteria

### Live Response & Forensics
- `get-processes` - List running processes on sensor
- `get-network-connections` - View active network connections
- `get-autoruns` - Check persistence mechanisms
- `dir-list` - Browse filesystem
- `yara-scan-process` / `yara-scan-file` / `yara-scan-memory` - YARA scanning

### Billing & Usage
- `get-org-invoice-url` - Get invoice with cost breakdown
- `get-billing-details` - Billing configuration
- `get-usage-stats` - Resource consumption metrics

### Detection Engineering
- `set-dr-general-rule` - Create/update detection rules
- `validate-dr-rule-components` - Validate rule syntax
- `generate-dr-rule-detection` - AI-generate detection logic
- `generate-dr-rule-respond` - AI-generate response actions

## Available Functions (125)

### Organization Management (8)
- `list-user-orgs` - List organizations available to user → `./functions/list-user-orgs.md`
- `get-org-info` - Get organization details → `./functions/get-org-info.md`
- `create-org` - Create new organization → `./functions/create-org.md`
- `get-org-errors` - Get organization errors → `./functions/get-org-errors.md`
- `dismiss-org-error` - Dismiss organization error → `./functions/dismiss-org-error.md`
- `get-org-invoice-url` - Get invoice URL → `./functions/get-org-invoice-url.md`
- `get-billing-details` - Get billing details → `./functions/get-billing-details.md`
- `get-usage-stats` - Get usage statistics → `./functions/get-usage-stats.md`

### API Keys (3)
- `list-api-keys` - List API keys → `./functions/list-api-keys.md`
- `create-api-key` - Create API key → `./functions/create-api-key.md`
- `delete-api-key` - Delete API key → `./functions/delete-api-key.md`

### Sensor Operations (13)
- `list-sensors` - List all sensors → `./functions/list-sensors.md`
- `list-with-platform` - List sensors by platform → `./functions/list-with-platform.md`
- `get-sensor-info` - Get sensor details → `./functions/get-sensor-info.md`
- `delete-sensor` - Delete sensor → `./functions/delete-sensor.md`
- `is-online` - Check if sensor is online → `./functions/is-online.md`
- `get-online-sensors` - Get all online sensors → `./functions/get-online-sensors.md`
- `add-tag` - Add tag to sensor → `./functions/add-tag.md`
- `remove-tag` - Remove tag from sensor → `./functions/remove-tag.md`
- `is-isolated` - Check if sensor is isolated → `./functions/is-isolated.md`
- `isolate-network` - Isolate sensor from network → `./functions/isolate-network.md`
- `rejoin-network` - Rejoin sensor to network → `./functions/rejoin-network.md`
- `get-time-when-sensor-has-data` - Get time range for sensor data → `./functions/get-time-when-sensor-has-data.md`
- `upgrade-sensors` - Upgrade sensors to specific version → `./functions/upgrade-sensors.md`

### Installation Keys (3)
- `list-installation-keys` - List installation keys → `./functions/list-installation-keys.md`
- `create-installation-key` - Create installation key → `./functions/create-installation-key.md`
- `delete-installation-key` - Delete installation key → `./functions/delete-installation-key.md`

### Cloud Sensors (4)
- `list-cloud-sensors` - List cloud sensor configs → `./functions/list-cloud-sensors.md`
- `get-cloud-sensor` - Get cloud sensor config → `./functions/get-cloud-sensor.md`
- `set-cloud-sensor` - Create/update cloud sensor → `./functions/set-cloud-sensor.md`
- `delete-cloud-sensor` - Delete cloud sensor → `./functions/delete-cloud-sensor.md`

### External Adapters (4)
- `list-external-adapters` - List external adapters → `./functions/list-external-adapters.md`
- `get-external-adapter` - Get external adapter config → `./functions/get-external-adapter.md`
- `set-external-adapter` - Create/update external adapter → `./functions/set-external-adapter.md`
- `delete-external-adapter` - Delete external adapter → `./functions/delete-external-adapter.md`

### Live Sensor Commands (20)
- `get-processes` - Get running processes → `./functions/get-processes.md`
- `get-process-modules` - Get process modules/DLLs → `./functions/get-process-modules.md`
- `get-process-strings` - Extract strings from process memory → `./functions/get-process-strings.md`
- `get-network-connections` - Get network connections → `./functions/get-network-connections.md`
- `get-os-version` - Get OS version info → `./functions/get-os-version.md`
- `get-users` - Get system users → `./functions/get-users.md`
- `get-services` - Get services → `./functions/get-services.md`
- `get-drivers` - Get drivers/kernel modules → `./functions/get-drivers.md`
- `get-autoruns` - Get autorun entries → `./functions/get-autoruns.md`
- `get-packages` - Get installed packages → `./functions/get-packages.md`
- `get-registry-keys` - Get Windows registry keys → `./functions/get-registry-keys.md`
- `dir-list` - List directory contents → `./functions/dir-list.md`
- `dir-find-hash` - Find files by hash → `./functions/dir-find-hash.md`
- `find-strings` - Find strings in process memory → `./functions/find-strings.md`
- `yara-scan-process` - Scan process with YARA → `./functions/yara-scan-process.md`
- `yara-scan-file` - Scan file with YARA → `./functions/yara-scan-file.md`
- `yara-scan-directory` - Scan directory with YARA → `./functions/yara-scan-directory.md`
- `yara-scan-memory` - Scan memory with YARA → `./functions/yara-scan-memory.md`
- `reliable-tasking` - Execute reliable task → `./functions/reliable-tasking.md`
- `list-reliable-tasks` - List reliable tasks → `./functions/list-reliable-tasks.md`

### Detection & Response Rules (10)
- `get-detection-rules` - Get all detection rules → `./functions/get-detection-rules.md`
- `list-dr-general-rules` - List D&R general rules → `./functions/list-dr-general-rules.md`
- `get-dr-general-rule` - Get D&R general rule → `./functions/get-dr-general-rule.md`
- `set-dr-general-rule` - Create/update D&R general rule → `./functions/set-dr-general-rule.md`
- `delete-dr-general-rule` - Delete D&R general rule → `./functions/delete-dr-general-rule.md`
- `list-dr-managed-rules` - List D&R managed rules → `./functions/list-dr-managed-rules.md`
- `get-dr-managed-rule` - Get D&R managed rule → `./functions/get-dr-managed-rule.md`
- `set-dr-managed-rule` - Create/update D&R managed rule → `./functions/set-dr-managed-rule.md`
- `delete-dr-managed-rule` - Delete D&R managed rule → `./functions/delete-dr-managed-rule.md`
- `get-mitre-report` - Get MITRE ATT&CK report → `./functions/get-mitre-report.md`

### False Positive Rules (4)
- `get-fp-rules` - Get all FP rules → `./functions/get-fp-rules.md`
- `get-fp-rule` - Get FP rule → `./functions/get-fp-rule.md`
- `set-fp-rule` - Create/update FP rule → `./functions/set-fp-rule.md`
- `delete-fp-rule` - Delete FP rule → `./functions/delete-fp-rule.md`

### Generic Rules (Hive) (4)
- `list-rules` - List rules from any Hive → `./functions/list-rules.md`
- `get-rule` - Get rule from Hive → `./functions/get-rule.md`
- `set-rule` - Create/update rule in Hive → `./functions/set-rule.md`
- `delete-rule` - Delete rule from Hive → `./functions/delete-rule.md`

### Outputs (3)
- `list-outputs` - List outputs → `./functions/list-outputs.md`
- `add-output` - Create output → `./functions/add-output.md`
- `delete-output` - Delete output → `./functions/delete-output.md`

### Secrets (4)
- `list-secrets` - List secret names → `./functions/list-secrets.md`
- `get-secret` - Get secret value → `./functions/get-secret.md`
- `set-secret` - Create/update secret → `./functions/set-secret.md`
- `delete-secret` - Delete secret → `./functions/delete-secret.md`

### Lookups (5)
- `list-lookups` - List lookups → `./functions/list-lookups.md`
- `get-lookup` - Get lookup → `./functions/get-lookup.md`
- `set-lookup` - Create/update lookup → `./functions/set-lookup.md`
- `query-lookup` - Query lookup → `./functions/query-lookup.md`
- `delete-lookup` - Delete lookup → `./functions/delete-lookup.md`

### Playbooks (4)
- `list-playbooks` - List playbooks → `./functions/list-playbooks.md`
- `get-playbook` - Get playbook → `./functions/get-playbook.md`
- `set-playbook` - Create/update playbook → `./functions/set-playbook.md`
- `delete-playbook` - Delete playbook → `./functions/delete-playbook.md`

### Extensions (6)
- `list-extension-configs` - List extension configs → `./functions/list-extension-configs.md`
- `get-extension-config` - Get extension config → `./functions/get-extension-config.md`
- `set-extension-config` - Create/update extension config → `./functions/set-extension-config.md`
- `delete-extension-config` - Delete extension config → `./functions/delete-extension-config.md`
- `subscribe-to-extension` - Subscribe to extension → `./functions/subscribe-to-extension.md`
- `unsubscribe-from-extension` - Unsubscribe from extension → `./functions/unsubscribe-from-extension.md`

### YARA Rules (4)
- `list-yara-rules` - List YARA rules → `./functions/list-yara-rules.md`
- `get-yara-rule` - Get YARA rule → `./functions/get-yara-rule.md`
- `set-yara-rule` - Create/update YARA rule → `./functions/set-yara-rule.md`
- `delete-yara-rule` - Delete YARA rule → `./functions/delete-yara-rule.md`

### Artifacts (2)
- `list-artifacts` - List artifacts → `./functions/list-artifacts.md`
- `get-artifact` - Get artifact → `./functions/get-artifact.md`

### Event Schemas (5)
- `get-event-schema` - Get event schema → `./functions/get-event-schema.md`
- `get-event-schemas-batch` - Get multiple event schemas → `./functions/get-event-schemas-batch.md`
- `get-event-types-with-schemas` - List event types with schemas → `./functions/get-event-types-with-schemas.md`
- `get-event-types-with-schemas-for-platform` - List event types by platform → `./functions/get-event-types-with-schemas-for-platform.md`
- `get-platform-names` - Get platform names → `./functions/get-platform-names.md`

### Queries (6)
- `run-lcql-query` - Run LCQL query → `./functions/run-lcql-query.md`
- `list-saved-queries` - List saved queries → `./functions/list-saved-queries.md`
- `get-saved-query` - Get saved query → `./functions/get-saved-query.md`
- `set-saved-query` - Create/update saved query → `./functions/set-saved-query.md`
- `delete-saved-query` - Delete saved query → `./functions/delete-saved-query.md`
- `run-saved-query` - Run saved query → `./functions/run-saved-query.md`

### Searching & Detection History (5)
- `search-hosts` - Search hosts → `./functions/search-hosts.md`
- `search-iocs` - Search IOCs → `./functions/search-iocs.md`
- `batch-search-iocs` - Batch search IOCs → `./functions/batch-search-iocs.md`
- `get-historic-events` - Get historic events → `./functions/get-historic-events.md`
- `get-historic-detections` - Get historic detections → `./functions/get-historic-detections.md`

### AI-Powered Generation (6)
- `generate-lcql-query` - Generate LCQL query from natural language → `./functions/generate-lcql-query.md`
- `generate-dr-rule-detection` - Generate D&R detection component → `./functions/generate-dr-rule-detection.md`
- `generate-dr-rule-respond` - Generate D&R respond component → `./functions/generate-dr-rule-respond.md`
- `generate-sensor-selector` - Generate sensor selector expression → `./functions/generate-sensor-selector.md`
- `generate-python-playbook` - Generate Python playbook script → `./functions/generate-python-playbook.md`
- `generate-detection-summary` - Generate detection summary → `./functions/generate-detection-summary.md`

### Validation Tools (2)
- `validate-dr-rule-components` - Validate D&R rule components → `./functions/validate-dr-rule-components.md`
- `validate-yara-rule` - Validate YARA rule syntax → `./functions/validate-yara-rule.md`

## Additional Resources

For detailed information on using the MCP tool, see [CALLING_API.md](../CALLING_API.md).

### Handling Large Results

When tool calls return large result sets (>100KB), the `lc_call_tool` returns a `resource_link` instead of inline data:

```json
{
  "is_temp_file": false,
  "reason": "results too large, see resource_link for content",
  "resource_link": "https://storage.googleapis.com/...",
  "resource_size": 34329,
  "success": true
}
```

**CRITICAL REQUIREMENT**: When you see `resource_link` in the response, you **MUST** follow this exact workflow. DO NOT attempt to guess the JSON structure or write jq queries before analyzing the schema.

**Why this is mandatory**: Skipping the analysis step results in incorrect queries, wasted tokens, and frustration. The schema reveals the actual structure, which may differ from what you expect.

### Step 1: Download and Analyze (REQUIRED)

**You MUST run the analyze script first. DO NOT skip this step.**

Run the analyze script with the `resource_link` URL:

```bash
bash ./marketplace/plugins/lc_essentials/scripts/analyze-lc-result.sh "https://storage.googleapis.com/..."
```

Replace the URL with the actual `resource_link` value from the API response.

**What this script does:**
1. Downloads the file to `/tmp/lc-result-{timestamp}.json`
2. Outputs the JSON schema to stdout showing object keys, array patterns, and data types
3. Prints the file path to stderr (after `---FILE_PATH---`)

**Example output:**
```
(stdout) {"sensors": [{"sid": "string", "hostname": "string", "platform": "string"}]}
(stderr) ---FILE_PATH---
(stderr) /tmp/lc-result-1731633216789456123.json
```

**Before proceeding to Step 2**, you MUST review the schema output to understand:
- Is the top-level structure an object or array?
- What are the available keys/fields?
- How is the data nested?

### Step 2: Extract Specific Data with jq

**Only after reviewing the schema**, use jq to extract the specific information requested. Use the file path shown in the script output.

Common patterns based on schema:

```bash
# If schema shows top-level array
jq '.[] | select(.hostname == "web-01")' /tmp/lc-result-{timestamp}.json

# If schema shows top-level object with named keys
jq '.sensors[] | {id: .sid, name: .hostname}' /tmp/lc-result-{timestamp}.json

# Count items
jq '. | length' /tmp/lc-result-{timestamp}.json
```

### Step 3: Clean Up

Remove the temporary file when done:

```bash
rm /tmp/lc-result-{timestamp}.json
```

Replace `{timestamp}` with the actual timestamp from Step 1's output.

See the "Handling Large Results" section in [CALLING_API.md](../CALLING_API.md) for more details.
