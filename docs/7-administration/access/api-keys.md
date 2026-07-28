# API Keys

The cloud uses API keys. An API key is a named secret key. You use an API key to get a JWT for the LC REST API at <https://api.limacharlie.io>.

A headless application can use this method to get REST authentication tokens that expire.

To get the list of available permissions programmatically, use this URL: <https://app.limacharlie.io/owner_permissions>

## Managing

You manage the API keys in the Organization view of the web app at <https://limacharlie.io>.

## Getting a JWT

Send an HTTP POST to `https://jwt.limacharlie.io` with the Organization ID and the API key. The JWT is valid for one hour.

=== "REST API"

    ```bash
    curl -X POST "https://jwt.limacharlie.io" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "oid=YOUR_OID&secret=YOUR_API_KEY"
    ```

    Response: `{ "jwt": "<JWT_VALUE_HERE>" }`

=== "Python"

    ```python
    from limacharlie.client import Client

    # JWT is acquired and refreshed automatically
    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    // JWT is acquired and refreshed automatically
    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    ```

=== "CLI"

    ```bash
    # Credentials are stored in ~/.limacharlie after login
    limacharlie auth login
    ```

### User API Keys

User API keys generate JSON web tokens (JWTs) for the REST API. Unlike Organization API keys, a User API key belongs to one specific user. It gives the same access in all organizations.

This access makes User API Keys harder to manage safely. Use Organization API keys when possible.

User API keys work with the same interfaces as Organization API keys. Only the method to get the JWT is different. Give `https://jwt.limacharlie.io/` a `uid` parameter instead of an `oid` parameter. The LimaCharlie web app shows the `uid` value.

`curl -X POST "https://jwt.limacharlie.io" -H "Content-Type: application/x-www-form-urlencoded" -d "uid=<YOUR_USER_ID>&secret=<YOUR_API_KEY>"`

Sometimes the JWT from a User API key is too large for normal API use. The API gateway then returns `HTTP 413 Payload too large`. If this happens, also give an `oid` with the `uid` to the `jwt.limacharlie.io` REST endpoint. The endpoint returns a JWT that is valid only for that organization.

`curl -X POST "https://jwt.limacharlie.io" -H "Content-Type: application/x-www-form-urlencoded" -d "oid=<YOUR_OID>&uid=<YOUR_USER_ID>&secret=<YOUR_API_KEY>"`

You can also use a User API Key to get the list of organizations that it can access. Query this REST endpoint:

`https://app.limacharlie.io/user_key_info?secret=<YOUR_USER_API_KEY>&uid=<YOUR_USER_ID>&with_names=true`

#### Ingestion Keys

[Artifact collection](../../5-integrations/extensions/limacharlie/artifact.md) in LC needs Ingestion Keys. You manage these keys in the REST API section of the LC web app. To manage Ingestion Keys, you need the `ingestkey.ctrl` permission.

## SDKs

The [Python SDK](../../6-developer-guide/sdks/python-sdk.md) and the [Go SDK](../../6-developer-guide/sdks/go-sdk.md) exchange the API Key for a JWT automatically. They also wrap the REST API in objects.

## Privileges

API Keys have on-off privileges.

For the full list, see the "REST API" section of your organization.

A REST call fails with a `401` if your API Key or token does not have all the necessary privileges. The error names the missing privilege.

## Required Privileges

This is a list of the privileges that some common tasks need.

### Go Live

To "go Live" in the web app, the user needs these privileges:

- `output.*`: to create the real-time output to the browser through HTTP.
- `sensor.task`: to send commands to the Sensor. This includes manual commands for the console and the commands that fill the tabs.

## Flair

An API Key name can contain "flair". A flair is a tag inside `[]`. The flair is optional. Put the flair at the end of the API key name to keep the name readable.

For example:
`orchestration-key[bulk]` is a key with a `bulk` flair.

A flair changes the behavior of an API key. It can also give usage hints to systems in LimaCharlie.

LimaCharlie supports these flairs:

- `bulk`: tells the REST API that this key makes many calls. The API gateway changes the API call limits for the key.
- `segment`: makes only the resources that this key created visible to this key. Use this flair to give limited access to a third party.

## Allowed IP Range

When you create an API key, you can add an `allowed_ip_range`. This value is an IP range in [CIDR notation](https://aws.amazon.com/what-is/cidr/). The API key works only from an IP address in that range. Use of the key from a different IP address fails. You can set this value only when you create an API key with the API, not in the web app.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment for security data, configurations, and assets. Each Organization has its own sensors, detection rules, data sources, and outputs. This structure supports multi-tenant setups for managed security providers, and for enterprises with many departments or clients.

In LimaCharlie, an Organization ID is a unique identifier for each tenant or customer account. It separates the organizations in the platform. LimaCharlie uses it to manage resources, permissions, and the separation of data. The Organization ID keeps the telemetry, the configurations, and the operations of each organization isolated from other customer environments.

Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. A sensor is a scalable, serverless method to connect the endpoints of an organization to the cloud.

## Programmatic Management

!!! info "Prerequisites"
    To manage API keys programmatically, you need an API key with the `apikey.ctrl` permission. For the first setup in the web app, see [Managing](#managing).

### List API Keys

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/orgs/YOUR_OID/keys" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.api_keys import ApiKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    keys = ApiKeys(org).list()
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    keys, err := org.GetAPIKeys()
    ```

=== "CLI"

    ```bash
    limacharlie api-key list
    ```

### Create an API Key

=== "REST API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/orgs/YOUR_OID/keys" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "key_name=ci-key&perms=dr.list,dr.set"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.api_keys import ApiKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    key = ApiKeys(org).create("ci-key", ["dr.list", "dr.set"])
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    key, err := org.CreateAPIKey("ci-key", []string{"dr.list", "dr.set"})
    ```

=== "CLI"

    ```bash
    limacharlie api-key create --name ci-key --permissions "dr.list,dr.set"
    ```

    To create the key and store its value in the [secret hive](../config-hive/secrets.md) in one step, add `--store-secret`:

    ```bash
    limacharlie api-key create --name <name> --permissions "..." --store-secret <secret-name> [--store-secret-tag <tag>]
    ```

    This command creates the key and writes its value to `hive://secret/<secret-name>`. The value is shown only one time, when you create the key. Direct storage removes the need to capture the value and pipe it again. If a secret with that name exists, the command updates it in place with its etag. The identity that runs this command needs the `secret.set` permission to write the secret, and also the permission to create API keys.

### Delete an API Key

=== "REST API"

    ```bash
    curl -s -X DELETE "https://api.limacharlie.io/v1/orgs/YOUR_OID/keys" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "key_hash=KEY_HASH_TO_DELETE"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.api_keys import ApiKeys

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    ApiKeys(org).delete("KEY_HASH_TO_DELETE")
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    err := org.DeleteAPIKey("KEY_HASH_TO_DELETE")
    ```

=== "CLI"

    ```bash
    limacharlie api-key delete --key-hash KEY_HASH_TO_DELETE --confirm
    ```

---

## See Also

- [SDKs](../../6-developer-guide/sdks/index.md)
- [Python SDK](../../6-developer-guide/sdks/python-sdk.md)
- [Go SDK](../../6-developer-guide/sdks/go-sdk.md)
