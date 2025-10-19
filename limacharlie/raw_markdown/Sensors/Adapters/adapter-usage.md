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


### Multi-Adapter

It is possible to execute multiple instances of adapters of the same type within the same adapter process, for example to have a single adapter process monitor files in multiple directories with slightly different configurations.

This is achieved by using a configuration file (as described above) with multiple YAML "documents" within like this:

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


## Runtime Configuration

The Adapter runtime supports some custom behaviors to make it more suitable for specific deployment scenarios:

  * `healthcheck`: an integer that specifies a port to start an HTTP server on that can be used for healthchecks.

## Core Configuration

All Adapter types support the same `client_options`, plus type-specific configurations. The following configurations are _required_ for every Adapter:

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.

  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.

  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.

  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

  * `client_options.hostname`: a hostname for the adapter.

### Example

Using inline parameters:

    ./lc-adapter file file_path=/path/to/logs.json \
      client_options.identity.installation_key=<INSTALLATION KEY> \
      client_options.identity.oid=<ORG ID> \
      client_options.platform=json \
      client_options.sensor_seed_key=<SENSOR SEED KEY> \
      client_options.mapping.event_type_path=<EVENT TYPE FIELD> \
      client_options.hostname=<HOSTNAME>


Using Docker:

    docker run -d --rm -it -p 4404:4404/udp refractionpoint/lc-adapter syslog \
      client_options.identity.installation_key=<INSTALLATION KEY> \
      client_options.identity.oid=<ORG ID> \
      client_options.platform=cef \
      client_options.hostname=<HOSTNAME> \
      client_options.sensor_seed_key=<SENSOR SEED KEY> \
      port=4404 \
      iface=0.0.0.0 \
      is_udp=true

Using a configuration file:

    ./lc-adapter file config_file.yaml

## Parsing and Mapping

### Transformation Order

Data sent via USP can be formatted in many different ways. Data is processed in a specific order as a pipeline:

  1. Regular Expression with named capture groups parsing a string into a JSON object.

  2. Built-in (in the cloud) LimaCharlie parsers that apply to specific `platform` values (like `carbon_black`).

  3. The various "extractors" defined, like `EventTypePath`, `EventTimePath`, `SensorHostnamePath` and `SensorKeyPath`.

  4. Custom `Mappings` directives provided by the client.

### Configurations

