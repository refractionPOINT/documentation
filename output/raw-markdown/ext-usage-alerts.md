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

Usage Alerts

* 09 Jan 2025
* 4 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Usage Alerts

* Updated on 09 Jan 2025
* 4 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The usage alerts Extension allows you to create, maintain, & automatically refresh usage alert conditions for an Organization.

For example, you can create a usage alert rule that will fire a detection when artifact downloads have reached a 1GB threshold in the last 30 days (43200 minutes). This alert will be saved as a managed  rule. When the threshold is reached, a detection will be created with the following `cat`:

`Usage alert - Output data over threshold - 1024 MB in 30.00 days`

These alert rules can be managed across tenants using the Infrastructure as Code extension.

Every hour, LimaCharlie will sync all of the usage alert rules in the configuration. They can also be manually synced by clicking the `Sync Usage Alert Rules` button on the extension page. When a usage alert rule is added, it will **not** be automatically synced immediately, unless you click on `Sync Usage Alert Rules`.

**NOTE**: The maximum timeframe is currently 43200 minutes (30 days).

## Usage - GUI

To define a new usage alert, simply click on the `Add New Usage Alert` button in the extension UI. Give it a name, like `Output data over threshold`, select a SKU (in this case, `output_data`), a timeframe, a limit, and click `Save`. ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(275).png "image(275).png")

If you want it to be added immediately, click on the `Sync Usage Alert Rules` button. Otherwise, it will get pushed automatically at the next hour interval.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(278).png "image(278).png")

This will create a managed D&R rule on the backend in the `dr-managed` hive and will sync automatically every hour.

```
hives:
    dr-managed:
        Output data over threshold:
            data:
                detect:
                    event: billing_record
                    op: and
                    rules:
                        - op: is
                          path: event/record/cat
                          value: output
                        - op: is
                          path: event/record/k
                          value: bytes_tx
                    target: billing
                respond:
                    - action: report
                      name: Usage alert - Output data over threshold - 1024 MB in 24.00 hours
                      suppression:
                        count_path: event/record/v
                        keys:
                            - output
                            - bytes_tx
                            - ext-usage-alerts
                            - Output data over threshold
                        max_count: 1.073741824e+09
                        min_count: 1.073741824e+09
                        period: 43200m
```

## Usage - Infrastructure as Code

If you are managing your organizations via infrastructure as code, you can also configure these rules in the `extension_config` hive.

```
hives:
    extension_config:
        ext-usage-alerts:
            data:
                usage_alert_rules:
                    - enabled: true
                      limit: 1024
                      name: Output data over threshold
                      sku: output_data
                      timeframe: 43200
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

* [Extensions](/docs/extensions)
* [Using Extensions](/docs/using-extensions)

---

###### What's Next

* [YARA Manager](/docs/ext-yara-manager)

Table of contents

+ [Usage - GUI](#usage-gui)
+ [Usage - Infrastructure as Code](#usage-infrastructure-as-code)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [billing](/docs/en/tags/billing)
* [extensions](/docs/en/tags/extensions)
