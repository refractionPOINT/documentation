The Infrastructure Extension allows you to perform infrastructure-as-code (IaC) modifications to your Organization. IaC modifications can be made in the web UI or via the LimaCharlie [CLI tool](https://github.com/refractionPOINT/python-limacharlie/#configs-1). Users can create new organizations from known templates or maintain a common configuration across multiple organizations.

> Scaling Organization Management
>
> If you’re an managed service company or need to manage a large number of Organizations, consider LimaCharlie’s MSSP setup. You can find more information about this [here](https://github.com/refractionPOINT/mssp-demo).

## Enabling the Infrastructure Extension

To enable the Infrastructure extension, navigate to the [Infrastructure extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-infrastructure) in the marketplace. Select the organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/infra-1.png "image(234).png")

After clicking **Subscribe**, the Infrastructure extension should be available almost immediately.

> Where to start?
>
> IaC can be a powerful tool for rapidly deploying and managing Organizations within LimaCharlie. To help you discover more possibilities, we have provided several example templates/configurations [here](https://github.com/refractionPOINT/templates).

## Using the Infrastructure Extension

Once enabled, you will see an Infrastructure as Code option under the **Organization Settings** within the LimaCharlie web UI. The extension also becomes available via the REST API.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/infra-2.png "image(240).png")

Within the Infrastructure As Code module, you can:

* **Apply a New Config** to an existing organization. Changes are made additively, and are good for merging new configuration parameters into your organization.
* **Edit the Entire Configuration** for an existing organization. This is your current configuration, and can be modified directly in the web UI.
* Perform **Fetch**, **Push**, or **Push-from-file** operations.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/infra-3.png "image(241).png")

## Actions via REST API

The REST interface for the Infrastructure extension mimics the CLI tool. The following REST API actions can be sent to interact with the Infrastructure extension:

```
{
  "params": {
    "sync_artifacts": {
      "type": "bool",
      "desc": "applies to artifacts"
    },
    "is_force": {
      "type": "bool",
      "desc": "make the org an exact copy of the configuration provided."
    },
    "is_dry_run": {
      "type": "bool",
      "desc": "do not apply config, just simulate."
    },
    "sync_integrity": {
      "type": "bool",
      "desc": "applies to integrity"
    },
    "action": {
      "is_required": true,
      "values": [
        "push",
        "fetch"
      ],
      "type": "enum",
      "desc": "action to take."
    },
    "sync_org_values": {
      "type": "bool",
      "desc": "applies to org_values"
    },
    "sync_resources": {
      "type": "bool",
      "desc": "applies to resources"
    },
    "config": {
      "type": "str",
      "desc": "configuration to apply."
    },
    "config_source": {
      "type": "str",
      "desc": "ARL where configs to apply are located."
    },
    "ignore_inaccessible": {
      "desc": "ignore resources which are inaccessible like locked or segmented.",
      "type": "bool"
    },
    "sync_fp": {
      "type": "bool",
      "desc": "applies to fp"
    },
    "sync_exfil": {
      "desc": "applies to exfil",
      "type": "bool"
    },
    "sync_dr": {
      "type": "bool",
      "desc": "applies to dr"
    },
    "sync_outputs": {
      "type": "bool",
      "desc": "applies to outputs"
    },
    "config_root": {
      "type": "str",
      "desc": "file name of the root config within config_source to apply."
    }
  }
}
```

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Managed Security Services Provider

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Command-line Interface
