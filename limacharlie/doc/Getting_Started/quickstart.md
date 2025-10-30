# Quickstart

LimaCharlie is infrastructure to connect sources of security data, automate activity based on what's being observed, and forward data to where you need it. There's no *correct* way to use it - every environment is different.

That said, the majority of LimaCharlie users require basic endpoint detection and response (EDR) capabilities. This guide will cover:

1. Creating a new [Organization](#creating-an-organization)
2. Deploying a [Sensor](#deploying-a-sensor) to the Organization
3. Adding [Sigma rules](#adding-sigma-rules) to detect suspicious activity
4. Forwarding detections to an external destination as an [Output](#output)

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

For a full overview of types of sensors and their capabilities, check out Sensors.

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

Writing your own rules is outside the scope of this guide, but we do encourage checking out [Detection & Response](../Detection_and_Response/writing-and-testing-rules.md) when you're finished.

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
