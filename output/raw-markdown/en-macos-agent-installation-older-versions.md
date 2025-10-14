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

macOS Agent Installation - Older Versions (macOS 10.14 and prior)

* 10 Dec 2024
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# macOS Agent Installation - Older Versions (macOS 10.14 and prior)

* Updated on 10 Dec 2024
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## macOS Sensor (macOS 10.14 and prior)

This document provides details of how to install, verify, and uninstall the LimaCharlie sensor on macOS (versions 10.14 and prior).  We also offer [documentation for macOS 10.15 and newer](/v2/docs/macos-agent-installation-latest-os-versions).

### Installer Options

When running the installer from the command line, you can pass the following arguments:

```
-v: display build version.
-q: quiet; do not display banner.
-d <INSTALLATION_KEY>: the installation key to use to enroll, no permanent installation.
-i <INSTALLATION_KEY>: install executable as a service with deployment key.
-r: uninstall executable as a service.
-c: uninstall executable as a service and delete identity files.
-w: executable is running as a macOS service.
-h: displays the list of accepted arguments.
```

### Installation Flow

1. Download the [Sensor installer file](https://downloads.limacharlie.io/sensor/mac/64)
2. Add execute permission to the installer file via the command line

> chmod +x hcp\_osx\_x64\_release\_4.23.0

3. Run the installer via the command line.  You'll pass the argument -i and your Installation Key.

> sudo ./hcp\_osx\_x64\_release\_4.23.0 -i YOUR\_INSTALLATION\_KEY\_GOES\_HERE

![Basic installation](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/01-Basic_installation.png)

You can obtain the installation key from the Installation Keys section of the LimaCharlie web application.  [More information about installation keys](https://doc.limacharlie.io/docs/documentation/docs/manage_keys.md).

The sensor will be installed as a launchctl service.  Installation will trigger the sensors enrollment with the LimaCharlie cloud.

![Installation success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/02-Installation_success.png)

4. You will be prompted to grant permissions for system extensions to be installed.

![Permissions required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/03_Older_Systems-System_Extension_Notice.png)

5. Click the "Open System Preferences" button
6. Unlock the preference pane using the padlock in the bottom left corner, then click the Allow button next to `System software from developer "Refraction Point, Inc" was blocked from loading.`

![Unlocked](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/04-Older_Systems-System_Software_Approval.png)

The installation is now complete and you should see a message indicating that the installation was successful.

## Verifying Installation

To verify that the sensor was installed successfully, you can log into the LimaCharlie web application and see if the device has appeared in the Sensors section.  Additionally, you can check the following on the device itself:

**Ensure the process is running**

In a Terminal, run the command:

> sudo launchctl list | grep com.refractionpoint.rphcp

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/Installed_correctly.png)

If the agent is running, this command should return a record as shown above.

**Ensure the Kernel Extension is loaded**

You can confirm that the kernel extension is loaded by running the command:

> kextstat | grep com.refractionpoint.

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/verifying-extension.png)

If the extension is loaded, this command should return a record as shown above.

### A note on permissions

Apple has purposely made installing extensions (like the ones used by LimaCharlie) a process that requires several clicks on macOS.  The net effect of this is that the first time the sensor is installed on a macOS system, permissions will need to be granted via System Preferences

Currently, the only way to automate the installation is to use an Apple-approved MDM solution. These solutions are often used by large organizations to manage their Mac fleet. If you are using such a solution, see your vendor's documentation on how to add extensions to the allow list which can be applied to your entire fleet.

We're aware this is an inconvenience and hope Apple will provide better solutions for security vendors in future.

## Uninstallation Flow

To uninstall the sensor:

1. Run the installer via the command line.

You'll pass the argument -c

> sudo ./hcp\_osx\_x64\_release\_4.23.0 -c

![Uninstall progress](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/Installed_correctly.png)

2. You should see a message indicating that the uninstallation was successful.

![Uninstall success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/3-Uninstall_Success.png)

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

* [macOS Agent Installation](/docs/macos-agent-installation)
* [macOS Agent Installation - MDM Configuration Profiles](/docs/macos-agent-installation-mdm-configuration-profiles)
* [macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)](/docs/macos-agent-installation-latest-os-versions)
* [Ingesting MacOS Unified Logs](/docs/ingesting-macos-unified-logs)
* [macOS Agent Installation via Jamf Now](/docs/installing-macos-agents-via-jamf-now)
* [Mac Unified Logging](/docs/adapter-types-mac-unified-logging)

---

###### What's Next

* [macOS Agent Installation - MDM Configuration Profiles](/docs/macos-agent-installation-mdm-configuration-profiles)

Table of contents

+ [macOS {{glossary.Sensor}} (macOS 10.14 and prior)](#macos-{{glossary-sensor}}-macos-10-14-and-prior-)
+ [Verifying Installation](#verifying-installation)
+ [Uninstallation Flow](#uninstallation-flow)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [macos](/docs/en/tags/macos)
* [sensors](/docs/en/tags/sensors)
