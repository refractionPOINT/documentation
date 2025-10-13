# Sublime Security Specific Docs: https://docs.limacharlie.io/docs/adapter-types-sublime-security
# For cloud sensor deployment, store credentials as hive secrets:

#   api_key: "hive://secret/sublime-api-key"

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

Sublime events can be ingested in LimaCharlie via a `json` Webhook Adapter configuration.

### Adapter Deployment

Sublime Security logs are ingested via a cloud-to-cloud webhook Adapter configured to receive JSON events. The steps of creating this Adapter and enabling the input include:

1. Creating the Webhook Adapter via the LimaCharlie CLI
2. Discovering the URL created for the Webhook Adapter.
3. Providing the completed URL to Sublime Security for webhook events.

#### 1. Creating the LimaCharlie Webhook Adapter

The following steps are modified from the generic Webhook Adapter creation documentation, found [here](/v2/docs/tutorial-creating-a-webhook-adapter).

Creating a Webhook Adapter requires a set of parameters, including organization ID, Installation Key, platform, and mapping details, among other parameters. The following configuration can be modified to easily configure a Webhook Adapter for ingesting Sublime Security events:

```
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

Note that in the mapping above, we make the following changes:

* `event_type_path` is mapped to the rule name from the Sublime alert
* `event_time_path` is mapped to the `created_at` field from the Sublime alert

#### 2. Building the Adapter URL

After creating the webhook, you'll need to retrieve the webhook URL from the [Get Org URLs](https://docs.limacharlie.io/apidocs/get-org-urls) API call. You'll need the following information to complete the Webhook URL:

* Organization ID
* Webhook name (from the config)
* Secret (from the config)

Let's assume the returned domain looks like `9157798c50af372c.hook.limacharlie.io`, the format of the URL would be:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

Note that the `secret` value can be provided in the webhook URL or as an HTTP header named `lc-secret`.

#### 3. Configuring the Sublime webhook Action

Within the Sublime Security console, navigate to **Manage** > **Actions**. From here, you can select **New Action** > **Webhook**.

Within the **Configure webhook** menu, provide a name and the Adapter URL constructed in Step 2 above.

As mentioned in Step 2, you can configure the HTTP header `lc-secret`, if so desired.

Upon configuration of the webhook within Sublime Security, alerts can be configured to be sent to the LimaCharlie platform. To test the Webhook, select **Trigger Custom Action** from any Flagged message, and send to the LimaCharlie webhook.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.