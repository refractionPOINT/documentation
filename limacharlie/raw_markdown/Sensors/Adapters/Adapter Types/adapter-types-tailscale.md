---
title: Tailscale
slug: adapter-types-tailscale
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-tailscale
articleId: 56fcbd25-83f5-48ea-89f7-1e2ba8fbc921
---

* * *

Tailscale

  *  __25 Apr 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Tailscale

  *  __Updated on 25 Apr 2025
  *  __ 2 Minutes to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

[Tailscale](https://tailscale.com/) is a VPN service that makes devices and applications accessible anywhere in the world. Relying on the open source WireGuard protocol, Tailscale enables encrypted point-to-point connections.

Tailscale events can be ingested in LimaCharlie via a `json` Webhook Adapter.

## Adapter Deployment

Tailscale events are ingested via a cloud-to-cloud webhook Adapter configured to receive JSON events. In the creation of the Adapter, we map fields directly to the expected Tailscale webhook events. The steps of creating this Adapter and enabling the input include:

  1. Creating the Webhook Adapter via the LimaCharlie CLI.

  2. Discovering the URL created for the Webhook Adapter.

  3. Providing the completed URL to Tailscale for Webhook events.




### 1\. Creating the LimaCharlie Webhook Adapter

The following steps are modified from the generic Webhook Adapter creation doc, found [here](/v2/docs/tutorial-creating-a-webhook-adapter).

Creating a Webhook Adapter requires a set of parameters, including organization ID, Installation Key, platform, and mapping details. The following configuration has been provided to configure a Webhook Adapter for ingesting Tailscale events:
    
    
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
    

The mapping above is based on the expected Webhook event from Tailscale ([example provided here](https://tailscale.com/kb/1213/webhooks/)). Note that in the mapping above, we make the following change:

  * `event_type_path` is mapped to the `message` field




### 2\. Building the Webhook URL

After creating the webhook, you'll need to retrieve the webhook URL from the [Get Org URLs](https://docs.limacharlie.io/apidocs/get-org-urls) API call. You'll need the following information to complete the Webhook URL:

  * Organization ID

  * Webhook name (from the config)

  * Secret (from the config)




Let's assume the returned domain looks like `9157798c50af372c.hook.limacharlie.io`, the format of the URL would be:

`https://9157798c50af372c.hook.limacharlie.io/OID/HOOKNAME/SECRET`

Note that the `secret` value can be provided in the webhook URL or as an HTTP header named `lc-secret`.

### 3\. Providing the URL to Tailscale for Webhook Events

Within the Tailscale Admin Console, navigate to **Settings** > **Webhooks**. Select **Add endpoint...**

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28168%29.png)

Provide the completed Webhook URL from Step 2, above. You can also select the various events you want sent via Webhook. Options include:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28170%29.png)

Select **Add endpoint**. Tailscale will provide you a webhook secret unique to this endpoint. You may want to keep this value, however it is not required within LimaCharlie.

#### 4\. Test Webhook Output

Within the Tailscale Admin Console, you can test the webhook out and ensure that LimaCharlie is receiving events. Within the Webhook Endpoint options, select **Test endpoint...**.

You should see the webhook event populate within the LimaCharlie Adapter a moment later. Note that the `event_type` will match the `message` field from the Tailscale webhook event.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ Tailscale ](/docs/ext-cloud-cli-tailscale)



* * *

###### What's Next

  * [ VMWare Carbon Black ](/docs/adapter-types-vmware-carbon-black) __



Table of contents

    * Adapter Deployment 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


