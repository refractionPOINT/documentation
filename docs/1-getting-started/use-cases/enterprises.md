# Enterprise SOC

The LimaCharlie Agentic SecOps Workspace (ASW) is a unified platform for modern cybersecurity operations.

The ASW supplies core cybersecurity capabilities and infrastructure through a public cloud model: on-demand, pay-per-use, and API-first. For the cybersecurity industry, this is a large change, comparable to the change that the IT public cloud made in IT.

For enterprises and other large organizations, the Agentic SecOps Workspace is a way to control security posture and to scale operations. The ASW helps teams see their environments, remove coverage gaps, and solve integration problems. It also helps them decrease spending on high-cost tools, avoid vendor lock-in, and build custom security solutions for their organization.

## 3 implementation plans for immediate value

The Agentic SecOps Workspace is a platform for cybersecurity operations, but you do not have to set up all of it at one time. The delivery model of the ASW is similar to a public cloud, which removes the barriers to adoption for an enterprise. The ASW scales and is API-first. Teams can therefore integrate the platform into their security operations in stages, and use more of its capabilities with time. These are three recommended first steps that help an enterprise get value from the ASW quickly.

### 1. Centralize telemetry data to improve visibility and streamline operations

The Agentic SecOps Workspace lets an enterprise bring all of its telemetry data into one place. This improves visibility, removes coverage gaps, and makes SecOps workflows more efficient. This is a general outline of the process:

**Bring your telemetry data into the ASW.** The Agentic SecOps Workspace lets enterprise teams ingest data from any source. You can deploy the endpoint detection and response (EDR) sensors of the platform on Windows, Mac, and Linux endpoints with full feature parity. With these sensors, security teams capture system events and other telemetry data in real time. Teams can also import event data from third-party EDR tools such as VMWare Carbon Black, CrowdStrike, SentinelOne, or Microsoft Defender. Browser-based EDR sensors are also available for Chrome and Edge deployments.

You can also bring log data into the ASW with a system of adapters or through a webhook. Supported log data sources include O365, 1Password, AWS CloudTrail, Google Cloud Platform (GCP), Slack Audit logs, and many more. For a full list, refer to the ASW documentation.

**Visualize and manage your telemetry data under a single plane.** The ASW normalizes the telemetry data to a common JSON format, and you explore the data through one interface. The immediate advantage for security teams is better visibility and an end to the coverage gaps that put organizational security and compliance at risk. One interface to manipulate data also helps teams remove the integration problems that other solutions cause and make their internal workflows more efficient.

**Go beyond observability.** The data-routing capabilities of the Agentic SecOps Workspace let you use it as an observability point solution, but the ASW can do much more. All telemetry data in the platform can go through an advanced detection and response engine. The multiplatform ASW sensor also does response actions on endpoints at wire speed.

From the first day, security teams can use the ASW for centralization and observability. They can also apply their own custom detection and response (D&R) logic to all telemetry data in the platform. They can use curated rulesets such as Sigma, Soteria, or SOC Prime rules for the same purpose. They can also run historical threat hunts against the data that the ASW stores.

The Agentic SecOps Workspace helps an enterprise improve visibility, remove coverage gaps, solve integration problems, and make workflows more efficient. This is only the first step of what a team can do with the platform.

#### 2. Reduce spending on SIEMs and other high-cost solutions

The ASW lets security teams bring in data from any source and export it to any destination. You can therefore use the platform as a pass-through to observe, transform, enrich, and anonymize data in flight. You can also route the data to different destinations in detail. This strategy can decrease the costs of security information and event management (SIEM) tools and other expensive third-party solutions.

**Identify inefficiencies in your current data flow.** Many organizations send 100% of their telemetry data to their SIEM. They use only a fraction of that data, but they pay for all of it. Review how you route your telemetry data now. Decide which data must go to your highest-cost tools, and which data can stay in lower-cost storage.

**Use the ASW's output controls to optimize your data routing.** The options are flexible and customizable:

You can send telemetry data to Splunk, Humio, Elastic, Amazon S3 buckets, Azure Event Hubs, Google Cloud Storage, and many other destinations.

You can also stream data to your destinations with different levels of granularity. At the most verbose level, you send all data events from a sensor to one destination. You can also create a stream that sends only specific events to your output destination.

Enterprise teams can thus route their data for the best cost savings. For example, a team can send only high-priority detections and failed 1Password login attempts to Splunk. It can send a second set of log data and events to an Amazon S3 bucket, and keep all other data in low-cost cold storage.

**Use free storage and transparent pricing for compliance and additional savings.** The ASW gives one year of free storage of all telemetry data for the cost of ingestion. The pricing is transparent and easy to calculate, so you can find the most cost-effective data flow and storage sites for your telemetry. By default, the ASW keeps all telemetry data for one year in a fully searchable and explorable format. The total cost of storage in the ASW cloud is often much lower than the cost of a traditional data lake. Many organizations can therefore use the built-in storage of the platform to meet compliance requirements and decrease costs.

The data routing capabilities of the ASW give enterprise teams full control of their telemetry data. Teams decrease spending on high-cost solutions and keep access to the critical data that compliance and operations need.

#### 3. Simplify tooling and control your infrastructure

The Agentic SecOps Workspace supplies the core components that secure and monitor an organization. With time, an enterprise can use the many capabilities of the ASW to build a custom security infrastructure that it controls fully. That is a long-term project, but an enterprise that adopts the ASW can start to make its stack simpler immediately:

**Replace one-off solutions.** Cybersecurity products become more specialized, so most enterprise teams use a patchwork of solutions and sometimes buy a tool for one narrow use case. First, identify your one-off tools and vendors. Then decide how an ASW solution can replace each one. The Agentic SecOps Workspace has an ecosystem of more than 100 cybersecurity capabilities and integrations, and a marketplace of add-ons that extend the platform. In many cases, an ASW solution replaces a single-use vendor with equal or better performance, which decreases tool sprawl and improves security operations.

**Upgrade existing tools or features.** The cybersecurity vendor space is fragmented, so many enterprise teams use tools that are good in one area but weak in others. Do not accept the weak parts of your stack. Use the ASW to supplement or replace the tools and features that perform badly.

**Begin your transition to infrastructure independence.** After a team removes its one-off and redundant tools, it must plan how to use the ASW to end vendor lock-in. Look for vendor contracts that expire soon and for products that are near end-of-life. Work with LimaCharlie engineers to build, validate, and deploy a custom replacement before that date.

In the near term, the Agentic SecOps Workspace lets an enterprise make its deployments much simpler. In the long term, it lets an organization take full control of its tooling, infrastructure, and security posture.
