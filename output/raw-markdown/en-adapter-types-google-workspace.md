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

Google Workspace

* 31 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Google Workspace

* Updated on 31 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

[Google Workspace](https://workspace.google.com/) provides various communication, collaboration, and productivity applications for businesses of all sizes. [Google Workspace audit logs](https://cloud.google.com/logging/docs/audit/gsuite-audit-logging) provide data to help track "Who did what, where, an when?".

Google Workspace Audit logs can be ingested via a Google Cloud Platform, deploye as a cloud-to-cloud LimaCharlie Adapter. Events will be ingested and observed via the `gcp` platform.

## Adapter Deployment

Prior to ingesting Google Workspace Audit logs in LimaCharlie, you must first configure logs to be written to GCP. Afterwards, a cloud-to-cloud GCP Adapter can be deployed to ingest these events into LimaCharlie.

The following steps help prepare this:

**Step 1: Enable Platform Sharing in Google Workspace**

In the Google Workspace admin console navigate to [Account -> Account Settings -> Legal and Compliance](https://admin.google.com/u/1/ac/companyprofile/legal)

Verify that under "Sharing options", `Google Cloud Platform Sharing Options` is set to Enabled.

For further details, refer to [Google's documentation on Audit logs for Google Workspace](https://cloud.google.com/logging/docs/audit/gsuite-audit-logging)

**Step 2: Verify logs appear in Google Cloud Platform**

In the GCP Console go to the [Logs Explorer](https://console.cloud.google.com/logs/query).  Ensure you're at the organization level (and not in a particular folder).

From the Resources drop-down, choose `Audited Resource`, then press Apply.

You should see logging details related to Google Workspace, under the following log name(s):

`logName:admin.googleapis.com`

**Step 3: Create a cloud-to-cloud GCP Adapter**

Once Google Workspace Audit logs are pushed to GCP, events can be ingested via either [Google Cloud Storage](/v2/docs/adapter-types-google-cloud-storage) or [Google Cloud Pubsub](/v2/docs/adapter-types-google-cloud-pubsub). Utilize the appropriate documentation to set up the desired Adapter.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Google Cloud Platform

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

* [Google Cloud Storage](/docs/outputs-destinations-google-cloud-storage)
* [Building Reports with BigQuery + Looker Studio](/docs/tutorials-reporting-building-reports-with-bigquery-looker-studio)
* [Google Cloud BigQuery](/docs/outputs-destinations-google-cloud-bigquery)
* [Tutorial: Ingesting Google Cloud Logs](/docs/tutorial-ingesting-google-cloud-logs)
* [Google Cloud Pubsub](/docs/outputs-destinations-google-cloud-pubsub)
* [Google Cloud Storage](/docs/adapter-types-google-cloud-storage)
* [Google Cloud Pubsub](/docs/adapter-types-google-cloud-pubsub)
* [Google Cloud](/docs/ext-cloud-cli-google-cloud)

---

###### What's Next

* [Azure Key Vault](/docs/azure-logs-key-vault)

Table of contents

+ [Adapter Deployment](#adapter-deployment)

Tags

* [adapters](/docs/en/tags/adapters)
* [gcp](/docs/en/tags/gcp)
* [google workspace](/docs/en/tags/google%20workspace)
* [sensors](/docs/en/tags/sensors)
