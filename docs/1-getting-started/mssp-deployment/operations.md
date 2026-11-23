---
description: How an MSSP runs a LimaCharlie deployment day to day across thousands of tenants, changing configuration through Git, closing the Git Sync gaps with the CLI, tuning, watching costs and health, and onboarding and offboarding customers.
---

# Operations

Part of [Recommended Deployment for MSSPs](index.md).

Once a few customers are running, the work moves from building to keeping thousands of tenants the same, except where a customer needs to be different. This page is the short list of what that takes. The [MSSP walkthrough](../mssp-walkthrough.md) has the details for most of it.

## Change everything through Git

The repository is the source of truth. A change is a pull request: CI runs the rules' unit tests and a replay, someone reviews, a merge rolls it out, and Git Sync applies it to every tenant on its next pull. The [IaC tutorial](../mssp-iac-tutorial.md) sets this up, and the [Git Sync reference](../../5-integrations/extensions/limacharlie/git-sync.md) lists every option.

Three habits keep it working:

- **Shared files in `global/`, exceptions in the customer's folder.** If you find yourself copying a file into a customer folder to change one line, that line belongs in a false-positive rule or a tag instead.
- **A pull never deletes.** Removing a record from Git leaves it running in the tenant. Delete it there too; the tutorial's [Delete things](../mssp-iac-tutorial.md#step-11-delete-things) step shows how.
- **Push catches drift.** A scheduled push writes each tenant's live configuration to `exports/`, so a change someone made in the console shows up as a diff.

### What Git Sync does not cover yet

Git Sync carries detection and false-positive rules, lookups, saved queries, YARA, playbooks, AI agents, SOPs, org notes, cloud adapters, Application Control policies and rules, investigation policies and plans, outputs, extension subscriptions and settings, and installation keys. It does not cover every product's configuration yet. Push the rest from the same repository with the CLI in your CI:

