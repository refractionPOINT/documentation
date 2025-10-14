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

Sensor Cull

* 08 Oct 2025
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Sensor Cull

* Updated on 08 Oct 2025
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The Sensor Cull Extension performs continuous cleaning of "old" sensors that have not connected to an Organization within a set period of time. This is useful for environments with cloud deployments or VM/template-based deployments that may enroll sensors repeatedly, and for a short period of time.

The extension works by creating rules that describe when specified sensors should be cleaned up.

## Enabling the Sensor Cull Extension

To enable the Sensor Cull extension, navigate to the [Sensor Cull extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-sensor-cull) in the LimaCharlie marketplace.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-cull-1.png)

After clicking **Subscribe**, the Sensor Cull extension should be available almost immediately.

## Using the Sensor Cull Extension

Once enabled, you will see a **Sensor Cull** option under **Sensors** within the LimaCharlie web UI. You can also interact with the extension via REST API.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-cull-2.png)

Within the Sensor Cull module, you have the ability to create rules. Sensor Cull rules are run automatically once a day, and can be edited as needed.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-cull-3.png)

Each rule specifies a single sensor `tag` used as a selector for the sensors the rule applies to. A rule also has a `name` (simply used for your bookkeeping), and a `ttl` which is the number of days a sensor can remain unconnected to LimaCharlie before it becomes eligible for cleanup.

## Actions via REST API

The following REST API actions can be sent to interact with the Sensor Cull extension:

### get\_rules

Get the list of existing rules

```
{
  "action": "get_rules"
}
```

### run

Perform an ad-hoc cleanup.

```
{
  "action": "run"
}
```

### add\_rule

The following example creates a rule name `my new rule` that applies to all sensors with the `vip` Tag, and cleans them up when they have not connected in 30 days.

```
{
  "action": "add_rule",
  "name": "my new rule",
  "tag": "vip",
  "ttl": 30
}
```

### del\_rule

Delete an existing rule by name.

```
{
  "action": "del_rule",
  "name": "my new rule"
}
```

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.

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

* [VDI & Virtual Machine Templates](/docs/vdi-virtual-machine-templates)

---

###### What's Next

* [Usage Alerts](/docs/ext-usage-alerts)

Table of contents

+ [Enabling the Sensor Cull Extension](#enabling-the-sensor-cull-extension)
+ [Using the Sensor Cull Extension](#using-the-sensor-cull-extension)
+ [Actions via REST API](#actions-via-rest-api)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
