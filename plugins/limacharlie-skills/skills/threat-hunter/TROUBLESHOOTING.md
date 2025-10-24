# Threat Hunting Troubleshooting

Query optimization, false positive management, and common hunting challenges with solutions.

## Table of Contents

- [Query Optimization](#query-optimization)
- [False Positive Management](#false-positive-management)
- [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
- [Performance Tuning](#performance-tuning)
- [Investigation Tips](#investigation-tips)

## Query Optimization

### Time Range Selection

**Problem:** Query takes too long to execute or times out.

**Solution:**
- Start with narrow time ranges (-24h, -7d)
- Gradually expand if needed
- Use specific time ranges for targeted hunts

**Example:**
```
# Instead of:
-30d | plat == windows | NEW_PROCESS | ...

# Use:
-24h | plat == windows | NEW_PROCESS | ...
```

### Platform Filtering

**Problem:** Query returns results from all platforms when only investigating Windows.

**Solution:**
- Always specify platform when relevant
- Use `plat ==` selector early in query
- Reduces data processing overhead

**Example:**
```
# Good:
-24h | plat == windows | NEW_PROCESS | ...

# Bad:
-24h | NEW_PROCESS | ... | routing/plat == "windows"
```

### Event Type Specificity

**Problem:** Using wildcard `*` event type returns too much data.

**Solution:**
- Use specific event types whenever possible
- Only use `*` when truly searching across all events
- Combine multiple specific queries instead

**Example:**
```
# Instead of:
-24h | plat == windows | * | event/* contains "mimikatz"

# Use:
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "mimikatz"
```

### Projection Optimization

**Problem:** Query returns too many fields, making results hard to analyze.

**Solution:**
- Project only necessary fields
- Use meaningful aliases
- Reduce data transfer and display overhead

**Example:**
```
# Good:
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as process event/COMMAND_LINE as cmd routing/hostname as host

# Bad:
-24h | plat == windows | NEW_PROCESS | event/* routing/*
```

### Aggregation Efficiency

**Problem:** Aggregation queries run slowly or produce too many results.

**Solution:**
- Use aggregation functions to reduce result volume
- Filter before aggregating
- Order results appropriately

**Example:**
```
# Efficient:
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process) ORDER BY(count DESC) | count >= 10

# Inefficient:
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process)
```

### Filter Ordering

**Problem:** Query filters inefficiently, processing unnecessary data.

**Solution:**
- Apply most restrictive filters first
- Use indexed fields when available
- Combine filters logically

**Example:**
```
# Good (filters early):
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" and event/COMMAND_LINE contains "-enc" | ...

# Less efficient (filters late):
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as path event/COMMAND_LINE as cmd | ...
# Then manually filter results
```

### Sensor Selector Optimization

**Problem:** Query searches all sensors when only targeting specific hosts.

**Solution:**
- Use hostname or tag selectors
- Target specific sensor groups
- Reduce query scope

**Example:**
```
# Targeted:
-24h | hostname == "WEB-SERVER-01" | NEW_PROCESS | ...

# Or by tag:
-24h | tag == "production" | NEW_PROCESS | ...

# Less efficient:
-24h | plat == windows | NEW_PROCESS | ... | routing/hostname == "WEB-SERVER-01"
```

## False Positive Management

### Understanding Context

**Problem:** Detection fires on legitimate administrative activity.

**Solution:**
- Understand normal business operations
- Document legitimate use cases
- Consider user, host, and time context

**Example Scenario:**
PowerShell execution detected, but it's from:
- IT administrator account
- Known management workstation
- During business hours
- For system maintenance

**Mitigation:**
```yaml
# Add exclusions to D&R rule
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: powershell.exe
    # Exclude known admin hosts
    - op: is
      path: routing/hostname
      value: ADMIN-WKS-01
      not: true
```

### Whitelisting Known-Good

**Problem:** Legitimate tools trigger alerts repeatedly.

**Solution:**
- Create lookup tables for known-good hashes
- Whitelist approved applications
- Document exceptions

**Example:**
```yaml
# Create lookup: hive://lookup/approved-tools
# Hash1
# Hash2
# Hash3

# Then in D&R rule:
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: certutil.exe
    - op: lookup
      path: event/HASH
      resource: hive://lookup/approved-tools
      not: true  # Only alert if NOT in approved list
```

### Baseline-Based Filtering

**Problem:** Alerts on common activity without context.

**Solution:**
- Establish baselines for normal behavior
- Alert only on deviations from baseline
- Use prevalence-based detection

**Example:**
```
# Baseline query (run weekly):
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT_UNIQUE(routing/sid) as prevalence GROUP BY(process)

# Hunt for low-prevalence processes:
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT_UNIQUE(routing/sid) as prevalence GROUP BY(process) | prevalence <= 5
```

### Suppression Configuration

**Problem:** Same alert fires multiple times for same event.

**Solution:**
- Use suppression in D&R rules
- Set appropriate suppression keys and periods
- Balance noise reduction with visibility

**Example:**
```yaml
respond:
  - action: report
    name: "Suspicious Activity"
    priority: 3
    suppression:
      max_count: 1      # Only report once
      period: 3600      # Per hour
      is_global: true   # Across all sensors
      keys:
        - '{{ .event.HASH }}'
        - '{{ .routing.hostname }}'
```

### Time-Based Filtering

**Problem:** Activity is normal during business hours but suspicious after-hours.

**Solution:**
- Use time-based detection logic
- Consider timezone differences
- Document expected schedules

**Example:**
```yaml
# D&R rule for after-hours detection
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
    - op: schedule
      schedule: "0 0-8,18-23 * * *"  # Outside 9am-6pm
```

### User-Based Exclusions

**Problem:** Certain users legitimately perform activities that would be suspicious for others.

**Solution:**
- Create user-based exclusions
- Maintain approved user lists
- Document privileged accounts

**Example:**
```yaml
# Create lookup: hive://lookup/admin-users
# admin1
# admin2
# svc-backup

detect:
  event: SENSITIVE_PROCESS_ACCESS
  op: and
  rules:
    - op: lookup
      path: event/USER
      resource: hive://lookup/admin-users
      not: true  # Only alert for non-admin users
```

### Stack Ranking vs. Hard Filtering

**Problem:** Filtering removes potentially interesting outliers.

**Solution:**
- Use stack ranking to find rare events
- Review both common and uncommon
- Let analysts make final determination

**Example:**
```
# Instead of filtering out common processes:
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH not in (...common processes...)

# Stack rank to see full picture:
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process) ORDER BY(count)
```

## Common Pitfalls and Solutions

### Pitfall 1: Alert Fatigue

**Problem:** Too many alerts, analysts become overwhelmed.

**Symptoms:**
- High volume of low-priority alerts
- Delayed response times
- Missed critical detections

**Solutions:**
1. Tune detection rules before deployment
2. Use appropriate priority levels
3. Implement suppression
4. Focus on high-fidelity detections
5. Review and disable noisy rules

**Action Plan:**
```
1. Audit current alert volume
2. Identify top 10 noisiest rules
3. Tune or disable each
4. Re-baseline alert volume
5. Repeat monthly
```

### Pitfall 2: Scope Creep

**Problem:** Hunt becomes unfocused, chasing too many leads.

**Symptoms:**
- Hunt takes days instead of hours
- Multiple unrelated findings
- Unclear objectives
- No actionable outcomes

**Solutions:**
1. Define clear hypothesis upfront
2. Set time limits for each hunt
3. Document scope boundaries
4. Stay focused on original question
5. Create new hunts for tangential findings

**Example:**
```
# Good: Focused hypothesis
"Hunt for PowerShell-based downloaders in the last 24 hours"

# Bad: Unfocused scope
"Hunt for any suspicious activity across all systems"
```

### Pitfall 3: Ignoring Baselines

**Problem:** No context for what's normal vs. abnormal.

**Symptoms:**
- Every finding looks suspicious
- Can't distinguish noise from signal
- High false positive rate

**Solutions:**
1. Establish baselines before hunting
2. Document normal business patterns
3. Use prevalence analysis
4. Compare against historical data

**Baseline Queries:**
```
# Process baselines (run monthly):
-30d | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process)

# Network baselines (run monthly):
-30d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst COUNT(event) as count GROUP BY(dst)

# User baselines (run monthly):
-30d | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/TargetUserName as user COUNT(event) as logons GROUP BY(user)
```

### Pitfall 4: Analysis Paralysis

**Problem:** Spending too much time analyzing without taking action.

**Symptoms:**
- Investigations drag on indefinitely
- No clear findings or outcomes
- Missed opportunities for timely response

**Solutions:**
1. Set time limits for investigations (2-4 hours)
2. Make go/no-go decisions at checkpoints
3. Escalate when stuck
4. Document and move on from dead ends
5. Timebox deep dives

**Investigation Template:**
```
Hour 1: Initial hunting and data gathering
Hour 2: Analysis and pivoting
Hour 3: Validation and documentation
Hour 4: Create detections and close out

If unclear after 4 hours: Escalate or park for later
```

### Pitfall 5: Missing Documentation

**Problem:** No record of hunting activities or findings.

**Symptoms:**
- Can't remember what was checked
- Duplicate work across team
- No lessons learned
- Can't recreate successful hunts

**Solutions:**
1. Document hypothesis before hunting
2. Record all queries executed
3. Note findings and false positives
4. Create runbooks for successful hunts
5. Share results with team

**Documentation Template:**
```markdown
## Hunt: [Name]
**Date:** 2025-10-23
**Hypothesis:** [What are we looking for?]
**Data Sources:** [Which events?]

### Queries Executed:
1. [Query 1] - [Findings]
2. [Query 2] - [Findings]

### Results:
- True Positives: [Count and details]
- False Positives: [Count and common patterns]
- IOCs Identified: [Hashes, IPs, domains]

### Follow-up Actions:
- [ ] Create D&R rule
- [ ] Update whitelist
- [ ] Hunt across more data
```

### Pitfall 6: Not Testing Rules

**Problem:** Deploying detection rules without validation.

**Symptoms:**
- Rules don't fire as expected
- Rules fire on everything
- Rules break incident response workflow

**Solutions:**
1. Always test with replay before deployment
2. Validate on known-good and known-bad data
3. Start with report-only mode
4. Monitor for 24-48 hours before enabling response actions
5. Document test results

**Testing Workflow:**
```
1. Create D&R rule in test organization
2. Replay known malicious event → Should fire
3. Replay known benign event → Should NOT fire
4. Deploy in report-only mode
5. Monitor for 24 hours
6. Review all detections
7. Tune as needed
8. Enable response actions
```

### Pitfall 7: Over-reliance on Automation

**Problem:** Trusting automated detections without manual validation.

**Symptoms:**
- False assumptions about security posture
- Missed sophisticated threats
- Blind spots in coverage

**Solutions:**
1. Combine automated detections with manual hunting
2. Regularly test detection coverage
3. Hunt for detection gaps
4. Challenge assumptions
5. Think like an attacker

**Balanced Approach:**
```
Weekly: Review automated detections
Bi-weekly: Hypothesis-driven threat hunts
Monthly: Red team exercise to test detections
Quarterly: Detection coverage assessment
```

### Pitfall 8: Forgetting Follow-up

**Problem:** Finding threats but not closing the loop with detections.

**Symptoms:**
- Same threats found repeatedly
- No improvement in detection rate
- Manual hunting becomes repetitive

**Solutions:**
1. Create D&R rules for confirmed threats
2. Update threat intelligence feeds
3. Share IOCs with team
4. Document lessons learned
5. Improve prevention controls

**Follow-up Checklist:**
```
- [ ] Create detection rule
- [ ] Test rule with replay
- [ ] Deploy to production
- [ ] Update threat intelligence
- [ ] Document in wiki
- [ ] Share with team
- [ ] Schedule review in 30 days
```

## Performance Tuning

### Query Response Time

**Problem:** Queries take too long to return results.

**Optimization Steps:**

1. **Reduce Time Range:**
```
# Instead of:
-30d | ...

# Try:
-7d | ...
```

2. **Add Platform Filter:**
```
# Add early in query:
-7d | plat == windows | ...
```

3. **Use Specific Event Types:**
```
# Instead of:
-7d | plat == windows | * | ...

# Use:
-7d | plat == windows | NEW_PROCESS | ...
```

4. **Limit Projections:**
```
# Only project needed fields:
... | event/FILE_PATH as path routing/hostname as host
```

5. **Use Aggregation:**
```
# Reduce result volume:
... | COUNT(event) as count GROUP BY(process)
```

### Memory Usage

**Problem:** Query consumes too much memory or fails.

**Solutions:**

1. **Add LIMIT clause (if supported):**
```
... | event/FILE_PATH as path | LIMIT 1000
```

2. **Use time-based chunking:**
```
# Run multiple smaller queries:
-24h | ...
-48h -24h | ...
-72h -48h | ...
```

3. **Narrow scope with filters:**
```
# Instead of all hosts:
-7d | hostname == "SPECIFIC-HOST" | ...
```

### Result Volume

**Problem:** Too many results to manually review.

**Solutions:**

1. **Use aggregation:**
```
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as process COUNT(event) as count GROUP BY(process) ORDER BY(count DESC)
```

2. **Focus on outliers:**
```
... | count <= 10  # Only rare events
```

3. **Use threshold filtering:**
```
... | COUNT(event) as connections GROUP BY(dst_ip) | connections > 100
```

## Investigation Tips

### Building Process Trees

**Problem:** Need to understand process lineage and relationships.

**Solution:**
Use `history_dump` sensor command to get full process tree:

```
# First, find suspicious process
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "suspicious" | routing/hostname as host

# Then use sensor command on identified host
history_dump
```

**Analysis:**
- Review parent-child relationships
- Identify process injection
- Understand attack sequence
- Find initial access point

### Collecting Evidence

**Problem:** Need to preserve files or data for analysis.

**Solution:**
Use sensor commands to collect evidence:

```
# Get file hash and signature
file_hash C:\suspicious\malware.exe

# Retrieve file
file_get C:\suspicious\malware.exe

# Get file metadata
file_info C:\suspicious\malware.exe

# Capture memory dump
mem_dump

# Get process memory strings
mem_strings --pid 1234
```

### Pivoting Effectively

**Problem:** Need to expand investigation from initial finding.

**Pivot Strategy:**

1. **By Hash:**
```
# Find all instances
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | routing/hostname as host
```

2. **By Domain:**
```
# Find all resolutions
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME == "evil.com" | routing/hostname as host
```

3. **By IP:**
```
# Find all connections
-7d | plat == windows | NETWORK_CONNECTIONS | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS == "1.2.3.4" | event/FILE_PATH as process routing/hostname as host
```

4. **By Process:**
```
# Find all network activity from process
-7d | plat == windows | NETWORK_CONNECTIONS | event/FILE_PATH == "C:\\malware.exe" | event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS as dst
```

### Checking Prevalence

**Problem:** Need to know if finding is isolated or widespread.

**Solution:**
Use COUNT_UNIQUE to determine prevalence:

```
# How many sensors saw this hash?
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | COUNT_UNIQUE(routing/sid) as sensor_count

# How many sensors resolved this domain?
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME == "evil.com" | COUNT_UNIQUE(routing/sid) as sensor_count

# How many users ran this process?
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH == "C:\\tool.exe" | COUNT_UNIQUE(event/USER) as user_count
```

### Timeline Analysis

**Problem:** Need to reconstruct attack sequence.

**Solution:**
Project timestamps and sort chronologically:

```
# Get all activity on host in time range
-24h | hostname == "COMPROMISED-HOST" | * | routing/event_type as type routing/event_time as time event/* as data | ORDER BY(time)
```

**Analysis Steps:**
1. Identify initial access time
2. Map lateral movement
3. Find persistence establishment
4. Identify data staging
5. Detect exfiltration

### Memory Analysis Workflow

**Problem:** Need to analyze running process memory.

**Workflow:**

1. **Identify suspicious process:**
```
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "\\Temp\\" | event/PROCESS_ID as pid routing/hostname as host
```

2. **Get memory strings:**
```
# Sensor command
mem_strings --pid <pid>
```

3. **Scan with YARA:**
```
# Sensor command
yara_scan hive://yara/malware-rules --pid <pid>
```

4. **Check handles:**
```
# Sensor command
mem_find_handle --pid <pid> lsass
```

5. **Capture full memory:**
```
# Sensor command
mem_dump
```

### Multi-Sensor Correlation

**Problem:** Need to identify if threat is isolated or widespread.

**Approach:**

1. **Start with single sensor finding:**
```
-24h | hostname == "HOST1" | NEW_PROCESS | event/HASH as hash
```

2. **Expand to all sensors:**
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | routing/hostname as host
```

3. **Identify affected population:**
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | COUNT_UNIQUE(routing/sid) as affected_count
```

4. **Map spread pattern:**
```
-7d | plat == windows | CODE_IDENTITY | event/HASH == "abc123..." | routing/hostname as host routing/event_time as time | ORDER BY(time)
```

### External Validation

**Problem:** Need to validate findings with external sources.

**Resources:**

1. **Hash reputation:**
   - VirusTotal
   - Hybrid Analysis
   - Any.run

2. **Domain/IP reputation:**
   - VirusTotal
   - AbuseIPDB
   - Shodan
   - URLhaus

3. **TTPs and techniques:**
   - MITRE ATT&CK
   - Threat intelligence feeds
   - Security vendor blogs

4. **File analysis:**
   - Joe Sandbox
   - Cuckoo Sandbox
   - Hybrid Analysis

**Validation Workflow:**
```
1. Extract IOC from hunt (hash, domain, IP)
2. Check against threat intelligence
3. Search OSINT sources
4. Review security vendor reports
5. Document findings
6. Update detection rules
```
