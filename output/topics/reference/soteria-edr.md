# Soteria EDR Rules

Soteria's EDR ruleset provides comprehensive threat detection coverage across Windows, Linux, and macOS platforms. You can review the dynamic MITRE ATT&CK mapping for each platform:

* [All rules](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json)
* [Windows](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//windows.json)
* [Linux](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//linux.json)
* [macOS](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//mac.json)

## Data Access and Privacy

Soteria operates with strict data privacy controls - Soteria does not receive access to your data, and you cannot view or edit their proprietary detection rules. LimaCharlie functions as a secure broker between your organization and Soteria's detection capabilities.

## Required Event Types

The following event types are utilized by Soteria rules and must be configured within your Organization for the rules to function properly:

* `CODE_IDENTITY`
* `DNS_REQUEST`
* `EXISTING_PROCESS`
* `FILE_CREATE`
* `FILE_MODIFIED`
* `MODULE_LOAD`
* `NETWORK_CONNECTIONS`
* `NEW_DOCUMENT`
* `NEW_NAMED_PIPE`
* `NEW_PROCESS`
* `REGISTRY_WRITE`
* `REGISTRY_CREATE`
* `SENSITIVE_PROCESS_ACCESS`
* `THREAD_INJECTION`

These event types can be configured through the Add-ons Marketplace.

## Enabling Soteria's EDR Rules

Soteria's EDR rules can be activated through two methods:

### Activating via the Web UI

To enable Soteria's EDR ruleset through the web interface:

1. Navigate to the **Extensions** section of the Add-On Marketplace
2. Search for "Soteria" or directly select `soteria-rules-edr`

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-1.png)

3. Under the Organization dropdown, select the tenant (organization) you want to subscribe to Soteria rules
4. Click **Subscribe**

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-3.png)

### Infrastructure as Code

For managing tenants and LimaCharlie functionality at scale, you can leverage LimaCharlie's Infrastructure as Code functionality to programmatically enable and configure Soteria EDR rules across multiple organizations.

## Understanding Organizations in LimaCharlie

In LimaCharlie, an **Organization** represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This multi-tenant structure is ideal for managed security service providers (MSSPs) or enterprises managing multiple departments or clients.