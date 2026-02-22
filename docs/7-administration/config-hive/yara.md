# Config Hive: Yara

## Format

A yara record in `hive` has a very basic format:

```json
{
    "rule": "data"
}
```

The `data` portion of the records in this hive must have a single key called `rule` who's value will be the yara rule content used by various LimaCharlie components.

A single rule record can contain a series of actual Yara rule, like this: https://github.com/Yara-Rules/rules/blob/master/malware/APT_APT1.yar

## Permissions

The `yara` hive requires the following permissions for the various operations:

* `yara.get`
* `yara.set`
* `yara.del`
* `yara.get.mtd`
* `yara.set.mtd`

## Usage

Yara rules can be create in the `yara` Hive. Those rules will then be available, either through the `ext-yara` Extension, or directly using the `yara_scan` command directly using the reference `hive://yara/your-rule-name`.

## Programmatic Management

!!! info "Prerequisites"
    All API and SDK examples require an API key with the appropriate permissions. See [API Keys](../access/api-keys.md) for setup instructions.

YARA sources stored in the `yara` hive can be managed via the Hive API or through the dedicated YARA source CLI commands. The Go SDK also provides dedicated YARA methods on the Organization object.

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

The data payload uses a `rule` key containing the YARA rule content.

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
    record = HiveRecord("my-rule", data={"rule": yara_content})
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

Let's create a new Yara rule using the LimaCharlie CLI in a terminal.
Assuming you have a Yara rule in the `rule.yara` file.

Load the rule in the LimaCharlie Hive via the CLI:

```
$ limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

You should get a confirmation that the rule was created, including metadata of the rule associated OID:

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

Next, assuming you want to issue a scan command directly to a Sensor (via the Console or a rule):

```
yara_scan hive://yara/my-rule
```
