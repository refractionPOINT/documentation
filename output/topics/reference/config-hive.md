# Config Hive Reference

The Config Hive is LimaCharlie's centralized configuration storage system that allows you to manage various security components including cloud sensors, detection rules, lookups, secrets, and Yara rules. Each hive type has specific permissions, formats, and use cases.

## Cloud Sensors

Cloud sensors enable ingestion of data from various sources including webhooks and cloud platforms.

### Format

Cloud sensor configurations define the sensor type and associated connection parameters.

### Permissions

* `cloudsensor.get` - Retrieve cloud sensor configurations
* `cloudsensor.set` - Create or update cloud sensor configurations
* `cloudsensor.del` - Delete cloud sensor configurations
* `cloudsensor.get.mtd` - Get cloud sensor metadata
* `cloudsensor.set.mtd` - Set cloud sensor metadata

### Command-Line Usage

```
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

### Example

```json
{
    "sensor_type": "webhook",
    "webhook": {
        "client_options": {
            "hostname": "test-webhook",
            "identity": {
                "installation_key": "3bc13b74-0d27-4633-9773-62293bf940a7",
                "oid": "aecec56a-046c-4078-bc08-8ebdc84dcad5"
            },
            "platform": "json",
            "sensor_seed_key": "test-webhook"
        },
        "secret": "super-secret-hook"
    }
}
```

---

## Detection & Response Rules

Detection and Response (D&R) rules define threat detection logic and automated response actions within your organization.

### Format

D&R rules consist of a `detect` section specifying detection logic and a `respond` section defining actions to take when detections occur.

### Permissions

There are three sub-categories within detection and response rules:

#### dr-general
Rules that your organization has created and controls:
* `dr.list` - List detection rules
* `dr.set` - Create or update detection rules
* `dr.del` - Delete detection rules

#### dr-managed
Rules managed or curated by another party (e.g., Soteria rules):
* `dr.list.managed` - List managed detection rules
* `dr.set.managed` - Create or update managed detection rules
* `dr.del.managed` - Delete managed detection rules

#### dr-service
Protected namespace with metadata-only access:
* `dr.list` or `dr.list.managed` (metadata only)
* `dr.set` or `dr.set.managed` (metadata only)

### Command-Line Usage

```
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

### Example

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

---

## Lookups

Lookups are key-value stores where the key is a string and the value is a dictionary containing metadata. Lookups can be queried by various parts of LimaCharlie, such as detection rules.

### Format

Lookup data can be ingested using one of the following root keys:

* `lookup_data` - Direct JSON representation with keys and dictionary metadata
* `newline_content` - String with keys separated by newlines (metadata assumed empty)
* `yaml_content` - YAML-formatted string containing a dictionary with string keys and dictionary metadata

### Permissions

* `lookup.get` - Retrieve lookup data
* `lookup.set` - Create or update lookup data
* `lookup.del` - Delete lookup data
* `lookup.get.mtd` - Get lookup metadata
* `lookup.set.mtd` - Set lookup metadata

### Usage

#### Infrastructure as Code

