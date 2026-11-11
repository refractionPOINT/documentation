# Console

The Investigation Engine lives in the web console under **Investigations
(experimental)** in the sidebar, at `/orgs/<oid>/investigate`. The section is shown
to users who hold both `investigation.get` and `insight.evt.get`, and only in
organizations where the feature is enabled. Controls that need more permissions are
disabled with a tooltip naming what you need. See [Permissions](permissions.md).

Inside the section, the tabs are **Runs**, **Approvals**, **Templates**, **Policy**
and **Performance**. A **New investigation** button is always at the top.

## Start an investigation

### From an alert, a case, an entity or a message

An **Investigate** button appears where you are looking at something to investigate:

| Where | What it starts from |
|---|---|
| A detection (detection viewer) | The detection. Also offers **Draft with AI** (see [below](#draft-a-template-with-ai)). |
| A case (case header, until the case is closed) | The case. |
| A Cloud Security entity page | The entity. |
| An Email Security message (message drawer) | The message. |
| The **New investigation** button, or **Start your first investigation** on an empty Runs list | The launcher, empty. |

On a detection or a case, **Investigate** starts a run immediately and opens it. No
template is sent, so the engine **picks the template by `applies_to`** against the
detection's category (or the case's severity and category). The caret beside the button
opens a menu: **Start with a template** lists the organization's templates so you can
pick one explicitly, and **More options…** opens the full launcher prefilled.

If no template matches, you see **No template fits this alert. Choose one with the
arrow next to the button.** Install or write a template with an `applies_to` that covers
the alert, or choose one by hand.

A run started on a case does not write a second case.

### The launcher

**New investigation** opens the launcher, **Start an investigation**.

#### What to investigate

- **Trigger**: Detection, Email message, Entity, Case or Question, and its
  identifier or text.
- **Plan template**: the organization's templates. If your link or the trigger implies
  a default that does not exist, you are asked to choose one.
- **Run as**: shown when the policy offers more than one identity. The default is the
  identity the policy names for the chosen template (**policy default**); the alternatives
  are the identities the policy allows, which can be **Your own token** and other
  policy secrets. "Everything the run reads or does happens with these permissions." The
  choices are looked up for the template you pick, so they change with it.

#### How to run it

- **Urgency** (Low, Medium, High, Critical; empty is Automatic) and **Mode** (**Triage
  only**, **Full (triage, scoping, containment)**, **Scope only**).
- **Speculation**: Conservative, Balanced or Aggressive; empty uses the policy
  default.
- **Create a case**: on by default. "Write the verdict and its proof to a case."
- **Also run a serial baseline**: starts a second run of the same alert, one step at a
  time, so the speedup is measured instead of estimated. The baseline never writes a
  case and never acts.
- **Strict**: refuse the run, instead of reducing the value, when an override would
  loosen the policy.

**Policy context** (category, priority, severity) feeds the policy lookup. **Tighten the
policy for this run** lets you lower budgets, raise decision thresholds, lower an
action class's autonomy mode or raise its minimum confidence. Overrides can only make
the policy stricter. A value looser than the policy is moved to the policy value, and
the launcher says so: **Some overrides were reduced to the policy value**.

The panel on the right is the **Effective policy** for the inputs you entered.

## Runs

The **Runs** tab lists the organization's runs, newest first, 50 at a time. While the
first page holds a run that is still in progress it refreshes every few seconds; a page
of finished runs does not refresh by itself, so reload to see runs started since.
Columns: State, Verdict, Trigger, Started by, Template, Time to
verdict, Speedup, Started and Actions (how many await a decision). Filters are
evaluated by the engine, so they cover all runs: search (detection, case, entity,
message or question), State, Verdict, Template, Time range, Started by, and **Mine**.

### A run

Opening a run shows its header (template and version, how the template was picked,
who started it, the identity it **Runs as**), a verdict chip, the live **P(true
positive)**, the run state and phase, and a strip of statistics: time to verdict,
speedup versus serial, steps (and how many were cancelled), cache hits, search events,
and LLM cost. A finished run is replayed from its log, and a live one updates itself.

The six tabs:

| Tab | What it shows |
|---|---|
| **Plan** | A dependency graph of the facts the engine gathered, by wave, ending in the proof. Click a node for its status, latency, request and result. Legend: in the completed proof, critical path, cancelled, speculative, unknown. Beside it, the **belief** chart (P(true positive) over time with the escalate, scope and dismiss thresholds) and **Why**: the plain-language reason for the verdict, the evidence that raised or lowered the probability, and the facts that are unknown. |
| **Timeline** | Bars per kind of step (indexed read, scan, live task, LLM judgement, action) showing what ran in parallel, what was cancelled and the critical path, with the time a serial run would have taken. |
| **Evidence** | Every fact the run gathered, filterable to *unknown* or *in proof*. A fact is **Known**, **Nothing found** (a real, complete negative), **Partial** (possibly incomplete) or **Unknown** (could not be determined, which is not a finding of absence). |
| **Actions** | The actions the run proposed or took, with the **Automatic actions** switch and, for a live run, **Cancel run** (with an option to also revert active leases). |
| **Case** | The case document the run wrote: summary, proof with cited facts, conclusion, signals, detections, entities, telemetry, artifacts, unknowns and actions, and a link to open the case. |
| **Compare** | What-if evaluation of the facts the run recorded, under another template or a tighter policy. It runs no new queries and changes nothing. Available once the run has finished. |

## Approvals

The **Approvals** tab is the inbox of actions across **all** runs, so you see what is
waiting for a person without opening each run. By default it shows actions in
**Awaiting approval**. Filter by state (including Proposed, Outcome uncertain, Active,
Executing, Reverting, Confirmed, Reverted, Failed, Denied and Expired) and by action
class.

Each row shows the run it came from, with its template, state, verdict, urgency and
case, and a link to open the run's evidence. The action card shows the class (such as
**Isolate from network**), the target, its state and mode, the confidence, the
deadline for a decision, the lease time left, who decided, and its history.

