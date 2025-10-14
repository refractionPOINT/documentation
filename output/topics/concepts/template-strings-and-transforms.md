# Template Strings and Transforms

Many areas of LimaCharlie support template strings and transforms, providing flexible data manipulation capabilities for customizing configurations, transforming data during ingestion, and modifying output formats.

## Overview

**Template Strings** allow you to customize configuration values based on context. For example, you can adjust a Detection Name in a D&R rule to include values from the detection itself.

**Transforms** enable you to change the shape of JSON data in flight, including moving, renaming, removing, and adding fields. For example, you can create an Output that works with `DNS_REQUEST` events but outputs only specific fields.

## Template Strings

Template strings in LimaCharlie use the format defined by Go "text templates" found in the [Go text/template documentation](https://pkg.go.dev/text/template). A useful guide is also available from [Hashicorp](https://learn.hashicorp.com/tutorials/nomad/go-template-syntax).

### Basic Example

A simple D&R rule customizing the detection name:

```yaml
- action: report
  name: Evil executable on {{ .routing.hostname }}
```

### LimaCharlie-Specific Functions

Template strings support these custom functions:

* `token`: applies MD5 hashing to the value provided
* `anon`: applies MD5 hashing to a secret seed value plus the value provided (for anonymization)
* `json`: marshals the input into a JSON string representation
* `prettyjson`: same as `json` but with indentation and newlines
* `parsetime`: parse a time format to another
* `split`: split a string based on a separator parameter
* `join`: join a list into a string joined by another string
* `replace`: replace all instances of a string with another
* `base`: return the file name in a file path
* `dir`: return the base directory path from a file path

### Anonymization Example

The `token` and `anon` functions can partially anonymize data:

```yaml
- action: report
  name: 'User {{token .event.USER_NAME }} accessed a website against policy.'
```

### Additional Examples

* `Full Data: {{prettyjson .event.OBJECT }}`
* `Original time:{{parsetime "{\"from\":\"2006/01/02 15:04:05\", \"to\":\"2006-01-02 15:04:05 MST\"}" .event.timestamp}}`
* `Packages: {{join "," .event.PACKAGES}}`

### Template Strings with Adapter Transforms

Template strings can be used with the `client_options.mapping.transform` option in Adapter configuration to modify data prior to ingestion, controlling which fields get ingested and their resulting names.

Available operators in Adapter configurations:

* `+` to add a field
* `-` to remove a field

Both support template strings for adding/removing values from JSON data.

#### Adapter Transform Example

Given this input data:

```json
{ "event":
  "webster" : {
     "a" : 1,
     "b" : 2,
     "d" : 3
    }
  }
}
```

To rename the `d` value to `c` on ingestion, remove the `d` field, and add a `hostname` field:

```yaml
client_options:
  mapping:
    transform:
      +c : '{{ .webster.d }}'
      -d: nil
      +hostname : '{{ "my-computer" }}'
```

Resulting ingested event:

```json
{ "event":
  "webster" : {
     "a" : 1,
     "b" : 2,
     "c" : 3
    },
    "hostname" : "my-computer"
  }
}
```

## Transforms

Transforms specify a JSON object that describes the transformation. The object structure matches the desired final JSON output shape.

### Transform Value Types

Key names are literal output key names. Values support three types:

1. **Template Strings**: Generated and placed at the corresponding key location in the output
2. **gjson selector**: Selects subsets of the input object and maps them within the output (syntax defined in [gjson documentation](https://github.com/tidwall/gjson/blob/master/SYNTAX.md))
3. **JSON objects**: Present as-is in the output

### Complete Transform Example

**Input:**

```json
{
    "event": {
        "EVENT": {
            "EventData": {
                "AuthenticationPackageName": "NTLM",
                "FailureReason": "%%2313",
                "IpAddress": "34.64.101.177",
                "IpPort": "0",
                "KeyLength": "0",
                "LmPackageName": "-",
                "LogonProcessName": "NtLmSsp",
                "LogonType": "3",
                "ProcessId": "0x0",
                "ProcessName": "-",
                "Status": "0xc000006d",
                "SubStatus": "0xc0000064",
                "SubjectDomainName": "-",
                "SubjectLogonId": "0x0",
                "SubjectUserName": "-",
                "SubjectUserSid": "S-1-0-0",
                "TargetDomainName": "",
                "TargetUserName": "ADMINISTRADOR",
                "TargetUserSid": "S-1-0-0",
                "TransmittedServices": "-",
                "WorkstationName": "-"
            },
            "System": {
                "Channel": "Security",
                "Computer": "demo-win-2016",
                "Correlation": {
                    "ActivityID": "{F207C050-075F-0001-AFE1-ED1F3897D801}"
                },
                "EventID": "4625",
                "EventRecordID": "2832700",
                "Execution": {
                    "ProcessID": "572",
                    "ThreadID": "2352"
                },
                "Keywords": "0x8010000000000000",
                "Level": "0",
                "Opcode": "0",
                "Provider": {
                    "Guid": "{54849625-5478-4994-A5BA-3E3B0328C30D}",
                    "Name": "Microsoft-Windows-Security-Auditing"
                },
                "Security": "",
                "Task": "12544",
                "TimeCreated": {
                    "SystemTime": "2022-07-15T22:48:24.996361600Z"
                },
                "Version": "0"
            }
        }
    },
    "routing": {
        "arch": 2,
        "did": "b97e9d00-ca17-4afe-a9cf-27c3468d5901",
        "event_id": "f24679e5-5484-4ca1-bee2-bfa09a5ba3db",
        "event_time": 1657925305984,
        "event_type": "WEL",
        "ext_ip": "35.184.178.65",
        "hostname": "demo-win-2016.c.lc-demo-infra.internal",
        "iid": "7d23bee6-aaaa-aaaa-aaaa-c8e8cca132a1",
        "int_ip": "10.128.0.2",
        "moduleid": 2,
        "oid": "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",
        "plat": 268435456,
        "sid": "bb4b30af-ff11-4ff4-836f-f014ada33345",
        "tags": ["edr", "lc:stable"],
        "this": "c5e16360c71baf3492f2dcd962d1eeb9"
    },
    "ts": "2022-07-15 22:48:25"
}
```

**Transform Definition:**

```json
{
    "message": "Interesting event from {{ .routing.hostname }}",
    "from": "{{ \"limacharlie\" }}",
    "dat": {
        "raw": "event.EVENT.EventData"
    },
    "anon_ip": "{{anon .routing.int_ip }}",
    "ts": "routing.event_time",
    "nope": "does.not.exist"
}
```

**Output:**

```json
{
    "dat": {
        "raw": {
            "AuthenticationPackageName": "NTLM",
            "FailureReason": "%%2313",
            "IpAddress": "34.64.101.177",
            "IpPort": "0",
            "KeyLength": "0",
            "LmPackageName": "-",
            "LogonProcessName": "NtLmSsp",
            "LogonType": "3",
            "ProcessId": "0x0",
            "ProcessName": "-",
            "Status": "0xc000006d",
            "SubStatus": "0xc0000064",
            "SubjectDomainName": "-",
            "SubjectLogonId": "0x0",
            "SubjectUserName": "-",
            "SubjectUserSid": "S-1-0-0",
            "TargetDomainName": "",
            "TargetUserName": "ADMINISTRADOR",
            "TargetUserSid": "S-1-0-0",
            "TransmittedServices": "-",
            "WorkstationName": "-"
        }
    },
    "from": "limacharlie",
    "message": "Interesting event from demo-win-2016.c.lc-demo-infra.internal",
    "nope": null,
    "ts": 1657925305984,
    "anon_ip": "e80b5017098950fc58aad83c8c14978e"
}
```

### Transforming Output Data

When passing events to an output, you can transform the original event in multiple ways. Custom Transforms are applied in the CUSTOM TRANSFORM area when creating an output.

![Custom Transform Configuration](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(310).png)

## Practical Examples

### Extracting Fields from Telemetry

Given a 4625 failed logon event, to send only specific fields to an output:

**Input Event:**

```json
{
  "event": {
    "EVENT": {
      "EventData": {
        "AuthenticationPackageName": "NTLM",
        "FailureReason": "%%2313",
        "IpAddress": "142.99.21.14",
        "TargetUserName": "administrator",
        "WorkstationName": "D-483"
      },
      "System": {
        "Channel": "Security",
        "Computer": "demo-win-2016",
        "EventID": "4625",
        "EventRecordID": "22690646",
        "TimeCreated": {
          "SystemTime": "2024-01-23T17:30:07.345840000Z"
        },
        "Version": "0",
        "_event_id": "4625"
      }
    }
  },
  "routing": {
    "event_type": "WEL",
    "hostname": "win-2016.corp.internal",
    "tags": ["windows"],
    "this": "8873fb9fcb26e2c0d4299ce765aff77d"
  },
  "ts": "2024-01-23 17:29:33"
}
```

**Transform (Field Extraction):**

```json
{
    "Source IP": "event.EVENT.EventData.IpAddress",
    "Username": "event.EVENT.EventData.TargetUserName",
    "Event ID": "event.EVENT.System.EventID",
    "Happened at": "event.EVENT.System.TimeCreated.SystemTime"
}
```

**Transform (Using Template Strings):**

```json
{
  "text": "Failed logon by {{ .event.EVENT.EventData.TargetUserName }} on {{ .routing.hostname }}"
}
```

**Output:**

```json
{
  "text": "Failed logon by administrator on win-2016.corp.internal"
}
```

### Output as String / Passthrough

The `custom_transform` in outputs can output pure text (non-JSON) from LimaCharlie. This is useful for forwarding ingested syslog data as-is to another destination.

This is accomplished by specifying a Template String instead of a Transform. When LimaCharlie determines the `custom_transform` string is not a valid Transform, it interprets it as a Template String:

```json
{
    "custom_transform": "{{ .event.text }}"
}
```

or

```json
{
    "custom_transform": "some text {{json .event.some_field }}"
}
```

## Custom Modifiers

Beyond the built-in modifiers for `gjson` (see [gjson playground](https://gjson.dev/)), LimaCharlie implements additional modifiers:

### parsejson

Takes no arguments. Converts an input string containing JSON into a decoded JSON object.

### extract

Takes a single argument `re`, which is a regular expression using "named capture groups" (defined in [re2 documentation](https://github.com/google/re2/wiki/Syntax)). Group names become keys in the output JSON object with matching values.

### parsetime

Takes two arguments: `from` and `to`. Converts an input string from one time format to another (formats defined in [Go time library](https://pkg.go.dev/time#pkg-constants)).

LimaCharlie also supports these special `from` formats:

* `epoch_s`: second-based epoch timestamp
* `epoch_ms`: millisecond-based epoch timestamp

### Complete Modifier Example

**Transform:**

```json
{
  "new_ts": "ts|@parsetime:{\"from\":\"2006-01-02 15:04:05\", \"to\":\"Mon, 02 Jan 2006 15:04:05 MST\"}",
  "user": "origin|@extract:{\"re\":\".*@(?P<domain>.+)\"}",
  "ctx": "event.EVENT.exec_context|@parsejson"
}
```

**Input:**

```json
{
  "ts": "2023-05-10 22:35:48",
  "origin": "someuser@gmail.com",
  "event": {
    "EVENT": {
      "exec_context": "{\"some\": \"embeded value\"}"
    }
  }
}
```

**Output:**

```json
{
  "new_ts": "Wed, 10 May 2023 22:35:48 UTC",
  "user": {
    "domain": "gmail.com\""
  },
  "ctx": {
    "some": "embeded value"
  }
}
```

## Related Topics

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments, making extensive use of template strings and transforms.