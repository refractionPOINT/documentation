I need to validate whether these two documents are about the same topic and then synthesize them appropriately.

Let me read both documents carefully:

1. **First document (en-tags-lookups)**: "Lookup Manager" - covers creating lookups, lookup types (Simple, Resource, List), using lookups in D&R rules, managing lookup data, API reference, best practices
2. **Second document (tags-lookups)**: "Lookup Manager" - covers the Lookup Manager extension, creating lookup tables, adding data, using lookups in D&R rules, lookup resources, managing data, best practices, automation

**Analysis**: Both documents are about the SAME topic - the Lookup Manager feature in LimaCharlie. They cover overlapping content but with some differences:
- First doc has more detail on lookup types (Simple, Resource, List)
- Second doc includes Python API examples and automation scripts
- Both cover D&R rule usage, management, and best practices
- Some terminology differences (lookup tables vs lookups)

These should be **MERGED** into a comprehensive single document while preserving ALL technical details from both.

# Lookup Manager

The Lookup Manager is a powerful feature in LimaCharlie that allows you to create and manage lookup tables for enriching detections, automating responses, and correlating security data.

## Overview

Lookups are key-value stores that can be referenced during event processing and used in Detection & Response (D&R) rules, pipelines, output destinations, and other automation workflows. They enable you to:

- Maintain allowlists and blocklists (IP addresses, domains, file hashes)
- Store threat intelligence indicators
- Create asset inventories (mapping hostnames to departments, criticality levels)
- Manage configuration data
- Enrich events with contextual information
- Store user/employee directories

## Creating a Lookup

### Via Web Interface

To create a lookup table:

1. Navigate to the **Lookups** or **Lookup Manager** section in your organization
2. Click **Add Lookup**
3. Provide a name for your lookup (use lowercase, numbers, and hyphens only)
4. Optionally add a description
5. Choose the lookup type or data format:
   - **Simple**: Basic key-value pairs
   - **Resource**: Links to external resources
   - **List**: Simple list of values
   - **CSV**: Tabular data with columns
6. Click **Create**

## Lookup Types

### Simple Lookups

Simple lookups store key-value pairs where both keys and values are strings.

**Example use case**: Store IP addresses with associated metadata

```yaml
key: 192.168.1.100
value: {"owner": "IT Department", "location": "HQ"}
```

### Resource Lookups

Resource lookups reference external URLs or resources that can be fetched and cached.

**Example use case**: Pull threat intelligence feeds from external sources

### List Lookups

List lookups store simple lists of values without keys.

**Example use case**: Maintain a list of known good executable hashes

### CSV Lookups

CSV lookups store tabular data with columns.

**Example use case**: Store structured asset inventory data with multiple attributes per entry

## Adding Data to Lookups

### Via Web Interface

1. Open your lookup table
2. Click **Add Entry** or **Import**
3. For key-value lookups: enter key and value
4. For CSV lookups: upload a CSV file or paste CSV data
5. Click **Save**

You can add entries to lookups manually through the web UI, one at a time.

### Via REST API

You can manage lookups programmatically using the LimaCharlie REST API.

#### Add or Update Entry

```
POST /v2/orgs/{oid}/lookup/{lookup_name}
Content-Type: application/json

{
  "key": "example_key",
  "value": "example_value"
}
```

#### Get Entry

```
GET /v2/orgs/{oid}/lookup/{lookup_name}/{key}
```

#### Delete Entry

```
DELETE /v2/orgs/{oid}/lookup/{lookup_name}/{key}
```

#### List All Entries

```
GET /v2/orgs/{oid}/lookup/{lookup_name}
```

### Via Python API

```python
from limacharlie import Manager

# Initialize manager
lc = Manager(oid='YOUR_ORG_ID', secret_api_key='YOUR_API_KEY')

# Add entries to a lookup
lc.lookup_add('my-lookup', {
    'key1': 'value1',
    'key2': 'value2'
})
```

### Via CLI

Use the LimaCharlie CLI for bulk operations:

```bash
limacharlie lookup add --name my_lookup --key "example_key" --value "example_value"
```

## Using Lookups in D&R Rules

You can reference lookups in your Detection & Response rules using the `lookup()` function.

### Lookup Resources

Lookups are referenced using the LimaCharlie Resource (LCR) syntax:

```
lcr://lookup/LOOKUP_NAME
```

For example:
- `lcr://lookup/allowed-ips`
- `lcr://lookup/critical-assets`
- `lcr://lookup/threat-indicators`

### Basic Lookup Syntax

```yaml
detect:
  op: lookup
  path: event/IP_ADDRESS
  lookup: my_blocklist
  case-sensitive: false
```

Or using LCR syntax:

