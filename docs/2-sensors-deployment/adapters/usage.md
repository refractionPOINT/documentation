# Adapter Usage

The Adapter can access many sources and many event types. The main mechanisms that specify the source and the type of events are:

1. Adapter Type: this shows the technical source of the events, like `syslog` or S3 buckets.
2. Platform: the platform shows the type of events that come from that source, like `text` or `carbon_black`.

The configurations that you can set change with the Adapter Type. To list all available Adapter Types and their configurations, run the adapter with no command line arguments.

You can give configurations to the adapter in one of three ways:

1. In a configuration file.
2. On the command line, in the format `config-name=config-value`.
3. In environment variables, in the format `config-name=config-value`.

This example shows a configuration file for an adapter that uses the `file` collection method:

```yaml
file: // The root of the config is the adapter collection method.
  client_options:
    identity:
      installation_key: e9a3bcdf-efa2-47ae-b6df-579a02f3a54d
      oid: 8cbe27f4-bfa1-4afb-ba19-138cd51389cd
    platform: json
    sensor_seed_key: testclient3
    mapping:
      event_type_path: syslog-events
  file_path: /var/log/syslog
```

## Multi-Adapter

You can run more than one adapter instance of the same type in the same adapter process. For example, one adapter process can monitor files in several directories with different configurations.

To do this, use a configuration file (as described above) that contains more than one YAML "document", like this:

```yaml
file:
  client_options:
    identity:
      installation_key: e9a3bcdf-efa2-47ae-b6df-579a02f3a54d
      oid: 8cbe27f4-bfa1-4afb-ba19-138cd51389cd
    platform: json
    sensor_seed_key: testclient1
    mapping:
      event_type_path: syslog-events
  file_path: /var/log/dir1/*

---

file:
  client_options:
    identity:
      installation_key: e9a3bcdf-efa2-47ae-b6df-579a02f3a54d
      oid: 8cbe27f4-bfa1-4afb-ba19-138cd51389cd
    platform: json
    sensor_seed_key: testclient2
    mapping:
      event_type_path: syslog-events
  file_path: /var/log/dir2/*

---

file:
  client_options:
    identity:
      installation_key: e9a3bcdf-efa2-47ae-b6df-579a02f3a54d
      oid: 8cbe27f4-bfa1-4afb-ba19-138cd51389cd
    platform: json
    sensor_seed_key: testclient3
    mapping:
      event_type_path: syslog-events
  file_path: /var/log/dir3/*
```

## Runtime Configuration

The Adapter runtime supports custom behaviors for specific deployments:

- `healthcheck`: an integer that gives a port. The adapter starts an HTTP server on this port for healthchecks.

## Core Configuration

All Adapter types support the same `client_options`, plus type-specific configurations. These configurations are *required* for every Adapter:

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) for this adapter.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, like `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: any name for this adapter. LimaCharlie generates Sensor IDs (SID) from this name, see below.
- `client_options.hostname`: a hostname for the adapter.

### Example

With inline parameters:

```bash
./lc-adapter file file_path=/path/to/logs.json \
  client_options.identity.installation_key=<INSTALLATION KEY> \
  client_options.identity.oid=<ORG ID> \
  client_options.platform=json \
  client_options.sensor_seed_key=<SENSOR SEED KEY> \
  client_options.mapping.event_type_path=<EVENT TYPE FIELD> \
  client_options.hostname=<HOSTNAME>
```

With Docker:

```bash
docker run -d --rm -it -p 4404:4404/udp refractionpoint/lc-adapter syslog \
  client_options.identity.installation_key=<INSTALLATION KEY> \
  client_options.identity.oid=<ORG ID> \
  client_options.platform=cef \
  client_options.hostname=<HOSTNAME> \
  client_options.sensor_seed_key=<SENSOR SEED KEY> \
  port=4404 \
  iface=0.0.0.0 \
  is_udp=true
