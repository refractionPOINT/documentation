# Reference: The `routing` Section

Every event and every detection in LimaCharlie is made of two parts: the **payload** (what happened) and the **`routing`** (metadata about where it happened, when, and on which sensor). The `routing` section is the consistent "envelope" wrapped around otherwise free-form data.

If you have ever looked at a raw event and wondered what that block of `oid`, `sid`, `event_type`, `event_time`, `hostname`… at the top is for, this page is for you.

---

## The Mental Model: Envelope vs. Payload

Think of a LimaCharlie event like a physical letter:

- The **envelope** (`routing`) is standardized. Every letter has a sender, a recipient, a postmark with a date, and an address. You can sort, route, and track letters using only the envelope, without ever opening them.
- The **letter inside** (`event` or `detect`) is the actual content. It is different for every kind of message.

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

The key insight: **the `event` object's fields change from one event type to another, but the `routing` object always has the same well-known fields.** That consistency is what makes `routing` so useful — you can write rules, queries, and outputs against it without knowing anything about the specific telemetry.

Where does it come from? You never write `routing` yourself. LimaCharlie's cloud builds it automatically as telemetry arrives, deriving the values from the sensor that reported the event (its identity, IP addresses, hostname, tags, etc.).

---

## A Fully Annotated Example

Here is a real-world `NEW_PROCESS` event with every routing field explained inline:

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

The exact set of fields present in `routing` depends on the source (an EDR endpoint produces more fields than a cloud log adapter), but the following are the standard ones.

### Identity Fields

These answer **"who/what produced this?"**

| Field | Type | Description |
|-------|------|-------------|
| `oid` | string (UUID) | **Organization ID.** The org that owns this telemetry. |
| `sid` | string (UUID) | **Sensor ID.** Uniquely identifies the sensor (endpoint or adapter) that reported the event. The single most useful field for pivoting to a specific machine. |
| `iid` | string (UUID) | **Installation Key ID.** The installation key used to enroll the sensor. Useful for grouping sensors deployed together. |
| `did` | string (UUID) | **Device ID.** A more stable hardware identifier. Survives re-installs where the `sid` may change. |
| `hostname` | string | Hostname reported by the sensor at the time of the event. |
| `moduleid` | integer | The internal sensor module / collector that generated the event. |

### Event Description Fields

These answer **"what happened and when?"**

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | The type of event, e.g. `NEW_PROCESS`, `DNS_REQUEST`, `NETWORK_CONNECTIONS`. This is what determines the shape of the `event` payload. |
| `event_time` | integer | Timestamp the event occurred, as reported by the endpoint. **Unix time in milliseconds** (13 digits). |
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
| `ext_plat` | string | **Extended platform** (only on multi-platform adapters, e.g. Carbon Black / CrowdStrike). Indicates the OS the *reported* endpoint runs, while `plat` describes the adapter itself. |

### Correlation Fields

