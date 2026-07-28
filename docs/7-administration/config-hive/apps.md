# Config Hive: Apps

The `app` hive stores mini web applications that users write with AI. Each record holds one self-contained HTML document, which contains HTML with inline JavaScript and CSS. The LimaCharlie web app renders this document in a sandboxed `<iframe>`. The result is a small custom "app". Users build an app in a conversation with AI, then show the app in many places in the web app.

Each app is one self-contained document. There are therefore no external asset fetches to authorize and no build step. The etag of the record content-addresses the whole app. The `schema_version` field lets the format change to a multi-asset layout later, and existing records continue to work.

## Security Model

An app often calls LimaCharlie APIs for the user that views it. To make this possible, the host mints a **user JWT that is scoped down to a subset of permissions** and gives it to the iframe. The granted set is always the intersection of the permissions that the app declares and the permissions that the viewer holds:

```text
granted_to_iframe = required_permissions ∩ viewing_user_permissions
```

A viewer therefore never gets authority that the viewer does not already have. A second problem is the "confused deputy" attack. In this attack, an author with low privilege writes an app that declares strong permissions. Those permissions become active only when an administrator opens the app. To close this hole, the cloud enforces these invariants at **write time**:

1. **Every declared permission must be a real, JWT-issuable permission.** The cloud rejects typos and invented strings.
2. **A permission must not be a root or backend-only permission.** The cloud never mints those into a user JWT.
3. **The author must already hold every permission that the author declares.** You cannot write an app that requests authority that you do not have. Trusted root and backend writes are exempt, so the platform can provision apps for a user.

As defense in depth, the Content-Security-Policy `connect-src` of the iframe also allowlists the network egress of the iframe. The allowlist has two dimensions:

- `allowed_origins` — third-party `https` origins that the app opts into. `https` is mandatory, so no one can exfiltrate the scoped JWT over cleartext.
- `required_services` — first-party LimaCharlie services other than `api.limacharlie.io`, which is always available. Authors name services from a curated allowlist. They do not hardcode internal hostnames, which are different for each deployment. The host resolves each service to the concrete, region-specific origin of the organization. The app uses the same scoped JWT against these services, and each service enforces the declared permissions on its own. `required_services` therefore controls only *where* the token can go, and never *what* the token can do.

## Format

```json
{
    "schema_version": 1,
    "display_name": "My App",
    "description": "A short blurb describing what the app does.",
    "icon": "🚀",
    "html": "<!doctype html><html>…</html>",
    "required_permissions": ["sensor.get", "sensor.task"],
    "allowed_origins": ["https://example.com"],
    "required_services": ["search", "cases"],
    "locations": ["standalone", "within_a_sensor"],
    "expected_context": ["sid", "atom"]
}
```

| Field | Required | Description |
| --- | --- | --- |
| `schema_version` | No | Version of the app content format. `0` or an omitted value is v1. The cloud rejects a version that is newer than the platform supports. Current max: `1`. |
| `display_name` | Yes | Label shown in the launcher and in embeds (max 256 chars). The record *name* is the stable slug or id; this field is the readable name. |
| `description` | No | Optional text that describes the app (max 4096 chars). |
| `icon` | No | Optional emoji, icon id, or small data-URI for the launcher (max 256 chars). |
| `html` | Yes | The one self-contained document that the iframe renders. |
| `required_permissions` | No | LimaCharlie permissions that the JavaScript of the app needs. The iframe JWT is scoped to the intersection of this set and the permissions of the viewer. Each entry must be a real, non-root, JWT-issuable permission that the author already holds. Can be empty for a static app, which is the safest kind. Max 64. |
| `allowed_origins` | No | Allowlist of external `https` origins that the JavaScript of the app can contact. Each entry must have only a scheme and a host: no path, query, fragment, or credentials. An empty list means "LimaCharlie only". Max 32. |
| `required_services` | No | First-party LimaCharlie services that the app must reach other than `api.limacharlie.io`. Valid values: `search`, `replay`, `cases`, `ai`. Max 16. |
| `locations` | No | Places in the web app that can show the app: `standalone`, `within_a_sensor`, `within_a_detection`, `within_a_case`, `within_a_dr_rule`. Max 8. |
| `expected_context` | No | Context keys that the app expects when it is embedded, for example `sid`, `atom`, or `detection_id`. The host then passes the correct identifiers from the surrounding object into the iframe. Max 32. |

Records use a strict unmarshal, and the cloud rejects unknown fields. The maximum record size is 10 MB. The cloud rejects larger documents.

## Permissions

To manage records in the `app` hive, you need the `app.*` permission set:

