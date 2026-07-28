# Cloud Security

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

LimaCharlie Cloud Security is an agentless cloud-native application protection
platform (CNAPP). It uses the same tenant, permission model, and automation
surface as the rest of LimaCharlie. It enumerates your cloud, identity, SaaS,
and AI estate continuously, and it builds a security graph from what it finds.
It then turns the results into one worklist that is ranked by risk. The
worklist connects to the sensors, D&R rules, Cases, and Outputs that you
already use.

!!! tip "In one sentence"
    Connect a cloud account, identity provider, or AI platform with a read-only
    credential. LimaCharlie then shows what you own, what is exposed, who can
    reach what, and which fix breaks the most attack paths. Every finding is
    automatable through the standard LimaCharlie event pipeline.

## What it covers

| Capability | What you get |
|---|---|
| **Inventory (CSPM)** | A system-of-record of your cloud resources that refreshes continuously — compute, storage, networking, identities. Each resource carries its misconfiguration findings. |
| **Attack paths** | Toxic combinations across resources. An internet-exposed workload that has a known-exploited vulnerability and can reach sensitive data is one finding, not three separate ones. |
| **Identity (CIEM)** | Which human or service can access what: public or external access to sensitive resources, privilege-escalation edges, dormant privileged identities. The score for access comes from the *capability* that a grant gives, not from the existence of the grant. |
| **Data security (DSPM)** | Which data stores exist, which are sensitive, and which sensitive stores are exposed. You declare sensitivity by policy, and you can add classification rules that use content. |
| **AI security (AISPM)** | Your OpenAI and Anthropic organizations as part of the estate: members, API keys, projects, and posture. They use the same findings and compliance lenses (`nist-ai-rmf`, `owasp-llm`). |
| **Compliance** | Pass or fail assessment of each framework control over the live estate. Assess the whole estate, or scope the assessment to named assignments. |
| **CAASM** | A merged inventory of third-party assets from EDR, IdP, MDM, and scanner sources, including LimaCharlie's own sensors. It reports coverage gaps and device posture — "seen by the identity provider, no EDR". |
| **Security graph & topology** | An explorable graph of resources, identities, and their relationships (`can_reach`, `exposed_to`, `has_permission_on`, `can_assume`, …). It also gives an aggregated topology view of the estate, a query language, and saved queries. |
| **Runtime fusion** | Resolution in both directions between LimaCharlie sensors and the cloud assets that they run on. Pivot from a cloud finding to the live endpoint and back. |
| **MSSP fleet** | A cross-tenant fleet board that totals risk across every organization that you manage. |

## Supported providers

Thirteen connectors cover five surfaces. All are agentless and read-only:

- **Cloud infrastructure** — Google Cloud (`gcp`, including folders/organizations),
  AWS (`aws`, including multi-account AWS Organizations), Azure (`azure`).
- **Identity** — Okta (`okta`), Microsoft Entra ID (`entra`), Google Workspace
  (`google_workspace`), 1Password (`1password`), Auth0 (`auth0`).
- **SaaS** — Cloudflare (`cloudflare`), GitHub (`github`).
- **AI** — OpenAI (`openai`), Anthropic (`anthropic`).
- **LimaCharlie** — your own LimaCharlie tenancy as a self-inventoried estate
  (`limacharlie`), including the MSSP fleet case.

Grant a scoped read credential. LimaCharlie stores it as a
[secret](../7-administration/config-hive/secrets.md), and the provider record
references it; the credential is never inlined. The cloud then sweeps the
estate on a schedule, on demand, or continuously from a change feed. For the
setup of each provider, see [Connecting Providers](providers.md).

## How it works

1. **Subscribe** the organization to the `ext-cloud-security` extension.
   This subscription is the enable gate and the billing gate for the
   product.
2. **Connect providers**: one `cloudsec_provider` Hive record for each cloud
   account, IdP tenant, or AI org. Before you save, a credential test
   probes every permission that the collector needs and reports which
   ones are missing.
3. **Sweeps build the graph**: each enumeration updates the resource
   system-of-record and the security graph, then derives the findings
   again. A condition that closes also closes its finding automatically.
4. **You work the findings**: one worklist ordered by `lc_risk`. It carries
   dispositions (mitigated, accepted, false positive), owners, tickets,
   chokepoint analysis, and full automation through `cloud_finding.*`
   events.

Everything that the web app shows is also available through the
[REST API](api-reference.md), the [CLI](cli.md), and — for configuration —
plain [Hive records](configuration.md). You can therefore onboard and govern a
fleet of tenants as code.

## In the console

Cloud Security is a top-level workspace in the organization sidebar. Its pages
map onto the capabilities above:

| Page | What it is |
|---|---|
| **Overview** | The risk overview: score, severity distribution, top attack paths, and the main chokepoint. |
| **Risks** | The findings worklist, with lenses (Public exposure & misconfig, Identity, Workload, Vulnerabilities, Data) and triage for each finding. |
| **Attack Paths** | The toxic-combination paths, grouped by shared fix. |
| **Identity & Access** | CIEM — who can reach what, with a single-identity "Identity 360" view. |
| **Data Security** | DSPM — data-store posture and exposure. |
| **Inventory** | The resource system-of-record, plus Third-party assets and Sensor coverage (CAASM) tabs. |
| **Topology** | An aggregated, explorable diagram of the estate. |
| **Compliance** | Framework assessment for each control, and scoped assignments. |
| **Explore** | The interactive Security graph and the Query console. |
| **Policies** | Data classification (crown jewels), coverage, asset coverage, exclusions, and suppression. |
| **Settings** | Provider connections and the Cases integration. |

A separate cross-tenant **Cloud Security Fleet** board totals risk across every
organization that you manage.

## Permissions

!!! info "Permissions"
    - `cloudsec.get` — read access to every Cloud Security view (findings,
      inventory, graph, topology, identity, compliance, CAASM) and the
      read-only policy previews.
    - `cloudsec.set` — finding triage and other writes (dispositions,
      owners/tickets, chokepoint dismissal, CAASM policy/ingest, provider
      credential tests).
    - `cloudsec_provider.get` / `.set` / `.del` — manage the provider
      connection records in the Hive.

    Every route also needs the organization to be subscribed to
    `ext-cloud-security`. An organization that is not subscribed receives
    `403`.

## Documentation

- [Getting Started](getting-started.md) — subscribe, connect a provider, run
  your first sweep.
- [Connecting Providers](providers.md) — the thirteen connectors, their
  credentials, and what each collects.
- [Provider Setup](provider-setup/index.md) — onboarding steps for every
  platform: the exact scopes, how to create the credential, the
  credential-secret formats, and troubleshooting for the first run.
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
