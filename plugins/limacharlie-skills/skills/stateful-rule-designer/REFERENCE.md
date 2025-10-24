# Stateful Rule Designer - Complete Reference

This document provides comprehensive technical details for all stateful rule operators and parameters.

## Table of Contents

- [Stateful Operators](#stateful-operators)
- [Parameters Reference](#parameters-reference)
- [Nested Stateful Logic](#nested-stateful-logic)
- [Event Relationships](#event-relationships)
- [Response Action Behavior](#response-action-behavior)
- [Memory and State Management](#memory-and-state-management)

## Stateful Operators

### with_child

Matches events that are **direct children** of the initial event. The child must be one level deep in the process tree.

#### Syntax

```yaml
detect:
  event: <EVENT_TYPE>
  # ... parent matching conditions ...
  with child:
    event: <EVENT_TYPE>  # Optional but recommended
    # ... child matching conditions ...
    count: <NUMBER>      # Optional: require N children
    within: <SECONDS>    # Optional: time window for count
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event` | String | Recommended | Event type to match (e.g., NEW_PROCESS, NETWORK_CONNECTIONS) |
| `op` | String | Yes | Operator for matching condition |
| `count` | Integer | No | Number of matching children required (default: 1) |
| `within` | Integer | No | Time window in seconds for count threshold |

#### Behavior

- Matches only immediate children (one level deep)
- If `count` is specified, requires that many children within time window
- If no `event` type specified, checks all child events (performance impact!)
- State is maintained until match found or parent process exits

#### Multiple Child Conditions

Use `and`/`or` operators to match multiple children:

```yaml
detect:
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
respond:
  - action: report
    name: Outlook Spawning Chrome and PowerShell Script
```

**Detection pattern**:
```
outlook.exe
├── chrome.exe      (child 1)
└── script.ps1      (child 2)
```

Both children must be observed for the rule to match.

### with_descendant

Matches events that are **descendants at any depth** (children, grandchildren, great-grandchildren, etc.) of the initial event.

#### Syntax

```yaml
detect:
  event: <EVENT_TYPE>
  # ... parent matching conditions ...
  with descendant:
    event: <EVENT_TYPE>  # Optional but recommended
    # ... descendant matching conditions ...
    count: <NUMBER>      # Optional: require N descendants
    within: <SECONDS>    # Optional: time window for count
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event` | String | Recommended | Event type to match |
| `op` | String | Yes | Operator for matching condition |
| `count` | Integer | No | Number of matching descendants required (default: 1) |
| `within` | Integer | No | Time window in seconds for count threshold |

#### Behavior

- Matches descendants at any depth in the process tree
- More resource-intensive than `with child` as it tracks entire tree
- If `count` is specified, requires that many descendants within time window
- State is maintained until match found or parent process exits

#### Example: Counting Descendants

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: explorer.exe
  case sensitive: false
  with descendant:
    event: NETWORK_CONNECTIONS
    op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    count: 10
    within: 300
respond:
  - action: report
    name: Explorer Process Tree Making Many External Connections
    priority: 3
```

**Detection pattern**: Any process in the Explorer process tree makes 10+ external network connections within 5 minutes.

### with_events

Detects **repetition of events** close together in time on the same sensor. Unlike `with child` and `with descendant`, this does not track process relationships but rather event proximity.

#### Syntax

```yaml
detect:
  event: <EVENT_TYPE>
  # ... initial event matching conditions ...
  with events:
    event: <EVENT_TYPE>
    # ... event matching conditions ...
    count: <NUMBER>      # Required
    within: <SECONDS>    # Required
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event` | String | Yes | Event type to match |
| `op` | String | Yes | Operator for matching condition |
| `count` | Integer | Yes | Number of matching events required |
| `within` | Integer | Yes | Time window in seconds |

#### Behavior

- Counts events on the same sensor within a time window
- Does not track process relationships
- Ideal for threshold-based detections (brute force, scanning)
- State is maintained for the duration of `within` window

#### Example: Brute Force Detection with User Context

```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: and
    rules:
      - op: is
        path: event/EVENT/System/EventID
        value: '4625'
      - op: is
        path: event/EVENT/System/Channel
        value: Security
      - op: exists
        path: event/EVENT/EventData/TargetUserName
        truthy: true
    count: 10
    within: 300
respond:
  - action: report
    name: "Brute Force Attack - {{ .event.EVENT.EventData.TargetUserName }}"
    priority: 4
    metadata:
      mitre: T1110
      description: 10+ failed logins in 5 minutes
    suppression:
      is_global: false
      keys:
        - '{{ .event.EVENT.EventData.TargetUserName }}'
        - '{{ .routing.sid }}'
      max_count: 1
      period: 1h
```

## Parameters Reference

### count

Specifies the number of matching child/descendant/proximal events required for detection.

**Syntax**: `count: <INTEGER>`

**Used with**: `with child`, `with descendant`, `with events`

**Default**: 1 (for `with child` and `with descendant`)

**Examples**:
- `count: 1` - Single occurrence (default)
- `count: 5` - Five occurrences
- `count: 10` - Ten occurrences

**Note**: For `with events`, `count` is **required**.

### within

Specifies the time window in seconds for counting events.

**Syntax**: `within: <INTEGER>`

**Used with**: `with child`, `with descendant`, `with events` (when `count` > 1)

**Unit**: Seconds

**Examples**:
- `within: 30` - 30 seconds
- `within: 60` - 1 minute
- `within: 300` - 5 minutes
- `within: 3600` - 1 hour

**Performance Tip**: Keep time windows as short as possible to minimize memory usage.

### report latest event

Controls which event is reported when a stateful rule matches.

**Syntax**: `report latest event: <BOOLEAN>`

**Used with**: `with child`, `with descendant`

**Default**: `false` (report parent event)

**Values**:
- `true` - Report the child/descendant event
- `false` - Report the parent event (default)

**Example**:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  report latest event: true  # Report chrome.exe event
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: chrome.exe
    case sensitive: false
respond:
  - action: report
    name: Outlook Spawning Chrome
```

**When to use each**:

- **Report Parent** when:
  - You want context about what initiated the chain
  - The parent process is the suspicious actor
  - Example: Malicious document spawning legitimate processes

- **Report Latest** when:
  - The child/descendant is the malicious component
  - You need details about the final outcome
  - Example: Legitimate process spawning malicious child

**Important**: Response actions (like `task`) **always** use the latest event in the chain, regardless of this setting.

### is stateless

Forces sub-rules to match within the same event rather than across different events.

**Syntax**: `is stateless: <BOOLEAN>`

**Used with**: `and`, `or` operators within stateful contexts

**Default**: `false` (stateful matching)

**Values**:
- `true` - All sub-rules must match the same event
- `false` - Sub-rules can match different events (default in stateful context)

#### The Problem Without is stateless

```yaml
detect:
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
        value: evil.exe
        case sensitive: false
      - op: contains
        path: event/COMMAND_LINE
        value: malicious-flag
        case sensitive: false
```

**Problem**: This could match:
- Child 1: `evil.exe`
- Child 2: Any process with `malicious-flag` in command line

These are **two different events**.

#### The Solution

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  with child:
    op: and
    is stateless: true  # Both conditions must match the same child event
    rules:
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: evil.exe
        case sensitive: false
      - op: contains
        path: event/COMMAND_LINE
        value: malicious-flag
        case sensitive: false
respond:
  - action: report
    name: Outlook Spawning Evil.exe with Malicious Flag
```

**Now requires**: A **single** child event that is both `evil.exe` AND has `malicious-flag` in the command line.

#### When to Use is stateless: true

Use `is stateless: true` when you need:

1. **Atomic Conditions**: Multiple properties must exist on the same event
2. **Precision**: Avoid false positives from conditions matching different events
3. **Performance**: Stateless matching is faster

#### Example: Precise Process Detection

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: explorer.exe
  case sensitive: false
  with descendant:
    op: and
    is stateless: true
    rules:
      - event: NEW_PROCESS
        op: ends with
        path: event/FILE_PATH
        value: cmd.exe
        case sensitive: false
      - op: contains
        path: event/COMMAND_LINE
        value: /c powershell
      - op: contains
        path: event/COMMAND_LINE
        value: -enc
respond:
  - action: report
    name: Explorer -> CMD Launching Encoded PowerShell
    priority: 4
```

**Requirement**: A **single** CMD process with both `/c powershell` AND `-enc` in the command line.

## Nested Stateful Logic

Stateful rules can be nested to create complex multi-stage detections. Each level adds another layer of stateful tracking.

### Two-Level Example

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  with descendant:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: powershell.exe
    case sensitive: false
    with descendant:
      event: NETWORK_CONNECTIONS
      op: is public address
      path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      count: 3
      within: 60
respond:
  - action: report
    name: Outlook -> PowerShell -> External Network Activity
    priority: 5
```

**Detection pattern**:
```
outlook.exe
└── powershell.exe
    └── 3+ external network connections within 60 seconds
```

### Combining Different Stateful Operators

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: svchost.exe
  case sensitive: false
  with child:
    event: NEW_PROCESS
    op: exists
    path: event/FILE_PATH
    with events:
      event: FILE_GET_REP
      op: is
      path: event/FILE_PATH
      value: C:\sensitive\data.txt
      count: 10
      within: 60
respond:
  - action: report
    name: Svchost Child Process Repeatedly Accessing Sensitive File
    priority: 4
```

**Detection pattern**: Svchost spawns a child that accesses `data.txt` 10+ times in 60 seconds.

### Multiple Child Patterns with Nesting

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: winword.exe
  case sensitive: false
  with child:
    op: or
    rules:
      # Pattern 1: PowerShell with network activity
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
        with descendant:
          event: NETWORK_CONNECTIONS
          op: is public address
          path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      # Pattern 2: WScript with file creation
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: wscript.exe
        case sensitive: false
        with descendant:
          event: NEW_DOCUMENT
          op: ends with
          path: event/FILE_PATH
          value: .exe
respond:
  - action: report
    name: Word Spawning Suspicious Script with Malicious Behavior
    priority: 5
```

**Detection pattern**: Word spawns either:
1. PowerShell that makes external connections, OR
2. WScript that creates executable files

### Nesting Guidelines

1. **Limit Depth**: Avoid more than 2-3 levels of nesting
2. **Performance**: Each level increases memory usage and CPU overhead
3. **Complexity**: Deeper nesting makes rules harder to understand and debug
4. **Testing**: Thoroughly test nested rules with synthetic events

**Acceptable**: 2 levels
```yaml
detect:
  event: NEW_PROCESS
  with child:
    event: NEW_PROCESS
    with descendant:
      event: NETWORK_CONNECTIONS
```

**Avoid**: 4+ levels
```yaml
detect:
  event: NEW_PROCESS
  with child:
    with descendant:
      with descendant:
        with descendant:
          # Too complex!
```

## Event Relationships

Events are related through routing metadata. Stateful rules automatically track these relationships.

### Routing Fields

| Field | Description | Example |
|-------|-------------|---------|
| `routing/this` | Current event's atom ID | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `routing/parent` | Parent event's atom ID | `12345678-90ab-cdef-1234-567890abcdef` |
| `routing/sid` | Sensor ID | `sensor-12345` |
| `routing/event_type` | Event type name | `NEW_PROCESS` |
| `routing/hostname` | Hostname of sensor | `WORKSTATION-01` |

### Process Tree Relationships

Process trees are tracked through the `routing/parent` field:

```
Process A (atom: AAA)
├── Process B (atom: BBB, parent: AAA)
│   └── Process C (atom: CCC, parent: BBB)
└── Process D (atom: DDD, parent: AAA)
```

- `with child` tracks immediate children (B and D are children of A)
- `with descendant` tracks all descendants (B, C, D are descendants of A)

### Using Routing in Response Actions

```yaml
respond:
  - action: task
    command: deny_tree <<routing/this>>    # Kill the current process
  - action: task
    command: deny_tree <<routing/parent>>  # Kill the parent process
```

## Response Action Behavior

Response actions in stateful rules have specific behaviors regarding which event they operate on.

### Key Principle

**Response actions always use the LATEST event in the chain**, regardless of the `report latest event` setting.

### Example: Killing a Malicious Child Process

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: excel.exe
  case sensitive: false
  with child:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: cmd.exe
    case sensitive: false
respond:
  - action: report
    name: Excel Spawning CMD
  - action: task
    # This references the cmd.exe event (latest in chain)
    command: deny_tree <<routing/this>>
```

### Example: Killing the Parent Process

If you want to kill the parent instead:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: excel.exe
  case sensitive: false
  with child:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: cmd.exe
    case sensitive: false
respond:
  - action: report
    name: Excel Spawning CMD
  - action: task
    # Use routing/parent to reference the excel.exe event
    command: deny_tree <<routing/parent>>
```

### Available Routing References

| Reference | Points To | Use Case |
|-----------|-----------|----------|
| `<<routing/this>>` | Latest event in chain | Kill the malicious child/descendant |
| `<<routing/parent>>` | Parent event | Kill the initiating process |

### Suppression in Stateful Rules

Always use suppression when triggering sensor commands to prevent runaway actions:

```yaml
respond:
  - action: task
    command: history_dump
    investigation: suspicious-chain
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
```

This prevents the same detection from triggering multiple sensor commands.

## Memory and State Management

Understanding how stateful rules manage memory is crucial for performance optimization.

### What State is Maintained

Each stateful rule maintains:

1. **Parent Event State**: The initial event that started the stateful matching
2. **Child/Descendant Tracking**: References to related events
3. **Counters**: For `count` and `within` parameters
4. **Timeouts**: For `within` time windows

### When State is Cleared

Stateful rule state is cleared when:

1. **Rule is Modified**: Any change to the rule resets all state
2. **Match is Found**: State is released after the rule matches
3. **Timeout Expires**: After `within` duration passes
4. **Process Exits**: When the parent process terminates
5. **Sensor Disconnects**: When the sensor goes offline

### State Lifecycle Example

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  with child:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: cmd.exe
    case sensitive: false
    count: 3
    within: 60
```

**Lifecycle**:
1. Outlook.exe launches - state created
2. cmd.exe spawns (1/3) - counter incremented
3. cmd.exe spawns (2/3) - counter incremented
4. 60 seconds pass - state cleared (timeout)
5. Outlook launches again - new state created

### Memory Impact by Rule Type

| Rule Type | Memory Usage | CPU Usage | State Duration |
|-----------|--------------|-----------|----------------|
| Stateless | Minimal | Low | None |
| with_child (count=1) | Low | Low | Until child found |
| with_child (count=10) | Medium | Medium | Until 10 children or timeout |
| with_descendant | Medium-High | Medium | Until descendant found |
| with_events | Medium | Medium | Duration of `within` window |
| Nested stateful | High | High | Cumulative of all levels |

### Forward-Looking Only

**Important**: Stateful rules are **forward-looking only**.

If you modify a rule that detects `excel.exe -> cmd.exe`, Excel must be launched **after** the rule is updated to begin tracking.

**Example**:
1. Excel is running (before rule deployed)
2. Rule deployed: `excel.exe -> cmd.exe`
3. Excel spawns CMD - **NO MATCH** (Excel was already running)
4. Excel is restarted
5. Excel spawns CMD - **MATCH** (Excel launched after rule was active)

### Best Practices for Memory Management

1. **Filter Early**: Reduce the number of parent events being tracked
2. **Specify Event Types**: Avoid checking all event types
3. **Short Time Windows**: Minimize state retention duration
4. **Use Platform Filters**: Reduce the event set early
5. **Avoid Deep Nesting**: Limit to 2-3 levels maximum
6. **Monitor Performance**: Watch for memory/CPU impact in production

---

This reference provides complete technical details for stateful rule operators. For practical examples, see [EXAMPLES.md](EXAMPLES.md). For testing and troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
