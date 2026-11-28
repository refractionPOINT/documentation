# Plan Templates

A **template** tells the Investigation Engine how to investigate one kind of alert. You
write:

1. **what to gather** (`gather`): steps, each one operator call, one fact pack, one check,
   one Playbook or one AI agent, that can read each other's answers;
2. **the rules that decide** (`rules`): `escalate` and `close` rules over what was gathered,
   each with an id and a sentence for the case;
3. optionally **AI**: focused `ask_ai` questions a rule reads, and one `ai_review`, the
   fallback when no rule decides;
4. **what to do about it** (`act`) and **how the case reads** (`case`).

The engine runs every ready step in parallel, stops gathering as soon as a rule decides,
and cancels the steps that can no longer change the outcome. You write the template; you do
not write the scheduling. There is no probability, weight or threshold: a run ends with an
[outcome](concepts.md#outcomes) a person can read, and the rule (or the AI) behind it.

## Where templates live

A template is a Hive record in the `investigation_plan` hive; the record name is the
template name. Use lowercase letters, digits, `-` and `_`, starting with a letter or digit,
at most 64 characters: that is what the CLI and the MCP save tools write, and it fits a D&R
rule's `template` parameter. There is no `name:` key in the YAML. An organization's templates are exactly its records: the engine adds
none. Manage them with `limacharlie investigate templates ...`, the console, the Hive API
or [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md#investigation-engine-records).

## The default library

The engine ships a library you can install and edit. It is installed as **drafts**, and
every action in it asks a person (`approval: required`). Change that in your copy, entry
by entry, once you have read what the template does.

| Template | Applies to | Starts from | Actions |
|---|---|---|---|
| `endpoint-detection` | any detection on a sensor (`detect_cat: ['*']`) | detection | `contain.network` (lease 2h, release), `tag.add`, close |
| `suspicious-process` | `encoded-powershell`, `lolbin-*`, `suspicious-process`, `rare-process` | detection | `contain.network` (lease 2h, release), `tag.add`, close |
| `mailsec-message` | `mailsec-ai-triage` | message | `contain.email` (lease 2h, release), close |
| `phishing-campaign` | `mailsec-ai-triage` | message | `contain.email`, `contain.network` (lease 2h, release), close |
| `identity-sign-in` | `identity-suspicious-sign-in` | none | close |
| `saas-admin-action` | `saas-risky-admin-action` | none | close |
| `cloud-exposure-finding` | `cloud-exposure-finding` | none | close |
| `code-finding` | `code-security-finding` | none | close |
| `appcontrol` | the Application Control policy categories | detection | close |
| `payload-reached-landing` | a check (`kind: check`) the email templates call | | |

```bash
limacharlie investigate kit --section library --oid "$OID"      # read them
limacharlie investigate templates install-defaults --oid "$OID" # install as drafts
```

`install-defaults` never overwrites a record silently: an existing one is skipped with its
installed and library versions unless you pass `--overwrite`.

## A template

```yaml
# investigation_plan/rare-process
status: draft
version: 1
description: "Triage a rare-process detection: a banned binary escalates and isolates the host; a command the AI judges malicious on a host that keeps alerting escalates when the template lets the AI decide; otherwise one AI review recommends."
applies_to:
  detect_cat: ['rare-process']
starts_from: detection
ai_may_decide: escalate
gather:
  ctx:
    use: detection_context
    args: {detection_id: $detection_id}
  host:
    use: host_context
    args: {sid: '$ctx__trigger.sid'}
  spread:
    use: hash_spread
    args: {hash: '$ctx__trigger.hash'}
  sensor:
    why: "Is this host a server?"
    op: sensor.get
    args: {sid: '$ctx__trigger.sid'}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$ctx__trigger.hash']}
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [ctx__trigger]
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary is on our banned software list."
    - id: judged_malicious_on_noisy_host
      when: ['cmd.label == "yes"', 'ctx__host_alerts.count >= 3']
      say: "The command was judged malicious on a host that raised {ctx__host_alerts.count} detections in the last week."
ai_review:
  question: "Is this process activity malicious? Judge the command, the host and how common the binary is; say what in the evidence shows it."
  sees: [ctx__trigger, host__card, spread__prevalence]
  needs: [ctx__trigger]
act:
  - do: contain.network
    target: '$ctx__trigger.sid'
    on_rules: [banned_binary, judged_malicious_on_noisy_host]
    approval: {when: '"server" in sensor.tags'}
    lease: 2h
    on_lease_end: release
  - do: tag.add
    target: '$ctx__trigger.sid'
    attrs: {tag: 'ie:malicious-process', ttl: 86400}
    on_rules: [banned_binary]
    approval: none
case:
  mode: create
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, default: medium}
```

Read it this way: `ctx` answers first; `host`, `spread`, `banned` and the AI question wait
for the fields of `ctx__trigger` they read, then run in parallel. A banned binary escalates
by rule: the host is isolated on its own for two hours, unless it is tagged `server`, in
which case a person approves first; it is also tagged for a day. The second rule reads the
AI's answer, so it is AI-assisted: `ai_may_decide: escalate` lets it escalate. There is no
close rule: a binary seen on many hosts is never what closes an alert, so only the review
reads the prevalence, and it recommends.

Top-level keys, exactly: `description`, `version`, `status`, `kind`, `applies_to`,
`starts_from`, `ai_may_decide`, `coalesce`, `deadline`, `scope`, `trust`, `gather`, `rules`,
`explain_signals`, `ai_review`, `act`, `hand_off`, `case` (and `params` for a check).
Unknown keys are errors: a typo is never silently ignored. A template in the engine's
earlier formats (`facts`, `proofs`, `evidence`, `prior`, `respond`, `report`, ...) is
refused with `legacy_template_format`.

| Key | Meaning |
|---|---|
| `status` | `draft` (the default) or `active`. See [Draft and active](#draft-and-active). |
| `kind` | `alert` (the default) or `check`. See [Checks](#checks-templates-other-templates-call). |
| `applies_to` | Which detections pick this template when a start names none. See [How templates are chosen](#how-templates-are-chosen). |
| `starts_from` | Which ids the run has. See below. |
| `ai_may_decide` | `off` (default), `escalate` or `close_and_escalate`. See [The AI](#the-ai). |
| `coalesce` | `sensor` (default: alerts on one sensor join the open run) or `off` (one run per alert). See [The Run Queue](run-queue.md#coalescing). |
| `deadline` | Caps the run's wall time (`10m`, `2h`); it never loosens the settings' budget. |
| `scope` | `{from: [step ids]}`: steps that run only once a rule or the AI escalated (who else, what else). |
| `trust` | Values and lookups your organization maintains as trusted (`{lookups: [...], values: [...]}`). A match skips active analysis of an initial target; it never makes anything benign. |
| `hand_off` | Hand a run that could not decide to an AI agent. See [Custom Code](custom-code.md#hand-off-to-an-ai-agent). |

## Where a run starts: `starts_from`

A run gets very little from what started it: the id of the thing it was started on, plus
`alert_time`. `starts_from` says which ids the template reads as `$name`:

| `starts_from` | Inputs |
|---|---|
| `detection` | `detection_id` |
| `message` | `msg_uuid`, `fired_signals`, `detection_id` |
| `case` | `case_id`, `detection_id` |
| `none` (default) | none |

**Start from the id and derive everything else with steps.** `detection.get` of
`$detection_id` gives the category, sensor, hash, command line and time.

Any other value a caller passes (a D&R rule's `inputs`, a console field) is an **optional
input**, read as `$?name` in a step's `args` only, and null when not given. Rules, conditions
and `act` entries never read `$?name`: a caller's value never decides an outcome and never
chooses what is acted on (`bad_reference`). To prefer a caller's value and fall back to the
derived one, use `plan.pick`: `{op: plan.pick, args: {candidates: ['$?msg_uuid', '$trigger.msg_uuid']}}`.

A run a D&R rule started answers `detection.get` of its own detection, and `event.get` of
the event the detection was raised on, from the document the rule handed over, with no read
and no wait (the step says `source: trigger`). Other reads go to storage.

## Gather

A step is one of:

| Form | What it is |
|---|---|
| `{op: <operator>, args: {...}}` | One operator call. `limacharlie investigate operators` lists them with their `args` and `output`. |
| `{use: <pack>, args: {...}}` | A fact pack: a tested bundle of steps, named `<id>__<step>` (`ctx__trigger`). `limacharlie investigate packs --brief` lists them. |
| `{use: template:<check>, args: {...}}` | A [check](#checks-templates-other-templates-call). |
| `{op: playbook, args: {name, data, returns}}` | A read-only Playbook. See [Custom Code](custom-code.md#playbook-steps). |
| `{op: ai_agent, args: {agent, prompt, sees, returns, budget}}` | A read-only AI agent. See [Custom Code](custom-code.md#ai-agent-steps). |

A step also takes:

- `why`: the question it answers, for the person reading the run.
- `ask`: the question for a person when the step stays unknown (the case's open question).
- `only_if: '<expression>'`: run it only when the condition is true. A skipped step reads as
  unknown. The condition can only cost a decision, never make one.
- `always: true`: gather it for the case even after a rule decided.
- `deadline: 40s` (op steps, 1s to 5m): how long the call may take. A call that does not
  answer in time is `unknown(timeout)`; a read that can stop early answers with what it read,
  incomplete.
- `record:` what the step puts in the case. See [Case](#case).

**References.** `$name` is a step or an input; `$name.path.to.field` reads into it;
`$list[0].field` indexes a list. A step that reads another waits for it; steps with no
dependency start at once. References are checked against the operator's output schema:
`$sender_history.prior_mesages_30d` is `unknown_field` with the suggestion
`prior_messages_30d`. Cycles are errors.

**Windows.** `[start, end]`, with bounds such as `-24h`, `+30m` (from the alert), `now`,
`now-7d`, an RFC 3339 time, or `{at: '$message.received', offset: -2h}`. No window may start
earlier than now minus 30 days (`window_outside_free_range`: validation refuses, it does not
clamp).

**Searches.** `search.exists` and `search.rows` take an LCQL `filter`. A value from a step
never goes into the text: write `:name` in the filter and bind it in
`params: {name: $step.path}`.

**Actions are never steps** (`action_in_gather`). A step that could change something has no
place in `gather`: call it from `act`.

## Expressions

Rules, `only_if`, approval conditions and signal explanations use one language: a path, or
a comparison of paths and literals, combined with `and`, `or`, `not` and parentheses.

```text
sender_history.prior_messages_30d > 0
message.sender_domain in org.trusted_domains
judge.label == "yes"
is_ok(trigger)
signals.all_explained
process_event.fields.FILE_PATH glob_nocase 'C:\Users\*\AppData\Local\Temp\*.exe'
```

- Operators: `== != < <= > >= in`, and the string tests `starts_with`, `ends_with`,
  `contains`, `glob`, each with a `_nocase` form. `glob` is a path glob (`*` within a path
  element, `**` across elements), not a regular expression; there is none. Windows paths
  ignore case: use the `_nocase` forms.
- `x in list` is true when the list holds `x`. `"/usr/sbin/cron" in lineage.paths` asks
  "any ancestor" without a loop.
- `is_ok(step)` is true when the step answered, false when it ran and did not answer.
- The roots are the steps, the starting inputs and `alert_time`, `signals` and `org`. A
  rule never reads `ai_review` or a `$?name` input.

## Unknown is never false

A step is **ok** (it answered), **unknown** (it failed, timed out, was not allowed, was
skipped: it has a `reason`), or **incomplete** (ok, but possibly missing data: truncated,
index lag, a lower bound). Expressions use three-valued logic:

- A comparison on an unknown step is unknown, never false. `not unknown` is unknown.
- A rule decides only when its condition is **true**.
- **An escalate rule reads incomplete answers for what they show**: `count > 0`, `found`,
  `x in list` hold as soon as the data shows them. A claim of absence (`count == 0`,
  `not found`) on incomplete data is unknown.
- **A close rule decides only on complete answers.** A value that is only derived, or a
  lower bound ("seen on 50+ hosts"), never closes anything. **A close never rests on a step
  that did not answer**: `not is_ok(x)` can raise or hold up a case, never close one
  (`close_rests_on_no_answer`).
- An answer is never more complete than its arguments: a lookup over the keys of a
  truncated listing is partial too.
- When no rule decides and nothing relevant is left to gather, the run says so:
  `couldnt_tell`, with what was missing. That is a good answer when the data is missing.

A sensor tagged `acl:<scope>` shows its content only to the scope's members: a read the run
key may not make is `unknown(acl_restricted)`. See
[Permissions](permissions.md#acl-scoped-sensors).

## Rules

```yaml
rules:
  escalate:
    - {id: banned_binary, when: 'banned.found', say: "The binary is on our banned software list."}
  close:
    - id: approved_and_signed
      when: ['approved.found', 'live_file.matches', 'live_file.verified']   # a list is "all of"
      say: "The binary is on our approved list, and the file on the host is that file, signed and verified."
  never_close_when:
    - 'message.stored_credential_harvest'
```

- `id` is required and unique across both sides (`[a-z_][a-z0-9_]*`). It is what the case,
  the run, the `act` entries and the test results name.
- `when` is a string, a list (all of), `{all: [...]}` or `{any: [...]}`, nested as needed.
- `say` is the sentence the case leads with. `{step.path}` puts a value in; a value not known
  reads `[unknown: step.path]`. A step only a `say` reads is gathered after the decision and
  never delays it.
- `never_close_when` blocks every close while a condition is true or unknown. To keep a case
  open when a read fails, say so: `never_close_when: ['not is_ok(hash)']`.
- **An escalate rule decides as soon as it holds**, and gathering stops. A close rule
  decides once it holds on complete answers and nothing blocks a close.
- Rules on both sides holding at the first decision is the outcome `conflict`; the case asks
  a person. A decision is pinned: a rule of the other side that holds later is listed in
  `verdict.contradicted_by`, never a conflict.
- The escalate rule whose facts arrived first decides. Other escalate rules that have `act`
  entries keep being gathered; one that holds is listed in `verdict.also_held` and fires its
  own entries.

## Signals: `explain_signals`

For alerts that come with reasons (Email Security's fired signals), every reason that fired
must be answered before anything closes:

```yaml
explain_signals:
  ms_sender_first_contact:
    question: Is this really the first time this sender wrote to the org?
    malicious_when: 'sender_history.prior_messages_30d == 0'
    benign_when: 'sender_history.prior_messages_30d > 0'
```

A fired signal whose `malicious_when` holds blocks every close, and so does one nothing
explains. `signals.all_explained` is true only when every fired signal has a benign
explanation that holds. Names are the detection's reason ids with `-` written `_`.

## The AI

**A focused question.** An `ask_ai` step asks one question about what other steps gathered:

```yaml
  cmd:
    op: ask_ai
    args:
      question: "Is this command line malicious? Answer yes only for explicit malicious behavior, no only for a recognizable benign use, otherwise unclear."
      sees: [ctx__trigger]
```

The answer is `label` (`yes`, `no`, `unclear`), a self-rated `confidence` (shown, never
used), a `rationale` and `evidence_complete` (true when every step it saw was complete).
Write the question so that yes means the risky reading. A close that must not rest on an AI
reading partial data requires it: `close: ['judge.label == "no"', judge.evidence_complete]`.
The AI answers through the `ai_agent` record named by the settings' `llm.agent`.

**The review.** `ai_review` runs only when no rule decided and nothing relevant is left to
gather. It reads the steps it `sees` and answers malicious, benign or unclear; a benign
answer counts only when every step it `needs` is known and complete. `act` entries name it
in `on_rules`.

**What the AI may decide.** A rule that reads an `ask_ai` step (directly or through other
steps), or an AI agent step, is **AI-assisted** (`validate` lists them in `ai_rules`). It,
and the review, decide only on the sides the template's `ai_may_decide` allows:

| `ai_may_decide` | The AI |
|---|---|
| `off` (default) | only recommends: the outcome is `ai_recommends_malicious` or `ai_recommends_benign`, and the entries that name the rule wait for a person |
| `escalate` | may escalate (`escalated_by_ai`); a benign answer recommends |
| `close_and_escalate` | may also close (`closed_by_ai`) |

Only the template says it: no settings field and no run override changes it, and a run
keeps the value it started with. An action that fires on an AI decision follows its own
`approval`.

**AI agents.** A step can hand a judgement to one of your AI agents, and a run that could
not decide can be handed off to one. See [Custom Code and AI Agents](custom-code.md).

## Act

Each entry is one action, the rules that fire it, and whether it waits for a person:

```yaml
act:
  - do: contain.network
    target: '$ctx__trigger.sid'
    on_rules: [banned_binary]
    approval: {when: '"server" in sensor.tags'}
    lease: 2h
    on_lease_end: release
  - {do: tag.add, target: '$ctx__trigger.sid', attrs: {tag: 'ie:malicious-process', ttl: 86400}, on_rules: [banned_binary], approval: none}
  - {do: close.false_positive, on_rules: [approved_and_signed], approval: required}
```

- `do`: `contain.network`, `contain.seal`, `contain.email`, `tag`, `tag.add`, `tag.remove`,
  `eradicate.file`, `close.false_positive`, `playbook:<name>` or
  `extension:<name>/<action>`.
- `approval` is **required**: `none` (acts on its own), `required` (always waits for a
  person) or `{when: <condition>}` (waits when the condition holds or is unknown).
- `lease` (1m to 7d) and `on_lease_end` (`release`, `hold`, or check again) for the actions
  that hold one. A tag lasts its `attrs.ttl`.
- `undo` names what reverts a Playbook or extension action.
- The key is `on_rules`, never `on`: YAML 1.1 parsers read a bare `on:` as `true`.

The full reference, with "check again", the action states, approvals, undo and the audit
log, is [Actions, Approvals and Undo](actions.md).

## Case

```yaml
case:
  mode: create                 # create | none. Stated, it decides for every start; leave it out to follow the settings
  severity: {escalated_by_rule: high, escalated_by_ai: high, ai_recommends_malicious: high, closed_by_rule: low, default: medium}
  kind: [phishing]
  attack: [T1566.002]
```

- `mode`: a stated `create` or `none` decides for every start that names no case, whatever
  the settings' `case` says. Left out, the settings decide. A start that names a case writes
  into it. A close entry with `mode: none` warns `close_entry_without_case`.
- `severity` is keyed by outcome, plus `default`.
- The case leads with the outcome sentence (the deciding rule's `say`, or the AI's
  recommendation and what was missing), then the fired signals, the detections, the
  evidence (each step a rule or the review read, with its sentence), what stayed unknown, the
  actions and the open question.

### What a step records

A step's `record:` names what the case shows of it:

```yaml
  link_landing:
    op: mailsec.link_resolve
    args: {links: '$message.links'}
    record:
      kind: entity                          # telemetry | entity | artifact
      entity_type: domain
      indicator: link_landing.final_domain
      title: Where the link lands
      note: "The link lands on {link_landing.final_domain}."
      malicious_when: 'link_landing.open_redirect'
      benign_when: 'link_landing.via_tracker'
```

The verdict is `malicious` when `malicious_when` holds, else `benign` when `benign_when`
holds, else `unknown`: an unknown never asserts a verdict. With `each`, one entity is written
per list element (`item_key`, `outcome_key`, `outcome_map`, `absence`, `outcome_notes`). An
artifact `ref` holds ids only. The engine adds, with no template, the telemetry of the steps a
rule or the review reads.

## Checks: templates other templates call

A **check** is a template with `kind: check`: `params`, `gather` and `rules`. A template
calls it as one step, `use: template:<name>`, and reads one fact from it: the check's
verdict. Write a check for logic several templates repeat, and for
[protected hosts](actions.md#approval) or ["check again"](actions.md#check-again-the-automatic-rollback-of-a-false-positive).

```yaml
# investigation_plan/host-is-protected
kind: check
status: active
description: "Is this host one we never isolate without a person?"
params:
  sid: {type: string, required: true, description: "The sensor."}
gather:
  host:
    op: sensor.get
    args: {sid: $sid}
  listed:
    op: lookup.get
    args: {name: protected-hosts, keys: ['$host.hostname']}
rules:
  escalate:
    - {id: tagged_protected, when: '"protected" in host.tags', say: "The host is tagged protected."}
    - {id: listed_protected, when: 'listed.found', say: "{host.hostname} is on the protected hosts list."}
  close:
    - {id: not_protected, when: ['not "protected" in host.tags', 'not listed.found'], say: "The host is neither tagged nor listed as protected."}
```

A calling template reads `protected.malicious`: an approval condition
`{when: 'protected.malicious'}` waits for a person while the check has not decided (unknown
waits). In a check, "escalated" means the condition the check tests holds.

- **A check never acts and never shapes the case.** It may not have `applies_to`,
  `starts_from`, `act`, `case`, `ai_review`, `explain_signals`, `scope`, `deadline`, `trust`,
  `ai_may_decide`, `coalesce` or `hand_off` (`check_forbidden_key`).
- **The call's fact**: `malicious`, `benign`, `outcome` (`escalated` or `closed`), `label`,
  `rule`, `say`, `ai_assisted`, `template`, `version`. Known only once the check decided;
  otherwise unknown, never false: `not x.malicious` is never a reason to close.
- **A check is a black box.** A caller cannot read its steps.
- **One call per element**: `each: '$message.links'`, `as: link`, `key: '$link.href'`,
  `max_items` (1 to 25, required). The fact then has `items`, `any_malicious`, `all_benign`,
  counts and `first_malicious`.
- **An active template runs only active checks.** Activating a template is the permission
  to act, and a check decides for its caller, so every check in an active template's closure
  (the checks it calls, the checks they call, and the check an `act` entry runs again at
  lease end) must itself be `status: active`. When one is a draft, the template does not run:
  a start that names it is refused with `check_not_active`, naming the check, and
  `applies_to` selection skips it (the trigger goes to the next matching active template, or
  to none), the same as a check that is missing or disabled (`check_missing`). An active
  check that calls a draft check is itself refused. Nothing is evaluated and nothing acts. A
  run already started keeps the checks it started with. A draft template may call a draft
  check directly: a person tests it and nothing acts.
- **Promoting a check is gated like activating a template.** Setting a check to
  `status: active`, and editing an active check, need a person (or an API key only when the
  settings record carries `allow-api-key-promotion`, see
  [Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)). An API key
  may still demote an active check to a draft: its active callers then stop running until a
  person promotes it again. Promote the checks before, or in the same push as, the template
  that calls them.
- **Versions.** A call names a check by record name: a saved check takes effect on the next
  run of every caller. `validate` with the check's name returns `used_by`, each caller
  validated against your draft; `as_active` refuses to preview a draft that would not run
  once active. At most 3 nested calls, 256 steps and 50 check instances per run.
- A check is never started on its own (`check_not_startable`). Test it with `params`
  samples.

## How templates are chosen

A start that names no template (a D&R rule without `template`, the console's Investigate on
a detection) gets the **active** template whose `applies_to` matches:

| Key | Matches |
|---|---|
| `detect_cat` | the detection's category |
| `rule` | the D&R rule, **namespaced**: `general.<record name>` |
| `tag` | any of the rule's or the case's tags |
| `severity` | the case's severity (a rule on a detection sends none) |
| `source` | `dr-rule`, `case` or `api` |

Values are exact (case-insensitive) or `*` globs. Every key the template lists must match.
When several active templates match, the one that lists more keys wins, then the one with
more exact values, then the lower name (warning `applies_to_tie`). A template without
`applies_to` is never chosen automatically. The run records why it got its template
(`template_selection`), and

```bash
limacharlie api "investigate/$OID/templates/coverage?category=rare-process&source=dr-rule" --oid "$OID"
```

shows which template a trigger picks (`as_active=<draft>` previews a draft taking over).

## Validate

```bash
limacharlie investigate templates validate --file plan.yaml --oid "$OID"
```

The report has `valid`, `errors` and `warnings` (each with a stable `code`, a `path`, a
message and often a `suggestion`), `ai_rules`, an `estimate` of the worst-case cost, and per
`act` entry its `do`, `approval`, lease and `acts_alone_possible`. Fix the errors, then the
warnings: they are the mistakes that pass validation but make a template useless. Every code
is listed with its fix in the kit (`limacharlie investigate kit --section codes`), and the
common ones in [Troubleshooting](troubleshooting.md#a-template-is-refused-when-you-save-or-validate-it).

The Hive validates the same shapes when a record is saved, so a record one side accepts is
not refused by the other.

## Test on past alerts

```bash
limacharlie investigate templates test --file plan.yaml --detect-cat rare-process --last 10 --oid "$OID"
```

A test runs the template for real, **read only**, with your own token, on past detections
(`--detection-id`), cases (`--case-id`), the newest alerts of a category
(`--detect-cat ... --last N`, N at most 25) or free inputs. Nothing is written: no run, no
case, no action. Per sample it says which rule decided (or what the AI recommended), what
stayed unknown and why, the cost, the actions it `would_propose` (with whether each would
wait for a person), and, for a closed case, whether the rule agreed with your analysts. The
`summary` counts per rule how many samples it decided and how many of those agree or
disagree.

Read it in this order: the validation, the summary, each `disagree` (tighten that rule),
then the undecided samples. A test never reads the pause or the circuit breaker, starts no
AI agent session, and counts against your organization's parallel runs.

After a template is live, `compare` replays an edit against finished runs offline (recorded
facts only, no call): see [API Reference](api-reference.md#templates-and-authoring).

## Draft and active

- **A draft only suggests.** It runs only through a test or a run a person starts, and its
  actions are recorded `suggested`: never executed, never approvable. A D&R rule never starts
  a draft (`template_draft`).
- **Making a template active is the permission to act.** An active template does what its
  `act` entries say, within the pause, the circuit breaker and its key's permissions.
- `templates save` always writes a draft. A person promotes it: `templates promote <name>
  --confirm`, or `save --status active`. An AI agent saves drafts and never promotes. An API
  key can write an active template only when the settings record is tagged
  `allow-api-key-promotion`.
- A run pins the template's version when it starts. A run whose template is no longer the
  active one it pinned only suggests.

Permissions: saving needs `investigation_plan.set` (reading `investigation_plan.get`).
Validating and testing need only `investigation.get` / `investigation.set` and store nothing.
