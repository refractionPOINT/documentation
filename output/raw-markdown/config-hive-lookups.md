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

Config Hive: Lookups

* 07 Oct 2025
* 3 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Config Hive: Lookups

* Updated on 07 Oct 2025
* 3 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Format

Lookups are dictionaries/maps/key-value-pairs where the key is a string. The lookup can then be queried by various parts of LimaCharlie (like  rules). The value component of a lookup must be a dictionary and represents metadata associated with the given key, which will be returned to the rule using the lookup.

Lookup data can be ingested by specifying one of the following root keys indicating the format of the lookupd data:

* `lookup_data`: represented direct as parsed JSON.
* `newline_content`: a string where each key is separated by a newline, LimaCharlie will assume the metadata is empty.
* `yaml_content`: a string in YAML format that contains a dictionary with the string keys and dictionary metadata like the `lookup_data`.

## Permissions

* `lookup.get`
* `lookup.set`
* `lookup.del`
* `lookup.get.mtd`
* `lookup.set.mtd`

## Usage

### Infrastructure as Code

```
hives:
    lookup:                             # Example lookup in the lookup hive
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
    extension_config:                   # Example lookup manager extension config
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

### Manually in the GUI

Lookups can be added in the web interface by navigating to Automation --> Lookups. Name your lookup, choose the format, and copy paste the contents of your lookup in the `JSON data` field.

LimaCharlie also provides several publicly available lookups for use in your Organization. More information and the contents of these can be found on [GitHub](https://github.com/refractionpoint/lc-public-lookups). The contents of these lookups can be used here as well.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/lookups.png)

### Automatically via the Lookup Manager

If your lookups change frequently and you wish to keep them up to date, LimaCharlie offers the lookup manager extension as a mechanism to automatically update your lookups every 24 hours. Documentation on the lookup manager can be found [here](/v2/docs/ext-lookup-manager).

## Example Lookup

```
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

```
{
  "newline_content": "lvalue1\nlvalue2\nlvalue3"
}
```

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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
* [Config Hive: Cloud Sensors](/docs/config-hive-cloud-sensors)
* [Config Hive: Secrets](/docs/config-hive-secrets)
* [Config Hive: Detection & Response Rules](/docs/config-hive-dr-rules)
* [Config Hive](/docs/config-hive)

---

###### What's Next

* [Config Hive: Secrets](/docs/config-hive-secrets)

Table of contents

+ [Format](#format)
+ [Permissions](#permissions)
+ [Usage](#usage)
+ [Example Lookup](#example-lookup)

Tags

* [api](/docs/en/tags/api)
* [platform](/docs/en/tags/platform)
