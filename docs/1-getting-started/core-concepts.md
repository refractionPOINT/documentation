# LimaCharlie Core Concepts

## Sensors

### Endpoint Agents

The LimaCharlie endpoint agent is a cross platform sensor. The sensor is small, runs at a low level, and does detection and response in real time.

The sensor has many capabilities.

- Flight Data Recorder (FDR) functions such as processes, network connections, and domain name requests.
- Host isolation, automated response rules, and a local cache of events for Incident Response (IR). Forensic functions such as memory dumps are also available.

Sensors limit the damage that an attacker can do with unauthorized access to the LimaCharlie platform. The sensor does not accept open-ended commands. An attacker therefore cannot use the sensor to upload malicious software to your hosts in secret. The sensor keeps its "read-only" qualities on your infrastructure. The cloud logs all access to the hosts and all interaction with them for audit. It also forwards these logs to your own infrastructure in a tamper-proof form.

The [Endpoint Agent Commands](../8-reference/endpoint-commands.md) section gives the full list of commands.

### Adapters

The LimaCharlie Adapter ingests any structured data, such as logs or telemetry, into the LimaCharlie platform in real time. The platform treats this data like any other data source. You can then apply detection and response rules to the data, or send the data to other outputs. Adapters support formats such as JSON, Syslog, and CEFL. You can deploy an adapter on-premise or cloud-to-cloud, with or without the EDR sensor.

Built-in mappings make ingestion more simple for known sources such as cloud platforms or Windows Event Logs. Text-based Adapters support custom mappings and automation for any structured text. Pre-defined Adapters give guided setups for common data sources such as AWS CloudTrail and GuardDuty. LimaCharlie also supports specialized adapters such as Office 365 and Slack, with detailed configuration instructions. Some cloud-to-cloud Adapters, such as AWS S3, delete the data after ingestion. Use a dedicated bucket with the correct permissions for these adapters.

## Installation Keys

You use an Installation Key to install a sensor. The key ties the sensor cryptographically to your account.

The [Installation Keys section](../2-sensors-deployment/installation-keys.md) gives more details.

## Tags

Sensors can have Tags. You add a Tag when you create the sensor. You can also add a Tag later with the web app, the API, or Detection & Response Rules.

The [Sensor tags section](../2-sensors-deployment/sensor-tags.md) gives more information.

## Detection & Response Rules

Detection & Response Rules are an automation engine. The Detection component matches an event, or it does not match. If the Detection component matches, LimaCharlie runs the Response component of the rule. The Response component can investigate, mitigate, or apply Tags automatically.

The [Detection & Response section](../3-detection-response/index.md) gives a detailed explanation.

## Insight

Insight is the built-in feature for data retention and search. It is enabled by default, and it is included in the free tier of 2 sensors.

LimaCharlie configures Insight for you. You get access to one year of your data to visualize and query.

You do not *have to* use the built-in data retention. You can send data directly to your infrastructure instead. But Insight is usually more simple to use. If you disable Insight, the data that LimaCharlie already collected stays stored and searchable for the original retention period. If you do not want to use Insight, read the next section (Outputs).

## Outputs

If you use Insight (data retention), this section is optional.

LimaCharlie can send the data to another location for long-term storage and analysis. The Outputs that you activate control the destination of the data. You can activate as many Output modules as you want. For example, you can send the data to several syslog destinations with the Syslog Output module, and also send it to cold storage with the Scp Output module.

Output is also split between four categories:

- event
- detect
- audit
- deployment

When you create an Output, select a Stream. The Stream sets the type of data that moves through the Output.

The [Outputs section](../5-integrations/outputs/index.md) gives more details and the exact configuration options.

## LimaCharlie Data Structures

You must know the core data structures in LimaCharlie to work with Detection & Response rules, LCQL queries, and outputs. All data in LimaCharlie moves through one of four primary structures.

### The Four Core Structures

#### 1. Events (`event` stream)

**What**: Real-time telemetry from sensors and adapters
**Structure**: Two top-level objects - `routing` (metadata) and `event` (event-specific data)
**Examples**: Process execution (NEW_PROCESS), DNS queries (DNS_REQUEST), network connections (NETWORK_CONNECTIONS), Windows Event Logs (WEL)

