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

SOC Prime Rules

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# SOC Prime Rules

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

To use SOC Prime rules in LimaCharlie, start by configuring lists in [SOC Prime](https://socprime.com/). You can learn how to do it [here](https://socprime.com/blog/enable-continuous-content-management-with-the-soc-prime-platform/).

After the lists have been configured, you can finish the configuration in LimaCharlie. Note that currently the SOC Prime API is not available for free users. It is available only for paid users or if they requested a trial.

First, enable the `socprime` add-on on the LimaCharlie marketplace.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2855%29.png)

Then, navigate to the Integrations page in your Organization, enter the SOC Prime Key & click `Update`.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2856%29.png)

When the Key is saved, you will get the ability to select the SOC Prime content lists you want to have populated in LimaCharlie as detection & response rules. After selecting the lists & clicking `Update`, you are all set to start receiving detections based on the SOC Prime lists.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2857%29.png)

A detection that comes from the SOC Prime Lists, will have `socprime` listed as a detection author.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2858%29.png)

Note that adding a new rule to a SOC Prime content list that is enabled in LC will see the new rule be applied during next sync (LimaCharlie syncs the SOC Prime rules every 3 hours).

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

* [Managed Rulesets](/docs/managed-rulesets)
* [Detection and Response Examples](/docs/detection-and-response-examples)
* [Detection and Response](/docs/detection-and-response)
* [Soteria Rules](/docs/soteria-rules)

---

###### What's Next

* [Community Rules](/docs/community-rules)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
