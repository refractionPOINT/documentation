# Adapter Usage

The Adapter can be used to access many different sources and many different event types. The main mechanisms specifying the source and type of events are:

1. Adapter Type: this indicates the technical source of the events, like `syslog` or S3 buckets.
2. Platform: the platform indicates the type of events that are acquired from that source, like `text` or `carbon_black`.

Depending on the Adapter Type specified, configurations that can be specified will change. Running the adapter with no command line arguments will list all available Adapter Types and their configurations.

Configurations can be provided to the adapter in one of three ways:

1. By specifying a configuration file.
2. By specifying the configurations via the command line in the format `config-name=config-value`.
3. By specifying the configurations via the environment variables in the format `config-name=config-value`.

Here's an example config as a config file for an adapter using the `file` method of collection:

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

It is possible to execute multiple instances of adapters of the same type within the same adapter process, for example to have a single adapter process monitor files in multiple directories with slightly different configurations.

This is achieved by using a configuration file (as described above) with multiple YAML "documents" within like this:

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

The Adapter runtime supports some custom behaviors to make it more suitable for specific deployment scenarios:

- `healthcheck`: an integer that specifies a port to start an HTTP server on that can be used for healthchecks.

## Core Configuration

All Adapter types support the same `client_options`, plus type-specific configurations. The following configurations are *required* for every Adapter:

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.
- `client_options.hostname`: a hostname for the adapter.

### Example

Using inline parameters:

```bash
./lc-adapter file file_path=/path/to/logs.json \
  client_options.identity.installation_key=<INSTALLATION KEY> \
  client_options.identity.oid=<ORG ID> \
  client_options.platform=json \
  client_options.sensor_seed_key=<SENSOR SEED KEY> \
  client_options.mapping.event_type_path=<EVENT TYPE FIELD> \
  client_options.hostname=<HOSTNAME>
```

Using Docker:

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

Using a configuration file:

```bash
./lc-adapter file config_file.yaml
```

## Parsing and Mapping

### Transformation Order

Data sent via USP can be formatted in many different ways. Data is processed in a specific order as a pipeline:

1. Regular Expression with named capture groups parsing a string into a JSON object.
2. Built-in (in the cloud) LimaCharlie parsers that apply to specific `platform` values (like `carbon_black`).
3. The various "extractors" defined, like `EventTypePath`, `EventTimePath`, `SensorHostnamePath` and `SensorKeyPath`.
4. Custom `Mappings` directives provided by the client.

### Configurations

The following configurations allow you to customize the way data is ingested by the platform, including mapping and redefining fields such as the event type path and time.

