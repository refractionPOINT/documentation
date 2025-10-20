# Artifact

The Artifact Extension provides low-level collection capabilities which can be configured to run automatically via Detection & Response rules, Sensor collections, or pushed via REST API. When enabled, an Artifact Collection menu will be available within the LimaCharlie web UI.

> Billing for Artifacts
>
> Note that while the Artifact extension is free to enable, ingested artifacts do incur a charge. Please refer to pricing details to confirm Artifact ingestion and retention costs.

## Enabling the Artifact Extension

To enable the Artifact extension, navigate to the [Artifact extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-artifact) in the marketplace. Select the Organization you wish to enable the extension for, and select **Subscribe.**

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/artifact-1.png "image(230).png")

After clicking **Subscribe**, the Artifact extension should be available almost immediately.

> Note that the Artifact extension first requires enabling of the Reliable Tasking extension. You can find more on that extension [here](./ext-reliable-tasking.md).

## Using the Artifact Extension

When enabled, you will see an **Artifact Collection** option under **Sensors** menu for the respective organization.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/artifact-2.png "image(223).png")

Within the Artifact Collection page, you can configure:

* Artifact collection rules for files.
* Artifact collection rules to stream Windows Event Log (WEL) events.
* Artifact collection rules to stream Mac Unified Log (MUL) events.
* PCAP capture rules to capture network traffic (Only available on Linux)

The following screenshot provides examples of capturing Windows Security and Sysmon Windows Event Logs via Artifact Collection. Rather than using an Adapter, capturing WEL events via the `wel://` pattern adds the corresponding events to the sensor telemetry, creating a real-time stream of Windows Event Log data. However, you can also specify the pattern to collect the specific `.evtx` files.

More information on Artifact collections can be found [here](/docs/artifacts).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/artifact-3.png "image(224).png")

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.
