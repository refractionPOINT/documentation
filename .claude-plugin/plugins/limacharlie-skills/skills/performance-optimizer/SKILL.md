---
name: performance-optimizer
description: Help users optimize LimaCharlie performance, reduce costs, manage billing, and implement efficient resource management strategies.
---

# LimaCharlie Performance and Cost Optimizer

This skill helps users optimize LimaCharlie performance, reduce operational costs, and implement efficient resource management. Use this skill when users ask about cost reduction, billing optimization, performance tuning, query optimization, or resource management.

## Navigation

- **[REFERENCE.md](./REFERENCE.md)** - Complete billing SKU reference, configuration details, performance modes, suppression syntax
- **[EXAMPLES.md](./EXAMPLES.md)** - Real-world optimization scenarios with before/after comparisons
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and debugging steps

## Introduction

LimaCharlie offers flexible, usage-based pricing alongside traditional quota-based billing. Understanding the billing model and implementing optimization strategies can significantly reduce costs while maintaining security effectiveness.

### Key Cost Components

1. **Sensors**: Per-endpoint quota or usage-based billing
2. **Event Processing**: Events processed by the platform
3. **Event Storage**: Telemetry data storage
4. **Outputs**: Data egress to external systems
5. **Extensions**: Additional services and integrations
6. **Queries**: Events evaluated during historical searches
7. **Artifacts**: File collection and storage
8. **Payloads**: Data sent to endpoints

---

## Quick Wins: Top 5 Optimization Techniques

### 1. Use GCP Same-Region Outputs (Zero Cost)

**Impact**: Eliminate output costs entirely

GCP outputs in the same region as your LimaCharlie datacenter are **FREE**:

| Datacenter | Free Region |
|------------|-------------|
| USA | us-central1 |
| Canada | northamerica-northeast1 |
| Europe | europe-west4 |
| UK | europe-west2 |
| India | asia-south1 |
| Australia | australia-southeast1 |

**Free mechanisms**: Google Cloud Storage, Pub/Sub, BigQuery

```yaml
# Example: Output to GCS (USA datacenter)
type: gcs
bucket: my-security-logs
region: us-central1  # FREE
```

### 2. Enable Sensor Culling

**Impact**: Reduce quota costs by 10-20%

Automatically remove stale sensors that haven't connected.

```json
{
  "action": "add_rule",
  "name": "cull-cloud-vms",
  "tag": "cloud-vm",
  "ttl": 3
}
```

Navigate to Add-ons → Extensions → "Sensor Cull" to enable.

### 3. Forward Detections Only

**Impact**: 90-99% output volume reduction

```yaml
# Bad: Forwards ALL events
stream: event

# Good: Forwards only alerts
stream: detection
```

Typical reduction: 100GB/month → 2-5GB/month

### 4. Optimize Query Time Ranges

**Impact**: 10-100x query cost reduction

```
# Bad: 30 days of data
-30d | NEW_PROCESS | event/FILE_PATH contains "malware"

# Good: 4 hours with platform filter
-4h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "malware"
```

### 5. Add Suppression to Noisy Rules

**Impact**: 50-95% detection volume reduction

```yaml
- action: report
  name: suspicious-process
  suppression:
    max_count: 1
    period: 1h
    is_global: true
    keys:
      - '{{ .event.HASH }}'
```

---

## Core Concepts

### Billing Models

**Quota-Based (vSensors)**
- Fixed monthly fee per vSensor
- Includes 1 year telemetry storage
- Best for: Stable deployments

**Usage-Based**
- Pay for sensor time + events
- No quota limits
- Best for: Variable workloads

**Sleeper Mode**
- $0.10 per sensor per 30 days
- Minimal telemetry until activated
- Best for: Incident response readiness

### Performance Modes

| Mode | CPU | Event Volume | Use Case |
|------|-----|--------------|----------|
| Low | ~1-2% | Minimal | IoT, legacy systems |
| Normal | ~2-5% | Standard | General monitoring |
| High | ~5-10% | Maximum | VIP endpoints |

```
set_performance_mode --mode low
```

See [REFERENCE.md](./REFERENCE.md) for automation with D&R rules.

### Event Suppression

Control how often D&R rules trigger:

```yaml
suppression:
  max_count: 1          # Max executions
  period: 1h            # Time window
  is_global: true       # Org-wide
  keys:
    - '{{ .event.FILE_PATH }}'
```

See [REFERENCE.md](./REFERENCE.md) for complete syntax.

---

## 5 Common Workflows

### Workflow 1: Reduce Output Costs by 90%+

**Scenario**: High costs from forwarding all events to SIEM

