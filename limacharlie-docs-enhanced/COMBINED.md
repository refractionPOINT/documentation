# LimaCharlie Documentation (LLM-Optimized)

This documentation has been optimized for AI/LLM consumption:
- Semantic categorization
- High-quality content only (stubs removed)
- No human UI metadata
- Clean markdown formatting

---

# Adapters

## Adapter Usage

**Source:** https://docs.limacharlie.io/docs/adapter-usage

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

```
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

### Multi-Adapter

It is possible to execute multiple instances of adapters of the same type within the same adapter process, for example to have a single adapter process monitor files in multiple directories with slightly different configurations.

This is achieved by using a configuration file (as described above) with multiple YAML "documents" within like this:

```
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

* `healthcheck`: an integer that specifies a port to start an HTTP server on that can be used for healthchecks.

## Core Configuration

All Adapter types support the same `client_options`, plus type-specific configurations. The following configurations are *required* for every Adapter:

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.
* `client_options.hostname`: a hostname for the adapter.

### Example

Using inline parameters:

```
./lc-adapter file file_path=/path/to/logs.json \
  client_options.identity.installation_key=<INSTALLATION KEY> \
  client_options.identity.oid=<ORG ID> \
  client_options.platform=json \
  client_options.sensor_seed_key=<SENSOR SEED KEY> \
  client_options.mapping.event_type_path=<EVENT TYPE FIELD> \
  client_options.hostname=<HOSTNAME>
```

Using Docker:

```
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

```
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

