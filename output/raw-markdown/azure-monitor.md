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

Azure Monitor

* 03 Jan 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Azure Monitor

* Updated on 03 Jan 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Azure Monitor Logs are a feature of Azure Monitor that collect and organize log and performance data from monitored resources. More information on Azure Monitor Logs can be found [here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs).

LimaCharlie can ingest and natively parse Azure Monitor Logs.

## Log Ingestion

Azure Monitor logs can be ingested via:

* [Azure Event Hub](/v2/docs/adapter-types-azure-event-hub)
* LimaCharlie [Webhooks](/v2/docs/tutorial-creating-a-webhook-adapter)

Upon ingestion, the log `category` field is used to define the Event Type.

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

* [Azure SQL Audit Logs](/docs/azure-sql-audit-logs)
* [Azure Event Hub](/docs/adapter-types-azure-event-hub)
* [Azure Storage Blob](/docs/outputs-destinations-azure-storage-blob)
* [Azure](/docs/ext-cloud-cli-azure)
* [Azure Network Security Group](/docs/azure-network-security-group)
* [Azure Kubernetes Service (AKS)](/docs/azure-kubernetes-service)
* [Azure Key Vault](/docs/azure-logs-key-vault)
* [Azure Event Hub](/docs/outputs-destinations-azure-event-hub)
* [Microsoft Entra ID](/docs/adapter-types-microsoft-entra-id)

---

###### What's Next

* [Azure Network Security Group](/docs/azure-network-security-group)

Table of contents

+ [Log Ingestion](#log-ingestion)

Tags

* [azure](/docs/en/tags/azure)
* [sensors](/docs/en/tags/sensors)