**Steps**:
1. Navigate to Organization Setup → Billing & Usage
2. Note current output_data (GB/month)
3. Change output: `stream: detection` (instead of `event`)
4. For zero cost, use GCP same-region (see Quick Win #1)

**Result**: 90-99% cost reduction

### Workflow 2: Optimize Expensive Queries

**Scenario**: Queries consuming too many events

**Steps**:
1. Check query cost estimation in web UI
2. Apply filters in order:
   - Smallest time range (`-4h`)
   - Platform filter (`plat == windows`)
   - Event type (`NEW_PROCESS`)
   - Specific fields (`event/FILE_PATH`)
3. Use aggregations: `COUNT`, `GROUP BY`, `LIMIT`
4. Save optimized query

**Result**: 10-100x cost reduction

### Workflow 3: Clean Up Stale Sensors

**Scenario**: Quota waste from inactive sensors

**Steps**:
1. Enable Sensor Cull extension
2. Create rules by deployment type:
   - Cloud VMs: 3-day TTL
   - Dev systems: 14-day TTL
   - Production: 90-day TTL
3. Run ad-hoc cleanup first (test)
4. Monitor via detection events
5. Reduce quota after cleanup

**Result**: 10-20% quota reduction

### Workflow 4: Reduce Detection Noise

**Scenario**: Thousands of duplicate alerts

**Steps**:
1. Identify noisy rule (Detections page)
2. Add suppression with unique keys (hash, domain, etc.)
3. Use threshold activation: `min_count: 5`
4. Create false positive rules for known benign activity

**Result**: 50-95% detection volume reduction

### Workflow 5: Set Up Cost Monitoring

**Scenario**: Need proactive cost alerts

**Steps**:
1. Enable Usage Alerts extension
2. Create alerts for key SKUs:
   - `output_data`: 100GB/30 days
   - `query_events`: 50M/7 days
3. Route alerts to team
4. Review weekly
5. Investigate and optimize when alerted

**Result**: Proactive cost control

---

## Quick Reference Cheat Sheet

### Query Optimization
```
-4h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "target"

Principles:
- Smallest time range
- Platform filter early
- Specific event types
- No wildcards
- Aggregate results
```

### Suppression Basics
```yaml
suppression:
  max_count: 1
  period: 1h
  is_global: true
  keys:
    - '{{ .event.HASH }}'
    - 'static-id'
```

### Performance Modes
```
set_performance_mode --mode low|normal|high
```

### Sensor Cull
```json
{"action": "add_rule", "name": "rule", "tag": "sensor-tag", "ttl": 7}
{"action": "del_rule", "name": "rule"}
{"action": "get_rules"}
{"action": "run"}
```

### Free Output Regions
- USA → us-central1
- Europe → europe-west4
- Canada → northamerica-northeast1

### Common Billing SKUs
- `output_data` - Output bytes
- `query_events` - Query evaluations
- `sensor_events` - Events processed
- `artifact_quota` - Artifact storage

---

## Best Practices

### General
1. Start with quick wins (GCP outputs, sensor culling)
2. Monitor before optimizing
3. Test changes on small scale first
4. Measure results
5. Regular reviews and iteration

### Rule Design
- Specify event types
- Platform filters early
- Most restrictive conditions first
- Suppression on sensor commands
- Meaningful suppression keys

### Query Design
- Smallest time range needed
- Platform + event type filters
- Specific field paths
- Aggregate instead of raw results
- Save optimized queries

### Output Strategy
- Forward detections, not events
- Use GCP same-region
- Apply suppression
- Aggregate before forwarding
- Review regularly

### Sensor Management
- Tag by type/deployment
- Cull rules per tag
- Conservative TTLs initially
- Exclude critical systems
- Monitor culling activity

---

## Troubleshooting

For detailed guides, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

**High output costs**: Check stream type, GCP region, forwarding rules
**Expensive queries**: Reduce time range, add filters, specific paths
**Quota waste**: Enable culling, review sensors, reduce quota
**Detection noise**: Add suppression, threshold activation, FP rules

---

## Additional Resources

### Documentation
- **[REFERENCE.md](./REFERENCE.md)** - Complete technical reference
- **[EXAMPLES.md](./EXAMPLES.md)** - 5 complete optimization examples
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Detailed troubleshooting

### External Links
- Pricing: https://limacharlie.io/pricing
- Sensor Cull: https://app.limacharlie.io/add-ons/extension-detail/ext-sensor-cull
- Usage Alerts: https://app.limacharlie.io/add-ons/extension-detail/ext-usage-alerts

### API Access
```bash
curl https://api.limacharlie.io/v1/usage/YOUR_OID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

```python
import limacharlie
lc = limacharlie.Manager()
org = lc.organization('YOUR_OID')
usage = org.usage()
```

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
- Billing model questions
- Extension cost management
- Output architecture
- Performance mode configuration
- Usage forecasting
- Cost attribution

This skill provides comprehensive guidance for optimizing LimaCharlie deployments for cost, performance, and operational efficiency while maintaining strong security posture.
