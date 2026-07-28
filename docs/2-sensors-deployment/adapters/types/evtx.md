# EVTX

## Overview

This Adapter converts a `.evtx` file and ingests it into LimaCharlie. A `.evtx` file uses the binary format that Microsoft applies to Windows Event Logs. Use this adapter to ingest historical Windows Event Logs, for example during an Incident Response (IR) engagement.

To collect Windows Event Logs in real time, see the [Windows Event Logs](../../tutorials/windows-event-logs.md) documentation.

## Configurations

Adapter Type: `evtx`

- `client_options`: see [common adapter configuration](../usage.md).
- `file_path`: the path to the `.evtx` file to ingest.
- `write_timeout_sec`: the number of seconds before a write to LimaCharlie times out (default: 600).

### Configuration File Example

```yaml
evtx:
  file_path: "C:\\Evidence\\Security.evtx"
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "wel"
    sensor_seed_key: "ir-evidence-01"
    hostname: "compromised-host"
```

### CLI Deployment

Get the [Adapter downloads](../deployment.md) from the deployment page.

```bash
/path/to/lc_adapter evtx \
  file_path=/path/to/Security.evtx \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.identity.oid=$OID \
  client_options.platform=wel \
  client_options.sensor_seed_key=ir-evidence-01 \
  client_options.hostname=compromised-host
```

## API Doc

See the [unofficial documentation on EVTX](https://www.giac.org/paper/gcia/2999/evtx-windows-event-logging/115806).
