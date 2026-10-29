# FAQ - Adapter Troubleshooting

This page covers [Adapters](../../2-sensors-deployment/adapters/index.md) that you run yourself (on-prem, in Docker, or as a service) and Cloud Adapters that LimaCharlie runs for you. For the endpoint agent, see [Sensor Troubleshooting](troubleshooting.md).

## Where do I find adapter errors?

It depends on where the adapter runs.

**On-prem adapters** write their logs to the console: errors go to stderr, everything else to stdout. Where that ends up depends on how you run it:

| How the adapter runs | Where to read its logs |
| --- | --- |
| In a terminal | The terminal itself. |
| systemd service | `journalctl -u <service-name> -f` |
| Docker | `docker logs -f <container>` |
| Windows service | A service has no console, so only startup errors are kept, in `lc_adapter.log` in the service's working directory (usually `C:\Windows\System32`). To see the full logs, stop the service and run the same command line in a console. |

**Cloud Adapters** have no console. LimaCharlie reports their errors in three places:

- **Platform Logs > Errors** in the web app, with the key `adapter/<adapter name>`. The CLI shows the same list with `limacharlie org errors`. Once you have fixed the cause, clear the entry with `limacharlie org dismiss-error --component adapter/<adapter name>`.
- The `last_error` and `last_error_ts` fields in the `sys_mtd` section of the adapter record. `limacharlie cloud-adapter get --key <adapter name>` shows them.
- The [`cloud_adapter_error`](../platform-events.md#cloud_adapter_error) deployment event, which you can match with a D&R rule.

**Both kinds** report events that the cloud could not process under the key `usp/<adapter hostname>` in **Platform Logs > Errors**. See [Some events are missing or dropped](#some-events-are-missing-or-dropped).

## How do I read the adapter logs?

A healthy adapter that starts and connects prints something like this:

```text
starting
loading config from file: config.yaml
found 1 configs to run
starting adapter: syslog
Configs in use (syslog):
----------------------------------
...
----------------------------------
DBG Oct 29 12:00:00: usp-client connecting
DBG Oct 29 12:00:01: usp-client connected
FLO Oct 29 12:00:10: last_ack=Oct 29 12:00:09 last_pressure=Oct 29 12:00:00
```

- `ERR`, `WRN` and `DBG` lines come from the adapter and its connection to LimaCharlie. `ERR` lines are the ones to read first.
- The adapter prints a `FLO` line every 10 seconds. `last_ack` is the last time LimaCharlie confirmed receiving data. If it stops moving while the source is producing data, the data is not reaching LimaCharlie. `last_pressure` is the last time LimaCharlie asked the adapter to slow down. An occasional update is normal, but if it moves on every line, the adapter is sending more than its connection can take and is falling behind.
- The `Configs in use` block is the configuration the adapter actually loaded, after merging the file, command-line arguments and environment variables. Check it first when a setting seems to be ignored. It contains your installation key and any source credentials, so remove them before you share the log.

Since adapter version 1.32.50, a message that repeats is printed once, then summarized as `last message repeated N more time(s)` about once a minute. This keeps a failure that retries in a loop from filling the disk. To print every line, set the environment variable `USP_LOG_NO_DEDUP=1`.

## The adapter exits right after starting

The adapter checks its configuration before connecting. When a check fails, it prints the list of available options followed by an error on the last line. The common ones:

| Error | Fix |
| --- | --- |
| `not enough arguments` | The first argument must be the adapter type (for example `syslog`), followed by either a config file or `key=value` options. |
| `missing oid` | Set `client_options.identity.oid`. |
| `missing installation_key` | Set `client_options.identity.installation_key`. |
| `missing platform` | Set `client_options.platform`, for example `text`, `json` or `cef`. |
| `os.Open(): ...` | The adapter could not read the config file. Check the path and its permissions. |
| `decoding error: json=... yaml=...` | The config file is not valid YAML or JSON. Check the indentation. |
| `invalid mapping.parsing_re: ...` or `invalid mapping.parsing_grok: ...` | The parsing expression does not compile. |
| `proxy URL must not contain credentials ...` | Put the proxy user and password in `client_options.proxy.username` and `client_options.proxy.password`, not in the URL. |

If the adapter starts but the source part fails (a file it cannot read, a port already in use, bad cloud credentials), the error names the adapter type, for example `error running adapter: ...`.

## The adapter does not connect to LimaCharlie

### Network access

The adapter needs outbound HTTPS (TCP 443) to two hosts:

- `api.limacharlie.io`, where the adapter looks up which datacenter your organization is in.
- Your organization's ingestion endpoint, which has the form `<id>.wss.limacharlie.io`. To find yours, run `limacharlie org urls` and look at the `lc_wss` value.

Adapters that use the `cloud` mode (configuration stored in LimaCharlie) also read their configuration from `api.limacharlie.io`.

Errors that point to the network:

- `site url for org not found`, or an error while looking up the URL: the adapter could not reach `api.limacharlie.io`, or the OID is wrong.
- `Dial(): ...`: the adapter could not open the connection to the ingestion endpoint. The text after it says why, for example a DNS failure, a timeout, or a refused connection.
- `x509: certificate signed by unknown authority`: something on the network is intercepting TLS. See below.

### Proxies

Since version 1.31.0, the adapter can connect through an HTTP proxy that supports `CONNECT`:

```yaml
client_options:
  proxy:
    url: http://proxy.corp.example:3128
    username: lc-adapter   # optional
    password: <password>   # optional, required if username is set
```

With a proxy configured, the adapter tries each connection 3 times before reporting an error. A `proxy returned status 407` error means the proxy wants credentials. `failed to connect to proxy` means the adapter could not reach the proxy itself.

If `client_options.proxy` is not set, the adapter uses the standard `HTTPS_PROXY` and `NO_PROXY` environment variables. It does not use the endpoint agent's `LC_PROXY`.

### TLS inspection

The endpoint agent pins its certificate, but the adapter trusts the operating system's certificate store. A TLS-inspecting proxy therefore works if its CA certificate is installed on the adapter host. On Linux you can also point the adapter at a CA bundle with the `SSL_CERT_FILE` environment variable. In Docker, the image only has the standard public CAs, so mount your CA bundle into the container and set `SSL_CERT_FILE` to its path.

### Errors returned by LimaCharlie

When LimaCharlie refuses the connection, the adapter prints the reason in an `ERR` line:

| Error | Cause and fix |
| --- | --- |
| `lc installation key not authorized` | The installation key does not exist in this organization. It was deleted, or it belongs to another organization, or there is a typo in the key or the OID. The key goes in `client_options.identity.installation_key`; use the key value itself, not its name or ID. |
| `temporary authorization failure, please retry` | A temporary problem on the LimaCharlie side. The adapter retries on its own. |
| `missing sensor seed key` | Set `client_options.sensor_seed_key`. |
| `unknown lc platform: <name>` | The value of `client_options.platform` is not a platform LimaCharlie knows. Check the spelling against the adapter type's documentation. |
| `too many indexing desc: ...` | Your `indexing` section has more entries than allowed. Remove some. |
| `failed to register` | LimaCharlie could not register the sensor. The adapter retries; contact support if it does not clear. |
| `over throughput of N bytes/s for free tier, come back later` | The organization is on the free tier and the adapter sends more data than the free tier allows. LimaCharlie disconnects it. Upgrading the organization lifts the limit. |

## The adapter is running but no data shows up

Work from the source to LimaCharlie:

1. **Is the adapter connected?** Look for `usp-client connected` in the logs, and check that `last_ack` in the `FLO` lines keeps moving.
2. **Does a sensor exist?** The adapter's sensor appears on its first event, not when the adapter starts. `limacharlie cloud-adapter sensors --key <record>` (or `external-adapter sensors`) lists the sensors an adapter created. If there are none, no event has reached LimaCharlie yet.
3. **Is the source producing data the adapter can read?** For example:
    - `syslog`: check that the device sends to the right port and protocol (`is_udp`), and that the host firewall lets the traffic in. When running in Docker, publish the port with the matching protocol, for example `-p 4404:4404/udp`.
    - `file`: check that the user running the adapter can read the file and that new lines are being written to it.
    - Cloud APIs (Okta, Microsoft 365, SentinelOne and so on): look for `ERR` lines from the adapter type. They usually show the HTTP status the vendor returned, for example 401 or 403 for credentials or permissions.
4. **Are you looking at the right time range?** LimaCharlie stores events at the time read from `client_options.mapping.event_time_path`. If that time is wrong, the events are stored, just not where you are looking. See [Events have the wrong time](#events-have-the-wrong-time).

## Events are not parsed the way I expect

Test the mapping against sample data before you change the adapter. `limacharlie usp validate` runs sample input through the same parsing as live data and shows the events it produces. Put the `mapping` section from your adapter config and some sample lines in one file:

```yaml
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

Each result shows the `event_type`, `event_time`, `hostname` and the parsed `json_payload`. An empty `results` list means nothing parsed, which usually means the regular expression does not match the lines. For JSON sources, use `json_input` with a sample object instead of `text_input`.

See [Parsing and Mapping](../../2-sensors-deployment/adapters/usage.md#parsing-and-mapping) for the options.

## Events have the wrong time

The time comes from the field named by `client_options.mapping.event_time_path`:

- A number is read as milliseconds since the epoch, or as seconds if milliseconds gives an impossible date.
- A string is parsed by recognizing common timestamp formats. If the string has no timezone, it is read as UTC unless you set `client_options.mapping.event_time_timezone`, for example `America/New_York`. Logs written in local time without a timezone appear shifted by your UTC offset until you set it.
- If there is no `event_time_path`, the field is missing, or the value can't be parsed, or the date is more than 10 years in the past or more than a year in the future, the event keeps the time at which the adapter read it.

## Some events are missing or dropped

If LimaCharlie receives an event it can't process, it drops that event and records an error under the key `usp/<adapter hostname>` in **Platform Logs > Errors**, for example `dropped 3 unprocessable record(s), last error: ...`. The error text names the cause. Test a sample of the failing data with `limacharlie usp validate` as shown above.

## A Cloud Adapter keeps failing or was disabled

A Cloud Adapter that fails is restarted every 30 seconds or so, and the error is recorded as described in [Where do I find adapter errors?](#where-do-i-find-adapter-errors). Connection errors that usually clear on their own, such as a dropped connection during maintenance, only appear in **Platform Logs > Errors** if they last more than an hour.

After 24 hours of continuous failure, LimaCharlie disables the adapter and emits a [`cloud_adapter_disabled`](../platform-events.md#cloud_adapter_disabled) deployment event. It does not disable an adapter whose configuration was edited while it was failing.

To bring it back, fix the cause in the configuration, then enable it in the web app or with:

```bash
limacharlie cloud-adapter enable --key <adapter name>
```

The error recorded for a Cloud Adapter ends with `(lc-host-ip: <address>)`. That is the public IP address the adapter's requests came from. Use it to check the vendor side when the source only accepts connections from allowed IP addresses.

To get an alert when an adapter is disabled, add a D&R rule on the `deployment` target:

```yaml
# Detection
target: deployment
event: cloud_adapter_disabled
op: exists
path: event/adapter

# Response
- action: report
  name: cloud-adapter-disabled
```

Use `cloud_adapter_error` as the event instead to be told about every new error.

## An adapter in cloud mode does not pick up my changes

An on-prem adapter started with `cloud conf_guid=... oid=...` checks its record in LimaCharlie every minute and restarts with the new configuration when it changes. The logs show `stopping previous adapter` and `starting new adapter` when it applies a change. If they don't:

- Check that `conf_guid` is the record's `GUID` from `sys_mtd`, and that `oid` is the organization the record is in.
- Check that the adapter can reach `api.limacharlie.io`.
- The adapter does not print the configuration it received. Add `show_config=true` to its command line to see it.

## New sensors appear, or old ones go offline

The Sensor ID of an adapter comes from the OID, `client_options.sensor_seed_key` and, for adapters that create one sensor per device, the sensor key. See [Sensor IDs](../../2-sensors-deployment/adapters/usage.md#sensor-ids). Changing any of them creates new sensors, and the old ones stop receiving data and show as offline. Changing the installation key alone keeps the same sensors.

If you deleted an adapter's sensor and it came back, see [Deleting an Adapter's Sensor](../../2-sensors-deployment/adapters/usage.md#deleting-an-adapters-sensor).

An adapter sensor shows as online while the adapter is connected, even if its source has stopped sending logs. To be alerted when data stops, see [Alerting on sensors that stop sending data](../../2-sensors-deployment/troubleshooting/non-responding-sensors.md).

## The healthcheck says OK but no data arrives

The `healthcheck` option starts an HTTP server that answers `{"status": "ok"}` while the adapter process is running. It does not check the connection to LimaCharlie or to the source. Use it to restart a crashed container, and use the `FLO` lines or a [data-based alert](../../2-sensors-deployment/troubleshooting/non-responding-sensors.md) to know whether data is flowing.

## Additional help

If these steps do not help, get in touch with us through the [Community Site](https://community.limacharlie.com/) or at `support@limacharlie.io`. Include the adapter type, how it runs (on-prem, Docker, service or Cloud Adapter), and the `ERR` lines or Platform Logs error. Remove installation keys, API keys and other credentials before you send logs.
