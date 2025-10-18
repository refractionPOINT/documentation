---
title: Splunk
slug: outputs-destinations-splunk
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-splunk
articleId: 9b5c335b-000f-4e6b-be79-fe99995c225f
---

* * *

Splunk

  *  __08 Oct 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Splunk

  *  __Updated on 08 Oct 2025
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

To send data from LimaCharlie to Splunk, you will need to configure an output.

Want to reduce Splunk spend?

[Watch the webinar recording](https://www.youtube.com/watch?v=lqPqkDkd7I8) to learn about using LimaCharlie to reduce spending on Splunk and other high-cost security data solutions.

### Splunk Setup

Follow Splunk's guide to [set up an HEC](https://docs.splunk.com/Documentation/Splunk/8.0.2/Data/UsetheHTTPEventCollector), and as you do, set the source type to `_json`.

### LimaCharlie Setup

From the **Outputs** view, click `Add Output`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/splunk-1.png)

Choose the type of stream you want to output from LimaCharlie.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/splunk-2\(1\).png)

Set `Webhook` or `Webhook Bulk` as a destination.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/splunk-3.png)

Enter the output name.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/splunk-4.png)

Enter the [correct HEC URI](https://docs.splunk.com/Documentation/Splunk/8.0.2/Data/UsetheHTTPEventCollector#Send_data_to_HTTP_Event_Collector) for your Splunk implementation as Destination Host. Use the /services/collector/event endpoint. Note if you are using Spunk Cloud, this will be the string from the URL `https://<host>.splunkcloud.com/`.

Here is a sample Splunk HEC configuration:

Destination Host = `https://host.domain.com:8088/services/collector/raw`  
Auth Header Name = Authorization  
Auth Header value = Splunk xxxxxx-xxxx-xxxx-xxxx-xxxxxx

Before saving the output, you can configure any of the advanced Output settings.

**Tag** \- Providing a tag name allows you to only send events from sensor with this tag. Tags can be managed at the sensor details view.

**Sensor** \- choosing a sensor ID will only send events or detections from this sensor.

Flatten will flatted the JSON; no changes are needed for the email configuration.

**Wrap JSON event with Event Type **- by default, we do not add prefix in front of every record. Prefix is useful for loading data into relational databases. If you are looking to receive a human-readable email, leave this option unchecked.

**Delete on Failure** \- when set to Yes, the system will completely delete the output configuration in case of failure. This is useful when you are configuring a temporary output needed for a short while and you don't want to have to worry about cleaning up later.

You can choose to only send a specific list of event types by configuring an allow list in the **Detection Category** section. Alternatively, if you want to exclude certain event types, you can denote it in a deny list **(Disallowed Detection Categories)**.

**Do not include routing** flag allows users to forward only the original logs to outputs, excluding the routing label. This can be helpful for users wanting to use LimaCharlie for storage optimization since the routing label can add significant overhead.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/splunk-5.png)

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

###### What's Next

  * [ Syslog ](/docs/outputs-destinations-syslog) __



Table of contents




Tags

  * [ outputs ](/docs/en/tags/outputs)


