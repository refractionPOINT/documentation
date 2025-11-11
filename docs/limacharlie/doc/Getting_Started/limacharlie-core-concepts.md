# LimaCharlie Core Concepts

## Sensors

### Endpoint Agents

The LimaCharlie endpoint agent is a cross platform endpoint Sensor. It is a low-level, light-weight sensor which executes detection and response functionality in real-time.

The sensor provides a wide range of advanced capability.

* Flight Data Recorder (FDR) type functionality like Processes, Network Connections, Domain Name requests etc.
* Host isolation, automated response rules, intelligent local caching of events for in-depth Incident Response (IR) as well as some forensic features like dumping memory.

Sensors are designed to limit the potential for abuse resulting from unauthorized access to the LimaCharlie platform. This is achieved by limiting open-ended commands which might enable an attacker to covertly upload malicious software to your hosts. This means the LimaCharlie sensor is extremely powerful but also keeps its "read-only" qualities on your infrastructure. Of course, all access and interactions with the hosts are also logged for audit both within the cloud and tamper-proof forwarding to your own infrastructure.

Full commands list is in the [Endpoint Agent Commands](../Sensors/Endpoint_Agent/endpoint-agent-commands.md) section.

### Adapters

The LimaCharlie Adapter allows for real-time ingestion of any structured data, such as logs or telemetry, into the LimaCharlie platform, treating it as a first-class data source. This enables users to apply detection and response rules or send data to other outputs. Adapters support formats like JSON, Syslog, and CEFL, and can be deployed on-premise or cloud-to-cloud, either with or without the EDR sensor. For known sources like cloud platforms or Windows Event Logs, built-in mappings simplify data ingestion. Text-based Adapters allow for custom mapping and automation of any structured text. Additionally, pre-defined Adapters offer guided setups for common data sources like AWS CloudTrail and GuardDuty, while specialized connectors like Office 365 and Slack are supported with detailed configuration guidance. Some cloud-to-cloud Adapters, such as AWS S3, delete data after ingestion, so dedicated buckets with proper permissions are recommended.

## Installation Keys

Installation Keys are used to install a sensor. By specifying a key during installation the sensor can cryptographically be tied to your account.

Get more details in the [Installation Keys section](../Sensors/installation-keys.md).

## Tags

Sensors can have Tags associated with them. Tags are added during creation or dynamically through the UI, API or Detection & Response Rules.

Get more information in the [Sensor tags section](../Sensors/sensor-tags.md).

## Detection & Response Rules

The Detection & Response Rules act as an automation engine. The Detection component is a rule that either matches an event or not. If the Detection component matches, the Response component of the rule is actioned. This can be used to automatically investigate, mitigate or apply Tags.

Detailed explanation in the [Detection & Response section](../Detection_and_Response/detection-and-response.md).

## Insight

Insight is our built-in data retention and search feature. It is included within our 2 sensor free tier as well.

When you enable Insight, we configure everything for you so that you get access to one year of your data for visualization and searching.

You don't *have to* use the built-in data retention; you can forward data directly to your infrastructure if preferred. However, it is generally much simpler and a better experience to use Insight. If you prefer not to use Insight, go through the next section (Outputs).

## Outputs

If you are using Insight (data retention) this section is optional.

LimaCharlie can relay the data somewhere for longer term storage and analysis. Where that data is sent depends on which Outputs are activated. You can have as many Output modules active as you want, so you can send it to multiple syslog destinations using the Syslog Output module and then send it to some cold storage over an Scp Output module.

Output is also split between four categories:

* event
* detect
* audit
* deployment

Selecting a Stream when creating an Output will select the relevant type of data to flow through it.

More details and exact configuration possibilities in the [Outputs section](../Outputs/outputs.md).

## LimaCharlie Data Structures

Understanding the core data structures in LimaCharlie is essential for working with Detection & Response rules, LCQL queries, and outputs. All data in LimaCharlie flows through one of four primary structures.

### The Four Core Structures

#### 1. Events (`event` stream)
**What**: Real-time telemetry from sensors and adapters
**Structure**: Two top-level objects - `routing` (metadata) and `event` (event-specific data)
**Examples**: Process execution (NEW_PROCESS), DNS queries (DNS_REQUEST), network connections (NETWORK_CONNECTIONS), Windows Event Logs (WEL)

Events are the foundation of LimaCharlie. They capture what's happening on your endpoints and in your infrastructure. Every event includes:
- `routing` object: Consistent metadata like sensor ID, timestamp, hostname, platform
- `event` object: Event-type-specific data like file paths, command lines, network addresses

[See complete Event Structure Reference](../Events/event-schemas.md#event-structure-reference)

#### 2. Detections (`detect` stream)
**What**: Alerts generated when D&R rules match events
**Structure**: Includes original event's `routing`, the triggering `detect` (event data), plus detection metadata
**Key Fields**: `cat` (detection name), `source`, `detect_id`, `priority`, `detect_mtd` (metadata), `detect_data` (extracted IOCs)

When a D&R rule matches an event, LimaCharlie creates a Detection. Detections inherit the event's routing information and add:
- Detection metadata: rule name, author, priority, tags
- Extracted data: Structured IOCs pulled from the event
- Links: References to documentation or playbooks

[See complete Detection Structure Reference](../Detection_and_Response/writing-and-testing-rules.md#understanding-detection-structure)

#### 3. Audit (`audit` stream)
**What**: Platform management and operational events
**Structure**: Flat object with `oid`, `ts` (timestamp), and audit-specific fields
**Examples**: Configuration changes, user actions, API calls, sensor deployments

Audit logs track what happens in your LimaCharlie organization:
- Who performed actions (`ident` - identity)
- What was affected (`entity` - object)
- Action characteristics (`mtd` - metadata)
- Error messages (`component`, `error`)

#### 4. Deployment Events (`deployment` stream)
**What**: Sensor deployment and lifecycle events
**Structure**: Similar to events - `routing` and `event` objects
**Examples**: Sensor installations, uninstallations, version updates

### Why These Structures Matter

#### For D&R Rules
D&R rules operate on Events and produce Detections. Understanding the Event structure helps you:
- Access the right fields with `event/` and `routing/` paths
- Filter by event type, platform, or sensor
- Correlate related events using `routing/this` and `routing/parent`

#### For LCQL Queries
LCQL can query all three primary streams (event, detect, audit). Knowing the structure helps you:
- Select the right fields for investigation
- Join data across streams
- Filter efficiently using the correct field paths

#### For Outputs
Each output stream type has a different structure. Understanding this helps you:
- Configure the right stream for your destination
- Build parsers for external systems
- Filter data before sending it

### Data Flow: Event → Detection

This is the most common data transformation in LimaCharlie:

```
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

- **Writing D&R Rules**: [Detection & Response Documentation](../Detection_and_Response/writing-and-testing-rules.md)
- **Querying Data**: [LCQL Examples](../Query_Console/lcql-examples.md)
- **Configuring Outputs**: [Output Stream Structures](../Outputs/outputs.md)
- **Event Schema Details**: [Event Schemas](../Events/event-schemas.md#event-structure-reference)

## API Keys

The API keys are represented as UUIDs. They are linked to your specific organization and enable you to programmatically acquire authorization tokens that can be used on our REST API. See the [API key section](../Platform_Management/Access_and_Permissions/api-keys.md) for more details.