| Product | Records | How to push them |
| --- | --- | --- |
| Email Security | `dr-mail`, `mailsec_policy` | `limacharlie sync push --hive-dr-mail --hive-mailsec-policy`. See [Email Security rules as code](../../email-security/custom-rules.md#infrastructure-as-code). |
| Email Security | `mailsec_provider` | A `limacharlie hive set` loop over the files, one per tenant. |
| Cloud Security | `cloudsec_provider`, `cloudsec_policy`, `cloudsec_query`, `cloudsec_code_rule` | A `limacharlie hive set` loop. See [Cloud Security API and IaC](../../8-reference/cloud-security-api-iac.md) and [Multi-tenant policy push](../../cloud-security/automation.md#multi-tenant-policy-push). |
| Host Posture (coming soon) | Default rules | The extension's install flow, run in your onboarding script. |
| Cloud-managed adapters | `external_adapter` | Git Sync can carry them, but leave it off: the record holds the installation key and source credentials in plain text, because these records cannot use `hive://secret/` references. CI fills the credentials in from its own secret store and runs `limacharlie external-adapter set`. See [Cloud-managed adapters](telemetry.md#logs-adapters). |

Keep these files out of the `index.yaml` that Git Sync reads, so the two tools never write the same record. An Organization API key works on one organization only, so CI needs a key per tenant. Credentials stay in each tenant's `secret` hive or in your CI's secret store, never in the repository.

## The tuning loop

Once a week per customer, or after any noisy day:

1. Look at the detections that were closed as false positives. For each one, add a false-positive rule in that customer's folder, or a tag if the exception is about a machine's role.
2. When the same false positive shows up in several customers, fix the shared rule in `global/` instead, with a unit test that proves it.
3. Replay changed rules against the last days of real data before merging. See [Replay](../../5-integrations/services/replay.md).
4. Read what your AI agents closed. An alert they keep closing the same way is a candidate for a false-positive rule or a [playbook](ai.md#turn-repeated-steps-into-playbooks).

The walkthrough's [feedback loop](../mssp-walkthrough.md#feedback-loop-on-detection-quality) covers the same ground.

## Watch costs

- Put [Usage Alerts](../../5-integrations/extensions/limacharlie/usage-alerts.md) in the shared template, on ingestion and output volume. A firewall sending everything, or an output sending to the wrong region, becomes a detection the same day.
- Keep sensors you are not monitoring in [sleeper mode](../../2-sensors-deployment/endpoint-agent/sleeper.md), and let [Sensor Cull](../../5-integrations/extensions/limacharlie/sensor-cull.md) remove the ones that are gone.
- Prefer outputs to GCP destinations in the datacenter's region for the full copy; other destinations bill on egress. See [Output billing](../../5-integrations/outputs/billing.md).
- Review AI spend per tenant in [cost tracking](../../9-ai-sessions/cost-tracking.md), and keep `max_budget_usd` on every agent.
- Use [Unified Billing](../../7-administration/billing/options.md) so every tenant lands on one invoice.

The walkthrough's [cost guardrails part](../mssp-walkthrough.md#part-16-cost-guardrails-and-operational-hygiene) has the template records.

## Watch health

Silence is the failure you do not see. Alert on it:

- **Sensors and devices that stop sending.** A per-device syslog sensor stays online as long as the adapter runs. Use [Alerting on sensors that stop sending data](../../2-sensors-deployment/troubleshooting/non-responding-sensors.md).
- **Cloud adapters that fail.** They report errors as events, and LimaCharlie disables one after a day of continuous failure. A D&R rule on the `deployment` target can alert on both. See [A Cloud Adapter keeps failing or was disabled](../../8-reference/faq/adapter-troubleshooting.md#a-cloud-adapter-keeps-failing-or-was-disabled).
- **Git Sync runs that fail.** See [Alerting on failures](../../5-integrations/extensions/limacharlie/git-sync.md#alerting-on-failures).
- **Outputs that drop.** A failing output is disabled until the next refresh and reports an `output_drop` event. See [Output delivery](../../5-integrations/outputs/delivery.md).

Each of these is a D&R rule you write once in `global/`.

## Look across tenants

A few views work across every tenant you manage:

- `limacharlie cloudsec fleet overview` and the console's Cloud Security fleet view roll risk up across tenants. See [Cloud Security CLI](../../cloud-security/cli.md).
- **Fleet Billing → AI Spend** rolls AI savings up across tenants. See [Fleet / MSSP rollup](../../9-ai-sessions/cost-tracking.md#fleet-mssp-rollup).
- Cases' [cross-case entity search](../../5-integrations/extensions/limacharlie/cases.md#cross-case-entity-search) looks for an indicator across the cases of every tenant you can read.
- Anything else, build on the public API with an API key per tenant. See [Custom portals and dashboards](ai.md#custom-portals-and-dashboards).

## Access

Your staff get access through Organization Groups by job function. Customer users go directly on their own organization, never into a staff group. Review both on a schedule, and remove leavers from the groups, not from each tenant. See [Designing access](../../7-administration/access/designing-access.md) and the walkthrough's [access part](../mssp-walkthrough.md#verify-access-on-a-cadence).

## Onboarding and offboarding

**Onboarding** is a script: create the organization in the customer's region, add it to the staff groups, store the deploy key and subscribe Git Sync, add the customer's folder with the shared includes, run the CLI pushes for the records Git Sync does not carry, and send the installation keys. Then follow the [rollout order](index.md#rollout-order-for-one-customer). See the walkthrough's [onboarding playbook](../mssp-walkthrough.md#part-18-onboarding-playbook-the-one-page-version) and the tutorial's [next customer](../mssp-iac-tutorial.md#step-12-onboard-the-next-customer) step.

**Offboarding** has an order: export what you keep, make sure the archive outputs have delivered, uninstall the agents, then delete the organization. Deleting first leaves the agents installed on the customer's machines. See [Offboarding a customer organization](../../7-administration/org-lifecycle.md#offboarding-a-customer-organization).
