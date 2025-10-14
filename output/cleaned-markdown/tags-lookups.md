# Lookup Manager

The Lookup Manager extension provides a centralized way to manage lookup tables in LimaCharlie. Lookup tables allow you to store reference data that can be used in Detection & Response (D&R) rules, pipelines, and other parts of the platform.

## Overview

Lookup tables are key-value stores that can be referenced during event processing. Common use cases include:

- Allowlists/denylists (IP addresses, domains, file hashes)
- Asset inventories (mapping hostnames to departments, criticality levels)
- Threat intelligence feeds
- Configuration data
- User/employee directories

## Creating a Lookup Table

1. Navigate to **Lookup Manager** in the LimaCharlie web interface
2. Click **Add Lookup**
3. Provide a unique name for your lookup table
4. (Optional) Add a description
5. Choose the data format:
   - **Key-Value**: Simple key-value pairs
   - **CSV**: Tabular data with columns
6. Click **Create**

## Adding Data to Lookups

### Via Web Interface

1. Open your lookup table
2. Click **Add Entry** or **Import**
3. For key-value lookups: enter key and value
4. For CSV lookups: upload a CSV file or paste CSV data
5. Click **Save**

### Via API

You can manage lookups programmatically using the LimaCharlie API:

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

## Using Lookups in D&R Rules

Reference lookup tables in your Detection & Response rules using the `lookup()` function:

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

## Lookup Resources

Lookups are referenced using the LimaCharlie Resource (LCR) syntax:

```
lcr://lookup/LOOKUP_NAME
```

For example:
- `lcr://lookup/allowed-ips`
- `lcr://lookup/critical-assets`
- `lcr://lookup/threat-indicators`

## Managing Lookup Data

### Updating Entries

- Via UI: Edit individual entries in the lookup table interface
- Via API: Use `lookup_add()` to update existing keys (will overwrite)

### Deleting Entries

- Via UI: Select entries and click **Delete**
- Via API: Use `lookup_delete()` to remove specific keys

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

## Best Practices

1. **Naming Convention**: Use descriptive, lowercase names with hyphens (e.g., `known-bad-domains`)
2. **Size Limits**: Keep lookup tables reasonably sized for performance. Very large datasets may be better suited for external integrations
3. **Updates**: Regularly update threat intelligence lookups to maintain accuracy
4. **Documentation**: Add descriptions to lookup tables explaining their purpose and data format
5. **Access Control**: Use appropriate permissions to control who can modify lookup tables
6. **Testing**: Test D&R rules that reference lookups to ensure proper behavior

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

## Performance Considerations

- Lookup operations are very fast (typically < 1ms)
- Lookups are cached in memory for quick access
- Large lookups (>100k entries) may impact memory usage
- Consider using external integrations for very large datasets (>1M entries)

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