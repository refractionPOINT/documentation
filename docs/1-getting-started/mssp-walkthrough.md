# So You Want to Start an MSSP — A LimaCharlie Walkthrough

This is the article we wish someone had handed us on day one of building a managed security service on LimaCharlie. It is opinionated on purpose: LimaCharlie gives you a lot of moving parts, and a new MSSP can spend weeks deciding things that should take an afternoon. The structure below works. You can absolutely deviate — but if you don't have a strong reason to, follow it.

The goal of this walkthrough is to get you from "I have a LimaCharlie account" to "I have a defensible, multi-tenant, infrastructure-as-code MSSP capable of onboarding a new customer in under an hour, with detection coverage, alerting, case management, AI assistance, and a working IaC export." It is a self-serve POC and a feature tour at the same time — read it linearly the first time, then jump back to the sections you need.

What this article assumes:

- You have signed up at [app.limacharlie.io](https://app.limacharlie.io). The first two sensors are free; everything else here can be done either inside the free tier or for a few dollars in pay-as-you-go usage.
- You have a billing domain (the email domain your team uses, e.g. `@yourmssp.com`). LimaCharlie's [Unified Billing](../7-administration/billing/options.md#unified-billing) ties tenants together by that domain, so use real company addresses for your operators, not personal ones.
- You can run shell commands locally and have a place to keep a private Git repository.

What this article is *not*:

- A reference manual. The doc tree under [Sensors](../2-sensors-deployment/index.md), [Detection & Response](../3-detection-response/index.md), [Integrations](../5-integrations/index.md), [Administration](../7-administration/index.md), and [Reference](../8-reference/index.md) is the reference manual. We link out to it everywhere.
- A list of every feature. LimaCharlie has many features that are great for some MSSPs and irrelevant for others (Velociraptor, Atomic Red Team, MFA-driven canaries, behavioral detection, etc.). When this walkthrough doesn't mention a thing, that doesn't mean it's bad — it means it's optional for the first 90 days.

---

## Part 1 — The mental model before you click anything

LimaCharlie hands you a small set of primitives that, once you internalize them, explain every UI screen and every API endpoint. Spend ten minutes here. It will save you days.

### The five primitives

| Primitive | What it is | Where it lives |
| --- | --- | --- |
| **Organization** (a.k.a. **tenant**, or **org**) | A fully isolated unit: its own sensors, rules, data, billing, audit log. One org has one OID (a UUID). | The thing you create when you click "Create Organization". |
| **Sensor / Adapter** | The thing that produces events. Sensors are EDR agents on hosts; adapters are connectors that ingest logs from cloud / SaaS / third-party security tools. Both stream events into the org. | [Sensors](../2-sensors-deployment/index.md), [Adapters](../2-sensors-deployment/adapters/index.md). |
| **D&R Rule** | A `detect:` block + `respond:` block in YAML. If `detect` matches an event, `respond` runs. This is the entire automation engine. | [D&R Rules](../3-detection-response/index.md). |
| **Hive** | The platform's typed key-value store. Each "kind" of configuration lives in its own hive: `dr-general` (your rules), `dr-managed` (rules managed by extensions/Sigma), `secret`, `lookup`, `query`, `yara`, `ai_agent`, etc. Everything you configure ends up as a record in some hive. | [Config Hive](../7-administration/config-hive/index.md). |
| **Output** | A continuous stream of one of the four data types (`event`, `detect`, `audit`, `deployment`) to an external destination — Splunk, S3, BigQuery, Slack, Teams, syslog, etc. | [Outputs](../5-integrations/outputs/index.md). |

The four data structures every event flows through (`event`, `detect`, `audit`, `deployment`) are explained in [Core Concepts](core-concepts.md#limacharlie-data-structures) — read that page once and refer back.

### The opinionated mental model

Every MSSP customer = **exactly one organization**. Don't share orgs across customers, don't try to sub-divide a customer into multiple orgs unless they have hard data-residency or legal-entity reasons. Customer-as-tenant is the architectural unit you will base every other decision on.

Your *staff* don't get permissions per-customer; they get permissions through **Organization Groups** that contain N customer orgs. You'll have a handful of groups by job function (engineers, L1 analysts, L2 analysts, read-only) and you'll add every new customer org to each relevant group at onboarding time. After that, staff onboarding/offboarding is a one-line operation.

Every config that matters is **a YAML file in a Hive**. The Infrastructure extension reads/writes those files; the Git Sync extension keeps them in lockstep with a Git repository. If you treat that Git repo as the source of truth from day one, you'll never have to "figure out" what's deployed where — you read the repo.

That's the model. The rest of this article is filling it in.

---

## Part 2 — Day 0: accounts, regions, and billing

### Pick one region and stick with it for now

When you create an organization, the region (e.g. `usa`, `europe`, `india`) is **permanent**. Pick the region that matches the majority of your customers' data-residency expectations. If you'll have customers in both EU and US, that's fine — you'll just create their orgs in different regions. The CLI and the web app handle multi-region transparently; cross-region operations are normal.

### Create your "control" organization first

Before you create any customer org, create one organization that will be your **internal control plane**. Call it something obvious like `<yourmssp>-control`. This org:

- Is *not* a customer tenant. No customer EDR sensors land here.
- Holds your IaC templates, your demo data, your training material, your `ai_agent` definitions, your shared `lookup` records, your shared YARA rules.
- Is the org you point Git Sync at first, before you replicate to customers.
- Is the place where your staff can experiment without touching customer data.

Creating this org puts you on the free tier (2 sensor quota). That's enough to validate everything in this walkthrough end-to-end — no credit card required until you scale beyond two real EDR sensors or enable a paid extension.

### Decide on Unified Billing now

If your team's emails all share a domain, opt into [Unified Billing](../7-administration/billing/options.md#unified-billing) immediately. With it, every customer org under your billing domain rolls up into one monthly invoice — paid by ACH or one card — and your billing cycle is the same across tenants. Without it, every customer org is its own billing relationship with its own credit card and its own cycle. **Set up Unified Billing before you onboard your first customer.** Migrating later is a support ticket, not a self-serve operation.

### Enable Strict SSO on your domain

Before you invite a single staff member, enable [Strict SSO Enforcement](../7-administration/access/sso.md#strict-sso-enforcement) on `@yourmssp.com`. This forces every authentication from your domain through your IdP (Okta / Entra / Google Workspace / etc.), which means: when an analyst leaves, disabling them in your IdP locks them out of every customer org instantly. This is the single most impactful access-control control you can apply. Do it on day zero, while you only have one user (you), so you can prove the flow works before relying on it.

---

## Part 3 — The control-org bootstrap

In the control org, do the following one-time setup. You'll get value from each of these immediately, and they'll be the foundation for every customer onboarding to come.

### Generate an API key for your CLI

Install the CLI:

```bash
pip install limacharlie
limacharlie login
```

This stores credentials in `~/.limacharlie`. The login wizard walks you through creating an Organization API key with the permissions it needs. Generated keys are scoped to a single org and a specific permission set — not to your user — which is the right default. See [API Keys](../7-administration/access/api-keys.md) for the full pattern.

Confirm it works:

```bash
limacharlie use            # shows orgs you can reach
limacharlie sensor list    # in the control org, will return [] for now
```

### Create your first Hive Secret

You'll be storing secrets (Anthropic API keys, GitHub deploy keys, third-party tokens) in the [Hive `secret`](../7-administration/config-hive/secrets.md) namespace. Even before you need one, prove it works:

```bash
echo "test-value" > /tmp/example.txt
limacharlie hive set secret --key example-secret --data /tmp/example.txt --data-key secret
limacharlie secret list
limacharlie secret delete --key example-secret --confirm
```

Anywhere a config field would normally take a credential, you'll instead use the syntax `hive://secret/<name>`. This means rules, outputs, and adapter configs **never** contain a literal credential — they contain a reference. That's the only way an IaC repo of these configs can be committed to Git without leaking.

### Subscribe to the Infrastructure extension

In the [Marketplace](https://app.limacharlie.io/add-ons) → **Infrastructure** → **Subscribe**. This adds the IaC machinery: fetch / push / dry-run / force, with selective sync for D&R, outputs, lookups, secrets, etc. See [Infrastructure Extension](../5-integrations/extensions/limacharlie/infrastructure.md).

While you're in the marketplace, also subscribe (in the control org) to: **Cases**, **Exfil**, **Lookup Manager**, **Usage Alerts**. These will be standard kit on every customer org; subscribing in the control org first lets you pre-populate templates.

---

## Part 4 — Designing the customer-org template

You will onboard customers many times. Every onboarding should produce a tenant that's already 90% configured. The way to make that happen is to define one **template org configuration**, in YAML, that you push to every new customer org on creation.

The template comprises:

1. **Connectivity primitives**: installation keys (one per environment / role: `key-server`, `key-workstation`, `key-vip`, `key-sleeper`).
2. **Adapter scaffolding**: the cloud/SaaS/identity adapters every customer is likely to want (M365, Okta or Entra, AWS CloudTrail, Google Workspace).
3. **Detection coverage baseline**: a curated set of D&R rules that work everywhere, plus subscriptions to managed rulesets.
4. **Alerting**: Cases extension config, Slack/Teams/PagerDuty webhooks, severity & SLA mapping.
5. **Outputs**: forward `detect` to the customer's SIEM (or yours), forward `audit` to long-term storage.
6. **Cost guardrails**: usage alerts, sensor cull, sleeper defaults.
7. **AI agent definitions**: triage / investigation / responder agent configs with empty per-customer credentials.

We'll build each of these in the next several sections. Keep in mind: at this point you are configuring the *control* org so the configurations exist as records you can later export and replicate. You are not yet onboarding a customer.

---

## Part 5 — What to connect in (telemetry)

Telemetry is the foundation. You can't write detections — let alone offer detection-and-response services — without it. LimaCharlie has two kinds of telemetry sources, both of which produce events flowing into the same `event` stream.

### EDR sensors (endpoints)

The LimaCharlie sensor runs on Windows, macOS, Linux, ChromeOS, and via browser extensions on Chrome and Edge. Feature parity is high across desktop OSes. Install via [Installation Keys](../2-sensors-deployment/installation-keys.md) — one key per role, **with role tags baked in**:

```bash
# server-class hosts: all production servers
limacharlie installation-key create \
  --description "Production servers" --tags "server,prod"

# workstation-class hosts: knowledge-worker machines
limacharlie installation-key create \
  --description "Workstations" --tags "workstation"

# VIP hosts: executives, on-call, devs with prod access
limacharlie installation-key create \
  --description "VIP" --tags "vip"

# pre-deployed sensors held in sleeper mode
limacharlie installation-key create \
  --description "Sleeper / pre-deployed" --tags "lc:sleeper"
```

Tags are sticky — anything installed with that key inherits the tags forever. Your D&R rules and Exfil profiles will key off these tags (e.g. `vip` sensors get more aggressive collection; `server` sensors get FIM on `/etc/`).

### Sleeper-mode pre-deployment — the MSSP cheat code

The `lc:sleeper` tag pattern above is worth its own paragraph. A sleeper sensor costs **$0.10 per 30 days** to keep installed and connected, with no telemetry collection running. Your customer's IT team can roll the agent out to thousands of machines now; whenever you need real telemetry from any subset, you remove the tag (manually or via a D&R rule) and they wake up within 10 minutes. This is the foundation of being able to offer 20-minute IR SLAs. See [Sleeper Mode](../2-sensors-deployment/endpoint-agent/sleeper.md) for the cost math and exact mechanics. Build sleeper-deploy paths into your customer onboarding documentation; do not save it for "advanced users".

### Adapters (logs, cloud, SaaS, third-party EDR)

Anything that's not a LimaCharlie sensor lands via an [Adapter](../2-sensors-deployment/adapters/index.md). The catalogue is large; the ones an MSSP almost always wants on a customer's first day:

| Customer asset | Adapter | Notes |
| --- | --- | --- |
| Microsoft 365 mailboxes | [Microsoft 365](../2-sensors-deployment/adapters/types/microsoft-365.md) | Audit, login, file-share events. |
| Identity provider | [Okta](../2-sensors-deployment/adapters/types/okta.md), [Microsoft Entra ID](../2-sensors-deployment/adapters/types/microsoft-entra-id.md), or [Duo](../2-sensors-deployment/adapters/types/duo.md) | This is where your account-takeover detections live. |
| Cloud control plane | [AWS CloudTrail](../2-sensors-deployment/adapters/types/aws-cloudtrail.md), [Azure Event Hub](../2-sensors-deployment/adapters/types/azure-event-hub.md), [GCP Pub/Sub](../2-sensors-deployment/adapters/types/google-cloud-pubsub.md) | Customers running in a public cloud — connect this on day 1. |
| Google Workspace | [Google Workspace](../2-sensors-deployment/adapters/types/google-workspace.md) | Same role as M365 for non-Microsoft shops. |
| Existing EDR | [CrowdStrike](../2-sensors-deployment/adapters/types/crowdstrike.md), [Defender for Endpoint](../2-sensors-deployment/adapters/types/microsoft-defender.md), [SentinelOne](../2-sensors-deployment/adapters/types/sentinelone.md), [Carbon Black](../2-sensors-deployment/adapters/types/carbon-black.md), [Sophos](../2-sensors-deployment/adapters/types/sophos.md) | Customer already has an EDR? Don't fight it — ingest its events as a parallel data source. |
| Network / firewall | [Syslog](../2-sensors-deployment/adapters/types/syslog.md), [PaloAlto / Fortinet via syslog](../2-sensors-deployment/adapters/types/syslog.md) | Long-tail visibility. |
| Anything weird | [JSON adapter](../2-sensors-deployment/adapters/types/json.md), [File adapter](../2-sensors-deployment/adapters/types/file.md), [Webhook adapter tutorial](../2-sensors-deployment/adapters/tutorials/webhook-adapter.md) | If a system can write JSON to disk or HTTP-POST a payload, you can ingest it. |

**Opinion:** for your first three customers, connect: EDR + identity (Okta/Entra) + M365/Workspace + cloud control plane (if applicable). That's the minimum-viable telemetry surface to credibly run detections. Everything else is gravy and can be added in week 2+.

### Tag-based segmentation, not org-based

A common mistake: separating environments (dev/prod) into different orgs. Don't. Use **sensor tags** (`prod`, `nonprod`, `dmz`, `pci`, `hipaa`) and write D&R rules that key off `tags`. One org = one customer; tags are how you express structure inside that customer.

### Tune what you collect with the Exfil extension

Some events are gold (`NEW_PROCESS`, `DNS_REQUEST`, `NETWORK_CONNECTIONS`, `CODE_IDENTITY`, `WEL` for relevant channels). Some are firehoses (`MODULE_LOAD`, `FILE_PATH` events on a build server). Subscribe to the [Exfil extension](../5-integrations/extensions/limacharlie/exfil.md) and use **Watch Rules** to get fine-grained: collect `MODULE_LOAD` only when the loaded DLL is interesting; collect everything from `vip`-tagged hosts; collect a stripped-down profile from `dev`-tagged hosts.

For sensors with extreme I/O (build servers, SQL hosts), tag them `ir`-eligible and use the [IR Mode pattern](../5-integrations/extensions/limacharlie/exfil.md#ir-mode) — full event collection without running every D&R rule, useful both in incidents and when you need rich data without the rule-engine cost.

---

## Part 6 — Detections: getting useful coverage in 30 minutes

You don't write rules from scratch on day one. You import known-good rulesets, see what fires, then layer your own.

### Step 1: Subscribe to the Sigma ruleset

In the marketplace, subscribe to the `sigma` add-on. This auto-applies a curated subset of [SigmaHQ](https://github.com/SigmaHQ/sigma) rules that the LimaCharlie team keeps up to date. Free, on by default. After enabling, generate a couple of test events from a sensor (run `cmd.exe /c whoami /all` on a Windows box) and watch the **Detections** view light up.

### Step 2: Browse the Community Rules library

In the web app, **Automation → Rules → Add Rule → Community Library**. Thousands of rules from Anvilogic, Sigma, Panther, and Okta. You can search by ATT&CK technique, CVE, or keyword, click "Load Rule", and the AI converter renders it as native LimaCharlie YAML in your editor. Pick five rules that match your customers' threat model (often: `T1059.001` PowerShell encoded commands, `T1003.001` LSASS access, `T1218` LOLBin abuse, `T1486` ransomware-like file ops, `T1136` new-account creation). See [Community Rules](../3-detection-response/managed-rulesets/community-rules.md).

### Step 3: Add the Soteria rulesets if you have customers in those clouds

[Soteria EDR](../3-detection-response/managed-rulesets/soteria/edr.md), [Soteria AWS](../3-detection-response/managed-rulesets/soteria/aws.md), and [Soteria M365](../3-detection-response/managed-rulesets/soteria/m365.md) are LimaCharlie-curated production rulesets. AWS and M365 in particular catch a *lot* of identity-misuse activity that custom rules struggle with. Subscribe selectively per customer — for AWS-heavy customers, Soteria AWS pays for itself in coverage.

### Step 4: Write your first custom rule

Every MSSP needs at least one rule that's theirs. A good first one — generic enough to live in your global ruleset, useful enough to fire in real life — is "executable launched from a Downloads folder". Save this as `dr-general/exec-from-downloads.yaml`:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: matches
      path: event/FILE_PATH
      case sensitive: false
      re: .:\\(users|temp)\\.*\\downloads\\.*\.(exe|scr|dll|js|vbs|cmd|bat|ps1|hta)
respond:
  - action: report
    name: exec-from-downloads
    metadata:
      description: Executable file launched from a user Downloads folder.
      level: medium
      tags:
        - attack.execution
        - mssp.baseline
```

Push it via CLI:

```bash
limacharlie dr set --key exec-from-downloads --input-file exec-from-downloads.yaml
```

Then test it. The cleanest feedback loop is the [Replay service](../5-integrations/services/replay.md):

```bash
# Run the rule against the past 24h of events on this org
limacharlie dr replay \
  --name exec-from-downloads \
  --start "$(date -d '24 hours ago' +%s)" \
  --end "$(date +%s)" \
  --dry-run --trace
```

Read the [D&R Rule Building Guidebook](../3-detection-response/tutorials/dr-rule-building-guidebook.md) once. It covers state, suppression, alternate targets (rules over `audit` events, rules over `detection` events, rules over `artifact` events), and the patterns you'll reach for as you grow.

### Step 5: Layer false-positive rules instead of editing detections

When something noisy fires, the wrong move is to add an exception inside the detection rule. The right move is to write a [false-positive rule](../3-detection-response/false-positives.md) in a separate `fp` hive that suppresses the noise. This keeps detections portable across customers and makes per-customer tuning explicit:

```yaml
# fp/customer-acme-vendor-installer.yaml
event: NEW_PROCESS
op: and
rules:
  - op: is
    path: routing/hostname
    value: ACME-DEPLOY01
  - op: starts with
    path: event/FILE_PATH
    value: C:\Users\ACME-Deploy\Downloads\
```

That rule lives only in customer ACME's tenant; the underlying detection lives globally.

### Step 6: Unit-test the rules you care about

For rules where regression risk is real, write a [unit test](../3-detection-response/unit-tests.md). It's a YAML file with sample events, expected matches, and expected non-matches. Run it in CI before every merge.

### Translating from other platforms

If you're an MSSP coming from Splunk / Sigma / Kusto / Sentinel and have an existing rule library, the [Sigma Converter](../3-detection-response/managed-rulesets/sigma-converter.md) and [uncoder.io](https://uncoder.io/) cover most of what you need. Convert in batch, review, then commit to your IaC repo.

---

## Part 7 — Queries and threat hunting (LCQL)

Detections are the streaming layer; queries are the batch / interactive layer. As an MSSP you need both — a detection fires when a known pattern matches in real time, but a *query* answers the question "did this thing — that we just learned about — happen anywhere in our customer base in the last 30 days?" That's where LimaCharlie's query language, [LCQL](../4-data-queries/lcql-examples.md), earns its keep.

LCQL runs against any of the four streams that Insight retains for a year by default: `event`, `detect`, `audit`, `deployment`. No SIEM required.

### The shape of an LCQL query

LCQL is pipe-separated. Five segments, each narrowing the result:

```text
<time-range> | <sensor-selector> | <event-types> | <filter> | <projection>
```

Concrete:

```text
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "psexec" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

That's: last 24 hours → only Windows sensors → only `NEW_PROCESS` events → command line contains `psexec` → project these three columns. The earlier you narrow, the faster and cheaper the query. The [LCQL Examples](../4-data-queries/lcql-examples.md) page is the best place to read your way into the language — copy a working query, modify the filter and projection, iterate.

### Where you'll run queries

- **Query Console UI** ([Query Console UI](../4-data-queries/query-console-ui.md)). The interactive console in the web app is where analysts run hunts, save them, and right-click any matching event to **Build a D&R Rule** — turning a one-off finding directly into a recurring detection. This is the fastest path from "I noticed something" to "we now detect it everywhere".
- **CLI** for scripting and CI:

    ```bash
    limacharlie search run \
      --query "-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains 'psexec'" \
      --start "$(date -d '24 hours ago' +%s)" \
      --end "$(date +%s)" \
      --stream event --limit 1000
    ```

    Full reference: [Query CLI](../4-data-queries/query-cli.md).
- **REST / SDK** when you're embedding hunts in your own tooling. See [Data & Queries — Programmatic Management](../4-data-queries/index.md#running-queries-programmatically) for Python and Go examples.

### Estimate cost before you run a hunt

Queries are billed per million events evaluated, not per result returned. Before you launch a 30-day hunt across a 200-sensor customer, estimate it:

```bash
limacharlie search estimate \
  --query "-30d | * | NEW_PROCESS | event/FILE_PATH ends with '.bat'" \
  --start "$(date -d '30 days ago' +%s)" \
  --end "$(date +%s)"
```

The console UI shows the estimate live as you type. The cure for an expensive query is almost always tightening the early segments — sensor selector and event type — not the filter.

### Saved queries belong in the IaC repo

LimaCharlie stores saved queries in the `query` Hive. That means they're committable, reviewable, and reproducible — exactly like D&R rules. Maintain a curated set of "MSSP-baseline hunts" in `hives/query.yaml` in your IaC repo and ship them to every customer org through the same Git Sync loop you use for everything else.

A starter set worth maintaining:

| Saved query | Purpose | Typical cadence |
| --- | --- | --- |
| `lolbin-execution-30d` | LOLBin abuse across all sensors | After a new TTP report |
| `external-rdp-90d` | RDP from public IPs | Weekly compliance review |
| `unsigned-binaries-7d` | Unsigned binaries in user-land | Weekly hygiene |
| `dns-to-newly-registered` | DNS to NRDs (against a `lookup`) | Daily |
| `local-account-creation` | New local accounts | Daily |
| `m365-impossible-travel` | Sign-ins from improbable geographies | Daily |
| `okta-mfa-bypass` | MFA-disabled-then-re-enabled patterns | Daily |
| `cloudtrail-iam-changes` | Sensitive IAM changes | Daily |

Manage like any hive record:

```bash
limacharlie search saved-create --name lolbin-execution-30d --input-file lolbin.yaml
limacharlie search saved-list
limacharlie search saved-run --name lolbin-execution-30d \
  --start "$(date -d '30 days ago' +%s)" --end "$(date +%s)"
```

### Hunting workflows that pay off for an MSSP

- **IOC sweeps.** A peer or feed gives you an IP, hash, or domain. Run one query across each customer's last 30 days. Anything that lights up gets escalated to a Cases entry with the IOC attached.
- **Cross-customer prevalence.** "Has this binary been seen anywhere in our fleet?" Loop the CLI over your customer OIDs, or use the [Cases cross-case entity search](../5-integrations/extensions/limacharlie/cases.md#cross-case-entity-search) for IOCs already attached to cases.
- **Detection prototyping.** Hunt first, write rule second. Iterate the filter in the console until the signal-to-noise is clean, then promote to a D&R rule with one click. Replay it across a week of history before deploying — see below.
- **Replay vs. query — know the difference.** [Replay](../5-integrations/services/replay.md) tests a *rule* against historical events to validate matches and noise. [Query](../4-data-queries/index.md) returns *events* that match a filter. You'll use both: query to investigate and prototype, replay to vet a rule before it's enabled.

### Hand queries to AI agents

Saved queries are addressable from D&R-driven AI sessions. The pattern that compounds: an agent's prompt instructs Claude to "run the saved query `m365-impossible-travel` for sensor `<sid>` over the last 24 hours" via the LimaCharlie MCP server. The agent reads the result, decides whether to escalate, and writes a note on the case. Every saved query you commit becomes a tool every AI agent can wield — your hunting library is your agent toolbox.

### Customer-facing dashboards

If a customer asks for a recurring report, two clean paths:

1. **Forward `event` and `detect` streams to BigQuery** ([BigQuery output](../5-integrations/outputs/destinations/bigquery.md)) and build a Looker Studio dashboard. The [BigQuery + Looker Studio tutorial](../4-data-queries/tutorials/bigquery-looker-studio.md) walks the entire setup. This is the right answer once a customer crosses ~50 sensors.
2. **Schedule saved-query runs** that post results into the customer's Slack or write to a flat file. A few lines of CLI in cron. Cheap, doesn't scale to ad-hoc analytics, fine until option 1 pays off.

---

## Part 8 — Alerting and case management

Detections are only half the loop. Your analysts need a queue with SLA timers, audit trails, and somewhere to write their findings. That's the [Cases extension](../5-integrations/extensions/limacharlie/cases.md).

### Subscribe to Cases and configure it once

Subscribe in the marketplace. By default every detection becomes a case (you can switch to `tailored` mode later, where only D&R rules with an explicit `ingest_detection` action create cases — useful as your alert volume grows).

The defaults are sensible but you should review:

| Setting | Default | What MSSPs typically change |
| --- | --- | --- |
| `severity_mapping` | priority 8–10 critical, 5–7 high, 3–4 medium, 0–2 low | Often unchanged. |
| `sla_config.critical.mttr_minutes` | 240 (4h) | Tighten to match your SLA contracts. |
| `auto_grouping_enabled` | `false` | **Turn this on.** Reduces case volume for noisy rules dramatically. |
| `auto_grouping_include_sensor` | `true` | Keep `true` — group only same-host detections. |
| `auto_grouping_include_category` | `false` | Set `true` if you want stricter grouping. |
| `auto_grouping_window_minutes` | 1440 | 60–240 is a more common MSSP value. |
| `retention_days` | 90 | Match your contractual retention. |

Update via CLI:

```bash
limacharlie case config-set --input-file cases-config.yaml
```

### Wire alert delivery

Cases tracks the queue; it does not page humans. Pages happen via D&R rules (or webhook subscriptions) that fanout to where humans are. The patterns:

- **Slack / Teams / Telegram channels for human-readable alerts.** Use [Slack output](../5-integrations/outputs/destinations/slack.md), [MS Teams output](../5-integrations/outputs/destinations/ms-teams.md), or [Telegram output](../5-integrations/outputs/destinations/telegram.md) on the `detect` stream.
- **PagerDuty for paging.** The [PagerDuty extension](../5-integrations/extensions/third-party/pagerduty.md) speaks the right protocol.
- **SMS via Twilio** ([extension](../5-integrations/extensions/third-party/twilio.md)) for the 3am page.
- **Email via SMTP** ([SMTP output](../5-integrations/outputs/destinations/smtp.md)) for daily summaries.

Don't fan everything out everywhere. The pattern that scales: low/medium goes to Slack, high goes to Slack + PagerDuty, critical goes to Slack + PagerDuty + SMS. Customer-specific overrides via tags or per-customer outputs.

### Webhook integration to the customer's own ITSM

Customers will eventually ask "can you push this into our Jira / ServiceNow / Zendesk?" You have two clean paths:

1. **Webhook output on the `detect` stream** — generic, fast to set up, you control the payload via [output allowlisting](../5-integrations/outputs/allowlisting.md).
2. **Cases webhook notifications** — Cases emits structured events (`created`, `status_changed`, `assigned`, `classified`, `note_added`) via the configured webhook adapter. This is what you want when the customer's ticketing system needs the full case lifecycle, not just first-fire alerts. See [Cases → Webhook Notifications](../5-integrations/extensions/limacharlie/cases.md#webhook-notifications).

### Real-time SOC dashboards

Cases offers a [WebSocket endpoint](../5-integrations/extensions/limacharlie/cases.md#real-time-updates-websocket) that streams case events as they happen. If you build a custom analyst console (most large MSSPs eventually do), this is the integration point. For day-1 MSSPs, the Cases UI in `app.limacharlie.io` is enough.

---

## Part 9 — Outputs: getting your data where it needs to go

Telemetry retention in Insight is one year and is included free. You don't *need* a SIEM to use LimaCharlie. But your customer might already have one, or you might want to build long-term archives or a billing-grade audit trail. That's where Outputs come in.

### The four streams

Every output is bound to one of: `event`, `detect`, `audit`, `deployment`. Pick streams deliberately — the cost shape is different. `event` is voluminous (everything telemetry); `detect` is sparse (only when rules fire); `audit` is critical for compliance; `deployment` is sensor-lifecycle.

### Patterns we recommend by default

| Need | Output | Stream |
| --- | --- | --- |
| Customer's existing SIEM | Splunk / Elastic / OpenSearch / Humio / Kafka | `event` + `detect` |
| Cold storage / compliance archive | [Amazon S3](../5-integrations/outputs/destinations/amazon-s3.md), [GCS](../5-integrations/outputs/destinations/google-cloud-storage.md), [Azure Blob](../5-integrations/outputs/destinations/azure-storage-blob.md) | `event` + `audit` |
| Big-data analytics | [BigQuery](../5-integrations/outputs/destinations/bigquery.md) | `event` (filtered) |
| Soar / playbook orchestration | [Tines](../5-integrations/outputs/destinations/tines.md), webhook | `detect` |
| Tamper-evident audit trail | S3 with object-lock, or syslog to an append-only collector | `audit` |

The `audit` stream is the one MSSPs forget about and regret. It's where every administrative action — user added, rule changed, output added, secret rotated — is logged. **Forward `audit` to immutable storage on every customer org.** Reading it back later is non-negotiable when a customer or auditor asks "who changed what".

### Filter outputs at the edge with allowlists

[Output allowlisting](../5-integrations/outputs/allowlisting.md) lets you filter the stream before it leaves the platform, rather than paying to ship everything and filtering on the receiver side. Use it. For a noisy event type (e.g., `MODULE_LOAD`), allowlist to the specific paths you actually need; for `event` to BigQuery, allowlist to the event types your dashboards consume.

---

## Part 10 — Multi-tenant access (your team, your customers)

Now we wire up the access model that you'll live with for the rest of the company's life. The reference page is [Designing Access for Multi-Org Deployments](../7-administration/access/designing-access.md) — it's the concrete how-to. Below is the opinionated short version.

### Three rules, repeated until you're tired of them

1. **One organization per customer.** No exceptions you'll regret.
2. **Staff get access via Organization Groups, by job function.** Never invite a staff member directly to a customer org.
3. **Customers get added directly to their own org only.** Never put a customer's user into a multi-tenant group.

### Create your staff groups

A starting set that scales:

| Group | Members | Permission level | Notes |
| --- | --- | --- | --- |
| `engineers-prod` | Senior detection engineers, platform admins | Administrator-equivalent | Gate to production change-control. |
| `engineers-nonprod` | All detection engineers | Administrator-equivalent | Sandbox / training / non-production tenants only. |
| `analysts-l2` | Senior analysts, IR leads | Administrator-equivalent | |
| `analysts-l1` | Front-line SOC | Operator-equivalent | |
| `read-only` | Leadership, sales, auditors | Viewer-equivalent | |

Create each group once. Add the control org and every customer org to each relevant group. From that point on, onboarding a staff member is `limacharlie group member-add --gid <id> --email <address>` — one line, no per-org work.

### Customer access goes directly on their org

`limacharlie --oid <customer_oid> user invite --email <address>`, then `user permissions set-role --role Viewer` (or Operator). Don't add customer users to any group, ever.

### Use Organization API keys for automation, never user keys

Every CI pipeline, every webhook, every adapter, every IaC script you write should authenticate with an [Organization API key](../7-administration/access/api-keys.md#organization-api-keys) scoped to the *minimum* permissions it needs and *only* on the org it operates against. A user API key has the user's full reach across every org they can see — if the user leaves, the key dies; if the key leaks, you've exposed every customer.

### Automate the new-customer onboarding checklist

The full checklist is in [Designing Access](../7-administration/access/designing-access.md#new-customer-onboarding-checklist). The condensed version, scriptable today:

```bash
# 1. Create the customer org (use the web UI for the first one,
#    then build a script using the limacharlie CLI for repeatability).
NEW_OID=<paste-new-oid>

# 2. Add it to every staff group
for GID in engineers-prod analysts-l2 analysts-l1 read-only; do
  limacharlie group org-add --gid "$GID" --oid "$NEW_OID"
done

# 3. Apply the IaC template (see Part 12)
limacharlie sync push \
  --oid "$NEW_OID" \
  --config /path/to/templates/customer-baseline.yaml \
  --is-force --dry-run   # remove --dry-run when you're confident

# 4. Invite customer contacts directly on the new org
limacharlie --oid "$NEW_OID" user invite --email contact@customer.example
limacharlie --oid "$NEW_OID" user permissions set-role \
  --email contact@customer.example --role Viewer
```

Once that script lives in your team's repo, onboarding a new customer is a 10-minute job, not a 10-hour one.

---

## Part 11 — AI: agentic SOC capabilities

This is the part that will surprise people coming from older platforms. LimaCharlie ships with a managed Claude runtime — [AI Sessions](../9-ai-sessions/index.md) — that lets you run autonomous agents triggered by D&R rules or schedules. You bring your Anthropic API key (Bring-Your-Own-Key); LimaCharlie runs the agents in isolated containers in cloud and bills only for the runtime overhead.

### Two patterns to know

- **D&R-driven sessions** ([guide](../9-ai-sessions/dr-sessions.md)). A detection fires; a D&R rule's `respond:` block has `action: start ai agent`; an isolated Claude session spins up with the prompt and event context you specify, runs to completion, posts findings (typically to a Cases note), and exits. Idempotent and debounced — you control whether duplicate detections create duplicate sessions.
- **User sessions** ([guide](../9-ai-sessions/user-sessions.md)). Your analysts log in and *interactively* drive a Claude session that has full access to your LimaCharlie org via MCP. Used for ad-hoc investigation when an analyst wants AI-assisted reasoning over the org's data.

### Pre-built agent recipes

The [`refractionPOINT/lc-ai`](https://github.com/refractionPOINT/lc-ai) repo ships with two pre-built **AI team** recipes you can deploy as IaC:

- **[Lean SOC](https://github.com/refractionPOINT/lc-ai/tree/main/ai-teams/lean-soc)** — four agents (triage / investigator / responder / reporter). Cheap, simple. Right starting point for an MSSP whose SOC capacity is "me and one other person".
- **[Tiered SOC](https://github.com/refractionPOINT/lc-ai/tree/main/ai-teams/tiered-soc)** — eight agents matching a traditional L1/L2/L3 + malware analyst + threat hunter + SOC manager + shift reporter shape. Right when you have a real analyst team and want AI to amplify each tier.

Both deploy via the `lc-essentials` Claude Code plugin (the easiest path) or directly as `ai_agent` Hive records (the IaC path). Both use only Sonnet/Opus and run on per-session budgets you set, so the worst-case cost per detection is bounded.

### A concrete first-step recipe

If you only deploy *one* AI thing on day 1, deploy **triage**. The flow:

1. Store your Anthropic API key as a Hive Secret: `limacharlie secret set --key anthropic-key ...`
2. Store an org-scoped LimaCharlie API key as a Hive Secret: `lc-api-key`.
3. Install the lean-soc triage `ai_agent` record (from the lc-ai repo).
4. Add the corresponding D&R rule that triggers it on every new detection.
5. Watch as obvious false positives are dismissed and real detections create cases with a pre-investigation summary attached.

Even at low alert volumes, this saves your L1 hours per day, and it scales linearly with detection volume because each session is independent.

### Cost guardrails on AI

Every D&R-driven agent should set:

- `max_budget_usd` — hard cap on Anthropic spend per session. $0.50–$5.00 is the typical range.
- `max_turns` — limits conversation length even if the budget allows more.
- `ttl_seconds` — wall-clock kill switch.
- `permission_mode: bypassPermissions` — for unattended automation, since otherwise tool calls block on a non-existent human approver.
- `idempotent_key` and/or `debounce_key` — so a detection storm doesn't trigger 200 sessions at once.

See the [`profile` reference](../9-ai-sessions/dr-sessions.md#profile-options) for the full list.

---

## Part 12 — Infrastructure as Code: the part that makes you scalable

Up to this point you may have been clicking buttons. That works for experimentation. It does not work for an MSSP. The moment you have your second customer, every config you care about needs to be in a Git repo, and that repo needs to be the source of truth.

### The two extensions you need

- **[Infrastructure extension](../5-integrations/extensions/limacharlie/infrastructure.md)** — `fetch`, `push`, `dry-run`, selective sync flags (`sync_dr`, `sync_outputs`, `sync_resources`, `sync_artifacts`, etc.). The thing the CLI talks to.
- **[Git Sync extension](../5-integrations/extensions/limacharlie/git-sync.md)** — connects an organization to a Git repo (over SSH with a deploy key), and can both push exports of the live config to Git and pull configs from Git on a schedule.

You will use both. Infrastructure for ad-hoc CLI work and PR-time validation. Git Sync for the ongoing "the world is whatever's in the repo" loop.

### Recommended repo layout

The pattern that holds up across many customers:

```text
mssp-iac/
├── README.md
├── hives/                     # Shared global rules / lookups / agents
│   ├── dr-general.yaml
│   ├── dr-managed.yaml
│   ├── lookup.yaml
│   ├── yara.yaml
│   └── ai_agent.yaml
├── outputs/
│   └── default-outputs.yaml   # SIEM / S3 / audit forwards
├── orgs/
│   ├── <oid-customer-acme>/
│   │   ├── index.yaml
│   │   ├── installation_keys.yaml
│   │   ├── extensions.yaml
│   │   ├── outputs.yaml
│   │   ├── hives/
│   │   │   ├── dr-general.yaml   # ACME-only rules
│   │   │   ├── fp.yaml           # ACME false-positive overrides
│   │   │   ├── secret.yaml       # ACME secrets (placeholders only)
│   │   │   └── extension_config.yaml
│   │   └── resources.yaml
│   └── <oid-customer-globex>/
│       └── index.yaml          # Pure inheritance from globals
└── templates/
    └── customer-baseline.yaml  # Used by onboarding script
```

The customer's `index.yaml` decides what global pieces apply to that customer:

```yaml
version: 3
include:
  - ../../hives/dr-general.yaml
  - ../../hives/lookup.yaml
  - ../../outputs/default-outputs.yaml
  # Customer-specific overrides:
  - hives/fp.yaml
  - hives/dr-general.yaml
  - outputs.yaml
  - extensions.yaml
  - installation_keys.yaml
```

This is exactly the pattern the [Git Sync docs](../5-integrations/extensions/limacharlie/git-sync.md#sharing-configurations-across-multiple-orgs) describe and the [`refractionPOINT/mssp-demo`](https://github.com/refractionPOINT/mssp-demo) reference repo demonstrates end-to-end.

### Secrets do not live in the repo

Every secret in your YAML is a `hive://secret/<name>` reference, not a value. The actual secrets live in the `secret` hive in each org and are managed out-of-band (manually on customer onboarding, or via a separate, more locked-down provisioning script). That way the IaC repo is safe to commit, share with engineers, and back up to S3.

### How to bootstrap the repo from where you are now

You've been clicking buttons in the control org. To turn that into the repo:

```bash
mkdir mssp-iac && cd mssp-iac
git init
mkdir -p orgs hives outputs templates

# Export everything from the control org
limacharlie sync fetch \
  --oid <control-oid> \
  --output orgs/<control-oid>/index.yaml

# Or use the Git Sync extension's "Push to Git" button
# in the control org's web UI.

git add . && git commit -m "Initial export from control org"
```

From there, refactor the export: pull rules that are reusable into `hives/dr-general.yaml`, write a slim `index.yaml` for the control org that includes them, and you have your first reusable global rule set. Every new customer org's `index.yaml` then includes the same files plus its own overrides.

### Validate before you push

```bash
# Always dry-run first; --is-force makes the org an exact mirror of the YAML
limacharlie sync push \
  --oid <customer-oid> \
  --config orgs/<customer-oid>/index.yaml \
  --is-force --is-dry-run
```

Read the diff. Then drop `--is-dry-run`. In CI, run dry-run on every PR; gate merges on a clean diff.

### Schedule recurring sync

Once the repo is the source of truth, configure Git Sync in each customer org to:

- **Pull from Git on a schedule** (every 15 minutes is a fine default), so a merge to `main` deploys without anyone running a CLI.
- Optionally, **push exports back to Git on a schedule**, into `exports/` subdirectory, so any drift caused by an emergency UI change is committed and reviewable.

That's the whole IaC loop. The Git repo is the source of truth, your IdP gates who can merge to `main`, every change is reviewed, every deploy is replayable.

---

## Part 13 — Cost guardrails and operational hygiene

Pay-as-you-go is great until a misconfigured adapter costs you $5,000 in a weekend. Set the guardrails on day 1, in the template, so every customer gets them automatically.

### Subscribe Usage Alerts on every customer org

[Usage Alerts](../5-integrations/extensions/limacharlie/usage-alerts.md) is the platform's bill-runaway protection. It creates managed D&R rules that fire detections (so they hit your existing alert pipeline) when a SKU exceeds a threshold over a window. Useful presets:

- Outbound output data > 1 GB / 30 days → fire detection.
- Sensor count > N (your contracted size) → fire detection.
- Insight retention > X events / 30 days → fire detection.

Manage these in the IaC repo through the `extension_config` hive — that way every customer org gets the same baseline, and customer-specific overrides live next to them.

### Sensor Cull keeps fleets clean

The [Sensor Cull extension](../5-integrations/extensions/limacharlie/sensor-cull.md) automatically removes sensors that haven't checked in for N days. Without it, decommissioned hosts pile up and you keep paying their connectivity fee. Default it to 30 days, deploy on every customer.

### Audit trail review on a cadence

Once a quarter, sweep the audit log of every customer org and the activity log of every staff group: who added users, who changed permissions, who modified rules, who rotated secrets. The CLI commands are in [Verifying and Reviewing Access](../7-administration/access/user-access.md#verifying-and-reviewing-access). Wrap them in a script that posts a summary to a Slack channel; review it the same week each quarter.

### Sleeper everything you're not actively using

If a customer's onboarding has stalled, tag their installed sensors `lc:sleeper`. They cost $0.10 per 30 days each instead of full price. Wake them up the moment the customer's IT readiness is fixed.

### Replay before you trust a new rule in production

The [Replay service](../5-integrations/services/replay.md) lets you rerun a rule against the past N days of telemetry from an org. Always replay a new rule against at least 7 days of customer data before declaring it production-ready. Replay is cheap; tuning a noisy rule in production is expensive.

---

## Part 14 — Onboarding playbook (the one-page version)

Print this. Put it in your runbook.

```text
NEW CUSTOMER ONBOARDING — TARGET: <60 MINUTES

Pre-work (you, before kickoff):
  [ ] Confirm region (US/EU/etc.) with customer
  [ ] Confirm telemetry sources they want connected
  [ ] Confirm contact emails for direct access
  [ ] Confirm SIEM/storage destinations (if any)

The org:
  [ ] Create customer org in target region
  [ ] Add to staff groups (engineers-prod, analysts-l1, analysts-l2, read-only)
  [ ] Apply IaC baseline (limacharlie sync push --is-force)
  [ ] Subscribe extensions: cases, exfil, lookup-manager, usage-alerts, sensor-cull
  [ ] Configure Git Sync against customer's repo subdirectory
  [ ] Enable strict SSO if customer is on a known IdP

Telemetry:
  [ ] Create installation keys (server / workstation / vip / sleeper)
  [ ] Hand customer the install commands and key strings
  [ ] Set up M365/Workspace adapter (if applicable)
  [ ] Set up identity adapter — Okta / Entra / Duo (if applicable)
  [ ] Set up cloud control plane adapter — CloudTrail/Event Hub/Pub-Sub (if applicable)
  [ ] Verify first events arrive on each connected source

Detection:
  [ ] Subscribe sigma ruleset
  [ ] Subscribe Soteria EDR ruleset (and AWS/M365 if applicable)
  [ ] Confirm baseline custom rules apply via IaC
  [ ] Run replay of all baseline rules over the last 24h, review noise

Alerting:
  [ ] Cases enabled, severity & SLA mapped per contract
  [ ] Slack/Teams channel webhook configured
  [ ] PagerDuty (if SLA tier requires paging)
  [ ] Audit stream forwarded to immutable storage

AI (optional but recommended):
  [ ] Anthropic key + LC API key stored in secret hive
  [ ] Triage agent deployed (lean-soc/triage)
  [ ] Optional: investigator + responder + reporter

Hand-off:
  [ ] Direct access invites to customer contacts
  [ ] Walkthrough call with customer (sensor view, detections, cases)
  [ ] Internal sign-off — engineers-prod, analysts-l2 reviewed posture
```

If your team can't run this list in under an hour by month two, you're missing automation. Invest there.

---

## Part 15 — A maturity ladder for the first year

A pragmatic path, not a marketing taxonomy.

**Month 1 — Visibility.** EDR + identity + M365/Workspace ingested for one or two friendly customers. Sigma + Soteria EDR running. Cases on. Slack alerts. IaC repo exists, single org committed.

**Month 2 — Repeatability.** Onboarding script. Customer-org template. Git Sync configured both directions on every org. Staff groups in place. Strict SSO enforced. Audit forwarded.

**Month 3 — Automation.** Triage agent live on every customer. Lean-SOC investigator on the highest-tier customers. False-positive rules per customer. Output allowlists deployed. Usage alerts deployed.

**Months 4–6 — Differentiation.** Custom detections specific to your customer verticals (industry-specific, e.g. healthcare-MFA-bypass patterns, fintech transaction-anomaly). Per-customer AI agent specialization. Threat-feed-driven rules from your own intel. Tiered-SOC if your analyst headcount supports it.

**Months 7–12 — Scale and hardening.** Customer-facing dashboards (BigQuery + Looker Studio, or a custom portal driven by Cases WebSockets). Multi-region presence if your customer geography requires it. Dedicated `engineers-prod` group with CI-only writes; humans only break-glass. Quarterly access reviews automated. Sleeper-mode IR offering productized.

You'll deviate. That's fine. The point is to have a direction.

---

## Part 16 — Suggested next steps

What to read next, in priority order, when you finish this article:

1. **[Designing Access](../7-administration/access/designing-access.md)** — the operational details of staff/customer access at scale.
2. **[Cases](../5-integrations/extensions/limacharlie/cases.md)** — the case lifecycle, SLA mechanics, classification, reporting.
3. **[D&R Rule Building Guidebook](../3-detection-response/tutorials/dr-rule-building-guidebook.md)** — patterns and traps when writing rules that will live in production for years.
4. **[LCQL Examples](../4-data-queries/lcql-examples.md)** — a dense reference of working hunts. Skim to learn the language by analogy.
5. **[Git Sync](../5-integrations/extensions/limacharlie/git-sync.md)** + **[Infrastructure](../5-integrations/extensions/limacharlie/infrastructure.md)** — the IaC details glossed over here.
6. **[AI Sessions: D&R-Driven](../9-ai-sessions/dr-sessions.md)** — once you have alert volume worth triaging.
7. **[lc-ai repo](https://github.com/refractionPOINT/lc-ai)** — pre-built AI agents and the lc-essentials Claude Code plugin.
8. **[mssp-demo repo](https://github.com/refractionPOINT/mssp-demo)** — a reference IaC repo configured exactly the way this walkthrough describes.

What to do next, in priority order, in your control org:

1. Bootstrap a Git repo from your control org with `limacharlie sync fetch`.
2. Onboard a real friendly customer end-to-end with the playbook above. Time it. Improve the slow steps.
3. Wire `audit` stream forwarding on every org. Stop waiting until you need it.
4. Deploy the lean-soc triage agent. Get one full week of automated triage data before deciding whether to deploy the rest of the team.
5. Run the access-review checklist from [Verifying and Reviewing Access](../7-administration/access/user-access.md#verifying-and-reviewing-access) once. Then schedule it.

Welcome to running an MSSP on a public-cloud security platform. The leverage is real — most of what historically took an MSSP weeks now takes hours — but the leverage cuts both ways. Set the guardrails, codify the configs, automate the onboarding, and the platform pays you back every month.

---

## See also

- [Security Service Providers (MSSP, MSP, MDR)](use-cases/mssp-msp-mdr.md) — the higher-level platform-fit overview for service providers.
- [What is LimaCharlie?](what-is-limacharlie.md) and [Core Concepts](core-concepts.md) — fundamentals.
- [Quickstart](quickstart.md) — single-tenant, get-something-running version.
- [Sleeper Mode](../2-sensors-deployment/endpoint-agent/sleeper.md) — the IR-SLA superpower.
- [Sensor Selectors](../8-reference/sensor-selector-expressions.md) — for tag-based segmentation as you grow.
- [LCQL Examples](../4-data-queries/lcql-examples.md), [Query Console UI](../4-data-queries/query-console-ui.md), [Query CLI](../4-data-queries/query-cli.md) — querying and threat hunting.
- [Permissions reference](../8-reference/permissions.md) — when you outgrow the predefined roles.