* `client_options.mapping.parsing_re`: regular expression with [named capture groups](https://github.com/StefanSchroeder/Golang-Regex-Tutorial/blob/master/01-chapter2.markdown#named-matches). The name of each group will be used as the key in the converted JSON parsing.
* `client_options.mapping.parsing_grok:`  grok pattern parsing for structured data extraction from unstructured log messages. Grok patterns combine regular expressions with predefined patterns to simplify log parsing and field extraction.
* `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers.
* `client_options.mapping.hostname`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie.
* `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports [template strings](/v2/docs/template-strings-and-transforms) based on each event.
* `client_options.mapping.event_time_path`: indicates which component of the event represents the Event Time of the resulting event in LimaCharlie.
* `client_options.mapping.rename_only`: *deprecated*
* `client_options.mapping.mappings`: *deprecated*
* `client_options.mapping.transform`: a [Transform](/v2/docs/template-strings-and-transforms) to apply to events.
* `client_options.mapping.drop_fields`: a list of field paths to be dropped from the data before being processed and retained.

Mapping Fields Deprecated

The `client_options.mapping.rename_only` and `client_options.mapping.mappings` fields have been deprecated in favor of `client_options.mapping.transform`. Please see [associated documentation](/v2/docs/template-strings-and-transforms) for use of the `transform` config.

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

```
2024-01-01 12:00:00 ACCEPT TCP 192.168.1.100:54321 10.0.0.5:443 packets=1 bytes=78
```

**LimaCharlie Configuration to Match Firewall Log:**

```
client_options:
  mapping:
    parsing_grok:
      message: '%{TIMESTAMP_ISO8601:timestamp} %{WORD:action} %{WORD:protocol} %{IP:src_ip}:%{NUMBER:src_port} %{IP:dst_ip}:%{NUMBER:dst_port} packets=%{NUMBER:packets} bytes=%{NUMBER:bytes}'
    event_type_path: "action"
    event_time_path: "timestamp"
```

**Fields Extracted by the Above Configuration:**

```
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

#### Regular Expressions

**With this log line as an example:**

```
Nov 09 10:57:09 penguin PackageKit[21212]: daemon quit
```

**you could apply the following regular expression as** `parsing_re`**:**

```
(?P<date>... \d\d \d\d:\d\d:\d\d) (?P<host>.+) (?P<exe>.+?)\[(?P<pid>\d+)\]: (?P<msg>.*)
```

which would result in the following event in LimaCharlie:

```
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

```
(?:<\d+>\s*)?(\w+)=(".*?"|\S+)
```

When in this mode, LimaCharlie assumes the regular expression will generate a list of matches where each match has 2 submatches, and submatch index 1 is the Key name, and submatch index 2 is the value. This is compatible with logs like CEF for example where the log could look like:

```
<20>hostname=my-host log_name=http_logs timestamp=....
```

which would end up generating:

```
{
  "hostname" : "my-host",
  "log_name": "http_logs",
  "timestamp": "..."
}
```

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

```
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

* `a`: `x`
* `b`: `y`
* `c/d/e`: `z`

The following extractors can be specified:

* `client_options.mapping.sensor_key_path`: indicates which component of the events represent unique sensor identifiers.
* `client_options.mapping.sensor_hostname_path`: indicates which component of the event represents the hostname of the resulting Sensor in LimaCharlie.
* `client_options.mapping.event_type_path`: indicates which component of the event represents the Event Type of the resulting event in LimaCharlie. It also supports [template strings](/v2/docs/template-strings-and-transforms) based on each event.
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

* `events_included`: optionally, a list of event\_type that this descriptor applies to.
* `events_excluded`: optionally, a list of event\_type this descriptor *does not* apply to.
* `path`: the element path this descriptor targets, like `user/metadata/user_id`.
* `regexp`: optionally, a regular expression used on the `path` field to extract the item to index, like `email: (.+)`.
* `index_type`: the category of index the value extracted belongs to, like `user` or `file_hash`.

Here is an example of a simple index descriptor:

```
events_included:
  - PutObject
path: userAgent
index_type: user
```

Put together in a client option, you could have:

```
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

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## CrowdStrike Falcon Cloud

**Source:** https://docs.limacharlie.io/docs/adapter-types-crowdstrike-falcon-cloud

# CrowdStrike Falcon ("falconcloud") Specific Docs: https://docs.limacharlie.io/docs/adapter-types-crowdstrike

sensor_type: "falconcloud"
  falconcloud:
    client_id: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_ID"
    client_secret: "YOUR_CROWDSTRIKE_FALCON_API_CLIENT_SECRET"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_FALCONCLOUD"
      hostname: "crowdstrike-falcon-adapter"
      platform: "falconcloud"
      sensor_seed_key: "falcon-cloud-sensor"
      indexing: []
    # Optional configuration
    write_timeout_sec: 600  # Default: 10 minutes
    is_using_offset: false  # Default: false (recommended)
    offset: 0               # Only used if is_using_offset is true
```

## API Doc

See the official [documentation](https://developer.crowdstrike.com/docs/openapi/) and [additional docs on the library used to access the Falcon APIs](https://github.com/CrowdStrike/gofalcon).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Google Cloud Pubsub

**Source:** https://docs.limacharlie.io/docs/adapter-types-google-cloud-pubsub

# Google Cloud Pub/Sub Specific Docs: https://docs.limacharlie.io/docs/adapter-types-google-cloud-pubsub

sensor_type: "pubsub"
pubsub:
  sub_name: "your-pubsub-subscription-name"
  project_name: "your-gcp-project-id"
  service_account_creds: "hive://secret/gcp-pubsub-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PUBSUB"
    platform: "json"
    sensor_seed_key: "gcp-pubsub-sensor"
    mapping:
      # Map Pub/Sub message to sensor fields
      sensor_hostname_path: "attributes.hostname"
      event_type_path: "attributes.eventType"
      event_time_path: "publishTime"
    indexing: []
  # Optional configuration
  max_ps_buffer: 1048576  # 1MB buffer (optional)
```

## API Doc

See the [official documentation](https://cloud.google.com/pubsub).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Google Cloud Platform

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Google Cloud Storage

**Source:** https://docs.limacharlie.io/docs/adapter-types-google-cloud-storage

# Google Cloud Storage (GCS) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-gcs

sensor_type: "gcs"
gcs:
  bucket_name: "your-gcs-bucket-for-limacharlie-logs"
  service_account_creds: "hive://secret/gcs-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GCS"
    platform: "json"
    sensor_seed_key: "gcs-log-processor"
    mapping:
      sensor_hostname_path: "resource.labels.instance_id"
      event_type_path: "logName"
      event_time_path: "timestamp"
    indexing: []
  # Optional configuration
  prefix: "security_logs/firewall/"  # Filter by path prefix
  parallel_fetch: 5                  # Parallel downloads
  single_load: false                 # Continuous processing
```

## API Doc

See the [official documentation](https://cloud.google.com/storage).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## IMAP

**Source:** https://docs.limacharlie.io/docs/adapter-types-imap

# IMAP Specific Docs: https://docs.limacharlie.io/docs/adapter-types-imap

sensor_type: "imap"
imap:
  server: "imap.yourmailserver.com:993"
  username: "hive://secret/imap-username"
  password: "hive://secret/imap-password"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_IMAP"
    hostname: "imap-email-collector"
    platform: "json"
    sensor_seed_key: "imap-sensor-001"
    mapping:
      sensor_hostname_path: "headers.X-Originating-IP"
      event_type_path: "headers.Subject"
      event_time_path: "headers.Date"
    indexing: []
  # Optional IMAP-specific configuration
  inbox_name: "INBOX"                    # Default: "INBOX"
  is_insecure: false                     # Default: false (use SSL/TLS)
  from_zero: false                       # Default: false (only new emails)
  include_attachments: true              # Default: false
  max_body_size: 102400                  # Default: 0 (no limit)
  attachment_ingest_key: "attachments_data"      # Default: empty
  attachment_retention_days: 30          # Default: 0 (no retention)
```

## Use Cases

Although this Adapter can be used on any IMAP server for any inbox, it is often used to perform enterprise wide analysis and alerting using Email Journaling.

Email Journaling is supported by all major email platforms to perform analysis at scale. It generally involves enabling a data flow of all emails on the platform towards a specific email account where all emails accumulate.

Documentation for common platforms:

## Example Format

Emails ingested through the IMAP Adapter are in raw format so that detailed header information can be included and analyzed. Below is an example of an email received into LimaCharlie from a Google Workspace mailbox:

```
{
    "event": {
        "headers": {
            "arc-authentication-results": [
                "i=1; mx.google.com; dkim=pass header.i=@evil.com header.s=google header.b=LdyiNwmQ; spf=pass (google.com: domain of badguy@evil.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=badguy@evil.com; dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=evil.com; dara=pass header.i=@gmail.com"
            ],
            "arc-message-signature": [
                "i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816; h=to:subject:message-id:date:from:mime-version:dkim-signature; bh=NWZDzWD3fcPGImfiLFJgiOAWQBc6o9f064zRNQOEAZA=; fh=LdhDNbjh6ex3RxMo3wPAKsbuLWT+x/GDPYiwjW9lr10=; b=Y4WpYrqSVH+EuabO9I4v/LUf9MpLBNxghhA3btw3i31h3YHwssUKcYmfGu/LN5+2qc O4h7QYPT8oq5Sbk5T9NYYXb/u2XEyFmcHq78X9r1VBGgRXVzDVoAVE6uYdE+bMSsnBCx grJrZV+HEejJh91iNRlJ8+RDlESBAWastC6YpDHmZkAveUjMUzFBYzTiqCmGBjNYjfoF FOZSrlXMPj4fitoFunI57miFMXjXxiselSo9UEMuyeEcHAuiGZUyNHhLDTri+Nmf/5w1 QvaKCTx7iL4HpeS7budFLf4CuPbqNVIKmvsGq5vn68WFSO8i8AOW08IsKVlw/13KWQlu 6pTg==; dara=google.com"
            ],
            "arc-seal": [
                "i=1; a=rsa-sha256; t=1725302104; cv=none; d=google.com; s=arc-20160816; b=VPXTfX1HVTFWRixWBstbi2VEAFi6Tt7tfZPEn+4DBZ84n6Jn0MxTWRLP/2Y2GZkDC4 /ugCK/hRaxSqb9UzO9H/AGyrc2qX+rrX1OwLyQqSX5mA6ovrtNOuuHdS5BIBZjNQJS9X +aZICM/ZlkBvcPTKk8xLv/7yLD08xfaIZLdDWmbasg+pxKE5l+nLaxg7mXNC++8PaJRV ziaF9M7xd+Cx1kzDaSMBjTaubqtv3k7rQCqCN7WSLtxn0l2oz/Mdzvntdfcc7/qLrwNi yfmoG/lB4SrikCJJ7DsnGBvn7uCQZjsVbVTi4wLzIUCjqk5XNjIbTVZ1zVQ/HNwvg43g 6MiQ=="
            ],
            "authentication-results": [
                "mx.google.com; dkim=pass header.i=@evil.com header.s=google header.b=LdyiNwmQ; spf=pass (google.com: domain of badguy@evil.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=badguy@evil.com; dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=evil.com; dara=pass header.i=@gmail.com"
            ],
            "content-type": [
                "multipart/alternative; boundary=\"00000000000006151206212733f4\""
            ],
            "date": [
                "Mon, 2 Sep 2024 11:34:26 -0700"
            ],
            "delivered-to": [
                "acme@gmail.com"
            ],
            "dkim-signature": [
                "v=1; a=rsa-sha256; c=relaxed/relaxed; d=evil.com; s=google; t=1725302104; x=1725906904; dara=google.com; h=to:subject:message-id:date:from:mime-version:from:to:cc:subject :date:message-id:reply-to; bh=NWZDzWD3fcPGImfiLFJgiOAWQBc6o9f064zRNQOEAZA=; b=LdyiNwmQU+l8TQfVFgJYRNMvGqiplaqTOqlGWpSMUGm8891aHvKrxkqpjnHULKaY5l PzU3i0TK4Xl5Mdhjde5ewyD1o5BWTx8qEOFMuiZBOwOQys6nzcwBzQxKEuc8d6+GN8Z1 2H4uBqSxYfOaHAVU5qVx5/7IJF4TMDY/LK8A4="
            ],
"from": [
                "Bad Guy <badguy@evil.io>"
            ],
            "message-id": [
                "<CAD-4=gGtg=3dbuOO8M6pLairyXpnTD6Oh3P1OXauW5-SOXV0yw@mail.gmail.com>"
            ],
            "mime-version": [
                "1.0"
            ],
            "received": [
                "by 2002:a05:7010:161f:b0:3f2:d648:d2e9 with SMTP id l31csp230833mdi; Mon, 2 Sep 2024 11:35:05 -0700 (PDT)",
                "from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41]) by mx.google.com with SMTPS id d2e1a72fcca58-715e5749b07sor4893537b3a.11.2024.09.02.11.35.04 for <acme@gmail.com> (Google Transport Security); Mon, 02 Sep 2024 11:35:04 -0700 (PDT)"
            ],
            "received-spf": [
                "pass (google.com: domain of badguy@evil.com designates 209.85.220.41 as permitted sender) client-ip=209.85.220.41;"
            ],
            "return-path": [
                "<badguy@evil.com>"
            ],
            "subject": [
                "more testing"
            ],
            "to": [
                "acme@gmail.com"
            ],
            "x-gm-message-state": [
                "AOJu0YzthcsAvu7FAaCG7tVsbF4IP4NAAP2ICmXBCZM3q/X+EjpqD6L+ HBDMSMll8JxmIsLL9Hq4U6l/4iwLiRBys3iUsJ3A03Tr5TQVO+PUZyvd5CBxtrsj0Hy675LgaQ7 0oJ2lN6XxBJuSm+/UvFWcTafXVHpnHqvcnYE6cByvJzwFOaEV06U="
            ],
"x-google-dkim-signature": [
                "v=1; a=rsa-sha256; c=relaxed/relaxed; d=1e100.net; s=20230601; t=1725302104; x=1725906904; h=to:subject:message-id:date:from:mime-version:x-gm-message-state :from:to:cc:subject:date:message-id:reply-to; bh=NWZDzWD3fcPGImfiLFJgiOAWQBc6o9f064zRNQOEAZA=; b=VNAyNje9Qf3Xz7pGtX6FCaK67/ICW8aVWws/VdEDA/Ay1XO91LBQdEv7cKjZ+mcm1K uS5gPPVBMXVf+68KmiWyoiartMf/X4VsuTWzJRHyrtL9O8fX26xcgElzkAmm9N6/hKYg qsZujh4fpii2jk8VIz3jGNWB41qUbJklu9BNSRLiwzQnew9Av/J48+JaxfZA38qD08x4 o7UPxTick1figeCmYpAR0x16ETNg6lLC8GdJEnnWlIUZJN+K2z3A7xwD6SdAjsy6HFur 6oonKeJjVIzirWToF2mspK5MHbGI8aXmFzpu51gvQsC9caRDNaod9C9GlwSM/2oLhQWN kozw=="
            ],
            "x-google-smtp-source": [
                "AGHT+IF4ypTOZTFYRo4zx1pdxWk8sJAzLq+8GoGM8toOjlzCT7o9u5Tw0AWDAwK+2MjV6eBL1v0fhHbYcjfipAgz4Y4="
            ],
"x-received": [
                "by 2002:a05:6a00:9451:b0:714:3153:ab4 with SMTP id d2e1a72fcca58-717458aeedemr5351482b3a.27.1725302104964; Mon, 02 Sep 2024 11:35:04 -0700 (PDT)",
                "by 2002:a05:6a20:c68e:b0:1ce:d412:f407 with SMTP id adf61e73a8af0-1ced412f48bmr6010277637.18.1725302103735; Mon, 02 Sep 2024 11:35:03 -0700 (PDT)"
            ]
        },
        "parts": [
            {
                "body_text": "One more test email.\r\n",
                "hashes": {
                    "md5": "cbe37e2ee4cf3c35d67a7c4a8e6a9e35",
                    "sha1": "c2f203f43304ab0a4c3154a84d0c876fa9c23204",
                    "sha256": "95dbb63f3fd41f7852395d84ef9570ef4db567c43d20e3f1e27c72c903b94686"
                },
                "headers": {
                    "content-type": [
                        "text/plain; charset=\"UTF-8\""
                    ]
                }
            },
            {
                "body_text": "<div dir=\"ltr\">One more test email.</div>\r\n",
                "hashes": {
                    "md5": "a2fcd5c1aa40abe526bbbbd58251a90f",
                    "sha1": "5748cc5fc2cd318a5584651731887ac9d9df4df2",
                    "sha256": "1f3877f593c1af2ad3e482aee2f4181a34e0f502799908f4ca330f3327d6c175"
                },
                "headers": {
                    "content-type": [
                        "text/html; charset=\"UTF-8\""
                    ]
                }
            }
        ]
    },
    "routing": {
        "arch": 9,
        "did": "",
        "event_id": "fb9554d8-522e-4977-a378-df7f3fcc186a",
        "event_time": 1725302106808,
        "event_type": "email",
        "ext_ip": "internal",
        "hostname": "testimap",
        "iid": "XXXXXXX",
        "int_ip": "",
        "moduleid": 6,
        "oid": "YYYYYY",
        "plat": 436207616,
        "sid": "ZZZZZZZZ",
        "tags": [
            "cloud2"
        ],
        "this": "f4925ea82ef44d18b349695466d6055a"
    }
}
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## IT Glue

**Source:** https://docs.limacharlie.io/docs/adapter-types-it-glue

# Adapter Documentation: https://docs.limacharlie.io/docs/adapter-types
# For Cloud Sensor configurations, use:
#        token: "hive://secret/itglue-api-token"

sensor_type: "itglue"
itglue:
  token: "hive://secret/itglue-api-token"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_ITGLUE"
    hostname: "itglue-adapter"
    platform: "json"
    sensor_seed_key: "itglue-audit-sensor"
    mapping:
      sensor_hostname_path: "attributes.resource_name"
      event_type_path: "attributes.action"
      event_time_path: "attributes.created_at"
    indexing: []
```

## API Doc

See the official [documentation](https://api.itglue.com/developer/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Kubernetes Pods Logs

**Source:** https://docs.limacharlie.io/docs/adapter-types-kubernetes-pods-logs

# Kubernetes Pods Specific Docs: https://docs.limacharlie.io/docs/adapter-types-k8s-pods

sensor_type: "k8_pods"
k8s_pods:
 В  В client_options:
 В  В  В identity:
 В  В  В  В oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
 В  В  В  В installation_key: "YOUR_LC_INSTALLATION_KEY_K8SPODS"
 В  В  В hostname: "k8s-worker-node"
 В  В  В platform: "k8s_pods"
 В  В  В sensor_seed_key: "k8s-pods-sensor"
 В  В root: "/var/log/pods" В  В  В  В  В  В  В  В  В  В  В  В  В  В  В # Required: Pod logs directory
 В  В write_timeout_sec: 600 В  В  В  В  В  В  В  В  В  В  В  В  В  В  # Optional: defaults to 600
 В  В include_pods_re: "^production_.*" В  В  В  В  В  В  В  В  В # Optional: include filter
 В  В exclude_pods_re: "^kube-system_kube-proxy-.*$" В  В # Optional: exclude filter
```

## Sample Kubernetes Configuration

An example Daemon Set configuration for Kubernetes:

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
 В name: lc-adapter-k8s-pods
 В namespace: default
spec:
 В minReadySeconds: 30
 В selector:
 В  В matchLabels:
 В  В  В name: lc-adapter-k8s-pods
 В template:
 В  В metadata:
 В  В  В labels:
 В  В  В  В name: lc-adapter-k8s-pods
 В  В spec:
 В  В  В containers:
 В  В  В - image: refractionpoint/lc-adapter-k8s-pods
 В  В  В  В name: lc-adapter-k8s-pods
 В  В  В  В volumeMounts:
 В  В  В  В - mountPath: /k8s-pod-logs
 В  В  В  В  В name: pod-logs
 В  В  В  В env:
 В  В  В  В - name: K8S_POD_LOGS
 В  В  В  В  В value: /k8s-pod-logs
 В  В  В  В - name: OID
 В  В  В  В  В value: aaaaaaaa-bfa1-bbbb-cccc-138cd51389cd
 В  В  В  В - name: IKEY
 В  В  В  В  В value: aaaaaaaa-9ae6-bbbb-cccc-5e42b854adf5
 В  В  В  В - name: NAME
 В  В  В  В  В value: k8s-pods
 В  В  В volumes:
 В  В  В - hostPath:
 В  В  В  В  В path: /var/log/pods
 В  В  В  В name: pod-logs
 В updateStrategy:
 В  В rollingUpdate:
 В  В  В maxUnavailable: 1
 В  В type: RollingUpdate
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.В

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Mac Unified Logging

**Source:** https://docs.limacharlie.io/docs/adapter-types-mac-unified-logging

# macOS Unified Logging Specific Docs: https://docs.limacharlie.io/docs/adapter-types-macos-unified-logging

sensor_type: "mac_unified_logging"
  mac_unified_logging:
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_MACOSUL"
      hostname: "user-macbook-pro"
      platform: "mac_unified_logging"
      sensor_seed_key: "macos-unified-logging-sensor"
    # Optional configuration
    write_timeout_sec: 600                           # Default: 600 seconds
    predicate: 'processImagePath endswith "/usr/sbin/sshd" OR subsystem == "com.apple.security"'
```

## Service Creation

If you want this adapter to run as a service, you can run the following script to add a plist file to the endpoint **with your variables replaced**. Please note that this example also has an example predicate, so if you do not wish to use a predicate, remove that line.

```
sudo -i

curl https://downloads.limacharlie.io/adapter/mac/64 -o /usr/local/bin/lc_adapter
chmod +x /usr/local/bin/lc_adapter

tee -a /Library/LaunchDaemons/io.limacharlie.adapter.macunifiedlogging.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>io.limacharlie.adapter.macunifiedlogging</string>
    <key>UserName</key>
	<string>root</string>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/usr/local/bin</string>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
      <key>PATH</key>
      <string>/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin</string>
    </dict>
    <key>Program</key>
    <string>/usr/local/bin/lc_adapter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/lc_adapter</string>
        <string>mac_unified_logging</string>
        <string>client_options.identity.installation_key=$INSTALLATION_KEY</string>
        <string>client_options.identity.oid=$OID</string>
        <string>client_options.hostname=$SENSOR_NAME</string>
        <string>client_options.platform=json</string>
        <string>client_options.sensor_seed_key=$SENSOR_NAME</string>
        <string>predicate=eventMessage CONTAINS[c] "corp.sap.privileges"</string>
    </array>
  </dict>
</plist>
EOF

launchctl load -w /Library/LaunchDaemons/io.limacharlie.adapter.macunifiedlogging.plist
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Microsoft 365

**Source:** https://docs.limacharlie.io/docs/adapter-types-microsoft-365

# Office 365 Management Activity API Specific Docs: https://docs.limacharlie.io/docs/adapter-types-office-365-management-activity-api
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/o365-tenant-id"
#   client_id: "hive://secret/o365-client-id"
#   client_secret: "hive://secret/o365-client-secret"

sensor_type: "office365"
office365:
  tenant_id: "hive://secret/azure-o365-tenant-id"
  client_id: "hive://secret/azure-o365-client-id"
  client_secret: "hive://secret/azure-o365-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_O365"
    hostname: "ms-o365-adapter"
    platform: "json"
    sensor_seed_key: "office365-audit-sensor"
    mapping:
      sensor_hostname_path: "ClientIP"
      event_type_path: "Operation"
      event_time_path: "CreationTime"
    indexing: []
  # Office 365 specific configuration
  content_types:
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
  # Optional configuration
  endpoint: "enterprise"                           # Default: "enterprise"
  start_time: "2024-01-01T00:00:00Z"              # Optional: historical start time
  domain: "yourcompany.onmicrosoft.com"           # Optional: for GCC environments
  publisher_id: "hive://secret/o365-publisher-id" # Optional: usually same as tenant_id
```

## Configuring a Microsoft 365 Adapter in the Web UI

### Preparing Office 365 details

To establish an Office 365 adapter, we will need to complete a few steps within the Azure portal. Ensure that you have the correct permissions to set up a new App registration.

* Within the Microsoft Azure portal, create a new App registration. You can follow Microsoft's Quickstart guide [here](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app).
* The LimaCharlie connector requires a secret for Office 365 data. You can create one under `Certificates & secrets`. Be sure to copy this value and save it somewhere - you can only view it once.

* Additionally, you'll need to ensure that the app has the correct permissions to view Office 365 data via the Management API. Within `API Permissions`, configure the following permissions:

  + `ActivityFeed.Read` (Delegated & Application)
  + `ActivityFeed.ReadDlp` (Delegated & Application) *[if you want DLP permissions]*

Additionally, you may need to grant admin consent to the above permissions.

At this point, you should have all the details you need to configure the Adapter.

### Setting Up the Adapter

Within the LimaCharlie web application, select `+ Add` Sensor, and then select `Office 365`:

You can select a pre-existing Installation Key or create a new one, unique for this adapter. Once an Installation Key is selected, you will be prompted with a form to finish setting up the adapter. Choose your desired adapter name, and provide the following values:

| Item | Azure Portal Location |
| --- | --- |
| Domain | Home |
| Tenant ID | App Registration Overview |
| Publisher ID | App Registration Overview |
| Client ID | App Registration Overview |
| Client Secret | Created during creation in Certificates & secrets |
| API Endpoint | `enterprise`, `gcc-gov`, `gcc-high-gov`, or `dod-gov` |

Finally, you will also need to select a "Content Type" to import. This is the type of events you want to bring in to LimaCharlie. The options are as follows:

* `Audit.AzureActiveDirectory`
* `Audit.Exchange`
* `Audit.SharePoint`
* `Audit.General`
* `DLP.All`

Without a value, the default is *all of the above*.

Click `Complete Cloud Installation`, and LimaCharlie will attempt to connect to the Microsoft Office 365 Management API and pull events.

## Sample Rule

When ingested into LimaCharlie, Office 365 data can be referenced directly in your D&R rules. You could do this via a platform operator:

```
op: is platform
name: office365
```

We can also reference Office 365 events directly. The following sample rule looks at `FileAccessed` events from anonymous user names, and reports accordingly.

```
# Detection
event: FileAccessed
path: event/UserId
op: contains
value: anon

# Response
- action: report
  name: OneDrive File Accessed by Anonymous User
```

Note that in the detection above, we pivot on the `FileAccessed` event, which is associated with SharePoint activity. Available event types will depend on source activity and events ingested. More information on audit log activities can be found [here](https://learn.microsoft.com/en-us/purview/audit-log-activities).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

---

## Microsoft Defender

**Source:** https://docs.limacharlie.io/docs/adapter-types-microsoft-defender

# Adapter Documentation: https://docs.limacharlie.io/docs/adapter-types
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/azure-tenant-id"
#   client_id: "hive://secret/defender-client-id"
#   client_secret: "hive://secret/defender-client-secret"

sensor_type: "defender"
defender:
  tenant_id: "hive://secret/azure-tenant-id"
  client_id: "hive://secret/azure-defender-client-id"
  client_secret: "hive://secret/azure-defender-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_DEFENDER"
    hostname: "ms-defender-adapter"
    platform: "json"
    sensor_seed_key: "defender-sensor"
    mapping:
      sensor_hostname_path: "machineDnsName"
      event_type_path: "alertType"
      event_time_path: "lastUpdateTime"
    indexing: []
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Mimecast

**Source:** https://docs.limacharlie.io/docs/adapter-types-mimecast

# Mimecast Specific Docs: https://docs.limacharlie.io/docs/adapter-types-mimecast
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/mimecast-client-id"
#   client_secret: "hive://secret/mimecast-client-secret"

sensor_type: "mimecast"
mimecast:
  client_id: "hive://secret/mimecast-client-id"
  client_secret: "hive://secret/mimecast-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_MIMECAST"
    hostname: "mimecast-logs-adapter"
    platform: "json"
    sensor_seed_key: "mimecast-audit-sensor"
    mapping:
      sensor_hostname_path: "sender"
      event_type_path: "eventType"
      event_time_path: "eventTime"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.services.mimecast.com/docs/auditevents/1/routes/api/audit/get-audit-events/post).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Okta

**Source:** https://docs.limacharlie.io/docs/adapter-types-okta

# Okta Specific Docs: https://docs.limacharlie.io/docs/adapter-types-okta
# For cloud sensor deployment, store credentials as hive secrets:

#   apikey: "hive://secret/okta-api-token"

sensor_type: "okta"
okta:
  apikey: "hive://secret/okta-api-key"
  url: "https://your-company.okta.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_OKTA"
    hostname: "okta-systemlog-adapter"
    platform: "json"
    sensor_seed_key: "okta-system-logs-sensor"
    mapping:
      sensor_hostname_path: "client.device"
      event_type_path: "eventType"
      event_time_path: "published"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.okta.com/docs/reference/api/system-log/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## PandaDoc

**Source:** https://docs.limacharlie.io/docs/adapter-types-pandadoc

# PandaDoc Specific Docs: https://docs.limacharlie.io/docs/adapter-types-pandadoc
# For cloud sensor deployment, store credentials as hive secrets:

#   api_key: "hive://secret/pandadoc-api-key"

sensor_type: "pandadoc"
pandadoc:
  api_key: "hive://secret/pandadoc-api-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PANDADOC"
    hostname: "pandadoc-events-adapter"
    platform: "json"
    sensor_seed_key: "pandadoc-logs-sensor"
    mapping:
      sensor_hostname_path: "ip"
      event_type_path: "method"
      event_time_path: "request_time"
    indexing: []
```

## API Doc

See the official [documentation](https://developers.pandadoc.com/reference/list-api-logs).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## S3

**Source:** https://docs.limacharlie.io/docs/adapter-types-s3

# AWS S3 Specific Docs: https://docs.limacharlie.io/docs/adapter-types-s3
# For cloud sensor deployment, store credentials as hive secrets:

#   access_key: "hive://secret/aws-access-key"
#   secret_key: "hive://secret/aws-secret-key"

sensor_type: "s3"
s3:
  bucket_name: "your-s3-bucket-name-for-logs"
  access_key: "hive://secret/aws-s3-access-key"
  secret_key: "hive://secret/aws-s3-secret-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_S3"
    hostname: "aws-s3-adapter"
    platform: "json"
    sensor_seed_key: "s3-log-processor"
    mapping:
      sensor_hostname_path: "source_host"
      event_type_path: "event_category"
      event_time_path: "timestamp"
    indexing: []
  # Optional S3-specific configuration
  prefix: "logs/application_xyz/"              # Filter by object prefix
  parallel_fetch: 5                           # Parallel downloads
  single_load: false                          # Continuous processing
```

## API Doc

See the [official documentation](https://aws.amazon.com/s3/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## SQS

**Source:** https://docs.limacharlie.io/docs/adapter-types-sqs

# AWS SQS Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sqs

sensor_type: "sqs"
sqs:
  queue_url: "https://sqs.us-east-1.amazonaws.com/123456789012/your-security-logs-queue"
  aws_access_key_id: "hive://secret/aws-access-key-id"
  aws_secret_access_key: "hive://secret/aws-secret-access-key"
  aws_region: "us-east-1"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SQS"
    platform: "json"
    sensor_seed_key: "aws-sqs-sensor"
    mapping:
      sensor_hostname_path: "source.instance_id"
      event_type_path: "detail.eventName"
      event_time_path: "time"
    indexing: []
  # Optional SQS-specific configuration
  max_messages: 10                       # Default: 10 (max messages per poll)
  wait_time_seconds: 20                  # Default: 20 (long polling)
  visibility_timeout: 300                # Default: 300 seconds
  delete_after_processing: true          # Default: true
```

## API Doc

See the [official documentation](https://aws.amazon.com/sqs/).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Sophos

**Source:** https://docs.limacharlie.io/docs/adapter-types-sophos

# Sophos Central Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sophos-central
# For cloud sensor deployment, store credentials as hive secrets:

#   clientid: "hive://secret/sophos-client-id"
#   clientsecret: "hive://secret/sophos-client-secret"
#   tenantid: "hive://secret/sophos-tenant-id"

sensor_type: "sophos"
sophos:
  clientid: "hive://secret/sophos-client-id"
  clientsecret: "hive://secret/sophos-client-secret"
  tenantid: "hive://secret/sophos-tenant-id"
  url: "https://api-us01.central.sophos.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SOPHOS"
    hostname: "sophos-central-adapter"
    platform: "json"
    sensor_seed_key: "sophos-siem-sensor"
    mapping:
      sensor_hostname_path: "endpoint.hostname"
      event_type_path: "type"
      event_time_path: "raisedAt"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.sophos.com/docs/siem-v1/1/overview).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Sublime Security

**Source:** https://docs.limacharlie.io/docs/adapter-types-sublime-security

# Sublime Security Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sublime-security
# For cloud sensor deployment, store credentials as hive secrets:

#   api_key: "hive://secret/sublime-api-key"

sensor_type: "sublime"
sublime:
  api_key: "hive://secret/sublime-api-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SUBLIME"
    hostname: "sublime-security-adapter"
    platform: "json"
    sensor_seed_key: "sublime-audit-sensor"
    mapping:
      sensor_hostname_path: "user.email"
      event_type_path: "type"
      event_time_path: "created_at"
    indexing: []
```

## API Doc

See the official [documentation](https://docs.sublime.security/reference/authentication).

## Ingesting Alerts

Sublime events can be ingested in LimaCharlie via a `json` Webhook Adapter configuration.

### Adapter Deployment

Sublime Security logs are ingested via a cloud-to-cloud webhook Adapter configured to receive JSON events. The steps of creating this Adapter and enabling the input include:

1. Creating the Webhook Adapter via the LimaCharlie CLI
2. Discovering the URL created for the Webhook Adapter.
3. Providing the completed URL to Sublime Security for webhook events.

#### 1. Creating the LimaCharlie Webhook Adapter

The following steps are modified from the generic Webhook Adapter creation documentation, found [here](/v2/docs/tutorial-creating-a-webhook-adapter).

Creating a Webhook Adapter requires a set of parameters, including organization ID, Installation Key, platform, and mapping details, among other parameters. The following configuration can be modified to easily configure a Webhook Adapter for ingesting Sublime Security events:

```
{
    "sensor_type": "webhook",
    "webhook": {
       "secret": "sublime-security",
        "client_options": {
            "hostname": "sublime-security",
            "identity": {
                "oid": "<your_oid>",
                "installation_key": "<your_installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "sublime-super-secret-key",
            "mapping" : {
                "event_type_path" : "data/flagged_rules/name",
                "event_time_path" : "created_at"
            }
        }
    }
}
```

Note that in the mapping above, we make the following changes:

* `event_type_path` is mapped to the rule name from the Sublime alert
* `event_time_path` is mapped to the `created_at` field from the Sublime alert

#### 2. Building the Adapter URL

After creating the webhook, you'll need to retrieve the webhook URL from the [Get Org URLs](https://docs.limacharlie.io/apidocs/get-org-urls) API call. You'll need the following information to complete the Webhook URL:

* Organization ID
* Webhook name (from the config)
* Secret (from the config)

Let's assume the returned domain looks like `9157798c50af372c.hook.limacharlie.io`, the format of the URL would be:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

Note that the `secret` value can be provided in the webhook URL or as an HTTP header named `lc-secret`.

#### 3. Configuring the Sublime webhook Action

Within the Sublime Security console, navigate to **Manage** > **Actions**. From here, you can select **New Action** > **Webhook**.

Within the **Configure webhook** menu, provide a name and the Adapter URL constructed in Step 2 above.

As mentioned in Step 2, you can configure the HTTP header `lc-secret`, if so desired.

Upon configuration of the webhook within Sublime Security, alerts can be configured to be sent to the LimaCharlie platform. To test the Webhook, select **Trigger Custom Action** from any Flagged message, and send to the LimaCharlie webhook.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

---

## Syslog

**Source:** https://docs.limacharlie.io/docs/adapter-types-syslog

# Syslog Specific Docs: https://docs.limacharlie.io/docs/adapter-types-syslog

sensor_type: "syslog"
  syslog:
    port: 1514
    iface: "0.0.0.0"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_SYSLOG"
      hostname: "syslog-adapter"
      platform: "linux"
      sensor_seed_key: "syslog-collector"
      mapping:
        parsing_grok:
          message: "^<%{INT:pri}>%{SYSLOGTIMESTAMP:timestamp}\\s+%{HOSTNAME:hostname}\\s+%{WORD:tag}(?:\\[%{INT:pid}\\])?:\\s+%{GREEDYDATA:message}"
        sensor_hostname_path: "hostname"
        event_type_path: "tag"
        event_time_path: "timestamp"
    # Optional syslog-specific configuration
    is_udp: false                               # TCP (default) vs UDP
    write_timeout_sec: 30                       # Write timeout
    ssl_cert: "/certs/syslog_server.pem"       # Optional SSL cert
    ssl_key: "/certs/syslog_server.key"        # Optional SSL key
    mutual_tls_cert: "/certs/client_ca.pem"    # Optional mTLS
```

#### Step 3: Configure syslog output to send messages to a local listener

This step will depend on the type of syslog daemon you are using (syslog, rsyslog, syslog-ng, etc.) Within the daemon configuration file, configure the desired facility(-ies) to direct to the local listener. In the following example, we configured `auth` and `authpriv` events to write to both `/var/log/audit.log` and `127.0.0.1:1514`.

```
auth,authpriv.*			/var/log/auth.log
auth,authpriv.*			@@127.0.0.1:1514
```

After applying the appropriate configuration, restart the syslog daemon.

#### Step 4: Confirm that syslog messages are sent to the correct location

Utilizing a tool like `netcat`, you can listen on the appropriate port to confirm that messages are being sent. The following command will spawn a `netcat` listener on port 1514:

```
nc -l -p 1514
```

#### Step 5: Run the LimaCharlie Adapter

Execute the binary Adapter with the syslog configuration file in order to start the LimaCharlie listener. If started correctly, you should see the following messages in `stdout`:

```
DBG <date>: usp-client connecting
DBG <date>: usp-client connected
DBG <date>: listening for connections on :1514
```

Double-check the LimaCharlie Sensors list, and you should see the text adapter with the respective hostname sending `Syslog` events.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Windows Event Log

**Source:** https://docs.limacharlie.io/docs/adapter-types-windows-event-log

# Windows Event Log (WEL) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-windows-event-log

# Basic Event Sources:
# evt_sources: "Security,System,Application"

# With XPath Filters:
# evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System:'*[System[Provider[@Name=\"Microsoft-Windows-Kernel-General\"]]]'"

# File-Based Sources:
# evt_sources: "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx:'*[System[(EventID=4624)]]'"

  wel:
    evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System,Application"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_WEL"
      hostname: "prod-dc01.example.local"
      platform: "windows"
      sensor_seed_key: "wel-collector"
    write_timeout_sec: 30
```

### XPath Filter Examples

Security Events (High Priority):

```
  Security:'*[System[(Level=1 or Level=2 or Level=3)]]'
```

Logon Events Only:

```
  Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'
```

System Errors:

```
  System:'*[System[(Level=1 or Level=2)]]'
```

Specific Provider:

```
  Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'
```

## API Doc

See the [official documentation](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Zendesk

**Source:** https://docs.limacharlie.io/docs/adapter-types-zendesk

# Zendesk Specific Docs: https://docs.limacharlie.io/docs/adapter-types-zendesk
# For cloud sensor deployment, store credentials as hive secrets:
#   api_token: "hive://secret/zendesk-api-token"
#   zendesk_email: "hive://secret/zendesk-email"

sensor_type: "zendesk"
zendesk:
  api_token: "hive://secret/zendesk-api-token"
  zendesk_domain: "yourcompany.zendesk.com"
  zendesk_email: "hive://secret/zendesk-api-email"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_ZENDESK"
    hostname: "zendesk-support-adapter"
    platform: "json"
    sensor_seed_key: "zendesk-audit-sensor"
    mapping:
      sensor_hostname_path: "actor_name"
      event_type_path: "action"
      event_time_path: "created_at"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

# Add Ons

## AI Agent Engine [LABS]

**Source:** https://docs.limacharlie.io/docs/ai-agent-engine

# Import LC SDK
import limacharlie
import json
# Instantiate the SDK with default creds.
lc = limacharlie.Manager()
# Instantiate the Extension manager object.
ext = limacharlie.Extension(lc)

# Issue a request to the "ext-ai-agent-engine" extension for the "my-agent-name" agent.
response = ext.request("ext-ai-agent-engine", "start_session", {
    "agent_definition": "my-agent-name",
    "message": "You're a cyber security expert, summarize this detection: {...}"
})

for msg in response['data']['responses']:
  print(f"AI says: {json.dumps(msg, indent=2)}")
```

## AI Agent structure

#### Example AI Agent Definition

The following is a sample AI Agent definition that simply aims at summarizing detections.

```
{
  "name": "my-agent",
  "description": "Some agent that does something...",
  "credentials": "hive://secret/ai-creds", // These credentials will be used when accessing LimaCharlie APIs.
  // Instructions are the core system behavior for the AI
  "instructions": "You are a cybersecurity expert system who's job it is to summarize detections/alerts for SOC analysts. Output as markdown. Include detailed technical context about the alert and if MITRE techniques are mentioned, summarize them. Also include what next steps of the investigation should be. The audience of the report is a cyber security team at a medium sized enterprise.",
  "max_iterations": 10, // If the AI makes tool calls to the LC API or LC Sensors, this limits the number of iterations the AI is called.
  "allowed_tools": [
    "get_sensor_info" // List of tool categories (see list_tools or the Available Tools section below).
  ]
}
```

### Available Tools

The tools available to the AI Agents are the same ones available from the official [LimaCharlie MCP Server](/v2/docs/mcp-server).

## Infrastructure as Code

Not currently available, coming up.

## Billing

The AI Agent Engine is billed per token processed, including initial messages, prompt and response.

## Privacy

Currently, the model in use is the commercial Gemini models.

Although the models may change (and eventually Bring-Your-Own-Model), these models will never use your data to train more models and LimaCharlie never uses the data to train models.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Command-line Interface

---

## Playbook [LABS]

**Source:** https://docs.limacharlie.io/docs/playbook

# Import LC SDK
import limacharlie
# Instantiate the SDK with default creds.
lc = limacharlie.Manager()
# Instantiate the Extension manager object.
ext = limacharlie.Extension(lc)

# Issue a request to the "ext-playbook" extension.
response = ext.request("ext-playbook", "run_playbook", {
    "name": "my-playbook",
    "credentials": "hive://secret/my-playbook-api-key",
    "data": {
        "some": "data"
    }
})

# The returned data from the playbook.
print(response)
```

## Playbook structure

A playbook is a normal python script. The only required component is a top level function called `playbook` which takes 2 arguments:

* `sdk`: an instance of the LC Python SDK ( `limacharlie.Manager()` ) pre-authenticated to the relevant Organization based on the credentials provided, if any, `None` otherwise.
* `data`: the optional JSON dictionary provided as context to your playbook.

The function must return a dictionary with the following optional keys:

1. `data`: a dictionary of data to return to the caller
2. `error`: an error message (string) to return to the caller
3. `detection`: a dictionary to use as detection
4. `cat`: a string to use as the category of the detection, if `detection` is specified.

This allows your playbook to return information about its execution, return data, errors or generate a detection. The python `print()` statement is not currently being returned to the caller or otherwise accessible, so you will want to use the `data` in order to return information about the execution of your playbook.

#### Example playbook

The following is a sample playbook that sends a webhook to an external product with a secret stored in LimaCharlie, and it returns the data as the response from the playbook.

```
import limacharlie
import json
import urllib.request

def playbook(sdk, data):
  # Get the secret we need from LimaCharlie.
  mySecret = limacharlie.Hive(sdk, "secret").get("my-secret-name").data["secret"]

  # Send the Webhook.
  request = urllib.request.Request("https://example.com/webhook", data=json.dumps(data).encode('utf-8'), headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mySecret}"
  }, method="POST")

  try:
    with urllib.request.urlopen(request) as response:
      response_body = response.read().decode('utf-8')
      # Parse the JSON response
      parsed_response = json.loads(response_body)
  except Exception as e:
    # Some error occured, let the caller/LC know.
    return {
      "error": str(e),
    }

  # Return the data to the caller/LC.
  return {
    "data": parsed_response,
  }
```

### Execution environment

Playbooks contents are cached for short periods of time ( on the order of 10 seconds ) in the cloud.

Playbooks are instantiated on demand and the instance is reused for an undefined amount of time.

Playbook code only executes during the main call to the `playbook` function, background on-going running is not supported.

The execution environment is provisioned on a per-Organization basis, meaning all your playbooks may execute within the same container, but NEVER on a container used by another Organization.

Although you have access to the local environment, this environment is ephemeral and can be wiped at any moment in between executions so you should take care that your playbook is self contained and doesn’t assume pre-existing conditions.

A single execution of a playbook is limited to 10 minutes.

The current execution environment is based on the default libraries provided by the `python:slim` Dockerhub official container plus the following packages:

* Python

  + `weasyprint`
  + `flask`
  + `gunicorn`
  + `flask`
  + `limacharlie` (LimaCharlie SDK/CLI)
  + `lcextension` (LimaCharlie Extension SDK)
  + `scikit-learn` (Python Machine Learning kit)
  + `jinja2`
  + `markdown`
  + `pillow`
* NodeJS
* AI

  + Claude Code (`claude`) CLI tool
  + Codex (`codex`) CLI tool
  + Gemini CLI (`gemini`) CLI tool

Custom packages and execution environment tweaks are not available in self-serve mode, but they *may* be available on demand, get in touch with us at support@limacharlie.io.

## Infrastructure as Code

Example:

```
hives:
    playbook:
        my-playbook:
            data:
                python: |-
                    def playbook(sdk, data):
                        if not sdk:
                            return {"error": "LC API key required to list sensors"}
                        return {
                            "data": {
                                "sensors": [s.getInfo() for s in sdk.sensors()]
                            }
                        }
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

## Billing

Playbooks are billed per seconds of total execution time.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## Velociraptor

**Source:** https://docs.limacharlie.io/docs/ext-velociraptor

# Detection
op: is
path: routing/log_type
target: artifact_event
value: velociraptor

# Response
- action: output
  name: artifacts-tailored
  suppression:
    is_global: false
    keys:
        - '{{ .event.original_path }}'
        - '{{ .routing.log_id }}'
    max_count: 1
    period: 1m
- action: report
  name: VR artifact ingested
```

To see how you could use something like this to automate post-processing of Velociraptor triage collections, check out this [open source example](https://github.com/shortstack/lcvr-to-timesketch) which sends KAPE Triage acquisitions to a webhook which then retrieves the collection for processing via [Plaso](https://github.com/log2timeline/plaso/) and into [Timesketch](https://github.com/google/timesketch).

To see how you can send Velociraptor data to BigQuery for further analysis, see this [tutorial](/v2/docs/velociraptor-to-bigquery).

## Using Velociraptor in D&R Rules

If you want to trigger a Velociraptor collection as a response to one of your detections, you can configure an extension request in the respond block of a rule.

This example will kick off the KAPE files Velociraptor artifact to collect event logs from the system involved in the detection.

```
- action: extension request
  extension action: collect
  extension name: ext-velociraptor
  extension request:
    artifact_list: ['Windows.KapeFiles.Targets']
    sid: '{{ .routing.sid }}' # Use a sensor selector OR a sid, **not both**
    sensor_selector: '' # Use a sensor selector OR a sid, **not both**
    args: '{{ "EventLogs=Y" }}'
    collection_ttl: 3600 # 1 hour - collection_ttl is specified in seconds
    retention_ttl: 7 # retention_ttl is specified in days
    ignore_cert: false
```

### Migrating D&R Rule from legacy Service to new Extension

***LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy Velociraptor service, preview the change and execute the conversion required in the rule "response".

Command line to preview Velociraptor rule conversion:

```
limacharlie extension convert_rules --name ext-velociraptor
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute Velociraptor rule conversion:

```
limacharlie extension convert_rules --name ext-velociraptor --no-dry-run
```

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

---

# Detection Response

## Detection Logic Operators

**Source:** https://docs.limacharlie.io/docs/detection-logic-operators

# Detection Logic Operators

Operators are used in the Detection part of a Detection & Response rule. Operators may also be accompanied by other available parameters, such as transforms, times, and others, referenced later in this page.

> For more information on how to use operators, read [Detection & Response Rules](/v2/docs/detection-and-response).

## Operators

### and, or

The standard logical boolean operations to combine other logical operations. Takes a single `rules:` parameter that contains a list of other operators to "AND" or "OR" together.

Example:

```
op: or
rules:
  - ...rule1...
  - ...rule2...
  - ...
```

### is

Tests for equality between the value of the `"value": <>` parameter and the value found in the event at the `"path": <>` parameter.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example rule:

```
event: NEW_PROCESS
op: is
path: event/PARENT/PROCESS_ID
value: 9999
```

### exists

Tests if any elements exist at the given path (regardless of its value).

Example rule:

```
event: NEW_PROCESS
op: exists
path: event/PARENT
```

The `exists` operator also supports an optional `truthy` parameter. When `true`, this parameter indicates the `exists` should treat `null` and `""` (empty string) values as if they were non-existent like:

The rule:

```
op: exists
path: some/path
truthy: true
```

applied to:

```
{
  "some": {
    "path": ""
  }
}
```

would NOT match.

### contains

The `contains` checks if a substring can be found in the value at the path.

An optional parameter `count: 3` can be specified to only match if the given
 substring is found *at least* 3 times in path.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example rule:

```
event: NEW_PROCESS
op: contains
path: event/COMMAND_LINE
value: reg
count: 2
```

### ends with, starts with

The `starts with` checks for a prefix match and `ends with` checks for a suffix match.

They both check if the value found at `path` matches the given `value`, based on the operator.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

### is greater than, is lower than

Check to see if a value is greater or lower (numerically) than a value in the event.

They both use the `path` and `value` parameters. They also both support the `length of` parameter as a boolean (true or false). If set to true, instead of comparing
 the value at the specified path, it compares the length of the value at that path.

### matches

The `matches` op compares the value at `path` with a regular expression supplied in the `re` parameter. Under the hood, this uses the Golang's `regexp` [package](https://golang.org/pkg/regexp/), which also enables you to apply the regexp to log files.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example:

```
event: FILE_TYPE_ACCESSED
op: matches
path: event/FILE_PATH
re: .*\\system32\\.*\.scr
case sensitive: false
```

### not

The `not` operator inverts the result of its rule. For example, when applied to an `is` operator, it changes the logic from "equals" to "does not equal". When applied to an or operator, it changes the logic from "any of these conditions are true" to "none of these conditions are true"

Example:

```
event: NEW_PROCESS
op: is
not: true
path: event/PARENT/PROCESS_ID
value: 9999
```

### string distance

The `string distance` op looks up the [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two strings. In other words it generates the minimum number of character changes required for one string to become equal to another.

For example, the Levenshtein Distance between `google.com` and `googlr.com` (`r` instead of `e`) is 1.

This can be used to find variations of file names or domain names that could be used for phishing, for example.

Suppose your company is `onephoton.com`. Looking for the Levenshtein Distance between all `DOMAIN_NAME` in `DNS_REQUEST` events, compared to `onephoton.com` it could detect an attacker using `onephot0n.com` in a phishing email domain.

The operator takes a `path` parameter indicating which field to compare, a `max` parameter indicating the maximum Levenshtein Distance to match and a `value` parameter that is either a string or a list of strings that represent the value(s) to compare to. Note that although `string distance` supports the `value` to be a list, most other operators do not.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example:

```
event: DNS_REQUEST
op: string distance
path: event/DOMAIN_NAME
value:
  - onephoton.com
  - www.onephoton.com
max: 2
```

This would match `onephotom.com` and `0nephotom.com` but NOT `0neph0tom.com`.

Using the [file name](#file-name) transform to apply to a file name in a path:

```
event: NEW_PROCESS
op: string distance
path: event/FILE_PATH
file name: true
value:
  - svchost.exe
  - csrss.exe
max: 2
```

This would match `svhost.exe` and `csrss32.exe` but NOT `csrsswin32.exe`.

### is 32 bit, is 64 bit, is arm

All of these operators take no additional arguments, they simply match if the relevant Sensor characteristic is correct.

Example:

```
op: is 64 bit
```

### is platform

Checks if the event under evaluation is from a sensor of the given platform.

Takes a `name` parameter for the platform name. The current platforms are:

* `windows`
* `linux`
* `macos`
* `ios`
* `android`
* `chrome`
* `vpn`
* `text`
* `json`
* GCP
* AWS
* `carbon_black`
* `crowdstrike`
* `1password`
* `office365`
* `msdefender`

Example:

```
op: is platform
name: 1password
```

### is tagged

Determines if the Tag supplied in the `tag` parameter is already associated with the sensor that the event under evaluation is from.

### lookup

Looks up a value against a [lookup add-on](https://app.limacharlie.io/add-ons/category/lookup) (a.k.a. resource) such as a threat feed.

```
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookups/malwaredomains
case sensitive: false
```

This rule will get the `event/DOMAIN_NAME` of a `DNS_REQUEST` event and check if it's a member of the `lookup` named `malwaredomains`. If it is, then the rule is a match.

The value is supplied via the `path` parameter and the lookup is defined in the `resource` parameter. Resources are of the form `hive://lookups/RESOURCE_NAME`. In order to access a lookup, your Organization must be subscribed to it.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

> API-based lookups, like VirusTotal and IP Geolocation, work a little bit differently. For more information, see [Using API-based lookups](/v2/docs/add-ons-api-integrations).

> You can create your own lookups and optionally publish them in the add-on marketplace. To learn more, see [Lookups](/v2/docs/config-hive-lookups) and [Lookup Manager](/v2/docs/ext-lookup-manager).

### scope

In some cases, you may want to limit the scope of the matching and the `path` you use to be within a specific part of the event. The `scope` operator allows you to do just that, reset the root of the `event/` in paths to be a sub-path of the event.

This comes in as very useful for example when you want to test multiple values of a connection in a `NETWORK_CONNECTIONS` event but always on a per-connection. If you  were to do a rule like:

```
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: starts with
    path: event/NETWORK_ACTIVITY/?/SOURCE/IP_ADDRESS
    value: '10.'
  - op: is
    path: event/NETWORK_ACTIVITY/?/DESTINATION/PORT
    value: 445
```

you would hit on events where *any* connection has a source IP prefix of `10.` and *any* connection has a destination port of `445`. Obviously this is not what we had in mind, we wanted to know if a *single* connection has those two characteristics.

The solution is to use the `scope` operator. The `path` in the operator will become the new `event/` root path in all operators found under the `rule`. So the above would become

Example:

```
event: NETWORK_CONNECTIONS
op: scope
path: event/NETWORK_ACTIVITY/
rule:
  op: and
  rules:
    - op: starts with
      path: event/SOURCE/IP_ADDRESS
      value: '10.'
    - op: is
      path: event/DESTINATION/PORT
      value: 445
```

### cidr

The `cidr` checks if an IP address at the path is contained within a given
[CIDR network mask](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing).

Example rule:

```
event: NETWORK_CONNECTIONS
op: cidr
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
cidr: 10.16.1.0/24
```

### is private address

The `is private address` checks if an IP address at the path is a private address
 as defined by [RFC 1918](https://en.wikipedia.org/wiki/Private_network).

Example rule:

```
event: NETWORK_CONNECTIONS
op: is private address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is public address

The `is public address` checks if an IP address at the path is a public address
 as defined by [RFC 1918](https://en.wikipedia.org/wiki/Private_network).

Example rule:

```
event: NETWORK_CONNECTIONS
op: is public address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

## Transforms

Transforms are transformations applied to the value being evaluated in an event, prior to the evaluation.

### file name

Sample: `file name: true`

The `file name` transform takes a `path` and replaces it with the file name component of the `path`. This means that a `path` of `c:\windows\system32\wininet.dll` will become `wininet.dll`.

### sub domain

Sample: `sub domain: "-2:"`

The `sub domain` extracts specific components from a domain name. The value of `sub domain` is in [slice notation](https://stackoverflow.com/questions/509211/understanding-slice-notation). It looks like `startIndex:endIndex`, where the index is 0-based and indicates which parts of the domain to keep.

Some examples:

* `0:2` means the first 2 components of the domain: `aa.bb` for `aa.bb.cc.dd`.
* `-1` means the last component of the domain: `cc` for `aa.bb.cc`.
* `1:` means all components starting at 1: `bb.cc` for `aa.bb.cc`.
* `:` means to test the operator to every component individually.

### is older than

Test if a value in event at the `"path": <>` parameter, assumed to be either a second-based epoch or a millisecond-based epoch is older than a number of seconds as specified by the `seconds` parameter, centered in time at "now" during evaluation.

Example rule:

```
event: login-attempt
op: is older than
path: routing/event_time
seconds: 3600
```

where the example above would match on a `login-attempt` event that occurred more than 1h ago.

## Times

All operators support an optional parameter named `times`. When specified, it must contain a list of Time Descriptors when the accompanying operator is valid. Your rule can mix-and-match multiple Time Descriptors as part of a single rule on per-operator basis.

Here's an example rule that matches a Chrome process starting between 11PM and 5AM, Monday through Friday, Pacific Time:

```
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: chrome.exe
case sensitive: false
times:
  - day_of_week_start: 2     # 1 - 7
    day_of_week_end: 6       # 1 - 7
    time_of_day_start: 2200  # 0 - 2359
    time_of_day_end: 2359    # 0 - 2359
    tz: America/Los_Angeles  # time zone
  - day_of_week_start: 2
    day_of_week_end: 6
    time_of_day_start: 0
    time_of_day_end: 500
    tz: America/Los_Angeles
```

#### Time Zone

The `tz` should match a TZ database name from the [Time Zones Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Google Cloud Platform

Amazon Web Services

---

## Detection and Response

**Source:** https://docs.limacharlie.io/docs/detection-and-response

# Detection and Response

Detection & Response rules automate actions based on the real-time events streaming into LimaCharlie. Each rule has two YAML descriptors: one that describes what to detect, and another that describes how to respond.

Note

It's recommended to read about [Events](/v2/docs/events) before diving into  rules.

## A Basic Rule

Here's a rule that detects DNS requests to `example.com` and responds by reporting them within the Organization with a category name `DNS Hit example.com`.

```
# Detection
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
value: example.com

# Response
- action: report
  name: DNS Hit example.com
```

This rule will detect and respond to requests to `example.com` within 100ms of the `DNS_REQUEST` event occurring. It uses the `is` operator to assess if the given `value` can be found inside the `event` at the given `path`.

Want more detection examples?

For examples, check out the [Detection and Response Examples](/v2/docs/detection-and-response-examples).

## Detection

### Targets and events

Detections must specify an `event` (or `events`), and may optionally specify a `target`. Each target offers different event types. Here are the 5 possible rule targets:

* `edr` (default): telemetry events from LimaCharlie sensors
* `detection`: detections generated by other rules
* `deployment`: lifecycle events around deployment & enrollment of sensors
* `artifact`: artifacts collected via REST API or via `artifact_get` Sensor command
* `artifact_event`: lifecycle events around artifacts such as ingestion

For a full list of events with examples, see [Events Reference](/v2/docs/events).

Most of this page focuses on `edr` events. For information about other targets, see [Detection on Alternate Targets](/v2/docs/detection-on-alternate-targets).

#### Detections against Adapter events

Similar to EDR telemetry, data received via Adapters are observable via Detection & Response rules. D&R rules that action on Adapter-based data are written the same way, with event and operator qualifiers and response actions based on successful detections.

Depending on the type of adapter, you can reference adapter data directly via the `platform` [sensor selector](/v2/docs/reference-sensor-selector-expressions) (e.g. `aws`, `msdefender`, `crowdstrike`, etc.)

### Operators

Detections must specify an `op` (logical operator). The types of operators used are a good indicator for how complex the rule will be.

Here's a simple detection that uses a single `is windows` operator to detect a Windows sensor connecting to the Internet:

```
event: CONNECTED
op: is windows
```

And here's a more complex detection that uses the `and` operator to detect a non-Windows sensor that's making a DNS request to example.com.

```
event: DNS_REQUEST
op: and
rules:
- op: is windows
  not: true
- op: is
  path: event/DOMAIN_NAME
  value: example.com
```

There are 3 operators here:

1. The `and` operator evaluates nested `rules` and will only itself be `true` if both of the rules inside it are `true`
2. The `is windows` operator is accompanied by the `not` parameter, reversing the matching outcome and effectively saying "anything but windows"
3. The `is` operator is comparing the `value` 'example.com' to the content of the event at the given `path`

Each operator may have parameters alongside it. Some parameters, such as `not`, are useable on all operators. Most operators have required parameters specific to them.

> For a full list of operators and their usage, see [Reference: Operators](/v2/docs/detection-logic-operators).

### Paths

The `path` parameter is used commonly in several operators to specify which part of the event should be evaluated.

Here's an example of a standard JSON `DNS_REQUEST` event from a sensor:

```
{
  "event": {
    "DNS_TYPE": 1,
    "TIMESTAMP": 1456285240,
    "DNS_FLAGS": 0,
    "DOMAIN_NAME": "example.com"
  },
  "routing": {
    "event_type": "DNS_REQUEST",
    "oid": "8cbe27f4-agh1-4afb-ba19-138cd51389cd",
    "sid": "d3d17f12-eecf-5287-b3a1-bf267aabb3cf",
    "hostname": "test-host-123"
    // ...and other standardized routing data
  }
}
```

This detection will match the above event's hostname:

```
event: DNS_REQUEST
op: is
path: routing/hostname # where the value lives
value: test-host-123   # the expected value at that path
```

This works a lot like file paths in a directory system. Since LimaCharlie events are always formatted with separate `event` and `routing` data, almost all paths start with either `event/` or `routing/`.

> Tip: you can visit the Timeline view of any Sensor to browse historical events and bring them directly into the D&R rule editor.

Paths may also employ the use of wildcards `*` to represent 0 or more directory levels, or `?` to represent exactly 1 directory level. This can be useful when working with events like `NETWORK_CONNECTIONS`:

```
{
  "event": {
    "NETWORK_ACTIVITY": [
      {
        "SOURCE": {
          "IP_ADDRESS": "172.16.223.138",
          "PORT": 50396
        },
        "IS_OUTGOING": 1,
        "DESTINATION": {
          "IP_ADDRESS": "23.214.49.56",
          "PORT": 80
        }
      },
      {
        "SOURCE": {
          "IP_ADDRESS": "172.16.223.138",
          "PORT": 50397
        },
        "IS_OUTGOING": 1,
        "DESTINATION": {
          "IP_ADDRESS": "189.247.166.18",
          "PORT": 80
        }
      },
      // ...there could be several connections
    ],
    "HASH": "2de228cad2e542b2af2554d61fab5463ecbba3ff8349ba88c3e48637ed8086e9",
    "COMMAND_LINE": "C:\\WINDOWS\\system32\\msfeedssync.exe sync",
    "PROCESS_ID": 6968,
    "FILE_IS_SIGNED": 1,
    "USER_NAME": "WIN-5KC7E0NG1OD\\dev",
    "FILE_PATH": "C:\\WINDOWS\\system32\\msfeedssync.exe",
    "PARENT_PROCESS_ID": 1892
  },
  "routing": { ... } // Omitted for brevity
}
```

Notice that the `NETWORK_ACTIVITY` inside this event is a list.

Here's a rule that would match a known destination IP in any of the entries within `NETWORK_ACTIVITY`:

```
event: NETWORK_CONNECTIONS
op: is
path: event/NETWORK_ACTIVITY/?/DESTINATION/IP_ADDRESS # <---
value: 189.247.166.18
```

The `?` saves us from enumerating each index within the list and instead evaluates *all* values at the indicated level. This can be very powerful when used in combination with lookups: lists of threat indicators such as known bad IPs or domains.

> To learn more about using lookups in detections, see the `lookup` [operator](/v2/docs/detection-logic-operators#lookup).

### Values

The `value` parameter is commonly used by several detection operations but can also be used by some response actions as well.

In most detections `value` will be used to specify a known value like all the previous examples on this page have done. They're also capable of referencing previously set sensor variables using `value: [[var-name]]` double square bracket syntax.

Values from events can also be forwarded in response actions using `value: <<event/FILE_PATH>>` double angle bracket syntax.

> To see how sensor variables and lookback values are used, see the `add var / del var` action in [Reference: Response Actions](/v2/docs/response-actions).

## Response

Responses are much simpler than Detections. They're a list of actions to perform upon a matching detection.

### Actions

The most common action is the `report` action, which creates a Detection that shows up in the LimaCharlie web app and passes it along to the `detections` output stream in real-time.

```
- action: report
  name: detected-something

# Example of accessing map values
- action: report
  name: Event detected by {{ .event.USER_NAME }} from {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}
```

Each item in the response specifies an `action` and any accompanying parameters for that `action`.

A more complex response action could include running an [endpoint agent command](/v2/docs/endpoint-agent-commands) such as `yara_scan` using a field from within the detected event. The following example looks for `NEW_DOCUMENT` events that meet certain criteria, then initiates a YARA scan against the offending file path.

Detect

```
event: NEW_DOCUMENT
op: and
rules:
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .\:\\(users|windows\\temp)\\.*
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .*\.(exe|dll)
```

Respond

```
# Report is optional, but informative
- action: report
  name: Executable written to Users or Temp (yara scan)

# Initiate a sensor command to yara scan the FILE_PATH
- action: task
  command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
  investigation: Yara Scan Executable
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
      - Yara Scan Executable
    max_count: 1
    period: 1m
```

Notice the use of `suppression` to prevent the same `FILE_PATH` from being scanned more than once per minute to prevent a resource runaway situation.

Which D&R Rule Triggered a Command?

To determine which D&R rule triggered a command on an endpoint, navigate to the `Platform Logs` section. If a command was triggered by a D&R rule, the audit log will show the associate rule. If the command was sent via the API, the audit logs will show the API key name.

> To learn about all possible actions, see [Reference: Response Actions](/v2/docs/response-actions).

## Putting It All Together

Let's take this knowledge and write a rule to detect something a little more interesting.

On Windows there's a command called `icacls` which can be used to modify access control lists. Let's write a rule which detects any tampering via that command.

The first thing we can do is detect any new `icacls` processes:

```
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: icacls.exe
```

And we'll set a basic response action to report the detection, too:

```
- action: report
  name: win-acl-tampering
```

If we save that, we'll start to see detections for any `icacls` processes spawning. However, not all of them will be particularly interesting from a security perspective. In this case, we only really care about invocations of `icacls` where the `grant` parameter is specified.

Let's make this rule more specific. We can do this by using the `and` operator to match multiple operators. We'll check for the string `"grant"` in the `COMMAND_LINE`, and while we're at it we'll make sure we don't bother evaluating other platforms by using the `is windows` operator.

```
event: NEW_PROCESS
op: and
rules:
- op: is windows
- op: ends with
	path: event/FILE_PATH
	value: icacls.exe
- op: contains
  path: event/COMMAND_LINE
  value: grant
```

This more specific rule means we'll see fewer false positives to look at or exclude later.

However, we still might miss some invocations of `icacls` with this detection if they use any capital letters — our operators are being evaluated with an implicit `case sensitive: true` by default. Let's turn case sensitivity off and observe the final rule:

```
# Detection
event: NEW_PROCESS
op: and
rules:
- op: is windows
- op: ends with
	case sensitive: false
	path: event/FILE_PATH
	value: icacls.exe
- op: contains
	case sensitive: false
  path: event/COMMAND_LINE
  value: grant

# Response
- action: report
  name: win-acl-tampering
```

This rule combines multiple operators to specify the exact conditions which might make an `icacls` process interesting. If it sees one, it'll report it as a `win-acl-tampering` detection which will be forwarded to Outputs and become viewable in the Detections page.

> Tip: test your rules without waiting for events! We recommend enabling the replay add-on for a better D&R rule writing experience.
>
> * Visit Timeline of a sensor and `Build D&R Rule` directly from real events
> * While drafting a rule, `Replay` an event against the rule to see if it would match
> * Replay a rule over historical events to see if any detections would have occurred

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Endpoint Detection & Response

---

## Detection on Alternate Targets

**Source:** https://docs.limacharlie.io/docs/detection-on-alternate-targets

# Detection
target: detection
op: and
rules:
- op: is
  path: cat
  value: virus-total-hit
- op: is
  path: routing/hostname
  value: ceo-laptop

# Response
- action: extension request
  extension name: pagerduty
  extension action: run
  request:
    group: '{{ "lc-alerts" }}'
    severity: '{{ "critical" }}'
    component: '{{ "vip-alert" }}'
    summary: '{{ "Alert on a VIP endpoint." }}'
    source: '{{ "limacharlie.io" }}'
    class: '{{ "dr-rules" }}'
```

This rule takes a pre-existing detection report named `virus-total-hit` and sends it to PagerDuty if it occurs on a specific hostname.

## Target: deployment

Deployment events relate to sensors connecting to the cloud: `enrollment`, `sensor_clone`, `sensor_over_quota`, `deleted_sensor`.

Take the `sensor_clone` event as an example. This event can happen when a Sensor is installed in a VM image, leading to duplicate sensor IDs connecting to the cloud. When this is detected we can use this event to automate behavior to de-duplicate the sensor.

The `deployment` target supports all of the same operators and actions as regular `edr` rules.

### Example

```
# Detection
target: deployment
event: sensor_clone
op: is windows

# Response
- action: task
  command: file_del %windir%\system32\hcp.dat
- action: task
  command: file_del %windir%\system32\hcp_hbs.dat
- action: task
  command: file_del %windir%\system32\hcp_conf.dat
- action: task
  command: restart
```

This rule de-duplicates sensors on Windows by deleting `.dat` files specific to the Windows installation and then issuing a `restart` sensor command.

> For samples of each `deployment` event type, see [Reference: Platform Events](/v2/docs/reference-platform-events).

## Target: artifact

Parsed artifacts can be run through the rule engine as if they were regular `edr` events, but there are some key differences. Namely, they support a subset of operators and actions, while adding some special parameters.

### Example

This rule will target parsed `/var/log/auth.log` entries to see if there are are auth failures.

```
# Detection
target: artifact
artifact type: txt
artifact path: /var/log/auth.log
op: matches
re: .*(authentication failure|Failed password).*
path: /text
case sensitive: false

# Response
- action: report
  name: Failed Auth
```

### Supported Operators

* `is`
* `and`
* `or`
* `exists`
* `contains`
* `starts with`
* `ends with`
* `is greater than`
* `is lower than`
* `matches`
* `string distance`

### Supported Resources

`lookup` and `external` resources are supported within rules just like the `edr` target.

### Supported Actions

The only response action supported for the `artifact` target is the `report` action.

### Special Parameters

* `artifact path`: matches the start of the artifact's `path` string, e.g. `/auth.log`
* `artifact type`: matches the artifact's `type` string, e.g. `pcap`, `zeek`, `auth`, `wel`
* `artifact source`: matches the artifact's `source` string, e.g. `hostname-123`

> Note: for duplicate Windows Event Log ingestions, the rule engine will use the log's `EventRecordID` to ensure a rule will not run more than once over the same record.

## Target: artifact\_event

For unparsed logs, it can be useful to use the `ingest` and `export_complete` lifecycle events from the `artifact_event` target to automate behaviors in response to artifacts.

> For samples of `ingest` and `export_complete`, see [Reference: Platform Events](/v2/docs/reference-platform-events).

### Example

```
# Detection
target: artifact_event
event: export_complete
op: starts with
path: routing/log_type
value: pcap
case sensitive: false

# Response
- action: report
  name: PCAP Artifact ready to Download
```

## Target: schedule

Schedule events are triggered automatically at various intervals per Organization or per Sensor, observable in  rules via the `schedule` target.

For more information, see [Reference: Schedule Events](/v2/docs/reference-schedule-events)

## Target: audit

Audit events are generated by the LimaCharlie platform and track changes and events from within the platform such as tasking, replays, hive changes, etc. These events can be viewed within the "Platform Logs" menu or by viewing events from the `audit-logs` sensor.

## Target: billing

Billing events are generated by the LimaCharlie platform and are related to aspects of the platform such as quotas, thresholds, and other cost-associated events. For an example, see the [Usage Alerts Extension](/v2/docs/ext-usage-alerts) documentation

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

## Managed Rulesets

**Source:** https://docs.limacharlie.io/docs/managed-rulesets

# Managed Rulesets

In addition to LimaCharlie's powerful custom detection & response capabilities, we also offer native integration with several managed rulesets. LimaCharlie currently offers:

* SnapAttack Community Edition

  + AWS
  + EDR
  + Microsoft/Office 365

A Word on Managed Rulesets

While managed rulesets can help your organizations achieve detection and response capabilities quickly, not all detections are suitable for every environment.

Ensure that you are fine-tuning managed rulesets within your environment via enabling/disabling rules or via [False Positive](/v2/docs/false-positive-rules) controls.

Managed rulesets offer several advantages, such as:

* Providing out-of-the-box coverage for common threats, reducing the time and effort to develop in-house rules.
* Curated rulesets are maintained and updated by their respective parties, often covering the latest threats.
* A foundation for building complex detection logic utilizing managed rulesets as inspiration.

Every environment is unique, and we recommend choosing rulesets that benefit your need(s) and/or use case(s).

What's the difference between Sigma and Soteria rules?

[Sigma](https://github.com/SigmaHQ/sigma) is an open source project that aims at creating a generic query language for security and  rules. It looks up known anomalies and Common Vulnerabilities and Exposures (CVEs).

As Sigma is an open source project,

* applying the Sigma ruleset is free
* there will be a higher rate of false positives

[Soteria](https://soteria.io/) is a US-based MSSP that has been using LimaCharlie for a long time. They developed a corpus of hundreds of behavioral signatures for Windows / Mac / Linux (signature not in terms of a hash, but in terms of a rule that describes a behavior). With one click, you can apply their rules in a managed way. When Soteria updates the rules for their customers, you will get those updates in real time as well.

As Soteria is a managed ruleset,

* applying the Soteria ruleset costs $0.5 per endpoint per month
* the rate of false positives is much lower

Amazon Web Services

Endpoint Detection & Response

Managed Security Services Provider

---

## Response Actions

**Source:** https://docs.limacharlie.io/docs/response-actions

# Response Actions

## Overview

Actions in LimaCharlie Detection & Response () rules define what happens after a detection is triggered. Common actions include generating reports, tagging sensors, isolating networks, and the frequently used `task` action, which sends commands to an Endpoint Agent to interrogate or take action on the endpoint. This is useful for tasks like gathering system information or isolating a compromised endpoint. Suppression settings manage repetitive alerts by limiting action frequency, ensuring efficient automation and response workflows.

> For more information on how to use Actions, read [Detection & Response rules](/v2/docs/detection-and-response).

## Suppression

Suppression is valuable to help manage repetitive or noisy alerts.

### Reduce Frequency

In some cases, you may want to limit the number of times a specific Action is executed over a certain period of time. You can achieve this through `suppression`. This feature is supported in every Actions.

A suppression descriptor can be added to an Action like:

```
- action: report
  name: evil-process-detected
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.FILE_PATH }}'
      - 'evil-process-detected'
```

The above example means that the `evil-process-detected` detection will be generated up to once per hour per `FILE_PATH`. Beyond the first `report` with a given `FILE_PATH`, during the one hour period, new `report` actions from this rule will be skipped.

The `is_global: true` means that the suppression should operate globally within the Org (tenant), if the value was `false`, the suppression would be scoped per-Sensor.

The `keys` parameter is a list of strings that support [templating](/v2/docs/template-strings-and-transforms). Together, the unique combination of values of all those strings (ANDed) will be the uniqueness key this suppression rule uses. By adding to the keys the `{{ .event.FILE_PATH }}` template, we indicate that the `FILE_PATH` of the event generating this `report` is part of the key, while the constant string `evil-process detected` is just a convenient way for us to specify a value related to this specific detection. If the `evil process-detected` component of the key was not specified, then *all* actions that also just specify the `{{ .event.FILE_PATH }}` would be contained in this suppression. This means that using `is_global: true` and a complex key set, it is possible to suppress some actions across multiple Actions across multiple D&R rules.

> Supported Time Period Formats
>
> LimaCharlie supports the following formats for time periods: **ns**, **us** (or **µs**, both are accepted), **ms**, **s**, **m**, **h** (nanoseconds, microseconds, milliseconds, seconds, minutes, and hours, respectively)

### Threshold Activation

The other way to use suppression is using the `min_count` parameter. When set, the specific action will be suppressed until `min_count` number of activations have been received in that period.

Here's an example of this:

```
- action: report
  name: high-alerts
  suppression:
    min_count: 3
    max_count: 3
    period: 24h
```

The above example means the `high-alerts` detection will be generated once per hour but only after the rule the action belongs to has matched 3 times within that period.

This could be useful if you wanted to create higher order alerts that trigger a different type of detection, or send a page alert to a SOC, when more than X alerts occurred on a single host per period.

> Note: Both `min_count` and `max_count` must be specified when setting a threshold.

### Variable Count

It is also possible to increment a suppression by a value that's not one (`1`). This is achieved using the `count_path` parameter, which is a path (like `event/record/v`) pointing to an integer that should be used to increment the suppression counter.

This is useful for things like billing alerts, where we set a threshold activation (meaning "alert me if above X") where the threshold is reached by increments of billable values.

Here's an example of this:

```
detect:
    event: billing_record
    op: is
    path: event/record/k
    target: billing
    value: ext-strelka:bytes_scanned

respond:
    - action: report
      name: strelka-bytes-reached
      suppression:
        count_path: event/record/v
        is_global: true
        keys:
          - strelka-bytes-usage
        max_count: 1048576
        min_count: 1048576
        period: 24h
```

The above will alert (generate a detection in this case) when 1MB (1024 x 1024 x 1) of bytes have been billed by the Strelka Extension based on the `bytes_scanned` SKU, per 24h.

It does so by incrementing the suppression counter by the billed value (found in `event/record/v`), resetting after 24h, and if the value of 1MB is reached, alert once and only once.

## Available Actions

Actions allow you to specify "what" happens after a detection is found.

### add tag, remove tag

```
- action: add tag
  tag: vip
  entire_device: false # defaults to false
  ttl: 30 # optional
```

#### Optional Parameters

The `add tag` action can optionally take a `ttl` parameter that is a number of seconds the tag should remain applied to the sensor.

The `add tag` action can optionally have the `entire_device` parameter set to `true`. When enabled, the new tag will apply to the entire Device ID, meaning that every sensor that shares this Device ID will have the tag applied (and relevant TTL). If a Device ID is unavailable for the sensor, it will still be tagged.

This can be used as a mechanism to synchronize and operate changes across an entire device. A D&R rule could detect a behavior and then tag all sensors on the device so they may act accordingly, like start doing full pcap.

For example, this would apply the `full_pcap` to all sensors on the device for 5 minutes:

```
- action: add tag
  tag: full_pcap
  ttl: 300
  entire_device: true
```

### add var, del var

Add or remove a value from the variables associated with a sensor.

```
- action: add var
  name: my-variable
  value: <<event/VOLUME_PATH>>
  ttl: 30 # optional
```

The `add var` action can optionally take a `ttl` parameter that is a number of seconds the variable should remain in state for the sensor.

### extension request

Perform an asynchronous request to an extension the Organization is subscribed to.

```
- action: extension request
  extension name: dumper # name of the extension
  extension action: dump # action to trigger
  extension request:     # request parameters
    sid: '{{ .routing.sid }}'
    pid: event.PROCESS_ID
```

The `extension request` parameters will vary depending on the extension (see the relevant extension's schema). The `extension request` parameter is a [transform](/v2/docs/template-strings-and-transforms).

You can also specify a `based on report: true` parameter. When true (defaults to false), the transform for the `extension request` will be based on the latest `report` action's report instead of the original event. This means you MUST have a `report` action *before* the `extension request`.

### isolate network

Isolates the sensor from the network in a persistent fashion (if the sensor/host reboots, it will remain isolated). Only works on platforms supporting the `segregate_network` [sensor command](/v2/docs/reference-endpoint-agent-commands#segregatenetwork).

```
- action: isolate network
```

When the network isolation feature is used, LimaCharlie will block connections to all destinations other than the LimaCharlie cloud (so that you can perform an investigation, take remediation actions, and then ultimately remove the isolation to resume normal network operation). The host will maintain internet connectivity to allow for you to perform those actions.

> The `segregate_network` command is stateless, so if the endpoint reboots, it will not be in effect. The isolate network command in D&R rules is stateful, so it sets a flag in the cloud to make sure the endpoint remains isolated even after reboots.

### seal

Seals the sensor in a persistent fashion (if the sensor/host reboots, it will remain sealed). Only works on platforms supporting the `seal` [sensor command](/v2/docs/reference-endpoint-agent-commands#seal).

```
- action: seal
```

Sealing a sensor enables tamper resistance, preventing direct modifications to the installed EDR.

> The `seal` command is stateless, so if the endpoint reboots, it will not be in effect. The seal command in D&R rules is stateful, so it sets a flag in the cloud to make sure the endpoint remains sealed even after reboots.

### unseal

Removes the seal status of a sensor that had it set using `seal`.

```
- action: unseal
```

### output

Forwards the matched event to an Output identified by `name` in the `tailored` [stream](/v2/docs/outputs).

This allows you to create highly granular Outputs for specific events.

The `name` parameter is the name of the Output.

Example:

```
- action: output
  name: my-output
```

### rejoin network

Removes the isolation status of a sensor that had it set using `isolate network`.

```
- action: rejoin network
```

### report

```
- action: report
  name: my-detection-name
  publish: true # defaults to true
  priority: 3   # optional
  metadata:     # optional & free-form
    author: Alice (alice@wonderland.com)
  detect_data:  # additional free-form field that can be used for extraction of specific elements
```

Reports the match as a detection. Think of it as an alert. Detections go a few places:

* The `detection` Output stream
* The organization's Detections page (if `insight` is enabled)
* The D&R rule engine, for chaining detections

The `name`, `metadata` and `detect_data` parameters support [string templates](/v2/docs/template-strings-and-transforms) like `detected {{ .cat }} on {{ .routing.hostname }}`, note that the context of the transform is the detection itself and not the original event, so you would refer to `.detect.event.USER_NAME` and not `.event.USER_NAME` for example.

The `metadata` is generally used to populate information about the rule, its author, remediation etc.

The `detect_data` is generally used to extract specific parts of the detected event into a known format that can be common across multiple detection, like extracting the `domain` or `hash` field for example.

#### Limiting Scope

There is a mechanism for limiting scope of a `report`, prefixing `name` with `__` (double underscore). This will cause the detection
generated to be visible to chained D&R rules and Services, but the detection will *not* be sent to the Outputs for storage.

This is a useful mechanism to automate behavior using D&R rules without generating extra traffic that is not useful.

#### Optional Parameters

The `priority` parameter, if set, should be an integer. It will be added to the root of the detection report as `priority`.

The `metadata` parameter, if set, can include any data. It will be added to the root of the detection report as `detect_mtd`. This can be used to include information for internal use like reference numbers or URLs.

### task

```
- action: task
  command: history_dump
  investigation: susp-process-inv
```

Sends a task in the `command` parameter to the sensor that the event under evaluation is from.

An optional `investigation` parameter can be given to create a unique identifier for the task and any events emitted from the sensor as a result of the task.

The `command` parameter supports [string templates](/v2/docs/template-strings-and-transforms) like `artifact_get {{ .event.FILE_PATH }}`.

> To view all possible commands, see [Endpoint Agent Commands](/v2/docs/reference-endpoint-agent-commands)

### undelete sensor

Un-deletes a sensor that was previously deleted.

```
detect:
    target: deployment
    event: deleted_sensor
    op: is
    path: routing/event_type
    value: deleted_sensor
respond:
    - action: undelete sensor
```

This can be used in conjunction with the `deleted_sensor` event to allow sensors to rejoin the fleet.

### wait

Adds a delay (up to 1 minute) before running the next response action.

This can be useful if a previous response action needs to finish running (i.e. a command or payload run via `task`) before you can execute the next action.

> The `wait` action will block processing any events from that sensor for the specified duration of time. This is because D&R rules are run at wire-speed and in-order.

The `duration` parameter supports two types of values:

* A string describing a duration, like `5s` for 5 seconds or `10ms` for 10 milliseconds, as defined by [this function call](https://pkg.go.dev/time#ParseDuration).
* An integer representing a number of seconds.

Example:

```
- action: wait
  duration: 10s
```

and

```
- action: wait
  duration: 5
```

### add hive tag

Adds a tag to a Hive record. This can be used to mark some Hive records like D&R rules automatically.

```
- action: add hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
```

Unless the rule is not expected to hit often, you likely want to couple this with a `suppression` statement to avoid doing a lot of tagging of the same rules like:

```
- action: add hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - 'high-hit'
      - 'hive-tag'
```

### remove hive tag

Removes a tag from a Hive record.

```
- action: remove hive tag
  hive name: dr-general
  record name: my-rule
  tag: high-hit
```

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

---

## Soteria Rules

**Source:** https://docs.limacharlie.io/docs/soteria-rules

# Soteria Rules

[Soteria](https://soteria.io/) is a US-based MSSP and longtime MSSP, and has built a wealth of experience writing and managing LimaCharlie [detection & response](/v2/docs/detection-and-response) rules. With one click, you can apply their rules to your environment. When Soteria updates the rules for their customers, you will get those updates in real time as well. Soteria provides their rules in the form of managed rulesets, available via the [Add-ons Marketplace](https://app.limacharlie.io/add-ons/category/rulesets).

Soteria  rule content

Please note that Soteria won’t get access to your data, and you won’t be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

Soteria provides the following rulesets:

Soteria rules are available for a fee, either per-Sensor or per-Organization, which can be found on their respective pages within the Add-ons Marketplace.

Managed Security Services Provider

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

## Stateful Rules

**Source:** https://docs.limacharlie.io/docs/stateful-rules

# Detect initial event
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: cmd.exe
case sensitive: false
with child: # Wait for child matching this nested rule
  op: ends with
  event: NEW_PROCESS
  path: event/FILE_PATH
  value: calc.exe
  case sensitive: false
```

Simply put, this will detect:

```
cmd.exe --> calc.exe
```

Because it uses `with child` it will not detect:

```
cmd.exe --> firefox.exe --> calc.exe
```

To do that, we could use `with descendant` instead.

## Detecting Proximal Events

To detect repetition of events close together on the same Sensor, we can use `with events`.

The `with events` parameter functions very similarly to `with child` and `with descendant`: it declares a nested stateful rule.

For example, let's detect a scenario where `5` bad login attempts occur within `60` seconds.

```
event: WEL
op: is windows
with events:
  event: WEL
  op: is
  path: event/EVENT/System/EventID
  value: '4625'
  count: 5
  within: 60
```

The top-level rule filters down meaningful events to `WEL` ones sent from Windows sensors using the `is windows` operator, and then it declares a stateful rule inside `with events`. It uses `count` and `within` to declare a suitable timespan to evaluate matching events.

## Stateful Rules

Stateful rules — the rules declared within `with child`, `with descendant` or `with events` — have full range. They can do anything a normal rule might do, including declaring nested stateful rules or using `and`/`or` operators to write more complex rules.

Here's a stateful rule that uses `and` to detect a specific combination of child events:

```
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
with child:
  op: and
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: chrome.exe
      case sensitive: false
    - op: ends with
      event: NEW_DOCUMENT
      path: event/FILE_PATH
      value: .ps1
      case sensitive: false
```

The above example is looking for an `outlook.exe` process that spawns a `chrome.exe` process and drops a `.ps1` (powershell) file to disk. Like this:

```
outlook.exe
|--+--> chrome.exe
|--+--> .ps1 file
```

### Counting Events

Rules declared using `with child` or `with descendant` also have the ability to use `count` and `within` to help scope the events it will statefully match.

For example, a rule that matches on Outlook writing 5 new `.ps1` documents within 60 seconds:

```
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
with child:
  op: ends with
  event: NEW_DOCUMENT
  path: event/FILE_PATH
  value: .ps1
  case sensitive: false
  count: 5
  within: 60
```

### Choosing Event to Report

A reported detection will include a copy of the event that was detected. When writing detections that match multiple events, the default behavior will be to include a copy of the initial parent event.

In many cases it's more desirable to get the latest event in the chain instead. For this, there's a `report latest event: true` flag that can be set. Piggy-backing on the earlier example:

```
# Detection
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
report latest event: true
with child:
  op: and
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: chrome.exe
      case sensitive: false
    - op: ends with
      event: NEW_DOCUMENT
      path: event/FILE_PATH
      value: .ps1
      case sensitive: false

# Response
- action: report
  name: Outlook Spawning Chrome & Powershell
```

The event returned in the detection will be either the `chrome.exe` `NEW_PROCESS` event or the `.ps1` `NEW_DOCUMENT` event, whichever was last. Without `report latest event: true` being set, it would default to including the `outlook.exe` `NEW PROCESS` event.

### Flipping back to stateless

Since all operators under the `with child` and `with descentant` are operating in stateful mode (meaning all the nodes don’t have to match a single event, but can match over multiple events), sometimes you want a operator and the operators underneath to flip back to stateless mode where they must match a single event. You can achieve this by setting `is stateless: true` in the operator like:

```
# Detection
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
report latest event: true
with child:
  op: and
  is stateless: true
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: evil.exe
      case sensitive: false
    - op: contains
      event: COMMAND_LINE
      path: event/FILE_PATH
      value: something-else
      case sensitive: false
```

## Caveats

### Testing Stateful Rules

Stateful rules are forward-looking only and changing a rule will reset its state.

Practically speaking, this means that if you change a rule that detects `excel.exe -> cmd.exe`, `excel.exe` will need to be relaunched while the updated rule is running for it to then begin watching for `cmd.exe`.

### Using Events in Actions

Using `report` to report a detection works according to the [Choosing Event to Report](#choosing-event-to-report) section earlier. Other actions have a subtle difference: they will *always* observe the latest event in the chain.

Consider the `excel.exe -> cmd.exe` example. The `cmd.exe` event will be referenced inside the response action if using lookbacks (i.e. `<<routing/this>>`). If we wanted to end the `excel.exe` process (and its descendants), we would write a `task` that references the parent of the current event (`cmd.exe`):

```
- action: task
  command: deny_tree <<routing/parent>>
```

In LimaCharlie, a Stateful Rule tracks and remembers the state of past events to make decisions based on historical context. Unlike stateless rules, which evaluate events in isolation, stateful rules can detect patterns over time, such as multiple failed logins within an hour. This enables more complex and accurate detection, allowing users to trigger actions only when specific conditions are met across multiple events or timeframes.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Unit Tests

**Source:** https://docs.limacharlie.io/docs/unit-tests

# Test 1: CobaltStrike mojo pipe pattern
                      - - event:
                            EVENT:
                              EventData:
                                EventType: CreatePipe
                                Image: C:\Windows\system32\rundll32.exe
                                PipeName: \mojo.5688.8052.183894939787088877
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "1234"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:00:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "17"
                                _event_id: "17"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 2: CobaltStrike demoagent pipe
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\explorer.exe
                                PipeName: \demoagent_11
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "5678"
                                RuleName: "-"
                                User: DOMAIN\user
                                UtcTime: "2025-06-17 18:01:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 3: Regex pattern f4c3
                      - - event:
                            EVENT:
                              EventData:
                                EventType: CreatePipe
                                Image: C:\temp\malicious.exe
                                PipeName: \f4c3ab
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "9999"
                                RuleName: "-"
                                User: DOMAIN\user
                                UtcTime: "2025-06-17 18:02:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "17"
                                _event_id: "17"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 4: Winsock2 CatalogChangeListener pattern
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\system32\svchost.exe
                                PipeName: \Winsock2\CatalogChangeListener-123-0,
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "1111"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:03:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                    non_match:
                      # Test 1: SearchIndexer.exe using legitimate pipe NOT in detection patterns
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\WINDOWS\system32\SearchIndexer.exe
                                PipeName: \SearchFilterHost
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "11816"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-16 20:42:20.099"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: workstation01.example.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: workstation01
                      # Test 2: Different event channel (not Sysmon)
                      - - event:
                            EVENT:
                              EventData:
                                PipeName: \mojo.5688.8052.183894939787088877
                              System:
                                Channel: Security
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 3: Wrong event ID (not 17 or 18)
                      - - event:
                            EVENT:
                              EventData:
                                PipeName: \demoagent_11
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                EventID: "1"
                                _event_id: "1"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 4: Legitimate Windows pipe not in detection patterns
                      - - event:
                            EVENT:
                              EventData:
                                EventType: ConnectPipe
                                Image: C:\Windows\system32\lsass.exe
                                PipeName: \lsass
                                ProcessGuid: "{a6385ccd-7fc6-6850-1702-000000001700}"
                                ProcessId: "700"
                                RuleName: "-"
                                User: NT AUTHORITY\SYSTEM
                                UtcTime: "2025-06-17 18:05:00.000"
                              System:
                                Channel: Microsoft-Windows-Sysmon/Operational
                                Computer: testhost.domain.com
                                EventID: "18"
                                _event_id: "18"
                          routing:
                            event_type: WEL
                            hostname: testhost
                      # Test 5: Non-WEL event type
                      - - event:
                            PROCESS_ID: 1234
                            FILE_PATH: \Device\NamedPipe\mojo.test
                          routing:
                            event_type: NEW_NAMED_PIPE
                            hostname: testhost
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: "Detects the creation of a named pipe with a pattern found in CobaltStrike malleable C2 profiles"
```

---

# Getting Started

## What is LimaCharlie?

**Source:** https://docs.limacharlie.io/docs/what-is-limacharlie

# What is LimaCharlie?

LimaCharlie is the **SecOps Cloud Platform** - delivering security operations for the modern era.

LimaCharlie’s SecOps Cloud Platform provides you with comprehensive enterprise protection that brings together critical cybersecurity capabilities and eliminates integration challenges and security gaps for more effective protection against today’s threats.

The SecOps Cloud Platform offers a unified platform where you can build customized solutions effortlessly. With open APIs, centralized telemetry, and automated detection and response mechanisms, it’s time cybersecurity moves into the modern era.

Simplifying procurement, deployment and integration of best-of-breed cybersecurity solutions, the SecOps Cloud Platform delivers complete protection tailored to each organization’s specific needs, much in the same way IT Clouds have supported enterprises for years.

Our documentation can walk you through setting up your own Organization, deploying Sensors, writing detection and response rules, or outputting your data to any destination of your choosing. To dive in immediately, see our [Quickstart](/v2/docs/quickstart) guide.

Dig in, and build the security program you need and have always wanted.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Integrations

## 1Password

**Source:** https://docs.limacharlie.io/docs/1password

# 1Password Specific Docs: https://docs.limacharlie.io/docs/adapter-types-1password

sensor_type: "1password"
  1password:
    token: "hive://secret/your-1password-api-token-secret"
    endpoint: "business"  # or "enterprise", "ca", "eu"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_1PASSWORD"
      hostname: "1password-audit-adapter"
      platform: "json"
      sensor_seed_key: "1password-sensor-unique-name"
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

## MCP Server

**Source:** https://docs.limacharlie.io/docs/mcp-server

# MCP Server

Overview

 The Model Context Protocol (MCP) is a standardized protocol used by AI Agents to access and leverage external tools and resources.

 Note that MCP itself is still experimental and cutting edge.

 LimaCharlie offers an MCP server at <https://mcp.limacharlie.io> which enables AI agents to:

* **Query and analyze** historical telemetry from any sensor
* **Actively investigate** endpoints using the LimaCharlie Agent (EDR) in real-time
* **Take remediation actions** like isolating endpoints, killing processes, and managing tags
* **Generate content** using AI-powered tools for LCQL queries, D&R rules, playbooks, and detection summaries
* **Manage platform configuration** including rules, outputs, adapters, secrets, and more
* **Access threat intelligence** through IOC searches and MITRE ATT&CK mappings

 This opens up the entire LimaCharlie platform to AI agents, regardless of their implementation or location.

## Transport Modes

 The server supports two transport modes based on the PUBLIC\_MODE environment variable:

### STDIO Mode (PUBLIC\_MODE=false, default)

 Used for local MCP clients like Claude Desktop or Claude Code:

* Communication through stdin/stdout using JSON-RPC
* Uses LimaCharlie SDK's default authentication
* Reads credentials from environment variables or config files

### HTTP Mode (PUBLIC\_MODE=true)

 Used when deploying as a public service:

* Server runs as a stateless HTTP API with JSON responses
* Authentication via HTTP headers
* Supports multiple organizations concurrently
* Run with: `uvicorn server:app`

## Requirements & Authentication

### For HTTP Mode

 The server requires authentication headers:

 1. **Authorization header** in one of these formats:

* `Authorization: Bearer <jwt>` (OID must be in x-lc-oid header)
* `Authorization: Bearer <jwt>:<oid>` (combined format)
* `Authorization: Bearer <api_key>:<oid>` (API key with OID)

 2. **x-lc-oid header** (if not included in Authorization):

* `x-lc-oid: <organization_id>`

### For STDIO Mode

 Set environment variables:

* `LC_OID`: Your LimaCharlie Organization ID
* `LC_API_KEY`: Your LimaCharlie API key
* `GOOGLE_API_KEY`: For AI-powered generation features (optional)

## Capabilities

 The LimaCharlie MCP server exposes over 100 tools organized by category:

### Investigation & Telemetry

* **Process inspection**: `get_processes`, `get_process_modules`, `get_process_strings`, `yara_scan_process`
* **System information**: `get_os_version`, `get_users`, `get_services`, `get_drivers`, `get_autoruns, get_packages`
* **Network analysis**: `get_network_connections`, `is_online`, `get_online_sensors`
* **File operations**: `find_strings`, `yara_scan_file`, `yara_scan_directory`, `yara_scan_memory`
* **Registry access**: `get_registry_keys`
* **Historical data**: `get_historic_events`, `get_historic_detections`, `get_time_when_sensor_has_data`

### Threat Response & Remediation

* **Network isolation**: `isolate_network`, `rejoin_network`, `is_isolated`
* **Sensor management**: `add_tag`, `remove_tag`, `delete_sensor`
* **Reliable tasking**: `reliable_tasking`, `list_reliable_tasks`

### AI-Powered Generation (requires GOOGLE\_API\_KEY)

* **Query generation**: `generate_lcql_query` - Create LCQL queries from natural language
* **Rule creation**: `generate_dr_rule_detection`, `generate_dr_rule_respond` - Generate D&R rules
* **Automation**: `generate_python_playbook` - Create Python playbooks
* **Analysis**: `generate_detection_summary` - Summarize detection data
* **Sensor selection**: `generate_sensor_selector` - Generate sensor selectors

### Platform Configuration

* **Detection & Response**: `get_detection_rules`, `set_dr_general_rule`, `set_dr_managed_rule`, `delete_dr_general_rule`
* **False Positive Management**: `get_fp_rules`, `set_fp_rule`, `delete_fp_rule`
* **YARA Rules**: `list_yara_rules`, `set_yara_rule`, `validate_yara_rule`, `delete_yara_rule`
* **Outputs & Adapters**: `list_outputs`, `add_output`, `delete_output`, `list_external_adapters`, `set_external_adapter`
* **Extensions**: `list_extension_configs`, `set_extension_config`, `delete_extension_config`
* **Playbooks**: `list_playbooks`, `set_playbook`, `delete_playbook`
* **Secrets Management**: `list_secrets`, `set_secret`, `delete_secret`
* **Saved Queries**: `list_saved_queries`, `set_saved_query`, `run_saved_query`
* **Lookups**: `list_lookups`, `set_lookup`, `query_lookup`, `delete_lookup`

### Threat Intelligence

* **IOC Search**: `search_iocs`, `batch_search_iocs`
* **Host Search**: `search_hosts`
* **MITRE ATT&CK**: `get_mitre_report`

### Administrative

* **API Keys**: `list_api_keys`, `create_api_key`, `delete_api_key`
* **Installation Keys**: `list_installation_keys`, `create_installation_key`, `delete_installation_key`
* **Cloud Sensors**: `list_cloud_sensors`, `set_cloud_sensor`, `delete_cloud_sensor`
* **Organization Info**: `get_org_info`, `get_usage_stats`
* **Artifacts**: `list_artifacts`, `get_artifact`

### Schema & Documentation

* **Event Schemas**: `get_event_schema`, `get_event_schemas_batch`, `get_event_types_with_schemas`
* **Platform Support**: `get_platform_names`, `list_with_platform`, `get_event_types_with_schemas_for_platform`

## Advanced Features

### Large Result Handling

 The server automatically handles large responses by uploading them to Google Cloud Storage (if configured):

* Set `GCS_BUCKET_NAME` for the storage bucket
* Configure `GCS_TOKEN_THRESHOLD` (default: 1000 tokens)
* Results are returned as signed URLs valid for 24 hours

### LCQL Query Execution

 The `run_lcql_query` tool supports:

* Streaming results for real-time monitoring
* Flexible time windows and limits
* Output formatting options

## Examples

### Claude Desktop/Code Configuration (STDIO)

```
  {
    "mcpServers": {
      "limacharlie": {
        "command": "python3",
        "args": ["/path/to/server.py"],
        "env": {
          "LC_OID": "your-org-id",
          "LC_API_KEY": "your-api-key",
          "GOOGLE_API_KEY": "your-google-api-key"
        }
      }
    }
  }
```

### HTTP Service Usage

```bash
claude mcp add --transport http limacharlie https://mcp.limacharlie.io/mcp \
--header "Authorization: Bearer API_KEY:OID" \
--header "x-lc-oid: OID"
```

## Environment Variables

* `PUBLIC_MODE`: Set to true for HTTP mode, false for STDIO (default: false)
* `GOOGLE_API_KEY`: API key for AI-powered features
* `GCS_BUCKET_NAME`: Google Cloud Storage bucket for large results
* `GCS_SIGNER_SERVICE_ACCOUNT`: Service account for GCS URL signing
* `GCS_TOKEN_THRESHOLD`: Token count threshold for GCS upload (default: 1000)
* `GCS_URL_EXPIRY_HOURS`: Hours until GCS URLs expire (default: 24)
* `LC_OID`: Organization ID (STDIO mode only)
* `LC_API_KEY`: API key (STDIO mode only)

## Notes

* The server is stateless when running in HTTP mode
* HTTP mode uses JSON responses (not Server-Sent Events)
* No OAuth flow is used - authentication is via bearer tokens only
* If you encounter missing capabilities, contact <https://community.limacharlie.com> for quick additions

Table of contents

+ [Transport Modes](#-transport-modes)
+ [Requirements &amp; Authentication](#-requirements-amp-authentication)
+ [Capabilities](#-capabilities)
+ [Advanced Features](#-advanced-features)
+ [Examples](#-examples)
+ [Environment Variables](#-environment-variables)
+ [Notes](#-notes)

---

# Outputs

## Azure Event Hub

**Source:** https://docs.limacharlie.io/docs/outputs-destinations-azure-event-hub

# Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

* `connection_string`: the connection string provided by Azure.

Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the "Connection String" provided by Azure.

Example:

```
connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
```

---

## Tines

**Source:** https://docs.limacharlie.io/docs/output-destinations-tines

# Tines

Output events and detections to [Tines](https://tines.io/).

* `dest_host`: the Tines-provided `Webhook URL`

Example:

```
dest_host: https://something.tines.com/webhook/de2314c5f6246d17e82bf7b5742c9eaf/2d2dbcd2ab3845e9592d33c0526bc123
```

Detections or events sent to Tines via an output can be used to subsequently create cases, or take other actions within Tines.

---

# Platform

## LimaCharlie SDK & CLI

**Source:** https://docs.limacharlie.io/docs/limacharlie-sdk

# LimaCharlie SDK & CLI

## Go

The Go library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

* Repo - <https://github.com/refractionPOINT/go-limacharlie>

### Getting Started

#### Authentication

You can use Client Options to declare your client/org, or you can use environment variables.

**Using Environment Variables:**

* `LC_OID`: Organization ID
* `LC_API_KEY`: your LC API KEY
* `LC_UID`: optional, your user ID

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)
    fmt.Printf("Hello, this is %s", org.GetOID())
}
```

**Using Client Options:**

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    clientOptions = limacharlie.ClientOptions{
        OID: "MY_OID",
        APIKey: "MY_API_KEY",
        UID: "MY_UID",
    }
    org, _ := limacharlie.NewOrganizationFromClientOptions(clientOptions, nil)
    fmt.Printf("Hello, this is %s", org.GetOID())
}
```

### SDK

#### Examples

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)

    // List all sensors
    sensors, err := org.ListSensors()
    if err != nil {
        fmt.Println(err)
    }
    for sid, sensor := range sensors {
        fmt.Printf("%s - %s", sid, sensor.Hostname)
    }

    // List D&R rules from Hive
    hiveClient := limacharlie.NewHiveClient(org)
    rules, _ := hiveClient.List(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey:  org.GetOID(),
    })
    for rule_name, _ := range rules {
        fmt.Println(rule_name)
    }

    // Add D&R rule to Hive
    enabled := true
    case_sensitive := false
    if _, err := hiveClient.Add(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "test_rule_name",
        Enabled:      &enabled,
        Data: limacharlie.Dict{
            "detect": limacharlie.Dict{
                "event":            "NEW_PROCESS",
                "op":               "is",
                "path":             "event/COMMAND_LINE",
                "value":            "whoami",
                "case sensitive":   &case_sensitive,
            },
            "respond": []limacharlie.Dict{{
                "action": "report",
                "name":   "whoami detection",
            }},
        },
    }); err != nil {
        fmt.Println(err)
    }

    // List extensions
    extensions, _ := org.Extensions()
    for _, extension_name := range extensions {
        fmt.Println(extension_name)
    }

    // Subscribe to extension
    subscription_request := org.SubscribeToExtension("binlib")
    if subscription_request != nil {
        fmt.Println(subscription_request)
    }

    // List payloads
    payloads, _ := org.Payloads()
    for payload, _ := range payloads {
        fmt.Println(payload)
    }

    // List installation keys
    installation_keys, _ := org.InstallationKeys()
    for _, key := range installation_keys {
        fmt.Println(key.Description)
    }

    // Create installation key
    key_request, _ := org.AddInstallationKey(InstallationKey{
		Description: "my-test-key",
## Python

The Python library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

* Repo - <https://github.com/refractionpoint/python-limacharlie>

### Getting Started

#### Installing

##### PyPi (pip)

The library and the CLI is available as a Python package on PyPi (<https://pypi.org/project/limacharlie/>). It can be installed using pip as shown below.

```
pip install limacharlie
```

##### Docker Image

In addition to the PyPi distribution we also offer a pre-built Docker image on DockerHub (<https://hub.docker.com/r/refractionpoint/limacharlie>).

```
docker run refractionpoint/limacharlie:latest whoami

# Using a specific version (Docker image tag matches the library version)
docker run refractionpoint/limacharlie:4.9.13 whoami

# If you already have a credential file locally, you can mount it inside the Docker container
docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami
```

#### Credentials

Authenticating to use the SDK / CLI can be done in a few ways.

**Option 1 - Logging In**
 The simplest is to login to an Organization using an [API key](https://doc.limacharlie.io/docs/documentation/docs/api_keys.md).

Use `limacharlie login` to store credentials locally. You will need an `OID` (Organization ID) and an API key, and (optionally) a `UID` (User ID), all of which you can get from the Access Management --> REST API section of the web interface.

The login interface supports named environments, or a default one used when no environment is selected.

To list available environments:

```
limacharlie use
```

Setting a given environment in the current shell session can be done like this:

```
limacharlie use my-dev-org
```

You can also specify a `UID` (User ID) during login to use a *user* API key representing
 the total set of permissions that user has (see User Profile in the web interface).

**Option 2 - Environment Variables**
 You can use the `LC_OID` and `LC_API_KEY` and `LC_UID` environment variables to replace the values used logging in. The environment variables will be used if no other credentials are specified.

### SDK

The root of the functionality in the SDK is from the `Manager` object. It holds the credentials and is tied to a specific LimaCharlie Organization.

You can authenticate the `Manager` using an `oid` (and optionally a `uid`), along with either a `secret_api_key` or `jwt` directly. Alternatively you can just use an environment name (as specified in `limacharlie login`). If no creds are provided, the `Manager` will try to use the default environment and credentials.

#### Importing

```
import limacharlie

YARA_SIG = 'https://raw.githubusercontent.com/Yara-Rules/rules/master/Malicious_Documents/Maldoc_PDF.yar'

# Create an instance of the SDK.
mgr = limacharlie.Manager()

# Get a list of all the sensors in the current Organization.
all_sensors = mgr.sensors()

# Select the first sensor in the list.
sensor = all_sensors[0]

# Tag this sensor with a tag for 10 minutes.
sensor.tag( 'suspicious', ttl = 60 * 10 )

# Send a task to the sensor (unidirectionally, not expecting a response).
sensor.task( 'os_processes' )

# Send a yara scan to that sensor for processes "evil.exe".
sensor.task( 'yara_scan -e *evil.exe ' + YARA_SIG )
```

#### Use of gevent

Note that the SDK uses the `gevent` package which sometimes has issues with other
 packages that operate at a low level in python. For example, Jupyter notebooks
 may see freezing on importing `limacharlie` and require a tweak to load:

```
{
 "display_name": "IPython 2 w/gevent",
 "language": "python",
 "argv": [
  "python",
  "-c", "from gevent.monkey import patch_all; patch_all(thread=False); from ipykernel.kernelapp import main; main()",
  "-f",
  "{connection_file}"
 ]
}
```

### Components

#### Manager

This is a the general component that provides access to the managing functions of the API like querying sensors online, creating and removing Outputs etc.

#### Firehose

The `Firehose` is a simple object that listens on a port for LimaCharlie.io data. Under the hood it creates a Syslog Output on limacharlie.io pointing to itself and removes it on shutdown. Data from limacharlie.io is added to `firehose.queue` (a `gevent Queue`) as it is received.

It is a basic building block of automation for limacharlie.io.

#### Spout

Much like the `Firehose`, the Spout receives data from LimaCharlie.io, the difference
 is that the `Spout` does not require opening a local port to listen actively on. Instead
 it leverages `stream.limacharlie.io` to receive the data stream over HTTPS.

A `Spout` is automatically created when you instantiate a `Manager` with the
`is_interactive = True` and `inv_id = XXXX` arguments in order to provide real-time
 feedback from tasking sensors.

#### Sensor

This is the object returned by `manager.sensor( sensor_id )`.

#### Artifacts

The `Artifacts` is a helpful class to upload [artifacts](/v2/docs/artifacts) to LimaCharlie without going through a sensor.

#### Extensions

The `Extensions` can be used to subscribe to and manage extensions within your org.

```
import limacharlie
from limacharlie import Extension

mgr = limacharlie.Manager()
ext = Extension(mgr)
ext.subscribe('binlib')
```

#### Payloads

The `Payloads` can be used to manage various executable [payloads](/v2/docs/payloads) accessible to sensors.

#### Replay

The `Replay` object allows you to interact with [Replay](/v2/docs/replay) jobs managed by LimaCharlie. These allow you to re-run [D&R Rules](/v2/docs/detection-and-response) on historical data.

Sample command line to query one sensor:

```
limacharlie-replay --sid 9cbed57a-6d6a-4af0-b881-803a99b177d9 --start 1556568500 --end 1556568600 --rule-content ./test_rule.txt
```

Sample command line to query an entire organization:

```
limacharlie-replay --entire-org --start 1555359000 --end 1556568600 --rule-name my-rule-name
```

#### Search

The `Search` object allows you to perform an IOC search across multiple organizations.

#### SpotCheck

The `SpotCheck` object (sometimes called Fleet Check) allows you to manage an active (query sensors directly as opposed to searching on indexed historical data) search for various IOCs on an organization's sensors.

#### Configs

The `Configs` is used to retrieve an organization's configuration as a config file, or apply
 an existing config file to an organization. This is the concept of Infrastructure as Code.

#### Webhook

The `Webhook` object demonstrates handling [webhooks emitted by the LimaCharlie cloud](/v2/docs/tutorial-creating-a-webhook-adapter), including verifying the shared-secret signing of the webhooks.

### Examples:

### Command Line Interface

Many of the objects available as part of the LimaCharlie Python SDK also support various command line interfaces.

#### Query

[LimaCharlie Query Language (LCQL)](/v2/docs/lcql) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie.

```
limacharlie query --help
```

#### ARLs

[Authenticated Resource Locators (ARLs)](/v2/docs/reference-authentication-resource-locator) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

ARLs can be used in the [YARA manager](/v2/docs/ext-yara-manager) to import rules from GitHub repositories and other locations.

Testing an ARL before applying it somewhere can be helpful to shake out access or authentication errors beforehand. You can test an ARL and see what files are fetched, and their contents, by running the following command:

```
limacharlie get-arl -a [github,Yara-Rules/rules/email]
```

#### Firehose

Listens on interface `1.2.3.4`, port `9424` for incoming connections from LimaCharlie.io.
 Receives only events from hosts tagged with `fh_test`.

```
python -m limacharlie.Firehose 1.2.3.4:9424 event -n firehose_test -t fh_test --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

#### Spout

Behaves similarly to the Firehose, but instead of listening from an internet accessible port, it connects to the `stream.limacharlie.io` service to stream the output over HTTPS. This means the Spout allows you to get ad-hoc output like the Firehose, but it also works through NATs and proxies.

It is MUCH more convenient for short term ad-hoc outputs, but it is less reliable than a Firehose for very large amounts of data.

```
python -m limacharlie.Spout event --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

#### Configs

The `fetch` command will get a list of the Detection & Response rules in your
 organization and will write them to the config file specified or the default
 config file `lc_conf.yaml` in YAML format.

```
limacharlie configs fetch --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca`
```

Then `push` can upload the rules specified in the config file (or the default one)
 to your organization. The optional `--force` argument will remove active rules not
 found in the config file. The `--dry-run` simulates the sync and displays the changes
 that would occur.

The `--config` allows you to specify an alternate config file and the `--api-key` allows
 you to specify a file on disk where the API should be read from (otherwise, of if `-` is
 specified as a file, the API Key is read from STDIN).

```
limacharlie configs push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca --config /path/to/template.yaml --all --ignore-inaccessible
```

All these capabilities are also supported directly by the `limacharlie.Configs` object.

The Sync functionality currently supports all common useful configurations. The `--no-rules` and `--no-outputs` flags can be used to ignore one or the other in config files and sync. Additional flags are also supported, see `limacharlie configs --help`.

To understand better the config format, do a `fetch` from your organization. Notice the use of the `include`
 statement. Using this statement you can combine multiple config files together, making
 it ideal for the management of complex rule sets and their versioning.

#### Spot Checks

Used to perform Organization-wide checks for specific indicators of compromise. Available as a custom API `SpotCheck` object or as a module from the command line. Supports many types of IoCs like file names, directories, registry keys, file hashes and YARA signatures.

```
python -m limacharlie.SpotCheck --no-macos --no-linux --tags vip --file c:\\evil.exe`
```

For detailed usage:

```
python -m limacharlie.SpotCheck --help
```

#### Search

Shortcut utility to perform IOC searches across all locally configured organizations.

```
limacharlie search --help
```

#### Extensions

Shortcut utility to manage extensions.

```
limacharlie extension --help
```

#### Artifact Upload

Shortcut utility to upload and retrieve [Artifacts](/v2/docs/artifacts) within LimaCharlie with just the CLI (no agent).

```
limacharlie artifacts --help
```

#### Artifact Download

Shortcut utility to download [Artifact Collection](/v2/docs/artifacts) in LimaCharlie locally.

```
limacharlie artifacts get_original --help
```

#### Replay

Shortcut utility to perform [Replay](/v2/docs/replay) jobs from the CLI.

```
limacharlie replay --help
```

#### Detection & Response

Shortcut utility to manage Detection and Response rules over the CLI.

```
limacharlie dr --help
```

#### Events & Detections

Print out to STDOUT events or detections matching the parameter.

```
limacharlie events --help
limacharlie detections --help
```

#### List Sensors

Print out all basic sensor information for all sensors matching the [selector](/v2/docs/reference-sensor-selector-expressions).

```
limacharlie sensors --selector 'plat == windows'
```

#### Invite Users

Invite single or multiple users to LimaCharlie. Invited users will be sent an email to confirm their address, enable the account and create a new password.

Keep in mind that this actions operates in the user context which means you need to use user scoped API key. For more information on how to obtain one, see <https://docs.limacharlie.io/apidocs/introduction#getting-a-jwt>

Invite a single user:

```
limacharlie users invite --email=user1@example.com
```

Invite multiple users:

```
limacharlie users invite --email=user1@example.com,user2@example.com,user3@example.com
```

Invite multiple users from new line delimited entries in a text file:

```
cat users_to_invite.txt
user1@example.com
user2@example.com
user3@example.com
```

```
limacharlie users invite --file=users_to_invite.txt
```

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Command-line Interface

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

# Query

## Query Console

**Source:** https://docs.limacharlie.io/docs/query-console

# Query Console

The **LimaCharlie Query Console** is a powerful feature within the LimaCharlie web application that enables users to interactively execute queries across their collected telemetry data using the [**LimaCharlie Query Language (LCQL)**](/v2/docs/lcql). The Query Console provides a streamlined interface to search, filter, and analyze events from multiple sources, such as EDR Sensors or telemetry from other integrated platforms. This allows security teams to easily perform targeted hunts, incident investigations, and data analysis across their fleet of devices.

Through the Query Console, users can write, execute, and save LCQL queries to explore various event types, such as network activity, process execution, and system changes. Queries can be customized for specific environments and saved for future use, offering a flexible solution for recurring investigations. Additionally, queries can be made programmatically via the REST API, allowing for automation and integration with other security workflows or platforms. Users can also leverage predefined examples or create unique queries to share with the LimaCharlie community, enhancing collaborative threat hunting and data exploration. The Query Console helps organizations gain deeper insights into their telemetry, simplifying large-scale data searches and empowering proactive security operations.

For examples and inspiration, see [LCQL Examples](/v2/docs/lcql-examples).

Endpoint Detection & Response

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Reference

## Reference: EDR Events

**Source:** https://docs.limacharlie.io/docs/reference-edr-events

# Reference: EDR Events

## Overview

This page provides a detailed overview of all events generated by the LimaCharlie Endpoint Agent. Each event type represents a specific system activity, from process creation to network connections and file modifications. Events serve as key components in detection, response, and monitoring, enabling security teams to track, analyze, and take action on endpoint behavior. Use this guide to understand the purpose and structure of each event for effective threat detection and investigation.

Generally, event types ending with `*_REP` are emitted in response to a command being issued to the endpoint agent.

## EDR Events by Supported OS

These are the events emitted by the endpoint agent for each supported operating system. Below the table, you can find descriptions of each event type.

| EDR Event Type | macOS | Windows | Linux | Chrome | Edge |
| --- | --- | --- | --- | --- | --- |
| [AUTORUN\_CHANGE](/v2/docs/reference-edr-events#autorunchange) |  | ☑️ |  |  |  |
| [CLOUD\_NOTIFICATION](/v2/docs/reference-edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [CODE\_IDENTITY](/v2/docs/reference-edr-events#codeidentity) | ☑️ | ☑️ | ☑️ |  |  |
| [CONNECTED](/v2/docs/reference-edr-events#connected) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [DATA\_DROPPED](/v2/docs/reference-edr-events#datadropped) | ☑️ | ☑️ | ☑️ |  |  |
| [DEBUG\_DATA\_REP](/v2/docs/reference-edr-events#getdebugdata) |  | ☑️ |  |  |  |
| [DELETED\_SENSOR](/v2/docs/reference-edr-events#deletedsensor) | ☑️ | ☑️ | ☑️ |  |  |
| [DIR\_FINDHASH\_REP](/v2/docs/reference-edr-events#dirfindhash) | ☑️ | ☑️ | ☑️ |  |  |
| [DIR\_LIST\_REP](/v2/docs/reference-edr-events#dirlist) | ☑️ | ☑️ | ☑️ |  |  |
| [DISCONNECTED](/v2/docs/reference-edr-events#disconnected) |  | ☑️ |  |  |  |
| [DNS\_REQUEST](/v2/docs/reference-edr-events#dnsrequest) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [DRIVER\_CHANGE](/v2/docs/reference-edr-events#driverchange) |  | ☑️ |  |  |  |
| [EXEC\_OOB](/v2/docs/reference-edr-events#execoob) | ☑️ |  | ☑️ |  |  |
| [EXISTING\_PROCESS](/v2/docs/reference-edr-events#existingprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [EXPORT\_COMPLETE](/v2/docs/reference-edr-events#exportcomplete) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_ADD](/v2/docs/reference-edr-events#fimadd) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_DEL](/v2/docs/reference-edr-events#fimdel) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_HIT](/v2/docs/reference-edr-events#fimhit) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_CREATE](/v2/docs/reference-edr-events#filecreate) | ☑️ | ☑️ |  |  |  |
| [FILE\_DEL\_REP](/v2/docs/reference-edr-events#filedel) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_DELETE](/v2/docs/reference-edr-events#filedelete) | ☑️ | ☑️ |  |  |  |
| [FILE\_GET\_REP](/v2/docs/reference-edr-events#fileget) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_HASH\_REP](/v2/docs/reference-edr-events#filehash) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_INFO\_REP](/v2/docs/reference-edr-events#fileinfo) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_MODIFIED](/v2/docs/reference-edr-events#filemodified) | ☑️ | ☑️ |  |  |  |
| [FILE\_MOV\_REP](/v2/docs/reference-edr-events#filemov) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_TYPE\_ACCESSED](/v2/docs/reference-edr-events#filetypeaccessed) | ☑️ | ☑️ |  |  |  |
| [GET\_DOCUMENT\_REP](/v2/docs/reference-edr-events#doccacheget) | ☑️ | ☑️ |  |  |  |
| [GET\_EXFIL\_EVENT\_REP](/v2/docs/reference-edr-events#exfilget) | ☑️ | ☑️ | ☑️ |  |  |
| [HIDDEN\_MODULE\_DETECTED](/v2/docs/reference-edr-events#hiddenmoduledetected) |  | ☑️ |  |  |  |
| [HISTORY\_DUMP\_REP](/v2/docs/reference-edr-events#historydump) | ☑️ | ☑️ | ☑️ |  |  |
| [HTTP\_REQUEST](/v2/docs/reference-edr-events#httprequest) |  |  |  | ☑️ | ☑️ |
| [HTTP\_REQUEST\_HEADERS](/v2/docs/reference-edr-events#httprequestheaders) |  |  |  | ☑️ |  |
| [HTTP\_RESPONSE\_HEADERS](/v2/docs/reference-edr-events#httpresponseheaders) |  |  |  | ☑️ |  |
| [INGEST](/v2/docs/reference-edr-events#ingest) | ☑️ | ☑️ | ☑️ |  |  |
| [LOG\_GET\_REP](/v2/docs/reference-edr-events#logget) |  |  |  |  |  |
| [LOG\_LIST\_REP](/v2/docs/reference-edr-events#loglist) |  |  |  |  |  |
| [MEM\_FIND\_HANDLES\_REP](/v2/docs/reference-edr-events#memfindhandle) |  | ☑️ |  |  |  |
| [MEM\_FIND\_STRING\_REP](/v2/docs/reference-edr-events#memfindstring) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_HANDLES\_REP](/v2/docs/reference-edr-events#memhandles) |  | ☑️ |  |  |  |
| [MEM\_MAP\_REP](/v2/docs/reference-edr-events#memmap) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_READ\_REP](/v2/docs/reference-edr-events#memread) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_STRINGS\_REP](/v2/docs/reference-edr-events#memstrings) | ☑️ | ☑️ | ☑️ |  |  |
| [MODULE\_LOAD](/v2/docs/reference-edr-events#moduleload) |  | ☑️ | ☑️ |  |  |
| [MODULE\_MEM\_DISK\_MISMATCH](/v2/docs/reference-edr-events#modulememdiskmismatch) | ☑️ | ☑️ | ☑️ |  |  |
| [NETSTAT\_REP](/v2/docs/reference-edr-events#netstat) | ☑️ | ☑️ | ☑️ |  |  |
| [NETWORK\_CONNECTIONS](/v2/docs/reference-edr-events#networkconnections) | ☑️ | ☑️ | ☑️ |  |  |
| [NETWORK\_SUMMARY](/v2/docs/reference-edr-events#networksummary) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_DOCUMENT](/v2/docs/reference-edr-events#newdocument) | ☑️ | ☑️ |  |  |  |
| [NEW\_NAMED\_PIPE](/v2/docs/reference-edr-events#newnamedpipe) |  | ☑️ |  |  |  |
| [NEW\_PROCESS](/v2/docs/reference-edr-events#newprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_REMOTE\_THREAD](/v2/docs/reference-edr-events#newremotethread) |  | ☑️ |  |  |  |
| [NEW\_TCP4\_CONNECTION](/v2/docs/reference-edr-events#newtcp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_TCP6\_CONNECTION](/v2/docs/reference-edr-events#newtcp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_UDP4\_CONNECTION](/v2/docs/reference-edr-events#newudp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_UDP6\_CONNECTION](/v2/docs/reference-edr-events#newudp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [OPEN\_NAMED\_PIPE](/v2/docs/reference-edr-events#opennamedpipe) |  | ☑️ |  |  |  |
| [OS\_AUTORUNS\_REP](/v2/docs/reference-edr-events#osautoruns) | ☑️ | ☑️ |  |  |  |
| [OS\_DRIVERS\_REP](/v2/docs/reference-edr-events#osdrivers) |  | ☑️ |  |  |  |
| [OS\_KILL\_PROCESS\_REP](/v2/docs/reference-edr-events#oskillprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_PACKAGES\_REP](/v2/docs/reference-edr-events#ospackages) |  | ☑️ |  |  |  |
| [OS\_PROCESSES\_REP](/v2/docs/reference-edr-events#osprocesses) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_RESUME\_REP](/v2/docs/reference-edr-events#osresume) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_SERVICES\_REP](/v2/docs/reference-edr-events#osservices) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_SUSPEND\_REP](/v2/docs/reference-edr-events#ossuspend) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_USERS\_REP](/v2/docs/reference-edr-events#osusers) |  | ☑️ |  |  |  |
| [OS\_VERSION\_REP](/v2/docs/reference-edr-events#osversion) | ☑️ | ☑️ | ☑️ |  |  |
| [PCAP\_LIST\_INTERFACES\_REP](/v2/docs/reference-edr-events#pcapifaces) |  |  | ☑️ |  |  |
| [PROCESS\_ENVIRONMENT](/v2/docs/reference-edr-events#processenvironment) |  | ☑️ | ☑️ |  |  |
| [RECEIPT](/v2/docs/reference-edr-events#receipt) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [REGISTRY\_CREATE](/v2/docs/reference-edr-events#registrycreate) |  | ☑️ |  |  |  |
| [REGISTRY\_DELETE](/v2/docs/reference-edr-events#registrydelete) |  | ☑️ |  |  |  |
| [REGISTRY\_LIST\_REP](/v2/docs/reference-edr-events#reglist) |  | ☑️ |  |  |  |
| [REGISTRY\_WRITE](/v2/docs/reference-edr-events#registrywrite) |  | ☑️ |  |  |  |
| [REJOIN\_NETWORK](/v2/docs/reference-edr-events#rejoinnetwork) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [REMOTE\_PROCESS\_HANDLE](/v2/docs/reference-edr-events#remoteprocesshandle) |  | ☑️ |  |  |  |
| [SEGREGATE\_NETWORK](/v2/docs/reference-edr-events#segregatenetwork) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [SENSITIVE\_PROCESS\_ACCESS](/v2/docs/reference-edr-events#sensitiveprocessaccess) |  | ☑️ |  |  |  |
| [SERVICE\_CHANGE](/v2/docs/reference-edr-events#servicechange) | ☑️ | ☑️ | ☑️ |  |  |
| [SHUTTING\_DOWN](/v2/docs/reference-edr-events#shuttingdown) | ☑️ | ☑️ | ☑️ |  |  |
| [SSH\_LOGIN](/v2/docs/reference-edr-events#sshlogin) | ☑️ |  |  |  |  |
| [SSH\_LOGOUT](/v2/docs/reference-edr-events#sshlogout) | ☑️ |  |  |  |  |
| [STARTING\_UP](/v2/docs/reference-edr-events#startingup) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_PROCESS](/v2/docs/reference-edr-events#terminateprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_TCP4\_CONNECTION](/v2/docs/reference-edr-events#terminatetcp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_TCP6\_CONNECTION](/v2/docs/reference-edr-events#terminatetcp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_UDP4\_CONNECTION](/v2/docs/reference-edr-events#terminateudp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_UDP6\_CONNECTION](/v2/docs/reference-edr-events#terminateudp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [THREAD\_INJECTION](/v2/docs/reference-edr-events#threadinjection) |  | ☑️ |  |  |  |
| [USER\_LOGIN](/v2/docs/reference-edr-events#userlogin) | ☑️ |  |  |  |  |
| [USER\_LOGOUT](/v2/docs/reference-edr-events#userlogout) | ☑️ |  |  |  |  |
| [USER\_OBSERVED](/v2/docs/reference-edr-events#userobserved) | ☑️ | ☑️ | ☑️ |  |  |
| [VOLUME\_MOUNT](/v2/docs/reference-edr-events#volumemount) | ☑️ | ☑️ |  |  |  |
| [VOLUME\_UNMOUNT](/v2/docs/reference-edr-events#volumeunmount) | ☑️ | ☑️ |  |  |  |
| [WEL](/v2/docs/reference-edr-events#wel) |  | ☑️ |  |  |  |
| [YARA\_DETECTION](/v2/docs/reference-edr-events#yaradetection) | ☑️ | ☑️ | ☑️ |  |  |

## Event Descriptions

### AUTORUN\_CHANGE

Generated when an Autorun is changed.

**Platforms:**

```
{
  "REGISTRY_KEY": "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
  "TIMESTAMP": 1627497894000
}
```

### CLOUD\_NOTIFICATION

This event is a receipt from the agent that it has received the task sent to it, and includes high-level errors (if any).

**Platforms:**

```
{
  "NOTIFICATION_ID": "ADD_EXFIL_EVENT_REQ",
  "NOTIFICATION": {
    "INVESTIGATION_ID": "digger-4afdeb2b-a0d8-4a37-83b5-48996117998e"
  },
  "HCP_IDENT": {
    "HCP_ORG_ID": "c82e5c17d5194ef5a4acc454a95d31db",
    "HCP_SENSOR_ID": "8fc370e6699a49858e75c1316b725570",
    "HCP_INSTALLER_ID": "00000000000000000000000000000000",
    "HCP_ARCHITECTURE": 0,
    "HCP_PLATFORM": 0
  },
  "EXPIRY": 0
}
```

### CODE\_IDENTITY

Unique combinations of file hash and file path. This event is emitted the first time the combination is seen, typically when the binary is executed or loaded. Therefore it's a great event to look for hashes without being overwhelmed by process execution or module loads.

ONGOING\_IDENTITY

The `ONGOING_IDENTITY` event emits code signature information even if not newly seen, however this data can become duplicative and verbose.

**Platforms:**

```
{
  "MEMORY_SIZE": 0,
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\B1B207E5-300E-434F-B4FE-A4816E6551BE\\dismhost.exe",
  "TIMESTAMP": 1456285265,
  "SIGNATURE": {
    "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Code Signing PCA",
    "CERT_CHAIN_STATUS": 124,
    "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\B1B207E5-300E-434F-B4FE-A4816E6551BE\\dismhost.exe",
    "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, OU=MOPR, CN=Microsoft Corporation"
  },
  "HASH": "4ab4024eb555b2e4c54d378a846a847bd02f66ac54849bbce5a1c8b787f1d26c"
}
```

### CONNECTED

This event is generated when a Sensor connects to the cloud.

**Platforms:**

```
{
    "HOST_NAME" : "demo-win-2016",
    "IS_SEGREGATED" : 0,
    "KERNEL_ACQ_AVAILABLE" : 1,
    "MAC_ADDRESS" : "42-01-0A-80-00-02"
}
```

### DEBUG\_DATA\_REP

Response from a `get_debug_data` request.

**Platforms:**

### DIR\_FINDHASH\_REP

Response event for the `dir_find_hash` sensor command.

**Platforms:**

**Sample Event:**

```
{
    "DIRECTORY_LIST": [
        {
            "HASH": "f11dda931637a1a1bc614fc2f320326b24336c5155679aa062acae7c79f33d67",
            "ACCESS_TIME": 1535994794247,
            "FILE_SIZE": 113664,
            "CREATION_TIME": 1467173189067,
            "MODIFICATION_TIME": 1467173190171,
            "FILE_NAME": "MALWARE_DEMO_WINDOWS_1.exe",
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\MALWARE_DEMO_WINDOWS_1.exe"
        },
        {
            "HASH": "e37726feee8e72f3ab006e023cb9d6fa1a4087274b47217d2462325fa8008515",
            "ACCESS_TIME": 1535989041078,
            "FILE_SIZE": 1016320,
            "CREATION_TIME": 1522507344821,
            "MODIFICATION_TIME": 1522507355732,
            "FILE_NAME": "lc_win_64.exe",
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\lc_win_64.exe"
        }
    ],
    "HASH": [
        "f11dda931637a1a1bc614fc2f320326b24336c5155679aa062acae7c79f33d67",
        "e37726feee8e72f3ab006e023cb9d6fa1a4087274b47217d2462325fa8008515"
    ],
    "FILE_PATH": "*.exe",
    "DIRECTORY_LIST_DEPTH": 0,
    "DIRECTORY_PATH": "c:\\users\\dev\\desktop\\"
}
```

### DIR\_LIST\_REP

Response event for the `dir_list` sensor command. Includes Alternate Data Streams on Windows.

**Platforms:**

**Sample Event:**

```
{
    "DIRECTORY_LIST": [
        {
            "FILE_NAME": "vssdk_full.exe",
            "CREATION_TIME": 1553437930012,
            "MODIFICATION_TIME": 1553437937000,
            "STREAMS": [
                {
                    "FILE_NAME": "::$DATA",
                    "SIZE": 13782032
                }
            ],
            "ACCESS_TIME": 1567868284440,
            "FILE_SIZE": 13782032,
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\vssdk_full.exe"
        },
        {
            "FILE_NAME": "UniversalLog.txt",
            "CREATION_TIME": 1553028205525,
            "MODIFICATION_TIME": 1553028206289,
            "STREAMS": [
                {
                    "FILE_NAME": "::$DATA",
                    "SIZE": 125
                },
                {
                    "FILE_NAME": ":Zone.Identifier:$DATA",
                    "SIZE": 377
                }
            ],
            "ACCESS_TIME": 1567868284158,
            "FILE_SIZE": 125,
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\UniversalLog.txt"
        }
    ]
}
```

### DISCONNECTED

This event is generated when a Sensor disconnects from the cloud.

**Platforms:**

```
{
  "DISCONNECTED": {},
  "ts": 1455674775
}
```

### DNS\_REQUEST

Generated from DNS responses and therefore includes both the requested domain and the response from the server. If the server responds with multiple responses (as allowed by the DNS protocol) the N answers will become N DNS\_REQUEST events, so you can always assume one DNS\_REQUEST event means one answer.

**Platforms:**

```
{
  "DNS_TYPE": 1,
  "TIMESTAMP": 1456285240,
  "DNS_FLAGS": 0,
  "DOMAIN_NAME": "time.windows.com"
}
```

### DRIVER\_CHANGE

Generated when a driver is changed.

**Platforms:**

```
{
  "PROCESS_ID": 0,
  "SVC_DISPLAY_NAME": "HbsAcq",
  "SVC_NAME": "HbsAcq",
  "SVC_STATE": 1,
  "SVC_TYPE": 1,
  "TIMESTAMP": 1517377895873
}
```

### EXISTING\_PROCESS

This event is similar to the NEW\_PROCESS event.  It gets emitted when a process existed prior to the LimaCharlie sensor loading.

**Platforms:**

### FILE\_CREATE

Generated when a file is created.

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Microsoft\\Windows\\WebCache\\V01tmp.log",
  "TIMESTAMP": 1468335271948
}
```

### FILE\_DEL\_REP

Response event for the `file_del` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_PATH": "C:\\test\\test.txt"
}
```

### FILE\_DELETE

Generated when a file is deleted.

> Be Aware:
>
> When adding this event to an event collection rule, you will be monitoring system-wide. This could result in a large number of events.

> Best Practices:
>
> * Utilize this selectively (ex. deploy on only suspect systems)
> * Use Exfil watch rules to specify paths that are of high interest
> * Consider using File Integrity Monitoring (FIM)
> * Look for this on an ad-hoc basis from the Sensor Console. ex.
>
>   ```
>   history_dump -e FILE_DELETE
>   ```

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\EBA4E4F0-3020-459E-9E34-D5336E244F05\\api-ms-win-core-processthreads-l1-1-2.dll",
  "TIMESTAMP": 1468335611906
}
```

### FILE\_GET\_REP

Response event for the `file_get` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_CONTENT": "$BASE64_ENCODED_FILE_CONTENTS",
  "FILE_PATH": "C:\\windows\\system32\\svchost.exe",
  "FILE_SIZE": 78880
}
```

### FILE\_HASH\_REP

Response event for the `file_hash` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_IS_SIGNED": 1,
  "FILE_PATH": "C:\\Windows\\System32\\svchost.exe",
  "HASH": "31780ff2aaf7bc71f755ba0e4fef1d61b060d1d2741eafb33cbab44d889595a0",
  "SIGNATURE": {
    "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Production PCA 2011",
    "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Publisher",
    "FILE_CERT_IS_VERIFIED_LOCAL": 1,
    "FILE_IS_SIGNED": 1,
    "FILE_PATH": "C:\\Windows\\System32\\svchost.exe"
  }
}
```

### FILE\_INFO\_REP

Response event for the `file_info` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "ACCESS_TIME": 1686685723546,
  "ATTRIBUTES": 0,
  "CREATION_TIME": 1686685723546,
  "FILE_IS_SIGNED": 1,
  "FILE_PATH": "C:\\Windows\\System32\\svchost.exe",
  "FILE_SIZE": 78880,
  "MODIFICATION_TIME": 1686685723546
}
```

### FILE\_MODIFIED

Generated when a file is modified.

> Be Aware:
>
> When adding this event to an event collection rule, you will be monitoring system-wide. This could result in a large number of events.

> Best Practices:
>
> * Utilize this selectively (ex. deploy on only suspect systems)
> * Use Exfil watch rules to specify paths that are of high interest
> * Consider using File Integrity Monitoring (FIM)
> * Look for this on an ad-hoc basis from the Sensor Console. ex.
>
>   ```
>   history_dump -e FILE_MODIFIED
>   ```

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Microsoft\\Windows\\WebCache\\V01.log",
  "TIMESTAMP": 1468335272949
}
```

### FILE\_MOV\_REP

Response event for the `file_mov` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "DESTINATION": "C:\\test\\test.txt.bak",
  "SOURCE": "C:\\test\\test.txt"
}
```

### FILE\_TYPE\_ACCESSED

Generated when a new process is observed interacting with certain file types.

The `RULE_NAME` component is the class of file extension involved:

* Rule 1: `.doc`, `.docm`, `.docx`
* Rule 2: `.xlt`, `.xlsm`, `.xlsx`
* Rule 3: `.ppt`, `.pptm`, `.pptx`, `.ppts`
* Rule 4: `.pdf`
* Rule 5: `.rtf`
* Rule 50: `.zip`
* Rule 51: `.rar`
* Rule 64: `.locky`, `.aesir`

**Platforms:**

```
{
  "PROCESS_ID": 2048,
  "RULE_NAME": 50,
  "FILE_PATH": "C:\\Program Files\\7-Zip\\7zG.exe"
}
```

### FIM\_ADD

Response event for the `fim_add` sensor command. An `ERROR: 0` implies the path was successfully added.

**Platforms:**

**Output:**

```
"event": {
  "ERROR":0
}
```

### FIM\_DEL

Response event for the `fim_del` sensor command. An `ERROR: 0` implies the path was successfully removed.

An `ERROR: 3` response implies the provided path was not found in the list of FIM patterns.

**Platforms:**

**Output:**

```
"event": {
  "ERROR":0
}
```

### FIM\_HIT

A file, directory, or registry key being monitored by File & Registry Integrity Monitoring has been modified.

**Platforms:**

```
{
  "PROCESS": {
    "MEMORY_USAGE": 25808896,
    "TIMESTAMP": 1541348299886,
    "COMMAND_LINE": "\"C:\\WINDOWS\\regedit.exe\" ",
    "PROCESS_ID": 4340,
    "THREADS": 3,
    "USER_NAME": "BUILTIN\\Administrators",
    "FILE_PATH": "C:\\WINDOWS\\regedit.exe",
    "PARENT_PROCESS_ID": 6260
  },
  "REGISTRY_KEY": "\\REGISTRY\\MACHINE\\SOFTWARE\\ActiveState\\New Value #1",
  "PROCESS_ID": 4340
}
```

### FIM\_LIST\_REP

Response event for the `fim_get` sensor command. The response will be a JSON list of FIM patterns.

**Platforms:**

**Output:**

```
{
  "PATTERNS": [
    0: "/home/*",
    1: "/home/*/.ssh/*",
    2: "/root/.ssh/authorized_keys"
  ]
}
```

### GET\_DOCUMENT\_REP

Generated when a `doc_cache_get` task requests a cached document.

**Platforms:**

### GET\_EXFIL\_EVENT\_REP

Response from an `exfil_get` sensor command.

**Platforms:**

### HIDDEN\_MODULE\_DETECTED

Generated when a `hidden_module_scan` command is issued.

Note that the name of the event does not confirm the presence of a hidden module. Please check the output to

confirm whether a hidden module was detected.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0,
  "ERROR_MESSAGE": "done"
}
```

### HISTORY\_DUMP\_REP

Response from `history_dump` sensor command. Does not itself contain the historic events but will be generated along them.

**Platforms:**

### HTTP\_REQUEST

This event is emitted whenever an HTTP request is made.

**Platforms:**

**Sample Event:**

```
{
  "URL": "https://play.google.com/log?authuser=0",
  "IP_ADDRESS": "172.217.2.142",
  "RESULT": 200,
  "PARENT": {
    "URL": "https://console.cloud.google.com"
  }
}
```

### HTTP\_REQUEST\_HEADERS

Provides HTTP Request headers.

**Platforms:**

**Sample Event:**

```
{
  "HEADERS": [
    {
      "NAME": "User-Agent",
      "VALUE": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    },
    {
      "NAME": "Accept",
      "VALUE": "*/*"
    }
  ]
}
```

### HTTP\_RESPONSE\_HEADERS

Provides HTTP Response headers.

**Platforms:**

**Sample Event:**

```
{
  "HEADERS": [
    {
      "NAME": "content-length",
      "VALUE": "859"
    },
    {
      "NAME": "cache-control",
      "VALUE": "max-age=3600"
    },
    {
      "NAME": "content-encoding",
      "VALUE": "br"
    },
    {
      "NAME": "content-type",
      "VALUE": "text/html; charset=utf-8"
    },
    {
      "NAME": "etag",
      "VALUE": "\"1540d7725dd15680377d45886baba56f620f7692faa530bc3597226ffadd77d1-br\""
    },
    {
      "NAME": "last-modified",
      "VALUE": "Thu, 21 Dec 2023 23:59:32 GMT"
    },
    {
      "NAME": "referrer-policy",
      "VALUE": "sameorigin"
    },
    {
      "NAME": "strict-transport-security",
      "VALUE": "max-age=3600 ; includeSubDomains"
    },
    {
      "NAME": "x-content-type-options",
      "VALUE": "nosniff"
    },
    {
      "NAME": "x-frame-options",
      "VALUE": "sameorigin"
    },
    {
      "NAME": "accept-ranges",
      "VALUE": "bytes"
    },
    {
      "NAME": "date",
      "VALUE": "Fri, 22 Dec 2023 19:10:58 GMT"
    },
    {
      "NAME": "x-served-by",
      "VALUE": "cache-dub4332-DUB"
    },
    {
      "NAME": "x-cache",
      "VALUE": "HIT"
    },
    {
      "NAME": "x-cache-hits",
      "VALUE": "1"
    },
    {
      "NAME": "x-timer",
      "VALUE": "S1703272259.579745,VS0,VE1"
    },
    {
      "NAME": "vary",
      "VALUE": "x-fh-requested-host, accept-encoding"
    },
    {
      "NAME": "alt-svc",
      "VALUE": "h3=\":443\";ma=86400,h3-29=\":443\";ma=86400,h3-27=\":443\";ma=86400"
    }
  ]
}
```

### LOG\_GET\_REP

Response from a `log_get` request.

### LOG\_LIST\_REP

Response from a `log_list` request.

### MEM\_FIND\_HANDLES\_REP

Response event for the `mem_find_handle` sensor command.

**Platforms:**

### MEM\_FIND\_STRING\_REP

Response event for the `mem_find_string` sensor command.

**Platforms:**

### MEM\_HANDLES\_REP

Response event for the `mem_handles` sensor command. This event will contain an array of handles identified in memory.

**Platforms:**

**Sample Event:**

```
{
    "HANDLES": [
      {
        "HANDLE_NAME": "\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options",
        "HANDLE_TYPE": "Key",
        "HANDLE_VALUE": 4,
        "PROCESS_ID": 908
      },
      {
        "HANDLE_NAME": "\\KnownDlls",
        "HANDLE_TYPE": "Directory",
        "HANDLE_VALUE": 48,
        "PROCESS_ID": 908
      },
      "..."]
}
```

### MEM\_MAP\_REP

Response event for the `mem_map` sensor command. This event will contain an array of arrays, representing processes and their associated memory data.

**Platforms:**

Sample Event:

```
{
    "MEMORY_MAP": [
      {
        "BASE_ADDRESS": 94100802174976,
        "MEMORY_ACCESS": 6,
        "MEMORY_SIZE": 4096,
        "MEMORY_TYPE": 3
      }
    ]
}
```

### MEM\_READ\_REP

Response event for the `mem_read` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "MEMORY_DUMP": "TGltYU...",
  "PROCESS_ID": 745
}
```

### MEM\_STRINGS\_REP

Response event for the `mem_strings` sensor command. The response will contain two arrays of arrays, `STRINGSA` and `STRINGSW`.

**Platforms:**

**Sample Event:**

```
{
    "PROCESS_ID" : 745,
    "STRINGSA" : [
        [
            0 : "/lib64/ld-linux-x86-64.so.2",
            1 : "__gmon_start__"
        ]
    ]
}
```

### MODULE\_LOAD

Generated when a module (like DLL on Windows) is loaded in a process.

**Platforms:**

```
{
  "MEMORY_SIZE": 241664,
  "PROCESS_ID": 2904,
  "FILE_PATH": "C:\\Windows\\System32\\imm32.dll",
  "MODULE_NAME": "imm32.dll",
  "TIMESTAMP": 1468335264989,
  "BASE_ADDRESS": 140715814092800
}
```

### NETSTAT\_REP

Response from a  `netstat` command to list active network sockets.

**Platforms:**

**Sample Event:**

```
{
  "FRIENDLY": 0,
  "NETWORK_ACTIVITY": [
    {
      "DESTINATION": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 0
      },
      "PROCESS_ID": 856,
      "PROTOCOL": "tcp4",
      "SOURCE": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 135
      }
    }
  ]
}
```

### NETWORK\_CONNECTIONS

List of recent network connections performed by a process.

**Platforms:**

```
{
  "NETWORK_ACTIVITY": [
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50396
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.214.49.56",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50397
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "189.247.166.18",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50398
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.217.70.67",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50399
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "104.110.238.53",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50400
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.214.49.56",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50401
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "204.79.197.203",
        "PORT": 80
      }
    }
  ],
  "HASH": "2de228cad2e542b2af2554d61fab5463ecbba3ff8349ba88c3e48637ed8086e9",
  "COMMAND_LINE": "C:\\WINDOWS\\system32\\msfeedssync.exe sync",
  "PROCESS_ID": 6968,
  "FILE_IS_SIGNED": 1,
  "USER_NAME": "WIN-5KC7E0NG1OD\\dev",
  "FILE_PATH": "C:\\WINDOWS\\system32\\msfeedssync.exe",
  "PARENT_PROCESS_ID": 1892
}
```

### NEW\_DOCUMENT

Generated when a file is created that matches a set list of locations and extensions. It indicates the file has been cached in memory and can be retrieved using the `doc_cache_get` task.

The following file patterns are considered "documents":

* `.bat`
* `.js`
* `.ps1`
* `.sh`
* `.py`
* `.exe`
* `.scr`
* `.pdf`
* `.doc`
* `.docm`
* `.docx`
* `.ppt`
* `.pptm`
* `.pptx`
* `.xlt`
* `.xlsm`
* `.xlsx`
* `.vbs`
* `.rtf`
* `.hta`
* `.lnk`
* `.xsl`
* `.com`
* `.png`
* `.jpg`
* `.asp`
* `.aspx`
* `.php`
* `\windows\system32\`

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\Desktop\\evil.exe",
  "TIMESTAMP": 1468335816308,
  "HASH": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### NEW\_NAMED\_PIPE

This event is emitted when a new Named Pipe is created by a process.

**Platforms:**

```
{
  "FILE_PATH": "\\Device\\NamedPipe\\LOCAL\\mojo.6380.1072.2134013463507075011",
  "PROCESS_ID": 6380
}
```

### NEW\_PROCESS

Generated when a new process starts.

**Platforms:**

```
{
  "PARENT": {
    "PARENT_PROCESS_ID": 7076,
    "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\Common7\\IDE\\devenv.exe\"  ",
    "MEMORY_USAGE": 438730752,
    "PROCESS_ID": 5820,
    "THREADS": 39,
    "FILE_PATH": "C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\Common7\\IDE\\devenv.exe",
    "BASE_ADDRESS": 798949376
  },
  "PARENT_PROCESS_ID": 5820,
  "COMMAND_LINE": "-q  -s {0257E42D-7F05-42C4-B402-34C1CC2F2EAD} -p 5820",
  "FILE_PATH": "C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\VC\\vcpackages\\VCPkgSrv.exe",
  "PROCESS_ID": 1080,
  "THREADS": 9,
  "MEMORY_USAGE": 8282112,
  "TIMESTAMP": 1456285660,
  "BASE_ADDRESS": 4194304
}
```

### NEW\_REMOTE\_THREAD

Generated when a thread is created by a process in another process. This is often used by malware during various forms of code injection.

In this case, the process id `492` created a thread (with id `9012`) in the process id `7944`. The parent process is also globally uniquely identified by the `routing/parent` and the process where the thread was started is globally uniquely identified by the `routing/target` (not visible here).

**Platforms:**

```
{
  "THREAD_ID": 9012,
  "PROCESS_ID": 7944,
  "PARENT_PROCESS_ID": 492
}
```

### NEW\_TCP4\_CONNECTION

Generated when a new TCPv4 connection is established, either inbound or outbound.

**Platforms:**

```
{
  "PROCESS_ID": 6788,
  "DESTINATION": {
    "IP_ADDRESS": "172.16.223.219",
    "PORT": 80
  },
  "STATE": 5,
  "TIMESTAMP": 1468335512047,
  "SOURCE": {
    "IP_ADDRESS": "172.16.223.163",
    "PORT": 63581
  }
}
```

### NEW\_TCP6\_CONNECTION

Generated when a new TCPv6 connection is established, either inbound or outbound.

**Platforms:**

### NEW\_UDP4\_CONNECTION

Generated when a new UDPv4 socket "connection" is established, either inbound or outbound.

**Platforms:**

```
{
  "TIMESTAMP": 1468335452828,
  "PROCESS_ID": 924,
  "IP_ADDRESS": "172.16.223.163",
  "PORT": 63057
}
```

### NEW\_UDP6\_CONNECTION

Generated when a new UDPv6 socket "connection" is established, either inbound or outbound.

**Platforms:**

### OPEN\_NAMED\_PIPE

This event is emitted when an existing Named Pipe is opened by a process.

**Platforms:**

```
{
  "FILE_PATH": "\\Device\\NamedPipe\\lsass",
  "PROCESS_ID": 2232
}
```

### OS\_AUTORUNS\_REP

Response from an `os_autoruns` request.

**Platforms:**

**Sample Event:**

```
{
  "TIMESTAMP": 1456194620,
  "AUTORUNS": [
    {
      "REGISTRY_KEY": "Software\\Microsoft\\Windows\\CurrentVersion\\Run\\VMware User Process",
      "FILE_PATH": "\"C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe\" -n vmusr",
      "HASH": "036608644e3c282efaac49792a2bb2534df95e859e2ddc727cd5d2e764133d14"
    }
  ]
}
```

### OS\_DRIVERS\_REP

Response from an `os_drivers` request.

**Platforms:**

**Sample Event:**

```
{
  "SVCS": [
    {
      "PROCESS_ID": 0,
      "SVC_TYPE": 1,
      "SVC_NAME": "1394ohci",
      "SVC_STATE": 1,
      "HASH": "9ecf6211ccd30273a23247e87c31b3a2acda623133cef6e9b3243463c0609c5f",
      "SVC_DISPLAY_NAME": "1394 OHCI Compliant Host Controller",
      "EXECUTABLE": "\\SystemRoot\\System32\\drivers\\1394ohci.sys"
    }
  ]
}
```

### OS\_KILL\_PROCESS\_REP

Response from an `os_kill_process` request.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0,
  "PROCESS_ID": 579
}
```

