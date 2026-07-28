# Sophos

## Overview

This Adapter connects to Sophos Central to fetch event logs.

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or if you create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name, see below.

### Adapter-specific Options

Adapter Type: `sophos`

- `tenantid`: your Sophos Central tenant ID
- `clientid`: your Sophos Central client ID
- `clientsecret`: your Sophos Central client secret
- `url`: your Sophos Central URL (ex: `https://api-us01.central.sophos.com`)

### Creating Your Credentials and Getting Your Tenant ID

Sophos documentation - <https://developer.sophos.com/getting-started-tenant>

1. Add a new credential in [Sophos Central Settings → Credentials](https://cloud.sophos.com/manage/config/settings/credentials)
2. Get your client ID and client secret from the credentials that you created
3. Get your JWT. Replace the values with the client ID and secret from the last step

   ```bash
   curl -XPOST -H "Content-Type:application/x-www-form-urlencoded" -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&scope=token" https://id.sophos.com/api/v2/oauth2/token
   ```

   Response content. Take the `access_token` from the output:

   ```json
   {
      "access_token": "SAVE_THIS_VALUE",
      "errorCode": "success",
      "expires_in": 3600,
      "message": "OK",
      "refresh_token": "<token>",
      "token_type": "bearer",
      "trackingId": "<uuid>"
   }
   ```

4. Get your tenant ID. You need the `access_token` (JWT) from the last step.

   ```bash
   curl -XGET -H "Authorization: Bearer YOUR_JWT_HERE" https://api.central.sophos.com/whoami/v1
   ```

   Response content. Take the `id` (`tenant_id`) and the `dataRegion` (`url`) from the output. You need these values for the configuration of your LimaCharlie Sophos adapter.

   ```json
   {
       "id": "57ca9a6b-885f-4e36-95ec-290548c26059",
       "idType": "tenant",
       "apiHosts": {
           "global": "https://api.central.sophos.com",
           "dataRegion": "https://api-us03.central.sophos.com"
       }
   }
   ```

5. You now have all the values for your adapter:

   1. `client_id`
   2. `client_secret`
   3. `tenant_id`
   4. `url`

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   clientid: "hive://secret/sophos-client-id"
#   clientsecret: "hive://secret/sophos-client-secret"
#   tenantid: "hive://secret/sophos-tenant-id"

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
