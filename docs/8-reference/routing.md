# Reference: The `routing` Section

Every event and every detection in LimaCharlie has two parts: the **payload** (what happened) and the **`routing`** (metadata about where it happened, when, and on which sensor). The `routing` section is the consistent "envelope" around data that is otherwise free-form.

This page explains the block of `oid`, `sid`, `event_type`, `event_time`, `hostname`… at the top of a raw event.

---

## The Mental Model: Envelope vs. Payload

A LimaCharlie event is similar to a physical letter:

- The **envelope** (`routing`) is standardized. Every letter has a sender, a recipient, a postmark with a date, and an address. You can sort, route, and track letters with only the envelope, and you do not open them.
- The **letter inside** (`event` or `detect`) is the content. It is different for each kind of message.

```json
{
  "routing": {
    "// this is the envelope": "always the same shape",
    "event_type": "NEW_PROCESS",
    "event_time": 1656959942437,
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",
    "hostname": "workstation-01"
  },
  "event": {
    "// this is the letter": "shape depends on event_type",
    "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
    "COMMAND_LINE": "cmd.exe /c whoami"
  }
}
```

**The fields of the `event` object change from one event type to another, but the `routing` object always has the same well-known fields.** This consistency makes `routing` useful. You can write rules, queries, and outputs against `routing` and know nothing about the specific telemetry.

You never write `routing` yourself. The LimaCharlie cloud builds it automatically when telemetry arrives. The cloud takes the values from the sensor that reported the event: its identity, IP addresses, hostname, tags, etc.

---

## A Fully Annotated Example

Here is a real `NEW_PROCESS` event. The inline comments explain every routing field:

```json
{
  "routing": {
    "oid": "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",   // Organization ID — which org owns this data
    "iid": "7d23bee6-aaaa-aaaa-aaaa-c8e8cca132a1",   // Installation Key ID — how the sensor was enrolled
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",   // Sensor ID — WHICH endpoint reported this
    "did": "b97e9d00-aaaa-aaaa-aaaa-27c3468d5901",   // Device ID — stable hardware identifier
    "event_type": "NEW_PROCESS",                      // WHAT kind of event this is
    "event_time": 1656959942437,                      // WHEN it happened (Unix ms, from the endpoint)
    "event_id": "8cec565d-14bd-4639-a1af-4fc8d5420b0c", // Unique ID for this exact event
    "hostname": "workstation-01",                     // Hostname of the sensor at event time
    "ext_ip": "203.0.113.45",                         // External (public) IP of the endpoint
    "int_ip": "10.0.1.25",                            // Internal (LAN) IP of the endpoint
    "plat": 268435456,                                // Platform code (268435456 = Windows)
    "arch": 2,                                        // Architecture code (2 = x64)
    "moduleid": 2,                                    // Sensor module that produced the event
    "this": "a443f9c48bef700740ef27e062c333c6",       // Hash identifying THIS object (the process)
    "parent": "42217cb0326ca254999554a862c3298e",     // Hash identifying the PARENT object
    "tags": ["production", "critical-assets"]         // Sensor tags at event time
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
    "COMMAND_LINE": "cmd.exe /c whoami",
    "PROCESS_ID": 4812,
    "USER_NAME": "Administrator"
  }
}
```

---

## Field Reference

The set of fields in `routing` depends on the source. An EDR endpoint produces more fields than a cloud log adapter. These are the standard fields.

### Identity Fields

These answer **"who/what produced this?"**

| Field | Type | Description |
|-------|------|-------------|
| `oid` | string (UUID) | **Organization ID.** The org that owns this telemetry. |
| `sid` | string (UUID) | **Sensor ID.** Uniquely identifies the sensor (endpoint or adapter) that reported the event. The most useful field to pivot to a specific machine. |
| `iid` | string (UUID) | **Installation Key ID.** The installation key that enrolled the sensor. Use it to group sensors that you deployed together. |
| `did` | string (UUID) | **Device ID.** A more stable hardware identifier. It stays the same across re-installs, but the `sid` can change. |
| `hostname` | string | Hostname that the sensor reports at the time of the event. |
| `moduleid` | integer | The internal sensor module / collector that generated the event. |

### Event Description Fields

