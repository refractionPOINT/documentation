# Sensor Variables

## Overview

Sensor variables are per-sensor key-value stores that allow D&R rules to share state across different rules evaluating events from the same sensor. A response action in one rule can set a variable, and a detection operator in another rule can read it — enabling patterns like conditional suppression, cross-rule coordination, and dynamic thresholds.

Variables are:

- **Scoped per sensor** — each sensor (SID) has its own independent set of variables.
- **Stored in memory** during the sensor's connection for fast, synchronous access during rule evaluation.
- **Persisted across reconnections** — when a sensor disconnects, its variables are saved and restored when it reconnects.
- **Optionally time-limited** — variables can have a TTL (time-to-live) in seconds, after which they expire automatically.

## Setting Variables (Response Actions)

Use the `add var` response action to set a variable, and `del var` to remove one.

### add var

```yaml
- action: add var
  name: my-variable
  value: some-value
  ttl: 60  # optional, in seconds
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name`    | Yes      | Name of the variable to set. |
| `value`   | Yes      | Value to store. Can be a literal string or a [lookback](#using-lookbacks) like `<<event/FILE_PATH>>`. |
| `ttl`     | No       | Time-to-live in seconds. The variable expires after this duration. If omitted, the variable persists indefinitely (until explicitly deleted or the sensor state is flushed). |

A single variable name can hold **multiple values**. Each call to `add var` adds a value to the set. For example, calling `add var` with `name: seen-paths` and `value: <<event/FILE_PATH>>` across multiple events builds up a set of file paths.

#### TTL Behavior

The `ttl` is **per value**, not per variable. Each value carries its own absolute expiration time, computed at insert time as `now + ttl`.

- **Adding new values to the same variable:** each value gets its own independent TTL timer. Values added at different times expire at different times.
- **Re-adding a value that already exists in the set:** the TTL is **reset** (the new expiration overwrites the old one). This is useful for keeping a value "alive" as long as related activity continues — re-issue `add var` with the same value on every relevant event and it will only expire after `ttl` seconds of silence.
- **Mixing TTLs:** within a single variable, some values can be short-lived and others long-lived; they are tracked independently.
- **Omitting `ttl`:** the value persists indefinitely. Combined with the limits below, indefinite values can fill the variable up — prefer a TTL whenever the data is naturally bounded in time.

#### Limits and Overrun Behavior

A sensor can hold up to **16 variable names**, and each variable name can hold up to **32 values**.

These limits exist to keep per-sensor state bounded. **Exceeding either limit is destructive — it does not evict the oldest entry to make room.** Specifically:

| Limit exceeded | Effect |
|----------------|--------|
| The 33rd unique value is added to a single variable | The **entire variable** (all of its values) is cleared, and `add var` returns an error. The new value is also lost. |
| The 17th distinct variable name is added to a sensor | **All variables** for that sensor are cleared, and `add var` returns an error. |

Because of this, you should design rule sets so the limits are not approached in normal operation:

- Always set a `ttl` unless you are certain the value set is naturally bounded.
- If you are using `<<event/...>>` lookbacks to populate a variable from a high-cardinality field (file paths, command lines, IPs), use a short TTL so the set self-prunes.
- Do not split unrelated state across many small variables on the same sensor; combine related state where possible.

Re-adding a value that is already present is **not** counted against the value limit (it just refreshes the existing entry's TTL), so refreshing a small fixed set of values with `add var` is safe.

### del var

```yaml
- action: del var
  name: my-variable
  value: some-value
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name`    | Yes      | Name of the variable. |
| `value`   | Yes      | Specific value to remove from the variable's set. Can be a literal or a lookback. An empty string (`value: ""`) removes **all** values for the variable — see below. |

#### Removing All Values for a Variable

To clear an entire variable (for example, when you've forgotten what's in it, or want to reset state), set `value` to an empty string:

```yaml
- action: del var
  name: my-variable
  value: ""
```

This removes every value associated with `my-variable` for the sensor in a single action. It is the only way to clear a variable without enumerating its current values, since there is no API to list a sensor's variables (see [Visibility](#visibility) below).

Alternatively, use a short `ttl` on `add var` so values expire naturally without explicit deletion.

### Using Lookbacks

The `value` parameter supports lookback syntax (`<<path>>`) to extract values from the current event:

```yaml
- action: add var
  name: recently-seen-processes
  value: <<event/FILE_PATH>>
  ttl: 300
```

This stores the actual file path from the event that triggered the rule.

## Reading Variables (Detection Operators)

To reference a sensor variable in a detection rule, use the `[[variable_name]]` syntax in the `value` parameter of an operator.

When the engine evaluates the operator, `[[variable_name]]` is replaced with the **set of values** currently stored in that variable for the sensor. The operator then checks if the value at `path` matches **any** of those values.

### Supported Operators

The `[[variable_name]]` syntax works with these operators:

- `is`
- `contains`
- `starts with`
- `ends with`
- `is greater than`
- `is lower than`

### Basic Example

**Rule 1** — When a process accesses a sensitive file, remember the file path:

```yaml
# Detect
event: FILE_TYPE_ACCESSED
op: starts with
path: event/FILE_PATH
value: /etc/shadow
```

```yaml
# Respond
- action: add var
  name: sensitive-files-accessed
  value: <<event/FILE_PATH>>
  ttl: 120
```

**Rule 2** — Detect a network connection from a process that recently accessed a sensitive file:

```yaml
# Detect
event: NEW_TCP4_CONNECTION
op: is
path: event/FILE_PATH
value: '[[sensitive-files-accessed]]'
```

```yaml
# Respond
- action: report
  name: Network Activity After Sensitive File Access
```

When Rule 2 evaluates, `[[sensitive-files-accessed]]` resolves to the set of file paths stored by Rule 1. If the current event's `FILE_PATH` matches any of them, the rule fires.

### Empty Variables

If a variable has no values (it was never set, has expired, or was deleted), the `[[variable_name]]` resolves to an **empty set**. Since no value can match an empty set, the operator returns `false`.

This is useful with `not: true` — if the variable is empty, the operator returns `false`, `not` flips it to `true`, and the rule proceeds. If the variable has a matching value, the operator returns `true`, `not` flips it to `false`, and the rule is suppressed.

## Common Patterns

### Conditional Suppression: "Detect A Unless B Happened Recently"

This is the most common use case for sensor variables. You want to detect an event, but suppress the detection if a related event occurred recently.

**Example:** Detect Windows Defender real-time protection being disabled (EID 5001), but not if a managed policy change (EID 5007) occurred recently — which indicates an expected, managed change.

**Rule 1 — Flag the managed change:**

```yaml
# Detect
event: WEL
op: and
rules:
  - op: is
    path: event/EVENT/System/Channel
    value: Microsoft-Windows-Windows Defender/Operational
  - op: is
    path: event/EVENT/System/EventID
    value: '5007'
  - op: is
    path: event/EVENT/EventData/New Value
    value: >-
      HKLM\SOFTWARE\Microsoft\Windows Defender\ManagedDefenderProductType =
      0x6
```

```yaml
# Respond
- action: add var
  name: defender_managed_change
  value: '5001'
  ttl: 60
```

This stores the value `"5001"` in the variable for 60 seconds.

**Rule 2 — Detect EID 5001 unless flagged:**

```yaml
# Detect
event: WEL
op: and
rules:
  - op: is
    path: event/EVENT/System/Channel
    value: Microsoft-Windows-Windows Defender/Operational
  - op: is
    path: event/EVENT/System/EventID
    value: '5001'
  - op: is
    not: true
    path: event/EVENT/System/EventID
    value: '[[defender_managed_change]]'
```

```yaml
# Respond
- action: report
  name: Defender Realtime Protection Disabled (Unmanaged)
```

**How it works:**

| Scenario | Variable state | `is` evaluates | `not` flips to | Result |
|----------|---------------|----------------|----------------|--------|
| 5007 arrived recently | `{"5001"}` | `"5001" == "5001"` → true | false | No detection (suppressed) |
| No recent 5007 | empty set | no match → false | true | Detection fires |
| After TTL expires | empty set | no match → false | true | Detection fires |

The key is storing the **value you expect to find at `path`** (the EventID `"5001"`) as the variable value, so the `is` comparison is meaningful.

!!! note "Ordering matters"
    This pattern only suppresses when Rule 1's event (the 5007) is processed **before** Rule 2's event (the 5001). If they can arrive in either order, consider setting the TTL long enough and using the variable in both directions.

### Dynamic Allowlisting

Build up a set of known-good values and suppress detections for them:

**Rule 1 — Learn approved applications during business hours:**

```yaml
# Detect
event: NEW_PROCESS
op: is
path: event/FILE_PATH
value: /opt/approved-installer
```

```yaml
# Respond
- action: add var
  name: approved-child-processes
  value: <<event/FILE_PATH>>
  ttl: 3600
```

**Rule 2 — Alert on unknown processes, skip approved ones:**

```yaml
# Detect
event: NEW_PROCESS
op: and
rules:
  - op: starts with
    path: event/FILE_PATH
    value: /opt/
  - op: is
    not: true
    path: event/FILE_PATH
    value: '[[approved-child-processes]]'
```

```yaml
# Respond
- action: report
  name: Unknown Process in /opt
```

## Caveats

### Variables Are Not Tags

Unlike [tags](../8-reference/response-actions.md#add-tag-remove-tag), which are visible in the sensor's metadata and can be used for organizational purposes, sensor variables are internal to the D&R engine and invisible outside of rule evaluation.

| Feature | Tags | Variables |
|---------|------|-----------|
| Visible in sensor info | Yes | No |
| Usable in D&R detection | `is tagged` operator | `[[var]]` in value |
| Propagation | Asynchronous | Synchronous (in-memory) |
| Scope | Per sensor or per device | Per sensor |
| TTL support | Yes | Yes |

### Synchronous Evaluation

Because sensor variables are stored in memory on the analytics node processing the sensor's events, they are read and written **synchronously** during rule evaluation. This means:

- A variable set by one rule's response is immediately visible to subsequent rules evaluating events from the same sensor.
- There is no propagation delay (unlike tags, which are asynchronous).

### State Persistence

Variables are persisted when a sensor disconnects and restored when it reconnects. The TTL continues to count down during the disconnection — if a variable's TTL expires while the sensor is offline, it will not be restored.

### Visibility

Sensor variables are internal to the D&R engine and **not** exposed through any read API:

- They do not appear in sensor info, the sensor's metadata, or audit events.
- There is no way to enumerate the variables currently held for a sensor.
- A specific variable's set can only be observed indirectly — by writing a rule that reads `[[variable_name]]` and reports the matching values.

Because variables cannot be inspected externally, treat them as ephemeral, rule-internal state. If you need a piece of state that is observable, queryable, or shared with operators, use [tags](../8-reference/response-actions.md#add-tag-remove-tag) instead — they are slower (asynchronous) but visible in the sensor's metadata. Combined with the destructive overrun behavior described above, this also means: always set a `ttl`, and keep variable contents bounded.

---

## See Also

- [D&R Rules Overview](index.md)
- [Response Actions](../8-reference/response-actions.md)
- [Stateful Rules](stateful-rules.md)
- [Detection Operators](../8-reference/detection-logic-operators.md)
