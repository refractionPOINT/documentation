---
name: dr-rule-builder
description: Use this skill when the user needs help creating, testing, validating, or troubleshooting Detection & Response (D&R) rules in LimaCharlie.
---

# LimaCharlie D&R Rule Builder

This skill helps you create, test, and validate Detection & Response (D&R) rules in LimaCharlie. Use this when users ask for help with rule creation, rule debugging, or understanding D&R rule syntax.

## What are D&R Rules?

Detection & Response (D&R) rules are similar to Google Cloud Functions or AWS Lambda. They are serverless functions that run in the LimaCharlie cloud and are applied in real-time to data coming from sensors. D&R rules allow you to:

- Detect specific behaviors or patterns in telemetry
- Automatically respond to detections with actions
- Create custom alerting logic
- Trigger automated remediation
- Chain multiple detections together

Rules are evaluated on a per-event basis. When a rule's detection component matches, the response component is executed.

## Rule Structure

All D&R rules follow this basic YAML structure:

```yaml
detect:
  # Detection logic goes here
  event: EVENT_TYPE
  op: OPERATOR
  # ... additional detection criteria

respond:
  # Response actions go here
  - action: ACTION_TYPE
    # ... action parameters
```

### Required Components

1. **detect**: The detection logic that determines if the rule matches
   - Must specify an `event` type (or use `target` for non-sensor events)
   - Must specify an `op` (operator) that defines the matching logic
   - Can include nested rules using `and`/`or` operators

2. **respond**: A list of actions to take when detection matches
   - Must be an array (even if only one action)
   - Each action has an `action` type and associated parameters

## Detection Operators

### Basic Comparison Operators

#### is
Tests for exact equality between a value in the event and a specified value.

```yaml
event: NEW_PROCESS
op: is
path: event/PROCESS_ID
value: 9999
```

#### exists
Tests if an element exists at the given path (regardless of value).

```yaml
event: NEW_PROCESS
op: exists
path: event/PARENT
```

The `exists` operator supports an optional `truthy` parameter to treat `null` and empty strings as non-existent:

```yaml
op: exists
path: some/path
truthy: true
```

#### contains
Checks if a substring is found in the value at the path. Supports an optional `count` parameter to match only if the substring appears at least N times.

```yaml
event: NEW_PROCESS
op: contains
path: event/COMMAND_LINE
value: reg
count: 2  # optional: must appear at least 2 times
```

#### starts with / ends with
Checks for prefix or suffix matches.

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: .exe
case sensitive: false
```

#### matches
Compares the value at path with a regular expression (using Go regexp syntax).

```yaml
event: FILE_TYPE_ACCESSED
op: matches
path: event/FILE_PATH
re: .*\\system32\\.*\.scr
case sensitive: false
```

#### is greater than / is lower than
Numerical comparison operators. Support `length of` parameter to compare string lengths instead of values.

```yaml
event: NETWORK_CONNECTIONS
op: is greater than
path: event/NETWORK_ACTIVITY/BYTES_SENT
value: 1048576  # 1MB
```

### Boolean Logic Operators

#### and / or
Combine multiple rules with boolean logic. Takes a `rules:` parameter containing a list of sub-rules.

```yaml
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: ends with
    path: event/FILE_PATH
    value: /sshd
  - op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

Nested boolean logic example:

```yaml
event: WEL
op: or
rules:
  - op: and
    rules:
      - op: is
        path: event/EVENT/System/Channel
        value: System
      - op: or
        rules:
          - op: is
            path: event/EVENT/System/EventID
            value: '4697'
          - op: is
            path: event/EVENT/System/EventID
            value: '7045'
  - op: and
    rules:
      - op: is
        path: event/EVENT/System/Channel
        value: Security
      - op: is
        path: event/EVENT/System/EventID
        value: '4698'
```

#### not
Inverts the result of its rule. Can be applied to any operator.

```yaml
event: NEW_PROCESS
op: is
not: true
path: event/PARENT/PROCESS_ID
value: 9999
```

### Platform and Sensor Operators

