# SentinelOne

This Adapter streams SentinelOne activities, threats, and alerts to LimaCharlie through the SentinelOne API. You can scope it to specific SentinelOne sites or accounts, which is a single tenant of an MSP console. It can also pull the agent inventory, so that each endpoint in scope becomes an individual LimaCharlie sensor.

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or if you create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name, see below.

### Adapter-specific Options

Adapter Type: `sentinel_one`

- `domain` - your SentinelOne MGMT endpoint, `https://<your-instance>.sentinelone.net`
- `api_key` - SentinelOne API token
- `start_time` - optional start time to fetch past events.
- `site_ids` - optional comma-separated SentinelOne Site IDs. The adapter scopes each request to these sites with the standard `siteIds` filter. A token for an MSP or partner console then pulls in a **single tenant**, not every site that the token can see. Find a Site ID in the SentinelOne console under *Sentinels → Site Info*.
- `account_ids` - optional comma-separated SentinelOne Account IDs; like `site_ids` but at the account level.
- `collect_agents` - optional boolean. When `true`, the adapter also polls the agent (endpoint) inventory (`/web/api/v2.1/agents`). It ships one `agents` record for each agent, and ships the record again each time the details of the agent change. The first poll reads the full inventory. The endpoints in scope then appear in LimaCharlie as individual sensors immediately, before they produce any threat, alert, or activity telemetry. The adapter excludes decommissioned agents. This option is off by default. The API token must have permission to view Endpoints. As with any permission problem on a polled endpoint, a `403` stops the adapter and shows an error. The adapter does not skip the feed silently.
- `agents_poll_interval` - optional. How often the adapter polls the agent inventory again when `collect_agents` is on, as a Go duration in nanoseconds. Default 15 minutes.
- `urls` - Advanced, CLI only: a comma-separated list of REST API paths to scrub. The scope from `site_ids` and `account_ids` also applies to custom paths. Each path in this list must accept the standard `siteIds` and `accountIds` filters when you configure a scope. If you omit this option, the adapter brings activities, alerts, and threats:

  ```text
  /web/api/v2.1/activities,
  /web/api/v2.1/cloud-detection/alerts,
  /web/api/v2.1/threats
  ```

### Endpoints as individual sensors

LimaCharlie multiplexes SentinelOne telemetry into one sensor for each SentinelOne agent. Threats, alerts, activities, and inventory records (with `collect_agents`) that carry the same agent id go to the same sensor for that endpoint. The sensor takes the name of the endpoint's hostname. With `site_ids`, this maps one tenant of a multi-tenant SentinelOne console into a LimaCharlie organization with one sensor for each endpoint. This is the same MSP workflow as the scope by Managed Organization ID in the [ThreatLocker adapter](threatlocker.md).

Agent inventory records arrive with the event type `s1_agent`; threats, alerts and activities arrive as `s1_threat`, `s1_alert` and `s1_activity`.

## Deployment Examples

### Web App

1. On the Sensors page, select Add Sensor.
2. Choose the SentinelOne sensor type.
3. Fill in the parameters.
4. Complete the cloud installation.

![image.png](../../../assets/images/image(301).png)

### On-prem deployment

Obey the instructions in [Adapter Deployment](../deployment.md). Download the binaries for your platform, then run the adapter:

```bash
./lc_adapter sentinel_one client_options.identity.installation_key=714e1fa5-aaaa-aaaa-aaaa-aaaaaaaaaaaa client_options.identity.oid=aaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa client_options.platform=sentinel_one client_options.hostname=s1 client_options.sensor_seed_key=s1 'domain=https://datacenter.sentinelone.net' "api_key=$S1_API_KEY"
```
