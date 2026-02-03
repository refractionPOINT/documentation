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

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