- `app.get`
- `app.set`
- `app.del`
- `app.get.mtd`
- `app.set.mtd`

!!! note
    These permissions control who can **manage app records**. They are separate from the `required_permissions` of an app, which the cloud mints into the iframe JWT for each viewer. Do not confuse the two.

## Programmatic Management

!!! info "Prerequisites"
    All API and SDK examples need an API key with the correct permissions. See [API Keys](../access/api-keys.md) for setup instructions.

### List Apps

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/app/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "app")
    records = hive.list()
    for name, record in records.items():
        print(name, record.data)
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
        }, nil)
        org, _ := limacharlie.NewOrganization(client)
        hc := limacharlie.NewHiveClient(org)

        records, _ := hc.List(limacharlie.HiveArgs{
            HiveName:     "app",
            PartitionKey: "YOUR_OID",
        })
        for name, record := range records {
            fmt.Println(name, record.Data)
        }
    }
    ```

=== "CLI"

    ```bash
    limacharlie hive list --hive-name app
    ```

### Get an App

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/app/YOUR_OID/my-app/data" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "app")
    record = hive.get("my-app")
    print(record.data)
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
        }, nil)
        org, _ := limacharlie.NewOrganization(client)
        hc := limacharlie.NewHiveClient(org)

        record, _ := hc.Get(limacharlie.HiveArgs{
            HiveName:     "app",
            PartitionKey: "YOUR_OID",
            Key:          "my-app",
        })
        fmt.Println(record.Data)
    }
    ```

=== "CLI"

    ```bash
    limacharlie hive get --hive-name app --key my-app
    ```

### Create / Update an App

!!! warning
    The cloud creates new hive records **disabled by default**. Each example below enables the app. To make the app start disabled, remove the `enabled` part. You can then enable the app later with `limacharlie hive enable --hive-name app --key …`.

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/hive/app/YOUR_OID/my-app/data" \
      -H "Authorization: Bearer $LC_JWT" \
      -d 'data={"display_name":"My App","html":"<!doctype html><html><body>Hello</body></html>","required_permissions":[]}' \
      -d 'usr_mtd={"enabled":true}'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive, HiveRecord

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "app")
    record = HiveRecord(
        "my-app",
        data={
            "display_name": "My App",
            "html": "<!doctype html><html><body>Hello</body></html>",
            "required_permissions": [],
        },
        enabled=True,
    )
    hive.set(record)
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
        }, nil)
        org, _ := limacharlie.NewOrganization(client)
        hc := limacharlie.NewHiveClient(org)

        enabled := true
        hc.Add(limacharlie.HiveArgs{
            HiveName:     "app",
            PartitionKey: "YOUR_OID",
            Key:          "my-app",
            Data: limacharlie.Dict{
                "display_name":         "My App",
                "html":                 "<!doctype html><html><body>Hello</body></html>",
                "required_permissions": []string{},
            },
            Enabled: &enabled,
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie hive set --hive-name app --key my-app \
      --input-file app.json --enabled
    ```

    Where `app.json` contains:

    ```json
    {
        "data": {
            "display_name": "My App",
            "html": "<!doctype html><html><body>Hello</body></html>",
            "required_permissions": []
        }
    }
    ```

    The `--enabled` flag creates and enables the record in one operation. Omit the flag, and omit `usr_mtd.enabled` in the file, to keep the app disabled. The app stays disabled until you call `limacharlie hive enable --hive-name app --key my-app`.

### Delete an App

=== "REST API"

    ```bash
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/hive/app/YOUR_OID/my-app" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "app")
    hive.delete("my-app")
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
        }, nil)
        org, _ := limacharlie.NewOrganization(client)
        hc := limacharlie.NewHiveClient(org)

        hc.Remove(limacharlie.HiveArgs{
            HiveName:     "app",
            PartitionKey: "YOUR_OID",
            Key:          "my-app",
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie hive delete --hive-name app --key my-app --confirm
    ```

### Enable / Disable an App

=== "CLI"

    ```bash
    # Disable an app:
    limacharlie hive disable --hive-name app --key my-app
    # Re-enable:
    limacharlie hive enable --hive-name app --key my-app
    ```

## See Also

- [Apps](../../apps/index.md) -- The guide for end users that explains how to build and use apps in the web app: the AI authoring flow, the `window.lc` runtime, and recipes for charts and tables.
- [Permissions Reference](../../8-reference/permissions.md) -- The `app.*` permissions that control the management of app records.
- [AI Sessions](../../9-ai-sessions/index.md) -- AI workflows that write and read LimaCharlie configuration.
