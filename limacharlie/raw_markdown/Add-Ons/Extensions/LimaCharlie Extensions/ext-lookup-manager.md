# Lookup Manager

The Lookup Manager Extension allows you to create, maintain & automatically refresh lookups in the Organization to then reference them in Detection & Response Rules.

The saved Lookup Configurations can be managed across tenants using Infrastructure as Code extension. To manage lookup versions across all of your tenants, update the file under the original Authenticated Resource Locator.

Every 24 hours, LimaCharlie will sync all of the lookups in the configuration. Lookups can also be manually synced by clicking the `Manual Sync` button on the extension page. When a lookup configuration is added, it will **not** be automatically synced immediately, unless you click on `Manual Sync`.

Lookup sources can be either direct links (URLs) to a given lookup or [ARLs](/v2/docs/reference-authentication-resource-locator).

Example JSON lookup: [link](https://loldrivers.io/api/drivers.json)

## Usage

### Option 1: Preconfigured Lookups![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(279\).png)

LimaCharlie provides a curated list of several publicly available JSON lookups for use within your organization. These are provided in the lookup manager GUI.

More details and the contents of each of these lookups can be found [here](https://github.com/refractionpoint/lc-public-lookups).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image \(1\).png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image \(2\).png)

### Option 2: Publicly available Lookups

Giving the lookup configuration a name, the URL _or_ [ARL](/v2/docs/reference-authentication-resource-locator), and clicking the Save button will create the new lookup source to sync to your lookups.

`[github,my-org/my-repo-name/path/to/lookup]`

### Option 3: Private Lookup Repository

To use a lookup from a private Github repository you will need to make use of an [Authentication Resource Locator](/v2/docs/reference-authentication-resource-locator).

**Step 1: Create a token in GitHub**  
In GitHub go to _Settings_ and click _Developer settings_ in the left hand side bar.

Next click _Personal access token_ followed by _Generate new token_. Select repo permissions and finally _Generate token_.

**Step 2: Connect LimaCharlie to your GitHub Repository**  
Inside of LimaCharlie, click on _Lookup Manager_ in the left hand menu. Then click _Add New Lookup Configuration_.

Give your lookup a name and then use the token you generated with the following format linked to your repository.

`[github,my-org/my-repo-name/path/to/lookup,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

## Infrastructure as Code

Example:
    
    
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
    

