---
name: stateful-rule-designer
description: Use this skill when users need to create complex stateful D&R rules that correlate multiple events over time, track parent-child relationships, or count event occurrences within timeframes.
---

# Stateful Rule Designer

You are an expert in designing complex stateful Detection & Response rules in LimaCharlie. Help users create rules that correlate multiple events over time, track process tree relationships, and detect sophisticated attack patterns that require temporal or relational context.

## What are Stateful Rules?

Stateful rules track and remember the state of past events to make decisions based on historical context. Unlike stateless rules that evaluate events in isolation, stateful rules can detect patterns over time and relationships between events.

### When to Use Stateful Rules

Use stateful rules when you need to:

1. **Track Parent-Child Relationships**: Detect when a specific process spawns a particular child process
2. **Monitor Process Trees**: Identify malicious behavior across multiple generations of processes
3. **Count Event Occurrences**: Alert when an event happens N times within a timeframe
4. **Correlate Related Events**: Connect events that share a common ancestor or timeframe
5. **Detect Multi-Stage Attacks**: Identify attack chains that unfold over time

### When to Use Stateless Rules

Stateless rules are simpler and more performant. Use them when:

- A single event contains all the information needed for detection
- No temporal or relational context is required
- The detection criteria can be evaluated in isolation

**Performance Principle**: Always prefer stateless rules unless you specifically need stateful correlation.

## Stateful Rule Operators

LimaCharlie provides three stateful operators, each designed for different correlation scenarios.

### with_child: Matching Immediate Children

The `with child` operator matches events that are **direct children** of the initial event. This is useful for detecting specific parent-child process spawning patterns.

#### Basic Example: cmd.exe spawning calc.exe

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: cmd.exe
  case sensitive: false
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: calc.exe
    case sensitive: false
respond:
  - action: report
    name: CMD Spawning Calculator
```

**This detects**:
```
cmd.exe --> calc.exe  (MATCH)
```

**This does NOT detect**:
```
cmd.exe --> firefox.exe --> calc.exe  (NO MATCH - calc is a grandchild)
```

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

#### Counting Children

Add `count` and `within` parameters to require multiple occurrences:

```yaml
detect:
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
    count: 5      # At least 5 PowerShell files
    within: 60    # Within 60 seconds
respond:
  - action: report
    name: Outlook Dropping Multiple PowerShell Scripts
    priority: 4
  - action: isolate network
```

**Detection pattern**: Outlook creates 5 or more `.ps1` files within 60 seconds.

### with_descendant: Matching Any Descendant

The `with descendant` operator matches events that are **descendants at any depth** (children, grandchildren, great-grandchildren, etc.) of the initial event.

#### Basic Example: cmd.exe spawning calc.exe anywhere in tree

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: cmd.exe
  case sensitive: false
  with descendant:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: calc.exe
    case sensitive: false
respond:
  - action: report
    name: CMD Process Tree Contains Calculator
```

**This detects**:
```
cmd.exe --> calc.exe                           (MATCH - direct child)
cmd.exe --> firefox.exe --> calc.exe           (MATCH - grandchild)
cmd.exe --> firefox.exe --> notepad --> calc   (MATCH - great-grandchild)
```

#### Real-World Example: Office Document Exploit Chain

Detect Office applications spawning PowerShell, even through intermediary processes:

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: excel.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: powerpnt.exe
      case sensitive: false
  with descendant:
    event: NEW_PROCESS
    op: and
    rules:
      - op: ends with
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
      - op: or
        rules:
          - op: contains
            path: event/COMMAND_LINE
            value: -enc
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: -encodedcommand
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: downloadstring
            case sensitive: false
respond:
  - action: report
    name: Office Application Process Tree Contains Encoded PowerShell
    priority: 5
    metadata:
      mitre: T1059.001, T1566.001
      description: Office app spawned PowerShell with encoded/download commands
  - action: task
    command: deny_tree <<routing/parent>>
    investigation: office-powershell-exploit
  - action: isolate network
