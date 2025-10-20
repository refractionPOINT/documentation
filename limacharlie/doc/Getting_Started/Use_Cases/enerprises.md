# Enterprise SOC

The LimaCharlie SecOps Cloud Platform (SCP) is a unified platform for modern cybersecurity operations.

The SCP delivers core cybersecurity capabilities and infrastructure via a public cloud model: on-demand, pay-per-use, and API-first. For the cybersecurity industry, this is a paradigm shift comparable to how the IT public cloud revolutionized IT.

For enterprises and other large organizations, the SecOps Cloud Platform is a powerful way to take control of security posture and scale operations. The SCP can help teams gain visibility into their environments, eliminate coverage gaps, solve integration challenges, reduce spending on high-cost tools, free themselves from vendor lock-in, and build custom security solutions to meet their organization's unique needs.

## 3 implementation plans for immediate value

The SecOps Cloud Platform is a comprehensive platform for cybersecurity operations—but it doesn't have to be implemented all at once. The SCP's public cloud-like delivery model eliminates adoption hurdles for enterprises. Easily scaled and API-first, the SCP enables teams to integrate the platform into their security operations gradually, leveraging its capabilities progressively as they go. Here are three recommended first steps to help enterprises realize value from the SCP quickly.

#### 1. Centralize telemetry data to improve visibility and streamline operations

The SecOps Cloud Platform allows enterprises to bring all of their telemetry data into one place—improving visibility, eliminating coverage gaps, and enabling streamlined SecOps workflows. Here is a general outline of what that looks like:

**Bring your telemetry data into the SCP.** The SecOps Cloud Platform allows enterprise teams to ingest data from any source. The platform's endpoint detection and response (EDR)-type sensors can be deployed directly on Windows, Mac, and Linux endpoints with full feature parity across these OSes. These sensors allow security teams to capture system events and other telemetry data in real time—or import event data from third-party EDR tools such as VMWare Carbon Black, CrowdStrike, SentinelOne, or Microsoft Defender. There are also browser-based EDR sensors to support Chrome and Edge deployments.

Log-type data can also be brought into the SCP using a system of adapters or via webhook. Supported log data sources include O365, 1Password, AWS CloudTrail, Google Cloud Platform (GCP), Slack Audit logs, and many more. For a comprehensive list, refer to the SCP documentation.

**Visualize and manage your telemetry data under a single plane.** Telemetry data brought into the SCP is normalized to a common JSON format and explorable through a single interface. The immediate advantage for security teams is improved visibility—and an end to coverage gaps that can jeopardize organizational security and compliance. In addition, the ability to manipulate data through a single UI helps teams eliminate integration challenges caused by other solutions and streamline their internal workflows.

**Go beyond observability.** The SecOps Cloud Platform's data-routing capabilities mean that it can be used as a simple observability point solution if you choose. But the SCP is capable of far more than this. All telemetry data brought into the platform can be run through an advanced detection and response engine, and wire-speed response actions can be taken on endpoints via the multiplatform SCP agent. From day one, security teams using the SCP for centralization and observability can also apply their own custom detection and response (D&R) logic to all telemetry data brought into the platform, leverage curated rulesets like Sigma, Soteria, or SOC Prime rules for the same purpose, or run historical threat hunts against data stored in the SCP.

The SecOps Cloud Platform helps enterprises improve visibility, eliminate coverage gaps, solve integration challenges, and make their workflows more efficient—and this is just the first step in what teams can achieve with the platform.

#### 2. Reduce spending on SIEMs and other high-cost solutions

Because the SCP lets security teams bring in data from any source and export it to any destination, the platform can also be used as a pass-through to observe, transform, enrich, and anonymize data in-flight and route it to different destinations in a fine-grained way. This strategy can significantly reduce the costs of security information and event management (SIEM) tools and other expensive third-party solutions.

**Identify inefficiencies in your current data flow.** Many organizations simply send 100% of their telemetry data to their SIEM. They only use a fraction of that data, but they pay for all of it. Conduct a thorough review of how you are currently routing your telemetry data. Determine what data truly needs to be sent to your highest-cost tools—and what can be retained in lower-cost storage.

**Use the SCP's output controls to optimize your data routing.** Your options here are highly flexible and customizable:

Telemetry data can be sent to Splunk, Humio, Elastic, Amazon S3 buckets, Azure Event Hubs, Google Cloud Storage, and many other destinations.

Data can also be streamed to your destination(s) of choice with different degrees of granularity. On the more verbose end of the spectrum, it is possible to send all data events from a sensor to a given destination. But you can also create a tailored stream that sends only specific events to your output destination.

Enterprise teams can thus route their data for optimal cost savings. For example, a team might send only high-priority detections and failed 1Password login attempts to Splunk, a secondary tranche of log data and events to an Amazon S3 bucket, and retain everything else in low-cost cold storage.

**Use free storage and transparent pricing for compliance and additional savings.** The SCP offers one year of free storage of all telemetry data for the cost of ingestion. Pricing is transparent and easy to calculate, making it simple to determine the most cost-effective data flow and storage sites for your telemetry. All telemetry data is retained for one year by default in a fully searchable and explorable format, so you don't have to worry about losing data that you may need later on. Because the total cost of storage in the SCP cloud is often far more affordable than traditional data lakes, many organizations will be able to use the platform's built-in storage to address compliance requirements and reduce costs.

The SCP's data routing capabilities put enterprise teams in full control of their telemetry data, allowing them to cut spending on high-cost solutions while ensuring access to critical data in order to meet compliance and operational needs.

#### 3. Simplify tooling and control your infrastructure

The SecOps Cloud Platform delivers the core components required to secure and monitor any organization. Over time, enterprises can leverage the SCP's numerous capabilities to develop a custom security infrastructure that they control completely. And while that is clearly a long-term project, enterprises that adopt the SCP can begin using the platform to simplify their stack right away:

**Replace one-off solutions.** The increasing specialization of cybersecurity products means most enterprise teams rely on a patchwork of solutions—and are sometimes forced to buy a tool to satisfy one, extremely narrow use case. Teams should begin by identifying their one-off tools and vendors and determining how they can be replaced with an SCP solution. The SecOps Cloud Platform offers a rich ecosystem of 100+ cybersecurity capabilities and integrations and a marketplace of add-ons to extend the platform. In many cases, teams will find that it is possible to replace single-use vendors with an SCP solution that offers equal or better performance, reducing tool sprawl and improving security operations at the same time.

**Upgrade existing tools or features.** The fragmentation of the current cybersecurity vendor space means that many enterprise teams end up using tools that excel in one arena but fall short in others. Instead of simply accepting the unsatisfactory parts of their stack, teams can use the SCP to augment or replace underperforming tools and features with best-in-breed alternatives.

**Begin your transition to infrastructure independence.** After teams shed one-off and redundant tools, they should begin to think strategically about how to leverage the SCP to free themselves from vendor lock-in once and for all. Look for vendor contracts due to expire or products nearing end-of-life and work with LimaCharlie engineers to develop, validate, and deploy a custom replacement ahead of time.

In the near term, the SecOps Cloud Platform lets enterprises simplify their deployments significantly. In the long term, it allows organizations to take full control of their tooling, infrastructure, and security posture.

## What's Next

* [[service-providers-mssp-msp-mdr|Security Service Providers (MSSP, MSP, MDR)]]
