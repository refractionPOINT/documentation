# Config Hive: Yara

## Format

A yara record in `hive` has a very basic format:

```
{
    "rule": "data"
}
```

The `data` portion of the records in this hive must have a single key called `rule` who's value will be the yara rule content used by various LimaCharlie components.

A single rule record can contain a series of actual Yara rule, like this: https://github.com/Yara-Rules/rules/blob/master/malware/APT\_APT1.yar

## Permissions

The `yara` hive requires the following permissions for the various operations:

* `yara.get`
* `yara.set`
* `yara.del`
* `yara.get.mtd`
* `yara.set.mtd`

## Usage

Yara rules can be create in the `yara` Hive. Those rules will then be available, either through the `ext-yara` Extension, or directly using the `yara_scan` command directly using the reference `hive://yara/your-rule-name`.

## Example

Let's create a new Yara rule using the LimaCharlie CLI in a terminal.

Assuming you have a Yara rule in the `rule.yara` file.

Load the rule in the LimaCharlie Hive via the CLI:

```
$ limacharlie hive set yara --key my-rule --data rule.yara --data-key rule
```

You should get a confirmation that the rule was created, including metadata of the rule associated OID:

```
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

> **Note:** In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

> **Note:** Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.