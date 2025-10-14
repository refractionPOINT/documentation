# Detection and Response Examples

The following are sample detection and response rules can help you get started in crafting efficient rules utilizing LimaCharlie's telemetry. In addition to these rules, we also recommend checking out [Sigma Rules](/v2/docs/sigma-rules) for more rules.

## Translating Existing Rules

Before listing examples, it's worth mentioning [uncoder.io](https://uncoder.io/) by [SOC Prime](https://socprime.com/) is a great resource for learning by analogy. If you're already familiar with another platform for rules or search queries (Sigma, Splunk, Kibana, etc.) you can use uncoder to translate to LimaCharlie's D&R rules.

## Examples

Note that through limacharlie.io, in order to provide an easier to edit format, the same rule configuration is used but is in YAML format instead. For example:

```
# Detection
op: ends with
event: NEW_PROCESS
path: event/FILE_PATH
value: .scr

# Response
- action: report
  name: susp_screensaver
- action: add tag
  tag: uses_screensaver
  ttl: 80000
```

### WanaCry

Simple WanaCry detection and mitigation rule:

```
# Detection
op: ends with
event: NEW_PROCESS
path: event/FILE_PATH
value: wanadecryptor.exe
case sensitive: false

# Response
- action: report
  name: wanacry
- action: task
  command: history_dump
- action: task
  command:
    - deny_tree
    - <<routing/this>>
```

### Classify Users

Tag any Sensor where the CEO logs in with "vip".

```
# Detection
op: is
event: USER_OBSERVED
path: event/USER_NAME
value: stevejobs
case sensitive: false

# Response
- action: add tag
  tag: vip
```

### SSH from External IP Address

The following example looks for connections to/from `sshd` involving a non-RFC1918 IP Address. Be mindful that this is only looking for network connections, not actual logons, so this could be noisy on an internet-facing system but still indicative of an exposed service.

```
# Detection
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: ends with
    path: event/FILE_PATH
    value: /sshd
  - op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS

 # Response
- action: report
  name: >-
    SSH from EXTERNAL IP - {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}
```

The `report` uses [Go Templates](/v2/docs/template-strings-and-transforms) to include the offending IP address in the detection name.

### RDP from External IP Address

Similar to the above SSH example, this example looks for RDP connections from an external IP address. Be mindful that this is only looking for network connections, not actual logons, so this could be noisy on an internet-facing system but still indicative of an exposed service.

```
# Detection
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

# Response
- action: report
  name: >-
    RDP from EXTERNAL IP - {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}
```

The `report` uses [Go Templates](/v2/docs/template-strings-and-transforms) to include the offending IP address in the detection name.

### Suspicious Windows Executable Names

```
# Detection
event: CODE_IDENTITY
op: matches
path: event/FILE_PATH
case sensitive: false
re: .*((\\.txt)|(\\.doc.?)|(\\.ppt.?)|(\\.xls.?)|(\\.zip)|(\\.rar)|(\\.rtf)|(\\.jpg)|(\\.gif)|(\\.pdf)|(\\.wmi)|(\\.avi)|( {5}.*))\\.exe

# Response
- action: report
  name: Executable with suspicious double extension
```

### Disable an Event at the Source

Turn off the sending of a specific event to the cloud. Useful to limit some verbose data sources when not needed.

```
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: exfil_del NEW_DOCUMENT
```

### Windows Event Logs

A simple example of looking for a specific Event ID in WEL events.

```
# Detection
event: WEL
op: and
rules:
  - op: is
    path: event/EVENT/System/EventID
    value: '4625'
  - op: is
    path: event/EVENT/System/Channel
    value: Security

# Response
- action: report
  name: Failed Logon
```

### Nested Logic

An example demonstrating nested boolean logic. This detection looks specifically for the following conditions:
 ((`4697` OR `7045`) in the `System` log) OR (`4698` in the `Security` log)

```
# Detection
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

### File Integrity Monitoring

#### Monitoring Sensitive Directories

Make sure the File Integrity Monitoring of some directories is enabled whenever Windows sensors connect.

```
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: fim_add --pattern 'C:\*\Programs\Startup\*' --pattern '\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*'
```

Similar example for a Linux web server.

```
# Detection
event: CONNECTED
op: is platform
name: linux

# Response
- action: task
  command: fim_add --pattern '/var/www/*'
