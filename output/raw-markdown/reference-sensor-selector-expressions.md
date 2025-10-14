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

Reference: Sensor Selector Expressions

* 31 Oct 2024
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Reference: Sensor Selector Expressions

* Updated on 31 Oct 2024
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Many components in LimaCharlie require selecting a set of Sensors based on some characteristics. The selector expression is a text field that describe what matching characteristics the selector is looking for.

The following fields are available in this evaluation:

* `sid`: the Sensor ID
* `oid`: the Organization ID
* `iid`: the Installation Key ID
* `plat`: the Platform name (see [platforms](/v2/docs/reference-id-schema#platforms))
* `ext_plat`: the Extended Platform name (see [platforms](/v2/docs/reference-id-schema#platforms))
* `arch`: the Architecture name (see [architectures](/v2/docs/reference-id-schema#architecture))
* `enroll`: the Enrollment as a second epoch timestamp
* `hostname`: the hostname
* `mac_addr`: the latest MAC address
* `alive`: second epoch timestamp of the last time the Sensor connected to the cloud
* `ext_ip`: the last external IP
* `int_ip` the last internal IP
* `isolated`: a boolean True if the sensor's network is isolated
* `should_isolate`: a boolean True if the sensor is marked to be isolated
* `kernel`: a boolean True if the sensor has some sort of "kernel" enhanced visibility
* `did`: the Device ID the sensor belongs to
* `tags`: the list of tags the sensor currently has

The following are the available operators:

* `==`: equals
* `!=`: not equal
* `in`: element in list, or substring in string
* `not in`: element not in list, or substring not in string
* `matches`: element matches regular expression
* `not matches`: element does not match regular expression

Here are some examples:

* all sensors with the test tag: `test in tags`
* all windows boxes with an internal IP starting in 10.3.x.x: `` plat == windows and int_ip matches `^10\.3\..*` ``
* all 1password sensors, strings starting with a number need to be quoted with a backtick: `` plat == `1password` ``
* all linux with network isolation or evil tag: `plat == linux or (isolated == true or evil in tags)`

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

* [LimaCharlie Query Language](/docs/lcql)
* [LCQL Examples](/docs/lcql-examples)
* [Velociraptor](/docs/ext-velociraptor)

---

###### What's Next

* [Events](/docs/events)

Tags

* [platform](/docs/en/tags/platform)
* [reference](/docs/en/tags/reference)
* [sensors](/docs/en/tags/sensors)
