# Walkthrough: From an Empty Organization to an Automatic Isolation

This page takes an organization with nothing configured to two working
investigations:

1. **Acts alone.** A detection fires, the engine confirms the binary is on your banned
   list, isolates the host for **one minute** on its own, releases it when the minute is
   up, and you undo the tag it added.
2. **Waits for a person.** The same template, changed so that a host tagged `server`
   waits for a person's approval before it is isolated.

Every step has the command or API call. A person or an AI agent can follow it from top
to bottom.

!!! info "Before you start"
    - The Investigation Engine is experimental. Its routes exist only where it is
      enabled for your organization; elsewhere every `/v1/investigate/...` call answers
      `404` with no `error_code`.
    - Isolation cuts the host off the network for the length of the lease. Use a test
      host.
    - When a call is refused, look up its `reason_code` or `error_code` in
      [Troubleshooting](troubleshooting.md).

## The shell variables used below

```bash
export OID="<organization UUID>"
export LC_JWT="<a LimaCharlie JWT for that organization>"
API="https://api.limacharlie.io/v1"
```

Get a JWT as described in [API keys](../7-administration/access/api-keys.md). The CLI
commands take `--oid "$OID"` and use the CLI's own login. They need CLI 5.14.0 or later
(`python -m pip install --upgrade limacharlie`).

## 1. Your own permissions

| To do | Permissions |
|---|---|
| Read runs, start runs, test templates, decide actions | `investigation.get`, `investigation.set`, `insight.evt.get` |
| Install, edit, promote and delete templates | `investigation_plan.get`, `investigation_plan.set`, `investigation_plan.del` |
| Write the settings record | `investigation_policy.get`, `investigation_policy.set` |
| Name a secret as the run identity | `secret.get` on that secret |
| Create the API key and its secret | `apikey.ctrl`, `secret.set` |
| Create the lookup and the D&R rule | `lookup.set`, `dr.set` |
| Approve or undo an isolation | the reads and writes above, plus `sensor.task` |

**No role holds `investigation_plan.*` or `investigation_policy.*`, not even Owner.**
Grant them explicitly. See [Permissions](permissions.md).

Check that the engine answers:

```bash
curl -s "$API/investigate/$OID/templates" -H "Authorization: Bearer $LC_JWT"
```

`{"templates": []}` means the engine is there and the organization has no template yet.

## 2. The key the engine runs as

A run started by a D&R rule has no person behind it. It runs as an **organization API
key** stored as a Hive secret and named in the settings record. Without one, rule starts
are refused (`reason_code: no_policy_identity`).

The key needs what the template below does: read the detection, the lookup and the
sensor, isolate and tag the host, and write the case.

```bash
limacharlie api-key create --name ie-runner \
  --permissions insight.det.get,insight.evt.get,lookup.get,sensor.get,sensor.task,sensor.tag,ext.request,investigation.get,investigation.set \
  --store-secret ie-runner --oid "$OID"
```

Only an organization API key works; a user API key is refused when the run starts
(`identity_secret_unavailable`). The key's own platform permissions are the limit on what
any run can do: give it what your templates need and nothing more.
[Permissions](permissions.md) lists what each operator and action needs, and
`limacharlie investigate settings get` checks a template's key before its first run
(`template_readiness`).

## 3. The settings record

The organization's settings are one record, `investigation_policy/default`. Save this as
`settings.yaml`:

```yaml
# investigation_policy/default
paused: false
circuit_breaker:
  per_hour: 20
  per_run: 5
identity:
  default: hive://secret/ie-runner
limits:
  max_parallel_runs: 100
case: create
```

```bash
limacharlie hive set --hive-name investigation_policy --key default \
  --input-file settings.yaml --enabled --oid "$OID"
limacharlie investigate settings get --oid "$OID"
```

`settings get` shows what the engine enforces. Read `identity_readiness` (is the key
usable) and `warnings` (empty when the record parsed). Every field is described in
[Settings](settings.md).

## 4. The lookup the template reads

The template decides on a list you own. Create the lookup `banned-software` with the
SHA-256 of the test binary you will run:

