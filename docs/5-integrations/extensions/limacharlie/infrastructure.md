# Infrastructure

The Infrastructure Extension allows you to perform infrastructure-as-code (IaC) modifications to your Organization. IaC modifications can be made in the web UI or via the LimaCharlie [CLI tool](https://github.com/refractionPOINT/python-limacharlie/#configs-1). Users can create new organizations from known templates or maintain a common configuration across multiple organizations.

> Scaling Organization Management
>
> If you're a managed service company or need to manage a large number of Organizations, keep the configuration in a Git repository and apply it with the [Git Sync](git-sync.md) extension. The [MSSP Git Sync tutorial](../../../1-getting-started/mssp-iac-tutorial.md) sets it up step by step. LimaCharlie's [MSSP demo setup](https://github.com/refractionPOINT/mssp-demo) shows the same idea driven from the CLI.

## Enabling the Infrastructure Extension

To enable the Infrastructure extension, navigate to the [Infrastructure extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-infrastructure) in the marketplace. Select the organization you wish to enable the extension for, and select **Subscribe**.

![infra 1.png "image(234).png"](../../../assets/images/infra-1.png "image(234).png")

After clicking **Subscribe**, the Infrastructure extension should be available almost immediately.

> Where to start?
>
> IaC can be a powerful tool for rapidly deploying and managing Organizations within LimaCharlie. We provide [example templates and configurations](https://github.com/refractionPOINT/templates) on GitHub.

## Using the Infrastructure Extension

Once enabled, you will see an Infrastructure as Code option under the **Organization Settings** within the LimaCharlie web UI. The extension also becomes available via the REST API.

![infra 2.png "image(240).png"](../../../assets/images/infra-2.png "image(240).png")

Within the Infrastructure As Code module, you can:

- **Apply a New Config** to an existing organization. Changes are made additively, and are good for merging new configuration parameters into your organization.
- **Edit the Entire Configuration** for an existing organization. This is your current configuration, and can be modified directly in the web UI.
- Perform **Fetch**, **Push**, or **Push-from-file** operations.

![infra 3.png "image(241).png"](../../../assets/images/infra-3.png "image(241).png")

## Actions via REST API

The REST interface for the Infrastructure extension mimics the CLI tool. The following REST API actions can be sent to interact with the Infrastructure extension:

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

## Backing up an organization with the CLI

`limacharlie sync pull` writes the organization's configuration to a YAML file. Two flags select everything:

- `--all` pulls every resource type and hive. It is strict: if the API key cannot read one of the hives, the pull fails with the missing permission.
- `--all-available` pulls the same set but skips the hives the key has no permission for, so a scheduled backup does not break when LimaCharlie adds a hive or a permission.

```bash
limacharlie sync pull --config-file org.yaml --all-available
```

For each skipped hive, the CLI prints a warning to stderr, also with `--quiet`, and the command still exits 0:

```text
Warning: skipped hive host_posture_rule: this key lacks host_posture.get; grant it to include this hive in the sync.
```

Grant the permission named in the warning to include that hive in the file. Use `--all-available` for nightly backups, and `--all` when you want a missing permission to be an error. A file written by `--all-available` leaves out the hives that were skipped, and nothing in the file records which. Do not restore such a file with `sync push --all --force`, which deletes cloud records that are missing from the file for every selected hive; restore with explicit `--hive-*` flags, or without `--force`. The two flags cannot be combined. `--all-available` is for `pull` only: `push` only touches the hives present in the file, so it does not hit hives the key cannot read. It needs a version of the Infrastructure extension that supports skipping; an older one fails on the first hive the key cannot read, as `--all` does.

## Related Articles

- [Integrity](integrity.md)