The following configurations allow you to customize the way data is ingested by the platform, including mapping and redefining fields such as the event type path and time.

  * `client_options.mapping.parsing_re`: regular expression with [named capture groups](https://github.com/StefanSchroeder/Golang-Regex-Tutorial/blob/master/01-chapter2.markdown#named-matches). The name of each group will be used as the key in the converted JSON parsing.

  * `client_options.mapping.parsing_grok: ` grok pattern parsing for structured data extraction from unstructured log messages. Grok patterns combine regular expressions with predefined patterns to simplify log parsing and field extraction.

  * `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers.

  * `client_options.mapping.hostname`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie.

  * `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports [template strings](../../Events/template-strings-and-transforms.md) based on each event.

  * `client_options.mapping.event_time_path`: indicates which component of the event represents the Event Time of the resulting event in LimaCharlie.

  * `client_options.mapping.rename_only`: _deprecated_

  * `client_options.mapping.mappings`: _deprecated_

  * `client_options.mapping.transform`: a [Transform](../../Events/template-strings-and-transforms.md) to apply to events.

  * `client_options.mapping.drop_fields`: a list of field paths to be dropped from the data before being processed and retained.

Mapping Fields Deprecated

The `client_options.mapping.rename_only` and `client_options.mapping.mappings` fields have been deprecated in favor of `client_options.mapping.transform`. Please see [associated documentation](../../Events/template-strings-and-transforms.md) for use of the `transform` config.

### Parsing

#### Named Group Parsing

If the data ingested in LimaCharlie is text (a syslog line for example), you may automatically parse it into a JSON format. To do this, you need to define one of the following:

  * a grok pattern, using the `client_options.mapping.parsing_grok` option

  * a regular expression, using the `client_options.mapping.parsing_re` option

#### Grok Patterns

##### Basic Syntax

Grok patterns use the following syntax:

The grok pattern line must start with **message:** , followed by the patterns, as in the example below

  * `%{PATTERN_NAME:field_name}` - Extract a pattern into a named field

  * `%{PATTERN_NAME}` - Match a pattern without extraction

Custom patterns can be defined using the pattern name as a key

##### Built-in Patterns

LimaCharlie includes standard Grok patterns for common data types:

  * `%{IP:field_name}` - IP addresses (IPv4/IPv6)

  * `%{NUMBER:field_name}` - Numeric values

  * `%{WORD:field_name}` - Single words (no whitespace)

  * `%{DATA:field_name}` - Any data up to delimiter

  * `%{GREEDYDATA:field_name}` - All remaining data

  * `%{TIMESTAMP_ISO8601:field_name}` - ISO 8601 timestamps

  * `%{LOGLEVEL:field_name}` - Log levels (DEBUG, INFO, WARN, ERROR)

**Example Firewall Log Record:**

    2024-01-01 12:00:00 ACCEPT TCP 192.168.1.100:54321 10.0.0.5:443 packets=1 bytes=78

**LimaCharlie Configuration to Match Firewall Log:**

    client_options:
      mapping:
        parsing_grok:
          message: '%{TIMESTAMP_ISO8601:timestamp} %{WORD:action} %{WORD:protocol} %{IP:src_ip}:%{NUMBER:src_port} %{IP:dst_ip}:%{NUMBER:dst_port} packets=%{NUMBER:packets} bytes=%{NUMBER:bytes}'
        event_type_path: "action"
        event_time_path: "timestamp"

**Fields Extracted by the Above Configuration:**

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

#### Regular Expressions

**With this log line as an example:**

    Nov 09 10:57:09 penguin PackageKit[21212]: daemon quit


**you could apply the following regular expression as**`parsing_re`**:**

    (?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)


which would result in the following event in LimaCharlie:

    {
      "date": "Nov 09 10:57:09",
      "host": "penguin",
      "exe": "PackageKit",
      "pid": "21212",
      "msg": "daemon quit"
    }


#### Key/Value Parsing

Alternatively you can specify a regular expression that does NOT contain Named Groups, like this:

    (?:<\d+>\s*)?(\w+)=(".*?"|\S+)

When in this mode, LimaCharlie assumes the regular expression will generate a list of matches where each match has 2 submatches, and submatch index 1 is the Key name, and submatch index 2 is the value. This is compatible with logs like CEF for example where the log could look like:

    <20>hostname=my-host log_name=http_logs timestamp=....

which would end up generating:

    {
      "hostname" : "my-host",
      "log_name": "http_logs",
      "timestamp": "..."
    }

#### Extraction

LimaCharlie has a few core constructs that all events and sensors have.
Namely:

  * Sensor ID

  * Hostname

  * Event Type

  * Event Time

You may specify certain fields from the JSON logs to be extracted into these common fields.

This process is done by specifying the "path" to the relevant field in the JSON data. Paths are like a directory path using `/` for each sub directory except that in our case, they describe how to get to the relevant field from the top level of the JSON.

For example, using this event:

    {
      "a": "x",
      "b": "y",
      "c": {
        "d": {
          "e": "z"
        }
      }
    }


The following paths would yield the following results:

  * `a`: `x`

  * `b`: `y`

  * `c/d/e`: `z`

The following extractors can be specified:

  * `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers.

  * `client_options.mapping.sensor_hostname_path`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie.

  * `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports [template strings](../../Events/template-strings-and-transforms.md) based on each event.

  * `client_options.mapping.event_time_path`: indicates which component of the event represents the Event Time of the resulting event in LimaCharlie.

### Indexing

Indexing occurs in one of 3 ways:

  1. By the built-in indexer for specific platforms like Carbon Black.

  2. By a generic indexer applied to all fields if no built-in indexer was available.

  3. Optionally, user-specific indexing guidelines.

#### User Defined Indexing

An Adapter can be configured to do custom indexing on the data it feeds.

This is done by setting the `indexing` element in the `client_options`. This field contains a list of index descriptors.

An index descriptor can have the following fields:

  * `events_included`: optionally, a list of event_type that this descriptor applies to.

  * `events_excluded`: optionally, a list of event_type this descriptor _does not_ apply to.

  * `path`: the element path this descriptor targets, like `user/metadata/user_id`.

  * `regexp`: optionally, a regular expression used on the `path` field to extract the item to index, like `email: (.+)`.

  * `index_type`: the category of index the value extracted belongs to, like `user` or `file_hash`.

Here is an example of a simple index descriptor:

    events_included:
      - PutObject
    path: userAgent
    index_type: user


Put together in a client option, you could have:

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


#### Supported Indexes

This is the list of currently supported index types:

  * `file_hash`

  * `file_path`

  * `file_name`

  * `domain`

  * `ip`

  * `user`

  * `service_name`

  * `package_name`

### Sensor IDs

USP Clients generate LimaCharlie Sensors at runtime. The ID of those sensors (SID) is generated based on the Organization ID (OID) and the Sensor Seed Key.

This implies that if want to re-key an IID (perhaps it was leaked), you may replace the IID with a new valid one. As long as you use the same OID and Sensor Seed Key, the generated SIDs will be stable despite the IID change.