- `client_options.mapping.parsing_re`: regular expression with [named capture groups](https://github.com/StefanSchroeder/Golang-Regex-Tutorial/blob/master/01-chapter2.markdown#named-matches). The name of each group will be used as the key in the converted JSON parsing.
- `client_options.mapping.parsing_grok:`  grok pattern parsing for structured data extraction from unstructured log messages. Grok patterns combine regular expressions with predefined patterns to simplify log parsing and field extraction.
- `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers. Each distinct value creates its own Sensor, for example one per firewall when logs from several devices arrive through the same adapter. The online status of these Sensors follows the adapter and the flow of logs, not the devices; to be alerted when a device stops reporting, see [Alerting on sensors that stop sending data](../troubleshooting/non-responding-sensors.md). It also supports template strings based on each event. Some platforms set the sensor key in their parser; see [Using One Sensor for All Devices](#using-one-sensor-for-all-devices) to report all their events as a single Sensor.
- `client_options.mapping.sensor_identity_type`: optionally declares the meaning of that sensor key: `email`, `username`, `github_login` or `device`. It overrides the built-in declaration only when `sensor_key_path` is also supplied. See [Sensor identity declarations](#sensor-identity-declarations).
- `client_options.mapping.sensor_hostname_path`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie. It also supports template strings based on each event.
- `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports template strings based on each event.
- `client_options.mapping.event_time_path`: indicates which component of the event represents the Event Time of the resulting event in LimaCharlie.
- `client_options.mapping.event_time_timezone`: specifies the timezone for parsing timestamps that don't include timezone information. Uses IANA timezone names (e.g., `America/New_York`, `Europe/London`, `UTC`). If not specified, timestamps without timezone info are treated as UTC.
- `client_options.mapping.rename_only`: *deprecated*
- `client_options.mapping.mappings`: *deprecated*
- `client_options.mapping.transform`: a Transform to apply to events.
- `client_options.mapping.drop_fields`: a list of field paths to be dropped from the data before being processed and retained.

### Sensor Identity Declarations

!!! note "Availability"
    Built-in parser declarations need no adapter change. A custom
    `sensor_identity_type` requires adapter version 1.32.40 or later. Entity
    associations require a Cloud Security subscription with
    [Entities](../../cloud-security/entity-pivot.md#adapter-identities-and-external-actors).

A multiplexed adapter creates a separate sensor for each sensor key. A declaration
explains whether that sensor represents a user or a device, allowing Entities
to associate its telemetry with the corresponding entity.

| `sensor_identity_type` | Meaning of the sensor key |
|---|---|
| `email` | An email address identifying a user. |
| `username` | A bare account name in the adapter's namespace. Names alone produce possible matches and never merge users. |
| `github_login` | A mutable GitHub login, normalized to lowercase with a terminal `[bot]` suffix preserved. Built-in parser evidence links only when exactly one current collected GitHub identity holds the login; stable numeric IDs prevent renamed or reclaimed logins from joining different people. |
| `device` | The vendor's device identifier. The sensor hostname supplies the device name; the vendor identifier does not link devices across providers. |

Built-in parsers declare `github_login` for `github`, `email` for `1password`, and `device` for `crowdstrike`, `sentinel_one`, `carbon_black`, `msdefender`,
`trend_worryfree` and `fortigate`. Other parsers leave the declaration empty unless
configured explicitly. An empty declaration does not infer an identity from the
platform or hostname.

Built-in parser declarations record `identity_source: parser`. The GitHub parser
also supplies the audit event's immutable numeric actor ID as `identity_id`,
which becomes an authoritative `github_user_id` identifier in Entities.
A login alone is corroborated evidence subject to the uniqueness guard, never an
authoritative identifier. Device parsers can supply an immutable vendor device ID;
it remains vendor evidence rather than a cross-provider identity link.

Customer declarations record `identity_source: mapping`. **All identifiers from a
customer mapping are possible and unconfirmed**, including the sensor ID. A
free-form log field can be influenced by outsiders; declaring its type never
merges entities or confirms a matching directory identity.

To declare a custom sensor key, set `client_options.mapping.sensor_identity_type`
next to `client_options.mapping.sensor_key_path`. Accepted nonempty values are
exactly the four lowercase values above. Unsupported values fail configuration
validation. A declaration without `sensor_key_path` does not override a parser's
default. When a configured `sensor_key_path` supplies a nonempty custom key, also
set `sensor_identity_type` to enable identity association; an omitted or empty
type leaves that custom key undeclared. If the configured path is absent in an
event, the parser's original key and identity declaration remain in use. An
extractor that explicitly returns an empty string preserves the existing sensor-ID
behavior for an empty key and omits the identity declaration. An empty template
result leaves the parser's original key and declaration unchanged.

For an identity declaration, the raw sensor key must be nonempty, valid UTF-8 and
at most **512 UTF-8 bytes**, and must be valid for its declared type. An
optional stable `identity_id` has the same byte bound and is also validated.
An invalid or oversized key or ID is not truncated: its identity declaration is omitted
while telemetry ingestion continues. This bound applies to the raw key before
identity normalization, independently of the sensor's display hostname.

The persisted declaration metadata consists of four additive fields:
`identity_type`, raw `identity_key`, optional immutable `identity_id`, and
`identity_source` (`parser` or `mapping`). Existing sensors pick up declarations
on their **next connection**. There is no
backfill of identities from old events or existing sensor names.

### Parsing

#### Named Group Parsing

If the data ingested in LimaCharlie is text (a syslog line for example), you may automatically parse it into a JSON format. To do this, you need to define one of the following:

- a grok pattern, using the `client_options.mapping.parsing_grok` option
- a regular expression, using the `client_options.mapping.parsing_re` option

#### Grok Patterns

##### Basic Syntax

Grok patterns use the following syntax:

The grok pattern line must start with **message:** , followed by the patterns, as in the example below

- `%{PATTERN_NAME:field_name}` - Extract a pattern into a named field
- `%{PATTERN_NAME}` - Match a pattern without extraction

Custom patterns can be defined using the pattern name as a key

This means that the patterns should not include extracted field names called message as it will conflict with the assumed root of the grok pattern called message.

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

Many log sources emit timestamps without timezone information (e.g., `2024-01-01 12:00:00` or `Jan 15 14:30:22`). By default, LimaCharlie interprets these as UTC. If your logs use local time, you can specify the timezone using `event_time_timezone`:

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

> **Note:** Unix epoch timestamps (e.g., `1704067200`) are timezone-agnostic and are not affected by this setting.

#### Regular Expressions

**With this log line as an example:**

```text
Nov 09 10:57:09 penguin PackageKit[21212]: daemon quit
```

**you could apply the following regular expression as** `parsing_re`**:**

```text
(?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)
```

which would result in the following event in LimaCharlie:

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

Alternatively you can specify a regular expression that does NOT contain Named Groups, like this:

```text
(?:<\d+>\s*)?(\w+)=(".*?"|\S+)
```

When in this mode, LimaCharlie assumes the regular expression will generate a list of matches where each match has 2 submatches, and submatch index 1 is the Key name, and submatch index 2 is the value. This is compatible with logs like CEF for example where the log could look like:

```text
<20>hostname=my-host log_name=http_logs timestamp=....
```

which would end up generating:

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

You may specify certain fields from the JSON logs to be extracted into these common fields.

This process is done by specifying the "path" to the relevant field in the JSON data. Paths are like a directory path using `/` for each sub directory except that in our case, they describe how to get to the relevant field from the top level of the JSON.

For example, using this event:

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

The following paths would yield the following results:

- `a`: `x`
- `b`: `y`
- `c/d/e`: `z`

The following extractors can be specified:

- `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers.
- `client_options.mapping.sensor_hostname_path`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie.
- `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports template strings based on each event.
- `client_options.mapping.event_time_path`: indicates which component of the event represents the Event Time of the resulting event in LimaCharlie.

### Indexing

Indexing occurs in one of 3 ways:

1. By the built-in indexer for specific platforms like Carbon Black.
2. By a generic indexer applied to all fields if no built-in indexer was available.
3. Optionally, user-specific indexing guidelines.

#### User Defined Indexing

An Adapter can be configured to do custom indexing on the data it feeds.

This is done by setting the `indexing` element in the `client_options`. This field contains a list of index descriptors.

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

Put together in a client option, you could have:

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

USP Clients generate LimaCharlie Sensors at runtime. The ID of those sensors (SID) is generated based on the Organization ID (OID), the Sensor Seed Key and, for adapters that create one sensor per sensor key, that sensor key.

This implies that if want to re-key an IID (perhaps it was leaked), you may replace the IID with a new valid one. As long as you use the same OID and Sensor Seed Key, the generated SIDs will be stable despite the IID change.

### Using One Sensor for All Devices

Some platforms create a separate Sensor for each device, agent or user found in the logs, even when `sensor_key_path` is not set. Their built-in parser reads the sensor key and hostname from each event. For example, `fortigate` uses the `devid` and `devname` fields, and `cef` uses the CEF host. Other platforms that do this include `crowdstrike`, `sentinel_one`, `carbon_black`, `msdefender`, `github` and `1password`.

When the logs of many devices pass through one collector, such as FortiAnalyzer or a syslog relay, you may want a single Sensor for the collector instead of one per device. Removing `sensor_key_path` does not do this, because the parser still sets the key. Instead, set both the sensor key and the hostname to a constant template:

```yaml
client_options:
  platform: fortigate
  mapping:
    sensor_key_path: '{{ "fortianalyzer" }}'
    sensor_hostname_path: '{{ "fortianalyzer" }}'
```

- The value must be a template, with the constant in quotes inside `{{ }}`. A plain value such as `fortianalyzer` is read as a field path. No event has that field, so the parser's own key is used and nothing changes.
- Set `sensor_hostname_path` too. If you only set the key, the parser keeps setting the hostname from each event, and the single Sensor's hostname keeps changing between device names.
- The parser still runs and the event data is not changed. The fields that identify each device, such as `devid` and `devname` for `fortigate`, stay in every event, so D&R rules, searches and Outputs can still tell devices apart.
- Leave `sensor_identity_type` unset. A constant key does not identify a user or a device, so the parser's [identity declaration](#sensor-identity-declarations) is dropped.
- The sensor key is part of the Sensor ID (see [Sensor IDs](#sensor-ids)), so the change creates a new Sensor. The per-device Sensors created before the change stop receiving data and show as offline. Delete them once the new Sensor is receiving events. They do not come back, because no event carries their key anymore.

The single Sensor shows as online as long as logs from any device keep arriving, so its status no longer tells you whether one particular device is reporting. A per-sensor check like the one in [Alerting on sensors that stop sending data](../troubleshooting/non-responding-sensors.md) cannot tell devices apart once they share a Sensor. Base per-device monitoring on the device field in the events instead.

To try the change without touching the adapter you use in production, run a second adapter with the new mapping and a different `sensor_seed_key`, and send it some of the same logs, or point it at a test organization. Confirm that only one Sensor appears, that its hostname is the constant you set, and that the device fields are still in its events. Then apply the same mapping to the production adapter.

### Deleting an Adapter's Sensor

Deleting a sensor that was created by an adapter does not stop the adapter. A deleted adapter sensor is not refused when it reconnects: every time an adapter connects for a sensor, LimaCharlie clears that sensor's deleted state. Because the SID is derived from the same inputs every time (see [Sensor IDs](#sensor-ids)), the adapter reconnects as the same sensor, and the sensor reappears in the sensor list with the same SID.

In practice:

- If the adapter is still running, deleting its sensor disconnects it, the adapter reconnects on its own and the sensor comes back shortly after. An adapter that creates a single sensor keeps that sensor connected even when its source has no new data, so this happens even if no new events arrive.
- If the adapter was stopped first, the sensor stays deleted until that adapter, or another adapter with the same OID, Sensor Seed Key and sensor key, runs again and connects for that sensor. That can be days or months later.
- For a multiplexed adapter, each sensor key comes back independently. A key that had events in the last few minutes comes back shortly after it is deleted; a key that has been idle comes back when its next event arrives.

To remove an adapter sensor for good, stop the source first: uninstall or stop the on-prem adapter, or delete or disable the cloud sensor (Cloud Adapter) configuration. Then delete the sensor.

Adapter sensors never produce the [`deleted_sensor`](../../8-reference/platform-events.md#deleted_sensor) deployment event, so an [`undelete sensor`](../../8-reference/response-actions.md#undelete-sensor) rule is not needed to bring them back.

### Discovering adapter types and finding an adapter's sensor

The CLI can enumerate the supported adapter types, describe their configuration schema, and locate the sensor an adapter produced. These commands work for both `cloud-adapter` (the hosted set) and `external-adapter` (the on-prem set); the examples below use `cloud-adapter`.

List the supported adapter/sensor type names:

```bash
limacharlie cloud-adapter list-types
```

Note that `external-adapter list-types` lists the on-prem set, which differs from the cloud set.

Show the configuration field listing for one adapter type. This indicates where each field lives (for example, `hostname` under `client_options`). Add `--output json` for the raw schema:

```bash
limacharlie cloud-adapter schema --type <t>
limacharlie cloud-adapter schema --type <t> --output json
```

Find the live sensor(s) an adapter produced, matched by installation-key IID:

```bash
limacharlie cloud-adapter sensors --key <adapter-record>
```

An empty result means the adapter has not delivered any events yet; the sensor materializes on the first event.

## Validating Configurations

Before deploying an adapter to production, test your parsing and mapping against sample data, then confirm the adapter itself starts and connects.

### Testing Parsing with Sample Data

`limacharlie usp validate` sends sample data and a mapping to LimaCharlie, which runs them through the same parsing as live adapter data and returns the events it would produce. Nothing is ingested.

Put the mapping and the sample data in one YAML or JSON file:

- `mapping`: the same content as `client_options.mapping` in your adapter config. A `mapping` (or `mappings`) section with at least one setting is required.
- `mappings`: a list of mappings, for configs that use `client_options.mappings`.
- `text_input`: sample lines, one event per line. Use it for text-based platforms such as `text` or `cef`.
- `json_input`: one sample object, or a list of them. Use it for JSON-based platforms such as `json`.
- `indexing`: optional, the same content as `client_options.indexing`.
- `hostname`: optional, the hostname to use when the mapping does not set one. Defaults to `validation-test`.

Then run it with the platform the adapter uses (`client_options.platform`):

=== "Text with a regular expression"

    ```yaml
    # test.yaml
    mapping:
      parsing_re: '^(?P<ts>\S+) (?P<host>\S+) (?P<action>\S+) (?P<msg>.*)$'
      event_type_path: action
      event_time_path: ts
      sensor_hostname_path: host
    text_input: |
      2026-10-29T12:00:00Z fw01 DENY blocked 10.0.0.5 -> 8.8.8.8
      2026-10-29T12:00:01Z fw01 ALLOW allowed 10.0.0.6 -> 1.1.1.1
    ```

    ```bash
    limacharlie usp validate --platform text --input-file test.yaml --output yaml
    ```

=== "JSON"

    ```yaml
    # test.yaml
    mapping:
      event_type_path: action
      event_time_path: ts
      sensor_hostname_path: host
    json_input:
      - ts: 1793275200
        host: web01
        action: LOGIN
        user: alice
    ```

    ```bash
    limacharlie usp validate --platform json --input-file test.yaml --output yaml
    ```

=== "CEF"

    ```yaml
    # test.yaml
    mapping:
      event_type_path: _cef/evt_name
    text_input: |
      CEF:0|Security|threatmanager|1.0|100|worm successfully stopped|10|src=10.0.0.1 dst=2.1.2.2 spt=1232
    ```

    ```bash
    limacharlie usp validate --platform cef --input-file test.yaml --output yaml
    ```

Each event in `results` shows what LimaCharlie would store. For the text example above:

```yaml
errors: []
results:
- event_time: 1793275200000
  event_type: DENY
  hostname: fw01
  index_records: null
  investigation_id: ''
  json_payload:
    action: DENY
    host: fw01
    msg: blocked 10.0.0.5 -> 8.8.8.8
    ts: '2026-10-29T12:00:00Z'
  sensor_key: ''
  sid_ccs: null
- ...
```

Things to check in the output:

- A line that `parsing_re` does not match is not rejected. It comes back with the whole line in `json_payload.text` and an empty `event_type`. If every result looks like that, the regular expression does not match your data.
- `event_time: 0` means `event_time_path` is not set, or its value could not be parsed as a time. Live events in that case get the time at which the adapter read them.
- `index_records` lists the values LimaCharlie indexes for searching, such as the IP addresses in the CEF example.
- `errors` lists events that could not be processed at all, for example when a [Transform](#configurations) fails.

### Common Validation Issues

When the request itself is invalid, the command fails with `API error (400)` and a generic `BACKEND_ERROR`, without saying what is wrong. Check these causes:

| Cause | Fix |
|-------|-----|
| No `mapping` or `mappings` section, or an empty one (`mapping: {}`) | Add a mapping with at least one setting, such as `event_type_path`. |
| `parsing_re` or `parsing_grok` does not compile | Fix the expression. Unbalanced parentheses are the usual cause. |
| No sample data, or both `text_input` and `json_input` | Provide exactly one of them. |
| `--platform` is not a known platform | Use the same value as `client_options.platform`, for example `text`, `json` or `cef`. |

### Checking the Adapter Configuration

The adapter checks its configuration when it starts, and exits with an error if something is missing or invalid, for example `missing oid`, `missing installation_key` or `missing platform`. It has no dry-run mode. To check a new configuration, run the adapter in the foreground and look for:

1. The `Configs in use` block, which shows the configuration the adapter actually loaded.
2. A `usp-client connected` line, which means LimaCharlie accepted the connection.

If the adapter exits or does not connect, see [Adapter Troubleshooting](../../8-reference/faq/adapter-troubleshooting.md) for the error messages and their fixes. To see which fields an adapter type accepts, use `limacharlie cloud-adapter schema --type <type>` (see [Discovering adapter types](#discovering-adapter-types-and-finding-an-adapters-sensor)).

### SDK Validation

The Python SDK runs the same validation with `USP.validate()`:

```python
--8<-- "snippets/python/usp_validate.py"
```
