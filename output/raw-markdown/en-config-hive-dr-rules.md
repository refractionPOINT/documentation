[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Config Hive: Detection & Response Rules

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Config Hive: Detection & Response Rules

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

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Config Hive: Yara](/docs/config-hive-yara)
* [Config Hive: Secrets](/docs/config-hive-secrets)
* [Config Hive: Cloud Sensors](/docs/config-hive-cloud-sensors)
* [Config Hive](/docs/config-hive)
* [Config Hive: Lookups](/docs/config-hive-lookups)

---

###### What's Next

* [Config Hive: Lookups](/docs/config-hive-lookups)

Table of contents

+ [Format](#format)
+ [Permissions](#permissions)
+ [Command-Line Usage](#command-line-usage)
+ [Usage](#usage)
+ [Example](#example)

Tags

* [api](/docs/en/tags/api)
* [platform](/docs/en/tags/platform)
