---
name: limacharlie-call
description: "**REQUIRED for ALL LimaCharlie operations** - list orgs, sensors, rules, detections, queries, and 120+ functions. NEVER call LimaCharlie MCP tools directly. Use cases: 'what orgs do I have', 'list sensors', 'search IOCs', 'run LCQL query', 'create detection rule'. This skill loads function docs and delegates to sub-agent."
allowed-tools: Task, Read, Bash
---

# LimaCharlie API Operations

Perform any LimaCharlie operation by dynamically loading function references.

## Core Concepts

**⚠️ CRITICAL**: The Organization ID (OID) is a **UUID** (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name.
- If you don't have the OID, use `list_user_orgs` function first to get the UUID from the org name
- All operations are delegated to the `limacharlie-api-executor` sub-agent which handles MCP tool calls

**⚠️ CRITICAL: Always Use the Sub-Agent**
You must NEVER call MCP tools directly. Always use the Task tool to spawn the `limacharlie-api-executor` sub-agent for all API operations.

## How to Use

**All LimaCharlie API operations are executed through the `limacharlie-api-executor` sub-agent for optimal performance.**

### Single API Call

1. Find the function you need in the index below
2. Spawn the `limacharlie-api-executor` agent with the Task tool:

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: <function-name>
    - Parameters: {<params>}
    - Extract: (optional) <what to extract>"
)
```

**Example**:
```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: get_sensor_info
    - Parameters: {\"oid\": \"8cbe27f4-bfa1-4afb-ba19-138cd51389cd\", \"sid\": \"xyz-123\"}
    - Extract: sensor hostname and online status"
)
```

### Parallel API Calls

For multiple independent API calls, spawn multiple agents in a **single message** for parallel execution:

```
<single message with multiple Task calls>
Task(subagent_type="lc-essentials:limacharlie-api-executor", prompt="Execute... sensor1")
Task(subagent_type="lc-essentials:limacharlie-api-executor", prompt="Execute... sensor2")
Task(subagent_type="lc-essentials:limacharlie-api-executor", prompt="Execute... sensor3")
</single message>
```

**Example** (checking data availability for 3 sensors in parallel):
```
<function_calls>
  <Task subagent_type="lc-essentials:limacharlie-api-executor"
        prompt="Execute LimaCharlie API call:
          - Function: get_time_when_sensor_has_data
          - Parameters: {\"oid\": \"...\", \"sid\": \"sensor1\", \"start\": 1234567890, \"end\": 1234567899}">
  <Task subagent_type="lc-essentials:limacharlie-api-executor"
        prompt="Execute LimaCharlie API call:
          - Function: get_time_when_sensor_has_data
          - Parameters: {\"oid\": \"...\", \"sid\": \"sensor2\", \"start\": 1234567890, \"end\": 1234567899}">
  <Task subagent_type="lc-essentials:limacharlie-api-executor"
        prompt="Execute LimaCharlie API call:
          - Function: get_time_when_sensor_has_data
          - Parameters: {\"oid\": \"...\", \"sid\": \"sensor3\", \"start\": 1234567890, \"end\": 1234567899}">
</function_calls>
```

### Getting Organization ID

If you don't have the OID (Organization ID), get it first with `list_user_orgs`:

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_user_orgs
    - Parameters: {}"
)
```

Then use the UUID from the results for subsequent calls.

## Functions by Use Case

Quick reference to find functions by common task:

### Timeline & Data Availability
- `get_time_when_sensor_has_data` - Check when sensor has data, data availability timeline, sensor overview
- `get_historic_events` - Query historical telemetry events
- `get_historic_detections` - Query historical detection alerts

### Sensor Status & Health
- `list_sensors` - **PRIMARY** - List all sensors with optional filtering (hostname, IP, online status, platform)
- `get_online_sensors` - Get online sensor IDs quickly
- `get_sensor_info` - Get detailed sensor information
- `is_online` - Check if sensor is currently online
- `upgrade_sensors` - Upgrade all sensors to specific version

### Threat Hunting & Investigation

**⚠️ CRITICAL LCQL Workflow:**
When querying historical data, ALWAYS use this two-step process:
1. **FIRST**: Call `generate_lcql_query` to convert natural language to LCQL syntax
2. **THEN**: Call `run_lcql_query` with the generated LCQL query

LCQL is NOT SQL - it uses pipe-based syntax like: `-24h | * | NEW_PROCESS | event.FILE_PATH contains 'powershell'`

**Functions:**
- `generate_lcql_query` - **USE THIS FIRST** - Convert natural language to LCQL syntax
- `run_lcql_query` - Execute LCQL query (requires actual LCQL syntax, NOT SQL/English)
- `search_iocs` - Search for indicators of compromise
- `batch_search_iocs` - Bulk IOC search
- `search_hosts` - Search for hosts by criteria

### Live Response & Forensics
- `get_processes` - List running processes on sensor
- `get_network_connections` - View active network connections
- `get_autoruns` - Check persistence mechanisms
- `dir_list` - Browse filesystem
- `yara_scan_process` / `yara_scan_file` / `yara_scan_memory` - YARA scanning

### Billing & Usage
- `get_org_invoice_url` - Get invoice with cost breakdown
- `get_billing_details` - Billing configuration
- `get_usage_stats` - Resource consumption metrics

### Detection Engineering
- `set_dr_general_rule` - Create/update detection rules
- `validate_dr_rule_components` - Validate rule syntax
- `generate_dr_rule_detection` - AI-generate detection logic
- `generate_dr_rule_respond` - AI-generate response actions

## Available Functions (124)

### Organization Management (8)
- `list_user_orgs` - List organizations available to user → `./functions/list-user-orgs.md`
- `get_org_info` - Get organization details → `./functions/get-org-info.md`
- `create_org` - Create new organization → `./functions/create-org.md`
- `get_org_errors` - Get organization errors → `./functions/get-org-errors.md`
- `dismiss_org_error` - Dismiss organization error → `./functions/dismiss-org-error.md`
- `get_org_invoice_url` - Get invoice URL → `./functions/get-org-invoice-url.md`
- `get_billing_details` - Get billing details → `./functions/get-billing-details.md`
- `get_usage_stats` - Get usage statistics → `./functions/get-usage-stats.md`

### API Keys (3)
- `list_api_keys` - List API keys → `./functions/list-api-keys.md`
- `create_api_key` - Create API key → `./functions/create-api-key.md`
- `delete_api_key` - Delete API key → `./functions/delete-api-key.md`

### Sensor Operations (12)
- `list_sensors` - List all sensors → `./functions/list-sensors.md`
- `get_sensor_info` - Get sensor details → `./functions/get-sensor-info.md`
- `delete_sensor` - Delete sensor → `./functions/delete-sensor.md`
- `is_online` - Check if sensor is online → `./functions/is-online.md`
- `get_online_sensors` - Get all online sensors → `./functions/get-online-sensors.md`
- `add_tag` - Add tag to sensor → `./functions/add-tag.md`
- `remove_tag` - Remove tag from sensor → `./functions/remove-tag.md`
- `is_isolated` - Check if sensor is isolated → `./functions/is-isolated.md`
- `isolate_network` - Isolate sensor from network → `./functions/isolate-network.md`
- `rejoin_network` - Rejoin sensor to network → `./functions/rejoin-network.md`
- `get_time_when_sensor_has_data` - Get time range for sensor data → `./functions/get-time-when-sensor-has-data.md`
- `upgrade_sensors` - Upgrade sensors to specific version → `./functions/upgrade-sensors.md`

### Installation Keys (3)
- `list_installation_keys` - List installation keys → `./functions/list-installation-keys.md`
- `create_installation_key` - Create installation key → `./functions/create-installation-key.md`
- `delete_installation_key` - Delete installation key → `./functions/delete-installation-key.md`

### Cloud Sensors (4)
- `list_cloud_sensors` - List cloud sensor configs → `./functions/list-cloud-sensors.md`
- `get_cloud_sensor` - Get cloud sensor config → `./functions/get-cloud-sensor.md`
- `set_cloud_sensor` - Create/update cloud sensor → `./functions/set-cloud-sensor.md`
- `delete_cloud_sensor` - Delete cloud sensor → `./functions/delete-cloud-sensor.md`

### External Adapters (4)
- `list_external_adapters` - List external adapters → `./functions/list-external-adapters.md`
- `get_external_adapter` - Get external adapter config → `./functions/get-external-adapter.md`
- `set_external_adapter` - Create/update external adapter → `./functions/set-external-adapter.md`
- `delete_external_adapter` - Delete external adapter → `./functions/delete-external-adapter.md`

### Live Sensor Commands (20)
- `get_processes` - Get running processes → `./functions/get-processes.md`
- `get_process_modules` - Get process modules/DLLs → `./functions/get-process-modules.md`
- `get_process_strings` - Extract strings from process memory → `./functions/get-process-strings.md`
- `get_network_connections` - Get network connections → `./functions/get-network-connections.md`
- `get_os_version` - Get OS version info → `./functions/get-os-version.md`
- `get_users` - Get system users → `./functions/get-users.md`
- `get_services` - Get services → `./functions/get-services.md`
- `get_drivers` - Get drivers/kernel modules → `./functions/get-drivers.md`
- `get_autoruns` - Get autorun entries → `./functions/get-autoruns.md`
- `get_packages` - Get installed packages → `./functions/get-packages.md`
- `get_registry_keys` - Get Windows registry keys → `./functions/get-registry-keys.md`
- `dir_list` - List directory contents → `./functions/dir-list.md`
- `dir_find_hash` - Find files by hash → `./functions/dir-find-hash.md`
- `find_strings` - Find strings in process memory → `./functions/find-strings.md`
- `yara_scan_process` - Scan process with YARA → `./functions/yara-scan-process.md`
- `yara_scan_file` - Scan file with YARA → `./functions/yara-scan-file.md`
- `yara_scan_directory` - Scan directory with YARA → `./functions/yara-scan-directory.md`
- `yara_scan_memory` - Scan memory with YARA → `./functions/yara-scan-memory.md`
- `reliable_tasking` - Execute reliable task → `./functions/reliable-tasking.md`
- `list_reliable_tasks` - List reliable tasks → `./functions/list-reliable-tasks.md`

### Detection & Response Rules (10)
- `get_detection_rules` - Get all detection rules → `./functions/get-detection-rules.md`
- `list_dr_general_rules` - List D&R general rules → `./functions/list-dr-general-rules.md`
- `get_dr_general_rule` - Get D&R general rule → `./functions/get-dr-general-rule.md`
- `set_dr_general_rule` - Create/update D&R general rule → `./functions/set-dr-general-rule.md`
- `delete_dr_general_rule` - Delete D&R general rule → `./functions/delete-dr-general-rule.md`
- `list_dr_managed_rules` - List D&R managed rules → `./functions/list-dr-managed-rules.md`
- `get_dr_managed_rule` - Get D&R managed rule → `./functions/get-dr-managed-rule.md`
- `set_dr_managed_rule` - Create/update D&R managed rule → `./functions/set-dr-managed-rule.md`
- `delete_dr_managed_rule` - Delete D&R managed rule → `./functions/delete-dr-managed-rule.md`
- `get_mitre_report` - Get MITRE ATT&CK report → `./functions/get-mitre-report.md`

### False Positive Rules (4)
- `get_fp_rules` - Get all FP rules → `./functions/get-fp-rules.md`
- `get_fp_rule` - Get FP rule → `./functions/get-fp-rule.md`
- `set_fp_rule` - Create/update FP rule → `./functions/set-fp-rule.md`
- `delete_fp_rule` - Delete FP rule → `./functions/delete-fp-rule.md`

### Generic Rules (Hive) (4)
- `list_rules` - List rules from any Hive → `./functions/list-rules.md`
- `get_rule` - Get rule from Hive → `./functions/get-rule.md`
- `set_rule` - Create/update rule in Hive → `./functions/set-rule.md`
- `delete_rule` - Delete rule from Hive → `./functions/delete-rule.md`

### Outputs (3)
- `list_outputs` - List outputs → `./functions/list-outputs.md`
- `add_output` - Create output → `./functions/add-output.md`
- `delete_output` - Delete output → `./functions/delete-output.md`

### Secrets (4)
- `list_secrets` - List secret names → `./functions/list-secrets.md`
- `get_secret` - Get secret value → `./functions/get-secret.md`
- `set_secret` - Create/update secret → `./functions/set-secret.md`
- `delete_secret` - Delete secret → `./functions/delete-secret.md`

### Lookups (5)
- `list_lookups` - List lookups → `./functions/list-lookups.md`
- `get_lookup` - Get lookup → `./functions/get-lookup.md`
- `set_lookup` - Create/update lookup → `./functions/set-lookup.md`
- `query_lookup` - Query lookup → `./functions/query-lookup.md`
- `delete_lookup` - Delete lookup → `./functions/delete-lookup.md`

### Playbooks (4)
- `list_playbooks` - List playbooks → `./functions/list-playbooks.md`
- `get_playbook` - Get playbook → `./functions/get-playbook.md`
- `set_playbook` - Create/update playbook → `./functions/set-playbook.md`
- `delete_playbook` - Delete playbook → `./functions/delete-playbook.md`

### Extensions (6)
- `list_extension_configs` - List extension configs → `./functions/list-extension-configs.md`
- `get_extension_config` - Get extension config → `./functions/get-extension-config.md`
- `set_extension_config` - Create/update extension config → `./functions/set-extension-config.md`
- `delete_extension_config` - Delete extension config → `./functions/delete-extension-config.md`
- `subscribe_to_extension` - Subscribe to extension → `./functions/subscribe-to-extension.md`
- `unsubscribe_from_extension` - Unsubscribe from extension → `./functions/unsubscribe-from-extension.md`

### YARA Rules (4)
- `list_yara_rules` - List YARA rules → `./functions/list-yara-rules.md`
- `get_yara_rule` - Get YARA rule → `./functions/get-yara-rule.md`
- `set_yara_rule` - Create/update YARA rule → `./functions/set-yara-rule.md`
- `delete_yara_rule` - Delete YARA rule → `./functions/delete-yara-rule.md`

### Artifacts (2)
- `list_artifacts` - List artifacts → `./functions/list-artifacts.md`
- `get_artifact` - Get artifact → `./functions/get-artifact.md`

### Event Schemas (5)
- `get_event_schema` - Get event schema → `./functions/get-event-schema.md`
- `get_event_schemas_batch` - Get multiple event schemas → `./functions/get-event-schemas-batch.md`
- `get_event_types_with_schemas` - List event types with schemas → `./functions/get-event-types-with-schemas.md`
- `get_event_types_with_schemas_for_platform` - List event types by platform → `./functions/get-event-types-with-schemas-for-platform.md`
- `get_platform_names` - Get platform names → `./functions/get-platform-names.md`

### Queries (6)
- `run_lcql_query` - Run LCQL query → `./functions/run-lcql-query.md`
- `list_saved_queries` - List saved queries → `./functions/list-saved-queries.md`
- `get_saved_query` - Get saved query → `./functions/get-saved-query.md`
- `set_saved_query` - Create/update saved query → `./functions/set-saved-query.md`
- `delete_saved_query` - Delete saved query → `./functions/delete-saved-query.md`
- `run_saved_query` - Run saved query → `./functions/run-saved-query.md`

### Searching & Detection History (5)
- `search_hosts` - Search hosts → `./functions/search-hosts.md`
- `search_iocs` - Search IOCs → `./functions/search-iocs.md`
- `batch_search_iocs` - Batch search IOCs → `./functions/batch-search-iocs.md`
- `get_historic_events` - Get historic events → `./functions/get-historic-events.md`
- `get_historic_detections` - Get historic detections → `./functions/get-historic-detections.md`

### AI-Powered Generation (6)
- `generate_lcql_query` - Generate LCQL query from natural language → `./functions/generate-lcql-query.md`
- `generate_dr_rule_detection` - Generate D&R detection component → `./functions/generate-dr-rule-detection.md`
- `generate_dr_rule_respond` - Generate D&R respond component → `./functions/generate-dr-rule-respond.md`
- `generate_sensor_selector` - Generate sensor selector expression → `./functions/generate-sensor-selector.md`
- `generate_python_playbook` - Generate Python playbook script → `./functions/generate-python-playbook.md`
- `generate_detection_summary` - Generate detection summary → `./functions/generate-detection-summary.md`

### Validation Tools (2)
- `validate_dr_rule_components` - Validate D&R rule components → `./functions/validate-dr-rule-components.md`
- `validate_yara_rule` - Validate YARA rule syntax → `./functions/validate-yara-rule.md`

## Additional Resources

For detailed information on using the MCP tool, see [CALLING_API.md](../CALLING_API.md).

### Handling Large Results

**The `limacharlie-api-executor` agent handles large results automatically.**

When API calls return large result sets (>100KB), the MCP tool returns a `resource_link` instead of inline data. The sub-agent will:

1. **Download** the data from the signed URL
2. **Analyze** the JSON schema to understand structure
3. **Extract** requested data using jq (if extraction instructions provided)
4. **Clean up** temporary files automatically
5. **Return** processed results to you

You don't need to handle this manually. Just include extraction instructions in your Task prompt:

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_sensors
    - Parameters: {\"oid\": \"...\"}
    - Extract: Count of total sensors and count of online sensors"
)
```

The agent will receive the `resource_link`, download the data, analyze the schema, extract the counts, and return:

```json
{
  "success": true,
  "data": {
    "total_sensors": 247,
    "online_sensors": 198
  },
  "metadata": {
    "function": "list_sensors",
    "result_size": "large",
    "extracted": true
  }
}
```

**Note**: If you need the full raw data (not extracted), omit the "Extract" instruction and the agent will return the complete dataset.

For more details on large result handling, see the agent documentation and [CALLING_API.md](../CALLING_API.md).
