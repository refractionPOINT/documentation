# Incident Response Troubleshooting Guide

This document provides troubleshooting guidance for common incident response challenges, technical issues, and operational questions.

## Sensor Command Issues

### Command Not Executing

**Symptoms:**
- Sensor command appears to be sent but no response received
- Command shows as "pending" indefinitely
- No output in timeline or investigation view

**Troubleshooting Steps:**

1. **Check sensor connectivity:**
   - Verify sensor shows as "online" in web console
   - Check last heartbeat timestamp
   - Review connectivity history

2. **Verify platform compatibility:**
   - Not all commands work on all platforms
   - Check REFERENCE.md for platform-specific commands
   - Example: `mem_handles` only works on Windows

3. **Check command syntax:**
   - Review command for typos
   - Verify required parameters included
   - Check file path format (case-sensitive on Linux)
   - Use quotes for paths with spaces

4. **Review sensor permissions:**
   - Sensor may lack required permissions (rare)
   - Check sensor event log for permission errors
   - Verify sensor installed with appropriate privileges

5. **Check sensor timeline for errors:**
   - Look for COMMAND_ERROR events
   - Review error messages for details

**Common Mistakes:**

```bash
# Wrong (missing required parameter)
mem_map

# Correct
mem_map --pid 1234

# Wrong (incorrect path separator for Windows)
file_info C:/Windows/System32/file.exe

# Correct
file_info C:\Windows\System32\file.exe

# Wrong (case mismatch on Linux)
file_info /VAR/LOG/auth.log

# Correct
file_info /var/log/auth.log
```

### Command Timeout

**Symptoms:**
- Command takes very long to execute
- Command appears to hang
- Partial results returned

**Causes:**
- Large file operations (artifact_get on large files)
- Recursive directory listing on large directories
- Memory dumps of large processes
- Network bandwidth limitations

**Solutions:**

1. **For large files:**
   - Use `file_info` and `file_hash` first to verify file before collection
   - Consider bandwidth and storage limits
   - Schedule large collections during off-hours

2. **For directory listings:**
   ```bash
   # Avoid recursive listing of large directories
   # Wrong
   dir_list C:\Users --recurse

   # Better - target specific subdirectories
   dir_list C:\Users\username\Downloads
   ```

3. **For memory operations:**
   - Memory dumps take time proportional to process size
   - Use dumper extension for full memory dumps (more efficient)
   - Consider using `mem_map` first to identify regions of interest

### "Access Denied" Errors

**Symptoms:**
- Command fails with "access denied" or "permission denied" error
- File operations fail on protected files
- Registry operations fail on protected keys

**Causes:**
- File locked by another process
- Protected system files (Windows protected files)
- SELinux/AppArmor restrictions (Linux)
- Antivirus protection

**Solutions:**

1. **Terminate locking process first:**
   ```bash
   # Identify process using file
   # On Windows, use handle finding
   mem_find_handle --pid <pid> --path "C:\locked-file.exe"

   # Terminate process
   os_kill_process --pid <pid>

   # Then delete file
   file_del C:\locked-file.exe
   ```

2. **For protected files:**
   - Collect using `artifact_get` instead of deletion
   - Boot into safe mode (requires manual intervention)
   - Some system files cannot be deleted while OS running

3. **For Linux with SELinux/AppArmor:**
   - Check security context
   - May require security policy adjustment (outside LC scope)

## Network Isolation Issues

### Isolation Not Working

**Symptoms:**
- Network isolation command executed but system still has connectivity
- System can still reach internet
- Other systems can still reach isolated system

**Troubleshooting:**

1. **Verify isolation type used:**
   ```yaml
   # Stateful isolation (persists across reboot) - D&R action
   - action: isolate network

   # Stateless isolation (does not persist) - sensor command
   segregate_network
   ```

2. **Check platform support:**
   - Windows: Fully supported
   - Linux: Fully supported
   - macOS: Fully supported
   - ChromeOS: Limited

