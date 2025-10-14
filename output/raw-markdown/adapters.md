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

Adapters

* 31 Oct 2024
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Adapters

* Updated on 31 Oct 2024
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The LimaCharlie Adapter provides real-time ingestion of logs and other telemetry. Adapters allow you to send *any* data to LimaCharlie, which becomes an observable telemetry stream. All ingested data is recognized as a first-class data source, allowing you to write [detection & response rules](/v2/docs/detection-and-response) directly against Adapter events or [output](/v2/docs/outputs) Adapter data to other destinations.

The LimaCharlie Adapter:

* Supports ingestion of any structured data, such as JSON, Syslog, or CEFL
* Can be deployed on-prem or via a cloud-to-cloud connector
* Ingest log data without the need for an Endpoint Agent.
* Can run alongside the Endpoint Agent to allow for additional telemetry collection.

For certain well known Adapter sources, we offer built-in mapping and recognition of events. This allows you to ingest a known source without the need to parse event structure yourself. Well-known Adapter types include cloud platforms, various third-party applications, and sources like Windows Event Logs.

Key concepts of Adapters include [deployment options](/v2/docs/adapter-deployment) and [usage/configurations](/v2/docs/adapter-usage).

## Text Adapters

Text-based Adapters facilitate the ingestion of *any* structured text into LimaCharlie. Events are ingested and normalized as JSON text events, however custom mapping options allow you to customize fields and data structures as you see fit. Ingested data is also observed via detection and response rules, allowing you to ingest any data source and automate on those events.

## Pre-defined Adapters

LimaCharlie has pre-defined Adapter types that offer built-in mapping and guided adapter setups. Note that our guided setups often utilize common ingestion methods, however are designed to help you quickly deploy an Adapter for frequent log sources.

For example, AWS CloudTrail *and* Amazon GuardDuty logs are available for ingestion from either an AWS S3 bucket or Simple Queue Service (SQS) events. Thus, the web app "helper" walks you through setting up either one of those sources, depending on your needs and architecture.

Cloud Adapter Sinks

Note - certain cloud-to-cloud adapters, such as AWS S3 and Google Cloud Storage ingest data as a sink, meaning blobs will be deleted as they are consumed. The ingestion API will require the ability to delete objects in these adapters. To avoid any errors, we recommend creating a dedicated bucket (with appropriate permissions) to ingest logs into LimaCharlie.

For other data streams, where unique connector details are required (e.g. Office 365 or Slack), we will provide guidance on establishing those connections. More information on pre-defined Adapters can be found [here](/v2/docs/adapter-types).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

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

* [Tutorial: Ingesting Telemetry from Cloud-Based External Sources](/docs/tutorial-ingesting-telemetry-from-cloud-based-external-sources)
* [Installation Keys](/docs/installation-keys)
* [Template Strings and Transforms](/docs/template-strings-and-transforms)

---

###### What's Next

* [Stdin](/docs/adapter-examples-stdin)

Table of contents

+ [Text Adapters](#text-adapters)
+ [Pre-defined Adapters](#pre-defined-adapters)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
