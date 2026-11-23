---
description: How an MSSP should build, tune, test and roll out detection and response across many tenants, with managed rulesets, false-positive rules, replay, shared threat intel, Cases as the shared queue, response actions and the Investigation Engine.
---

# Detection and Response

Part of [Recommended Deployment for MSSPs](index.md).

Every product in LimaCharlie ends up as events in the tenant. [Detection and response (D&R) rules](../../3-detection-response/index.md) are the one engine that acts on all of them: EDR, adapters, mail, cloud findings, App Control, vulnerabilities. This page covers how to build that layer once and run it in every tenant.

## Layer the rules

Build detection in three layers, each in its own place in Git:

| Layer | What it is | Where it lives |
| --- | --- | --- |
| Managed rulesets | Rules LimaCharlie or a partner maintains | Extension subscriptions in your shared template |
| Your rules | Northwind's own detections, written once | `dr-general` records in `global/` |
| Customer exceptions | False-positive rules and tags for one customer | `fp` records in that customer's folder |

### Managed rulesets

Subscribe these in the template so every tenant starts with coverage:

- [Sigma](../../3-detection-response/managed-rulesets/sigma-converter.md): LimaCharlie maintains the Sigma backend and a converted rule set.
- Soteria rulesets for [EDR](../../3-detection-response/managed-rulesets/soteria/edr.md), [AWS](../../3-detection-response/managed-rulesets/soteria/aws.md) and [Microsoft 365](../../3-detection-response/managed-rulesets/soteria/m365.md).
- [SOC Prime](../../3-detection-response/managed-rulesets/soc-prime.md), if you have a SOC Prime account.
- The [Community Rules](../../3-detection-response/managed-rulesets/community-rules.md) library for one-off additions.

