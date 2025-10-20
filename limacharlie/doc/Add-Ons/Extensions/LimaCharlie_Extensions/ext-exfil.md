# Exfil (Event Collection)

The Exfil Extension helps manage which real-time [events](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md) get sent from EDR sensors to LimaCharlie. By default, LimaCharlie Sensors send events to the cloud based on a standard profile. This extension exposes those profiles for customization. The Exfil extension allows you to customize Event Collection from LimaCharlie Sensors, as well as mitigate sensors with high I/O or large [detection and response](/v2/docs/detection-and-response) rulesets.

> Event Collection Rule Synchronization
>
> Please note that Exfil (or Event Collection) rule configurations are synchronized with sensors every few minutes.

## Enabling the Exfil Extension

To enable the Exfil extension, navigate to the [Exfil extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-exfil) in the marketplace. Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/exfil-1.png "image(231).png")

After clicking subscribe, the Exfil extension should be available almost immediately.

## Using the Exfil Extension

Once the extension is enabled, you will see an **Event Collection** option under **Sensors** in the LimaCharlie web UI.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/exfil-2.png "image(227).png")

There are three rule options within the Exfil extension:

* **Event Collection Rules** manage events sent by the Sensor to the LimaCharlie cloud.
* **Performance Rules** are useful for high I/O servers, but may impact event accuracy. This feature is available only on Windows Sensors.
* **Watch Rules** allow for conditional operators for an event, allowing you to specify a list of sensors to help manage high-volume events. Conditional operators for Watch Rule events include:

  + The **event** itself, such as `MODULE_LOAD`.
  + The **path** within the event component to be evaluated, such as `FILE_PATH`.
  + The **operator** to evaluate or compare that should be done between the path and the value.
  + The **value** to be used in comparison with the operator.

A sample **Watch Rule** might be

```
Event: MODULE_LOAD
Path: FILE_PATH
Operator: ends with
Value: wininet.dll
```

The above rule would configures the sensor(s) to send *only* `MODULE_LOAD` events where the `FILE_PATH` ends with the value `wininet.dll`.

> Performance Rules
>
> Performance rules, applied via tag to a set of Sensors, are useful for high I/O systems. These rules can be set via the web application or REST API.

### Throughput Limits

Enabling *every* event for Exfil can produce an exceedingly large amount of traffic. Our first recommendation would be to optimize events required for detection & response rules, in order to ensure that all rules are active. We'd also recommend prioritizing events that contribute to outputs, such as forwarded `DNS_REQUESTS`.

LimaCharlie attempts to process all events in real-time. However, if events fall behind, they are enqueued to a certain limit. If that limit is reached (e.g. in the case of a long, sustained burst or enabling *all* events at the same time), the queue may eventually get dropped. In that event, an error is emitted to the platform logs.

Seeing event collection errors is a sign you may need to do one of the following:

1. Reduce the population of events collected.
2. Reduce the number of  rules you run or rule complexity.
3. Adopt a selective subset of events by utilizing Watch Rules that only bring back events with specific values.
4. Enable the IR mode (below).

#### Afterburner

Before a backlogged queue is dropped, LimaCharlie attempts to increase performance by entering a special mode we call "afterburner." This mode tries to address one of the common scenarios that can lead to a large influx of data: spammy processes starting over and over. This happens in situations such as the building of software, in which executables like `devenv.exe` or `git` can be called hundreds of times per second. The afterburner mode attempts to (1) de-duplicate those processes and (2) assess only each one through the D&R rules and Outputs.

#### IR Mode

The afterburner mode does not address all possible causes or situations. To help with this, LimaCharlie offers "IR mode." This mode is enabled by tagging a LimaCharlie sensor with the tag `ir`. The goal of "IR mode" is to provide a solution for users who want to record a very large number of events, but do not need to run D&R rules over all of them. When enabled, "IR mode" will not de-duplicate events. Furthermore, D&R rules will *only* be run against the follow event types:

1. `CODE_IDENTITY`
2. `DNS_REQUEST`
3. `NETWORK_CONNECTIONS`
4. `NEW_PROCESS`

IR mode is designed to give a balance between recording all events, while maintaining basic D&R rule capabilities.

## Actions via REST API

The following REST API actions can be sent to interact with the Exfil extension:

**List Rules**

```
{
  "action": "list_rules"
}
```

### Event Collection Rules

**Add Event Collection Rule**

```
{
  "action": "add_event_rule",
  "name": "windows-vip",
  "events": [
    "NEW_TCP4_CONNECTION",
    "NEW_TCP6_CONNECTION"
  ],
  "tags": [
    "vip"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Event Collection Rule**

```
{
  "action": "remove_event_rule",
  "name": "windows-vip"
}
```

### Watch Rules

**Add Watch Rule**

```
{
  "action": "add_watch",
  "name": "wininet-loading",
  "event": "MODULE_LOAD",
  "operator": "ends with",
  "value": "wininet.dll",
  "path": [
    "FILE_PATH"
  ],
  "tags": [
    "server"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Watch Rule**

```
{
  "action": "remove_watch",
  "name": "wininet-loading"
}
```

### Performance Rules

**Add Performance Rule**

```
{
  "action": "add_perf_rule",
  "name": "sql-servers",
  "tags": [
    "sql"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Performance Rule**

```
{
  "action": "remove_perf_rule",
  "name": "sql-servers"
}
```

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