```bash
cat > banned.yaml <<'EOF'
lookup_data:
  "<sha256 of the test binary>": {mtd: "test entry"}
EOF
limacharlie hive set --hive-name lookup --key banned-software \
  --input-file banned.yaml --enabled --oid "$OID"
```

## 5. The template

Save as `banned-binary.yaml`:

```yaml
# investigation_plan/banned-binary
status: draft
version: 1
description: "Isolate the host for one minute and tag it for a day when the binary that raised the detection is on our banned software list."
applies_to:
  rule: ['general.banned-binary-exec']
starts_from: detection
gather:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary {trigger.hash} is on our banned software list."
act:
  - do: contain.network
    target: '$trigger.sid'
    on_rules: [banned_binary]
    approval: none
    lease: 1m
    on_lease_end: release
  - do: tag.add
    target: '$trigger.sid'
    attrs: {tag: 'ie:banned-binary', ttl: 86400}
    on_rules: [banned_binary]
    approval: none
case:
  mode: create
  severity: {escalated_by_rule: high, default: medium}
```

Read it as: fetch the detection, look its hash up in your list; if it is there, isolate
the host on its own (`approval: none`) for one minute and then release it
(`on_lease_end: release`), and tag the host for 24 hours.

Validate it, then save it. `templates save` always writes a draft:

```bash
limacharlie investigate templates validate --file banned-binary.yaml --oid "$OID"
limacharlie investigate templates save banned-binary --file banned-binary.yaml --oid "$OID"
```

