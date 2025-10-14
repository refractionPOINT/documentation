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

Test a New Sensor Version

* 25 Apr 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Test a New Sensor Version

* Updated on 25 Apr 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Prior to rolling out a new Sensor version, we recommend testing to ensure everything works as intended within your environment. While we test Sensors before releasing them, we cannot predict every niche use case. We also recommend testing on `dev` or `test` systems prior to deployment in production, again, to eliminate any concerns of resource utilization or Sensor operations.

Sensor version testing is done via LimaCharlie's tagging functionality.

When you tag a Sensor with `lc:latest`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the latest version of the sensor will be used instead. You can apply this tag to a handful of systems to test-deploy the latest version.

Alternatively, you can tag a sensor with `lc:stable`. Similarly, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the stable version of the sensor will be used instead.

You can tag a Sensor by opening the sensors list, selecting a sensor you would like to test, and navigating to the `tags` field on the sensor `Overview`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(314).png)

Simply type `lc:stable` and click `Update Tags`.

Note: It can take up to 10 minutes to update the sensor to the tagged version.

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

###### Related articles

* [Endpoint Agent Versioning and Upgrades](/docs/endpoint-agent-versioning-and-upgrades)
* [Updating Sensors to the Newest Version](/docs/updating-sensors-to-the-newest-version)

---

###### What's Next

* [Updating Sensors to the Newest Version](/docs/updating-sensors-to-the-newest-version)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [sensors](/docs/en/tags/sensors)
* [tutorial](/docs/en/tags/tutorial "Tutorial")
