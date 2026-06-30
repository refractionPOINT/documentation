# AI Cost Tracking & Savings

LimaCharlie tracks two things about your AI agents: **what they cost**, and **how much analyst work they take off your team's plate**. The second is expressed in dollars you can put in front of a CFO and defend, line by line — measured from your real case resolution mix, not a hypothetical.

This page explains exactly how those numbers are produced — every input, the formula, and the assumptions — so the figure you see is something you understand and can tune, not a black box. For the hard per-session spend cap, see `max_budget_usd` in [D&R-Driven Sessions](dr-sessions.md) and [User Sessions](user-sessions.md).

## Where to find it

| View | Location | Scope |
|------|----------|-------|
| **Cost Analytics** | An organization's AI Agents usage page | AI spend, tokens, and unit economics for one org, broken down by model and trigger rule |
| **AI Resolution & Savings** | Same AI Agents usage page | The savings model: resolution mix, analyst-equivalent value, ROI, per-profile P&L |
| **AI Savings (7d)** | Fleet Billing → AI Spend tab | A cross-tenant (MSSP) rollup of savings across every managed organization |

## The big picture

The model combines three things you already have in LimaCharlie:

- **Your AI spend** — what your AI agents cost to run over a period.
- **Your Cases** — the investigations that were worked, and *who* worked each one.
- **Your cost profiles** — what an hour of analyst time is worth to you, and how long an investigation takes by hand.

From those, it produces a **resolution mix** (how investigations were handled) and a **savings figure** (the analyst work AI displaced, minus what it cost).

```mermaid
graph LR
    A["AI spend over the period"] --> M{{"Cost & Savings model"}}
    B["Cases — who worked each one"] --> M
    C["Cost profiles (ai_cost_model Hive)"] --> M
    M --> R["Resolution mix:<br/>AI-only / AI+Human / Human-only"]
    M --> S["Savings: net savings & ROI"]
```

## The core idea: who did the work

The model does **not** try to guess whether a piece of work was "worth doing." It starts from a simpler, more honest premise:

> Every case is real work that had to be done. The only question is **who did it** — an AI agent, a human analyst, or both.

So every case that was worked in the period falls into one of three buckets:

| Resolution | Meaning |
|---|---|
| **AI-only** | An AI agent worked the case and no person took action on it. |
| **AI + Human** | Both an AI agent and a person took action on the case. |
| **Human-only** | Only people worked the case — AI was not involved. This is the baseline you're trying to shrink. |

How does LimaCharlie know? From the **case timeline**. Every action on a case is recorded there — when an AI agent adds its findings, classifies, or resolves a case, that activity is attributed to the agent; when an analyst does the same, it's attributed to the person. A case is "AI-touched" if an agent acted on it, and "human-touched" if a person acted on it.

```mermaid
graph TD
    Case["A case worked in the period"] --> Q1{"Did an AI agent act on it?"}
    Q1 -->|No| Q2{"Did a person act on it?"}
    Q1 -->|Yes| Q3{"Did a person also act on it?"}
    Q3 -->|No| AIonly["AI-only"]
    Q3 -->|Yes| Both["AI + Human"]
    Q2 -->|Yes| Human["Human-only"]
    Q2 -->|No| Untouched["Not yet worked — excluded"]
```

The **resolution mix** — the share of investigations in each bucket — is the headline metric. It tells you, at a glance, how much of your investigative workload your agents are actually carrying.

## Cost profiles

A **cost profile** is a named category of analyst work that AI stands in for — for example *SOC L1 Triage* or *Incident Responder*. Each profile answers two questions:

- What does an hour of this analyst's time cost you (fully burdened)?
- How long does one investigation of this kind take to handle **by hand**, without AI?

Profiles are stored as records in the **`ai_cost_model` Hive**, one record per profile. Because Hives are per-organization, each organization (and, for an MSSP, each managed tenant) has its own set of profiles.

Each profile has these fields:

| Field | Meaning |
|---|---|
| `label` | Display name, e.g. "SOC L1 Triage". |
| `loaded_hourly_rate` | Fully-burdened analyst cost per hour, in USD (salary + benefits + overhead). |
| `minutes_per_investigation` | Standard analyst minutes to handle one investigation of this work **without** AI. |
| `rate_source_note` | Free-text note recording where the rate came from — shown alongside the savings figure so it's defensible in a finance review. |

You can manage profiles two ways:

- In the **AI Resolution & Savings** panel, use **Manage profiles** to add, edit, or remove them.
- Directly as records in the **`ai_cost_model` Hive** (Infrastructure-as-Code, the API, or the [CLI](cli.md)).

A typical set of profiles for a managed SOC might look like:

| Profile | Loaded rate | Minutes / investigation | Cost to handle one |
|---|---|---|---|
| SOC L1 Triage | $55/hr | 12 | $11.00 |
| SOC L2 Analyst | $85/hr | 45 | $63.75 |
| Incident Responder | $120/hr | 180 | $360.00 |

