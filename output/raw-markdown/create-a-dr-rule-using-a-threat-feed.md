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

Create a D&R Rule Using a Threat Feed

* 08 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Create a D&R Rule Using a Threat Feed

* Updated on 08 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

A common use case for  rules is to use them to compare telemetry against known malicious IPs, domain names, or file hashes via threat feeds. With LimaCharlie, it is easy to leverage public threat feeds or create your own.

To configure a threat feed, it must first be enabled within the Add-ons Marketplace. First, select a threat feed from the plethora available for free. In the following example, we will enable `crimeware-ips`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/crimeware-ips(1).png)

Select `Subscribe`, which will make the feed available to the respective Organization.

Once subscribed, you can write a D&R rule to detect whenever there is a match to an IP within the threat feed. Navigate to `D&R Rules` within the web application main page, and select `+ New Rule`. Begin your rule with the following template:

```
event: NETWORK_CONNECTIONS
op: lookup
path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
resource: hive://lookup/crimeware-ips
```

## Additional Telemetry Points

Configure a lookup based on file hash:

```
op: lookup
event: CODE_IDENTITY
path: event/HASH
resource: hive://lookup/my-hash-lookup
```

Configure a lookup based on domain name(s):

```
op: lookup
event: DNS_REQUEST
path: event/DOMAIN_NAME
resource: hive://lookup/my-dns-lookup
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

* [Detection and Response Examples](/docs/detection-and-response-examples)
* [Detection and Response](/docs/detection-and-response)
* [Lookups](/docs/lookups)
* [Lookup Manager](/docs/ext-lookup-manager)
* [API Integrations](/docs/add-ons-api-integrations)
* [VirusTotal](/docs/api-integrations-virustotal)

---

###### What's Next

* [Detection Logic Operators](/docs/detection-logic-operators)

Table of contents

+ [Additional Telemetry Points](#additional-telemetry-points)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [detection and response](/docs/en/tags/detection%20and%20response)
* [tutorial](/docs/en/tags/tutorial "Tutorial")
