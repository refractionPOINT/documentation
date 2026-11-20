# Investigation Engine

!!! info "Pre-release"
    The Investigation Engine is documented here ahead of general availability.
    Names, defaults and screens can still change before release, and the
    service is only reachable where it has been enabled for your organization.

The Investigation Engine investigates an alert for you. You hand it a detection,
a case, an entity or a question. It gathers the facts its plan template lists, every
fact whose inputs are ready **in parallel**, stops as soon as the verdict is
settled, writes the result to a [case](../5-integrations/extensions/limacharlie/cases.md),
and proposes or takes containment actions **only as far as your organization's
policy allows**.

It is deterministic at its core. A language model can judge an ambiguous fact in
a small, bounded call, but it does not drive each step. The engine, not the model,
decides what runs next, what can be skipped and when to stop.

!!! tip "Start here"
    New to the engine, or an AI agent setting it up? Follow the
    [Walkthrough](walkthrough.md): from an empty organization to a finished
    investigation, every step copy-pasteable.

## How to read these pages

1. [Walkthrough](walkthrough.md): set it up and use it, end to end.
2. [Concepts](concepts.md): facts, proofs, unknowns, runs, identity.
3. [Plan Templates](templates.md): the library, writing, testing, publishing.
4. [Policies and Autonomy](policies.md), with the
   [policy record reference](../7-administration/config-hive/investigation-policy.md):
   what the engine may do on its own.
5. [Automatic Starts](automation.md): D&R rules on detections and on new cases.
6. [Troubleshooting](troubleshooting.md): every refusal and error, and what to do.

Reference: [Permissions](permissions.md), [API Reference](api-reference.md),
[MCP Tools](mcp.md), [CLI](cli.md), [Console](console.md) and
[Build and Tune Templates with an AI Agent](build-templates-with-ai.md).

## What you get

| Capability | What it gives you |
|---|---|
| **Runs** | One investigation per alert, case, entity or question: a verdict (`true_positive`, `false_positive` or `inconclusive`), the proof behind it, an evidence graph, a step timeline and the actions taken. |
| **Plan templates** | Reusable, versioned plans for a class of alerts, stored as Hive records in your organization. Install the [default library](templates.md#the-default-library), edit it, write your own. |
| **Test on past alerts** | Run a template, read-only, on real past detections and cases before it ever acts. |
| **Policies and autonomy** | Per action class: `off`, `suggest`, `approve` or `auto`, with confidence bars, leases, caps and approvers. The policy record is the only thing that decides what the engine may do. |
| **Approvals inbox** | Every action that waits for a person, across all runs, in one list. |
| **Automatic starts** | A D&R rule starts a run with the [`start investigation`](../8-reference/response-actions.md#start-investigation) response action, on a detection or on a new case. |
| **Cases** | Each run writes its case: summary, proof, entities, telemetry, unknowns, actions. |
| **Performance stats** | What the engine did, how fast and at what cost, per template and action class. |
| **Waves** | For a one-off question, a batch of checks that run in parallel and answer compactly, with no plan and no verdict. |

## Rules that never bend

- **Unknown is never false.** A step that failed, timed out, was not allowed or
  whose data is incomplete is *unknown*. It never reads as "nothing found".
- **Every search stays inside the free time range.** No search window may start
  earlier than 30 days before now.
- **A run can never do more than its identity can.** Every read and every action
  uses the permissions of the identity the run executes as.
- **A draft template never acts on its own.** Drafts run only when a person starts
  them, with every action capped at `suggest`. A person promotes a template to
  `active`.
- **Nothing is installed for you.** An organization's templates are exactly its
  `investigation_plan` records, and no D&R rule is added for you.
- **Nothing is learned behind your back.** Templates weigh evidence exactly as their
  author wrote, and no history, score or label changes what the engine may do.
