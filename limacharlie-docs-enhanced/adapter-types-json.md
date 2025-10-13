## Overview

This Adapter allows you to ingest logs from a file as JSON.

Adapter type: `file`

## Configuration

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

## Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment).

```
chmod +x /path/to/lc_adapter

/path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
file_path=/path/to/file
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.
