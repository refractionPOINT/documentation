# IIS Logs

Microsoft Internet Information Services (IIS) is a web server that is common on Microsoft Windows servers. This Adapter sends IIS web logs to LimaCharlie with the Adapter binary.

Telemetry Platform (if applicable): `iis`

## Deployment Configurations

All adapters support the same `client_options`. Always set them when you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to set these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) for this adapter.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name for this adapter. LimaCharlie generates Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

IIS web logs usually have a standard schema, unless an administrator changes it. The `iis` platform in LimaCharlie expects this structure:

`#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) cs(Referer) sc-status sc-substatus sc-win32-status time-taken`

#### Log Structure

If your IIS logs have a different structure, contact the LimaCharlie team. The team can customize the parser.

These are the fields:

| Field Name | Explanation |
| --- | --- |
| date | Date of log entry |
| time | Time of log entry |
| s-ip | The IP address of the web server |
| cs-method | The method of request from the client |
| cs-uri-stem | The URI requested by the client |
| cs-uri-query | The query added to the URI in the client request |
| s-port | The server port |
| cs-username | The client username (if the client supplies one) |
| c-ip | The IP address of the client |
| cs-user-agent | The user-agent of the client |
| cs-referer | The referer that directed the client to the site |
| sc-status | The service status code |
| sc-substatus | The service substatus code (if applicable) |
| sc-win32-status | The Windows status code |
| time-taken | The time to render the requested resources |

## Configuration File

IIS keeps the logs on the disk of the web server, in files that roll daily. To collect IIS web logs, use a binary Adapter that monitors the IIS log folders for new files. The Adapter type is `file`, and the platform is `iis`.

Use the configuration file below as a start to monitor the directories of IIS web logs. Replace each value in `< >` characters with a value that is unique to your Organization or deployment. *Do not include the* `<` *or* `>` *characters in your config file!*

### Please customize according to your environment/LimaCharlie organization

```yaml
file:
  client_options:
    identity:
      installation_key: <installation key>
      oid: <organization id>
    platform: iis
    sensor_seed_key: <sensor_seed_key>
    // The following will map the timestamp of the event to the timestamp in the web log. Remove if you'd prefer to keep the event time as the time of ingestion.
    mapping:
      event_time_path: ts
  file_path: <C:\path\to\web\logs\u*.log>
  no_follow: false
```

These notes apply to the IIS platform parser:

- LimaCharlie uses the server IP address (`s-ip` in the logs) as the hostname.
- The parser combines the `date` and `time` fields into one field, `ts`. The configuration above uses this field as the event time, unless you remove the mapping.
- The `sensor_seed_key` can be any value. Make sure that it is unique for each web server.
- To collect logs from more than one folder, set more than one configuration in one file.
- The `no_follow: false` option makes sure that the Adapter monitors for new files and for writes to existing files. Remove this option if you ingest "dead" log files.
- The Adapter telemetry shows all IIS events as `IIS_WEBLOG`.

If you have questions about the collection of IIS web logs, contact the LimaCharlie team.

After you set the config file, run the Adapter on Windows with this command. The example assumes that the file is named `config.yaml`:

`<adapter_name>.exe file config.yaml`

## Example Event

```json
{
    "c-ip": "192.168.1.11",
    "cs-method": "GET",
    "cs-referer)": "-",
    "cs-uri-query": "-",
    "cs-uri-stem": "/path/to/my/web/page",
    "cs-user-agent": "Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/128.0.0.0+Safari/537.36",
    "cs-username": "-",
    "s-ip": "192.168.1.10",
    "s-port": "99",
    "sc-status": "401",
    "sc-substatus": "2",
    "sc-win32-status": "5",
    "time-taken": "143",
    "ts": "2024-09-05 12:36:14"
}
```
