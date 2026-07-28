# Canarytokens

Canarytokens are a free and quick way to help defenders find that an attacker breached them, because the attacker announces itself. Canarytokens are digital traps, or tripwires, that you put in the network of an organization as a "lure" for adversaries. When an adversary uses a canary, the canary sends an alert. The alert can go to LimaCharlie.

A webhook adapter ingests Canarytokens into LimaCharlie. LimaCharlie recognizes them as the `canary_token` platform.

## A Little More

LimaCharlie published a [blog post about the Canarytoken integration](https://limacharlie.io/blog/early-warnings-with-limacharlie-and-canarytokens) in April 2023.

## Adapter Deployment

A cloud-to-cloud webhook adapter ingests Canarytoken alerts. You configure the adapter to receive JSON events. LimaCharlie has a pre-built mapping for Canarytoken alerts. You can do the first deployment of a Canarytokens adapter in two ways:

- With the LimaCharlie web app
- With the LimaCharlie CLI

Steps 2 and 3 are the same for both methods.

### 1a. Initial deployment via the LimaCharlie web UI

In the LimaCharlie web app, go to **Sensors** > **Sensors List** > **+ Add** Sensor. Select the **Canary Token** option.

After you select or create an Installation Key, the web app asks you to name the adapter and select a Secret value.

Click **Complete Cloud Installation** to create the cloud-to-cloud adapter. Then go to step 2.

### 1b. Initial deployment via the LimaCharlie CLI

The LimaCharlie CLI can also deploy a Canarytokens adapter. This step comes from the [generic Webhook Adapter creation guide](../tutorials/webhook-adapter.md).

Change this configuration to set up a webhook adapter that receives Canarytokens events.

```json
{
    "sensor_type": "webhook",
    "webhook": {
       "secret": "canarytoken-secret",
        "client_options": {
            "hostname": "canarytokens",
            "identity": {
                "oid": "<your_oid>",
                "installation_key": "<your_installation_key>"
            },
            "platform": "canary_token",
            "sensor_seed_key": "canary-super-secret-key",
            "mapping" : {
                "event_type_path" : {{ 'Canarytoken Hit' }}
            }
        }
    }
}
```

In the mapping above, the `event_type_path` field is set to the static string `Canarytoken Hit`. You can change it to any value.

To create this webhook adapter, run this command. Replace `<json_config_file>` with the name of the config file above:

`limacharlie hive set cloud_sensor --key canarytoken --data <json_config_file>`

### 2. Building the Webhook URL

After you create the webhook, get the webhook URL from the [Get Org URLs](https://api.limacharlie.io/static/swagger/get-org-urls) API call. To complete the webhook URL, you need this information:

- Organization ID
- Webhook name (from the config)
- Secret (from the config)

If the returned domain is `9157798c50af372c.hook.limacharlie.io`, the URL has this format:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

You can give the `secret` value in the webhook URL or in an HTTP header named `lc-secret`.

### 3. Configuring the Canaryalert Webhook Output

Go to the [Canarytokens generate page](https://canarytokens.org/generate) and create the token that you want.

![image.png](../../../assets/images/image(173).png)

1. Use the URL from step 2 as the webhook URL.
2. Give a reminder note. The note also appears in the Canarytoken alert when an adversary trips the token.
3. Click **Create my Canarytoken**. The page then supplies the content for the selected token.

When an adversary trips the Canarytoken, a webhook alert goes to the LimaCharlie adapter.
