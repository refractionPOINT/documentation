# Console

The Investigation Engine lives in the web console under **Investigations
(experimental)** in the sidebar, at `/orgs/<oid>/investigate`. The section is shown
to users who hold both `investigation.get` and `insight.evt.get`, and only in
organizations where the feature is enabled. Controls that need more permissions are
disabled with a tooltip naming what you need. See [Permissions](permissions.md).

Inside the section, the tabs are **Runs**, **Approvals**, **Templates**, **Policy**
and **Performance** (shown only to people who hold `investigation_policy.set`, which
the statistics need). **Auto-investigation** has its own sections: **Overview**,
**Automatic actions** and **Settings**. A **New investigation** button is always at the
top.

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

A one-click run on a case writes no case: it neither opens a second one nor writes
into the existing one. To have a run write its findings into the case, start it from
the API with `"case": "attach:<case number>"`, or with a D&R rule on the case (see
[Automatic Starts](automation.md#dr-rules-on-a-new-case)).

When the engine refuses a start, the console shows why and a link to the page that
fixes it (**Open templates**, **Open policy** or **Open runs**): for example "No
active template applies to this trigger" or "The policy names no identity for runs
started without a person". The causes are the `reason_code` values in
[Troubleshooting](troubleshooting.md#why-a-start-was-refused-reason_code).

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
- **Create a case**: on by default. "Write the outcome and what decided it to a case."
- **Also run a serial baseline**: starts a second run of the same alert, one step at a
  time, so the speedup is measured instead of estimated. The baseline never writes a
  case and never acts.
- **Strict**: refuse the run, instead of reducing the value, when an override would
  loosen the policy.

**Policy context** (category, priority, severity) feeds the policy lookup. **Tighten the
policy for this run** lets you lower budgets or lower an action class's autonomy
mode. Overrides can only make the policy stricter. A value looser than the policy is moved to the policy value, and
the launcher says so: **Some overrides were reduced to the policy value**.

The panel on the right is the **Effective policy** for the inputs you entered.

## Runs

The **Runs** tab lists the organization's runs, newest first, 50 at a time. Columns:
State, Outcome (such as **Closed by rule**, **AI recommends: benign** or **Couldn't
tell**), Trigger, Started by, Template, Time to verdict, Started and Actions (how many
await a decision). A Speedup column appears only when the page holds a run that has a
serial baseline.

- **Filters** are evaluated by the engine, so they cover all runs: search (detection,
  case, entity, message or question), State, Outcome, Template, Time range, Started by
  (an email, or an identity such as `user:<id>`) and **Mine**. **Not decided yet** under
  Outcome lists the runs that have no outcome. The **Waiting for a person** chip lists
  the runs in the state **Waiting for a decision** (they have their answer, and their
  actions wait for a person).
- **The filter is in the address.** Every filter is read from and written to the page's
  query string (`kind`, `session`, `state`, `outcome`, `template`, `q`, `since`,
  `entity`, `started_by`), so a link to the page reproduces your view. A value the
  engine would refuse is dropped. A template's page has a **View runs** button. A check
  has no runs of its own, so each template that calls it, in the check's **Used by**
  list, has a **View its runs** link.
- **New runs.** The first page is read again every 20 seconds while the tab is visible
  (every 5 seconds while a run on it is in progress). Runs that arrive are counted
  (**Show 3 new runs**) and put on top when you ask, so the rows do not move under you;
  when the whole first page is new, the button says **50+** and starts the list over.
  A row you already see updates in place.
- **Order.** The list is newest first. Column headers do not sort the rows loaded so
  far, since that would look like a sort of the whole list. The engine can order the
  whole list, newest first, oldest first, or by time to verdict (shortest or longest
  first, runs without one last): see [Listing runs](api-reference.md#runs).

### A run

Opening a run shows its header. It leads with what was investigated, as a link (a
detection opens the Detections page on that detection, a case opens the case), when
the run started in your time zone, how many more alerts joined it, the case it wrote
to, and what waits: **N actions wait for a decision** (a link to the **Actions** tab) or
**The AI's recommendation waits for a person to decide**. It also shows the template
and version, how the template was picked and who started it, and the identity the run
**Runs as**. A run on a draft template carries the chip **Draft template: actions are
suggestions only**. The top tiles are time to verdict (to the first decision), search
and AI cost. **How it ran** holds the rest: speedup versus serial (only when a
measured baseline exists), steps and how many were cancelled, cache hits and
speculation. A finished run is replayed from its log, and a live one updates itself.

The free search range a run used is its own lookback when its overrides lowered
`budgets.lookback_days`, and otherwise the policy's lookback (30 days at most).

At the top, the **outcome banner** says how the run ended, in one of eight
[outcomes](concepts.md#outcomes): **Closed by rule**, **Escalated by rule**, **Closed by
the AI**, **Escalated by the AI**, **AI recommends: benign**, **AI recommends:
malicious**, **Couldn't tell** or **Conflict: the rules disagree**. Under it is what
decided: the rule's id and its own sentence (**Decided by rule**), or **Decided by the
AI-assisted rule**, or **Decided by the AI review**. While nothing has decided it reads
**Investigating**. Two lines complete it:

- **Also held: `<rule>`, `<rule>`.** The other rules that held with the deciding one.
  After a decision, **A close rule also held afterwards (the escalation stands):
  `<rule>`** (or the mirror sentence when the run closed) names a rule on the opposite
  side that held later. Neither changes the outcome.
- **On a conflict, both rules are named**: **The escalate rule that held: `<rule>`** and
  **The close rule that held: `<rule>`**. A run recorded by an older engine shows only the
  escalate rule.

**When the AI recommends**, the banner says **Waiting for you** and **What the AI
recommends** shows the label, the AI's rationale, what it **Cited** (click a citation
to open that step) and "Self-rated confidence N%, not a probability". The buttons:

- **Close as benign** approves the case close the engine proposed (capped at
  approval), after a confirmation. The case is closed as a false positive.
- **Add `<keys>` to "`<lookup>`" and close** appears when a cited step read one of your
  [Lookups](../7-administration/config-hive/lookups.md). It adds the keys the Lookup
  did not list, then closes as benign. The next alert a rule checks against that list
  closes by rule, with no AI call. It needs write access to that Lookup; an optimized
  Lookup is refused with a pointer to the Lookups page.

These buttons act on the close the engine proposed, so they need
`close.false_positive` in `approve` or `auto` in the policy. In `suggest` the close is
only a suggestion: there is nothing to approve or deny, and you close or work the case
in Cases. See [What "AI recommends" means](walkthrough.md#9-what-ai-recommends-means).

**There is no manual Escalate button.** Escalating is something a template does: an
`escalate` rule, and the `act` entries that fire on it. To decline the proposed close,
use **Deny** on the action in [Approvals](#approvals), and work the case in Cases. To
have a pattern you keep escalating by hand escalate by itself, write the rule (see
[How to Think About Templates](how-to-think-about-templates.md#8-turn-repeated-decisions-into-rules)).

**What was missing** lists, when nothing decided, each step that stayed unknown, why,
what needed it (**Needed by**), and the question for a person (**Ask:**). When a
step is a [check](templates.md#checks-templates-other-templates-call) that could not
tell, what the check itself was missing is listed under it.

**Checks in a run.** A template's call of a check is one collapsible node with its
**outcome badge** (escalated, closed, couldn't tell, conflict). Expanded, it shows the
check's own steps, and a row per element when the call ran once per element (named by
its key, such as the link's URL). When the decision rested on a call, the outcome banner
shows the chain: the template's rule, the call, and the check's rule. The check's
sentence also appears in the case, after the template's own.

Each element of a per-element call has one of the engine's states, in plain words:

| Shown | Means |
|---|---|
| An outcome (escalated, closed, conflict) | The element ran and answered. |
| **Couldn't tell** | The element ran and could not tell. Only elements that ran count here. |
| **Not needed** (neutral) | The run was already decided, so the engine stopped this element on purpose. It is not an element that could not tell. |
| **Stopped before answering** | The run was cancelled, or its time or AI budget ran out, before the element finished. |

The call's summary line is the engine's own sentence ("1 of 4 links checked: 1
malicious, 2 not needed once item X was malicious, 1 not checked (limit 3)"). The
console's count is the fallback and adds "N not needed" and "N stopped before
answering". "Checked" counts only elements that ran. Results of a
[test on past alerts](#test-on-past-alerts) show **Not needed** the same way. **Checks
this run called** compares the version the run froze with the check as it is now, and
says **Changed since this run** or **Deleted since this run**; its link opens the check
as it is now, not the frozen version.

Engine reasons print as a sentence instead of a generic failure: rate limits, a source
that was not covered, a check that could not tell, and the identity and ancestry
reasons each have one, and **What the check lacked** names the element ("for item X").
When the engine refuses a start because of a check (`check_not_startable`,
`check_missing`, `check_not_callable`, `check_invalid`, `check_cycle`,
`check_depth_limit`, `check_size_limit`), the console explains it and links to the
Templates page.

The six tabs:

| Tab | What it shows |
|---|---|
| **Plan** | A dependency graph of the steps the engine gathered, by wave, ending in the outcome. The path of the steps that decided it is highlighted; a recommendation or "Couldn't tell" highlights none. Click a node for its status, latency, request and result, and **In plain words**: **Why** it ran, what it **Found**, and what **Used by** it (a rule, another step, the AI review, the case), or **Not used for the decision**. A step its `only_if` skipped shows as **Skipped by its condition**, with the reason. **Attempts** says **Tried N times** when the step was cancelled and gathered again, lists each earlier attempt with its cancel reason, and, when the step waited for a detection to be stored, how long (**Waited 1 min 40 s for the record to be stored, then found it**; a wait that gave up leaves the step unknown, never "nothing found"). |
| **Timeline** | Bars per kind of step (indexed read, scan, live task, AI question, action) showing what ran in parallel, what was cancelled and the critical path, with the time a serial run would have taken. |
| **Evidence** | Every step the run gathered, filterable to *unknown* or **Behind the decision**. A step is **Known**, **Nothing found** (a real, complete negative), **Partial** (possibly incomplete), **Unknown** (could not be determined, which is not a finding of absence) or skipped. The engine pages the evidence 1,000 facts at a time; when the tab shows fewer facts than the run has, it says **Showing N of M facts** and that the counts, filters and search cover only those. |
| **Actions** | The actions the run proposed or took, read as in [Approvals](#reading-an-action), with the [pause switch](#pause-automatic-actions) and, for a live run, **Cancel run**. **Also revert active leases** undoes the run's leases; a lease of a class whose permission you lack is kept, and a warning stays on screen (**N leases were not reverted because you lack the permission for ...**) until you dismiss it, with the leases still listed as active. |
| **Case** | The case document the run wrote: the outcome sentence, signals and how each was answered, detections, entities, telemetry, the evidence, what stayed unknown, the open question and the actions, and a link to open the case. |
| **Compare** | What-if evaluation of what the run recorded, under another template or a tighter policy: the outcome and **What decided** on each side. It runs no new queries and changes nothing. Available once the run has finished. |

## Approvals

The **Approvals** tab is the inbox of actions across **all** runs, so you see what is
waiting for a person without opening each run. The tab carries a count of what waits
for a person (actions awaiting approval and actions whose outcome is uncertain), shown
as **50+** when there are more than a page.

### Views, filters and order

Three saved views set the states shown:

| View | What it lists |
|---|---|
| **Waiting for a person** (the default) | Actions **awaiting approval**, and actions whose **outcome is uncertain**. |
| **What ran** | Every action that ran or is running: executing, reverting, active, confirmed, reverted, failed, and uncertain. An **Automatic** badge on a card marks an action the policy ran by itself (see [below](#reading-an-action)). The view cannot be narrowed to those alone in the console; the [API](api-reference.md#actions) can (`automatic=true`). |
| **All actions** | Every state. |

You can also pick states one by one (Proposed, Awaiting approval, Outcome uncertain,
Active, Executing, Reverting, Confirmed, Reverted, Failed, Denied and Expired). The
other filters are evaluated by the engine over every action, page by page, never over
the rows loaded so far:

- **Action class** (such as **Isolate from network**).
- **Template**: the template of the run the action came from.
- **Target**: an exact target, such as a sensor ID or `mail:<id>`.
- **Only what I can decide**: the approval requests that you are allowed to approve or
  deny now, judged against the approver list each action was proposed with. A policy
  that names no approvers admits everyone. It lists approval requests only: combined
  with states that leave out **Awaiting approval**, nothing is listed.

**Order** is **Soonest deadline** or **Recently changed**. The views that list only
what waits for a person, and **Only what I can decide**, open on the soonest deadline,
so the request about to expire is on top. Views of what ran open on the latest change.
The engine always puts what needs a person first, then orders inside each state. Every
filter and the order are kept in the page's address, so a link reproduces your view.

### Reading an action

Each row shows the run it came from (template, state, outcome, urgency, case, with a
link to its evidence) and a **why** block, so you can decide without opening the run:

- **Started by**: what started the run, with links: the detection (opened in the
  Detections page), the Email Security message, or the case, plus the D&R rule, the
  entity, the question, the category and the severity.
- **Why it decided**: "The run was decided by rule `<id>`", followed by that rule's own
  sentence. When the rule read [checks](templates.md#checks-templates-other-templates-call),
  each is listed ("Through the check `<check>/<rule>` for item ..."). An AI-assisted
  rule and the AI review are named as such.
- **Not decided**: when no rule or AI decided the run (an AI recommendation, for
  example), the row says so and points to the run's evidence.
- When the engine shortened a field to fit the list, the row says "Part of this was
  shortened to fit the list" and points to the run for the full text.

The action card shows the class, the target, its state and mode, the deadline, the
lease time left, who decided, and its history. Every row appears once. Identical
proposals (same class, template, mode and parameters) are **grouped** where the first
appears, with **Select all N**; nothing is filtered out. An **Automatic** badge marks an
action the policy executed by itself, and **Expires soon** marks one in its last five
minutes (the shipped approval timeout is 15 minutes).

The deadline says what it means in each state:

| State | The card says |
|---|---|
| Awaiting approval, or a proposal held for a prerequisite | **Expires in 12:34 if nobody decides. Nothing runs.** A countdown follows. |
| Executing, reverting, outcome uncertain | **The engine checks it again at** a time. |
| Active | The lease countdown. |

### Buttons

| State | Buttons |
|---|---|
| Awaiting approval | **Approve**, **Deny** |
| Active | **Revert**, **Extend lease** (+1 h or +2 h), **Confirm** |
| Suggestion | **Dismiss** only (see below) |
| Outcome uncertain | None |

Every button asks for confirmation and takes an optional note recorded in the action's
history. The confirmation dialog repeats the why block. **Confirm** keeps an action in
place and stops its lease from reverting it.

A button is disabled unless you hold `investigation.set` and `insight.evt.get` **and**
the permission of the action's class (see [Permissions](permissions.md#permission-of-the-action-class)).
A **close** asks for the permission of what it closes: `investigation.set` alone for
a case, and `mailsec.set` as well for an email message. **Approve**, **Deny**, **Extend
lease** and **Confirm** also require being on the class's approver list when the
policy sets one, and a button you cannot use says so; **Revert** does not.

### Approve or deny several at once

Rows can be selected, and **Approve selected** and **Deny selected** decide them one
by one: the engine checks each action against the policy as if you had decided it on
its own, and the console reports every result ("Approved 2 of 3", with the reason for
each refusal in plain words). Refused rows stay selected. Two kinds of action are never
approved in bulk, and the confirmation says how many it leaves out:

- **An action that cannot be undone.** Decide it on its own card.
- **A suggestion.** Nobody can approve it.

The dialog lists the classes and how many targets each touches.

### Suggestions, held actions and uncertain actions

- **A suggestion** is an action whose class is in `suggest` mode, or whose run used a
  draft template (a draft is capped at `suggest`). It is never executed, so it has **no
  Approve button**, whoever you are and whatever you hold. **Deny** becomes **Dismiss**,
  which closes the suggestion; nothing runs either way. The card says **Suggestion
  only: nothing will run** and links to the **Policy** page. A proposal keeps the mode it
  was made with, so changing the policy afterwards does not unlock it: to execute the
  action, set the class to `approve` or `auto` in the policy and start a **new** run from
  an **active** template. The "only an approver named by the policy" wording appears only
  where the policy does name approvers.
- **An action held for a reason** lists why under **Policy notes**: it rests on an AI
  decision or on a check's verdict (so it has no registered authorization and waits for
  a person even in `auto`), it cannot be undone and the policy names no exact class for
  it, the approver lists have nobody in common, the source is off, or the engine could not
  read the policy. See [Policies](policies.md#autonomy-modes).
- **An uncertain action** has **no buttons**: the engine could not confirm whether the
  action took effect, and it settles it by itself. A late answer from the platform makes
  it active or failed. When none comes by the time the card shows, a reversible action is
  undone to be safe, and an irreversible one is marked failed and escalated to a person.
  There is nothing for you to press; check the target yourself. The card also shows
  what the engine knows about the effect (for example, that the platform accepted the
  request but never reported the change).
- **A class that cannot execute** (see [Action classes](policies.md#action-classes))
  can be proposed but fails when approved.
- **A tag** (`tag`, `tag.add`) holds no lease, so it goes straight from **Executing** to
  **Confirmed**, whether a rule ran it under `auto` or a person approved it. It has no
  **Extend lease** and no **Confirm**; **Revert** removes it. The card says how long it
  lasts, in words: **Tag lasts 7 days once applied**, and once applied, **Applied,
  removed automatically on `<date>`**, which is the time it was applied plus its `ttl`
  (what its template declares).

An error on a decision is translated: you are not on the approver list, or the action is
in suggest mode. Anything else shows the engine's message.

## Templates

The **Templates** tab lists the organization's `investigation_plan` records with
their status (Draft or Active), **kind**, version, the categories each applies to, and
description. A badge marks templates that appeared while you had the page open, for
example one an AI agent just saved. Filter by kind: an **alert** template starts runs,
a **check** is called by other templates (see
[Checks](templates.md#checks-templates-other-templates-call)).

A **check's page** shows its params, **Used by** (the live list of the templates that
call it) and a test with params. It has no **AI may decide** switch: the switch
belongs to the templates that call the check.
In the editor, a call of a check has a picker for the check, a form generated from its
params, and the `each` and `max_items` fields. **Delete** lists **Used by**, and
**Validate** and **Save** on a check show "Saving this breaks N templates" before the
write: the templates that call it, checked again against your edit. Nothing blocks the
save.

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
- Editing an active template warns that the change applies right away to the runs that start by themselves
  right away. Move it back to draft first to test safely.
- Saving needs `investigation_plan.get` and `investigation_plan.set`. If the record
  changed since you opened it, you are told to reload and apply your edit again.

### Compare with my draft

In the editor of a template (not of a check), **Compare this text with finished runs
(without saving)** asks "would this edit have decided differently?". Pick one finished
run by id, or the last N (1 to 10) finished runs of the template you are editing or
copying. The editor text is sent as an inline plan; nothing is saved and no query is
run. The result is a summary ("2 of 5 runs would have ended differently"), one line per
run (was *X*, would be *Y*, or same), a link to the run, and the full comparison under
**Details**. Each side of the comparison shows the checks behind a decision. A run
that cannot be compared (still executing, or a wrong id) is reported on its own line
and does not stop the others. When you edit the text after a comparison, the results
dim and a note says they describe the earlier text. Each run is its own `compare`
request, so N is capped at 10; see [Compare](api-reference.md#runs).

### Test on past alerts

On a template's page (or in the editor, to test unsaved text), **Test on past alerts**
runs the template's real read-only steps on alerts that already happened. It creates
no run, no case and no action; only the test result is kept, for 24 hours. You build a list of samples, at most 25 alerts in
total:

- **A detection**, by detection id;
- **A case**, by case id: its classification is the expected answer;
- **Last N of a category**: the newest N detections of that category, N from 1 to 25.

On a **check's** page the samples are **params** instead: the call's arguments and the
outcome you expect (escalated, closed, couldn't tell or conflict).

The result shows a progress bar, then the summary: **Decided by rules** (how many of
the alerts a rule decided), one line per rule (how many it decided, how many agree
and disagree with the analysts), **AI recommendation on the rest** (agree, disagree,
unclear), the unknowns, the cost per alert and the time. Below, **Results per alert**
gives each alert's outcome, the deciding rule or **AI recommends: ...**, **What was
missing**, the cost, the actions the template **would propose**, and two chips:
**Rule agrees with the case** or **Rule disagrees with the case**, and **AI agrees
with the case**, **AI disagrees with the case** or **AI unclear** (or **No closed
case**). These figures are for your information: nothing waits on them.

If steps were refused for lack of permission, a banner lists them: the test ran with
the permissions of whoever started it, so grant the permission of the product each of
those steps reads (for example `mailsec.get` for email steps) and test again. Until
then those steps stay unknown and the outcomes mean little. Results are kept for 24
hours. You need `investigation.set`, `investigation.get` and `insight.evt.get`: the
console starts the test with the first and follows it with the second.

### Make active, or back to draft

On the template's page:

- **What this template does** outlines the template in plain words: where it
  **Starts from**, the steps it gathers (with **Only if**, **Ask a person** and the AI
  steps marked), **Escalate when** and **Close when** rules (the **AI-assisted** ones
  marked), **Never close when**, the signals to explain, the **AI review**, the
  actions and when each fires, and the case severity.
- **AI may decide** sets what the AI may decide for this template: **Off: the AI only
  recommends** (the default), **May escalate** or **May close and escalate**. It
  writes `ai_may_decide.<template>` in the `default` policy record after a
  confirmation, says where the current value comes from (this template's entry, the
  `"*"` entry, or off by default), and lists any other policy record that allows less.
  The last test on past alerts is shown beside it, for information only. It needs
  `investigation_policy.get` to read and `investigation_policy.set` to change. See
  [What the AI may decide](policies.md#what-the-ai-may-decide).
- **Make active** asks for confirmation. When the engine still has a test of this
  template (kept for 24 hours), the dialog shows it for information (alerts run, how
  many the rules decided and how they agreed with closed cases). It shows no warning when
  there is no test: a test is not required, but look at it. **Make active** is disabled
  until the engine reports the template valid. Active templates "are picked by
  detections, rules and cases on their own, and can propose actions within your org
  policy."
- **Back to draft** stops detections and cases from picking the template. Runs already
  in progress are not affected.
- **Delete** removes the template from the organization and cannot be undone.
- **Last changed by** shows who changed the template last and when, and the same line
  is on a policy record in the editor.
- **View runs** opens the Runs tab filtered to this template.

Making a template active is done by a person signed in as a user, in the console or with a user login in the CLI. An API key cannot write an active
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

The **Policy** tab is the one page for the policy the engine applies. Policy records are
`investigation_policy` Hive records, edited here, with the Hive API, the CLI,
infrastructure-as-code or Git Sync. See [Policies and Autonomy](policies.md). The page
shows, from top to bottom:

- **Warnings.** A banner when the engine ignores part of the policy, with one sentence
  per warning (the codes are in [Troubleshooting](troubleshooting.md#policy-warnings)).
  A record that does not parse is shown in the error tone: the engine is enforcing the
  last good policy, or suggest-only, and what the page shows is what is enforced. The
  same banner appears in the launcher's policy panel and on the auto-investigation
  overview.
- **Policy records.** One row per `investigation_policy` record: its name, what it
  applies to (every run, or the runs or the targets its `match` selects), whether it
  is on, who **last changed** it and when, and what the engine **ignores** in it
  (retired fields, an empty approver list, a wildcard `auto` that does not automate
  irreversible actions, `automation_routes`). **Edit** opens that record in the editor;
  a new record is created by typing a name. Reading the table needs
  `investigation_policy.get`; saving a record needs `investigation_policy.set`. A record
  that matches a run can only narrow what `default` allows.
- **What the AI may decide, per template.** For each template, what the `default`
  record grants, which entry it comes from (the template's own, the `"*"` entry, or off
  by default) and the other records that allow less. Change a template's value with the
  **AI may decide** switch on its page. See
  [What the AI may decide](policies.md#what-the-ai-may-decide).
- **Effective policy.** What the organization's policy allows, record by record. Leave
  the lookup empty for the organization default, or enter a category, severity,
  priority and a template to see what applies to that alert (the template selects its
  run identity). It lists the records applied, the budgets, speculation by urgency,
  and each action class with its mode, lease, approvers and the record each value
  comes from. When no secret identity is configured it says that runs started by
  detections or cases are refused.
- **Automatic actions**: the pause switch, and links to the **Action log & undo** and
  to **Engine performance**.

The former separate **Action policies** page is now the records table and its editor on
this page.

### Pause automatic actions

**Pause automatic actions** saves the
[`autonomy-manual-pause` policy record](../7-administration/config-hive/investigation-policy.md#emergency-pause-and-resume),
which caps every action class at `approve`:

- **Nothing runs by itself.** An action the policy would have executed automatically
  waits in [Approvals](#approvals) for a person.
- **A person can still approve.** Approving works as usual, with the same permissions
  and approver lists. Investigations continue.
- **A class the policy already holds at `suggest` or `off` stays there.** The pause
  never raises a mode and never turns a suggestion into something a person can approve.

The switch shows **Paused: nothing runs by itself; a person can still approve** and who
paused it and when. Pausing and resuming each ask for confirmation and say what they do:
resuming lets actions in `auto` mode run by themselves again, in every run of the
organization. Resuming deletes the record. Changing the switch needs the Hive
permissions of that record (`investigation_policy.set` to pause,
`investigation_policy.del` to resume). The same switch is at the top of every run's
**Actions** tab and in the auto-investigation settings.

A pause that an earlier console saved (`mode: suggest`) still reads as paused, with a
note that it also refuses approvals; pause again to rewrite it. A pause record that is
present but disabled, or that someone edited, is shown as not in effect, with a button to
restore it.

## Auto-investigation

**Auto-investigation** has its own sections under Investigations: **Overview**,
**Automatic actions** and **Settings**. It is the switch that makes the engine
investigate a product's alerts by itself, with no rule to write. Turning a source on is
one step that installs or activates that product's template, creates the key it
investigates with and subscribes its detections: see
[the key that turning a source on creates](permissions.md#the-key-that-turning-a-source-on-creates).
Turning one on needs permission to change investigation policies.

### A source's mode

Each source (Email Security, Endpoint detections, Cloud and identity alerts; the page
marks the ones that are not available yet) has a mode:

| Mode | What the engine does |
|---|---|
| **Watch** | Investigates every alert and records what it found and what it would have done. It changes nothing, and your team works as before. A new source starts here. |
| **Suggest** | Investigates every alert and posts a recommendation on it. It changes nothing on its own. |
| **Automatic** | Investigates every alert and takes the actions your policy sets to `auto`. The policy, not the mode, decides what runs. |

The mode never grants anything: the [policy](policies.md) alone decides what the engine
may do, so the engine reads no history or score to move a source from one mode to the next: you change it in **Settings**. **Settings** also
holds the detection categories that feed each source (empty uses the product's default;
end a name with `*` to match a prefix), the spending limits (per day, per month, per
investigation and how many run at the same time) and the template each source runs
(the one the product's setup installed, unless you switch it). When a limit is reached,
the remaining alerts are skipped and your team handles them as usual; the overview says
how many.

### Setup, step by step

Turning a source on, or saving its settings, lists the steps the engine took, each
with its own status: **done**, **already in place, nothing changed**, **replaced, and the
old key was revoked** (the setup-owned key was rotated; the reason names what was added
and removed), **undone, because a later step failed**, or **failed**. The engine's reason
is shown under every step that has one. The steps are the template, the investigation
key, the detection intake and the settings. After a save, **What the last save did**
keeps the list, so a key rotation and its reason stay visible. A refusal carries its
reason code, translated; a code the console does not know is shown as sent. See
[Turning a source on: what to expect from setup](permissions.md#turning-a-source-on-what-to-expect-from-setup).

Two answers are not edit conflicts:

- **Setup is already running** for this organization (from another tab or person). It
  finishes within a few minutes; **Reload** then.
- **Someone else changed these settings** while you were editing. Nothing was saved;
  reload to see their changes, or save yours over theirs after a confirmation.

### Key readiness

**Key readiness**, on **Settings** and on the **Overview**, has one row per source that
is on: the key's reference (never the key), **Ready** or **Not ready**, the permissions it
lacks, the engine's hint on how to fix it, and the extra permissions it holds (for
information only). A key that is not ready also appears under **Needs you**. The check
runs with your own permissions. See [The readiness check](permissions.md#the-readiness-check).

### Overview

The overview shows, for today, 7 days or 30 days: the alerts the engine saw, the ones it
investigated, grouped into campaigns (each investigated once), skipped for budget,
skipped because the product's data was not complete within 24 hours, failed, in
progress and waiting for product data. It shows spending against the limits, **Needs
you** (a limit reached or near, failed investigations, keys that are not ready) and a
list of the alerts with what happened to each and why.

### Automatic actions

**Automatic actions** is the log of everything the engine did by itself. Each entry says
why, links to its investigation and can be undone, one at a time or up to 100 selected
at once. Undo asks whether the engine was wrong. **No, I just prefer it undone** saves
nothing about the engine. **Yes, the engine was wrong** is saved as a label on the run:
it changes nothing by itself, so to stop it from happening again, change the template's
rule or the policy mode.

The log is open to anyone with `investigation.get` and `insight.evt.get`. **Undo** needs
`investigation.set`. A reader sees slightly fewer entries than an administrator only on
older data: the engine hides the entries of legacy runs that kept their opinion hidden
(no current run does).

## Performance

The **Performance** tab aggregates runs over the last 24 hours, 7 days, 30 days or a
custom range, optionally for one template. It shows the **speed-up versus serial**,
where the gain comes from (steps running together versus stopping early), runs by
outcome, time to decision, cancelled work, cache hit rate, batched calls, speculation
efficiency, search events (billed and free), AI spend, analyst feedback (labels and corrections), the
operator latency table and the actions by class and state.

The speedup is only shown for runs that have a serial baseline of the same
investigation: start it with **Also run a serial baseline**. The page reads at most the
2,000 most recent runs of the range and says when it truncated. It needs
`investigation_policy.set` on top of the read permissions, like the
[stats](api-reference.md#stats) it is built from.
