# Tutorial: Creating a Webhook Adapter

LimaCharlie supports webhooks as a method to ingest telemetry. Webhooks are cloud [Adapters](../deployment.md), because you cannot deploy them on-prem or with the downloadable Adapter binary.

To create a webhook adapter, enable a webhook with the `cloud_sensor` Hive feature. The webhook enables a specific URL that can receive webhooks from any platform. LimaCharlie ingests the received data as a Sensor, like an Office365 or Syslog Adapter.

## Creating a Webhook Adapter

You can create a webhook adapter with the web app, the API, or the CLI. First, examine the basic webhook configuration and the values that the adapter needs.

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

- `secret`: the secret value that is part of the URL that accepts your webhooks. Use it to stop or revoke unauthorized access to a hook.
- `signature_secret`, `signature_header`, `signature_scheme`: placeholders for generic validation of webhook signatures. If you need a specific format, contact LimaCharlie.
- `client_options.hostname`: your own name for the webhook adapter.
- `client_options.identity.oid`: the OID of the organization that receives the data.
- `client_options.identity.installation_key`: the installation key for the adapter.
- `client_options.platform`: the data format (usually `json` for webhooks).
- `client_options.sensor_seed_key`: an arbitrary value that generates a stable Sensor ID.

When you give this configuration to LimaCharlie, the webhook adapter appears and can ingest webhook events. This example creates the record with the LimaCharlie CLI:

```bash
echo '{"sensor_type": "webhook", "webhook": {"secret": "some-secret-value-hard-to-predict", "signature_secret": "", "signature_header": "", "signature_scheme": "", "client_options": {"hostname": "<any_name>", "identity": {"oid": "<oid>", "installation_key": "<installation_key>"}, "platform": "json", "sensor_seed_key": "test-webhook"}}}' | limacharlie hive set cloud_sensor --key my-webhook --data -
```

After you create the webhook, LimaCharlie gives you a geo-dependent URL for the location of your LimaCharlie Organization. You can also get your webhook URLs with one of these commands:

- REST API: [getOrgURLs](https://api.limacharlie.io/static/swagger/#/Org/get_orgs__oid___urls)
- Python SDK:

```python
python3 -c "from limacharlie.client import Client; from limacharlie.sdk.organization import Organization; print(Organization(Client()).get_urls()['hooks'])"
```

## Using the webhook adapter

After you get the webhook URL in the previous step, you need only a few more values to construct the webhook ingestion.

If the returned domain is `9157798c50af372c.hook.limacharlie.io`, the URL format is:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`, where:

- OID is the Organization OID from the configuration above.
- HOOKNAME is the name of the hook from the configuration above.
- SECRET is the secret value from the configuration. Put the secret value in the URL, or in an HTTP header named `lc-secret`.

## Supported Webhook Format

When you send data with POST requests to the URL, the body of the request must be one or more JSON events. These formats are supported:

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

You can also compress one of these formats with gzip.

With the complete webhook URL, you can send events. The events are shown in the Timeline of your webhook Adapter.
