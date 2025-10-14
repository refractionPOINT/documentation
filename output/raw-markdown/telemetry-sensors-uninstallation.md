[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v1

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Telemetry](telemetry-sensors)
* [Detection and Response](detecting-related-events)
* [Platform Management](platform-configuration-limacharlie-sdk)
* [Outputs](output-whitelisting)
* [Add-Ons](developer-grant-program)
* [FAQ](faq-privacy)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Sensor Uninstallation

* 07 Feb 2024
* 2 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# Sensor Uninstallation

* Updated on 07 Feb 2024
* 2 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

There are multiple options available to uninstall the LimaCharlie sensor, depending on the operating system and/or method of installation. macOS and Windows systems allow for easy uninstallation via sensor commands or D&R rules. Linux systems may require additional steps, as detailed below.

## macOS and Windows

When uninstalling macOS and Windows Sensors, please attempt to utilize a method similar to sensor deployment. For example, if sensors were deployed via a package manager, then the same package manager may have uninstall options as well. This will help keep software inventories up to date.

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
C:\Windows\System32\rphcp.exe -c       # If this throws an error about the service, it's safe to ignore
del C:\Windows\System32\rphcp.exe
```

#### macOS

Manual installation of macOS Sensors is detailed [here](/v1/docs/macos-sensor-installation-latest-os-versions#uninstallation-flow).

### Sensor Commands

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. More information on that can be found [here](/v1/docs/sensor-commands-management#uninstall).

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

As an alternative approach, you can also use a Detection & Response (D&R) rule to automatically trigger an uninstall of the LimaCharlie sensor when a sensor connects to the LimaCharlie cloud. Below is an example of the rule you can use for this purpose. This example is specific to Windows-based endpoints, but can be modified based on your needs:

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

### Package Management Tools

For Package Management tools, and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than installing from LimaCharlie. This will help keep software inventories up to date.

## Linux

Linux Sensor uninstallation depends on how the sensor was installed. For example, if installed via a Debian package (`dpkg` file), you should uninstall via the same mechanism. If you installed via the SystemV installation method, please utilize the bottom of [this script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh#L97).

### Sensor Command

The `uninstall` command does not work for Linux systems. However, there is a chained command that can be run from the Sensor Console:

```
 run --shell-command "service limacharlie stop; rm /bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp ; rm /etc/hcp_conf; rm /etc/hcp_hbs"
```

The above command removes LimaCharlie and associated files from the system when run remotely. Note that the above command could also be coupled with a D&R rule for automated sensor uninstallation, if necessary.

### Debian Systems

If the sensor was originally installed with the .deb file, this option is the cleanest uninstall method.

```
apt remove limacharlie
```

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

###### What's Next

* [Sysmon Comparison](/v1/docs/telemetry-sensors-sysmon-comparison)

Table of contents

+ [macOS and Windows](#macos-and-windows)
+ [Linux](#linux)