3. **Verify isolation event in timeline:**
   - Look for SEGREGATE_NETWORK event
   - Check event for error messages
   - Confirm event timestamp matches isolation attempt

4. **Test isolation:**
   ```bash
   # Check network connections after isolation
   netstat

   # Should only see LC relay connections
   # No other outbound connections should be present
   ```

5. **Check sensor version:**
   - Ensure sensor is recent version
   - Update sensor if outdated

**Important Notes:**

- Network isolation maintains LC connectivity via relay
- Isolation blocks direct internet and LAN access
- DNS resolution is blocked (except for LC infrastructure)
- Local network discovery is blocked

### Cannot Rejoin Network

**Symptoms:**
- Rejoin command executed but system still isolated
- System cannot reach network after rejoin attempt

**Troubleshooting:**

1. **Match isolation and rejoin types:**
   ```yaml
   # If you used stateful isolation (D&R action)
   - action: isolate network

   # Must use stateful rejoin
   - action: rejoin network

   # If you used stateless isolation (command)
   segregate_network

   # Must use stateless rejoin
   rejoin_network
   ```

2. **Check for multiple isolation actions:**
   - If multiple D&R rules applied isolation, may need multiple rejoins
   - Review timeline for SEGREGATE_NETWORK events
   - Count isolation events and ensure matching rejoin count

3. **Verify rejoin event:**
   - Look for REJOIN_NETWORK event in timeline
   - Check for error messages

4. **Manual intervention if needed:**
   - If system remains isolated, reboot may clear stateless isolation
   - For stateful isolation, ensure rejoin action executed successfully

### Isolation Interfering with Business Operations

**Symptoms:**
- Isolated system needs network access for business function
- Critical service impacted by isolation

**Solutions:**

1. **Temporary rejoin for specific tasks:**
   ```yaml
   # Rejoin network
   - action: rejoin network

   # Perform necessary business function (manual)

   # Re-isolate after task complete
   - action: isolate network
   ```

2. **Use investigation box:**
   - If available, move investigation to isolated VLAN
   - Maintain partial network access for business needs

3. **Plan ahead:**
   - For critical systems, have isolation exception process
   - Consider alternative containment methods (firewall rules, etc.)
   - Balance security response with business continuity

## D&R Rule Issues

### Rule Not Matching Expected Events

**Symptoms:**
- Detection rule exists but no alerts generated
- Test event should match but doesn't trigger rule
- Historical events that should match didn't alert

**Troubleshooting:**

1. **Use replay service:**
   ```bash
   # Test rule against historical events
   limacharlie replay --rule-content rule.yaml --events test-event.json
   ```

2. **Enable trace mode:**
   - Add trace: true to rule for detailed logging
   - Review trace output to see where rule fails
   - Check each condition evaluation

3. **Common path syntax issues:**
   ```yaml
   # Wrong - incorrect path
   path: event/FILE_PATH/NAME

   # Correct
   path: event/FILE_PATH

   # Wrong - missing array index for network events
   path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS

   # Correct (use template variable in response)
   {{ index (index .event.NETWORK_ACTIVITY 0) "DESTINATION" "IP_ADDRESS" }}
   ```

4. **Check event type:**
   ```yaml
   # Ensure event type matches
   detect:
     event: NEW_PROCESS  # Must match actual event type
   ```

5. **Verify field existence:**
   - Not all events have all fields
   - Use `op: exists` to check for field presence first
   - Review sample events in timeline to confirm field paths

6. **Case sensitivity:**
   ```yaml
   # Case-sensitive by default
   op: contains
   path: event/FILE_PATH
   value: Malware  # Won't match "malware"

   # Case-insensitive
   op: contains
   path: event/FILE_PATH
   value: malware
   case sensitive: false  # Will match "Malware", "MALWARE", etc.
   ```

### Too Many False Positives

**Symptoms:**
- Detection rule generates excessive alerts
- Most alerts are benign activity
- Alert fatigue setting in

**Solutions:**

