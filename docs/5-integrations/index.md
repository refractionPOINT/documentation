# Integrations

LimaCharlie connects to external systems in three directions: outbound (sending data out), inbound (acting on external data), and enrichment (pulling context into detections). This section covers all three.

## Outbound — get data out of LimaCharlie

[**Outputs**](outputs/index.md) stream telemetry, detections, audit logs, and deployment events to external destinations on a continuous basis. Use them to feed your SIEM, archive to object storage, or trigger external systems via webhook.

Destination categories:

- **SIEM / streaming**: Splunk, Elastic, OpenSearch, Humio, Apache Kafka
- **Object storage**: Amazon S3, Azure Storage Blob, Google Cloud Storage, BigQuery, SCP, SFTP
- **Messaging**: Slack, Microsoft Teams, Telegram, SMTP, Tines
- **HTTP**: Webhook (single), Webhook (bulk)
- **Cloud streaming**: Azure Event Hub, Google Pub/Sub, syslog

See [Outputs](outputs/index.md) for the complete list and operational reference (testing, allowlisting, billing, stream structures).

## Inbound — let LimaCharlie act on external systems

[**Extensions**](extensions/index.md) add capabilities to LimaCharlie. Some collect or process data (Artifact, BinLib, Velociraptor, Zeek), some manage internal platform features (Git Sync, YARA Manager, Sensor Cull), some integrate workflow tools (PagerDuty, Twilio, Cases, Playbook).

[**Cloud CLI**](extensions/cloud-cli/index.md) is one specific extension that runs cloud-provider CLIs (AWS, Azure, GCP, Okta, etc.) as D&R response actions. Use it to take action *in* a cloud service from a LimaCharlie detection — disable an Okta user, isolate an EC2 instance, revoke a GitHub token.

## Enrichment — pull external data into detections

[**API Integrations**](api-integrations/index.md) let D&R rules and lookups query external services for context: VirusTotal, GreyNoise, Hybrid Analysis, IP geolocation, etc. Cheap to set up, useful for adding signal to existing detections.

Cloud CLI vs API Integrations: Cloud CLI runs commands *into* a cloud service (action). API Integrations *read* from an external service (lookup). They complement each other.

## Tutorials

End-to-end recipes combining several pieces:

- [VirusTotal Integration](tutorials/virustotal-integration.md)
- [Human-in-the-Loop Response](tutorials/human-in-the-loop-response.md)
- [Hayabusa BigQuery](tutorials/hayabusa-bigquery.md)
- [Velociraptor BigQuery](tutorials/velociraptor-bigquery.md)

## Services

- [Replay](services/replay.md) — replay historical events through D&R rules for testing
