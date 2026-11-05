# Cloud Security

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
| **Data security (DSPM)** | Which data stores exist, which are sensitive (you declare it by policy), and which sensitive stores are exposed. |
| **AI security (AISPM)** | Your OpenAI and Anthropic organizations as first-class estate: members, API keys, projects, and posture — with the same findings and compliance lenses (`nist-ai-rmf`, `owasp-llm`). |
| **Compliance** | Per-control pass/fail assessment of frameworks over the live estate, whole-estate or scoped to named assignments. |
| **Entities** | Resolve identifiers into User and Host entities with confidence, relationships and permission-aware activity. Built from your LimaCharlie sensors alone, with no provider required; providers add directory identities, devices and cloud context. [Usage, CLI and MCP tools](entity-pivot.md) and the [API reference](entities-api.md). D&R rules and outputs can use it too: [Pivots in Rules and Outputs](rule-pivots.md). |
| **CAASM** | A merged third-party asset inventory (EDR / IdP / MDM / scanner sources, including LimaCharlie's own sensors) with coverage-gap and device-posture findings — "seen by the identity provider, no EDR". |
| **Security graph & topology** | An explorable graph of resources, identities, and their relationships (`can_reach`, `exposed_to`, `has_permission_on`, `can_assume`, …) plus an aggregated estate topology view, with a query language and saved queries. |
| **Runtime fusion** | Bidirectional resolution between LimaCharlie sensors and the cloud assets they run on — pivot from a cloud finding to the live endpoint and back. |
| **Code security** | Scan connected repositories in the hosted service, run the LimaCharlie scanner inside your own environment, or push existing SARIF and CycloneDX results into the same findings worklist. Static analysis runs LimaCharlie's default rules and your own, all editable. |
| **Your own detections** | Author your own CSPM rules — in the same detection format as the built-in pack — and disable, re-severity, or replace any built-in rule for your organization. |
| **Remediation SLAs** | Declare how long a finding may stay open, per severity, class, account, or owner, and work the worklist by deadline as well as by risk. |
| **MSSP fleet** | A cross-tenant fleet board that rolls up risk across every organization you manage. |

## Supported providers

Fifteen connectors across six surfaces, all agentless and read-only by default:

- **Cloud infrastructure** — Google Cloud (`gcp`, including folders/organizations),
  AWS (`aws`, including multi-account AWS Organizations), Azure (`azure`).
- **Identity** — Okta (`okta`), Microsoft Entra ID (`entra`), Google Workspace
  (`google_workspace`), 1Password (`1password`), Auth0 (`auth0`).
- **SaaS** — Cloudflare (`cloudflare`).
- **Source control** — GitHub (`github`), GitLab.com and self-managed GitLab
  (`gitlab`), Bitbucket Cloud (`bitbucket`). These drive
  [Code Security](code-security/index.md). A GitHub App can optionally be granted
  write access for pull-request checks and AutoFix pull requests.
- **AI** — OpenAI (`openai`), Anthropic (`anthropic`).
- **LimaCharlie** — your own LimaCharlie tenancy as a self-inventoried estate
  (`limacharlie`), including the MSSP fleet case.

You grant a scoped read credential (stored as a LimaCharlie
[secret](../7-administration/config-hive/secrets.md), referenced — never inlined —
from the provider record), and the platform sweeps the estate on a schedule, on
demand, or continuously from a change feed. See
[Connecting Providers](providers.md) for the per-provider setup.

## What we look for

Cloud Security checks configuration, identity and exposure. The table lists the
classes of problem it reports for each surface, and what it does not look at.
Each provider's [setup page](provider-setup/index.md) repeats this list for that
provider. The list is by category, not by rule. It grows as new checks ship.

| Surface | What we look for | Not checked |
|---|---|---|
| **AWS** | **Root and IAM:** root without MFA or with access keys, weak password policy, unused credentials, admin policies attached, missing Access Analyzer, accounts with no guardrail SCP. **Logging and detection:** CloudTrail integrity, encryption and coverage, AWS Config, GuardDuty and Security Hub switched off, missing CIS alarm filters. **Network:** VPC flow logs, default security groups, NACLs, high-risk ports open to the internet, peering, transit gateway and VPN settings. **Compute:** IMDSv1, public or unencrypted EBS volumes, snapshots and AMIs, privileged or root ECS containers, secrets in CodeBuild and Lambda, unauthenticated Lambda URLs, cross-account Lambda layers. **Data:** S3 public access, TLS, MFA delete, ACLs, logging and cross-account access, EFS, KMS rotation and key policy, Secrets Manager rotation, public resource policies on DynamoDB, SQS, SNS, Glue and Backup. **Databases and managed data services:** RDS and Aurora, DocumentDB, Neptune, Redshift, ElastiCache, OpenSearch, MSK and similar services, for encryption, TLS, public access, public snapshots and audit logs. **EKS clusters:** see Kubernetes below. | Workloads and RBAC inside EKS clusters. |
| **Azure** | **Governance:** Defender plans and alert emails off, User Access Administrator, wildcard custom roles, too many subscription owners, orphaned role assignments, no Conditional Access on the management plane. **Logging:** activity log not exported, missing categories and alerts, no Network Watcher. **Storage:** shared-key access, stale keys, open firewall, public access, no private endpoint, no SAS expiry policy, soft delete and versioning off, weak SMB. **Key Vault:** public access, keys and secrets without expiry, no rotation, long-lived certificates. **Databases:** SQL, PostgreSQL, MySQL, Cosmos DB and Redis for auditing, Entra authentication, threat protection, TDE and firewall rules. **VMs:** password SSH, no encryption at host, unmanaged disks. **AKS clusters:** see Kubernetes below. | Workloads and RBAC inside AKS clusters. |
| **Google Cloud** | **IAM:** personal accounts holding access, service account admin and impersonation grants, separation of duties, organization and folder grants, API keys, KMS rotation. **Logging:** audit logs, log sinks, log alerts. **VPC:** default network, flow logs, DNS logging, DNSSEC, VPC Service Controls, SSH and RDP open to the internet. **Compute:** default service account, Shielded VM, OS Login, external IPs, customer-supplied disk keys. **Data:** Cloud SQL flags, TLS and backups, BigQuery and Dataproc customer-managed keys. **GKE clusters and workloads:** see Kubernetes below. | |
| **Kubernetes** | **Cluster level (GKE, EKS, AKS):** public API endpoint, private nodes, local accounts that bypass cloud identity, workload identity, audit logs, Secrets encryption, network policy engine, supported versions. Provider-specific: Azure RBAC, Entra integration and node encryption (AKS); legacy ABAC, static client certificates and node hardening (GKE); cluster-admin access entries (EKS). **Inside the cluster (GKE only):** privileged and host-namespace pods, host path mounts, dangerous capabilities, default service account tokens, secrets in environment variables, risky RBAC, public Services and Ingress without TLS, missing admission control. | In-cluster checks on EKS and AKS. |
| **Microsoft Entra ID and 365** | **Entra ID:** Conditional Access gaps (MFA, legacy authentication, risky sign-ins, managed devices, administrators), Security Defaults, user consent, guests, app registrations and secrets, PIM, Global Administrator count, password and authentication methods, Intune enrollment. **Exchange and Defender for Office 365:** Safe Links, Safe Attachments, anti-phishing, anti-spam and anti-malware coverage, DKIM, SPF and DMARC, audit logging, DLP, forwarding, SMTP and Direct Send. **SharePoint, OneDrive, Teams, Power BI and Fabric:** sharing and external access. | Settings that need a licence you do not have, or a grant you did not give, report NOT_ASSESSED, not pass. |
| **Mail posture (Entra, Google Workspace)** | External auto-forwarding, DMARC missing or monitor-only, transport rules that bypass filtering (Entra), suspicious mailbox delegates. | |
| **GitHub** | **Organization:** owner count, default repository permission, member rights to create repositories and teams. **Branch protection:** required reviews, status checks, signed commits, force pushes, deletion, administrator enforcement. **Repositories:** secret scanning, Dependabot and code scanning off, no SECURITY.md or CODEOWNERS, unpinned Actions. **Apps and Actions:** over-permissive Apps, Actions secrets on public repositories, OIDC trust with a wildcard subject. | |
| **GitLab, Bitbucket** | Repository inventory for [Code Security](code-security/index.md). GitLab also reports whether the group enforces two-factor authentication. | Organization and branch protection checks. |
| **Okta, Google Workspace, 1Password, Auth0** | Generic identity checks, plus identity attack paths. Okta, Google Workspace and Auth0: users without MFA and privileged accounts with no sign-in for 90 days or more. Okta also checks API tokens that are too old, and Google Workspace app-specific passwords that are too old. Auth0 also flags a tenant MFA policy that is off. 1Password: the user and group directory, and vaults when you connect 1Password Connect, feed the identity graph. | Okta sign-on, password and authenticator policies. Google Workspace tenant policies such as 2-step enforcement. Auth0 attack protection and session lifetimes. 1Password MFA state and sign-in activity. |
| **Cloudflare** | Zone TLS and SSL mode, minimum TLS version, DNSSEC, origin addresses exposed by unproxied records, public R2 buckets, API tokens without expiry or too old, members without two-factor authentication. Cloudflare Security Center insights appear as findings. | |
| **OpenAI, Anthropic** | Keys older than 90 days, keys owned by people who left, pending invites (listed as staged seats), audit-log availability. OpenAI also reports keys never used, admin keys never used, and active mTLS certificates past expiry. Anthropic also reports keys that are not limited to a workspace. With an Anthropic Compliance key: SSO not enforced, SCIM off, no IP allowlist, unbounded retention, no domain capture. | Anthropic key usage, so a key that was never used is not flagged. |
| **LimaCharlie** | MFA not required at sign-in, users without MFA, API keys with no IP restriction, keys created by people who left the organization, telemetry outputs over unencrypted transport, enrollment keys that are old and unused, configuration records that fail to apply, stored secrets with no expiry. | |

### Across providers

These checks run on the connected estate as a whole, not on one provider.

- **Attack paths.** An exposed workload with a known-exploited vulnerability that
  can reach sensitive data. Paths that start from a weakly held identity, such as a
  user without MFA, a key whose owner left or an external principal. A privileged
  identity whose device fails a posture check.
- **Public and external access** to sensitive data stores, and the identities that
  can reach them.
- **Privilege escalation** and **dormant or unused privileges**. A privileged
  identity unused for 90 days or more, and grants never exercised in the observed
  window.
- **AI services.** Public inference endpoints, no customer-managed key, an
  over-broad identity, and audit logging off.
- **Data stores.** Public access, non-TLS connections, soft delete or purge
  protection off, audit logging off.
- **Coverage gaps.** Assets seen by one tool and missing another, such as a user
  or device in your identity provider with no EDR sensor, and places where the
  platform could not read a surface. See [CAASM](caasm.md) and
  [Findings & Triage](findings.md).
- **Device posture.** Unencrypted storage, rooted or jailbroken devices and
  screen lock off, when your MDM source reports them.

Data sensitivity is declared by you, in the
[classification policy](configuration.md#classification-crown-jewels). Cloud
Security does not read your data or classify its content, so a store counts as
sensitive only when your policy says so.

## How it works

1. **Enable** the organization for the `ext-cloud-security` extension — the
   subscription is the product's enable (and billing) gate. Subscribe from
   **Extensions → Cloud Security** in the console or with
   `limacharlie extension subscribe --name ext-cloud-security`.
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

Nearly everything the console shows is also available through the
[REST API](api-reference.md), the [CLI](cli.md), and — for configuration —
plain [Hive records](configuration.md), so a fleet of tenants can be
onboarded and governed as code. (A few surfaces are console-only, notably the
printable posture report.)

## In the console

Cloud Security is a top-level workspace in the organization sidebar. Its pages
map onto the capabilities above:

| Page | What it is |
|---|---|
| **Overview** | The risk overview: score, severity distribution, top attack paths and the marquee chokepoint. |
| **Risks** | The findings worklist, with lenses (All risks / Public exposure & misconfig / Identity / Vulnerabilities / Data) and per-finding triage. |
| **Attack Surface** | The toxic-combination paths, grouped by shared fix, on an interactive graph canvas — plus a **Query console** tab for ad-hoc graph queries and saved queries. |
| **Identity & Access** | CIEM — who can reach what, with a per-identity drill-down (**Grants** and **Access map** tabs). |
| **Data Security** | DSPM — data-store posture and exposure. |
| **Code security** | [Code Security](code-security/index.md): repository scan status, the priority fix queue, container images, SBOM downloads, GitHub webhook status, and results from hosted or customer-run scanners. |
| **Inventory** | The estate itself, in four views: **Topology** (the landing view — an aggregated diagram of the estate), **Resources** (the resource system-of-record), **Third-party assets**, and **Sensor coverage** (CAASM). |
| **Compliance** | Per-control framework assessment and scoped assignments. |
| **Report** | A print-optimized posture report over the current estate, also reachable from **Overview → View report**. |
| **Policies** | Data classification (crown jewels), coverage, asset coverage, agent vulnerabilities, code scanning, code rules, exclusions, suppression, VEX, and SLAs. |
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
    - `cloudsec_provider.get.mtd` / `.set.mtd` — read and write the records'
      user metadata (tags, comments, enabled state).

    Every route additionally requires the organization to be subscribed to
    `ext-cloud-security`. API calls from an unsubscribed organization return
    `403`; in the console the Cloud Security pages render an "enable Cloud
    Security" screen instead of the product.

## Documentation

- [Getting Started](getting-started.md) — enable the product, connect a
  provider, run your first sweep.
- [Free Tier and Limits](free-tier.md) — Cloud Security is free forever for
  small environments such as a home lab: what is included, what counts toward
  the limits and what happens at them.
- [Connecting Providers](providers.md) — the fifteen connectors, their
  credentials, and what each collects.
- [Code Security](code-security/index.md) — scan repositories, check pull requests,
  ingest SARIF or CycloneDX, and run the workflow in GitHub Actions.
- [Provider Setup](provider-setup/index.md) — onboarding walkthrough for every
  platform: exact scopes, how to create the credential, credential-secret
  formats, and first-run troubleshooting.
- [Findings & Triage](findings.md) — the worklist, finding classes,
  dispositions, chokepoints.
- [Remediation SLAs](remediation-sla.md) — due dates on findings, the derived
  states, and breach events.
- [Security Graph & Queries](graph.md) — attack paths, topology, graph
  queries, CIEM, DSPM, sensor↔asset resolution.
- [Compliance](compliance.md) — frameworks, reports, scoped assignments.
- [CAASM](caasm.md) — third-party asset inventory, coverage gaps, device posture.
- [Custom Posture Rules](custom-rules.md) — author your own CSPM detections and
  retune the built-in ones.
- [Configuration Reference](configuration.md) — the `cloudsec_provider`,
  `cloudsec_policy`, `cloudsec_query`, and `cloudsec_code_rule` Hive records.
- [Command Line Interface](cli.md) — the `limacharlie cloudsec` command
  group.
- [API Reference](api-reference.md) — the `/cloudsec` REST surface.
- [Automation & IaC](automation.md) — onboarding recipes, CSV exports, fleet
  management, and the findings↔Cases loop.