1. **Add more specific conditions:**
   ```yaml
   # Too broad
   detect:
     event: NEW_PROCESS
     op: contains
     path: event/FILE_PATH
     value: powershell

   # More specific
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: contains
         path: event/FILE_PATH
         value: powershell
       - op: contains
         path: event/COMMAND_LINE
         value: -encodedcommand
       - op: is not tagged
         tag: dev-workstation  # Exclude dev systems
   ```

2. **Create false positive rules:**
   ```yaml
   # FP rule (processes before detection rules)
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: contains
         path: event/FILE_PATH
         value: powershell
       - op: contains
         path: event/COMMAND_LINE
         value: legitimate-script.ps1
   respond:
     - action: false positive
   ```

3. **Use stateful detection:**
   ```yaml
   # Require threshold before alerting
   detect:
     event: WEL
     op: is
     path: event/EVENT/System/EventID
     value: '4625'
     with events:
       event: WEL
       op: is
       path: event/EVENT/System/EventID
       value: '4625'
       count: 5  # Only alert after 5 occurrences
       within: 300  # Within 5 minutes
   ```

4. **Use suppression:**
   ```yaml
   respond:
     - action: report
       name: detection
     - action: task
       command: history_dump
       suppression:
         is_global: false
         keys:
           - '{{ .routing.hostname }}'
         max_count: 1
         period: 1h  # Only once per host per hour
   ```

5. **Tune over time:**
   - Start with low priority (1-2)
   - Monitor FP rate
   - Add FP rules for known-good patterns
   - Increase priority once tuned

### Response Actions Not Executing

**Symptoms:**
- Detection generates alert but response actions don't execute
- Some actions execute but not others
- Actions appear to succeed but have no effect

**Troubleshooting:**

1. **Check action syntax:**
   ```yaml
   # Wrong - typo in action name
   - action: isolate-network

   # Correct
   - action: isolate network

   # Wrong - invalid parameter
   - action: task
     command: history_dump
     timeout: 60s  # timeout not a valid parameter

   # Correct
   - action: task
     command: history_dump
   ```

2. **Verify template variables:**
   ```yaml
   # Wrong - incorrect template syntax
   - action: task
     command: file_del { .event.FILE_PATH }

   # Correct
   - action: task
     command: file_del {{ .event.FILE_PATH }}

   # Wrong - field doesn't exist in this event type
   - action: task
     command: file_del {{ .event.FILE_PATH }}
     # But event type is DNS_REQUEST which has no FILE_PATH
   ```

3. **Check suppression:**
   - Action may be suppressed due to previous execution
   - Review suppression config
   - Check detection timeline for suppressed actions

4. **Verify sensor online:**
   - Task actions require sensor connectivity
   - Check sensor status when action was attempted

5. **Check action order:**
   ```yaml
   # Wrong - wait happens before task completes
   - action: task
     command: deny_tree <<routing/this>>
   - action: wait
     duration: 5s
   - action: task
     command: file_del {{ .event.FILE_PATH }}
   # If process is child of event process, file_del might fail

   # Correct - ensure process dead before file operations
   - action: task
     command: deny_tree <<routing/this>>
   - action: wait
     duration: 5s  # Give time for termination
   - action: task
     command: file_del {{ .event.FILE_PATH }}
   ```

### Rule Performance Issues

**Symptoms:**
- High CPU or memory usage
- Detection lag or delays
- System responsiveness issues

**Causes:**
- Too many complex rules
- Inefficient rule logic
- Excessive stateful detection
- Runaway response actions

**Solutions:**

1. **Optimize rule conditions:**
   ```yaml
   # Inefficient - checks all events
   detect:
     event: *
     op: contains
     path: event/*
     value: malware

   # Efficient - specific event type and path
   detect:
     event: NEW_PROCESS
     op: contains
     path: event/FILE_PATH
     value: malware
   ```

2. **Use platform filters:**
   ```yaml
   # Add platform filter early
   detect:
     event: NEW_PROCESS
     op: is windows  # Filter by platform first
     rules:
       - op: contains
         path: event/COMMAND_LINE
         value: powershell
   ```