`validate` prints `valid: true` and, under `actions`, each entry with
`acts_alone_possible`. A draft only suggests: started now, its actions would be recorded
`suggested` and nothing would happen to the host. Optionally test it on past
detections first ([Test on past alerts](templates.md#test-on-past-alerts)).

## 6. A person makes it active

Making a template active is the permission to act. Read the template, then:

```bash
limacharlie investigate templates promote banned-binary --confirm --oid "$OID"
```

The Hive accepts an active template only from a person signed in as a user (the console,
or the CLI after `limacharlie auth login --oauth`), not from an API key, unless the
settings record carries the `allow-api-key-promotion` tag (see
[Permissions](permissions.md#active-templates-can-only-be-written-by-a-person)).

## 7. The D&R rule that starts it

Save as `rule.yaml`. It reports any process started from the test path and starts the
template on that detection:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: \ie-walkthrough-test.exe
  case sensitive: false
respond:
  - action: report
    name: banned-binary-exec
  - action: start investigation
    template: banned-binary
    urgency: high
```

```bash
limacharlie dr set --key banned-binary-exec --input-file rule.yaml --enabled --oid "$OID"
```

`--enabled` matters: a new rule (and a new record in most hives) is created disabled
without it, and a disabled rule or lookup looks exactly like one that never matches. The run
is tied to the detection the `report` just raised. See
[Automatic Starts](automation.md).

## 8. Fire it and watch

Copy the test binary to the test host as `ie-walkthrough-test.exe` and run it. Then:

```bash
limacharlie investigate runs list --template banned-binary --limit 1 --oid "$OID"
limacharlie investigate runs get <run_id> --oid "$OID"
```

What you see, in order:

1. The run's `verdict.outcome` is `escalated_by_rule`, `decided_by.rule` is
   `banned_binary` and `decided_by.say` is the rule's sentence.
2. Under `actions`, the `contain.network` action goes `proposed`, `executing`, `active`,
   with `automatic: true` and `lease_until` one minute after it took effect. The
   `tag.add` action is `confirmed` (a tag holds no lease; it lasts its `ttl`).
3. One minute later the isolation is `reverted`, with `undo_cause: lease_expiry`. The host
   is back on the network.
4. The case holds the outcome sentence, the evidence and both actions.

`runs get` also shows how long each part took (`detection_to_accepted_ms`,
`queue_wait_ms`, `time_to_verdict_ms`). See [Concepts](concepts.md#runs).

## 9. Undo

The tag stays for a day. Undo it now (the action is reversible and in effect, so
`eligibility.revert` is true):

```bash
limacharlie api "investigate/$OID/runs/<run_id>/actions/<tag action id>/revert" \
  -X POST --json -F note="walkthrough cleanup" --oid "$OID"
```

The action becomes `reverted` and the tag is removed from the host. The same call on the
isolation while it is still `active` would release the host before the lease ends.

To undo everything the engine did on its own in one call, use the bulk undo (up to 100
actions per call):

```bash
curl -s -X POST "$API/investigate/$OID/actions/automatic/undo" \
  -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
  -d '{"ids": ["<action id>", "<action id>"], "was_engine_wrong": false}'
```

`was_engine_wrong` is required: `false` is a plain undo, `true` records that the engine
was wrong (a person signed in as a user only). Each result says its own state. Every undo, approval and denial is an entry in the
organization's audit log, filed under who decided it. See
[Actions, Approvals and Undo](actions.md).

## 10. The same with an approval

Servers should not be isolated without a person. Change the `approval` of the isolation
entry and add the step its condition reads (this version also drops the `tag.add` entry, to
keep the example short):

```yaml
# investigation_plan/banned-binary
status: draft
version: 2
description: "Isolate the host for one minute when the binary that raised the detection is on our banned software list; a server waits for a person."
applies_to:
  rule: ['general.banned-binary-exec']
starts_from: detection
gather:
  trigger:
    op: detection.get
    args: {detect_id: $detection_id, window: [-29d, now]}
  banned:
    why: "Is this binary on our banned software list?"
    op: lookup.get
    args: {name: banned-software, keys: ['$trigger.hash']}
  host:
    why: "Is this host a server?"
    op: sensor.get
    args: {sid: '$trigger.sid'}
rules:
  escalate:
    - id: banned_binary
      when: 'banned.found'
      say: "The binary {trigger.hash} is on our banned software list."
act:
  - do: contain.network
    target: '$trigger.sid'
    on_rules: [banned_binary]
    approval: {when: '"server" in host.tags'}
    approval_timeout: 30m
    lease: 1m
    on_lease_end: release
case:
  mode: create
  severity: {escalated_by_rule: high, default: medium}
```

`approval: {when: ...}` waits for a person when the condition holds **or is unknown**,
and acts alone only when it is false. If the sensor read fails, the isolation waits.

A draft never replaces an active template, so a person replaces it explicitly:

```bash
limacharlie investigate templates validate --file banned-binary.yaml --oid "$OID"
limacharlie investigate templates save banned-binary --file banned-binary.yaml \
  --overwrite --status active --oid "$OID"
```

An AI agent must not pass `--status active`: it saves under a new name and a person
decides. The run identity needs `sensor.get`, which step 2 granted.

Tag the test host `server`, run the binary again, then:

```bash
limacharlie investigate actions list --state awaiting_approval --oid "$OID"
```

The isolation is `awaiting_approval` with `approval_reason: approval_condition` and a
`deadline` 30 minutes out. Approve it:

```bash
limacharlie investigate actions approve <run_id> <action_id> --oid "$OID"
```

It executes, stays in effect for one minute and is released. Deny instead
(`actions deny ... --note "..."`) and nothing happens to the host; leave it and it
expires at its deadline (`expired_reason: approval_timeout`).

## 11. The emergency stop

```bash
limacharlie investigate settings pause --oid "$OID"
```

While paused, nothing acts alone: an action that would have acted alone waits for a
person (`approval_reason: paused`). Runs still investigate, and approvals, undos and lease
ends still work. `settings resume` lifts it; actions that waited keep waiting for a person.
If Git Sync manages the settings record, set `paused` in git instead, or the next sync
overwrites it. See [Settings](settings.md#pause).

## Next

- [Plan Templates](templates.md) for every key of a template.
- [Actions, Approvals and Undo](actions.md) for `hold` and "check again" at the end of a
  lease: the automatic rollback of a false positive.
- [The Run Queue](run-queue.md) for what happens under a burst of alerts.
- [Custom Code and AI Agents](custom-code.md) to call your own Playbooks and AI agents.