#### is platform
Checks if the event is from a sensor of the given platform.

Supported platforms: `windows`, `linux`, `macos`, `ios`, `android`, `chrome`, `vpn`, `text`, `json`, GCP, AWS, `carbon_black`, `crowdstrike`, `1password`, `office365`, `msdefender`

```yaml
op: is platform
name: windows
```

#### is windows / is 32 bit / is 64 bit / is arm
Platform and architecture checks that take no additional arguments.

```yaml
event: CODE_IDENTITY
op: is windows
```

#### is tagged
Determines if the sensor has a specific tag applied.

```yaml
op: is tagged
tag: vip
```

### Network Operators

#### is public address / is private address
Checks if an IP address is public or private (per RFC 1918).

```yaml
event: NETWORK_CONNECTIONS
op: is public address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

#### cidr
Checks if an IP address is within a CIDR network mask.

```yaml
event: NETWORK_CONNECTIONS
op: cidr
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
cidr: 10.16.1.0/24
```

### Advanced Operators

#### string distance
Calculates Levenshtein Distance between strings to find variations (useful for phishing detection).

```yaml
event: DNS_REQUEST
op: string distance
path: event/DOMAIN_NAME
value:
  - onephoton.com
  - www.onephoton.com
max: 2  # maximum edit distance to match
```

#### lookup
Looks up a value against a threat feed or custom lookup resource.

```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malwaredomains
case sensitive: false
```

#### scope
Limits the scope of matching to a specific sub-path of the event. This is crucial for events with arrays.

```yaml
event: NETWORK_CONNECTIONS
op: scope
path: event/NETWORK_ACTIVITY/
rule:
  op: and
  rules:
    - op: starts with
      path: event/SOURCE/IP_ADDRESS
      value: '10.'
    - op: is
      path: event/DESTINATION/PORT
      value: 445
```

#### is older than
Tests if a timestamp value is older than a specified number of seconds.

```yaml
event: login-attempt
op: is older than
path: routing/event_time
seconds: 3600  # 1 hour
```

## Event Paths

Events have a well-defined structure with two main components:

### Event Data
Access event-specific data using the `event/` prefix:

```yaml
path: event/FILE_PATH
path: event/COMMAND_LINE
path: event/PROCESS_ID
path: event/DOMAIN_NAME
path: event/HASH
```

### Routing Metadata
Access routing information using the `routing/` prefix:

```yaml
path: routing/sid          # Sensor ID
path: routing/hostname     # Host name
path: routing/event_type   # Event type
path: routing/event_time   # Event timestamp
path: routing/this         # Current atom ID
path: routing/parent       # Parent atom ID
path: routing/tags         # Sensor tags
```

### Array Navigation
Use `?` as a wildcard for any array index, or specific indices like `0`, `1`, etc:

```yaml
path: event/NETWORK_ACTIVITY/?/IP_ADDRESS  # any connection
path: event/NETWORK_ACTIVITY/0/IP_ADDRESS  # first connection
```

## Transforms

Transforms modify values before comparison.

### file name
Extracts just the filename from a path.

```yaml
event: NEW_PROCESS
op: is
path: event/FILE_PATH
file name: true
value: svchost.exe
```

### sub domain
Extracts specific components from a domain name using slice notation.

```yaml
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
sub domain: "-2:"  # last 2 components (e.g., "example.com" from "www.subdomain.example.com")
value: example.com
```

Slice notation examples:
- `0:2` = first 2 components: `aa.bb` from `aa.bb.cc.dd`
- `-1` = last component: `cc` from `aa.bb.cc`
- `1:` = all starting at index 1: `bb.cc` from `aa.bb.cc`
- `:` = test operator on every component individually

## Stateful Rules

Stateful rules track relationships between events over time or across process trees.

### with child
Matches direct children of the initial event.

```yaml
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
```

This detects: `cmd.exe -> calc.exe` but NOT `cmd.exe -> firefox.exe -> calc.exe`

### with descendant
Matches any descendant (children, grandchildren, etc.) of the initial event.

```yaml
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
```

This detects both: `cmd.exe -> calc.exe` AND `cmd.exe -> firefox.exe -> calc.exe`

### with events
Detects repetition of events close together on the same sensor.

```yaml
event: WEL
op: is windows
with events:
  event: WEL
  op: is
  path: event/EVENT/System/EventID
  value: '4625'  # failed login
  count: 5
  within: 60  # 5 failed logins within 60 seconds
