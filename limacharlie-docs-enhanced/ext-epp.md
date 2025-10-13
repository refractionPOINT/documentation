## Overview

The Endpoint Protection (EPP) management in LimaCharlie enables users to view the status of existing EPP solutions (including Windows Free Defender), manage parameters of the deployment and unify alerting from the deployment at scale. This makes it perfect for teams wanting a unified view of the EPP solution, or service providers looking to offer Managed EPP to their customers at scale.

The only requirement is for the LimaCharlie agent to be deployed and the EPP Extension enabled (free).

Once deployed, EPP can be used natively along with the rest of LimaCharlie’s automation and routing capabilities.

## How it Works

LimaCharlie Endpoint Protection integrates with third-party EDR solutions to provide a better view of security operations and extend agent’s capabilities. Currently this extension applies to:

* Microsoft Windows Defender

The LimaCharlie agent communicates with Windows Defender to determine its status, transfer events, and trigger remediation commands. LimaCharlie Endpoint Protection codifies the best practices of collecting events and alerting on detections. When enabled, this extension creates a starter set of  rules. In addition to alerting, these rules can be customized to better align with the operational complexity of user’s environments. The LC Endpoint Protection extension provides a reliable and cost efficient way of securing endpoints at scale.

The Endpoint Protection add-on requires agent version `4.33.5` or higher.

## Enabling and configuring Endpoint Protection

To enable Endpoint Protection, first ensure LimaCharlie Endpoint Agent version is 4.33.5 and above, [update](/v2/docs/endpoint-agent-versioning-and-upgrades) if necessary.

Navigate to the [Endpoint Protection extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-epp) in the Add-Ons marketplace. Choose the target Organization and select `Subscribe`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(335).png)

Once subscribed, you can see the Endpoint Protection in the list of Extensions.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(332).png)

The Endpoint Protection extension does two things once both sync settings are enabled:

1. Creates an artifact collection rule named `defender-log-streaming`

   * This rule adds a WEL pattern that collects MS Defender logs, `wel://Microsoft-Windows-Windows Defender/Operational:*` so that LimaCharlie receives the events the Defender produces.

     > Note
     >
     > If you already have Defender logs coming in via the Artifact extension, you can uncheck the `Sync Extension Config` box to avoid duplicating entries.
2. Creates D&R rules

   * Generates several D&R rules that alert on various detections and actions taken by Defender.![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(291).png)
3. To apply the Artifact extension configuration and D&R rules, click `Apply Configuration`.

When the SYNC toggles are on, the collection rules and D&R rules are continuously synchronized with LimaCharlie library of best practices.

Once the extension is enabled, it also extends the Web UI with Endpoint Protection functionality, as described below.

## Using the Endpoint Protection extension

Endpoint Protection capabilities are used in three ways.

**Verify Protection**

Select a Windows Sensor in the organization. In the Sensor Overview, there is a new section, “Endpoint Protection” that shows the current protection status. Verify that Defender is listed as active on the sensor.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(333).png)

**Perform Scan**

Select a Windows Sensor.

Click on File System. Select the folder, and click on the scan icon  `Scan with EPP`

**Endpoint Protection Commands**

Select a Windows Sensor. Open the Sensor Console As you type “epp” you’ll see the available commands. Try `epp_status`  - it will return the status.

> Events required in Exfil config
>
> The EPP solution relies on some new events. They are now defaults, and the extension adds them to existing orgs. In rare case you may need to add them manually to Sensor / Event Collection / Event Collection or your Infra As Code. Here is the list:
>
> ```
> EPP_STATUS_REP,EPP_LIST_EXCLUSIONS_REP,EPP_ADD_EXCLUSION_REP,EPP_REM_EXCLUSION_REP,
> EPP_LIST_QUARANTINE_REP,EPP_SCAN_REP
> ```

For reference, this is a list of Endpoint Protection commands:

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(323).png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(325).png)![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(327).png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(329).png)![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(328).png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(330).png)

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Endpoint Detection & Response

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.