These answer **"what happened and when?"**

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | The type of event, e.g. `NEW_PROCESS`, `DNS_REQUEST`, `NETWORK_CONNECTIONS`. It sets the shape of the `event` payload. |
| `event_time` | integer | Timestamp of the event, as the endpoint reports it. **Unix time in milliseconds** (13 digits). |
| `event_id` | string (UUID) | A globally unique identifier for this specific event occurrence. |

### Network / Location Fields

| Field | Type | Description |
|-------|------|-------------|
| `ext_ip` | string | External (public-facing) IP address of the endpoint. |
| `int_ip` | string | Internal (private/LAN) IP address of the endpoint. |

### Platform Fields

| Field | Type | Description |
|-------|------|-------------|
| `plat` | integer | Platform code as an integer (e.g. `268435456` = Windows, `536870912` = Linux). See [ID Schema](id-schema.md#platform) for the full table. |
| `arch` | integer | Architecture code (e.g. `1` = x86, `2` = x64). See [ID Schema](id-schema.md#architecture). |
| `ext_plat` | string | **Extended platform** (only on multi-platform adapters, e.g. Carbon Black / CrowdStrike). Shows the OS of the *reported* endpoint. `plat` describes the adapter itself. |

### Correlation Fields

These let you connect events to each other — see [Event Correlation](#event-correlation-with-this-parent-and-target) below.

| Field | Type | Description |
|-------|------|-------------|
| `this` | string (hash) | Hash that uniquely identifies the primary object of the event (e.g. the process for a `NEW_PROCESS`). |
| `parent` | string (hash) | Hash that identifies the parent object (e.g. the parent process). |
| `target` | string (hash) | Hash that identifies a target object when the event has two objects (e.g. the process where a remote thread was created). Present only on relevant event types. |
| `investigation_id` | string | Set when a command or investigation produces the event. It is echoed back, so that you can correlate a request with its result. See [investigation_id](#investigation_id). |

### Other Fields

| Field | Type | Description |
|-------|------|-------------|
| `tags` | array[string] | The tags of the sensor at the moment the event was generated. These are the tags *at event time*, and they can be different from the current tags of the sensor. |

> **Note:** Cloud-adapter and SaaS-log events (Office 365, GCP, Okta, etc.) carry the identity, event-description, and platform fields. They usually do **not** carry endpoint-specific fields such as `this`/`parent`/`target`, `int_ip`, or process hashes. Those fields apply only to EDR telemetry.

---

## `routing` in Detections

When a [D&R rule](../3-detection-response/index.md) matches an event and generates a **detection**, the detection **inherits the `routing` of the event that triggered it**. The cloud copies the payload of the triggering event into a `detect` field, and adds detection-specific metadata at the top level.

```json
{
  "cat": "Suspicious PowerShell Execution",
  "source": "dr-general",
  "routing": {
    "oid": "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",
    "event_type": "NEW_PROCESS",
    "event_time": 1656959942437,
    "hostname": "workstation-01",
    "this": "a443f9c48bef700740ef27e062c333c6",
    "parent": "42217cb0326ca254999554a862c3298e"
  },
  "detect": {
    "FILE_PATH": "C:\\...\\powershell.exe",
    "COMMAND_LINE": "powershell.exe -enc SGVsbG8gV29ybGQ="
  },
  "detect_id": "f1e2d3c4-aaaa-aaaa-aaaa-123456789abc"
}
```

The detection carries the original `routing`. You therefore know which sensor, host, and process sent the alert. You can also use the correlation hashes to run response actions against the correct object.

---

## Using `routing` in D&R Rules

In Detection & Response rules, use the `routing/` path prefix to read the `routing` object. Use the `event/` prefix for payload fields.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    # Only fire on Windows endpoints
    - op: is
      path: routing/plat
      value: 0x10000000   # 268435456 = Windows

    # Only fire on sensors tagged "production"
    - op: is tagged
      tag: production

    - op: contains
      path: event/COMMAND_LINE
      value: powershell
      case sensitive: false
```

You can also **template** routing values into response actions with the `<<routing/FIELD>>` syntax. For example, to kill the exact process that triggered a rule:

```yaml
respond:
  - action: task
    command: deny_tree <<routing/this>>
```

…or to kill the *parent* of the offending process:

```yaml
respond:
  - action: task
    command: deny_tree <<routing/parent>>
```

---

## Event Correlation with `this`, `parent`, and `target`

The three hash fields turn a flat stream of events into a connected graph.

- **`this`** — a stable hash that identifies the object the event is *about* (for a `NEW_PROCESS`, the new process itself).
- **`parent`** — the object that creates or owns `this` (for a process, its parent process).
- **`target`** — a third object, when an event acts on something else (e.g. a remote thread injected from one process *into* another).

The cloud computes the hashes consistently across events, so you can trace them:

```text
   explorer.exe                 (routing/this = AAA)
        │  spawns
        ▼
   cmd.exe         (routing/parent = AAA, routing/this = BBB)
        │  spawns
        ▼
   powershell.exe  (routing/parent = BBB, routing/this = CCC)
```

A later `DNS_REQUEST` from that `powershell.exe` carries `routing/this = CCC`. You can therefore link the network activity to the exact process chain. This is the basis of [stateful rules](../3-detection-response/stateful-rules.md) and of process-tree response actions such as `deny_tree`.

```yaml
# Match any event coming from one specific process
detect:
  op: is
  path: routing/this
  value: "a443f9c48bef700740ef27e062c333c6"
```

---

## `investigation_id`

When you send a command to a sensor, you can attach an `investigation_id`. Send the command with [Reliable Tasking](../5-integrations/extensions/limacharlie/reliable-tasking.md) or directly. The sensor echoes that value into the `routing.investigation_id` of the `RECEIPT` or `*_REP` response event.

You can then correlate a request with its answer. For example, write a D&R rule that reacts to the result of a command that you sent:

```yaml
detect:
  event: RECEIPT
  op: starts with
  path: routing/investigation_id
  value: my-custom-investigation-
```

---

## Where You'll See `routing`

The same `routing` envelope appears on many LimaCharlie surfaces:

| Surface | Notes |
|---------|-------|
| **`event` stream** | Every piece of sensor/adapter telemetry. |
| **`detect` stream** | Detections inherit the `routing` of the triggering event. |
| **`deployment` stream** | Sensor lifecycle events use the same `routing` envelope. |
| **Outputs** | When you forward data to a SIEM, S3, webhook, etc., LimaCharlie sends the full `{routing, event}` structure. Parse `routing/event_type` to route to the correct index. |
| **LCQL queries** | Refer to routing fields with the `routing/` prefix, e.g. `routing/hostname`. |
| **Schema API** | Learned schema elements are namespaced, e.g. `s:routing/sid`, `i:routing/event_time`. See [Event Schemas](event-schemas.md). |

> The `audit` stream is the exception. Audit logs use a different, flatter structure and do **not** have a `routing` object. For details, see [Output Stream Structures](../5-integrations/outputs/stream-structures.md#3-audit-stream-structure).

---

## Frequently Asked Questions

**Is `event_time` in seconds or milliseconds?**
Milliseconds (a 13-digit number). LimaCharlie *API parameters* usually use seconds (10 digits). Divide `event_time` by 1000 before you use it in an API query.

**What's the difference between `sid`, `did`, and `iid`?**
`sid` identifies a *sensor installation*. `did` identifies the *device or hardware* below it, and is more stable across re-installs. `iid` identifies the *installation key* that enrolled the sensor. Use `sid` for daily pivoting and `did` for long-term device tracking.

**Why do my cloud-adapter events have fewer routing fields than my EDR events?**
Fields such as `this`/`parent`/`target`, `int_ip`, and process hashes are endpoint concepts. Cloud and SaaS log sources have no process tree and no LAN IP, so those fields are absent.

**Are the `tags` in routing the sensor's current tags?**
No. They are a snapshot of the tags of the sensor *at the moment the event was generated*. If you re-tag a sensor, older events keep the old tags.

**Can I add my own fields to `routing`?**
No. The platform builds `routing`. To attach your own context, use `investigation_id` on commands, sensor tags, or fields in the `event`/`detect` payload.

---

## Related Documentation

- [Output Stream Structures](../5-integrations/outputs/stream-structures.md) — the full structure of every output stream
- [Event Schemas](event-schemas.md) — how the learned schema namespaces `routing/*` and `event/*`
- [ID Schema](id-schema.md) — `oid`/`iid`/`sid`/`did` and the `plat`/`arch` value tables
- [Core Concepts: Data Structures](../1-getting-started/core-concepts.md#limacharlie-data-structures)
- [Stateful Rules](../3-detection-response/stateful-rules.md) — correlating events with `this`/`parent`/`target`
- [D&R Rule Building Guidebook](../3-detection-response/tutorials/dr-rule-building-guidebook.md)
