# Adapters

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

> **Cloud Adapter Sinks**
> 
> Note - certain cloud-to-cloud adapters, such as AWS S3 and Google Cloud Storage ingest data as a sink, meaning blobs will be deleted as they are consumed. The ingestion API will require the ability to delete objects in these adapters. To avoid any errors, we recommend creating a dedicated bucket (with appropriate permissions) to ingest logs into LimaCharlie.

For other data streams, where unique connector details are required (e.g. Office 365 or Slack), we will provide guidance on establishing those connections. More information on pre-defined Adapters can be found [here](/v2/docs/adapter-types).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.