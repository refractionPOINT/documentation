# Grid: Your AI Field Engineer

Grid puts a working AI security engineer in your environment. You describe the
outcome that you want in plain English — "triage quarantined phishing in our
Google Workspace and open a case for anything risky". Grid then builds the
automation that delivers that outcome, and it continues to watch over it for
you.

Grid needs no rule syntax, no detection logic, and no manual integration work
from you. You supply the goal, and Grid builds and runs the security program.

!!! tip "The one-sentence version"
    Grid takes a plain-language goal and makes it into supervised security
    automation that runs in your LimaCharlie organization — usually in a few
    minutes.

## What Grid actually gives you

Grid is not a chatbot that answers questions and then forgets them. When you
onboard with Grid, you get an **AI Field Deployed Engineer (FDE)** — a
persistent, named expert that stays in your organization.

The FDE is modeled on a real Forward Deployed Engineer: the resident expert
that a security vendor puts with a customer to design, build, and tune the
setup of that customer. Two things make the FDE different from a usual AI
assistant:

- **It supervises. It does not do the repetitive work itself.** To "automate
  phishing triage," the FDE does not read your emails one by one. It *builds* a
  dedicated worker agent whose only job is email triage, connects the data
  source and the trigger that feed it, and gives it a place to file its
  findings. The FDE then watches that worker: the quality of the work, the flow
  of the data, and the need for tuning.
- **It continues to work when you do not watch it.** The FDE runs unattended on
  a schedule that you choose (from every 30 minutes to every week). At each run
  it checks the workers that it built, looks for gaps, and corrects what
  drifts.

The FDE is like an engineer that designs your security automation, builds it,
and then comes back every day to make sure that it still works — but it does
the first build in minutes and it never takes a day off.

## Built on battle-hardened infrastructure

Grid is new. The infrastructure below it is not.

Every worker agent, trigger, and detection that Grid builds runs on the
**LimaCharlie platform** — the same Agentic SecOps workspace that MSSPs and
security teams already use to run detection and response across their fleets at
scale. The data pipeline, the detection-and-response engine, the secrets vault,
the case management, and the audit trail are not new code written for an AI
demonstration. Grid is an expert *operator* of infrastructure that carried real
production security workloads for years.

This is important in two practical ways:

- **Everything that Grid builds is real LimaCharlie configuration** — D&R
  rules, cloud adapters, playbooks, AI agents — that you can inspect, edit,
  export, or run yourself. Grid keeps no part of your automation in a Grid-only
  black box.
- **The guardrails are platform guardrails.** LimaCharlie itself enforces the
  permissions, the data residency, the audit logging, and the rollback of Grid.
  The good intentions of the AI do not enforce them (more on this below).

## How it works, end to end

Grid runs as a short, guided conversation. These are all the steps:

1. **You state the outcome.** Grid asks one main question: what do you want to
   be true in this organization that is not true today? You answer in plain
   language. Grid leads with expert recommendations and does not ask you for
   technical details.
2. **Grid connects the data, if necessary.** An FDE needs the data that its
   outcome depends on. If the source that you need (a SaaS feed, cloud logs,
   endpoint telemetry) does not flow yet, Grid helps you connect it first. Grid
   guides you through the credentials and selects the correct adapter type for
   you.
3. **Grid proposes a charter.** It writes a complete plan in plain language:
   the outcome, what it will build, what runs automatically, what needs your
   approval, and how you will know that it works. Grid validates the plan
   against your *real* data before it shows the plan to you, so the plan holds
   verified details and not guesses. You review the plan and reply **go**, or
   ask for changes.
4. **Grid builds the whole solution.** At its first run, the FDE builds the
   *complete* solution end to end — every worker agent, every trigger, every
   detection — and tests it before it hands control back to you. There is no
   "phase one now, the rest later."
5. **Grid shows you what it built.** You get a visual map (the "story") of
   everything that now runs in your organization: the FDE supervisor, every
   worker that it created, and the connections between them.
6. **Grid keeps watch.** After that, the FDE runs on its schedule. It
   supervises what it built and flags anything that needs your attention.

!!! note "Talking in outcomes, not plumbing"
    Grid speaks in outcomes and implications — "the system will investigate
    each restore request and flag the risky ones, at a cost of about X" — and
    not in LimaCharlie mechanics. To use Grid, you do not need to know what a
    D&R rule is. The mechanics are available if you want them, but they are
    never necessary.

