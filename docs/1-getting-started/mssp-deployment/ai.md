---
description: How an MSSP uses AI as a main user of LimaCharlie, to set up tenants, manage thousands of them through Git, investigate and respond, turn repeated work into deterministic playbooks, and build custom portals on the public API.
---

# AI as a Main User

Part of [Recommended Deployment for MSSPs](index.md).

The public API and the `limacharlie` CLI cover the platform, and every CLI command has `--ai-help`, help written for a model. The MCP server exposes a set of tools for agents; for anything it does not cover, the agent uses the CLI or the API. So an AI agent can do what a person on your team can, within the permissions you give it. That makes AI a main user of the platform, not a chat box on the side.

The principle from the [overview](index.md#how-to-think-about-limacharlie) applies here more than anywhere: deterministic automation first, AI on top. Rules, false-positive rules, playbooks and policies do the repeated work without spending tokens. AI does the work that needs judgement, and writes more of the deterministic pieces as it goes.

## What it costs

There is no separate charge for using the API, the CLI or the MCP server. Metered operations, such as searches, playbook runtime and AI session runtime, bill the same whichever interface starts them.

For AI Sessions, LimaCharlie bills the session's runtime per minute. The model's tokens are billed by your own provider, on your own key. See [AI Sessions billing](../../9-ai-sessions/index.md#billing). Any frontier model can drive the CLI; see [Using the CLI with frontier models](../../6-developer-guide/frontier-models.md).

## Setting up tenants with AI

[Set up with an AI assistant](../../ai-setup.md) is a page written for the assistant to follow: paste one line into Claude or Codex and it learns what the customer runs, proposes a plan, connects the sources and checks they work. The short guides for [Claude](../../claude.md) and [Codex](../../codex.md) explain how to give each one access.

For an MSSP, the useful version is the same assistant pointed at your Git repository instead of one organization. Ask it to write ACME's folder from what you know about ACME: installation keys, the adapters for their Microsoft 365 tenant, the false-positive rules for their software, the App Control audit policy, the Deception policy once available. The assistant can build a tenant's whole posture this way, as files you review.

## Managing many tenants: the AI opens pull requests

Let the AI change your configuration the same way your engineers do:

1. The agent works on a branch of the repository that Git Sync reads, using the `limacharlie` CLI to read tenants (detections, false positives, sensor lists) and to replay rules.
2. It opens a pull request: a new rule in `global/`, a false-positive rule in `orgs/<ACME OID>/`, a tag change on an installation key.
3. Your CI runs the unit tests and a replay against sample data. A person reviews and merges.
4. On its next pull, Git Sync applies the change in each tenant that includes the changed file, for the types that tenant's Git Sync settings enable.

The agent never needs write access to production tenants for this. Its pull request is the change, your review is the gate, and Git is the record of who changed what. See [Run changes through pull requests](../mssp-iac-tutorial.md#step-10-run-changes-through-pull-requests).

For working across tenants directly:

- The [CLI](../../6-developer-guide/cli.md) takes the organization ID (`--oid`) on organization-scoped commands, and the [MCP server](../../6-developer-guide/mcp-server.md) exposes many of the same operations as tools. The Claude Code plugin from the public [lc-ai repository](https://github.com/refractionPOINT/lc-ai) adds skills for multi-organization work.
- Give automation an Organization API key per tenant with only the permissions it needs. Agents that operate on an organization need `ai_agent.operate`. See [API keys](../../7-administration/access/api-keys.md) and the walkthrough's [API key recipes](../mssp-walkthrough.md#use-organization-api-keys-for-automation-never-user-keys).

## Investigation and response

LimaCharlie runs AI agents for you as [AI Sessions](../../9-ai-sessions/index.md): managed Claude Code instances in isolated containers, with the `limacharlie` CLI already installed. There are two ways to start one, plus SOC Bots on top.

### Unattended: agents started by D&R rules

A D&R rule with the [`start ai agent`](../../8-reference/response-actions.md#start-ai-agent) action starts a session on any event, detection, case event or schedule. Define the agent once as an `ai_agent` record, synced by Git Sync to the tenants that include it, and point many rules at it. See [D&R-driven sessions](../../9-ai-sessions/dr-sessions.md).

Controls an MSSP should set on every agent:

- **`data:` for event fields.** Pass only the fields the agent needs. The platform labels them as untrusted in the prompt, which helps the model treat attacker-controlled text such as command lines and email subjects as data. It is a label, not a security boundary, so also limit what the agent may do. Keep the `prompt` as fixed instructions.
- **`debounce_key`** so one host or one case gets one session at a time.
- **`max_budget_usd`, `max_turns` and `ttl_seconds`** as hard caps on each session.
- **[Tool permissions](../../9-ai-sessions/tool-permissions.md)**: which tools the agent may use, on top of the API key's LimaCharlie permissions.

A typical chain: Cases opens a case, the case event starts a triage agent, the agent reads the case, searches telemetry, adds its findings as notes and either closes it as a false positive or escalates. The walkthrough's [AI part](../mssp-walkthrough.md#part-14-ai-agentic-soc-capabilities) has a full set of agents to deploy as records.

### Interactive: user sessions and SOC Bots

[User sessions](../../9-ai-sessions/user-sessions.md) are an analyst's own AI terminal, in the web app or the CLI. [SOC Bots](../../9-ai-sessions/soc-bots.md) are named specialists in the web app that keep their own conversations, work in groups under a coordinator, and run routines on a schedule. Their ready-made **Service provider team** covers onboarding, billing, detection across tenants and customer reports. Bots act as the user who runs them, with that user's permissions, and the ready-made bots ask before changing or disrupting anything. SOC Bots are rolling out to accounts gradually.

### What the agents know about each customer

Give agents the context your analysts carry in their heads, as records in each tenant:

| Feature | What it holds |
| --- | --- |
| [SOPs](../../9-ai-sessions/sops.md) | Your procedures, which agents read and follow |
| [Org notes](../../9-ai-sessions/org-notes.md) | Free-form facts about the customer's environment |
| [Memory](../../9-ai-sessions/memory.md) | Key/value memory per agent, kept between sessions |
| [Skills](../../9-ai-sessions/skills.md) | Claude Code skills stored in the organization |

All four are records Git Sync carries (`sop`, `org_notes`, `ai_memory`, `ai_skill`). Shared SOPs go in `global/`; a customer's notes go in their folder.

### Providers and cost

Agents run on Claude with your Anthropic key by default, or on Claude through [AWS Bedrock or Google Vertex AI](../../9-ai-sessions/alternative-providers.md) so the tokens bill to your cloud account. User sessions can also run on OpenAI, Google Gemini or OpenRouter with your own key. See [AI providers](../../9-ai-sessions/providers.md).

[Cost tracking](../../9-ai-sessions/cost-tracking.md) shows AI spend by model and trigger rule per tenant, and the **Fleet Billing → AI Spend** tab rolls savings up across your tenants.

### Investigation Engine (coming soon)

The Investigation Engine runs plan templates on detections and cases, with AI answering focused questions inside the plan and autonomy declared in policy. See [Detection and response](detection-response.md#investigation-engine-coming-soon).

<!-- TODO(link): Investigation Engine -> ../../investigation-engine/index.md -->

## Turn repeated steps into playbooks

The most useful thing to ask an AI is to make itself cheaper. When an agent runs the same steps on every alert of a kind (enrich an IP, check three lookups, look up the user, decide), those steps cost tokens every time and can come out slightly different each time.

Ask the agent to write those steps as a [Python playbook](../../5-integrations/extensions/limacharlie/playbook.md): a `playbook(sdk, data)` function stored as a `playbook` record. When the request passes an API key in `credentials` (a `hive://secret/` reference), `sdk` is a client authenticated with it; without one, `sdk` is `None`. Have the playbook depend only on its inputs and current data, not on anything left over from an earlier run. Then:

- A D&R rule calls it with an `extension request` to `ext-playbook`, so the step runs on every matching event with no AI involved. A playbook can return a detection, so it can raise an alert itself.
- The agent calls the same playbook through the CLI or API, and spends its tokens on what is left.
- The playbook is a record, so it goes through Git, review and tests like any rule, and reaches every tenant that includes it.

A playbook is billed by seconds of execution time, not by tokens, and runs the same code every time. The same goes for D&R rules: ask the agent to write a rule or a false-positive rule for any alert it keeps closing the same way.

## Custom portals and dashboards

Build customer portals and cross-tenant dashboards on the public API, with the [Python or Go SDK](../../6-developer-guide/sdk-overview.md) and an API key per tenant. An AI agent can write one for you from a description: your brand, your service tiers, the numbers each customer sees.

[Apps](../../apps/index.md) are different. An app is a small tool inside the LimaCharlie console, stored in one organization and shown to console users of that organization. Use apps for per-tenant analyst views, not as a multi-tenant portal or a customer-facing site.

For a tool that runs inside LimaCharlie with its own console UI, build an [extension](../../6-developer-guide/extensions/building-extensions.md).
