# Endpoint Agent Installation

The Endpoint Agent is signed, and the same for everyone. The endpoint agent's customization, which indicates the owner, is done at installation based on the installation key used. The Installation Key specifies where the Sensor should connect to enroll, as well as the encryption key used to start the enrollment process.

> **Enterprise-wide deployment**: Looking to deploy many endpoint agents at once? Check out Enterprise Sensor Deployment.

Installing the endpoint agent does not require a reboot.

## Installing the Endpoint Agent

The sensors are designed to be simple to use and re-package for any deployment methodology you use in your Organization.

The sensor requires administrative privileges to install. On Windows this means an Administrator or System account, on macOS and Linux it means the root account.

Before installing, you will need the installation key you want to use.

For OS-specific installation instructions, choose your OS in the nav bar on the left.

## Required Permissions

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

> **Note**: The sensors require these elevated privileges for legitimate security monitoring including process detection, file system monitoring, network analysis, and kernel-level telemetry collection.

## Downloading the Agents

To download the single installers relevant for your deployment, access the `/download/[platform]/[architecture]` control plane. The `platform` component is one of `win`, `linux` or `osx` while the `architecture` component is either `32` or `64`.

For example:

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

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.