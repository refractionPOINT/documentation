# Performance Optimizer - Examples

Real-world optimization scenarios with complete before/after comparisons and cost calculations.

[← Back to SKILL.md](./SKILL.md)

## Table of Contents

1. [Example 1: Reducing Output Costs by 90%](#example-1-reducing-output-costs-by-90)
2. [Example 2: Query Optimization (50x Cost Reduction)](#example-2-query-optimization-50x-cost-reduction)
3. [Example 3: Sensor Culling (20% Quota Reduction)](#example-3-sensor-culling-20-quota-reduction)
4. [Example 4: Rule Optimization (Detection Volume Reduction)](#example-4-rule-optimization-detection-volume-reduction)
5. [Example 5: Comprehensive Organization Optimization](#example-5-comprehensive-organization-optimization)

---

## Example 1: Reducing Output Costs by 90%

### Scenario

- Current: 100GB/month output to Splunk
- Cost: $X/month (based on LimaCharlie pricing)
- Goal: Reduce to <10GB/month

### Initial State

**Output Configuration:**
```yaml
# Output configuration
name: splunk-output
stream: event           # ALL events forwarded
destination: splunk
```

**Metrics:**
- Output volume: 100GB/month
- Events forwarded: ~50 million/month
- Splunk ingestion cost: Additional $Y/month
- LimaCharlie output cost: $X/month

### Analysis

**Problem Identification:**
- Forwarding all events to Splunk
- Most events are not security-relevant
- Splunk also charges for ingestion
- Double cost: LimaCharlie egress + Splunk ingestion

**Cost Drivers:**
- DNS requests: 40% of volume
- Process events: 30% of volume
- Network connections: 20% of volume
- Other events: 10% of volume

### Optimization Steps

#### Step 1: Switch to Detection-Only Forwarding

**New Configuration:**
```yaml
# Output configuration
name: splunk-output
stream: detection       # Only detections forwarded
destination: splunk
```

**Impact:**
- Output volume: 100GB → 5GB (~95% reduction)
- Events forwarded: 50M → 50K detections
- Detections are high-value alerts only

#### Step 2: Add Tailored Output for High-Value Events

**Additional Output:**
```yaml
# Additional output for specific events
name: splunk-high-value
stream: tailored
destination: splunk
```

**D&R Rule for Tailored Forwarding:**
```yaml
# Forward process events from VIP endpoints only
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: vip
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
respond:
  - action: output
    name: splunk-high-value
```

**Impact:**
- Additional volume: ~3GB/month
- Total: 5GB + 3GB = 8GB/month
- Still 92% reduction from baseline

#### Step 3: Alternative - GCP Hub Approach

**Zero-Cost Architecture:**
```yaml
# Route through GCS (same region = FREE)
name: gcs-archive
type: gcs
bucket: security-logs
region: us-central1  # Must match LimaCharlie datacenter

# Then export from GCS to Splunk using GCP tools
# Charged by GCP egress rates instead
```

**Process:**
1. LimaCharlie → GCS (FREE)
2. GCS → Splunk via Google Cloud Functions
3. Pay only GCP egress rates (typically lower)

### Results

| Metric | Before | After (Detection-Only) | After (GCP Hub) | Savings |
|--------|--------|------------------------|-----------------|---------|
| Output Volume | 100GB | 8GB | 100GB (free) | 92% / 100% |
| LimaCharlie Cost | $X | $0.08X | $0 | 92% / 100% |
| Splunk Ingestion | 50M events | 50K + targeted | Via GCP | Major reduction |
| Total Cost | $X + $Y | $0.08X + $0.05Y | GCP costs only | ~90%+ |

### Key Learnings

1. **Detection stream is sufficient** for most SIEM use cases
2. **Tailored outputs** provide flexibility for high-value events
3. **GCP same-region** eliminates LimaCharlie output costs entirely
4. **Splunk benefits too** from reduced ingestion volume
5. **Security coverage maintained** - all alerts still forwarded

---

## Example 2: Query Optimization (50x Cost Reduction)

### Scenario

- Frequent threat hunting queries
- Average query: $5 cost (10M events evaluated)
- Goal: Reduce query costs by 90%

### Initial Query (Bad)

```
-7d | * | event/* contains "malware.exe"
```

**Characteristics:**
- Time range: 7 days
- Event types: ALL (wildcard)
- Field: Wildcard (`event/*`)
- Platform: All platforms

**Performance:**
- Events in range: 100M total events
- Events evaluated: 100M (all events scanned)
- Estimated cost: $50
- Execution time: 45 seconds

### Analysis

**Inefficiencies Identified:**
1. **Time range too broad**: 7 days when recent activity is target
2. **No event type filter**: Scanning all event types
3. **No platform filter**: Including Linux/macOS (no malware.exe)
4. **Wildcard field search**: Scanning all event fields
5. **No aggregation**: Returning all matching events

### Optimization Process

#### Step 1: Reduce Time Range

```
-24h | * | event/* contains "malware.exe"
```

**Impact:**
- Events evaluated: 100M → 14M
- Cost: $50 → $7
- **Reduction: 7x**
- Execution time: 8 seconds

**Rationale:** Most investigations focus on recent activity.

#### Step 2: Specify Event Type

```
-24h | NEW_PROCESS | event/* contains "malware.exe"
```

**Impact:**
- Events evaluated: 14M → 2M (only process events)
- Cost: $7 → $1
- **Reduction: 50x from original**
- Execution time: 2 seconds

**Rationale:** Filenames only appear in process events.

#### Step 3: Specify Field Path

```
-24h | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```

**Impact:**
- Events evaluated: 2M (same)
- Cost: $1 (same, but faster execution)
- **Total Reduction: 50x**
- Execution time: 1.5 seconds

**Rationale:** No need to scan all fields, just FILE_PATH.

#### Step 4: Add Platform Filter

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```

**Impact:**
- Events evaluated: 2M → 1.5M
- Cost: $1 → $0.75
- **Total Reduction: 66x**
- Execution time: 1 second

**Rationale:** malware.exe only exists on Windows.

#### Step 5: Use Aggregation

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe" |
  event/FILE_PATH as path
  routing/hostname as host
  COUNT(event) as count
  GROUP BY(path host)
  ORDER BY(count DESC)
  LIMIT 100
```

**Impact:**
- Events evaluated: 1.5M (same)
- Cost: $0.75 (same)
- Result size: Small summary instead of all events
- **Total Reduction: 66x + much faster to analyze**
- Execution time: 1 second

**Rationale:** Summary is more useful than thousands of individual events.

### Optimization Comparison

| Version | Time Range | Filters | Events Evaluated | Cost | Time | Reduction |
|---------|-----------|---------|------------------|------|------|-----------|
| Original | 7 days | None | 100M | $50 | 45s | Baseline |
| Step 1 | 24 hours | None | 14M | $7 | 8s | 7x |
| Step 2 | 24 hours | Event type | 2M | $1 | 2s | 50x |
| Step 3 | 24 hours | Event + field | 2M | $1 | 1.5s | 50x |
| Step 4 | 24 hours | Event + field + platform | 1.5M | $0.75 | 1s | 66x |
| Step 5 | 24 hours | All + aggregation | 1.5M | $0.75 | 1s | 66x |

### Final Query Template

**Optimized pattern for threat hunting:**
```
-<small_timerange> | plat == <platform> | <EVENT_TYPE> | event/<FIELD> <operator> "<value>" |
  event/<field1> as name1
  routing/<field2> as name2
  COUNT(event) as count
  GROUP BY(name1 name2)
  ORDER BY(count DESC)
  LIMIT <reasonable_number>
```

### Results

**Cost Savings:**
- Original: $50 per query
- Optimized: $0.75 per query
- **Savings: 98.5% per query**

**If 100 queries per month:**
- Original: $5,000/month
- Optimized: $75/month
- **Annual savings: ~$59,000**

**Additional Benefits:**
- Faster execution (45s → 1s)
- Easier to analyze results (summary vs. raw events)
- Better query performance for all users
- Reduced platform load

### Query Optimization Checklist

For any query, apply these optimizations:

- [ ] Smallest time range needed (prefer hours over days)
- [ ] Platform filter (`plat == windows/linux/macos`)
- [ ] Specific event type (`NEW_PROCESS`, `DNS_REQUEST`, etc.)
- [ ] Exact field paths (avoid `event/*`)
- [ ] Use simple operators when possible (avoid regex)
- [ ] Aggregate results (`COUNT`, `GROUP BY`)
- [ ] Limit result size (`LIMIT`)
- [ ] Test on small time range first

---

## Example 3: Sensor Culling (20% Quota Reduction)

### Scenario

- Current quota: 500 sensors
- Active sensors: ~400 consistently
- Stale sensors: ~100 (cloud VMs, dev systems)
- Monthly cost: $500 (example pricing)
- Goal: Reduce quota waste

### Initial State

**Sensor Breakdown:**
- Windows servers (production): 150 active
- Linux servers (production): 100 active
- Windows workstations: 80 active
- macOS laptops: 70 active
- Cloud VMs (AWS/Azure): 60 stale, 40 active
- Development VMs: 30 stale, 10 active
- **Total quota: 500**
- **Active: 450, Stale: 50** (realized after investigation)

**Cost Analysis:**
- Quota cost: $500/month (example)
- Wasted on stale: $50/month
- Annual waste: $600/year

### Analysis

**Stale Sensor Identification:**

Using web UI sensor list:
1. Sort by "Last Seen"
2. Identify sensors offline >30 days
3. Categorize by tag:
   - `cloud-vm`: 60 sensors (last seen: 1-30 days ago)
   - `development`: 30 sensors (last seen: 7-60 days ago)
   - `production`: 10 sensors (last seen: 90+ days ago, decommissioned)

**Root Causes:**
- Cloud VMs: Auto-scaling creates new sensors, old ones never removed
- Dev VMs: Developers create test environments, forget to delete
- Production: Servers decommissioned but sensors not removed manually

### Implementation

#### Step 1: Enable Sensor Cull Extension

**Via Web UI:**
1. Navigate to Add-ons → Extensions
2. Search "Sensor Cull"
3. Click Subscribe
4. Navigate to Sensors → Sensor Cull

#### Step 2: Create Cull Rules

**Cloud VMs (Ephemeral):**
```json
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```
- TTL: 3 days (appropriate for auto-scaling)
- Rationale: Cloud VMs scale down rapidly

**Development Systems:**
```json
{
  "action": "add_rule",
  "name": "cull-dev-systems",
  "tag": "development",
  "ttl": 14
}
```
- TTL: 14 days (2 weeks)
- Rationale: Dev VMs may be temporarily offline

**Production Servers:**
```json
{
  "action": "add_rule",
  "name": "cull-old-production",
  "tag": "production",
  "ttl": 90
}
```
- TTL: 90 days (3 months)
- Rationale: Conservative for production, catches decommissioned servers

**VIP Endpoints:**
- No cull rule created
- Critical systems never automatically removed

#### Step 3: Test with Ad-Hoc Run

**Before automating, run manually:**
```json
{
  "action": "run"
}
```

**Results of test run:**
- Cloud VMs culled: 60 sensors
- Dev systems culled: 30 sensors
- Production culled: 10 sensors (verified decommissioned)
- **Total culled: 100 sensors**

#### Step 4: Monitor Culling Activity

**Create D&R rule to track deletions:**
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
      denied_for: "{{ .event.denied_for }}"
```

**Result:** Detection created each time sensor is culled for visibility.

#### Step 5: Reduce Quota

**After initial cleanup:**
- Old quota: 500
- Active sensors: 400
- Buffer: 25 (for growth)
- New quota: 425

**After optimization stabilizes (30 days):**
- Consistent active: 400
- Buffer: 20
- Final quota: 420

### Results

**Immediate Impact:**
- 100 stale sensors removed
- Quota reduced: 500 → 420
- Saved quota slots: 80

**Cost Savings:**
- Old cost: $500/month
- New cost: $420/month
- **Savings: $80/month = $960/year**
- **ROI: Immediate**

**Ongoing Benefits:**
- Automatic culling prevents re-accumulation
- Cleaner sensor list
- Easier to identify active systems
- More accurate quota planning

### Sensor Culling by Deployment Type

| Deployment Type | Recommended TTL | Expected Cull Rate | Rationale |
|----------------|-----------------|-------------------|-----------|
| Cloud VMs (auto-scale) | 1-3 days | High (50-70%) | Very ephemeral |
| Docker containers | 1 day | Very high (80%+) | Rapid churn |
| Kubernetes pods | 1 day | Very high (80%+) | Container lifecycle |
| Development VMs | 7-14 days | Medium (30-50%) | Test environments |
| Laptops/workstations | 60-90 days | Low (5-10%) | May be offline |
| Servers (prod) | 90-180 days | Very low (<5%) | Stable infrastructure |
| VIP endpoints | Never | 0% | Critical systems |

### Maintenance Strategy

**Weekly:**
- Review culled sensor detections
- Verify no critical systems accidentally removed

**Monthly:**
- Check quota utilization
- Adjust TTLs if needed based on patterns

**Quarterly:**
- Review all cull rules
- Update tags and rules as infrastructure changes
- Consider quota reduction if consistently under-utilized

### Key Learnings

1. **Tag-based culling** is essential for different lifecycle management
2. **Start conservative** with TTLs, reduce based on patterns
3. **Test before automating** with ad-hoc runs
4. **Monitor culling activity** for unexpected removals
5. **Exclude critical systems** from automatic culling
6. **ROI is immediate** - no downside to enabling sensor culling

---

## Example 4: Rule Optimization (Detection Volume Reduction)

### Scenario

- Rule generating 10,000 detections/day
- Mostly duplicates (same hash, same behavior)
- SIEM overwhelmed with alerts
- Analysts experiencing alert fatigue
- Goal: Reduce noise while maintaining coverage

### Initial State

**Original Rule:**
```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: suspicious.exe
respond:
  - action: report
    name: suspicious-process-detected
  - action: output
    name: siem-output
```

**Characteristics:**
- No suppression
- No threshold
- No false positive filtering
- Alerts on every occurrence

**Metrics:**
- Detections: 10,000/day
- Unique hashes: 50
- False positives: ~30% (legitimate suspicious.exe)
- Average occurrences per hash: 200/day
- SIEM alert volume: Overwhelming
- Analyst time wasted: 4 hours/day triaging

### Analysis

**Detection Breakdown:**
- Same 5 hashes: 70% of detections (7,000/day)
- Next 10 hashes: 20% of detections (2,000/day)
- Remaining 35 hashes: 10% of detections (1,000/day)
- Known false positives: 3,000/day (legitimate internal tool)

**Problems Identified:**
1. No suppression - every occurrence alerts
2. No threshold - single occurrence triggers alert
3. No FP filtering - known benign tool alerting
4. Same hash seen hundreds of times per day
5. SIEM receiving duplicate information

### Optimization Steps

#### Step 1: Add Basic Suppression

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: suspicious.exe
respond:
  - action: report
    name: suspicious-process-detected
    suppression:
      max_count: 1
      period: 1h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
        - 'suspicious-process'
  - action: output
    name: siem-output
```

**Impact:**
- Detection volume: 10,000/day → 240/day (1 per hash per hour)
- **Reduction: 97.6%**
- Coverage maintained: Still detects all unique hashes
- SIEM ingestion: 10K → 240 alerts/day

#### Step 2: Add Threshold Activation

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: suspicious.exe
respond:
  - action: report
    name: suspicious-process-detected
    suppression:
      min_count: 3              # Must occur 3 times
      max_count: 3              # Then alert once
      period: 1h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
        - 'suspicious-process'
  - action: output
    name: siem-output
```

**Impact:**
- Filters out one-off anomalies
- Only alerts on persistent behavior
- Detection volume: 240/day → ~170/day
- **Further reduction: ~30%**
- Higher confidence detections

#### Step 3: Add False Positive Rule

```yaml
# Separate D&R rule to filter known benign
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
      value: a1b2c3d4e5f6...  # Known benign tool hash
respond:
  # No action = detection suppressed
```

**Impact:**
- Removes 3,000 false positives (converted to 125 detections/day suppressed)
- Detection volume: 170/day → ~100/day
- **Reduction from original: 99%**
- Much higher signal-to-noise ratio

#### Step 4: Add Detection Enrichment

```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: suspicious.exe
respond:
  - action: report
    name: suspicious-process-detected
    detect_data:
      file_path: "{{ .event.FILE_PATH }}"
      file_hash: "{{ .event.HASH }}"
      command_line: "{{ .event.COMMAND_LINE }}"
      hostname: "{{ .routing.hostname }}"
      user: "{{ .event.USER_NAME }}"
      parent_process: "{{ .event.PARENT.FILE_PATH }}"
      first_seen: "{{ .routing.event_time }}"
    suppression:
      min_count: 3
      max_count: 3
      period: 1h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
        - 'suspicious-process'
  - action: output
    name: siem-output
```

**Impact:**
- Richer context in each alert
- Analysts spend less time investigating
- Better SIEM correlation
- Same detection volume but more value per alert

### Results Comparison

| Metric | Before | After Step 1 | After Step 2 | After Step 3 | Final |
|--------|--------|--------------|--------------|--------------|-------|
| Detections/day | 10,000 | 240 | 170 | 100 | 100 |
| SIEM alerts | 10,000 | 240 | 170 | 100 | 100 |
| False positives | 3,000 | 70 | 50 | 0 | 0 |
| Analyst time | 4h/day | 30min/day | 20min/day | 15min/day | 15min/day |
| Reduction | - | 97.6% | 98.3% | 99% | 99% |

### Cost and Productivity Impact

**SIEM Costs:**
- Before: 10,000 alerts/day × $0.10/alert = $1,000/day
- After: 100 alerts/day × $0.10/alert = $10/day
- **Savings: $990/day = $29,700/month**

**Analyst Productivity:**
- Before: 4 hours/day triaging noise
- After: 15 minutes/day reviewing high-confidence alerts
- **Time saved: 3.75 hours/day per analyst**
- If 5 analysts: 18.75 hours/day = 2.34 FTE worth of time

**Detection Quality:**
- Signal-to-noise ratio: 7:10 → 10:10 (70% → 100%)
- False positive rate: 30% → 0%
- Mean time to triage: 5 minutes → 1 minute

### Additional Optimization: Time-Based Rules

For even more precision, add time-based filtering:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: suspicious.exe
  case sensitive: false
  times:
    - day_of_week_start: 2     # Monday
      day_of_week_end: 6       # Friday
      time_of_day_start: 2200  # 10 PM
      time_of_day_end: 2359    # 11:59 PM
      tz: America/Los_Angeles
    - day_of_week_start: 1     # Sunday
      day_of_week_end: 1       # Sunday
      time_of_day_start: 0     # All day
      time_of_day_end: 2359
      tz: America/Los_Angeles
respond:
  - action: report
    name: off-hours-suspicious-process
```

**Use case:** Only alert during off-hours when execution is suspicious.

### Key Learnings

1. **Suppression is essential** for high-volume detections
2. **Hash-based keys** effectively deduplicate process detections
3. **Threshold activation** filters transient anomalies
4. **False positive rules** eliminate known benign activity
5. **Enrichment** adds value without increasing volume
6. **Time-based rules** add context-aware alerting
7. **99% reduction** without sacrificing security coverage

---

## Example 5: Comprehensive Organization Optimization

### Scenario

- Organization: 300 sensors (mixed Windows, Linux, cloud)
- Current monthly cost: $2,000 (example)
- Goal: Reduce costs by 30-40% without sacrificing security
- Timeline: 60 days for full implementation

### Initial Baseline

**Infrastructure:**
- Sensors: 300 quota (250 active, 50 stale)
  - Windows: 120 (servers + workstations)
  - Linux: 80 (servers + containers)
  - macOS: 50 (laptops)
- Cloud: 50 AWS EC2 instances (high churn)

**Usage Metrics:**
- Outputs: 150GB/month to Splunk
- Queries: 200M events/month
- Extensions: 5 active (YARA, VirusTotal, etc.)
- Detections: 50,000/month
- Storage: 1 year retention (included in quota)

**Cost Breakdown (Example):**
- Sensor quota: $1,200/month
- Outputs: $450/month
- Queries: $200/month
- Extensions: $150/month
- **Total: $2,000/month**

### Phase 1: Sensor Culling (Week 1-2)

**Action:**
Implement sensor culling rules for different deployment types.

**Cloud VMs:**
```json
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```

**Development Systems:**
```json
{
  "action": "add_rule",
  "name": "cull-dev-systems",
  "tag": "development",
  "ttl": 14
}
```

**Production:**
```json
{
  "action": "add_rule",
  "name": "cull-old-production",
  "tag": "production",
  "ttl": 90
}
```

**Results:**
- 50 stale sensors removed
- Quota reduced: 300 → 250
- Monthly savings: $200
- **Phase 1 savings: $200/month**

### Phase 2: Output Optimization (Week 3-4)

**Current State:**
```yaml
# Forwarding all events
name: splunk-output
stream: event
destination: splunk
volume: 150GB/month
```

**Action:**
1. Set up GCS bucket in same region (us-central1)
2. Switch to detection-only forwarding to Splunk
3. Archive all events to GCS (free)

**New Configuration:**
```yaml
# Detection-only to Splunk
name: splunk-detections
stream: detection
destination: splunk

# Full events to GCS (free)
name: gcs-archive
type: gcs
bucket: security-telemetry
region: us-central1
stream: event
```

**Results:**
- Output to Splunk: 150GB → 3GB
- Output to GCS: 150GB (FREE)
- LimaCharlie output costs: $450 → $9
- **Phase 2 savings: $441/month**

### Phase 3: Rule Optimization (Week 5-6)

**Action:**
Audit all D&R rules and add suppression to top 10 noisiest rules.

**Top Noisy Rules Identified:**
1. DNS lookup detection: 15,000/month
2. Process spawn detection: 10,000/month
3. Network connection alert: 8,000/month
4. File modification alert: 7,000/month
5. Registry change detection: 5,000/month
6. Others: 5,000/month

**Example Optimization - DNS Detection:**

**Before:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
respond:
  - action: report
    name: malicious-domain-detected
```

**After:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
respond:
  - action: report
    name: malicious-domain-detected
    detect_data:
      domain: "{{ .event.DOMAIN_NAME }}"
      sensor: "{{ .routing.hostname }}"
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.DOMAIN_NAME }}'
        - 'malicious-domain'
```

**Results:**
- Detection volume: 50,000/month → 15,000/month
- **Reduction: 70%**
- Lower SIEM ingestion (reduces Splunk costs)
- Better analyst efficiency
- **Phase 3 savings: $50/month** (downstream SIEM savings)

### Phase 4: Query Optimization (Week 7-8)

**Action:**
1. Review common queries used by team
2. Update saved searches with optimizations
3. Train team on efficient querying
4. Implement query guidelines

**Common Query Issues Found:**
- Average time range: 7-14 days (too broad)
- No platform filters
- Wildcard field searches
- No event type specifications

**Query Optimization Example:**

**Before:**
```
-7d | * | event/* contains "powershell"
```
- Events evaluated: 200M
- Cost: $100

**After:**
```
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell" |
  event/FILE_PATH as path
  routing/hostname as host
  COUNT(event) as count
  GROUP BY(path host)
  LIMIT 100
```
- Events evaluated: 15M
- Cost: $7.50

**Results:**
- Query events: 200M/month → 80M/month
- **Reduction: 60%**
- **Phase 4 savings: $120/month**

### Phase 5: Performance Mode Optimization (Ongoing)

**Action:**
Tag-based performance mode assignment to optimize event collection.

**Configuration:**

```yaml
# VIP endpoints - high mode
detect:
  target: deployment
  event: enrollment
  op: is tagged
  tag: vip
respond:
  - action: task
    command: set_performance_mode --mode high

# Servers - normal mode (default)
# No rule needed, normal is default

# Workstations - low mode
detect:
  target: deployment
  event: enrollment
  op: is tagged
  tag: workstation
respond:
  - action: task
    command: set_performance_mode --mode low
```

**Distribution:**
- VIP endpoints (high): 10 sensors
- Servers (normal): 80 sensors
- Workstations (low): 160 sensors

**Results:**
- Reduced event volume from workstations (~40% of sensors)
- Lower storage and processing overhead
- Maintained high visibility for critical assets
- **Phase 5 savings: $50/month** (storage/processing reduction)

### Phase 6: Cost Monitoring Setup (Week 9-10)

**Action:**
Enable usage alerts for proactive cost management.

**Alert Configuration:**
```yaml
hives:
  extension_config:
    ext-usage-alerts:
      data:
        usage_alert_rules:
          - enabled: true
            limit: 107374182400     # 100GB
            name: Output data threshold
            sku: output_data
            timeframe: 43200

          - enabled: true
            limit: 100000000        # 100M events
            name: Query events threshold
            sku: query_events
            timeframe: 10080

          - enabled: true
            limit: 50
            name: Sensor quota headroom
            sku: sensor_quota
            timeframe: 1440
```

**Results:**
- Proactive alerting prevents cost overruns
- Early warning for unusual usage patterns
- Better budget forecasting

### Final Results

| Component | Before | After | Savings | % Reduction |
|-----------|--------|-------|---------|-------------|
| Sensors | 300 quota | 250 quota | $200/mo | 17% |
| Outputs | 150GB ($450) | 3GB ($9) | $441/mo | 98% |
| Queries | 200M ($200) | 80M ($80) | $120/mo | 60% |
| Rules/SIEM | N/A | Downstream | $50/mo | - |
| Performance | N/A | Optimized | $50/mo | - |
| Extensions | $150 | $130 | $20/mo | 13% |
| **Total** | **$2,000/mo** | **$1,119/mo** | **$881/mo** | **44%** |

**Annual Savings: $10,572**

### Timeline Summary

| Phase | Weeks | Effort | Savings | Cumulative |
|-------|-------|--------|---------|------------|
| 1. Sensor Culling | 1-2 | Low | $200/mo | $200/mo |
| 2. Output Optimization | 3-4 | Medium | $441/mo | $641/mo |
| 3. Rule Optimization | 5-6 | Medium | $50/mo | $691/mo |
| 4. Query Optimization | 7-8 | Medium | $120/mo | $811/mo |
| 5. Performance Modes | Ongoing | Low | $50/mo | $861/mo |
| 6. Cost Monitoring | 9-10 | Low | $0 | $861/mo |
| **Total** | **10 weeks** | - | **$881/mo** | **$881/mo** |

### Additional Benefits Beyond Cost Savings

**Operational Improvements:**
- Cleaner sensor inventory (50 stale sensors removed)
- Better SIEM performance (70% fewer alerts)
- Improved analyst productivity (less alert fatigue)
- Faster query execution (optimized queries)
- Better cost visibility (usage alerts)

**Security Improvements:**
- Maintained full detection coverage
- Higher signal-to-noise ratio
- Better alert enrichment
- Focused resources on high-value assets
- Improved incident response capabilities

**Team Benefits:**
- Reduced alert fatigue for analysts
- Better query performance
- Proactive cost awareness
- More efficient workflows
- Better budget predictability

### Lessons Learned

1. **Quick wins matter**: GCP outputs and sensor culling provide immediate ROI
2. **Phased approach works**: Incremental changes allow measurement and adjustment
3. **No security trade-offs needed**: 44% cost reduction with maintained coverage
4. **Team training is essential**: Query optimization requires team buy-in
5. **Monitoring prevents regression**: Usage alerts keep costs under control
6. **Documentation is key**: Maintain runbooks for optimization techniques
7. **Regular reviews**: Quarterly audits catch new optimization opportunities

### Maintenance Plan

**Weekly:**
- Review usage alerts
- Check for anomalous usage patterns

**Monthly:**
- Review culled sensors
- Audit new D&R rules for suppression
- Check output volume trends
- Review query costs

**Quarterly:**
- Comprehensive audit of all rules
- Review and update sensor tags
- Validate cull rule TTLs
- Update optimization documentation
- Team training refresher

**Annually:**
- Full cost-benefit analysis
- Review platform changes/new features
- Update optimization strategy
- Budget planning for next year

---

[← Back to SKILL.md](./SKILL.md) | [View Reference →](./REFERENCE.md) | [Troubleshooting →](./TROUBLESHOOTING.md)
