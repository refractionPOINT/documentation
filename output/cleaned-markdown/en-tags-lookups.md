# Lookup Manager

The Lookup Manager is a powerful feature in LimaCharlie that allows you to create and manage lookup tables for enriching detections, automating responses, and correlating security data.

## Overview

Lookups are key-value stores that can be used in Detection & Response (D&R) rules, output destinations, and other automation workflows. They enable you to:

- Maintain allowlists and blocklists
- Store threat intelligence indicators
- Create asset inventories
- Manage configuration data
- Enrich events with contextual information

## Creating a Lookup

To create a lookup table:

1. Navigate to the **Lookups** section in your organization
2. Click **Add Lookup**
3. Provide a name for your lookup (use lowercase, numbers, and hyphens only)
4. Optionally add a description
5. Choose the lookup type:
   - **Simple**: Basic key-value pairs
   - **Resource**: Links to external resources
   - **List**: Simple list of values

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

## Using Lookups in D&R Rules

You can reference lookups in your Detection & Response rules using the `lookup()` function.

### Basic Lookup Syntax

```yaml
detect:
  op: lookup
  path: event/IP_ADDRESS
  lookup: my_blocklist
  case-sensitive: false
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

### Adding Entries

You can add entries to lookups through:

- **Web UI**: Manually add entries one at a time
- **REST API**: Programmatically manage lookup data
- **CLI**: Use the LimaCharlie CLI for bulk operations

### Bulk Import

To import data in bulk, use the REST API or CLI:

```bash
limacharlie lookup add --name my_lookup --key "example_key" --value "example_value"
```

### Updating Entries

Update existing entries by submitting a new value with the same key:

```bash
limacharlie lookup add --name my_lookup --key "existing_key" --value "new_value"
```

### Deleting Entries

Remove entries from a lookup:

```bash
limacharlie lookup del --name my_lookup --key "key_to_delete"
```

## Lookup Performance

Lookups are optimized for fast access:

- Cached at the sensor level for minimal latency
- Updated automatically when changes are made
- Supports thousands of entries with minimal performance impact

## Best Practices

1. **Naming Convention**: Use descriptive names like `ip_allowlist` or `threat_indicators`
2. **Documentation**: Add descriptions to explain the purpose of each lookup
3. **Regular Maintenance**: Review and update lookup data regularly
4. **Version Control**: Keep backups of critical lookup data
5. **Access Control**: Limit who can modify lookup tables
6. **Size Management**: Keep lookups focused and avoid storing unnecessary data

## API Reference

### Add or Update Entry

```
POST /v2/orgs/{oid}/lookup/{lookup_name}
Content-Type: application/json

{
  "key": "example_key",
  "value": "example_value"
}
```

### Get Entry

```
GET /v2/orgs/{oid}/lookup/{lookup_name}/{key}
```

### Delete Entry

```
DELETE /v2/orgs/{oid}/lookup/{lookup_name}/{key}
```

### List All Entries

```
GET /v2/orgs/{oid}/lookup/{lookup_name}
```

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