Events are the foundation of LimaCharlie. They record what happens on your endpoints and in your infrastructure. Every event includes:

- `routing` object: Consistent metadata like sensor ID, timestamp, hostname, platform
- `event` object: Event-type-specific data like file paths, command lines, network addresses

[See complete Event Structure Reference](../8-reference/event-schemas.md#event-structure-reference)

#### 2. Detections (`detect` stream)

**What**: Alerts generated when D&R rules match events
**Structure**: Includes original event's `routing`, the triggering `detect` (event data), plus detection metadata
**Key Fields**: `cat` (detection name), `source`, `detect_id`, `priority`, `detect_mtd` (metadata), `detect_data` (extracted IOCs)

When a D&R rule matches an event, LimaCharlie creates a Detection. A Detection inherits the routing information of the event and adds:

- Detection metadata: rule name, author, priority, tags
- Extracted data: Structured IOCs taken from the event
- Links: References to documentation or playbooks

[See complete Detection Structure Reference](../3-detection-response/tutorials/writing-testing-rules.md)

#### 3. Audit (`audit` stream)

**What**: Platform management and operational events
**Structure**: Flat object with `oid`, `ts` (timestamp), and audit-specific fields
**Examples**: Configuration changes, user actions, API calls, sensor deployments

Audit logs record what happens in your LimaCharlie organization:

- Who did the actions (`ident` - identity)
- What the action affected (`entity` - object)
- Action characteristics (`mtd` - metadata)
- Error messages (`component`, `error`)

#### 4. Deployment Events (`deployment` stream)

**What**: Sensor deployment and lifecycle events
**Structure**: Similar to events - `routing` and `event` objects
**Examples**: Sensor installations, uninstallations, version updates

### Why These Structures Matter

#### For D&R Rules

D&R rules operate on Events and produce Detections. Knowledge of the Event structure helps you to:

- Access the right fields with `event/` and `routing/` paths
- Filter by event type, platform, or sensor
- Correlate related events with `routing/this` and `routing/parent`

#### For LCQL Queries

LCQL can query all three primary streams (event, detect, audit). Knowledge of the structure helps you to:

- Select the right fields for investigation
- Join data across streams
- Filter efficiently with the correct field paths

#### For Outputs

Each output stream type has a different structure. Knowledge of the structure helps you to:

- Configure the right stream for your destination
- Build parsers for external systems
- Filter data before you send it

### Data Flow: Event → Detection

This is the most common data transformation in LimaCharlie:

```text
1. Sensor generates Event
   {routing: {...}, event: {FILE_PATH: "evil.exe", ...}}

2. D&R rule matches Event
   detect: {event: NEW_PROCESS, op: contains, path: event/FILE_PATH, value: "evil"}

3. LimaCharlie creates Detection
   {routing: {...},          # Inherited from Event
    detect: {...},           # Copy of the Event data
    cat: "Suspicious File",  # Detection metadata
    detect_id: "uuid...",
    priority: 5,
    detect_data: {malicious_file: "evil.exe"}}
```

### Field Path Patterns

All LimaCharlie structures use consistent path patterns:

- **Events**: `event/FIELD_NAME` or `routing/FIELD_NAME`
- **Detections**: `detect/FIELD_NAME` (for event data), `routing/FIELD_NAME`, or top-level like `cat`, `priority`
- **Audit**: Direct field access like `ident`, `entity/type`, `mtd/action`

### Next Steps

- **Writing D&R Rules**: [Detection & Response Documentation](../3-detection-response/tutorials/writing-testing-rules.md)
- **Querying Data**: [LCQL Examples](../4-data-queries/lcql-examples.md)
- **Configuring Outputs**: [Output Stream Structures](../5-integrations/outputs/index.md)
- **Event Schema Details**: [Event Schemas](../8-reference/event-schemas.md#event-structure-reference)

## API Keys

API keys are UUIDs. Each key is linked to one organization. You use a key to get authorization tokens for the REST API from your programs. The [API key section](../7-administration/access/api-keys.md) gives more details.

---

## See Also

- [Quickstart Guide](quickstart.md)
- [Sensor Deployment](../2-sensors-deployment/index.md)
- [Detection & Response](../3-detection-response/index.md)
- [LCQL Queries](../4-data-queries/index.md)
