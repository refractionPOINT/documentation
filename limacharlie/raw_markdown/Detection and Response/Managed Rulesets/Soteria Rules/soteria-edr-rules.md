# Soteria EDR Rules

Soteria's EDR ruleset provides coverage across Windows, Linux, and macOS. You can check the dynamic MITRE ATT&CK mapping here:

  * [All rules](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json)
  * [Windows](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//windows.json)
  * [Linux](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//linux.json)
  * [macOS](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//mac.json)

## Data access

Please note that Soteria won't get access to your data, and you won't be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

The following events are utilized by Soteria rules. Please ensure that they are configured within your Organization:

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

This can also be done in the Add-ons Marketplace.

## Enabling Soteria's EDR Rules

Soteria's EDR rules can be activated via two means.

### Activating via the Web UI

To enable Soteria's EDR ruleset, navigate to the **Extensions** section of the Add-On Marketplace and search for Soteria. You can also directly select `soteria-rules-edr`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-1.png)

_Please note: Pricing may reflect when the screenshot was taken, not the actual pricing_

Under the Organization dropdown, select a tenant (organization) you want to subscribe to Soteria rules and click **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-3.png)

### Infrastructure as Code

Alternatively, to manage tenants and LimaCharlie functionality at scale, you can leverage our Infrastructure as Code functionality.
