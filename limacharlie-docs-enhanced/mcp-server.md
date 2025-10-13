# MCP Server
Overview

 The Model Context Protocol (MCP) is a standardized protocol used by AI Agents to access and leverage external tools and resources.

 Note that MCP itself is still experimental and cutting edge.

 LimaCharlie offers an MCP server at <https://mcp.limacharlie.io> which enables AI agents to:

* **Query and analyze** historical telemetry from any sensor
* **Actively investigate** endpoints using the LimaCharlie Agent (EDR) in real-time
* **Take remediation actions** like isolating endpoints, killing processes, and managing tags
* **Generate content** using AI-powered tools for LCQL queries, D&R rules, playbooks, and detection summaries
* **Manage platform configuration** including rules, outputs, adapters, secrets, and more
* **Access threat intelligence** through IOC searches and MITRE ATT&CK mappings

 This opens up the entire LimaCharlie platform to AI agents, regardless of their implementation or location.

## Transport Modes

 The server supports two transport modes based on the PUBLIC\_MODE environment variable:

### STDIO Mode (PUBLIC\_MODE=false, default)

 Used for local MCP clients like Claude Desktop or Claude Code:

* Communication through stdin/stdout using JSON-RPC
* Uses LimaCharlie SDK's default authentication
* Reads credentials from environment variables or config files

### HTTP Mode (PUBLIC\_MODE=true)

 Used when deploying as a public service:

* Server runs as a stateless HTTP API with JSON responses
* Authentication via HTTP headers
* Supports multiple organizations concurrently
* Run with: `uvicorn server:app`

## Requirements & Authentication

### For HTTP Mode

 The server requires authentication headers:

 1. **Authorization header** in one of these formats:

* `Authorization: Bearer <jwt>` (OID must be in x-lc-oid header)
* `Authorization: Bearer <jwt>:<oid>` (combined format)
* `Authorization: Bearer <api_key>:<oid>` (API key with OID)

 2. **x-lc-oid header** (if not included in Authorization):

* `x-lc-oid: <organization_id>`

### For STDIO Mode

 Set environment variables:

* `LC_OID`: Your LimaCharlie Organization ID
* `LC_API_KEY`: Your LimaCharlie API key
* `GOOGLE_API_KEY`: For AI-powered generation features (optional)

## Capabilities

 The LimaCharlie MCP server exposes over 100 tools organized by category:

### Investigation & Telemetry

* **Process inspection**: `get_processes`, `get_process_modules`, `get_process_strings`, `yara_scan_process`
* **System information**: `get_os_version`, `get_users`, `get_services`, `get_drivers`, `get_autoruns, get_packages`
* **Network analysis**: `get_network_connections`, `is_online`, `get_online_sensors`
* **File operations**: `find_strings`, `yara_scan_file`, `yara_scan_directory`, `yara_scan_memory`
* **Registry access**: `get_registry_keys`
* **Historical data**: `get_historic_events`, `get_historic_detections`, `get_time_when_sensor_has_data`

### Threat Response & Remediation

* **Network isolation**: `isolate_network`, `rejoin_network`, `is_isolated`
* **Sensor management**: `add_tag`, `remove_tag`, `delete_sensor`
* **Reliable tasking**: `reliable_tasking`, `list_reliable_tasks`

### AI-Powered Generation (requires GOOGLE\_API\_KEY)

* **Query generation**: `generate_lcql_query` - Create LCQL queries from natural language
* **Rule creation**: `generate_dr_rule_detection`, `generate_dr_rule_respond` - Generate D&R rules
* **Automation**: `generate_python_playbook` - Create Python playbooks
* **Analysis**: `generate_detection_summary` - Summarize detection data
* **Sensor selection**: `generate_sensor_selector` - Generate sensor selectors

### Platform Configuration

* **Detection & Response**: `get_detection_rules`, `set_dr_general_rule`, `set_dr_managed_rule`, `delete_dr_general_rule`
* **False Positive Management**: `get_fp_rules`, `set_fp_rule`, `delete_fp_rule`
* **YARA Rules**: `list_yara_rules`, `set_yara_rule`, `validate_yara_rule`, `delete_yara_rule`
* **Outputs & Adapters**: `list_outputs`, `add_output`, `delete_output`, `list_external_adapters`, `set_external_adapter`
* **Extensions**: `list_extension_configs`, `set_extension_config`, `delete_extension_config`
* **Playbooks**: `list_playbooks`, `set_playbook`, `delete_playbook`
* **Secrets Management**: `list_secrets`, `set_secret`, `delete_secret`
* **Saved Queries**: `list_saved_queries`, `set_saved_query`, `run_saved_query`
* **Lookups**: `list_lookups`, `set_lookup`, `query_lookup`, `delete_lookup`

### Threat Intelligence

* **IOC Search**: `search_iocs`, `batch_search_iocs`
* **Host Search**: `search_hosts`
* **MITRE ATT&CK**: `get_mitre_report`

### Administrative

* **API Keys**: `list_api_keys`, `create_api_key`, `delete_api_key`
* **Installation Keys**: `list_installation_keys`, `create_installation_key`, `delete_installation_key`
* **Cloud Sensors**: `list_cloud_sensors`, `set_cloud_sensor`, `delete_cloud_sensor`
* **Organization Info**: `get_org_info`, `get_usage_stats`
* **Artifacts**: `list_artifacts`, `get_artifact`

### Schema & Documentation

* **Event Schemas**: `get_event_schema`, `get_event_schemas_batch`, `get_event_types_with_schemas`
* **Platform Support**: `get_platform_names`, `list_with_platform`, `get_event_types_with_schemas_for_platform`

## Advanced Features

### Large Result Handling

 The server automatically handles large responses by uploading them to Google Cloud Storage (if configured):

* Set `GCS_BUCKET_NAME` for the storage bucket
* Configure `GCS_TOKEN_THRESHOLD` (default: 1000 tokens)
* Results are returned as signed URLs valid for 24 hours

### LCQL Query Execution

 The `run_lcql_query` tool supports:

* Streaming results for real-time monitoring
* Flexible time windows and limits
* Output formatting options

## Examples

### Claude Desktop/Code Configuration (STDIO)

```
  {
    "mcpServers": {
      "limacharlie": {
        "command": "python3",
        "args": ["/path/to/server.py"],
        "env": {
          "LC_OID": "your-org-id",
          "LC_API_KEY": "your-api-key",
          "GOOGLE_API_KEY": "your-google-api-key"
        }
      }
    }
  }
```

### HTTP Service Usage

```bash
claude mcp add --transport http limacharlie https://mcp.limacharlie.io/mcp \
--header "Authorization: Bearer API_KEY:OID" \
--header "x-lc-oid: OID"
```

## Environment Variables

* `PUBLIC_MODE`: Set to true for HTTP mode, false for STDIO (default: false)
* `GOOGLE_API_KEY`: API key for AI-powered features
* `GCS_BUCKET_NAME`: Google Cloud Storage bucket for large results
* `GCS_SIGNER_SERVICE_ACCOUNT`: Service account for GCS URL signing
* `GCS_TOKEN_THRESHOLD`: Token count threshold for GCS upload (default: 1000)
* `GCS_URL_EXPIRY_HOURS`: Hours until GCS URLs expire (default: 24)
* `LC_OID`: Organization ID (STDIO mode only)
* `LC_API_KEY`: API key (STDIO mode only)

## Notes

* The server is stateless when running in HTTP mode
* HTTP mode uses JSON responses (not Server-Sent Events)
* No OAuth flow is used - authentication is via bearer tokens only
* If you encounter missing capabilities, contact <https://community.limacharlie.com> for quick additions