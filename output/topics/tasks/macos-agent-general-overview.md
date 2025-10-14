# macOS Agent Installation

LimaCharlie's Mac Sensor interfaces with the kernel to acquire deep visibility into the host's activity while taking measures to preserve the host's performance. The Mac sensor currently supports all versions of MacOS 10.7 and up.

## Installation Instructions

Executing the installer via the command line, pass the `-i INSTALLATION_KEY` argument where `INSTALLATION_KEY` is the key mentioned above.

* [Step-by-step instructions for macOS 10.15 (Catalina) and newer](/v2/docs/macos-agent-installation-latest-os-versions)
* [Step-by-step instructions for macOS 10.14 (Mojave) and older](/v2/docs/macos-agent-installation-older-versions)

You may also pass the value `-` instead of the `INSTALLATION_KEY` like: `-i -`. This will make the installer look for the Installation Key in an alternate place in the following order:

* Environment variable `LC_INSTALLATION_KEY`
* Text file in current working directory: `lc_installation_key.txt`

### Looking for alternative installation methods?

* macOS Agent Installation - [MDM Configuration profiles](/v2/docs/macos-agent-installation-mdm-configuration-profiles)

## Uninstalling the Agent

For additional agent uninstall options, see [Endpoint Agent Uninstallation](endpoint-agent-uninstallation.md)

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.