```yaml
detect:
  event: NEW_PROCESS
  op: lookup
  path: event/FILE_PATH
  resource: 'lcr://lookup/known-bad-hashes'

respond:
  - action: report
    name: known_malware_execution
```

### Lookup Operators

- `lookup`: Check if a value exists in a lookup table
- `lookup_with_default`: Return a default value if key not found
- `lookup_many`: Check multiple values against a lookup

Example with default value:

```yaml
detect:
  event: NEW_PROCESS
  op: lookup_with_default
  path: event/USER_NAME
  resource: 'lcr://lookup/user-departments'
  default: 'unknown'
  value: 'finance'
```

### Example: Allowlist Detection

```yaml
detect:
  op: and
  rules:
    - op: is
      path: event/COMMAND_LINE
      value: powershell.exe
    - op: not
      rule:
        op: lookup
        path: event/HASH
        lookup: known_good_hashes
```

This rule detects PowerShell execution where the hash is NOT in the `known_good_hashes` lookup.

## Managing Lookup Data

### Updating Entries

You can update existing entries by submitting a new value with the same key:

**Via CLI:**
```bash
limacharlie lookup add --name my_lookup --key "existing_key" --value "new_value"
```

**Via UI:** Edit individual entries in the lookup table interface

**Via API:** Use `lookup_add()` to update existing keys (will overwrite)

### Deleting Entries

Remove entries from a lookup:

**Via CLI:**
```bash
limacharlie lookup del --name my_lookup --key "key_to_delete"
```

**Via UI:** Select entries and click **Delete**

**Via API:**
```python
# Delete specific keys
lc.lookup_delete('my-lookup', ['key1', 'key2'])
```

### Clearing a Lookup

To remove all entries from a lookup table:

```python
# Clear all entries
lc.lookup_clear('my-lookup')
```

## Lookup Performance

Lookups are optimized for fast access:

- Cached at the sensor level for minimal latency
- Lookup operations are very fast (typically < 1ms)
- Lookups are cached in memory for quick access
- Updated automatically when changes are made
- Supports thousands of entries with minimal performance impact
- Large lookups (>100k entries) may impact memory usage
- Consider using external integrations for very large datasets (>1M entries)

## Best Practices

1. **Naming Convention**: Use descriptive names like `ip_allowlist` or `threat_indicators`. Use lowercase names with hyphens (e.g., `known-bad-domains`)
2. **Documentation**: Add descriptions to explain the purpose of each lookup and data format
3. **Regular Maintenance**: Review and update lookup data regularly, especially threat intelligence lookups
4. **Version Control**: Keep backups of critical lookup data
5. **Access Control**: Limit who can modify lookup tables using appropriate permissions
6. **Size Management**: Keep lookups focused and avoid storing unnecessary data. Keep lookup tables reasonably sized for performance. Very large datasets may be better suited for external integrations
7. **Testing**: Test D&R rules that reference lookups to ensure proper behavior

## Common Use Cases

### Threat Intelligence

Store indicators of compromise (IOCs) and check events against them:

```yaml
detect:
  op: lookup
  path: event/FILE_HASH
  lookup: malware_hashes
```

### Asset Management

Maintain an inventory of critical assets:

```yaml
detect:
  op: and
  rules:
    - op: lookup
      path: event/IP_ADDRESS
      lookup: critical_assets
    - op: is
      path: event/EVENT_TYPE
      value: NETWORK_CONNECTIONS
```

### User Allowlisting

Exclude known admin activity from alerts:

```yaml
detect:
  op: not
  rule:
    op: lookup
    path: event/USER_NAME
    lookup: admin_users
```

## Automation

Automate lookup updates using the API in scheduled scripts:

```python
import requests
from limacharlie import Manager

def update_threat_feed():
    # Fetch latest threat intel
    response = requests.get('https://threat-feed.example.com/indicators.json')
    indicators = response.json()
    
    # Update lookup
    lc = Manager(oid='YOUR_ORG_ID', secret_api_key='YOUR_API_KEY')
    
    # Convert to key-value format
    lookup_data = {indicator['value']: indicator['type'] for indicator in indicators}
    
    # Update lookup (replaces all entries)
    lc.lookup_clear('threat-indicators')
    lc.lookup_add('threat-indicators', lookup_data)

# Run periodically via cron or similar
update_threat_feed()
```

## Troubleshooting

### Lookup Not Found Error

If you get a "lookup not found" error in a D&R rule:
1. Verify the lookup name is correct (case-sensitive)
2. Check that the lookup exists in your organization
3. Ensure proper LCR syntax: `lcr://lookup/LOOKUP_NAME`

### Performance Issues

If lookups are causing performance problems:
1. Check the size of your lookup tables
2. Consider splitting large lookups into smaller, more specific ones
3. Review how frequently lookups are being updated
4. Contact support for optimization guidance