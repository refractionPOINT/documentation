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

Endpoint Agent

* 01 Nov 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Endpoint Agent

* Updated on 01 Nov 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The LimaCharlie Endpoint Agent is a key component of LimaCharlie’s security platform, acting as a Sensor that collects rich endpoint detection and response (EDR) telemetry. Installed on endpoint devices, the agent continuously monitors system activity, gathering data on processes, network connections, file changes, and user behavior. This telemetry is then sent to LimaCharlie’s cloud for analysis, enabling real-time detection of potential threats and incidents.

Beyond data collection, the agent also supports automated response actions based on customizable detection rules. These actions include isolating compromised endpoints, killing malicious processes, and quarantining suspicious files, allowing for quick containment and mitigation of security risks. By functioning as both a sensor and an active responder, the LimaCharlie Endpoint Agent provides organizations with a powerful tool for detecting, analyzing, and responding to threats in real-time.

## Endpoint Agent Types

* [Windows](/v2/docs/windows-agent-installation)
* [Mac](/v2/docs/macos-agent-installation)
* [Linux](/v2/docs/linux-agent-installation)
* [Chrome](/v2/docs/chrome-agent-installation)
* [Edge](/v2/docs/edge-agent-installation)

Don't see what you're looking for?

Need support for a platform you don't see here? Get in touch via [Slack](https://slack.limacharlie.io) or email.

## Quota

All sensors register with the cloud, and many of them may go online / offline over the course of a regular day. For billing purposes, organizations must specify a sensor quota which represents the number of **concurrent online sensors** allowed to be connected to the cloud.

If the quota is maxed out when a sensor attempts to come online, the sensor will be dismissed and a `sensor_over_quota` event will be emitted in the deployments stream.

For more information, see [Billing](/v2/docs/billing) and [Billing FAQ](/v2/docs/faq-billing).

## Events

All sensors observe host & network activity, packaging telemetry and sending it to the cloud. The types of observable events are dependent on the sensor's type.

For an introduction to events and their structure, check out [Events](/v2/docs/events).

## Commands

Windows, Mac, Linux, Chrome, and Edge sensors all offer commands as a safe way of interacting with a host for investigation, management, or threat mitigation purposes.

For an introduction to commands and their usage, check out [Endpoint Agent Commands](/v2/docs/endpoint-agent-commands).

## Installation Keys

Read more about Installation Keys and their recommended usage [here](/v2/docs/installation-keys).

## Sensor Versions & Upgrades

Read more about Endpoint Agent Versioning [here](/v2/docs/endpoint-agent-versioning-and-upgrades).

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

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

* [Sensors](/docs/sensors)
* [Windows Agent Installation](/docs/windows-agent-installation)
* [Endpoint Agent Uninstallation](/docs/endpoint-agent-uninstallation)
* [Endpoint Agent Versioning and Upgrades](/docs/endpoint-agent-versioning-and-upgrades)
* [Installation Keys](/docs/installation-keys)
* [Sensor Connectivity](/docs/sensor-connectivity)

---

###### What's Next

* [Endpoint Agent Commands](/docs/endpoint-agent-commands)

Table of contents

+ [Endpoint Agent Types](#endpoint-agent-types)
+ [Quota](#quota)
+ [Events](#events)
+ [Commands](#commands)
+ [Installation Keys](#installation-keys)
+ [Sensor Versions &amp; Upgrades](#sensor-versions-amp-upgrades)

Tags

* [browser agent](/docs/en/tags/browser%20agent)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [linux](/docs/en/tags/linux)
* [macos](/docs/en/tags/macos)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
