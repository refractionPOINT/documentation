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

Config Hive: Yara

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Config Hive: Yara

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

Next, assuming you want to issue a scan command directly to a Sensor (via the Console or a  rule):

```
yara_scan hive://yara/my-rule
```

Command-line Interface

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

* [Config Hive: Cloud Sensors](/docs/config-hive-cloud-sensors)
* [Config Hive: Detection & Response Rules](/docs/config-hive-dr-rules)
* [Config Hive](/docs/config-hive)
* [Config Hive: Lookups](/docs/config-hive-lookups)
* [Config Hive: Secrets](/docs/config-hive-secrets)

---

###### What's Next

* [Infrastructure as Code](/docs/infrastructure-as-code)

Table of contents

+ [Format](#format)
+ [Usage](#usage)
+ [Example](#example)

Tags

* [api](/docs/en/tags/api)
* [platform](/docs/en/tags/platform)
