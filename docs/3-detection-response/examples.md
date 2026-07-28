# Detection and Response Examples

These sample detection and response rules help you write efficient rules with LimaCharlie telemetry. For more rules, see [Sigma Rules](managed-rulesets/sigma-converter.md).

## Translating Existing Rules

[uncoder.io](https://uncoder.io/) by [SOC Prime](https://socprime.com/) helps you learn by analogy. If you know another platform for rules or search queries (Sigma, Splunk, Kibana, etc.), you can use uncoder to translate to LimaCharlie D&R rules.

More resources are available.

This video shows how to use community resources with LimaCharlie.

## Examples

In limacharlie.io, the same rule configuration is in YAML format. This format is easier to edit. For example:

```yaml
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

```yaml
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

Add the "vip" tag to any Sensor where the CEO logs in.

```yaml
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

This example looks for connections to or from `sshd` with a non-RFC1918 IP address. The rule looks only for network connections, not for logons. On an internet-facing system the rule can be noisy, but it still shows an exposed service.

```yaml
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

The `report` uses [Go Templates](../4-data-queries/template-strings.md) to include the offending IP address in the detection name.

### RDP from External IP Address

This example is similar to the SSH example above. It looks for RDP connections from an external IP address. The rule looks only for network connections, not for logons. On an internet-facing system the rule can be noisy, but it still shows an exposed service.

```yaml
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

The `report` uses [Go Templates](../4-data-queries/template-strings.md) to include the offending IP address in the detection name.

### Suspicious Windows Executable Names

```yaml
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

Stop the sensor from sending a specific event to the cloud. Use this rule to limit verbose data sources that you do not need.

```yaml
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: exfil_del NEW_DOCUMENT
```

### Windows Event Logs

This example looks for a specific Event ID in WEL events.

```yaml
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

This example shows nested boolean logic. The detection looks for these conditions:
 ((`4697` OR `7045`) in the `System` log) OR (`4698` in the `Security` log)

```yaml
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

Enable File Integrity Monitoring of some directories each time that a Windows sensor connects.

```yaml
# Detection
event: CONNECTED
op: is platform
name: windows

# Response
- action: task
  command: fim_add --pattern 'C:\*\Programs\Startup\*' --pattern '\REGISTRY\*\Microsoft\Windows\CurrentVersion\Run*'
```

Similar example for a Linux web server.

```yaml
# Detection
event: CONNECTED
op: is platform
name: linux

# Response
- action: task
  command: fim_add --pattern '/var/www/*'
```

#### FIM Hit Detection

A FIM pattern that you add with `fim_add` only puts `FIM_HIT` events on the timeline of the affected system. To see the hits on a FIM rule, capture the event and generate a Detection.

```yaml
# Detection
event: FIM_HIT
op: exists
path: event/FILE_PATH

# Response
- action: report
  name: FIM Hit - {{ .event.FILE_PATH }}
```

### YARA Scanning

Resource Utilization

CPU intensive actions such as a YARA scan can decrease endpoint performance. Always test rules that run sensor commands, such as the examples below, before you deploy them at scale in production. Use [suppression](../8-reference/response-actions.md#suppression) to stop runaway conditions.

These examples use D&R rules to start automatic YARA scans on an endpoint. The YARA rule must exist in your organization before you use it in a D&R rule.

#### YARA Scan Processes

This example looks for `NEW_PROCESS` events that obey some criteria. It then starts a YARA scan of the process ID in memory. This rule, or a similar rule, also needs a companion [YARA Detection](#yara-detections) rule.

```yaml
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

The `suppression` block stops a scan of the same `PROCESS_ID` more than one time each minute. This stops a resource runaway situation.

#### YARA Scan Files

This example looks for `NEW_DOCUMENT` events that obey some criteria. It then starts a YARA scan of the file path. This rule, or a similar rule, also needs a companion [YARA Detection](#yara-detections) rule.

```yaml
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

The `suppression` block stops a scan of the same `FILE_PATH` more than one time each minute. This stops a resource runaway situation.

### YARA Detections

A YARA scan only sends a `YARA_DETECTION` event to the timeline of the affected system. To see the hits from a YARA scan, capture the event and generate a Detection. The two examples below separate a YARA detection on disk from a YARA detection in memory. The rules check for `event/PROCESS/*` fields to find if the detection is a file or a process. Security teams can give a different severity to each one (dormant malware or running malware).

#### YARA Detection On-Disk (file)

```yaml
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

```yaml
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

Both rules generate a Detection report and add a tag to the system where the detection occurred.

### Mention of an Internal Resource

Look for references to private URLs in proxy logs.

```yaml
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

Sometimes users install a sensor on a VM image by mistake. Each new instance of the image then uses the same sensor ID (SID) on different machines with different names. When LimaCharlie detects this, it produces a `sensor_clone` event.

You can use these events to deduplicate. This example targets Windows clones.

```yaml
# Detection
target: deployment
event: sensor_clone
op: is platform
name: windows

# Response
- action: re-enroll
```

Sensors send telemetry to the LimaCharlie cloud as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

---

## See Also

- [D&R Rules Overview](index.md)
- [Detection Operators](../8-reference/detection-logic-operators.md)
- [Response Actions](../8-reference/response-actions.md)
