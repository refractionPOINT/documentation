# Endpoint Agent Commands and Events

## Endpoint Agent Commands

Endpoint Agent commands offer a safe way to interact with a Sensor's host either for investigation, management, or threat mitigation purposes.

### Sending Commands

Commands can be sent to Sensors via:

* Manually using the Console of a sensor in the [web application](https://app.limacharlie.io).
* Manually using the [CLI](https://github.com/refractionPOINT/python-limacharlie)
* Programmatically in the response action of a [Detection & Response](/v2/docs/detection-and-response) rule, via the `task` action.
* Programmatically using the [REST API](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI0OQ-task-sensor)

### Sensor REPort/REPly Events

Regardless of which you choose, sent commands will be acknowledged immediately with an empty response, followed by a `CLOUD_NOTIFICATION` event being sent by the sensor. The content of command outputs are delivered as sensor [events](/v2/docs/endpoint-agent-events-overview) suffixed with `_REP`, depending on the command.

**Please ensure that you have enabled the appropriate response event(s) in** [**Event Collection**](ext-exfil.md) **to ensure that you will receive the Sensor response.**

This non-blocking approach makes responses accessible via the [event streams](../concepts/sensors.md) passing through Detection & Response rules and Outputs.

### Command Structure

Commands follow typical CLI conventions using a mix of positional arguments and named optional arguments.

Here's `dir_list` as an example:

```
dir_list [-h] [-d DEPTH] rootDir fileExp

positional arguments:
    rootDir     the root directory where to begin the listing from
    fileExp     a file name expression supporting basic wildcards like * and ?

optional arguments:
    -h, --help      show this help message and exit
    -d DEPTH, --depth DEPTH     optional maximum depth of the listing, defaults to a single level
```

The Console in the web application will provide autocompletion hints of possible commands for a sensor and their parameters. For API users, commands and their usage details may be retrieved via the `/tasks` and `/task` REST API endpoints.

### Investigation IDs

To assist in finding the responses more easily, you may specify an arbitrary `investigation_id` string with a command. The response will then include that value under `routing/investigation_id`. Under the hood, this is exactly how the Console view in the web application works.

If an `investigation_id` is prefixed with `__` (double underscore) it will omit the resulting events from being forwarded to Outputs. This is primarily to allow Services to interact with sensors without spamming.

### Command Line Format

When issuing commands to sensors as a command line (versus a list of tokens), the quoting and escaping of arguments can be confusing. This is a short explanation:

The command line tasks are parsed as if they were issued to a shell like `sh` or `cmd.exe` with a few tweaks to make it easier and more intuitive to use.

Arguments are parsed as separated by spaces, like: `dir_list /home/user *` is equal to 2 arguments: `/home/user` and `*`.

If an argument contains spaces, for example a single directory like `/file/my files`, you must use either single (`'`) or double (`"`) quotes around the argument, like: `dir_list "/files/my files"`.

A backslash (`\`), like in Windows file paths does not need to be escaped. It is only interpreted as an escape character when it is followed by a single or double quote.

The difference between single quotes and double quotes is that double quotes support escaping characters within using `\`, while single quotes never interpret `\` as an escape character. For example:

* `log_get --file "c:\\temp\\my dir\\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file 'c:\\temp\\my dir\\' --type json` becomes `log_get`, `--file`, `c:\\temp\\my dir\\`, `--type`, `json`
* `log_get --file 'c:\temp\my dir\' --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file "c:\temp\my dir\\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`

This means that as a general statement, unless you want to embed quoted strings within specific arguments, it is easier to use single quotes around arguments and not worry about escaping `\`.

## Endpoint Agent Events Overview

This section describes and provides information about the various events emitted by the LimaCharlie Endpoint Agent Sensor. These events can be leveraged in [D&R rules](/v2/docs/detection-and-response) and queried with [LCQL](../concepts/lcql.md).

> **Important note about Event Collection**
>
> Only events enabled in the Exfil configuration will be shipped by the endpoint agent. If you're not seeing a specific event you expect, make sure that the desired event type is enabled in the [Exfil extension](ext-exfil.md) configuration. Ensure your Exfil settings are properly configured to capture all required event types for your use case.

### Atoms

Atoms are Globally Unique Identifiers (GUIDs). An example might be: `1e9e242a512d9a9b16d326ac30229e7b`. You can treat them as opaque values. These unique values are used to relate events together rather than using Process IDs, which are themselves unreliable.

#### Relationships

Atoms can be found in up to 3 spots in an event:

* `routing/this`: current event
* `routing/parent`: parent of the current event
* `routing/target`: target of the current event

Using atom references from a single event, the chain of ancestor events can be constructed. Here's a simplified example of an event and its parent event:

**Child event:**

```json
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

```json
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

> **Tip:** when using custom storage and/or searching solutions it's helpful to index the values of `routing/this` and `routing/parent` for each event. Doing so will speed up searching during threat hunting and investigations.

Finally, the `routing/target` is only sometimes found in an event, and it represents an event that interacts with another event without having a parent-child relationship. For example, in the `NEW_REMOTE_THREAD` event, this `target` represents a process where a remote thread was created.

### Key Concepts

**Endpoint Agents** are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, **Sensors** send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

**Exfil (Event Collection)** is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.