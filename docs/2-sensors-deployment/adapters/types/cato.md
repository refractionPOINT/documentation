# Cato

## Overview

This adapter connects to the Cato API and fetches logs from the [events feed](https://support.catonetworks.com/hc/en-us/articles/360019839477-Cato-API-EventsFeed-Large-Scale-Event-Monitoring).

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter uses.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

Adapter Type: `cato`

- `apikey`: your CATO API key/token
- `accountid`: your CATO account ID

### Manual Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter cato client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
apikey=$API_KEY \
accountid=$ACCOUNT_ID
```

## API Doc

See the official [Cato API Events Feed documentation](https://support.catonetworks.com/hc/en-us/articles/360019839477-Cato-API-EventsFeed-Large-Scale-Event-Monitoring).