```

With a configuration file:

```bash
./lc-adapter file config_file.yaml
```

## Parsing and Mapping

### Transformation Order

Data that you send through USP can have many formats. The data is processed as a pipeline, in this order:

1. A regular expression with named capture groups parses a string into a JSON object.
2. Built-in (in the cloud) LimaCharlie parsers that apply to specific `platform` values (like `carbon_black`).
3. The various "extractors" defined, like `EventTypePath`, `EventTimePath`, `SensorHostnamePath` and `SensorKeyPath`.
4. Custom `Mappings` directives from the client.

### Configurations

These configurations change how the cloud ingests the data. They also map and redefine fields such as the event type path and the event time.

- `client_options.mapping.parsing_re`: regular expression with [named capture groups](https://github.com/StefanSchroeder/Golang-Regex-Tutorial/blob/master/01-chapter2.markdown#named-matches). Each group name becomes a key in the converted JSON.
- `client_options.mapping.parsing_grok:`  a grok pattern that extracts structured data from unstructured log messages. Grok patterns combine regular expressions with predefined patterns.
- `client_options.mapping.sensor_key_path`: shows which component of the events represents the unique sensor identifier.
- `client_options.mapping.sensor_hostname_path`: shows which component of the event is the hostname of the resulting Sensor in LimaCharlie.
- `client_options.mapping.event_type_path`: shows which component of the event is the Event Type of the resulting event in LimaCharlie. It also supports template strings that are based on each event.
- `client_options.mapping.event_time_path`: shows which component of the event is the Event Time of the resulting event in LimaCharlie.
- `client_options.mapping.event_time_timezone`: the timezone to use for timestamps that have no timezone information. Use IANA timezone names (for example, `America/New_York`, `Europe/London`, `UTC`). If you do not set this option, timestamps with no timezone information are UTC.
- `client_options.mapping.rename_only`: *deprecated*
- `client_options.mapping.mappings`: *deprecated*
- `client_options.mapping.transform`: a Transform to apply to events.
- `client_options.mapping.drop_fields`: a list of field paths to remove from the data before the data is processed and kept.

### Parsing

#### Named Group Parsing

If the data that LimaCharlie ingests is text (a syslog line, for example), you can parse it into JSON automatically. To do this, define one of these options:

- a grok pattern, using the `client_options.mapping.parsing_grok` option
- a regular expression, using the `client_options.mapping.parsing_re` option

#### Grok Patterns

##### Basic Syntax

Grok patterns use the following syntax:

The grok pattern line must start with **message:** , and then the patterns, as in the example below

- `%{PATTERN_NAME:field_name}` - Extract a pattern into a named field
- `%{PATTERN_NAME}` - Match a pattern without extraction

To define custom patterns, use the pattern name as a key

The patterns must not include an extracted field name called message. That name conflicts with the assumed root of the grok pattern, which is also called message.

##### Built-in Patterns

LimaCharlie includes standard Grok patterns for common data types:

- `%{IP:field_name}` - IP addresses (IPv4/IPv6)
- `%{NUMBER:field_name}` - Numeric values
- `%{WORD:field_name}` - Single words (no whitespace)
- `%{DATA:field_name}` - Any data up to delimiter
- `%{GREEDYDATA:field_name}` - All remaining data
- `%{TIMESTAMP_ISO8601:field_name}` - ISO 8601 timestamps
- `%{LOGLEVEL:field_name}` - Log levels (DEBUG, INFO, WARN, ERROR)

**Example Firewall Log Record:**

```text
2024-01-01 12:00:00 ACCEPT TCP 192.168.1.100:54321 10.0.0.5:443 packets=1 bytes=78
```

**LimaCharlie Configuration to Match Firewall Log:**

```yaml
client_options:
  mapping:
    parsing_grok:
      message: '%{TIMESTAMP_ISO8601:timestamp} %{WORD:action} %{WORD:protocol} %{IP:src_ip}:%{NUMBER:src_port} %{IP:dst_ip}:%{NUMBER:dst_port} packets=%{NUMBER:packets} bytes=%{NUMBER:bytes}'
    event_type_path: "action"
    event_time_path: "timestamp"
```

**Fields Extracted by the Above Configuration:**

```json
{
  "timestamp": "2024-01-01 12:00:00",
  "action": "ACCEPT",
  "protocol": "TCP",
  "src_ip": "192.168.1.100",
  "src_port": "54321",
  "dst_ip": "10.0.0.5",
  "dst_port": "443",
  "packets": "1",
  "bytes": "78"
}
```

##### Timezone Handling

Many log sources send timestamps with no timezone information (for example, `2024-01-01 12:00:00` or `Jan 15 14:30:22`). By default, LimaCharlie reads these as UTC. If your logs use local time, set the timezone with `event_time_timezone`:

```yaml
client_options:
  mapping:
    parsing_grok:
      message: '%{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:host} %{GREEDYDATA:message}'
    event_time_path: "timestamp"
    event_time_timezone: "America/New_York"