```

**Detection pattern**:
```
excel.exe --> wmiprvse.exe --> cmd.exe --> powershell.exe -enc ...
```

Even with multiple intermediary processes, this will detect the suspicious PowerShell execution.

#### Counting Descendants

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

### with_events: Counting Proximal Events

The `with events` operator detects **repetition of events** close together in time on the same sensor. This is ideal for threshold-based detections like brute force attempts or scanning activity.

#### Basic Example: Multiple Failed Login Attempts

```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'  # Failed logon
    count: 5
    within: 60
respond:
  - action: report
    name: Multiple Failed Login Attempts
    priority: 3
  - action: add tag
    tag: brute-force-attempt
    ttl: 3600
```

**Detection pattern**: 5 failed login events (Event ID 4625) within 60 seconds on the same sensor.

#### Advanced Example: Scanning Detection

Detect port scanning by counting multiple connection attempts:

```yaml
detect:
  event: NEW_TCP4_CONNECTION
  op: is platform
  name: windows
  with events:
    event: NEW_TCP4_CONNECTION
    op: and
    rules:
      - op: exists
        path: event/DESTINATION/PORT
      - op: is private address
        path: event/DESTINATION/IP_ADDRESS
        not: true  # External IPs only
    count: 50
    within: 30
respond:
  - action: report
    name: Potential Port Scanning Activity
    priority: 3
    metadata:
      mitre: T1046
      description: 50+ external TCP connections in 30 seconds
  - action: task
    command: history_dump
    investigation: port-scan
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 5m
```

**Detection pattern**: 50 external TCP connections within 30 seconds from the same sensor.

#### Brute Force Detection with User Context

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
  - action: add tag
    tag: under-brute-force
    ttl: 3600
```

**Detection pattern**: 10 failed logins for the same user within 5 minutes.

## Event Selection: Choosing What to Report

By default, stateful rules report the **parent event** (the initial event that triggered the stateful matching). However, you often want to report the **latest event** in the chain instead.

### Default Behavior: Report Parent Event

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
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

**Reported event**: The `outlook.exe` NEW_PROCESS event

### Report Latest Event Instead

Use `report latest event: true` to report the child/descendant:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  report latest event: true  # Report the child event
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

**Reported event**: The `chrome.exe` NEW_PROCESS event

### When to Use Each

**Report Parent** when:
- You want context about what initiated the chain
- The parent process is the suspicious actor
- Example: Malicious document spawning legitimate processes

**Report Latest** when:
- The child/descendant is the malicious component
- You need details about the final outcome
- Example: Legitimate process spawning malicious child

### Using Events in Response Actions

**Important**: Response actions (like `task`) always use the **latest event** in the chain, regardless of the `report latest event` setting.

#### Example: Killing a Malicious Child Process

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

#### Example: Killing the Parent Process

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

## Nested Stateful Logic

Stateful rules can be nested to create complex multi-stage detections.

### Example: Three-Level Detection

Detect Outlook spawning PowerShell which then creates network connections:

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
    metadata:
      mitre: T1566.001, T1059.001, T1071
      description: Multi-stage attack chain detected
  - action: task
    command: deny_tree <<routing/parent>>
  - action: isolate network
```

**Detection pattern**:
```
outlook.exe
└── powershell.exe
    └── 3+ external network connections within 60 seconds
```

### Example: Combining with_child and with_events

Detect a process spawning children that repeatedly access the same file:

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

### Example: Multiple Child Patterns with Nesting

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

## Flipping Between Stateful and Stateless

Within a stateful context (under `with child` or `with descendant`), all operators are **stateful by default**, meaning sub-rules can match across different events. Sometimes you need to require that multiple conditions match **the same event**.

### The Problem

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

**Problem**: In stateful mode, this could match:
- Child 1: `evil.exe`
- Child 2: Any process with `malicious-flag` in command line

These are **two different events**.

### The Solution: is stateless: true

Use `is stateless: true` to require all sub-rules match the **same event**:

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

### When to Use is stateless: true

Use `is stateless: true` when you need:

1. **Atomic Conditions**: Multiple properties must exist on the same event
2. **Precision**: Avoid false positives from conditions matching different events
3. **Performance**: Stateless matching is faster

### Example: Precise Process Detection

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

## Performance Considerations

Stateful rules consume more resources than stateless rules because they maintain state in memory.

### Memory Usage

Each stateful rule maintains:

1. **Parent Event State**: The initial event that started the stateful matching
2. **Child/Descendant Tracking**: References to related events
3. **Counters**: For `count` and `within` parameters
4. **Timeouts**: For `within` time windows

### Best Practices for Performance

#### 1. Filter Early

Put the most restrictive conditions in the **parent** event:

```yaml
# Good: Filters to specific process immediately
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe  # Very specific
  case sensitive: false
  with child:
    # ... child matching ...

