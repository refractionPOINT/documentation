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

macOS Agent Installation

* 01 Nov 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# macOS Agent Installation

* Updated on 01 Nov 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie's Mac Sensor interfaces with the kernel to acquire deep visibility into the host's activity while taking measures to preserve the host's performance. The Mac sensor currently supports all versions of MacOS 10.7 and up.

## Installation Instructions

Executing the installer via the command line, pass the `-i INSTALLATION_KEY` argument where `INSTALLATION_KEY` is the key mentioned above.

* [Step-by-step instructions for macOS 10.15 (Catalina) and newer](/v2/docs/macos-agent-installation-latest-os-versions)
* [Step-by-step instructions for macOS 10.14 (Mojave) and older](/v2/docs/macos-agent-installation-older-versions)

You may also pass the value `-` instead of the `INSTALLATION_KEY` like: `-i -`. This will make the installer look for the Installation Key in an alternate place in the following order:

* Environment variable `LC_INSTALLATION_KEY`
* Text file in current working directory: `lc_installation_key.txt`

Looking for alternative installation methods?

* macOS Agent Installation - [MDM Configuration profiles](/v2/docs/macos-agent-installation-mdm-configuration-profiles)

## Uninstalling the Agent

For additional agent uninstall options, see [Endpoint Agent Uninstallation](/v2/docs/endpoint-agent-uninstallation)

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

* [macOS Agent Installation - MDM Configuration Profiles](/docs/macos-agent-installation-mdm-configuration-profiles)
* [macOS Agent Installation - Older Versions (macOS 10.14 and prior)](/docs/macos-agent-installation-older-versions)
* [macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)](/docs/macos-agent-installation-latest-os-versions)
* [Ingesting MacOS Unified Logs](/docs/ingesting-macos-unified-logs)
* [macOS Agent Installation via Jamf Now](/docs/installing-macos-agents-via-jamf-now)
* [Mac Unified Logging](/docs/adapter-types-mac-unified-logging)
* [Endpoint Agent Events Overview](/docs/endpoint-agent-events-overview)

---

###### What's Next

* [macOS Agent Installation - Latest Versions (macOS 15 Sequoia and newer)](/docs/clone-macos-agent-installation-latest-versions-macos-15-sequoia-and-newer)

Table of contents

+ [Installation Instructions](#installation-instructions)
+ [Uninstalling the Agent](#uninstalling-the-agent)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [macos](/docs/en/tags/macos)
* [sensors](/docs/en/tags/sensors)
