# Stateful Rules

## Overview

> It's recommended to first read [Detection & Response rules](writing-and-testing-rules.md) before diving into stateful rules.

In LimaCharlie, a Stateful Rule tracks and remembers the state of past events to make decisions based on historical context. Unlike stateless rules, which evaluate events in isolation, stateful rules can detect patterns over time, such as multiple failed logins within an hour. This enables more complex and accurate detection, allowing users to trigger actions only when specific conditions are met across multiple events or timeframes.

Events in LimaCharlie have well-defined relationships to one another using `routing/this`, `routing/parent`, `routing/target`, and can even be implicitly related by occurring in a similar timeframe. The relation context can be useful for writing more complex rules.

These are called "stateful" rules.

## Detecting Children / Descendants

To detect events in a tree you can use the following parameters:

  * `with child`: matches children of the initial event

  * `with descendant`: matches descendants (children, grandchildren, etc.) of the initial event




Aside from how deep they match, the `with child` and `with descendant` parameters operate identically: they declare a nested stateful rule.

For example, let's detect a `cmd.exe` process spawning a `calc.exe` process:
    
    
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
    

Simply put, this will detect:
    
    
    cmd.exe --> calc.exe
    

Because it uses `with child` it will not detect:
    
    
    cmd.exe --> firefox.exe --> calc.exe
    

To do that, we could use `with descendant` instead.

## Detecting Proximal Events

To detect repetition of events close together on the same Sensor, we can use `with events`.

The `with events` parameter functions very similarly to `with child` and `with descendant`: it declares a nested stateful rule.

For example, let's detect a scenario where `5` bad login attempts occur within `60` seconds.
    
    
    event: WEL
    op: is windows
    with events:
      event: WEL
      op: is
      path: event/EVENT/System/EventID
      value: '4625'
      count: 5
      within: 60
    

The top-level rule filters down meaningful events to `WEL` ones sent from Windows sensors using the `is windows` operator, and then it declares a stateful rule inside `with events`. It uses `count` and `within` to declare a suitable timespan to evaluate matching events.

## Stateful Rules

Stateful rules — the rules declared within `with child`, `with descendant` or `with events` — have full range. They can do anything a normal rule might do, including declaring nested stateful rules or using `and`/`or` operators to write more complex rules.

Here's a stateful rule that uses `and` to detect a specific combination of child events:
    
    
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
    

The above example is looking for an `outlook.exe` process that spawns a `chrome.exe` process and drops a `.ps1` (powershell) file to disk. Like this:
    
    
    outlook.exe
    |--+--> chrome.exe
    |--+--> .ps1 file
    

### Counting Events

Rules declared using `with child` or `with descendant` also have the ability to use `count` and `within` to help scope the events it will statefully match.

For example, a rule that matches on Outlook writing 5 new `.ps1` documents within 60 seconds:
    
    
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
    

### Choosing Event to Report

A reported detection will include a copy of the event that was detected. When writing detections that match multiple events, the default behavior will be to include a copy of the initial parent event.

In many cases it's more desirable to get the latest event in the chain instead. For this, there's a `report latest event: true` flag that can be set. Piggy-backing on the earlier example:
    
    
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
    

The event returned in the detection will be either the `chrome.exe` `NEW_PROCESS` event or the `.ps1` `NEW_DOCUMENT` event, whichever was last. Without `report latest event: true` being set, it would default to including the `outlook.exe` `NEW PROCESS` event.

### Flipping back to stateless

Since all operators under the `with child` and `with descentant` are operating in stateful mode (meaning all the nodes don’t have to match a single event, but can match over multiple events), sometimes you want a operator and the operators underneath to flip back to stateless mode where they must match a single event. You can achieve this by setting `is stateless: true` in the operator like:
    
    
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

## Caveats

### Testing Stateful Rules

Stateful rules are forward-looking only and changing a rule will reset its state.

Practically speaking, this means that if you change a rule that detects `excel.exe -> cmd.exe`, `excel.exe` will need to be relaunched while the updated rule is running for it to then begin watching for `cmd.exe`.

### Using Events in Actions

Using `report` to report a detection works according to the Choosing Event to Report section earlier. Other actions have a subtle difference: they will _always_ observe the latest event in the chain.

Consider the `excel.exe -> cmd.exe` example. The `cmd.exe` event will be referenced inside the response action if using lookbacks (i.e. `<<routing/this>>`). If we wanted to end the `excel.exe` process (and its descendants), we would write a `task` that references the parent of the current event (`cmd.exe`):
    
    
    - action: task
      command: deny_tree <<routing/parent>>
    

