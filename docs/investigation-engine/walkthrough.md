# Walkthrough: From an Empty Organization to a Finished Investigation

This page takes an organization with nothing configured to a finished
investigation, one step at a time. Every step has the API call, and the CLI or MCP
equivalent where one exists. It is written so that a person or an AI agent can
follow it from top to bottom without guessing.

!!! info "Read this first"
    - The Investigation Engine is in pre-release. Its routes exist only where it is
      enabled for your organization; elsewhere every `/v1/investigate/...` call answers
      the same `404` as an unknown path. See [API Reference](api-reference.md).
    - Steps 1 to 6 are setup, done once. Steps 7 to 13 are the daily use.
    - When a call is refused, look up its `reason_code` or `error_code` in
      [Troubleshooting](troubleshooting.md).

The other pages are the reference for each part:
[How to Think About Templates](how-to-think-about-templates.md),
[Concepts](concepts.md), [Plan Templates](templates.md),
[Policies and Autonomy](policies.md) and the
[policy record reference](../7-administration/config-hive/investigation-policy.md),
[Automatic Starts](automation.md), [Permissions](permissions.md),
[API Reference](api-reference.md), [CLI](cli.md), [MCP Tools](mcp.md) and
[Console](console.md).

## The shell variables used below

```bash
export OID="<organization UUID>"
export LC_JWT="<a LimaCharlie JWT for that organization>"
API="https://api.limacharlie.io/v1"
```

Get a JWT as described in [API keys](../7-administration/access/api-keys.md): a POST
to `https://jwt.limacharlie.io` with the organization ID and an API key. The JWT is
valid for one hour. An API key must have a key id to use the Investigation Engine;
the keys you create today have one. The CLI commands take `--oid "$OID"` and use the
CLI's own login.

!!! note "CLI availability"
    The `limacharlie investigate ...` commands below are not in a released CLI version
    yet; check with `limacharlie investigate --help`. Every one of them has an API
    equivalent on this page. The other CLI commands used here (`api-key create`,
    `hive set`, `dr set`) are in the current release.

## 1. Prerequisites and your own permissions

You need:

- an organization where the Investigation Engine is enabled;
- for case-based investigations, the organization
  [subscribed to Cases](../5-integrations/extensions/limacharlie/cases.md): every run
  writes its result to a case by default;
- an AI provider credential (an Anthropic API key, for example) for the AI
  questions and the AI review;
- for the person doing the setup, the permissions below.

| To do | Permissions |
|---|---|
| Use the engine: read runs, start runs, test templates | `investigation.get`, `investigation.set`, `insight.evt.get` |
| Install, edit and delete templates | `investigation_plan.get`, `investigation_plan.set`, `investigation_plan.del` |
| Write and delete the policy | `investigation_policy.get`, `investigation_policy.set`, `investigation_policy.del` |
| Name a secret as the run identity in the policy | `secret.get` on that secret |
| Create the API key and the secrets below | `apikey.ctrl`, `secret.set` |
| Create the AI agent record | `ai_agent.set` |
| Install D&R rules | `dr.set` |
| Approve an action | `investigation.set`, `insight.evt.get` and the action class's own permission (`sensor.task` for network isolation, `mailsec.act` for email quarantine) |

**No role holds `investigation_plan.*` or `investigation_policy.*`, not even Owner.**
Grant them explicitly, to a person or to an API key. See
[Permissions](permissions.md).

Check that the engine answers before going further:

```bash
curl -s "$API/investigate/$OID/templates" -H "Authorization: Bearer $LC_JWT"
```

`{"templates": []}` means the engine is there and the organization has no template
yet. A `404` with no `error_code` means the engine is not enabled on this API host.
A `401` names the permission you are missing.

## 2. The AI agent record

