# OTX

AlienVault's Open Threat Exchange (OTX) is the "neighborhood watch of the global intelligence community." It enables private companies, independent security researchers, and government agencies to openly collaborate and share the latest information about emerging threats, attack methods, and malicious actors, promoting greater security across the entire community.

More information about OTX can be found [here](https://otx.alienvault.com/).

## Enabling the OTX Extension

Before utilizing the OTX extension, you will need an AlienVault OTX API Key. This can be found in your AlienVault OTX account [here](https://otx.alienvault.com/).

To enable the OTX extension, navigate to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx). Select the Organization you wish to enable the extension for, and select **Subscribe**.

Once the extension is enabled, navigate to Extensions > OTX. You will need to provide your OTX API Key, which can be done directly in the form or via LimaCharlie's [Secrets Manager](../../../7-administration/config-hive/secrets.md).

Pulses will be synced to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After providing a valid API key, the Extension will automatically create [Detection & Response rules](https://doc.limacharlie.io/docs/detection-and-response) for your organization. The OTX rules make use of the following events:

* Process Events
  + [CODE_IDENTITY](../../../8-reference/edr-events.md#codeidentity)
  + [EXISTING_PROCESS](../../../8-reference/edr-events.md#existingprocess)
  + [MEM_HANDLES_REP](../../../8-reference/edr-events.md#memhandlesrep) (response to the [mem_handles](../../../8-reference/endpoint-commands.md#memhandles) Sensor command)
  + [NEW_PROCESS](../../../8-reference/edr-events.md#newprocess)
* Network Events
  + [DNS_REQUEST](../../../8-reference/edr-events.md#dnsrequest)
  + [HTTP_REQUEST](../../../8-reference/edr-events.md#httprequest)
  + [NETWORK_CONNECTIONS](../../../8-reference/edr-events.md#networkconnections)
  + [NEW_TCP4_CONNECTION](../../../8-reference/edr-events.md#newtcp4connection)
  + [NEW_TCP6_CONNECTION](../../../8-reference/edr-events.md#newtcp6connection)
  + [NEW_UDP4_CONNECTION](../../../8-reference/edr-events.md#newudp4connection)
  + [NEW_UDP6_CONNECTION](../../../8-reference/edr-events.md#newudp6connection)

Please ensure that the events you are interested in using with OTX lookups are enabled in the **Sensors >** Event Collection menu.
