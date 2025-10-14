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

Endpoint Agent Uninstallation

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Endpoint Agent Uninstallation

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

There are multiple options available to uninstall the LimaCharlie Sensor, depending on the operating system and/or method of installation. macOS and Windows systems allow for easy uninstallation via sensor commands or  rules. Linux systems may require additional steps, as detailed below.

## Manually Uninstalling the Endpoint Agent

When uninstalling macOS and Windows Sensors, please attempt to utilize a method similar to sensor deployment. For example, if sensors were deployed via a package manager, then the same package manager may have uninstall options as well. This will help keep software inventories up to date.

Details on manual uninstallation is found at the bottom of each respective OS' installation procedures.

## Uninstalling Endpoint Agents from the Platform

### Sensor Commands

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. More information on that can be found [here](/v2/docs/endpoint-agent-commands#uninstall).

On Windows, the command defaults to uninstalling the sensor as if installed from the direct installer exe. If an MSI was used for installation, you can add a `--msi` flag to the `uninstall` command to trigger an uninstallation that is compatible with MSI.

### SDK

To run the uninstall command against *all* Sensors, a simple loop with the SDK in Python would work:

```
import limacharlie
lc = limacharlie.Manager()
for sensor in lc.sensors():
  sensor.task( 'uninstall' )
```

### Using a D&R Rule

As an alternative approach, you can also use a Detection & Response (D&R) rule to automatically trigger an uninstall of the LimaCharlie sensor when a sensor connects to the LimaCharlie cloud.  Below is an example of the rule you can use for this purpose. This example is specific to Windows-based endpoints, but can be modified based on your needs:

```
# Detect
event: SYNC
op: is windows

# Respond
- action: task
  command: uninstall --is-confirmed
- action: add tag
  tag: uninstalled
```

## Package Management Tools

For Package Management tools, and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than installing from LimaCharlie. This will help keep software inventories up to date.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

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

* [Endpoint Agent](/docs/endpoint-agent)
* [Docker Agent Installation](/docs/docker-agent-installation)
* [macOS Agent Installation](/docs/macos-agent-installation)
* [Endpoint Agent Events Overview](/docs/endpoint-agent-events-overview)
* [Chrome Agent Installation](/docs/chrome-agent-installation)
* [Windows Agent Installation](/docs/windows-agent-installation)
* [macOS Agent Installation via Jamf Now](/docs/installing-macos-agents-via-jamf-now)
* [Linux Agent Installation](/docs/linux-agent-installation)
* [Endpoint Agent Installation](/docs/endpoint-agent-installation)
* [Edge Agent Installation](/docs/edge-agent-installation)
* [macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)](/docs/macos-agent-installation-latest-os-versions)
* [macOS Agent Installation - Older Versions (macOS 10.14 and prior)](/docs/macos-agent-installation-older-versions)

---

###### What's Next

* [Endpoint Agent Versioning and Upgrades](/docs/endpoint-agent-versioning-and-upgrades)

Table of contents

+ [Manually Uninstalling the {{glossary.Endpoint Agent}}](#manually-uninstalling-the-{{glossary-endpoint-agent}})
+ [Uninstalling Endpoint Agents from the Platform](#uninstalling-endpoint-agents-from-the-platform)
+ [Package Management Tools](#package-management-tools)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [linux](/docs/en/tags/linux)
* [macos](/docs/en/tags/macos)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
