---

Config Hive: Cloud Sensors

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Config Hive: Cloud Sensors

* Updated on 05 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Format

## Permissions

* `cloudsensor.get`
* `cloudsensor.set`
* `cloudsensor.del`
* `cloudsensor.get.mtd`
* `cloudsensor.set.mtd`

## Command-Line Usage

Hive secrets can be managed from the command-line, via the `limacharlie hive` command. Positional and optional arguments for command-line usage are below:

```
usage: limacharlie hive [-h] [-k KEY] [-d DATA] [-pk PARTITIONKEY] [--etag ETAG] [--expiry EXPIRY] [--enabled ENABLED] [--tags TAGS] action hive_name

positional arguments:
  action                the action to take, one of: list, list_mtd, get, get_mtd, set, update, remove
  hive_name             the hive name

options:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     the name of the key.
  -d DATA, --data DATA  file containing the JSON data for the record, or "-" for stdin.
  -pk PARTITIONKEY, --partition-key PARTITIONKEY
                        the partition key to use instead of the default OID.
  --etag ETAG           the optional previous etag expected for transactions.
  --expiry EXPIRY       a millisecond epoch timestamp when the record should expire.
  --enabled ENABLED     whether the record is enabled or disabled.
  --tags TAGS           comma separated list of tags.
```

## Usage

## Example

```
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

Thank you for your feedback! Our team will get back to you

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Config Hive: Yara](/docs/config-hive-yara)
* [Config Hive: Detection & Response Rules](/docs/config-hive-dr-rules)
* [Config Hive: Secrets](/docs/config-hive-secrets)
* [Config Hive](/docs/config-hive)
* [Config Hive: Lookups](/docs/config-hive-lookups)

---

###### What's Next

* [Config Hive: Detection & Response Rules](/docs/config-hive-dr-rules)

Table of contents

+ [Format](#format)
+ [Permissions](#permissions)
+ [Command-Line Usage](#command-line-usage)
+ [Usage](#usage)
+ [Example](#example)

Tags

* [api](/docs/en/tags/api)
* [platform](/docs/en/tags/platform)
