# Forensic Investigation Troubleshooting

Common issues, solutions, and best practices for forensic investigations with LimaCharlie.

## Table of Contents

1. [Query and LCQL Issues](#query-and-lcql-issues)
2. [Sensor Command Issues](#sensor-command-issues)
3. [Artifact Collection Issues](#artifact-collection-issues)
4. [Memory Analysis Issues](#memory-analysis-issues)
5. [Timeline Reconstruction Issues](#timeline-reconstruction-issues)
6. [Performance and Scaling](#performance-and-scaling)
7. [Data Retention and Storage](#data-retention-and-storage)

---

## Query and LCQL Issues

### No Results from LCQL Query

**Symptoms**: Query returns no events, but you expect results.

**Common causes and solutions**:

1. **Time window too narrow**:
   ```
   # Problem: -1h might be too short
   -1h | plat == windows | NEW_PROCESS

   # Solution: Expand time window
   -24h | plat == windows | NEW_PROCESS
   -7d | plat == windows | NEW_PROCESS
   ```

2. **Platform filter incorrect**:
   ```
   # Problem: Wrong platform
   plat == linux | NEW_PROCESS  # But target is Windows

   # Solution: Use correct platform
   plat == windows | NEW_PROCESS

   # Or omit platform filter if unsure
   -24h | NEW_PROCESS
   ```

3. **Event type not available on platform**:
   ```
   # Problem: REGISTRY_WRITE doesn't exist on Linux
   plat == linux | REGISTRY_WRITE

   # Solution: Use platform-appropriate event types
   plat == windows | REGISTRY_WRITE  # Windows only
   plat == linux | FILE_MODIFIED     # Cross-platform
   ```

4. **Field path incorrect**:
   ```
   # Problem: Wrong field path
   event/FILE_NAME  # This field doesn't exist

   # Solution: Use correct field path
   event/FILE_PATH
   ```

5. **Hostname filter incorrect**:
   ```
   # Problem: Hostname doesn't match exactly
   routing/hostname == "server"  # Actual: "server.domain.com"

   # Solution: Use contains or exact match
   routing/hostname contains "server"
   routing/hostname == "server.domain.com"
   ```

**Debugging approach**:
1. Start with broadest possible query: `-24h | *`
2. Add filters one at a time
3. Check each field path exists in event schema
4. Verify sensor is online and sending data
5. Check Organization retention settings

---

### Query Timeout

**Symptoms**: Query runs but times out before completion.

**Common causes and solutions**:

1. **Time window too large**:
   ```
   # Problem: Querying entire year
   -365d | plat == windows | NEW_PROCESS

   # Solution: Break into smaller chunks
   -7d | plat == windows | NEW_PROCESS
   # Run multiple queries for different time ranges
   ```

2. **Too many events without filtering**:
   ```
   # Problem: Querying all events
   -30d | *

   # Solution: Add event type filters
   -30d | NEW_PROCESS NETWORK_CONNECTIONS
   ```

3. **Complex aggregations**:
   ```
   # Problem: Heavy aggregation
   -30d | plat == windows | NEW_PROCESS | COUNT(event) as count GROUP BY(event/FILE_PATH event/COMMAND_LINE event/USER_NAME)

   # Solution: Reduce GROUP BY fields or time window
   -7d | plat == windows | NEW_PROCESS | COUNT(event) as count GROUP BY(event/FILE_PATH)
   ```

4. **Large result set**:
   ```
   # Problem: Returning millions of events
   -30d | plat == windows | NEW_PROCESS | event/TIMESTAMP as time event/FILE_PATH as process

   # Solution: Add more filters
   -30d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "suspicious" | event/TIMESTAMP as time event/FILE_PATH as process
   ```

**Best practices**:
- Start with short time windows (1-7 days)
- Filter by event type before other conditions
- Use specific hostname filters when investigating single system
- Limit field selection to only what you need
- Use aggregation to reduce result volume

---

### Incorrect Query Results

**Symptoms**: Query returns results, but they don't match expectations.

**Common issues**:

1. **AND vs OR confusion**:
   ```
   # Problem: Using OR when you need AND
   event/FILE_PATH contains "malware" or event/HASH == "abc123"
   # Returns: All files with "malware" OR files with hash abc123

   # Solution: Use AND
   event/FILE_PATH contains "malware" and event/HASH == "abc123"
   # Returns: Only files with "malware" AND hash abc123
   ```

2. **Case sensitivity**:
   ```
   # Problem: Case-sensitive match
   event/FILE_PATH == "C:\Windows\System32\cmd.exe"  # Won't match if case differs

   # Solution: Use contains (case-insensitive)
   event/FILE_PATH contains "cmd.exe"
   ```

3. **Partial path matching**:
   ```
   # Problem: Expecting exact match
   event/FILE_PATH == "cmd.exe"  # Won't match full path

   # Solution: Use ends with or contains
   event/FILE_PATH ends with "cmd.exe"
   event/FILE_PATH contains "\\cmd.exe"
   ```

4. **Timezone confusion**:
   ```
   # All timestamps in LCQL are UTC
   # If you specify absolute time, use UTC
   2024-01-15T14:00:00Z to 2024-01-15T15:00:00Z  # UTC
   ```

---

## Sensor Command Issues

### Command Not Responding

**Symptoms**: Sensor command issued but no response received.

**Common causes**:

1. **Sensor offline**:
   - Check sensor status in UI
   - Verify network connectivity
   - Check sensor installation and service status

2. **Command queued but not executed**:
   - Sensor may be offline when command issued
   - Command will execute when sensor reconnects
   - Check sensor command queue

3. **Insufficient permissions**:
   - Some commands require elevated privileges
   - Ensure sensor running with appropriate permissions
   - Windows: Local System or Administrator
   - Linux: root

4. **Command syntax error**:
   ```bash
   # Problem: Wrong path format
   file_info C:\path\to\file.exe  # Missing quotes if spaces

   # Solution: Use quotes
   file_info "C:\path with spaces\file.exe"
   ```

**Troubleshooting steps**:
1. Verify sensor is online in UI
2. Check sensor connectivity (last seen timestamp)
3. Try simple command first: `os_processes`
4. Review sensor error logs if available
5. Verify command syntax
6. Check Organization permissions and quotas

---

### File Not Found Errors

**Symptoms**: Commands like `file_info`, `file_hash`, or `artifact_get` fail with "file not found".

**Common causes**:

1. **Incorrect path**:
   ```bash
   # Problem: Wrong path or typo
   file_info C:\Windows\System32\notepad.exe  # Typo in filename

   # Solution: Verify path, use tab completion where possible
   file_info C:\Windows\System32\notepad.exe
   ```

2. **File doesn't exist**:
   - File may have been deleted
   - Use LCQL to find file creation/deletion: `-7d | plat == windows | FILE_DELETE | event/FILE_PATH contains "filename"`

3. **Path escaping**:
   ```bash
   # Problem: Spaces in path not handled
   file_info C:\Program Files\app.exe

   # Solution: Use quotes
   file_info "C:\Program Files\app.exe"
   ```

4. **Wildcards not supported**:
   ```bash
   # Problem: Wildcards in wrong command
   file_hash C:\Windows\*.exe  # file_hash doesn't support wildcards

   # Solution: Use dir_list then iterate
   dir_list C:\Windows
   # Then file_hash specific files
   ```

5. **Case sensitivity (Linux)**:
   ```bash
   # Problem: Wrong case on Linux
   file_info /home/user/File.txt  # Actual: /home/user/file.txt

   # Solution: Use correct case
   file_info /home/user/file.txt
   ```

---

### Permission Denied Errors

**Symptoms**: Commands fail with access denied or permission errors.

**Common causes**:

1. **Insufficient sensor privileges**:
   - Sensor not running as SYSTEM/root
   - File locked by another process
   - System files require elevated access

2. **File in use**:
   ```bash
   # Problem: File locked
   artifact_get C:\Windows\System32\config\SAM  # Locked by system

   # Solution: Registry hives require special handling or system offline
   # Consider memory dump or MFT collection instead
   ```

3. **Protected system files**:
   - Some files protected by OS
   - May need to boot to forensic environment
   - Consider alternative evidence sources

**Solutions**:
- Verify sensor running with administrative privileges
- Use alternative collection methods (memory dump, MFT)
- Check file permissions with `file_info`
- Consider offline collection from disk image

---

## Artifact Collection Issues

### Artifact Collection Fails

**Symptoms**: `artifact_get` command fails or artifact not uploaded.

**Common causes**:

1. **File too large**:
   - Default size limits may apply
   - Check Organization settings for artifact size limits
   - Consider collecting selectively or compressing

2. **Network issues**:
   - Sensor can't reach LimaCharlie cloud
   - Firewall blocking uploads
   - Bandwidth limitations

3. **Storage quota exceeded**:
   - Organization artifact storage quota full
   - Check quota in Organization settings
   - Clean up old artifacts or increase quota

4. **File locked or in use**:
   - File being written or locked
   - System files may be locked
   - Retry or use alternative collection method

**Troubleshooting**:
1. Check artifact size: `file_info <path>`
2. Verify sensor connectivity
3. Check Organization artifact storage quota
4. Review sensor command history for errors
5. Try collecting smaller file first (test)

---

### Artifact Download Fails

**Symptoms**: Can't download artifact from Artifact Collection UI.

**Common causes**:

1. **Artifact expired**:
   - Retention period passed
   - Artifact automatically deleted
   - Check retention policy

2. **Browser issues**:
   - Try different browser
   - Clear cache
   - Check browser console for errors

3. **Network issues**:
   - Corporate firewall/proxy
   - VPN issues
   - Try from different network

4. **Large file download**:
   - Connection timeout
   - Resume not supported
   - Use API for large downloads

**Solutions**:
- Download via API for large files
- Use download manager
- Break large collections into smaller parts
- Verify artifact still within retention period

---

## Memory Analysis Issues

### Memory Commands Not Available

**Symptoms**: Commands like `mem_map`, `mem_strings` not recognized.

**Common causes**:

1. **Platform not supported**:
   - Memory commands available on Windows and Linux
   - Some commands Windows-only (mem_handles)

2. **Sensor version**:
   - Old sensor version may not support memory commands
   - Update sensor to latest version

3. **Process not found**:
   ```bash
   # Problem: PID no longer exists
   mem_map --pid 1234  # Process terminated

   # Solution: Get current process list
   os_processes
   # Use current PID
   ```

**Solutions**:
- Verify platform support
- Update sensor to latest version
- Confirm process still running
- Check LimaCharlie documentation for feature availability

---

### Memory Dump Fails

**Symptoms**: Memory dump via Dumper extension fails or incomplete.

**Common causes**:

1. **Insufficient disk space**:
   - Memory dump size = RAM size
   - Sensor needs temp space for dump
   - Check endpoint disk space

2. **Insufficient memory**:
   - System under memory pressure
   - May cause dump to fail
   - Consider collecting when system idle

3. **Timeout**:
   - Large memory takes time to dump
   - Default timeout may be too short
   - Memory dump is resource-intensive

4. **Upload failure**:
   - Network issues during upload
   - Large file upload may timeout
   - Check sensor connectivity

**Solutions**:
- Ensure adequate disk space (RAM size + 20%)
- Collect during low activity period
- Verify network stability
- Check sensor logs for specific error
- Consider increasing timeout in extension configuration

---

### Volatility Analysis Fails

**Symptoms**: Volatility can't parse memory dump or gives errors.

**Common causes**:

1. **Profile mismatch**:
   ```bash
   # Problem: Wrong profile
   vol.py -f memory.dmp --profile=Win7SP1x64 pslist  # But it's Win10

   # Solution: Use Volatility 3 (auto-detection) or imageinfo
   vol3 -f memory.dmp windows.info
   vol3 -f memory.dmp windows.pslist
   ```

2. **Corrupted dump**:
   - Incomplete download
   - Network corruption during transfer
   - Verify file size and hash

3. **Unsupported OS version**:
   - Very new or very old OS
   - Custom kernel
   - Try alternative tools (Rekall, WinDbg)

4. **Insufficient RAM for analysis**:
   - Volatility needs substantial RAM
   - Analyzing 16GB dump may need 32GB+ RAM
   - Use machine with adequate resources

**Solutions**:
- Use Volatility 3 for better profile detection
- Verify dump integrity (file size, hash)
- Ensure analysis machine has adequate RAM
- Try alternative memory forensics tools
- Break analysis into smaller commands

---

## Timeline Reconstruction Issues

### Timeline Has Gaps

**Symptoms**: Expected events missing from timeline.

**Common causes**:

1. **Sensor offline**:
   - Sensor disconnected during incident
   - No telemetry when offline
   - Check CONNECTED/DISCONNECTED events

2. **Event type not enabled**:
   - Some events may be filtered by policy
   - Check sensor configuration and D&R rules
   - Verify event types are being collected

3. **Data retention**:
   - Events older than retention period deleted
   - Default retention varies by plan
   - Historical data may not be available

4. **High volume event filtering**:
   - Some high-volume events may be sampled
   - Check if critical event types are fully collected
   - Review Organization event collection settings

**Solutions**:
- Check sensor connection history
- Verify sensor configuration and enabled event types
- Review retention policy
- Correlate with other data sources (Windows Event Logs, syslog)
- Use artifact collection for historical logs

---

### Events Out of Order

**Symptoms**: Timeline shows events in unexpected sequence.

**Common causes**:

1. **Timestamp precision**:
   - Multiple events in same second
   - Events may appear in different order
   - Timestamps have millisecond precision

2. **Clock skew**:
   - System clock incorrect
   - Check STARTING_UP events for system time
   - Correlate with known good time sources

3. **Time zone confusion**:
   - All LC timestamps are UTC
   - Local time display may confuse
   - Always work in UTC for forensics

**Solutions**:
- Sort by timestamp with additional fields for tie-breaking
- Verify system clock accuracy
- Always use UTC for timeline analysis
- Consider clock skew in analysis
- Cross-reference with external time sources

---

### Cannot Correlate Events

**Symptoms**: Difficulty linking related events across different types.

**Common causes**:

1. **Process ID reuse**:
   - PIDs can be reused after process termination
   - Use FILE_PATH and TIMESTAMP for correlation
   - Consider process start time

2. **Missing join fields**:
   - Not all events have all fields
   - PROCESS_ID may not be in all event types
   - Use alternative correlation methods

3. **Hash not available**:
   - FILE_HASH may not be in all file events
   - Use FILE_PATH for correlation
   - Run file_hash command to get hash

**Solutions**:
- Use multiple correlation fields (PID + timestamp + path)
- Build process tree from NEW_PROCESS events
- Use hash-based correlation when available
- Consider file path and user for correlation
- Build custom correlation logic in analysis

---

## Performance and Scaling

### Slow Query Performance

**Symptoms**: Queries take long time to complete.

**Optimizations**:

1. **Reduce time window**:
   ```
   # Instead of -30d, use -7d or -24h
   -24h | plat == windows | NEW_PROCESS
   ```

2. **Filter by event type first**:
   ```
   # Good: Event type filter first
   -7d | NEW_PROCESS | event/FILE_PATH contains "suspicious"

   # Less efficient: Condition before event type
   -7d | event/FILE_PATH contains "suspicious" | NEW_PROCESS
   ```

3. **Use specific hostname filters**:
   ```
   # More efficient
   -7d | routing/hostname == "specific-host" | NEW_PROCESS

   # Less efficient (queries all hosts)
   -7d | NEW_PROCESS | routing/hostname == "specific-host"
   ```

4. **Limit field selection**:
   ```
   # Good: Select only needed fields
   event/TIMESTAMP as time event/FILE_PATH as process

   # Less efficient: Select all fields with *
   event/* as data
   ```

5. **Use aggregation to reduce results**:
   ```
   # Aggregate instead of returning all events
   -7d | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process)
   ```

---

### Running Out of Storage

**Symptoms**: Can't collect more artifacts, storage quota exceeded.

**Solutions**:

1. **Clean up old artifacts**:
   - Review and delete artifacts from completed investigations
   - Set appropriate retention periods

2. **Increase quota**:
   - Contact LimaCharlie support
   - Upgrade plan if needed

3. **Collect selectively**:
   - Don't collect entire directories
   - Target specific files of interest
   - Use compression where possible

4. **Use external storage**:
   - Download and store artifacts externally
   - Delete from LC after external backup
   - Maintain local forensic archive

---

## Data Retention and Storage

### Historical Data Not Available

**Symptoms**: Cannot query events older than certain period.

**Common causes**:

1. **Retention period expired**:
   - Data deleted per retention policy
   - Check Organization retention settings
   - Default varies by subscription plan

2. **Sensor not installed**:
   - Sensor installed after event occurred
   - No retroactive data collection
   - Only events after sensor install available

3. **Event type not collected**:
   - Event type may have been disabled in past
   - Check historical sensor configuration
   - Some event types may not have been available

**Solutions**:
- Review and adjust retention policy
- Collect static artifacts (logs, registry) for historical data
- Use artifact collection to preserve evidence beyond retention
- Consider longer retention or archival strategy
- Export critical events for long-term storage

---

### Chain of Custody Concerns

**Symptoms**: Need to prove evidence integrity for legal proceedings.

**Best practices**:

1. **Hash everything**:
   ```bash
   # Hash before collection
   file_hash C:\evidence\file.exe
   # Document hash
   # Collect
   artifact_get C:\evidence\file.exe --investigation CASE-001
   # Hash after download
   # Verify match
   ```

2. **Use investigation IDs**:
   ```bash
   # All commands for same investigation
   artifact_get C:\malware.exe --investigation CASE-001
   history_dump --investigation CASE-001
   os_processes --investigation CASE-001
   ```

3. **Document everything**:
   - Timestamp of collection (UTC)
   - Collector identity
   - Reason for collection
   - Source sensor ID and hostname
   - Commands used
   - Results observed

4. **Maintain evidence log**:
   - Who accessed evidence
   - When accessed
   - Purpose of access
   - Any modifications (none for forensics)
   - Chain of custody form

5. **Preserve original**:
   - Never analyze original evidence
   - Work on copies
   - Maintain original in secure storage
   - Document any analysis

---

### Cannot Reproduce Investigation

**Symptoms**: Another investigator can't reproduce your findings.

**Common causes**:

1. **LCQL queries not documented**:
   - Document all queries used
   - Include exact query syntax
   - Note time windows used

2. **Timestamps ambiguous**:
   - Specify timezone (use UTC)
   - Include millisecond precision
   - Document time range clearly

3. **Sensor commands not recorded**:
   - Document all commands executed
   - Include command parameters
   - Save command outputs

4. **Context missing**:
   - Document investigative reasoning
   - Explain why specific queries used
   - Include hypothesis and findings

**Solutions**:
- Document all LCQL queries in report
- Save query results as CSV exports
- Record sensor commands and outputs
- Maintain detailed investigation notes
- Include all queries in report appendix
- Use investigation IDs consistently
- Export key evidence for reference

---

## General Troubleshooting Tips

### 1. Start Simple, Add Complexity

- Begin with broadest query: `-24h | *`
- Add filters incrementally
- Test each addition
- Identify where query breaks

### 2. Verify Assumptions

- Check sensor is online
- Verify platform is correct
- Confirm event types are collected
- Validate field paths exist

### 3. Check Documentation

- Review LimaCharlie docs for latest syntax
- Check release notes for changes
- Verify feature availability for your plan
- Consult community forums

### 4. Use Test Queries

- Test queries on known-good data first
- Verify query logic with expected results
- Use small time windows for testing
- Expand once query works

### 5. Break Down Problems

- Isolate issue (query, command, collection)
- Test components individually
- Rule out network, permissions, etc.
- Narrow down root cause systematically

---

## Getting Help

**LimaCharlie Documentation**: https://doc.limacharlie.io

**Community Slack**: Join for peer support and tips

**Support Tickets**: For plan-specific issues and bugs

**This Skill**: Return to SKILL.md for methodology, REFERENCE.md for commands, EXAMPLES.md for scenarios, ADVANCED.md for techniques

---

## Additional Resources

**For command reference**: See REFERENCE.md

**For investigation scenarios**: See EXAMPLES.md

**For advanced analysis**: See ADVANCED.md

**For core methodology**: See SKILL.md
