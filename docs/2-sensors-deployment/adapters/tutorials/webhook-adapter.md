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
- SECRET is the secret value provided in the configuration. You can provide the secret value in the URL or as an HTTP header named `lc-secret`.

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
