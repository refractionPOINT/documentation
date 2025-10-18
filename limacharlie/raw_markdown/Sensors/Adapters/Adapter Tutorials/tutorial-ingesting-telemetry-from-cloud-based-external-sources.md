---
title: Tutorial: Ingesting Telemetry from Cloud-Based External Sources
slug: tutorial-ingesting-telemetry-from-cloud-based-external-sources
breadcrumb: Sensors > Adapters > Adapter Tutorials
source: https://docs.limacharlie.io/docs/tutorial-ingesting-telemetry-from-cloud-based-external-sources
articleId: 0329e83a-b7af-44ff-bc4a-f1fdc64a093f
---

* * *

Tutorial: Ingesting Telemetry from Cloud-Based External Sources

  *  __25 Apr 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Tutorial: Ingesting Telemetry from Cloud-Based External Sources

  *  __Updated on 25 Apr 2025
  *  __ 1 Minute to read 



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

LimaCharlie allows for ingestion of logs or telemetry from any external source in real-time. It includes built-in parsing for popular formats, with the option to define your own for custom sources.

There are two ways to ingest logs or telemetry from external sources:

  * Run the [LimaCharlie Adapter](/v2/docs/adapters) on premises or on your cloud

  * Provide credentials for the destination and allow LimaCharlie cloud to connect directly (available for cloud-based Adapters)




To connect with the cloud-based external source, first ensure you have the appropriate `cloudsensor.*` permissions.

After the permissions have been enabled, navigate to the `Sensors` page of the web app and click `Add Sensor`.

Choose an external source you would like to ingest logs or telemetry from, or filter the list to only include `Cloud & External Sources` to see available options.

If there is an external source you wish to connect that is not listed, you can still ingest via the LimaCharlie Adapter with self-defined parsing. Alternatively, please contact us to discuss adding this source in LimaCharlie.

After selecting the Sensor type, choose or create an [Installation Key](/v2/docs/installation-keys). Then, enter the name for the sensor and provide method-specific credentials for connection.

If the sensor you selected is cloud-based, you will see the call to action `Complete Cloud Installation`.

_Note: Sensors that support cloud to cloud communication, can also be installed by running an adapter on-prem or on cloud hosted by the customer. While it is a rare scenario, some customers might prefer that option when they do not want to share the sensor's API credentials with LimaCharlie._

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

  * [ Adapter Deployment ](/docs/adapter-deployment)
  * [ Adapter Usage ](/docs/adapter-usage)
  * [ Adapters ](/docs/adapters)
  * [ Adapter Types ](/docs/adapter-types)
  * [ Adapter Examples ](/docs/adapter-examples)
  * [ Tutorial: Creating a Webhook Adapter ](/docs/tutorial-creating-a-webhook-adapter)



* * *

###### What's Next

  * [ Adapter Usage ](/docs/adapter-usage) __



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ telemetry ](/docs/en/tags/telemetry)
  * [ tutorial ](/docs/en/tags/tutorial "Tutorial")