```

#### FIM Hit Detection

Adding a FIM pattern with `fim_add` by itself will only cause `FIM_HIT` events to be generated on the affected system's timeline. To know that we have positive hits on a FIM rule, we want to capture the relevant event and generate a proper Detection.

```
# Detection
event: FIM_HIT
op: exists
path: event/FILE_PATH

# Response
- action: report
  name: FIM Hit - {{ .event.FILE_PATH }}
```

### YARA Scanning

> **Resource Utilization**
>
> Performing CPU intensive actions such as YARA scanning can impact endpoint performance if not optimized. Be sure to always test rules that carry out sensor commands (like the examples below) before deploying at scale in production. Use [suppression](/v2/docs/response-actions#suppression) to prevent runaway conditions.

Here are a few examples of using D&R rules to initiate automatic YARA scans on an endpoint. Note that the defined YARA rule must exist in your org before using it in a D&R rule.

#### YARA Scan Processes

This example looks for `NEW_PROCESS` events that meet certain criteria, then initiates a YARA scan against the offending process ID in memory. Note, this or a similar D&R rule will also depend on a companion [YARA Detection](/v2/docs/detection-and-response-examples#yara-detections) rule.

```
# Detection
event: NEW_PROCESS
op: and
rules:
  - op: starts with
    path: event/FILE_PATH
    value: C:\Users\
  - op: contains
    path: event/FILE_PATH
    value: \Downloads\

# Response
## Report is optional, but informative
- action: report
  name: Execution from Downloads directory
## Initiate a sensor command to yara scan the PROCESS_ID
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

Notice the use of `suppression` to prevent the same `PROCESS_ID` from being scanned more than once per minute to prevent a resource runaway situation.

#### YARA Scan Files

This example looks for `NEW_DOCUMENT` events that meet certain criteria, then initiates a YARA scan against the offending file path. Note, this or a similar D&R rule will also depend on a companion [YARA Detection](/v2/docs/detection-and-response-examples#yara-detections) rule.

```
# Detection
event: NEW_DOCUMENT
op: and
rules:
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .\:\\(users|windows\\temp)\\.*
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .*\.(exe|dll)

# Response
## Report is optional, but informative
- action: report
  name: Executable written to Users or Temp (yara scan)
## Initiate a sensor command to yara scan the FILE_PATH
- action: task
  command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
  investigation: Yara Scan Executable
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
      - Yara Scan Executable
    max_count: 1
    period: 1m
```

Notice the use of `suppression` to prevent the same `FILE_PATH` from being scanned more than once per minute to prevent a resource runaway situation.

### YARA Detections

Running a YARA scan by itself only sends a `YARA_DETECTION` event to the affected system's timeline. To know that we have positive hits on a YARA scan, we want to capture the relevant event and generate a proper Detection. The following two examples split out a YARA detection on-disk, versus in-memory. Notice we simply check for the presence of `event/PROCESS/*` fields to determine if it's a file or process detection, which may have different severities to security teams (dormant malware versus running malware).

#### YARA Detection On-Disk (file)

```
# Detection
event: YARA_DETECTION
op: and
rules:
  - not: true
    op: exists
    path: event/PROCESS/*
  - op: exists
    path: event/RULE_NAME

# Response
- action: report
  name: YARA Detection on Disk - {{ .event.RULE_NAME }}
- action: add tag
  tag: yara_detection_disk
  ttl: 80000
```

#### YARA Detection In-Memory (process)

```
# Detection
event: YARA_DETECTION
op: and
rules:
  - op: exists
    path: event/RULE_NAME
  - op: exists
    path: event/PROCESS/*

# Response
- action: report
  name: YARA Detection in Memory - {{ .event.RULE_NAME }}
- action: add tag
  tag: yara_detection_memory
  ttl: 80000
```

Both rules will generate a Detection report and add a tag to the system which the detection occurred on.

### Mention of an Internal Resource

Look for references to private URLs in proxy logs.

```
# Detection
target: artifact
op: contains
path: /text
value: /corp/private/info

# Response
- action: report
  name: web-proxy-private-url
```

### De-duplicate Cloned Sensors

Sometimes users install a sensor on a VM image by mistake. This means every time a new instance of the image gets started the same sensor ID (SID) is used for multiple boxes with different names. When detected, LimaCharlie produces a `sensor_clone` event.

We can use these events to deduplicate. This example targets Windows clones.

```
# Detection
target: deployment
event: sensor_clone
op: is platform
name: windows

# Response
- action: re-enroll
```