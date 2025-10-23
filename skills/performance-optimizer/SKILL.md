---
name: performance-optimizer
description: Help users optimize LimaCharlie performance, reduce costs, manage billing, and implement efficient resource management strategies.
---

# LimaCharlie Performance and Cost Optimizer

This skill helps users optimize LimaCharlie performance, reduce operational costs, and implement efficient resource management. Use this skill when users ask about cost reduction, billing optimization, performance tuning, query optimization, or resource management.

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding LimaCharlie Billing](#understanding-limacharlie-billing)
3. [Performance Mode](#performance-mode)
4. [Event Suppression](#event-suppression)
5. [Query Optimization](#query-optimization)
6. [Output Cost Optimization](#output-cost-optimization)
7. [Sensor Culling](#sensor-culling)
8. [Rule Optimization](#rule-optimization)
9. [Cost Monitoring and Alerts](#cost-monitoring-and-alerts)
10. [Best Practices](#best-practices)
11. [Optimization Examples](#optimization-examples)

---

## Introduction

LimaCharlie offers flexible, usage-based pricing alongside traditional quota-based billing. Understanding the billing model and implementing optimization strategies can significantly reduce costs while maintaining security effectiveness.

### Key Cost Components

LimaCharlie billing includes several components:

1. **Sensors (vSensors)**: Per-endpoint quota or usage-based billing
2. **Event Processing**: Number of events processed by the platform
3. **Event Storage**: Storage of telemetry data (included with quota or charged separately)
4. **Outputs**: Data egress to external systems
5. **Extensions**: Additional services and integrations
6. **Queries (LCQL)**: Events evaluated during historical searches
7. **Artifacts**: File collection and storage
8. **Payloads**: Data sent to endpoints

### Optimization Goals

- Reduce unnecessary event volume
- Minimize output data egress costs
- Optimize query performance and cost
- Remove stale sensors
- Improve D&R rule efficiency
- Monitor and alert on usage thresholds

---

## Understanding LimaCharlie Billing

### Billing Models

#### Quota-Based Billing (vSensors)

**How it works:**
- Set a quota of concurrent sensors (vSensors)
- Pay predictable monthly fee per vSensor
- Includes 1 year of full telemetry storage
- Charged one month ahead

**Example:**
- 100 vSensor quota = 100 concurrent endpoints
- Can mix: 50 Windows + 30 Linux + 20 macOS = 100 total
- Pricing available at: https://limacharlie.io/pricing

**When to use:**
- Predictable, stable deployments
- Need consistent budget forecasting
- Want included telemetry storage
- Enterprise environments with fixed fleet size

#### Usage-Based Billing

**How it works:**
- Pay only for what you use
- Charges based on:
  - Sensor connection time
  - Events processed
  - Events stored
- No quota limits
- Billed monthly in arrears

**When to use:**
- Variable or seasonal workloads
- Incident response scenarios
- Development/testing environments
- Sleeper mode deployments

#### Sleeper Mode

**Special low-cost deployment mode:**
- Deploy sensors with `lc:sleeper` tag
- Cost: $0.10 per sensor per 30 days
- Example: 100 sensors = $10/month
- Minimal telemetry collection
- Activate when needed with `lc:usage` tag or by removing `lc:sleeper`

**Use cases:**
- Pre-deployed incident response capability
- Rapid activation without redeployment
- Competitive IR SLAs
- Disaster recovery preparedness

### Billable Components

#### 1. Sensors
- **Quota-based**: Fixed monthly per vSensor
- **Usage-based**: Connection time + events processed/stored
- **Sleeper mode**: $0.10/sensor/30 days

#### 2. Event Processing
- Events evaluated by D&R rules
- Platform event processing
- Real-time telemetry ingestion

#### 3. Event Storage
- Included with quota-based billing (1 year)
- Charged separately for usage-based billing
- Insight add-on extends retention

#### 4. Outputs
- Data egress to external systems
- Billed per GB transmitted
- Exception: GCP outputs in same region are free
- Pricing: Check https://limacharlie.io/pricing

#### 5. Queries (LCQL)
- Charged per million events evaluated
- Cost depends on query efficiency
- Time range affects total cost
- Better-tuned queries = lower cost

#### 6. Artifacts
- File collection from endpoints
- Storage of collected files
- Priced per GB

#### 7. Payloads
- Data sent to endpoints
- Example: $0.19 per GB
- 1GB payload to 10 endpoints = $1.90
- Impacts Atomic Red Team, Dumper extensions

#### 8. Extensions
- Add-on services (Yara, VirusTotal, etc.)
- Variable pricing based on extension
- Some extensions are usage-based

### Free Output Regions

GCP outputs in the same region as your LimaCharlie datacenter are **FREE**:

| Datacenter | Free Region |
|------------|-------------|
| USA | us-central1 |
| Canada | northamerica-northeast1 |
| Europe | europe-west4 |
| UK | europe-west2 |
| India | asia-south1 |
| Australia | australia-southeast1 |

**Free GCP mechanisms:**
- Google Cloud Storage (GCS)
- Google Pub/Sub
- Google BigQuery

**Optimization tip:** Route outputs through GCP in the same region to eliminate output costs.

### Viewing Billing Information

**Web UI:**
1. Navigate to Organization Setup
2. Click "Billing & Usage" tab
3. View metered usage breakdown
4. Check current quota and charges

**API:**
```bash
# Get organization usage stats
curl https://api.limacharlie.io/v1/usage/YOUR_OID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Python SDK:**
```python
import limacharlie
lc = limacharlie.Manager()
org = lc.organization('YOUR_OID')
usage = org.usage()
print(usage)
```

---

## Performance Mode

### What is Performance Mode?

The `set_performance_mode` command adjusts sensor resource usage and telemetry collection levels. This balances visibility against endpoint performance impact.

### Available Modes

#### Low Performance Mode
```
set_performance_mode --mode low
```

**Characteristics:**
- Minimal CPU and memory usage
- Reduced telemetry collection
- Lower event volume
- Suitable for resource-constrained systems

**When to use:**
- Legacy systems with limited resources
- Virtual machines with tight resource allocations
- Endpoints experiencing performance issues
- Cost-sensitive deployments

#### Normal Performance Mode (Default)
```
set_performance_mode --mode normal
```

**Characteristics:**
- Balanced resource usage
- Standard telemetry collection
- Default configuration

**When to use:**
- Standard deployments
- Typical workstations and servers
- General-purpose monitoring

#### High Performance Mode
```
set_performance_mode --mode high
```

**Characteristics:**
- Maximum telemetry visibility
- Higher CPU and memory usage
- Comprehensive event collection
- Enhanced detection capabilities

**When to use:**
- High-value targets (VIP endpoints)
- Critical servers requiring maximum visibility
- Investigation and incident response
- Threat hunting exercises

### Setting Performance Mode via D&R Rules

Automate performance mode assignment based on tags:

```yaml
# Set high performance for VIP endpoints
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
        - performance-mode-set

# Set low performance for IoT devices
detect:
  target: deployment
  event: enrollment
  op: is tagged
  tag: iot
respond:
  - action: task
    command: set_performance_mode --mode low
    suppression:
      max_count: 1
      period: 24h
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - performance-mode-set
```

### Performance Mode Impact

| Metric | Low | Normal | High |
|--------|-----|--------|------|
| CPU Usage | ~1-2% | ~2-5% | ~5-10% |
| Memory Usage | ~50-100MB | ~100-200MB | ~200-400MB |
| Event Volume | Minimal | Standard | Maximum |
| Detection Coverage | Basic | Standard | Comprehensive |
| Cost Impact | Lowest | Medium | Highest |

### Best Practices

1. **Default to Normal**: Use normal mode for most deployments
2. **High for Critical**: Apply high mode only to critical assets
3. **Low for Constrained**: Use low mode for resource-limited systems
4. **Tag-Based Assignment**: Automate mode assignment with tags and D&R rules
5. **Monitor Impact**: Track performance metrics after mode changes

---

## Event Suppression

Event suppression reduces detection noise, action frequency, and costs by controlling how often D&R rules trigger.

### Suppression Types

#### 1. Frequency Reduction

Limit action execution frequency:

```yaml
- action: report
  name: evil-process-detected
  suppression:
    max_count: 1          # Execute at most once
    period: 1h            # Per hour
    is_global: true       # Across entire org (false = per sensor)
    keys:
      - '{{ .event.FILE_PATH }}'
      - 'evil-process-detected'
```

**Result:** Same process detection only alerts once per hour per file path.

#### 2. Threshold Activation

Only execute after minimum activations:

```yaml
- action: report
  name: high-frequency-alerts
  suppression:
    min_count: 5          # Must match 5 times
    max_count: 5          # Then alert once
    period: 1h            # Within 1 hour
    is_global: false      # Per sensor
```

**Result:** Only alerts after 5 occurrences within the period.

#### 3. Variable Count Suppression

Increment by dynamic values (useful for billing alerts):

```yaml
detect:
  event: billing_record
  op: is
  path: event/record/k
  target: billing
  value: output_data
respond:
  - action: report
    name: output-data-threshold-reached
    suppression:
      count_path: event/record/v    # Increment by this value
      is_global: true
      keys:
        - output-data-usage
      max_count: 1073741824           # 1GB in bytes
      min_count: 1073741824
      period: 24h
```

**Result:** Alerts when 1GB of output data transmitted in 24 hours.

### Suppression Scope

#### Global Suppression (`is_global: true`)
- Applies across entire organization
- All sensors share the suppression counter
- Use for org-wide limits

**Example:**
```yaml
suppression:
  is_global: true
  keys:
    - 'org-wide-limit'
  max_count: 10
  period: 1h
```

**Result:** Total of 10 actions across all sensors per hour.

#### Per-Sensor Suppression (`is_global: false`)
- Applies per individual sensor
- Each sensor has its own counter
- Use for sensor-specific limits

**Example:**
```yaml
suppression:
  is_global: false
  keys:
    - '{{ .routing.sid }}'
    - 'per-sensor-limit'
  max_count: 5
  period: 1h
```

**Result:** Each sensor can trigger 5 times per hour.

### Suppression Keys

Keys define uniqueness for suppression:

```yaml
keys:
  - '{{ .event.FILE_PATH }}'      # Dynamic from event
  - '{{ .routing.hostname }}'     # Dynamic from routing
  - 'static-identifier'           # Static string
  - 'my-detection-name'           # Detection identifier
```

**How it works:**
- Keys are combined (ANDed) to create unique suppression identifier
- Same key combination = same suppression counter
- Different keys = different suppression counters

**Example:**
```yaml
keys:
  - '{{ .event.FILE_PATH }}'
  - 'malware-detection'
```

Suppression tracks separately for:
- `C:\malware.exe` + `malware-detection`
- `C:\evil.exe` + `malware-detection`

### Suppression Time Formats

Supported formats: `ns`, `us`, `ms`, `s`, `m`, `h`

Examples:
- `1h` = 1 hour
- `30m` = 30 minutes
- `86400s` = 24 hours
- `500ms` = 500 milliseconds

### Cost Optimization with Suppression

#### Reduce Sensor Command Frequency

**Problem:** Repeated YARA scans waste resources.

**Solution:**
```yaml
- action: task
  command: yara_scan hive://yara/malware-rule --pid "{{ .event.PROCESS_ID }}"
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
      - 'yara-scan'
    max_count: 1
    period: 5m
```

**Result:** Each process scanned at most once per 5 minutes.

#### Reduce Detection Volume

**Problem:** Noisy detection creates thousands of alerts.

**Solution:**
```yaml
- action: report
  name: common-but-suspicious
  suppression:
    max_count: 1
    period: 24h
    is_global: true
    keys:
      - '{{ .event.HASH }}'
      - 'common-suspicious'
```

**Result:** Same file hash only alerts once per day org-wide.

#### Reduce Extension Calls

**Problem:** VirusTotal lookups consume API quota.

**Solution:**
```yaml
- action: extension request
  extension name: vt
  extension action: scan_hash
  extension request:
    hash: '{{ .event.HASH }}'
  suppression:
    is_global: true
    keys:
      - '{{ .event.HASH }}'
      - 'vt-scan'
    max_count: 1
    period: 168h  # 7 days
```

**Result:** Each hash looked up at most once per week.

### Best Practices for Suppression

1. **Always Suppress Sensor Commands**: Prevent resource exhaustion
2. **Use Appropriate Scope**: Global for org-wide, per-sensor for endpoint-specific
3. **Choose Meaningful Keys**: Include relevant identifiers (hash, path, domain)
4. **Set Reasonable Periods**: Balance detection coverage vs. noise
5. **Include Detection Name**: Add static identifier to keys for clarity
6. **Test Suppression Logic**: Verify suppression works as expected
7. **Document Suppression Rationale**: Explain why suppression is needed

---

## Query Optimization

LCQL queries are charged per million events evaluated. Efficient queries reduce cost and improve performance.

### Understanding Query Cost

**Cost Model:**
- Charged per million events evaluated (not matched, evaluated)
- Larger time ranges = more events evaluated
- Better filtering = fewer events evaluated
- Cost estimation shown before query runs

**Example Cost Calculation:**
```
Time range: Last 24 hours
Total events in range: 10 million
Query cost estimation: $X per million events evaluated
Estimated cost: $10X
```

### Query Optimization Strategies

#### 1. Limit Time Range

**Bad:**
```
-30d | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell"
```
- Evaluates 30 days of data
- Millions of events scanned

**Good:**
```
-2h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell"
```
- Evaluates 2 hours of data
- Significantly fewer events
- **Cost Reduction: 360x**

**Best Practice:** Use the smallest time range that meets your needs.

#### 2. Use Event Type Filters

**Bad:**
```
-24h | plat == windows | * | event/* contains "malware.exe"
```
- Searches ALL event types
- Evaluates every event

**Good:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```
- Filters to NEW_PROCESS events only
- Evaluates only process creation events
- **Cost Reduction: 10-50x** (depending on event mix)

**Best Practice:** Always specify event types when possible.

#### 3. Use Platform Filters

**Bad:**
```
-24h | NEW_PROCESS | event/FILE_PATH contains "cmd.exe"
```
- Searches across all platforms
- Includes Linux, macOS events that never match

**Good:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "cmd.exe"
```
- Filters to Windows only
- Skips irrelevant platforms
- **Cost Reduction: 2-5x** (depending on platform mix)

**Best Practice:** Filter by platform early in query.

#### 4. Use Sensor Selectors

**Bad:**
```
-24h | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```
- Searches all sensors

**Good:**
```
-24h | production in tags and plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```
- Filters to production Windows sensors only
- **Cost Reduction: Varies by selector specificity**

**Best Practice:** Target specific sensors when investigating known scope.

#### 5. Optimize Filter Order

**Bad:**
```
-24h | plat == windows | NEW_PROCESS | event/* contains "malware" | event/FILE_PATH ends with ".exe"
```
- Generic search first
- Specific filter last

**Good:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with ".exe" | event/FILE_PATH contains "malware"
```
- Specific filters first
- Narrows scope quickly
- **Cost Reduction: 10-20%**

**Best Practice:** Put most restrictive filters first.

#### 6. Use Specific Paths

**Bad:**
```
-24h | plat == windows | NEW_PROCESS | event/* contains "suspicious"
```
- Searches all fields
- Inefficient wildcard

**Good:**
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "suspicious" or event/COMMAND_LINE contains "suspicious"
```
- Targets specific fields
- More efficient evaluation
- **Cost Reduction: 30-50%**

**Best Practice:** Specify exact field paths instead of wildcards.

#### 7. Limit Result Sets

Use projections to limit output:

```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware" |
  event/FILE_PATH as path
  routing/hostname as host
  COUNT(event) as count
  GROUP BY(path host)
  ORDER BY(count DESC)
  LIMIT 100
```

**Benefits:**
- Reduces data transfer
- Faster results
- Easier to analyze

#### 8. Use Aggregations

Instead of retrieving all events, aggregate:

**Bad:**
```
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "google"
```
- Returns thousands of individual events

**Good:**
```
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "google" |
  event/DOMAIN_NAME as domain
  COUNT(event) as count
  GROUP BY(domain)
```
- Returns summarized data
- Much smaller result set
- **Performance Improvement: 100x+**

### Query Performance Monitoring

**Query Status Indicators:**
1. **Syntax Errors**: Shown in real-time
2. **Cost Estimation**: "At most" cost before running
3. **Progress**: Running total as query executes
4. **Event Types**: Available types in fetched data
5. **Query Fields**: Fields present in results

**Histogram View:**
- Shows event distribution over time
- Indicates query progress
- Helps identify data density

### Example Query Optimizations

#### Example 1: Failed Login Investigation

**Before:**
```
-7d | * | event/* contains "4625"
```
- 7 days of all events
- Wildcard search
- Estimated cost: HIGH

**After:**
```
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" |
  event/EVENT/EventData/TargetUserName as user
  event/EVENT/EventData/IpAddress as ip
  COUNT(event) as attempts
  GROUP BY(user ip)
  ORDER BY(attempts DESC)
```
- 24 hours instead of 7 days
- Platform filter
- Specific event type
- Specific field path
- Aggregated results
- **Cost Reduction: 50-100x**

#### Example 2: Domain Reputation Check

**Before:**
```
-30d | DNS_REQUEST | event/DOMAIN_NAME contains "suspicious"
```
- 30 days of DNS requests
- Vague domain match

**After:**
```
-24h | plat == windows and production in tags | DNS_REQUEST |
  event/DOMAIN_NAME ends with "suspicious-domain.com" |
  event/DOMAIN_NAME as domain
  routing/hostname as host
  COUNT_UNIQUE(routing/sid) as sensor_count
  GROUP BY(domain)
```
- 24 hours instead of 30 days
- Platform and tag filter
- Specific domain suffix
- Aggregation by unique sensors
- **Cost Reduction: 30-60x**

#### Example 3: Process Tree Analysis

**Before:**
```
-7d | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe"
```
- 7 days of process events
- All platforms
- Simple parent filter

**After:**
```
-4h | plat == windows and server in tags | NEW_PROCESS |
  event/PARENT/FILE_PATH ends with "cmd.exe" |
  event/PARENT/FILE_PATH as parent
  event/FILE_PATH as child
  COUNT(event) as spawn_count
  GROUP BY(parent child)
  ORDER BY(spawn_count DESC)
  LIMIT 50
```
- 4 hours instead of 7 days
- Platform and tag filter
- Specific match instead of contains
- Grouped and limited results
- **Cost Reduction: 40-80x**

### Query Cost Best Practices

1. **Start Small**: Begin with short time ranges, expand if needed
2. **Filter Early**: Apply platform, tag, event type filters first
3. **Be Specific**: Use exact paths and event types
4. **Aggregate Results**: Use COUNT, GROUP BY instead of raw events
5. **Test Queries**: Run against small time ranges first
6. **Monitor Costs**: Check cost estimation before running
7. **Save Efficient Queries**: Build library of optimized queries
8. **Use Saved Searches**: Reuse proven, efficient queries

---

## Output Cost Optimization

Outputs forward data to external systems and are billed per GB transmitted. Optimization reduces egress costs.

### Understanding Output Costs

**Billing Model:**
- Charged per GB of data transmitted
- Pricing available at: https://limacharlie.io/pricing
- Exception: GCP outputs in same region are FREE

**Cost Factors:**
1. Output volume (GB transmitted)
2. Number of events forwarded
3. Event size (full events vs. filtered fields)
4. Output destination (GCP same-region is free)

### Output Optimization Strategies

#### 1. Use Targeted Outputs

Instead of forwarding all events, create targeted outputs:

**Bad:**
```yaml
# Output configuration
stream: event
# Forwards ALL events
```

**Good:**
```yaml
# Output configuration
stream: tailored
# Use D&R rules to selectively forward events
```

Then use D&R rules to forward specific events:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/COMMAND_LINE
      value: suspicious
respond:
  - action: output
    name: siem-output
```

**Result:** Only suspicious process events forwarded, not everything.
**Cost Reduction: 90-99%**

#### 2. Use GCP Same-Region Outputs

**Free Output Options:**

Route outputs through GCP in same region:

**Example: USA Datacenter → GCS (us-central1)**
```yaml
# Output to Google Cloud Storage
type: gcs
bucket: my-security-logs
region: us-central1  # Same as USA datacenter
```

**Result:** Zero output costs.

**Example: Europe Datacenter → Pub/Sub (europe-west4)**
```yaml
# Output to Google Pub/Sub
type: pubsub
project: my-project
topic: security-events
region: europe-west4  # Same as Europe datacenter
```

**Result:** Zero output costs.

**Free GCP Mechanisms:**
- Google Cloud Storage (GCS)
- Google Pub/Sub
- Google BigQuery

**Regional Mapping:**
| LimaCharlie Datacenter | Free GCP Region |
|------------------------|-----------------|
| USA | us-central1 |
| Canada | northamerica-northeast1 |
| Europe | europe-west4 |
| UK | europe-west2 |
| India | asia-south1 |
| Australia | australia-southeast1 |

#### 3. Filter Output Fields

Send only necessary fields instead of full events:

**Bad:**
```yaml
# D&R rule forwarding full event
- action: output
  name: siem-output
# Forwards entire event (100s of fields)
```

**Good:**
Use projections or transforms to limit fields (requires advanced configuration).

**Alternative:** Use detection reports with specific `detect_data`:

```yaml
- action: report
  name: suspicious-process
  detect_data:
    file_path: "{{ .event.FILE_PATH }}"
    command_line: "{{ .event.COMMAND_LINE }}"
    hostname: "{{ .routing.hostname }}"
    timestamp: "{{ .routing.event_time }}"
# Output forwards only detections stream (smaller than events)
```

**Result:** Smaller payloads, reduced costs.
**Cost Reduction: 50-80%**

#### 4. Use Detection Stream Instead of Event Stream

**Comparison:**

| Stream | Volume | Use Case |
|--------|--------|----------|
| `event` | Very High | Full telemetry forwarding |
| `detection` | Low | Alerts and detections only |
| `audit` | Low | Platform audit events |
| `deployment` | Low | Sensor lifecycle events |
| `artifact` | Medium | Artifact collection events |
| `tailored` | Variable | Custom D&R forwarding |

**Strategy:**
- Forward `detection` stream for alerts
- Use `tailored` stream for specific high-value events
- Avoid forwarding `event` stream to external SIEMs

**Cost Reduction: 95-99%** compared to full event stream.

#### 5. Use Suppression in Output Rules

Limit output frequency with suppression:

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
        - 'malicious-domain-output'
  - action: output
    name: siem-output
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.DOMAIN_NAME }}'
        - 'malicious-domain-output'
```

**Result:** Each malicious domain forwarded once per 24h, not every occurrence.
**Cost Reduction: Varies, potentially 50-90%**

#### 6. Aggregate Before Outputting

Instead of forwarding individual events, aggregate and forward summaries:

**Strategy:**
1. Use stateful rules with `min_count`
2. Report after threshold reached
3. Forward report (summary) instead of individual events

**Example:**
```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'
    count: 5
    within: 300
respond:
  - action: report
    name: brute-force-detected
    detect_data:
      sensor: "{{ .routing.hostname }}"
      event_count: 5
      timeframe: "5 minutes"
  - action: output
    name: siem-output
```

**Result:** 1 aggregated alert forwarded instead of 5 individual events.
**Cost Reduction: 80%+**

#### 7. Use Output Allowlisting

Control which events are forwarded using output filters (if supported by output type).

### Output Cost Monitoring

**Track Output Usage:**

1. **Web UI**: Navigate to Billing & Usage → Metered Usage
2. **Look for**: "Output Data" metric
3. **Monitor**: GB transmitted and associated costs

**Set Usage Alerts:**

Use the Usage Alerts extension:

```yaml
# In extension_config hive
hives:
  extension_config:
    ext-usage-alerts:
      data:
        usage_alert_rules:
          - enabled: true
            limit: 100         # GB
            name: Output data threshold
            sku: output_data
            timeframe: 43200   # 30 days in minutes
```

**Result:** Detection when output data exceeds 100GB in 30 days.

### Output Architecture Patterns

#### Pattern 1: GCP Hub and Spoke

**Architecture:**
1. LimaCharlie → GCP (same region, FREE)
2. GCP → External SIEM (charged by GCP rates)

**Benefits:**
- Zero LimaCharlie output costs
- Leverage GCP networking rates
- Use GCP tools for filtering/transformation

#### Pattern 2: Detection-Only Forwarding

**Architecture:**
1. Process all events with D&R rules in LimaCharlie
2. Forward only detections to SIEM
3. Store full telemetry in LimaCharlie Insight (1 year)

**Benefits:**
- Minimal output costs (detections are ~1% of events)
- Full telemetry available in LimaCharlie for hunting
- SIEM receives high-value alerts only

#### Pattern 3: Hybrid Approach

**Architecture:**
1. Forward detections to SIEM
2. Forward specific high-value event types via tailored output
3. Use GCP same-region for cold storage

**Benefits:**
- Balanced visibility in SIEM
- Controlled output costs
- Comprehensive archival

### Output Cost Best Practices

1. **Evaluate Necessity**: Question if every event needs forwarding
2. **Prefer GCP Same-Region**: Use free output options when possible
3. **Forward Detections, Not Events**: SIEMs need alerts, not raw telemetry
4. **Use Suppression**: Prevent duplicate forwarding
5. **Monitor Output Volume**: Track GB transmitted monthly
6. **Set Usage Alerts**: Get notified before costs spike
7. **Aggregate When Possible**: Summarize before forwarding
8. **Test Output Configuration**: Validate volume before production
9. **Review Regularly**: Audit outputs quarterly

---

## Sensor Culling

Sensor culling automatically removes stale sensors that haven't connected, reducing quota usage and costs.

### Why Cull Sensors?

**Common Scenarios:**
1. **Cloud/VM deployments**: Ephemeral instances enroll repeatedly
2. **Template-based deployments**: Each instance enrolls separately
3. **Decommissioned endpoints**: Sensors remain in org after removal
4. **Test environments**: Temporary sensors left behind

**Impact:**
- Sensors count against quota even when offline
- Unused quota = wasted costs
- Cluttered sensor list
- Difficult to identify active sensors

### Sensor Cull Extension

**What it does:**
- Automatically removes sensors that haven't connected within specified period
- Runs daily
- Tag-based rules for different sensor types
- No manual cleanup needed

**How it works:**
1. Define cull rules based on sensor tags
2. Set TTL (time to live) in days
3. Extension runs daily, removes sensors exceeding TTL
4. Frees up quota automatically

### Enabling Sensor Cull

**Web UI:**
1. Navigate to Add-ons → Extensions
2. Search for "Sensor Cull"
3. Click Subscribe
4. Available immediately under Sensors → Sensor Cull

**Marketplace Link:**
https://app.limacharlie.io/add-ons/extension-detail/ext-sensor-cull

### Creating Cull Rules

#### Via Web UI

1. Navigate to Sensors → Sensor Cull
2. Click "Add Rule"
3. Configure:
   - **Name**: Descriptive rule name
   - **Tag**: Sensor tag to match
   - **TTL**: Days before culling

#### Via REST API

**Get existing rules:**
```json
{
  "action": "get_rules"
}
```

**Add rule:**
```json
{
  "action": "add_rule",
  "name": "cull-ephemeral-vms",
  "tag": "ephemeral",
  "ttl": 7
}
```

**Delete rule:**
```json
{
  "action": "del_rule",
  "name": "cull-ephemeral-vms"
}
```

**Run ad-hoc cleanup:**
```json
{
  "action": "run"
}
```

#### Via Infrastructure as Code

Manage rules in your IaC configuration:

```yaml
# Sensor Cull extension configuration
# Managed via Infrastructure as Code extension
```

### Cull Rule Examples

#### Example 1: Cloud VMs

**Scenario:** AWS EC2 instances auto-scale, creating many temporary sensors.

**Rule:**
```json
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```

**Result:** Cloud VMs not connected in 3 days are removed.

**Setup:**
1. Create installation key with tag `cloud-vm`
2. Use this key for cloud deployments
3. Sensors auto-culled after 3 days offline

#### Example 2: Development Environment

**Scenario:** Developers spin up test VMs frequently, forget to remove sensors.

**Rule:**
```json
{
  "action": "add_rule",
  "name": "cull-dev-sensors",
  "tag": "development",
  "ttl": 14
}
```

**Result:** Dev sensors not connected in 2 weeks are removed.

#### Example 3: Kubernetes Pods

**Scenario:** Containerized workloads with ephemeral sensors.

**Rule:**
```json
{
  "action": "add_rule",
  "name": "cull-k8s-pods",
  "tag": "kubernetes",
  "ttl": 1
}
```

**Result:** Kubernetes sensors offline for 1 day are removed.

#### Example 4: Long-Term Servers

**Scenario:** Production servers expected to be always-on.

**Rule:**
```json
{
  "action": "add_rule",
  "name": "cull-old-servers",
  "tag": "server",
  "ttl": 90
}
```

**Result:** Servers offline for 90 days are removed (likely decommissioned).

### Cull Strategy by Deployment Type

| Deployment Type | Recommended TTL | Tag |
|----------------|-----------------|-----|
| Cloud VMs (auto-scaling) | 1-3 days | cloud-vm, ephemeral |
| Docker containers | 1 day | docker, container |
| Kubernetes pods | 1 day | kubernetes, k8s |
| Development VMs | 7-14 days | development, test |
| Laptops/workstations | 60-90 days | workstation, laptop |
| Servers | 90-180 days | server, production |
| VIP endpoints | Never cull | vip, critical |

### Best Practices for Sensor Culling

1. **Tag Appropriately**: Use installation key tags for classification
2. **Conservative TTLs Initially**: Start longer, reduce based on patterns
3. **Different Rules per Type**: Servers vs. cloud VMs need different TTLs
4. **Exclude Critical Systems**: Don't cull VIP or critical sensors
5. **Monitor Cull Activity**: Review culled sensors periodically
6. **Document Rules**: Maintain documentation of TTL rationale
7. **Test First**: Run ad-hoc cleanup to see impact before automating
8. **Align with Lifecycle**: Match TTLs to endpoint lifecycle

### Preventing Accidental Culling

**Strategy 1: Exclude Critical Tags**

Don't create cull rules for:
- `vip`
- `critical`
- `production` (unless high TTL)

**Strategy 2: Long TTLs for Persistent Systems**

Use longer TTLs for systems that may legitimately be offline:
- Laptops: 60-90 days (may be powered off for weeks)
- Servers: 90-180 days (long maintenance windows)

**Strategy 3: Manual Culling for Production**

For production environments:
- Use manual culling only
- Review sensor list quarterly
- Delete sensors via web UI after verification

### Monitoring Culled Sensors

**Track Deleted Sensors:**

Create D&R rule to detect culling:

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
      denied_for: "{{ .event.denied_for }}"
```

**Result:** Detection created when sensor is culled, providing visibility.

### Cost Impact of Sensor Culling

**Scenario:**
- 500 sensor quota
- 100 stale sensors (offline, forgotten)
- Sensor cost: $1/sensor/month (example pricing)

**Without Culling:**
- Pay for 500 sensors
- Cost: $500/month
- 100 sensors wasted

**With Culling:**
- Stale sensors auto-removed
- Reduce quota to 400
- Cost: $400/month
- **Savings: $100/month = $1,200/year**

**ROI:** Sensor culling pays for itself immediately.

---

## Rule Optimization

Efficient D&R rules reduce platform load, improve performance, and lower costs.

### Rule Performance Principles

1. **Filter Early**: Most restrictive conditions first
2. **Specify Event Types**: Always use `event:` parameter
3. **Avoid Expensive Operations**: Minimize regex, lookups
4. **Use Suppression**: Control action frequency
5. **Scope Appropriately**: Target specific sensors/platforms

### Performance Optimization Techniques

#### 1. Event Type Filtering

**Bad:**
```yaml
detect:
  op: contains
  path: event/FILE_PATH
  value: malware.exe
```
- Evaluates ALL event types
- Most events don't have FILE_PATH

**Good:**
```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: malware.exe
```
- Evaluates only NEW_PROCESS events
- **Performance Improvement: 10-50x**

#### 2. Platform Filtering

**Bad:**
```yaml
detect:
  event: NEW_PROCESS
  op: contains
  path: event/FILE_PATH
  value: cmd.exe
```
- Evaluates across all platforms
- cmd.exe only on Windows

**Good:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform
      name: windows
    - op: contains
      path: event/FILE_PATH
      value: cmd.exe
```
- Filters to Windows immediately
- **Performance Improvement: 2-5x**

#### 3. Operator Selection

**Operator Performance (fastest to slowest):**
1. `is` - Exact match (fastest)
2. `exists` - Field presence check
3. `ends with` / `starts with` - Prefix/suffix match
4. `contains` - Substring search
5. `matches` - Regular expression (slowest)

**Example:**

**Bad:**
```yaml
op: matches
path: event/FILE_PATH
re: .*\.exe$
```

**Good:**
```yaml
op: ends with
path: event/FILE_PATH
value: .exe
case sensitive: false
```

**Performance Improvement: 5-10x**

#### 4. Rule Ordering

**Bad:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains             # Generic, slow
      path: event/COMMAND_LINE
      value: powershell
    - op: is platform          # Specific, fast
      name: windows
```

**Good:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is platform          # Specific, fast - evaluated first
      name: windows
    - op: contains             # Generic, slow - evaluated if first passes
      path: event/COMMAND_LINE
      value: powershell
```

**Performance Improvement: 10-20%**

#### 5. Avoid Wildcards

**Bad:**
```yaml
op: contains
path: event/*
value: suspicious
```
- Searches all event fields
- Very inefficient

**Good:**
```yaml
op: or
rules:
  - op: contains
    path: event/FILE_PATH
    value: suspicious
  - op: contains
    path: event/COMMAND_LINE
    value: suspicious
```
- Targets specific fields
- **Performance Improvement: 50-100x**

### Suppression in Rules

Always use suppression with sensor commands:

**Bad:**
```yaml
- action: task
  command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
```
- Runs on every match
- Can overwhelm sensor

**Good:**
```yaml
- action: task
  command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
      - 'yara-scan'
    max_count: 1
    period: 5m
```
- Limits to once per process per 5 minutes
- **Cost/Performance Impact: Prevents runaway commands**

### Detection Volume Optimization

#### Use Threshold Activation

Instead of alerting on every occurrence, require multiple events:

```yaml
detect:
  event: WEL
  op: is windows
  with events:
    event: WEL
    op: is
    path: event/EVENT/System/EventID
    value: '4625'
    count: 5
    within: 300
respond:
  - action: report
    name: brute-force-attempt
```

**Result:** 1 detection instead of 5, but still catches behavior.
**Detection Volume Reduction: 80%**

#### Use Suppression on Reports

```yaml
- action: report
  name: common-suspicious-activity
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.HASH }}'
      - 'common-suspicious'
```

**Result:** Each unique hash alerts once per hour max.

### Rule Scoping

#### Tag-Based Scoping

Apply different rules to different sensor groups:

```yaml
# Strict rules for production
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: production
    - op: contains
      path: event/COMMAND_LINE
      value: suspicious
```

```yaml
# Relaxed rules for development
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: development
    - op: contains
      path: event/COMMAND_LINE
      value: very-suspicious
    # Higher threshold for dev environments
```

**Result:** Appropriate sensitivity per environment.

#### Time-Based Rules

Activate rules only during specific times:

```yaml
detect:
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
    - day_of_week_start: 1     # Sunday
      day_of_week_end: 1       # Sunday
      time_of_day_start: 0     # All day Sunday
      time_of_day_end: 2359
      tz: America/Los_Angeles
respond:
  - action: report
    name: off-hours-browser-usage
```

**Result:** Only detect during off-hours, reducing noise.

### False Positive Rules

Create FP rules to filter known benign detections:

```yaml
# False Positive Rule (separate D&R rule)
detect:
  target: detection
  event: detection
  op: and
  rules:
    - op: is
      path: detect/cat
      value: suspicious-process
    - op: is
      path: detect/routing/hostname
      value: known-dev-server
respond:
  # No action = detection suppressed
```

**Result:** Detection occurs but is filtered before outputs.

### Rule Performance Monitoring

**Metrics to Track:**
1. Detection volume per rule
2. False positive rate
3. Action execution frequency
4. Rule hit frequency

**Tools:**
- LimaCharlie Detections page
- Usage statistics
- Custom reporting via API

### Rule Optimization Checklist

- [ ] Event type specified
- [ ] Platform filter applied
- [ ] Most restrictive conditions first
- [ ] Appropriate operators (avoid regex when simpler operators work)
- [ ] Suppression on all sensor commands
- [ ] Suppression on high-frequency detections
- [ ] Tag-based scoping where appropriate
- [ ] Time-based scoping if applicable
- [ ] False positive rules for known benign activity
- [ ] Unit tests included
- [ ] Tested against historical data with replay

---

## Cost Monitoring and Alerts

Proactive monitoring prevents unexpected billing and enables budget management.

### Usage Alerts Extension

The Usage Alerts extension automatically monitors billing SKUs and creates detections when thresholds are exceeded.

#### Enabling Usage Alerts

**Web UI:**
1. Navigate to Add-ons → Extensions
2. Search for "Usage Alerts"
3. Click Subscribe

**Marketplace Link:**
https://app.limacharlie.io/add-ons/extension-detail/ext-usage-alerts

#### Creating Usage Alerts

##### Via Web UI

1. Navigate to Usage Alerts extension page
2. Click "Add New Usage Alert"
3. Configure:
   - **Name**: Descriptive alert name
   - **SKU**: Billing SKU to monitor
   - **Limit**: Threshold value
   - **Timeframe**: Period in minutes (max 43200 = 30 days)
4. Click Save
5. Click "Sync Usage Alert Rules" for immediate activation

##### Via Infrastructure as Code

```yaml
hives:
  extension_config:
    ext-usage-alerts:
      data:
        usage_alert_rules:
          - enabled: true
            limit: 1024               # 1GB
            name: Output data over threshold
            sku: output_data
            timeframe: 43200          # 30 days
          - enabled: true
            limit: 100
            name: Artifact quota reached
            sku: artifact_quota
            timeframe: 43200
          - enabled: true
            limit: 10000000           # 10 million
            name: Query events threshold
            sku: query_events
            timeframe: 10080          # 7 days
```

#### How Usage Alerts Work

1. **Alert Rule Created**: User defines SKU, limit, timeframe
2. **Synced Hourly**: Extension syncs rules to managed D&R rules
3. **Billing Events Monitored**: D&R rule watches `billing_record` events
4. **Threshold Detection**: Suppression tracks cumulative usage
5. **Detection Created**: Alert fired when threshold exceeded

**Generated D&R Rule Example:**
```yaml
detect:
  event: billing_record
  op: and
  target: billing
  rules:
    - op: is
      path: event/record/cat
      value: output
    - op: is
      path: event/record/k
      value: bytes_tx
respond:
  - action: report
    name: Usage alert - Output data over threshold - 1024 MB in 30.00 days
    suppression:
      count_path: event/record/v
      keys:
        - output
        - bytes_tx
        - ext-usage-alerts
        - Output data over threshold
      max_count: 1073741824        # 1GB in bytes
      min_count: 1073741824
      period: 43200m               # 30 days
```

### Common Billing SKUs

| SKU | Description | Unit |
|-----|-------------|------|
| `output_data` | Output data transmitted | Bytes |
| `artifact_quota` | Artifact storage quota | Count |
| `query_events` | Events evaluated in queries | Count |
| `sensor_events` | Sensor events processed | Count |
| `sensor_retained` | Sensor events retained | Count |
| `payload_data_sent` | Payload data sent to endpoints | Bytes |
| `ext-*` | Extension-specific usage | Varies |

### Usage Alert Examples

#### Example 1: Output Data Threshold

**Scenario:** Alert when output data exceeds 100GB in 30 days

```yaml
- enabled: true
  limit: 107374182400           # 100GB in bytes
  name: Output data threshold
  sku: output_data
  timeframe: 43200              # 30 days
```

**Result:** Detection created when 100GB transmitted.

#### Example 2: Artifact Storage Limit

**Scenario:** Alert when artifact storage reaches 50GB

```yaml
- enabled: true
  limit: 53687091200            # 50GB in bytes
  name: Artifact storage limit
  sku: artifact_quota
  timeframe: 43200
```

#### Example 3: Query Cost Control

**Scenario:** Alert when query events exceed 50 million in 7 days

```yaml
- enabled: true
  limit: 50000000
  name: Query events threshold
  sku: query_events
  timeframe: 10080              # 7 days
```

**Result:** Detection when expensive queries consume too much.

#### Example 4: Extension Usage Monitoring

**Scenario:** Monitor VirusTotal API usage

```yaml
- enabled: true
  limit: 1000
  name: VirusTotal lookups threshold
  sku: ext-vt:lookups
  timeframe: 43200
```

### Responding to Usage Alerts

When usage alert fires:

1. **Investigate Source**:
   - Check which outputs/extensions/queries caused spike
   - Review recent configuration changes
   - Identify unexpected behavior

2. **Implement Mitigation**:
   - Optimize outputs (see Output Cost Optimization)
   - Optimize queries (see Query Optimization)
   - Add suppression to high-volume rules
   - Disable unnecessary outputs/extensions temporarily

3. **Adjust Thresholds**:
   - If alert is expected usage, increase limit
   - If alert is anomalous, investigate root cause

4. **Route Alerts**:
   - Forward usage alerts to Slack for team visibility
   - Create runbooks for common usage spikes

### Proactive Cost Monitoring

#### Weekly Usage Review

Schedule regular reviews:

**Web UI:**
1. Navigate to Billing & Usage
2. Review Metered Usage section
3. Identify trends and anomalies

**API/SDK:**
```python
import limacharlie

lc = limacharlie.Manager()
org = lc.organization('YOUR_OID')
usage = org.usage()

# Analyze usage patterns
for sku, data in usage.items():
    print(f"{sku}: {data}")
```

#### Budget Forecasting

Based on usage trends, forecast monthly costs:

1. **Track Growth**: Monitor sensor count, event volume trends
2. **Project Costs**: Extrapolate based on current usage
3. **Set Budgets**: Define acceptable cost ranges
4. **Alert on Deviation**: Use usage alerts to catch overages

#### Usage Optimization Workflow

1. **Monitor**: Track usage via alerts and dashboards
2. **Analyze**: Identify high-cost components
3. **Optimize**: Apply optimization techniques
4. **Measure**: Verify cost reduction
5. **Iterate**: Continuously improve

### Cost Attribution

For multi-tenant or departmental cost tracking:

**Strategy:**
1. Use separate organizations per department/client
2. Tag sensors by cost center
3. Use outputs per department
4. Track usage per organization

**Benefits:**
- Accurate cost attribution
- Chargebacks to departments
- Budget accountability
- Granular cost control

---

## Best Practices

### Comprehensive Optimization Strategy

#### 1. Baseline Assessment

Before optimizing:

**Assess Current State:**
- Review current billing
- Identify largest cost components
- Document sensor inventory
- Audit outputs and rules
- Check query patterns

**Example:**
- Sensors: 500 (quota-based)
- Output data: 200GB/month
- Query events: 100M/month
- Extensions: 5 active
- Total cost: $X/month

#### 2. Set Optimization Goals

Define targets:

**Example Goals:**
- Reduce output costs by 50%
- Optimize queries to <50M events/month
- Remove 20% stale sensors
- Reduce detection volume by 30%

#### 3. Prioritize Optimizations

Focus on highest impact:

**Impact Matrix:**
| Optimization | Cost Reduction | Effort | Priority |
|-------------|----------------|--------|----------|
| GCP same-region outputs | High | Low | 1 |
| Sensor culling | Medium | Low | 2 |
| Query optimization | Medium | Medium | 3 |
| Rule suppression | Medium | Medium | 4 |
| Detection stream vs. event stream | High | Medium | 5 |

#### 4. Implement Incrementally

Roll out changes gradually:

**Phase 1: Quick Wins**
- Enable sensor culling
- Switch to GCP same-region outputs
- Add usage alerts

**Phase 2: Rule Optimization**
- Audit D&R rules
- Add suppression to high-volume rules
- Optimize expensive rules

**Phase 3: Query Optimization**
- Review saved queries
- Optimize common searches
- Train team on efficient querying

**Phase 4: Architecture Changes**
- Reevaluate output strategy
- Consider detection-only forwarding
- Implement aggregation patterns

#### 5. Measure and Iterate

Track results:

**Metrics:**
- Cost reduction (%)
- Performance improvement
- Detection quality (false positive rate)
- Operational efficiency

**Review Cycle:**
- Weekly: Usage alerts and anomalies
- Monthly: Cost trends and optimization opportunities
- Quarterly: Comprehensive audit and strategy adjustment

### Platform-Specific Optimizations

#### Windows Optimization

**Challenge:** High event volume from Windows endpoints

**Optimizations:**
1. **Performance Mode**: Use `low` mode for workstations, `normal` for servers
2. **Event Suppression**: Suppress noisy event types (e.g., DNS_REQUEST on servers)
3. **Targeted FIM**: Monitor only critical paths, not entire filesystem
4. **WEL Filtering**: Forward only security-relevant Windows Event Logs

#### Linux Optimization

**Challenge:** Container/VM churn creates sensor sprawl

**Optimizations:**
1. **Sensor Culling**: Aggressive TTLs (1-3 days) for containers
2. **Tag-Based Rules**: Different rules for containers vs. bare metal
3. **Minimal Telemetry**: Use `low` performance mode for containers
4. **Network Optimization**: Reduce DNS_REQUEST forwarding

#### macOS Optimization

**Challenge:** Limited deployment, lower event volume

**Optimizations:**
1. **Standard Configuration**: Use `normal` performance mode
2. **Targeted Detection**: macOS-specific threat detections
3. **Reasonable Culling**: 60-90 day TTL for laptops (may be powered off)

#### Cloud/Container Optimization

**Challenge:** Ephemeral workloads, high sensor churn

**Optimizations:**
1. **Aggressive Culling**: 1-day TTL for pods/containers
2. **Tag-Based Classification**: Separate installation keys for ephemeral vs. persistent
3. **Minimal Event Collection**: Reduce telemetry for short-lived workloads
4. **Consolidated Detection**: Detect at orchestration layer, not per-container

### Multi-Org Optimization

For MSPs, MSSPs, or enterprises with multiple organizations:

#### Unified Billing

**Benefits:**
- Single invoice for all organizations
- Centralized billing management
- Consistent billing cycle
- ACH or manual invoicing options

**Setup:**
- Contact LimaCharlie sales
- Requires shared email domain
- Organizations grouped by billing domain

#### Cross-Org Cost Management

**Strategies:**
1. **Standardized Configurations**: Use IaC for consistent deployments
2. **Shared Outputs**: Route multiple orgs through single GCP hub
3. **Centralized Monitoring**: Aggregate usage alerts across orgs
4. **Template Approach**: Define org templates with optimized defaults

### Development vs. Production

#### Development/Test Organizations

**Cost Optimization:**
- **Sleeper Mode**: Deploy with `lc:sleeper` for dormant periods
- **Minimal Retention**: Disable Insight (1-year retention)
- **Local Outputs**: No external forwarding
- **Aggressive Culling**: 7-day TTL
- **Usage-Based Billing**: Pay only when active

#### Production Organizations

**Cost Optimization:**
- **Quota-Based Billing**: Predictable costs
- **Retention Included**: Leverage 1-year storage
- **Optimized Outputs**: GCP same-region or detection-only
- **Conservative Culling**: 90-day TTL for servers
- **Performance Mode**: Tag-based, per endpoint type

### Team Optimization

#### Training and Documentation

**Key Areas:**
1. **Query Optimization**: Train analysts on efficient LCQL
2. **Rule Design**: Best practices for D&R rule performance
3. **Cost Awareness**: Educate team on billing model
4. **Output Strategy**: Understand when to forward vs. retain

**Resources:**
- Internal runbooks
- Optimization guidelines
- Query templates
- Rule libraries

#### Governance and Policy

**Establish Policies:**
1. **Query Guidelines**: Time range limits, required filters
2. **Rule Review**: Approval process for new D&R rules
3. **Output Approval**: Evaluate cost before adding outputs
4. **Usage Review**: Regular cost review cadence

#### Automation

**Automate Common Tasks:**
1. **Sensor Culling**: Automatic via extension
2. **Usage Alerts**: Proactive cost monitoring
3. **Reporting**: Scheduled usage reports
4. **Compliance**: Automated compliance checks

### Optimization Maintenance

#### Continuous Improvement

**Ongoing Activities:**
1. **Monitor Usage**: Weekly usage alert review
2. **Audit Rules**: Quarterly D&R rule review
3. **Optimize Queries**: Update saved searches as patterns change
4. **Review Outputs**: Validate output necessity semi-annually
5. **Update Documentation**: Keep runbooks current

#### Stay Current

**Keep Up with Platform Changes:**
1. **New Features**: Leverage new optimization capabilities
2. **Pricing Updates**: Adjust strategies based on pricing changes
3. **Best Practices**: Adopt emerging best practices
4. **Community**: Engage with LimaCharlie community for tips

---

## Optimization Examples

### Example 1: Reducing Output Costs by 90%

**Scenario:**
- Current: 100GB/month output to Splunk
- Cost: $X/month (based on LimaCharlie pricing)
- Goal: Reduce to <10GB/month

**Initial State:**
```yaml
# Output configuration
name: splunk-output
stream: event           # ALL events forwarded
destination: splunk
```

**Analysis:**
- Forwarding all events to Splunk
- Most events are not security-relevant
- Splunk also charges for ingestion

**Optimization Steps:**

**Step 1:** Switch to detection-only forwarding
```yaml
# Output configuration
name: splunk-output
stream: detection       # Only detections forwarded
destination: splunk
```
**Result:** Reduced from 100GB to 5GB (~95% reduction)

**Step 2:** Add tailored output for high-value events
```yaml
# Additional output for specific events
name: splunk-high-value
stream: tailored
destination: splunk
```

D&R rule for tailored forwarding:
```yaml
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

**Result:**
- Detections: 2GB
- High-value events: 3GB
- Total: 5GB (95% reduction from 100GB)
- **Cost Savings: ~90%**

**Additional Step:** Consider GCP hub
```yaml
# Route through GCS (same region = FREE)
name: gcs-archive
type: gcs
bucket: security-logs
region: us-central1

# Then export from GCS to Splunk (uses GCP egress rates)
```
**Result:** Eliminate LimaCharlie output costs entirely.

### Example 2: Query Optimization (50x Cost Reduction)

**Scenario:**
- Frequent threat hunting queries
- Average query: $5 cost (10M events evaluated)
- Goal: Reduce query costs by 90%

**Bad Query:**
```
-7d | * | event/* contains "malware.exe"
```
- Time range: 7 days
- Event types: ALL
- Field: Wildcard
- Events evaluated: 100M
- Estimated cost: $50

**Optimization Process:**

**Step 1:** Reduce time range
```
-24h | * | event/* contains "malware.exe"
```
- Events evaluated: 14M
- Cost: $7
- **Reduction: 7x**

**Step 2:** Specify event type
```
-24h | NEW_PROCESS | event/* contains "malware.exe"
```
- Events evaluated: 2M
- Cost: $1
- **Reduction: 50x from original**

**Step 3:** Specify field path
```
-24h | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```
- Events evaluated: 2M
- Cost: $1 (same, but faster execution)
- **Total Reduction: 50x**

**Step 4:** Add platform filter
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe"
```
- Events evaluated: 1.5M
- Cost: $0.75
- **Total Reduction: 66x**

**Step 5:** Use aggregation
```
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware.exe" |
  event/FILE_PATH as path
  routing/hostname as host
  COUNT(event) as count
  GROUP BY(path host)
```
- Events evaluated: 1.5M
- Cost: $0.75
- Result size: Small summary vs. all matching events
- **Total Reduction: 66x + faster results**

**Outcome:**
- Original cost: $50
- Optimized cost: $0.75
- **Savings: 98.5%**
- **Bonus:** Faster query execution, easier analysis

### Example 3: Sensor Culling (20% Quota Reduction)

**Scenario:**
- Current quota: 500 sensors
- Active sensors: ~400 consistently
- Stale sensors: ~100 (cloud VMs, dev systems)
- Monthly cost: $500 (example)

**Analysis:**
- 20% of quota wasted on stale sensors
- Mix of cloud VMs (ephemeral) and forgotten dev VMs

**Implementation:**

**Step 1:** Identify sensor types
- Cloud VMs: Tagged `cloud-vm`
- Dev systems: Tagged `development`
- Production: Tagged `production`
- VIP: Tagged `vip`

**Step 2:** Create cull rules
```json
// Cloud VMs (ephemeral)
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}

// Development systems
{
  "action": "add_rule",
  "name": "cull-dev-systems",
  "tag": "development",
  "ttl": 14
}

// Production (conservative)
{
  "action": "add_rule",
  "name": "cull-old-production",
  "tag": "production",
  "ttl": 90
}

// VIP: No cull rule (never remove)
```

**Step 3:** Monitor initial run
```json
{
  "action": "run"
}
```

**Results:**
- Cloud VMs culled: 60 sensors
- Dev systems culled: 30 sensors
- Production culled: 10 sensors (long-decommissioned)
- Total culled: 100 sensors

**Step 4:** Reduce quota
- Old quota: 500
- New quota: 400
- Buffer: Maintained

**Outcome:**
- Quota reduced from 500 to 400
- Monthly cost: $500 → $400
- **Savings: $100/month = $1,200/year**
- **ROI: Immediate**
- Ongoing: Automatic culling prevents re-accumulation

### Example 4: Rule Optimization (Detection Volume Reduction)

**Scenario:**
- Rule generating 10,000 detections/day
- Mostly duplicates (same hash, same behavior)
- SIEM overwhelmed with alerts
- Analysts experiencing alert fatigue

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

**Analysis:**
- No suppression
- Same process detected repeatedly
- Every instance forwarded to SIEM

**Optimization:**

**Step 1:** Add suppression to report
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

**Result:**
- Detection volume: 10,000/day → 240/day (per unique hash per hour)
- **Reduction: 97.6%**

**Step 2:** Add threshold activation
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

**Result:**
- Only alerts if process seen 3+ times in 1 hour
- Filters out one-off anomalies
- **Further Reduction: ~30%**

**Outcome:**
- Original: 10,000 detections/day
- Optimized: ~170 detections/day
- **Reduction: 98.3%**
- **Benefits:**
  - Reduced analyst alert fatigue
  - Lower SIEM ingestion costs
  - Focused on persistent threats
  - Maintained detection coverage

### Example 5: Comprehensive Organization Optimization

**Scenario:**
- Organization: 300 sensors (mixed Windows, Linux, cloud)
- Current monthly cost: $2,000 (example)
- Goal: Reduce costs by 30-40% without sacrificing security

**Initial Baseline:**
- Sensors: 300 quota (250 active, 50 stale)
- Outputs: 150GB/month to Splunk ($X)
- Queries: 200M events/month ($Y)
- Extensions: 5 active
- Detections: 50,000/month

**Phase 1: Sensor Culling**

**Action:**
- Implement sensor culling rules
- Cloud VMs: 3-day TTL
- Dev systems: 14-day TTL
- Production: 90-day TTL

**Result:**
- 50 stale sensors removed
- Quota reduced: 300 → 250
- **Savings: $50/month**

**Phase 2: Output Optimization**

**Action:**
- Switch to GCS (us-central1) for free output
- Forward detections + critical events only
- Use detection stream instead of event stream

**Before:**
```yaml
stream: event    # 150GB/month
```

**After:**
```yaml
stream: detection    # 3GB/month
```

**Result:**
- Output volume: 150GB → 3GB
- LimaCharlie output cost: $X → $0 (GCS same-region)
- **Savings: $X/month** (based on output pricing)

**Phase 3: Rule Optimization**

**Action:**
- Audit all D&R rules
- Add suppression to top 10 noisiest rules
- Implement threshold activation for behavioral detections
- Create FP rules for known benign activity

**Result:**
- Detection volume: 50,000/month → 15,000/month
- **Reduction: 70%**
- Lower SIEM ingestion costs (if applicable)

**Phase 4: Query Optimization**

**Action:**
- Review common queries
- Update saved searches with optimizations
- Train team on efficient querying
- Implement query guidelines

**Result:**
- Query events: 200M/month → 80M/month
- **Reduction: 60%**
- **Savings: $Y/month** (based on query pricing)

**Phase 5: Performance Mode Optimization**

**Action:**
- Tag-based performance mode assignment
- VIP endpoints: `high` mode (10 sensors)
- Servers: `normal` mode (80 sensors)
- Workstations: `low` mode (160 sensors)

**Result:**
- Reduced event volume from workstations
- Lower storage and processing costs
- Maintained high visibility for critical assets

**Total Outcome:**

| Component | Before | After | Savings |
|-----------|--------|-------|---------|
| Sensors | 300 quota | 250 quota | $50/month |
| Outputs | 150GB | 3GB (free) | $X/month |
| Queries | 200M events | 80M events | $Y/month |
| Detections | 50,000/month | 15,000/month | Downstream savings |
| **Total** | **$2,000/month** | **~$1,200/month** | **~$800/month (40%)** |

**Annual Savings: ~$9,600**

**Additional Benefits:**
- Improved SIEM performance (70% fewer detections)
- Better analyst efficiency (less alert fatigue)
- Maintained security coverage
- Cleaner sensor inventory
- Better cost visibility

---

## When to Use This Skill

Use the performance-optimizer skill when users ask about:

- Reducing LimaCharlie costs
- Optimizing billing and usage
- Lowering output costs
- Query optimization and cost reduction
- Performance tuning
- Sensor management and culling
- Event suppression strategies
- Detection volume reduction
- Rule optimization
- Cost monitoring and alerts
- Budget management
- Usage-based vs. quota-based billing
- Billing model questions
- Extension cost management
- LCQL query performance
- Output architecture
- Multi-tenant cost optimization
- Development vs. production cost strategies
- Performance mode configuration
- Identifying cost drivers
- Usage forecasting
- Cost attribution

This skill provides comprehensive guidance for optimizing LimaCharlie deployments for cost, performance, and operational efficiency while maintaining strong security posture.