```

### Counting in Stateful Rules
Stateful rules support `count` and `within` parameters:

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
  count: 5     # at least 5 occurrences
  within: 60   # within 60 seconds
```

### Choosing Event to Report
By default, stateful rules report the parent event. Use `report latest event: true` to report the child/descendant instead:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  report latest event: true
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

### Flipping to Stateless Mode
Within a stateful context, use `is stateless: true` to require all sub-rules to match a single event:

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: outlook.exe
case sensitive: false
with child:
  op: and
  is stateless: true  # both conditions must match on the same child event
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

## Response Actions

Actions define what happens when a detection matches.

### report
Creates a detection (alert) that is sent to outputs and appears in the Detections page.

```yaml
- action: report
  name: my-detection-name
  publish: true  # default: true
  priority: 3    # optional severity level
  metadata:      # optional free-form metadata
    author: Alice (alice@wonderland.com)
    description: Detected suspicious behavior
  detect_data:   # optional structured data for extraction
    domain: "{{ .event.DOMAIN_NAME }}"
```

The `name`, `metadata`, and `detect_data` support Go template strings:

```yaml
- action: report
  name: "Suspicious process {{ .event.FILE_PATH }} on {{ .routing.hostname }}"
```

Prefix the name with `__` (double underscore) to limit scope to D&R rule chaining only (won't send to outputs):

```yaml
- action: report
  name: __internal-detection
```

### task
Sends a command to the sensor to perform an action.

```yaml
- action: task
  command: history_dump
  investigation: susp-process-inv  # optional investigation ID
```

Common commands:
- `history_dump` - Get recent process history
- `deny_tree <<routing/this>>` - Kill process tree
- `segregate_network` - Isolate from network
- `yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"` - Scan with YARA

The `command` parameter supports template strings:

```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: file-collection
```

### add tag / remove tag
Adds or removes tags on the sensor.

```yaml
- action: add tag
  tag: vip
  ttl: 30           # optional: seconds before tag expires
  entire_device: false  # optional: apply to all sensors with same device ID
```

### isolate network / rejoin network
Isolates the sensor from the network (or removes isolation). Persists across reboots.

```yaml
- action: isolate network
```

```yaml
- action: rejoin network
```

### add var / del var
Adds or removes a variable associated with the sensor.

```yaml
- action: add var
  name: my-variable
  value: <<event/VOLUME_PATH>>
  ttl: 30  # optional
```

### extension request
Performs an asynchronous request to an extension.

```yaml
- action: extension request
  extension name: dumper
  extension action: dump
  extension request:
    sid: '{{ .routing.sid }}'
    pid: "{{ .event.PROCESS_ID }}"
  based on report: false  # optional: use report instead of event as context
```

### output
Forwards the matched event to a specific Output.

```yaml
- action: output
  name: my-output
```

### seal / unseal
Enables or disables tamper resistance on the sensor.

```yaml
- action: seal
```

```yaml
- action: unseal
```

### wait
Adds a delay before running the next action (max 1 minute).

```yaml
- action: wait
  duration: 10s  # or just: 10
```

### undelete sensor
Un-deletes a sensor that was previously deleted.

```yaml
detect:
  target: deployment
  event: deleted_sensor
  op: is
  path: routing/event_type
  value: deleted_sensor
respond:
  - action: undelete sensor
```

## Suppression

Suppression controls how frequently actions execute to prevent alert fatigue and resource exhaustion.

### Reduce Frequency
Limit how often an action executes:

```yaml
- action: report
  name: evil-process-detected
  suppression:
    max_count: 1      # execute at most once
    period: 1h        # per hour
    is_global: true   # across entire org (false = per sensor)
    keys:
      - '{{ .event.FILE_PATH }}'
      - 'evil-process-detected'
```

Supported time formats: `ns`, `us`, `ms`, `s`, `m`, `h`

### Threshold Activation
Only execute after a minimum number of activations:

```yaml
- action: report
  name: high-alerts
  suppression:
    min_count: 3   # must match 3 times
    max_count: 3   # then alert once
    period: 24h    # within 24 hours
```

### Variable Count
Increment suppression by a dynamic value from the event:

```yaml
detect:
  event: billing_record
  op: is
  path: event/record/k
  target: billing
  value: ext-strelka:bytes_scanned
respond:
  - action: report
    name: strelka-bytes-reached
    suppression:
      count_path: event/record/v  # increment by this value
      is_global: true
      keys:
        - strelka-bytes-usage
      max_count: 1048576  # 1MB
      min_count: 1048576
      period: 24h
```

### Practical Suppression Example
Prevent YARA scanning the same process multiple times:

```yaml
- action: task
  command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
  investigation: Yara Scan Process
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
      - Yara Scan Process
    max_count: 1
    period: 1m
```

## Time-Based Rules

Limit when rules are active using time descriptors:

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: chrome.exe
case sensitive: false
times:
  - day_of_week_start: 2     # Monday=1, Sunday=7
    day_of_week_end: 6       # Friday
    time_of_day_start: 2200  # 10 PM
    time_of_day_end: 2359    # 11:59 PM
    tz: America/Los_Angeles
  - day_of_week_start: 2
    day_of_week_end: 6
    time_of_day_start: 0
    time_of_day_end: 500     # 5 AM
    tz: America/Los_Angeles
```

Time zones should match [TZ database names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Unit Testing Rules

D&R rules can include unit tests to validate behavior:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: calc.exe
  case sensitive: false
respond:
  - action: report
    name: calculator-launched
tests:
  match:
    # Test 1: Should match
    - - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
    # Test 2: Should also match
    - - event:
          FILE_PATH: C:\temp\CALC.EXE
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
  non_match:
    # Test 1: Should NOT match (wrong extension)
    - - event:
          FILE_PATH: C:\Windows\System32\notepad.exe
          PROCESS_ID: 9999
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
    # Test 2: Should NOT match (wrong event type)
    - - event:
          FILE_PATH: C:\Windows\System32\calc.exe
        routing:
          event_type: CODE_IDENTITY
          hostname: testhost
```

### Unit Test Structure
- `tests.match`: Array of test cases that should trigger the detection
- `tests.non_match`: Array of test cases that should NOT trigger the detection
- Each test case is an array of events (to support stateful rules)
- Tests are automatically run when rules are created or updated

## Testing and Validation

### Using the Replay Service

#### Validate Rule Syntax
```bash
limacharlie replay --validate --rule-content my-rule.yaml
```

#### Test Against a Single Event
```bash
limacharlie replay --rule-content my-rule.yaml --events test-event.json
```

#### Test Against Historical Data
```bash
# Test against one sensor
limacharlie replay --sid SENSOR_ID --start 1556568500 --end 1556568600 --rule-content my-rule.yaml

# Test against entire org
limacharlie replay --entire-org --last-seconds 604800 --rule-content my-rule.yaml
```

### Trace Mode
Enable detailed trace output to debug where rules fail:

```bash
limacharlie replay --rule-content my-rule.yaml --events test-event.json --trace
```

## Best Practices

### Performance Optimization

1. **Filter Early**: Put the most restrictive conditions first
   ```yaml
   # Good: filters by event type immediately
   event: CODE_IDENTITY
   op: and
   rules:
     - op: is windows
     - op: ends with
       path: event/FILE_PATH
       value: .exe
   ```

2. **Use Event Type Filters**: Always specify `event:` at the top level when possible
   ```yaml
   # Good
   event: NEW_PROCESS
   op: contains
   path: event/COMMAND_LINE
   value: powershell
   ```

3. **Avoid Expensive Operations**: Minimize use of regex and lookups when simpler operators work
   ```yaml
   # Better
   op: ends with
   value: .exe

   # Avoid if not necessary
   op: matches
   re: .*\.exe$
   ```

4. **Use Suppression**: Always use suppression when triggering sensor commands
   ```yaml
   - action: task
     command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
     suppression:
       is_global: false
       keys:
         - '{{ .event.PROCESS_ID }}'
       max_count: 1
       period: 5m
   ```

### False Positive Management

1. **Use Case Sensitivity Wisely**: Set `case sensitive: false` for file paths and domains
   ```yaml
   op: ends with
   path: event/FILE_PATH
   value: .exe
   case sensitive: false
   ```

2. **Exclude Known Good Paths**: Use `not` to exclude system directories
   ```yaml
   op: matches
   path: event/FILE_PATH
   re: ^.\:\\windows\\
   case sensitive: false
   not: true
   ```

3. **Create False Positive Rules**: Use FP rules to filter out known benign detections
   ```yaml
   # False Positive Rule (separate from D&R rule)
   op: is
   path: detect/routing/hostname
   value: dev-server-1
   ```

### Rule Organization

1. **Use Descriptive Names**: Make detection names clear and actionable
   ```yaml
   - action: report
     name: "Outlook spawning PowerShell with encoded command"
   ```

2. **Add Metadata**: Include context for SOC analysts
   ```yaml
   - action: report
     name: suspicious-behavior
     metadata:
       author: security-team@company.com
       mitre: T1059.001
       severity: high
       remediation: "Investigate process tree and command line"
   ```

3. **Use detect_data for Extraction**: Extract key fields for consistent parsing
   ```yaml
   - action: report
     name: malicious-domain
     detect_data:
       domain: "{{ .event.DOMAIN_NAME }}"
       ip: "{{ .event.IP_ADDRESS }}"
       sensor: "{{ .routing.hostname }}"
   ```

## Common Examples

### Example 1: Detect Process Execution from Downloads

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\
      case sensitive: false
respond:
  - action: report
    name: Execution from Downloads Directory
    priority: 2
    metadata:
      description: Process executed from Downloads folder
      mitre: T1204
  - action: add tag
    tag: execution-from-downloads
    ttl: 3600
```

### Example 2: Detect Lateral Movement (RDP from External IP)

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: C:\WINDOWS\System32\svchost.exe
    - op: contains
      path: event/COMMAND_LINE
      value: TermService
    - op: is
      path: event/NETWORK_ACTIVITY/DESTINATION/PORT
      value: 3389
    - op: is public address
      path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
respond:
  - action: report
    name: "RDP from External IP - {{ index (index .event.NETWORK_ACTIVITY 0) \"SOURCE\" \"IP_ADDRESS\" }}"
    priority: 3
  - action: task
    command: history_dump
    investigation: rdp-external-access
```

### Example 3: Detect Multiple Failed Logins

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
    count: 5
    within: 300
respond:
  - action: report
    name: Multiple Failed Login Attempts
    priority: 3
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .routing.sid }}'
  - action: add tag
    tag: brute-force-attempt
    ttl: 3600
