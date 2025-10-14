# Adapter Tutorials

## Tutorial: Creating a Webhook Adapter

LimaCharlie supports webhooks as a telemetry ingestion method. Webhooks are technically cloud Adapters, as they cannot be deployed on-prem or through the downloadable Adapter binary. Webhook adapters are created by enabling a webhook through the platform.

## Tutorial: Ingesting Google Cloud Logs

With LimaCharlie, you can easily ingest Google Cloud logs for further processing and automation. This article covers the following high-level steps of shipping logs from GCP into LimaCharlie:

- Create a Log Sink to Pubsub in GCP
- Create a Subscription to the Pubsub topic
- Configure LimaCharlie to ingest from the subscription

## Tutorial: Ingesting Telemetry from Cloud-Based External Sources

LimaCharlie allows for ingestion of logs or telemetry from any external source in real-time. It includes built-in parsing for popular formats, with the option to define your own for custom sources. There are two ways to ingest logs or telemetry from external sources:

- Using webhooks for push-based ingestion
- Using adapters for pull-based ingestion from cloud services