### OS\_PACKAGES\_REP

List of packages installed on the system. This is currently Windows only but will be expanded to MacOS and Linux in the future.

**Platforms:**

**Sample Event:**

```
"PACKAGES": [
  {
    "PACKAGE_NAME": "Microsoft Windows Driver Development Kit Uninstall"
  }
]
```

### OS\_PROCESSES\_REP

Response from an `os_process` request.

**Platforms:**

**Sample Event:**

```
{
  "PROCESSES": [
    {
      "COMMAND_LINE": "/sbin/init",
      "FILE_PATH": "/usr/lib/systemd/systemd",
      "HASH": "477209848fabcaf52c060d98287f880845cb07fc9696216dbcfe9b6ea8e72bcd"
    }
  ]
}
```

### OS\_RESUME\_REP

Response from an `os_resume` request.

**Platforms:**

### OS\_SERVICES\_REP

Response from an `os_services` request.

**Platforms:**

**Sample Event:**

```
{
  "SVCS": [
    {
      "PROCESS_ID": 0,
      "SVC_TYPE": 32,
      "DLL": "%SystemRoot%\\System32\\AJRouter.dll",
      "SVC_NAME": "AJRouter"
    }
  ]
}
```

### OS\_SUSPEND\_REP

Response from an `os_suspend` request.