3. **Limit stateful detection:**
   ```yaml
   # Avoid very long time windows
   with events:
     event: NEW_PROCESS
     count: 100
     within: 86400  # 24 hours - may be expensive

   # Better - shorter window
   with events:
     event: NEW_PROCESS
     count: 10
     within: 300  # 5 minutes
   ```

4. **Use suppression to prevent runaway:**
   ```yaml
   respond:
     - action: task
       command: history_dump
       suppression:
         is_global: false
         max_count: 1
         period: 5m  # Prevent repeated execution
   ```

## Artifact Collection Issues

### Artifact Collection Failing

**Symptoms:**
- artifact_get command fails
- No file appears in artifact storage
- Timeout or error message

**Troubleshooting:**

1. **Verify Artifact extension enabled:**
   - Check Extensions page in web console
   - Ensure Artifact Collection extension is active
   - Verify extension configuration

2. **Check file path:**
   ```bash
   # Verify file exists first
   file_info C:\path\to\file.exe

   # If file_info succeeds, artifact_get should work
   artifact_get C:\path\to\file.exe
   ```

3. **Check file size:**
   - Default limit is 100MB per file
   - Larger files may fail or timeout
   - Check artifact size limits in extension config
   - Consider alternative collection methods for very large files

4. **Verify file accessibility:**
   - File may be locked by another process
   - File may be in use by system
   - Try `file_hash` first (succeeds even if file locked)

5. **Check permissions:**
   - Sensor must have read access to file
   - Protected system files may fail

6. **Check network connectivity:**
   - Artifact upload requires internet connectivity
   - If sensor isolated, artifact upload may fail
   - Rejoin network, collect artifacts, then re-isolate if needed

7. **Check storage quota:**
   - Organization may have artifact storage limits
   - Check current usage vs. quota
   - Clean up old artifacts if needed

### Artifact Collection Slow

**Symptoms:**
- Artifact collection takes very long
- Multiple collections slow down sensor
- Bandwidth saturation

**Causes:**
- Large files
- Many simultaneous collections
- Limited bandwidth
- Network congestion

**Solutions:**

1. **Prioritize critical artifacts:**
   - Collect most critical files first
   - Defer less critical collections

2. **Schedule large collections:**
   - During off-hours
   - When bandwidth available
   - Stagger collections across systems

3. **Use selective collection:**
   ```bash
   # Instead of collecting entire log directory
   # Wrong
   artifact_get /var/log/*.log

   # Better - target specific logs
   artifact_get /var/log/auth.log
   artifact_get /var/log/syslog
   ```

4. **Compress before collection:**
   ```bash
   # Create archive on endpoint
   run tar czf /tmp/logs.tar.gz /var/log/

   # Collect compressed archive
   artifact_get /tmp/logs.tar.gz

   # Clean up
   file_del /tmp/logs.tar.gz
   ```

## LCQL Query Issues

### Query Returns No Results

**Symptoms:**
- LCQL query executes but returns empty result set
- Expected events not found

**Troubleshooting:**

1. **Check time range:**
   ```
   # Too narrow
   -1h | NEW_PROCESS | ...

   # Broaden time range
   -24h | NEW_PROCESS | ...
   ```

2. **Verify event type:**
   ```
   # Wrong event type
   -24h | PROCESS_CREATED | ...

   # Correct
   -24h | NEW_PROCESS | ...
   ```

3. **Check platform filter:**
   ```
   # May be filtering out relevant systems
   -24h | plat == linux | NEW_PROCESS | ...

   # Try without platform filter
   -24h | NEW_PROCESS | ...
   ```

4. **Verify field paths:**
   ```
   # Wrong path
   -24h | NEW_PROCESS | event/FILENAME == 'malware.exe'

   # Correct
   -24h | NEW_PROCESS | event/FILE_PATH contains 'malware.exe'
   ```

5. **Test with broader query:**
   ```
   # Start very broad
   -24h | NEW_PROCESS

   # Add filters incrementally
   -24h | NEW_PROCESS | event/FILE_PATH contains 'powershell'
   ```

