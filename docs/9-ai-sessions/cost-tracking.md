# AI Cost Tracking & Savings

AI Sessions can take on work that a human analyst would otherwise do. Cost Tracking turns that into numbers a CFO can audit: what your AI agents spend, what analyst work they took on, and the net savings — measured from your real case resolution mix, not a hypothetical.

This page covers the cost analytics and savings views in the LimaCharlie web app. For the hard per-session spend cap, see `max_budget_usd` in [D&R-Driven Sessions](dr-sessions.md) and [User Sessions](user-sessions.md).

## Where to find it

| View | Location | Scope |
|------|----------|-------|
| **Cost Analytics** | An organization's AI usage page | AI spend, tokens, and unit economics for one org, with per-model and per-rule breakdowns |
| **AI Resolution & Savings** | Same AI usage page | The savings model: resolution mix, analyst-equivalent value, ROI |
| **AI Savings (7d)** | Fleet Billing → AI Spend tab | A cross-tenant (MSSP) rollup of savings across every managed organization |

## The two halves of cost

LimaCharlie uses a Bring Your Own Key model, so AI cost has two parts:

- **AI spend** — the Claude API token cost reported by the AI gateway for D&R-driven and interactive sessions. This is what Cost Analytics charts and breaks down by model and trigger rule, and what the savings calculation nets out. Per-minute session runtime is billed separately on your invoice.
- **Analyst-equivalent value** — what the same investigations would have cost in human analyst time. This is the savings side, and it is anchored to how your cases were actually resolved.

Savings is the first netted against the second:

```text
net savings = analyst-equivalent value − logged human time − AI spend
```

## Cost profiles

A **cost profile** is a named category of analyst work that AI stands in for — for example "SOC L1 Triage" or "IR Analyst". Each profile has:

| Field | Meaning |
|-------|---------|
| **Label** | Display name, e.g. *SOC L1 Triage* |
| **Loaded hourly rate** | Fully-burdened analyst cost per hour, in USD |
| **Minutes per investigation** | Standard analyst minutes to handle one investigation of this kind **without** AI |
| **Rate basis** (optional) | A note on where the rate came from, so a reported figure survives a finance review |

From these, the **cost to handle** one investigation of that profile is:

```text
cost to handle = loaded_hourly_rate × (minutes_per_investigation / 60)
```

!!! note "Configure at least one profile"
    Savings are only computed once an organization has a cost profile. Open the AI usage page → **AI Resolution & Savings** → **Manage profiles** to add one. Until then the panel shows a setup prompt rather than fabricated numbers.

Profiles are stored per organization and can be created, edited, and removed from that panel.

## How savings are measured

The model is **resolution-anchored**: every case is real work that had to be done — the only question is who did it. LimaCharlie classifies each case from its timeline into one of three buckets:

- **AI-only** — handled entirely by an AI session
- **AI + Human** — an AI session contributed, a human also logged time
- **Human-only** — no AI involvement

Any case an AI touched (AI-only or AI + Human) is credited the full cost to handle. The human time actually logged against cases is then subtracted, so AI + Human cases are netted down by recorded human effort. Human-only cases contribute nothing.

### Per-severity valuation

Cases are valued per **severity**, not at one blanket rate. When you have more than one cost profile, LimaCharlie tiers them by cost — the cheapest profile handles the lowest severities, the most expensive handles the highest (e.g. an L1 triage rate for informational cases, an IR analyst rate for critical ones). The analyst-equivalent value is the sum across severities of:

```text
cases at that severity × cost to handle of that severity's profile
```

### Headline metrics

The savings view surfaces:

| Metric | Meaning |
|--------|---------|
| **Net savings** | Analyst-equivalent value minus logged human time and AI spend |
| **ROI** | Analyst-equivalent value divided by AI spend |
| **AI automation rate** | Share of investigations that were AI-handled |
| **Analyst-hours freed** | The manual hours the AI-handled cases represent (rate-independent) |
| **FTE-equivalent** | Those analyst-hours expressed as a fraction of one full-time analyst over the selected range |
| **Cost / investigation** | AI spend per AI-handled case |

A **per-profile P&L** table breaks net savings down by cost profile, and a **cumulative net savings** chart shows how savings accrued over the range. The trend uses real daily AI spend with the period's analyst value distributed across days by AI activity — it shows accrual, not a per-day measurement.

!!! tip "Pick a profile to scope the view"
    The profile selector switches the figures between *all profiles* and a single profile's slice — e.g. "how much did I save on IR Analyst cases?" versus the whole caseload.

## Exporting the data

The savings panel's **Export** menu produces three CSV files for finance and reporting tooling:

- **Savings breakdown** — the per-profile P&L (AI cases, analyst hours, analyst-equivalent value, logged human, AI spend, net savings, ROI)
- **Raw resolution data** — the underlying counts (resolution modes, logged seconds by profile, AI-handled cases by severity)
- **Spend by model & rule** — AI spend, sessions, and tokens broken down by model and trigger rule

Money is exported as plain USD numbers so the files drop straight into a spreadsheet.

## Fleet / MSSP rollup

On the **Fleet Billing → AI Spend** tab, the **AI Savings (7d)** card sums savings across every managed organization that has a cost profile configured. It reports fleet net savings, ROI, analyst-equivalent value, analyst-hours and FTE-equivalent, and the fleet automation rate. Tenants without a cost profile are excluded from the rollup (and the card says how many of your AI tenants are counted). Per-tenant detail lives on each tenant's own AI usage page.

## Relationship to per-session budgets

Cost Tracking is for measurement and reporting — it does **not** cap spend. To hard-limit what a single session can spend, set `max_budget_usd` on the session (see [D&R-Driven Sessions](dr-sessions.md) and [User Sessions](user-sessions.md)). The fleet view flags enabled agents that have no per-session budget cap, since those can spend without limit.

## See also

- [D&R-Driven Sessions](dr-sessions.md) — `max_budget_usd` and session triggering
- [User Sessions](user-sessions.md) — interactive sessions and budgets
- [Billing options](../7-administration/billing/options/) — how LimaCharlie billing works overall
