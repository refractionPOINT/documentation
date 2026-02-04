# Schema Data Types

## All Data Types

The data types in your schema can be further subdivided into three categories. Primitives, Code Blocks, and Objects (including tables). These data types allow for a cleaner UI and a more intuitive schema.

For a direct code reference, check out the type definition [here](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go).

### Before you Start

When getting started, we recommend utilizing the simplest data type applicable for each field in your schema as to enable quick and reliable testing of your service.

## Primitives

The following is the list of primitive values. Note that the following fields are also affected by filters:

* number, time and date types are affected by `min` and `max`
* events and string types are affected by `whitelist` and `blacklist`
* only string types are affected by `valid_re` and `invalid_re` (regex)
* SID types (and maybe platforms) are affected by `platforms` filters

Oops, some fields may be missing support for filters

Please reach out if any of the above use-cases don't work as you might expect.

| name | description |
| --- | --- |
| string |  |
| integer |  |
| bool |  |
| enum | Requires the field `enum_values` |
| complex\_enum | a complex enum allows for a more detailed enum selection, including categories and description. Requires the field `complex_enum_values` |
| sid | your Organization's sensor ids |
| oid | your Organization's ID |
| platform |  |
| architecture |  |
| sensor\_selector |  |
| tag |  |
| duration |  |
| time |  |
| url |  |
| domain |  |
| yara\_rule\_name | Will show your Organization's list of yara rules available, if the user has permission |
| event\_name |  |
| secret | Will show your Organization's list of secrets as per the secrets manager |

## Code Blocks

There are currently 3 code types available:

1. JSON
2. YAML
3. Yara\_rule

Yara Rule UI Support is limited

Code blocks do not support the field `is_list`. If your extensions require a set of code blocks, we reocmmend wrapping it into key-value pair using the 'record' data type (see 'objects' section below).

## Objects (and tables)

While objects generally reflect a nested layer of abstraction, it's utility grows when using the field `is_list` to utilize the tables UI, or when defining a set of key-value pairs in the 'record' data type.

Note: there is a functional difference between an 'object' and 'record' data type.

**Single Objects**
 Plain objects allow for nested fields, and are visually indifferent from if the nested fields were flattened to begin with. They also allow for extra context to be wrapped in the parent object's description.

```text
table: {
  is_list: false,
  data_type: "object",
  object: {
    fields: { ... }, // key-value pairs
    requirements: null
  }
}
```

**Lists of Objects**
 Lists of objects display as tables and allow for a more complex and scalable data structure. Simply enable `is_list` on a base object.

```text
table: {
  is_list: true,
  data_type: "object",
  object: {
    fields: { ... }, // key-value pairs
    requirements: null
  }
}
```

**Record Type**
 Records are inherently lists of a key-value pair, where the value is the defined object, and the key may vary. Record types require a key to be defined in the nested object details, and also supports additional fields for the nested element's name and description.

```text
table: {
  is_list: true,
  data_type: "object",
  object: {
    key: {
      name: "key",
      data_type: "string"
    },
    element_name: "single row", // optional
    element_desc: "a single row that represents a key-value pair on a record type", // optional

    fields: { ... }, // key-value pairs
    requirements: null
  }
}
```
