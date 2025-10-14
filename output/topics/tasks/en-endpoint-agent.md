# Endpoint Agent Installation and Uninstallation

The Endpoint Agent is a signed, universal binary that connects endpoints to the LimaCharlie platform. Customization occurs at installation time using an Installation Key, which specifies the enrollment endpoint and encryption key. The agent does not require a reboot after installation.

> **Enterprise-wide deployment**: Looking to deploy many endpoint agents at once? Check out Enterprise Sensor Deployment.

## Overview

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more. They send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs, offering a scalable, serverless solution for securely connecting endpoints to the cloud.

Installation keys are Base64-encoded strings that associate Sensors and Adapters with the correct Organization. They are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations.

## Installing the Endpoint Agent

The sensors are designed to be simple to use and re-package for any deployment methodology you use in your Organization. Administrative privileges are required for installation.

Before installing, you will need the installation key you want to use. For OS-specific installation instructions, choose your OS in the nav bar on the left.

### Required Permissions

**Windows**

* Administrative privileges - Must run as LocalSystem service
* SeDebugPrivilege - Debug programs privilege
* SeBackupPrivilege - Back up files and directories privilege
* SeRestorePrivilege - Restore files and directories privilege

**Linux**

* Root privileges (UID 0) - Required for system monitoring
* RLIMIT_MEMLOCK set to RLIM_INFINITY - For eBPF program loading
* Mount capabilities - For filesystem mounting
* CAP_BPF or CAP_SYS_ADMIN - For eBPF kernel module operation
* CAP_NET_ADMIN - For network monitoring

**macOS**

* Root privileges (UID 0) - Required for system monitoring
* Kernel extension entitlements - Including com.apple.security.cs.debugger
* Apple KPI dependencies - bsd, libkern, dsep, mach kernel programming interfaces

**Cross-Platform Requirements**

* File system read/write access to system directories
* Process monitoring capabilities
* Network monitoring and outbound HTTPS access
* Registry access (Windows) for system configuration

> Note: The sensors require these elevated privileges for legitimate security monitoring including process detection, file system monitoring, network analysis, and kernel-level telemetry collection.

### Downloading the Agents

To download the single installers relevant for your deployment, access the `/download/[platform]/[architecture]` control plane. The `platform` component is one of `win`, `linux` or `osx` while the `architecture` component is either `32` or `64`.

**Download URLs:**

* <https://downloads.limacharlie.io/sensor/windows/32> for the Windows 32 bit executable installer
* <https://downloads.limacharlie.io/sensor/windows/64> for the Windows 64 bit executable installer
* <https://downloads.limacharlie.io/sensor/windows/msi32> for the Windows 32 bit MSI installer
* <https://downloads.limacharlie.io/sensor/windows/msi64> for the Windows 64 bit MSI installer
* <https://downloads.limacharlie.io/sensor/linux/64> for the Linux 64 bit installer
* <https://downloads.limacharlie.io/sensor/linux/alpine64> for the Linux Alpine 64 bit installer
* <https://downloads.limacharlie.io/sensor/linux/deb32> for the Linux 32 bit Debian package
* <https://downloads.limacharlie.io/sensor/linux/deb64> for the Linux 64 bit Debian package
* <https://downloads.limacharlie.io/sensor/linux/debarm64> for the Linux ARM 64 bit Debian package
* <https://downloads.limacharlie.io/sensor/mac/64> for the macOS 64 bit installer
* <https://downloads.limacharlie.io/sensor/mac/arm64> for the macOS ARM 64 bit (Apple Silicon) installer
* <https://downloads.limacharlie.io/sensor/chrome> for the Chrome extension
* <https://downloads.limacharlie.io/sensor/edge> for the MS Edge extension

## Uninstalling the Endpoint Agent

There are multiple options available to uninstall the LimaCharlie Sensor, depending on the operating system and/or method of installation. macOS and Windows systems allow for easy uninstallation via sensor commands or rules. Linux systems may require additional steps.

### Manual Uninstallation

When uninstalling macOS and Windows Sensors, utilize a method similar to sensor deployment. For example, if sensors were deployed via a package manager, then the same package manager may have uninstall options as well. This will help keep software inventories up to date.

Details on manual uninstallation is found at the bottom of each respective OS' installation procedures.

### Uninstalling from the Platform

**Sensor Commands**

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. More information on that can be found [here](/v2/docs/endpoint-agent-commands#uninstall).

On Windows, the command defaults to uninstalling the sensor as if installed from the direct installer exe. If an MSI was used for installation, you can add a `--msi` flag to the `uninstall` command to trigger an uninstallation that is compatible with MSI.

**SDK**

To run the uninstall command against *all* Sensors, a simple loop with the SDK in Python:

```python
import limacharlie
lc = limacharlie.Manager()
for sensor in lc.sensors():
  sensor.task( 'uninstall' )
```

**Using a D&R Rule**

You can use a Detection & Response (D&R) rule to automatically trigger an uninstall of the LimaCharlie sensor when a sensor connects to the LimaCharlie cloud. Below is an example rule for Windows-based endpoints (can be modified based on your needs):

```yaml
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

For Package Management tools and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than uninstalling from LimaCharlie. This will help keep software inventories up to date.