# Config Hive: Apps

The `app` hive stores user-authored, AI-generated mini web applications. Each record holds a single, self-contained HTML document (HTML plus inline JavaScript and CSS) that the LimaCharlie web UI renders inside a sandboxed `<iframe>`. The result is a small custom "app" that users can build conversationally through AI and surface throughout the LimaCharlie console.

Because each app is a single self-contained document, there are no external asset fetches to authorize and no build step: the whole app is content-addressed by the record's etag. The `schema_version` field exists so the format can evolve to a multi-asset layout later without breaking existing records.

## Security Model

An app frequently needs to call LimaCharlie APIs on behalf of the user viewing it. To make that possible, the host mints a **user JWT scoped down to a subset of permissions** and hands it to the iframe. The granted set is always the intersection of what the app declares and what the viewer actually holds:

```text
granted_to_iframe = required_permissions ∩ viewing_user_permissions
```

A viewer can therefore never gain authority they don't already have. To also close the classic "confused deputy" hole — where a low-privilege author crafts an app requesting powerful permissions that only become active when an admin opens it — the following invariants are enforced at **write time**:

1. **Every declared permission must be a real, JWT-issuable permission.** Typos and invented strings are rejected.
2. **No permission may be a root/backend-only permission.** Those are never minted into a user JWT.
3. **The author must already hold every permission they declare.** You cannot author an app that requests authority you do not yourself possess. (Trusted root/backend writes are exempt, so the platform can provision apps on a user's behalf.)

As defense in depth, the iframe's network egress is also allowlisted via the iframe's Content-Security-Policy `connect-src`, across two dimensions:

- `allowed_origins` — arbitrary third-party `https` origins the app opts into. `https` is mandatory so the scoped JWT can never be exfiltrated over cleartext.
- `required_services` — first-party LimaCharlie services beyond the always-available `api.limacharlie.io`. Authors name services from a curated allowlist rather than hardcoding internal hostnames (which differ per deployment); the host resolves each to the org's concrete, region-specific origin. The same scoped JWT is used against them, and each service independently enforces the declared permissions — so `required_services` brokers only *where* the token may go, never *what* it may do.

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
| `schema_version` | No | App content format version. `0`/omitted is treated as v1. A version newer than the platform supports is rejected. Current max: `1`. |
| `display_name` | Yes | Human label shown in the launcher and embeds (max 256 chars). The record *name* is the stable slug/id; this is the pretty name. |
| `description` | No | Optional blurb describing the app (max 4096 chars). |
| `icon` | No | Optional emoji, icon id, or small data-URI for the launcher (max 256 chars). |
| `html` | Yes | The single self-contained document rendered in the iframe. |
| `required_permissions` | No | LimaCharlie permissions the app's JS needs. The iframe JWT is scoped to the intersection of this set and the viewer's own permissions. Each entry must be a real, non-root, JWT-issuable permission that the author already holds. May be empty for a purely static app (the safest kind). Max 64. |
| `allowed_origins` | No | Allowlist of external `https` origins the app's JS may contact. Each must be scheme + host only (no path, query, fragment, or credentials). Empty means "LimaCharlie only". Max 32. |
| `required_services` | No | First-party LimaCharlie services the app needs to reach beyond `api.limacharlie.io`. Valid values: `search`, `replay`, `cases`, `ai`. Max 16. |
| `locations` | No | Where the app may be surfaced in the UI: `standalone`, `within_a_sensor`, `within_a_detection`, `within_a_case`, `within_a_dr_rule`. Max 8. |
| `expected_context` | No | Context keys the app expects when embedded (e.g. `sid`, `atom`, `detection_id`), so the host passes the right identifiers from the surrounding object into the iframe. Max 32. |

Records use a strict unmarshal: unknown fields are rejected. The maximum record size is 10 MB; larger documents are rejected.

## Permissions

Managing records in the `app` hive requires the `app.*` permission set:

- `app.get`
- `app.set`
- `app.del`
- `app.get.mtd`
- `app.set.mtd`

!!! note
    These permissions gate who can **manage app records**. They are entirely separate from an app's own `required_permissions`, which are minted into the per-viewer iframe JWT. Do not conflate the two.

## Programmatic Management

!!! info "Prerequisites"
    All API and SDK examples require an API key with the appropriate permissions. See [API Keys](../access/api-keys.md) for setup instructions.

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
    New hive records are created **disabled by default**. Each example below explicitly enables the app — drop the `enabled` portion if you want the app to start disabled and enable it later via `limacharlie hive enable --hive-name app --key …`.

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

    The `--enabled` flag creates-and-enables the record in one shot. Omit it (and `usr_mtd.enabled` in the file) to leave the app disabled until you call `limacharlie hive enable --hive-name app --key my-app`.

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

- [Apps](../../apps/index.md) -- The end-user guide to building and using apps in the console: the AI authoring flow, the `window.lc` runtime, and recipes for charts and tables.
- [Permissions Reference](../../8-reference/permissions.md) -- The `app.*` permissions that gate app record management.
- [AI Sessions](../../9-ai-sessions/index.md) -- AI-driven workflows that author and consume LimaCharlie configuration.