# Bad: Matches all processes
detect:
  event: NEW_PROCESS
  op: exists
  path: event/FILE_PATH  # Matches everything!
  with child:
    op: ends with
    path: event/FILE_PATH
    value: outlook.exe
```

#### 2. Use Specific Event Types

Always specify the `event` type to avoid matching all events:

```yaml
# Good: Specific event type
detect:
  event: NEW_PROCESS
  op: is platform
  name: windows
  with child:
    event: NEW_PROCESS  # Specific
    op: ends with
    path: event/FILE_PATH
    value: calc.exe

# Bad: No event type specified
detect:
  event: NEW_PROCESS
  op: is platform
  name: windows
  with child:
    # Missing event type - will check ALL child events!
    op: ends with
    path: event/FILE_PATH
    value: calc.exe
```

#### 3. Limit Time Windows

Keep `within` parameters as short as possible:

```yaml
# Good: Short, relevant window
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'
    count: 5
    within: 60  # 1 minute is sufficient for brute force

# Avoid: Unnecessarily long windows
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'
    count: 5
    within: 86400  # 24 hours - holds state too long!
```

#### 4. Use Platform Filters

Filter by platform early to reduce the event set:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows  # Filter to Windows immediately
    - op: ends with
      path: event/FILE_PATH
      value: outlook.exe
      case sensitive: false
  with child:
    # ... child matching ...
```

#### 5. Avoid Deep Nesting

Excessive nesting increases complexity and memory usage:

```yaml
# Acceptable: 2 levels
detect:
  event: NEW_PROCESS
  with child:
    event: NEW_PROCESS
    with descendant:
      event: NETWORK_CONNECTIONS

# Avoid: 4+ levels
detect:
  event: NEW_PROCESS
  with child:
    with descendant:
      with descendant:
        with descendant:
          # Too complex!
```

#### 6. Use Suppression with Actions

Always use suppression when triggering sensor commands:

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

### Resource Impact Comparison

| Rule Type | Memory Usage | CPU Usage | State Duration |
|-----------|--------------|-----------|----------------|
| Stateless | Minimal | Low | None |
| with_child (count=1) | Low | Low | Until child found |
| with_child (count=10) | Medium | Medium | Until 10 children or timeout |
| with_descendant | Medium-High | Medium | Until descendant found |
| with_events | Medium | Medium | Duration of `within` window |
| Nested stateful | High | High | Cumulative of all levels |

### When State is Cleared

Stateful rule state is cleared when:

1. **Rule is Modified**: Any change to the rule resets all state
2. **Match is Found**: State is released after the rule matches
3. **Timeout Expires**: After `within` duration passes
4. **Process Exits**: When the parent process terminates
5. **Sensor Disconnects**: When the sensor goes offline

**Important**: Stateful rules are **forward-looking only**. If you modify a rule that detects `excel.exe -> cmd.exe`, Excel must be launched **after** the rule is updated to begin tracking.

## Complex Attack Scenario Examples

### Example 1: Ransomware Execution Chain

Detect ransomware deployment pattern: RDP logon followed by unsigned executable with mass file operations.

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4624'  # Successful logon
    - op: is
      path: event/EVENT/EventData/LogonType
      value: '10'    # RDP logon
    - op: is public address
      path: event/EVENT/EventData/IpAddress
  report latest event: true
  with descendant:
    event: NEW_PROCESS
    op: and
    is stateless: true
    rules:
      - op: is
        path: event/SIGNATURE/FILE_IS_SIGNED
        value: 0  # Unsigned
      - op: contains
        path: event/FILE_PATH
        value: \Users\
        case sensitive: false
    with descendant:
      event: FILE_MODIFIED
      op: exists
      path: event/FILE_PATH
      count: 50
      within: 60
