# OTX

AlienVault's Open Threat Exchange (OTX) is the "neighborhood watch of the global intelligence community." Private companies, independent security researchers, and government agencies use OTX to collaborate openly. They share the latest information about new threats, attack methods, and malicious actors. This gives more security to the full community.

[More information about OTX](https://otx.alienvault.com/) is available on the AlienVault site.

## Enabling the OTX Extension

Before you use the OTX extension, you need an AlienVault OTX API Key from your [AlienVault OTX account](https://otx.alienvault.com/).

1. Go to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx).
2. Select the organization to enable the extension for.
3. Select **Subscribe**.
4. After the extension is enabled, go to Extensions > OTX.
5. Give your OTX API Key. Enter the key in the form, or use the LimaCharlie [Secrets Manager](../../../7-administration/config-hive/secrets.md).

The extension syncs pulses to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After you give a valid API key, the extension automatically creates [Detection & Response rules](https://doc.limacharlie.io/docs/detection-and-response) for your organization. The OTX rules use these events:

- Process Events
  - [CODE_IDENTITY](../../../8-reference/edr-events.md#code_identity)
  - [EXISTING_PROCESS](../../../8-reference/edr-events.md#existing_process)
  - [MEM_HANDLES_REP](../../../8-reference/edr-events.md#mem_handles_rep) (response to the [mem_handles](../../../8-reference/endpoint-commands.md) Sensor command)
  - [NEW_PROCESS](../../../8-reference/edr-events.md#new_process)
- Network Events
  - [DNS_REQUEST](../../../8-reference/edr-events.md#dns_request)
  - [HTTP_REQUEST](../../../8-reference/edr-events.md#http_request)
  - [NETWORK_CONNECTIONS](../../../8-reference/edr-events.md#network_connections)
  - [NEW_TCP4_CONNECTION](../../../8-reference/edr-events.md#new_tcp4_connection)
  - [NEW_TCP6_CONNECTION](../../../8-reference/edr-events.md#new_tcp6_connection)
  - [NEW_UDP4_CONNECTION](../../../8-reference/edr-events.md#new_udp4_connection)
  - [NEW_UDP6_CONNECTION](../../../8-reference/edr-events.md#new_udp6_connection)

Make sure that the events that you use with OTX lookups are enabled in the **Sensors >** Event Collection menu.
