# Performance Optimizer - Troubleshooting

Common issues and detailed debugging steps for LimaCharlie performance optimization.

[← Back to SKILL.md](./SKILL.md)

## Table of Contents

1. [High Output Costs](#high-output-costs)
2. [Expensive Query Costs](#expensive-query-costs)
3. [Quota Waste Issues](#quota-waste-issues)
4. [Detection Noise Problems](#detection-noise-problems)
5. [Sensor Culling Issues](#sensor-culling-issues)
6. [Suppression Not Working](#suppression-not-working)
7. [Performance Mode Issues](#performance-mode-issues)
8. [Usage Alerts Not Firing](#usage-alerts-not-firing)
9. [GCP Output Issues](#gcp-output-issues)
10. [Query Performance Problems](#query-performance-problems)

---

## High Output Costs

### Symptom

- Unexpectedly high output costs
- Output data usage exceeding budget
- Billing shows large output_data SKU charges

### Diagnosis Steps

#### Step 1: Check Current Output Volume

**Via Web UI:**
1. Navigate to Organization Setup → Billing & Usage
2. Look for "output_data" metric
3. Note GB transmitted in current period

**Via API:**
```bash
curl https://api.limacharlie.io/v1/usage/YOUR_OID \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.usage.output_data'
```

#### Step 2: Identify Output Configurations

**Via Web UI:**
1. Navigate to Outputs
2. Review all configured outputs
3. Note stream type for each

**Check for:**
- Outputs using `stream: event` (forwards all events)
- Multiple outputs to same destination
- Outputs without proper filtering

#### Step 3: Analyze Output Destinations

**For each output, verify:**
- Destination type (Splunk, S3, Slack, etc.)
- Region/location
- Is it GCP in same region? (should be free)

### Common Causes

#### Cause 1: Forwarding Full Event Stream

**Problem:**
```yaml
stream: event  # Forwards ALL events
```

**Solution:**
```yaml
stream: detection  # Forward only alerts
```

**Impact:** 90-99% reduction in output volume

#### Cause 2: Non-GCP Output or Wrong Region

**Problem:**
```yaml
# Forwarding to S3 (charged)
type: s3
bucket: security-logs
```

**Solution:**
```yaml
# Use GCS in same region (free)
type: gcs
bucket: security-logs
region: us-central1  # Match your datacenter
```

**Impact:** Zero LimaCharlie output costs

#### Cause 3: Multiple Redundant Outputs

**Problem:**
- 3 different outputs forwarding same events
- Each counts toward output_data

**Solution:**
- Consolidate outputs
- Use single GCS output, then fan out from GCS
- Remove redundant forwarding

#### Cause 4: No Suppression on Output Actions

**Problem:**
```yaml
- action: output
  name: siem-output
# No suppression, forwards every match
```

**Solution:**
```yaml
- action: output
  name: siem-output
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.HASH }}'
```

### Resolution Steps

#### Quick Fix: Switch to Detection Stream

**Immediate action:**
1. Navigate to Outputs
2. Edit primary output
3. Change `stream: event` to `stream: detection`
4. Save

**Result:** Immediate 90%+ reduction

#### Medium-Term: Migrate to GCP Same-Region

**Steps:**
1. Create GCS bucket in same region as datacenter
2. Create new output:
   ```yaml
   type: gcs
   bucket: security-telemetry
   region: us-central1
   stream: event
   ```
3. Test for 24 hours
4. If successful, remove old output
5. Set up export from GCS to final destination

**Result:** Zero LimaCharlie output costs

#### Long-Term: Implement Tailored Outputs

**Strategy:**
1. Use `stream: tailored`
2. Create D&R rules for selective forwarding
3. Forward only high-value events

**Example:**
```yaml
# Only forward from VIP endpoints
detect:
  event: NEW_PROCESS
  op: is tagged
  tag: vip
respond:
  - action: output
    name: tailored-output
    suppression:
      max_count: 1
      period: 5m
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.HASH }}'
```

### Verification

**After implementing fixes:**
1. Wait 24 hours
2. Check Billing & Usage
3. Verify output_data reduced
4. Monitor for 1 week to confirm sustained reduction

**Expected results:**
- output_data should drop by 90%+ within 24 hours
- Cost reduction visible in next billing period

### Prevention

1. **Default to detection stream** for all SIEM outputs
2. **Use GCP same-region** whenever possible
3. **Add usage alerts** for output_data threshold
4. **Monthly review** of output configurations
5. **Suppression on output actions** in D&R rules

---

## Expensive Query Costs

### Symptom

- High query_events usage
- Queries taking a long time to complete
- Frequent "query too expensive" warnings

### Diagnosis Steps

#### Step 1: Identify Expensive Queries

**Via Web UI:**
1. Navigate to Telemetry → Historical Query
2. Note the "At most" cost estimation before running
3. If very high (>10M events), query needs optimization

**Check recent queries:**
- Review query history
- Identify patterns in expensive queries
- Note common issues (long time ranges, no filters)

#### Step 2: Analyze Query Structure

**Look for:**
- Long time ranges (>7 days)
- No platform filters
- No event type specification
- Wildcard field searches (`event/*`)
- No aggregation

### Common Causes

#### Cause 1: Excessively Long Time Range

**Problem:**
```
-30d | NEW_PROCESS | event/FILE_PATH contains "malware"
```
- Evaluating 30 days of data
- Millions of unnecessary events scanned

**Solution:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware"
```
- Reduce to smallest time range needed
- Add platform filter
- **Impact:** 30-60x cost reduction

#### Cause 2: No Event Type Filter

**Problem:**
```
-24h | * | event/FILE_PATH contains "suspicious"
```
- Scanning ALL event types
- Most don't have FILE_PATH field

**Solution:**
```
-24h | NEW_PROCESS | event/FILE_PATH contains "suspicious"
```
- Specify event type
- **Impact:** 10-50x cost reduction

#### Cause 3: Wildcard Field Searches

**Problem:**
```
-24h | NEW_PROCESS | event/* contains "malware"
```
- Searching all event fields
- Very inefficient

**Solution:**
```
-24h | NEW_PROCESS | event/FILE_PATH contains "malware" or event/COMMAND_LINE contains "malware"
```
- Target specific fields
- **Impact:** 30-50% cost reduction

#### Cause 4: No Platform Filter

**Problem:**
```
-24h | NEW_PROCESS | event/FILE_PATH contains "cmd.exe"
```
- Searching all platforms
- cmd.exe only on Windows

**Solution:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "cmd.exe"
```
- Add platform filter early
- **Impact:** 2-5x cost reduction

### Resolution Steps

#### Quick Fix: Optimize Current Query

**Apply this template:**
```
-<shortest_time_range> | plat == <platform> | <EVENT_TYPE> | event/<specific_field> <operator> "<value>"
```

**Example transformation:**
```
# Before
-7d | * | event/* contains "powershell"

# After
-4h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell"
```

#### Add Aggregation

**Instead of:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "suspicious"
```

**Use:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "suspicious" |
  event/FILE_PATH as path
  routing/hostname as host
  COUNT(event) as count
  GROUP BY(path host)
  ORDER BY(count DESC)
  LIMIT 100
```

**Benefits:**
- Same events evaluated
- Much smaller result set
- Easier to analyze
- Faster execution

#### Create Saved Searches

**For frequent queries:**
1. Optimize the query
2. Save as named search
3. Share with team
4. Document optimization rationale

### Verification

**Test optimized query:**
1. Note "At most" cost estimate
2. Compare to original
3. Verify results are equivalent
4. Measure execution time improvement

**Expected improvement:**
- 10-100x cost reduction
- 2-10x faster execution
- Same or better results

### Prevention

1. **Default to 4-hour time ranges** for investigations
2. **Always specify platform** when relevant
3. **Always specify event type**
4. **Use specific field paths** (no wildcards)
5. **Aggregate results** with GROUP BY
6. **Create query templates** for common investigations
7. **Train team** on optimization techniques
8. **Set usage alerts** for query_events threshold

### Query Optimization Checklist

Before running any query, verify:
- [ ] Smallest time range needed
- [ ] Platform filter applied
- [ ] Event type specified
- [ ] Specific field paths (no `event/*`)
- [ ] Simple operators preferred over regex
- [ ] Aggregation with GROUP BY
- [ ] LIMIT on results
- [ ] Cost estimate reviewed

---

## Quota Waste Issues

### Symptom

- Paying for sensors that aren't active
- High percentage of offline sensors
- Quota utilization seems inefficient

### Diagnosis Steps

#### Step 1: Review Sensor List

**Via Web UI:**
1. Navigate to Sensors
2. Sort by "Last Seen"
3. Identify sensors offline >30 days

**Count stale sensors:**
- Offline 1-7 days: Potentially ephemeral
- Offline 7-30 days: Likely abandoned
- Offline >30 days: Definitely stale

#### Step 2: Analyze Sensor Tags

**Group stale sensors by tag:**
- Cloud VMs: High churn expected
- Development: Often abandoned
- Production: Should be rare

#### Step 3: Calculate Waste

**Formula:**
```
Wasted quota = (Stale sensors / Total quota) × 100%
Wasted cost = Stale sensors × Cost per sensor
```

**Example:**
- Total quota: 500
- Stale sensors: 100
- Waste: 20%
- Cost per sensor: $1/month
- Wasted cost: $100/month = $1,200/year

### Common Causes

#### Cause 1: Cloud VM Auto-Scaling

**Problem:**
- Auto-scaling creates new instances
- Each gets unique sensor ID
- Old instances removed but sensors remain

**Solution:**
Enable sensor culling with short TTL:
```json
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```

#### Cause 2: Development Environment Sprawl

**Problem:**
- Developers create test VMs
- VMs destroyed but sensors not removed
- Accumulates over time

**Solution:**
```json
{
  "action": "add_rule",
  "name": "cull-dev-systems",
  "tag": "development",
  "ttl": 14
}
```

#### Cause 3: Decommissioned Systems

**Problem:**
- Production servers decommissioned
- Sensors not manually removed

**Solution:**
```json
{
  "action": "add_rule",
  "name": "cull-old-production",
  "tag": "production",
  "ttl": 90
}
```

#### Cause 4: No Sensor Culling Enabled

**Problem:**
- Sensor culling extension not enabled
- Manual cleanup required

**Solution:**
1. Navigate to Add-ons → Extensions
2. Subscribe to "Sensor Cull"
3. Create appropriate cull rules
4. Run ad-hoc cleanup first

### Resolution Steps

#### Immediate: Manual Cleanup

**For urgent quota relief:**
1. Navigate to Sensors
2. Sort by "Last Seen"
3. Manually delete sensors offline >90 days
4. Verify they're not critical systems first

**Caution:** Only delete sensors you're certain are stale.

#### Short-Term: Enable Sensor Culling

**Steps:**
1. Subscribe to Sensor Cull extension
2. Create conservative cull rules initially
3. Run ad-hoc: `{"action": "run"}`
4. Review culled sensors
5. Adjust TTLs if needed

**Start conservative:**
- Cloud VMs: 7 days (reduce to 3 after validation)
- Development: 30 days (reduce to 14)
- Production: 180 days (reduce to 90)

#### Long-Term: Proper Tagging Strategy

**Implement at enrollment:**
1. Create installation keys with tags:
   - `cloud-vm` for ephemeral instances
   - `development` for test systems
   - `production` for stable infrastructure
   - `vip` for critical systems (never cull)

2. Use tags in cull rules
3. Different TTLs per deployment type

### Verification

**After implementing culling:**
1. Wait 24-48 hours for first run
2. Check culled sensor detections (if monitoring enabled)
3. Review sensor count reduction
4. Verify no critical systems culled

**Monitor for 30 days:**
- Track sensor count trends
- Ensure active sensors not accidentally culled
- Adjust TTLs based on patterns

### Prevention

1. **Tag sensors at enrollment**
2. **Enable sensor culling** from day one
3. **Appropriate TTLs** per deployment type
4. **Exclude critical systems** (vip tag)
5. **Monthly quota reviews**
6. **Monitor culling activity**

### Sensor Culling Best Practices

| Deployment | TTL | Monitoring |
|-----------|-----|------------|
| Cloud VMs | 1-3 days | Daily |
| Containers | 1 day | Daily |
| Dev VMs | 7-14 days | Weekly |
| Workstations | 60-90 days | Monthly |
| Servers | 90-180 days | Monthly |
| VIP | Never | N/A |

---

## Detection Noise Problems

### Symptom

- Overwhelming number of detections
- Mostly duplicate alerts
- Analyst alert fatigue
- SIEM overwhelmed

### Diagnosis Steps

#### Step 1: Identify Noisy Rules

**Via Web UI:**
1. Navigate to Detections
2. Sort by detection name
3. Group by 24-hour periods
4. Identify highest-volume rules

**Metrics to collect:**
- Detections per day
- Unique vs. duplicate ratio
- False positive rate

#### Step 2: Analyze Detection Patterns

**For top noisy rule:**
- How many unique values? (hashes, domains, IPs)
- How many detections per unique value?
- Are these true positives or false positives?
- Is every occurrence meaningful?

#### Step 3: Review Rule Configuration

**Check for:**
- No suppression configured
- No threshold activation
- No false positive filtering
- Too broad detection logic

### Common Causes

#### Cause 1: No Suppression

**Problem:**
```yaml
- action: report
  name: suspicious-process
# Alerts on EVERY occurrence
```

**Solution:**
```yaml
- action: report
  name: suspicious-process
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.HASH }}'
      - 'suspicious-process'
```

**Impact:** 95%+ reduction for duplicate detections

#### Cause 2: No Threshold

**Problem:**
- Single occurrence triggers alert
- Transient anomalies create noise

**Solution:**
```yaml
suppression:
  min_count: 3      # Require 3 occurrences
  max_count: 3      # Then alert once
  period: 1h
```

**Impact:** Filters one-off anomalies

#### Cause 3: Known False Positives

**Problem:**
- Legitimate tool flagged as suspicious
- Generates thousands of alerts

**Solution:**
Create false positive rule:
```yaml
detect:
  target: detection
  event: detection
  op: and
  rules:
    - op: is
      path: detect/cat
      value: suspicious-process-detected
    - op: is
      path: detect/detect/event/HASH
      value: a1b2c3d4...  # Known benign hash
respond:
  # No action = suppressed
```

#### Cause 4: Overly Broad Detection Logic

**Problem:**
```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: temp
# Matches any process with "temp" in path
```

**Solution:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: matches
      path: event/FILE_PATH
      re: '\\temp\\suspicious\.exe$'
      case sensitive: false
# Much more specific
```

### Resolution Steps

#### Step 1: Add Hash-Based Suppression

**For process-based detections:**
```yaml
suppression:
  max_count: 1
  period: 24h
  is_global: true
  keys:
    - '{{ .event.HASH }}'
    - 'detection-name'
```

**For domain-based detections:**
```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: true
  keys:
    - '{{ .event.DOMAIN_NAME }}'
    - 'detection-name'
```

#### Step 2: Implement Threshold Activation

**For behavioral detections:**
```yaml
suppression:
  min_count: 5
  max_count: 5
  period: 5m
  is_global: false
  keys:
    - '{{ .routing.sid }}'
    - 'detection-name'
```

**Use cases:**
- Failed login attempts
- Port scans
- Brute force attempts
- Repeated suspicious behavior

#### Step 3: Create FP Rules

**Process:**
1. Identify false positive patterns
2. Create detection-target rule
3. Filter specific conditions
4. Leave respond section empty (suppresses)

**Example for known benign:**
```yaml
detect:
  target: detection
  event: detection
  op: and
  rules:
    - op: is
      path: detect/cat
      value: malware-detected
    - op: is
      path: detect/routing/hostname
      value: dev-server-01
respond:
  # Suppressed for this specific host
```

#### Step 4: Refine Detection Logic

**Make detections more specific:**
- Add platform filters
- Narrow file path matches
- Include parent process context
- Add user context
- Consider time-based rules

### Verification

**After optimization:**
1. Wait 24 hours
2. Compare detection volume
3. Verify true positives still detected
4. Check false positive rate

**Expected results:**
- 50-95% detection volume reduction
- Maintained or improved detection quality
- Better signal-to-noise ratio

### Prevention

1. **Always include suppression** in new rules
2. **Use threshold activation** for behavioral detections
3. **Create FP rules** as needed
4. **Regular rule audits** (quarterly)
5. **Test rules** before production deployment
6. **Monitor detection volume** trends

---

## Sensor Culling Issues

### Symptom

- Sensors not being culled as expected
- Wrong sensors being culled
- Cull rules not running

### Diagnosis Steps

#### Step 1: Verify Extension Enabled

**Via Web UI:**
1. Navigate to Add-ons → Extensions
2. Confirm "Sensor Cull" shows as subscribed
3. Check extension status

#### Step 2: Review Cull Rules

**Via extension interface:**
```json
{
  "action": "get_rules"
}
```

**Verify:**
- Rules exist
- Tags match sensor tags
- TTLs are appropriate

#### Step 3: Check Sensor Tags

**For sensors that should be culled:**
1. Navigate to Sensors
2. Select sensor
3. View tags
4. Confirm tag matches cull rule

### Common Issues

#### Issue 1: Sensor Missing Expected Tag

**Problem:**
- Cull rule targets tag "cloud-vm"
- Sensor has tag "cloud" instead
- Sensor never culled

**Solution:**
```json
{
  "action": "del_rule",
  "name": "cull-cloud-vms"
}
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud",
  "ttl": 3
}
```

Or retag sensors:
- Update installation key to add correct tag
- Or manually tag existing sensors

#### Issue 2: TTL Too Long

**Problem:**
```json
{
  "tag": "cloud-vm",
  "ttl": 30
}
```
- Cloud VMs offline for 29 days not culled
- TTL too conservative

**Solution:**
```json
{
  "action": "del_rule",
  "name": "cull-cloud-vms"
}
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```

#### Issue 3: Critical Sensor Accidentally Culled

**Problem:**
- Production server temporarily offline
- Culled by aggressive rule

**Prevention:**
1. Tag critical systems with "vip"
2. Don't create cull rules for "vip" tag
3. Use long TTLs for production (90+ days)

**Recovery:**
- Sensor will re-enroll on next connection
- Same SID if using persistent installation

#### Issue 4: Extension Not Running

**Problem:**
- Extension subscribed but not active
- Rules created but no culling happening

**Solution:**
1. Run ad-hoc cull:
   ```json
   {
     "action": "run"
   }
   ```
2. Wait for results
3. If still not working, contact support

### Resolution Steps

#### Verify Tag Consistency

**Audit:**
1. List all cull rules
2. List all sensor tags
3. Ensure tags match

**Fix mismatches:**
- Update installation keys
- Retag sensors as needed
- Update cull rules

#### Test with Ad-Hoc Run

**Process:**
1. Create or update rule
2. Run: `{"action": "run"}`
3. Wait 5-10 minutes
4. Check sensor count
5. Review culled sensors (if monitoring enabled)

#### Implement Cull Monitoring

**Create detection rule:**
```yaml
detect:
  target: deployment
  event: deleted_sensor
  op: exists
  path: routing/event_type
respond:
  - action: report
    name: sensor-culled
    metadata:
      sid: "{{ .routing.sid }}"
      hostname: "{{ .routing.hostname }}"
      tags: "{{ .routing.tags }}"
      offline_days: "{{ .event.denied_for }}"
```

**Benefits:**
- Visibility into culling activity
- Catch unexpected culls
- Audit trail

### Verification

**After fixing:**
1. Run ad-hoc cull
2. Verify expected sensors culled
3. Verify critical sensors NOT culled
4. Monitor for 7 days

**Expected behavior:**
- Stale sensors removed daily
- Active sensors untouched
- Critical systems never culled

### Best Practices

1. **Start conservative** with TTLs
2. **Test with ad-hoc run** before automating
3. **Monitor culling activity**
4. **Exclude critical systems**
5. **Document cull rules** and rationale
6. **Regular audits** of culled sensors

---

## Suppression Not Working

### Symptom

- Expected suppression not occurring
- Actions still executing too frequently
- Suppression keys not matching

### Diagnosis Steps

#### Step 1: Verify Suppression Syntax

**Check for:**
```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: true
  keys:
    - '{{ .event.HASH }}'
```

**Common syntax errors:**
- Missing keys
- Wrong template syntax
- Invalid time format
- Missing is_global

#### Step 2: Test Key Values

**Add logging action:**
```yaml
- action: report
  name: test-suppression-keys
  detect_data:
    key1: '{{ .event.HASH }}'
    key2: '{{ .routing.sid }}'
# Check detection to see actual key values
```

#### Step 3: Review Suppression Period

**Verify:**
- Period appropriate for use case
- Time format correct (h, m, s)
- Period hasn't expired

### Common Issues

#### Issue 1: Dynamic Keys Not Resolving

**Problem:**
```yaml
keys:
  - '{{ .event.FILE_PATH }}'
```
- Field doesn't exist in all events
- Results in empty key
- No suppression applied

**Solution:**
```yaml
keys:
  - '{{ .event.FILE_PATH | default "unknown" }}'
  - 'detection-name'
```

Or use field that always exists:
```yaml
keys:
  - '{{ .event.HASH }}'
  - 'detection-name'
```

#### Issue 2: Keys Too Specific

**Problem:**
```yaml
keys:
  - '{{ .event.FILE_PATH }}'
  - '{{ .routing.sid }}'
  - '{{ .routing.event_time }}'
```
- Every event has different timestamp
- Keys never match
- No suppression occurs

**Solution:**
```yaml
keys:
  - '{{ .event.HASH }}'
  - 'detection-name'
# Remove timestamp - too specific
```

#### Issue 3: Wrong Scope

**Problem:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .event.HASH }}'
```
- Per-sensor suppression
- Same hash on different sensors not suppressed

**Solution:**
```yaml
suppression:
  is_global: true  # Suppress org-wide
  keys:
    - '{{ .event.HASH }}'
```

#### Issue 4: Period Too Short

**Problem:**
```yaml
suppression:
  period: 1m
```
- 1 minute suppression
- Actions still occur frequently

**Solution:**
```yaml
suppression:
  period: 1h  # or 24h
```

### Resolution Steps

#### Test Suppression Logic

**Create test rule:**
```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: notepad.exe
respond:
  - action: report
    name: test-suppression
    detect_data:
      hash: '{{ .event.HASH }}'
      sid: '{{ .routing.sid }}'
    suppression:
      max_count: 1
      period: 1h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
        - 'test-suppression'
```

**Trigger multiple times:**
1. Launch notepad.exe repeatedly
2. Check detections
3. Should see only 1 detection per hour

#### Verify Key Uniqueness

**Log keys:**
```yaml
- action: report
  name: key-logging
  detect_data:
    key_hash: '{{ .event.HASH }}'
    key_path: '{{ .event.FILE_PATH }}'
# Review actual values in detections
```

#### Use Static Identifier

**Always include:**
```yaml
keys:
  - '{{ .event.HASH }}'
  - 'detection-name'  # Static identifier
```

**Benefits:**
- Clear suppression intent
- Easier to debug
- Prevents conflicts with other rules

### Verification

**After fixing:**
1. Trigger detection multiple times
2. Verify suppression occurs
3. Check period respected
4. Confirm scope correct

### Prevention

1. **Always include static identifier** in keys
2. **Test suppression** before production
3. **Use fields that always exist**
4. **Document suppression logic**
5. **Choose appropriate period**
6. **Consider scope** (global vs. per-sensor)

---

## Performance Mode Issues

### Symptom

- Performance mode not applying to sensors
- Sensors stuck in wrong mode
- Mode changes not taking effect

### Diagnosis

#### Step 1: Verify Command Syntax

**Correct command:**
```
set_performance_mode --mode low
set_performance_mode --mode normal
set_performance_mode --mode high
```

**Check for:**
- Correct flag: `--mode` (not `-mode`)
- Valid values: low, normal, high
- No typos

#### Step 2: Check D&R Rule

**If automating via D&R:**
```yaml
detect:
  target: deployment
  event: enrollment
  op: is tagged
  tag: vip
respond:
  - action: task
    command: set_performance_mode --mode high
```

**Verify:**
- Rule targets enrollment events
- Tag matches sensor tags
- Command syntax correct

#### Step 3: Verify Suppression

**Common issue:**
```yaml
respond:
  - action: task
    command: set_performance_mode --mode high
    suppression:
      max_count: 1
      period: 24h
      keys:
        - '{{ .routing.sid }}'
```

**Check:**
- Suppression may prevent reapplication
- If sensor reboots, mode may reset

### Resolution

#### Manual Mode Setting

**For immediate fix:**
1. Navigate to Sensors
2. Select sensor
3. Tasks → Send Command
4. Enter: `set_performance_mode --mode high`
5. Execute

#### Automated via D&R

**Best practice:**
```yaml
detect:
  target: deployment
  event: enrollment
  op: is tagged
  tag: vip
respond:
  - action: task
    command: set_performance_mode --mode high
    suppression:
      max_count: 1
      period: 24h
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - 'performance-mode-set'
```

**Reapplication:**
- Mode set once per sensor per 24h
- On enrollment (new sensors)
- On reconnection after suppression expires

### Verification

**Check mode:**
1. Sensor event stream shows mode changes
2. Monitor event volume changes
3. CPU/memory usage reflects mode

**Expected impact:**
- Low: Minimal events, low resource usage
- Normal: Standard events, moderate resources
- High: Maximum events, higher resources

---

## Usage Alerts Not Firing

### Symptom

- Usage exceeds threshold but no alert
- Alert configured but not triggering
- Missing expected alert detections

### Diagnosis

#### Step 1: Verify Extension Enabled

**Check:**
1. Navigate to Add-ons → Extensions
2. Confirm "Usage Alerts" subscribed
3. Extension status active

#### Step 2: Review Alert Configuration

**Via Web UI or IaC:**
```yaml
usage_alert_rules:
  - enabled: true
    limit: 1073741824
    name: Output data threshold
    sku: output_data
    timeframe: 43200
```

**Verify:**
- enabled: true
- Correct SKU
- Appropriate limit
- Timeframe in minutes

#### Step 3: Check Current Usage

**Compare:**
- Alert limit: 1GB (1073741824 bytes)
- Current usage: ?
- Has threshold been reached?

### Common Issues

#### Issue 1: Limit Not Reached

**Problem:**
- Alert set for 100GB
- Current usage: 50GB
- Alert won't fire until threshold exceeded

**Solution:**
- Adjust limit if testing
- Or wait for usage to reach threshold

#### Issue 2: Wrong SKU

**Problem:**
```yaml
sku: output_bytes  # Wrong
```

**Solution:**
```yaml
sku: output_data  # Correct
```

**Valid SKUs:**
- `output_data`
- `query_events`
- `sensor_events`
- `artifact_quota`
- `ext-*` (extension-specific)

#### Issue 3: Timeframe Too Long

**Problem:**
```yaml
timeframe: 43200  # 30 days
```
- Usage resets before threshold reached
- Never accumulates enough

**Solution:**
```yaml
timeframe: 10080  # 7 days
# Or adjust limit lower
```

#### Issue 4: Not Synced

**Problem:**
- Rules created but not synced
- Extension not generating D&R rules

**Solution:**
1. Click "Sync Usage Alert Rules" in extension UI
2. Wait a few minutes
3. Check for generated D&R rules

### Resolution

#### Sync Alert Rules

**Via Web UI:**
1. Navigate to Usage Alerts extension
2. Click "Sync Usage Alert Rules"
3. Confirm sync successful

**Verify generated D&R rules:**
1. Navigate to D&R Rules
2. Look for rules with "Usage alert" prefix
3. Verify rule matches configuration

#### Test with Lower Threshold

**For testing:**
```yaml
- enabled: true
  limit: 100000  # Very low limit
  name: Test alert
  sku: output_data
  timeframe: 60  # 1 hour
```

**Generate usage:**
- Create output traffic
- Wait for alert
- Verify firing

**Then adjust:**
- Set appropriate threshold
- Extend timeframe
- Resync

### Verification

**After fixes:**
1. Confirm extension enabled
2. Verify rules synced
3. Check generated D&R rules
4. Monitor for alerts when threshold reached

**Expected behavior:**
- Alert fires when limit exceeded
- Detection created with usage details
- Alert respects timeframe

---

## GCP Output Issues

### Symptom

- GCP output not free as expected
- Output failing to GCS/Pub/Sub
- Still being charged for "free" outputs

### Diagnosis

#### Step 1: Verify Region Matching

**Check datacenter:**
1. Note your LimaCharlie datacenter region
2. Verify GCP resource region matches exactly

**Required matches:**
| LC Datacenter | GCP Region |
|---------------|------------|
| USA | us-central1 |
| Europe | europe-west4 |
| Canada | northamerica-northeast1 |

#### Step 2: Verify Output Configuration

**Check output:**
```yaml
type: gcs
bucket: my-bucket
region: us-central1  # Must match datacenter
```

**Common errors:**
- Wrong region (us-west1 instead of us-central1)
- Missing region specification
- Typo in region name

#### Step 3: Check Billing

**Verify:**
- Look for output_data charges
- If still charged, region mismatch likely
- GCP region must be EXACTLY correct

### Common Issues

#### Issue 1: Wrong GCP Region

**Problem:**
```yaml
region: us-west1  # Wrong - not us-central1
```
- Not the free region
- Charged for output

**Solution:**
```yaml
region: us-central1  # Correct for USA datacenter
```

#### Issue 2: Wrong LimaCharlie Datacenter

**Problem:**
- Organization in USA datacenter
- Using europe-west4 in GCP
- Not same region = charged

**Solution:**
- Can't change org datacenter after creation
- Must use us-central1 for USA org
- Or create new org in Europe datacenter

#### Issue 3: Wrong Output Mechanism

**Problem:**
```yaml
type: s3  # AWS S3 - always charged
```

**Solution:**
```yaml
type: gcs  # Google Cloud Storage - free if same region
```

**Free mechanisms:**
- gcs (Google Cloud Storage)
- pubsub (Google Pub/Sub)
- bigquery (Google BigQuery)

#### Issue 4: Authentication Failure

**Problem:**
- GCP output configured correctly
- But failing to deliver
- Authentication error

**Solution:**
- Verify GCP credentials in LimaCharlie
- Check IAM permissions on GCP side
- Ensure service account has write access

### Resolution

#### Update to Correct Region

**Steps:**
1. Verify your LC datacenter region
2. Update output configuration:
   ```yaml
   type: gcs
   bucket: security-logs
   region: us-central1  # Match datacenter
   ```
3. Test output
4. Monitor billing to confirm free

#### Create Resources in Correct Region

**GCS Bucket:**
```bash
gsutil mb -l us-central1 gs://security-logs
```

**Pub/Sub Topic:**
```bash
gcloud pubsub topics create security-events --region=us-central1
```

### Verification

**After fixing:**
1. Wait 24-48 hours
2. Check Billing & Usage
3. Verify output_data = 0 or minimal
4. Confirm events flowing to GCP

**Expected:**
- Zero LimaCharlie output charges
- All events in GCS/Pub/Sub
- Billing shows output_data but $0 cost

---

## Query Performance Problems

### Symptom

- Queries timing out
- Very slow query execution
- "Query too complex" errors

### Diagnosis

See "Expensive Query Costs" section above for detailed diagnosis and resolution.

**Quick checks:**
- Time range >7 days?
- No platform filter?
- No event type specified?
- Wildcard field searches?
- No aggregation?

**Quick fixes:**
- Reduce time range
- Add platform filter
- Specify event type
- Use specific field paths
- Add aggregation

---

## Getting Help

If issues persist after trying these troubleshooting steps:

### Community Resources

- LimaCharlie Community Slack
- GitHub Discussions
- Documentation: https://doc.limacharlie.io

### Support Channels

**For subscribers:**
- Email: support@limacharlie.io
- In-app support chat
- Slack support channel (for enterprise)

**Information to provide:**
- Organization ID
- Specific error messages
- Steps to reproduce
- Expected vs. actual behavior
- Relevant configuration (rules, outputs, etc.)

---

[← Back to SKILL.md](./SKILL.md) | [View Reference →](./REFERENCE.md) | [View Examples →](./EXAMPLES.md)
