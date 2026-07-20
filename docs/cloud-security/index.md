# Cloud Security

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

LimaCharlie Cloud Security is an agentless cloud-native application protection
platform (CNAPP) built into the same tenant, permission model, and automation
surface as the rest of LimaCharlie. It continuously enumerates your cloud,
identity, SaaS, and AI estate, builds a security graph out of it, and turns what
it finds into a single risk-ranked worklist — connected to the sensors, D&R
rules, Cases, and Outputs you already use.

!!! tip "In one sentence"
    Connect a cloud account, identity provider, or AI platform with a read-only
    credential, and LimaCharlie shows you what you own, what is exposed, who can
    reach what, and exactly which fix breaks the most attack paths — with every
    finding automatable through the standard LimaCharlie event pipeline.

## What it covers

| Capability | What you get |
|---|---|
| **Inventory (CSPM)** | A continuously refreshed system-of-record of your cloud resources — compute, storage, networking, identities — with misconfiguration findings per resource. |
| **Attack paths** | Toxic combinations across resources: an internet-exposed workload with a known-exploited vulnerability that can reach sensitive data is one finding, not three disconnected ones. |
| **Identity (CIEM)** | Who — human or service — can access what: public/external access to sensitive resources, privilege-escalation edges, dormant privileged identities. Access is scored by the *capability* a grant actually confers, not by the mere existence of a grant. |
| **Data security (DSPM)** | Which data stores exist, which are sensitive (you declare it by policy, optionally augmented by content-based classification rules), and which sensitive stores are exposed. |
| **AI security (AISPM)** | Your OpenAI and Anthropic organizations as first-class estate: members, API keys, projects, and posture — with the same findings and compliance lenses (`nist-ai-rmf`, `owasp-llm`). |
| **Compliance** | Per-control pass/fail assessment of frameworks over the live estate, whole-estate or scoped to named assignments. |
| **CAASM** | A merged third-party asset inventory (EDR / IdP / MDM / scanner sources, including LimaCharlie's own sensors) with coverage-gap and device-posture findings — "seen by the identity provider, no EDR". |
| **Security graph & topology** | An explorable graph of resources, identities, and their relationships (`can_reach`, `exposed_to`, `has_permission_on`, `can_assume`, …) plus an aggregated estate topology view, with a query language and saved queries. |
| **Runtime fusion** | Bidirectional resolution between LimaCharlie sensors and the cloud assets they run on — pivot from a cloud finding to the live endpoint and back. |
| **MSSP fleet** | A cross-tenant fleet board that rolls up risk across every organization you manage. |

## Supported providers

Thirteen connectors across five surfaces, all agentless and read-only:

- **Cloud infrastructure** — Google Cloud (`gcp`, including folders/organizations),
  AWS (`aws`, including multi-account AWS Organizations), Azure (`azure`).
- **Identity** — Okta (`okta`), Microsoft Entra ID (`entra`), Google Workspace
  (`google_workspace`), 1Password (`1password`), Auth0 (`auth0`).
- **SaaS** — Cloudflare (`cloudflare`), GitHub (`github`).
- **AI** — OpenAI (`openai`), Anthropic (`anthropic`).
- **LimaCharlie** — your own LimaCharlie tenancy as a self-inventoried estate
  (`limacharlie`), including the MSSP fleet case.

You grant a scoped read credential (stored as a LimaCharlie
[secret](../7-administration/config-hive/secrets.md), referenced — never inlined —
from the provider record), and the platform sweeps the estate on a schedule, on
demand, or continuously from a change feed. See
[Connecting Providers](providers.md) for the per-provider setup.

## How it works

1. **Subscribe** the organization to the `ext-cloud-security` extension —
   this is the product's enable (and billing) gate.
2. **Connect providers**: one `cloudsec_provider` Hive record per cloud
   account / IdP tenant / AI org. A pre-save credential test probes every
   permission the collector needs and reports which are missing.
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

## In the console

Cloud Security is a top-level workspace in the organization sidebar. Its pages
map onto the capabilities above:

| Page | What it is |
|---|---|
| **Overview** | The risk overview: score, severity distribution, top attack paths and the marquee chokepoint. |
| **Risks** | The findings worklist, with lenses (Public exposure & misconfig / Identity / Workload / Vulnerabilities / Data) and per-finding triage. |
| **Attack Paths** | The toxic-combination paths, grouped by shared fix. |
| **Identity & Access** | CIEM — who can reach what, with a single-identity "Identity 360" view. |
| **Data Security** | DSPM — data-store posture and exposure. |
| **Inventory** | The resource system-of-record, plus Third-party assets and Sensor coverage (CAASM) tabs. |
| **Topology** | An aggregated, explorable diagram of the estate. |
| **Compliance** | Per-control framework assessment and scoped assignments. |
| **Explore** | The interactive Security graph and the Query console. |
| **Policies** | Data classification (crown jewels), coverage, asset coverage, exclusions, and suppression. |
| **Settings** | Provider connections and the Cases integration. |

A separate cross-tenant **Cloud Security Fleet** board rolls risk up across every
organization you manage.

## Permissions

!!! info "Permissions"
    - `cloudsec.get` — read access to every Cloud Security view (findings,
      inventory, graph, topology, identity, compliance, CAASM) and the
      read-only policy previews.
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
- [Connecting Providers](providers.md) — the thirteen connectors, their
  credentials, and what each collects.
- [Findings & Triage](findings.md) — the worklist, finding classes,
  dispositions, chokepoints.
- [Security Graph & Queries](graph.md) — attack paths, topology, graph
  queries, CIEM, DSPM, sensor↔asset resolution.
- [Compliance](compliance.md) — frameworks, reports, scoped assignments.
- [CAASM](caasm.md) — third-party asset inventory, coverage gaps, device posture.
- [Configuration Reference](configuration.md) — the `cloudsec_provider`,
  `cloudsec_policy`, and `cloudsec_query` Hive records.
- [Command Line Interface](cli.md) — the `limacharlie cloudsec` command
  group.
- [API Reference](api-reference.md) — the `/cloudsec` REST surface.
- [Automation & IaC](automation.md) — onboarding recipes, CSV exports, fleet
  management, and the findings↔Cases loop.
