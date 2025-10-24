# Performance Optimizer - Technical Reference

Complete technical reference for LimaCharlie performance optimization, billing, and configuration.

[← Back to SKILL.md](./SKILL.md)

## Table of Contents

1. [Billing Model Details](#billing-model-details)
2. [Billable Components](#billable-components)
3. [Complete Billing SKU Reference](#complete-billing-sku-reference)
4. [Performance Mode Details](#performance-mode-details)
5. [Event Suppression Syntax](#event-suppression-syntax)
6. [Output Cost Tables](#output-cost-tables)
7. [Viewing Billing Information](#viewing-billing-information)
8. [Regional Configuration](#regional-configuration)

---

## Billing Model Details

### Quota-Based Billing (vSensors)

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

### Usage-Based Billing

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

### Sleeper Mode

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

---

## Billable Components

### 1. Sensors

**Quota-based**: Fixed monthly per vSensor
**Usage-based**: Connection time + events processed/stored
**Sleeper mode**: $0.10/sensor/30 days

### 2. Event Processing

- Events evaluated by D&R rules
- Platform event processing
- Real-time telemetry ingestion

### 3. Event Storage

- Included with quota-based billing (1 year)
- Charged separately for usage-based billing
- Insight add-on extends retention

### 4. Outputs

- Data egress to external systems
- Billed per GB transmitted
- **Exception**: GCP outputs in same region are FREE
- Pricing: Check https://limacharlie.io/pricing

### 5. Queries (LCQL)

- Charged per million events evaluated
- Cost depends on query efficiency
- Time range affects total cost
- Better-tuned queries = lower cost

### 6. Artifacts

- File collection from endpoints
- Storage of collected files
- Priced per GB

### 7. Payloads

- Data sent to endpoints
- Example: $0.19 per GB
- 1GB payload to 10 endpoints = $1.90
- Impacts Atomic Red Team, Dumper extensions

### 8. Extensions

- Add-on services (Yara, VirusTotal, etc.)
- Variable pricing based on extension
- Some extensions are usage-based

---

## Complete Billing SKU Reference

### Core SKUs

| SKU | Description | Unit | Usage Context |
|-----|-------------|------|---------------|
| `sensor_quota` | vSensor quota allocation | Count | Quota-based billing |
| `sensor_events` | Events processed by sensors | Count | Usage-based billing |
| `sensor_retained` | Events stored | Count | Usage-based billing |
| `sensor_connect_time` | Sensor connection time | Seconds | Usage-based billing |
| `output_data` | Data transmitted via outputs | Bytes | All outputs except GCP same-region |
| `query_events` | Events evaluated in LCQL queries | Count | Historical searches |
| `artifact_quota` | Artifact storage used | Bytes | File collections |
| `payload_data_sent` | Data sent to endpoints | Bytes | Task payloads, extensions |

### Extension-Specific SKUs

| SKU | Description | Unit |
|-----|-------------|------|
| `ext-vt:lookups` | VirusTotal API lookups | Count |
| `ext-yara:scans` | YARA scan executions | Count |
| `ext-insight:retention` | Extended retention storage | GB/month |
| `ext-*` | Various extension-specific metrics | Varies |

### Output-Specific SKUs

| SKU | Description | Unit |
|-----|-------------|------|
| `output_data` | Generic output data | Bytes |
| `bytes_tx` | Bytes transmitted | Bytes |

---

## Performance Mode Details

### Mode Characteristics

#### Low Performance Mode

**Command:**
```
set_performance_mode --mode low
```

**Characteristics:**
- Minimal CPU and memory usage
- Reduced telemetry collection
- Lower event volume
- Suitable for resource-constrained systems

**Resource Impact:**
- CPU: ~1-2%
- Memory: ~50-100MB
- Event Volume: Minimal
- Detection Coverage: Basic

**When to use:**
- Legacy systems with limited resources
- Virtual machines with tight resource allocations
- Endpoints experiencing performance issues
- Cost-sensitive deployments
- IoT devices

#### Normal Performance Mode (Default)

**Command:**
```
set_performance_mode --mode normal
```

**Characteristics:**
- Balanced resource usage
- Standard telemetry collection
- Default configuration

**Resource Impact:**
- CPU: ~2-5%
- Memory: ~100-200MB
- Event Volume: Standard
- Detection Coverage: Standard

**When to use:**
- Standard deployments
- Typical workstations and servers
- General-purpose monitoring

#### High Performance Mode

**Command:**
```
set_performance_mode --mode high
```

**Characteristics:**
- Maximum telemetry visibility
- Higher CPU and memory usage
- Comprehensive event collection
- Enhanced detection capabilities

**Resource Impact:**
- CPU: ~5-10%
- Memory: ~200-400MB
- Event Volume: Maximum
- Detection Coverage: Comprehensive

**When to use:**
- High-value targets (VIP endpoints)
- Critical servers requiring maximum visibility
- Investigation and incident response
- Threat hunting exercises

### Automating Performance Mode with D&R Rules

#### Set High Performance for VIP Endpoints

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
        - performance-mode-set
```

#### Set Low Performance for IoT Devices

```yaml
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

---

## Event Suppression Syntax

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
- `24h` = 24 hours

### Suppression Best Practices

1. **Always Suppress Sensor Commands**: Prevent resource exhaustion
2. **Use Appropriate Scope**: Global for org-wide, per-sensor for endpoint-specific
3. **Choose Meaningful Keys**: Include relevant identifiers (hash, path, domain)
4. **Set Reasonable Periods**: Balance detection coverage vs. noise
5. **Include Detection Name**: Add static identifier to keys for clarity
6. **Test Suppression Logic**: Verify suppression works as expected
7. **Document Suppression Rationale**: Explain why suppression is needed

### Common Suppression Patterns

#### Suppress Sensor Commands

**Problem:** Repeated YARA scans waste resources.

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

#### Suppress by Hash

```yaml
suppression:
  max_count: 1
  period: 24h
  is_global: true
  keys:
    - '{{ .event.HASH }}'
    - 'detection-name'
```

#### Suppress by Domain

```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: true
  keys:
    - '{{ .event.DOMAIN_NAME }}'
    - 'malicious-domain'
```

#### Suppress Extension Calls

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

---

## Output Cost Tables

### Output Pricing Model

**General Rule:**
- Charged per GB transmitted
- Check current pricing: https://limacharlie.io/pricing
- Exception: GCP same-region outputs are FREE

### Free Output Regions

GCP outputs in the same region as your LimaCharlie datacenter are **FREE**:

| LimaCharlie Datacenter | Free GCP Region | Location |
|------------------------|-----------------|----------|
| USA | us-central1 | Iowa, USA |
| Canada | northamerica-northeast1 | Montreal, Canada |
| Europe | europe-west4 | Netherlands |
| UK | europe-west2 | London, UK |
| India | asia-south1 | Mumbai, India |
| Australia | australia-southeast1 | Sydney, Australia |

### Free GCP Output Mechanisms

1. **Google Cloud Storage (GCS)**
   ```yaml
   type: gcs
   bucket: my-security-logs
   region: us-central1  # Must match datacenter
   ```

2. **Google Pub/Sub**
   ```yaml
   type: pubsub
   project: my-project
   topic: security-events
   region: us-central1
   ```

3. **Google BigQuery**
   ```yaml
   type: bigquery
   project: my-project
   dataset: security_data
   table: events
   region: us-central1
   ```

### Output Volume Examples

| Stream Type | Typical Volume (100 sensors) | Monthly Output |
|-------------|------------------------------|----------------|
| `event` (all events) | ~1-2GB per sensor per day | 3-6TB |
| `detection` (alerts only) | ~10-50MB total per day | 300MB-1.5GB |
| `tailored` (selective) | Variable | 10-100GB |
| `audit` | ~1-10MB per day | 30-300MB |

### Cost Reduction Comparison

| Strategy | Output Volume | Cost (Example) | Savings |
|----------|---------------|----------------|---------|
| All events to paid SIEM | 3TB/month | $XXX | Baseline |
| Detections only to paid SIEM | 1GB/month | $X | 99.97% |
| All events to GCP same-region | 3TB/month | $0 | 100% |
| Detections to SIEM + Events to GCS | 1GB + 3TB free | $X | ~99% |

---

## Viewing Billing Information

### Web UI

**Steps:**
1. Navigate to Organization Setup
2. Click "Billing & Usage" tab
3. View metered usage breakdown
4. Check current quota and charges

**Available Metrics:**
- Sensor quota usage
- Output data transmitted
- Query events evaluated
- Extension usage
- Artifact storage
- Historical trends

### REST API

**Get organization usage stats:**

```bash
curl https://api.limacharlie.io/v1/usage/YOUR_OID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response format:**
```json
{
  "usage": {
    "sensor_quota": 100,
    "output_data": 10737418240,
    "query_events": 50000000,
    ...
  },
  "period": "2024-01-01T00:00:00Z"
}
```

### Python SDK

**Basic usage query:**

```python
import limacharlie

lc = limacharlie.Manager()
org = lc.organization('YOUR_OID')
usage = org.usage()

# Print all usage metrics
for sku, data in usage.items():
    print(f"{sku}: {data}")
```

**Specific metric query:**

```python
# Get output data usage
output_usage = usage.get('output_data', 0)
print(f"Output data: {output_usage / (1024**3):.2f} GB")

# Get query events
query_events = usage.get('query_events', 0)
print(f"Query events: {query_events / 1000000:.2f}M")
```

---

## Regional Configuration

### Datacenter Locations

| Region | Datacenter Location | Code |
|--------|-------------------|------|
| USA | Iowa, USA | us-central1 |
| Canada | Montreal, Canada | northamerica-northeast1 |
| Europe | Netherlands | europe-west4 |
| UK | London, UK | europe-west2 |
| India | Mumbai, India | asia-south1 |
| Australia | Sydney, Australia | australia-southeast1 |

### Selecting Your Datacenter

**During Organization Creation:**
- Choose datacenter closest to your primary operations
- Consider data residency requirements
- Cannot be changed after creation

**Impact on Costs:**
- Affects which GCP region is free for outputs
- May impact output latency to external systems
- Data residency compliance considerations

### Multi-Region Strategy

**For global deployments:**

1. **Single-Region Approach**
   - One organization in central location
   - Acceptable latency for most use cases
   - Simpler management

2. **Multi-Org Approach**
   - Separate organizations per region
   - Optimal latency and data residency
   - More complex management
   - Unified billing available (contact sales)

### Data Residency

**Compliance Considerations:**
- GDPR: Use Europe or UK datacenter for EU data
- Data sovereignty: Choose region matching requirements
- Sector-specific: Healthcare, finance may have specific needs

**What stays in region:**
- Sensor telemetry data
- Detection events
- Stored artifacts
- Audit logs

**What may leave region:**
- Outputs to external systems
- API calls from other regions
- Cross-organization integrations

---

## Advanced Configuration

### Query Cost Estimation

**Cost Model:**
- Charged per million events evaluated
- Not charged for events matched, but events evaluated
- Cost shown before query execution ("At most" estimate)

**Example Calculation:**
```
Time range: Last 24 hours
Total events in range: 10 million
Cost per million events: $X
Estimated cost: $10X
```

### Rule Performance Metrics

**Operator Performance (fastest to slowest):**
1. `is` - Exact match (fastest)
2. `exists` - Field presence check
3. `ends with` / `starts with` - Prefix/suffix match
4. `contains` - Substring search
5. `matches` - Regular expression (slowest)

**Platform Filter Impact:**
- Windows-only filter: ~40-60% of events (typical)
- Linux-only filter: ~20-40% of events
- macOS-only filter: ~5-20% of events

**Event Type Filter Impact:**
- NEW_PROCESS: ~10-20% of all events
- NETWORK_CONNECTIONS: ~20-40% of all events
- DNS_REQUEST: ~15-30% of all events
- FILE_* events: ~10-30% of all events

### Sensor Culling Recommendations

| Deployment Type | Recommended TTL | Rationale |
|----------------|-----------------|-----------|
| Cloud VMs (auto-scaling) | 1-3 days | Highly ephemeral |
| Docker containers | 1 day | Very ephemeral |
| Kubernetes pods | 1 day | Container churn |
| Development VMs | 7-14 days | Frequent rebuilds |
| Laptops/workstations | 60-90 days | May be offline for weeks |
| Servers | 90-180 days | Long maintenance windows |
| VIP endpoints | Never cull | Critical systems |

---

## Usage Alert Configuration

### Alert Rule Structure

```yaml
hives:
  extension_config:
    ext-usage-alerts:
      data:
        usage_alert_rules:
          - enabled: true
            limit: <threshold_value>
            name: <descriptive_name>
            sku: <billing_sku>
            timeframe: <minutes>
```

### Common Alert Configurations

#### Output Data Alert

```yaml
- enabled: true
  limit: 107374182400           # 100GB in bytes
  name: Output data threshold
  sku: output_data
  timeframe: 43200              # 30 days in minutes
```

#### Query Cost Alert

```yaml
- enabled: true
  limit: 50000000               # 50M events
  name: Query events threshold
  sku: query_events
  timeframe: 10080              # 7 days in minutes
```

#### Artifact Storage Alert

```yaml
- enabled: true
  limit: 53687091200            # 50GB in bytes
  name: Artifact storage limit
  sku: artifact_quota
  timeframe: 43200              # 30 days
```

#### Sensor Event Processing Alert

```yaml
- enabled: true
  limit: 1000000000             # 1B events
  name: Event processing threshold
  sku: sensor_events
  timeframe: 43200              # 30 days
```

### Alert Timeframe Limits

- Minimum: 60 minutes (1 hour)
- Maximum: 43200 minutes (30 days)
- Common values:
  - 1 hour: 60
  - 1 day: 1440
  - 7 days: 10080
  - 30 days: 43200

---

## Multi-Organization Billing

### Unified Billing

**Requirements:**
- Multiple organizations under single entity
- Shared email domain across organizations
- Contact LimaCharlie sales to enable

**Benefits:**
- Single invoice for all organizations
- Centralized billing management
- Consistent billing cycle
- ACH or manual invoicing options
- Simplified accounting

**Process:**
1. Contact sales@limacharlie.io
2. Provide list of organization IDs
3. Confirm shared email domain
4. Unified billing configured
5. Single invoice generated monthly

### Cost Attribution

**Strategy 1: Separate Organizations**
- One org per department/client
- Clear cost boundaries
- Individual billing or unified
- Granular control

**Strategy 2: Tagging Strategy**
- Single org with comprehensive tagging
- Manual cost attribution via usage analysis
- More complex tracking
- Shared resources

**Best Practice:**
- Use separate orgs for clear cost attribution
- Use unified billing for consolidated invoicing
- Tag sensors consistently for reporting

---

[← Back to SKILL.md](./SKILL.md) | [View Examples →](./EXAMPLES.md) | [Troubleshooting →](./TROUBLESHOOTING.md)
