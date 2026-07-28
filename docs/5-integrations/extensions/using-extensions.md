# Using Extensions

## Components

You interact with Extensions through two main components:

### Configurations

Extension Configurations are records in [Hive](../../7-administration/config-hive/index.md). Each Extension keeps its configuration in the Hive record of the same name in the `extension_configuration` Hive.

To change a configuration, store the new value in the record. LimaCharlie validates the value and sends it to the Extension.

Configurations store settings that change rarely. The developer of the Extension does not need to manage secure storage for these settings.

Each Extension publishes the structure of its configuration in its "schema".

Schemas are available through the [Schema API](https://api.limacharlie.io/static/swagger/#/Extension-Schema/getExtensionSchema) or the LimaCharlie CLI: `limacharlie extension schema --help`.

### Requests

A request is a direct, individual call to an Extension. A request contains an "action" and a "payload" (JSON object) for the Extension. You can flag some requests so that the Extension impersonates the requester (identity and permissions) during execution.

The "action" and the "payload" depend on the Extension that receives them. Each Extension documents its actions and payload structures in the "schema" that it publishes.

Schemas are available through the [Schema API](https://api.limacharlie.io/static/swagger/#/Extension-Schema/getExtensionSchema) or the LimaCharlie CLI: `limacharlie extension schema --help`.

## Interacting

### Interactively

The LimaCharlie web app shows a machine-generated user interface for each Extension. It builds this interface from the schema that the Extension publishes.

### Automation

[Detection & Response Rules](../../3-detection-response/index.md) are the main automation mechanism in LimaCharlie. These rules interact with Extensions through the `extension request` action in the Response component.

### API

More than one API interacts with Extensions:

- Get the schema for an Extension: [https://api.limacharlie.io/static/swagger/#/Extension-Schema](https://api.limacharlie.io/static/swagger/#/Extension-Request)
- Make requests to an Extension: <https://api.limacharlie.io/static/swagger/#/Extension-Request>

LimaCharlie Extensions expand and customize a security environment. They integrate third-party tools, automate workflows, and add new capabilities. An organization subscribes to an Extension and grants it specific permissions on the infrastructure of the organization. An Extension can be private or public. A private Extension gives tailored use, and a public Extension gives broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

## Programmatic Management

!!! info "Prerequisites"
    All API examples need an API key with the `extension` permission. See [API Keys](../../7-administration/access/api-keys.md) for setup.

### List Subscribed Extensions

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/orgs/YOUR_OID/subscriptions" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    subscribed = Extensions(org).list_subscribed()
    print(subscribed)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        extensions, _ := org.Extensions()
        fmt.Println(extensions)
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension list
    ```

### List Available Extensions

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/extension/definition" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    available = Extensions(org).get_all()
    print(available)
    ```

=== "Go"

    The Go SDK has no dedicated method to list all available extensions. Use the REST API directly.

=== "CLI"

    ```bash
    limacharlie extension list-available
    ```

### Subscribe to an Extension

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/orgs/YOUR_OID/subscription/extension/ext-reliable-tasking" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Extensions(org).subscribe("ext-reliable-tasking")
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        _ = org.SubscribeToExtension("ext-reliable-tasking")
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension subscribe --name ext-reliable-tasking
    ```

### Unsubscribe from an Extension

=== "REST API"

    ```bash
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/orgs/YOUR_OID/subscription/extension/ext-reliable-tasking" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Extensions(org).unsubscribe("ext-reliable-tasking")
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        _ = org.UnsubscribeFromExtension("ext-reliable-tasking")
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension unsubscribe --name ext-reliable-tasking
    ```

### Call an Extension (Request)

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking" \
      -H "Authorization: Bearer $LC_JWT" \
      -d oid="YOUR_OID" \
      -d action="list_jobs" \
      -d data='{}'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    result = Extensions(org).request(
        extension_name="ext-reliable-tasking",
        action="list_jobs",
        data={},
    )
    print(result)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        var resp limacharlie.Dict
        _ = org.ExtensionRequest(
            &resp,
            "ext-reliable-tasking",
            "list_jobs",
            limacharlie.Dict{},
            false,
        )
        fmt.Println(resp)
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension request \
      --name ext-reliable-tasking \
      --action list_jobs \
      --data '{}'
    ```

### Get Extension Schema

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/extension/schema/ext-reliable-tasking?oid=YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.extensions import Extensions

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    schema = Extensions(org).get_schema("ext-reliable-tasking")
    print(schema)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        schema, _ := org.GetExtensionSchema("ext-reliable-tasking")
        fmt.Println(schema)
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension schema --name ext-reliable-tasking
    ```

### Extension Configuration CRUD

Extension configurations are stored in the `extension_config` [Hive](../../7-administration/config-hive/index.md). Use the CLI or Hive API to manage them.

#### List Configs

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/extension_config/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    configs = Hive(org, "extension_config").list()
    print(configs)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        configs, _ := hive.List(limacharlie.HiveArgs{
            HiveName:     "extension_config",
            PartitionKey: "YOUR_OID",
        })
        fmt.Println(configs)
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension config-list
    ```

#### Get Config

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/extension_config/YOUR_OID/ext-reliable-tasking/data" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    config = Hive(org, "extension_config").get("ext-reliable-tasking")
    print(config)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        config, _ := hive.Get(limacharlie.HiveArgs{
            HiveName:     "extension_config",
            PartitionKey: "YOUR_OID",
            Key:          "ext-reliable-tasking",
        })
        fmt.Println(config)
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension config-get --name ext-reliable-tasking
    ```

#### Set Config

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/hive/extension_config/YOUR_OID/ext-reliable-tasking/data" \
      -H "Authorization: Bearer $LC_JWT" \
      -d data='{"setting_a": "value1"}' \
      -d usr_mtd='{"enabled": true}'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive, HiveRecord

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Hive(org, "extension_config").set(HiveRecord(
        name="ext-reliable-tasking",
        data={"setting_a": "value1"},
        enabled=True,
    ))
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        enabled := true
        hive.Add(limacharlie.HiveArgs{
            HiveName:     "extension_config",
            PartitionKey: "YOUR_OID",
            Key:          "ext-reliable-tasking",
            Data:         limacharlie.Dict{"setting_a": "value1"},
            Enabled:      &enabled,
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension config-set \
      --name ext-reliable-tasking \
      --input-file config.yaml
    ```

#### Delete Config

=== "REST API"

    ```bash
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/hive/extension_config/YOUR_OID/ext-reliable-tasking" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Hive(org, "extension_config").delete("ext-reliable-tasking")
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        hive.Remove(limacharlie.HiveArgs{
            HiveName:     "extension_config",
            PartitionKey: "YOUR_OID",
            Key:          "ext-reliable-tasking",
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie extension config-delete --name ext-reliable-tasking
    ```