These let you connect events to each other — see [Event Correlation](#event-correlation-with-this-parent-and-target) below.

| Field | Type | Description |
|-------|------|-------------|
| `this` | string (hash) | Hash uniquely identifying the primary object of the event (e.g. the process for a `NEW_PROCESS`). |
| `parent` | string (hash) | Hash identifying the parent object (e.g. the parent process). |
| `target` | string (hash) | Hash identifying a target object, when the event involves two objects (e.g. the process a remote thread was created in). Present only on relevant event types. |
| `investigation_id` | string | Set when the event was produced in response to a command or investigation. Echoed back so you can correlate a request with its result. See [investigation_id](#investigation_id). |

### Other Fields

| Field | Type | Description |
|-------|------|-------------|
| `tags` | array[string] | The sensor's tags at the moment the event was generated. Note: this reflects tags *at event time*, which may differ from the sensor's current tags. |

> **Note:** Cloud-adapter and SaaS-log events (Office 365, GCP, Okta, etc.) carry the identity, event-description, and platform fields, but typically do **not** carry endpoint-specific fields like `this`/`parent`/`target`, `int_ip`, or process hashes — those only make sense for EDR telemetry.

---

## `routing` in Detections

When a [D&R rule](../3-detection-response/index.md) matches an event and generates a **detection**, the detection **inherits the `routing` of the event that triggered it**. The triggering event's payload is copied into a `detect` field, and detection-specific metadata is added at the top level.

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

This is powerful: because the detection carries the original `routing`, you immediately know which sensor, host, and process the alert came from — and you can use the correlation hashes to take response actions against exactly the right object.

---

## Using `routing` in D&R Rules

Inside Detection & Response rules, you reach into the `routing` object using the `routing/` path prefix (just as you use `event/` for payload fields).

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

You can also **template** routing values into response actions using the `<<routing/FIELD>>` syntax. For example, to kill the exact process that triggered a rule:

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

- **`this`** — a stable hash identifying the object the event is *about* (for a `NEW_PROCESS`, the new process itself).
- **`parent`** — the object that created/owns `this` (for a process, its parent process).
- **`target`** — a third object, when an event acts on something else (e.g. a remote thread injected from one process *into* another).

Because the hashes are computed consistently across events, you can follow them:

```text
   explorer.exe                 (routing/this = AAA)
        │  spawns
        ▼
   cmd.exe         (routing/parent = AAA, routing/this = BBB)
        │  spawns
        ▼
   powershell.exe  (routing/parent = BBB, routing/this = CCC)
```

A later `DNS_REQUEST` made by that `powershell.exe` will carry `routing/this = CCC`, letting you tie the network activity back to the exact process chain. This is the foundation of [stateful rules](../3-detection-response/stateful-rules.md) and process-tree response actions like `deny_tree`.

```yaml
# Match any event coming from one specific process
detect:
  op: is
  path: routing/this
  value: "a443f9c48bef700740ef27e062c333c6"
```

---

## `investigation_id`

When you issue a command to a sensor (for example via [Reliable Tasking](../5-integrations/extensions/limacharlie/reliable-tasking.md) or directly), you can attach an `investigation_id`. The sensor echoes that value into the `routing.investigation_id` of the resulting `RECEIPT` or `*_REP` response event.

This lets you correlate a request with its answer — for instance, writing a D&R rule that reacts to the result of a command you sent:

```yaml
detect:
  event: RECEIPT
  op: starts with
  path: routing/investigation_id
  value: my-custom-investigation-
```

---

## Where You'll See `routing`

The same `routing` envelope appears across multiple LimaCharlie surfaces:

| Surface | Notes |
|---------|-------|
| **`event` stream** | Every piece of sensor/adapter telemetry. |
| **`detect` stream** | Detections inherit the triggering event's `routing`. |
| **`deployment` stream** | Sensor lifecycle events use the same `routing` envelope. |
| **Outputs** | When you forward data to a SIEM, S3, webhook, etc., the full `{routing, event}` structure is sent. Parse `routing/event_type` to route to the right index. |
| **LCQL queries** | Reference routing fields with the `routing/` prefix, e.g. `routing/hostname`. |
| **Schema API** | Learned schema elements are namespaced, e.g. `s:routing/sid`, `i:routing/event_time`. See [Event Schemas](event-schemas.md). |

> The `audit` stream is the exception — audit logs use a different, flatter structure and do **not** have a `routing` object. See [Output Stream Structures](../5-integrations/outputs/stream-structures.md#3-audit-stream-structure).

---

## Frequently Asked Questions

**Is `event_time` in seconds or milliseconds?**
Milliseconds (a 13-digit number). Remember that LimaCharlie *API parameters* generally use seconds (10 digits), so divide `event_time` by 1000 when feeding it back into an API query.

**What's the difference between `sid`, `did`, and `iid`?**
`sid` identifies a *sensor installation*, `did` identifies the underlying *device/hardware* (more stable across re-installs), and `iid` identifies the *installation key* used to enroll. Use `sid` for day-to-day pivoting and `did` for long-term device tracking.

**Why do my cloud-adapter events have fewer routing fields than my EDR events?**
Fields like `this`/`parent`/`target`, `int_ip`, and process hashes are endpoint concepts. Cloud and SaaS log sources don't have a process tree or a LAN IP, so those fields are simply absent.

**Are the `tags` in routing the sensor's current tags?**
No — they are a snapshot of the sensor's tags *at the moment the event was generated*. If you re-tag a sensor, older events keep the old tags.

**Can I add my own fields to `routing`?**
No. `routing` is built by the platform. To attach your own context, use `investigation_id` on commands, sensor tags, or fields inside the `event`/`detect` payload.

---

## Related Documentation

- [Output Stream Structures](../5-integrations/outputs/stream-structures.md) — the full structure of every output stream
- [Event Schemas](event-schemas.md) — how the learned schema namespaces `routing/*` and `event/*`
- [ID Schema](id-schema.md) — `oid`/`iid`/`sid`/`did` and the `plat`/`arch` value tables
- [Core Concepts: Data Structures](../1-getting-started/core-concepts.md#limacharlie-data-structures)
- [Stateful Rules](../3-detection-response/stateful-rules.md) — correlating events with `this`/`parent`/`target`
- [D&R Rule Building Guidebook](../3-detection-response/tutorials/dr-rule-building-guidebook.md)