**Platforms:**

### OS\_USERS\_REP

Response from an `os_users` request.

**Platforms:**

**Sample Event:**

```
{
  "USERS": [
    {
      "USER_NAME": "Administrator"
    }
  ]
}
```

### OS\_VERSION\_REP

Response from an `os_version` request.

**Platforms:**

**Sample Event:**

```
{
  "BUILD_NUMBER": 20348
}
```

### PCAP\_LIST

\_INTERFACES\_REP
 Response from a `pcap_ifaces` request.

**Platforms:**

**Sample Event:**

```
{
  "INTERFACE": [
    {
      "NAME": "ens4",
      "IPV4": ["10.128.15.198"]
    }
  ]
}
```

### PROCESS\_ENVIRONMENT

Generated when a process starts. It lists all environment variables associated with that new process.

**Platforms:**

```
{
  "ENVIRONMENT_VARIABLES": [
    "LANG=en_US.UTF-8",
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "NOTIFY_SOCKET=/run/systemd/notify",
    "LISTEN_PID=18950",
    "LISTEN_FDS=2"
  ],
  "PROCESS_ID": 13463
}
```

### RECEIPT

This event is used as a generic response to some commands. The contents of a `RECEIPT` event usually contain an `ERROR` code that you can use to determine if the command was successful (`ERROR` codes can be explored [here](/v2/docs/reference-error-codes)). It's often a good idea to issue the original command with an `investigation_id` which will get echoed in the `RECEIPT` related to that command to make it easier to track.

