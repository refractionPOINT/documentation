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

Sensors

* 08 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Sensors

* Updated on 08 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Overview

In LimaCharlie, **Sensors** refer to the broad set of telemetry collection mechanisms used to gather, process, and act on data across a variety of environments. Sensors come in different forms, each designed to capture specific types of data to provide comprehensive visibility and security across endpoints, networks, and cloud platforms.

* [**Endpoint Agents**](/v2/docs/endpoint-agent) are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more. The data is streamed back to the LimaCharlie platform where it can be analyzed, used in detection and response rules, or forwarded to other systems. Endpoint agents provide detailed, granular insight into endpoint security and are typically used for threat detection, investigation, and response.
* [**Adapters**](/v2/docs/adapters) serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

  + **On-Premise Adapters** are deployed within a local infrastructure and are capable of ingesting structured data from various sources like JSON, Syslog, or CEFL. These adapters transform any available telemetry into first-class data streams that can be integrated into LimaCharlie’s detection and automation systems, allowing you to act on data from non-traditional sources.
  + **Cloud Adapters** operate in cloud-to-cloud connections, enabling direct data intake from cloud platforms and services. LimaCharlie offers pre-defined Adapters for common cloud services like AWS CloudTrail, Google Cloud, and Microsoft 365. These Adapters are typically configured to ingest log data or events without the need for custom deployment, making it easy to centralize cloud-based telemetry for detection and analysis.

All Sensor types—whether endpoint agents or adapters—are recognized as first-class data sources in LimaCharlie, giving users complete flexibility to manage, analyze, and automate security workflows based on the data collected.

> Note on network connectivity:
>
> You can find details about how the LimaCharlie Sensors communicate with the cloud in our [FAQ](/v2/docs/faq-sensor-installation).

Don't see what you're looking for?

Need support for a platform you don't see here? Drop a note in the [LimaCharlie Community](https://community.limacharlie.com/) chat.

Amazon Web Services

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

* [Endpoint Agent Events Overview](/docs/endpoint-agent-events-overview)
* [Endpoint Agent Installation](/docs/endpoint-agent-installation)
* [Endpoint Agent](/docs/endpoint-agent)

---

###### What's Next

* [Installation Keys](/docs/installation-keys)

Table of contents

+ [Overview](#overview)

Tags

* [sensors](/docs/en/tags/sensors)
