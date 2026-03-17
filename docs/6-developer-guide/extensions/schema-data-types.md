# Schema Data Types

## All Data Types

The data types in your schema can be subdivided into three categories: Primitives, Code Blocks, and Objects (including records and tables). These data types allow for a cleaner UI and a more intuitive schema.

For a direct code reference, check out the type definitions in [Go](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go) or [Python](https://github.com/refractionPOINT/lc-extension/blob/master/python/lcextension/schema.py).

### Before you Start

When getting started, we recommend using the simplest data type applicable for each field in your schema to enable quick and reliable testing of your service.

## Schema Element Fields

Each field in a schema is a `SchemaElement` with the following properties:

| Field | Type | Description |
| --- | --- | --- |
| `label` | string | Human-readable label for the field |
| `description` | string | Description of the field |
| `placeholder` | string | Placeholder text to display |
| `data_type` | string | One of the data types listed below |
| `is_list` | bool | Whether this field accepts a list of items |
| `display_index` | int | Controls the display order in the UI |
| `default_value` | any | Default value for optional fields |
| `object` | object | If `data_type` is `object` or `record`, contains the nested schema definition |
| `enum_values` | list | If `data_type` is `enum`, the list of possible values |
| `complex_enum_values` | list | If `data_type` is `complex_enum`, list of objects with `label`, `value`, `category_key`, and `reference_link` fields |
| `filter` | object | Validation filters (see below) |

### Filters

Filters can be applied to restrict valid values for certain data types:

* `min` and `max`: apply to `integer`, `time`, and `duration` types
* `whitelist` and `blacklist`: apply to `event_name` and `string` types
* `valid_re` and `invalid_re`: apply to `string` types only (regex validation)
* `platforms`: applies to `sid` and `platform` types

!!! note
    Some filter combinations may not be fully supported for all types. Please reach out if a filter does not work as expected.

## Primitives

| Name | Description |
| --- | --- |
| `string` | Free-form text input |
| `text` | Multi-line text input |
| `integer` | Numeric integer value |
| `bool` | Boolean true/false toggle |
| `enum` | Single selection from a list. Requires the `enum_values` field |
| `complex_enum` | Detailed enum selection with categories, descriptions, and reference links. Requires the `complex_enum_values` field |
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
| `yara_rule_name` | Selector from your Organization's YARA rules (requires appropriate permissions) |
| `secret` | Selector from your Organization's secrets manager |

## Code Blocks

The following code block data types are available:

| Name | Description |
| --- | --- |
| `json` | JSON editor |
| `yaml` | YAML editor |
| `yara_rule` | YARA rule editor |
| `code` | Generic code editor |

!!! note
    YARA rule UI support is limited. Code blocks do not support the `is_list` field. If your extension requires a set of code blocks, wrap them in a key-value pair using the `record` data type (see Objects section below).

## Objects and Records

Objects and records provide structured, nested data. Objects group related fields together, while records define key-value collections where keys are user-specified.

### Single Objects

Plain objects allow for nested fields. They are visually the same as if the nested fields were flattened. The parent object's description provides additional context.

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

Records use the `record` data type to define key-value collections where each entry has a user-specified key and a structured value. The `key` field in the object definition specifies the key's name and type. Optional `element_name` and `element_desc` fields provide UI labels for each entry.

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
