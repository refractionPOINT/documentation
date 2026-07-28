# Config Hive: Yara

## Format

A yara record in `hive` has a basic format:

```json
{
    "rule": "data"
}
```

The `data` part of a record in this hive must have one key called `rule`. The value of this key is the yara rule content that different LimaCharlie components use.

One rule record can contain a series of yara rules, like this: <https://github.com/Yara-Rules/rules/blob/master/malware/APT_APT1.yar>

## Permissions

The `yara` hive needs these permissions for its operations:

- `yara.get`
- `yara.set`
- `yara.del`
- `yara.get.mtd`
- `yara.set.mtd`

## Usage

You can create Yara rules in the `yara` Hive. The `ext-yara` Extension can then use those rules. The `yara_scan` command can also use them directly with the reference `hive://yara/your-rule-name`.

## Programmatic Management

!!! info "Prerequisites"
    All API and SDK examples need an API key with the correct permissions. See [API Keys](../access/api-keys.md) for setup instructions.

You can manage the YARA sources in the `yara` hive with the Hive API, or with the dedicated CLI commands for YARA sources. The Go SDK also has dedicated YARA methods on the Organization object.

### List YARA Sources

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/yara/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "yara")
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

        sources, _ := org.YaraListSources()
        for name, source := range sources {
            fmt.Println(name, source.Content)
        }
    }
    ```

=== "CLI"

    ```bash
    limacharlie yara sources-list
    ```

### Get a YARA Source

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/yara/YOUR_OID/my-rule/data" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "yara")
    record = hive.get("my-rule")
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

        content, _ := org.YaraGetSource("my-rule")
        fmt.Println(content)
    }
    ```

=== "CLI"

    ```bash
    limacharlie yara source-get --name my-rule
    ```

### Create / Update a YARA Source

The data payload uses a `rule` key that contains the YARA rule content.

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/hive/yara/YOUR_OID/my-rule/data" \
      -H "Authorization: Bearer $LC_JWT" \
      -d '{"data": "{\"rule\": \"rule ExampleRule { strings: $s = \\\"suspicious\\\" condition: $s }\"}"}'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive, HiveRecord

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "yara")

    yara_content = """
    rule ExampleRule {
        strings:
            $s = "suspicious"
        condition:
            $s
    }
    """
    # New hive records are disabled by default — pass enabled=True so
    # the rule is picked up by YARA scans.
    record = HiveRecord("my-rule", data={"rule": yara_content}, enabled=True)
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

        yaraContent := `rule ExampleRule {
        strings:
            $s = "suspicious"
        condition:
            $s
    }`
        org.YaraSourceAdd("my-rule", limacharlie.YaraSource{
            Content: yaraContent,
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie yara source-add --name my-rule \
      --source-file rules.yar
    ```

    Where `rules.yar` contains your YARA rule content.

### Delete a YARA Source

=== "REST API"

    ```bash
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/hive/yara/YOUR_OID/my-rule" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "yara")
    hive.delete("my-rule")
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

        org.YaraSourceDelete("my-rule")
    }
    ```

=== "CLI"

    ```bash
    limacharlie yara source-delete --name my-rule
    ```

## Example

This example creates a new Yara rule with the LimaCharlie CLI in a terminal.
The example assumes that you have a Yara rule in the `rule.yara` file.

Load the rule into the LimaCharlie Hive with the CLI:

```bash
limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

The CLI returns a confirmation that it created the rule. The confirmation includes the metadata of the rule and the OID:

```json
{
  "guid": "d88826b7-d583-4bcc-b7d3-4f450a12e1be",
  "hive": {
    "name": "yara",
    "partition": "8cbe27f4-aaaa-bbbb-cccc-138cd51389cd"
  },
  "name": "my-rule"
}
```

Next, to send a scan command directly to a Sensor, from the web app or from a rule, use this command:

```text
yara_scan hive://yara/my-rule
```
