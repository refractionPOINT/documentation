# Template Strings and Transforms

Many areas of LimaCharlie support template strings and transforms, providing powerful mechanisms to customize configurations and reshape data in flight.

## Overview

**Template Strings** allow you to customize configuration values based on context. For example, you can adjust Detection Names in D&R rules to include values from the detection itself, or modify data upon ingestion from an Adapter.

**Transforms** allow you to change the shape of JSON data dynamically. This includes moving, renaming, removing, and adding fields in JSON objects. For example, you can create an Output that works with `DNS_REQUEST` events but outputs only specific fields from the event.

## Template Strings

Template strings in LimaCharlie use the format defined by Go's "text templates" found [here](https://pkg.go.dev/text/template). A useful guide provided by Hashicorp is also available [here](https://learn.hashicorp.com/tutorials/nomad/go-template-syntax).

### Basic Usage

The most basic example for a D&R rule customizing the detection name:

```
- action: report
  name: Evil executable on {{ .routing.hostname }}
```

### LimaCharlie-Specific Functions

Template strings support several LimaCharlie-specific functions:

* `token`: applies an MD5 hashing function on the value provided
* `anon`: applies an MD5 hashing function on a secret seed value, plus the value provided
* `json`: marshals the input into a JSON string representation
* `prettyjson`: same as `json` but with indentation and newlines
* `parsetime`: parse a time format to another
* `split`: split a string based on a separator parameter
* `join`: join a list into a string joined by another string
* `replace`: replace all occurrences of a string with another
* `base`: return the file name in a file path
* `dir`: return the base directory path from a file path

### Anonymization Example

The `token` and `anon` functions can be used to partially anonymize data anywhere a template string is supported:

```
- action: report
  name: 'User {{token .event.USER_NAME }} accessed a website against policy.'
```

### Additional Examples

* `Full Data: {{prettyjson .event.OBJECT }}`
* `Original time:{{parsetime "{\"from\":\"2006/01/02 15:04:05\", \"to\":\"2006-01-02 15:04:05 MST\"}" .event.timestamp}}`
* `Packages: {{join "," .event.PACKAGES}}`

### Template Strings and Adapter Transforms

Template strings can be used in conjunction with the `client_options.mapping.transform` option in Adapter configuration. These allow you to modify data prior to ingestion, controlling which fields get ingested and their resulting field names.

The following options are available in Adapter configurations:

* `+` to add a field
* `-` to remove a field

Both support template strings, meaning you can add/remove values from JSON data to replace/supplement other fields.

#### Example

Given the following data:

```
{ "event":
  "webster" : {
     "a" : 1,
     "b" : 2,
     "d" : 3
    }
  }
}
```

To rename the `d` value to `c` on ingestion, remove the `d` value, and add a field called `hostname`, use this configuration:

```
...
   client_options:
     mapping:
       transform:
         +c : '{{ .webster.d }}',
         -d: nil,
         +hostname : '{{ "my-computer" }}',
```

The resulting event to be ingested would be:

```
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

With Transforms, you specify a JSON object that describes the transformation. This object is in the shape of the final JSON you would like to transform to.

### Transform Value Types

Key names are the literal key names in the output. Values support one of 3 types:

1. **Template Strings**: As described above. The template string will be generated and placed at the same location as the key in the transform object.
2. **`gjson` selector**: The selector syntax is defined [here](https://github.com/tidwall/gjson/blob/master/SYNTAX.md). It makes it possible to select subsets of the input object and map it within the resulting object as defined by the transform.
3. **JSON objects**: Which will be present in the output as-is.

### Complete Transform Example

#### Input

```
{
    "event": {
        "EVENT": {
            "EventData": {
                "AuthenticationPackageName": "NTLM",
                "FailureReason":             "%%2313",
                "IpAddress":                 "34.64.101.177",
                "IpPort":                    "0",
                "KeyLength":                 "0",
                "LmPackageName":             "-",
                "LogonProcessName":          "NtLmSsp",
                "LogonType":                 "3",
                "ProcessId":                 "0x0",
                "ProcessName":               "-",
                "Status":                    "0xc000006d",
                "SubStatus":                 "0xc0000064",
                "SubjectDomainName":         "-",
                "SubjectLogonId":            "0x0",
                "SubjectUserName":           "-",
                "SubjectUserSid":            "S-1-0-0",
                "TargetDomainName":          "",
                "TargetUserName":            "ADMINISTRADOR",
                "TargetUserSid":             "S-1-0-0",
                "TransmittedServices":       "-",
                "WorkstationName":           "-",
            },
            "System": {
                "Channel":  "Security",
                "Computer": "demo-win-2016",
                "Correlation": {
                    "ActivityID": "{F207C050-075F-0001-AFE1-ED1F3897D801}",
                },
                "EventID":       "4625",
                "EventRecordID": "2832700",
                "Execution": {
                    "ProcessID": "572",
                    "ThreadID":  "2352",
                },
                "Keywords": "0x8010000000000000",
                "Level":    "0",
                "Opcode":   "0",
                "Provider": {
                    "Guid": "{54849625-5478-4994-A5BA-3E3B0328C30D}",
                    "Name": "Microsoft-Windows-Security-Auditing",
                },
                "Security": "",
                "Task":     "12544",
                "TimeCreated": {
                    "SystemTime": "2022-07-15T22:48:24.996361600Z",
                },
                "Version": "0",
            },
        },
    },
    "routing": {
        "arch":       2,
        "did":        "b97e9d00-ca17-4afe-a9cf-27c3468d5901",
        "event_id":   "f24679e5-5484-4ca1-bee2-bfa09a5ba3db",
        "event_time": 1657925305984,
        "event_type": "WEL",
        "ext_ip":     "35.184.178.65",
        "hostname":   "demo-win-2016.c.lc-demo-infra.internal",
        "iid":        "7d23bee6-aaaa-aaaa-aaaa-c8e8cca132a1",
        "int_ip":     "10.128.0.2",
        "moduleid":   2,
        "oid":        "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",
        "plat":       268435456,
        "sid":        "bb4b30af-ff11-4ff4-836f-f014ada33345",
        "tags": [
            "edr",
            "lc:stable",
        ],
        "this": "c5e16360c71baf3492f2dcd962d1eeb9",
    },
    "ts": "2022-07-15 22:48:25",
}
```

#### Transform Definition

```
{
    "message": "Interesting event from {{ .routing.hostname }}",  // a format string
    "from":    "{{ \"limacharlie\" }}",                           // a format string with only a literal value
    "dat": {                                                      // define a sub-object in the output
        "raw": "event.EVENT.EventData"                            // a "raw" key where we map a specific object from the input
    },
    "anon_ip": "{{anon .routing.int_ip }}",                       // an anonymized version of the internal IP
    "ts":   "routing.event_time",                                 // map a specific simple value
    "nope": "does.not.exist"                                      // map a value that is not present
}
```

#### Output

```
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

