# Sensors

Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Once installed, they send telemetry and artifacts from a host to their registered organization. The sensor is grounded in LimaCharlie's open source EDR roots, but is flexible in bringing security data in from different sources.

## Sensor Types

* [Windows](/v1/docs/windows)
* [Mac](/v1/docs/sensors-operating-systems-macos)
* [Linux](/v1/docs/linux)
* [Chrome](/v1/docs/chrome)
* [Edge](/v1/docs/sensors-operating-systems-edge)

> **Note**: Don't see what you're looking for? Need support for a platform you don't see here? Get in touch via [Slack](https://slack.limacharlie.io) or email.

## Quota

All sensors register with the cloud, and many of them may go online / offline over the course of a regular day. For billing purposes, organizations must specify a sensor quota which represents the number of **concurrent online sensors** allowed to be connected to the cloud.

If the quota is maxed out when a sensor attempts to come online, the sensor will be dismissed and a [`sensor_over_quota`](/v1/docs/reference-events-deployment) event will be emitted in the deployments stream.

## Events

All sensors observe host & network activity, packaging telemetry and sending it to the cloud. The types of observable events are dependent on the sensor's type.

> For an introduction to events and their structure, check out [Events](/v1/docs/reference-events).

## Commands

Windows, Mac, Linux, Chrome, and Edge sensors all offer commands as a safe way of interacting with a host for investigation, management, or threat mitigation purposes.

> For an introduction to commands and their usage, check out [Sensor Commands](/v1/docs/sensors-sensor-commands). Alternatively, check out any the sensor types individually to see their supported commands.

## Installation Keys

An Installation Key binds a sensor to the Organization that generated the key, optionally tagging them as well to differentiate groups of sensors from one another.

It has the following properties:

* OID: The Organization Id that this key should enroll into.
* IID: Installer ID that is generated and associated with every Installation Key.
* Tags: A list of Tags automatically applied to sensors enrolling with the key.
* Desc: The description used to help you differentiate uses of various keys.

### Recommended Usage

We recommend using multiple installation keys per organization to differentiate endpoints in your deployment.

For example, you may create a key with Tag "server" that you will use to install on your servers, a key with "vip" for executives in your organization, or a key with "sales" for the sales department, etc. This way you can use the tags on various sensors to figure out different detection and response rules for different types of hosts on your infrastructure.

## Sensor Versions

Windows, Mac, and Linux (EDR-class) sensors' versions are fixed and can be managed per-organization. They will not upgrade unless you choose to do so.

There are always two versions available to roll out — `Stable` or `Latest` — which can be deployed via the web application or via the [`/modules` REST API](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI2OA-update-sensors).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.