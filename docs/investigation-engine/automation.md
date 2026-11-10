# Automatic Starts

Runs usually start from a person, an API call or an AI agent. Two entry points start
them **without a person**: a D&R rule, and a new case. A run without a person has no
token of its own, so it executes with the identity named in the organization's
[policy](policies.md#run-identity), and it can only use **active** templates.

## Before you enable either

1. **A policy identity.** Set `identity.default` in the `default` investigation policy
   to a Hive secret holding an organization API key. Without it, every automatic start
   is refused with a message that names `identity.default`.
2. **At least one active template** whose `applies_to` matches what you expect, or a
   rule that names its template. A draft is never used.
3. **Autonomy you are comfortable with.** Start with every class in `suggest`. See
   [Policies and Autonomy](policies.md).

## D&R rules: `start investigation`

The [`start investigation`](../8-reference/response-actions.md#start-investigation)
response action starts a run for the detection the rule just reported.

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
  created, and the detection id is the run's idempotency key: one detection starts one
  run.
- The run's trigger carries the detection's category and priority and the rule's tags,
  with `source: dr-rule` and `rule: general.<rule record name>`. Those are what
  `applies_to` matches on. A rule never sends a severity.
- With no `template`, the engine picks the **active** template whose `applies_to` best
  matches. With no match, no run starts and the detection is still reported.
- The action sends only what you list under `inputs`, plus the detection id. A template
  that takes `detection_id` and derives everything else works unchanged. See
  [Run inputs](templates.md#run-inputs).
- Starting a run never delays the rule: the request is sent in the background and a
  failure never blocks the detection.

The full parameter list, limits and behavior are in the [response actions
reference](../8-reference/response-actions.md#start-investigation).

!!! tip "Pick `coalesce_key` on purpose"
    Alerts with the same `coalesce_key` join the run that is already open instead of
    starting another. The default, `sid:<sensor id>`, makes a burst of alerts on one
    host one investigation. A key built from a field some events lack renders the same
    text for all of them and joins everything into one run.

## The case trigger

A new case that somebody else opens can start a run **in that case**. The engine reads
case events from the case audit feed, so there is no polling and nothing to set up per
organization. It is configured in the `default` investigation policy:

```yaml
# investigation_policy/default
triggers:
  case_created:
    severities: [high, critical]   # required: which severities start a run
    tags: [phishing]               # optional: the case must carry at least one of these
    template: auto                 # a template name, or auto (chosen by applies_to)
```

| Field | Meaning |
|---|---|
| `severities` | One or more of `critical`, `high`, `medium`, `low`, `info`. Required, unless `enabled: false`. |
| `tags` | Optional. A case starts a run only if it carries any one of these tags. |
| `template` | A template name, or `auto` (the default) to choose the active template whose `applies_to` matches the case (`severity`, `tag`, `detect_cat`, `source`). Only the `default` record may set it. |
| `enabled` | Set `false` to switch the trigger off. |

Behavior:

- **The run attaches to that case.** It never creates a second case. It writes its
  entities, telemetry references, findings and a proposed classification into the case.
  The case is the human record; the run is the machine record.
- **One case starts at most one run**, however many times the event is delivered.
- **Cases the engine wrote never start a run**, so it cannot trigger itself.
- The run's inputs are the case id and, if the case already has a detection, the
  detection id of its first one.
- **Other policy records can only narrow it.** A matching record can intersect the
  severities and tags or set `enabled: false`. It cannot enable the trigger, widen it,
  or name the template.
- Only an **active** template can start from a case. If nothing applies, or there is no
  policy identity, the event is acknowledged and logged with the reason, and no run
  starts.
- A case is created before the rules and people that tag it act. The tags are read a few
  seconds after creation, so a tag filter sees the tags the case had then. If you need
  later tags, filter on severity instead.

## What you see

A run started this way appears in the Runs list like any other, with **Started by**
shown as **Automation**. Its case has the run linked, and its actions follow the policy.
If the policy asks for notifications, [events](policies.md#notifications) are written to
the organization's audit log.
