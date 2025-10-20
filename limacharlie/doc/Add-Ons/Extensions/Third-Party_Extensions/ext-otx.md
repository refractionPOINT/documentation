# OTX

AlienVault's Open Threat Exchange (OTX) is the "neighborhood watch of the global intelligence community." It enables private companies, independent security researchers, and government agencies to openly collaborate and share the latest information about emerging threats, attack methods, and malicious actors, promoting greater security across the entire community.

More information about OTX can be found [here](https://otx.alienvault.com/).

## Enabling the OTX Extension

Before utilizing the OTX extension, you will need an AlienVault OTX API Key. This can be found in your AlienVault OTX account [here](https://otx.alienvault.com/).

To enable the OTX extension, navigate to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx). Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(236).png)

Once the extension is enabled, navigate to Extensions > OTX. You will need to provide your OTX API Key, which can be done directly in the form or via LimaCharlie's [Secrets Manager](../../../Platform_Management/Config_Hive/config-hive-secrets.md). Click Save.

Pulses will be synced to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After providing a valid API key, the Extension will automatically create [Detection & Response rules](../../../Detection_and_Response/detection-and-response-examples.md) for your organization. The OTX  rules make use of the following events:

* Process Events
  + [CODE\_IDENTITY](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#codeidentity)
  + [EXISTING\_PROCESS](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#existingprocess)
  + [MEM\_HANDLES\_REP](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#memhandlesrep) (response to the [mem\_handles](../../../Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md#memhandles) Sensor command)
  + [NEW\_PROCESS](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#newprocess)
* Network Events
  + [DNS\_REQUEST](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#dnsrequest)
  + [HTTP\_REQUEST](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#httprequest)
  + [NETWORK\_CONNECTIONS](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#networkconnections)
  + [NEW\_TCP4\_CONNECTION](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#newtcp4connection)
  + [NEW\_TCP6\_CONNECTION](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#newtcp6connection)
  + [NEW\_UDP4\_CONNECTION](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#newudp4connection)
  + [NEW\_UDP6\_CONNECTION](../../../Events/Endpoint_Agent_Events_Overview/reference-edr-events.md#newudp6connection)

Please ensure that the events you are interested in using with OTX lookups are enabled in the **Sensors >** Event Collection menu.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.
