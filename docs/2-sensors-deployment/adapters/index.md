# Adapters

Adapters enable log ingestion from external sources into LimaCharlie. They transform various log formats into normalized LimaCharlie events.

## Deployment Options

- [Deployment Guide](deployment.md) - How to deploy adapters
- [Adapters as a Service](as-a-service.md) - Cloud-managed adapter deployment
- [Usage & Configuration](usage.md) - Configuration options and best practices

## Adapter Types

### Cloud Providers

- [AWS CloudTrail](types/aws-cloudtrail.md)
- [AWS GuardDuty](types/aws-guardduty.md)
- [AWS S3](types/s3.md)
- [AWS SQS](types/sqs.md)
- [Azure Event Hub](types/azure-event-hub.md)
- [GCP Pub/Sub](types/google-cloud-pubsub.md)
- [GCP Storage](types/google-cloud-storage.md)

### Azure Services

- [Key Vault](types/azure/key-vault.md)
- [Kubernetes Service](types/azure/kubernetes-service.md)
- [Monitor](types/azure/monitor.md)
- [Network Security Group](types/azure/network-security-group.md)
- [SQL Audit Logs](types/azure/sql-audit-logs.md)

### Identity & Access

- [Okta](types/okta.md)
- [Microsoft Entra ID](types/microsoft-entra-id.md)
- [Duo](types/duo.md)
- [1Password](types/1password.md)
- [Bitwarden](types/bitwarden.md)

### Security Tools

- [Check Point Harmony](types/checkpoint-harmony.md)
- [CrowdStrike](types/crowdstrike.md)
- [Cylance](types/cylance.md)
- [Microsoft Defender](types/microsoft-defender.md)
- [Proofpoint TAP](types/proofpoint-tap.md)
- [SentinelOne](types/sentinelone.md)
- [Sophos](types/sophos.md)
- [Carbon Black](types/carbon-black.md)
- [Sublime Security](types/sublime-security.md)
- [Trend Micro Vision One](types/trend-micro.md)
- [ThreatLocker](types/threatlocker.md)

### IT & Business Platforms

- [Microsoft 365](types/microsoft-365.md)
- [Slack Audit](types/slack-audit-logs.md)
- [Google Workspace](types/google-workspace.md)
- [Gmail](types/gmail.md)
- [Atlassian](types/atlassian.md)
- [HubSpot](types/hubspot.md)
- [Zendesk](types/zendesk.md)
- [ServiceNow](types/servicenow.md)
- [PandaDoc](types/pandadoc.md)
- [Mimecast](types/mimecast.md)
- [Box](types/box.md)

### Infrastructure

- [Kubernetes Pods](types/kubernetes-pods.md)
- [IIS](types/iis.md)
- [Cato](types/cato.md)
- [Tailscale](types/tailscale.md)

### Generic Formats

- [Syslog](types/syslog.md)
- [JSON](types/json.md)
- [File](types/file.md)
- [Stdin](types/stdin.md)
- [Windows Event Log](types/windows-event-log.md)
- [EVTX](types/evtx.md)
- [Mac Unified Logging](types/mac-unified-logging.md)
- [IMAP](types/imap.md)

### Other

- [Canary Tokens](types/canarytokens.md)
- [IT Glue](types/it-glue.md)

## Tutorials

- [Creating a Webhook Adapter](tutorials/webhook-adapter.md)
- [Ingesting Google Cloud Logs](tutorials/google-cloud-logs.md)

---

## See Also

- [Adapter Deployment](deployment.md)
- [Adapters as a Service](as-a-service.md)
- [Outputs](../../5-integrations/outputs/index.md)
