# SOC Bots

SOC Bots are named AI specialists that work for you in the LimaCharlie web app. Each bot has a name, a responsibility and its own conversation, and keeps them between visits. You can put several bots in a group, where a coordinator takes your request, hands parts of it to the right specialists and gives you one answer.

SOC Bots were previously called LimaCharlie Bots.

## Where to find them

- **The SOC Bots button** in the top bar opens the full workspace at `/sessions/workspace`.
- **The bot in the bottom-right corner** of every page opens the same bots in a small chat window, so you can keep working on the page you are on.

SOC Bots are rolling out to accounts gradually. If your account does not have them yet, the top bar shows the AI Terminal button instead.

Bots act as your own user. They can see and change only what your LimaCharlie permissions allow, in the organizations you have access to. The ready-made bots below ask before anything that changes or disrupts your environment, such as isolating a host or deleting a rule.

Bots run on the AI provider you set up for AI Sessions. See [AI Providers](providers.md) and [Cost Tracking & Savings](cost-tracking.md).

## Ready-made teams

The quickest way to start is a ready-made team. Pick one on the welcome screen, in **Create group** while you have fewer than two bots, or under **Add a ready-made team** in the corner chat. LimaCharlie creates its bots and their group in one step. Each team comes with suggested first tasks that fill the message box for you to edit and send.

If you said whether you are a service provider when you signed up, the matching team is marked **Recommended for you**.

### Service provider team

For MSSPs, MSPs, MDR and incident response firms. It helps you launch and grow a security service: customer onboarding, pricing and billing, detections across tenants, and customer reports.

| Bot | What it does |
|-----|--------------|
| **Practice Lead** (coordinator) | Plans the launch of your security service on LimaCharlie and coordinates the team. |
| **Business Advisor** | Helps you package, price and position your security service. |
| **Billing Specialist** | Explains and forecasts your LimaCharlie costs, per customer and in total. |
| **Tenant Onboarding Engineer** | Creates customer organizations from a reusable template and deploys sensors and log sources. |
| **Multi-Tenant Detection Engineer** | Builds and tunes detection coverage once and rolls it out to every customer. |
| **SOC Analyst** | Triages alerts across customers, investigates, and writes customer-ready reports. |

The [MSSP walkthrough](../1-getting-started/mssp-walkthrough.md) covers the same path step by step.

### In-house security team

For enterprise, mid-market and public-sector security and IT teams. It helps you roll out LimaCharlie, migrate from your current tools side by side, tune detections, and keep costs and compliance in check.

| Bot | What it does |
|-----|--------------|
| **Security Lead** (coordinator) | Plans your rollout of LimaCharlie and coordinates the team. |
| **Migration Specialist** | Plans a safe move from your current EDR, SIEM or log tools, side by side first. |
| **Deployment Engineer** | Rolls out sensors and connects the log, cloud and email sources you need. |
| **Detection & Response Engineer** | Turns on detection coverage, tunes the noise, and automates response. |
| **Threat Hunter** | Investigates alerts and hunts across endpoint, identity, cloud and email data. |
| **Budget & Compliance Advisor** | Estimates costs, plans retention and data forwarding, and maps controls to frameworks. |

### Platform specialists

For anyone exploring LimaCharlie: one expert per product area.

| Bot | What it does |
|-----|--------------|
| **Chief of Staff** (coordinator) | Turns your request into a plan, delegates it to the specialists, and delivers the outcome. |
| **Sensor Fleet Operator** | Operates the sensor fleet, telemetry sources, and safe endpoint actions. |
| **D&R Rulesmith** | Builds, tests, and tunes detection, response, and automation content. |
| **LCQL Hunter** | Hunts across telemetry and turns evidence into investigations. |
| **CloudSec Cartographer** | Maps cloud assets, identities, exposures, vulnerabilities, and attack paths. |
| **MailSec Investigator** | Investigates email threats and operates Email Security. |

Ready-made bots load the LimaCharlie skills they rely on (see [AI Skills](skills.md)). Their pricing advice uses the public prices on [limacharlie.io/pricing](https://limacharlie.io/pricing). For discounts or contract terms, they send you to LimaCharlie sales.

A team is yours once it is created. You can rename its bots, change their instructions, add or remove members, or pick a different coordinator.

## Your own bots and groups

To make a bot of your own, choose **Or create a single bot** on the welcome screen, or **New bot** later. Give it a name and a one-sentence responsibility. **Advanced configuration** sets its model, instructions, allowed tools and usage limits, or copies them from a saved [profile](tool-permissions.md).

To make a group, choose **Create group**, pick two or more bots and choose a coordinator. In a group:

- A message without a mention goes to the coordinator, which may delegate the work.
- Mention a bot by its handle, such as `@threat-hunter`, to send a message straight to it.
- Bots added to a group can read its existing history.

## Routines

A routine runs a task for a bot on a schedule and posts the result in its conversation, for example a weekday morning brief of new detections. Manage them under **Routines** in the workspace.

## Limits

| Limit | Value |
|-------|-------|
| Bots per user | 20 |
| Bots per group | 6 |
| Enabled routines per user | 20 |
| Shortest routine interval | 5 minutes |

A ready-made team needs a free bot slot for each of its six bots. If you do not have enough, the team picker says how many slots it needs.
