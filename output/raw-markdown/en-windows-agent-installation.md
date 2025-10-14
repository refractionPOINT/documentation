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

Windows Agent Installation

* 05 Oct 2024
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Windows Agent Installation

* Updated on 05 Oct 2024
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Windows Agent Installation Instructions

Windows MSI Installation Versioning

Our MSI packages are created programmatically, and thus will have a version of `1.0.0.0` upon compilation and download. Note Sensor versions will reflect the latest version as of the MSI download, and sensor version control is managed via the LimaCharlie application, not the MSI package.

### System Requirements

The LimaCharlie.io agent supports Windows XP 32 bit and up (32 and 64 bit). However, Windows XP and 2003 support is for the more limited capabilities of the agent that do not require kernel support.

### Installing via MSI

[Windows Installer](https://learn.microsoft.com/en-us/windows/win32/msi/windows-installer-portal) is an installation and configuration service provided with Windows. Microsoft Software Installer, or MSI, files allow for an easy and portable installation format on Windows systems.

LimaCharlie makes portable MSI files available with each new sensor release. They are available at a static URL for easy downloading:

* [32-bit MSI installer](https://downloads.limacharlie.io/sensor/windows/msi32)
* [64-bit MSI installer](https://downloads.limacharlie.io/sensor/windows/msi64)

Similar to executable installation, when installing with an MSI, you will need to provide the desired Installation Key, passed through as the `InstallationKey` variable.

**32-bit MSI installation command:**

`hcp_win_x86_release_<sensor_version>.msi InstallationKey=<installation_key>`

**64-bit MSI installation command:**

`hcp_win_x64_release_<sensor_version>.msi InstallationKey=<installation_key>`

Executing the installer via the command line, pass the `-i INSTALLATION_KEY` argument where `INSTALLATION_KEY` is the key mentioned above. This will install the sensor as a Windows service and trigger its enrollment.

You may also install the Windows sensor using the MSI version. With the MSI, install using:

```
installer.msi InstallationKey="INSTALLATION_KEY"
```

You may also pass the value `-` instead of the `INSTALLATION_KEY` like: `-i -`. This will make the installer look for the installation key in an alternate place in the following order:

* Environment variable `LC_INSTALLATION_KEY`
* Text file in current working directory: `lc_installation_key.txt`

#### Verify the service is running

In an administrative command prompt issue the command `sc query rphcpsvc` and confirm the `STATE` displayed is `RUNNING`.

## Uninstalling the Agent

For additional agent uninstall options, see [Endpoint Agent Uninstallation](/v2/docs/endpoint-agent-uninstallation)

### Manual Uninstallation

#### Windows EXE

On Windows, the LimaCharlie sensor can be uninstalled on individual endpoints by running the installer EXE with the `-c` argument, which will remove the Sensor and its service entirely.

Example:

```
C:\Windows\System32\rphcp.exe -c
del C:\Windows\System32\rphcp.exe
```

#### Windows MSI

If uninstalling via the Windows MSI installer, the `/x` switch can be used to uninstall.

Example:

```
msiexec /x lc_sensor.msi /qn
```

If you run into issues where the service is still present (`sc.exe query rphcpsvc`) or the exe is still left behind (`C:\Windows\System32\rphcp.exe`), you can remove them with the following:

```
C:\Windows\System32\rphcp.exe -c       # If this throws an error about the service, it's safe to ignore
del C:\Windows\System32\rphcp.exe
```

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

* [Endpoint Agent](/docs/endpoint-agent)
* [Endpoint Agent Uninstallation](/docs/endpoint-agent-uninstallation)
* [Building a custom MSI installer for Windows](/docs/building-a-custom-msi-installer-for-windows)

---

###### What's Next

* [Building a custom MSI installer for Windows](/docs/building-a-custom-msi-installer-for-windows)

Table of contents

+ [Windows Agent Installation Instructions](#windows-agent-installation-instructions)
+ [Uninstalling the Agent](#uninstalling-the-agent)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
