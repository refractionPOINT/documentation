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

Google Cloud Storage

* 07 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Google Cloud Storage

* Updated on 07 Aug 2025
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

This Adapter allows you to ingest files/blobs stored in Google Cloud Storage (GCS).

Note that this adapter operates as a sink by default, meaning it will "consume" files from the GCS bucket by deleting them once ingested.

## Configurations

Adapter Type: `gcs`

* `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).
* `bucket_name`: the name of the bucket to ingest from.
* `service_account_creds`: the string version of the JSON credentials for a (Google) Service Account to use accessing the bucket.
* `prefix`: only ingest files with a given path prefix.
* `single_load`: if `true`, the adapter will not operate as a sink, it will ingest all files in the bucket once and will then exit.

### Infrastructure as Code Deployment

```
# Google Cloud Storage (GCS) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-gcs

sensor_type: "gcs"
gcs:
  bucket_name: "your-gcs-bucket-for-limacharlie-logs"
  service_account_creds: "hive://secret/gcs-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GCS"
    platform: "json"
    sensor_seed_key: "gcs-log-processor"
    mapping:
      sensor_hostname_path: "resource.labels.instance_id"
      event_type_path: "logName"
      event_time_path: "timestamp"
    indexing: []
  # Optional configuration
  prefix: "security_logs/firewall/"  # Filter by path prefix
  parallel_fetch: 5                  # Parallel downloads
  single_load: false                 # Continuous processing
```

## API Doc

See the [official documentation](https://cloud.google.com/storage).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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
* [Google Workspace](/docs/adapter-types-google-workspace)
* [Google Cloud BigQuery](/docs/outputs-destinations-google-cloud-bigquery)
* [Tutorial: Ingesting Google Cloud Logs](/docs/tutorial-ingesting-google-cloud-logs)
* [Google Cloud Pubsub](/docs/outputs-destinations-google-cloud-pubsub)
* [Google Cloud Pubsub](/docs/adapter-types-google-cloud-pubsub)
* [Google Cloud](/docs/ext-cloud-cli-google-cloud)

---

###### What's Next

* [SQS](/docs/adapter-types-sqs)

Table of contents

+ [Overview](#overview)
+ [Configurations](#configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [gcp](/docs/en/tags/gcp)
* [sensors](/docs/en/tags/sensors)