**Platforms:**

### REGISTRY\_CREATE

This event is generated whenever a registry key / value is created on a Windows OS.

**Platforms:**

```
{
  "PROCESS_ID":  764,
  "REGISTRY_KEY":   "\\REGISTRY\\A\\{fddf4643-a007-4086-903e-be998801d0f7}\\Events\\{8fb5d848-23dc-498f-ac61-84b93aac1c33}"
}
```

### REGISTRY\_DELETE

This event is generated whenever a registry key / value is deleted on a Windows OS.

**Platforms:**

```
{
  "PROCESS_ID":  764,
  "REGISTRY_KEY":   "\\REGISTRY\\A\\{fddf4643-a007-4086-903e-be998801d0f7}\\Events\\{8fb5d848-23dc-498f-ac61-84b93aac1c33}"
}
```

### REGISTRY\_LIST\_REP

This event is generated in response to the `reg_list` command to list keys and values in a registry key.

**Platforms:**

**Sample Event:**

```
{
    "REGISTRY_KEY": [
      "ActiveState"
    ],
    "ROOT": "hklm\\software",
    "REGISTRY_VALUE": [
      {
        "TYPE": 4,
        "NAME": "Order"
      }
    ],
    "ERROR": 0
}
```

### REGISTRY\_WRITE

