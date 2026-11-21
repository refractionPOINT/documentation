# Automatic Starts

Runs usually start from a person, an API call or an AI agent. A **D&R rule** starts
them without a person, with the
[`start investigation`](../8-reference/response-actions.md#start-investigation)
response action: on a detection the rule reports, or on a new case. This is the only
way a run starts without a person; the engine itself listens to nothing.

A run without a person has no token of its own, so it executes with the identity
named in the organization's [policy](policies.md#run-identity), and it can only use
**active** templates.

## Before you add a rule

1. **A policy identity.** Set `identity.default` in the `default` investigation policy
   to a Hive secret holding an organization API key, or give the template its own
   `identity.templates.<name>.default`. Without one every start is refused
   (`no_policy_identity`). See [step 3 of the walkthrough](walkthrough.md#3-the-run-identity-an-api-key-the-policy-names).
2. **An active template** whose `applies_to` matches what the rule sends, or a rule
   that names its template. A draft is never used (`template_draft`).
3. **Autonomy you are comfortable with.** Start with every class in `suggest`.

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
- **One detection starts at most one run**: the detection id is the run's idempotency
  key.
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
- Starting a run never delays the rule and never fails the detection.

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
- The engine reads the case's severity, tags and detection with the policy's identity,
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
run linked, and its actions follow the policy. If the policy asks for notifications,
[events](policies.md#notifications) are written to the organization's audit log.
