# Wiz

## Overview

This Adapter allows you to connect to the [Wiz GraphQL API](https://win.wiz.io/reference/welcome) to fetch cloud security data — Issues, vulnerability findings, audit logs, and anything else exposed by a Wiz GraphQL query.

The adapter is **query-driven**: rather than hard-coding one feed, you supply the GraphQL `query` to run and tell the adapter where to find the items in the response (`data_path`), which field carries the timestamp it should use to advance its watermark (`time_field`), and which field uniquely identifies an item for de-duplication (`id_field`). This lets a single adapter type pull any paginated Wiz query.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `wiz`

- `client_id`: your Wiz service account Client ID.
- `client_secret`: your Wiz service account Client Secret.
- `url`: your tenant's Wiz GraphQL API endpoint, e.g. `https://api.<region>.app.wiz.io/graphql`.
- `query`: the GraphQL query to run (required).
- `variables`: an object of GraphQL variables passed with the query (e.g. paging and time-filter inputs).
- `time_field`: the field on each returned item that holds its timestamp, used to advance the watermark (e.g. `createdAt`, `updatedAt`).
- `data_path`: the path into the JSON response to the array of items, e.g. `["data", "securityIssues", "issues"]`.
- `id_field`: the field that uniquely identifies an item, used to de-duplicate across polls (e.g. `id`).

The adapter authenticates with the OAuth2 `client_credentials` grant against `https://auth.app.wiz.io/oauth/token` (audience `wiz-api`), then repeatedly executes `query` against `url`, walking `data_path` to the items and tracking progress via `time_field` and `id_field`.

### Getting Your Credentials

1. In the Wiz portal, go to **Settings → Service Accounts** and create a service account.
2. Grant it the read scopes for the data you intend to query (e.g. `read:issues`, `read:vulnerabilities`).
3. Copy the **Client ID** and **Client Secret**.
4. Your GraphQL **endpoint URL** is shown in the Wiz portal under the API/service-account details (it is region-specific).

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   client_id: "hive://secret/wiz-client-id"
#   client_secret: "hive://secret/wiz-client-secret"

sensor_type: "wiz"
wiz:
  client_id: "hive://secret/wiz-client-id"
  client_secret: "hive://secret/wiz-client-secret"
  url: "https://api.us1.app.wiz.io/graphql"
  query: |
    query IssuesTable($first: Int, $after: String, $filterBy: IssueFilters) {
      issues(first: $first, after: $after, filterBy: $filterBy) {
        nodes {
          id
          createdAt
          severity
          status
          entitySnapshot { name type }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  variables:
    first: 100
  time_field: "createdAt"
  data_path: ["data", "issues", "nodes"]
  id_field: "id"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_WIZ"
    hostname: "wiz-adapter"
    platform: "wiz"
    sensor_seed_key: "wiz-sensor"
```

> The `query`, `data_path`, `time_field`, and `id_field` above are an illustrative Issues example. Adjust them to match the exact Wiz GraphQL query you want to pull — the `data_path` must point at the array of items the query returns.

## API Doc

See the official [Wiz API documentation](https://win.wiz.io/reference/welcome).