This event is generated whenever a registry value is written to on a Windows OS.

The `REGISTRY_VALUE` contains the first 16 bytes of the value written to the registry. If this value is a valid ASCII or Unicode string, the value will be as-is. On the other hand if the value is binary data, it will be a base64 encoded string, see examples below.

The `SIZE` is the size value used in the original registry write call. The `TYPE` is the Windows data type of the entry written as per [Microsoft's definition](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/25cce700-7fcf-4bb6-a2f3-0f6d08430a55).

**Platforms:**

Valid string payload:

```
{
  "PROCESS_ID":1820,
  "REGISTRY_KEY":"\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows Defender\\Diagnostics\\LastKnownGoodPlatformLocation",
  "REGISTRY_VALUE":"C:\\Progr",
  "SIZE":1,
  "TYPE":1,
}
```

Binary payload:

```
{
  "PROCESS_ID": 1700,
  "REGISTRY_KEY": "\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Diagnostics\\DiagTrack\\HeartBeats\\Default\\LastHeartBeatTime",
  "REGISTRY_VALUE": "bMPGjjDM1wE=","SIZE": 11,
  "TYPE": 11
}
```

### REJOIN\_NETWORK

Emitted after a sensor is allowed network connectivity again (after it was previously segregated). An error code of 0 indicates success.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0
}
```

### REMOTE\_PROCESS\_HANDLE

Generated whenever a process opens a handle to another process with access flags like `VM_READ`, `VM_WRITE`, or `PROCESS_CREATE_THREAD`.

The `ACCESS_FLAGS` is the access mask as defined [here](https://docs.microsoft.com/en-us/windows/desktop/procthread/process-security-and-access-rights).

**Platforms:**

```
{
  "ACCESS_FLAGS": 136208,
  "PARENT_PROCESS_ID": 6492,
  "PROCESS_ID": 2516
}
```

### SEGREGATE\_NETWORK

Emitted when a sensor is segregated (isolated) from the network using the `segregate_network` command. An error code of 0 indicates success.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0
}
```

### SENSITIVE\_PROCESS\_ACCESS

Generated when a process gains sensitive access to operating system processes like `lsass.exe` on Windows.

Note

SENSITIVE\_PROCESS\_ACCESS currently is only emitted for processes accessing `lsass.exe` on Windows.

**Platforms:**

```
{
  "EVENTS": [
    {
      "event": {
        "COMMAND_LINE": "C:\\WINDOWS\\system32\\lsass.exe",
        "FILE_PATH": "C:\\WINDOWS\\system32\\lsass.exe",
        "PARENT_PROCESS_ID": 484,
        "PROCESS_ID": 636,
        "THREADS": 12,
        "USER_NAME": "BUILTIN\\Administrators"
      }
    }
  ]
}
```

### SERVICE\_CHANGE

Generated when a Service is changed.

**Platforms:**

```
{
  "PROCESS_ID": 0,
  "SVC_TYPE": 32,
  "DLL": "%SystemRoot%\\system32\\wlidsvc.dll",
  "SVC_NAME": "wlidsvc",
  "SVC_STATE": 1,
  "HASH": "b37199495115ed423ba99b7317377ce865bb482d4e847861e871480ac49d4a84",
  "SVC_DISPLAY_NAME": "Microsoft Account Sign-in Assistant",
  "TIMESTAMP": 1467942600540,
  "EXECUTABLE": "%SystemRoot%\\system32\\svchost.exe -k netsvcs"
}
```

### SEGREGATE\_NETWORK

Emitted when a sensor is segregated (isolated) from the network using the `segregate_network` command.

**Platforms:**

### SSH\_LOGIN

Generated when a user logs in via SSH.

**Platforms:**

```
{
  "USER_NAME": "root",
  "TIMESTAMP": 1468335816308
}
```

### SELF\_TEST

Internal event to manually request a power-on-self-test (POST) from the sensor.

### SHUTTING\_DOWN

Event generated when the sensor shuts down. Note: this event may not be observed if the host shuts down abruptly or too quickly.

**Platforms:**

**Event Data**

| Field | Type | Notes |
| --- | --- | --- |
| ts | Epoch timestamp |  |

**Sample Event:**

```
{
  "SHUTTING_DOWN": {
    "ts": 1455674775
  }
}
```

### SSH\_LOGOUT

Generated when a user logs out via SSH.

**Platforms:**

```
{
  "USER_NAME": "root",
  "TIMESTAMP": 1468335916308
}
```

### STARTING\_UP

Event generated when the sensor starts.

**Platforms:**

**Event Data**

| Field | Type | Notes |
| --- | --- | --- |
| ts | Epoch timestamp |  |

**Sample Event:**

```
{
  "STARTING_UP": {
    "ts": 1455674775
  }
}
```

### TERMINATE\_PROCESS

Generated when a process exits.

**Platforms:**

```
{
  "PARENT_PROCESS_ID": 5820,
  "TIMESTAMP": 1456285661,
  "PROCESS_ID": 6072
}
```

### TERMINATE\_TCP4\_CONNECTION

Generated when a TCPv4 connection terminates.

```
{
  "DESTINATION": {
    "IP_ADDRESS": "61.55.252.93",
    "PORT": 443
  },
  "PROCESS_ID": 4784,
  "SOURCE": {
    "IP_ADDRESS": "172.16.223.138",
    "PORT": 50145
  }
}
```

### TERMINATE\_TCP6\_CONNECTION

Generated when a TCPv6 connection terminates.

### TERMINATE\_UDP4\_CONNECTION

Generated when a UDPv4 socket terminates.

### TERMINATE\_UDP6\_CONNECTION

Generated when a UDPv6 socket terminates.

### THREAD\_INJECTION

This event is generated when the sensor detects what looks like a thread injection into a remote process.

**Platforms:**

```
{
  "event": {
    "EVENTS": [
      {
        "event": {
          "ACCESS_FLAGS": 2097151,
          "PARENT_PROCESS_ID": 5380,
          "PROCESS_ID": 4276,
          "SOURCE": {
            "BASE_ADDRESS": 140701160243200,
            "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --continue-active-setup",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "HASH": "c47fc20231ffc1e3befef952478363bff96cf3af1f36da4bd1129c8ed0e17fdb",
            "MEMORY_USAGE": 5881856,
            "PARENT_ATOM": "df4e951a09e365cb46c36c11659ee556",
            "PARENT_PROCESS_ID": 5972,
            "PROCESS_ID": 5380,
            "THIS_ATOM": "37b57d228af708b25d097f32659ee557",
            "THREADS": 3,
            "TIMESTAMP": 1704912214704,
            "USER_NAME": "WINDOWS-SERVER-\\whitney"
          },
          "TARGET": {
            "COMMAND_LINE": "C:\\Windows\\system32\\sppsvc.exe",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Windows\\system32\\sppsvc.exe",
            "HASH": "1ca5b9745872748575c452e456966b8ed1c4153757e9f4faf6f86c78c53d4ae8",
            "MEMORY_USAGE": 6156288,
            "PARENT_ATOM": "74be005ef68f6edb8682d972659ee024",
            "PARENT_PROCESS_ID": 628,
            "PROCESS_ID": 4276,
            "THIS_ATOM": "fe1dee93442392ea97becdad659ee516",
            "THREADS": 3,
            "TIMESTAMP": 1704912150174,
            "USER_NAME": "NT AUTHORITY\\NETWORK SERVICE"
          }
        },
        "routing": {
          "arch": 2,
          "did": "",
          "event_id": "d61caa47-225a-4f6a-9f3a-6094cdb3c383",
          "event_time": 1704912219717,
          "event_type": "REMOTE_PROCESS_HANDLE",
          "ext_ip": "104.198.223.172",
          "hostname": "windows-server-2022-bc76d608-9d83-4c6c-bdd5-f86bbd385a94-0.c.lc-demo-infra.internal.",
          "iid": "3c5c33e6-daaf-4029-be0b-94f50b86777e",
          "int_ip": "10.128.15.197",
          "moduleid": 2,
          "oid": "bc76d608-9d83-4c6c-bdd5-f86bbd385a94",
          "parent": "37b57d228af708b25d097f32659ee557",
          "plat": 268435456,
          "sid": "ccd0c386-88c1-4f8d-954c-581a95a1cc34",
          "tags": [
            "windows"
          ],
          "target": "fe1dee93442392ea97becdad659ee516",
          "this": "87509849fc608bce8a236f49659ee55b"
        }
      },
      {
        "event": {
          "PARENT_PROCESS_ID": 5380,
          "PROCESS_ID": 4276,
          "SOURCE": {
            "BASE_ADDRESS": 140701160243200,
            "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --continue-active-setup",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "HASH": "c47fc20231ffc1e3befef952478363bff96cf3af1f36da4bd1129c8ed0e17fdb",
            "MEMORY_USAGE": 5881856,
            "PARENT_ATOM": "df4e951a09e365cb46c36c11659ee556",
            "PARENT_PROCESS_ID": 5972,
            "PROCESS_ID": 5380,
            "THIS_ATOM": "37b57d228af708b25d097f32659ee557",
            "THREADS": 3,
            "TIMESTAMP": 1704912214704,
            "USER_NAME": "WINDOWS-SERVER-\\whitney"
          },
          "TARGET": {
            "COMMAND_LINE": "C:\\Windows\\system32\\sppsvc.exe",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Windows\\system32\\sppsvc.exe",
            "HASH": "1ca5b9745872748575c452e456966b8ed1c4153757e9f4faf6f86c78c53d4ae8",
            "MEMORY_USAGE": 6156288,
            "PARENT_ATOM": "74be005ef68f6edb8682d972659ee024",
            "PARENT_PROCESS_ID": 628,
            "PROCESS_ID": 4276,
            "THIS_ATOM": "fe1dee93442392ea97becdad659ee516",
            "THREADS": 3,
            "TIMESTAMP": 1704912150174,
            "USER_NAME": "NT AUTHORITY\\NETWORK SERVICE"
          },
          "THREAD_ID": 3672
        },
        "routing": {
          "arch": 2,
          "did": "",
          "event_id": "ece7d85e-a43c-49d3-bc9a-28ace6dc1b02",
          "event_time": 1704912219967,
          "event_type": "NEW_REMOTE_THREAD",
          "ext_ip": "104.198.223.172",
          "hostname": "windows-server-2022-bc76d608-9d83-4c6c-bdd5-f86bbd385a94-0.c.lc-demo-infra.internal.",
          "iid": "3c5c33e6-daaf-4029-be0b-94f50b86777e",
          "int_ip": "10.128.15.197",
          "moduleid": 2,
          "oid": "bc76d608-9d83-4c6c-bdd5-f86bbd385a94",
          "parent": "37b57d228af708b25d097f32659ee557",
          "plat": 268435456,
          "sid": "ccd0c386-88c1-4f8d-954c-581a95a1cc34",
          "tags": [
            "windows"
          ],
          "target": "fe1dee93442392ea97becdad659ee516",
          "this": "b30a499edf9ec2e424b07d20659ee55b"
        }
      }
    ]
  }
  "ts": "2024-01-10 18:43:39"
}
```

