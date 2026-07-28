# Estimating Data Ingestion

This guide helps you estimate how much data your organization ingests into LimaCharlie. Use the estimate to plan your costs before you deploy.

## How LimaCharlie Bills for Data

LimaCharlie has two billing models. The model depends on the data source:

LimaCharlie bills **EDR endpoints** (Windows, macOS, Linux, Chrome) at a flat rate, **per endpoint per month**. The price includes all the telemetry from the sensor and 1 year of full telemetry retention. You do not need to estimate the data volume for EDR endpoints. The price for each endpoint includes all the telemetry that the endpoint generates.

LimaCharlie bills **external telemetry** (data ingested through [Adapters](../../2-sensors-deployment/adapters/index.md)) **per GB ingested**. This model covers third-party log sources: cloud providers, identity platforms, SaaS applications, network devices, and other security tools. These sources also include 1 year of telemetry retention.

For current pricing details, see [limacharlie.io/pricing](https://limacharlie.io/pricing).

## Company Size Definitions

The estimates in this guide use the size brackets below. Each bracket has a number of employees and the typical infrastructure for that number:

| Size | Employees | Typical Endpoints | Typical Servers |
|------|-----------|-------------------|-----------------|
| Small | 50–200 | 50–200 | 5–20 |
| Medium | 200–1,000 | 200–1,000 | 20–100 |
| Large | 1,000–5,000 | 1,000–5,000 | 100–500 |

> [!NOTE]
> These values are guidelines. Your actual numbers depend on your industry, the maturity of your infrastructure, and the data sources that you ingest. Use these estimates as a starting point, then adjust them for your environment.

## External Telemetry Sources

The tables below give estimates of the **daily ingestion volumes** for common categories of external data sources. All values are in GB/day.

### Cloud Infrastructure Logs

Logs from cloud providers (AWS CloudTrail, Azure Monitor, GCP Audit Logs). These logs cover API calls, resource changes, and access events.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| AWS CloudTrail | 0.5–2 GB | 2–10 GB | 10–50 GB | Scales with the number of AWS accounts and the volume of API calls |
| AWS GuardDuty | 0.1–0.5 GB | 0.5–2 GB | 2–8 GB | The volume of findings depends on the threat activity |
| Azure Monitor / Activity Logs | 0.5–2 GB | 2–8 GB | 8–40 GB | Includes sign-in, audit, and resource logs |
| GCP Audit Logs | 0.5–1 GB | 1–5 GB | 5–25 GB | Admin activity + data access logs |

**Typical total — Cloud:** 1–5 GB/day (small), 5–25 GB/day (medium), 25–120 GB/day (large)

### Identity & Access Management

Logs from identity providers. These logs track authentications, MFA events, directory changes, and access policies.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| Okta System Log | 0.1–0.5 GB | 0.5–2 GB | 2–8 GB | ~50–200 events per user per day |
| Microsoft Entra ID | 0.1–0.5 GB | 0.5–3 GB | 3–10 GB | Sign-in + audit + provisioning logs |
| Duo | 0.05–0.2 GB | 0.2–1 GB | 1–3 GB | MFA authentication events |
| 1Password | < 0.1 GB | 0.1–0.3 GB | 0.3–1 GB | Vault access and item usage events |

**Typical total — Identity:** 0.2–1 GB/day (small), 1–5 GB/day (medium), 5–20 GB/day (large)

### Email & Collaboration

Audit logs from email and collaboration platforms. These logs cover user activity, admin actions, and compliance events.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| Microsoft 365 Audit | 0.2–1 GB | 1–5 GB | 5–20 GB | 50–200 audit records for each active user each day. SharePoint and Teams users generate more |
| Google Workspace | 0.1–0.5 GB | 0.5–3 GB | 3–12 GB | Admin, Drive, Login, and Token activity |
| Slack Audit Log | < 0.1 GB | 0.1–0.5 GB | 0.5–2 GB | Enterprise Grid only. Tracks workspace access and admin events |

**Typical total — Collaboration:** 0.3–1.5 GB/day (small), 1.5–8 GB/day (medium), 8–35 GB/day (large)

### Network Security

Logs from firewalls, IDS/IPS, VPN concentrators, and network proxies. These log sources often have the highest volume.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| Firewalls (Palo Alto, Fortinet, etc.) | 1–5 GB | 5–30 GB | 30–150 GB | Connection and traffic logs have a very high volume. Threat-only logs are 10–50x smaller |
| IDS/IPS | 0.5–2 GB | 2–10 GB | 10–50 GB | The volume of alerts depends on the tuning of the rules |
| VPN / ZTNA | 0.1–0.5 GB | 0.5–2 GB | 2–10 GB | Session and authentication events |
| Web Proxy / DNS | 0.5–3 GB | 3–15 GB | 15–80 GB | Logging for each request has a very high volume |

> [!WARNING]
> Network security devices are usually the largest source of log data. Firewall traffic logs alone can be larger than all the other sources together. To control the volume, ingest only threat events and denied connections, not the full connection logs.

**Typical total — Network:** 2–10 GB/day (small), 10–55 GB/day (medium), 55–290 GB/day (large)

### Third-Party Security Tools

Logs from other EDR, endpoint protection, or security detection platforms. You forward these logs into LimaCharlie for central analysis.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| CrowdStrike | 0.5–2 GB | 2–8 GB | 8–40 GB | The event volume scales with the number of endpoints and the detection verbosity |
| Microsoft Defender | 0.5–2 GB | 2–8 GB | 8–30 GB | Alerts, incidents, and raw detection events |
| SentinelOne | 0.5–2 GB | 2–8 GB | 8–30 GB | Deep Visibility data has a high volume |
| Sophos | 0.2–1 GB | 1–4 GB | 4–15 GB | Endpoint and network protection events |

**Typical total — Security Tools:** 1–5 GB/day (small), 5–25 GB/day (medium), 25–100 GB/day (large)

### SaaS & Other Applications

Audit and activity logs from business applications.

| Source | Small | Medium | Large | Notes |
|--------|-------|--------|-------|-------|
| GitHub Audit | < 0.1 GB | 0.1–0.5 GB | 0.5–2 GB | Scales with the number of repos and developers |
| Kubernetes (pods/audit) | 0.5–2 GB | 2–10 GB | 10–50 GB | Very variable. Depends on the cluster size and the logging level |
| Custom Syslog sources | 0.1–1 GB | 1–5 GB | 5–20 GB | Changes by a large amount for each application |

## Putting It All Together

The table below shows the estimated **total daily external ingestion** for a typical set of data sources at each company size. Most organizations do not ingest every source in the tables above.

| Scenario | Small | Medium | Large |
|----------|-------|--------|-------|
| **Minimal** — Identity + Cloud only | 1–5 GB/day | 5–25 GB/day | 25–120 GB/day |
| **Moderate** — Above + Email/Collab + one security tool | 3–12 GB/day | 12–60 GB/day | 60–270 GB/day |
| **Comprehensive** — Above + Network + multiple security tools | 5–25 GB/day | 25–140 GB/day | 140–500+ GB/day |

> [!NOTE]
> These estimates assume normal logging verbosity. Verbose logging or debug logging on a source can increase the volumes by 2–10x. A filter that keeps only security-relevant events reduces the volumes by a large amount.

## Tips for Managing Ingestion Costs

1. **Start with high-value, low-volume sources.** Identity logs and cloud audit trails give good security visibility at low data volumes.
2. **Filter at the source.** Many adapters can filter data to reduce noise. For firewalls, ingest only threat events and denied connections, not all the traffic logs. This filter can reduce the volume by 90% or more.
3. **Use the LimaCharlie [Usage Alerts](../../5-integrations/extensions/limacharlie/usage-alerts.md) extension** to set thresholds. The extension tells you about an unexpected increase before it changes your bill.
4. **Monitor your actual usage** in the Billing & Usage section of the settings of your organization. Compare your usage with these estimates and adjust your ingestion strategy.
5. **Remember that EDR endpoints are flat-rate.** You can ingest the telemetry of a third-party EDR, or deploy the LimaCharlie sensor. The flat rate for each endpoint is often less expensive, and the sensor gives more telemetry.

---

## See Also

- [Adapters Overview](../../2-sensors-deployment/adapters/index.md)
- [Billing Options](options.md)
- [Billing FAQ](../../8-reference/faq/billing.md)
- [Usage Alerts](../../5-integrations/extensions/limacharlie/usage-alerts.md)
- [Pricing](https://limacharlie.io/pricing)
