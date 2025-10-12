# Billing
Billing in LimaCharlie is done on monthly cycles and per-Organization (multi-tenant). Sensors can be billed on a quota, set within the organization, or billed on a usage basis.

Need simplified billing for many organizations?

Some features, such as centralized billing are available to larger LC users like MSSPs. For more details contact us at [sales@limacharlie.io](http://mailto:sales@limacharlie.io).

Exact pricing is available on the [LimaCharlie website](https://limacharlie.io) or [Web App](https://app.limacharlie.io).

## Services

### Sensors

There are two categories of sensors: sensors billed on Quota set by the user (vSensor basis), and sensors billed on usage basis.

| Sensor Type | Billed on | Cost |
| --- | --- | --- |
| Windows | Quota | $3.00/sensor/month |
| Linux | Quota | $3.00/sensor/month |
| macOS | Quota | $3.00/sensor/month |
| Docker | Quota | $3.00/sensor/month |
| VMWare Carbon Black EDR | Quota | $0.6/sensor/month |
| Chrome OS | Quota | $0.30/sensor/month |
| Syslog | Usage basis | $0.20/GB |
| Amazon AWS CloudTrail Logs | Usage basis | $0.20/GB |
| Google Cloud Platform (GCP) Logs | Usage basis | $0.20/GB |
| 1Password | Usage basis | $0.20/GB |
| Microsoft/Office 365 | Usage basis | $0.20/GB |
| Windows Event Logs | Usage basis | $0.20/GB |
| Microsoft Defender | Usage basis | $0.20/GB |
| Duo | Usage basis | $0.20/GB |
| GitHub | Usage basis | $0.20/GB |
| Slack | Usage basis | $0.20/GB |
| CrowdStrike | Usage basis | $0.20/GB |
| IT Glue | Usage basis | $0.20/GB |
| Other external sources | Usage basis | $0.20/GB |

For more information about vSensors and the examples, visit our [help center page.](https://help.limacharlie.io/en/articles/5931547-how-is-the-cost-of-sensors-add-ons-calculated-in-limacharlie)

The Quota is the number of sensors (agents) concurrently online that should be  supported by the given Organization. The Quota applies to concurrently online sensors, meaning that you may have more sensors registered than your quota.

If sensors attempt to connect to the cloud while the Quota is full, they will simply be turned away for a short period of time. In that case, a special `sensor_over_quota` will also be emitted which you can use in [D&R rules](/v2/docs/detection-and-response) for automation.

To avoid frequent churn, Quota modifications are limited by:

* Up to one quota decrease per day.
* Any number of quota increases per day.

The endpoint service includes [Outputs](/v2/docs/outputs) as well as [D&R rules](/v2/docs/detection-and-response) processed in real-time.

### Insight (Retention)

Insight is also a foundational service of LimaCharlie. It provides a flat 1 year of full retention (full telemetry) for a single price in order to make billing more predictable.

### Usage Based Billing

See [Sleeper Deployment](/docs/sleeper) for more details.

| Connected Time | Events Processed | Events Retained |
| --- | --- | --- |
| $0.10 per 30 days | $0.67 per 100,000 events | $0.17 per 100,000 events |

### Replay (Retroactive Scanning)

[Replay](/v2/docs/replay) allows you to run [D&R rules](/v2/docs/detection-and-response) or [False Positives](/v2/docs/false-positive-rules) against external or historical telemetry. Not to be confused with Searching for specific IoCs which is a free feature of Insight.

Its pricing is based on the number of events (telemetry) scanned.

**Looking for more insight on utilizing replay?**

Pricing is $0.01 per block of 200,000 events. So a query scanning 1,000,000 events will cost $0.05.

The "dry run" mechanism of Replay can also provide you a high watermark of the cost of a query without actually running it.

Replay jobs can also be launched with a maximum number of operation evaluations to consume during the life-cycle of the job. This limit is approximate due to the de-centralized nature of Replay jobs and may vary a bit.

### Artifact Collection

[Artifacts](/v2/docs/artifacts) allows you to ingest artifacts like Syslog, Windows Events Logs as well as more complex file formats like Packet Captures (PCAP), Windows Prefetch files, Portable Executable (PE) etc.

Ingested files can then be downloaded as originals or viewed in parsed formats right from your browser. You can also run [D&R rules](/v2/docs/detection-and-response) against them.

Unlike Insight, the retention period is variable based on a number of days (up to 365) as specified by the user at ingestion time.

All billing for it is done at ingestion time based on the number of days and the size of the file. The billing metric is therefore "byte-days".

For example, a file that is 100 MB and is ingested with a retention period of 10 days would be one-time billed for `100 X 10 MB-days`.

## Add-Ons

LimaCharlie Add-Ons are billed on the vSensor basis. When an add-on is used with a sensor billed on usage (eg., 1Password), the Add-On is free. For more information and the examples, visit our [billing FAQ](/v2/docs/faq-billing).

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

---

### Related articles

* [Billing Options](/docs/billing-options)
* [FAQ - Billing](/docs/faq-billing)
* [Sleeper Deployment](/docs/sleeper)

---

#### What's Next

* [Using Custom Billing Plans](/docs/using-custom-billing-plans)

Table of contents

+ [Services](#services)
+ [Add-Ons](#add-ons)

Tags

* [platform](/docs/en/tags/platform)