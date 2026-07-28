# Event Schemas

LimaCharlie standardizes on JSON for all data sources. Because of this, a schema in LimaCharlie is dynamic.

LimaCharlie supplies a Schema API. Use this API to create schemas in external systems that need more strictly typed data.

The Schema API exposes the "learned" schema of specific event types. When data comes into LimaCharlie, the API collects the fields and the types that it sees for those events. You can then retrieve this learned schema.

## API

### Listing Schemas

To get the list of all available schemas, do a `GET` to `api.limacharlie.io/v1/orgs/YOUR-OID/schema`.

The returned data looks like:

```json
{
  "event_types": [
    "evt:New-ExchangeAssistanceConfig",
    "det:00285-WIN-RDP_Connection_From_Non-RFC-1918_Address",
    "det:VirusTotal hit on DNS request",
    "evt:WEL",
    "evt:SHUTTING_DOWN",
    "evt:NETSTAT_REP",
    "evt:AdvancedHunting-DeviceEvents",
    "evt:NEW_DOCUMENT",
    "sched:12h_per_cloud_adapter",
    "sched:1h_per_sensor",
    "sched:3h_per_sensor",
    ...
}
```

Each element in the list of schemas has a prefix and a value.

Prefixes can be:

- `evt` for an Event.
- `dep` for a Deployment Event.
- `det` for a Detection.
- `art` for an Artifact Event.
- `sched` for Scheduling Events.

The value is the Event Type. For Detections, the value is the `cat` (detection name).

### Retrieveing Schema Definition

To retrieve a specific schema definition, do a `GET` on `api.limacharlie.io/v1/orgs/YOUR-OID/schema/EVENT-TYPE`. The `EVENT-TYPE` is one of the exact keys that the listing API above returns.

The returned data looks like:

```json
{
  "schema": {
    "elements": [
      "i:routing/event_time",
      "s:routing/sid",
      "i:routing/moduleid",
      "i:event/PROCESS_ID",
      "s:routing/this",
      "i:event/DNS_TYPE",
      "s:routing/iid",
      "s:routing/did",
      "i:event/DNS_FLAGS",
      "i:routing/tags",
      "s:event/IP_ADDRESS",
      "s:routing/event_type",
      "i:event/MESSAGE_ID",
      "s:event/CNAME",
      "s:event/DOMAIN_NAME",
      "s:routing/ext_ip",
      "s:routing/parent",
      "s:routing/hostname",
      "s:routing/int_ip",
      "i:routing/plat",
      "s:routing/oid",
      "i:routing/arch",
      "s:routing/event_id"
    ],
    "event_type": "evt:DNS_REQUEST"
  }
}
```

Each element in the returned `schema.elements` data has a prefix and a value.

The prefix is one of:

- `i` shows that the element is an Integer.
- `s` shows that the element is a String.
- `b` shows that the element is a Boolean.

The value is a path in the JSON. For example, the schema above represents this event:

```json
{
  "event": {
    "CNAME": "cs9.wac.phicdn.net",
    "DNS_TYPE": 5,
    "DOMAIN_NAME": "ocsp.digicert.com",
    "MESSAGE_ID": 19099,
    "PROCESS_ID": 1224
  },
  "routing": {
    "arch": 2,
    "did": "b97e9d00-aaaa-aaaa-aaaa-27c3468d5901",
    "event_id": "8cec565d-14bd-4639-a1af-4fc8d5420b0c",
    "event_time": 1656959942437,
    "event_type": "DNS_REQUEST",
    "ext_ip": "35.1.1.1",
    "hostname": "demo-win-2016.c.lc-demo-infra.internal",
    "iid": "7d23bee6-aaaa-aaaa-aaaa-c8e8cca132a1",
    "int_ip": "10.1.1.1",
    "moduleid": 2,
    "oid": "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",
    "parent": "42217cb0326ca254999554a862c3298e",
    "plat": 268435456,
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",
    "tags": [
      "edr"
    ],
    "this": "a443f9c48bef700740ef27e062c333c6"
  }
}
```

## Event Structure Reference

All events in LimaCharlie use a canonical structure with two top-level objects: `routing` and `event`. You must know this structure to write D&R rules, to write LCQL queries, and to configure outputs.

### Top-Level Structure

```json
{
  "routing": { /* metadata about the event */ },
  "event": { /* event-specific data */ }
}
```

### The `routing` Object

The `routing` object contains **metadata** about the event: the source of the event, the time of the event, and the relation to other events. This metadata is the same for all event types. Use it for correlation, for filtering, and for investigation.

#### Core Routing Fields