respond:
  - action: report
    name: "Potential Ransomware Chain: RDP -> Unsigned Exe -> Mass File Modifications"
    priority: 5
    metadata:
      mitre: T1021.001, T1486
      description: External RDP followed by unsigned binary with rapid file changes
      recommended_action: Isolate immediately and investigate
  - action: task
    command: deny_tree <<routing/parent>>
  - action: isolate network
  - action: task
    command: history_dump
    investigation: ransomware-chain
```

**Detection pattern**:
```
RDP Logon (external IP)
└── unsigned.exe (from \Users\)
    └── 50+ file modifications in 60 seconds
```

### Example 2: Living-off-the-Land Attack

Detect LOLBin abuse: Office app spawning legitimate Windows binary with suspicious arguments.

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: excel.exe
      case sensitive: false
  report latest event: true
  with descendant:
    event: NEW_PROCESS
    op: or
    rules:
      # certutil downloading
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: certutil.exe
            case sensitive: false
          - op: or
            rules:
              - op: contains
                path: event/COMMAND_LINE
                value: urlcache
              - op: contains
                path: event/COMMAND_LINE
                value: http
      # mshta executing remote content
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: mshta.exe
            case sensitive: false
          - op: contains
            path: event/COMMAND_LINE
            value: http
      # regsvr32 with scriptlet
      - op: and
        is stateless: true
        rules:
          - op: ends with
            path: event/FILE_PATH
            value: regsvr32.exe
            case sensitive: false
          - op: or
            rules:
              - op: contains
                path: event/COMMAND_LINE
                value: /i:http
              - op: contains
                path: event/COMMAND_LINE
                value: scrobj.dll
respond:
  - action: report
    name: "Office App Spawning LOLBin with Suspicious Arguments"
    priority: 4
    metadata:
      mitre: T1566.001, T1218
      description: Office application spawned legitimate binary for malicious purpose
  - action: task
    command: deny_tree <<routing/this>>
  - action: task
    command: history_dump
    investigation: lolbin-abuse
  - action: add tag
    tag: lolbin-detected
    ttl: 3600
```

**Detection pattern**: Office apps spawning certutil/mshta/regsvr32 with download or execution arguments.

### Example 3: Credential Dumping Detection

Detect credential theft: Process accessing LSASS followed by network exfiltration.

```yaml
detect:
  event: SENSITIVE_PROCESS_ACCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/TARGET/FILE_PATH
      value: lsass.exe
      case sensitive: false
  report latest event: true
  with events:
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: is public address
        path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      - op: is greater than
        path: event/NETWORK_ACTIVITY/BYTES_SENT
        value: 10240  # 10KB+
    count: 1
    within: 300  # Within 5 minutes
respond:
  - action: report
    name: LSASS Access Followed by External Data Transfer
    priority: 5
    metadata:
      mitre: T1003.001, T1041
      description: Potential credential dumping and exfiltration
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
  - action: task
    command: history_dump
    investigation: credential-theft
  - action: extension request
    extension name: dumper
    extension action: dump
    extension request:
      sid: '{{ .routing.sid }}'
      pid: '{{ .event.PROCESS_ID }}'
```

**Detection pattern**: Process accesses LSASS memory, then transfers 10KB+ to external IP within 5 minutes.

### Example 4: Lateral Movement Detection

Detect PsExec-style lateral movement: Remote service creation followed by process execution.

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '7045'  # Service installation
    - op: is
      path: event/EVENT/System/Channel
      value: System
    - op: contains
      path: event/EVENT/EventData/ImagePath
      value: \ADMIN$
      case sensitive: false
  report latest event: true
  with descendant:
    event: NEW_PROCESS
    op: and
    is stateless: true
    rules:
      - op: is
        path: event/PARENT/FILE_PATH
        value: C:\Windows\System32\services.exe
      - op: contains
        path: event/FILE_PATH
        value: \ADMIN$
        case sensitive: false
    within: 30
respond:
  - action: report
    name: "Lateral Movement: Remote Service Creation and Execution"
    priority: 5
    metadata:
      mitre: T1021.002, T1569.002
      description: Service installed via ADMIN$ share and executed
  - action: task
    command: history_dump
    investigation: lateral-movement
  - action: task
    command: deny_tree <<routing/this>>
  - action: add tag
    tag: lateral-movement-detected
    ttl: 7200