```

### Example 4: Detect Office Document Spawning PowerShell

```yaml
detect:
  event: NEW_PROCESS
  op: or
  rules:
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: winword.exe
      case sensitive: false
    - op: ends with
      path: event/PARENT/FILE_PATH
      value: excel.exe
      case sensitive: false
  with child:
    op: and
    rules:
      - op: ends with
        event: NEW_PROCESS
        path: event/FILE_PATH
        value: powershell.exe
        case sensitive: false
      - op: contains
        path: event/COMMAND_LINE
        value: -enc
        case sensitive: false
respond:
  - action: report
    name: Office Application Spawning Encoded PowerShell
    priority: 4
    metadata:
      mitre: T1059.001, T1566.001
      description: Potential macro-based malware execution
  - action: task
    command: deny_tree <<routing/this>>
  - action: isolate network
```

### Example 5: Threat Feed Lookup

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malwaredomains
  case sensitive: false
respond:
  - action: report
    name: "DNS request to known malicious domain: {{ .event.DOMAIN_NAME }}"
    priority: 4
  - action: add tag
    tag: contacted-malicious-domain
    ttl: 86400
  - action: task
    command: history_dump
    investigation: malicious-dns
```

## Event Targets

Most rules target sensor events, but you can also target other event types:

### Artifact Collection
```yaml
detect:
  target: artifact
  op: contains
  path: /text
  value: /corp/private/info
respond:
  - action: report
    name: web-proxy-private-url
```

