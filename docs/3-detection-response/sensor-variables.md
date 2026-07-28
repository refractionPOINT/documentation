# Sensor Variables

## Overview

Sensor variables are key-value stores for each sensor. They let D&R rules share state between rules that evaluate events from the same sensor. A response action in one rule can set a variable, and a detection operator in another rule can read it. This supports patterns such as conditional suppression, coordination between rules, and dynamic thresholds.

Variables are:

- **Scoped per sensor** — each sensor (SID) has its own independent set of variables.
- **Stored in memory** while the sensor is connected. This gives fast, synchronous access during rule evaluation.
- **Persisted across reconnections** — when a sensor disconnects, the cloud saves its variables and restores them when the sensor reconnects.
- **Optionally time-limited** — a variable can have a TTL (time-to-live) in seconds. The variable then expires automatically.

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
| `value`   | Yes      | Value to store. Can be a literal string or a [lookback](#using-lookbacks) such as `<<event/FILE_PATH>>`. |
| `ttl`     | No       | Time-to-live in seconds. The variable expires after this time. If you do not set it, the variable persists indefinitely, until you delete it or the cloud flushes the sensor state. |

A single variable name can hold **multiple values**. Each call to `add var` adds a value to the set. For example, `add var` with `name: seen-paths` and `value: <<event/FILE_PATH>>` collects a set of file paths across many events.

#### TTL Behavior

The `ttl` applies **to each value**, not to the variable. Each value has its own absolute expiration time. The cloud computes this time at insert as `now + ttl`.

- **New values in the same variable:** each value gets its own independent TTL timer. Values that you add at different times expire at different times.
- **A value that is already in the set:** the TTL is **reset**, and the new expiration replaces the old one. Use this to keep a value while related activity continues. Send `add var` with the same value on each relevant event. The value then expires only after `ttl` seconds without activity.
- **Different TTLs:** in one variable, some values can be short-lived and others long-lived. The cloud tracks each value independently.
- **No `ttl`:** the value persists indefinitely. With the limits below, indefinite values can fill the variable. Set a TTL when the data is bounded in time.

#### Limits and Overrun Behavior

A sensor can hold up to **16 variable names**, and each variable name can hold up to **32 values**.

These limits keep the state of each sensor bounded. **If you go above either limit, the effect is destructive. The cloud does not remove the oldest entry to make room.** The effects are:

| Limit exceeded | Effect |
|----------------|--------|
| The 33rd unique value is added to a single variable | The cloud clears the **entire variable** and all of its values, and `add var` returns an error. The new value is also lost. |
| The 17th distinct variable name is added to a sensor | The cloud clears **all variables** for that sensor, and `add var` returns an error. |

Therefore, design your rule sets so that normal operation stays below the limits:

- Always set a `ttl`, unless you are sure that the set of values is bounded.
- Use a short TTL when an `<<event/...>>` lookback fills a variable from a field with high cardinality. Examples are file paths, command lines, and IP addresses. The set then prunes itself.
- Do not split unrelated state into many small variables on the same sensor. Combine related state when possible.

A value that is already present does **not** count against the value limit. It only refreshes the TTL of the existing entry. Therefore, it is safe to refresh a small fixed set of values with `add var`.

### del var

```yaml
- action: del var
  name: my-variable
  value: some-value
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name`    | Yes      | Name of the variable. |
| `value`   | Yes      | The value to remove from the set of the variable. Can be a literal or a lookback. An empty string (`value: ""`) removes **all** values of the variable, as described in the next section. |

#### Removing All Values for a Variable

You can clear an entire variable when you do not know its contents, or when you want to reset the state. To do this, set `value` to an empty string:

```yaml
- action: del var
  name: my-variable
  value: ""
```

This removes every value of `my-variable` for the sensor in one action. There is no API to list the variables of a sensor, as described in [Visibility](#visibility). Therefore, this is the only way to clear a variable without a list of its current values.

You can also use a short `ttl` on `add var`. The values then expire without an explicit deletion.

### Using Lookbacks

The `value` parameter supports the lookback syntax (`<<path>>`) to extract values from the current event:

```yaml
- action: add var
  name: recently-seen-processes
  value: <<event/FILE_PATH>>
  ttl: 300
```

This stores the file path from the event that triggered the rule.

## Reading Variables (Detection Operators)

To use a sensor variable in a detection rule, put the `[[variable_name]]` syntax in the `value` parameter of an operator.

When the engine evaluates the operator, it replaces `[[variable_name]]` with the **set of values** in that variable for the sensor. The operator then checks if the value at `path` matches **any** of those values.

### Supported Operators

The `[[variable_name]]` syntax works with these operators:

- `is`
- `contains`
- `starts with`
- `ends with`
- `is greater than`
- `is lower than`

### Basic Example

**Rule 1** — When a process accesses a sensitive file, store the file path:

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

When Rule 2 evaluates, `[[sensitive-files-accessed]]` resolves to the set of file paths that Rule 1 stored. If the `FILE_PATH` of the current event matches one of them, the rule fires.

### Empty Variables

A variable can have no values because you never set it, because it expired, or because you deleted it. In that condition, `[[variable_name]]` resolves to an **empty set**. No value can match an empty set, so the operator returns `false`.

This is useful with `not: true`. If the variable is empty, the operator returns `false`, `not` changes it to `true`, and the rule continues. If the variable has a value that matches, the operator returns `true`, `not` changes it to `false`, and the rule is suppressed.

## Common Patterns

### Conditional Suppression: "Detect A Unless B Happened Recently"

This is the most common use of sensor variables. You detect an event, but you suppress the detection if a related event occurred recently.

**Example:** Detect that Windows Defender real-time protection is disabled (EID 5001). Do not report the detection if a managed policy change (EID 5007) occurred recently, because that change is expected and managed.

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

Store the **value that you expect to find at `path`** (the EventID `"5001"`) as the value of the variable. The `is` comparison is then meaningful.

!!! note "Ordering matters"
    This pattern suppresses the detection only if the cloud processes the event of Rule 1 (the 5007) **before** the event of Rule 2 (the 5001). If the two events can arrive in either order, set a TTL that is long enough and use the variable in both directions.

### Dynamic Allowlisting

Collect a set of known-good values and suppress the detections for them:

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

[Tags](../8-reference/response-actions.md#add-tag-remove-tag) are visible in the metadata of the sensor, and you can use them to organize sensors. Sensor variables are different. They are internal to the D&R engine, and they are not visible outside rule evaluation.

| Feature | Tags | Variables |
|---------|------|-----------|
| Visible in sensor info | Yes | No |
| Usable in D&R detection | `is tagged` operator | `[[var]]` in value |
| Propagation | Asynchronous | Synchronous (in-memory) |
| Scope | Per sensor or per device | Per sensor |
| TTL support | Yes | Yes |

### Synchronous Evaluation

The analytics node that processes the events of the sensor keeps the sensor variables in memory. Therefore, the engine reads and writes them **synchronously** during rule evaluation. This means:

- A variable that the response of one rule sets is immediately visible to the later rules that evaluate events from the same sensor.
- There is no delay in propagation. Tags are different, because they are asynchronous.

### State Persistence

The cloud saves the variables when a sensor disconnects and restores them when the sensor reconnects. The TTL continues to count down during the disconnection. If the TTL of a variable expires while the sensor is offline, the cloud does not restore that variable.

### Visibility

Sensor variables are internal to the D&R engine and **not** exposed through any read API:

- They do not appear in sensor info, in the metadata of the sensor, or in audit events.
- There is no way to list the variables that a sensor holds.
- You can see the set of one variable only indirectly. Write a rule that reads `[[variable_name]]` and reports the values that match.

You cannot inspect variables from outside the engine, so treat them as temporary state inside the rules. Use [tags](../8-reference/response-actions.md#add-tag-remove-tag) instead if you need state that you can see, query, or share with operators. Tags are slower because they are asynchronous, but they are visible in the metadata of the sensor. Because of the destructive behavior above when you go above a limit, always set a `ttl` and keep the contents of each variable bounded.

---

## See Also

- [D&R Rules Overview](index.md)
- [Response Actions](../8-reference/response-actions.md)
- [Stateful Rules](stateful-rules.md)
- [Detection Operators](../8-reference/detection-logic-operators.md)