```

**Detection pattern**: Service creation via ADMIN$ followed by process execution within 30 seconds.

### Example 5: Data Staging and Exfiltration

Detect data staging: Archive creation followed by upload to cloud storage.

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: 7z.exe
      case sensitive: false
    - op: ends with
      path: event/FILE_PATH
      value: winrar.exe
      case sensitive: false
    - op: contains
      path: event/COMMAND_LINE
      value: tar.exe -c
  report latest event: true
  with descendant:
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: is public address
        path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      - op: or
        rules:
          - op: contains
            path: event/DOMAIN_NAME
            value: dropbox
          - op: contains
            path: event/DOMAIN_NAME
            value: mega.nz
          - op: contains
            path: event/DOMAIN_NAME
            value: wetransfer
    within: 600  # 10 minutes
respond:
  - action: report
    name: "Data Staging and Cloud Upload Detected"
    priority: 4
    metadata:
      mitre: T1560, T1567.002
      description: Archive tool used followed by connection to file sharing service
  - action: task
    command: history_dump
    investigation: data-exfiltration
  - action: add tag
    tag: potential-exfiltration
    ttl: 7200
  - action: task
    command: segregate_network
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'
      max_count: 1
      period: 1h
```

**Detection pattern**: Archive creation tool followed by connection to cloud storage within 10 minutes.

## Testing Stateful Rules

Testing stateful rules requires special consideration because they track state over time.

### Important Testing Caveats

1. **Forward-Looking Only**: Stateful rules only track events that occur **after** the rule is active
2. **State Reset**: Changing a rule resets all state
3. **Parent Must Occur First**: For `cmd.exe -> calc.exe` detection, CMD must launch **after** the rule is active

### Testing Workflow

#### Step 1: Validate Syntax

```bash
limacharlie replay --validate --rule-content my-stateful-rule.yaml
```

#### Step 2: Test with Synthetic Events

Create test events that simulate the attack chain:

**parent-event.json**:
```json
{
  "routing": {
    "event_type": "NEW_PROCESS",
    "this": "parent-atom-id",
    "hostname": "testhost",
    "sid": "test-sid"
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
    "PROCESS_ID": 1234
  }
}
```

**child-event.json**:
```json
{
  "routing": {
    "event_type": "NEW_PROCESS",
    "this": "child-atom-id",
    "parent": "parent-atom-id",
    "hostname": "testhost",
    "sid": "test-sid"
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\calc.exe",
    "PROCESS_ID": 5678
  }
}
```

**Combine into single test file** (events.json):
```json
[
  {
    "routing": {
      "event_type": "NEW_PROCESS",
      "this": "parent-atom-id",
      "hostname": "testhost",
      "sid": "test-sid"
    },
    "event": {
      "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
      "PROCESS_ID": 1234
    }
  },
  {
    "routing": {
      "event_type": "NEW_PROCESS",
      "this": "child-atom-id",
      "parent": "parent-atom-id",
      "hostname": "testhost",
      "sid": "test-sid"
    },
    "event": {
      "FILE_PATH": "C:\\Windows\\System32\\calc.exe",
      "PROCESS_ID": 5678
    }
  }
]
```

**Test**:
```bash
limacharlie replay --rule-content my-rule.yaml --events events.json
```

#### Step 3: Use Unit Tests

Add unit tests directly to your rule:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: cmd.exe
  case sensitive: false
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: calc.exe
    case sensitive: false
respond:
  - action: report
    name: CMD Spawning Calculator
tests:
  match:
    # Should match: cmd.exe -> calc.exe
    - - event:
          FILE_PATH: C:\Windows\System32\cmd.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          this: parent-1
          hostname: testhost
      - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          this: child-1
          parent: parent-1
          hostname: testhost
  non_match:
    # Should NOT match: notepad.exe -> calc.exe
    - - event:
          FILE_PATH: C:\Windows\System32\notepad.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          this: parent-2
          hostname: testhost
      - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          this: child-2
          parent: parent-2
          hostname: testhost
