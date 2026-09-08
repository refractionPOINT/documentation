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

Adapter Type: `trendmicro`

- `api_token`: your Trend Micro Vision One API key (sent as a Bearer token).
- `region`: the Vision One data region your tenant lives in. One of `us` (default), `eu`, `sg`, `jp`, `in`, `au`.

The `region` selects the API base URL:

| Region | Base URL |
| --- | --- |
| `us` | `https://api.xdr.trendmicro.com` |
| `eu` | `https://api.eu.xdr.trendmicro.com` |
| `sg` | `https://api.sg.xdr.trendmicro.com` |
| `jp` | `https://api.xdr.trendmicro.co.jp` |
| `in` | `https://api.in.xdr.trendmicro.com` |
| `au` | `https://api.au.xdr.trendmicro.com` |

The adapter polls `<base_url>/v3.0/workbench/alerts`.

### Getting Your Credentials

1. In the Vision One console, go to **Administration → API Keys**.
2. Create an API key with a role that grants read access to the Workbench.
3. Copy the generated **Authentication token** — this is your `api_token`.

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store the token as a hive secret:

#   api_token: "hive://secret/trendmicro-api-token"

sensor_type: "trendmicro"
trendmicro:
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