## Your first few minutes

To meet Grid, give it a goal and watch it work.

1. **Open Grid** and sign in. You can also create an account: Grid can create a
   new organization for you as part of onboarding.
2. **Describe the outcome that you want.** Be concrete about the result, not
   about the method. Good first prompts:
    - *"Triage quarantined phishing in our Google Workspace and open a case for
      anything risky."*
    - *"Watch our cloud audit logs for risky permission changes and alert me
      before anything bad happens."*
    - *"Review endpoint detections each morning and summarize what actually
      matters."*
3. **Answer the few questions that Grid asks.** Grid asks only for what it
   cannot find on its own — your goal, any hard constraints, and the occasional
   judgment call where your preference has to win. If Grid needs a credential
   (an API key, an LLM provider key), it gives you a secure form. You never
   paste secrets into the chat.
4. **Read the charter and reply `go`.** Confirm what will run on its own and
   what will ask you first.
5. **Watch Grid build,** then examine the story map of what now exists.

You now have a supervised AI engineer that runs in your organization.

!!! tip "Start small, then grow"
    You do not have to automate everything at the same time. Give your FDE one
    clear outcome to own. When you trust it, open a chat and ask it to take on
    more.

## You stay in control

You set the level of autonomy. It is not a default that you must accept.

- **Approval gates.** During onboarding you decide which actions the FDE can
  take on its own and which actions must ask a human first. You can put an
  approval step in front of any action that changes your environment, notifies
  people, or deletes something. When the FDE wants to do a gated action, it
  opens a **case** that explains what it wants to do, why, and the cost — and
  then waits for your go-ahead. Nothing risky happens silently.
- **Least privilege, enforced by the platform.** Each FDE (and each worker that
  it builds) runs with its own scoped API key that holds only the permissions
  its job needs. That key — not the prompt of the AI — is the real boundary. An
  action outside its grant cannot happen.
- **Full audit trail.** Everything that Grid does is ordinary LimaCharlie
  activity: logged, attributable, and open to review like any other operation
  in your organization.

## Everything is visible and reversible

Grid always shows you what it changed.

- **The story map** shows the full graph of what an FDE owns — the supervisor,
  its workers, the triggers, the data sources, the playbooks — and how they
  connect. It is the picture of your automation, and it stays current as the
  FDE builds.
- **One-tag rollback.** Every resource that an FDE creates or touches carries a
  tag with the name of that FDE. To remove an FDE and its *entire* footprint —
  every worker, rule, and secret that it ever made — you run one tag query. No
  orphaned configuration stays behind, and you can undo everything.

## Talking to your FDE

Your FDE is not a script that you start and forget. You can open a chat with it
at any time from the organization overview ("**Chat with FDE**").

In a chat the FDE behaves differently from its unattended runs. It orients
itself in read-only mode and gives you a short status in plain language — what
it built, what is pending, anything unhealthy — and then waits for your
direction. The FDE does not run its build-and-supervise program while you talk
to it, so you can ask questions, request changes, or hand it new work without
it going off on its own. Direct it as you direct an engineer on your team.

## What it costs

A LimaCharlie organization runs on a free tier by default, and many Grid setups
fit inside it. Some outcomes need paid components — a high-volume data feed,
deployed endpoint sensors, or a deterministic playbook — and in that case Grid
tells you *before* it builds: which paid piece the outcome needs, why, in plain
terms, and what you will need to do (add a payment method, raise a quota). If
you do not want the paid piece, Grid offers to re-scope the plan to free-tier
pieces only. You never get a surprise bill from automation that you did not
approve.

## Where to go next

Grid is the guided, outcome-first entry point to the AI capabilities of
LimaCharlie. Everything that Grid builds is standard platform configuration, so
when you want more depth, the rest of this documentation applies directly:

- [AI Sessions Overview](index.md) — the AI runtime that the FDEs of Grid run
  on.
- [User Sessions](user-sessions.md) — interactive AI sessions, including the
  chat experience behind "Chat with FDE."
- [D&R-Driven Sessions](dr-sessions.md) — how scheduled and event-triggered AI
  runs work internally.
- [AI Memory](memory.md) — how an FDE remembers its charter and state across
  runs.
- [Tool Permissions & Profiles](tool-permissions.md) — the permission model
  that limits what every agent can do.
- [Story Tags](../8-reference/story-tags.md) — the tagging schema behind the
  story map and one-tag rollback.
