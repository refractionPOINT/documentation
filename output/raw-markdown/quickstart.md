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

Quickstart

* 31 Oct 2024
* 4 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Quickstart

* Updated on 31 Oct 2024
* 4 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie is infrastructure to connect sources of security data, automate activity based on what's being observed, and forward data to where you need it. There's no *correct* way to use it - every environment is different.

That said, the majority of LimaCharlie users require basic endpoint detection and response (EDR) capabilities. This guide will cover:

1. Creating a new [**Organization**](/v2/docs/quickstart#creating-an-organization)
2. Deploying a [**Sensor**](/v2/docs/quickstart#deploying-a-sensor) to the Organization
3. Adding [**Sigma rules**](/v2/docs/quickstart#adding-sigma-rules) to detect suspicious activity
4. Forwarding detections to an external destination as an [**Output**](/v2/docs/quickstart#output)

All of this can be done within our free tier, which offers full platform functionality for up to two (2) sensors. If you haven't already signed up for a free account, please do so at [app.limacharlie.io](https://app.limacharlie.io).

Let's get started!

## Creating an Organization

LimaCharlie organizations are isolated tenants in the cloud, conceptually equivalent to "projects". They can be configured to suit the needs of each deployment.

After accepting the initial Terms of Service, you'll be offered a prompt to create an organization in a selected `Region` with a globally unique `Name`.

Region Selection

The region that you select for an organization is permanent. Please also consider regulatory requirements for you and/or your customers' data.

Once the organization is created, you'll be forwarded to our initial dashboard and Sensor list, which will be empty and ready for the next step.

## Deploying a Sensor

From the Sensors page in your new organization, click `Add Sensor` to open the setup flow for new sensors. Generally speaking, Sensors are executables that install on hosts and connect them to the LimaCharlie cloud to send telemetry, receive commands, and other capabilities.

Sensors Overview

For a full overview of types of sensors and their capabilities, check out [Sensors](/v2/docs/sensors).

The setup flow should make this process straightforward. For example's sake, let's say we're installing a sensor on a Windows 10 (64 bit) machine we have in front of us.

* Choose the Windows sensor type
* Create an Installation Key - this registers the executable to communicate securely with your organization
* Choose the `64 bit (.exe)` installer
* Follow the on-screen instructions to execute the installer properly
* See immediate feedback when the sensor registers successfully with the cloud

Potential Issues

Since sensors are executables that talk to the cloud, antivirus software and networking layers may interfere with installation. If you run into an issue, take a look at troubleshooting.

With a Windows sensor connected to the cloud, you should gain a lot of visibility into the endpoint. If we view the new sensor inside the web application, we'll have access to views such as:

* `Timeline`: the viewer for telemetry events being collected from the endpoint
* `Processes`: the list of processes running on the endpoint, their level of network activity, and commands to manipulate processes (i.e. kill / pause / resume process, or view modules)
* `File System`: an explorer for the endpoint's file system, right in the browser
* `Console`: a safe shell-like environment for issuing commands
* `Live Feed`: a running view of the live output of all the sensor's events

With telemetry coming in from the cloud, let's add rules to detect potentially malicious activity.

## Adding Sigma Rules

Writing security rules and automations from scratch is a huge effort. To set an open, baseline standard of coverage, LimaCharlie maintains a `sigma` add-on which can be enabled for free, and is kept up to date with the [openly maintained threat signatures](https://github.com/SigmaHQ/sigma).

Enabling the Sigma add-on will automatically apply rules to your organization to match these threat signatures so we can begin to see Detections on incoming endpoint telemetry.

Writing Detection and Response rules

Writing your own rules is outside the scope of this guide, but we do encourage checking out [Detection & Response](/v2/docs/detection-and-response) when you're finished.

## Output

Security data generated from sensors is yours to do with as you wish. For example's sake, let's say we want to forward detections to an [Amazon S3 bucket](https://aws.amazon.com/s3/) for longer-lived storage of detections.

From the Outputs page in your organization, click `Add Output` to open the setup flow for new outputs. Again, the setup flow should make this process straightforward.

* Choose the Detections stream
* Choose the Amazon S3 destination
* Configure the Output and ensure it connects securely to the correct bucket:

  + Output Name
  + Bucket Name
  + Key ID
  + Secret Key
  + Region
* Optionally, you can view samples of the detection stream's data (assuming recent detections have occurred)

With this output in place you can extend the life of your detections beyond the 1 year LimaCharlie retains them, and stage them for any tool that can pull from S3.

Endpoint Detection & Response

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

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
* [Sigma Rules](/docs/sigma-rules)

---

###### What's Next

* [LimaCharlie Core Concepts](/docs/limacharlie-core-concepts)

Table of contents

+ [Creating an Organization](#creating-an-organization)
+ [Deploying a Sensor](#deploying-a-sensor)
+ [Adding Sigma Rules](#adding-sigma-rules)
+ [Output](#output)