```yaml
hives:
    lookup:                             # Example lookup in the lookup hive
        example-lookup:
            data:
                lookup_data:
                    8.8.8.8: {}
                    8.8.4.4: {}
                    1.1.1.1: {}
                optimized_lookup_data:
                    _LC_INDICATORS: null
                    _LC_METADATA: null
            usr_mtd:
                enabled: true
                expiry: 0
                tags:
                    - example-lookup
                comment: ""
    extension_config:                   # Example lookup manager extension config
        ext-lookup-manager:
            data:
                lookup_manager_rules:
                    - arl: ""
                      format: json
                      name: tor
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
                      tags:
                        - tor
                    - arl: ""
                      format: json
                      name: talos
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/talos-ip-blacklist.json]'
                      tags:
                        - talos
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

#### Manually in the GUI

Lookups can be added in the web interface by navigating to **Automation** → **Lookups**. Name your lookup, choose the format, and copy paste the contents of your lookup in the `JSON data` field.

LimaCharlie also provides several publicly available lookups for use in your organization. More information and the contents of these can be found on [GitHub](https://github.com/refractionpoint/lc-public-lookups).

![Lookups Interface](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/lookups.png)

#### Automatically via the Lookup Manager

If your lookups change frequently and you wish to keep them up to date, LimaCharlie offers the lookup manager extension as a mechanism to automatically update your lookups every 24 hours. Documentation on the lookup manager can be found [here](/v2/docs/ext-lookup-manager).

### Example Lookup

```json
{
  "lookup_data": {
    "c:\\windows\\system32\\ping.exe": {
      "mtd1": "known_bin",
      "mtd2": 4
    },
    "c:\\windows\\system32\\sysmon.exe": {
      "mtd1": "good_val",
      "mtd2": 10
    }
  }
}
```

or

```json
{
  "newline_content": "lvalue1\nlvalue2\nlvalue3"
}
```

---

## Secrets

The secrets hive allows you to decouple secrets from their usage or configuration across LimaCharlie. This enables you to grant permissions to users that allow them to see the configuration of an output without having access to the associated credentials.

The most common usage is for storing secret keys used by various [Adapters](../concepts/adapters.md) or [Outputs](../concepts/outputs.md). By referencing secrets within the Config Hive, you can configure these services without needing to reveal secret keys to all users.

### Format

A secret record in hive has a very basic format:

```json
{
    "secret": "data"
}
```

The `data` portion of the records in this hive must have a single key called `secret` whose value will be used by various LimaCharlie components.

### Permissions

* `secret.get` - Retrieve secret data
* `secret.set` - Create or update secret data
* `secret.del` - Delete secret data
* `secret.get.mtd` - Get secret metadata
* `secret.set.mtd` - Set secret metadata

### Secret Management

#### Creating Secrets

With the appropriate permissions, users can create secrets in the following ways:

1. Using the LimaCharlie CLI: `limacharlie hive set secret` command
2. Via the web app: **Organization Settings** → **Secrets Manager**

#### Updating Secrets

Once they are set, secrets can be updated via the following methods:

1. Using the LimaCharlie CLI: `limacharlie hive update secret` command
2. Via the web app: **Organization Settings** → **Secrets Manager**. Select the secret you wish to update, and update in the dialog box. Click **Save Secret** to save changes.

### Usage

Using a secret in combination with an output has very few steps:

1. Create a secret in the `secret` hive
2. Create an Output and use the format `hive://secret/my-secret-name` as the value for a credentials field

### Example

Create a simple secret using the LimaCharlie CLI:

First, create a small file with the secret record in it:

```bash
$ echo "my-secret-value" > my-secret
```

Next, set this secret in Hive via the LimaCharlie CLI:

```bash
$ limacharlie hive set secret --key my-secret --data my-secret --data-key secret
```

You should get a confirmation that the secret was created, including metadata of the secret and associated OID:

```json
{
    "guid": "3a7a2865-a439-4d1a-8f50-b9a6d833075c",
    "hive": {
        "name": "secret",
        "partition": "8cbe27f4-aaaa-bbbb-cccc-138cd51389cd"
    },
    "name": "my-secret"
}
```

Next, create an output in the web app, using the value `hive://secret/my-secret` as the Secret Key value.

![Secret Configuration](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/secret.png)

When viewing the output's configuration, the secret will refer to the hive ARN rather than the actual credentials.

---

## Yara Rules

Yara rules can be stored in the Config Hive and used for scanning operations across your organization.

### Format

A yara record in hive has a very basic format:

```json
{
    "rule": "data"
}
```

The `data` portion of the records in this hive must have a single key called `rule` whose value will be the yara rule content used by various LimaCharlie components.

A single rule record can contain a series of actual Yara rules, like this: https://github.com/Yara-Rules/rules/blob/master/malware/APT_APT1.yar

### Permissions

* `yara.get` - Retrieve yara rules
* `yara.set` - Create or update yara rules
* `yara.del` - Delete yara rules
* `yara.get.mtd` - Get yara rule metadata
* `yara.set.mtd` - Set yara rule metadata

### Usage

Yara rules can be created in the `yara` Hive. Those rules will then be available either through the `ext-yara` Extension or directly using the `yara_scan` command with the reference `hive://yara/your-rule-name`.

### Example

Create a new Yara rule using the LimaCharlie CLI:

Assuming you have a Yara rule in the `rule.yara` file, load the rule in the LimaCharlie Hive via the CLI:

```bash
$ limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

You should get a confirmation that the rule was created, including metadata of the rule and associated OID:

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

To issue a scan command directly to a Sensor (via the Console or a rule):

```
yara_scan hive://yara/my-rule
```