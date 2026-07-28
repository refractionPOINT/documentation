# Installation Keys

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to associate them with the correct Organization. You create installation keys for each organization. The keys let you label and control your deployment population.

There are four components of an Installation Key:

- **Organization ID (OID)**: The Organization ID that this key enrolls into.
- **Installer ID (IID)**: The Installer ID that the cloud generates and associates with each Installation Key.
- **Tags**: A list of Tags that the cloud applies automatically to sensors that enroll with the key.
- **Description**: The description that helps you identify the use of each key.

## Management

You manage installation keys on the **Sensors > Installation Keys** page in the web app.

On this page, the `Connectivity` section shows the URLs for Sensor and Adapter connectivity.

### Pinned Certificates

Typically, Sensors need access over port 443 and use pinned SSL certificates. This is the default deployment option. It does not support traffic interception.

If you must install sensors without pinned certificates, create an installation key with a specific flag. Use the REST API and set the `use_public_root_ca` flag to `true`.

See the [Python SDK Manager.replicantRequest source](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1386) for more detail.

## Use of Tags

Use at least one Installation Key for each organization. Then use different keys to identify the parts of your infrastructure. For example, create a key with the Tag "server" for your servers, a key with "vip" for the executives in your organization, or a key with "sales" for the sales department. You can then use the tags on the sensors to apply different detection and response rules to different types of hosts.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives you full control of security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises with many departments or clients.

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to associate them with the correct Organization. You create installation keys for each organization. The keys let you label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier for each tenant or customer account. It separates the different organizations in LimaCharlie, so LimaCharlie can manage resources, permissions, and data segregation securely. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. This gives multi-tenant support and a clear separation between customer environments.

In LimaCharlie, an Organization ID (OID) is a unique identifier for each tenant or customer account. It separates the different organizations in LimaCharlie, so LimaCharlie can manage resources, permissions, and data segregation securely. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. This gives multi-tenant support and a clear separation between customer environments.

Like agents, Sensors send telemetry to the LimaCharlie cloud as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

Adapters ingest data from on-premise environments and from cloud environments.

## Programmatic Management

!!! info "Prerequisites"
    All programmatic examples need an API key with the `ikey.list`, `ikey.set`, and `ikey.del` permissions. For setup instructions, see [API Keys](../7-administration/access/api-keys.md).

### List Installation Keys

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/installationkeys/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.installation_keys import InstallationKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    keys = InstallationKeys(org).list()
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    keys, err := org.InstallationKeys()
    ```

=== "CLI"

    ```bash
    limacharlie installation-key list
    ```

### Create an Installation Key

=== "REST API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/installationkeys/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "desc=Production+servers&tags=server,prod"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.installation_keys import InstallationKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    key = InstallationKeys(org).create("Production servers", tags=["server", "prod"])
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    iid, err := org.AddInstallationKey(limacharlie.InstallationKey{
        Description: "Production servers",
        Tags:        []string{"server", "prod"},
    })
    ```

=== "CLI"

    ```bash
    limacharlie installation-key create --description "Production servers" --tags "server,prod"
    ```

### Delete an Installation Key

=== "REST API"

    ```bash
    curl -s -X DELETE "https://api.limacharlie.io/v1/installationkeys/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "iid=IID_TO_DELETE"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.installation_keys import InstallationKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    InstallationKeys(org).delete("IID_TO_DELETE")
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    err := org.DelInstallationKey("IID_TO_DELETE")
    ```

=== "CLI"

    ```bash
    limacharlie installation-key delete --iid IID_TO_DELETE --confirm
    ```

---

## See Also

- [Sensor Deployment Overview](index.md)
- [Windows Installation](endpoint-agent/windows/installation.md)
- [Linux Installation](endpoint-agent/linux/installation.md)
- [Python SDK](../6-developer-guide/sdks/python-sdk.md)
- [Go SDK](../6-developer-guide/sdks/go-sdk.md)
