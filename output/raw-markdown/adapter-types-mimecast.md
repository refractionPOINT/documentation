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

Mimecast

* 07 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Mimecast

* Updated on 07 Aug 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Overview

This Adapter allows you to connect to the Mimecast API to stream audit events as they happen.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `mimecast`

* `client_id`: your Mimecast client ID
* `client_secret`: your Mimecast client secret

### CLI Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment#adapter-binaries).

```
chmod +x /path/to/lc_adapter

/path/to/lc_adapter mimecast client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_options.mappings.event_type_path=category \
client_id=$CLIENT_ID client_secret=$CLIENT_SECRET
```

### Infrastructure as Code Deployment

```
# Mimecast Specific Docs: https://docs.limacharlie.io/docs/adapter-types-mimecast
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/mimecast-client-id"
#   client_secret: "hive://secret/mimecast-client-secret"

sensor_type: "mimecast"
mimecast:
  client_id: "hive://secret/mimecast-client-id"
  client_secret: "hive://secret/mimecast-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_MIMECAST"
    hostname: "mimecast-logs-adapter"
    platform: "json"
    sensor_seed_key: "mimecast-audit-sensor"
    mapping:
      sensor_hostname_path: "sender"
      event_type_path: "eventType"
      event_time_path: "eventTime"
    indexing: []
```

## API Doc

See the official [documentation](https://developer.services.mimecast.com/docs/auditevents/1/routes/api/audit/get-audit-events/post).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

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

###### Related articles

* [Adapter Usage](/docs/adapter-usage)
* [Adapter Deployment](/docs/adapter-deployment)
* [Adapter Examples](/docs/adapter-examples)
* [Okta](/docs/ext-cloud-cli-okta)

---

###### What's Next

* [Okta](/docs/adapter-types-okta)

Table of contents

+ [Overview](#overview)
+ [Deployment Configurations](#deployment-configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
