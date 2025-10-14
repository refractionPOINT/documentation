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

Zeek

* 09 Oct 2025
* 3 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Zeek

* Updated on 09 Oct 2025
* 3 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Zeek Extension Pricing

While it is Free to enable the Zeek extension, pricing is applied to processed PCAPs at a rate of $0.02/GB.

[Zeek](https://zeek.org/) is a comprehensive platform for network traffic analysis and intrusion detection.

Once enabled, this extension allows you to generate Zeek logs from packet capture (PCAP) files collected via Artifacts. The resulting Zeek log files are subsequently parsed and pushed into the `ext-zeek` Sensor timeline as JSON. You can create detection & response rules to automate based on Zeek log data.

LimaCharlie will automatically kick off Zeek based on the artifact ID provided in a  rule action.

## Configuration

To enable the Zeek extension, navigate to the [Zeek extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-zeek) in the marketplace. Select the Organization you wish to enable the extension for, and select Subscribe.

When enabled, you may configure the response of a D&R rule to run Zeek against an artifact event. Here is an example D&R rule:

**Detect:**

```
artifact type: pcap
event: ingest
op: exists
path: /
target: artifact_event
```

**Respond:**

```
- action: extension request
  extension action: run_on
  extension name: ext-zeek
  extension request:
    artifact_id: '{{ .routing.log_id }}'
    retention: 30
```

## Results

```
/opt/zeek/bin/zeek -C LogAscii::use_json=T --no-checksums --readfile /path/to/your.pcap
```

Upon running Zeek, several JSON log files are generated. The log files are parsed and pushed into the `ext-zeek` sensor timeline.

![Screenshot 2024-02-20 1.04.52 PM.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot%202024-02-20%201.04.52%20PM.png)

## Usage

### Via Automatic PCAP Collection

**Note: This is only available on Linux sensors**

Enable PCAP collection on your Linux sensors via a PCAP capture rule within the artifact collection extension.

For example, if you have an interface `ens4` and would like to gather PCAPs of network traffic on that interface on TCP port 80, you would craft the following rule.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/zeek-2.png)

Once ~30MB of traffic has been collected, a PCAP will be uploaded as an artifact in LimaCharlie. Subsequent PCAPs will continue to be uploaded as additional PCAPs as they hit the size threshold.

All PCAPs uploaded will trigger the [D&R rule below](#dr-rule).

### Via Manual PCAP Upload

If you have already generated a PCAP on a system or systems, you can manually ingest those as artifacts by running the following in your sensor console:

```
artifact_get --file /path/to/your.pcap --type pcap
```

This will trigger the [D&R rule below](#dr-rule).

### D&R Rule

**Detect:**

```
artifact type: pcap
event: ingest
op: exists
path: /
target: artifact_event
```

**Respond:**

```
- action: extension request
  extension action: run_on
  extension name: ext-zeek
  extension request:
    artifact_id: '{{ .routing.log_id }}'
    retention: 30
```

### Migrating D&R Rule from legacy Service to new Extension

***LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy zeek service, preview the change and execute the conversion required in the rule "response".

Command line to preview zeek rule conversion:

```
limacharlie extension convert_rules --name ext-zeek
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute zeek rule conversion:

```
limacharlie extension convert_rules --name ext-zeek --no-dry-run
```

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

###### What's Next

* [Hayabusa to BigQuery](/docs/hayabusa-to-bigquery)

Table of contents

+ [Configuration](#configuration)
+ [Results](#results)
+ [Usage](#usage)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