The **cost to handle** one investigation is simply:

```text
cost to handle = loaded_hourly_rate × (minutes_per_investigation / 60)
```

It's the only modeled number in the whole system; everything else is measured.

!!! note "Configure at least one profile"
    Savings are only computed once an organization has a cost profile. Until then the panel shows a setup prompt rather than fabricated numbers.

## How savings are calculated

Savings answer: *of the work the AI agents did, how much analyst labor did that displace, and what did it cost?*

```mermaid
graph TD
    AH["AI-handled cases<br/>(AI-only + AI+Human)"] --> GD["Analyst-equivalent value =<br/>cases × cost to handle"]
    P["Cost profile(s)"] --> CTH["Cost to handle one =<br/>rate × minutes / 60"]
    CTH --> GD
    L["Logged human time on cases"] --> LC["Human cost = hours × rate"]
    GD --> NET["Net savings =<br/>analyst-equivalent value − human cost − AI spend"]
    LC --> NET
    AI["AI spend"] --> NET
    GD --> ROI["ROI = analyst-equivalent value ÷ AI spend"]
    AI --> ROI
```

Step by step:

1. **Count the AI-handled cases.** That's the AI-only and AI+Human buckets combined — every case an agent touched.
2. **Value each one at its cost to handle.** By default each case is valued at the cost profile matching its severity (see [Per-severity valuation](#per-severity-valuation)); when you select a single profile, the whole AI-handled caseload is valued at that profile. The result is the **analyst-equivalent value** — what it would have cost to do all that work by hand.
    - Note the crediting rule: **any case an AI agent worked is credited the full cost to handle it** — including AI+Human cases. We then subtract the human time that was actually spent (next step), rather than trying to estimate a split.
3. **Subtract the human time that was still spent.** When an analyst logs time against a case (see below), that time is valued at the profile rate and subtracted. If no human time was logged, nothing is subtracted.
4. **Subtract the AI spend.** What the agents cost to run over the period.
5. **The result is net savings.** And **ROI** is the analyst-equivalent value divided by the AI spend.

```text
net savings = analyst-equivalent value − logged human time − AI spend
```

### A worked example

Over the last 30 days, using a single *SOC L1 Triage* profile ($55/hr, 12 min → $11.00 to handle one):

| Quantity | Value |
|---|---|
| AI-only cases | 800 |
| AI+Human cases | 150 |
| Human-only cases | 200 |
| Logged human time (on the AI+Human cases) | 40 hours |
| AI spend | $260 |

- AI-handled cases = 800 + 150 = **950**
- Analyst-equivalent value = 950 × $11.00 = **$10,450**
- Human cost = 40 hrs × $55 = **$2,200**
- Net savings = $10,450 − $2,200 − $260 = **$7,990**
- ROI = $10,450 ÷ $260 ≈ **40×**
- Resolution mix = 70% AI-only, 13% AI+Human, 17% Human-only

Every number traces back to something concrete: the case counts come from your Cases, the human cost from logged time, the AI spend from your agents' usage, and the rate from a profile you set with a documented source.

### Per-severity valuation

A single rate rarely fits every case — triaging an informational alert isn't IR work. When you have **more than one cost profile**, LimaCharlie values each AI-handled case at the profile that matches its **severity** rather than one blanket rate. It tiers your profiles by cost — the cheapest handles the lowest severities, the most expensive handles the highest (e.g. L1 triage for informational cases, an incident responder rate for critical ones). The analyst-equivalent value is then the sum across severities of:

```text
cases at that severity × cost to handle of that severity's profile
```

With a single profile, the whole AI-handled caseload is valued at that one profile (as in the worked example above).

## The metrics you get

For the selected time range, the **AI Resolution & Savings** panel shows:

| Metric | Meaning |
|--------|---------|
| **Net savings** | Analyst-equivalent value minus logged human time and AI spend |
| **ROI** | Analyst-equivalent value divided by AI spend |
| **AI automation rate** | Share of investigations that were AI-handled |
| **Analyst-hours freed** | The manual hours the AI-handled cases represent (rate-independent) |
| **FTE-equivalent** | Those analyst-hours expressed as a fraction of one full-time analyst over the range |
| **Cost / investigation** | AI spend per AI-handled case |

Beneath the headline figure the full arithmetic is shown (analyst-equivalent value − logged human time − AI spend = net savings), so nothing is hidden. You also get:

- The **resolution mix** as a single bar with the counts beside it.
- A **profile selector** if you've defined more than one cost profile, so you can value the same activity against different kinds of analyst work, or scope the view to one — e.g. *"how much did I save on Incident Responder cases?"*
- A **per-profile P&L** table breaking net savings down by cost profile.
- A **cumulative net savings** chart showing how savings accrued over the range. It uses real daily AI spend with the period's analyst value distributed across days by AI activity — accrual, not a per-day measurement.
- The **rate source note** from the selected profile, so anyone reading the figure can see where the rate came from.

If you haven't created a profile yet, the panel prompts you to add one. If there's no AI activity in the range, it says so rather than showing an empty number.

## Logging human time on cases

For AI+Human cases, the human still spent some time — and the only honest way to know how much is for the analyst to **record it on the case**. When time is logged on a case, it's subtracted from the analyst-equivalent value, so the savings figure reflects the work AI genuinely took off your team. Logged time can also be tagged with the cost profile it belongs to, so it's valued at the right rate.

If your team doesn't log time, the model still works — AI+Human cases are credited the full cost to handle them (the crediting rule above), and you simply won't see the human time netted out. Logging time makes the figure more precise; it's never required.

## AI spend

The **AI spend** in the calculation is the Claude API token cost reported by the AI gateway for your agents' sessions over the selected period. This is what **Cost Analytics** charts and breaks down by model and trigger rule, and what the savings calculation nets out. Per-minute session runtime is billed separately on your invoice.

## Exporting the data

The savings panel's **Export** menu produces three CSV files for finance and reporting tooling:

- **Savings breakdown** — the per-profile P&L (AI cases, analyst hours, analyst-equivalent value, logged human, AI spend, net savings, ROI).
- **Raw resolution data** — the underlying counts (resolution modes, logged seconds by profile, AI-handled cases by severity).
- **Spend by model & rule** — AI spend, sessions, and tokens broken down by model and trigger rule.

Money is exported as plain USD numbers so the files drop straight into a spreadsheet.

## Fleet / MSSP rollup

On the **Fleet Billing → AI Spend** tab, the **AI Savings (7d)** card sums savings across every managed organization that has a cost profile configured. It reports fleet net savings, ROI, analyst-equivalent value, analyst-hours and FTE-equivalent, and the fleet automation rate. Tenants without a cost profile are excluded from the rollup (and the card says how many of your AI tenants are counted). Per-tenant detail lives on each tenant's own AI Agents usage page.

## Tuning it for trust

A few practices make the figure something you can stand behind:

- **Use your real loaded rate**, and fill in the `rate_source_note` (e.g. "FY26 loaded SOC cost ÷ 1,600 productive hours"). The number is only as credible as its rate.
- **Set realistic handling times.** `minutes_per_investigation` should reflect what a comparable investigation actually takes your team by hand.
- **Log human time** on cases your analysts touch, so AI+Human savings reflect reality.
- **Define a profile per kind of work** (triage vs. deep IR), so per-severity valuation has the right rates to tier.

A note on precision: the **resolution mix is measured** from your Cases — it is not an estimate. The **savings figure depends on the cost profiles you provide**, so it's only as accurate as those profiles. All amounts are in **USD**.

## Relationship to per-session budgets

Cost Tracking is for measurement and reporting — it does **not** cap spend. To hard-limit what a single session can spend, set `max_budget_usd` on the session (see [D&R-Driven Sessions](dr-sessions.md) and [User Sessions](user-sessions.md)). The fleet view flags enabled agents that have no per-session budget cap, since those can spend without limit.

## FAQ

**What counts as an AI agent "working" a case?**
Any action an AI agent records on the case — adding findings or notes, classifying it, or resolving it. That activity appears on the case timeline and is attributed to the agent.

**Why is a case counted as AI+Human?**
Because both an agent and a person took action on it. The AI did work on the case, and an analyst also did. It's credited the full cost-to-handle, with any logged human time subtracted.

**Are Human-only cases counted as savings?**
No. They're shown in the resolution mix as your manual baseline, but they contribute nothing to savings — AI wasn't involved.

**My SOC has several analyst tiers with different rates. How do I model that?**
Create a cost profile for each (e.g. L1, L2, IR), each with its own rate and handling time. With more than one profile, cases are valued per severity automatically; you can also select a single profile to value the whole caseload against one kind of work.

**Is this a bill or a charge?**
No. The savings figure is an internal estimate of displaced analyst labor for your own reporting. It is not an invoice and nothing is charged based on it.

**Why might savings be negative?**
If AI spend (plus any logged human time) exceeds the value of the work displaced, the figure is shown as a net cost — honestly — rather than hidden. That's a sign to revisit the profile, or that the agents are doing low-volume or expensive work.

## See also

- [D&R-Driven Sessions](dr-sessions.md) — how agents are triggered to work cases automatically, and `max_budget_usd`.
- [User Sessions](user-sessions.md) — interactive sessions and budgets.
- [Tool Permissions & Profiles](tool-permissions.md) — what agents are allowed to do.
- [Command Line Interface](cli.md) — manage Hive records, including `ai_cost_model`, from the CLI.
- [Billing options](../7-administration/billing/options.md) — how LimaCharlie billing works overall.
