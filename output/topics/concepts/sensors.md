# Sensors

## Overview

In LimaCharlie, **Sensors** refer to the broad set of telemetry collection mechanisms used to gather, process, and act on data across a variety of environments. Sensors come in different forms, each designed to capture specific types of data to provide comprehensive visibility and security across endpoints, networks, and cloud platforms.

* [**Endpoint Agents**](../reference/endpoint-agent.md) are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more. The data is streamed back to the LimaCharlie platform where it can be analyzed, used in detection and response rules, or forwarded to other systems. Endpoint agents provide detailed, granular insight into endpoint security and are typically used for threat detection, investigation, and response.
* [**Adapters**](adapters.md) serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

  + **On-Premise Adapters** are deployed within a local infrastructure and are capable of ingesting structured data from various sources like JSON, Syslog, or CEFL. These adapters transform any available telemetry into first-class data streams that can be integrated into LimaCharlie's detection and automation systems, allowing you to act on data from non-traditional sources.
  + **Cloud Adapters** operate in cloud-to-cloud connections, enabling direct data intake from cloud platforms and services. LimaCharlie offers pre-defined Adapters for common cloud services like AWS CloudTrail, Google Cloud, and Microsoft 365. These Adapters are typically configured to ingest log data or events without the need for custom deployment, making it easy to centralize cloud-based telemetry for detection and analysis.

All Sensor types—whether endpoint agents or adapters—are recognized as first-class data sources in LimaCharlie, giving users complete flexibility to manage, analyze, and automate security workflows based on the data collected.

> Note on network connectivity:
>
> You can find details about how the LimaCharlie Sensors communicate with the cloud in our [FAQ](/v2/docs/faq-sensor-installation).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.