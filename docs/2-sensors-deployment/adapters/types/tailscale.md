# Tailscale

[Tailscale](https://tailscale.com/) is a VPN service that makes devices and applications accessible from anywhere in the world. Tailscale uses the open source WireGuard protocol to make encrypted point-to-point connections.

LimaCharlie can ingest Tailscale events with a `json` Webhook Adapter.

## Adapter Deployment

A cloud-to-cloud webhook Adapter receives Tailscale events as JSON. When you create the Adapter, you map the fields directly to the Tailscale webhook events. To create this Adapter and enable the input, do these steps:

1. Create the Webhook Adapter with the LimaCharlie CLI.
2. Find the URL that LimaCharlie creates for the Webhook Adapter.
3. Give the completed URL to Tailscale for Webhook events.

### 1. Creating the LimaCharlie Webhook Adapter

These steps are adapted from the [generic Webhook Adapter creation guide](../tutorials/webhook-adapter.md).

A Webhook Adapter needs parameters that include the organization ID, the Installation Key, the platform, and the mapping details. The configuration below sets up a Webhook Adapter that ingests Tailscale events:

```json
{
    "sensor_type": "webhook",
    "webhook": {
       "secret": "tailscale-secret",
        "client_options": {
            "hostname": "tailscale",
            "identity": {
                "oid": "<your_oid>",
                "installation_key": "<your_installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "tailscale-super-secret-key",
            "mapping" : {
                "event_type_path" : "message"
            }
        }
    }
}
```

The mapping above is based on the Webhook event from Tailscale (see the [Tailscale webhook example](https://tailscale.com/kb/1213/webhooks/)). The mapping makes this change:

- `event_type_path` is mapped to the `message` field

### 2. Building the Webhook URL

After you create the webhook, get the webhook URL from the [Get Org URLs](https://api.limacharlie.io/static/swagger/#/Org/get_orgs__oid___urls) API call. To complete the Webhook URL, you need this information:

- Organization ID
- Webhook name (from the config)
- Secret (from the config)

If the returned domain is `9157798c50af372c.hook.limacharlie.io`, the URL has this format:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

You can give the `secret` value in the webhook URL or in an HTTP header named `lc-secret`.

### 3. Providing the URL to Tailscale for Webhook Events

In the Tailscale Admin Console, go to **Settings** > **Webhooks**. Select **Add endpoint...**

![image.png](../../../assets/images/image(168).png)

Give the completed Webhook URL from Step 2 above. You can also select the events that the Webhook sends. These options are available:

![image.png](../../../assets/images/image(170).png)

Select **Add endpoint**. Tailscale gives you a webhook secret that is unique to this endpoint. You can keep this value, but LimaCharlie does not need it.

#### 4. Test Webhook Output

In the Tailscale Admin Console, you can test the webhook and make sure that LimaCharlie receives events. In the Webhook Endpoint options, select **Test endpoint...**.

The webhook event appears in the LimaCharlie Adapter a moment later. The `event_type` matches the `message` field from the Tailscale webhook event.
