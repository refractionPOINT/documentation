# Sublime Security

[Sublime Security](https://sublime.security/) is an email security platform. Users can create custom detections, get visibility and control, and stop malicious emails.

## Ingesting Audit Logs

You can ingest audit logs from Sublime cloud-to-cloud through the API.

### Adapter-specific Options

Adapter Type: `sublime`

- `api_key`: your Okta API key/token

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter sublime client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=sublime \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
api_key=$API_KEY
```

### Infrastructure as Code Deployment

```python
# For cloud sensor deployment, store credentials as hive secrets:

#   api_key: "hive://secret/sublime-api-key"

sensor_type: "sublime"
sublime:
  api_key: "hive://secret/sublime-api-key"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_SUBLIME"
    hostname: "sublime-security-adapter"
    platform: "json"
    sensor_seed_key: "sublime-audit-sensor"
    mapping:
      sensor_hostname_path: "user.email"
      event_type_path: "type"
      event_time_path: "created_at"
    indexing: []
```

## API Doc

See the official [documentation](https://docs.sublime.security/reference/authentication).

## Ingesting Alerts

LimaCharlie can ingest Sublime events with a `json` Webhook Adapter configuration.

### Adapter Deployment

A cloud-to-cloud webhook Adapter that receives JSON events ingests the Sublime Security logs. To create this Adapter and enable the input, do these steps:

1. Create the Webhook Adapter with the LimaCharlie CLI.
2. Find the URL that LimaCharlie creates for the Webhook Adapter.
3. Give the completed URL to Sublime Security for webhook events.

#### 1. Creating the LimaCharlie Webhook Adapter

These steps are adapted from the [generic Webhook Adapter creation guide](../tutorials/webhook-adapter.md).

A Webhook Adapter needs a set of parameters. These include the organization ID, the Installation Key, the platform, the mapping details, and other parameters. Change the configuration below to configure a Webhook Adapter that ingests Sublime Security events:

```json
{
    "sensor_type": "webhook",
    "webhook": {
       "secret": "sublime-security",
        "client_options": {
            "hostname": "sublime-security",
            "identity": {
                "oid": "<your_oid>",
                "installation_key": "<your_installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "sublime-super-secret-key",
            "mapping" : {
                "event_type_path" : "data/flagged_rules/name",
                "event_time_path" : "created_at"
            }
        }
    }
}
```

The mapping above makes these changes:

- `event_type_path` is mapped to the rule name from the Sublime alert
- `event_time_path` is mapped to the `created_at` field from the Sublime alert

#### 2. Building the Adapter URL

After you create the webhook, get the webhook URL from the [Get Org URLs](https://api.limacharlie.io/static/swagger/get-org-urls) API call. You need this information to complete the Webhook URL:

- Organization ID
- Webhook name (from the config)
- Secret (from the config)

If the returned domain is `9157798c50af372c.hook.limacharlie.io`, the format of the URL is:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

You can give the `secret` value in the webhook URL or in an HTTP header named `lc-secret`.

#### 3. Configuring the Sublime webhook Action

In the Sublime Security console, go to **Manage** > **Actions**. Then select **New Action** > **Webhook**.

![image.png](../../../assets/images/image(174).png)

In the **Configure webhook** menu, give a name and the Adapter URL that you built in Step 2.

![image.png](../../../assets/images/image(175).png)

As Step 2 explains, you can configure the HTTP header `lc-secret`.

After you configure the webhook in Sublime Security, you can configure alerts to go to LimaCharlie. To test the Webhook, select **Trigger Custom Action** on a Flagged message and send it to the LimaCharlie webhook.
