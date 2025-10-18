---
title: Sensor Tags
slug: sensor-tags
breadcrumb: Telemetry > Sensors
source: https://docs.limacharlie.io/docs/sensor-tags
articleId: 8bda6eed-2bc3-4d5b-8d8d-a79249afc305
---

* * *

Sensor Tags

  *  __31 Oct 2024
  *  __ 4 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Sensor Tags

  *  __Updated on 31 Oct 2024
  *  __ 4 Minutes to read 



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

Tags in LimaCharlie are simple strings that can be associated with any number of sensors. A Sensor can also have an arbitrary number of tags associated with it.

Tags appear in every event coming from a sensor under the `routing` component of the event. This greatly simplifies the writing of detection and response rules based on the presence of specific tags, at the cost of including more non-unique data per event.  
Tags can be used for a variety of purposes, including:

  * to classify endpoints

  * automate detection and response

  * create powerful workflows

  * trigger automations




## Use Cases for Sensor Tags

### Classification

You can use tags to classify an endpoint in a number of different ways based on what is important to you. Some examples of classifications are shown below for inspiration.

**Departments**

Create tags to classify endpoints based on what business department they belong to. e.g. sales, finance, operations, development, support, legal, executives.

**Usage Type**

You may wish to tag endpoints based on their type of usage. e.g. workstation, server, production, staging.

By having endpoints tagged in this manner you can easily identify endpoints and decide what actions you may wish to take while considering the tag. For example, if you see an endpoint is tagged with `workstation` and `executives`, and you happen to see suspicious activity on the endpoint, it may be worthwhile for you to prioritize response.

### Automating detection and response

You can use tags to automate detection and response.

For example, you can create a detection & response rule so that when a specific user logs in on a device, the box is tagged as `VIP-sales` and the sensor starts collecting an extended list of events from that box.

### Creating workflows

You can use tags to create workflows and automations. For instance, you can configure an output (forwarder) to send all detections containing `VIP-sales` tag to Slack so that you can review them asap, while detections tagged as `sales` can be sent to an email address.

### Trigger Automations

Create a Yara scanning rule so that endpoints tagged as 'sales' are continuously scanned against the specific sets of Yara signatures.

## Adding Tags

Tags can be added to a sensor a few different ways:

  1. Enrollment: the installation keys can optionally have a list of Tags that will get applied to sensors that use them.

  2. Manually: using the API as described below, either manually by a human or through some other integration.

  3. Detection & Response: automated detection and response rules can programatically add a tag (and check for tags).




### Manual API

Issue a `POST` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules. To achieve this, in the response part of the detection & response rule, specify the add tag action. For example, to tag a device as DESKTOP, you would say:
    
    
    - action: add tag
    tag: DESKTOP
    

## Removing Tags

### Manual API

Issue a `DELETE` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

### Manual in the web app

In the web app, click on the sensor in question to expand it. You will see the list of tags you can add/edit/remove.

## Checking Tags

### Manual API

Issue a `GET` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

## System Tags

We provide system level functionality with a few system tags. Those tags are listed below for reference:

### lc:latest

When you tag a sensor with `lc:latest`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the latest version of the sensor will be used instead. This means you can tag a representative set of computers in the Organization with the `lc:latest` tag in order to test-deploy the latest version and confirm no negative effects.

### lc:stable

When you tag a sensor with `lc:stable`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the _stable_ version of the sensor will be used instead. This means you can upgrade an organization as a whole, but leave a few specific sensors behind by assigning the lc:stable tag to them.

### lc:experimental

When you tag a sensor with `lc:experimental`, the sensor version currently assigned to the Organization will be ignored for that specific sensor. An experimental version of the sensor will be used instead. This tag is typically used when working with the LimaCharlie team to troubleshoot sensor-specific issues.

### lc:no_kernel

When you tag a sensor with `lc:no_kernel`, the kernel component will not be loaded on the host.

### lc:debug

When you tag a sensor with `lc:debug`, the debug version of the sensor currently assigned to the Organization will be used.

### lc:limit-update

When you tag a sensor with lc:limit-update, the sensor will not update the version it's running at run-time. The version will only be loaded when the sensor starts from scratch like after a reboot.

### lc:sleeper

When you tag a sensor with _lc:sleeper_ , the sensor will keep its connection to the LimaCharlie Cloud, but will disable all other functionality to avoid any impact on the system.

### lc:usage

When you tag a sensor with _lc:usage_ , the sensor will work as usual, but its connection will not count against the normal sensor quota. Instead, the time the sensor spends connected will be billed separately per second, and so will events received by the sensor. For more details, see [Sleeper Deployments](/v2/docs/sleeper).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

  * [ Response Actions ](/docs/response-actions)
  * [ Installation Keys ](/docs/installation-keys)
  * [ Template Strings and Transforms ](/docs/template-strings-and-transforms)
  * [ Endpoint Agent Versioning and Upgrades ](/docs/endpoint-agent-versioning-and-upgrades)
  * [ Updating Sensors to the Newest Version ](/docs/updating-sensors-to-the-newest-version)
  * [ Test a New Sensor Version ](/docs/test-a-new-sensor-version)



* * *

###### What's Next

  * [ Artifacts ](/docs/artifacts) __



Table of contents

    * Use Cases for Sensor Tags 
    * Adding Tags 
    * Removing Tags 
    * Checking Tags 
    * System Tags 



Tags

  * [ detection and response ](/docs/en/tags/detection%20and%20response)
  * [ platform ](/docs/en/tags/platform)
  * [ sensors ](/docs/en/tags/sensors)


