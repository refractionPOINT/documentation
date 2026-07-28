# Template Strings and Transforms

Many areas of LimaCharlie support template strings and transforms.

A template string lets you set the value of a configuration from the context. For example, you can add a value from the detection to the Detection Name of a D&R rule. You can also use transforms to select, change, or remove fields when an Adapter ingests data.

A transform changes the shape of JSON data while the data passes through LimaCharlie. You can move, rename, remove, and add fields in the JSON. For example, you can create an Output that works with `DNS_REQUEST` events but sends only specific fields from the event.

## Template Strings

Template strings in LimaCharlie use the [Go `text/template` format](https://pkg.go.dev/text/template). [Hashicorp's Go template syntax tutorial](https://learn.hashicorp.com/tutorials/nomad/go-template-syntax) is also a useful reference.

This example shows a D&R rule that sets the detection name:

```yaml
- action: report
  name: Evil executable on {{ .routing.hostname }}
```

Template strings also support functions that are specific to LimaCharlie:

- `token`: applies an MD5 hash function to the value that you supply.
- `anon`: applies an MD5 hash function to a secret seed value plus the value that you supply.
- `json`: converts the input into a JSON string.
- `prettyjson`: the same as `json`, but with indentation and newlines.
- `parsetime`: converts one time format to another.
- `split`: splits a string on a separator parameter.
- `join`: joins a list into one string with another string between the items.
- `replace`: replaces all instances of one string with another string.
- `base`: returns the file name in a file path.
- `dir`: returns the base directory path from a file path.

Use the `token` and `anon` functions to partly anonymize data. These functions work anywhere that supports a template string. For example:

```yaml
- action: report
  name: 'User {{token .event.USER_NAME }} accessed a website against policy.'
```

Other examples:

- `Full Data: {{prettyjson .event.OBJECT }}`
- `Original time:{{parsetime "{\"from\":\"2006/01/02 15:04:05\", \"to\":\"2006-01-02 15:04:05 MST\"}" .event.timestamp}}`
- `Packages: {{join "," .event.PACKAGES}}`

### Template Strings and Adapter Transforms

You can also use template strings with the `client_options.mapping.transform` option in the [Adapter configuration](../2-sensors-deployment/adapters/usage.md). This option lets you change data before ingestion. You control *what* fields LimaCharlie ingests and the names of the fields.

Adapter configurations support these options:

- `+` to add a field
- `-` to remove a field

Both options support template strings. You can add values to the JSON data or remove values from it, to replace or supplement other fields.

#### Additive vs Replacement Mode

A transform operates in one of two modes:

- **Replacement mode** (default): if *no* keys in the transform have a `+` or `-` prefix, LimaCharlie discards the original event. It builds the output only from the keys that you defined. The [Transforms](#transforms) section below describes the same behavior.
- **Additive mode**: if *any* key in the transform has a `+` or `-` prefix, the whole transform changes to additive mode. LimaCharlie keeps the original event as the base. The keys of the transform then add, change, or remove fields in that event.

You can mix prefixed and non-prefixed keys in the same transform. One `+` or `-` key changes the whole map to additive mode, and the non-prefixed keys still apply. Each non-prefixed key replaces the value at its path. This behavior is usually what you want when you add data to an event. Remember this behavior if you expect a non-prefixed key to rebuild the event from that key only.

#### Example: Renaming and Adding Fields

This is the input data:

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

This configuration renames the `d` value to `c` on ingestion, removes the d value, and adds a field named `hostname`:

```text
...
   client_options:
     mapping:
       transform:
         +c : '{{ .webster.d }}',
         -d: nil,
         +hostname : '{{ "my-computer" }}',
```

LimaCharlie then ingests this event:

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

#### Example: Parsing a Stringified JSON Field in Place

Adapters often receive an event with a field that holds a JSON-encoded string instead of a nested object. This is common with log sources such as Parquet, Teleport, or audit logs. If nothing parses that field, it arrives in LimaCharlie as an opaque string. You cannot query it as structured data.

Additive mode with the [`@parsejson` modifier](#custom-modifiers) decodes that string in place. The rest of the event does not change. For example, this is an event:

```json
{
  "ts": "2026-01-15 12:00:00",
  "user": "alice",
  "event_data": "{\"action\":\"login\",\"src\":\"10.0.0.5\"}"
}
```

This adapter configuration replaces `event_data` with the decoded object. Every other field stays the same:

```yaml
client_options:
  mapping:
    transform:
      +event_data: "event_data|@parsejson"
```

To keep the raw string and add the parsed copy next to it, use a different output key:

```yaml
client_options:
  mapping:
    transform:
      +event_data_parsed: "event_data|@parsejson"
```

Both forms stay in additive mode because the key has a `+` prefix. LimaCharlie keeps all the other fields in the event.

## Transforms

With Transforms, you specify a JSON object that describes the transformation.

This object has the shape of the final JSON that you want.

Key names are the literal key names in the output. Values support one of 3 types:

1. Template Strings, as described above. LimaCharlie generates the template string and puts it at the same place as the key in the transform object.
2. A `gjson` selector. For the selector syntax, see the [gjson syntax reference](https://github.com/tidwall/gjson/blob/master/SYNTAX.md). A selector selects a subset of the input object and maps that subset into the output object that the transform defines.
3. Other JSON objects. These objects are present in the output.

This is an example Input to a transform:

```json
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

This is the Transform definition:

```json
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

The Output is:

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

When you pass events to an output, you can transform the original event in more than one way. When you create an output, apply Custom Transforms in the CUSTOM TRANSFORM area of the screenshot below. This example transforms a detection event and sends it through a custom webhook to a web application.

![Output data transformation settings](../assets/images/image(310).png)

### Examples

#### Extracting Fields from Telemetry

This is a 4625 failed logon event. You want to send events like it to an output, but only some of the fields.

```json
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

This Output Transform extracts only the `IpAddress`, `TargetUserName`, `EventID`, and the `SystemTime` when the event was created. The new field names can be any names that you want.

```json
{
    "Source IP": "event.EVENT.EventData.IpAddress",
    "Username": "event.EVENT.EventData.TargetUserName",
    "Event ID": "event.EVENT.System.EventID",
    "Happened at": "event.EVENT.System.TimeCreated.SystemTime"
}
```

This example uses Template Strings to output text and specific fields.

```json
{
  "text": "Failed logon by {{ .event.EVENT.EventData.TargetUserName }} on {{ .routing.hostname }}"
}
```

With the sample WEL event, the example generates this output.

```json
{
  "text": "Failed logon by administrator on win-2016.corp.internal"
}
```

### Output as String / Passthrough

You can also use the `custom_transform` field in outputs to send pure text (non-JSON) from LimaCharlie. For example, you ingest syslog data and want to forward that syslog data unchanged to another system.

To do this, put a Template String in the `custom_transform` field instead of a Transform. If LimaCharlie finds that the `custom_transform` string is not a valid Transform, it reads the string as a Template String:

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

### Custom Modifiers

The [gjson playground](https://gjson.dev/) shows the built-in modifiers for `gjson`. LimaCharlie adds these modifiers:

- `parsejson`: this modifier takes no arguments. The input is a string that holds a JSON object. The output is the decoded JSON object.
- `extract`: this modifier takes one argument, `re`. This argument is a regular expression that uses "named capture groups", as the [re2 documentation](https://github.com/google/re2/wiki/Syntax) defines them. The group names become the keys of the output JSON object, and the matching values become the values.
- `parsetime`: this modifier takes two arguments, `from` and `to`. It reads an input string in the `from` time format and writes the time in the `to` format. Both formats use the [Go `time` library format constants](https://pkg.go.dev/time#pkg-constants). LimaCharlie also supports these `from` formats:
  - `epoch_s`: an epoch timestamp in seconds
  - `epoch_ms`: an epoch timestamp in milliseconds

For example, this transform:

```json
{
  "new_ts": "ts|@parsetime:{\"from\":\"2006-01-02 15:04:05\", \"to\":\"Mon, 02 Jan 2006 15:04:05 MST\"}",
  "user": "origin|@extract:{\"re\":\".*@(?P<domain>.+)\"}",
  "ctx": "event.EVENT.exec_context|@parsejson"
}
```

applied to:

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

results in:

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
