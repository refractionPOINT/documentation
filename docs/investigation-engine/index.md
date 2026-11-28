# Investigation Engine

!!! warning "Experimental"
    The Investigation Engine is experimental. It is reachable only where it has been
    enabled for your organization, and names, defaults and screens can still change.
    Each page says what is not available yet.

The Investigation Engine investigates an alert, decides what it is, and acts on its
own when you have written that it may. A person reviews afterwards.

You describe one kind of alert in a **template**: what to fetch, the rules that decide,
and what to do about each decision. When a detection fires, a D&R rule starts a run. The
engine fetches every step whose inputs are ready **in parallel**, stops as soon as a rule
decides, writes a [case](../5-integrations/extensions/limacharlie/cases.md), and takes the
actions the template lists: isolate the host for one hour, tag it, close the case as a
false positive. Each action says whether it acts on its own or waits for a person, how long
it stays in effect and what happens when that time is up.

The template is the authority. No organization policy sits above it and turns its actions
on, off or into suggestions. Three things still apply to every template of an
organization, because they belong to no single template: an emergency **pause**, a
**circuit breaker** on automatic containments, and the platform permissions of the key the
engine runs as.

!!! tip "Start here"
    Follow the [Walkthrough](walkthrough.md): from an empty organization to a host isolated
    by itself for one minute, released, and undone, then the same with an approval.

## Where it sits

| You want | Use |
|---|---|
| Decide on what the event in hand carries | A [D&R rule](../3-detection-response/index.md). A false-positive rule drops what never needs a look. |
| Decide on what you have to go and fetch (who started the process, what else ran on the host, whether the hash is on your list) | An Investigation Engine template. A D&R rule starts it with [`start investigation`](../8-reference/response-actions.md#start-investigation). |
| Run your own Python, as a read or as an action | A [Playbook](../5-integrations/extensions/limacharlie/playbook.md), called from a template as a step or an action. See [Custom Code and AI Agents](custom-code.md). |
| A judgement that needs more than one question | An [AI agent](../9-ai-sessions/index.md), called from a template as a step, or handed a run the template could not decide. |
| A one-off question, no template | A [wave](concepts.md#waves-and-fact-packs). |

A template that fetches nothing is a D&R rule in the wrong place, and validation says so
(`decides_on_trigger_only`). The engine has no loops and no second detection language: a
template is steps, rules and actions.

## How to read these pages

1. [Walkthrough](walkthrough.md): set it up and see it act, end to end.
2. [Concepts](concepts.md): runs, steps, unknowns, outcomes, actions, identity, cost.
3. [Plan Templates](templates.md): every section of a template, validation, testing,
   draft and active.
4. [Actions, Approvals and Undo](actions.md): `approval`, leases, `on_lease_end`, undo,
   bulk undo, the audit log.
5. [Settings](settings.md): the one settings record (pause, circuit breaker, identity,
   budgets, limits, case, notifications).
6. [The Run Queue](run-queue.md): coalescing, fairness, the parallel limit, the hourly
   cap, the queue display and Flush.
7. [Custom Code and AI Agents](custom-code.md): Playbook steps and actions, extension
   actions, AI agent steps and hand-off.
8. [Automatic Starts](automation.md): D&R rules on a detection and on a new case.
9. [How to Think About Templates](how-to-think-about-templates.md) and
   [Build Templates with an AI Agent](build-templates-with-ai.md).
10. [Troubleshooting](troubleshooting.md).

Reference: [Permissions](permissions.md), [API Reference](api-reference.md),
[Command Line Interface](cli.md), [MCP Tools](mcp.md), [Console](console.md), and the
[settings record](../7-administration/config-hive/investigation-policy.md).

## Rules that never bend

- **The template says what happens.** An action the template does not list is never
  taken. Every `act` entry must say `approval` (`none`, `required` or a condition), so no
  action acts on its own by omission and a reader always sees which ones do.
- **A draft never acts.** A draft template only suggests: its actions are recorded as
  `suggested` and never executed. Making a template active is the permission to act. An AI
  agent saves drafts; a person promotes them.
- **Unknown is never false.** A step that failed, timed out, was not allowed or was
  skipped is *unknown*. It never reads as "nothing found", and "nothing found" on
  incomplete data never closes an alert.
- **A run can never do more than its key.** Every read and every action uses the
  permissions of the identity the run executes as.
- **Every search stays inside the free time range.** No search window starts earlier
  than 30 days before now.
- **A person's decision on a case wins.** An automatic close never overrides a case a
  person already decided.
- **Every action keeps its record.** What acted, on what, why, for how long, who
  approved or undid it, and how to undo it.
- **Nothing is installed or learned for you.** An organization's templates are exactly
  its `investigation_plan` records, no D&R rule is added for you, and no history or score
  changes what a template does.

## Not available yet

- The engine runs only where it has been enabled; it is not generally available.
- Billing per run is not on. This documentation states no price.
- The `limacharlie investigate queue` and `limacharlie investigate answer` commands are in
  the CLI's source but not in the latest release on PyPI (5.14.0). Until a release
  includes them, use the [API routes](api-reference.md) or the [MCP tools](mcp.md).
- There is no CLI command and no MCP tool for undo, extend or confirm. Use the API or the
  console.
- An AI agent can be a step or a hand-off, not an action.