### USER\_LOGIN

Generated when a user logs in to the operating system.

**Platforms:**

### USER\_LOGOUT

Generated when a user logs out of the operating system.

**Platforms:**

### USER\_OBSERVED

Generated the first time a user is observed on a host.

**Platforms:**

```
{
  "TIMESTAMP": 1479241363009,
  "USER_NAME": "root"
}
```

### VOLUME\_MOUNT

This event is generated when a volume is mounted.

**Platforms:**

```
{
  "VOLUME_PATH": "E:",
  "DEVICE_NAME": "\\Device\\HarddiskVolume3"
}
```

### VOLUME\_UNMOUNT

This event is generated when a volume is unmounted.

**Platforms:**

```
{
  "VOLUME_PATH": "/Volumes/RECOVERY",
  "VOLUME_NAME": "/dev/disk2s1"
}
```

### YARA\_DETECTION

Generated when a YARA scan finds a match.

**Platforms:**

```
{
  "RULE_NAME": "malware_detection_rule",
  "FILE_PATH": "C:\\malicious.exe",
  "HASH": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Endpoint Detection & Response

---

## Reference: Endpoint Agent Commands

**Source:** https://docs.limacharlie.io/docs/reference-endpoint-agent-commands

# Reference: Endpoint Agent Commands

## Supported Commands by OS

For commands which emit a report/reply event type from the agent, the corresponding event type is provided.

| Command | Report/Reply Event | macOS | Windows | Linux | Chrome | Edge |
| --- | --- | --- | --- | --- | --- | --- |
| [artifact\_get](/v2/docs/reference-endpoint-agent-commands#artifactget) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [deny\_tree](/v2/docs/reference-endpoint-agent-commands#denytree) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_find\_hash](/v2/docs/reference-endpoint-agent-commands#dirfindhash) | [DIR\_FINDHASH\_REP](/v2/docs/edr-events#dirfindhashrep) | ☑️ | ☑️ | ☑️ |  |  |
| [dir\_list](/v2/docs/reference-endpoint-agent-commands#dirlist) | [DIR\_LIST\_REP](/v2/docs/edr-events#dirlistrep) | ☑️ | ☑️ | ☑️ |  |  |
| [dns\_resolve](/v2/docs/reference-endpoint-agent-commands#dnsresolve) | [DNS\_REQUEST](/v2/docs/edr-events#dnsrequest) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [doc\_cache\_get](/v2/docs/reference-endpoint-agent-commands#doccacheget) | [GET\_DOCUMENT\_REP](/v2/docs/edr-events#getdocumentrep) | ☑️ | ☑️ |  |  |  |
| [get\_debug\_data](/v2/docs/reference-endpoint-agent-commands#getdebugdata) | [DEBUG\_DATA\_REP](/v2/docs/edr-events#debugdatarep) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_add](/v2/docs/reference-endpoint-agent-commands#exfiladd) | [CLOUD\_NOTIFICATION](/v2/docs/edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_del](/v2/docs/reference-endpoint-agent-commands#exfildel) | [CLOUD\_NOTIFICATION](/v2/docs/edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ |  |  |
| [exfil\_get](/v2/docs/reference-endpoint-agent-commands#exfilget) | [GET\_EXFIL\_EVENT\_REP](/v2/docs/edr-events#getexfileventrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_del](/v2/docs/reference-endpoint-agent-commands#filedel) | [FILE\_DEL\_REP](/v2/docs/edr-events#filedelrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_get](/v2/docs/reference-endpoint-agent-commands#fileget) | [FILE\_GET\_REP](/v2/docs/edr-events#filegetrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_hash](/v2/docs/reference-endpoint-agent-commands#filehash) | [FILE\_HASH\_REP](/v2/docs/edr-events#filehashrep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_info](/v2/docs/reference-endpoint-agent-commands#fileinfo) | [FILE\_INFO\_REP](/v2/docs/edr-events#fileinforep) | ☑️ | ☑️ | ☑️ |  |  |
| [file\_mov](/v2/docs/reference-endpoint-agent-commands#filemov) | [FILE\_MOV\_REP](/v2/docs/edr-events#filemovrep) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_add](/v2/docs/reference-endpoint-agent-commands#fimadd) | [FIM\_ADD](/v2/docs/edr-events#fimadd) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_del](/v2/docs/reference-endpoint-agent-commands#fimdel) | [FIM\_DEL](/v2/docs/edr-events#fimdel) | ☑️ | ☑️ | ☑️ |  |  |
| [fim\_get](/v2/docs/reference-endpoint-agent-commands#fimget) | [FIM\_LIST\_REP](/v2/docs/edr-events#fimlistrep) | ☑️ | ☑️ | ☑️ |  |  |
| [hidden\_module\_scan](/v2/docs/reference-endpoint-agent-commands#hiddenmodulescan) | [HIDDEN\_MODULE\_DETECTED](/v2/docs/edr-events#hiddenmoduledetected) |  | ☑️ | ☑️ |  |  |
| [history\_dump](/v2/docs/reference-endpoint-agent-commands#historydump) | [HISTORY\_DUMP\_REP](/v2/docs/edr-events#historydumprep) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [log\_get](/v2/docs/reference-endpoint-agent-commands#logget) | N/A |  | ☑️ |  |  |  |
| [logoff](/v2/docs/reference-endpoint-agent-commands#logoff) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_find\_handle](/v2/docs/reference-endpoint-agent-commands#memfindhandle) | [MEM\_FIND\_HANDLES\_REP](/v2/docs/edr-events#memfindhandlesrep) |  | ☑️ |  |  |  |
| [mem\_find\_string](/v2/docs/reference-endpoint-agent-commands#memfindstring) | [MEM\_FIND\_STRING\_REP](/v2/docs/edr-events#memfindstringrep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_handles](/v2/docs/reference-endpoint-agent-commands#memhandles) | [MEM\_HANDLES\_REP](/v2/docs/edr-events#memhandlesrep) |  | ☑️ |  |  |  |
| [mem\_map](/v2/docs/reference-endpoint-agent-commands#memmap) | [MEM\_MAP\_REP](/v2/docs/edr-events#memmaprep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_read](/v2/docs/reference-endpoint-agent-commands#memread) | [MEM\_READ\_REP](/v2/docs/edr-events#memreadrep) | ☑️ | ☑️ | ☑️ |  |  |
| [mem\_strings](/v2/docs/reference-endpoint-agent-commands#memstrings) | [MEM\_STRINGS\_REP](/v2/docs/edr-events#memstringsrep) | ☑️ | ☑️ | ☑️ |  |  |
| [netstat](/v2/docs/reference-endpoint-agent-commands#netstat) | [NETSTAT\_REP](/v2/docs/edr-events#netstatrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_autoruns](/v2/docs/reference-endpoint-agent-commands#osautoruns) | [OS\_AUTORUNS\_REP](/v2/docs/edr-events#osautorunsrep) | ☑️ | ☑️ |  |  |  |
| [os\_drivers](/v2/docs/reference-endpoint-agent-commands#osdrivers) | N/A |  | ☑️ |  |  |  |
| [os\_kill\_process](/v2/docs/reference-endpoint-agent-commands#oskillprocess) | [OS\_KILL\_PROCESS\_REP](/v2/docs/edr-events#oskillprocessrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_packages](/v2/docs/reference-endpoint-agent-commands#ospackages) | [OS\_PACKAGES\_REP](/v2/docs/edr-events#ospackagesrep) |  | ☑️ | ☑️ | ☑️ | ☑️ |
| [os\_processes](/v2/docs/reference-endpoint-agent-commands#osprocesses) | [OS\_PROCESSES\_REP](/v2/docs/edr-events#osprocessesrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_resume](/v2/docs/reference-endpoint-agent-commands#osresume) | [OS\_RESUME\_REP](/v2/docs/edr-events#osresumerep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_services](/v2/docs/reference-endpoint-agent-commands#osservices) | [OS\_SERVICES\_REP](/v2/docs/edr-events#osservicesrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_suspend](/v2/docs/reference-endpoint-agent-commands#ossuspend) | [OS\_SUSPEND\_REP](/v2/docs/edr-events#ossuspendrep) | ☑️ | ☑️ | ☑️ |  |  |
| [os\_users](/v2/docs/reference-endpoint-agent-commands#osusers) | [OS\_USERS\_REP](/v2/docs/edr-events#osusersrep) |  | ☑️ |  |  |  |
| [os\_version](/v2/docs/reference-endpoint-agent-commands#osversion) | [OS\_VERSION\_REP](/v2/docs/edr-events#osversionrep) | ☑️ | ☑️ | ☑️ |  |  |
| [put](/v2/docs/reference-endpoint-agent-commands#put) | [RECEIPT](/v2/docs/edr-events#receipt) | ☑️ | ☑️ | ☑️ |  |  |
| [rejoin\_network](/v2/docs/reference-endpoint-agent-commands#rejoinnetwork) | [REJOIN\_NETWORK](/v2/docs/edr-events#rejoinnetwork) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [restart](/v2/docs/reference-endpoint-agent-commands#restart) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [run](/v2/docs/reference-endpoint-agent-commands#run) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [seal](/v2/docs/reference-endpoint-agent-commands#seal) |  |  | ☑️ |  |  |  |
| [segregate\_network](/v2/docs/reference-endpoint-agent-commands#segregatenetwork) | [SEGREGATE\_NETWORK](/v2/docs/edr-events#segregatenetwork) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [set\_performance\_mode](/v2/docs/reference-endpoint-agent-commands#setperformancemode) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [shutdown](/v2/docs/reference-endpoint-agent-commands#shutdown) |  | ☑️ | ☑️ | ☑️ |  |  |
| [uninstall](/v2/docs/reference-endpoint-agent-commands#uninstall) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [yara\_scan](/v2/docs/reference-endpoint-agent-commands#yarascan) | [YARA\_DETECTION](/v2/docs/edr-events#yaradetection) | ☑️ | ☑️ | ☑️ |  |  |
| [yara\_update](/v2/docs/reference-endpoint-agent-commands#yaraupdate) | N/A | ☑️ | ☑️ | ☑️ |  |  |
| [epp\_status](/v2/docs/reference-endpoint-agent-commands#eppstatus) | [EPP\_STATUS\_REP] | ☑️ |  |  |  |  |
| [epp\_scan](/v2/docs/reference-endpoint-agent-commands#eppscan) | [EPP\_SCAN\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_exclusions](/v2/docs/reference-endpoint-agent-commands#epplistexclusions) | [EPP\_LIST\_EXCLUSIONS\_REP] | ☑️ |  |  |  |  |
| [epp\_add\_exclusion](/v2/docs/reference-endpoint-agent-commands#eppaddexclusion) | [EPP\_ADD\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_rem\_exclusion](/v2/docs/reference-endpoint-agent-commands#eppremexclusion) | [EPP\_REM\_EXCLUSION\_REP] | ☑️ |  |  |  |  |
| [epp\_list\_quarantine](/v2/docs/reference-endpoint-agent-commands#epplistquarantine) | [EPP\_LIST\_QUARANTINE\_REP] | ☑️ |  |  |  |  |

## Command Descriptions

### artifact\_get

Retrieve an artifact from a Sensor.

The artifact collection command allows you to retrieve files directly from an EDR Sensor. This command is useful for collecting a single or multiple files from a Sensor in response to a detection or for incident triage purposes.

Artifacts can be collected via the automated Artifact Collection in the web UI, initiated via API calls, or pulled via the `artifact_get` command. Each approach provides value, depending on your use case. Utilizing the Artifact Collection capability can automate artifact collection across a fleet, whereas sensor commands can help collect files from a single Sensor under investigation.

**Platforms:**

**Report/Reply Event:**
 N/A

**Usage:**

```
usage: artifact_get [-h] [--file FILE] [--source SOURCE] [--type TYPE]
                    [--payload-id PAYLOADID] [--days-retention RETENTION]
                    [--is-ignore-cert]

optional arguments:
  --file FILE           file path to get
  --source SOURCE       optional os specific artifact source (not currently supported)
  --type TYPE           optional artifact type
  --payload-id PAYLOADID
                        optional specifies an idempotent payload ID to use
  --days-retention RETENTION
                        number of days the data should be retained, default 30
  --is-ignore-cert      if specified, the sensor will ignore SSL cert mismatch
                        while upload the artifact
```

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the logs to be pushed to the cloud.

Unlike the main sensor transport (which uses a pinned certificate), the Artifact Collection feature uses Google infrastructure and their public SSL certificates. This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

### deny\_tree

Tells the sensor that all activity starting at a specific process (and its children) should be denied and killed. This particular command is excellent for ransomware mitigation.

**Platforms:**

**Usage:**

```
usage: deny_tree [-h] atom [atom ...]

positional arguments:
  atom        atoms to deny from
```

### dir\_find\_hash

Find files matching hashes starting at a root directory.

**Platforms:**

**Reply/Report Event:**
[DIR\_FINDHASH\_REP](/v2/docs/reference-edr-events#dirfindhashrep)

**Usage:**

```
usage: dir_find_hash [-h] [-d DEPTH] --hash HASHES rootDir fileExp

positional arguments:
  rootDir               the root directory where to begin the search from
  fileExp               a file name expression supporting basic wildcards like
                        * and ?

optional arguments:
  -d DEPTH, --depth DEPTH
                        optional maximum depth of the listing, defaults to a
                        single level
  --hash HASHES         sha256 to search for, can be specified multiple times
```

### dir\_list

List the contents of a directory.

> Windows Directories
>
> When using dir\_list on Windows systems, ensure the rootDir value is contained within double quotes AND backslashes are escaped. To list all files in a directory, a wildcard (e.g., \*) must be used for the fileExp value.
>
> For example, this will list all files in C:\
>
> * dir\_list “c:\\” \*
>
> These examples will **NOT** work correctly and will not show any files, but will not give an error since they are properly formatted:
>
> * dir\_list c:\\ \* (Missing double quotes)
> * dir\_list “c:\\” (Missing fileExp value)

**Platforms:**

**Report/Reply Event:**
[DIR\_LIST\_REP](/v2/docs/reference-edr-events#dirlistrep)

**Usage:**

```
usage: dir_list [-h] [-d DEPTH] rootDir fileExp

positional arguments:
  rootDir               the root directory where to begin the listing from
  fileExp               a file name expression supporting basic wildcards like
                        * and ?

optional arguments:
  -d DEPTH, --depth DEPTH
                        optional maximum depth of the listing, defaults to a
                        single level
```

### dns\_resolve

Cause the sensor to do a network resolution. Mainly used for internal purposes. An error code of 0 indicates a successful command.

**Platforms:**

**Usage:**

```
dns_resolve [-h] domain

positional arguments:
  domain      domain name to resolve
```

**Sample Output:**

```
{
   "ERROR" : 0
}
```

You wll also see a corresponding `DNS_REQUEST` event in the Sensor timeline.

**Sample** `DNS_REQUEST` **Event:**

```
{
  "DNS_TYPE": 1,
  "DOMAIN_NAME": "www.google.com",
  "IP_ADDRESS": "142.251.116.105",
  "MESSAGE_ID": 30183
}
```

### doc\_cache\_get

Retrieve a document / file that was cached on the sensor.

**Platforms:**

**Report/Reply Event:**
[GET\_DOCUMENT\_REP](/v2/docs/reference-edr-events#getdocumentrep)

This command is currently listed to the following document types:

* .bat
* .js
* .ps1
* .sh
* .py
* .exe
* .scr
* .pdf
* .doc
* .docm
* .docx
* .ppt
* .pptm
* .pptx
* .xlt
* .xlsm
* .xlsx
* .vbs
* .rtf
* .hta
* .lnk
* Any files created in `system32` on Windows.

**Usage:**

```
usage: doc_cache_get [-h] [-f FILE_PATTERN] [-s HASHSTR]

optional arguments:
  -f FILE_PATTERN, --file_pattern FILE_PATTERN
                        a pattern to match on the file path and name of the
                        document, simple wildcards ? and * are supported
  -s HASHSTR, --hash HASHSTR
                        hash of the document to get
```

### exfil\_add

Add an LC event to the list of events sent back to the backend by default.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**

**Usage:**

```
usage: exfil_add [-h] -e EXPIRE event

positional arguments:
  event                 name of event to start exfiling

optional arguments:
  -e EXPIRE, --expire EXPIRE
                        number of seconds before stopping exfil of event
```

### exfil\_del

Remove an LC event from the list of events always sent back to the backend.

Exfil Service

Rather than using the `exfil_add` and `exfil_del` commands exclusively, it is recommended to use the [Exfil extension](/v2/docs/ext-exfil) available through the web UI and REST interface.

**Platforms:**

**Usage:**

```
usage: exfil_del [-h] event

positional arguments:
  event       name of event to stop exfiling
```

### exfil\_get

List all LC events sent back to the backend by default.

**Platforms:**

**Report/Reply Event:**
[GET\_EXFIL\_EVENT\_REP](/v2/docs/reference-edr-events#getexfileventrep)

**Usage:**

```
usage: exfil_get [-h]
```

### file\_del

Delete a file from the endpoint.

**Platforms:**

**Report/Reply Event:**
[FILE\_DEL\_REP](/v2/docs/reference-edr-events#filedelrep)

\*\*Usage: \*\*

```
usage: file_del [-h] file

positional arguments:
  file        file path to delete
```

### file\_get

Retrieve a file from the endpoint.

*Note: The* `file_get` *command is limited to 10MB in size. For files larger than 10MB, please utilize the* `artifact_get` *command.*

**Platforms:**

**Report/Reply Event:**
[FILE\_GET\_REP](/v2/docs/reference-edr-events#filegetrep)

**Usage:**

```
usage: file_get [-h] [-o OFFSET] [-s MAXSIZE] file

positional arguments:
  file                  file path to file to get

optional arguments:
  -o OFFSET, --offset OFFSET
                        offset bytes to begin reading the file at, in base 10
  -s MAXSIZE, --size MAXSIZE
                        maximum number of bytes to read, in base 10, max of
                        10MB
```

### file\_hash

Compute the hash of a file.

**Platforms:**

**Report/Reply Event:**
[FILE\_HASH\_REP](/v2/docs/reference-edr-events#filehashrep)

**Usage:**

```
usage: file_hash [-h] file

positional arguments:
  file        file path to hash
```

### file\_info

Get file information, timestamps, sizes, etc.

**Platforms:**

**Report/Reply Event:**
[FILE\_INFO\_REP](/v2/docs/reference-edr-events#fileinforep)

**Usage:**

```
usage: file_info [-h] file

positional arguments:
  file        file path to file to get info on
```

### file\_mov

Move / rename a file on the endpoint.

**Platforms:**

**Report/Reply Event:**
[FILE\_MOV\_REP](/v2/docs/reference-edr-events#filemovrep)

**Usage:**

```
usage: file_mov [-h] srcFile dstFile

positional arguments:
  srcFile     source file path
  dstFile     destination file path
```

### fim\_add

Add a file or registry path pattern to monitor for modifications.

FIM rules are not persistent. This means that once an asset restarts, the rules will be gone. The recommended way of managing rule application is to use [Detection & Response rules](/v2/docs/detection-and-response) in a similar way to managing events sent to the cloud.

A sample  rule is available [here](/v2/docs/detection-and-response-examples).

Note that instead of using the `fim_add` and `fim_del` commands directly it is recommended to use [the Integrity extension](/v2/docs/ext-integrity) available through the web UI and REST interface.

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_ADD](/v2/docs/reference-edr-events#fimadd)

Patterns include basic wildcards:

* for one character: `?`
* for at least one character: `+`
* for any number of characters: `*`
* escape character: `\`

Note that the pattern is not a string literal, therefore "" needs to be escaped by one more level than usual.

So for example, you could do:

* `?:\*\Programs\Startup\*`
* `\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*`

Which would result in: `fim_add --pattern "?:\*\Programs\Startup\*" --pattern "\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*"`

**Usage:**

```
usage: fim_add [-h] --pattern PATTERNS

optional arguments:
  --pattern PATTERNS  file path or registry path pattern to monitor
```

### fim\_del

Remove a pattern from monitoring.

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_DEL](/v2/docs/reference-edr-events#fimdel)

```
usage: fim_del [-h] --pattern PATTERNS

optional arguments:
  --pattern PATTERNS  file path or registry path pattern to stop monitoring
```

### fim\_get

Get the list of the current monitored pattern(s).

**Platforms:**
   (see [this](/v2/docs/linux-agent-installation) for notes on Linux support)

**Report/Reply Event:**
[FIM\_LIST\_REP](/v2/docs/reference-edr-events#fimlistrep)

```
usage: fim_get [-h]
```

### get\_debug\_data

Retrieve debug data from the EDR sensor.

**Platforms:**

**Report/Reply Event:**
[DEBUG\_DATA\_REP](/v2/docs/reference-edr-events#debugdatarep)

### hidden\_module\_scan

Look for hidden modules in a process's (or all) memory. Hidden modules are DLLs or dylibs loaded manually (not by the OS).

**Platforms:**

**Report/Reply Event:**
[HIDDEN\_MODULE\_DETECTED](/v2/docs/reference-edr-events#hiddenmoduledetected)

**Usage:**

```
usage: hidden_module_scan [-h] pid

positional arguments:
  pid         pid of the process to scan, or "-1" for ALL processes
```

### history\_dump

Send to the backend the entire contents of the sensor event cache, i.e. detailed events of everything that happened recently.

**Platforms:**

**Report/Reply Event:**
[HISTORY\_DUMP\_REP](/v2/docs/reference-edr-events#historydumprep)

**Usage:**

```
usage: history_dump [-h] [-r ROOT] [-a ATOM] [-e EVENT]

optional arguments:
  -r ROOT, --rootatom ROOT
                        dump events present in the tree rooted at this atom
  -a ATOM, --atom ATOM  dump the event with this specific atom
  -e EVENT, --event EVENT
                        dump events of this type only
```

### log\_get

`log_get` is a legacy command that has been replaced with `artifact_get`. You can still issue a `log_get` command from the Sensor, however the parameters and output are the same as `artifact_get`.

### logoff

Execute a logoff for all the users

**Platforms:**

```
usage: logoff --is-confirmed
```

### mem\_find\_handle

Find specific open handles in memory on Windows.

**Platforms:**

**Report/Reply Event:**
[MEM\_FIND\_HANDLES\_REP](/v2/docs/reference-edr-events#memfindhandlesrep)

**Usage:**

```
mem_find_handle [-h] needle

positional arguments:
  needle      substring of the handle names to get
```

### mem\_find\_string

Find specific strings in memory.

**Platforms:**

**Report/Reply Event:**
[MEM\_FIND\_STRING\_REP](/v2/docs/reference-edr-events#memfindstringrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_find_string [-h] -s STRING [STRING ...] pid

positional arguments:
  pid                   pid of the process to search in, 0 for all processes

optional arguments:
  -s STRING [STRING ...], --strings STRING [STRING ...]
                        list of strings to look for
```

### mem\_handles

List all open handles from a process (or all) on Windows.

**Platforms:**

