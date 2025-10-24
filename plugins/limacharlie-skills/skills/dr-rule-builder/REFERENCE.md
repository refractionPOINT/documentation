# D&R Rule Reference

Complete reference documentation for all Detection & Response operators, actions, and syntax.

## Table of Contents

- [All Detection Operators](#all-detection-operators)
- [All Response Actions](#all-response-actions)
- [Transforms](#transforms)
- [Event Paths](#event-paths)
- [Stateful Rules Advanced](#stateful-rules-advanced)
- [Suppression Advanced](#suppression-advanced)
- [Time-Based Rules](#time-based-rules)
- [Event Targets](#event-targets)
- [Template Strings](#template-strings)

## All Detection Operators

### Basic Comparison Operators

#### is
Tests for exact equality between a value in the event and a specified value.

**Parameters:**
- `path`: Path to the value in the event
- `value`: Value to compare against

**Example:**
```yaml
event: NEW_PROCESS
op: is
path: event/PROCESS_ID
value: 9999
```

#### exists
Tests if an element exists at the given path (regardless of value).

**Parameters:**
- `path`: Path to check for existence
- `truthy`: (optional) Treat `null` and empty strings as non-existent

**Example:**
```yaml
event: NEW_PROCESS
op: exists
path: event/PARENT
```

**With truthy:**
```yaml
op: exists
path: some/path
truthy: true
```

#### contains
Checks if a substring is found in the value at the path.

**Parameters:**
- `path`: Path to the value
- `value`: Substring to search for
- `count`: (optional) Minimum number of times substring must appear
- `case sensitive`: (optional) Default: true

**Example:**
```yaml
event: NEW_PROCESS
op: contains
path: event/COMMAND_LINE
value: reg
count: 2  # must appear at least 2 times
case sensitive: false
```

#### starts with
Checks if a value starts with a specified prefix.

**Parameters:**
- `path`: Path to the value
- `value`: Prefix to match
- `case sensitive`: (optional) Default: true

**Example:**
```yaml
event: NEW_PROCESS
op: starts with
path: event/FILE_PATH
value: C:\Windows\
case sensitive: false
```

#### ends with
Checks if a value ends with a specified suffix.

**Parameters:**
- `path`: Path to the value
- `value`: Suffix to match
- `case sensitive`: (optional) Default: true

**Example:**
```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: .exe
case sensitive: false
```

#### matches
Compares the value at path with a regular expression using Go regexp syntax.

**Parameters:**
- `path`: Path to the value
- `re`: Regular expression pattern
- `case sensitive`: (optional) Default: true

**Example:**
```yaml
event: FILE_TYPE_ACCESSED
op: matches
path: event/FILE_PATH
re: .*\\system32\\.*\.scr
case sensitive: false
```

#### is greater than
Numerical comparison operator (value > specified).

**Parameters:**
- `path`: Path to the numeric value
- `value`: Number to compare against
- `length of`: (optional) Compare string lengths instead of values

**Example:**
```yaml
event: NETWORK_CONNECTIONS
op: is greater than
path: event/NETWORK_ACTIVITY/BYTES_SENT
value: 1048576  # 1MB
```

**Length comparison:**
```yaml
event: NEW_PROCESS
op: is greater than
path: event/COMMAND_LINE
value: 1000
length of: true
```

#### is lower than
Numerical comparison operator (value < specified).

**Parameters:**
- `path`: Path to the numeric value
- `value`: Number to compare against
- `length of`: (optional) Compare string lengths instead of values

**Example:**
```yaml
event: NEW_PROCESS
op: is lower than
path: event/PROCESS_ID
value: 1000
```

### Boolean Logic Operators

#### and
Combine multiple rules - all must match.

**Parameters:**
- `rules`: List of sub-rules that must all match

**Example:**
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

**Nested example:**
```yaml
event: WEL
op: and
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
```

#### or
Combine multiple rules - at least one must match.

**Parameters:**
- `rules`: List of sub-rules where at least one must match

**Example:**
```yaml
event: NEW_PROCESS
op: or
rules:
  - op: ends with
    path: event/FILE_PATH
    value: cmd.exe
    case sensitive: false
  - op: ends with
    path: event/FILE_PATH
    value: powershell.exe
    case sensitive: false
```

#### not
Inverts the result of its rule. Can be applied to any operator.

**Parameters:**
- `not`: Set to `true` to invert the result

**Example:**
```yaml
event: NEW_PROCESS
op: is
not: true
path: event/PARENT/PROCESS_ID
value: 9999
```

**With other operators:**
```yaml
op: matches
path: event/FILE_PATH
re: ^C:\\Windows\\
case sensitive: false
not: true  # matches everything NOT in C:\Windows\
```

### Platform and Sensor Operators

#### is platform
Checks if the event is from a sensor of the given platform.

**Supported platforms:**
- `windows`
- `linux`
- `macos`
- `ios`
- `android`
- `chrome`
- `vpn`
- `text`
- `json`
- GCP
- AWS
- `carbon_black`
- `crowdstrike`
- `1password`
- `office365`
- `msdefender`

**Parameters:**
- `name`: Platform name

**Example:**
```yaml
op: is platform
name: windows
```

#### is windows
Shortcut for checking Windows platform. Takes no additional parameters.

**Example:**
```yaml
event: CODE_IDENTITY
op: is windows
```

#### is 32 bit
Checks if the sensor is 32-bit architecture. Takes no additional parameters.

**Example:**
```yaml
event: NEW_PROCESS
op: is 32 bit
```

#### is 64 bit
Checks if the sensor is 64-bit architecture. Takes no additional parameters.

**Example:**
```yaml
event: NEW_PROCESS
op: is 64 bit
```

#### is arm
Checks if the sensor is ARM architecture. Takes no additional parameters.

**Example:**
```yaml
event: NEW_PROCESS
op: is arm
```

#### is tagged
Determines if the sensor has a specific tag applied.

**Parameters:**
- `tag`: Tag name to check

**Example:**
```yaml
op: is tagged
tag: vip
```

### Network Operators

#### is public address
Checks if an IP address is public (not in private ranges per RFC 1918).

**Parameters:**
- `path`: Path to the IP address

**Example:**
```yaml
event: NETWORK_CONNECTIONS
op: is public address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

#### is private address
Checks if an IP address is private (in RFC 1918 ranges).

**Parameters:**
- `path`: Path to the IP address

**Example:**
```yaml
event: NETWORK_CONNECTIONS
op: is private address
path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
```

#### cidr
Checks if an IP address is within a CIDR network mask.

**Parameters:**
- `path`: Path to the IP address
- `cidr`: CIDR notation (e.g., "10.16.1.0/24")

**Example:**
```yaml
event: NETWORK_CONNECTIONS
op: cidr
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
cidr: 10.16.1.0/24
```

**Multiple CIDRs:**
```yaml
event: NETWORK_CONNECTIONS
op: or
rules:
  - op: cidr
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    cidr: 10.0.0.0/8
  - op: cidr
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    cidr: 192.168.0.0/16
```

### Advanced Operators

#### string distance
Calculates Levenshtein Distance between strings to find variations. Useful for detecting typosquatting, phishing domains, or similar strings.

**Parameters:**
- `path`: Path to the value
- `value`: String or list of strings to compare against
- `max`: Maximum edit distance to match

**Example:**
```yaml
event: DNS_REQUEST
op: string distance
path: event/DOMAIN_NAME
value:
  - onephoton.com
  - www.onephoton.com
max: 2  # matches domains within 2 character edits
```

**Single value:**
```yaml
event: NEW_PROCESS
op: string distance
path: event/FILE_PATH
value: C:\Windows\System32\svchost.exe
max: 3
```

#### lookup
Looks up a value against a threat feed or custom lookup resource.

**Parameters:**
- `path`: Path to the value to lookup
- `resource`: Resource identifier (e.g., "hive://lookup/malwaredomains")
- `case sensitive`: (optional) Default: true

**Example:**
```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malwaredomains
case sensitive: false
```

**Custom lookup:**
```yaml
event: NEW_PROCESS
op: lookup
path: event/HASH
resource: hive://lookup/custom-iocs
```

#### scope
Limits the scope of matching to a specific sub-path of the event. This is crucial for events with arrays, as it applies the rule to each array element individually.

**Parameters:**
- `path`: Path to scope to (usually an array)
- `rule`: Single rule to evaluate in that scope

**Example:**
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

**Why scope matters:**
Without `scope`, rules checking multiple fields might match across different array elements. With `scope`, all conditions must match on the same array element.

#### is older than
Tests if a timestamp value is older than a specified number of seconds.

**Parameters:**
- `path`: Path to the timestamp
- `seconds`: Number of seconds

**Example:**
```yaml
event: login-attempt
op: is older than
path: routing/event_time
seconds: 3600  # 1 hour
```

## All Response Actions

### report
Creates a detection (alert) that is sent to outputs and appears in the Detections page.

**Parameters:**
- `name`: Detection name (supports templates)
- `publish`: (optional) Default: true. Set to false to suppress external publishing
- `priority`: (optional) Severity level (1-5)
- `metadata`: (optional) Free-form key-value metadata
- `detect_data`: (optional) Structured data for extraction

**Example:**
```yaml
- action: report
  name: my-detection-name
  publish: true
  priority: 3
  metadata:
    author: Alice (alice@wonderland.com)
    description: Detected suspicious behavior
    mitre: T1059.001
  detect_data:
    domain: "{{ .event.DOMAIN_NAME }}"
    ip: "{{ .event.IP_ADDRESS }}"
```

**Template name:**
```yaml
- action: report
  name: "Suspicious process {{ .event.FILE_PATH }} on {{ .routing.hostname }}"
```

**Internal detection (D&R chaining only):**
Prefix with `__` to limit scope to D&R rule chaining (won't send to outputs):
```yaml
- action: report
  name: __internal-detection
```

### task
Sends a command to the sensor to perform an action.

**Parameters:**
- `command`: Command to execute (supports templates)
- `investigation`: (optional) Investigation ID to group related tasks

**Common commands:**
- `history_dump` - Get recent process history
- `deny_tree <<routing/this>>` - Kill process tree
- `segregate_network` - Isolate from network
- `rejoin_network` - Remove network isolation
- `yara_scan <resource> --pid <pid>` - Scan process with YARA
- `artifact_get <path>` - Collect artifact
- `mem_map --pid <pid>` - Get memory map
- `os_kill_process --pid <pid>` - Kill process
- `os_suspend --pid <pid>` - Suspend process
- `os_resume --pid <pid>` - Resume process

**Example:**
```yaml
- action: task
  command: history_dump
  investigation: susp-process-inv
```

**Template command:**
```yaml
- action: task
  command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
  investigation: Yara Scan Process
```

```yaml
- action: task
  command: artifact_get {{ .event.FILE_PATH }}
  investigation: file-collection
```

### add tag
Adds a tag to the sensor.

**Parameters:**
- `tag`: Tag name
- `ttl`: (optional) Seconds before tag expires
- `entire_device`: (optional) Apply to all sensors with same device ID (default: false)

**Example:**
```yaml
- action: add tag
  tag: vip
  ttl: 30
  entire_device: false
```

**Permanent tag:**
```yaml
- action: add tag
  tag: compromised
```

### remove tag
Removes a tag from the sensor.

**Parameters:**
- `tag`: Tag name
- `entire_device`: (optional) Remove from all sensors with same device ID (default: false)

**Example:**
```yaml
- action: remove tag
  tag: vip
```

### isolate network
Isolates the sensor from the network. Persists across reboots.

**Parameters:** None

**Example:**
```yaml
- action: isolate network
```

### rejoin network
Removes network isolation from the sensor.

**Parameters:** None

**Example:**
```yaml
- action: rejoin network
```

### add var
Adds a variable associated with the sensor.

**Parameters:**
- `name`: Variable name
- `value`: Variable value (supports `<<path>>` syntax)
- `ttl`: (optional) Seconds before variable expires

**Example:**
```yaml
- action: add var
  name: my-variable
  value: <<event/VOLUME_PATH>>
  ttl: 30
```

**Template value:**
```yaml
- action: add var
  name: last-suspicious-process
  value: "{{ .event.FILE_PATH }}"
```

### del var
Removes a variable from the sensor.

**Parameters:**
- `name`: Variable name

**Example:**
```yaml
- action: del var
  name: my-variable
```

### extension request
Performs an asynchronous request to an extension.

**Parameters:**
- `extension name`: Name of the extension
- `extension action`: Action to perform
- `extension request`: Request payload (supports templates)
- `based on report`: (optional) Use report instead of event as context (default: false)

**Example:**
```yaml
- action: extension request
  extension name: dumper
  extension action: dump
  extension request:
    sid: '{{ .routing.sid }}'
    pid: "{{ .event.PROCESS_ID }}"
  based on report: false
```

### output
Forwards the matched event to a specific Output.

**Parameters:**
- `name`: Output name

**Example:**
```yaml
- action: output
  name: my-output
```

### seal
Enables tamper resistance on the sensor.

**Parameters:** None

**Example:**
```yaml
- action: seal
```

### unseal
Disables tamper resistance on the sensor.

**Parameters:** None

**Example:**
```yaml
- action: unseal
```

### wait
Adds a delay before running the next action. Maximum 1 minute.

**Parameters:**
- `duration`: Delay in seconds (can be string like "10s" or number)

**Example:**
```yaml
- action: wait
  duration: 10s
```

**Numeric format:**
```yaml
- action: wait
  duration: 10
```

### undelete sensor
Un-deletes a sensor that was previously deleted. Only works with deployment events.

**Parameters:** None

**Example:**
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

### re-enroll
Re-enrolls a sensor (typically used with sensor_clone events).

**Parameters:** None

**Example:**
```yaml
detect:
  target: deployment
  event: sensor_clone
  op: is platform
  name: windows
respond:
  - action: re-enroll
```

## Transforms

Transforms modify values before comparison.

### file name
Extracts just the filename from a full path.

**Applied to:** Path values

**Example:**
```yaml
event: NEW_PROCESS
op: is
path: event/FILE_PATH
file name: true
value: svchost.exe
```

This matches:
- `C:\Windows\System32\svchost.exe`
- `C:\Temp\svchost.exe`
- `/usr/local/bin/svchost.exe`

### sub domain
Extracts specific components from a domain name using slice notation.

**Applied to:** Domain values

**Slice notation:**
- `0:2` = first 2 components: `aa.bb` from `aa.bb.cc.dd`
- `-1` = last component: `cc` from `aa.bb.cc`
- `-2:` = last 2 components: `bb.cc` from `aa.bb.cc`
- `1:` = all starting at index 1: `bb.cc` from `aa.bb.cc`
- `:` = test operator on every component individually

**Example:**
```yaml
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
sub domain: "-2:"  # last 2 components
value: example.com
```

This extracts `example.com` from:
- `www.subdomain.example.com`
- `mail.example.com`
- `example.com`

**First component:**
```yaml
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
sub domain: "0"
value: www
```

**Test each component:**
```yaml
event: DNS_REQUEST
op: contains
path: event/DOMAIN_NAME
sub domain: ":"
value: evil
```

This matches if ANY component contains "evil":
- `evil.example.com`
- `www.evil.com`
- `sub.domain.evil.net`

### length of
Compares the length of a string instead of its value.

**Applied to:** String comparison operators

**Example:**
```yaml
event: NEW_PROCESS
op: is greater than
path: event/COMMAND_LINE
value: 1000
length of: true
```

**With is lower than:**
```yaml
event: DNS_REQUEST
op: is lower than
path: event/DOMAIN_NAME
value: 5
length of: true
```

## LimaCharlie Structure Reference

Understanding the core data structures in LimaCharlie is essential for writing effective D&R rules. This section explains what Events and Detections are, their structure, and how to work with them.

### Events vs Detections

**Events** are raw telemetry from sensors and adapters. **Detections** are alerts created when your D&R rules match events.

```
Sensor → Event → D&R Rule Matches → Detection
```

### Event Structure

Every event has two top-level objects:

```json
{
  "routing": { /* metadata about where/when/who */ },
  "event": { /* event-specific data */ }
}
```

#### The `routing` Object

Contains **metadata** consistent across all event types:

| Field | Type | Description | D&R Usage |
|-------|------|-------------|-----------|
| `sid` | string (UUID) | Sensor ID | Filter/correlate by endpoint |
| `hostname` | string | Sensor hostname | Host-based detection rules |
| `event_type` | string | Type of event | `event: NEW_PROCESS` filters |
| `event_time` | integer | Unix timestamp (milliseconds) | Temporal correlation, time-based rules |
| `event_id` | string (UUID) | Unique event ID | Deduplication, tracking |
| `oid` | string (UUID) | Organization ID | Multi-tenant filtering |
| `iid` | string (UUID) | Installation Key ID | Deployment group filtering |
| `did` | string (UUID) | Device ID (hardware) | Track across reinstalls |
| `plat` | integer | Platform (Windows, Linux, etc.) | OS-specific rules with `op: is windows` |
| `arch` | integer | Architecture (x86, x64, ARM) | Architecture-specific detection |
| `int_ip` | string | Internal IP address | Network segmentation rules |
| `ext_ip` | string | External IP address | Geolocation-based rules |
| `this` | string (hash) | Current process/object hash | Process tracking across events |
| `parent` | string (hash) | Parent process hash | Process tree correlation |
| `target` | string (hash) | Target object hash | Track objects in actions |
| `tags` | array | Sensor tags at event time | Tag-based filtering |
| `moduleid` | integer | Sensor module ID | Module-specific rules |

#### The `event` Object

Contains **event-specific data** that varies by event type:

- **NEW_PROCESS**: `FILE_PATH`, `COMMAND_LINE`, `PROCESS_ID`, `USER_NAME`, `PARENT`, `HASH`
- **DNS_REQUEST**: `DOMAIN_NAME`, `IP_ADDRESS`, `DNS_TYPE`, `DNS_FLAGS`
- **NETWORK_CONNECTIONS**: `NETWORK_ACTIVITY` array with connection details
- **FILE_MODIFIED**: `FILE_PATH`, `ACTION`, `HASH`, `SIZE`
- **WEL** (Windows Event Logs): `EVENT` object with nested Windows event structure

### Detection Structure

When a D&R rule matches, LimaCharlie creates a Detection with this structure:

```json
{
  "cat": "Detection Name",
  "source": "dr-general",
  "routing": { /* inherited from event */ },
  "detect": { /* copy of event data */ },
  "detect_id": "unique-uuid",
  "priority": 5,
  "detect_data": { /* extracted IOCs */ },
  "link": "https://playbook-url",
  "author": "security-team",
  "source_rule": "rule-name",
  "rule_tags": ["windows", "process"]
}
```

#### Detection Fields

| Field | Type | Description | How to Set |
|-------|------|-------------|------------|
| `cat` | string | Detection name | `name:` in `report` action |
| `source` | string | Rule hive (dr-general, dr-managed) | Automatic |
| `routing` | object | Same as event routing | Inherited automatically |
| `detect` | object | Triggering event data | Inherited automatically |
| `detect_id` | string | Unique detection ID | Automatic |
| `priority` | integer | Priority 0-10 (higher = more critical) | `priority:` in response |
| `detect_data` | object | **Structured IOCs** | Custom fields in `report` action |
| `link` | string | URL to playbook/docs | `link:` in response |
| `author` | string | Rule author | `author:` in response |
| `source_rule` | string | Rule name | Automatic from rule name |
| `rule_tags` | array | Tags from rule | `metadata: {tags: [...]}` |

### Using Routing Fields in D&R Rules

#### Filter by Platform

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows  # Same as: path: routing/plat, value: 268435456
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
```

#### Correlate by Process Hash

```yaml
# Track all events from a specific process
detect:
  op: is
  path: routing/this
  value: "a443f9c48bef700740ef27e062c333c6"
```

#### Filter by Sensor Tags

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: exists
      path: routing/tags
    - op: contains
      path: routing/tags
      value: critical-servers
```

#### Host-Based Rules

```yaml
detect:
  event: NEW_PROCESS
  op: is
  path: routing/hostname
  value: domain-controller-01
```

### Extracting Structured Data with detect_data

The `detect_data` field is powerful for creating structured IOCs:

```yaml
respond:
  - action: report
    name: Suspicious Process Execution
    priority: 7
    # These create detect_data fields:
    suspicious_file: << event/FILE_PATH >>
    command_line: << event/COMMAND_LINE >>
    process_hash: << routing/this >>
    parent_hash: << routing/parent >>
    hostname: << routing/hostname >>
    timestamp: << routing/event_time >>
```

Creates a Detection with:

```json
{
  "cat": "Suspicious Process Execution",
  "priority": 7,
  "detect_data": {
    "suspicious_file": "C:\\Windows\\System32\\cmd.exe",
    "command_line": "cmd.exe /c whoami",
    "process_hash": "a443f9c48bef700740ef27e062c333c6",
    "parent_hash": "42217cb0326ca254999554a862c333c6",
    "hostname": "workstation-01",
    "timestamp": 1656959942437
  }
}
```

### Event → Detection Example

**Original Event:**
```json
{
  "routing": {
    "sid": "bb4b30af-...",
    "hostname": "workstation-01",
    "event_type": "DNS_REQUEST",
    "this": "a443f9c4..."
  },
  "event": {
    "DOMAIN_NAME": "malicious.example.com",
    "IP_ADDRESS": "198.51.100.42"
  }
}
```

**D&R Rule:**
```yaml
detect:
  event: DNS_REQUEST
  op: ends with
  path: event/DOMAIN_NAME
  value: .example.com

respond:
  - action: report
    name: Suspicious DNS Query
    priority: 5
    queried_domain: << event/DOMAIN_NAME >>
    resolved_ip: << event/IP_ADDRESS >>
    querying_process: << routing/this >>
```

**Resulting Detection:**
```json
{
  "cat": "Suspicious DNS Query",
  "source": "dr-general",
  "routing": { /* same as event */ },
  "detect": { /* same as event */ },
  "priority": 5,
  "detect_data": {
    "queried_domain": "malicious.example.com",
    "resolved_ip": "198.51.100.42",
    "querying_process": "a443f9c4..."
  }
}
```

### Best Practices for D&R Rules

1. **Use `event:` at top level**: Filter by event type early for performance
2. **Leverage routing for context**: Use `routing/hostname`, `routing/tags`, `routing/this` for context
3. **Extract meaningful IOCs**: Always populate `detect_data` with actionable indicators
4. **Set priority correctly**: Use 0-3 for info, 4-6 for medium, 7-10 for critical
5. **Correlate with hashes**: Use `routing/this` and `routing/parent` to track process relationships
6. **Platform-specific rules**: Use `op: is windows` or check `routing/plat` explicitly

## Event Paths

### Complete Routing Paths

All routing metadata available:

```yaml
path: routing/sid              # Sensor ID
path: routing/hostname         # Host name
path: routing/event_type       # Event type
path: routing/event_time       # Event timestamp (Unix epoch)
path: routing/this             # Current atom ID
path: routing/parent           # Parent atom ID
path: routing/tags             # Sensor tags (array)
path: routing/plat             # Platform ID
path: routing/arch             # Architecture
path: routing/int_ip           # Internal IP address
path: routing/ext_ip           # External IP address
path: routing/iid              # Installation ID
path: routing/oid              # Organization ID
```

### Common Event-Specific Paths

Paths vary by event type. Common patterns:

**Process Events (NEW_PROCESS, EXISTING_PROCESS, TERMINATE):**
```yaml
path: event/FILE_PATH
path: event/COMMAND_LINE
path: event/PROCESS_ID
path: event/PARENT/FILE_PATH
path: event/PARENT/PROCESS_ID
path: event/USER_NAME
path: event/HASH
```

**Network Events (NETWORK_CONNECTIONS):**
```yaml
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
path: event/NETWORK_ACTIVITY/SOURCE/PORT
path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
path: event/NETWORK_ACTIVITY/DESTINATION/PORT
path: event/NETWORK_ACTIVITY/BYTES_SENT
path: event/NETWORK_ACTIVITY/BYTES_RECEIVED
```

**DNS Events (DNS_REQUEST):**
```yaml
path: event/DOMAIN_NAME
path: event/IP_ADDRESS
```

**File Events (FILE_TYPE_ACCESSED, NEW_DOCUMENT):**
```yaml
path: event/FILE_PATH
path: event/HASH
path: event/SIZE
```

**Windows Event Logs (WEL):**
```yaml
path: event/EVENT/System/EventID
path: event/EVENT/System/Channel
path: event/EVENT/System/Provider/@Name
path: event/EVENT/EventData/Data/?/@Name
path: event/EVENT/EventData/Data/?/#text
```

## Stateful Rules Advanced

### with child
Matches direct children of the initial event.

**Parameters:**
- All standard detection parameters apply to the child rule
- `count`: (optional) Minimum number of matching children
- `within`: (optional) Time window in seconds

**Example:**
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

**With counting:**
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

### with descendant
Matches any descendant (children, grandchildren, etc.) of the initial event.

**Parameters:**
- All standard detection parameters apply to the descendant rule
- `count`: (optional) Minimum number of matching descendants
- `within`: (optional) Time window in seconds

**Example:**
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

### with events
Detects repetition of events close together on the same sensor.

**Parameters:**
- All standard detection parameters
- `count`: Required minimum number of matching events
- `within`: Required time window in seconds

**Example:**
```yaml
event: WEL
op: is windows
with events:
  event: WEL
  op: is
  path: event/EVENT/System/EventID
  value: '4625'  # failed login
  count: 5
  within: 60
```

### report latest event
By default, stateful rules report the parent event. Use `report latest event: true` to report the child/descendant instead.

**Example:**
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

Now the detection includes Chrome's process details instead of Outlook's.

### is stateless
Within a stateful context, use `is stateless: true` to require all sub-rules to match a single event.

**Example:**
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

Without `is stateless: true`, the `and` would match if ANY child matched the first condition and ANY child (possibly different) matched the second condition. With it, the same child must match both.

## Suppression Advanced

### Complete Suppression Parameters

**Parameters:**
- `max_count`: Maximum number of times to execute action
- `min_count`: (optional) Minimum activations before first execution
- `period`: Time window (formats: `ns`, `us`, `ms`, `s`, `m`, `h`)
- `is_global`: Scope across entire org (true) or per sensor (false)
- `keys`: (optional) List of key values for grouping
- `count_path`: (optional) Path to dynamic increment value

### Reduce Frequency

```yaml
- action: report
  name: evil-process-detected
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.FILE_PATH }}'
      - 'evil-process-detected'
```

**How it works:** Creates a suppression key from the specified keys. Action executes at most `max_count` times within `period` for each unique key combination.

### Threshold Activation

```yaml
- action: report
  name: high-alerts
  suppression:
    min_count: 3   # must match 3 times first
    max_count: 3   # then alert once
    period: 24h
```

**How it works:** Action doesn't execute until detection matches `min_count` times. Then executes `max_count` times (usually same as min_count for single alert).

### Variable Count

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

**How it works:** Instead of incrementing by 1 per activation, increments by the value at `count_path`. Useful for tracking cumulative metrics.

### Practical Examples

**Prevent duplicate sensor commands:**
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

**Rate limit per file path:**
```yaml
- action: report
  name: suspicious-file-access
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
    max_count: 5
    period: 1h
```

**Alert on threshold:**
```yaml
- action: report
  name: excessive-failed-logins
  suppression:
    is_global: false
    keys:
      - '{{ .routing.sid }}'
    min_count: 10
    max_count: 10
    period: 5m
```

## Time-Based Rules

Limit when rules are active using time descriptors.

**Parameters:**
- `day_of_week_start`: Start day (1=Monday, 7=Sunday)
- `day_of_week_end`: End day (1=Monday, 7=Sunday)
- `time_of_day_start`: Start time (HHMM format, 24-hour)
- `time_of_day_end`: End time (HHMM format, 24-hour)
- `tz`: Time zone ([TZ database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

**Example - After hours detection:**
```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: chrome.exe
case sensitive: false
times:
  - day_of_week_start: 2     # Monday
    day_of_week_end: 6       # Friday
    time_of_day_start: 2200  # 10 PM
    time_of_day_end: 2359    # 11:59 PM
    tz: America/Los_Angeles
  - day_of_week_start: 2
    day_of_week_end: 6
    time_of_day_start: 0     # 12 AM
    time_of_day_end: 500     # 5 AM
    tz: America/Los_Angeles
```

**Example - Weekend only:**
```yaml
event: NEW_PROCESS
op: contains
path: event/COMMAND_LINE
value: sensitive-operation
times:
  - day_of_week_start: 6     # Saturday
    day_of_week_end: 7       # Sunday
    time_of_day_start: 0
    time_of_day_end: 2359
    tz: UTC
```

**Example - Business hours:**
```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malwaredomains
times:
  - day_of_week_start: 1     # Monday
    day_of_week_end: 5       # Friday
    time_of_day_start: 900   # 9 AM
    time_of_day_end: 1700    # 5 PM
    tz: America/New_York
```

## Event Targets

Most rules target sensor events (default), but you can specify other targets.

### Artifact Collection
Target artifacts collected by the sensor.

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

**Common artifact paths:**
- `/text` - Text content
- `/routing/type` - Artifact type
- `/routing/source` - Source identifier

### Deployment Events
Target organizational events like sensor enrollment, deletion, or cloning.

**sensor_clone:**
```yaml
detect:
  target: deployment
  event: sensor_clone
  op: is platform
  name: windows
respond:
  - action: re-enroll
```

**deleted_sensor:**
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

**new_sensor:**
```yaml
detect:
  target: deployment
  event: new_sensor
  op: is platform
  name: windows
respond:
  - action: add tag
    tag: new-windows-sensor
```

### Billing Events
Target billing records to monitor usage.

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
    suppression:
      count_path: event/record/v
      is_global: true
      keys:
        - storage-usage
      max_count: 1099511627776  # 1TB
      min_count: 1099511627776
      period: 24h
```

**Common billing keys:**
- `storage:bytes` - Storage usage
- `events:processed` - Events processed
- `ext-*` - Extension usage

### Detection Events
Target detections from other rules (D&R chaining).

```yaml
detect:
  target: detect
  event: __internal-detection
  op: is
  path: detect/name
  value: __internal-detection
respond:
  - action: report
    name: final-detection
```

## Template Strings

Many fields support Go template syntax for dynamic values.

### Available Context

**In action fields:**
- `.event.*` - Event data
- `.routing.*` - Routing metadata

**In report action (also includes):**
- `.detect.*` - Detection data from the triggering rule

### Template Functions

**Basic access:**
```yaml
"{{ .event.FILE_PATH }}"
"{{ .routing.hostname }}"
"{{ .routing.sid }}"
```

**Nested/array access:**
```yaml
"{{ index .event.NETWORK_ACTIVITY 0 }}"
"{{ index (index .event.NETWORK_ACTIVITY 0) \"SOURCE\" \"IP_ADDRESS\" }}"
```

**Conditional:**
```yaml
"{{ if .event.USER_NAME }}User: {{ .event.USER_NAME }}{{ else }}No user{{ end }}"
```

**Iteration (not commonly needed in D&R):**
```yaml
"{{ range .routing.tags }}{{ . }}, {{ end }}"
```

### Common Template Patterns

**Action names:**
```yaml
- action: report
  name: "Process {{ .event.FILE_PATH }} on {{ .routing.hostname }}"
```

**Task commands:**
```yaml
- action: task
  command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
```

```yaml
- action: task
  command: artifact_get "{{ .event.FILE_PATH }}"
```

**Suppression keys:**
```yaml
suppression:
  keys:
    - '{{ .event.FILE_PATH }}'
    - '{{ .routing.hostname }}'
```

**Metadata:**
```yaml
metadata:
  hostname: "{{ .routing.hostname }}"
  sensor_id: "{{ .routing.sid }}"
  process: "{{ .event.FILE_PATH }}"
```

**detect_data:**
```yaml
detect_data:
  domain: "{{ .event.DOMAIN_NAME }}"
  ip: "{{ .event.IP_ADDRESS }}"
  sensor: "{{ .routing.hostname }}"
  tags: "{{ .routing.tags }}"
```

### Special Syntax

**Double angle brackets (path reference):**
```yaml
command: deny_tree <<routing/this>>
```

This is NOT a template - it's a special D&R syntax for referencing event paths. Used in sensor commands.

**Single angle brackets (invalid):**
Don't use `<< .event.field >>` - use either:
- `<<event/field>>` for path reference
- `{{ .event.field }}` for template

---

[Back to SKILL.md](SKILL.md) | [Examples](EXAMPLES.md) | [Troubleshooting](TROUBLESHOOTING.md)
