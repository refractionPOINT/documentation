---
name: limacharlie-call
description: Perform LimaCharlie API operations using Haiku sub-agent. Access 124 functions for sensors, rules, outputs, cloud integrations, artifacts, AI-powered generation, and validation. Load function references on-demand from ./functions/ directory.
allowed-tools: Task, Read, Bash
---

# LimaCharlie API Operations

Perform any LimaCharlie operation by dynamically loading function references.

## Core Concepts

**⚠️ CRITICAL**: The Organization ID (OID) is a **UUID** (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name.
- If you don't have the OID, use `list-user-orgs` function first to get the UUID from the org name
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

If you don't have the OID (Organization ID), get it first with `list-user-orgs`:

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
- `get-time-when-sensor-has-data` - Check when sensor has data, data availability timeline, sensor overview
- `get-historic-events` - Query historical telemetry events
- `get-historic-detections` - Query historical detection alerts

### Sensor Status & Health
- `is-online` - Check if sensor is currently online
- `get-online-sensors` - List all online sensors
- `get-sensor-info` - Get detailed sensor information
- `list-sensors` - List all sensors in organization
- `list-with-platform` - Filter sensors by OS platform

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

## Available Functions (124)

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
