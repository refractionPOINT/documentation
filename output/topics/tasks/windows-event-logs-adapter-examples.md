These documents are identical duplicates. Here is the synthesized version:

# Windows Event Logs

This example shows collecting Windows Event Logs (`wel`) from a Windows box natively (and therefore is only available using the Windows Adapter). This is useful for cases where you'd like to collect WEL without running the LimaCharlie Windows Agent.

## Configuration Example

```
./lc_adapter wel client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d `
    client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd `
    client_options.sensor_seed_key=domain-controller1 `
    client_options.platform=wel `
    evt_sources=security:*,application:*,system:*,Microsoft-Windows-Windows Defender/Operational:*
```

## Parameter Breakdown

* **`lc_adapter`**: The CLI Adapter executable
* **`wel`**: The collection method the Adapter should use locally. The `wel` value will use a native local Windows Event Logs subscription
* **`client_options.identity.installation_key=....`**: The Installation Key value from LimaCharlie
* **`client_options.identity.oid=....`**: The Organization ID from LimaCharlie the installation key above belongs to
* **`client_options.platform=wel`**: Indicates the type of data that will be received from this adapter. In this case it's `wel` events
* **`client_options.sensor_seed_key=....`**: The value that identifies this instance of the Adapter. Record it to re-use the Sensor ID generated for this Adapter later if you have to re-install the Adapter
* **`evt_sources=....`**: A comma separated list of event channels to collect along with an XPath filter expression for each. The format is `CHANNEL_NAME:FILTER_EXPRESSION` where a filter of `*` means all events. Common channels include: `security`, `system`, and `application`

## Key Concepts

**Adapters** serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

**Installation Keys** are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

**Sensors** send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Similar to agents, Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.