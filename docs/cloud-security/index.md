# Cloud Security

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

LimaCharlie Cloud Security is an agentless cloud-native application protection
platform (CNAPP) built into the same tenant, permission model, and automation
surface as the rest of LimaCharlie. It continuously enumerates your cloud and
identity estate, builds a security graph out of it, and turns what it finds
into a single risk-ranked worklist of findings — connected to the sensors,
D&R rules, Cases, and Outputs you already use.

!!! tip "In one sentence"
    Connect a cloud account or identity provider with a read-only credential,
    and LimaCharlie shows you what you own, what is exposed, who can reach
    what, and exactly which fix breaks the most attack paths — with every
    finding automatable through the standard LimaCharlie event pipeline.

## What it covers

| Capability | What you get |
|---|---|
| **Inventory (CSPM)** | A continuously refreshed system-of-record of your cloud resources — compute, storage, networking, identities — with misconfiguration findings per resource. |
| **Attack paths** | Toxic combinations across resources: an internet-exposed workload with a known-exploited vulnerability that can reach sensitive data is one finding, not three disconnected ones. |
| **Identity (CIEM)** | Who — human or service — can access what: public/external access to sensitive resources, privilege-escalation edges, dormant privileged identities. |
| **Data security (DSPM)** | Which data stores exist, which are sensitive (you declare it by policy, or opt into content-based auto-classification), and which sensitive stores are exposed. |
| **Compliance** | Per-control pass/fail assessment of frameworks (e.g. `cis-gcp`) over the live estate, whole-estate or scoped to named assignments. |
| **CAASM** | A merged third-party asset inventory (EDR / IdP / MDM / scanner sources) with coverage-gap findings — "seen by the identity provider, no EDR". |
| **Security graph** | An explorable graph of resources, identities, and their relationships (`can_reach`, `exposed_to`, `has_permission_on`, `can_assume`, …) with a query language and saved queries. |
| **Runtime fusion** | Bidirectional resolution between LimaCharlie sensors and the cloud assets they run on — pivot from a cloud finding to the live endpoint and back. |

## Supported providers

Cloud infrastructure: **GCP**, **AWS** (including multi-account AWS
Organizations), **Azure**. Identity and SaaS surfaces: **Okta**,
**Google Workspace**, **1Password**, **Cloudflare**.

All collection is agentless and read-only: you grant a scoped read credential
(stored as a LimaCharlie [secret](../7-administration/config-hive/secrets.md), referenced —
never inlined — from the provider record), and the platform sweeps the estate
on a schedule, on demand, or continuously from a change feed.

## How it works

1. **Subscribe** the organization to the `ext-cloud-security` extension —
   this is the product's enable (and billing) gate.
2. **Connect providers**: one `cloudsec_provider` Hive record per cloud
   account / IdP tenant. A pre-save credential test probes every permission
   the collector needs and reports which are missing.
3. **Sweeps build the graph**: each enumeration updates the resource
   system-of-record and the security graph, then re-derives findings.
   Closed conditions close their findings automatically.
4. **You work the findings**: one worklist ordered by `lc_risk`, with
   dispositions (mitigated / accepted / false positive), owners, tickets,
   chokepoint analysis, and full automation through `cloud_finding.*`
   events.

Everything the console shows is also available through the
[REST API](api-reference.md), the [CLI](cli.md), and — for configuration —
plain [Hive records](configuration.md), so a fleet of tenants can be
onboarded and governed as code.

## Permissions

!!! info "Permissions"
    - `cloudsec.get` — read access to every Cloud Security view (findings,
      inventory, graph, compliance, CAASM).
    - `cloudsec.set` — finding triage and other writes (dispositions,
      owners/tickets, chokepoint dismissal, CAASM policy/ingest, provider
      credential tests).
    - `cloudsec_provider.get` / `.set` / `.del` — manage provider
      connection records in the Hive.

    Every route additionally requires the organization to be subscribed to
    `ext-cloud-security`; unsubscribed organizations receive `403`.

## Documentation

- [Getting Started](getting-started.md) — subscribe, connect a provider, run
  your first sweep.
- [Findings & Triage](findings.md) — the worklist, finding classes,
  dispositions, chokepoints.
- [Security Graph & Queries](graph.md) — attack paths, graph queries, CIEM,
  DSPM, sensor↔asset resolution.
- [Compliance](compliance.md) — frameworks, reports, scoped assignments.
- [CAASM](caasm.md) — third-party asset inventory and coverage gaps.
- [Configuration Reference](configuration.md) — the `cloudsec_provider`,
  `cloudsec_policy`, and `cloudsec_query` Hive records.
- [Command Line Interface](cli.md) — the `limacharlie cloudsec` command
  group.
- [API Reference](api-reference.md) — the `/cloudsec` REST surface.
- [Automation & IaC](automation.md) — onboarding recipes, CSV exports, and
  the findings↔Cases loop.
