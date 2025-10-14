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

Soteria EDR Rules

* 09 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Soteria EDR Rules

* Updated on 09 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Soteria's EDR ruleset provides coverage across Windows, Linux, and macOS. You can check the dynamic MITRE ATT&CK mapping here:

* [All rules](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fstorage.googleapis.com%2Fsoteria-detector-mapping%2F%2Fall.json)
* [Windows](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//windows.json)
* [Linux](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//linux.json)
* [macOS](https://mitre-attack.github.io/attack-navigator/#layerURL=https://storage.googleapis.com/soteria-detector-mapping//mac.json)

Data access

Please note that Soteria won’t get access to your data, and you won’t be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

The following events are utilized by Soteria rules. Please ensure that they are configured within your Organization:

* `CODE_IDENTITY`
* `DNS_REQUEST`
* `EXISTING_PROCESS`
* `FILE_CREATE`
* `FILE_MODIFIED`
* `MODULE_LOAD`
* `NETWORK_CONNECTIONS`
* `NEW_DOCUMENT`
* `NEW_NAMED_PIPE`
* `NEW_PROCESS`
* `REGISTRY_WRITE`
* `REGISTRY_CREATE`
* `SENSITIVE_PROCESS_ACCESS`
* `THREAD_INJECTION`

This can also be done in the Add-ons Marketplace.

## Enabling Soteria's EDR Rules

Soteria's EDR rules can be activated via two means.

### Activating via the Web UI

To enable Soteria's EDR ruleset, navigate to the **Extensions** section of the Add-On Marketplace and search for Soteria. You can also directly select `soteria-rules-edr`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-1.png)

*Please note: Pricing may reflect when the screenshot was taken, not the actual pricing*

Under the Organization dropdown, select a tenant (organization) you want to subscribe to Soteria rules and click **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-edr-3.png)

### Infrastructure as Code

Alternatively, to manage tenants and LimaCharlie functionality at scale, you can leverage our Infrastructure as Code functionality.

Endpoint Detection & Response

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

* [Reference: EDR Events](/docs/reference-edr-events)
* [Soteria M365 Rules](/docs/soteria-m365-rules)
* [Soteria AWS Rules](/docs/soteria-aws-rules)
* [Soteria Rules](/docs/soteria-rules)
* [Managed Rulesets](/docs/managed-rulesets)

---

###### What's Next

* [Soteria M365 Rules](/docs/soteria-m365-rules)

Table of contents

+ [Enabling Soteria's EDR Rules](#enabling-soteria-s-edr-rules)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