**Report/Reply Event:**
[MEM\_HANDLES\_REP](/v2/docs/reference-edr-events#memhandlesrep)

**Usage:**

```
mem_handles [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the handles from, 0 for all
                        processes
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### mem\_map

Display the map of memory pages from a process including size, access rights, etc.

**Platforms:**

**Report/Reply Event:**
[MEM\_MAP\_REP](/v2/docs/reference-edr-events#memmaprep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_map [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target proces
```

### mem\_read

Retrieve a chunk of memory from a process given a base address and size.

**Platforms:**

**Report/Reply Event:**
[MEM\_READ\_REP](/v2/docs/reference-edr-events#memreadrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_read [-h] [-p PID] [-a PROCESSATOM] baseAddr memSize

positional arguments:
  baseAddr              base address to read from, in HEX FORMAT
  memSize               number of bytes to read, in HEX FORMAT

optional arguments:
  -p PID, --pid PID     pid of the process to get the map from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### mem\_strings

List strings from a process's memory.

**Platforms:**

**Report/Reply Event:**
[MEM\_STRINGS\_REP](/v2/docs/reference-edr-events#memstringsrep)

**Due to recent changes in MacOS, this may be less reliable on that platform.**

**Usage:**

```
mem_strings [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to get the strings from
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### netstat

List network connections and sockets listening.

**Platforms:**

**Usage:**

```
netstat [-h]
```

**Sample Output:**

```
{
  "FRIENDLY": 0,
  "NETWORK_ACTIVITY": [
    {
      "DESTINATION": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 0
      },
      "PROCESS_ID": 716,
      "PROTOCOL": "tcp4",
      "SOURCE": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 135
      },
      "STATE": 2
    },
    {
      ...
    }
  ]
}
```

Netstat `STATE` fields can be mapped via the Windows `MIB_TCP_STATE` table, found [here](https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_lh).

| State | Value |
| --- | --- |
| 1 | CLOSED |
| 2 | LISTEN |
| 3 | SYN-SENT |
| 4 | SYN-RECEIVED |
| 5 | ESTABLISHED |
| 6 | FIN-WAIT-1 |
| 7 | FIN-WAIT-2 |
| 8 | CLOSE-WAIT |
| 9 | CLOSING |
| 10 | LAST-ACK |
| 11 | TIME-WAIT |
| 12 | DELETE TCB |

### os\_autoruns

List pieces of code executing at startup, similar to SysInternals autoruns.

**Platforms:**

```
usage: os_autoruns [-h]
```

### os\_drivers

List all drivers on Windows.

**Platforms:**

```
usage: os_drivers [-h]
```

### os\_kill\_process

Kill a process running on the endpoint.

**Platforms:**

```
usage: os_kill_process [-h] [-p PID] [-a PROCESSATOM]

optional arguments:
  -p PID, --pid PID     pid of the process to kill
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
```

### os\_packages

List installed software packages.

**Platforms:**

```
usage: os_packages [-h]
```

### os\_processes

List all running processes on the endpoint.

For a faster response time, we recommend running `os_processes --is-no-modules`.

**Platforms:**

```
usage: os_processes [-h] [-p PID] [--is-no-modules]

optional arguments:
  -p PID, --pid PID  only get information on process id
  --is-no-modules    do not report modules in processes
```

### os\_resume

Resume execution of a process on the endpoint.

**Platforms:**

```
usage: os_resume [-h] [-p PID] [-a PROCESSATOM] [-t TID]

optional arguments:
  -p PID, --pid PID     process id
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
  -t TID, --tid TID     thread id
```

### os\_services

List all services (Windows, launchctl on MacOS and initd on Linux).

**Platforms:**

```
usage: os_services [-h]
```

### os\_suspend

Suspend a process running on the endpoint.

**Platforms:**

```
usage: os_suspend [-h] [-p PID] [-a PROCESSATOM] [-t TID]

optional arguments:
  -p PID, --pid PID     process id
  -a PROCESSATOM, --processatom PROCESSATOM
                        the atom of the target process
  -t TID, --tid TID     thread id
```

### os\_users

List system users.

**Platforms:**

```
usage: os_users [-h]
```

### os\_version

Get detailed OS information on the endpoint.

**Platforms:**

```
usage: os_version [-h]
```

### put

Upload a payload to an endpoint without executing it.

**Platforms:**

```
usage: put [-h] --payload-name NAME [--payload-path PATH] [--is-ignore-cert]

optional arguments:
  --payload-name NAME  name of the payload to run
  --payload-path PATH  full path where to put the payload (including file name)
  --is-ignore-cert     if specified, the sensor will ignore SSL cert mismatch
```

**Report/Reply Event(s):**
`RECEIPT`
`CLOUD_NOTIFICATION`

Error Codes

A 200 `ERROR` code implies a successful `put` command, and will include the resulting file path. Any other error codes can be investigated [here](/v2/docs/reference-error-codes).

**Command Notes:**

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the sensor to pull the payload to execute from the cloud.

Unlike the main sensor transport (which uses a pinned certificate), the Payloads feature uses Google infrastructure and their public SSL certificates.

This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

**Example:**

Assume you have a payload named `sample-script.sh`, and you wanted to upload it to the `/tmp` folder on a remote system, keeping the same name:

```
put --payload-name "sample_script.sh" --payload-path "/tmp/sample_script.sh"
```

If successful, this action will yield the following `RECEIPT` event:

```
"details":{
    "event":{
        "ERROR":200
        "FILE_PATH":"/tmp/sample-script.sh"
    }
"routing" : {...}
```

### pcap\_ifaces

List the network interfaces available for capture on a host.

**Platforms:**

**Usage:**

```
pcap_ifaces [-h]
```

**Sample Output:**

```
{
  "INTERFACE": [
    {
      "IPV4": [
        "10.128.15.198"
      ],
      "IPV6": [
        "fe80::4001:aff:fe80:fc6"
      ],
      "NAME": "ens4"
    },
    {
      "IPV4": [
        "127.0.0.1"
      ],
      "IPV6": [
        "::1"
      ],
      "NAME": "lo"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "any"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "nflog"
    },
    {
      "IPV4": [],
      "IPV6": [],
      "NAME": "nfqueue"
    }
  ]
}
```

### reboot

Execute an immediate system reboot (no warnings and zero delay time)

**Platforms:**

```
usage: reboot --is-confirmed
```

### reg\_list

List the keys and values in a Windows registry key.

**Platforms:**

```
usage: reg_list [-h] reg

positional arguments:
  reg         registry path to list, must start with one of "hkcr", "hkcc", "hkcu", "hklm", "hku", e.g. "hklm\software"...
```

### rejoin\_network

Tells the sensor to allow network connectivity again (after it was segregated).

**Platforms:**

**Report/Reply Event:**
[REJOIN\_NETWORK](/v2/docs/reference-edr-events#rejoinnetwork)

**Usage:**

```
usage: rejoin_network [-h]
```

### restart

Forces the LimaCharlie agent to re-initialize. This is typically only useful when dealing with cloned sensor IDs in combination with the remote deletion of the identity file on disk.

**Platforms:**

### run

Execute a payload or a shell command on the sensor.

**Platforms:**

```
usage: run [-h] [--payload-name NAME] [--arguments ARGUMENTS]
           [--shell-command SHELLCMD] [--timeout TIMEOUT] [--is-ignore-cert][--interpreter INTERPRETER]

optional arguments:
  --payload-name NAME   name of the payload to run
  --arguments ARGUMENTS
                        arguments to run the payload with
  --shell-command SHELLCMD
                        shell command to run
  --timeout TIMEOUT     number of seconds to wait for payload termination
  --is-ignore-cert      if specified, the sensor will ignore SSL cert mismatch
                        while upload the log
  --interpreter INTERPRETER
specifies that the named payload should be executed with
a specific interpreter like "powershell"
```

Note on usage scenarios for the `--is-ignore-cert` flag: If the sensor is deployed on a host where built-in root CAs are not up to date or present at all, it may be necessary to use the `--is-ignore-cert` flag to allow the sensor to pull the payload to execute from the cloud.

Using Arguments

In some cases, using the `--arguments` parameter may result in an error. If so, insert a leading space into the provided arguments.

For example `--arguments ' -ano'`

Unlike the main sensor transport (which uses a pinned certificate), the Payloads feature uses Google infrastructure and their public SSL certificates.

This may sometimes come up in unexpected ways. For example fresh Windows Server installations do not have the root CAs for `google.com` enabled by default.

Some shell execution requires embedding quotes within the command, for example when executing powershell. Here’s an example:

```
run --shell-command "powershell.exe -command \"Get-MpComputerStatus | Select-Object AMRunningMode\""
```

The above starts `powershell.exe` and passes it the `-command` argument and the value of the `-command` is `"Get-MpComputerStatus | Select-Object AMRunningMode”`.

###

### seal

Instruct the sensor to harden itself from tampering. This capability protects against use cases such as local admin users attempting to uninstall the LimaCharlie service. Please note that sealed status is currently only reflected in `CONNECTED` and `SYNC` events.

Seal Availability

Supported on sensor version 4.29.0 or newer and currently only supported on Windows.

Important note: the `seal` direct sensor command is stateless, meaning it will not survive a reboot. For this reason, in almost all cases, you want to automate the change of status in D&R rules using the `seal` and `unseal` [response actions](/v2/docs/response-actions) instead of this task. Alternatively you can also use the REST API endpoint `{`SID`}/seal` to change the status in a way that survives reboots.

The `should_seal` Boolean parameter indicates whether a Sensor has yet to complete the `seal` command.

**Platforms:**

**Usage:**

```
usage: seal [--enable] [--disable]
```

**Sample Event:**
 On Sensors version 4.29.0 or newer, you will see the following metadata within `SYNC` or `CONNECTED` events:

```
{
 ... ,
 "SEAL_STATUS" : {
    "ERROR": 0,
    "IS_DISABLED": 1
    }
}
```

### segregate\_network

Tells the sensor to stop all network connectivity on the host except LC comms to the backend. So it's network isolation, great to stop lateral movement.

Note that you should never upgrade a sensor version while the network is isolated through this mechanism. Doing so may result in the agent not regaining connectivity to the cloud, requiring a reboot to undo.

This command primitive is NOT persistent, meaning a sensor you segregate from the network using this command alone, upon reboot will rejoin the network. To achieve isolation from the network in a persistent way, see the `isolate network` and `rejoin network` [Detection & Response rule actions](/v2/docs/response-actions).

**Platforms:**

**Report/Reply Event:**
[SEGREGATE\_NETWORK](/v2/docs/reference-edr-events#segregatenetwork)

**Usage:**

```
usage: segregate_network [-h]
```

### set\_performance\_mode

Turn on or off the high performance mode on a sensor. This mode is designed for very high performance servers requiring high IO throughout. This mode reduces the accuracy of certain events which in turn reduces impact on the system, and is not useful for the vast majority of hosts. You can read more about Performance Mode and its caveats [here](/v2/docs/ext-exfil#performance-rules).

**Platforms:**

**Usage:**

```
usage: set_performance_mode [-h] [--is-enabled]

optional arguments:
  --is-enabled  if specified, the high performance mode is enabled, otherwise
                disabled
```

### shutdown

Execute an immediate system shut down (no warnings and zero delay time)

**Platforms:**

```
usage: shutdown --is-confirmed
```

### uninstall

Uninstall the sensor from that host.

*For more information on Sensor uninstallation, including Linux systems, check* [*here*](/v2/docs/endpoint-agent-uninstallation)*.*

**Platforms:**

**Usage:**

```
usage: uninstall [-h] [--is-confirmed]

optional arguments:
  --is-confirmed  must be specified as a confirmation you want to uninstall
                  the sensor
```

### yara\_scan

Scan for a specific yara signature in memory and files on the endpoint.

**Platforms:**

**The memory component of the scan on MacOS may be less reliable due to recent limitations imposed by Apple.**

```
yara_scan [--pid PID] [--filePath FILEPATH] [--processExpr PROCESSEXPR] [--is-memory-only] [--is-no-validation] [--root-dir ROOT-DIR] [--file-exp FILE-EXP] [--depth DEPTH] RULE

Positional arguments:
  RULE                   rule to compile and run on sensor, Yara resource reference like "hive://yara/my-source,other-source", literal rule or "https://" URL or base64 encoded rule

Options:
  --pid PID, -p PID      pid of the process to scan [default: -1]
  --filePath FILEPATH, -f FILEPATH
                         path to the file scan
  --processExpr PROCESSEXPR, -e PROCESSEXPR
                         expression to match on to scan (matches on full process path)
  --is-memory-only       only scan the memory, ignore files on disk. [default: true]
  --is-no-validation     if specified, do not validate the rule before sending. [default: false]
  --root-dir ROOT-DIR, -r ROOT-DIR
                         the root directory where to begin the search for files to scan
  --file-exp FILE-EXP, -x FILE-EXP
                         a file name expression supporting basic wildcards like * and ? to match against files in the --root-dir [default: *]
  --depth DEPTH, -d DEPTH
                         optional maximum depth of the search for files to scan, defaults to a single level
```

### yara\_update

Update the compiled yara signature bundle that is being used for constant memory and file scanning on the sensor.

Note

Instead of using the `yara_update` command directly it is recommended to use [the YARA extension](/v2/docs/ext-yara) available through the web UI and REST interface.

**Platforms:**

```
usage: yara_update [-h] rule

positional arguments:
  rule        rule to compile and set on sensor for constant scanning, literal rule or "https://" URL or base64 encoded rule
```

### epp\_status

Get the current status of EPP on a sensor.

**Platforms:**

```
usage: epp_status [-h]
```

### epp\_scan

Scan a directory or file using the EPP on the sensor.

**Platforms:**

```
usage: epp_scan [-h] path

positional arguments:
  path        File or directory to scan
```

### epp\_list\_exclusions

List all the exclusions for EPP on a sensor.

**Platforms:**

```
usage: epp_list_exclusions [-h]
```

### epp\_add\_exclusion

Add a new exclusion to EPP on a sensor.

**Platforms:**

```
usage: epp_add_exclusion [-h] value [--type]

positional arguments:
  value        Value of the exclusion to add
optional arguments:
  --type  Type of exclusion. Options are: extension, path, process
```

### epp\_rem\_exclusion

Remove an exclusion for EPP on a sensor.

**Platforms:**

```
usage: epp_rem_exclusion [-h] value [--type]

positional arguments:
  value        Value of the exclusion to remove
optional arguments:
  --type  Type of exclusion. Options are: extension, path, process
```

### epp\_list\_quarantine

List quarantined EPP on a sensor.

**Platforms:**

```
usage: epp_list_quarantine [-h]
```

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, a Sensor ID (SID) is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

---

## Template Strings and Transforms

**Source:** https://docs.limacharlie.io/docs/template-strings-and-transforms

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

---

# Sensors

## Container Clusters

**Source:** https://docs.limacharlie.io/docs/container-clusters

# Requires an LC_INSTALLATION_KEY environment variable
# specifying the installation key value.
# Requires a HOST_FS environment variable that specifies where
# the host's root filesystem is mounted within the container
# like "/rootfs".
# Requires a NET_NS environment variable that specific where
# the host's namespaces directory is mounted within the container
# like "/netns".
# Example:
# export ENV HOST_FS=/rootfs
# docker run --privileged --net=host -v /:/rootfs:ro -v /var/run/docker/netns:/netns:ro --env HOST_FS=/rootfs --env NET_NS=/netns --env LC_INSTALLATION_KEY=your_key refractionpoint/limacharlie_sensor

FROM alpine

RUN mkdir lc
WORKDIR /lc

RUN wget https://downloads.limacharlie.io/sensor/linux/alpine64 -O lc_sensor
RUN chmod 500 ./lc_sensor

CMD ./lc_sensor -d -
```

And this is a sample Kubernetes `deployment` on

a cluster supporting eBPF (kernel > 5.7):

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lc-sensor
  namespace: lc-monitoring
  labels:
    app: lc-monitoring
spec:
  minReadySeconds: 30
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      app: lc-monitoring
  template:
    metadata:
      namespace: lc-monitoring
      labels:
        app: lc-monitoring
    spec:
      hostNetwork: true
      hostPID: true
      containers:
        - name: lc-sensor
          image: refractionpoint/limacharlie_sensor:latest
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: true
            privileged: true
            capabilities:
              add: ['CAP_SYS_ADMIN']
          resources:
            requests:
              memory: 128M
              cpu: 0.01
            limits:
              memory: 256M
              cpu: 0.9
          volumeMounts:
            - mountPath: /rootfs
              name: all-host
            - mountPath: /netns
              name: all-host-ns
            - mountPath: /sys/kernel/debug
              name: all-host-krnl
            - mountPath: /sys/kernel/btf
              name: btf
            - mountPath: /lib/modules
              name: libmodules
          env:
            - name: HOST_FS
              value: /rootfs
            - name: NET_NS
              value: /netns
            - name: LC_INSTALLATION_KEY
              value: <<<< YOUR INSTALLATION KEY GOES HERE >>>>
      volumes:
        - name: all-host
          hostPath:
            path: /
        - name: all-host-ns
          hostPath:
            path: /var/run/docker/netns
        - name: all-host-krnl
          hostPath:
            path: /sys/kernel/debug
        - name: btf
          hostPath:
            path: /sys/kernel/btf
        - name: libmodules
          hostPath:
            path: /lib/modules
```

a cluster not supporting eBPF (kernel < 5.7):

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lc-sensor
  namespace: lc-monitoring
  labels:
    app: lc-monitoring
spec:
  minReadySeconds: 30
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      app: lc-monitoring
  template:
    metadata:
      namespace: lc-monitoring
      labels:
        app: lc-monitoring
    spec:
      containers:
        - name: lc-sensor
          image: refractionpoint/limacharlie_sensor:latest
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: true
            privileged: true
          resources:
            requests:
              memory: 128M
              cpu: 0.01
            limits:
              memory: 256M
              cpu: 0.9
          volumeMounts:
            - mountPath: /rootfs
              name: all-host-fs
            - mountPath: /netns
              name: all-host-ns
          env:
            - name: HOST_FS
              value: /rootfs
            - name: NET_NS
              value: /netns
            - name: LC_INSTALLATION_KEY
              value: <<<< YOUR INSTALLATION KEY GOES HERE >>>>
      volumes:
        - name: all-host-fs
          hostPath:
            path: /
        - name: all-host-ns
          hostPath:
            path: /var/run/docker/netns
      hostNetwork: true
```

#### SELinux

On some hardened versions of Linux, certain file paths are prevented from loading `.so` (Shared Object) files. LimaCharlie requires a location where
 it can write `.so` files and load them. To enable this on hardened versions of Linux, you can specify a `LC_MOD_LOAD_LOC` environment variable containing
 a path to a valid directory for loading, like `/lc` for example. This environment variable needs to be set for the sensor executable (`rphcp`) at runtime.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Detecting Sensors No Longer Sending Data

**Source:** https://docs.limacharlie.io/docs/non-responding-sensors

# LimaCharlie D&R Rule to trigger this playbook
# every 30 minutes.
# detection:
#   target: schedule
#   event: 30m_per_org
#   op: exists
#   path: /
# response:
# - action: extension request
#   extension name: ext-playbook
#   extension action: run_playbook
#   extension request:
#     name: check-missing-data
#     credentials: hive://secret/playbook-missing-data-creds

SENSOR_SELECTOR = "plat == windows and `server` in tags"
DATA_WITHIN = 10 * 60 * 1000 # 10 minutes

def notify_missing_data(sdk: limacharlie.Limacharlie, sensor: limacharlie.Sensor):
    # TODO: Implement this, but it's optional if all you want is a detection
    # since those will be generated automatically.
    pass

def get_relevant_sensors(sdk: limacharlie.Limacharlie) -> list[limacharlie.Sensor]:
    sensors = sdk.sensors(selector=SENSOR_SELECTOR)
    relevant_sensors = []
    for sensor in sensors:
        relevant_sensors.append(sensor)
    return relevant_sensors

def playbook(sdk: limacharlie.Limacharlie, data: dict) -> dict | None:
    # Get the sensors we care about.
    relevant_sensors = get_relevant_sensors(sdk)

    stopped_sensors = []

    # For each sensor, check if we've received data within that time period.
    for sensor in relevant_sensors:
        # To do that we will get the data overview and see if a recent time stamp is present.
        data_overview = sensor.getHistoricOverview(int(time.time() - DATA_WITHIN), int(time.time()))
        after = int(time.time() * 1000) - DATA_WITHIN
        for timestamp in data_overview:
            if timestamp > after:
                print(f"Data received for sensor {sensor.sid} at {timestamp}")
                break
        else:
            print(f"No data received for sensor {sensor.sid} in the last {DATA_WITHIN} seconds")
            notify_missing_data(sdk, sensor)
            stopped_sensors.append(sensor)

    # Report a detection for stopped sensors.
    if stopped_sensors:
        return {"detection":{
            "stopped_sensors": [sensor.sid for sensor in stopped_sensors]
        }}
    return None
```

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Endpoint Agent Uninstallation

**Source:** https://docs.limacharlie.io/docs/endpoint-agent-uninstallation

# Detect
event: SYNC
op: is windows

# Respond
- action: task
  command: uninstall --is-confirmed
- action: add tag
  tag: uninstalled
```

## Package Management Tools

For Package Management tools, and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than installing from LimaCharlie. This will help keep software inventories up to date.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

---

## Payload Manager

**Source:** https://docs.limacharlie.io/docs/payload-manager

# Payload Manager

[Payloads](/v2/docs/payloads), such as scripts, pre-built binaries, or other files, can be deployed to LimaCharlie sensors for any reason necessary.

One method of adding payloads to an Organization is via the web UI on the payloads screen. This is suitable for ad-hoc payload needs, however does not scale past a handful of payloads, or for multiple organizations requiring access the same payload(s).

The payload manager allows you to create, maintain, and automatically create/update payloads within your organization(s). Furthermore, payload configurations can be saved and utilized across multiple organizations using LimaCharlie's Infrastructure as Code capabilities.

Payloads added in the payload manager will be synced once every 24 hours per org.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

# Tutorials

## Detection and Response Examples

**Source:** https://docs.limacharlie.io/docs/detection-and-response-examples

# Detection
op: ends with
event: NEW_PROCESS
path: event/FILE_PATH
value: .scr

# Response
- action: report
  name: susp_screensaver
- action: add tag
  tag: uses_screensaver
  ttl: 80000
```

### WanaCry

Simple WanaCry detection and mitigation rule:

```
# Detection
op: ends with
event: NEW_PROCESS
path: event/FILE_PATH
value: wanadecryptor.exe
case sensitive: false

# Response
- action: report
  name: wanacry
- action: task
  command: history_dump
- action: task
  command:
    - deny_tree
    - <<routing/this>>
```

### Classify Users

Tag any Sensor where the CEO logs in with "vip".

```
# Detection
op: is
event: USER_OBSERVED
path: event/USER_NAME
value: stevejobs
case sensitive: false

# Response
- action: add tag
  tag: vip
```

### SSH from External IP Address

The following example looks for connections to/from `sshd` involving a non-RFC1918 IP Address. Be mindful that this is only looking for network connections, not actual logons, so this could be noisy on an internet-facing system but still indicative of an exposed service.

```
# Detection
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: ends with
    path: event/FILE_PATH
    value: /sshd
  - op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS

 # Response
- action: report
  name: >-
    SSH from EXTERNAL IP - {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}
```

The `report` uses [Go Templates](/v2/docs/template-strings-and-transforms) to include the offending IP address in the detection name.

### RDP from External IP Address

Similar to the above SSH example, this example looks for RDP connections from an external IP address. Be mindful that this is only looking for network connections, not actual logons, so this could be noisy on an internet-facing system but still indicative of an exposed service.

```
# Detection
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: is
    path: event/FILE_PATH
    value: C:\WINDOWS\System32\svchost.exe
  - op: contains
    path: event/COMMAND_LINE
    value: TermService
  - op: is
    path: event/NETWORK_ACTIVITY/DESTINATION/PORT
    value: 3389
  - op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS

# Response
- action: report
  name: >-
    RDP from EXTERNAL IP - {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}
```

The `report` uses [Go Templates](/v2/docs/template-strings-and-transforms) to include the offending IP address in the detection name.

### Suspicious Windows Executable Names

```
# Detection
event: CODE_IDENTITY
op: matches
path: event/FILE_PATH
case sensitive: false
re: .*((\\.txt)|(\\.doc.?)|(\\.ppt.?)|(\\.xls.?)|(\\.zip)|(\\.rar)|(\\.rtf)|(\\.jpg)|(\\.gif)|(\\.pdf)|(\\.wmi)|(\\.avi)|( {5}.*))\\.exe

# Response
- action: report
  name: Executable with suspicious double extension
```

### Disable an Event at the Source

Turn off the sending of a specific event to the cloud. Useful to limit some verbose data sources when not needed.

```
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: exfil_del NEW_DOCUMENT
```

### Windows Event Logs

A simple example of looking for a specific Event ID in WEL events.

```
# Detection
event: WEL
op: and
rules:
  - op: is
    path: event/EVENT/System/EventID
    value: '4625'
  - op: is
    path: event/EVENT/System/Channel
    value: Security

# Response
- action: report
  name: Failed Logon
```

### Nested Logic

An example demonstrating nested boolean logic. This detection looks specifically for the following conditions:
 ((`4697` OR `7045`) in the `System` log) OR (`4698` in the `Security` log)

```
# Detection
event: WEL
op: or
rules:
  - op: and
    rules:
      - op: is
        path: event/EVENT/System/Channel
        value: System
      - op: or
        rules:
          - op: is
            path: event/EVENT/System/EventID
            value: '4697'
          - op: is
            path: event/EVENT/System/EventID
            value: '7045'
  - op: and
    rules:
      - op: is
        path: event/EVENT/System/Channel
        value: Security
      - op: is
        path: event/EVENT/System/EventID
        value: '4698'
```

### File Integrity Monitoring

#### Monitoring Sensitive Directories

Make sure the File Integrity Monitoring of some directories is enabled whenever Windows sensors connect.

```
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: fim_add --pattern 'C:\*\Programs\Startup\*' --pattern '\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*'
```

Similar example for a Linux web server.

```
# Detection
event: CONNECTED
op: is platform
name: linux

# Response
- action: task
  command: fim_add --pattern '/var/www/*'
```

#### FIM Hit Detection

Adding a FIM pattern with `fim_add` by itself will only cause `FIM_HIT` events to be generated on the affected system's timeline. To know that we have positive hits on a FIM rule, we want to capture the relevant event and generate a proper Detection.

```
# Detection
event: FIM_HIT
op: exists
path: event/FILE_PATH

# Response
- action: report
  name: FIM Hit - {{ .event.FILE_PATH }}
```

### YARA Scanning

Resource Utilization

Performing CPU intensive actions such as YARA scanning can impact endpoint performance if not optimized. Be sure to always test rules that carry out sensor commands (like the examples below) before deploying at scale in production. Use [suppression](/v2/docs/response-actions#suppression) to prevent runaway conditions.

Here are a few examples of using D&R rules to initiate automatic YARA scans on an endpoint. Note that the defined YARA rule must exist in your org before using it in a D&R rule.

#### YARA Scan Processes

This  example looks for `NEW_PROCESS` events that meet certain criteria, then initiates a YARA scan against the offending process ID in memory. Note, this or a similar D&R rule will also depend on a companion [YARA Detection](/v2/docs/detection-and-response-examples#yara-detections) rule.

```
# Detection
event: NEW_PROCESS
op: and
rules:
  - op: starts with
    path: event/FILE_PATH
    value: C:\Users\
  - op: contains
    path: event/FILE_PATH
    value: \Downloads\

# Response
## Report is optional, but informative
- action: report
  name: Execution from Downloads directory
## Initiate a sensor command to yara scan the PROCESS_ID
- action: task
  command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
  investigation: Yara Scan Process
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
      - Yara Scan Process
    max_count: 1
    period: 1m
```

Notice the use of `suppression` to prevent the same `PROCESS_ID` from being scanned more than once per minute to prevent a resource runaway situation.

#### YARA Scan Files

This  example looks for `NEW_DOCUMENT` events that meet certain criteria, then initiates a YARA scan against the offending file path. Note, this or a similar D&R rule will also depend on a companion [YARA Detection](/v2/docs/detection-and-response-examples#yara-detections) rule.

```
# Detection
event: NEW_DOCUMENT
op: and
rules:
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .\:\\(users|windows\\temp)\\.*
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .*\.(exe|dll)

# Response
## Report is optional, but informative
- action: report
  name: Executable written to Users or Temp (yara scan)
## Initiate a sensor command to yara scan the FILE_PATH
- action: task
  command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
  investigation: Yara Scan Executable
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
      - Yara Scan Executable
    max_count: 1
    period: 1m
```

Notice the use of `suppression` to prevent the same `FILE_PATH` from being scanned more than once per minute to prevent a resource runaway situation.

### YARA Detections

Running a YARA scan by itself only sends a `YARA_DETECTION` event to the affected system's timeline. To know that we have positive hits on a YARA scan, we want to capture the relevant event and generate a proper Detection. The following two examples split out a YARA detection on-disk, versus in-memory. Notice we simply check for the presence of `event/PROCESS/*` fields to determine if it's a file or process detection, which may have different severities to security teams (dormant malware versus running malware).

#### YARA Detection On-Disk (file)

```
# Detection
event: YARA_DETECTION
op: and
rules:
  - not: true
    op: exists
    path: event/PROCESS/*
  - op: exists
    path: event/RULE_NAME

# Response
- action: report
  name: YARA Detection on Disk - {{ .event.RULE_NAME }}
- action: add tag
  tag: yara_detection_disk
  ttl: 80000
```

#### YARA Detection In-Memory (process)

```
# Detection
event: YARA_DETECTION
op: and
rules:
  - op: exists
    path: event/RULE_NAME
  - op: exists
    path: event/PROCESS/*

# Response
- action: report
  name: YARA Detection in Memory - {{ .event.RULE_NAME }}
- action: add tag
  tag: yara_detection_memory
  ttl: 80000
```

Both rules will generate a Detection report and add a tag to the system which the detection occurred on.

### Mention of an Internal Resource

Look for references to private URLs in proxy logs.

```
# Detection
target: artifact
op: contains
path: /text
value: /corp/private/info

# Response
- action: report
  name: web-proxy-private-url
```

### De-duplicate Cloned Sensors

Sometimes users install a sensor on a VM image by mistake. This means every time a new instance of the image gets started the same sensor ID (SID) is used for multiple boxes with different names. When detected, LimaCharlie produces a `sensor_clone` event.

We can use these events to deduplicate. This example targets Windows clones.

```
# Detection
target: deployment
event: sensor_clone
op: is platform
name: windows

# Response
- action: re-enroll
```

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Log Collection Guide

**Source:** https://docs.limacharlie.io/docs/logcollectionguide

# Stream journalctl to syslog adapter
journalctl -f -q --output=json | nc localhost 514
```

**Method 2: Output to File and Monitor**

```
# Create a systemd service to write journal to file
sudo tee /etc/systemd/system/journal-export.service << EOF
[Unit]
Description=Export systemd journal to file
After=systemd-journald.service

[Service]
ExecStart=/usr/bin/journalctl -f -q --output=json
StandardOutput=append:/var/log/journal-export.json
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable journal-export.service
sudo systemctl start journal-export.service
```

Then monitor the file:

```
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "json"  # JSON format for structured data
    sensor_seed_key: "journalctl-logs"
    mapping:
      sensor_hostname_path: "_HOSTNAME"
      event_type_path: "_SYSTEMD_UNIT"
      event_time_path: "__REALTIME_TIMESTAMP"
  file_path: "/var/log/journal-export.json"
```

## Multi-File Collection

For collecting multiple log types simultaneously:

```
# /var/log/messages
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "system-logs"
  file_path: "/var/log/messages"

# Kernel logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "kernel-logs"
  file_path: "/var/log/kern.log"

# Audit logs
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "audit-logs"
  file_path: "/var/log/audit/audit.log"

# Web server logs (glob pattern for multiple files)
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "web-logs"
  file_path: "/var/log/nginx/*.log"
```

## Best Practices

* **Use JSON format when possible** - Modern logs often support JSON output, which provides better structure and parsing.
* **Configure appropriate Grok patterns** - Grok provides pre-built patterns for common log formats and is easier to maintain than regex. Use `parsing_grok` over `parsing_re` when possible.
* **Set sensor\_seed\_key appropriately** - Use descriptive names that identify the log source for easier management.
* **Monitor file permissions** - Ensure the adapter has read access to log files.
* **Use backfill carefully** - Only enable for initial historical data collection to avoid duplicates.
* **Implement proper field mapping** - Extract hostname, timestamps, and event types for better searchability.
* **Pattern testing** - Test Grok patterns against sample log lines before deployment. Common patterns include %{COMMONAPACHELOG}, %{SYSLOGTIMESTAMP}, and %{NGINXACCESS}.

## Troubleshooting

Common issues:

* **File permission errors**: Check that the adapter process has read access to log files
* **Parse failures**: Validate Grok patterns against actual log formats
* **Missing logs**: Verify file paths and glob patterns
* **Connection issues**: Check network connectivity and authentication credentials

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

