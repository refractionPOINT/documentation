# LimaCharlie Essentials Plugin

Essential LimaCharlie skills for API access, sensor management, detection engineering, and security operations. Includes 116 comprehensive skills covering core operations, historical data, forensics, detection rules, configuration management, and administration. Includes a specialized script for efficiently analyzing large API result sets.

## Important: Organization ID (OID) Requirements

**⚠️ OID is a UUID, not an Organization Name**

Most skills in this plugin require an **Organization ID (OID)**, which is a UUID like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`, **NOT** the human-readable organization name.

**To get your OID:**
```
Use the `list-user-orgs` skill to see all organizations you have access to and their corresponding OIDs.
```

This skill returns a mapping of organization names to their UUIDs, which you'll need for most other operations.

**Exception - Skills that don't require a specific OID:**

A small number of skills operate at the user-level or global level and **do not require a specific organization ID**. For these skills, **omit the `oid` parameter` when calling the API:

- **`list-user-orgs`** - Lists all organizations you have access to (user-level operation)
- **`create-org`** - Creates a new organization (user-level operation)
- **`get-platform-names`** - Gets list of platform names from ontology (global operation)

All other 113 skills require a valid, specific organization ID.

## What It Does

This plugin provides 116 comprehensive skills:

### Skills Organized by Category

### Core Operations & Documentation
- **Documentation Search**: Intelligent search through LimaCharlie docs (platform, Python SDK, Go SDK)
- **Organization Management**: List orgs, get org info, create orgs, manage API keys
- **Sensor Management**: List/search/delete sensors, get sensor info, check online status

### Event Schemas & Telemetry
- **Event Schemas**: Get schemas for event types, list available events by platform
- **Platform Support**: Get platform names and platform-specific event types

### Live Sensor Interaction
- **Process Investigation**: Get processes, modules, strings, YARA scan processes
- **Network Analysis**: Get network connections, investigate C2 communications
- **System Forensics**: Get OS version, users, services, drivers, autoruns, packages
- **File System**: List directories, find files by hash, string search across processes
- **Windows Registry**: Query registry keys and values (Windows sensors only)
- **YARA Scanning**: Scan processes, files, directories, and memory with YARA rules

### Detection & Response
- **D&R Rules**: List, get, create, update, delete detection rules (general and managed)
- **False Positive Rules**: Manage FP rules to suppress known-good detections
- **YARA Rules**: Manage organization-wide YARA rules for threat hunting
- **Rule Validation**: Validate D&R rule components and YARA syntax

### Historical Data & Investigation
- **Historic Events**: Query historical telemetry using LCQL
- **Historic Detections**: Search past detection hits
- **LCQL Queries**: Run LCQL queries, manage saved queries
- **IOC Search**: Search for IoCs (IPs, domains, hashes) across historical data
- **Host Search**: Search for hosts by hostname or other attributes

### Configuration & Integrations
- **Extensions**: List, get, create, update, delete extension configs
- **Outputs**: Manage output destinations (SIEM, cloud storage, webhooks)
- **External Adapters**: Configure cloud sensors and external data sources
- **Secrets**: Securely store and manage credentials for integrations
- **Lookups**: Manage lookup tables for enrichment

### Response & Tasking
- **Network Isolation**: Isolate/rejoin sensors from the network
- **Reliable Tasking**: Execute commands on sensors with guaranteed delivery
- **Playbooks**: Manage automated response playbooks

### Advanced Features
- **Installation Keys**: Create and manage sensor deployment keys
- **Tags**: Add/remove tags from sensors
- **Artifacts**: List and retrieve artifacts from investigations
- **MITRE ATT&CK**: Get MITRE ATT&CK coverage reports
- **Billing & Usage**: View usage stats, billing details, SKU definitions

## Usage Examples

### Getting Started
```
"List all my organizations" → Uses list-user-orgs
"Show me all sensors in my org" → Uses list-sensors
"Get event schema for DNS_REQUEST" → Uses get-event-schema
```

### Investigation
```
"Get running processes on sensor XYZ" → Uses get-processes
"Show network connections for sensor ABC" → Uses get-network-connections
"YARA scan process 1234 on sensor DEF" → Uses yara-scan-process
"Search for IP 1.2.3.4 in historical data" → Uses search-iocs
```

### Detection Engineering
```
"List all D&R rules" → Uses list-rules
"Create a new D&R rule for suspicious PowerShell" → Uses set-rule
"Get all detections from the last 24 hours" → Uses get-historic-detections
```

### Configuration
```
"Configure Slack output" → Uses add-output
"Create installation key for production deployment" → Uses create-installation-key
"Set up cloud sensor for AWS CloudTrail" → Uses set-cloud-sensor
```

## How It Works

Skills in this plugin connect to the LimaCharlie API via MCP (Model Context Protocol) to:

1. **Authenticate** using your LimaCharlie API credentials
2. **Execute operations** against your organization(s)
3. **Return results** in a structured, readable format

Most skills require:
- **OID**: Organization ID (UUID) - get this via `list-user-orgs`
- **Additional parameters**: Sensor IDs, rule names, query parameters, etc.

### Large Result Handling

When API calls return large datasets (>100KB), the response includes a `resource_link` URL. To work with these large result sets:

1. **Download**: Use curl to download the resource_link to a temp file
2. **Analyze**: Run the `analyze-lc-result.sh` script to understand the JSON structure
3. **Extract**: Use jq queries to extract the specific information you need
4. **Cleanup**: Remove the temp file when done

The analyze script outputs a JSON schema showing object keys, array patterns, and data types, allowing you to craft precise jq queries to extract only the information you need—keeping your conversation context clean and focused.

See [CALLING_API.md](./CALLING_API.md) for details on how large result handling works.

## Documentation Coverage

- **Platform Documentation**: Complete LimaCharlie platform docs
- **Python SDK**: Python SDK reference and examples
- **Go SDK**: Go SDK reference and examples
- **API Reference**: Direct API access documentation

## Skills Summary

See [SKILLS_SUMMARY.md](./SKILLS_SUMMARY.md) for a complete list of all 120 skills with descriptions.

## API Calling Guide

See [CALLING_API.md](./CALLING_API.md) for comprehensive documentation on making direct API calls to LimaCharlie.
