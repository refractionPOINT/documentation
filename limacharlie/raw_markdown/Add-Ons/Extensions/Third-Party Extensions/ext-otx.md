# OTX

AlienVault's Open Threat Exchange (OTX) is the "neighborhood watch of the global intelligence community." It enables private companies, independent security researchers, and government agencies to openly collaborate and share the latest information about emerging threats, attack methods, and malicious actors, promoting greater security across the entire community.

More information about OTX can be found [here](https://otx.alienvault.com/).

## Enabling the OTX Extension

Before utilizing the OTX extension, you will need an AlienVault OTX API Key. This can be found in your AlienVault OTX account [here](https://otx.alienvault.com/).

To enable the OTX extension, navigate to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx). Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(236).png)

Once the extension is enabled, navigate to Extensions > OTX. You will need to provide your OTX API Key, which can be done directly in the form or via LimaCharlie's [Secrets Manager](../../../Platform%20Management/Config%20Hive/config-hive-secrets.md). Click Save.

Pulses will be synced to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After providing a valid API key, the Extension will automatically create [Detection & Response rules](../../../Detection%20and%20Response/writing-and-testing-rules.md) for your organization. The OTX  rules make use of the following events:

  * Process Events

    * [CODE_IDENTITY](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#codeidentity)

    * [EXISTING_PROCESS](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#existingprocess)

    * [MEM_HANDLES_REP](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#memhandlesrep) (response to the [mem_handles](../../../Sensors/Endpoint%20Agent/Endpoint%20Agent%20Commands/reference-endpoint-agent-commands.md#memhandles) Sensor command)

    * [NEW_PROCESS](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#newprocess)

  * Network Events

    * [DNS_REQUEST](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#dnsrequest)

    * [HTTP_REQUEST](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#httprequest)

    * [NETWORK_CONNECTIONS](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#networkconnections)

    * [NEW_TCP4_CONNECTION](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#newtcp4connection)

    * [NEW_TCP6_CONNECTION](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#newtcp6connection)

    * [NEW_UDP4_CONNECTION](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#newudp4connection)

    * [NEW_UDP6_CONNECTION](../../../Events/Endpoint%20Agent%20Events%20Overview/reference-edr-events.md#newudp6connection)




Please ensure that the events you are interested in using with OTX lookups are enabled in the **Sensors > Event Collection** menu.