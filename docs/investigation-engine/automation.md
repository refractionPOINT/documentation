# Automatic Starts

Runs usually start from a person, an API call or an AI agent. A **D&R rule** starts
them without a person, with the
[`start investigation`](../8-reference/response-actions.md#start-investigation)
response action: on a detection the rule reports, or on a new case. This is the only
way a run starts without a person; the engine itself listens to nothing.

A run without a person has no token of its own, so it executes with the identity
named in the organization's [settings](settings.md#identity), and it can only use
**active** templates. What the run does is what that template's `act` entries say.
Every start goes through the [run queue](run-queue.md): it is never dropped for load.

## Before you add a rule

1. **A run identity.** Set `identity.default` in the settings record
   (`investigation_policy/default`) to a Hive secret holding an organization API key, or
   give the template its own `identity.templates.<name>.default`. Without one every start
   is refused (`no_policy_identity`). See [step 2 of the walkthrough](walkthrough.md#2-the-key-the-engine-runs-as).
2. **An active template** whose `applies_to` matches what the rule sends, or a rule
   that names its template. A draft is never used (`template_draft`).
3. **Actions you have read.** An active template acts as its `act` entries say. Keep
   `approval: required` on the entries you are not ready to let act alone, and remember
   the [pause](settings.md#pause) if something goes wrong.

When a start is refused for a reason you can fix, a record appears on the
organization's **Errors** page under the rule's name. See
[A D&R rule matched but no investigation started](troubleshooting.md#a-dr-rule-matched-but-no-investigation-started).

## D&R rules on a detection

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
    template: suspicious-process
    urgency: high
    coalesce_key: "sid:{{ .routing.sid }}"
```

- Put the action **after** `report`. The run is tied to the detection `report` just
  created: its id, category and priority, plus the rule's tags. Without a `report`, the
  run only knows the rule name and the sensor.
- **One run per rule and detection**: a repeated delivery returns the run it already has
  (the idempotency key is `detection:<id>:<rule>`); two rules that match one detection start
  two runs, each with its own template and inputs.
- **Alerts with the same `coalesce_key` join the open run** instead of starting
  another. The default, `sid:<sensor id>`, makes a burst of alerts on one host one
  investigation. A key built from a field some events lack renders the same text for
  all of them and joins everything into one run.
- The trigger carries `source: dr-rule`, `rule: general.<rule record name>`, the
  detection's category and priority and the rule's tags; `applies_to` matches on them.
  A rule never sends a severity. With no `template`, the engine picks the active
  template whose `applies_to` best matches (see
  [How templates are chosen](templates.md#how-templates-are-chosen)).
- The run gets the detection id plus exactly the `inputs` the action lists. A template
  with `starts_from: detection` that derives everything else from the detection works
  unchanged; the action's other inputs are optional inputs (`$?name`) the template's
  steps may read. See [Where a run starts](templates.md#where-a-run-starts-starts_from).
- The detection the rule reported travels with the start, so the run reads it at
  once. When it cannot (an event restricted by resource ACL tags), the engine reads the
  detection itself and, since it may not be stored yet, retries that lookup for up to
  about two minutes before the step is `unknown(not_found)`.
- A rule with `target: detection` and no `report` starts the run on the detection it
  matched, so "investigate every detection of this category" is one rule:

    ```yaml
    detect:
      target: detection
      op: starts with
      path: cat
      value: email-security-
    respond:
      - action: start investigation
        template: mailsec-message
        inputs: {msg_uuid: '{{ .detect.event.msg_uuid }}'}
    ```

- Starting a run never delays the rule and never fails the detection. The host sends the
  start in the background; when the engine is busy or unreachable it keeps the start and
  sends it again for up to 15 minutes. A start it could not deliver in that time is
  reported on the organization's **Errors** page, never dropped silently.

### Sensors with resource ACL tags

A sensor tagged `acl:<scope>` is visible only to the members of that scope. For a run on
such a sensor, two keys must allow it:

1. **The rule** must list the scope in its `acl_scopes`, or the `start investigation`
   action is refused for events from that sensor (reported on the **Errors** page under the
   rule's name), like the other actions that send event content out of the rule. See
   [Resource ACLs](../7-administration/access/resource-acls.md).
2. **The run's key** must be a member of the scope to read the sensor's content. Otherwise
   its reads of that sensor are `unknown(acl_restricted)` and the detection read by its id
   is `unknown(not_found_or_restricted)`. `limacharlie investigate settings get` lists, per
   template, the scopes its key is outside of (`template_readiness.<template>.acl`).

The host does not hand an ACL-restricted detection over with the start, so such a run reads
the detection from storage, which can take longer than a run on an untagged sensor.

## D&R rules on a new case

Cases posts every change of a case into your organization's event stream; the event
type is the change, such as `case_created`. A rule on `case_created` with a `case`
parameter starts a run **in that case**:

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

The default library ships this rule as `investigate-high-critical-case`: read it with
the authoring kit (`sections=library`, under `rules`) and install it as a D&R rule.
It is never installed for you.

Besides the identity and an active template, the organization must be
[subscribed to Cases](../5-integrations/extensions/limacharlie/cases.md), and the
identity must be able to read the case (`investigation.get`) and write it
(`investigation.set`).

**What the rule can match.** The `case_created` event has:

| Path | Meaning |
|---|---|
| `event/case_number` | The case number, for the `case` parameter. |
| `event/by` | Who opened the case: an email for a person, a key name for an API key, `system` for a case opened automatically from a detection. |
| `event/metadata/severity` | The severity the case was opened with. |
| `event/metadata/detect_id` | The detection the case was opened for, when there is one. |
| `event/metadata/tags` | Always empty on `case_created`: tags are added afterwards and arrive on the `case_tags_updated` event. |

`event/principal_type` is `unknown` on `case_created`, so do not match on it. To skip
the cases opened automatically from a detection, require that `by` is not `system`:

```yaml
detect:
  event: case_created
  op: and
  rules:
    - {op: is, path: event/by, value: system, not: true}
    - op: or
      rules:
        - {op: is, path: event/metadata/severity, value: high}
        - {op: is, path: event/metadata/severity, value: critical}
respond:
  - action: start investigation
    case: '{{ .event.case_number }}'
```

**What happens.**

- **The run writes into that case.** No second case is opened. It adds its entities,
  telemetry references, findings and a proposed classification.
- **One run per rule and case**, however many times the event is delivered or however
  many events of that case the rule matches (the idempotency key is
  `case:<number>:<rule>`, the coalesce key `case:<number>`).
- **No loops.** The engine never starts a run for a case it wrote itself (`own_case`),
  whatever the rule matches, so a run's own writes into a case cannot start another run.
- The engine reads the case's severity, tags and detection with the run identity,
  then picks the template the rule names, or the active one whose `applies_to` matches
  (`source: case`, `severity`, `tag`, `detect_cat`, `rule`). The run's inputs are the
  case number and, when the case has one, the detection it was opened for.
- **No `report` is needed**, and a `report` before the action is not sent: reporting on
  a case event would open another case.
- The rule reads the severity the case was **opened** with: a case opened as `medium`
  and raised later does not start a run. Start those from the case page.
- If `case` renders empty or not to a case number, the action fails for that event and
  nothing is sent. Take `case` only from Cases events: its value decides which case the
  run writes into.
- Cases delivers its events on a best-effort basis. In rare cases an event is not
  delivered and no run starts; start it from the case page when you need it.

## Test a rule

A rule that uses `start investigation` can be tested with the rule tester or replay
like any other rule. A match is reported as an `investigation` action and nothing is
started.

## What you see

A run started by a rule appears in the Runs list like any other, started by
`dr-rule:<rule>` (on a detection) or `case:<case number>` (on a case). Its case has the
run linked, and its actions follow the template. If the settings ask for notifications,
[events](settings.md#notifications) go to the destinations they name.