```

The timezone must be a valid [IANA timezone name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Common examples:

| Timezone | Description |
|----------|-------------|
| `America/New_York` | US Eastern Time |
| `America/Los_Angeles` | US Pacific Time |
| `Europe/London` | UK Time |
| `Europe/Paris` | Central European Time |
| `Asia/Tokyo` | Japan Standard Time |
| `UTC` | Coordinated Universal Time |

> **Note:** Unix epoch timestamps (for example, `1704067200`) have no timezone, and this setting does not change them.

#### Regular Expressions

**With this log line as an example:**

```text
Nov 09 10:57:09 penguin PackageKit[21212]: daemon quit
```

**you could apply the following regular expression as** `parsing_re`**:**

```text
(?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)
```

This gives the following event in LimaCharlie:

```json
{
  "date": "Nov 09 10:57:09",
  "host": "penguin",
  "exe": "PackageKit",
  "pid": "21212",
  "msg": "daemon quit"
}
```

#### Key/Value Parsing

As an alternative, you can give a regular expression that does NOT contain Named Groups, like this:

```text
(?:<\d+>\s*)?(\w+)=(".*?"|\S+)
```

In this mode, LimaCharlie expects the regular expression to generate a list of matches. Each match has 2 submatches. Submatch index 1 is the Key name, and submatch index 2 is the value. This mode works with logs such as CEF, where the log can look like this:

```text
<20>hostname=my-host log_name=http_logs timestamp=....
```

This generates:

```json
{
  "hostname" : "my-host",
  "log_name": "http_logs",
  "timestamp": "..."
}
```

#### Extraction

LimaCharlie has a few core constructs that all events and sensors have.
Namely:

- Sensor ID
- Hostname
- Event Type
- Event Time

You can select fields from the JSON logs to extract into these common fields.

To do this, give the "path" to the field in the JSON data. A path is like a directory path that uses `/` for each sub directory. In this case, the path shows how to get to the field from the top level of the JSON.

For example, with this event:

```json
{
  "a": "x",
  "b": "y",
  "c": {
    "d": {
      "e": "z"
    }
  }
}
```

These paths give these results:

- `a`: `x`
- `b`: `y`
- `c/d/e`: `z`

You can specify these extractors:

- `client_options.mapping.sensor_key_path`: shows which component of the events represents the unique sensor identifier.
- `client_options.mapping.sensor_hostname_path`: shows which component of the event is the hostname of the resulting Sensor in LimaCharlie.
- `client_options.mapping.event_type_path`: shows which component of the event is the Event Type of the resulting event in LimaCharlie. It also supports template strings that are based on each event.
- `client_options.mapping.event_time_path`: shows which component of the event is the Event Time of the resulting event in LimaCharlie.

### Indexing

Indexing occurs in one of 3 ways:

1. By the built-in indexer for specific platforms like Carbon Black.
2. By a generic indexer applied to all fields if no built-in indexer was available.
3. Optionally, user-specific indexing guidelines.

#### User Defined Indexing

You can configure an Adapter to do custom indexing on the data that it feeds.

To do this, set the `indexing` element in the `client_options`. This field contains a list of index descriptors.

An index descriptor can have the following fields:

- `events_included`: optionally, a list of event\_type that this descriptor applies to.
- `events_excluded`: optionally, a list of event\_type this descriptor *does not* apply to.
- `path`: the element path this descriptor targets, like `user/metadata/user_id`.
- `regexp`: optionally, a regular expression used on the `path` field to extract the item to index, like `email: (.+)`.
- `index_type`: the category of index the value extracted belongs to, like `user` or `file_hash`.

Here is an example of a simple index descriptor:

```yaml
events_included:
  - PutObject
path: userAgent
index_type: user
```

In a client option, this can look like this:

```text
{
  "client_options": {
    ...,
    "indexing": [{
      "events_included": ["PutObject"],
      "path": "userAgent",
      "index_type": "user"
    }, {
      "events_included": ["DelObject"],
      "path": "original_user/userAgent",
      "index_type": "user"
    }]
  }
}
```

#### Supported Indexes

This is the list of currently supported index types:

- `file_hash`
- `file_path`
- `file_name`
- `domain`
- `ip`
- `user`
- `service_name`
- `package_name`

### Sensor IDs

USP Clients generate LimaCharlie Sensors at runtime. LimaCharlie generates the ID of those sensors (SID) from the Organization ID (OID) and the Sensor Seed Key.

If you must re-key an IID because it leaked, replace the IID with a new valid one. If you keep the same OID and Sensor Seed Key, the generated SIDs stay stable after the IID change.

### Discovering adapter types and finding an adapter's sensor

The CLI can list the supported adapter types, show their configuration schema, and find the sensor that an adapter produced. These commands work for both `cloud-adapter` (the hosted set) and `external-adapter` (the on-prem set). The examples below use `cloud-adapter`.

List the supported adapter/sensor type names:

```bash
limacharlie cloud-adapter list-types
```

`external-adapter list-types` lists the on-prem set, which is different from the cloud set.

Show the configuration field listing for one adapter type. The listing shows where each field is (for example, `hostname` under `client_options`). Add `--output json` for the raw schema:

```bash
limacharlie cloud-adapter schema --type <t>
limacharlie cloud-adapter schema --type <t> --output json
```

Find the live sensors that an adapter produced, matched by installation-key IID:

```bash
limacharlie cloud-adapter sensors --key <adapter-record>
```

An empty result means that the adapter did not deliver any events yet. The sensor appears on the first event.

## Validating Configurations

Before you deploy an adapter to production, validate your configuration and test the parsing rules. This makes sure that the data is ingested correctly.

### Validating Adapter Configuration

The adapter binary supports a `--validate` flag. This flag checks your configuration, but it does not start the adapter:

```bash
# Validate a YAML config file
./lc_adapter --validate syslog config.yaml

