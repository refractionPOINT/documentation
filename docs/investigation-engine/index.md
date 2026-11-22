# Investigation Engine

!!! info "Pre-release"
    The Investigation Engine is documented here ahead of general availability.
    Names, defaults and screens can still change before release, and the
    service is only reachable where it has been enabled for your organization.

The Investigation Engine investigates an alert for you. You hand it a detection,
a case, an entity or a question. It gathers what its plan template lists, every
step whose inputs are ready **in parallel**, stops as soon as one of the template's
rules decides, writes the result to a
[case](../5-integrations/extensions/limacharlie/cases.md), and proposes or takes
containment actions **only as far as your organization's policy allows**.

It is deterministic at its core. Templates decide with rules your team writes and can
read: "close when the binary is on our approved list and the file on the host is
signed", "escalate when a recipient clicked a link that lands on a password page".
The AI answers focused questions and, when no rule decides, reviews the evidence and
**recommends**. It decides alone only for the templates where your policy says so.
The engine, not the AI, decides what runs next, what can be skipped and when to stop.

!!! tip "Start here"
    New to the engine, or an AI agent setting it up? Follow the
    [Walkthrough](walkthrough.md): from an empty organization to a finished
    investigation, every step copy-pasteable.

## How to read these pages

1. [Walkthrough](walkthrough.md): set it up and use it, end to end.
2. [How to Think About Templates](how-to-think-about-templates.md): the method for
   writing a template, from the analyst's questions to rules you own.
3. [Concepts](concepts.md): steps, rules, outcomes, unknowns, runs, identity.
4. [Plan Templates](templates.md): the library and every section of a template,
   validation, testing, making a template active.
5. [Policies and Autonomy](policies.md), with the
   [policy record reference](../7-administration/config-hive/investigation-policy.md):
   what the engine may do on its own, and what the AI may decide.
6. [Automatic Starts](automation.md): D&R rules on detections and on new cases.
7. [Troubleshooting](troubleshooting.md): every refusal and error, and what to do.

Reference: [Permissions](permissions.md), [API Reference](api-reference.md),
[MCP Tools](mcp.md), [CLI](cli.md), [Console](console.md) and
[Build and Tune Templates with an AI Agent](build-templates-with-ai.md).

## What you get

| Capability | What it gives you |
|---|---|
| **Runs** | One investigation per alert, case, entity or question, ending with one [outcome](concepts.md#outcomes): closed or escalated by a rule, closed or escalated by the AI, the AI recommends, couldn't tell, or conflict. With it: the rule or the AI answer behind it, what was missing, each step's reason and finding, and the actions taken. |
| **Plan templates** | Reusable, versioned plans for a class of alerts, stored as Hive records in your organization: steps to gather, rules that decide, an optional AI review. Install the [default library](templates.md#the-default-library), edit it, write your own. |
| **Checks** | Logic several templates repeat, written once as a [check](templates.md#checks-templates-other-templates-call) (for example where a link lands) and called by each template, once or per element of a list. |
| **Test on past alerts** | Run a template, read-only, on real past detections and cases: which rule decided each alert, and whether it agreed with your analysts. |
| **Policies and autonomy** | Per action class: `off`, `suggest`, `approve` or `auto`, with leases, caps and approvers; per template, whether the AI may decide. The policy record is the only thing that decides what the engine may do. One Policy page lists the records, what the engine ignores in them and what the AI may decide per template, and a pause switch stops anything running by itself while a person can still approve. |
| **Approvals inbox** | Every action that waits for a person, across all runs, in one list: why each is there, the soonest deadline first, filters by template, target and what you may decide, and approve or deny several at once. A suggestion has no Approve button, and an action whose outcome is uncertain has none either. |
| **Auto-investigation** | Turn on a product (Email Security, for example) and the engine investigates its alerts by itself, starting in **Watch** mode where it changes nothing. One step installs the template, the key and the detection intake, and the console shows what each did. A log lists everything the engine did on its own, and each entry can be undone. |
| **Automatic starts** | A D&R rule starts a run with the [`start investigation`](../8-reference/response-actions.md#start-investigation) response action, on a detection or on a new case. |
| **Cases** | Each run writes its case: the outcome sentence, the evidence behind it, entities, telemetry, what stayed unknown, the open question, the actions. |
| **Performance stats** | What the engine did, how fast and at what cost, per template and action class. |
| **Waves** | For a one-off question, a batch of checks that run in parallel and answer compactly, with no rules and no outcome. |

## Rules that never bend

- **Unknown is never false.** A step that failed, timed out, was not allowed, was
  skipped or whose data is incomplete is *unknown*. It never reads as "nothing found",
  and "nothing found" never closes an alert.
- **Every search stays inside the free time range.** No search window may start
  earlier than 30 days before now.
- **A run can never do more than its identity can.** Every read and every action
  uses the permissions of the identity the run executes as.
- **A draft template never acts on its own.** Drafts run only when a person starts
  them, with every action capped at `suggest`. A person makes a template
  active.
- **Nothing is installed for you.** An organization's templates are exactly its
  `investigation_plan` records, and no D&R rule is added for you.
- **The AI recommends unless you say otherwise.** It decides alone only where the
  `default` policy's `ai_may_decide` allows it: a template's own entry, or `"*"` for
  every template. An `act` entry that fires on an AI decision always waits for a
  person. The case close after `closed_by_ai` follows the `close.false_positive`
  mode, so under `auto` it runs by itself.
- **Nothing is learned behind your back.** Templates decide exactly as their rules
  say, and no history, score or label changes what the engine may do.