### Deployment Events
```yaml
detect:
  target: deployment
  event: sensor_clone
  op: is platform
  name: windows
respond:
  - action: re-enroll
```

### Billing Events
```yaml
detect:
  target: billing
  event: billing_record
  op: is
  path: event/record/k
  value: storage:bytes
respond:
  - action: report
    name: storage-alert
```

## Troubleshooting

### Rule Not Matching

1. **Verify event structure**: Use Historic View to examine actual event structure
2. **Check case sensitivity**: Add `case sensitive: false` where appropriate
3. **Use trace mode**: Run replay with `--trace` to see where rule fails
4. **Verify event type**: Ensure `event:` matches the actual event type
5. **Check path syntax**: Ensure paths use `/` separators and correct structure

### Performance Issues

1. **Add event type filter**: Always specify `event:` at top level
2. **Reorder rules**: Put most restrictive conditions first
3. **Use suppression**: Prevent runaway sensor commands
4. **Avoid wildcards**: Use specific paths instead of `event/?/field`
5. **Optimize regex**: Use simpler operators when possible

### False Positives

1. **Create FP rules**: Filter known benign behaviors
2. **Add exclusions**: Use `not: true` to exclude system paths
3. **Increase specificity**: Add more matching criteria
4. **Use stateful rules**: Require multiple correlated events
5. **Adjust thresholds**: Use `min_count` to require repetition

