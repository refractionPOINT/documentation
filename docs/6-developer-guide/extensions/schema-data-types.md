# Schema Data Types

## All Data Types

The data types in your schema have three categories: Primitives, Code Blocks, and Objects (which include records and tables). These data types give a cleaner UI and a more intuitive schema.

For a direct code reference, see the type definitions in [Go](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go) or [Python](https://github.com/refractionPOINT/lc-extension/blob/master/python/lcextension/schema.py).

### Before you Start

When you start, use the simplest data type that applies to each field in your schema. A simple data type lets you test your service quickly and reliably.

## Schema Element Fields

Each field in a schema is a `SchemaElement` with these properties:

| Field | Type | Description |
| --- | --- | --- |
| `label` | string | Human-readable label for the field |
| `description` | string | Description of the field |
| `placeholder` | string | Placeholder text to display |
| `data_type` | string | One of the data types listed below |
| `is_list` | bool | Shows if this field accepts a list of items |
| `display_index` | int | Controls the display order in the UI |
| `default_value` | any | Default value for optional fields |
| `object` | object | If `data_type` is `object` or `record`, contains the nested schema definition |
| `enum_values` | list | If `data_type` is `enum`, the list of possible values |
| `complex_enum_values` | list | If `data_type` is `complex_enum`, list of objects with `label`, `value`, `category_key`, and `reference_link` fields |
| `filter` | object | Validation filters (see below) |

### Filters

Use filters to restrict the valid values for certain data types:

- `min` and `max`: apply to `integer`, `time`, and `duration` types
- `whitelist` and `blacklist`: apply to `event_name` and `string` types
- `valid_re` and `invalid_re`: apply to `string` types only (regex validation)
- `platforms`: applies to `sid` and `platform` types

!!! note
    Not all filter combinations have full support for all types. Ask for help if a filter does not work as you expect.

## Primitives

| Name | Description |
| --- | --- |
| `string` | Free-form text input |
| `text` | Multi-line text input |
| `integer` | Numeric integer value |
| `bool` | Boolean true/false toggle |
| `enum` | Single selection from a list. Needs the `enum_values` field |
| `complex_enum` | Detailed enum selection with categories, descriptions, and reference links. Needs the `complex_enum_values` field |
| `sid` | Sensor ID selector from your Organization's sensors |
| `oid` | Your Organization's ID |
| `platform` | Platform selector |
| `architecture` | Architecture selector |
| `sensor_selector` | Sensor selector expression |
| `tag` | Sensor tag selector |
| `duration` | Duration in milliseconds |
| `time` | Timestamp in milliseconds since epoch |
| `url` | URL input |
| `domain` | Domain name input |
| `event_name` | Event name selector |
| `yara_rule_name` | Selector from your Organization's YARA rules (needs the appropriate permissions) |
| `secret` | Selector from your Organization's secrets manager |

## Code Blocks

These code block data types are available:

| Name | Description |
| --- | --- |
| `json` | JSON editor |
| `yaml` | YAML editor |
| `yara_rule` | YARA rule editor |
| `code` | Generic code editor |

!!! note
    YARA rule UI support is limited. Code blocks do not support the `is_list` field. If your extension needs a set of code blocks, put them in a key-value pair with the `record` data type (see the Objects section below).

## Objects and Records

Objects and records give structured, nested data. Objects group related fields together. Records define key-value collections in which the user specifies the keys.

### Single Objects

Plain objects allow nested fields. In the UI, they look the same as flattened nested fields. The description of the parent object gives more context.

```json
{
  "my_config": {
    "data_type": "object",
    "is_list": false,
    "description": "Configuration group",
    "object": {
      "fields": {
        "field_a": { "data_type": "string", "description": "..." },
        "field_b": { "data_type": "integer", "description": "..." }
      },
      "requirements": null
    }
  }
}
```

### Lists of Objects

Lists of objects display as tables in the UI. Enable `is_list` on an object to create a table.

```json
{
  "my_table": {
    "data_type": "object",
    "is_list": true,
    "description": "A table of entries",
    "object": {
      "fields": {
        "name": { "data_type": "string", "description": "Entry name" },
        "value": { "data_type": "string", "description": "Entry value" }
      },
      "requirements": null
    }
  }
}
```

### Records

Records use the `record` data type to define key-value collections. Each entry has a key that the user specifies and a structured value. The `key` field in the object definition sets the name and the type of the key. The optional `element_name` and `element_desc` fields give UI labels for each entry.

```json
{
  "my_records": {
    "data_type": "record",
    "is_list": true,
    "description": "A set of named configurations",
    "object": {
      "key": {
        "name": "config_name",
        "data_type": "string"
      },
      "element_name": "configuration",
      "element_desc": "A named configuration entry",
      "fields": {
        "enabled": { "data_type": "bool", "description": "Whether this config is active" },
        "threshold": { "data_type": "integer", "description": "Alert threshold" }
      },
      "requirements": null
    }
  }
}
```
