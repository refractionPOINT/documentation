## Overview

This category describes and provides samples for the various events emitted by the LimaCharlie Endpoint Agent Sensor. These events can be leveraged in [D&R rules](/v2/docs/detection-and-response) and queried with [LCQL](/v2/docs/lcql).

Important note about Event Collection

Only events enabled in the Exfil configuration will be shipped by the endpoint agent. If you're not seeing a specific event you expect, make sure that the desired event type is enabled in the [Exfil extension](/v2/docs/ext-exfil) configuration. Ensure your Exfil settings are properly configured to capture all required event types for your use case.

## Atoms

Atoms are Globally Unique Identifiers (GUIDs). An example might be: `1e9e242a512d9a9b16d326ac30229e7b`. You can treat them as opaque values. These unique values are used to relate events together rather than using Process IDs, which are themselves unreliable.

### Relationships

Atoms can be found in up to 3 spots in an event:

* `routing/this`: current event
* `routing/parent`: parent of the current event
* `routing/target`: target of the current event

Using atom references from a single event, the chain of ancestor events can be constructed. Here's a simplified example of an event and its parent event:

**Child event:**

```
{
  "event": {...},
  "routing": {
    "this": "abcdef",
    "parent": "zxcv"
    ...
  }
}
```

**Parent event:**

```
{
  "event": {...},
  "routing": {
    "this": "zxcv",
    "parent": "poiuy"
    ...
  }
}
```

API users may construct a tree from a single atom using these 2 endpoints:

* `/insight/{oid}/{sid}/{atom}` - get event by atom
* `/insight/{oid}/{sid}/{atom}/children` - get children of an atom

These can be called recursively on each event's `routing/parent` and/or child events to complete a full tree if required - this is how the tree view works in the Timeline of a sensor in the web application.

The parent-child relationship serves to describe parent and child processes via the `NEW_PROCESS` or `EXISTING_PROCESS` events, but other types of events may also have parents. For example, on `NETWORK_SUMMARY` events, the `parent` will be the process that generated the network connections.

Tip: when using custom storage and/or searching solutions it's helpful to index the values of `routing/this` and `routing/parent` for each event. Doing so will speed up searching during threat hunting and investigations.

Finally, the `routing/target` is only sometimes found in an event, and it represents an event that interacts with another event without having a parent-child relationship. For example, in the `NEW_REMOTE_THREAD` event, this `target` represents a process where a remote thread was created.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.
