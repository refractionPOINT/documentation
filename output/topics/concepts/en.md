# BinLib

Binary Library, or "BinLib", is a collection of executable binaries (such as EXE or ELF files) that have been observed within your environment. If enabled, this Extension helps you build your own private collection of observed executables for subsequent analysis and searching.

When LimaCharlie observes a binary and path for the first time a `CODE_IDENTITY` event is generated. The metadata from this event is stored within `binlib`, and is available for searching, tagging, and downloading. Additionally, you can run YARA scans against observed binaries.

## Enabling BinLib

BinLib requires subscribing to the `ext-reliable-tasking` Extension in order to function properly. This can be enabled in the Add-ons marketplace.

BinLib can be a powerful addition to your detection and response capabilities. Analysts can:

* Look for historical evidence of malicious binaries
* Tag previously-observed files for data enrichment (i.e. MITRE ATT&CK Techniques)
* Compare observed hashes to known good or known bad lists
* YARA scan and auto-tag for integration in detection & response rules

## Usage

First, subscribe your tenant to the BinLib extension.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/binlib-1.png)

To perform one of the following operations against your own library, choose the command and select **Run Request.**

The BinLib page in the web app offers an easy way to get started with some of the core requests exposed by the extension: Check Hash, Search, and Yara Scan.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/binlib-2.png)

### check_hash

*Accepted Values: MD5, SHA1, SHA256*

The `check_hash` operation lets you search to see if a particular hash has been observed in your Organization. Output includes a boolean if the hash was found and three hash values, if available.

Sample Output:

```
{
  "data": {
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

### get_hash_data

*Accepted Values: MD5, SHA1, SHA256*

**Careful Downloading Binaries**

LimaCharlie does not filter the binaries observed by your organization. You must exercise caution if downloading a malicious file. We recommend downloading potential malicious binaries to an isolated analysis system.

The `get_hash_data` operation provides a link to the raw data for the hash of interest, allowing you to download the resulting binary file (if previously observed within your environment).

Sample Output:

```
{
  "data": {
    "download_url": "https://storage.googleapis.com/lc-library-bin/b_2f5d0c...",
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

### get_hash_metadata

*Accepted Values: MD5, SHA1, SHA256*

The `get_hash_metadata` operation obtains the metadata for a hash of interest, including signing details, file type, and additional hashes.

```
{
  "data": {
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "metadata": {
      "imp_hash": "c105252faa9163fd63fb81bb334c61bf",
      "res_company_name": "Google LLC",
      "res_file_description": "Google Chrome Installer",
      "res_product_name": "Google Chrome Installer",
      "res_product_version": "113.0.5672.127",
      "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb",
      "sig_authentihash": "028f24e2c1fd42a3edaf0dcf8a59afe39201fa7d3bb5804dca8559fde41b3f34",
      "sig_issuer": "US, DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1",
      "sig_serial": "0e4418e2dede36dd2974c3443afb5ce5",
      "sig_subject": "US, California, Mountain View, Google LLC, Google LLC",
      "size": 5155608,
      "type": "pe"
    },
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

### search

The `search` operation searches the library for binary data points, including or *other than* a known hash.

Searchable fields include:

* imp_hash
* res_company_name
* res_file_description
* res_product_name
* sha256
* sig_authentihash
* sig_hash
* sig_issuer
* sig_subject
* size
* type

Note that search criteria are ANDed. Binaries must meet ALL criteria to be returned.

Search results can be downloaded as a CSV.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/binlib-3.png)

### tag

The `tag` operation allows you to add tag(s) to a hash, allowing for additional classification within binlib.

The below example Tags the Google Installer with the `google` tag.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/binlib-4.png)

Successful tagging yields an `updated` event:

```
{
  "data": {
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb",
    "updated": true
  }
}
```

### untag

The `untag` operation removes a tag from a binary.

### YARA scan

The `yara_scan` operation lets you run YARA scans across observed files. Scans require:

* Criteria or hash to filter files to be scanned
* Rule name(s) or rule(s)

You also have the option to tag hits on match.

Note that search criteria are ANDed. Binaries must meet ALL criteria to be returned.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/binlib-5.png)

## Automating

Here are some examples of useful rules that could be used to automate interactions with Binlib.

### Scan all acquired files with Yara

This rule will automatically scan all acquired files in binlib with a Yara rule:

```
detect:

event: acquired
op: is tagged
tag: ext:binlib

respond:

- action: report
  name: binlib-test
- action: extension request
  extension action: yara_scan
  extension name: binlib
  extension request:
    hash: '{{ .event.sha256 }}'
    rule_names:
      - yara_rule_name_here
```

and this rule will alert on matches:

```
detect:

event: yara_scan
op: exists
path: event/matches/hash

respond:

- action: report
  name: YARA Match via Binlib
```

# Enterprise SOC

The LimaCharlie SecOps Cloud Platform (SCP) is a unified platform for modern cybersecurity operations.

The SCP delivers core cybersecurity capabilities and infrastructure via a public cloud model: on-demand, pay-per-use, and API-first. For the cybersecurity industry, this is a paradigm shift comparable to how the IT public cloud revolutionized IT.

For enterprises and other large organizations, the SecOps Cloud Platform is a powerful way to take control of security posture and scale operations. The SCP can help teams gain visibility into their environments, eliminate coverage gaps, solve integration challenges, reduce spending on high-cost tools, free themselves from vendor lock-in, and build custom security solutions to meet their organization's unique needs.

## 3 implementation plans for immediate value

The SecOps Cloud Platform is a comprehensive platform for cybersecurity operations—but it doesn't have to be implemented all at once. The SCP's public cloud-like delivery model eliminates adoption hurdles for enterprises. Easily scaled and API-first, the SCP enables teams to integrate the platform into their security operations gradually, leveraging its capabilities progressively as they go. Here are three recommended first steps to help enterprises realize value from the SCP quickly.

### 1. Centralize telemetry data to improve visibility and streamline operations

The SecOps Cloud Platform allows enterprises to bring all of their telemetry data into one place—improving visibility, eliminating coverage gaps, and enabling streamlined SecOps workflows. Here is a general outline of what that looks like:

**Bring your telemetry data into the SCP.** The SecOps Cloud Platform allows enterprise teams to ingest data from any source. The platform's endpoint detection and response (EDR)-type sensors can be deployed directly on Windows, Mac, and Linux endpoints with full feature parity across these OSes. These sensors allow security teams to capture system events and other telemetry data in real time—or import event data from third-party EDR tools such as VMWare Carbon Black, CrowdStrike, SentinelOne, or Microsoft Defender. There are also browser-based EDR sensors to support Chrome and Edge deployments.

Log-type data can also be brought into the SCP using a system of adapters or via webhook. Supported log data sources include O365, 1Password, AWS CloudTrail, Google Cloud Platform (GCP), Slack Audit logs, and many more. For a comprehensive list, refer to the SCP documentation.

**Visualize and manage your telemetry data under a single plane.** Telemetry data brought into the SCP is normalized to a common JSON format and explorable through a single interface. The immediate advantage for security teams is improved visibility—and an end to coverage gaps that can jeopardize organizational security and compliance. In addition, the ability to manipulate data through a single UI helps teams eliminate integration challenges caused by other solutions and streamline their internal workflows.

**Go beyond observability.** The SecOps Cloud Platform's data-routing capabilities mean that it can be used as a simple observability point solution if you choose. But the SCP is capable of far more than this. All telemetry data brought into the platform can be run through an advanced detection and response engine, and wire-speed response actions can be taken on endpoints via the multiplatform SCP agent. From day one, security teams using the SCP for centralization and observability can also apply their own custom detection and response (D&R) logic to all telemetry data brought into the platform, leverage curated rulesets like Sigma, Soteria, or SOC Prime rules for the same purpose, or run historical threat hunts against data stored in the SCP.

The SecOps Cloud Platform helps enterprises improve visibility, eliminate coverage gaps, solve integration challenges, and make their workflows more efficient—and this is just the first step in what teams can achieve with the platform.

### 2. Reduce spending on SIEMs and other high-cost solutions

Because the SCP lets security teams bring in data from any source and export it to any destination, the platform can also be used as a pass-through to observe, transform, enrich, and anonymize data in-flight and route it to different destinations in a fine-grained way. This strategy can significantly reduce the costs of security information and event management (SIEM) tools and other expensive third-party solutions.

**Identify inefficiencies in your current data flow.** Many organizations simply send 100% of their telemetry data to their SIEM. They only use a fraction of that data, but they pay for all of it. Conduct a thorough review of how you are currently routing your telemetry data. Determine what data truly needs to be sent to your highest-cost tools—and what can be retained in lower-cost storage.

**Use the SCP's output controls to optimize your data routing.** Your options here are highly flexible and customizable:

Telemetry data can be sent to Splunk, Humio, Elastic, Amazon S3 buckets, Azure Event Hubs, Google Cloud Storage, and many other destinations.

Data can also be streamed to your destination(s) of choice with different degrees of granularity. On the more verbose end of the spectrum, it is possible to send all data events from a sensor to a given destination. But you can also create a tailored stream that sends only specific events to your output destination.

Enterprise teams can thus route their data for optimal cost savings. For example, a team might send only high-priority detections and failed 1Password login attempts to Splunk, a secondary tranche of log data and events to an Amazon S3 bucket, and retain everything else in low-cost cold storage.

**Use free storage and transparent pricing for compliance and additional savings.** The SCP offers one year of free storage of all telemetry data for the cost of ingestion. Pricing is transparent and easy to calculate, making it simple to determine the most cost-effective data flow and storage sites for your telemetry. All telemetry data is retained for one year by default in a fully searchable and explorable format, so you don't have to worry about losing data that you may need later on. Because the total cost of storage in the SCP cloud is often far more affordable than traditional data lakes, many organizations will be able to use the platform's built-in storage to address compliance requirements and reduce costs.

The SCP's data routing capabilities put enterprise teams in full control of their telemetry data, allowing them to cut spending on high-cost solutions while ensuring access to critical data in order to meet compliance and operational needs.

### 3. Simplify tooling and control your infrastructure

The SecOps Cloud Platform delivers the core components required to secure and monitor any organization. Over time, enterprises can leverage the SCP's numerous capabilities to develop a custom security infrastructure that they control completely. And while that is clearly a long-term project, enterprises that adopt the SCP can begin using the platform to simplify their stack right away:

**Replace one-off solutions.** The increasing specialization of cybersecurity products means most enterprise teams rely on a patchwork of solutions—and are sometimes forced to buy a tool to satisfy one, extremely narrow use case. Teams should begin by identifying their one-off tools and vendors and determining how they can be replaced with an SCP solution. The SecOps Cloud Platform offers a rich ecosystem of 100+ cybersecurity capabilities and integrations and a marketplace of add-ons to extend the platform. In many cases, teams will find that it is possible to replace single-use vendors with an SCP solution that offers equal or better performance, reducing tool sprawl and improving security operations at the same time.

**Upgrade existing tools or features.** The fragmentation of the current cybersecurity vendor space means that many enterprise teams end up using tools that excel in one arena but fall short in others. Instead of simply accepting the unsatisfactory parts of their stack, teams can use the SCP to augment or replace underperforming tools and features with best-in-breed alternatives.

**Begin your transition to infrastructure independence.** After teams shed one-off and redundant tools, they should begin to think strategically about how to leverage the SCP to free themselves from vendor lock-in once and for all. Look for vendor contracts due to expire or products nearing end-of-life and work with LimaCharlie engineers to develop, validate, and deploy a custom replacement ahead of time.

In the near term, the SecOps Cloud Platform lets enterprises simplify their deployments significantly. In the long term, it allows organizations to take full control of their tooling, infrastructure, and security posture.

# LimaCharlie Query Language

Beta Feature: LCQL is currently in Beta, and features may change in the future.

LimaCharlie Query Language (LCQL) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie. Telemetry ingested via EDR sensors or adapters are searchable via LCQL, and can be searched en masse. Sample use cases for LCQL include:

* Analyze your entire, multi-platform fleet for network connections of interest.
* Search across all Windows Event Logs for unique user activity.
* Look at all Linux systems for specific package installation events.
* Analyze all volume mounts and unmounts on macOS devices
* And many more!!!

The steps below walk you through creating your own LCQL queries. If you're looking for samples or LCQL inspiration, check out our [LCQL Examples](/v2/docs/lcql-examples) page.

## Building LimaCharlie Queries

LCQL queries contain 4 components with a 5th optional one, each component is separated by a pipe (`|`):

1. **Timeframe**: the time range the query applies to. This can be either a single offset in the past like `-1h` or `-30m`. Or it can be a date time range like `2022-01-22 10:00:00 to 2022-01-25 14:00:00`.

   Note: the time frame is still used in the CLI and API, but no longer exposed in the UI; use the time selector control instead.

2. **Sensor selector**: the set of sensors to query. This can be either `*` for all sensors, or a [Sensor Selector expression](/v2/docs/reference-sensor-selector-expressions), like `plat == windows` or `hostname == foo.com or hostname == bar.com`  (Note: a full list of platform types can be found in the [ID Schema Reference](/v2/docs/reference-id-schema))

3. **Event type**: the  event types to include in the query. Use  `or`  to search for multiple events at once, for example `NEW_PROCESS or DNS_REQUEST`, or a `*` to go over all event types.

4. **Filters**: the actual query filters. The filters are a series of statements combined with " and " and " or " that can be associated with parenthesis (`()`). String literals, when used, can be double-quoted to be case insensitive or single-quoted to be case sensitive. Selectors behave like  rules, for example: `event/FILE_PATH`.

The [Query Console UI](/v2/docs/query-console-ui) provides a type-ahead assistance to bring up the available operators and help design the query.

5. **Projection (optional)**: a list of fields you would like to extract from the results with a possible alias, like: `event/FILE_PATH as path event/USER_NAME AS user_name event/COMMAND_LINE`. The Projection can also support a grouping functionality by adding `GROUP BY(field1 field2 ...)` at the end of the projection statement.

When grouping, all fields being projected must either be in the `GROUP BY` statement, or have an aggregator modifier. An aggregator modifer is, for example, `COUNT( host )` or `COUNT_UNIQUE( host )` instead of just `host`.

A full example with grouping is:

`-1h | * | DNS_REQUEST | event/DOMAIN_NAME contains "apple" | event/DOMAIN_NAME as dns COUNT_UNIQUE(routing/hostname) as hostcount GROUP BY(dns host)`

which would give you the number of hosts having resolved a domain containing `apple`, grouped by domain.

All of this can result in a query like:

`-30m | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell" | event/COMMAND_LINE as cli event/FILE_PATH as path routing/hostname as host`

OR

`-30m | plat == windows | * | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`

> **Projection Syntax**
>
> Note: There is no space between `BY` and the `(` opening of the parentheses in a projection.
>
> Example: `GROUP BY(dns host)` or `COUNT_UNIQUE(routing/hostname)`