# Infrastructure

The Infrastructure Extension lets you make infrastructure-as-code (IaC) changes to your Organization. You can make IaC changes in the web app or with the LimaCharlie [CLI tool](https://github.com/refractionPOINT/python-limacharlie/#configs-1). You can create new organizations from known templates. You can also keep one common configuration across many organizations.

> Scaling Organization Management
>
> If you are a managed service company, or if you must manage many Organizations, look at the LimaCharlie [MSSP demo setup](https://github.com/refractionPOINT/mssp-demo).

## Enabling the Infrastructure Extension

To enable the Infrastructure extension, do these steps:

1. Open the [Infrastructure extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-infrastructure) in the marketplace.
2. Select the organization that you want to enable the extension for.
3. Select **Subscribe**.

![infra 1.png "image(234).png"](../../../assets/images/infra-1.png "image(234).png")

After you select **Subscribe**, the Infrastructure extension becomes available almost immediately.

> Where to start?
>
> IaC deploys and manages Organizations in LimaCharlie quickly. LimaCharlie supplies [example templates and configurations](https://github.com/refractionPOINT/templates) on GitHub.

## Using the Infrastructure Extension

After you enable the extension, an Infrastructure as Code option shows under **Organization Settings** in the LimaCharlie web app. The extension also becomes available through the REST API.

![infra 2.png "image(240).png"](../../../assets/images/infra-2.png "image(240).png")

In the Infrastructure As Code module, you can do these actions:

- **Apply a New Config** to an existing organization. The extension adds the changes to the current configuration. Use this action to merge new configuration parameters into your organization.
- **Edit the Entire Configuration** for an existing organization. This is your current configuration. You can change it directly in the web app.
- Do **Fetch**, **Push**, or **Push-from-file** operations.

![infra 3.png "image(241).png"](../../../assets/images/infra-3.png "image(241).png")

## Actions via REST API

The REST interface for the Infrastructure extension copies the CLI tool. Send these REST API actions to the Infrastructure extension:

```json
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

## Related Articles

- [Integrity](integrity.md)
