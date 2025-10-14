[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Tutorial: Creating a Webhook Adapter

* 02 Jan 2025
* 3 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Tutorial: Creating a Webhook Adapter

* Updated on 02 Jan 2025
* 3 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie supports webhooks as a telemetry ingestion method. Webhooks are technically cloud [Adapters](/v2/docs/adapters), as they cannot be deployed on-prem or through the downloadable Adapter binary.

Webhook adapters are created by enabling a webhook through the `cloud_sensor` [Hive](/v2/docs/config-hive) feature. Webhook creation will enable a specific URL that can receive webhooks from any platform. Received data will be ingested in LimaCharlie as a Sensor, similar to an Office365 or Syslog Adapter.

## Creating a Webhook Adapter

Webhook adapters can be created either through the webapp, API, or CLI. Before creation, let's look at the basic webhook configuration and values necessary to build the adapter.

```
{
    "sensor_type": "webhook",
    "webhook": {
        // This secret value will be part of the URL to accept your webhooks.
        // It enables you to prevent or revoke unauthorized access to a hook.
        "secret": "some-secret-value-hard-to-predict",

        // Placeholder for generic webhook signature validation.
        // If you require a specific format, please get in touch with us.
        "signature_secret": "",
        "signature_header": "",
        "signature_scheme": "",

        // Format with which the data is ingested in LC.
        "client_options": {
            // Provide your own name for the webhook adapter
            "hostname": "<any_name>",
            "identity": {
                // Provide the OID of the organization you wish to send to
                "oid": "<oid>",
                // Provide the installation key to be used for the adapter
                "installation_key": "<installation_key>"
            },
            "platform": "json",
            "sensor_seed_key": "<any-super-secret-seed-key>"
        }
    }
}
```

When the above configuration is provided to LimaCharlie, a webhook adapter will appear and be available for webhook event ingestion. Here's an example of creating the above record through the LimaCharlie CLI:

```
echo '{"sensor_type": "webhook", "webhook": {"secret": "some-secret-value-hard-to-predict", "signature_secret": "", "signature_header": "", "signature_scheme": "", "client_options": {"hostname": "<any_name>", "identity": {"oid": "<oid>", "installation_key": "<installation_key>"}, "platform": "json", "sensor_seed_key": "test-webhook"}}}' | limacharlie hive set cloud_sensor --key my-webhook --data -
```

After creating the webhook, you will be provided with a geo-dependent URL, respective to your LimaCharlie Organization location. You can also retrieve your webhook URLs with either of the following commands:

* REST API: [getOrgURLs](https://docs.limacharlie.io/apidocs/get-org-urls)
* Python SDK:

```
python3 -c "import limacharlie; print(limacharlie.Manager().getOrgURLs()['hooks'])"
```

## Using the webhook adapter

After capturing the webhook URL in the previous step, only a few more pieces of data are necessary to construct the webhook ingestion.

Let's assume the returned domain looks like `9157798c50af372c.hook.limacharlie.io`, the format of the URL would be:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`, where:

* OID is the Organization OID provided in the configuration above.
* HOOKNAME is the name of the hook provided in the configuration above.
* SECRET is the secret value provided in the configuration. You can provide the secret value in the URL or as an HTTP header named `lc-secret`.

## Supported Webhook Format

When sending data via POST requests to the URL, the body of your request is expected to be one or many JSON events. Supported formats include:

* Simple JSON object:

  + `{"some":"data"}`
* List of JSON objects:

  + `[{"some":"data"},{"some":"data"}]`
* Newline separated JSON objects like:

```
{"some":"data"}
{"some":"data"}
{"some":"data"}
```

Or, one of the above, but compressed using gzip.

With the completed webhook URL, you can begin sending events and will see them in the Timeline for your webhook Adapater.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Webhook](/docs/outputs-destinations-webhook)
* [Webhook (Bulk)](/docs/outputs-destinations-webhook-bulk)
* [Tutorial: Ingesting Telemetry from Cloud-Based External Sources](/docs/tutorial-ingesting-telemetry-from-cloud-based-external-sources)

---

###### What's Next

* [Tutorial: Ingesting Google Cloud Logs](/docs/tutorial-ingesting-google-cloud-logs)

Table of contents

+ [Creating a Webhook Adapter](#creating-a-webhook-adapter)
+ [Using the webhook adapter](#using-the-webhook-adapter)
+ [Supported Webhook Format](#supported-webhook-format)

Tags

* [adapters](/docs/en/tags/adapters)
* [tutorial](/docs/en/tags/tutorial "Tutorial")
