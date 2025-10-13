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

The following Output Transform would extract only the `IpAddress`, `TargetUserName`, `EventID`, and `SystemTime` the event was created. Notice, the newly mapped field names can be whatever you want.

```
{
    "Source IP": "event.EVENT.EventData.IpAddress",
    "Username": "event.EVENT.EventData.TargetUserName",
    "Event ID": "event.EVENT.System.EventID",
    "Happened at": "event.EVENT.System.TimeCreated.SystemTime"
}
```

The following example outputs text and specified fields using [Template Strings](/v2/docs/template-strings-and-transforms).

```
{
  "text": "Failed logon by {{ .event.EVENT.EventData.TargetUserName }} on {{ .routing.hostname }}"
}
```

The above example would generate the following output using the provided sample WEL.

```
{
  "text": "Failed logon by administrator on win-2016.corp.internal"
}
```

### Output as String / Passthrough

The `custom_transform` in outputs can also be used to output pure text (non-JSON) from LimaCharlie. This is useful if, for example, you are ingesting syslog data, and want to forward this syslog data as-is to something else.

This is accomplished by specifying a Template String in the `custom_transform` field instead of a Transform. In those cases, when LimaCharlie determines the `custom_transform` string is not a valid Transform, it will interpret it as a Template String like:

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

### Custom Modifiers

Beyond the built-in modifiers for `gjson` (as seen in their [playground](https://gjson.dev/), LimaCharlie also implements several new modifiers:

* `parsejson`: this modifier takes no arguments, it takes in as input a string that represents a JSON object and outputs the decoded JSON object.
* `extract`: this modifier takes a single argument, `re` which is a regular expression that uses "named capture groups" (as defined in the [re2 documentation](https://github.com/google/re2/wiki/Syntax)). The group names become the keys of the output JSON object with the matching values.
* `parsetime`: this modifier takes two arguments, `from` and `to`. It will convert an input string from a given time format (as defined in the Go `time` library format [here](https://pkg.go.dev/time#pkg-constants)) and outputs the resulting time in the `to` format. Beyond the time constants from the previous link, LimaCharlie also supports a `from` format of:

  + `epoch_s`: a second based epoch timestamp
  + `epoch_ms`: a millisecond based epoch timestamp

For example:
The transform:

```
{
  "new_ts": "ts|@parsetime:{\"from\":\"2006-01-02 15:04:05\", \"to\":\"Mon, 02 Jan 2006 15:04:05 MST\"}",
  "user": "origin|@extract:{\"re\":\".*@(?P<domain>.+)\"}"
  "ctx": "event.EVENT.exec_context|@parsejson"
}
```

applied to:

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

would result in:

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

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.