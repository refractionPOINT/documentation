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
| Windows service | A service has no console. Only errors that stop the adapter from starting are kept, in `lc_adapter.log` in the service's working directory (usually `C:\Windows\System32`). To see the full logs, stop the service and run the same command line in a console. |

**Cloud Adapters** have no console. LimaCharlie reports their errors in three places:

- **Platform Logs > Errors** in the web app, with the key `adapter/<adapter name>`. The CLI shows the same list with `limacharlie org errors`. Once you have fixed the cause, clear the entry with `limacharlie org dismiss-error --component adapter/<adapter name>`.
- The `last_error` and `last_error_ts` fields in the `sys_mtd` section of the adapter record, which you can see with `limacharlie cloud-adapter get --key <adapter name>`.
- The [`cloud_adapter_error`](../platform-events.md#cloud_adapter_error) deployment event, which you can match with a D&R rule.

**Both kinds** report problems with the data itself under the key `usp/<adapter hostname>` in **Platform Logs > Errors**: events that could not be processed, lines a regular expression did not match, and free tier throttling. See [Some events are missing or dropped](#some-events-are-missing-or-dropped).

## How do I read the adapter logs?

An adapter that starts and connects prints something like this:

```text
starting
loading config from file: config.yaml
found 1 configs to run
starting adapter: syslog
log deduplication enabled: repeats within 1m0s are summarized, set USP_LOG_NO_DEDUP=1 to disable
DBG Oct 29 12:00:00: usp-client connecting
DBG Oct 29 12:00:01: usp-client connected
Configs in use (syslog):
----------------------------------
...
----------------------------------
FLO Oct 29 12:00:10: last_ack=Oct 29 12:00:09 last_pressure=Oct 29 12:00:00
```

- `ERR`, `WRN` and `DBG` lines come from the adapter and its connection to LimaCharlie. Read the `ERR` lines first.
- The adapter prints a `FLO` line every 10 seconds. `last_ack` is the last time LimaCharlie confirmed receiving data. If it stops moving while the source is producing data, the data is not reaching LimaCharlie. `last_pressure` is the last time the adapter had to wait because too much of its data was still waiting to be confirmed by LimaCharlie. If it moves on every line, the adapter is reading faster than it can send and is falling behind.
- When LimaCharlie asks the adapter to slow down, the adapter logs `backing off N seconds`.
- The `Configs in use` block is the configuration the adapter loaded, either from the file or from the command-line arguments and environment variables, depending on which you used. Check it when a setting seems to be ignored. It contains your installation key and any source credentials, so remove them before you share the log. An adapter in [cloud mode](#an-adapter-in-cloud-mode-does-not-pick-up-my-changes) does not print it unless you add `show_config=true`.

Since adapter version 1.32.50, an `ERR`, `WRN` or `DBG` message that repeats is printed once, then summarized as `last message repeated N more time(s) between <time> and <time>: <message>` about once a minute. Each level is also limited to 3000 lines a minute, and a `log rate limit (3000/min) reached` line counts what was left out. This keeps a failure that retries in a loop from filling the disk. To print every line, set the environment variable `USP_LOG_NO_DEDUP=1`.

## The adapter exits right after starting

When an adapter can't start, it prints the error on stderr and exits with code 1. If the problem is with the arguments or the config file, it also prints the list of available options before the error.

| Error | Fix |
| --- | --- |
| `not enough arguments` | The first argument must be the adapter type (for example `syslog`), followed by either a config file or `key=value` options. |
| `unknown adapter_type: <name>` | The first argument is not an adapter type. Check the spelling against the [adapter types](../../2-sensors-deployment/adapters/index.md#adapter-types). |
| `os.Open(): ...` | The adapter could not read the config file. Check the path and its permissions. |
| `decoding error: json=... yaml=...` | The config file is not valid YAML or JSON. Check the indentation. |
| `error instantiating client: invalid mapping.parsing_re: ...` or `invalid mapping.parsing_grok: ...` | The parsing expression does not compile. |
| `error instantiating client: client_options: missing oid` (or `missing installation_key`, `missing platform`) | A required setting is missing. Only some adapter types check this before connecting. The others connect anyway, and LimaCharlie refuses them with one of the [errors below](#errors-returned-by-limacharlie). |

Other startup failures end with `error running adapter: ...` and the reason, for example a file the adapter can't read, a port already in use, or credentials the source refused.

Problems with the connection to LimaCharlie also stop the adapter if they happen on its first connection. Under systemd or Docker, the service's restart policy starts it again (the [systemd unit](../../2-sensors-deployment/adapters/as-a-service.md#linux-systemd) in our guide uses `Restart=always`). A Windows service created with `-install` is not restarted automatically; to have Windows restart it, run `sc failure <service_name> reset= 86400 actions= restart/60000`. Once an adapter has connected, it reconnects on its own every 5 seconds after a disconnection, logging `error reconnecting: ...` as a warning while it can't.

## The adapter does not connect to LimaCharlie

### Network access

The adapter needs outbound HTTPS (TCP 443) to two hosts:

- `api.limacharlie.io`, where the adapter looks up which datacenter your organization is in.
- Your organization's ingestion endpoint, which has the form `<id>.wss.limacharlie.io`. To find yours, run `limacharlie org urls` and look at the `lc_wss` value.

Adapters in `cloud` mode, which read their configuration from LimaCharlie, also fetch it from `api.limacharlie.io`.

Errors that point to the network:

- An error from the datacenter lookup: the adapter could not reach `api.limacharlie.io`.
- `site url for org not found`: LimaCharlie answered, but has no ingestion endpoint for this OID. Check the OID.
- `Dial(): ...`: the adapter could not open the connection to the ingestion endpoint. The text after it says why, for example a DNS failure, a timeout, or a refused connection.
- `x509: certificate signed by unknown authority`: something on the network is intercepting TLS. See [TLS inspection](#tls-inspection).

### Proxies

Since version 1.31.0, the adapter can send its data through an HTTP proxy that supports `CONNECT`:

```yaml
client_options:
  proxy:
    url: http://proxy.corp.example:3128
    username: lc-adapter   # optional
    password: <password>   # optional, required if username is set
```

If `client_options.proxy` is not set, the adapter uses the standard `HTTPS_PROXY` and `NO_PROXY` environment variables for its data. It does not use the endpoint agent's `LC_PROXY`.

Neither setting applies to the requests the adapter makes to `api.limacharlie.io`: the datacenter lookup, and the configuration fetch in `cloud` mode. Those connect directly. On a network where only the proxy can reach the internet:

- Allow direct access to `api.limacharlie.io`, or
- Skip the lookup by setting `client_options.dest_url` to `wss://<your lc_wss value>/usp`, for example `wss://0123456789abcdef.wss.limacharlie.io/usp`. This does not help an adapter in `cloud` mode, which still has to reach `api.limacharlie.io` for its configuration.

Errors from the proxy:

- `proxy returned status 407`: the proxy wants credentials. Put them in `client_options.proxy.username` and `client_options.proxy.password`. Credentials written inside the URL are ignored.
- `failed to connect to proxy`: the adapter could not reach the proxy itself.
- With a proxy configured, the adapter tries each connection 3 times before reporting an error.

### TLS inspection

The endpoint agent pins its certificate, but the adapter trusts the operating system's certificate store. A TLS-inspecting proxy therefore works if its CA certificate is installed on the adapter host. On Linux you can also point the adapter at a CA bundle with the `SSL_CERT_FILE` environment variable. In Docker, the image only has the standard public CAs, so mount your CA bundle into the container and set `SSL_CERT_FILE` to its path.

### Errors returned by LimaCharlie

When LimaCharlie refuses the connection, the adapter prints the reason in an `ERR` line. On the first connection, the adapter then exits.

| Error | Cause and fix |
| --- | --- |
| `lc installation key not authorized` | The installation key is missing, does not exist in this organization, or has a typo. It may have been deleted or belong to another organization, or the OID may be wrong. The key goes in `client_options.identity.installation_key`; use the key value itself, not its name or ID. |
| `temporary authorization failure, please retry` | A temporary problem on the LimaCharlie side. Start the adapter again, or let its service restart it. |
| `missing sensor seed key` | Set `client_options.sensor_seed_key`. |
| `unknown lc platform: <name>` | `client_options.platform` is missing (the name is empty) or is not a platform LimaCharlie knows. Check the spelling against the adapter type's documentation. |
| `invalid timezone "<name>": ...` | `client_options.mapping.event_time_timezone` is not an IANA timezone name such as `America/New_York`. |
| `only one of regex or grok can be set` | The mapping sets both `parsing_re` and `parsing_grok`. Keep one. |
| `too many indexing desc: ...` | Your `indexing` section has more entries than allowed. Remove some. |
| `failed to register` | LimaCharlie could not register the sensor. Start the adapter again; contact support if it does not clear. |

## The adapter is running but no data shows up

Work from the source to LimaCharlie:

1. **Is the adapter connected?** Look for `usp-client connected` in the logs, and check that `last_ack` in the `FLO` lines keeps moving.
2. **Does a sensor exist?** The adapter's sensor appears on its first event, not when the adapter starts. `limacharlie cloud-adapter sensors --key <record>` (or `external-adapter sensors`) lists the sensors an adapter created. If there are none, no event has reached LimaCharlie yet.
3. **Is the source producing data the adapter can read?** See [Errors from specific adapter types](#errors-from-specific-adapter-types). For cloud APIs (Okta, Microsoft 365, SentinelOne and so on), look for `ERR` lines from the adapter type. They usually show the HTTP status the vendor returned, for example 401 or 403 for credentials or permissions.
4. **Is the organization on the free tier?** See [Some events are missing or dropped](#some-events-are-missing-or-dropped).
5. **Are you looking at the right time range?** LimaCharlie stores events at their event time. If that time is wrong, the events are stored, just not where you are looking. See [Events have the wrong time](#events-have-the-wrong-time).

## Errors from specific adapter types

### Syslog

- Check that the device sends to the right port and protocol (`is_udp`), and that the host firewall lets the traffic in. In Docker, publish the port with the matching protocol, for example `-p 4404:4404/udp`.
- `ssl cannot be enabled for udp`: TLS is only supported with TCP.
- `tls handshake with <address> failed` warnings: a client tried to connect without TLS, or with a certificate the adapter does not accept.
- Over UDP, nothing tells the device to slow down. When the adapter falls behind (`last_pressure` moving on every `FLO` line), messages can be lost before the adapter reads them. Use TCP for high volumes.

### File

Check that the user running the adapter can read the file, and that new lines are being written to it.

### Windows Event Log

- `missing evt_sources, a csv of SOURCE-NAME:FILTER`: set `evt_sources`, for example `evt_sources=Security,System`. See [Windows Event Log](../../2-sensors-deployment/adapters/types/windows-event-log.md) for filters.
- `failed creating event subscription: ...`: Windows refused the subscription. Common causes are a channel name that does not exist, an invalid XPath filter, and an account that can't read that log. Run the adapter as an administrator, or with an account in the local Event Log Readers group.
- `wel (Windows Event Logs) collection not supported outside of Windows`: the `wel` type only runs on Windows. To read exported `.evtx` files elsewhere, use the [EVTX](../../2-sensors-deployment/adapters/types/evtx.md) adapter.

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

Each result shows the `event_type`, `event_time`, `hostname` and the parsed `json_payload`. A line that the regular expression does not match comes back with the whole line in `json_payload.text` and an empty `event_type`. For JSON sources, use `json_input` with a sample object instead of `text_input`. If the command fails with a generic `BACKEND_ERROR`, see [Common Validation Issues](../../2-sensors-deployment/adapters/usage.md#common-validation-issues).

See [Parsing and Mapping](../../2-sensors-deployment/adapters/usage.md#parsing-and-mapping) for the options and [Testing Parsing with Sample Data](../../2-sensors-deployment/adapters/usage.md#testing-parsing-with-sample-data) for the file format.

## Events have the wrong time

For most platforms, the time comes from the field named by `client_options.mapping.event_time_path`:

- A number is read as milliseconds since the epoch, or as seconds if milliseconds gives an impossible date.
- A string is parsed by recognizing common timestamp formats. If the string has no timezone, it is read as UTC unless you set `client_options.mapping.event_time_timezone`, for example `America/New_York`. Logs written in local time without a timezone appear shifted by your UTC offset until you set it.
- A timestamp without a year, like the classic syslog `Oct 29 12:00:00`, is placed at the most recent past occurrence of that date.
- A date before January 1st ten years ago, or after the end of next year, is rejected.

If there is no `event_time_path`, the field is missing, or the value is rejected, the event keeps the time at which the adapter read it.

Some platforms read the time from the record themselves, for example `cef` and `sentinel_one`. For those, the event has the record's own time even without an `event_time_path`.

## Some events are missing or dropped

**Events LimaCharlie could not process.** LimaCharlie drops the event and tells the adapter, which logs the cause in an `ERR` line right away. It also adds an entry under the key `usp/<adapter hostname>` in **Platform Logs > Errors**, at most once a minute per connection, for example `dropped 3 unprocessable record(s), last error: ...`. Test a sample of the failing data with `limacharlie usp validate` as shown above.

**Lines a regular expression did not match.** These are not dropped: they are stored with the whole line in a `text` field and no event type. LimaCharlie reports them under `usp/<adapter hostname>` as `regex pattern did not match payload (sample: "...", payload_size: N)`, or `grok pattern ...` for grok.

**Free tier throttling.** An organization on the free tier can only ingest a limited amount of adapter data per second. Above that, LimaCharlie slows the adapter down: the adapter logs `backing off N seconds`, and Platform Logs shows `adapter throttled to N bytes/s (free tier): data above this rate is held back at the source until the org is upgraded` under `usp/<adapter hostname>`. Data waits at the source while the adapter is held back. A source that can't wait, such as syslog over UDP, loses what it sends in the meantime. An adapter that ignores the slow-down is disconnected with `over throughput of N bytes/s for free tier, come back later`. Upgrading the organization lifts the limit.

**Restarts.** Data the adapter has read but LimaCharlie has not yet confirmed is kept in memory. When the adapter is stopped normally (Ctrl-C, `systemctl stop`, `docker stop`), it waits up to a minute for that data to be confirmed before exiting. If the process is killed, or that minute runs out, the unconfirmed data is lost.

## A Cloud Adapter keeps failing or was disabled

LimaCharlie retries a failing Cloud Adapter on its own. After a connection error, or when an adapter that was running fails, it retries about every 30 seconds. When an adapter fails to start for another reason, such as invalid credentials, the wait grows between attempts, up to about 5 minutes.

Every failed attempt updates the adapter's `last_error`, emits a `cloud_adapter_error` event and updates the entry in **Platform Logs > Errors**, unless the same error was recorded less than 30 seconds earlier. The exception is the connection errors that usually clear on their own, such as `Dial()` errors or `websocket: bad handshake`: they only appear in **Platform Logs > Errors** once they have lasted more than an hour. They still update `last_error` and emit the event.

After 24 hours of continuous failure, LimaCharlie disables the adapter, emits a [`cloud_adapter_disabled`](../platform-events.md#cloud_adapter_disabled) deployment event and adds an `adapter_disabled` entry to the audit log. It does not disable an adapter whose configuration was edited while it was failing.

To bring it back, fix the cause in the configuration, then enable it in the web app or with:

```bash
limacharlie cloud-adapter enable --key <adapter name>
```

The entry in **Platform Logs > Errors** ends with `(lc-host-ip: <address>)`. That is the public IP address the adapter's requests came from. Use it to check the vendor side when the source only accepts connections from allowed IP addresses.

To get an alert when an adapter is disabled, add a D&R rule on the `deployment` target:

```yaml
# Detection
target: deployment
event: cloud_adapter_disabled
op: exists
path: routing/oid

# Response
- action: report
  name: cloud-adapter-disabled
```

The rule fires once per disabled adapter. To hear about failures earlier, match `cloud_adapter_error` instead. That event fires on every failed attempt, so add a [suppression](../response-actions.md#suppression) to report each adapter at most once every few hours:

```yaml
# Detection
target: deployment
event: cloud_adapter_error
op: exists
path: routing/oid

# Response
- action: report
  name: cloud-adapter-error
  suppression:
    is_global: false
    keys:
      - '{{ .event.adapter_name }}'
    max_count: 1
    period: 6h
```

The two events name the adapter in different fields: `event/adapter` for `cloud_adapter_disabled` and `event/adapter_name` for `cloud_adapter_error`.

## An adapter in cloud mode does not pick up my changes

An on-prem adapter started with `cloud conf_guid=... oid=...` checks its record in LimaCharlie every minute and restarts with the new configuration when it changes. The logs show `stopping previous adapter` and `starting new adapter` when it applies a change. If they don't:

- Check that `conf_guid` is the record's `GUID` from `sys_mtd`, and that `oid` is the organization the record is in.
- Check that the adapter can reach `api.limacharlie.io` directly. It does not use a proxy for this, see [Proxies](#proxies).
- The adapter does not print the configuration it received. Add `show_config=true` to its command line to see it.

## New sensors appear, or old ones go offline

The Sensor ID of an adapter comes from the OID, `client_options.sensor_seed_key` and, for adapters that create one sensor per device, the sensor key. See [Sensor IDs](../../2-sensors-deployment/adapters/usage.md#sensor-ids). Changing any of them creates new sensors, and the old ones stop receiving data and show as offline. Changing the installation key alone keeps the same sensors.

If you deleted an adapter's sensor and it came back, see [Deleting an Adapter's Sensor](../../2-sensors-deployment/adapters/usage.md#deleting-an-adapters-sensor).

An adapter sensor shows as online while the adapter is connected, even if its source has stopped sending logs. To be alerted when data stops, see [Alerting on sensors that stop sending data](../../2-sensors-deployment/troubleshooting/non-responding-sensors.md).

## The healthcheck says OK but no data arrives

The `healthcheck` option starts an HTTP server that answers `{"status": "ok"}` while the adapter process is running. It does not check the connection to LimaCharlie or to the source. Use it to restart a crashed container, and use the `FLO` lines or a [data-based alert](../../2-sensors-deployment/troubleshooting/non-responding-sensors.md) to know whether data is flowing.

## Additional help

If these steps do not help, get in touch with us through the [Community Site](https://community.limacharlie.com/) or at `support@limacharlie.io`. Include the adapter type and version, how it runs (on-prem, Docker, service or Cloud Adapter), and the `ERR` lines or Platform Logs error. Remove installation keys, API keys and other credentials before you send logs.
