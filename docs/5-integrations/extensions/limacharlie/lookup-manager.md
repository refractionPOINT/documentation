# Lookup Manager

The Lookup Manager Extension lets you create, maintain, and automatically refresh lookups in the Organization. You can then reference these lookups in Detection & Response Rules.

You can manage the saved Lookup Configurations across tenants with the Infrastructure as Code extension. To manage lookup versions across all of your tenants, update the file under the original Authenticated Resource Locator.

Every 24 hours, LimaCharlie syncs all of the lookups in the configuration. To sync the lookups manually, click the `Manual Sync` button on the extension page. When you add a lookup configuration, LimaCharlie does **not** sync it immediately. To sync it immediately, click `Manual Sync`.

A lookup source is a direct link (URL) to a lookup, or an [ARL](../../../8-reference/authentication-resource-locator.md).

Example JSON lookup: [LOLDrivers API](https://loldrivers.io/api/drivers.json)

## Usage

### Option 1: Preconfigured Lookups

LimaCharlie supplies a curated list of public JSON lookups for your organization. The lookup manager GUI shows these lookups.

For the contents of each public lookup, see [lc-public-lookups](https://github.com/refractionpoint/lc-public-lookups).

![image (1).png "Screenshot 2024 10 22 at 13.23.35(2).png"](../../../assets/images/image-(1).png "Screenshot 2024-10-22 at 13.23.35(2).png")

![image (2).png "Screenshot 2024 10 22 at 13.23.45(1).png"](../../../assets/images/image-(2).png "Screenshot 2024-10-22 at 13.23.45(1).png")

### Option 2: Publicly available Lookups

Give the lookup configuration a name and the URL *or* [ARL](../../../8-reference/authentication-resource-locator.md). Then click the Save button. LimaCharlie creates the new lookup source and syncs it to your lookups.

`[github,my-org/my-repo-name/path/to/lookup]`

### Option 3: Private Lookup Repository

To use a lookup from a private GitHub repository, you need an [Authentication Resource Locator](../../../8-reference/authentication-resource-locator.md).

**Step 1: Create a token in GitHub.** Do these steps:

1. In GitHub, go to *Settings*.
2. Click *Developer settings* in the left side bar.
3. Click *Personal access token*.
4. Click *Generate new token*.
5. Select the repo permissions.
6. Click *Generate token*.

**Step 2: Connect LimaCharlie to your GitHub Repository.** Do these steps:

1. In LimaCharlie, click *Lookup Manager* in the left menu.
2. Click *Add New Lookup Configuration*.
3. Give your lookup a name.
4. Use the token that you generated in the format below, with the link to your repository.

`[github,my-org/my-repo-name/path/to/lookup,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

## Infrastructure as Code

Example:

```yaml
hives:
    extension_config:
        ext-lookup-manager:
            data:
                lookup_manager_rules:
                    - arl: ""
                      format: json
                      name: alienvault
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/alienvault-ip-reputation.json]'
                      tags:
                        - alienvault
                    - arl: ""
                      format: json
                      name: tor
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
                      tags:
                        - tor
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```
