# How to Think About Templates

A template answers the questions a good analyst already asks about one kind of
alert. When do we close it? When do we escalate it? What do we have to look at to
know? This page is the method for writing one, in the order that works. The field
reference is in [Plan Templates](templates.md).

A template has four parts:

| Part | Key | What it is |
|---|---|---|
| Gather | `gather` | The questions: steps that fetch answers. Steps run in parallel unless one reads another's answer. |
| Rules | `rules` | The decisions: "escalate when ..." and "close when ...", each with an id and a sentence for the case. Rules are the only way the engine decides on its own by default. |
| AI review | `ai_review` | Optional. A second opinion when no rule decided. It recommends; a person decides, unless the policy lets the AI decide for this template. |
| Act and case | `act`, `case` | What to propose when a rule decides, and how the case reads. |

There is no probability, prior, weight or threshold anywhere. A run ends with an
[outcome](concepts.md#outcomes) a person can read, and the rule or the AI answer
behind it.

## 1. Write down the analyst's questions

Pick one alert type. Before you write any YAML, write the questions a good analyst
checks before closing it, and the findings that make them escalate. For a remote
administration tool that started on a host:

- Is the binary on our approved remote-admin tools list?
- Is it on our banned software list?
- Is the file on the host really the approved one, and is it signed?
- If it is not approved, is it set to start on its own?

Each question becomes one step under `gather`.

## 2. Write the deciding rules first, cheapest first

Write each rule as a complete sentence before you write it as an expression:
"close when the binary is approved and the file on the host is that file, signed".
Then translate it:

```yaml
rules:
  escalate:
    - id: banned_tool
      when: 'banned.found'
      say: "The binary {alert__trigger.hash} is on our banned software list."
  close:
    - id: approved_and_signed
      when: ['approved.found', 'file_on_host.matches', 'file_on_host.verified']   # a list means "all of"
      say: "The binary is on our approved remote-admin tools list, and the file on the host is that file, signed and verified."
```

- **A close rule needs positive benign evidence.** "Nothing was found" never closes
  anything. The engine enforces it: a missing, failed or partial answer never makes
  a rule true, and a close rule only decides on complete answers. See
  [Unknown is never false](concepts.md#unknown-is-never-false).
- **An escalate rule decides the moment it holds**, and the engine stops gathering
  and cancels what can no longer matter (the outcome, or an action that can still
  fire).
- **Which rule decides.** The escalate rule that holds first decides, and the
  decision never moves: a close rule that holds later is only listed in
  `verdict.contradicted_by` and noted in the case. Other escalate rules that have `act` entries keep counting:
  one that also holds is listed in `verdict.also_held` and fires its own `act`
  entries. On the close side, the first deterministic close rule in order that holds
  decides, then the first AI-assisted one.
  Give each rule the actions it alone justifies.
- The `say` sentence is what the case leads with. `{step.path}` puts a value in.

Start with the rules that read cheap, exact answers. A Lookup read costs almost
nothing; a live read of the host takes seconds; an AI question costs tokens.

## 3. Use your own lists

The most reliable rules read your organization's own
[Lookups](../7-administration/config-hive/lookups.md):
approved software, banned hashes, partner domains, approved admin scripts. They are
exact, cheap, and you own them. The `lookup.get` step reads one:

```yaml
gather:
  approved:
    why: "Is this binary on our approved remote-admin tools list?"
    op: lookup.get
    args: {name: approved-remote-tools, keys: ['$alert__trigger.hash']}
```

A key the Lookup does not list is `found: false`, and that answer is complete. A
Lookup that does not exist is unknown (`not_found`), never "not listed". The run's
identity needs `lookup.get`.

## 4. Gather only what a rule or the review reads

Add a step only when a rule, a signal explanation, the AI review or another step
reads its answer. A step nothing reads is the warning `unused_step`: it only costs.

- **Chain** a step to an earlier answer when it needs one: `'$alert__trigger.sid'`
  makes the step wait for `alert`. Steps that read nothing of each other start at
  once, in parallel.
- **Add `only_if:`** when a step is worth its cost only in some cases: a live sensor
  read, a detonation, a search across every recipient. The step waits for what its
  condition reads, runs when it is true, and is skipped when it is false. A skipped
  step reads as unknown, so a condition can only ever cost you a decision, never make
  one.
- **Add `ask:`** on a step whose missing answer a person can fill in. When the step
  stays unknown, the case asks that question.
- **Add `why:`** when the operator's default sentence does not say what you are
  asking. Every step tells the person reading the run why it ran, what it found and
  which rule used it.

```yaml
  file_on_host:
    why: "Is the file on the host the approved one, and is it signed?"
    ask: "Can someone check the file on this host? The sensor could not be read."
    op: sensor.read.file_hash
    args: {sid: '$alert__trigger.sid', path: '$alert__trigger.file_path', hash: '$alert__trigger.hash'}
    only_if: 'approved.found'      # only worth a live read when the binary is approved
```

Here is the whole template. It never asks the AI anything: the same data always
gives the same answer, and it costs a few Lookup reads and at most one live read.

<!-- validate: template -->
```yaml
description: "Remote admin tool started on a host: our own lists and the file on the host decide."
version: 1
status: draft
applies_to:
  detect_cat: ['remote-admin-tool']
starts_from: detection
gather:
  alert:
    use: detection_context          # a tested bundle: the detection, the host's recent alerts...
    args: {detection_id: $detection_id}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$alert__trigger.hash']}
  approved:
    why: "Is this binary on our approved remote-admin tools list?"
    op: lookup.get
    args: {name: approved-remote-tools, keys: ['$alert__trigger.hash']}
  file_on_host:
    why: "Is the file on the host the approved one, and is it signed?"
    ask: "Can someone check the file on this host? The sensor could not be read."
    op: sensor.read.file_hash
    args: {sid: '$alert__trigger.sid', path: '$alert__trigger.file_path', hash: '$alert__trigger.hash'}
    only_if: 'approved.found'
  starts_on_its_own:
    op: sensor.read.autoruns
    args: {sid: '$alert__trigger.sid', hash: '$alert__trigger.hash'}
    only_if: 'not approved.found'
rules:
  escalate:
    - id: banned_tool
      when: 'banned.found'
      say: "The binary {alert__trigger.hash} is on our banned software list."
    - id: unapproved_and_persisted
      when: ['approved.found == false', 'starts_on_its_own.found']
      say: "An unapproved remote-admin tool is set to start on its own."
  close:
    - id: approved_and_signed
      when: ['approved.found', 'file_on_host.matches', 'file_on_host.verified']
      say: "The binary is on our approved remote-admin tools list, and the file on the host is that file, signed and verified."
act:
  - {class: contain.network, target: '$alert__trigger.sid', on_rules: [banned_tool, unapproved_and_persisted]}
case:
  mode: create
  severity: {escalated_by_rule: high, closed_by_rule: low, default: medium}
```

When neither list has the binary and it does not start on its own, no rule holds and
the run ends `couldnt_tell`, listing what it could not establish. That is the right
answer: the template does not know enough to decide, and it says so.

## 5. Add the AI review only for what rules cannot decide

Some alerts need judgement no list can give: a command line nobody has seen, a
message whose wording matters. Add one `ai_review` for those. It runs only when no
rule decided and nothing relevant is left to gather. Say what it must judge, and
what it must have seen before it may answer benign:

```yaml
ai_review:
  question: "Is this process activity malicious? Say what in the evidence shows it."
  sees: [alert__trigger, lineage, host__card, spread__prevalence]   # the steps it reads
  needs: [alert__trigger, lineage]                                  # it may not answer benign without these
```

The review **recommends**: the outcome is `ai_recommends_benign` or
`ai_recommends_malicious`, nothing is acted on, and a person decides with one click
(see [What "AI recommends" means](walkthrough.md#9-what-ai-recommends-means)). Its
self-rated confidence is shown, labelled "self-rated", and never used.

A narrower tool is the `ask_ai` step: one focused question whose answer rules can
read (`cmd.label == "yes"`). A rule that reads an `ask_ai` answer, directly or
through another step, is **AI-assisted**: it also only recommends unless the policy
lets the AI decide. `validate_plan` lists those rules in `ai_rules`.

Do not ask the AI what an exact read answers. "Is this hash on our banned list?" is
a Lookup read, not an AI question.

## 6. Test on past alerts

Run the template, read-only, on 10 to 25 past alerts of the kind it covers, including
ones analysts closed as true positive and as false positive
(see [Test on past alerts](templates.md#test-on-past-alerts)). Look at three things:

1. **How many alerts the rules decided** (`decided_by_rules`). Few means the rules
   miss the fact that decides.
2. **How often each rule agreed with the analysts** (`rules.<id>.agree` and
   `disagree`). A rule that disagrees is too eager: read the alerts it decided and
   tighten its condition.
3. **How often the AI recommendation agreed on the rest** (`ai.agree`,
   `ai.disagree`, `ai.unclear`).

Read every disagreement. The numbers are for you: nothing at run time reads them,
and nothing waits for them.

## 7. Promote

A person makes the template active (**Make active** on the template's page). Its
rules now act within your [policy](policies.md)'s modes: with every class in
`suggest`, the engine proposes and never executes.

Separately, when the AI's record on your past alerts is good enough for you, turn
on **AI may decide** for this template: `escalate`, or `close_and_escalate`. It is
off by default. See [What the AI may decide](policies.md#what-the-ai-may-decide).
Testing is not a gate: you decide when, and you can switch it on for many tenants
at once.

## 8. Turn repeated decisions into rules

Watch what people do with the runs:

- **People keep closing the same AI-recommended alert for the same reason.** Put that
  reason in a Lookup, or write the rule. The console's **Add to list and close** does
  the first for you: the next identical alert closes by your rule, with no AI call.
- **"Couldn't tell" keeps naming the same missing step.** A step, an operator
  permission or an identity permission is missing. The `reason` on the missing step
  says which (see [Troubleshooting](troubleshooting.md#a-run-finished-but-the-outcome-means-little)).
- **A rule keeps disagreeing with analysts.** Tighten it, or move it to the AI
  review's evidence instead of letting it decide.

Over time, more alerts close and escalate by rules your team wrote and can read, and
fewer need the AI or a person.

## Checklist

- [ ] Each close rule rests on positive, complete evidence, never on "nothing found".
- [ ] The cheapest rules come first, and each escalate rule carries the actions it alone justifies.
- [ ] Every step is read by a rule, the review, an `act` entry or another step, or
      is `always: true`.
- [ ] Expensive steps have an `only_if`.
- [ ] Steps a person could answer have an `ask`.
- [ ] `validate_plan` has no errors and no warnings you cannot explain.
- [ ] The test on past alerts shows the rules agreeing with analysts.
- [ ] The template is saved as a draft; a person promotes it.