### Query Too Slow

**Symptoms:**
- Query takes long time to execute
- Query times out
- High resource usage

**Causes:**
- Very broad time range
- Inefficient filters
- Large result set
- Using `*` for event type

**Solutions:**

1. **Limit time range:**
   ```
   # Avoid very long ranges
   -30d | * | ...

   # Use shorter range
   -24h | NEW_PROCESS | ...
   ```

2. **Use specific event types:**
   ```
   # Avoid wildcard
   -24h | * | event/* contains 'malware'

   # Use specific type
   -24h | NEW_PROCESS | event/FILE_PATH contains 'malware'
   ```

3. **Add platform filter early:**
   ```
   # Filter platform first
   -24h | plat == windows | NEW_PROCESS | ...
   ```

4. **Use projections to limit data:**
   ```
   # Return only needed fields
   -24h | NEW_PROCESS | event/FILE_PATH as path routing/hostname as host
   ```

5. **Use aggregations:**
   ```
   # Instead of all events, count unique
   -24h | NEW_PROCESS | event/FILE_PATH as path COUNT_UNIQUE(event) as count GROUP BY(path)
   ```

### Query Syntax Errors

**Symptoms:**
- Query fails to execute
- Syntax error message
- Unexpected results

**Common Mistakes:**

```
# Wrong - missing pipe
-24h plat == windows | NEW_PROCESS

# Correct
-24h | plat == windows | NEW_PROCESS

# Wrong - incorrect comparison operator
-24h | NEW_PROCESS | event/FILE_PATH = 'malware.exe'

# Correct
-24h | NEW_PROCESS | event/FILE_PATH == 'malware.exe'

# Wrong - incorrect AND syntax
-24h | NEW_PROCESS | event/FILE_PATH contains 'malware' and event/FILE_PATH contains '.exe'

# Correct
-24h | NEW_PROCESS | event/FILE_PATH contains 'malware' AND event/FILE_PATH contains '.exe'

# Wrong - incorrect field separator
-24h | NEW_PROCESS | event.FILE_PATH

# Correct
-24h | NEW_PROCESS | event/FILE_PATH
```

## Investigation Challenges

### Cannot Determine Initial Infection Vector

**Symptoms:**
- Malware found but origin unclear
- No obvious entry point
- Timeline doesn't show initial compromise

**Investigation Strategies:**

1. **Expand time range:**
   - Initial compromise may be days/weeks before detection
   - Search back to last known-good state
   - Review timeline for first malware execution

2. **Check common entry points:**
   ```
   # Email attachments
   -7d | NEW_DOCUMENT | event/FILE_PATH contains '\Downloads\' | event/FILE_PATH as path routing/hostname as host routing/event_time as time

   # Web downloads
   -7d | NEW_PROCESS | event/PARENT/FILE_PATH contains 'chrome.exe' OR event/PARENT/FILE_PATH contains 'firefox.exe' | event/FILE_PATH as process routing/event_time as time

   # Removable media
   -7d | VOLUME_MOUNT | event/MOUNT_POINT as mount routing/event_time as time

   # Remote access
   -7d | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/IpAddress as source routing/event_time as time
   ```

3. **Analyze process ancestry:**
   ```bash
   # Get full process tree
   history_dump

   # Trace malware back to parent processes
   # Look for unusual parent-child relationships
   ```

4. **Check browser history:**
   ```bash
   # Collect browser history
   artifact_get C:\Users\username\AppData\Local\Google\Chrome\User Data\Default\History

   # Analyze for malicious URLs, downloads
   ```

5. **Review email logs:**
   - Check email server logs for malicious attachments
   - Search for phishing emails
   - Correlate email receipt with file creation times

### Attacker Cleanup / Anti-Forensics

**Symptoms:**
- Expected evidence missing
- Log files deleted
- Timeline gaps
- Event log clearing

**Detection:**

