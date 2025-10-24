# Artifact Collection Troubleshooting

Common issues, solutions, and optimization strategies for artifact collection.

## Table of Contents

1. [Collection Failures](#collection-failures)
2. [Storage Issues](#storage-issues)
3. [Performance Problems](#performance-problems)
4. [Cost Management](#cost-management)
5. [Permission Issues](#permission-issues)
6. [Network Problems](#network-problems)
7. [Platform-Specific Issues](#platform-specific-issues)
8. [Best Practices Review](#best-practices-review)

---

## Collection Failures

### Artifact Collection Fails

**Symptoms**: Commands execute but artifacts don't appear in storage.

**Common Causes**:

1. **Extension Not Enabled**
   - Check: Navigate to **Extensions** and verify Artifact extension is subscribed
   - Solution: Subscribe to the Artifact extension

2. **Reliable Tasking Not Enabled**
   - Check: Artifact extension requires Reliable Tasking as a dependency
   - Solution: Subscribe to the Reliable Tasking extension

3. **Sensor Offline**
   - Check: Sensor status in web UI
   - Solution: Use Reliable Tasking to queue the command for when sensor comes online

4. **File/Path Doesn't Exist**
   - Check: Use `dir_list` or `file_info` to verify path exists
   - Solution: Correct the file path

5. **Insufficient Sensor Permissions**
   - Check: Error events in sensor timeline
   - Solution: Run sensor with appropriate privileges, or adjust file permissions

6. **Disk Space Issues**
   - Check: Sensor disk space
   - Solution: Free up disk space on endpoint

**Diagnostic Steps**:

```bash
# 1. Verify file exists
file_info --path C:\path\to\file.exe

# 2. Check if you can hash it
file_hash --path C:\path\to\file.exe

# 3. Try collecting a known good file
artifact_get C:\Windows\System32\notepad.exe

# 4. Check sensor timeline for error events
# Look for ARTIFACT_GET_REP with error field
```

---

### File Collection Returns Empty

**Symptoms**: Collection succeeds but file is 0 bytes.

**Common Causes**:

1. **File is Locked**
   - File is in use by another process
   - Solution: Use shadow copy or try again later

2. **File is Actually Empty**
   - Verify with `file_info` command
   - Check file size before collecting

3. **Permission Denied**
   - Sensor doesn't have permission to read file
   - Solution: Elevate sensor privileges or adjust file permissions

**Diagnostic Steps**:

```bash
# Check file size
file_info --path C:\path\to\file.exe

# Try file_get instead (for smaller files)
file_get --path C:\path\to\file.exe
```

---

### Commands Don't Execute

**Symptoms**: Commands sent but no response received.

**Common Causes**:

1. **Sensor Offline**
   - Check sensor status
   - Solution: Use Reliable Tasking

2. **Syntax Error**
   - Incorrect command syntax
   - Solution: Verify command syntax in REFERENCE.md

3. **Unsupported Platform**
   - Command not supported on sensor's platform
   - Solution: Check platform compatibility

4. **Sensor Version Too Old**
   - Old sensor version may not support command
   - Solution: Update sensor

**Diagnostic Steps**:

```bash
# Test with simple command
os_processes

# Check sensor version in web UI
# Update if necessary
```

---

## Storage Issues

### Artifacts Not Appearing in UI

**Symptoms**: Collection succeeds but artifacts don't show in Artifact Collection UI.

**Common Causes**:

1. **Wrong Organization Selected**
   - Check you're viewing the correct organization
   - Solution: Switch to correct organization

2. **Retention Period Expired**
   - Artifacts deleted after retention period
   - Check: Default is 30 days
   - Solution: Increase retention for critical artifacts

3. **Artifacts Still Uploading**
   - Large artifacts take time to upload
   - Solution: Wait and refresh

4. **Filter Settings in UI**
   - UI filters may be hiding artifacts
   - Solution: Clear all filters

**Diagnostic Steps**:

1. Check sensor timeline for `ARTIFACT_GET_REP` event
2. Verify event shows success
3. Note artifact ID from event
4. Use REST API to check if artifact exists:

```bash
GET https://api.limacharlie.io/v1/orgs/{oid}/artifacts
```

---

### Unable to Download Artifacts

**Symptoms**: Artifact exists but download fails.

**Common Causes**:

1. **Network Issues**
   - Connection problems
   - Solution: Retry download, check network

2. **Permission Issues**
   - User doesn't have permission
   - Solution: Verify user has artifact download permissions

3. **Artifact Corrupted**
   - Rare, but possible
   - Solution: Re-collect if possible

4. **Browser Issues**
   - Browser blocking download
   - Solution: Try different browser or use REST API

**Diagnostic Steps**:

```bash
# Try downloading via REST API
curl -H "Authorization: Bearer $JWT" \
https://api.limacharlie.io/v1/orgs/{oid}/artifacts/{artifact_id} \
--output artifact.bin
```

---

### Storage Quota Exceeded

**Symptoms**: Collection fails with quota exceeded error.

**Common Causes**:

1. **Too Many Artifacts Collected**
   - Exceeded organization storage limits
   - Solution: Delete old artifacts, increase quota

2. **Large Artifacts**
   - Memory dumps filling storage
   - Solution: Use shorter retention, be selective

**Solutions**:

1. **Delete Old Artifacts**:
   - Navigate to Artifact Collection UI
   - Filter by old dates
   - Delete unnecessary artifacts

2. **Reduce Retention**:
   ```yaml
   extension request:
     target: memory
     retention: 7  # Reduce from 30 to 7 days
   ```

3. **Add Suppression to Rules**:
   ```yaml
   suppression:
     max_count: 1
     period: 24h
   ```

4. **Contact Support** to increase quota if needed

---

## Performance Problems

### Memory Dumps Not Completing

**Symptoms**: Memory dump command sent but never completes.

**Common Causes**:

1. **Large Memory Size**
   - Systems with 32GB+ RAM take significant time
   - Solution: Be patient, dumps can take 30+ minutes

2. **Insufficient Disk Space**
   - Endpoint doesn't have enough free disk space
   - Solution: Free up disk space equal to RAM size + 20%

3. **Network Bandwidth**
   - Upload is slow on limited bandwidth
   - Solution: Schedule during off-hours, use faster connection

4. **Sensor Resource Constraints**
   - Sensor overloaded
   - Solution: Reduce other activity, try during low-load period

**Best Practices**:

- Don't collect memory dumps unnecessarily
- Use process memory (`mem_map`, `mem_strings`) instead when possible
- Schedule large dumps during maintenance windows
- Use shorter retention periods (7 days instead of 30)

**Diagnostic Steps**:

```bash
# Check available disk space first
# Then request dump with shorter retention
extension request: {target: "memory", sid: "sensor-id", retention: 7}
```

---

### Collection Commands Slow

**Symptoms**: Commands take long time to complete.

**Common Causes**:

1. **Large Files**
   - Collecting large files takes time
   - Solution: Expected behavior, be patient

2. **Wildcard Collections**
   - `artifact_get C:\Users\*\Downloads\*` collecting many files
   - Solution: Be more specific with paths

3. **Network Latency**
   - Slow connection to sensor
   - Solution: Expected for remote sensors

4. **Sensor Under Load**
   - Endpoint CPU/disk heavily utilized
   - Solution: Retry during lower load

**Optimization**:

```bash
# Instead of wildcard collection:
artifact_get C:\Users\*\Downloads\*

# Be specific:
artifact_get C:\Users\alice\Downloads\suspicious.exe
```

---

### Sensor Becomes Unresponsive

**Symptoms**: Sensor stops responding after collection command.

**Common Causes**:

1. **Memory Dump on Low Resource System**
   - Memory dump exhausting resources
   - Solution: Don't dump on low-spec systems

2. **Too Many Simultaneous Collections**
   - Multiple heavy commands at once
   - Solution: Stagger commands, use `wait` action

3. **Disk Full**
   - Endpoint disk filled during collection
   - Solution: Free disk space before collecting

**Prevention**:

```yaml
# Space out commands in D&R rules
respond:
  - action: task
    command: mem_map --pid {{ .event.PROCESS_ID }}
  - action: wait
    duration: 5s
  - action: task
    command: mem_strings --pid {{ .event.PROCESS_ID }}
  - action: wait
    duration: 10s
  - action: extension request
    extension name: ext-dumper
    extension action: request_dump
    extension request:
      target: memory
      sid: <<routing.sid>>
      retention: 7
```

---

## Cost Management

### Unexpected High Costs

**Symptoms**: Artifact ingestion costs higher than expected.

**Common Causes**:

1. **Event Log Files Instead of Streaming**
   - Collecting `.evtx` files instead of using `wel://`
   - Solution: Use `wel://` for real-time streaming (free)

2. **No Suppression on Rules**
   - Same file collected repeatedly
   - Solution: Add suppression to D&R rules

3. **Wildcard Collections**
   - Unintentionally collecting many files
   - Solution: Be more specific with paths

4. **Long Retention Periods**
   - 30-90 day retention increasing storage costs
   - Solution: Reduce retention to minimum needed

5. **Automated Collection Too Aggressive**
   - D&R rules collecting too frequently
   - Solution: Add filters and suppression

**Cost Reduction Strategies**:

1. **Use Streaming for Logs**:
   ```yaml
   # DON'T DO THIS (costs money):
   - action: task
     command: artifact_get C:\Windows\System32\winevt\Logs\Security.evtx

   # DO THIS INSTEAD (free):
   # Configure in Artifact Collection UI
   Pattern: wel://Security:*
   ```

2. **Add Suppression**:
   ```yaml
   - action: task
     command: artifact_get {{ .event.FILE_PATH }}
     suppression:
       max_count: 1
       period: 24h
       is_global: false
       keys:
         - '{{ .event.FILE_PATH }}'
   ```

3. **Filter Before Collecting**:
   ```yaml
   # Add more specific detection criteria
   detect:
     op: and
     rules:
       - op: matches
         path: event/FILE_PATH
         re: .*\\malware\.exe$  # Specific file, not wildcard
   ```

4. **Hash Before Collecting**:
   ```yaml
   # Check hash first, don't collect known-good files
   - action: task
     command: file_hash --path {{ .event.FILE_PATH }}
   # Then decide whether to collect
   ```

5. **Reduce Retention**:
   ```yaml
   extension request:
     target: memory
     retention: 7  # Instead of 30
   ```

6. **Use file_get for Small Files**:
   ```bash
   # For files < 1MB, use file_get (no storage cost)
   file_get --path /etc/passwd

   # Instead of artifact_get
   artifact_get /etc/passwd  # Incurs cost
   ```

---

### Monitoring Costs

**Set Up Usage Alerts**:

1. Navigate to Usage Alerts extension
2. Configure alerts for artifact ingestion
3. Set thresholds for daily/monthly usage
4. Receive notifications when approaching limits

**Review Regularly**:

- Check billing dashboard weekly
- Review top artifact producers
- Identify and optimize expensive rules
- Archive old artifacts

---

## Permission Issues

### Access Denied Errors

**Symptoms**: Collection fails with access denied or permission error.

**Common Causes**:

1. **Sensor Not Elevated**
   - Windows: Sensor running without admin rights
   - Linux: Sensor not running as root
   - Solution: Run sensor with appropriate privileges

2. **File Permissions**
   - File has restrictive permissions
   - Solution: Adjust file permissions or elevate sensor

3. **System Protected Files**
   - Windows protected system files
   - Solution: Use shadow copy or boot-time collection

**Platform-Specific Solutions**:

**Windows**:
```bash
# For locked system files, try Volume Shadow Copy
# This requires manual intervention or scheduled task
```

**Linux**:
```bash
# Ensure sensor running as root for system files
# Or adjust file permissions:
chmod +r /path/to/file
```

---

### Unable to Collect Registry

**Symptoms**: Windows registry hive collection fails.

**Common Causes**:

1. **Hives Are Locked**
   - Registry hives in use by system
   - Solution: Use registry export or shadow copy

2. **Insufficient Privileges**
   - Sensor not running as SYSTEM or Administrator
   - Solution: Elevate sensor privileges

**Alternative Approach**:

Instead of collecting registry hives directly, use registry export:

```bash
# This may require a custom task or script
# Registry access is better done through sensor commands
```

---

## Network Problems

### Artifacts Upload Slowly

**Symptoms**: Artifacts take very long to appear in storage.

**Common Causes**:

1. **Limited Bandwidth**
   - Slow internet connection on endpoint
   - Solution: Schedule large collections during off-hours

2. **Large Files**
   - Memory dumps, large logs
   - Solution: Expected behavior, be patient

3. **Network Congestion**
   - Corporate network congestion
   - Solution: Schedule during low-traffic periods

**Optimization**:

- Compress before collecting (if tool supports)
- Use Reliable Tasking to queue for off-hours
- Avoid collecting during business hours
- Consider on-premises Forwarder for air-gapped networks

---

### PCAP Not Capturing

**Symptoms**: PCAP collection configured but no captures appear.

**Common Causes**:

1. **Platform Not Supported**
   - PCAP only works on Linux
   - Solution: Only configure for Linux sensors

2. **Interface Not Accessible**
   - Specified network interface doesn't exist
   - Solution: Verify interface name

3. **Tag Not Applied**
   - Tag-based trigger but tag not on sensor
   - Solution: Verify sensor has correct tag

4. **Artifact Collection Rules Not Configured**
   - Rules not properly set up
   - Solution: Double-check configuration in UI

**Diagnostic Steps**:

1. Verify platform is Linux
2. Check sensor has required tag
3. Verify Artifact Collection rule is enabled
4. Check sensor timeline for PCAP-related events

**Example Configuration**:

```yaml
# In Artifact Collection UI:
Interface: eth0
Filter: ""  # or specific filter like "port 443"
Trigger: tag==pcap-capture
Duration: 300
```

**Triggering**:

```yaml
# In D&R rule:
- action: add tag
  tag: pcap-capture
  ttl: 300
```

---

## Platform-Specific Issues

### Windows Event Log Collection Issues

**Symptoms**: Unable to collect Windows Event Logs.

**Common Causes**:

1. **Log Doesn't Exist**
   - Specified log not present on system
   - Solution: Verify log name with `wevtutil el` or check Event Viewer

2. **Log Name Incorrect**
   - Case-sensitive or path issues
   - Solution: Use exact name from Event Viewer

3. **Insufficient Permissions**
   - Sensor can't access Security log
   - Solution: Ensure sensor runs with admin privileges

**Common Log Names**:

```bash
# Correct:
log_get Security
log_get System
log_get Application
log_get Microsoft-Windows-Sysmon/Operational

# Incorrect:
log_get security  # Wrong case
log_get Sec  # Incomplete
```

---

### macOS Unified Log Issues

**Symptoms**: MUL collection not working on macOS.

**Common Causes**:

1. **Incorrect Pattern**
   - MUL pattern syntax wrong
   - Solution: Use `mul://` prefix correctly

2. **Permissions**
   - macOS restricting log access
   - Solution: Ensure proper sensor permissions

**Example Patterns**:

```yaml
# Correct:
mul://*
mul://process=="loginwindow"

# Incorrect:
log_get unified  # Wrong command
```

---

### Linux-Specific Issues

**Symptoms**: Collections failing on Linux.

**Common Causes**:

1. **SELinux/AppArmor Restrictions**
   - Security modules blocking access
   - Solution: Adjust policies or disable temporarily

2. **File Paths**
   - Case-sensitive file paths
   - Solution: Verify exact path with `ls`

3. **Permissions**
   - Sensor not running as root
   - Solution: Run sensor with sudo or as root

**Common Linux Collections**:

```bash
# Logs
artifact_get /var/log/auth.log
artifact_get /var/log/syslog
artifact_get /var/log/secure

# Configs
artifact_get /etc/ssh/sshd_config
artifact_get /etc/passwd

# User artifacts
artifact_get /home/*/.bash_history
artifact_get /root/.ssh/authorized_keys
```

---

## Best Practices Review

### Evidence Preservation

**Chain of Custody**:
- Document what was collected, when, and why
- Use investigation IDs to track related artifacts
- Preserve original timestamps and metadata
- Maintain audit logs of collection activities

**Integrity**:
```bash
# Always hash before collecting
file_hash --path C:\suspicious.exe

# Verify hash after download
# Compare with hash from file_hash command
```

---

### Efficient Collection

**Priority Order**:

1. **Volatile Data** (collect first):
   ```bash
   os_processes
   netstat
   mem_map --pid <pid>
   mem_strings --pid <pid>
   ```

2. **Critical Files**:
   ```bash
   artifact_get C:\malware.exe
   ```

3. **Logs and History**:
   ```bash
   log_get Security
   history_dump
   ```

4. **Large Dumps** (last):
   ```yaml
   extension request: {target: "memory"}
   extension request: {target: "mft"}
   ```

---

### Automation Best Practices

**Always Include Suppression**:

```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
    - artifact-collection
```

**Test Before Deploying**:

1. Test rule on single sensor
2. Verify artifacts collect correctly
3. Check costs for single collection
4. Estimate fleet-wide costs
5. Deploy to production

**Monitor After Deployment**:

- Check collection volumes daily
- Review costs weekly
- Verify artifacts are useful
- Adjust rules as needed

---

### Resource Management

**Prevent Exhaustion**:

```yaml
# Space out heavy commands
- action: task
  command: mem_strings --pid {{ .event.PROCESS_ID }}
- action: wait
  duration: 10s
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  suppression:
    max_count: 1
    period: 24h
```

**Set Reasonable Limits**:

- Max 1 memory dump per sensor per day
- Max 10 file collections per sensor per hour
- Use global suppression for fleet-wide limits

---

## Getting Help

### Diagnostic Information to Collect

When contacting support, provide:

1. **Sensor Information**:
   - Sensor ID
   - Platform and version
   - Online/offline status

2. **Command Details**:
   - Exact command sent
   - Timestamp
   - Expected vs actual result

3. **Error Messages**:
   - Error events from timeline
   - Screenshot of issue
   - Relevant logs

4. **Configuration**:
   - D&R rule YAML (if applicable)
   - Artifact Collection rules
   - Extension subscriptions

### Support Resources

- **LimaCharlie Documentation**: https://doc.limacharlie.io
- **Community Slack**: LimaCharlie Slack workspace
- **Support Email**: support@limacharlie.io
- **REST API Reference**: https://api.limacharlie.io/static/swagger/

### Self-Service Debugging

1. **Check Sensor Timeline**:
   - Look for error events
   - Verify commands were received
   - Check response events

2. **Test with Simple Commands**:
   ```bash
   # Start with simple command
   os_processes

   # Then try file operation
   file_info --path C:\Windows\System32\notepad.exe

   # Then try collection
   artifact_get C:\Windows\System32\notepad.exe
   ```

3. **Verify Prerequisites**:
   - Artifact extension enabled
   - Reliable Tasking enabled
   - Sensor online
   - Proper permissions

4. **Review Recent Changes**:
   - Did rules change recently?
   - Was sensor updated?
   - Did network configuration change?
