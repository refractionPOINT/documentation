# Wiz

## Overview

This Adapter connects to the [Wiz GraphQL API](https://win.wiz.io/reference/welcome) and ships the items returned by a GraphQL query you supply, such as Issues, vulnerability findings or audit logs.

The adapter is query-driven. You provide the `query` to run and tell the adapter where the items sit in the response (`data_path`), which field holds each item's timestamp (`time_field`) and which field uniquely identifies an item (`id_field`).

Every 30 seconds the adapter sends the query once and ships the items from that single response. It does not follow `pageInfo` or `$after` cursors, so it reads at most one page per poll. See [How polling works](#how-polling-works) for what that means for your query.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

Adapter Type: `wiz`

- `client_id`: your Wiz service account Client ID (required).
- `client_secret`: your Wiz service account Client Secret (required).
- `url`: your tenant's Wiz GraphQL API endpoint, like `https://api.<region>.app.wiz.io/graphql` (required).
- `query`: the GraphQL query to run (required). It must declare a `$filterBy` variable and return items newest first, see below.
- `time_field`: the field on each item that holds its timestamp, like `createdAt` (required). The adapter also uses this name as the key inside `filterBy`, so the query's filter input must accept it.
- `data_path`: the path into the JSON response to the array of items, like `["data", "issues", "nodes"]` (required). Every element except the last must be an object, and the last must be an array.
- `id_field`: the field that uniquely identifies an item, like `id` (required).
- `variables`: an object of GraphQL variables sent with the query, like `first` or `orderBy`. Optional.
- `token_url`: overrides the OAuth token endpoint. Optional, defaults to `https://auth.app.wiz.io/oauth/token`. Set it if your tenant authenticates somewhere other than the Wiz commercial cloud.

The adapter authenticates with the OAuth2 `client_credentials` grant (audience `wiz-api`) against the token endpoint. It caches the token and requests a new one when less than a minute of validity remains.

### How polling works

On each poll the adapter sends your `query` with a copy of `variables` in which it has set `filterBy.<time_field>` to `{"after": "<watermark>"}`. The watermark is an RFC 3339 timestamp. If your `variables` already contain a `filterBy` object, the adapter keeps your other keys and only adds or replaces the `<time_field>` key.

- **Declare `$filterBy`.** The adapter always sends `filterBy` in the variables. Your query must declare a `$filterBy` variable and pass it to the field you are querying, otherwise the time filter never reaches Wiz and every poll covers the same window. The filter input type must accept `<time_field>: {after: <timestamp>}`. For Issues that is `$filterBy: IssueFilters` with `createdAt`.
- **Return items newest first.** The adapter takes the watermark from the first item in the response, so the newest item must come first. If the order is ascending, the watermark lands on the oldest item and the adapter re-reads the same items on every poll. Pass an ordering through `variables` (the example query declares `$orderBy`), sorted descending on the same field as `time_field`. The valid ordering values depend on the query you run, so take them from the Wiz API reference.
- **Set `first` high enough.** There is no paging. If more new items arrive between two polls than the page holds, the extra items are skipped, because the watermark moves to the newest item. Use the largest page size Wiz allows for your query.
- **Timestamps and IDs must be strings.** An item is skipped if its `id_field` or `time_field` value is not a string.
- **First run and restarts.** The first poll asks for the last 24 hours. The watermark lives in memory only, so a restarted adapter looks back 24 hours again and may ship items it already sent.

Each shipped event is one item from the array at `data_path`, unchanged. A GraphQL error returned with HTTP 200 shows up in the adapter's error log as a `data_path` error, because the response has no `data` object. Non-200 responses are logged with the response body.

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
    query IssuesTable($filterBy: IssueFilters, $first: Int, $orderBy: IssueOrder) {
      issues: issuesV2(filterBy: $filterBy, first: $first, orderBy: $orderBy) {
        nodes {
          id
          createdAt
          severity
          status
          entitySnapshot { name type }
        }
      }
    }
  variables:
    first: 100
    # REQUIRED before you deploy: add an orderBy entry that sorts by createdAt,
    # newest first. The IssueOrder values are in the Wiz API reference, so they
    # are not filled in here.
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

This example is incomplete until you add the `orderBy` variable. Without it Wiz returns its default order, which the adapter cannot use to track its watermark. The query, `data_path`, `time_field` and `id_field` are an illustrative Issues example. Adjust them to the query you want to pull. The query must declare `$filterBy` and return newest items first, and `data_path` must point at the array of items.

## API Doc

See the official [Wiz API documentation](https://win.wiz.io/reference/welcome).
