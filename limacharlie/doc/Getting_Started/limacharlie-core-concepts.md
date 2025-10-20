# LimaCharlie Core Concepts

### Sensors

#### Endpoint Agents

The LimaCharlie endpoint agent is a cross platform endpoint Sensor. It is a low-level, light-weight sensor which executes detection and response functionality in real-time.

The sensor provides a wide range of advanced capability.

* Flight Data Recorder (FDR) type functionality like Processes, Network Connections, Domain Name requests etc.
* Host isolation, automated response rules, intelligent local caching of events for in-depth Incident Response (IR) as well as some forensic features like dumping memory.

Sensors are designed to limit the potential for abuse resulting from unauthorized access to the LimaCharlie platform. This is achieved by limiting open-ended commands which might enable an attacker to covertly upload malicious software to your hosts. This means the LimaCharlie sensor is extremely powerful but also keeps its "read-only" qualities on your infrastructure. Of course, all access and interactions with the hosts are also logged for audit both within the cloud and tamper-proof forwarding to your own infrastructure.

Full commands list is in the [Endpoint Agent Commands](../Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md) section.

#### Adapters

The LimaCharlie Adapter allows for real-time ingestion of any structured data, such as logs or telemetry, into the LimaCharlie platform, treating it as a first-class data source. This enables users to apply detection and response rules or send data to other outputs. Adapters support formats like JSON, Syslog, and CEFL, and can be deployed on-premise or cloud-to-cloud, either with or without the EDR sensor. For known sources like cloud platforms or Windows Event Logs, built-in mappings simplify data ingestion. Text-based Adapters allow for custom mapping and automation of any structured text. Additionally, pre-defined Adapters offer guided setups for common data sources like AWS CloudTrail and GuardDuty, while specialized connectors like Office 365 and Slack are supported with detailed configuration guidance. Some cloud-to-cloud Adapters, such as AWS S3, delete data after ingestion, so dedicated buckets with proper permissions are recommended.

### Installation Keys

Installation Keys are used to install a sensor. By specifying a key during installation the sensor can cryptographically be tied to your account.

Get more details in the [Installation Keys section](../Platform_Management/Installation_Keys/installation-keys.md).

### Tags

Sensors can have Tags associated with them. Tags are added during creation or dynamically through the UI, API or Detection & Response Rules.

Get more information in the [Sensor tags section](../Sensors/sensor-tags.md).

### Detection & Response Rules

The Detection & Response Rules act as an automation engine. The Detection component is a rule that either matches an event or not. If the Detection component matches, the Response component of the rule is actioned. This can be used to automatically investigate, mitigate or apply Tags.

Detailed explanation in the [Detection & Response section](../Detection_and_Response/detection-and-response.md).

### Insight

Insight is our built-in data retention and search feature. It is included within our 2 sensor free tier as well.

When you enable Insight, we configure everything for you so that you get access to one year of your data for visualization and searching.

You don't *have to* use the built-in data retention; you can forward data directly to your infrastructure if preferred. However, it is generally much simpler and a better experience to use Insight. If you prefer not to use Insight, go through the next section (Outputs).

### Outputs

If you are using Insight (data retention) this section is optional.

LimaCharlie can relay the data somewhere for longer term storage and analysis. Where that data is sent depends on which Outputs are activated. You can have as many Output modules active as you want, so you can send it to multiple syslog destinations using the Syslog Output module and then send it to some cold storage over an Scp Output module.

Output is also split between four categories:

* event
* detect
* audit
* deployment

Selecting a Stream when creating an Output will select the relevant type of data to flow through it.

More details and exact configuration possibilities in the [Outputs section](../Outputs/outputs.md).

### API Keys

The API keys are represented as UUIDs. They are linked to your specific organization and enable you to programmatically acquire authorization tokens that can be used on our REST API. See the [API key section](../Platform_Management/Access_and_Permissions/api-keys.md) for more details.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
