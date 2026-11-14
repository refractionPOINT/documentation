# Tutorial: Creating a Webhook Adapter

LimaCharlie supports webhooks as a telemetry ingestion method. Webhooks are technically cloud [Adapters](../deployment.md), as they cannot be deployed on-prem or through the downloadable Adapter binary.

Webhook adapters are created by enabling a webhook through the `cloud_sensor` Hive feature. Webhook creation will enable a specific URL that can receive webhooks from any platform. Received data will be ingested in LimaCharlie as a Sensor, similar to an Office365 or Syslog Adapter.

## Creating a Webhook Adapter

Webhook adapters can be created either through the webapp, API, or CLI. Before creation, let's look at the basic webhook configuration and values necessary to build the adapter.

```json
{
    "sensor_type": "webhook",
    "webhook": {
        "secret": "some-secret-value-hard-to-predict",
        "signature_secret": "",
        "signature_header": "",
        "signature_scheme": "",
        "events_path": "",
        "client_options": {
            "hostname": "<any_name>",
            "identity": {
                "oid": "<oid>",
                "installation_key": "<installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "<any-super-secret-seed-key>"
        }
    }
}
```

Field descriptions:

- `secret`: this secret value will be part of the URL to accept your webhooks. It enables you to prevent or revoke unauthorized access to a hook.
- `signature_scheme`, `signature_header`, `signature_secret`: optional verification of a signature the sender computes over each request. Leave all three empty to authenticate with `secret` alone. The supported scheme is `hmac-sha256`, the format GitHub uses for `X-Hub-Signature-256`:
  - `signature_header` is the header carrying the signature (default `X-Hub-Signature-256`), and its value must be `sha256=` followed by the hex HMAC-SHA256 of the raw request body.
  - `signature_secret` is the HMAC key: the value, or a reference to a stored secret like `hive://secret/<name>`. If the scheme is set without it, every request is refused.
  - A request with a missing or wrong signature is refused with `401`. A request carrying a signature already accepted in the last 24 hours is acknowledged with `{"success":true,"duplicate":true}` and not ingested again.
  - JSON events from a verified request carry `"__lc_signature_verified": true`, so a D&R rule can require it. The field is removed from events of any request that was not verified.
  - If you require another signature format, please get in touch with us.