```
# Detect log clearing
-24h | WEL | event/EVENT/System/EventID == "1102" | routing/hostname as host routing/event_time as time

# Detect file deletion
-24h | NEW_DOCUMENT | event/FILE_PATH contains '\EventLog\' | routing/hostname as host event/FILE_PATH as path

# Look for timestamp manipulation
# Manual timeline review for anomalies
```

**Recovery Strategies:**

1. **Use external logging:**
   - Check SIEM/log aggregation system
   - Logs forwarded before deletion may still exist
   - Network traffic logs may show activity

2. **Check LimaCharlie timeline:**
   - LC timeline not affected by local log deletion
   - May have captured events before cleanup
   - Review timeline for all event types

3. **Analyze remaining artifacts:**
   - Prefetch files (Windows) survive log cleanup
   - Registry keys may remain
   - Network forensics from firewall logs

4. **Recover deleted files:**
   - File carving on disk (requires external tools)
   - Shadow copies (Windows)
   - Backups

### Encrypted/Obfuscated Malware

**Symptoms:**
- Encoded PowerShell commands
- Packed executables
- Obfuscated scripts
- Encrypted payloads

**Investigation Techniques:**

1. **Memory analysis:**
   ```bash
   # Malware may decrypt in memory
   mem_strings --pid <pid>
   mem_map --pid <pid>

   # Look for decoded strings
   mem_find_string --pid <pid> --string 'http'
   ```

2. **Behavioral analysis:**
   - Focus on actions, not content
   - Process creation, network connections, file operations
   - Chain of events more important than individual artifacts

3. **Collect for offline analysis:**
   ```bash
   # Collect suspicious files
   artifact_get C:\path\to\packed.exe

   # Analyze with external tools
   # VirusTotal, sandbox, static analysis
   ```

4. **Decode PowerShell:**
   - Extract base64 encoded commands from timeline
   - Decode using external tools
   - Search decoded content for IOCs

5. **Network analysis:**
   - Even if malware encrypted, network IOCs visible
   - DNS requests, IP addresses, ports
   - C2 traffic patterns

### Persistent Threat Detection

**Symptoms:**
- Malware returns after removal
- Reinfection shortly after remediation
- Recurring detections

**Investigation:**

1. **Comprehensive persistence check:**
   ```bash
   # Windows autoruns
   os_autoruns

   # Services
   os_services

   # Scheduled tasks
   run schtasks /query /fo LIST /v

   # WMI persistence
   run wmic /namespace:\\root\subscription path __EventFilter get /format:list
   run wmic /namespace:\\root\subscription path __EventConsumer get /format:list

   # Registry Run keys (multiple locations)
   # Check HKLM and HKCU Run keys
   ```

2. **Search for secondary payloads:**
   ```bash
   # Look for dropped files
   dir_list C:\ProgramData
   dir_list C:\Windows\Temp
   dir_list C:\Users\*\AppData\Local\Temp

   # Hash known-good files to detect replacements
   ```

3. **Check for backdoors:**
   ```bash
   # Review listening ports
   netstat

   # Check for web shells (web servers)
   dir_list /var/www/html --recurse

   # Look for remote access tools
   os_packages
   ```

4. **Network-based reinfection:**
   ```
   # Check for network shares with malware
   -24h | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/PORT == 445 | routing/hostname as host event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst
   ```

## Response Planning Challenges

### Balancing Speed vs. Thoroughness

**Challenge:** Need fast response but also comprehensive investigation.

**Best Practices:**

1. **Parallel containment and investigation:**
   - Contain immediately (network isolation)
   - Investigate while contained
   - Don't wait for full investigation to contain

2. **Automate containment, manual remediation:**
   ```yaml
   # Automate immediate containment
   respond:
     - action: isolate network
     - action: task
       command: history_dump

   # Manual remediation after investigation
   # Ensures thoroughness
   ```

3. **Staged response:**
   - Phase 1: Immediate containment (automated)
   - Phase 2: Investigation (manual)
   - Phase 3: Remediation (manual)
   - Phase 4: Recovery (manual)

