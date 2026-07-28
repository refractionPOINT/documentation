# Behavioral Detection

## Overview

LimaCharlie supports behavioral detection patterns with D&R rules and the suppression system. These patterns detect unusual behavior, for example a user that logs in from a new country, or a host that resolves an unusual domain. They do not need external analytics infrastructure.

This page covers:

- **First-Seen Detection** — alert the first time that a specific combination of entity and behavior occurs
- **Cardinality Detection** — alert when an entity goes above a threshold of unique values (e.g., unique domains, unique hosts)
- **Volume Detection** — alert when a cumulative metric (e.g., bytes transferred) crosses a threshold
- **Multi-Signal Aggregation** — combine multiple detection signals into a composite risk indicator

All patterns use the existing D&R rules engine and [suppression](../8-reference/response-actions.md#suppression) system.

## First-Seen Detection

Suppression with `max_count: 1` fires an action one time only for each unique key combination in each time window. This makes it a first-seen detector. The action fires the first time that an `(entity, value)` pair occurs. For the rest of the window, suppression stops the action.

### First-Seen with Event Fields

When the value that you track is in the event, one rule is enough.

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

The suppression key combines a constant label with the domain name. The scope is one sensor (`is_global: false`). The first DNS request for a domain on a sensor fires the report. Suppression stops the later requests for the same domain on the same sensor for 30 days.

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

`is_global: true` makes the suppression org-wide. All sensors share the counter. This is important for detections that are scoped to a user, because the user can log in from different sensors.

### First-Seen with Lookup Metadata

When a lookup supplies the value that you track (e.g., a GeoIP country from an IP address), you can use the lookup metadata in the suppression key templates. Use the `.mtd` namespace.

The `.mtd` namespace contains the metadata that the lookup operator of the detection returns. The key name is the resource name, with underscores in place of the special characters. For the [IP Geolocation](../5-integrations/api-integrations/ip-geolocation.md) lookup (`lcr://api/ip-geo`), the metadata is under `.mtd.lcr___api_ip_geo`.

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
2. Looks up the `SOURCE_IP` with the GeoIP API
3. Generates a suppression key from the user name and the country ISO code
4. Reports one time for each unique `(user, country)` combination in 30 days

**First time a user logs in from a new ASN:**

```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/SOURCE_IP
  resource: lcr://api/ip-asn

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
        - '{{ .mtd.lcr___api_ip_asn.autonomous_system_number }}'
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
> The `.mtd` key name comes from the lookup resource name, with `_` in place of `/` and `:`. For example:
>
> - `lcr://api/ip-geo` becomes `.mtd.lcr___api_ip_geo`
> - `lcr://api/ip-asn` becomes `.mtd.lcr___api_ip_asn`
> - `hive://lookup/my-list` becomes `.mtd.my_list`

### Combining First-Seen with Other Operators

First-seen detection combines with all D&R operators through `and`/`or`:

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

Some entities accumulate too many unique values. An example is a host that resolves an unusual number of unique domains. To detect this, use a **two-rule chaining pattern**:

1. **Rule 1 (dedup):** Reports one time for each unique value with `max_count: 1`
2. **Rule 2 (count):** Targets the detection from Rule 1 and counts with `min_count: N`

### Example: DGA / C2 Beaconing Detection

Detect a host that resolves more than 100 unique domains in 1 hour:

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

Rule 1 fires one time for each unique domain, for each sensor, in each hour (deduplication). Rule 2 chains on the `detection` target and counts the unique domains that triggered Rule 1. When the count reaches 100, Rule 2 fires one time only.

### Example: Lateral Movement Detection

Detect a user that accesses more than 5 unique hosts in 6 hours:

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

Detect a host that connects to more than 50 unique external IPs in 1 hour:

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

The `count_path` suppression parameter increments the counter by a value from the event, and not by 1. This lets you detect a threshold on cumulative metrics such as the bytes transferred.

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

The counter increments by the value at `event/bytes_out` for each matching event. When the cumulative bytes reach 1 GB (1,073,741,824 bytes), the report fires one time only.

## Multi-Signal Aggregation

Many detection rules can feed one shared suppression counter to make a composite risk indicator. When independent detections report with a shared key, the counter accumulates across them.

### Example: Risk Score Aggregation

Each indicator rule generates a detection:

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

The aggregation rule fires when 5 indicators accumulate on one host in 1 hour:

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

Because Rule A and Rule B report the same detection name (`indicator-hit`), the aggregation rule counts them together. Different types of suspicious activity on the same host add to the same counter.

## Suppression Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_count` | integer | Maximum number of times that the action runs in each period for each key. Use `1` for first-seen. |
| `min_count` | integer | Minimum number of activations before the action fires. You must use it with `max_count`. |
| `period` | string | Time window. Formats: `s`, `m`, `h`. Range: 1s to 720h (30 days). |
| `is_global` | boolean | `true` = org-wide counter. `false` (default) = per-sensor counter. |
| `keys` | list | Template strings that form the uniqueness key. Supports `{{ .event.* }}`, `{{ .routing.* }}`, and `{{ .mtd.* }}`. |
| `count_path` | string | Path to an integer in the event. The counter uses this value as the increment, and not 1. |

### Template Namespaces in Keys

| Namespace | Source | Example |
|-----------|--------|---------|
| `.event.*` | Raw event payload | `{{ .event.FILE_PATH }}` |
| `.routing.*` | Event routing metadata | `{{ .routing.hostname }}` |
| `.mtd.*` | Detection metadata from lookup operators | `{{ .mtd.lcr___api_ip_geo.country.iso_code }}` |

## Limitations

- **Static thresholds only.** The thresholds (count values, periods) are constants that you set. There is no adaptive baseline that learns "normal" from historical data.
- **Fixed time windows.** The suppression period is a fixed window that resets when it expires. It is not a rolling or sliding window.
- **Maximum period: 30 days.** Suppression counters reset after the period expires. "First seen within 30 days" is the longest tracking window.
- **No statistical comparison.** These patterns detect "above N" or "first occurrence". They cannot detect "unusual compared to historical baseline."
- **Cardinality detection needs two rules.** The dedup+count pattern needs rule chaining through the `detection` target.

---

## See Also

- [D&R Rules Overview](index.md)
- [Response Actions — Suppression](../8-reference/response-actions.md#suppression)
- [Stateful Rules](stateful-rules.md)
- [IP Geolocation](../5-integrations/api-integrations/ip-geolocation.md)
- [Template Transforms](../4-data-queries/template-transforms.md)
