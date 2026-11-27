# Console

The web app's **Investigations** section is the console of the Investigation Engine. It
uses the same [API](api-reference.md) as the CLI and the MCP tools, with the same
[permissions](permissions.md): a control the gateway would refuse is disabled, with a
tooltip naming the permission you need. The section needs `investigation.get` and
`insight.evt.get` to show at all.

!!! warning "Experimental"
    Screens and labels can change. Console changes reach production with a web app
    release, so what you see can lag behind these pages.

The section has five pages: **Runs**, **Actions**, **Templates**, **Settings** and
**Measure**, plus **New investigation**. A banner says how many actions wait for a person.

## Start an investigation

- **From a detection, a case or an email message**, the **Investigate** button starts a run
  of the active template whose `applies_to` matches it.
- **New investigation** opens the launcher: what to investigate (a detection, a case, an
  entity or a question), which template, and optional inputs and tighter budgets. A draft
  template can be run here: it only suggests.

## Runs

The list of the organization's runs, filtered and sorted by the engine (state, outcome,
template, trigger, who started it, time). The run queue panel above it shows what waits
(`queued`, running, parked on an AI agent) against the parallel limit, by rule and by
template, the hour's cap, and **Flush** for a rule, a template or everything queued. Flush
asks first and cannot be undone. See [The Run Queue](run-queue.md).

A run's page shows:

- the outcome sentence and what decided it, or the AI's recommendation and what was
  missing;
- the evidence: each step a rule or the review read, with its sentence;
- how it ran: every step with its status, reason, timing and cost, the steps it skipped or
  cancelled, Playbook and AI agent steps, and a hand-off with the agent's proposal;
- its actions, each with how it is decided (acts on its own, after a person approves, or
  on a condition), why it waits, its lease and what happens at its end, its "check again"
  history and its buttons;
- the case it wrote, and whether the template or the settings decided that
  (`case_mode_from`).

## Actions

The approvals inbox: every action that waits for a person, across all runs, what needs a
person first. Filter by why it waits (the template asks, a condition held, the AI
recommended it, the organization is paused, the circuit breaker), by template, target and
state; a **Held** view lists the actions kept for a person at the end of their lease.

Each action shows what it does in words, on which target (a hostname, a message subject),
why it waits and until when. The buttons follow its `eligibility`: **Approve** and **Deny**
while it waits; **Extend**, **Confirm** and **Undo** while a leased action is in effect or
held; **Undo** for a tag or a confirmed action. A suggestion (a draft's action) has no
Approve button. An action whose outcome is not known has no button: the engine settles it.

The log of automatic actions lists what the engine did on its own, with **Undo** per entry
and for a selection. See [Actions, Approvals and Undo](actions.md).

## Templates

The organization's templates and checks, draft and active, including stored records that do
not load (with why). From here:

- install the default library (as drafts), create, copy and edit a template, with
  validation as you type;
- read a template in words: each `act` entry is one line ("Isolates the host on its own when
  `banned_binary` decides, unless the host is tagged server; kept 2h, then released"), and a
  line says what the AI may decide;
- test it on past alerts, and compare an edit against finished runs;
- **Make active**, or back to draft. A draft shows that it only suggests.

Saving and promoting need `investigation_plan.get` and `investigation_plan.set`.

## Settings

One form over the [settings record](settings.md): the **pause** at the top with who set it
and when; the **circuit breaker** caps with the live count ("3 of 20 automatic containments
in the last hour"); the run keys with their readiness per template (missing permissions,
ACL scopes); notifications; the AI agent; limits, budgets and the case mode; and a read-only
view of the record. Writing needs `investigation_policy.get` and `investigation_policy.set`.
If Git Sync manages the record, change it in git instead.

## Measure

Per template: runs and outcomes, time to verdict and from detection to verdict and to
action, AI spend, which rules decided how many runs, which evidence was missing and why,
hand-offs and the drafts agents proposed, and per action how often it acted alone, waited
(by reason), was approved, denied, expired, released, held or undone. The console shows it only to people who
also hold `investigation_policy.set`; the same numbers are a plain read through the API, CLI
and MCP.