4. **Use investigation IDs:**
   - Group all related forensic collections
   - Maintain evidence chain
   - Don't sacrifice evidence for speed

### Determining Automation Scope

**Challenge:** Which response actions to automate vs. require human approval?

**Decision Framework:**

**Automate:**
- Network isolation (reversible, low risk)
- Process termination for known malware (high confidence)
- Forensic collection (non-destructive)
- Tagging and alerting

**Require approval:**
- File deletion (destructive)
- Account lockouts (business impact)
- Remediation on production systems
- Novel/unknown threats

**Progressive approach:**
```yaml
# Phase 1: Alert only
respond:
  - action: report

# Phase 2: Alert + collect (after validation)
respond:
  - action: report
  - action: task
    command: history_dump

# Phase 3: Alert + collect + contain (after validation)
respond:
  - action: report
  - action: task
    command: history_dump
  - action: isolate network

# Phase 4: Full automation (after extensive validation)
respond:
  - action: report
  - action: isolate network
  - action: task
    command: deny_tree <<routing/this>>
```

### Handling False Positives in Production

**Challenge:** Detection firing on legitimate activity, causing business disruption.

**Immediate Response:**

1. **Create FP rule quickly:**
   ```yaml
   # Temporary FP rule
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: contains
         path: event/FILE_PATH
         value: legitimate-app.exe
       - op: is
         path: routing/hostname
         value: affected-server
   respond:
     - action: false positive
   ```

2. **Disable aggressive response:**
   - Remove destructive actions temporarily
   - Keep detection but disable containment
   - Investigate FP root cause

3. **Rejoin affected systems:**
   ```yaml
   # If systems were isolated
   - action: rejoin network
   ```

**Long-term Fix:**

1. **Tune detection rule:**
   - Add more specific conditions
   - Exclude known-good patterns
   - Increase threshold for stateful detection

2. **Create whitelist:**
   - Tag known-good systems
   - Exclude from detection
   ```yaml
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: contains
         path: event/FILE_PATH
         value: suspicious-pattern
       - op: is not tagged
         tag: approved-dev-system
   ```

3. **Test before production:**
   - Use replay service
   - Start with low priority
   - Monitor FP rate in dev environment first

## Escalation Guidance

### When to Escalate

**Escalate to senior IR team when:**
- Scope exceeds single system (enterprise-wide compromise)
- Advanced persistent threat (APT) indicators
- Data exfiltration confirmed
- Ransom demand received
- Unable to contain threat
- Critical infrastructure impacted
- Public disclosure risk
- Legal/regulatory implications

### When to Engage External Help

**Engage external IR firm when:**
- Internal team overwhelmed
- Specialized expertise needed (APT, nation-state)
- Legal requirement (breach notification, forensics)
- Need independent validation
- Reputation management required
- Insurance claim support needed

### When to Involve Law Enforcement

**Contact law enforcement when:**
- Ransom demand (FBI recommends reporting)
- Nation-state actor suspected
- Critical infrastructure attack
- Child exploitation material
- Financial fraud
- Required by regulation
- Criminal prosecution desired

**Caution:**
- Preserve evidence with law enforcement involvement in mind
- Chain of custody critical
- May slow response/recovery
- Legal counsel advisable

## Documentation Best Practices

### What to Document

**During incident:**
1. Timeline of events (automated via LC)
2. Actions taken by responders
3. Decisions made and rationale
4. Systems affected
5. Data accessed/exfiltrated
6. Indicators of compromise
7. Lessons learned

**Tools:**
- Investigation IDs for grouping related actions
- Timeline export from LC
- Detection reports
- Artifact collection inventory
- Responder notes

### Documentation Template

