# API Integrations

API Integrations let D&R rules and [lookups](../../7-administration/config-hive/lookups.md) query external services for context. These services include threat intelligence reputation, IP geolocation, ASN lookups, and similar sources of enrichment. Each integration is read-only. It pulls data *from* the external service into LimaCharlie at the time of evaluation.

## When to use an API Integration vs Cloud CLI

- **API Integrations** — *read* from an external service to enrich a detection (this section).
- **[Cloud CLI](../extensions/cloud-cli/index.md)** — *write* actions into a cloud service as a response. For example, disable a user or isolate an instance.

The two work together. API integrations add context to detections. Cloud CLI takes action on them.

## Available Integrations

- [AlphaMountain](alphamountain.md) — domain reputation
- [EchoTrail](echotrail.md) — Windows process baselining
- [GreyNoise](greynoise.md) — internet noise / scanner data
- [Hybrid Analysis](hybrid-analysis.md) — file analysis
- [IP ASN](ip-asn.md) — IP-to-ASN lookups
- [IP Geolocation](ip-geolocation.md) — IP-to-location lookups
- [Pangea](pangea.md) — intel from many sources through Pangea
- [VirusTotal](virustotal.md) — file / URL / domain reputation

## See Also

- [Lookups](../../7-administration/config-hive/lookups.md) — the mechanism that API integrations use
- [Cloud CLI](../extensions/cloud-cli/index.md) — the action side of integrations
