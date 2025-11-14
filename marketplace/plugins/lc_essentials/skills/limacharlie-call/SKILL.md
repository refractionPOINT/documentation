---
name: limacharlie-call
description: Perform LimaCharlie API operations using MCP tool. Access 119 functions for sensors, rules, outputs, cloud integrations, artifacts, and more. Load function references on-demand from ./functions/ directory.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_api_call, Read
---

# LimaCharlie API Operations

Perform any LimaCharlie operation by dynamically loading function references.

## Core Concepts

**⚠️ CRITICAL**: The Organization ID (OID) is a **UUID** (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name.
- If you don't have the OID, use `list-user-orgs` function first to get the UUID from the org name
- All API calls use the MCP tool: `mcp__plugin_lc-essentials_limacharlie__lc_api_call`

## How to Use

1. Find the function you need in the index below
2. Read the function's reference file: `./functions/{function-name}.md`
3. Follow the instructions in that file to make the API call
4. If an OID is needed, get it first with `list-user-orgs`

## Available Functions (119)

### Organization Management (9)
- `list-user-orgs` - List organizations available to user → `./functions/list-user-orgs.md`
- `get-org-info` - Get organization details → `./functions/get-org-info.md`
- `create-org` - Create new organization → `./functions/create-org.md`
- `get-org-errors` - Get organization errors → `./functions/get-org-errors.md`
- `dismiss-org-error` - Dismiss organization error → `./functions/dismiss-org-error.md`
- `get-org-invoice-url` - Get invoice URL → `./functions/get-org-invoice-url.md`
- `get-billing-details` - Get billing details → `./functions/get-billing-details.md`
- `get-usage-stats` - Get usage statistics → `./functions/get-usage-stats.md`
- `get-sku-definitions` - Get SKU definitions → `./functions/get-sku-definitions.md`

### API Keys (3)
- `list-api-keys` - List API keys → `./functions/list-api-keys.md`
- `create-api-key` - Create API key → `./functions/create-api-key.md`
- `delete-api-key` - Delete API key → `./functions/delete-api-key.md`

### Sensor Operations (12)
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

### Detection & Response Rules (11)
- `get-detection-rules` - Get all detection rules → `./functions/get-detection-rules.md`
- `list-dr-general-rules` - List D&R general rules → `./functions/list-dr-general-rules.md`
- `get-dr-general-rule` - Get D&R general rule → `./functions/get-dr-general-rule.md`
- `set-dr-general-rule` - Create/update D&R general rule → `./functions/set-dr-general-rule.md`
- `delete-dr-general-rule` - Delete D&R general rule → `./functions/delete-dr-general-rule.md`
- `list-dr-managed-rules` - List D&R managed rules → `./functions/list-dr-managed-rules.md`
- `get-dr-managed-rule` - Get D&R managed rule → `./functions/get-dr-managed-rule.md`
- `set-dr-managed-rule` - Create/update D&R managed rule → `./functions/set-dr-managed-rule.md`
- `delete-dr-managed-rule` - Delete D&R managed rule → `./functions/delete-dr-managed-rule.md`
- `validate-dr-rule-components` - Validate D&R rule components → `./functions/validate-dr-rule-components.md`
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

### YARA Rules (5)
- `list-yara-rules` - List YARA rules → `./functions/list-yara-rules.md`
- `get-yara-rule` - Get YARA rule → `./functions/get-yara-rule.md`
- `set-yara-rule` - Create/update YARA rule → `./functions/set-yara-rule.md`
- `delete-yara-rule` - Delete YARA rule → `./functions/delete-yara-rule.md`
- `validate-yara-rule` - Validate YARA rule → `./functions/validate-yara-rule.md`

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

## Additional Resources

For detailed information on using the MCP tool, see [CALLING_API.md](../CALLING_API.md).
