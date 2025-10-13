[## HubSpot

Overview This Adapter allows you to connect to HubSpot to fetch account activity logs . Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webh...](/docs/adapter-types-hubspot)

Updated on : 16 Jul 2025

[## Google Workspace

Google Workspace provides various communication, collaboration, and productivity applications for businesses of all sizes. Google Workspace audit logs provide data to help track "Who did what, where, an when?". Google Workspace Audit logs can b...](/docs/adapter-types-google-workspace)

Updated on : 31 Oct 2024

[## Azure Logs

5 Articles  in this category](/docs/telemetry-adapters-adapter-types-azure-logs)

[## 1Password

1Password provides an events API to fetch audit logs. Events can be ingested directly via a cloud-to-cloud or CLI Adapter . See 1Password's official API documentation here . 1Password telemetry can be addressed via the 1password platform. A...](/docs/1password)

Updated on : 15 Aug 2025

[## Atlassian

Atlassian makes a suite of products that help foster enterprise work management, IT service management, and Agile development. Atlassian's products include: Bitbucket Confluence Jira Work Management (this includes a suite of products, inc...](/docs/atlassian)

Updated on : 28 May 2025

[## AWS CloudTrail

AWS CloudTrail logs allow you to monitor AWS deployments. CloudTrail logs can provide granular visibility into AWS instances and can be used within D&R rules to identify AWS abuse. This Adapter allows you to ingest AWS CloudTrail events...](/docs/adapter-types-aws-cloudtrail)

Updated on : 01 Nov 2024

[## AWS GuardDuty

Overview This Adapter allows you to ingest AWS GuardDuty events via either an S3 bucket or SQS message queue . AWS GuardDuty helps you protect your AWS accounts with intelligent threat detection. Telemetry Platform: guard\_duty Deploym...](/docs/adapter-types-aws-guardduty)

Updated on : 06 Jun 2025

[## Azure Event Hub

Overview This Adapter allows you to connect to an Azure Event Hub to fetch structured data stored there. Azure Event Hubs are fully managed, real-time data ingestion services that allow for event streaming from various Microsoft Azure services...](/docs/adapter-types-azure-event-hub)

Updated on : 16 Jul 2025

[## Canarytokens

Canarytokens are a free, quick, painless way to help defenders discover they've been breached (by having attackers announce themselves). Canarytokens are digital traps, or tripwires, that can be placed in an organization's network as a "lure" for ad...](/docs/adapter-types-canarytokens)

Updated on : 24 Apr 2025

[## Cato

Overview This Adapter allows you to connect to the Cato API to fetch logs from the events feed . Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creati...](/docs/adapter-types-cato)

Updated on : 16 Jul 2025

[## CrowdStrike Falcon Cloud

Overview This Adapter allows you to connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console. Deployment Configurations All adapters support the same client\_options , which you should always spec...](/docs/adapter-types-crowdstrike-falcon-cloud)

Updated on : 16 Jul 2025

[## Duo

Overview This Adapter allows you to connect to the Duo Admin API and fetch logs from it. Configurations Adapter Type: duo client\_options : common configuration for adapter as defined here . integration\_key : an integration key create...](/docs/adapter-types-duo)

Updated on : 16 Jul 2025

[## EVTX

Overview This Adapter allows you to ingest and convert a .evtx file into LimaCharlie. The .evtx files are the binary format used by Microsoft for Windows Event Logs. This is useful to ingest historical Windows Event Logs, for example during a...](/docs/adapter-types-evtx)

Updated on : 07 Aug 2025

[## File

Overview This Adapter allows you to ingest logs from a file, either as a one time operation or by following its output (like tail -f ). A more detailed guide to file collection can be found in the Log Collection Guide . Configuration All ad...](/docs/adapter-types-file)

Updated on : 20 Aug 2025

[## Google Cloud Pubsub

Overview This Adapter allows you to ingest events from a Google Cloud Pubsub subscription. Configurations Adapter Type: pubsub client\_options : common configuration for adapter as defined here . sub\_name : the name of the subscriptio...](/docs/adapter-types-google-cloud-pubsub)

Updated on : 07 Aug 2025

[## Google Cloud Storage

Overview This Adapter allows you to ingest files/blobs stored in Google Cloud Storage (GCS). Note that this adapter operates as a sink by default, meaning it will "consume" files from the GCS bucket by deleting them once ingested. Configuration...](/docs/adapter-types-google-cloud-storage)

Updated on : 07 Aug 2025

[## SQS

Overview This Adapter allows you to ingest events received from an AWS SQS instance. Configurations Adapter Type: sqs client\_options : common configuration for adapter as defined here . access\_key : an Access Key from AWS used to a...](/docs/adapter-types-sqs)

Updated on : 07 Aug 2025

[## IIS Logs

Microsoft's Internet Information Services (IIS) web server is a web server commonly found on Microsoft Windows servers. This Adapter assists with sending IIS web logs to LimaCharlie via the Adapter binary. Telemetry Platform (if applicable): iis...](/docs/adapter-types-iis)

Updated on : 06 Dec 2024

[## IMAP

Overview This Adapter allows you to ingest emails as events from an IMAP server. Configurations Adapter Type: imap client\_options : common configuration for adapter as defined here . server : the domain and port of the IMAP server, l...](/docs/adapter-types-imap)

Updated on : 07 Aug 2025

[## IT Glue

Overview This Adapter allows you to connect to IT Glue to fetch activity logs. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook adapte...](/docs/adapter-types-it-glue)

Updated on : 07 Aug 2025

[## JSON

Overview This Adapter allows you to ingest logs from a file as JSON. Adapter type: file Configuration All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook adapte...](/docs/adapter-types-json)

Updated on : 06 Jun 2025

[## Kubernetes Pods Logs

Overview This Adapter allows you to ingest the logs from the pods running in a Kubernetes cluster. The adapter relies on local filesystem access to the standard Kubernetes pod logging structure. This means the adapter is best run as a Daemon Set...](/docs/adapter-types-kubernetes-pods-logs)

Updated on : 16 Jul 2025

[## Mac Unified Logging

Overview This Adapter allows you to collect events from MacOS Unified Logging. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook adapte...](/docs/adapter-types-mac-unified-logging)

Updated on : 16 Jul 2025

[## Microsoft Defender

Overview LimaCharlie can ingest Microsoft 365 Defender logs via three methods Azure Event Hub Adapter , the Microsoft Defender API , or a Custom Webhook Documentation for creating an event hub can be found here here . Telemetry Platform: ...](/docs/adapter-types-microsoft-defender)

Updated on : 07 Aug 2025

[## Microsoft Entra ID

Microsoft Entra ID , formerly Azure Active Directory, is an identity and access management solution from Microsoft that helps organizations secure and manage identities for hybrid and multicloud environments. The Entra ID API Adapter currently rec...](/docs/adapter-types-microsoft-entra-id)

Updated on : 06 Jun 2025

[## Microsoft 365

Microsoft 365, formerly Office 365, is a product family of productivity software, collaboration and cloud-based services owned by Microsoft. This Adapter allows you to ingest audit events from the Office 365 Management Activity API . Microsoft 3...](/docs/adapter-types-microsoft-365)

Updated on : 07 Aug 2025

[## Mimecast

Overview This Adapter allows you to connect to the Mimecast API to stream audit events as they happen. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or c...](/docs/adapter-types-mimecast)

Updated on : 07 Aug 2025

[## Okta

Overview This Adapter allows you to connect to Okta to fetch system logs. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook adapter. If...](/docs/adapter-types-okta)

Updated on : 07 Aug 2025

[## PandaDoc

Overview This Adapter allows you to connect to PandaDoc to fetch API logs . Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook adapter....](/docs/adapter-types-pandadoc)

Updated on : 07 Aug 2025

[## S3

Overview This Adapter allows you to ingest files/blobs stored in AWS S3. Note that this adapter operates as a sink by default, meaning it will "consume" files from the S3 bucket by deleting them once ingested. AWS S3 Requirements Required ...](/docs/adapter-types-s3)

Updated on : 07 Aug 2025

[## Slack Audit Logs

Slack audit logs allow for ingestion of audit events in a Slack Enterprise Grid organization. Events can be ingested directly from the Slack API via a cloud-to-cloud or CLI Adapter . Slack telemetry can be addressed via the slack platform. N...](/docs/adapter-types-slack-audit-logs)

Updated on : 25 Apr 2025

[## SentinelOne

This Adapter allows you to stream SentinelOne activities, threats, and alerts to LimaCharlie via SentinelOne API. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binar...](/docs/sentinelone)

Updated on : 04 Apr 2025

[## Sophos

Overview This Adapter allows you to connect to Sophos Central to fetch event logs. Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webhook ad...](/docs/adapter-types-sophos)

Updated on : 07 Aug 2025

[## Stdin

Overview This Adapter allows you to ingest logs from the adapter stdin. Configurations Adapter Type: stdin client\_options : common configuration for adapter as defined here . API Doc None](/docs/adapter-types-stdin)

Updated on : 06 Jun 2025

[## Syslog

Fix typo in the config example.](/docs/adapter-types-syslog)

Updated on : 20 Aug 2025

[## Sublime Security

Sublime Security is a comprehensive email security platform that allows users to create custom detections, gain visibility and control, and focus on prevention of malicious emails. Ingesting Audit Logs Audit logs from Sublime can be ingested clo...](/docs/adapter-types-sublime-security)

Updated on : 07 Aug 2025

[## Tailscale

Tailscale is a VPN service that makes devices and applications accessible anywhere in the world. Relying on the open source WireGuard protocol, Tailscale enables encrypted point-to-point connections. Tailscale events can be ingested in LimaCharli...](/docs/adapter-types-tailscale)

Updated on : 25 Apr 2025

[## VMWare Carbon Black

Overview LimaCharlie can ingest Carbon Black events from a number of storage locations. Typically, an organization would export Carbon Black data via the API to a storage mechanism, such as an S3 bucket, which would then be ingested by LimaCharlie....](/docs/adapter-types-vmware-carbon-black)

Updated on : 06 Jun 2025

[## Windows Event Log

Overview This Adapter allows you to connect to the local Windows Event Logs API on Windows. This means this Adapter is only available from Windows builds and only works locally (will not connect to remote Windows instances). Configurations Adap...](/docs/adapter-types-windows-event-log)

Updated on : 30 Jul 2025

[## Zendesk

Overview This Adapter allows you to connect to Zendesk to fetch account activity logs . Deployment Configurations All adapters support the same client\_options , which you should always specify if using the binary adapter or creating a webh...](/docs/adapter-types-zendesk)

Updated on : 07 Aug 2025