Managed rulesets are billed per add-on; see the marketplace listing and [pricing](https://limacharlie.io/pricing).

### Your own rules

Write your rules once in `global/` and every tenant that includes the file runs them. The CLI can draft a rule from a description (`limacharlie ai generate-detection`, see [Writing and testing rules](../../3-detection-response/tutorials/writing-testing-rules.md)), and the [D&R rule building guidebook](../../3-detection-response/tutorials/dr-rule-building-guidebook.md) covers the language. The [walkthrough](../mssp-walkthrough.md#step-4-a-detection-pattern-catalogue) has a catalogue of patterns to start from.

Rules on adapter and product events work the same as rules on EDR events. A rule on `EMAIL_VERDICT`, `cloud_finding.created` or an Okta sign-in uses the same operators, the same response actions and the same suppression.

[Stateful rules](../../3-detection-response/stateful-rules.md) and [sensor variables](../../3-detection-response/sensor-variables.md) work per sensor. A mailbox, an adapter and an endpoint are different sensors, so a single rule cannot follow a sequence from one to the other. [What the products do together](synergy.md#what-is-not-supported) lists what to use instead.

### False positives per customer

Do not edit a shared rule to fit one customer. Add a [false-positive rule](../../3-detection-response/false-positives.md) in that customer's folder instead. FP rules filter the detections of every rule in the tenant, so ACME's software deployment tool is silenced for ACME and nobody else. The **Mark False Positive** button on a detection drafts one for you; copy the result into Git.

For exceptions that change behaviour rather than silence an alert, use a tag. A server ACME runs its backups from gets a tag, and your rule checks for it. The tag goes on that customer's installation key or the sensor, and the shared rule stays shared.

## Test before you ship

A change to `global/` reaches every tenant on the next pull, so test it first:

- **Unit tests.** A rule record can carry a `tests` block of events that should and should not match. LimaCharlie runs them when the rule is created or updated and refuses the rule if one fails. Stateful rules cannot carry tests. See [Unit tests](../../3-detection-response/unit-tests.md).
- **Replay.** Run a rule over past events in a tenant, or over a file of sample events in CI, before you merge. Replay is billed per event evaluated. See [Replay](../../5-integrations/services/replay.md) and the walkthrough's [replay commands](../mssp-walkthrough.md#step-7-replay-against-historical-data-before-you-trust-it).
- **Pull requests.** Run the tests and a replay in your repository's CI, and merge only when they pass. The [IaC tutorial](../mssp-iac-tutorial.md#step-10-run-changes-through-pull-requests) sets this up.

## Threat intel, shared across products

Keep indicators in [lookups](../../7-administration/config-hive/lookups.md). The [Lookup Manager](../../5-integrations/extensions/limacharlie/lookup-manager.md) fetches feeds into `lookup` records every 24 hours. Your own block lists are lookups too.

One lookup serves several products:

- EDR and adapter D&R rules match against it with `op: lookup`.
- Email Security tests every link against the lookups named in a `threat_feeds` policy, and `dr-mail` rules can use `op: lookup` on links, attachment hashes and sender domains. See [IOC feeds](../../email-security/ioc-feeds.md).
- Rules on Cloud Security finding events can use it, as they can on any event.

Cloud Security's custom posture rules cannot: their operator allowlist excludes `lookup` (see [Custom rules](../../cloud-security/custom-rules.md)).

The walkthrough's [threat intelligence part](../mssp-walkthrough.md#part-13-threat-intelligence-and-lookups) has the feed and block-list setup.

## Cases: the shared queue

[Cases](../../5-integrations/extensions/limacharlie/cases.md) is the queue your analysts and agents work from. It is in public beta: it can change without notice.

In the default `all` ingestion mode, every detection in the tenant becomes a case, whatever product produced it. In `tailored` mode, only detections a D&R rule forwards with the `ingest_detection` action do. Pick `tailored` when a tenant produces detections you want to keep but not triage. Turn on [auto-grouping](../../5-integrations/extensions/limacharlie/cases.md#auto-grouping) in the template, so a new detection from a sensor joins that sensor's open case instead of opening another.

What feeds the queue:

| Source | How it reaches Cases |
| --- | --- |
| Your rules and managed rulesets | Any `report` action |
| Cloud Security | The Cases toggle installs rules that open a case on high and critical findings, resolve it when the finding closes and reopen it if it comes back |
| Email Security | The opt-in Cases detection pack: one case per message group |
| Application Control | Four managed alert rules, off by default |
| Vulnerability Reporting | A rule you write on `vuln_finding.*` events |
| Host Posture (coming soon) | A shipped rule that reports each finding |
| Deception (coming soon) | A shipped rule pack; each hit opens a critical case on the endpoint that held the decoy |

Cases has severity mapping, SLA targets, assignees, merging, notes, a dashboard and a summary report. Set the severity mapping, SLAs and `retention_days` in your onboarding script. Case events (creation, status changes, assignments, notes) are sent to the tenant's webhook adapter, so a D&R rule can react to a new case: start an AI agent, run a playbook, notify a channel. See [Webhook notifications](../../5-integrations/extensions/limacharlie/cases.md#webhook-notifications).

Two limits to plan around: Cases accepts up to 100 detections per minute per organization (fewer on the free tier), and a case's entities are added by people, agents or the API, not extracted automatically. [Cross-case entity search](../../5-integrations/extensions/limacharlie/cases.md#cross-case-entity-search) finds only what was attached.

### Getting alerts out

Send cases and detections where your team works with [Outputs](../../5-integrations/outputs/index.md): [Slack](../../5-integrations/outputs/destinations/slack.md), [Microsoft Teams](../../5-integrations/outputs/destinations/ms-teams.md), a [webhook](../../5-integrations/outputs/destinations/webhook.md) or [Tines](../../5-integrations/outputs/destinations/tines.md). For ticketing, use a webhook, or an extension such as [HaloPSA](../../5-integrations/extensions/third-party/halopsa.md), [ServiceNow](../../5-integrations/extensions/third-party/servicenow.md) or [PagerDuty](../../5-integrations/extensions/third-party/pagerduty.md). Webhooks can carry a shared secret so the receiver can check the signature; see [Allowlisting and signatures](../../5-integrations/outputs/allowlisting.md).

## Response

The [response actions](../../8-reference/response-actions.md) an MSSP uses most:

| Action | What it does |
| --- | --- |
| `report` | Creates a detection, which Cases and Outputs pick up |
| `isolate network` | Cuts the host off the network except for LimaCharlie |
| `add tag`, with an optional `ttl` | Moves the host into another policy: App Control lockdown, a stricter Exfil profile, a watch list |
| `task` | Runs a sensor command on the host: collect a file, list processes, dump memory |
| `extension request` | Calls any extension: a [playbook](../../5-integrations/extensions/limacharlie/playbook.md), [Reliable Tasking](../../5-integrations/extensions/limacharlie/reliable-tasking.md) for hosts that are offline, Email Security's mail actions |
| `output` | Sends the matched event to one named output |
| `start ai agent` | Starts an AI session with the event as untrusted input |

Response actions act on the sensor the event came from. For an event from a mailbox, a firewall or the Cloud Security adapter, that is not the machine you want to act on. [What the products do together](synergy.md) shows how to reach the right host.

For destructive steps, put a person in the loop. The [Feedback extension](../../5-integrations/extensions/limacharlie/feedback.md) sends an approval request to chat and runs the response only on a yes. See [Human-in-the-loop response](../../5-integrations/tutorials/human-in-the-loop-response.md).

## Investigation Engine (coming soon)

The Investigation Engine is not generally available yet, and most of its documentation is not published.

<!-- TODO(link): Investigation Engine -> ../../investigation-engine/index.md -->

It investigates a detection or a case by following a plan template: it runs the plan's checks, in parallel where it can, stops when a rule in the template decides, and writes the result to the case. The rules your team writes make the decisions. AI answers focused questions inside the plan, and decides alone only where your policy allows it.

What it may do is declared in an [`investigation_policy` record](../../7-administration/config-hive/investigation-policy.md). Each class of action has one of four modes:

| Mode | Behaviour |
| --- | --- |
| `off` | The engine does not propose it |
| `suggest` | The engine records what it would do and does nothing |
| `approve` | The engine asks for approval and acts only on a yes before the deadline |
| `auto` | The engine acts when the policy's limits, confidence, permissions and evidence checks pass; otherwise it holds the action as a suggestion |

Nothing in the engine changes these modes on its own: no history, score or sampling promotes an action. A pause record stops everything. Policies and plan templates are records, so Git Sync rolls them out; see [Investigation policies and plans](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans). An investigation starts without a person only from a D&R rule.

For a new tenant, start with `close.false_positive` on `suggest` and every eradication action on `approve`, read what the engine would have done for two weeks, then move the classes you trust to `auto`.