- `events_path`: optional path to a list of events inside each JSON object the sender posts, for senders that batch several events in an envelope. See [Splitting batched events](#splitting-batched-events-events_path).
- `client_options.hostname`: provide your own name for the webhook adapter.
- `client_options.identity.oid`: the OID of the organization you wish to send to.
- `client_options.identity.installation_key`: the installation key to be used for the adapter.
- `client_options.platform`: the data format (typically `json` for webhooks).
- `client_options.sensor_seed_key`: an arbitrary value used to generate a stable Sensor ID.

When the above configuration is provided to LimaCharlie, a webhook adapter will appear and be available for webhook event ingestion. Here's an example of creating the above record through the LimaCharlie CLI:

```bash
echo '{"sensor_type": "webhook", "webhook": {"secret": "some-secret-value-hard-to-predict", "signature_secret": "", "signature_header": "", "signature_scheme": "", "client_options": {"hostname": "<any_name>", "identity": {"oid": "<oid>", "installation_key": "<installation_key>"}, "platform": "json", "sensor_seed_key": "test-webhook"}}}' | limacharlie hive set cloud_sensor --key my-webhook --data -
```

After creating the webhook, you will be provided with a geo-dependent URL, respective to your LimaCharlie Organization location. You can also retrieve your webhook URLs with either of the following commands:

- REST API: [getOrgURLs](https://api.limacharlie.io/static/swagger/#/Org/get_orgs__oid___urls)
- Python SDK:

```python
python3 -c "from limacharlie.client import Client; from limacharlie.sdk.organization import Organization; print(Organization(Client()).get_urls()['hooks'])"
```

## Using the webhook adapter

After capturing the webhook URL in the previous step, only a few more pieces of data are necessary to construct the webhook ingestion.

Let's assume the returned domain looks like `9157798c50af372c.hook.limacharlie.io`, the format of the URL would be:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`, where:

- OID is the Organization OID provided in the configuration above.
- HOOKNAME is the name of the hook provided in the configuration above.
- SECRET is the secret value provided in the configuration. You can provide the secret value in the URL, as an HTTP header named `lc-secret`, or in the standard `Authorization` header (see below).

### Sending the secret in the Authorization header

Some platforms can only be configured with a URL and an `Authorization` header value. For those, leave the secret out of the URL (use `https://<hook-domain>/OID/HOOKNAME`) and put it in the `Authorization` header. The secret is looked for in this order, and the first location that carries a value is the one used:

1. the last component of the URL path,
2. the `lc-secret` header,
3. the `Authorization` header.

The `Authorization` header can take any of these forms:

- `Authorization: SECRET`
- `Authorization: Bearer SECRET` (the scheme is not case sensitive)
- `Authorization: Basic BASE64` where `BASE64` is the encoding of `username:SECRET`. The username is ignored, the password must be the secret.

A raw value that starts with `Bearer ` or `Basic ` is read as that scheme, so a secret that itself starts that way must be sent in the URL or the `lc-secret` header. Any other value is refused with a `401`, like a wrong secret. Webhooks with a signature scheme configured (`signature_scheme`) still require a valid signature on top of the secret.

## Supported Webhook Format

When sending data via POST requests to the URL, the body of your request is expected to be one or many JSON events. Supported formats include:

- Simple JSON object:

  - `{"some":"data"}`
- List of JSON objects:

  - `[{"some":"data"},{"some":"data"}]`
- Newline separated JSON objects like:

```json
{"some":"data"}
{"some":"data"}
{"some":"data"}
```

Or, one of the above, but compressed using gzip.

With the completed webhook URL, you can begin sending events and will see them in the Timeline for your webhook Adapter.

## Splitting batched events (`events_path`)

Some platforms push several events in a single request, wrapped in an envelope, for example:

```json
{"jsonrpc": "2.0", "method": "addEvents", "params": {"events": [{"id": 1}, {"id": 2}, {"id": 3}]}, "id": 123}
```

By default this whole envelope is ingested as a single event. Set `events_path` to the location of the list inside the envelope, as object keys separated by `/` (here `params/events`), to ingest each element of the list as its own event instead:

- Each object in the list becomes an event.
- Each string in the list is handled like a line of newline-separated text, so formats such as CEF go through the adapter's normal text parsing.
- If a list mixes objects and strings, all the objects are ingested as events, then all the strings as text lines. The relative order between the two kinds is not kept.
- A list that holds anything other than objects and strings (numbers, `null`, nested lists) is not split: the envelope is ingested unchanged, so no data is lost.
- If the path is missing from an object or does not lead to a list (a ping or test message, for example), that object is ingested unchanged.
- An empty list produces no event; the request is still acknowledged.
- Keys are matched exactly, and `events_path` has no wildcards or list indexes. It is applied to each JSON object of the request, so it also works with the list and newline-separated formats below. It is not applied to form-encoded bodies.

Signature verification, if enabled, is computed over the original request body. Detection rules that you attach to the webhook (`dr_rules`) are evaluated on each split event.

## Example: Bitdefender GravityZone Event Push Service

[Bitdefender GravityZone](https://www.bitdefender.com/business/support/en/77209-135319-setpusheventsettings.html) can push events to an HTTPS endpoint, and only needs a `2xx` response back. It sends its configured `authorization` value in the `Authorization` header, and batches events as `params/events` in a JSON-RPC message.

First create the webhook adapter, with `events_path` set:

```bash
echo '{"sensor_type": "webhook", "webhook": {"secret": "some-secret-value-hard-to-predict", "events_path": "params/events", "client_options": {"hostname": "bitdefender-gravityzone", "identity": {"oid": "<oid>", "installation_key": "<installation_key>"}, "platform": "json", "sensor_seed_key": "bitdefender-gravityzone"}}}' | limacharlie hive set cloud_sensor --key bitdefender --data -
```

Then, in the GravityZone [`setPushEventSettings`](https://www.bitdefender.com/business/support/en/77209-135319-setpusheventsettings.html) API call, use the hook URL without the secret and pass the secret as the `authorization` value:

```json
{
    "params": {
        "status": 1,
        "serviceType": "jsonRPC",
        "serviceSettings": {
            "url": "https://<hook-domain>/<oid>/bitdefender",
            "requireValidSslCertificate": true,
            "authorization": "Bearer some-secret-value-hard-to-predict"
        },
        "subscribeToEventTypes": {
            "modules": true,
            "new-incident": true
        }
    },
    "jsonrpc": "2.0",
    "method": "setPushEventSettings",
    "id": "1"
}
```

Every event of each push shows up individually in the Timeline of the adapter.