```

#### Step 4: Live Testing on Non-Production Sensors

1. Deploy rule to test organization
2. Manually trigger the behavior (safely!)
3. Verify detection fires
4. Check that the correct event is reported

#### Step 5: Replay Against Historical Data

**Warning**: This may not work as expected for stateful rules because historical data is replayed "as-is" without rebuilding process trees.

```bash
# May have limited effectiveness for stateful rules
limacharlie replay --entire-org --last-seconds 604800 --rule-content my-rule.yaml
```

## Best Practices Summary

### When to Use Stateful Rules

1. **Parent-Child Process Detection**: Office apps spawning shells
2. **Multi-Stage Attacks**: Download -> Execute -> Persist chains
3. **Threshold Detection**: Multiple failed logins, port scanning
4. **Time-Based Correlation**: Related events within a window
5. **Process Tree Behavior**: Suspicious descendants anywhere in tree

### When to Avoid Stateful Rules

1. **Single Event Detection**: All info is in one event
2. **Simple Pattern Matching**: File path, hash, domain lookups
3. **High-Volume Events**: Will cause memory pressure
4. **Long Time Windows**: State held for hours/days
5. **Broad Matching**: Millions of parent events

### Design Guidelines

1. **Start Specific**: Filter parent events as narrowly as possible
2. **Use Event Types**: Always specify `event:` in child rules
3. **Limit Time Windows**: Keep `within` parameters short
4. **Add Platform Filters**: Use `is platform` early
5. **Test Thoroughly**: Create unit tests and validate with replay
6. **Use Suppression**: Prevent runaway sensor commands
7. **Document Logic**: Use comments and metadata
8. **Monitor Performance**: Watch for memory/CPU impact
9. **Prefer with_child**: Use `with descendant` only when necessary
10. **Report Appropriately**: Choose parent vs latest event based on context

### Common Mistakes to Avoid

1. **Missing Event Type**: Not specifying `event:` in child rules
2. **Too Broad Parent**: Matching all processes instead of specific ones
3. **Long Time Windows**: Using `within: 86400` (24 hours)
4. **Deep Nesting**: 4+ levels of stateful operators
5. **No Suppression**: Triggering sensor commands without limits
6. **Forgetting is stateless**: Accidentally matching across different events
7. **Not Testing**: Deploying without validation
8. **Reporting Wrong Event**: Not using `report latest event` when needed

## Reference: Stateful Parameters

### Common Parameters

| Parameter | Used With | Description | Example |
|-----------|-----------|-------------|---------|
| `with child` | All events | Match direct children | `with child:` |
| `with descendant` | All events | Match any descendant | `with descendant:` |
| `with events` | All events | Match proximal events | `with events:` |
| `count` | with_child, with_descendant, with_events | Number of occurrences | `count: 5` |
| `within` | with_child, with_descendant, with_events | Time window (seconds) | `within: 60` |
| `report latest event` | with_child, with_descendant | Report child instead of parent | `report latest event: true` |
| `is stateless` | and, or | Match within single event | `is stateless: true` |

### Event Relationships

Events are related through routing metadata:

- `routing/this`: Current event's atom ID
- `routing/parent`: Parent event's atom ID
- `routing/target`: Target event (for some event types)

Stateful rules automatically track these relationships.

## When to Get Help

Consult with security experts when:

1. **Complex Attack Chains**: Multi-stage attacks with many branches
2. **Performance Issues**: Rules causing memory/CPU problems
3. **False Positive Tuning**: High noise that's hard to filter
4. **Advanced Nesting**: 3+ levels of stateful operators
5. **Custom Use Cases**: Unique detection requirements

Always test rules in a non-production environment before deploying to production sensors.

---

## Key Reminders

1. Stateful rules are **forward-looking only** - state starts when the rule is active
2. Modifying a rule **resets all state** - parent processes must restart
3. Response actions always use the **latest event** in the chain
4. Use `is stateless: true` to require conditions match the **same event**
5. Always use **suppression** with sensor commands
6. **Test thoroughly** with unit tests and replay before deploying
7. Keep time windows **short** to minimize memory usage
8. **Filter early** with specific parent event criteria

This skill provides comprehensive guidance for creating sophisticated stateful detection rules. When helping users, always emphasize testing, performance considerations, and the importance of understanding the attack chain they're trying to detect.
