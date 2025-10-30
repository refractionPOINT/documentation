# YARA Troubleshooting Guide

Performance optimization, suppression strategies, and debugging for YARA rules in LimaCharlie.

**See also:**
- [SKILL.md](./SKILL.md): Overview and quick start
- [REFERENCE.md](./REFERENCE.md): Complete syntax reference
- [EXAMPLES.md](./EXAMPLES.md): Complete rule examples

---

## Table of Contents

1. [Performance Issues](#performance-issues)
2. [Suppression Strategies](#suppression-strategies)
3. [Rule Debugging](#rule-debugging)
4. [Scanning Issues](#scanning-issues)
5. [False Positives](#false-positives)
6. [Best Practices](#best-practices)

---

## Performance Issues

### Understanding YARA Performance Impact

YARA scanning is CPU-intensive and can impact endpoint performance if not properly managed.

**Resource consumption:**
- CPU: High during active scanning
- Memory: Moderate (depends on rule complexity)
- Disk I/O: High for file scanning
- Network: Minimal (unless rules are fetched remotely)

### Critical Rule: Always Use Suppression

**Without suppression:**
- Same file/process scanned repeatedly
- High CPU utilization on endpoints
- Performance degradation
- Wasted resources
- Potential sensor instability

**With suppression:**
- Resources scanned once per time period
- Controlled CPU utilization
- Predictable performance impact
- Efficient resource usage

### Symptom: High CPU Usage

**Problem:** Sensors showing high CPU utilization after deploying YARA scans.

**Diagnosis:**
1. Check D&R rule event frequency
2. Verify suppression is configured
3. Review YARA rule complexity
4. Check file size limits

**Solutions:**

**1. Add suppression if missing:**
```yaml
respond:
  - action: task
    command: yara_scan hive://yara/my-rule --pid "{{ .event.PROCESS_ID }}"
    suppression:
      is_global: false
      keys:
        - '{{ .event.PROCESS_ID }}'
      max_count: 1
      period: 5m
```

**2. Increase suppression period:**
```yaml
suppression:
  period: 10m  # Increase from 5m to 10m
```

**3. Add file size limits:**
```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    # ... other rules
    - op: is lower than
      path: event/FILE_SIZE
      value: 10485760  # 10 MB limit
```

**4. Narrow detection scope:**
```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    # Only scan specific file types
    - op: ends with
      path: event/FILE_PATH
      value: .exe
      case sensitive: false
    # Only scan specific directories
    - op: contains
      path: event/FILE_PATH
      value: \Downloads\
```

**5. Optimize YARA rules:**
```yara
condition:
    // Fast checks first
    filesize < 2MB and
    uint16(0) == 0x5A4D and
    // Slower string matching last
    2 of ($string*)
```

### Symptom: Slow Scanning

**Problem:** YARA scans taking too long to complete.

**Diagnosis:**
1. Check file sizes being scanned
2. Review YARA rule complexity
3. Check number of strings in rule
4. Verify scanning method (file vs. memory)

**Solutions:**

**1. Limit file sizes:**
```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    - op: is lower than
      path: event/FILE_SIZE
      value: 5242880  # 5 MB
```

**2. Simplify YARA rules:**
```yara
// Before (slow)
strings:
    $s1 = "string1"
    $s2 = "string2"
    // ... 50 more strings
condition:
    any of them

// After (faster)
strings:
    $s1 = "unique_malware_identifier_12345"
    $s2 = "specific_pattern"
condition:
    all of them
```

**3. Use specific patterns:**
```yara
// Slow: generic strings
strings:
    $generic = "Windows"

// Fast: specific strings
strings:
    $specific = "UNIQUE_MALWARE_MUTEX_NAME"
```

**4. Add quick filters:**
```yara
condition:
    // Quick filter
    uint16(0) == 0x5A4D and
    filesize < 1MB and
    // Then check strings
    any of them
```

### Symptom: Sensor Instability

**Problem:** Sensors becoming unresponsive or crashing after YARA deployment.

**Diagnosis:**
1. Check if suppression is configured
2. Review D&R rule trigger frequency
3. Verify file size limits
4. Check for infinite loops in detection logic

**Solutions:**

**1. Emergency fix - Disable D&R rule:**
```
Navigate to D&R Rules → Find problematic rule → Set to "Disabled"
```

**2. Add conservative suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
    - '{{ .routing.sid }}'  # Include sensor ID
  max_count: 1
  period: 1h  # Long period for stability
```

**3. Staged rollout:**
```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    # ... detection logic
    # Only apply to test sensors
    - op: is tagged
      tag: yara-test-group
```

**4. Add circuit breaker:**
```yaml
suppression:
  is_global: true  # Organization-wide limit
  keys:
    - YARA_SCAN_GLOBAL_LIMIT
  max_count: 100   # Max 100 scans org-wide
  period: 1m       # Per minute
```

---

## Suppression Strategies

### Basic Suppression

**By Process ID:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.PROCESS_ID }}'
  max_count: 1
  period: 1m
```

**By File Path:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 5m
```

**By File Hash:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.HASH }}'
  max_count: 1
  period: 10m
```

### Advanced Suppression

**Multi-key suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
    - '{{ .routing.sid }}'
    - Yara Scan Identifier
  max_count: 1
  period: 5m
```

**Per-sensor suppression:**
```yaml
suppression:
  is_global: false  # Different limit per sensor
  keys:
    - '{{ .routing.sid }}'
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 5m
```

**Global suppression (organization-wide):**
```yaml
suppression:
  is_global: true  # Same limit across all sensors
  keys:
    - '{{ .event.HASH }}'
  max_count: 1
  period: 1h
```

**Time-based suppression:**
```yaml
# 1 minute
suppression:
  period: 1m

# 5 minutes
suppression:
  period: 5m

# 1 hour
suppression:
  period: 1h

# 24 hours
suppression:
  period: 24h
```

**Count-based suppression:**
```yaml
# Allow once
suppression:
  max_count: 1

# Allow 3 times
suppression:
  max_count: 3

# Allow 10 times
suppression:
  max_count: 10
```

### Suppression Patterns by Use Case

**High-frequency events (NEW_PROCESS):**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.PROCESS_ID }}'
  max_count: 1
  period: 1m  # Short period OK for processes
```

**Medium-frequency events (NEW_DOCUMENT):**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 5m  # Medium period for files
```

**Low-frequency events (specific detections):**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.HASH }}'
  max_count: 1
  period: 1h  # Long period for rare events
```

**Production deployments:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
    - '{{ .routing.sid }}'
    - Production YARA Scan
  max_count: 1
  period: 10m  # Conservative period
```

### Testing Suppression

**Step 1: Start with conservative suppression:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.FILE_PATH }}'
  max_count: 1
  period: 10m  # Long period
```

**Step 2: Deploy to test sensors:**
```yaml
detect:
  op: and
  rules:
    # ... detection logic
    - op: is tagged
      tag: yara-test
```

**Step 3: Monitor scan frequency:**
- Check detection logs
- Monitor CPU usage
- Review scan count

**Step 4: Adjust as needed:**
```yaml
# If too many scans:
suppression:
  period: 15m  # Increase period

# If too few scans:
suppression:
  period: 5m   # Decrease period
```

---

## Rule Debugging

### Symptom: Rule Not Matching

**Problem:** YARA rule should match but doesn't trigger detection.

**Diagnosis:**

**1. Test rule locally:**
```bash
# Install YARA locally
yara my-rule.yar /path/to/test/file
```

**2. Check rule syntax:**
```bash
# Validate syntax
yara -w my-rule.yar /path/to/test/file
```

**3. Verify rule is deployed:**
```bash
# Check Config Hive
limacharlie hive get yara --key my-rule
```

**4. Check D&R rule triggers:**
- Review event logs
- Verify D&R rule is enabled
- Check D&R rule conditions

**Solutions:**

**1. Simplify condition:**
```yara
// Before
condition:
    uint16(0) == 0x5A4D and
    filesize < 1MB and
    3 of ($string*) and
    any of ($hex*)

// After (test incrementally)
condition:
    any of them
```

**2. Add debug logging:**
```yaml
respond:
  - action: report
    name: "YARA scan triggered for {{ .event.FILE_PATH }}"
  - action: task
    command: yara_scan hive://yara/my-rule -f "{{ .event.FILE_PATH }}"
```

**3. Check string encoding:**
```yara
// If matching Unicode strings
strings:
    $text = "malware" wide ascii
```

**4. Use case-insensitive matching:**
```yara
strings:
    $text = "malware" nocase
```

### Symptom: Too Many False Positives

**Problem:** YARA rule matching legitimate files.

**Diagnosis:**
1. Review matched files
2. Identify common patterns
3. Test against known-good files

**Solutions:**

**1. Add file type checks:**
```yara
condition:
    uint16(0) == 0x5A4D and  // PE files only
    2 of ($string*)
```

**2. Increase string requirements:**
```yara
// Before
condition:
    any of them

// After
condition:
    3 of them  // Require more strings
```

**3. Add exclusions:**
```yara
strings:
    $malware = "suspicious"
    $legitimate1 = "Microsoft Corporation"
    $legitimate2 = "Signed by: Trusted CA"

condition:
    $malware and
    not (any of ($legitimate*))
```

**4. Use more specific strings:**
```yara
// Before (generic)
strings:
    $s1 = "cmd"

// After (specific)
strings:
    $s1 = "cmd.exe /c whoami" fullword
```

**5. Add D&R exclusions:**
```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: is
      path: event/RULE_NAME
      value: My_YARA_Rule
    # Exclude known false positives
    - not: true
      op: contains
      path: event/FILE_PATH
      value: C:\Windows\System32\

respond:
  - action: report
    name: YARA Detection (filtered)
```

### Symptom: Rule Not Updating

**Problem:** Updated YARA rule not taking effect.

**Solutions:**

**1. Verify rule is updated in Config Hive:**
```bash
limacharlie hive get yara --key my-rule
```

**2. Re-set the rule:**
```bash
limacharlie hive set yara --key my-rule --data my-rule.yar --data-key rule
```

**3. Manual sync (if using YARA Manager):**
- Navigate to YARA Manager extension
- Click **Manual Sync** button

**4. Check D&R rule references correct key:**
```yaml
respond:
  - action: task
    command: yara_scan hive://yara/my-rule  # Verify key name
```

---

## Scanning Issues

### Symptom: Scan Not Executing

**Problem:** D&R rule triggers but YARA scan doesn't execute.

**Diagnosis:**
1. Check sensor console for errors
2. Verify rule exists in Config Hive
3. Check suppression isn't blocking
4. Review sensor permissions

**Solutions:**

**1. Check rule reference:**
```yaml
# Correct
command: yara_scan hive://yara/my-rule -f "{{ .event.FILE_PATH }}"

# Wrong - missing hive://
command: yara_scan yara/my-rule -f "{{ .event.FILE_PATH }}"
```

**2. Verify file path:**
```yaml
# Add debug logging
respond:
  - action: report
    name: "Attempting scan of {{ .event.FILE_PATH }}"
  - action: task
    command: yara_scan hive://yara/my-rule -f "{{ .event.FILE_PATH }}"
```

**3. Check suppression:**
```yaml
# Temporarily remove suppression to test
respond:
  - action: task
    command: yara_scan hive://yara/my-rule -f "{{ .event.FILE_PATH }}"
    # suppression: ...  # Comment out
```

**4. Verify sensor has access:**
```bash
# List available rules
limacharlie hive list yara
```

### Symptom: Scan Timeout

**Problem:** YARA scan times out before completing.

**Solutions:**

**1. Reduce file size limit:**
```yaml
detect:
  rules:
    - op: is lower than
      path: event/FILE_SIZE
      value: 5242880  # Reduce to 5 MB
```

**2. Simplify YARA rule:**
```yara
// Reduce number of strings
strings:
    $s1 = "specific_pattern"
    $s2 = "another_specific_pattern"
    // Remove generic strings

condition:
    all of them  // Faster than complex logic
```

**3. Scan memory instead of disk:**
```yaml
# If file is already loaded in memory
respond:
  - action: task
    command: yara_scan hive://yara/my-rule --pid "{{ .event.PROCESS_ID }}"
```

### Symptom: No YARA_DETECTION Event

**Problem:** YARA scan completes but no YARA_DETECTION event generated.

**Diagnosis:**
1. Rule didn't match (expected behavior)
2. YARA_DETECTION event is generated but not detected by D&R rule
3. Sensor issue

**Solutions:**

**1. Test rule locally:**
```bash
yara my-rule.yar /path/to/test/file
```

**2. Check D&R rule for YARA_DETECTION:**
```yaml
detect:
  event: YARA_DETECTION
  op: exists
  path: event/RULE_NAME

respond:
  - action: report
    name: "YARA Detection: {{ .event.RULE_NAME }}"
```

**3. Review timeline:**
- Check sensor timeline for YARA_DETECTION events
- Verify event occurred

---

## False Positives

### Identifying False Positives

**Indicators of false positives:**
- Matches on legitimate software
- Matches on Windows system files
- Matches on signed binaries
- High detection volume on common files

### Reducing False Positives

**1. Add file type validation:**
```yara
condition:
    uint16(0) == 0x5A4D and  // Must be PE file
    filesize > 10KB and       // Minimum size
    filesize < 5MB and        // Maximum size
    3 of ($string*)           // Multiple indicators
```

**2. Require multiple indicators:**
```yara
condition:
    (uint16(0) == 0x5A4D) and
    (2 of ($malware_string*)) and
    (1 of ($malware_hex*)) and
    not (any of ($legitimate*))
```

**3. Add signature checks (D&R):**
```yaml
detect:
  event: NEW_DOCUMENT
  op: and
  rules:
    # ... file detection
    # Exclude signed files
    - not: true
      op: exists
      path: event/SIGNATURE/CERT_CHAIN/*/CERT_ISSUER

respond:
  - action: task
    command: yara_scan hive://yara/my-rule -f "{{ .event.FILE_PATH }}"
```

**4. Path-based exclusions:**
```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: is
      path: event/RULE_NAME
      value: My_YARA_Rule
    # Exclude system directories
    - not: true
      op: starts with
      path: event/FILE_PATH
      value: C:\Windows\
      case sensitive: false

respond:
  - action: report
    name: YARA Detection (filtered)
```

**5. Known-good hash exclusions:**
```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: is
      path: event/RULE_NAME
      value: My_YARA_Rule
    # Exclude known-good hashes
    - not: true
      op: is
      path: event/HASH
      value: abc123...

respond:
  - action: report
    name: YARA Detection (filtered)
```

### Managing False Positive Reports

**Create FP suppression rule:**
```yaml
detect:
  event: YARA_DETECTION
  op: and
  rules:
    - op: is
      path: event/RULE_NAME
      value: My_YARA_Rule
    - op: or
      rules:
        # Known FP: Legitimate Software X
        - op: is
          path: event/FILE_PATH
          value: C:\Program Files\LegitSoftware\app.exe
        # Known FP: Development Tools
        - op: contains
          path: event/FILE_PATH
          value: \Visual Studio\

respond:
  # No report - suppress false positive
  - action: add tag
    tag: yara-false-positive
    ttl: 3600
```

---

## Best Practices

### Pre-Deployment Testing

**1. Test rules locally:**
```bash
# Test against known samples
yara my-rule.yar /path/to/malware/samples/

# Test against clean files
yara my-rule.yar /path/to/clean/files/
```

**2. Use D&R replay:**
```bash
# Test D&R integration
limacharlie replay --rule-content dr-rule.yaml --events test-events.json
```

**3. Staged rollout:**
```yaml
# Phase 1: Test sensors only
detect:
  op: and
  rules:
    # ... detection logic
    - op: is tagged
      tag: yara-test-phase1

# Phase 2: Pilot group
detect:
  op: and
  rules:
    # ... detection logic
    - op: is tagged
      tag: yara-pilot

# Phase 3: Production
detect:
  # ... detection logic (no tag filter)
```

### Monitoring and Tuning

**1. Monitor detection volume:**
- Check detection count per hour
- Review false positive rate
- Monitor CPU usage

**2. Review matched files:**
- Investigate first 10-20 matches
- Verify true positives
- Identify false positive patterns

**3. Adjust suppression:**
```yaml
# If too many scans:
suppression:
  period: 10m  # Increase

# If too few detections:
suppression:
  period: 2m   # Decrease
```

**4. Refine rules:**
```yara
// Add version tracking
meta:
    version = "1.1"
    changelog = "Reduced false positives by adding exclusions"

// Add exclusions
strings:
    $exclude1 = "Legitimate Software Name"

condition:
    (all of ($malware*)) and
    not ($exclude1)
```

### Performance Monitoring

**Metrics to track:**
- Scan execution count (per hour)
- CPU usage (during scans)
- Scan duration (average)
- Detection rate (true vs. false positives)

**Optimization checklist:**
- [ ] Suppression configured
- [ ] File size limits set
- [ ] Specific detection scope
- [ ] YARA rules optimized (fast checks first)
- [ ] Staged rollout completed
- [ ] False positives addressed
- [ ] Monitoring in place

### Documentation

**Document each rule:**
```yara
meta:
    description = "Detects XYZ malware family"
    author = "Security Team"
    date = "2025-01-15"
    version = "1.0"
    reference = "https://internal-wiki/yara-rules/xyz-malware"

    // Deployment info
    deployed_date = "2025-01-20"
    test_results = "10/10 true positives, 0 false positives"
    known_fps = "None"

    // Performance
    avg_scan_time = "500ms"
    max_file_size = "5MB"
```

**Maintain changelog:**
```
# YARA Rule Changelog

## v1.2 - 2025-01-25
- Reduced false positives by adding Microsoft signature exclusion
- Increased suppression period from 5m to 10m
- Added file size limit of 5MB

## v1.1 - 2025-01-20
- Added additional string patterns
- Improved detection rate by 15%

## v1.0 - 2025-01-15
- Initial deployment
```

---

For syntax details, see [REFERENCE.md](./REFERENCE.md). For complete examples, see [EXAMPLES.md](./EXAMPLES.md).
