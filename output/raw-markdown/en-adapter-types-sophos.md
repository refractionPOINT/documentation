[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Sophos

* 07 Aug 2025
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Sophos

* Updated on 07 Aug 2025
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Overview

This Adapter allows you to connect to Sophos Central to fetch event logs.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `sophos`

* `tenantid`: your Sophos Central tenant ID
* `clientid`: your Sophos Central client ID
* `clientsecret`: your Sophos Central client secret
* `url`: your Sophos Central URL (ex: `https://api-us01.central.sophos.com`)

### Creating Your Credentials and Getting Your Tenant ID

Sophos documentation - <https://developer.sophos.com/getting-started-tenant>

1. Add a new credential [here](https://cloud.sophos.com/manage/config/settings/credentials)
2. Get your client ID and client secret from the credentials you just created
3. Get your JWT -- be sure to replace the values with the client ID and secret from the last step

   ```
   curl -XPOST -H "Content-Type:application/x-www-form-urlencoded" -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&scope=token" https://id.sophos.com/api/v2/oauth2/token
   ```

   Response content -- grab the `access_token` from the output:

   ```
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
4. Get your tenant ID -- you will need the `access_token` (JWT) from the last step.

   ```
   curl -XGET -H "Authorization: Bearer YOUR_JWT_HERE" https://api.central.sophos.com/whoami/v1
   ```

   Response content -- grab the `id` (`tenant_id`) and `dataRegion` (`url`) from the output. You will need these for your LimaCharlie Sophos adapter configuration.

   ```
   {
       "id": "57ca9a6b-885f-4e36-95ec-290548c26059",
       "idType": "tenant",
       "apiHosts": {
           "global": "https://api.central.sophos.com",
           "dataRegion": "https://api-us03.central.sophos.com"
       }
   }
   ```
5. Now you have all the pieces for your adapter:

   1. `client_id`
   2. `client_secret`
   3. `tenant_id`
   4. `url`

### Infrastructure as Code Deployment

```
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

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [Stdin](/docs/adapter-types-stdin)

Table of contents

+ [Overview](#overview)
+ [Deployment Configurations](#deployment-configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
