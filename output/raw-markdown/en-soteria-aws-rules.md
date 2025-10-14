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

Soteria AWS Rules

* 10 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Soteria AWS Rules

* Updated on 10 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Soteria's AWS ruleset provides coverage across multiple AWS telemetry streams, including:

* [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)
* [AWS GuardDuty](https://aws.amazon.com/guardduty/)

Data access

Please note that Soteria won’t get access to your data, and you won’t be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

To leverage detection logic provided by the ruleset:

1. Subscribe your tenant to the Soteria AWS [ruleset extension](https://app.limacharlie.io/add-ons/extension-detail/soteria-rules-aws).
2. Subscribe your tenant to [tor](/v2/docs/ext-lookup-manager) lookup (provided at no cost).
3. Configure [AWS CloudTrail](/v2/docs/adapter-types-aws-cloudtrail) and [AWS GuardDuty](/v2/docs/adapter-types-aws-guardduty) adapters to start collecting AWS audit logs.

## Enabling Soteria's AWS Rules

Soteria's AWS rules can be activated via two means.

### Activating via the Web UI

To enable Soteria's AWS ruleset, navigate to the **Extensions** section of the **Add-On Marketplace** and search for Soteria. You can also directly select `soteria-rules-aws`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-aws-1.png)

*Please note: Pricing may reflect when the screenshot was taken, not the actual pricing*

Under the Organization dropdown, select a tenant (organization) you want to subscribe to **soteria-rules-aws** and click **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-aws-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-aws-3.png)

### Infrastructure as Code

Alternatively, to manage tenants and LimaCharlie functionality at scale, you can leverage our Infrastructure as Code functionality.

Amazon Web Services

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

* [Soteria M365 Rules](/docs/soteria-m365-rules)
* [Soteria Rules](/docs/soteria-rules)
* [Soteria EDR Rules](/docs/soteria-edr-rules)
* [Managed Rulesets](/docs/managed-rulesets)

---

###### What's Next

* [Soteria EDR Rules](/docs/soteria-edr-rules)

Table of contents

+ [Enabling Soteria's AWS Rules](#enabling-soteria-s-aws-rules)

Tags

* [aws](/docs/en/tags/aws)
* [detection and response](/docs/en/tags/detection%20and%20response)