| Field | Type | Description | Use Cases |
|-------|------|-------------|-----------|
| `oid` | string (UUID) | Organization ID | Multi-tenant filtering, audit trails |
| `sid` | string (UUID) | Sensor ID - uniquely identifies the endpoint | Host-based correlation, sensor management |
| `event_type` | string | Type of event (e.g., `NEW_PROCESS`, `DNS_REQUEST`) | Event filtering in D&R rules, LCQL queries |
| `event_time` | integer | Unix timestamp in milliseconds | Timeline analysis, temporal correlation |
| `event_id` | string (UUID) | Unique identifier for this specific event | Deduplication, event tracking |
| `hostname` | string | Hostname of the sensor | Host-based investigations |
| `iid` | string (UUID) | Installation Key ID used to install the sensor | Deployment tracking, sensor grouping |
| `did` | string (UUID) | Device ID - hardware identifier | Device tracking across reinstalls |

#### Network Information

| Field | Type | Description | Use Cases |
|-------|------|-------------|-----------|
| `ext_ip` | string | External IP address of the sensor | Geolocation, network-based correlation |
| `int_ip` | string | Internal IP address of the sensor | Network segmentation analysis |

#### Platform Information

| Field | Type | Description | Use Cases |
|-------|------|-------------|-----------|
| `plat` | integer | Platform identifier (Windows, Linux, macOS, etc.) | Platform-specific rules |
| `arch` | integer | Architecture (x86, x64, ARM, etc.) | Architecture-specific analysis |
| `moduleid` | integer | Sensor module that generated the event | Module-specific filtering |

#### Process Correlation Fields

| Field | Type | Description | Use Cases |
|-------|------|-------------|-----------|
| `this` | string (hash) | Hash representing the current process or object | Process tracking across events |
| `parent` | string (hash) | Hash of the parent process | Process tree reconstruction |
| `target` | string (hash) | Hash of the target object (in actions on other objects) | Object tracking, lateral movement detection |

#### Other Routing Fields

| Field | Type | Description | Use Cases |
|-------|------|-------------|-----------|
| `tags` | array[string] | Sensor tags applied at event time | Tag-based filtering, dynamic grouping |

### The `event` Object

The `event` object contains **event-specific data** that varies by event type. For example:

- **NEW_PROCESS** events contain: `FILE_PATH`, `COMMAND_LINE`, `PROCESS_ID`, `PARENT` (full parent process info)
- **DNS_REQUEST** events contain: `DOMAIN_NAME`, `IP_ADDRESS`, `DNS_TYPE`, `DNS_FLAGS`
- **NETWORK_CONNECTIONS** events contain: `NETWORK_ACTIVITY` array with connection details
- **WEL** (Windows Event Log) events contain: `EVENT` object with nested Windows event structure

### Event Structure in Practice

#### Accessing Fields in D&R Rules

In Detection & Response rules, use the `event/` and `routing/` path prefixes to access fields:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: routing/plat
      value: 0x10000000  # Windows
    - op: contains
      path: event/COMMAND_LINE
      value: powershell
      case sensitive: false
```

#### Event Correlation Using Routing

The `routing/this`, `routing/parent`, and `routing/target` hashes let you correlate events:

```yaml
# Track all events from a specific process
detect:
  op: is
  path: routing/this
  value: "a443f9c48bef700740ef27e062c333c6"
```

### Relationship to Other Structures

> Events and detections share the `routing` metadata envelope. For a dedicated explanation, see [The `routing` Section](routing.md).

**Events → Detections**: When a D&R rule matches an event, a Detection is created. The Detection inherits the `routing` object from the event that triggered the rule. It then adds detection-specific metadata.

**Events → Outputs**: You can send events to external systems through the "event" output stream. The full event structure, both `routing` and `event`, is sent.

**Events → Audit**: Audit logs track platform actions and use a different structure. For details, see the Output Stream Structures documentation.

### Platform-Specific Considerations

#### Windows Events

- Windows Event Logs often include nested structures such as `event/EVENT/System/EventID`
- Process events include detailed parent information in `event/PARENT`

#### Linux Events

- File paths use forward slashes
- Process events can include user and group information

#### Cloud Adapter Events

- Can have custom `event` structures that depend on the source system
- `routing/event_type` shows the adapter and event type (e.g., `WEL`, `AdvancedHunting-DeviceEvents`)

### Best Practices

1. **Use routing fields for correlation**: `sid`, `hostname`, `this`, and `parent` are the same across all events
2. **Filter by event_type early**: For performance, most D&R rules should specify `event:` at the top level
3. **Leverage platform and architecture**: For logic that is specific to an OS, use `routing/plat` and `routing/arch`
4. **Understand timestamp format**: `routing/event_time` is Unix milliseconds (not seconds)
5. **Hash consistency**: `routing/this` and `routing/parent` use the same hashing algorithm, so you can track an object across events
