# Behavioral Detection

## Overview

LimaCharlie supports behavioral detection patterns using D&R rules and the suppression system. These patterns detect anomalous behavior — like a user logging in from a new country or a host resolving an unusual domain — without requiring external analytics infrastructure.

This page covers:

- **First-Seen Detection** — alert the first time a specific combination of entity + behavior is observed
- **Cardinality Detection** — alert when an entity exceeds a threshold of unique values (e.g., unique domains, unique hosts)
- **Volume Detection** — alert when a cumulative metric (e.g., bytes transferred) crosses a threshold
- **Multi-Signal Aggregation** — combine multiple detection signals into a composite risk indicator

All patterns use the existing D&R rules engine and [suppression](../8-reference/response-actions.md#suppression) system.

## First-Seen Detection

Suppression with `max_count: 1` fires an action exactly once per unique key combination per time window. This makes it a first-seen detector: the first time a `(entity, value)` pair is observed, the action fires. For the rest of the window, it is suppressed.

### First-Seen with Event Fields

When the value you want to track is directly in the event, a single rule is sufficient.

**First time a host resolves a domain (within 30 days):**

```yaml
detect:
  event: DNS_REQUEST
  op: exists
  path: event/DOMAIN_NAME

respond:
  - action: report
    name: new-domain-for-host
    suppression:
      max_count: 1
      period: 720h
      is_global: false
      keys:
        - 'first-domain'
        - '{{ .event.DOMAIN_NAME }}'
```

The suppression key combines a constant label with the domain name, scoped per-sensor (`is_global: false`). The first DNS request for a given domain on a given sensor fires the report. Subsequent requests for the same domain on the same sensor are suppressed for 30 days.

**First time a process hash runs on a host:**

```yaml
detect:
  event: NEW_PROCESS
  op: exists
  path: event/HASH

respond:
  - action: report
    name: new-process-hash-on-host
    suppression:
      max_count: 1
      period: 720h
      is_global: false
      keys:
        - 'first-process'
        - '{{ .event.HASH }}'
```

**First time a user logs in from a new source IP (org-wide):**

```yaml
detect:
  event: USER_LOGIN
  op: exists
  path: event/USER_NAME

respond:
  - action: report
    name: new-login-source-for-user
    suppression:
      max_count: 1
      period: 720h
      is_global: true
      keys:
        - 'first-login-src'
        - '{{ .event.USER_NAME }}'
        - '{{ .event.SOURCE_IP }}'
```

Using `is_global: true` means the suppression is org-wide — the counter is shared across all sensors. This is important for user-scoped detections where the user may log in from different sensors.

### First-Seen with Lookup Metadata

When the value you want to track is derived from a lookup (e.g., a GeoIP country from an IP address), the lookup metadata can be referenced in suppression key templates using the `.mtd` namespace.

The `.mtd` namespace contains the metadata returned by the detection's lookup operator. The key name is the resource name with special characters replaced by underscores. For the [IP Geolocation](../5-integrations/api-integrations/ip-geolocation.md) lookup (`lcr://api/ip-geo`), the metadata is available under `.mtd.lcr___api_ip_geo`.

**First time a user logs in from a new country:**

```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/SOURCE_IP
  resource: lcr://api/ip-geo

respond:
  - action: report
    name: first-login-from-country
    suppression:
      max_count: 1
      period: 720h
      is_global: true
      keys:
        - 'first-country'
        - '{{ .event.USER_NAME }}'
        - '{{ .mtd.lcr___api_ip_geo.country.iso_code }}'
```

This rule:

1. Matches every `USER_LOGIN` event
2. Looks up the `SOURCE_IP` via the GeoIP API
3. Generates a suppression key from the user name and the resolved country ISO code
4. Reports once per unique `(user, country)` combination per 30 days

**First time a user logs in from a new ASN:**

```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/SOURCE_IP
  resource: lcr://api/ip-geo

respond:
  - action: report
    name: first-login-from-asn
    suppression:
      max_count: 1
      period: 720h
      is_global: true
      keys:
        - 'first-asn'
        - '{{ .event.USER_NAME }}'
        - '{{ .mtd.lcr___api_ip_geo.autonomous_system.number }}'
```

**First time a threat-intel-matched hash appears on a host:**

```yaml
detect:
  event: NEW_PROCESS
  op: lookup
  path: event/HASH
  resource: hive://lookup/threat-intel-hashes

respond:
  - action: report
    name: first-ti-match-on-host
    suppression:
      max_count: 1
      period: 720h
      is_global: false
      keys:
        - 'first-ti-hash'
        - '{{ .event.HASH }}'
        - '{{ .mtd.threat_intel_hashes.category }}'
```

> **Metadata Key Naming**
>
> The `.mtd` key name is derived from the lookup resource name with `/` and `:` replaced by `_`. For example:
>
> - `lcr://api/ip-geo` becomes `.mtd.lcr___api_ip_geo`
> - `hive://lookup/my-list` becomes `.mtd.my_list`

### Combining First-Seen with Other Operators

First-seen detection composes naturally with all D&R operators using `and`/`or`:

**First time a rare domain is resolved on a VIP host:**

```yaml
detect:
  op: and
  rules:
    - event: DNS_REQUEST
      op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/rare-domains
    - op: is tagged
      tag: vip

respond:
  - action: report
    name: rare-domain-on-vip
    priority: 1
    suppression:
      max_count: 1
      period: 720h
      is_global: false
      keys:
        - 'first-rare-domain'
        - '{{ .event.DOMAIN_NAME }}'
```

## Cardinality Detection

To detect when an entity accumulates too many unique values (e.g., a host resolving an unusual number of unique domains), use a **two-rule chaining pattern**:

1. **Rule 1 (dedup):** Reports once per unique value using `max_count: 1`
2. **Rule 2 (count):** Targets the detection from Rule 1 and counts using `min_count: N`

### Example: DGA / C2 Beaconing Detection

Detect a host resolving more than 100 unique domains in 1 hour:

```yaml
# Rule 1: Deduplicate — report once per unique domain per sensor per hour
detect:
  event: DNS_REQUEST
  op: exists
  path: event/DOMAIN_NAME

respond:
  - action: report
    name: dns-domain-observed
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - 'dns-dedup'
        - '{{ .event.DOMAIN_NAME }}'
```

```yaml
# Rule 2: Count — fire when unique domains exceed threshold
detect:
  event: dns-domain-observed
  target: detection
  op: exists
  path: detect

respond:
  - action: report
    name: excessive-dns-diversity
    suppression:
      min_count: 100
      max_count: 100
      period: 1h
      is_global: false
      keys:
        - 'dns-diversity-count'
```

Rule 1 fires once per unique domain per sensor per hour (deduplication). Rule 2 chains on the `detection` target, counting how many unique domains triggered Rule 1. When the count reaches 100, Rule 2 fires exactly once.

### Example: Lateral Movement Detection

Detect a user accessing more than 5 unique hosts in 6 hours:

```yaml
# Rule 1: Deduplicate per (user, host)
detect:
  event: USER_LOGIN
  op: exists
  path: event/USER_NAME

respond:
  - action: report
    name: user-host-access-observed
    suppression:
      max_count: 1
      period: 6h
      is_global: true
      keys:
        - 'lateral-dedup'
        - '{{ .event.USER_NAME }}'
        - '{{ .routing.hostname }}'
```

```yaml
# Rule 2: Count unique hosts per user
detect:
  event: user-host-access-observed
  target: detection
  op: exists
  path: detect

respond:
  - action: report
    name: possible-lateral-movement
    suppression:
      min_count: 5
      max_count: 5
      period: 6h
      is_global: true
      keys:
        - 'lateral-count'
        - '{{ .detect.event.USER_NAME }}'
```

### Example: Excessive External Connections

Detect a host connecting to more than 50 unique external IPs in 1 hour:

```yaml
# Rule 1: Deduplicate unique external destination IPs per sensor
detect:
  event: NEW_TCP4_CONNECTION
  op: is public address
  path: event/IP_ADDRESS

respond:
  - action: report
    name: external-conn-observed
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - 'ext-conn-dedup'
        - '{{ .event.IP_ADDRESS }}'
```

```yaml
# Rule 2: Count unique destinations per sensor
detect:
  event: external-conn-observed
  target: detection
  op: exists
  path: detect

respond:
  - action: report
    name: excessive-external-connections
    suppression:
      min_count: 50
      max_count: 50
      period: 1h
      is_global: false
      keys:
        - 'ext-conn-count'
```

## Volume Detection

The `count_path` suppression parameter increments the counter by a value extracted from the event instead of by 1. This enables threshold detection on cumulative metrics like bytes transferred.

### Example: Data Exfiltration Threshold

Alert when a host uploads more than 1 GB to external IPs in 24 hours:

```yaml
detect:
  event: USP_NETFLOW
  op: is public address
  path: event/dst_ip

respond:
  - action: report
    name: high-egress-volume
    suppression:
      min_count: 1073741824
      max_count: 1073741824
      period: 24h
      is_global: false
      count_path: event/bytes_out
      keys:
        - 'egress-volume'
```

The counter increments by the value at `event/bytes_out` for each matching event. When the cumulative bytes reach 1 GB (1,073,741,824 bytes), the report fires exactly once.

## Multi-Signal Aggregation

Multiple detection rules can feed into a shared suppression counter to create a composite risk indicator. When independent detections all report with a shared key, the counter accumulates across them.

### Example: Risk Score Aggregation

Individual indicator rules each generate a detection:

```yaml
# Rule A: Suspicious DNS resolution
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/suspicious-domains

respond:
  - action: report
    name: indicator-hit
```

```yaml
# Rule B: Sensitive process access
detect:
  event: SENSITIVE_PROCESS_ACCESS
  op: exists
  path: event/TARGET/FILE_PATH

respond:
  - action: report
    name: indicator-hit
```

Aggregation rule — fires when 5 indicators accumulate on a single host in 1 hour:

```yaml
detect:
  event: indicator-hit
  target: detection
  op: exists
  path: detect

respond:
  - action: report
    name: high-risk-host
    priority: 1
    suppression:
      min_count: 5
      max_count: 5
      period: 1h
      is_global: false
      keys:
        - 'risk-aggregation'
```

Since both Rule A and Rule B report the same detection name (`indicator-hit`), the aggregation rule counts them together. Different types of suspicious activity on the same host contribute to the same counter.

## Suppression Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_count` | integer | Maximum action executions per period per key. Use `1` for first-seen. |
| `min_count` | integer | Minimum activations before the action fires. Must be used with `max_count`. |
| `period` | string | Time window. Formats: `s`, `m`, `h`. Range: 1s to 720h (30 days). |
| `is_global` | boolean | `true` = org-wide counter. `false` (default) = per-sensor counter. |
| `keys` | list | Template strings that form the uniqueness key. Supports `{{ .event.* }}`, `{{ .routing.* }}`, and `{{ .mtd.* }}`. |
| `count_path` | string | Path to an integer in the event to use as the increment value instead of 1. |

### Template Namespaces in Keys

| Namespace | Source | Example |
|-----------|--------|---------|
| `.event.*` | Raw event payload | `{{ .event.FILE_PATH }}` |
| `.routing.*` | Event routing metadata | `{{ .routing.hostname }}` |
| `.mtd.*` | Detection metadata from lookup operators | `{{ .mtd.lcr___api_ip_geo.country.iso_code }}` |

## Limitations

- **Static thresholds only.** The thresholds (count values, periods) are user-defined constants. There is no adaptive baseline that learns "normal" from historical data.
- **Fixed time windows.** The suppression period is a fixed window that resets on expiry, not a rolling/sliding window.
- **Maximum period: 30 days.** Suppression counters reset after the period expires. "First seen within 30 days" is the longest tracking window.
- **No statistical comparison.** These patterns detect "above N" or "first occurrence" — they cannot detect "unusual compared to historical baseline."
- **Cardinality detection requires two rules.** The dedup+count pattern needs rule chaining via the `detection` target.

---

## See Also

- [D&R Rules Overview](index.md)
- [Response Actions — Suppression](../8-reference/response-actions.md#suppression)
- [Stateful Rules](stateful-rules.md)
- [IP Geolocation](../5-integrations/api-integrations/ip-geolocation.md)
- [Template Transforms](../4-data-queries/template-transforms.md)