Templates use the AI in two places: `ask_ai` steps, one focused question such as
"is this command line malicious?", and the AI review, the fallback when no rule
decided. Each call is one structured call through the organization's `ai_agent`
[Hive record](../9-ai-sessions/dr-sessions.md#ai-agent-record-fields): the record
decides the model, the system prompt and the provider credentials, and your provider
bills the tokens on your credentials. The policy's `llm.agent` names the record
(step 4); when it names none, the engine looks for the record named
**`investigation-judge`**.

Store the provider key as a secret, then create the record:

```bash
# The provider key, as a Hive secret.
curl -s -X POST "$API/hive/secret/$OID/anthropic-key/data" \
  -H "Authorization: Bearer $LC_JWT" \
  -d 'data={"secret":"<your Anthropic API key>"}' \
  -d 'usr_mtd={"enabled":true}'

# The AI agent record the AI questions and the review run with.
curl -s -X POST "$API/hive/ai_agent/$OID/investigation-judge/data" \
  -H "Authorization: Bearer $LC_JWT" \
  -d 'data={"anthropic_secret":"hive://secret/anthropic-key","prompt":"You are a security analyst. Answer each question about the data block with one of the allowed labels and a short rationale."}' \
  -d 'usr_mtd={"enabled":true}'
```

The record needs a `prompt` and one credential source; `model` is optional. It does
not need `lc_api_key_secret`, since an AI question makes no tool calls. Without the
record, every `ask_ai` step and the review are `unknown` with the reason
`llm_agent_not_found`. Rules that do not read the AI still decide; the rest of the
runs end `couldnt_tell`.

## 3. The run identity: an API key the policy names

Every read a run makes and every action it takes is authorized as the run's
**identity**. A run started by a person can use that person's own token, but a run
started by a D&R rule has no person behind it, so the policy must name an
**organization API key** stored as a Hive secret. Runs started by rules are refused
without one (`reason_code` `no_policy_identity`).

Create the key and store it as a secret in one step with the CLI:

```bash
limacharlie api-key create --name investigation-engine \
  --permissions insight.det.get,insight.evt.get,sensor.list,sensor.get,investigation.get,investigation.set,lookup.get \
  --store-secret investigation-engine-key --oid "$OID"
```

Or create an organization API key in the console (**Access Management**, **REST API**)
and store its value as the secret `investigation-engine-key` with the same `curl`
as in step 2. Only an **organization** API key works; a user API key is refused when
the run starts (`reason_code` `identity_secret_unavailable`).

The permissions above let a run read detections, telemetry, sensors and lookups and
write its case. Add what your templates and actions need, and nothing more:

| For | Add |
|---|---|
| Email templates (`mailsec-*`, `phishing-campaign`) | `mailsec.get` |
| Live reads of a host (`sensor.read.*` operators) | `sensor.task.read` and `output.set` |
| Network isolation, sealing (`contain.network`, `contain.seal`) | `sensor.task` |
| Email quarantine (`contain.email`) | `mailsec.act` |
| Sensor tags (`tag.add`, `tag.remove`) | `sensor.tag` |
| Closing a false-positive email (`close.false_positive` on a message) | `mailsec.set` |

A step the identity may not read comes back `unknown` with the reason `forbidden`,
never as "nothing found". The identity key is a powerful credential: a run started
by a person executes with the **key's** permissions, not the person's, unless the
request picks `caller` and the policy allows it.

## 4. The policy: start in `suggest`

The `investigation_policy` record named `default` sets the identity, the AI agent and
what the engine may do on its own. This minimal policy never executes anything without
a person: containment and tagging are only suggested, and closing a case as a false
positive waits for a person's approval, so that **Close as benign** and
**Add to list and close** (step 9) have something to act on:

<!-- validate: policy -->
```yaml
# investigation_policy/default
identity:
  default: hive://secret/investigation-engine-key
llm:
  agent: hive://ai_agent/investigation-judge
ai_may_decide:
  "*": "off"               # the AI recommends; a person decides (the default)
autonomy:
  contain.network: {mode: suggest}
  contain.email: {mode: suggest}
  tag.add: {mode: suggest}
  close.false_positive: {mode: approve, approval_timeout: 24h}   # a person confirms every close
```

Quote `"off"`: some YAML readers, including the one in current `limacharlie hive set` releases, turn
a bare `off` into the boolean false, and the policy is then refused (`policy_type` at
`/ai_may_decide/*`).

Why `approve` for the close: after `ai_recommends_benign` the engine proposes the close
capped at `approve`. Under `suggest` it stays a suggestion, so there is nothing to
approve or deny and the step 9 buttons do nothing: you would close the case in Cases
instead. With `approve`, a close a rule decided (`closed_by_rule`) also waits for a
person until you raise the class to `auto`. `approval_timeout: 24h` keeps a proposal
open for a day; the default, 15 minutes, would expire it before most people look. A
decided run that only waits for a person holds no concurrent-run slot
(`budgets.max_concurrent_runs` counts the runs that still gather or execute), so a
day of pending closes does not stop new investigations. The backlog is bounded:
once an organization has about 50 times `max_concurrent_runs` decided runs waiting
for a person (500 at the default; the engine counts it per server, so refusals can
start somewhat later), new starts are refused with `too_many_runs` until some
are decided or expire. Work the approvals inbox daily.

Write it (the Hive takes the record's data as JSON):

```bash
curl -s -X POST "$API/hive/investigation_policy/$OID/default/data" \
  -H "Authorization: Bearer $LC_JWT" \
  -d 'data={"identity":{"default":"hive://secret/investigation-engine-key"},"llm":{"agent":"hive://ai_agent/investigation-judge"},"ai_may_decide":{"*":"off"},"autonomy":{"contain.network":{"mode":"suggest"},"contain.email":{"mode":"suggest"},"tag.add":{"mode":"suggest"},"close.false_positive":{"mode":"approve","approval_timeout":"24h"}}}' \
  -d 'usr_mtd={"enabled":true}'
```

Or save the YAML above as `policy.yaml` and run
`limacharlie hive set --hive-name investigation_policy --key default --input-file policy.yaml --enabled --oid "$OID"`.

To change what the AI may decide for one template later, without touching the rest of
the record, use the CLI (it writes only `ai_may_decide`, conditional on the version it
read):

```bash
limacharlie investigate policy ai --oid "$OID"
limacharlie investigate policy ai-set suspicious-process escalate --confirm --oid "$OID"
```

Saving a policy that names a secret for the first time needs read access to that
secret, and the secret must already exist. Sections you leave out (budgets,
operators, speculation) keep the platform defaults. Always send
`usr_mtd.enabled: true` (or `--enabled`): a disabled record is ignored.

Check what the engine will apply:

```bash
curl -s "$API/investigate/$OID/policy/effective" -H "Authorization: Bearer $LC_JWT"
limacharlie investigate policy get --oid "$OID"
```

The answer lists the records applied, the budgets, what the AI may decide
(`ai_may_decide`), each action class with its mode and where each value came from, the run identity, and
`warnings` (for example a record that does not parse).

**What `approve` and `auto` change.** Once you trust what the engine proposes, raise
one class at a time:

<!-- validate: policy -->
```yaml
autonomy:
  contain.network:
    mode: approve                      # a person decides each isolation
    approvers: [alice@example.com]     # optional: only these people may approve
    approval_timeout: 30m              # unanswered requests expire (default 15m)
  contain.email:
    mode: auto                         # executed by itself once the rule decided
    max_targets_per_run: 3
    max_targets_per_hour: 10
```

- `approve` sends the action to the approvals inbox. A person with the permissions of
  step 1 approves or denies it. `approvers` lists the people allowed to decide, by the
  exact email (or API key name) they act as; a list that matches nobody blocks every
  approval.
- `auto` executes the action without a person **only** when the template binds the
  action to an authorization the engine can re-check from the run's evidence (the
  `authorize:` key of an `act` entry), and for the false-positive close the engine
  proposes after a close outcome. Any other action of an active template waits for a
  person even under `auto`, with the reason `no_registered_authorization`. In the
  default library, only the `contain.email` entries of `mailsec-message` and
  `phishing-campaign` carry an authorization.
- `ai_may_decide` is separate from the modes: it says whether an AI answer may
  **decide** the outcome for a template (`off`, `escalate`, `close_and_escalate`).
  Leave it `off` until you have read how the AI's recommendations compare with your
  analysts' decisions. See [What the AI may decide](policies.md#what-the-ai-may-decide).
- To stop everything from running by itself at once, with a person still able to
  approve, save the `autonomy-manual-pause` record
  (see [Emergency pause](../7-administration/config-hive/investigation-policy.md#emergency-pause-and-resume)).

The full record reference is
[Investigation Action Policies](../7-administration/config-hive/investigation-policy.md);
how records combine is in [Policies and Autonomy](policies.md).

## 5. Install a template from the library and make it active

An organization's templates are exactly its `investigation_plan` records. The default
library is content you choose to install. List it:

```bash
curl -s "$API/investigate/$OID/authoring-kit?sections=library" -H "Authorization: Bearer $LC_JWT"
limacharlie investigate kit --section library --oid "$OID"
```

Each entry has `name`, `description`, `version`, `status`, `applies_to` and the
`yaml` to store. Install `endpoint-detection`, the template for any detection on a
sensor, as a **draft**:

```bash
limacharlie investigate templates install-defaults --name endpoint-detection --oid "$OID"
```

Over the API, write the entry's `yaml` as the record. The Hive takes the template as
the record's `data`; with `jq` and `yq` installed:

```bash
curl -s "$API/investigate/$OID/authoring-kit?sections=library" -H "Authorization: Bearer $LC_JWT" \
  | jq -r '.library[] | select(.name=="endpoint-detection") | .yaml' > endpoint-detection.yaml
curl -s -X POST "$API/hive/investigation_plan/$OID/endpoint-detection/data" \
  -H "Authorization: Bearer $LC_JWT" \
  --data-urlencode "data=$(yq -o=json '.' endpoint-detection.yaml)" \
  -d 'usr_mtd={"enabled":true}'
```

An MCP agent fetches the library with `investigate_authoring_kit` (`sections:
["library"]`) and saves it with `investigate_save_plan`, which always writes a draft.

**Create the lists its rules read.** `endpoint-detection` closes on your
`approved-software` Lookup and escalates on your `banned-software` Lookup, both keyed
by file hash. Until they exist, those rules never hold (the Lookup read is
`unknown(not_found)`), and the run falls back to the AI-assisted rules and the review.
Create them in **Lookups** with the hashes you already know, or later from the
console's **Add to list and close** (step 9).

**Test it on past alerts** before it acts. A test runs the template's real read-only
steps on alerts that already happened, as you, and writes nothing but its own result:

```bash
limacharlie investigate templates test endpoint-detection \
  --detect-cat <a detection category you have> --last 10 --oid "$OID"
```

```bash
curl -s -X POST "$API/investigate/$OID/test-plan" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"template": "endpoint-detection", "samples": [{"detect_cat": "<category>", "last": 10}], "wait_seconds": 10}'
# 202 while it runs: poll with the test_id it returned
curl -s "$API/investigate/$OID/test-plan/<test_id>?after=0&wait=10" -H "Authorization: Bearer $LC_JWT"
```

Read the summary: how many samples a rule decided (`decided_by_rules`), how often
each rule agreed with the analysts (`rules`), how the AI's recommendations fared on
the rest (`ai`), and the reasons steps stayed unknown. See
[Test on past alerts](templates.md#test-on-past-alerts).

**Make it active.** A person makes a template active, and only an active template can be
started by a D&R rule or chosen automatically. In the console open
**Investigations**, **Templates**, the template, and **Make active**. From the CLI,
signed in as a user (`limacharlie auth login --oauth`):

```bash
limacharlie investigate templates promote endpoint-detection --confirm --oid "$OID"
```

A write of `status: active` from an API key is refused by default, so an AI agent
can draft and test but never make a template active. See
[Active templates can only be written by a person](permissions.md#active-templates-can-only-be-written-by-a-person).

## 6. Optional: notifications

To hear about decisions and pending approvals, add `notify` to the `default` policy
record. Events are written to the organization's audit log, which your Outputs on the
audit stream deliver:

<!-- validate: policy -->
```yaml
notify:
  action.needs_approval: ['output:slack-soc']
  run.decided: ['output:slack-soc']
```

See [Notifications](policies.md#notifications).

## 7. Start a run

### A person, through the API, the CLI, MCP or the console

```bash
curl -s -X POST "$API/investigate/$OID/runs" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"trigger": {"detection_id": "<detection id>"}, "plan": {"template": "endpoint-detection"}, "wait_seconds": 30}'
```

```bash
limacharlie investigate runs start --template endpoint-detection \
  --detection-id <detection id> --wait 30 --oid "$OID"
```

- The answer is `{"run": {...}, "joined": false}`, HTTP `201` (`200` when the start
  joined an open run). `wait_seconds` blocks up to that long for the outcome.
- Leave `plan` out to let the engine choose the **active** template whose
  `applies_to` matches the trigger. A person's start is matched on what the request
  says, not on the detection's record, so add the detection's category (and `tags` or
  `severity` if your `applies_to` uses them) to `trigger`:
  `{"trigger": {"detection_id": "<detection id>", "category": "<detect_cat>"}}`.
  `detect_cat` matches `category`, `tag` matches `tags`, `severity` matches `severity`,
  and `source` is `api`. Without a category, no `detect_cat` matches, not even `*`, and
  the start is refused with `no_template_applies`. The console's **Investigate** sends
  them for you. `{"auto": true}` is refused for a person.
- To investigate an existing case **and write into it**, send
  `"trigger": {"case_id": "<case number>"}` with `"case": "attach:<case number>"`.
  Without `case`, a run on a case writes a **new** case (the policy default,
  `create`). `"case": "none"` writes no case.
- MCP: `investigate_start` with `template` and `detection_id`.
- Console: **Investigate** on a detection, a case, an entity or an email message, or
  **New investigation**. See [Console](console.md).
- A run started on a **draft** template runs with every action capped at `suggest`.

### A D&R rule on a detection

Add `start investigation` after `report` in a rule's response:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: powershell.exe
respond:
  - action: report
    name: suspicious-powershell
  - action: start investigation
    template: endpoint-detection
```

```bash
limacharlie dr set --key investigate-powershell --input-file rule.yaml --oid "$OID"
```

The run is tied to the detection `report` just created; one detection starts at most
one run. Without `template`, the engine picks the active template whose `applies_to`
matches. See [Automatic Starts](automation.md#dr-rules-on-a-detection).

### A D&R rule on a new case

Cases posts every case change into your organization's event stream. A rule on the
`case_created` event starts a run **in that case**:

```yaml
detect:
  event: case_created
  op: or
  rules:
    - {op: is, path: event/metadata/severity, value: high}
    - {op: is, path: event/metadata/severity, value: critical}
respond:
  - action: start investigation
    case: '{{ .event.case_number }}'
```

The default library ships this rule as `investigate-high-critical-case`
(`GET /authoring-kit?sections=library` or the MCP tool `investigate_authoring_kit`, under `rules`); install it as a D&R rule.
The engine never starts a run in a case it wrote itself. See
[Automatic Starts](automation.md#dr-rules-on-a-new-case).

### An inline plan

A person can run a template that is not stored, for a one-off: `plan.inline` is the
template YAML as a string.

```bash
curl -s -X POST "$API/investigate/$OID/runs" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  --data-binary @- <<'EOF'
{"trigger": {"detection_id": "<detection id>"},
 "plan": {"inline": "description: \"One-off check: escalate when the host raised five or more detections this week.\"\nstarts_from: detection\ngather:\n  trigger:\n    op: detection.get\n    args: {detect_id: $detection_id, window: [-29d, now]}\n  related:\n    op: detection.list\n    args: {sids: ['$trigger.sid'], window: [-7d, now]}\nrules:\n  escalate:\n    - {id: busy_host, when: 'related.count >= 5', say: \"The host raised {related.count} detections this week.\"}\ncase:\n  mode: none\n"},
 "case": "none"}
EOF
```

An inline plan is always a draft (actions capped at `suggest`), runs with the
caller's own token unless the policy has an `identity.templates.inline` entry, and is
refused for a run started by a rule (`inline_plan_not_allowed`). For a one-off
question that needs no decision, a [wave](concepts.md#waves-and-fact-packs) is lighter.

## 8. Follow the run

```bash
curl -s "$API/investigate/$OID/runs/<run id>" -H "Authorization: Bearer $LC_JWT"
limacharlie investigate runs get <run id> --oid "$OID"
```

- **State:** `queued`, `running`, `decided` (the outcome is final, scoping or
  actions may still run), `completed`, `cancelled`, `failed` or `budget_exhausted`.
- **Outcome:** `verdict.outcome` is one of the eight outcomes below, with
  `decided_by` (the rule or the AI that decided, and its sentence), the AI's
  `recommendation` when it recommends, and `missing` (what stayed unknown, why, which
  rule needed it, and the question for a person). `verdict.label` is derived from it.
  `ai_agent` names the AI agent record the run used.

  | `verdict.outcome` | What it means | What you do |
  |---|---|---|
  | `closed_by_rule` | A close rule held on complete evidence. `decided_by.say` is its sentence. | Approve the proposed close (with step 4's policy it waits for a person), or nothing once `close.false_positive` is `auto`. |
  | `escalated_by_rule` | An escalate rule held. | Work the case. The rule's `act` entries are proposed under their modes. |
  | `closed_by_ai` | The AI decided to close, because `ai_may_decide` lets it close for this template. | The close follows the `close.false_positive` mode: approve it, or nothing under `auto`. Spot-check. |
  | `escalated_by_ai` | The AI decided to escalate, because `ai_may_decide` lets it. | Work the case. Its `act` entries wait for a person. |
  | `ai_recommends_benign` | The AI recommends closing. Nothing was done. | Decide: see [step 9](#9-what-ai-recommends-means). |
  | `ai_recommends_malicious` | The AI recommends escalating. Nothing was done. | Decide: see [step 9](#9-what-ai-recommends-means). |
  | `couldnt_tell` | No rule decided and the AI did not answer either way. | Read `missing`: answer its `ask`, or fix what made a step unknown ([Troubleshooting](troubleshooting.md#a-run-finished-but-the-outcome-means-little)). |
  | `conflict` | Rules on both sides held, or an AI-assisted rule recommended against a deterministic rule of the other side. | Decide, then fix the rules so they cannot both hold. |

- **Events**, as a long-poll: pass the last `next` as `after` until `done` is true.

  ```bash
  curl -s "$API/investigate/$OID/runs/<run id>/events?after=0&wait=10" -H "Authorization: Bearer $LC_JWT"
  limacharlie investigate runs events <run id> --follow --oid "$OID"
  ```

  Event types include `run.created`, `run.state`, `run.phase`, `step`, `fact`,
  `verdict` (it carries the outcome), `action`, `input`, `case`, `usage` and `final`.
  Event data carries structure, never customer values.
- **Steps**, the plan graph and the outcome timeline: `GET .../runs/<run id>/steps`
  (`runs steps` in the CLI). Every step carries `narrative`: `why` it ran, what it
  `found`, and what `used` it (`rule:<id>`, `ai_review`, another step, or nothing:
  "not used for the decision"). A step its `only_if` skipped is `skipped`, with the
  reason.
- **The case:** `case_id` appears with the first case write and `case_final` turns
  `true` once the write made after the run ended has landed. The case leads with the
  outcome sentence. The case document the run wrote: `GET .../runs/<run id>/case`
  (`runs case`). Open the case itself in Cases.

## 9. What "AI recommends" means

`ai_recommends_benign` and `ai_recommends_malicious` mean the AI answered, but the
policy does not let it decide for this template (`ai_may_decide` is `off`, or
`escalate` for a benign answer). So **nothing was done**: no case close, no
containment. A person decides. The run gives you what you need:

- `verdict.recommendation`: `label` (`benign` or `malicious`), `rationale`,
  `citations` (the step fields it used: open those steps), `by` (the AI-assisted rule
  or `ai_review`) and `self_rated_confidence`. The confidence is the AI's own rating:
  it is not a probability, and the engine never uses it.
- The steps' narratives, and `missing`: what the AI did not have.

These actions need `close.false_positive` in `approve` (or `auto`), as in step 4's
policy. If the class is in `suggest`, the close is only suggested: there is nothing to
approve or deny, so close the case, or work it, in Cases.

**To close (you agree it is benign).** After `ai_recommends_benign` the engine
proposes the close (`close.false_positive`) of the case the run wrote (and, for an
email, of the message) at most at `approve`, so it waits in `awaiting_approval` even
when the class is `auto`. Approving it is the console's
**Close as benign**:

```bash
# Find the close the run proposed
curl -s "$API/investigate/$OID/actions?run_id=<run id>&class=close.false_positive&state=awaiting_approval" \
  -H "Authorization: Bearer $LC_JWT"
# Approve it
curl -s -X POST "$API/investigate/$OID/runs/<run id>/actions/<action id>/approve" -H "Authorization: Bearer $LC_JWT"
```

You need `investigation.set` and `insight.evt.get`; closing an email message also needs
`mailsec.set`. The proposal expires after the class's `approval_timeout`.

**To escalate (you think it is malicious, or you disagree with a benign
recommendation).** The console has no Escalate button: escalation is something a
template does, with an `escalate` rule. By hand, deny the proposed close with a note
(**Deny** in the console's Approvals tab), then work the case:

```bash
curl -s -X POST "$API/investigate/$OID/runs/<run id>/actions/<action id>/deny" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" -d '{"note": "escalated: unexpected parent process"}'
```

After `ai_recommends_malicious` nothing is proposed: open the case and contain by
hand, or start a new run once you have a rule that decides.

**To make the next one decide by rule.** When a cited step read one of your Lookups
(`lookup.get`), the console offers **Add to list and close**: it adds the keys the
Lookup did not list (the hash, the domain) to that Lookup, then approves the close.
The next identical alert is `closed_by_rule`, with no AI call. Over the API, add the
key to the `lookup` Hive record, then approve as above. When people keep making the
same call, write the rule: see
[How to Think About Templates](how-to-think-about-templates.md#8-turn-repeated-decisions-into-rules).

## 10. Approve, deny, undo

```bash
# The approvals inbox: what waits for a person, across every run
curl -s "$API/investigate/$OID/actions?state=awaiting_approval" -H "Authorization: Bearer $LC_JWT"
limacharlie investigate actions list --state awaiting_approval --oid "$OID"

# Decide
curl -s -X POST "$API/investigate/$OID/runs/<run id>/actions/<action id>/approve" -H "Authorization: Bearer $LC_JWT"
curl -s -X POST "$API/investigate/$OID/runs/<run id>/actions/<action id>/deny" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" -d '{"note": "expected maintenance"}'
```

| Verb | When | Body |
|---|---|---|
| `approve`, `deny` | The action is `awaiting_approval` | `note` (deny) |
| `extend` | An active lease, to keep it longer | `seconds` |
| `confirm` | An active lease, to keep it in place for good | |
| `revert` | An `active` or `confirmed` action: undo it | `note` |

- An action in `suggest` mode is never executed: approving it is refused with
  `this action class is in suggest mode`. To execute, raise the class in the policy and
  start a new run on an active template.
- When the policy names `approvers`, only they may approve, deny, extend or confirm
  (`403`, `error_code` `forbidden`). Anyone with the class permission may revert.
- A `tag` or `tag.add` holds no lease: it is `confirmed` as soon as it is added and
  lasts its `ttl`, so `extend` and `confirm` are refused for it (`409`, and
  `eligibility` says `false`). `revert` removes the tag.
- Each action carries `eligibility`, what the caller may decide on it.
- The CLI has `actions approve` and `actions deny`; use the API or the console for the
  other verbs.

## 11. Cancel

```bash
curl -s -X POST "$API/investigate/$OID/runs/<run id>/cancel" -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" -d '{"revert_leases": true}'
limacharlie investigate runs cancel <run id> --revert-leases --oid "$OID"
```

Steps in flight stop. Every action still waiting for a person expires at once and can
no longer be approved. Active leases stay in place unless `revert_leases` is `true`;
a lease of a class whose permission you do not hold is not reverted and is listed in
`skipped_reverts`. Cancelling a run that already ended changes nothing.

## 12. Read the performance stats

```bash
curl -s "$API/investigate/$OID/stats?since=2026-11-01T00:00:00Z&template=endpoint-detection" \
  -H "Authorization: Bearer $LC_JWT"
limacharlie investigate stats --template endpoint-detection --oid "$OID"
```

The report needs `investigation_policy.set` on top of the read permissions: a
person without it gets `403`. It covers runs by state and by outcome (`runs.by_outcome`), time to a decision, the speed-up against a serial baseline,
search and AI cost, per-operator calls and errors, and for each template and action
class what became of the actions (suggested, approved, denied, expired, executed
automatically, failed, undone, held). The report says what the engine did; it never
scores whether an outcome was right. See [Stats](api-reference.md#stats).

## 13. Limits and costs

| What | Limit |
|---|---|
| Concurrent runs per organization | `budgets.max_concurrent_runs`, default 10: the runs that still gather or execute. Over it a start is refused (`too_many_runs`, `429`). Tests and waves count too; a decided run that only waits for a person does not. |
| Decided runs waiting for a person | About 50 times `max_concurrent_runs` (500 by default, counted per engine server, so refusals can start somewhat later). Over it a start is refused (`too_many_runs`) until some are decided or expire. |
| A run's time, steps and AI spend | `max_wall_seconds` 600, `max_steps_per_run` 200, `max_llm_usd_per_run` 0.50 by default. |
| Search history | Every search stays within the last 30 days (`lookback_days`, at most 30). |
| API rate limits, per caller and organization | 300 starts, 600 waves, 300 tests and 600 comparisons per hour. |
| D&R starts | 2 per second sustained per organization, bursts of 20; over it a start is dropped. |
| Test on past alerts | At most 25 samples; the result is kept 24 hours. |

Who pays:

- **Searches** stay inside the free time range, so they carry no search charge.
- **AI questions and reviews** run on the provider credentials of your `ai_agent`
  record, so your provider bills those tokens. The run reports what they cost and
  stops launching new AI calls once `max_llm_usd_per_run` is reached; a call already
  in flight can take it slightly past. A template whose rules decide most alerts
  costs little: the review runs only when no rule decided.
- **Operators that bill per use**, such as artifact collection, are off unless the
  policy allows them.

## Next

- Write your own template, or understand the library's:
  [How to Think About Templates](how-to-think-about-templates.md).
- Something was refused or did not start: [Troubleshooting](troubleshooting.md).
- Write and tune templates with an AI agent:
  [Build and Tune Templates with an AI Agent](build-templates-with-ai.md).