```
Incident ID: [unique-id]
Date/Time Detected: [timestamp]
Incident Type: [malware/breach/exfiltration/etc]
Severity: [Critical/High/Medium/Low]
Systems Affected: [hostnames]
Detection Method: [D&R rule/alert/user report]

Timeline:
- [timestamp]: Initial detection
- [timestamp]: Containment action taken
- [timestamp]: Investigation findings
- [timestamp]: Remediation completed
- [timestamp]: Systems restored

Actions Taken:
1. Network isolation applied to [systems]
2. Process [pid] terminated on [system]
3. Artifacts collected: [list]
4. Malware removed from [locations]

Indicators of Compromise:
- File hashes: [list]
- IPs: [list]
- Domains: [list]
- File paths: [list]

Root Cause:
[Description of how compromise occurred]

Remediation:
[Steps taken to eradicate threat]

Lessons Learned:
[What went well, what needs improvement]

Follow-up Actions:
- [ ] Create detection rules
- [ ] Update threat intelligence
- [ ] Apply patches
- [ ] Update documentation
- [ ] Train team on new TTPs
```

## Performance Optimization

### Reducing Alert Fatigue

**Problem:** Too many low-value alerts overwhelming team.

**Solutions:**

1. **Tune detection priority:**
   - Reserve priority 5 for critical, actionable alerts
   - Use priority 1-2 for informational detections
   - Focus attention on priority 4-5

2. **Aggregate similar alerts:**
   - Use stateful detection to batch similar events
   - Create summary alerts instead of per-event

3. **Filter noise:**
   - Create FP rules for known-benign patterns
   - Use tagging to exclude dev/test systems
   - Implement whitelist for approved tools

4. **Automate low-level response:**
   - Automate collection and initial triage
   - Reserve human review for high-priority alerts

### Optimizing Response Workflow

**Problem:** Response process slow or inefficient.

**Solutions:**

1. **Create playbooks:**
   - Document common scenarios
   - Define response procedures
   - Train team on playbooks

2. **Automate repetitive tasks:**
   - Forensic collection
   - Evidence gathering
   - Reporting

3. **Use investigation IDs:**
   - Group related actions
   - Streamline evidence review

4. **Prepare response tools:**
   - Pre-create D&R response rules
   - Have rejoin/unseal procedures ready
   - Document containment rollback process

## Additional Resources

### Training and Skill Development

**Recommended skills for IR team:**
- LCQL query language
- D&R rule creation
- Windows event log analysis
- Linux system administration
- Network traffic analysis
- Malware analysis basics
- MITRE ATT&CK framework

**Practice scenarios:**
- Use EXAMPLES.md scenarios for training
- Conduct tabletop exercises
- Test detection rules with replay service
- Simulate incidents in lab environment

### External Resources

**Reference documentation:**
- LimaCharlie documentation site
- MITRE ATT&CK knowledge base
- SANS Digital Forensics resources
- NIST Cybersecurity Framework

**Communities:**
- LimaCharlie community forums
- Security researcher communities
- DFIR mailing lists
- Industry ISACs

### Regular Review and Improvement

**Periodic activities:**

1. **Monthly:**
   - Review detection rule performance
   - Update threat intelligence
   - Tune false positive rules
   - Check automation effectiveness

2. **Quarterly:**
   - Conduct IR tabletop exercise
   - Update response playbooks
   - Review and improve D&R rules
   - Train team on new techniques

3. **Annually:**
   - Full IR plan review
   - Gap analysis
   - Tool evaluation
   - Team training and certification

4. **Post-incident:**
   - Lessons learned session
   - Update playbooks
   - Create new detection rules
   - Share intelligence with community

## Summary

This troubleshooting guide covers:

- **Technical issues**: Command execution, network isolation, D&R rules, queries, artifacts
- **Investigation challenges**: Finding IOC, dealing with anti-forensics, encrypted malware
- **Operational challenges**: Automation decisions, FP handling, escalation guidance
- **Best practices**: Documentation, performance optimization, continuous improvement

When troubleshooting:
1. Start with basics (connectivity, syntax, permissions)
2. Use LC tools (replay, trace, timeline review)
3. Check documentation (REFERENCE.md for syntax)
4. Test incrementally (simplify query/rule to isolate issue)
5. Document findings (help future troubleshooting)

For additional help:
- LimaCharlie support
- Community forums
- Documentation site
- This troubleshooting guide