# Validate CLI parameters
./lc_adapter --validate wel evt_sources=Security,System client_options.identity.oid=... client_options.identity.installation_key=... client_options.platform=wel
```

The flag does the following:

1. Parses and validates the configuration structure
2. Checks for required fields (OID, installation key, platform, etc.)
3. Reports configuration errors, and does not connect to LimaCharlie

Exit codes:

- `0`: Configuration is valid
- `1`: Configuration has errors (details printed to stderr)

### Testing Parsing with Sample Data

The adapter also supports a `--test-parsing` flag. This flag sends sample data to the LimaCharlie validation API to check that your parsing rules work correctly:

```bash
# Test parsing with a sample log file
./lc_adapter --test-parsing sample.log syslog config.yaml
```

The flag does the following:

1. Reads sample data from the file that you specify
2. Sends the data to the LimaCharlie validation API with your mapping configuration
3. Shows the parsed events or the parsing errors
4. Exits with an error (code 1) if it parsed no events. This usually means that the parsing rules are incorrect.

Exit codes:

- `0`: Parsing successful, at least one event was parsed
- `1`: Parsing failed (API errors) or no events were parsed

Example successful output:

```text
starting
loading config from file: config.yaml
found 1 configs to run
testing parsing with platform=text
PARSING SUCCESSFUL

Parsed 3 event(s):

Event 1:
  {
    "event_type": "INFO",
    "hostname": "server01",
    "json_payload": {
      "hostname": "server01",
      "level": "INFO",
      "message": "User login successful"
    }
  }
```

Example error output when the adapter parses no events (for example, the regex does not match):

```text
starting
loading config from file: config.yaml
found 1 configs to run
testing parsing with platform=text
PARSING FAILED

WARNING: No events were parsed from the sample data.

This usually indicates one of the following issues:
  - The parsing_re regex does not match the input format
  - The platform type does not match the data format
  - The sample data is empty or contains only whitespace

Suggestions:
  - Verify your parsing_re regex matches the sample data
  - Check that the platform matches your data format (text, json, cef, etc.)
  - Ensure the sample file contains valid log data
parsing test failed: no events parsed from sample data
```

**Note**: For API authentication, the config must contain a valid API key in `client_options.identity.installation_key`. An installation key is not enough.

### Testing Parsing via Python CLI

You can also test parsing with the LimaCharlie Python CLI:

```bash
# Validate with a text file containing sample logs
limacharlie usp validate --platform text --mapping-file mapping.yaml --input-file sample.log

# Validate CEF parsing with inline sample data
limacharlie usp validate --platform cef --mapping-file cef-mapping.yaml --input "CEF:0|Security|threatmanager|1.0|100|worm|10|src=192.168.1.1"

# Validate JSON parsing
limacharlie usp validate --platform json --mapping-file mapping.yaml --input-file sample.json --json-input

# Output parsed events as JSON for inspection
limacharlie usp validate --platform text --mapping-file mapping.yaml --input-file sample.log --output-format json
```

The validation API processes your sample data with the parsing engine and returns:

- **On success**: the parsed events, which show how the data is transformed
- **On failure**: error messages that show the problem

### Common Validation Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `missing platform` | No `platform` field in client_options | Add `client_options.platform` (for example, `text`, `json`, `cef`) |
| `missing oid` | No organization ID configured | Add `client_options.identity.oid` |
| `missing installation_key` | No installation key configured | Add `client_options.identity.installation_key` |
| `regex pattern did not match` | The parsing regex does not match the input format | Test the regex against your sample data |
| `no events parsed from sample data` | The regex does not match, the platform is wrong, or the input is empty | Check that parsing_re matches your data, check the platform type, and make sure that the sample file has content |

### SDK Validation

For programmatic validation, use the `validateUSP` method in the Python SDK:

```python
from limacharlie import Manager

manager = Manager()
result = manager.validateUSP(
    platform='text',
    mapping={
        'parsing_re': r'(?P<timestamp>\S+) (?P<message>.*)',
        'event_type_path': 'event_type'
    },
    text_input='2024-01-01T12:00:00Z Test message\n2024-01-01T12:00:01Z Another message'
)

if result.get('errors'):
    print('Validation failed:', result['errors'])
else:
    print('Parsed events:', result['results'])
```
