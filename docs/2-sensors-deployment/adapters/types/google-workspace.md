# Google Workspace

[Google Workspace](https://workspace.google.com/) gives communication, collaboration, and productivity applications to businesses of all sizes. [Google Workspace audit logs](https://cloud.google.com/logging/docs/audit/gsuite-audit-logging) supply data that helps you track "Who did what, where, and when?".

LimaCharlie ingests Google Workspace Audit logs through Google Cloud Platform, with a cloud-to-cloud LimaCharlie Adapter. The `gcp` platform ingests and shows the events.

## Adapter Deployment

Before LimaCharlie can ingest Google Workspace Audit logs, you must configure the logs to write to GCP. Then deploy a cloud-to-cloud GCP Adapter to ingest these events into LimaCharlie.

These steps prepare the deployment:

### Step 1: Enable Platform Sharing in Google Workspace

In the Google Workspace admin console, go to [Account -> Account Settings -> Legal and Compliance](https://admin.google.com/u/1/ac/companyprofile/legal).

Under "Sharing options", check that `Google Cloud Platform Sharing Options` is set to Enabled.

For more details, see [Google's documentation on Audit logs for Google Workspace](https://cloud.google.com/logging/docs/audit/gsuite-audit-logging).

### Step 2: Verify logs appear in Google Cloud Platform

In the GCP Console, go to the [Logs Explorer](https://console.cloud.google.com/logs/query). Make sure that you are at the organization level, and not in a folder.

From the Resources drop-down, choose `Audited Resource`. Then press Apply.

Log details for Google Workspace appear under this log name:

`logName:admin.googleapis.com`

### Step 3: Create a cloud-to-cloud GCP Adapter

After GCP receives the Google Workspace Audit logs, you can ingest the events with [Google Cloud Storage](google-cloud-storage.md) or [Google Cloud Pubsub](google-cloud-pubsub.md). Use the page for the Adapter that you choose.
