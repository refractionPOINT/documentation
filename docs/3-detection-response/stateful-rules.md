# Stateful Rules

## Overview

> Read [Detection & Response rules](tutorials/writing-testing-rules.md) before you continue with stateful rules.

In LimaCharlie, a Stateful Rule keeps the state of past events and makes decisions from that history. A stateless rule evaluates each event alone. A stateful rule detects patterns over time, such as many failed logins in one hour. This gives more complex and more accurate detection. Users can trigger actions only when specific conditions occur across many events or timeframes.

Events in LimaCharlie have defined relationships to each other through `routing/this`, `routing/parent`, and `routing/target`. Two events can also have an implicit relation when they occur in a similar timeframe. This relation context helps you write more complex rules.

These are called "stateful" rules.

## Detecting Children / Descendants

To detect events in a tree, use these parameters:

- `with child`: matches children of the initial event
- `with descendant`: matches descendants (children, grandchildren, etc.) of the initial event

The `with child` and `with descendant` parameters are the same, except for the depth that they match. Both declare a nested stateful rule.

For example, this rule detects a `cmd.exe` process that spawns a `calc.exe` process:

```yaml
# Detect initial event
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: cmd.exe
case sensitive: false
with child: # Wait for child matching this nested rule
  op: ends with
  event: NEW_PROCESS
  path: event/FILE_PATH
  value: calc.exe
  case sensitive: false
```

This detects:

```batch
cmd.exe --> calc.exe
```

Because it uses `with child`, it does not detect:

```batch
cmd.exe --> firefox.exe --> calc.exe
```

To detect that chain, use `with descendant` instead.

## Detecting Proximal Events

To detect repeated events close together on the same Sensor, use `with events`.

The `with events` parameter works like `with child` and `with descendant`. It declares a nested stateful rule.

For example, this rule detects `5` bad login attempts in `60` seconds.

```yaml
event: WEL
op: is windows
with events:
  event: WEL
  op: is
  path: event/EVENT/System/EventID
  value: '4625'
  count: 5
  within: 60
```

The top-level rule uses the `is windows` operator to keep only the `WEL` events from Windows sensors. It then declares a stateful rule inside `with events`. The stateful rule uses `count` and `within` to set the timespan for the events that match.

## Stateful Rules

Stateful rules are the rules that you declare in `with child`, `with descendant`, or `with events`. They have full range and can do everything that a normal rule does. They can declare nested stateful rules, and they can use the `and` and `or` operators for more complex rules.

This stateful rule uses `and` to detect a specific combination of child events:

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
with child:
  op: and
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: chrome.exe
      case sensitive: false
    - op: ends with
      event: NEW_DOCUMENT
      path: event/FILE_PATH
      value: .ps1
      case sensitive: false
```

The example above looks for an `outlook.exe` process that spawns a `chrome.exe` process and writes a `.ps1` (powershell) file to disk. Like this:

```text
outlook.exe
|--+--> chrome.exe
|--+--> .ps1 file
```

### Counting Events

Rules that you declare with `with child` or `with descendant` can also use `count` and `within`. These parameters set the scope of the events that the rule matches statefully.

For example, this rule matches when Outlook writes 5 new `.ps1` documents in 60 seconds:

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
with child:
  op: ends with
  event: NEW_DOCUMENT
  path: event/FILE_PATH
  value: .ps1
  case sensitive: false
  count: 5
  within: 60
```

### Choosing Event to Report

A reported detection includes a copy of the event that the rule detected. When a detection matches many events, the default is a copy of the initial parent event.

In many cases, the latest event in the chain is more useful. To get it, set the `report latest event: true` flag. This example extends the earlier one:

```yaml
# Detection
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
report latest event: true
with child:
  op: and
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: chrome.exe
      case sensitive: false
    - op: ends with
      event: NEW_DOCUMENT
      path: event/FILE_PATH
      value: .ps1
      case sensitive: false

# Response
- action: report
  name: Outlook Spawning Chrome & Powershell
```

The detection returns the `chrome.exe` `NEW_PROCESS` event or the `.ps1` `NEW_DOCUMENT` event, whichever came last. Without `report latest event: true`, the default is the `outlook.exe` `NEW PROCESS` event.

### Flipping back to stateless

All operators under `with child` and `with descentant` operate in stateful mode. In this mode, the nodes do not have to match one single event, but can match across many events. Sometimes you want an operator and the operators below it to return to stateless mode, where they must match a single event. To do this, set `is stateless: true` in the operator:

```yaml
# Detection
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
report latest event: true
with child:
  op: and
  is stateless: true
  rules:
    - op: ends with
      event: NEW_PROCESS
      path: event/FILE_PATH
      value: evil.exe
      case sensitive: false
    - op: contains
      event: COMMAND_LINE
      path: event/FILE_PATH
      value: something-else
      case sensitive: false
```

## Caveats

### Testing Stateful Rules

Stateful rules look forward only, and a change to a rule resets its state.

For example, you change a rule that detects `excel.exe -> cmd.exe`. You must start `excel.exe` again while the new rule runs. The rule then starts to watch for `cmd.exe`.

### Using Events in Actions

The `report` action obeys the rules in [Choosing Event to Report](#choosing-event-to-report) above. Other actions are different: they *always* see the latest event in the chain.

Look at the `excel.exe -> cmd.exe` example again. A lookback in the response action (`<<routing/this>>`) refers to the `cmd.exe` event. To stop the `excel.exe` process and its descendants, write a `task` that refers to the parent of the current event (`cmd.exe`):

```yaml
- action: task
  command: deny_tree <<routing/parent>>
```

---

## See Also

- [D&R Rules Overview](index.md)
- [Writing Rules](tutorials/writing-testing-rules.md)
