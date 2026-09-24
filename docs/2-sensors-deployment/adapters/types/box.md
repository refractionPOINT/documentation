# Box

## Overview

This Adapter allows you to connect to the [Box Events API](https://developer.box.com/reference/get-events/) to fetch your enterprise's admin event logs (the `admin_logs` stream — logins, uploads/downloads, sharing, admin actions, etc.).

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `box`

- `client_id`: your Box app's Client ID.
- `client_secret`: your Box app's Client Secret.
- `subject_id`: your Box **Enterprise ID** — the adapter authenticates as the enterprise (`box_subject_type=enterprise`).

The adapter authenticates with the OAuth2 Client Credentials Grant (CCG) against `https://api.box.com/oauth2/token` and polls `https://api.box.com/2.0/events?stream_type=admin_logs`.

### Getting Your Credentials

1. In the [Box Developer Console](https://app.box.com/developers/console), create a **Custom App** with **Server Authentication (Client Credentials Grant)**.
2. Under the app's **Configuration**, copy the **Client ID** and **Client Secret**, and enable the **Manage enterprise properties** application scope (required to read the `admin_logs` event stream).
3. A Box admin must **authorize** the app under **Admin Console → Apps → Custom Apps Manager** (using the app's Client ID).
4. Your `subject_id` is the **Enterprise ID**, found in **Admin Console → Account & Billing**.

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/box-client-id"
#   client_secret: "hive://secret/box-client-secret"

sensor_type: "box"
box:
  client_id: "hive://secret/box-client-id"
  client_secret: "hive://secret/box-client-secret"
  subject_id: "1234567"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_BOX"
    hostname: "box-adapter"
    platform: "box"
    sensor_seed_key: "box-sensor"
```

## API Doc

See the official [documentation](https://developer.box.com/reference/get-events/).
