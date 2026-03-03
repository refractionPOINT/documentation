# Config Hive: Detection & Response Rules

## Format

## Permissions

There are three "sub-categories" within detection and response rules contained in Hive.

* `dr-general` pertains to rules that your Organization has created and/or controls.
* `dr-managed` pertains to rules that you can use for detection, however are managed or curated by another party (i.e. Soteria rules).
* `dr-service` is a protected namespace, and users will only ever have metadata permissions.

### dr-general

* `dr.list`
* `dr.set`
* `dr.del`

### dr-managed

* `dr.list.managed`
* `dr.set.managed`
* `dr.del.managed`

### dr-service

* `dr.list` or `dr.list.managed` (metadata only)
* `dr.set` or `dr.set.managed` (metadata only)

## Command-Line Usage

```yaml
usage: limacharlie hive [-h] [-k KEY] [-d DATA] [-pk PARTITIONKEY] [--etag ETAG] [--expiry EXPIRY] [--enabled ENABLED] [--tags TAGS] action hive_name

positional arguments:
  action                the action to take, one of: list, list_mtd, get, get_mtd, set, update, remove
  hive_name             the hive name

options:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     the name of the key.
  -d DATA, --data DATA  file containing the JSON data for the record, or "-" for stdin.
  -pk PARTITIONKEY, --partition-key PARTITIONKEY
                        the partition key to use instead of the default OID.
  --etag ETAG           the optional previous etag expected for transactions.
  --expiry EXPIRY       a millisecond epoch timestamp when the record should expire.
  --enabled ENABLED     whether the record is enabled or disabled.
  --tags TAGS           comma separated list of tags.
```

## Usage

## Example

```json
{
  "detect": {
    "event": "WEL",
    "op": "and",
    "rules": [
      {
        "op": "is",
        "path": "event/EVENT/System/Channel",
        "value": "Microsoft-Windows-Windows Defender/Operational"
      },
      {
        "op": "is",
        "path": "event/EVENT/System/EventID",
        "value": "1006"
      }
    ]
  },
  "respond": [
    {
      "action": "report",
      "name": "windows-defender-malware-detected"
    }
  ]
}
```

## Programmatic Management

!!! info "Prerequisites"
    You need a valid API key with `dr.list` and `dr.set` permissions.
    See [API Keys](../access/api-keys.md) for setup instructions.

The D&R rules hive is named `dr-general`. Managed rules use `dr-managed`.

### List Rules

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/hive/dr-general/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    hive = Hive(org, "dr-general")
    rules = hive.list()
    for name, record in rules.items():
        print(name, record.enabled)
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)
    hc := limacharlie.NewHiveClient(org)
    records, _ := hc.List(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
    })
    for name, record := range records {
        fmt.Println(name, record.UsrMtd.Enabled)
    }
    ```

=== "CLI"

    ```bash
    limacharlie hive list dr-general
    # Or use the D&R shortcut:
    limacharlie dr list
    ```

### Get a Rule

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/hive/dr-general/YOUR_OID/RULE_NAME/data" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    hive = Hive(org, "dr-general")
    rule = hive.get("my-detection-rule")
    print(rule.data)
    ```

=== "Go"

    ```go
    hc := limacharlie.NewHiveClient(org)
    record, _ := hc.Get(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "my-detection-rule",
    })
    fmt.Println(record.Data)
    ```

=== "CLI"

    ```bash
    limacharlie hive get dr-general --key my-detection-rule
    # Or use the D&R shortcut:
    limacharlie dr get --key my-detection-rule
    ```

### Set a Rule

=== "REST API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/hive/dr-general/YOUR_OID/my-rule/data" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d 'data={"detect":{"event":"NEW_PROCESS","op":"ends with","path":"event/FILE_PATH","value":".bat"},"respond":[{"action":"report","name":"bat-file-execution"}]}' \
      -d 'usr_mtd={"enabled":true}'
    ```

=== "Python"

    ```python
    from limacharlie.sdk.hive import Hive, HiveRecord

    hive = Hive(org, "dr-general")
    hive.set(HiveRecord(
        name="my-rule",
        data={
            "detect": {
                "event": "NEW_PROCESS",
                "op": "ends with",
                "path": "event/FILE_PATH",
                "value": ".bat",
            },
            "respond": [
                {"action": "report", "name": "bat-file-execution"}
            ],
        },
        enabled=True,
    ))
    ```

=== "Go"

    ```go
    enabled := true
    hc := limacharlie.NewHiveClient(org)
    hc.Add(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "my-rule",
        Data: limacharlie.Dict{
            "detect": limacharlie.Dict{
                "event": "NEW_PROCESS",
                "op":    "ends with",
                "path":  "event/FILE_PATH",
                "value": ".bat",
            },
            "respond": limacharlie.List{
                limacharlie.Dict{"action": "report", "name": "bat-file-execution"},
            },
        },
        Enabled: &enabled,
    })
    ```

=== "CLI"

    ```bash
    limacharlie hive set dr-general --key my-rule --data rule.json
    # Or use the D&R shortcut:
    limacharlie dr set --key my-rule --input-file rule.yaml
    ```

### Delete a Rule

=== "REST API"

    ```bash
    curl -s -X DELETE "https://api.limacharlie.io/v1/hive/dr-general/YOUR_OID/my-rule" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    hive = Hive(org, "dr-general")
    hive.delete("my-rule")
    ```

=== "Go"

    ```go
    hc := limacharlie.NewHiveClient(org)
    hc.Remove(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "my-rule",
    })
    ```

=== "CLI"

    ```bash
    limacharlie hive remove dr-general --key my-rule
    # Or use the D&R shortcut:
    limacharlie dr delete --key my-rule --confirm
    ```

---

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