## Template Strings

Many fields support Go template syntax for dynamic values:

### Available Context

In most actions:
- `.event.*` - Event data
- `.routing.*` - Routing metadata
- `.detect.*` - Detection data (in report actions)

### Common Templates

```yaml
# Access event fields
"{{ .event.FILE_PATH }}"
"{{ .event.DOMAIN_NAME }}"
"{{ .event.PROCESS_ID }}"

# Access routing fields
"{{ .routing.hostname }}"
"{{ .routing.sid }}"

# Access nested/array fields
"{{ index .event.NETWORK_ACTIVITY 0 }}"
"{{ index (index .event.NETWORK_ACTIVITY 0) \"SOURCE\" \"IP_ADDRESS\" }}"

# Use in action parameters
- action: report
  name: "Process {{ .event.FILE_PATH }} on {{ .routing.hostname }}"

- action: task
  command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
```

## Additional Resources

### CLI Commands

```bash
# List rules
limacharlie dr list

# Add a rule
limacharlie dr add --rule-name my-rule --rule-file rule.yaml

# Delete a rule
limacharlie dr delete --rule-name my-rule

# Test rule
limacharlie replay --rule-content rule.yaml --events events.json

# Validate rule
limacharlie replay --validate --rule-content rule.yaml
```

### Rule Development Workflow

1. **Draft**: Write rule in YAML format
2. **Validate**: Use `limacharlie replay --validate`
3. **Test**: Create test events and unit tests
4. **Replay**: Test against historical data
5. **Deploy**: Add to production with `limacharlie dr add`
6. **Monitor**: Watch detections and adjust as needed
7. **Iterate**: Refine based on false positives/negatives

## Key Reminders

1. Always test rules before deploying to production
2. Use suppression with sensor commands to prevent resource exhaustion
3. Add unit tests to catch regressions
4. Include metadata for SOC context
5. Use case-insensitive matching for file paths and domains
6. Put most restrictive conditions first for performance
7. Use stateful rules for behavior-based detections
8. Create false positive rules for organization-specific exclusions
9. Monitor rule performance with replay metrics
10. Document rules with clear names and metadata

This skill provides comprehensive guidance for creating effective D&R rules. When helping users, always encourage testing and validation before production deployment.