| State | Buttons |
|---|---|
| Proposed, Awaiting approval | **Approve**, **Deny** |
| Active | **Revert**, **Extend lease** (+1 h or +2 h), **Confirm** |
| Outcome uncertain | None that work today (see below) |

Every button asks for confirmation and takes an optional note recorded in the action's
history. **Confirm** keeps an action in place and stops its lease from reverting it.

- A proposal in **Suggest** mode is never executed, and **Approve** on it is refused
  with "this action class is in suggest mode", even if you hold every permission. A
  proposal keeps the mode it was made with, so changing the policy afterwards does not
  unlock it. To execute an action, set the class to `approve` or `auto` in the policy and
  start a **new** run, with an active template: a run on a draft template is capped at
  Suggest whatever the policy says.
- An **Outcome uncertain** action means the engine could not confirm whether the action
  took effect. It settles itself: a late answer from the platform makes it active or
  failed, and when none comes, a reversible action is undone to be safe, while an
  irreversible one is escalated to a person. The console may still offer **Revert** and
  **Confirm** on it, but the engine only accepts those on an active (or, for Revert,
  confirmed) action, so on an uncertain one they return an error. Check the target
  yourself instead.
- A class that is not available yet (see [Action classes](policies.md#action-classes))
  can be proposed but fails when approved.

A button is disabled unless you hold `investigation.set` and `insight.evt.get` **and**
the permission of the action's class (see [Permissions](permissions.md#permission-of-the-action-class)).
**Approve** and **Deny** also require being on the class's approver list when the
policy sets one; the other decisions do not check it.

## Templates

The **Templates** tab lists the organization's `investigation_plan` records with
their status (Draft or Active), version, the categories each applies to, and
description. A badge marks templates that appeared while you had the page open, for
example one an AI agent just saved.

### Install default templates

**Install default templates** opens a dialog that lists the
[default library](templates.md#the-default-library). Each row shows the template, its
version, its status as shipped and one of **Not installed**, **Installed** or **Update
available**.

- **Install as** is **Draft (default)** or **Active**. Draft is selected whenever you
  open the dialog, **whatever status the library recommends**: the column shows
  the library's recommendation ("Recommended: Draft" for the current library) for
  information only. Each row has its own **Active** switch to
  override the choice for that template.
- **Install selected** and **Install all** write a copy of each template into your
  organization, one at a time, with your own token. A failure on one template does not
  stop the others.
- Anything that would be written as **Active** shows a warning (active templates start
  from detection rules and cases on their own), and installing **all** as Active asks
  you to confirm.
- A template that is already installed is never replaced silently. If a newer library
  version exists, selecting the update asks you to confirm: **An update replaces your
  version**, including any changes you made, and writes it with the status chosen
  for it. If that replaces a live (Active) template with a Draft, the dialog says so and
  asks again, since it stops that template from running on its own.
- The result lists each template as **Installed**, **Updated**, **Already exists** (a
  record with that name, possibly disabled, was left alone), **Already up to date** (the
  record changed after the list was read and is no longer older than the library's),
  **Changed meanwhile** (someone made it active or draft after you confirmed; open the
  dialog again) or **Failed**.
- You need `investigation_plan.get` and `investigation_plan.set`; without them the
  dialog explains what is missing.

### Create, edit and copy

**New template** and **Edit** open a YAML editor. Names use letters, digits, dots,
dashes and underscores and must start with a letter or digit. **Start from** offers a
blank skeleton or a library example, and **Copy** on a template creates `<name>-copy`
as a draft at version 1.

- **Validate** asks the engine to check the text and shows errors and warnings with
  their paths and suggestions, plus the worst-case estimate (steps, searches, AI steps,
  seconds, budgets exceeded).
- **Save** writes the Hive record. Saving never changes the status: "New templates and
  copies are drafts; use Make active on the template's page."
- Editing an active template warns that the change applies to automatic investigations
  right away. Move it back to draft first to test safely.
- Saving needs `investigation_plan.get` and `investigation_plan.set`. If the record
  changed since you opened it, you are told to reload and apply your edit again.

### Test on past alerts

On a template's page (or in the editor, to test unsaved text), **Test on past alerts**
runs the template's real read-only steps on alerts that already happened. It creates
no run, no case and no action; only the test result is kept, for 24 hours. You build a list of samples, at most 25 alerts in
total:

- **A detection**, by detection id;
- **A case**, by case id: its classification is the expected answer;
- **Last N of a category**: the newest N detections of that category, N from 1 to 25.

The result shows a progress bar, then summary cards: **Alerts tested**, **Verdicts**,
**Agreement with closed cases**, **Unknowns**, **Cost** and **Time per alert**. Below,
**Results per alert** gives each alert's verdict, probability and basis, the proof, the
unknowns, the cost, the actions the template **would propose**, and a chip: **Agrees
with the case**, **Disagrees with the case**, **Undecided** or **No closed case**.

If steps were refused for lack of permission, a banner lists them: the test ran with
the permissions of whoever started it, so grant the permission of the product each of
those facts reads (for example `mailsec.get` for email steps) and test again. Until
then those facts stay unknown and the verdicts mean little. Results are kept for 24
hours. You need `investigation.set`, `investigation.get` and `insight.evt.get`: the
console starts the test with the first and follows it with the second.

### Make active, or back to draft

On the template's page:

- **Make active** asks for confirmation and shows the last test from this browser
  (alerts run, verdict counts and the agreement with closed cases), or
  "This template has not been tested from this browser." A test is not required, but
  look at it. **Make active** is disabled until the engine reports the template valid.
  Active templates "are picked by detections, rules and cases on their own, and can
  propose actions within your org policy."
- **Back to draft** stops detections and cases from picking the template. Runs already
  in progress are not affected.
- **Delete** removes the template from the organization and cannot be undone.

Promotion is made by a person in the console. An API key cannot write an active
template unless the organization opted out. See [Permissions](permissions.md#active-templates-can-only-be-written-by-a-person).

### Draft a template with AI

**Draft with AI** (on the Templates tab, and on a detection) opens **Draft a template
with AI**. Describe the alerts you want investigated in plain words, or start from a
detection as the example alert. An AI agent looks at your data, writes a plan, tests it
on past alerts and saves it as a **draft**. The new draft appears in the list, and you
decide whether it goes live. The workflow it follows is described in
[Build and Tune Templates with an AI Agent](build-templates-with-ai.md).

The button needs `investigation.get`, `investigation.set`, `insight.evt.get`,
`investigation_plan.get`, `investigation_plan.set` and `ai_agent.exec`, and it uses the
**Investigation plan author** AI agent from the AI agent catalog. If that agent is not
installed in your organization, the dialog offers **Install the plan author**, or tells
you to ask an administrator. The agent works with its own API key, so it can only read
what that key allows; missing permissions show up as forbidden steps in its tests.

## Policy

The **Policy** tab does not edit policies. Policy records are `investigation_policy`
Hive records, which you edit with the Hive API, the CLI or infrastructure-as-code. See
[Policies and Autonomy](policies.md). The tab shows:

- **Effective policy**: what the organization's policy allows, record by record. Leave
  the lookup empty for the organization default, or enter a
  category, severity, priority and a template to see what applies to that alert (the
  template selects its run identity). It lists the
  policy records applied, the budgets, decision thresholds, speculation by urgency, and
  the actions and autonomy table (mode, minimum confidence, lease, approvers and the
  record each value comes from).
- **Automatic actions**: the pause switch.

### Pause automatic actions

The switch shows **Running: actions in auto mode can execute** or **Paused: nothing
executes without a person**, and who paused it and when. **Pause automatic actions**
stops every action that would execute on its own, in every run of the organization.
"Actions that wait for approval are not affected." **Resume automatic actions** lets
actions in `auto` mode execute again. Everyone with console access can see the state;
changing it needs `org.conf.set`. The same switch is at the top of every run's
**Actions** tab.

## Performance

The **Performance** tab aggregates runs over the last 24 hours, 7 days, 30 days or a
custom range, optionally for one template. It shows the **speed-up versus serial**,
where the gain comes from (steps running together versus stopping early), time to
verdict, cancelled work, cache hit rate, batched calls, speculation efficiency, search
events (billed and free), LLM spend, analyst feedback (labels and corrections), the
operator latency table and the actions by class and state.

The speedup is only shown for runs that have a serial baseline of the same
investigation: start it with **Also run a serial baseline**. The page reads at most the
2,000 most recent runs of the range and says when it truncated.
