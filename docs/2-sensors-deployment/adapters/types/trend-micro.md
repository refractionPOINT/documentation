# Trend Micro Vision One

## Overview

This Adapter allows you to connect to the [Trend Micro Vision One](https://automation.trendmicro.com/xdr/home) (XDR) API to fetch Workbench alerts.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `trendmicro` for the CLI adapter, `trend_micro` for the cloud sensor. The name differs by deployment method:

- CLI adapter type: `trendmicro`, like `./lc_adapter trendmicro ...`, with the options under a `trendmicro:` block in a config file.
- Cloud sensor (Infrastructure as Code): `sensor_type: "trend_micro"`, with the options under a `trend_micro:` block.

The options are the same in both cases.

- `api_token`: your Trend Micro Vision One API key (sent as a Bearer token).
- `region`: the Vision One data region your tenant lives in. One of `us` (default), `eu`, `sg`, `jp`, `in`, `au`.
- `url`: optional override for the Vision One API root, like `https://api.xdr.trendmicro.com`. When empty, the root comes from `region`.

The `region` selects the API base URL:

| Region | Base URL |
| --- | --- |
| `us` | `https://api.xdr.trendmicro.com` |
| `eu` | `https://api.eu.xdr.trendmicro.com` |
| `sg` | `https://api.sg.xdr.trendmicro.com` |
| `jp` | `https://api.xdr.trendmicro.co.jp` |
| `in` | `https://api.in.xdr.trendmicro.com` |
| `au` | `https://api.au.xdr.trendmicro.com` |

The adapter polls `<base_url>/v3.0/workbench/alerts` every 60 seconds. The first poll looks back 24 hours.

### Getting Your Credentials

1. In the Vision One console, go to **Administration → API Keys**.
2. Create an API key with a role that grants read access to the Workbench.
3. Copy the generated **Authentication token** — this is your `api_token`.

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter trendmicro client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=trend_micro \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
api_token=$API_TOKEN \
region=us
```

### Infrastructure as Code Deployment

```yaml
# For cloud sensor deployment, store the token as a hive secret:

#   api_token: "hive://secret/trendmicro-api-token"

sensor_type: "trend_micro"
trend_micro:
  api_token: "hive://secret/trendmicro-api-token"
  region: "us"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_TRENDMICRO"
    hostname: "trendmicro-vision-one-adapter"
    platform: "trend_micro"
    sensor_seed_key: "trendmicro-sensor"
```

## API Doc

See the official [Trend Micro Vision One API documentation](https://automation.trendmicro.com/xdr/home).