## Transforming Output Data

When passing events to an output, you have the option to transform the original event in multiple ways. When creating an output, Custom Transforms are applied in the CUSTOM TRANSFORM area. This is useful for transforming detection events to pass via custom webhook to web applications.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(310).png)

## Practical Examples

### Extracting Fields from Telemetry

Given a Windows Event Log 4625 (failed logon) event:

```
{
  "event": {
    "EVENT": {
      "EventData": {
        "AuthenticationPackageName": "NTLM",
        "FailureReason": "%%2313",
        "IpAddress": "142.99.21.14",
        # <extra fields removed>
        "TargetUserName": "administrator",
        "WorkstationName": "D-483"
      },
      "System": {
        "Channel": "Security",
        "Computer": "demo-win-2016",
        # <extra fields removed>
        "EventID": "4625",
        "EventRecordID": "22690646",
        # <extra fields removed>
        "TimeCreated": {
          "SystemTime": "2024-01-23T17:30:07.345840000Z"
        },
        "Version": "0",
        "_event_id": "4625"
      }
    }
  },
  "routing": {
    # <extra fields removed>
    "event_type": "WEL",
    "hostname": "win-2016.corp.internal",
     # <extra fields removed>
    "tags": [
      "windows"
    ],
    "this": "8873fb9fcb26e2c0d4299ce765aff77d"
  },
  "ts": "2024-01-23 17:29:33"
}
```

#### Extract Specific Fields with Custom Names

This transform extracts only the `IpAddress`, `TargetUserName`, `EventID`, and `SystemTime`:

```
{
    "Source IP": "event.EVENT.EventData.IpAddress",
    "Username": "event.EVENT.EventData.TargetUserName",
    "Event ID": "event.EVENT.System.EventID",
    "Happened at": "event.EVENT.System.TimeCreated.SystemTime"
}
```

#### Generate Text with Template Strings

This transform outputs text with embedded fields:

```
{
  "text": "Failed logon by {{ .event.EVENT.EventData.TargetUserName }} on {{ .routing.hostname }}"
}
```

Output:

```
{
  "text": "Failed logon by administrator on win-2016.corp.internal"
}
```

## Output as String / Passthrough

The `custom_transform` in outputs can also be used to output pure text (non-JSON) from LimaCharlie. This is useful if, for example, you are ingesting syslog data and want to forward this syslog data as-is to something else.

This is accomplished by specifying a Template String in the `custom_transform` field instead of a Transform. When LimaCharlie determines the `custom_transform` string is not a valid Transform, it will interpret it as a Template String:

```
{
    "custom_transform": "{{ .event.text }}"
}
```

or

```
{
    "custom_transform": "some text {{json .event.some_field }}"
}
```

## Custom Modifiers

Beyond the built-in modifiers for `gjson` (as seen in their [playground](https://gjson.dev/)), LimaCharlie also implements several new modifiers:

### parsejson

Takes no arguments. Takes as input a string representing a JSON object and outputs the decoded JSON object.

### extract

Takes a single argument, `re`, which is a regular expression that uses "named capture groups" (as defined in the [re2 documentation](https://github.com/google/re2/wiki/Syntax)). The group names become the keys of the output JSON object with the matching values.

### parsetime

Takes two arguments, `from` and `to`. Converts an input string from a given time format (as defined in the Go `time` library format [here](https://pkg.go.dev/time#pkg-constants)) and outputs the resulting time in the `to` format. 

Beyond the standard time constants, LimaCharlie also supports these `from` formats:

* `epoch_s`: a second-based epoch timestamp
* `epoch_ms`: a millisecond-based epoch timestamp

### Custom Modifiers Example

Transform:

```
{
  "new_ts": "ts|@parsetime:{\"from\":\"2006-01-02 15:04:05\", \"to\":\"Mon, 02 Jan 2006 15:04:05 MST\"}",
  "user": "origin|@extract:{\"re\":\".*@(?P<domain>.+)\"}",
  "ctx": "event.EVENT.exec_context|@parsejson"
}
```

Applied to:

```
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

Results in:

```
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

## Integration with Adapters

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. Template strings and transforms can be applied during the ingestion process to shape data before it enters the LimaCharlie platform, providing powerful preprocessing capabilities.