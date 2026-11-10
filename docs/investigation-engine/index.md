# Investigation Engine

!!! info "Pre-release"
    The Investigation Engine is documented here ahead of general availability.
    Names, defaults and screens can still change before release, and the
    service is only reachable in datacenters where it has been enabled for your
    organization.

The Investigation Engine investigates an alert for you. You hand it a detection,
a case, an entity or a question. It works out which facts it needs, gathers every
fact whose inputs are ready **in parallel**, stops as soon as the verdict is
settled, writes the result to a [case](../5-integrations/extensions/limacharlie/cases.md),
and proposes or takes containment actions **only as far as your organization's
policy allows**.

It is deterministic at its core. A language model can judge an ambiguous fact in
a small, bounded call, but it does not drive each step. The engine, not the model,
decides what runs next, what can be skipped and when to stop.

!!! tip "In one sentence"
    An analyst writes down once how to investigate a kind of alert (a *plan
    template*); the engine then runs that plan on every matching alert, in
    parallel, with a verdict, the proof behind it and a case, and containment
    stays under the control of an org-wide autonomy policy.

## What you get

| Capability | What it gives you |
|---|---|
| **Runs** | One investigation per alert, case, entity or question: a verdict (`true_positive`, `false_positive` or `inconclusive`), the proof or evidence behind it, an evidence graph, a step timeline and the actions taken. See [Concepts](concepts.md). |
| **Plan templates** | Reusable, versioned plans for a class of alerts, stored as Hive records in your organization. You install the [default library](templates.md#the-default-library), edit it and write your own. |
| **Test on past alerts** | Run a draft template, read-only, on real past detections and cases before it ever acts. See [Test on past alerts](templates.md#test-on-past-alerts). |
| **Policies and autonomy** | Per action class: `off`, `suggest`, `approve` or `auto`, with confidence bars, leases, caps, approvers and a global pause switch. See [Policies and Autonomy](policies.md). |
| **Approvals inbox** | Every action that waits for a person, across all runs, in one list. |
| **Automatic starts** | A D&R rule can start a run with the [`start investigation`](automation.md#dr-rules-start-investigation) response action, and new cases can start one with the [case trigger](automation.md#the-case-trigger). |
| **Cases** | The engine writes the case for each run: summary, proof, entities, telemetry, unknowns, actions. People's edits to those cases are recorded as feedback. |
| **Waves** | For a one-off question, send a batch of questions that run in parallel and read compact answers, with no plan and no verdict. See [Waves and fact packs](concepts.md#waves-and-fact-packs). |
| **Console, API, MCP, CLI** | The same service from every surface: [console](console.md), [API](api-reference.md), [MCP tools](mcp.md) and the [CLI](cli.md). |

## Rules that never bend

- **Unknown is never false.** A step that failed, timed out, was not allowed or
  whose data is incomplete is *unknown*. It never reads as "nothing found". See
  [Unknown, absent and incomplete](concepts.md#unknown-absent-and-incomplete).
- **Every search stays inside the free time range.** No search window may start
  earlier than 30 days before now.
- **A run can never do more than its identity can.** Every read and every action
  uses the permissions of the identity the run executes as.
- **A draft template never acts on its own.** Drafts run only when a person starts
  them, with every action capped at `suggest`. A person promotes a template to
  `active`.
- **Nothing is installed for you.** An organization's templates are exactly its
  `investigation_plan` Hive records. The default library is content you choose to
  install.

## Where to go next

| I want to... | Read |
|---|---|
| Understand the vocabulary: facts, proofs, unknowns, runs | [Concepts](concepts.md) |
| Use the console | [Console](console.md) |
| Understand templates, install the defaults, test on past alerts | [Plan Templates](templates.md) |
| Let an AI agent write and test a template | [Build and Tune Templates with an AI Agent](build-templates-with-ai.md) |
| Decide what the engine may do on its own | [Policies and Autonomy](policies.md) |
| Start runs from D&R rules or new cases | [Automatic Starts](automation.md) |
| Give people and keys the right access | [Permissions](permissions.md) |
| Call it from code | [API Reference](api-reference.md), [MCP Tools](mcp.md), [CLI](cli.md) |
