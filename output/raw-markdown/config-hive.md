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

Config Hive

* 02 Jan 2025
* 5 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Config Hive

* Updated on 02 Jan 2025
* 5 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The Config Hive, or "Hive", is the main configuration system for LimaCharlie. It is a generic set of APIs using by LimaCharlie to maintain the configuration of various systems within the platform. We make the Config Hive accessible to help you configure the wide range of systems, features, and extensions within LimaCharlie in a cohesive way. Each feature or system configuration lives in its own "hive".

Components managed through Hive:

* Cloud Sensors (`cloud_sensor`)
* Detection & Response Rules (`dr-general`, `dr-managed` and `dr-service`)
* False Positive Rules (`fp`)
* Lookups (`lookup`)
* [Secrets](/v2/docs/config-hive-secrets) (`secret`)

The Hive contains configuration records organized in a simple hierarchy: `/hive/{hive_name}/{oid}/{record_name}`. Let's examine each part of this record:

* The `hive_name` represents the type of records it contains. For example, the `cloud_sensor` hive name will contain all records relating to cloud sensors (cloud hosted [LimaCharlie Adapters](/v2/docs/adapters)).
* The `oid` is a "partition" for the records, in this case an Organization ID.
* The `record_name` is the unique name for the record.

Setting and updating records in Hive will automatically orchestrate the necessary changes in the relevant service. For example, updating a `cloud_sensor` record will automatically reapply the new configurations to the cloud hosted LimaCharlie Adapter. Deleting the same record will stop the Adapter.

The record data itself will be dependant on the hive name, but it will always be a JSON dictionary.

## Exploring

The best way to explore configurations in LimaCharlie and hive is through the LimaCharlie CLI (`pip install limacharlie`).

The CLI offers a simple interface to list, get and modify records in a single unified way regardless of the type of configuration.

The core command line commands are:

* `limacharlie hive list --help`
* `limacharlie hive get --help`
* `limacharlie hive set --help`
* `limacharlie hive update --help`
* `limacharlie hive remove --help`

For example, if you want to explore the  rules ("general" namespace) stored in LimaCharlie, you could issue:

```
limacharlie hive list dr-general
```

## Record Structure

Records contain 3 components:

* The record data itself (referenced to as `data`), who's format is dependant on the hive where it lives.
* User Metadata (referenced to as `usr_mtd`). As outlined below, this is metadata that can modified directly by you and can be exposed to users using specific permissions without giving access to the full record data.
* System Metadata (referenced to as `sys_mtd`). This is metadata that is generated and maintained by the Hive system.

### User Metadata

The user metadata format is the following:

```
{
    "expiry": 123,          // a milisecond epoch time when the record will automatically expire and be deleted.
    "tags": ["abc", "def"], // a list of tags on this record.
    "enabled": true         // a boolean indicating whether the record is in an "enabled" state or not.
}
```

### System Metadata

The system metadata format is the following:

```
{
    "etag": "abc",        // a unique tag representing the current state of data of the record. Can be used for optimistic transactions: https://en.wikipedia.org/wiki/HTTP_ETag
    "last_author": "abc", // the identity of the last entity having modified the record.
    "last_mod": 123,      // a milisecond epoch of the last time the record was modified.
    "created_by": "abc",  // the identity of the entity that originally created the record.
    "created_at": 123,    // a milisecond epoch of the time the record was originally created.
    "guid": "abc",        // a globally unique identifier of the record (not its data).
    "last_error": "abc",  // the contents of the last error related to the record.
    "last_error_ts": 123  // the milisecond epoch of the last time an error occured relating to the record.
}
```

## Accessing

### REST

The config hive can be accessed through the LimaCharlie REST API (https://api.limacharlie.io/static/swagger/).

### Python CLI

Install the Python LimaCharlie CLI using `pip install limacharlie`.

Possible operations: `limacharlie hive --help`

Repository: https://github.com/refractionPOINT/python-limacharlie/

## Conditional Update

One of the advantages of the Hive system is the ability to perform conditional updates (where you prevent two entities from updating
 and overwriting each other's changes).

You may perform conditional record updates using the `etag` parameter. When set during an update, the hive system will verify that
 the record it is about to update currently has the etag provided. If the etags do not match, the update is not performed. This allows
 you to:

1. Get a Record X
2. Update some values of X locally
3. Set the updated Record X, including the etag received during the Get

This enables you to detect when "update collision" occur. An example implementation can be found in the `update` function of the Python SDK [here](https://github.com/refractionPOINT/python-limacharlie/blob/016abfe041877132e4c6dd948f1532b173ca7883/limacharlie/Hive.py#L121).

### Infrastructure as Code

The Hive system also simplifies how you can store and apply your configurations through infrastructure as code.

All hive related configurations are found under the key `hives`, followed by the hive name. For example:

```
hives:
  dr-general:
    Microsoft Defender MALWAREPROTECTION_RTP_DISABLED:
      data:
        detect:
          event: WEL
          op: and
          rules:
            - op: is
              path: event/EVENT/System/Channel
              value: Microsoft-Windows-Windows Defender/Operational
            - op: is
              path: event/EVENT/System/EventID
              value: "5001"
        respond:
          - action: report
            name: Microsoft-defender-MALWAREPROTECTION_RTP_DISABLED
      usr_mtd:
        enabled: true
        expiry: 0
        tags:
          - defender
```

The above example refers to the `dr-general` hive (general namespace for D&R rules), to the record named `Microsoft Defender MALWAREPROTECTION_RTP_DISABLED` who's `data` contains the actual content of the D&R rule, and this record is enabled, does not expire. The record is tagged with `defender`.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Command-line Interface

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

* [LimaCharlie SDK & CLI](/docs/limacharlie-sdk)

---

###### What's Next

* [Config Hive: Cloud Sensors](/docs/config-hive-cloud-sensors)

Table of contents

+ [Exploring](#exploring)
+ [Record Structure](#record-structure)
+ [Accessing](#accessing)
+ [Conditional Update](#conditional-update)

Tags

* [platform](/docs/en/tags/platform)
