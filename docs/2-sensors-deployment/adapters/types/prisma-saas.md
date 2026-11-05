# Palo Alto SaaS Security (Prisma SaaS)

## Overview

This Adapter ingests events from [Palo Alto Networks SaaS Security](https://docs.paloaltonetworks.com/saas-security) (formerly Prisma SaaS) into LimaCharlie using the SaaS Security **Log Events API**. Activity monitoring, incident, remediation, policy violation and admin audit events are forwarded in their original JSON form — the adapter does not reshape payloads.

The adapter authenticates with an API client (OAuth 2.0 client credentials) and long-polls the Log Events API. Each event is delivered to LimaCharlie as soon as Palo Alto Networks makes it available.

## Prerequisites

- A SaaS Security tenant with a **Data Security** license (or a CASB-X / CASB-PA license). The Log Events API is part of the Data Security syslog and API integration.
- An **API client** for the tenant with the **Log File Access** scope (see [Creating the API client](#creating-the-api-client)).
- The region your tenant is hosted in (see [Regions](#regions)).

### Creating the API client

1. In Strata Cloud Manager, go to **Configuration → SaaS Security → Settings → Directory & External Services**.
2. Select **Add Syslog/API Client**, then choose **API Client**.
3. Give the client a name and grant it the **Log File Access** scope.
4. Save the client and copy the **Client ID** and **Client Secret**.

> ⚠️ **The client secret is shown only once.** Store it right away, ideally as a hive secret (`hive://secret/<name>`) rather than in clear text. If you lose it you must create a new API client.

Refer to Palo Alto Networks' documentation on [adding an API client](https://docs.paloaltonetworks.com/saas-security/data-security/syslog-and-api-integration/api-client-integration/add-your-api-client-app) and the [Log Events API](https://docs.paloaltonetworks.com/saas-security/data-security/syslog-and-api-integration/api-client-integration/log-events-api) for the latest console steps.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter. For this adapter the default is `prisma_saas`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `prisma_saas`

| Key | Required | Description |
| --- | --- | --- |
| `client_id` | yes | The API client ID. |
| `client_secret` | yes | The API client secret. In the cloud this can be a hive secret reference such as `hive://secret/prisma-saas-client-secret`. |
| `region` | no | Region the tenant is hosted in, see [Regions](#regions). Default `us`. |
| `base_url` | no | Override of the API host, e.g. `https://api.example.paloaltonetworks.com`. Must be `https`. Use it to reach a region that is not yet in the `region` list; otherwise prefer `region`. |
| `max_concurrent_polls` | no | Advanced. Number of long-poll requests kept in flight at once. Default `4`. The default is appropriate for almost all tenants; leave it unset unless you have been advised otherwise. |

### Regions

The `region` value selects the API host the adapter talks to. Use the region where your SaaS Security tenant is hosted.

| `region` | Palo Alto Networks region | API host |
| --- | --- | --- |
| `us` (default) | US (VPC1) | `https://api.aperture.paloaltonetworks.com` |
| `eu` | Europe (EU1) | `https://api.aperture-eu.paloaltonetworks.com` |
| `apac` | Asia Pacific (AP1) | `https://api.aperture-apac.paloaltonetworks.com` |
| `uk` | United Kingdom | `https://api.aperture-uk.paloaltonetworks.com` |
| `uk2` | United Kingdom 2 (UK2) | `https://api.uk2.prisma-saas.paloaltonetworks.com` |
| `in` | India (IN1) | `https://api.in1.prisma-saas.paloaltonetworks.com` |
| `au` | Australia (AU1) | `https://api.au1.prisma-saas.paloaltonetworks.com` |
| `jp` | Japan (JP1) | `https://api.jp1.prisma-saas.paloaltonetworks.com` |

## How it works

The adapter requests an access token with the API client credentials (`POST /oauth/token`) and renews it before it expires. It then long-polls the Log Events API; the server holds each request open for up to 20 seconds and replies as soon as events are available, or with an empty response when there are none.

Events are shipped as received. The LimaCharlie event type is the event's `log_type` and the event time is its `timestamp`.

### Caveats

- **Events are consumed from a queue.** Palo Alto Networks keeps events in a queue and reading an event removes it. There is no cursor and no replay, so each event can be read **once**, by **one** consumer. Only one API client per tenant can read the logs: do not run a second reader (another adapter, a SIEM connector or a script) against the same tenant, or the readers will each see only part of the events.
- **Events expire after about one hour.** If the adapter is stopped for longer than that, the events produced in the meantime are lost. Events that are in flight when the adapter stops may also not be recovered.
- **Syslog and API can run together.** Sending the same logs through a SaaS Security syslog integration while this adapter reads the API is fine; the two do not compete. Running **two API clients** against the same tenant is not.
- **Use a dedicated API client.** Do not reuse the client for other tooling, since any other reader of the queue will take events away from LimaCharlie.

## Event Types

The adapter sets the LimaCharlie event type to the event's `log_type`:

| Event type | Description |
| --- | --- |
| `activity_monitoring` | User and file activity in monitored SaaS applications. |
| `incident` | Policy match incidents raised by SaaS Security, including `severity` (0–5), the matched policy rule and the affected asset. |
| `remediation` | Remediation actions taken on an asset or incident. |
| `policy_violation` | Policy violation events. |
| `admin_audit` | Administrator activity in the SaaS Security console (`admin_id`, `admin_role`, `event_type`, `field`, old and new values). |

Palo Alto Networks documents additional event types on its syslog integration (for example `ba_incident_event`); any `log_type` delivered by the Log Events API is forwarded under its own name.

### Sample events

An `activity_monitoring` event:

```json
{
  "log_type": "activity_monitoring",
  "item_type": "File",
  "item_name": "My File",
  "user": "John Smith",
  "source_ip": "10.10.10.10",
  "location": "Somewhere, USA",
  "action": "delete",
  "target_name": null,
  "target_type": null,
  "serial": "mySerial",
  "cloud_app_instance": "My Cloud App",
  "timestamp": "2017-02-17T00:18:58.961Z"
}
```

`incident` events carry the same base fields plus incident details such as `severity`, `incident_id`, `policy_rule_name`, `incident_category`, `incident_owner`, `asset_id`, `item_owner`, `exposure`, `item_cloud_url` and `datetime_edited`.

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter prisma_saas \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=prisma_saas \
  client_options.sensor_seed_key=prisma-saas \
  client_id=$PRISMA_SAAS_CLIENT_ID \
  client_secret=$PRISMA_SAAS_CLIENT_SECRET \
  region=us
```

## Docker Deployment

Create a configuration file, `prisma_saas.yaml`:

```yaml
prisma_saas:
  client_id: "YOUR_API_CLIENT_ID"
  client_secret: "YOUR_API_CLIENT_SECRET"
  region: "us"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PRISMA_SAAS"
    hostname: "prisma-saas-adapter"
    platform: "prisma_saas"
    sensor_seed_key: "prisma-saas-sensor"
```

The adapter is published as the [`refractionpoint/lc-adapter`](https://hub.docker.com/r/refractionpoint/lc-adapter) image. Mount the configuration file into the container:

```bash
docker run -d --rm \
  -v /path/to/prisma_saas.yaml:/conf/prisma_saas.yaml:ro \
  refractionpoint/lc-adapter prisma_saas /conf/prisma_saas.yaml
```

## Infrastructure as Code Deployment

Cloud-hosted adapters are deployed as a `cloud_sensor` record in the Hive. Store the client secret as a hive secret and reference it:

```yaml
# For cloud sensor deployment, store the client secret as a hive secret:
#
#   client_secret: "hive://secret/prisma-saas-client-secret"

sensor_type: "prisma_saas"
prisma_saas:
  client_id: "YOUR_API_CLIENT_ID"
  client_secret: "hive://secret/prisma-saas-client-secret"
  region: "us"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_PRISMA_SAAS"
    hostname: "prisma-saas-adapter"
    platform: "prisma_saas"
    sensor_seed_key: "prisma-saas-sensor"
```

## Configuring a Palo Alto SaaS Security Adapter in the Web UI

Within the LimaCharlie web application, select `+ Add Sensor`, then choose **Palo Alto SaaS Security (Prisma SaaS)**.

Pick or create an Installation Key for this adapter, then fill in:

| Field | Value |
| --- | --- |
| Client ID | The API client ID. |
| Client Secret | The API client secret (a hive secret reference is accepted). |
| Region | The region your tenant is hosted in. Defaults to `us`. |

Click `Complete Cloud Installation`. LimaCharlie will authenticate against the Palo Alto Networks API and begin pulling events.

## Sample Rule

The adapter ships each record under an event type matching its `log_type`, so D&R rules can route directly on it. This rule reports every SaaS Security incident with a severity of 4 or 5:

```yaml
# Detection
event: incident
op: is greater than
path: event/severity
value: 3

# Response
- action: report
  name: Palo Alto SaaS Security High Severity Incident
```

## API Docs

- [Log Events API](https://docs.paloaltonetworks.com/saas-security/data-security/syslog-and-api-integration/api-client-integration/log-events-api)
- [API client authentication](https://docs.paloaltonetworks.com/saas-security/data-security/syslog-and-api-integration/api-client-integration/api-client-authentication)
