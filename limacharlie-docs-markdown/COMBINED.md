# LimaCharlie Complete Documentation

---

# Getting Started

# Quickstart
LimaCharlie is infrastructure to connect sources of security data, automate activity based on what's being observed, and forward data to where you need it. There's no *correct* way to use it - every environment is different.

That said, the majority of LimaCharlie users require basic endpoint detection and response (EDR) capabilities. This guide will cover:

1. Creating a new [**Organization**](/v2/docs/quickstart#creating-an-organization)
2. Deploying a [**Sensor**](/v2/docs/quickstart#deploying-a-sensor) to the Organization
3. Adding [**Sigma rules**](/v2/docs/quickstart#adding-sigma-rules) to detect suspicious activity
4. Forwarding detections to an external destination as an [**Output**](/v2/docs/quickstart#output)

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

For a full overview of types of sensors and their capabilities, check out [Sensors](/v2/docs/sensors).

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

Writing your own rules is outside the scope of this guide, but we do encourage checking out [Detection & Response](/v2/docs/detection-and-response) when you're finished.

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

Endpoint Detection & Response

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

---

# Use Cases
LimaCharlie's vast array of capabilities can be applied to countless scenarios.

The following table contains some common use cases driving the adoption of the SecOps Cloud Platform among our customer base.

| Common LimaCharlie Use Cases | | |
| --- | --- | --- |
| [Security Service Providers (MSSP, MSP, MDR)](/v2/docs/service-providers-mssp-msp-mdr) | [Enterprise SOC](/v2/docs/enerprises) | [Building Products](/v2/docs/building-products) |
| [Threat Hunting](/v2/docs/threat-hunting) | [Incident Response](/v2/docs/incident-response) | [SOAR / Automation](/v2/docs/soar-automation) |
| [Cost Effective SIEM Alternative](/v2/docs/cost-effective-siem) | [Network Monitoring](/v2/docs/network-monitoring) | [Cloud Security](/v2/docs/cloud-security) |
| [Observability Pipeline](/v2/docs/observability-pipeline) | [Endpoint Detection and Response (EDR)](/v2/docs/endpoint-detection-and-response-edr) | [Build CTI Capabilties](/v2/docs/build-cti-capabilities) |
| [File and Registry Integrity Monitoring (FIM)](/v2/docs/file-and-registry-integrity-monitoring-fim-deployments) | [Uncovering Adversary Techniques](/v2/docs/uncovering-adversary-techniques) | [WEL Monitoring](/v2/docs/wel-monitoring) |
| [SecOps Development](/v2/docs/secops-development) | [Purple Teaming](/v2/docs/purple-teaming) | [Security Monitoring for DevOps](/v2/docs/security-monitoring-for-devops) |
| [M&A Cyber Due Dilligence](/v2/docs/ma-cyber-due-diligence) | [Table Top Exercises](/v2/docs/table-top-exercises) | [ChromeOS Support](/v2/docs/chromeos-support) |
|  | [Sleeper Mode](/v2/docs/sleeper-mode) |  |

The SCP is under continuous development which includes the regular addition of expanded features and capabilities. Newer features such as our Endpoint protection ([EPP](/v2/docs/ext-epp)) and our [MCP server](/v2/docs/mcp-server) are not yet included in the use case table, but make strong cases for adopting LimaCharlie in their own right.

---

# What is LimaCharlie?
LimaCharlie is the **SecOps Cloud Platform** - delivering security operations for the modern era.

LimaCharlie’s SecOps Cloud Platform provides you with comprehensive enterprise protection that brings together critical cybersecurity capabilities and eliminates integration challenges and security gaps for more effective protection against today’s threats.

The SecOps Cloud Platform offers a unified platform where you can build customized solutions effortlessly. With open APIs, centralized telemetry, and automated detection and response mechanisms, it’s time cybersecurity moves into the modern era.

Simplifying procurement, deployment and integration of best-of-breed cybersecurity solutions, the SecOps Cloud Platform delivers complete protection tailored to each organization’s specific needs, much in the same way IT Clouds have supported enterprises for years.

Our documentation can walk you through setting up your own Organization, deploying Sensors, writing detection and response rules, or outputting your data to any destination of your choosing. To dive in immediately, see our [Quickstart](/v2/docs/quickstart) guide.

Dig in, and build the security program you need and have always wanted.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Sensors

# Chrome Agent Installation
LimaCharlie's Chrome Sensor is built as a browser extension and provides visibility for activity performed within the browser. This sensor is particularly useful for gaining affordable network visibility in organizations that make heavy use of ChromeOS.

It is delivered as the [LimaCharlie Sensor](https://chrome.google.com/webstore/detail/limacharlie-sensor/ljdgkaegafdgakkjekimaehhneieecki) extension available in the Chrome Web Store.

## Installation Instructions

The Chrome sensor is available in the Chrome Web Store.

1. In the LimaCharlie web app (app.limacharlie.io), go to the "Installation Keys" section, select your Installation Key and click the "Chrome Key" copy icon to
    copy the key to your clipboard.
2. Install the sensor from: <https://downloads.limacharlie.io/sensor/chrome>
3. A new tab will open where you can add your installation key from before. If you close it by mistake, you can re-open it by:

   1. From the Extensions page at chrome://extensions/ click on the "Details" button of the LimaCharlie Sensor extension.
   2. Go to the "Extension options" section, and enter your installation key from the previous step. Click save.

The installation key can also be pre-configured through the Managed Storage feature (key named `installation_key`) if you are using a managed Chrome deployment.

## Troubleshooting the Chrome Sensor

If the Chrome extension is giving connectivity issues, the following may help.

First, try uninstalling/re-installing the extension.

If the extension continues to fail to connect, please provide the LimaCharlie support team with the following details:

1. Open a new browser tab
2. Go to `chrome://extensions/`
3. Ensure "Developer Mode" is enabled (see toggle in the top right)

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2838%29.png)

4. Click the `background.html` link in the LimaCharlie Sensor entry.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2839%29.png)

5. In the window that opens, click Console and provide us with a screenshot of what appears for analysis.

Please also include your Organization ID, which can be found within the LimaCharlie web interface in the REST API section under `OID`.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

---

# Endpoint Agent Uninstallation
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

# FAQ - Sensor Installation
## How can I add LimaCharlie traffic to an allow list?

The tables below show the hostnames and IPs used to connect to LimaCharlie. All connections use TCP port 443 and TLS 1.2+

## What Hostnames and IPs does LimaCharlie use for each region?

### Canada (Quebec)

| Hostname | IP | Use |
| --- | --- | --- |
| aae67d7e76570ec1.lc.limacharlie.io | 35.203.33.203 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| aae67d7e76570ec1.edr.limacharlie.io | 35.201.82.57 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| aae67d7e76570ec1.wss.limacharlie.io | 35.201.96.199 | Chrome, Edge and Adapters |
| aae67d7e76570ec1.ingest.limacharlie.io | 34.149.216.238 | Logs and Artifacts |
| aae67d7e76570ec1.replay.limacharlie.io | 142.250.115.121 | Replay |
| aae67d7e76570ec1.live.limacharlie.io | 34.120.175.14 | Live feed |
| aae67d7e76570ec1.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### US (Iowa)

| Hostname | IP | Use |
| --- | --- | --- |
| 9157798c50af372c.lc.limacharlie.io | 35.194.62.236 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 9157798c50af372c.edr.limacharlie.io | 34.149.165.165 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 9157798c50af372c.wss.limacharlie.io | 34.102.223.182 | Chrome, Edge and Adapters |
| 9157798c50af372c.ingest.limacharlie.io | 34.120.157.194 | Logs and Artifacts |
| 9157798c50af372c.replay.limacharlie.io | 142.250.115.121 | Replay |
| 9157798c50af372c.live.limacharlie.io | 34.120.123.4 | Live feed |
| 9157798c50af372c.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### India (Mumbai)

| Hostname | IP | Use |
| --- | --- | --- |
| 4d897015b0815621.lc.limacharlie.io | 35.200.151.24 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 4d897015b0815621.edr.limacharlie.io | 34.102.207.18 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 4d897015b0815621.wss.limacharlie.io | 34.98.108.101 | Chrome, Edge and Adapters |
| 4d897015b0815621.ingest.limacharlie.io | 34.149.161.19 | Logs and Artifacts |
| 4d897015b0815621.replay.limacharlie.io | 142.250.115.121 | Replay |
| 4d897015b0815621.live.limacharlie.io | 35.244.221.119 | Live feed |
| 4d897015b0815621.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### UK (London)

| Hostname | IP | Use |
| --- | --- | --- |
| 70182cf634c346bd.lc.limacharlie.io | 35.242.152.114 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 70182cf634c346bd.edr.limacharlie.io | 34.107.134.233 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 70182cf634c346bd.wss.limacharlie.io | 35.244.147.201 | Chrome, Edge and Adapters |
| 70182cf634c346bd.ingest.limacharlie.io | 34.149.56.238 | Logs and Artifacts |
| 70182cf634c346bd.replay.limacharlie.io | 142.250.115.121 | Replay |
| 70182cf634c346bd.live.limacharlie.io | 35.244.146.102 | Live feed |
| 70182cf634c346bd.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Europe (Emshaven)

| Hostname | IP | Use |
| --- | --- | --- |
| b76093c3662d5b4f.lc.limacharlie.io | 35.204.142.125 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| b76093c3662d5b4f.edr.limacharlie.io | 34.111.194.87 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| b76093c3662d5b4f.wss.limacharlie.io | 130.211.22.248 | Chrome, Edge and Adapters |
| b76093c3662d5b4f.ingest.limacharlie.io | 34.120.5.160 | Logs and Artifacts |
| b76093c3662d5b4f.replay.limacharlie.io | 142.250.115.121 | Replay |
| b76093c3662d5b4f.live.limacharlie.io | 34.120.64.23 | Live feed |
| b76093c3662d5b4f.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Australia (Sydney)

| Hostname | IP | Use |
| --- | --- | --- |
| abc32764762fce67.lc.limacharlie.io | 34.151.84.52 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| abc32764762fce67.edr.limacharlie.io | 34.54.253.51 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| abc32764762fce67.wss.limacharlie.io | 34.96.104.54 | Chrome, Edge and Adapters |
| abc32764762fce67.ingest.limacharlie.io | 35.241.63.128 | Logs and Artifacts |
| abc32764762fce67.replay.limacharlie.io | 34.49.249.16 | Replay |
| abc32764762fce67.live.limacharlie.io | 34.8.102.215 | Live feed |
| abc32764762fce67.hook.limacharlie.io | 34.49.185.177 | Webhooks |

## How much data does the LimaCharlie Sensor produce per day?

The amount of data that is produced by the sensor is dependent on how much, and what kind of activity is taking place on the endpoint. That being said, the average data produced per endpoint across thousands of deployments is approximately 1MB per day.

## How much resources does the LimaCharlie agent consume?

The total footprint of the agent on disk combined with what is in memory is approximately 50MB. The agent typically runs under 1% CPU.

Depending on what actions you may be performing it may increase (e.g. if you’re doing a full YARA scan it’s expected that the CPU usage will increase). When you use our YARA trickle scan, that also keeps CPU usage within reasonable bounds. You’ll only see YARA scans spike CPU when you do a full manual scan.

Depending on the configuration of the agent (it’s fully customizable), the network bandwidth will vary, but we typically see aproximately 2MB per day on Windows hosts.

## Why does my sensor initially connect successfully but then disappears?

Sometimes we see the agent connect to the LimaCharlie cloud, enrolls, then disconnects (which is normal the first time after enrollment) and never connects again, or it doesn't show that kernel has been acquired.

This behavior is typical with SSL interception. Sometimes it's a network device, but at other times some security products on the host can do that without being very obvious.

You can confirm if there is SSL interception by performing the following steps to check the SSL fingerprint of the LimaCharlie cloud from the host.

**Confirm the region of your** Organization

If you already know where your organization's region is located, you can move to the next step. To verify the organization's region where the data is processed and stored, click `Add Sensor` from the `Sensors` view. You will then see the region listed under `Sensor Connectivity`.
![Sensor - Region](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Sensor%20-%20Region.png)

**Open the test URL**
Via web browser, navigate to one of the below test URLs that corresponds to the correct region:

[Test URL - US Region](https://9157798c50af372c.lc.limacharlie.io/)
[Test URL - UK Region](https://70182cf634c346bd.lc.limacharlie.io/)
[Test URL - India Region](https://4d897015b0815621.lc.limacharlie.io/)
[Test URL - Europe Region](https://b76093c3662d5b4f.lc.limacharlie.io/)
[Test URL - Canada Region](https://aae67d7e76570ec1.lc.limacharlie.io/)

No website will open; you should get a "Your connection is not private" type of message instead.

**Display the SSL Certificate**

By clicking near the URL bar on the exclamation mark, you will open a small menu and you can click "Certificate status"/"Certificate validity"/"Certificate is not valid" which will display the certificate information.

![certifricate](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certifricate.png)

![certificate-1](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certificate-1.png)

**Confirm the SHA-1 and SHA-256 fingerprints**

The SHA-1 and SHA-256 fingerprints should match the values below that correspond to the region your organization is in.

If the SHA-1 and SHA-256 fingerprints you are seeing do not match what's listed below, that's an indicator of the SSL interception.

| Region | SHA-256 Fingerprint | SHA-1 Fingerprint |
| --- | --- | --- |
| US | 14 44 8C B6 A1 19 A5 BE 18 AE 28 07 E3 D6 BD 55 B8 7A 5E 0C 3F 2D 78 03 6E 7C 6A 2A AA 45 8F 60 | 1A 72 67 08 D0 83 7D A9 62 85 39 55 A1 12 1B 10 B0 F4 56 1A |
| UK | 49 49 B0 41 D6 14 F3 3B 86 BF DF 14 24 F8 BD 2F E1 98 39 41 5A 99 E6 F1 C7 A2 C8 AB 34 0C FE 1D | 2E 49 00 DB F8 3A 2A 88 E0 15 76 D5 C5 4F 8F F3 7D 27 77 DD |
| India | 68 6F 08 3D 53 3F 08 E0 22 EB F6 67 0C 3C 41 08 75 D6 0E 67 03 88 D9 B6 E1 F8 19 6B DA 54 5A A3 | 37 57 DD 4E CF 2B 25 0B CA EA E2 E6 E3 B2 98 48 29 19 F3 6B |
| Europe | EF B3 FA A7 78 AB F0 B0 41 00 CF A3 5F 44 3F 9A 4D 16 28 B9 83 22 85 E3 36 44 D5 DC F9 5C 78 5B | 07 72 B3 31 1A 89 D6 54 1D 71 C3 07 AD B5 8A 26 FD 30 7E 5D |
| Canada | D3 40 8B 59 AE 5A 28 75 D1 65 71 50 52 2E 6F 45 26 EE E8 19 3A 9A 74 39 C1 64 60 B8 6A 92 15 47 | E3 EF AE 6A 0E 7F 18 83 15 FE F2 02 6C F3 2D 4E 59 95 4D 0A |

## What happens if a host is offline?

When the host is offline, the Sensor will keep collecting telemetry and store it locally in a "ring buffer" (which limits the total possible size). The buffer is ~60mb, so the amount of time it will cover will vary based on how much telemetry the individual endpoint generates. e.g. A domain controller will likely be generating many more events than a regular end user workstation.

When the host is back online, the content of this buffer will be flushed to the cloud where [detection and response](/v2/docs/detection-and-response) () rules will apply as usual.

The same ring buffer is used when the Sensor runs normally, even if data is not sent to the cloud in real-time. The cloud can then retroactively request the full or partial content of the ring buffer, bringing your telemetry current.

## How can I tell which Installation Key was used to enroll a sensor?

On occasion you may need to check which installation key was used to enroll a sensor. You can do so by comparing the sensors `Installer ID` with the Installation Key's `Adapter Key` value.

1. Go to the Sensors section and click into the sensor in question to view its details page. Take note of the `Installer ID`.
2. Go to the Install Sensors section.  Click the copy icon under the `Adapter Key`.
3. Compare these two values; the Installer ID on a sensor should be the same as the Adapter Key of the installation key used.

If you need to check a large list of sensors, you can perform an export of all sensors from the main sensors list page, or use the LimaCharlie API.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

# Installation Keys
Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

There are four components of an Installation Key:

* Organization ID **(**OID**)**: The Organization ID that this key should enroll into.
* **Installer ID (IID)**: Installer ID that is generated and associated with every Installation Key.
* **Tags**: A list of Tags automatically applied to sensors enrolling with the key.
* **Description**: The description used to help you differentiate uses of various keys.

## Management

Installation keys can be managed on the **Sensors > Installation Keys** page in the web app.

On this page, under the `Connectivity` section, you will see the various URLs associated with Sensor and Adapter connectivity.

### Pinned Certificates

Typically, Sensors require access over port 443 and use pinned SSL certificates. This is the default deployment option, and does not support traffic interception.

If you need to install sensors without pinned certificates, an installation key must be created with a specific flag. This must be done via the REST API, by setting the `use_public_root_ca` flag to `true`.

More details can be found [here](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Manager.py#L1386).

## Use of Tags

Generally speaking, we use at least one Installation Key per organization. Then we use different keys to help differentiate parts of our infrastructure. For example, you may create a key with Tag "server" that you will use to install on your servers, a key with "vip" for executives in your organization, or a key with "sales" for the sales department, etc. This way you can use the tags on various sensors to figure out different detection and response rules for different types of hosts on your infrastructure.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

# Sensor Tags
Tags in LimaCharlie are simple strings that can be associated with any number of sensors. A Sensor can also have an arbitrary number of tags associated with it.

Tags appear in every event coming from a sensor under the `routing` component of the event. This greatly simplifies the writing of detection and response rules based on the presence of specific tags, at the cost of including more non-unique data per event.
 Tags can be used for a variety of purposes, including:

* to classify endpoints
* automate detection and response
* create powerful workflows
* trigger automations

## Use Cases for Sensor Tags

### Classification

You can use tags to classify an endpoint in a number of different ways based on what is important to you.  Some examples of classifications are shown below for inspiration.

**Departments**

Create tags to classify endpoints based on what business department they belong to.  e.g. sales, finance, operations, development, support, legal, executives.

**Usage Type**

You may wish to tag endpoints based on their type of usage.  e.g. workstation, server, production, staging.

By having endpoints tagged in this manner you can easily identify endpoints and decide what actions you may wish to take while considering the tag.  For example, if you see an endpoint is tagged with `workstation` and `executives`, and you happen to see suspicious activity on the endpoint, it may be worthwhile for you to prioritize response.

### Automating detection and response

You can use tags to automate detection and response.

For example, you can create a detection & response rule so that when a specific user logs in on a device, the box is tagged as `VIP-sales` and the sensor starts collecting an extended list of events from that box.

### Creating workflows

You can use tags to create workflows and automations. For instance, you can configure an output (forwarder) to send all detections containing `VIP-sales` tag to Slack so that you can review them asap, while detections tagged as `sales` can be sent to an email address.

### Trigger Automations

Create a Yara scanning rule so that endpoints tagged as 'sales' are continuously scanned against the specific sets of Yara signatures.

## Adding Tags

Tags can be added to a sensor a few different ways:

1. Enrollment: the installation keys can optionally have a list of Tags that will get applied to sensors that use them.
2. Manually: using the API as described below, either manually by a human or through some other integration.
3. Detection & Response: automated detection and response rules can programatically add a tag (and check for tags).

### Manual API

Issue a `POST` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules. To achieve this, in the response part of the detection & response rule, specify the add tag action. For example, to tag a device as DESKTOP, you would say:

```
- action: add tag
tag: DESKTOP

```

## Removing Tags

### Manual API

Issue a `DELETE` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

### Manual in the web app

In the web app, click on the sensor in question to expand it. You will see the list of tags you can add/edit/remove.

## Checking Tags

### Manual API

Issue a `GET` to `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

## System Tags

We provide system level functionality with a few system tags.  Those tags are listed below for reference:

### lc:latest

When you tag a sensor with `lc:latest`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the latest version of the sensor will be used instead. This means you can tag a representative set of computers in the Organization with the `lc:latest` tag in order to test-deploy the latest version and confirm no negative effects.

### lc:stable

When you tag a sensor with `lc:stable`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the *stable* version of the sensor will be used instead. This means you can upgrade an organization as a whole, but leave a few specific sensors behind by assigning the lc:stable tag to them.

### lc:experimental

When you tag a sensor with `lc:experimental`, the sensor version currently assigned to the Organization will be ignored for that specific sensor. An experimental version of the sensor will be used instead. This tag is typically used when working with the LimaCharlie team to troubleshoot sensor-specific issues.

### lc:no\_kernel

When you tag a sensor with `lc:no_kernel`, the kernel component will not be loaded on the host.

### lc:debug

When you tag a sensor with `lc:debug`, the debug version of the sensor currently assigned to the Organization will be used.

### lc:limit-update

When you tag a sensor with lc:limit-update, the sensor will not update the version it's running at run-time. The version will only be loaded when the sensor starts from scratch like after a reboot.

### lc:sleeper

When you tag a sensor with *lc:sleeper*, the sensor will keep its connection to the LimaCharlie Cloud, but will disable all other functionality to avoid any impact on the system.

### lc:usage

When you tag a sensor with *lc:usage*, the sensor will work as usual, but its connection will not count against the normal sensor quota. Instead, the time the sensor spends connected will be billed separately per second, and so will events received by the sensor. For more details, see [Sleeper Deployments](/v2/docs/sleeper).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

# Enterprise-wide Agent Deployment
To install sensors en masse, you can simply navigate to the `Installation Keys` section under Sensors, grab the Sensor download package and installation keys. You can then use a `cURL` command with a download link and Installation Key, or use any kind of enterprise deployment tool to install en masse.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%283%29.png)

Documentation on installing sensors can be found [here](/v2/docs/endpoint-agent-installation). Of course, mass deployments can be done using RMM, SCCM, MDM, and other tools.

We have provided [sample MDM profiles](/v2/docs/macos-agent-installation-mdm-configuration-profiles) for mass deployments on macOS.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

---

# Events

# Ingesting Sysmon Event Logs
Sysmon can be a valuable addition to any defender's toolkit, given it's verbosity and generous log data. It's worth noting that LimaCharlie's native EDR capabilities mirror much of the same telemetry. However, Sysmon and LimaCharlie can be combined to provide granular coverage across Windows systems.

With Sysmon deployed, you can utilize LimaCharlie's native Windows Event Log (WEL) streaming capabilities to bring logs into the Sensor timeline.

1. Install [Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon) on the endpoint.

   * This can easily be done via LimaCharlie's Payload functionality, with a  rule, or manually.
   * Please note that the LimaCharlie agent must be restarted in order for Sysmon data to show up in the timeline.
   * Example rule to deploy Sysmon via payloads on Windows systems tagged with `deploy-sysmon`:

     ```
     detect:
       events:
         - CONNECTED
       op: and
       rules:
         - op: is platform
           name: windows
         - op: is tagged
           tag: deploy-sysmon
     respond:
     - action: task
       command: put --payload-name sysmon.exe --payload-path "C:\Windows\Temp\sysmon.exe"
     - action: wait
       duration: 10s
     - action: task
       command: put --payload-name sysmon-config.xml --payload-path "C:\Windows\Temp\sysmon-config.xml"
     - action: wait
       duration: 10s
     - action: task
       command: run --shell-command "C:\Windows\Temp\sysmon.exe -accepteula -i C:\Windows\Temp\sysmon-config.xml"
     - action: wait
       duration: 10s
     - action: task
       command: file_del "C:\Windows\Temp\sysmon.exe"
     - action: task
       command: file_del "C:\Windows\Temp\sysmon-config.xml"
     - action: remove tag
       tag: deploy-sysmon
     - action: task
       command: restart

     ```
2. Within the Organization where you wish to collect Sysmon data, go to the `Event Collection > Event Collection Rules` section.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2892%29.png)

3. Ensure that for Windows systems, `WEL` events are collected.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2893%29.png)

4. Go to the `Artifact Collection` section and add a new collection rule with the following path to bring in all Sysmon events:

`wel://Microsoft-Windows-Sysmon/Operational:*`

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2894%29.png)

**Note:** You can use tagging or other filters to narrow down the systems that logs are collected from.

Event Filtering

You can filter events by event ID to import select events. For example:

`wel://Microsoft-Windows-Sysmon/Operational:16`

`wel://Microsoft-Windows-Sysmon/Operational:25`

5. Allow up to 10 minutes for data to come into LimaCharlie after setting up a new Artifact Collection rule. Data will flow in real-time after that point.
6. Navigate to the Timeline view of a Sensor to confirm that Sysmon logs are present. You can search for Event Type `WEL` and Search for `Microsoft-Windows-Sysmon` to validate the telemetry.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2896%29.png)

Endpoint Detection & Response

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

# Endpoint Agent Events Overview
## Overview

This category describes and provides samples for the various events emitted by the LimaCharlie Endpoint Agent Sensor. These events can be leveraged in [D&R rules](/v2/docs/detection-and-response) and queried with [LCQL](/v2/docs/lcql).

Important note about Event Collection

Only events enabled in the Exfil configuration will be shipped by the endpoint agent. If you're not seeing a specific event you expect, make sure that the desired event type is enabled in the [Exfil extension](/v2/docs/ext-exfil) configuration. Ensure your Exfil settings are properly configured to capture all required event types for your use case.

## Atoms

Atoms are Globally Unique Identifiers (GUIDs). An example might be: `1e9e242a512d9a9b16d326ac30229e7b`. You can treat them as opaque values. These unique values are used to relate events together rather than using Process IDs, which are themselves unreliable.

### Relationships

Atoms can be found in up to 3 spots in an event:

* `routing/this`: current event
* `routing/parent`: parent of the current event
* `routing/target`: target of the current event

Using atom references from a single event, the chain of ancestor events can be constructed. Here's a simplified example of an event and its parent event:

**Child event:**

```
{
  "event": {...},
  "routing": {
    "this": "abcdef",
    "parent": "zxcv"
    ...
  }
}

```

**Parent event:**

```
{
  "event": {...},
  "routing": {
    "this": "zxcv",
    "parent": "poiuy"
    ...
  }
}

```

API users may construct a tree from a single atom using these 2 endpoints:

* `/insight/{oid}/{sid}/{atom}` - get event by atom
* `/insight/{oid}/{sid}/{atom}/children` - get children of an atom

These can be called recursively on each event's `routing/parent` and/or child events to complete a full tree if required - this is how the tree view works in the Timeline of a sensor in the web application.

The parent-child relationship serves to describe parent and child processes via the `NEW_PROCESS` or `EXISTING_PROCESS` events, but other types of events may also have parents. For example, on `NETWORK_SUMMARY` events, the `parent` will be the process that generated the network connections.

Tip: when using custom storage and/or searching solutions it's helpful to index the values of `routing/this` and `routing/parent` for each event. Doing so will speed up searching during threat hunting and investigations.

Finally, the `routing/target` is only sometimes found in an event, and it represents an event that interacts with another event without having a parent-child relationship. For example, in the `NEW_REMOTE_THREAD` event, this `target` represents a process where a remote thread was created.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

---

# Events
## Events Overview

LimaCharlie provides a multitude of events based on actions generated by sensors, systems, services, artifacts, and other key functions of the platform. The following pages provide details on structured events available in LimaCharlie. Note, this section only describes events generated by the LimaCharlie Endpoint Agent Sensor or the LimaCharlie platform. Events generated by third-party sources (i.e., ingested via an [Adapter](/v2/docs/adapters)) will be provided in their raw format, and can be addressed as such within [Detection & Response rules](/v2/docs/detection-and-response).

Missing events on a sensor timeline?

Not seeing an expected event in your timeline? Be sure that you included all events of interest in your [Exfil Control](/v2/docs/ext-exfil).

## Operationalizing Events

Events can be observed and matched by [Detection & Response rules](/v2/docs/detection-and-response) to automate behavior and can also be streamed via [Outputs](/v2/docs/outputs) to the destination of your choice.

## Schema

Specific Event schemas are learned and available through the Schema API, learn more [here](/v2/docs/event-schemas).

## Streams

There are 6 different event streams moving through LimaCharlie:

| Name | Description | D&R Target | Output |
| --- | --- | --- | --- |
| Events | Events sent from sensors | <default> | ✅ |
| Deployment | Lifecycle events sent from sensors | `deployment` | ✅ |
| Detections | Detections reported from D&R rules | `detection` | ✅ |
| Artifacts | Artifacts sent from sensors (or API) | `artifact` | ✅ |
| Artifact Events | Lifecycle events for artifacts | `artifact_event` | ✅ |
| Audit | Audit logs for management activity within LimaCharlie | `audit` | ✅ |
| Billing | Billing activity within LimaCharlie | `billing` | ✅ |

## Formatting

At a high level, events in LimaCharlie are in standard formatted JSON.

```
{
  "type": "object",
  "properties": {
    "event": {
      "type": "any",
      "description": "Schema is determined by the routing/event_type"
    },
    "routing": {
      "type": "object",
      "properties": {
        "this": {
          "type": "string",
          "description": "GUID (i.e. 1e9e242a512d9a9b16d326ac30229e7b) - see 'Atoms' section for more detail",
          "format": "Atom"
        },
        "event_type": {
          "type": "string",
          "description": "The event type (e.g. NEW_PROCESS, NETWORK_SUMMARY) dictates the 'event' schema"
        },
        "event_time": {
          "type": "integer",
          "description": "The time the event was observed on the host"
        },
        "latency": {
          "type": "integer",
          "description": "The time difference between event time and event arrival, in milliseconds"
        },
        "event_id": {
          "type": "string",
          "format": "UUID"
        },
        "oid": {
          "type": "string",
          "format": "UUID",
          "description": "Organization ID"
        },
        "sid": {
          "type": ["string", "null"],
          "format": "UUID",
          "description": "Sensor ID"
        },
        "did": {
          "type": ["string", "null"],
          "format": "UUID",
          "description": "Device ID"
        },
        "iid": {
          "type": ["string", "null"],
          "format": "UUID",
          "description": "Installer Key ID"
        },
        "investigation_id": {
          "type": ["string", "null"],
          "format": "string",
          "description": "Events responding to a command will include this if it was provided along with the command"
        },
        "parent": {
          "type": ["string", "null"],
          "description": "Atom of possible parent event",
          "format": "Atom"
        },
        "target": {
          "type": ["string", "null"],
          "description": "Atom of possible target event",
          "format": "Atom"
        },
        "hostname": {
          "type": ["string", "null"],
        },
        "arch": {
          "type": ["integer", "null"],
          "description": "Integer corresponds with sensor architecture"
        },
        "plat": {
          "type": ["integer", "null"],
          "description": "Integer corresponds with sensor platform"
        },
        "tags": {
          "type": ["array"],
          "format": "string",
          "description": "Tags applied to sensor at the time the event was sent"
        },
      }
    }
  }
}

```

The following is a sample event utilizing the above schema:

```
{
  "event": {
    "BASE_ADDRESS": 140702709383168,
    "COMMAND_LINE": "C:\\\\Windows\\\\System32\\\\evil.exe -Embedding",
    "FILE_IS_SIGNED": 1,
    "FILE_PATH": "C:\\\\Windows\\\\System32\\\\evil.exe",
    "HASH": "5ef1322b96f176c4ea4b8304caf8b45e2e42c3188aa52ed1fd6196afc04b7297",
    "MEMORY_USAGE": 9515008,
    "PARENT": {
      "BASE_ADDRESS": 140697905135616,
      "COMMAND_LINE": "C:\\\\Windows\\\\system32\\\\unknown.exe -k Launch",
      "CREATION_TIME": 1625797634428,
      "FILE_IS_SIGNED": 1,
      "FILE_PATH": "C:\\\\Windows\\\\system32\\\\unknown.exe",
      "HASH": "438b6ccd84f4dd32d9684ed7d58fd7d1e5a75fe3f3d14ab6c788e6bb0ffad5e7",
      "MEMORY_USAGE": 19070976,
      "PARENT_ATOM": "ebf1884039c7650401b2198f60f89d2d",
      "PARENT_PROCESS_ID": 123,
      "PROCESS_ID": 1234,
      "THIS_ATOM": "ad48d1f14a8e5a114e85f79b60f89d2d",
`      "THREADS": 14,
      "TIMESTAMP": 1626905901981,
      "USER_NAME": "NT AUTHORITY\\\\SYSTEM"
    },
    "PARENT_PROCESS_ID": 580,
    "PROCESS_ID": 5096,
    "THREADS": 6,
    "USER_NAME": "BUILTIN\\\\Administrators"
  },
  "routing": {
    "this": "655c970d2052b9f1c365839b611baf96",
    "parent": "ad48d1f14a3e5a114e85f79b60f89d2d",
    "arch": 2,
    "did": "3ef599f3-64dc-51f5-8322-62b0a6b8eef7",
    "event_id": "bdf6df69-b72c-470a-994b-216f1cdde9a7",
    "event_time": 1629204374140,
    "latency": 78,
    "event_type": "NEW_PROCESS",
    "ext_ip": "123.456.78.901",
    "hostname": "test-host-123",
    "iid": "e22638c9-44a6-455a-83e2-a689ac9868a7",
    "int_ip": "10.4.34.227",
    "moduleid": 2,
    "oid": "8cbe27f4-agh1-4afb-ba19-138cd51389cd",
    "plat": 268435456,
    "sid": "d3d17f12-eecf-5287-b3a1-bf267aabb3cf",
    "tags": ["server"],
  },
}

```

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Exfil (Event Collection)
The Exfil Extension helps manage which real-time [events](/v2/docs/reference-edr-events) get sent from EDR Sensors to LimaCharlie. By default, LimaCharlie Sensors send events to the cloud based on a standard profile. This extension exposes those profiles for customization. The Exfil extension allows you to customize Event Collection from LimaCharlie Sensors, as well as mitigate Sensors with high I/O or large [detection and response](/v2/docs/detection-and-response) rulesets.

> Event Collection Rule Synchronization
>
> Please note that Exfil (or Event Collection) rule configurations are synchronized with sensors every few minutes.

## Enabling the Exfil Extension

To enable the Exfil extension, navigate to the [Exfil extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-exfil) in the marketplace. Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(231).png "image(231).png")

After clicking subscribe, the Exfil extension should be available almost immediately.

## Using the Exfil Extension

Once the extension is enabled, you will see an **Event Collection** option under **Sensors** in the LimaCharlie web UI.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(227).png "image(227).png")

There are three Rule options within the Exfil extension:

* **Event Collection Rules** manage events sent by the Sensor to the LimaCharlie cloud.
* **Performance Rules** are useful for high I/O servers, but may impact event accuracy. This feature is available only on Windows Sensors.
* **Watch Rules** allow for conditional operators for an event, allowing you to specify a list of sensors to help manage high-volume events. Conditional operators for Watch Rule events include:

  + The **event** itself, such as `MODULE_LOAD`.
  + The **path** within the event component to be evaluated, such as `FILE_PATH`.
  + The **operator** to evaluate or compare that should be done between the path and the value.
  + The **value** to be used in comparison with the operator.

A sample **Watch Rule** might be

```
Event: MODULE_LOAD
Path: FILE_PATH
Operator: ends with
Value: wininet.dll
```

The above rule would configures the Sensor(s) to send *only* `MODULE_LOAD` events where the `FILE_PATH` ends with the value `wininet.dll`.

> Performance Rules
>
> Performance rules, applied via tag to a set of Sensors, are useful for high I/O systems. These rules can be set via the web application or REST API.

### Throughput Limits

Enabling *every* event for Exfil can produce an exceedingly large amount of traffic. Our first recommendation would be to optimize events required for detection & response rules, in order to ensure that all rules are active. We’d also recommend prioritizing events that contribute to outputs, such as forwarded `DNS_REQUESTS`.

LimaCharlie attempts to process all events in real-time. However, if events fall behind, they are enqueued to a certain limit. If that limit is reached (e.g. in the case of a long, sustained burst or enabling *all* events at the same time), the queue may eventually get dropped. In that event, an error is emitted to the platform logs.

Seeing event collection errors is a sign you may need to do one of the following:

1. Reduce the population of events collected.
2. Reduce the number of  rules you run or rule complexity.
3. Adopt a selective subset of events by utilizing Watch Rules that only bring back events with specific values.
4. Enable the IR mode (below).

#### Afterburner

Before a backlogged queue is dropped, LimaCharlie attempts to increase performance by entering a special mode we call “afterburner.” This mode tries to address one of the common scenarios that can lead to a large influx of data: spammy processes starting over and over. This happens in situations such as the building of software, in which executables like `devenv.exe` or `git` can be called hundreds of times per second. The afterburner mode attempts to (1) de-duplicate those processes and (2) assess only each one through the D&R rules and Outputs.

#### IR Mode

The afterburner mode does not address all possible causes or situations. To help with this, LimaCharlie offers “IR mode.” This mode is enabled by tagging a LimaCharlie sensor with the tag `ir`. The goal of “IR mode” is to provide a solution for users who want to record a very large number of events, but do not need to run D&R rules over all of them. When enabled, “IR mode” will not de-duplicate events. Furthermore, D&R rules will *only* be run against the follow event types:

1. `CODE_IDENTITY`
2. `DNS_REQUEST`
3. `NETWORK_CONNECTIONS`
4. `NEW_PROCESS`

IR mode is designed to give a balance between recording all events, while maintaining basic D&R rule capabilities.

## Actions via REST API

The following REST API actions can be sent to interact with the Exfil extension:

**List Rules**

```
{
  "action": "list_rules"
}
```

### Event Collection Rules

**Add Event Collection Rule**

```
{
  "action": "add_event_rule",
  "name": "windows-vip",
  "events": [
    "NEW_TCP4_CONNECTION",
    "NEW_TCP6_CONNECTION"
  ],
  "tags": [
    "vip"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Event Collection Rule**

```
{
  "action": "remove_event_rule",
  "name": "windows-vip"
}
```

### Watch Rules

**Add Watch Rule**

```
{
  "action": "add_watch",
  "name": "wininet-loading",
  "event": "MODULE_LOAD",
  "operator": "ends with",
  "value": "wininet.dll",
  "path": [
    "FILE_PATH"
  ],
  "tags": [
    "server"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Watch Rule**

```
{
  "action": "remove_watch",
  "name": "wininet-loading"
}
```

### Performance Rules

**Add Performance Rule**

```
{
  "action": "add_perf_rule",
  "name": "sql-servers",
  "tags": [
    "sql"
  ],
  "platforms": [
    "windows"
  ]
}
```

**Remove Performance Rule**

```
{
  "action": "remove_perf_rule",
  "name": "sql-servers"
}
```

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Endpoint Detection & Response

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Reference: EDR Events
## Overview

This page provides a detailed overview of all events generated by the LimaCharlie Endpoint Agent. Each event type represents a specific system activity, from process creation to network connections and file modifications. Events serve as key components in detection, response, and monitoring, enabling security teams to track, analyze, and take action on endpoint behavior. Use this guide to understand the purpose and structure of each event for effective threat detection and investigation.

Generally, event types ending with `*_REP` are emitted in response to a command being issued to the endpoint agent.

## EDR Events by Supported OS

These are the events emitted by the endpoint agent for each supported operating system. Below the table, you can find descriptions of each event type.

| EDR Event Type | macOS | Windows | Linux | Chrome | Edge |
| --- | --- | --- | --- | --- | --- |
| [AUTORUN\_CHANGE](/v2/docs/reference-edr-events#autorunchange) |  | ☑️ |  |  |  |
| [CLOUD\_NOTIFICATION](/v2/docs/reference-edr-events#cloudnotification) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [CODE\_IDENTITY](/v2/docs/reference-edr-events#codeidentity) | ☑️ | ☑️ | ☑️ |  |  |
| [CONNECTED](/v2/docs/reference-edr-events#connected) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [DATA\_DROPPED](/v2/docs/reference-edr-events#datadropped) | ☑️ | ☑️ | ☑️ |  |  |
| [DEBUG\_DATA\_REP](/v2/docs/reference-edr-events#getdebugdata) |  | ☑️ |  |  |  |
| [DELETED\_SENSOR](/v2/docs/reference-edr-events#deletedsensor) | ☑️ | ☑️ | ☑️ |  |  |
| [DIR\_FINDHASH\_REP](/v2/docs/reference-edr-events#dirfindhash) | ☑️ | ☑️ | ☑️ |  |  |
| [DIR\_LIST\_REP](/v2/docs/reference-edr-events#dirlist) | ☑️ | ☑️ | ☑️ |  |  |
| [DISCONNECTED](/v2/docs/reference-edr-events#disconnected) |  | ☑️ |  |  |  |
| [DNS\_REQUEST](/v2/docs/reference-edr-events#dnsrequest) | ☑️ | ☑️ | ☑️ | ☑️ | ☑️ |
| [DRIVER\_CHANGE](/v2/docs/reference-edr-events#driverchange) |  | ☑️ |  |  |  |
| [EXEC\_OOB](/v2/docs/reference-edr-events#execoob) | ☑️ |  | ☑️ |  |  |
| [EXISTING\_PROCESS](/v2/docs/reference-edr-events#existingprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [EXPORT\_COMPLETE](/v2/docs/reference-edr-events#exportcomplete) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_ADD](/v2/docs/reference-edr-events#fimadd) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_DEL](/v2/docs/reference-edr-events#fimdel) | ☑️ | ☑️ | ☑️ |  |  |
| [FIM\_HIT](/v2/docs/reference-edr-events#fimhit) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_CREATE](/v2/docs/reference-edr-events#filecreate) | ☑️ | ☑️ |  |  |  |
| [FILE\_DEL\_REP](/v2/docs/reference-edr-events#filedel) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_DELETE](/v2/docs/reference-edr-events#filedelete) | ☑️ | ☑️ |  |  |  |
| [FILE\_GET\_REP](/v2/docs/reference-edr-events#fileget) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_HASH\_REP](/v2/docs/reference-edr-events#filehash) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_INFO\_REP](/v2/docs/reference-edr-events#fileinfo) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_MODIFIED](/v2/docs/reference-edr-events#filemodified) | ☑️ | ☑️ |  |  |  |
| [FILE\_MOV\_REP](/v2/docs/reference-edr-events#filemov) | ☑️ | ☑️ | ☑️ |  |  |
| [FILE\_TYPE\_ACCESSED](/v2/docs/reference-edr-events#filetypeaccessed) | ☑️ | ☑️ |  |  |  |
| [GET\_DOCUMENT\_REP](/v2/docs/reference-edr-events#doccacheget) | ☑️ | ☑️ |  |  |  |
| [GET\_EXFIL\_EVENT\_REP](/v2/docs/reference-edr-events#exfilget) | ☑️ | ☑️ | ☑️ |  |  |
| [HIDDEN\_MODULE\_DETECTED](/v2/docs/reference-edr-events#hiddenmoduledetected) |  | ☑️ |  |  |  |
| [HISTORY\_DUMP\_REP](/v2/docs/reference-edr-events#historydump) | ☑️ | ☑️ | ☑️ |  |  |
| [HTTP\_REQUEST](/v2/docs/reference-edr-events#httprequest) |  |  |  | ☑️ | ☑️ |
| [HTTP\_REQUEST\_HEADERS](/v2/docs/reference-edr-events#httprequestheaders) |  |  |  | ☑️ |  |
| [HTTP\_RESPONSE\_HEADERS](/v2/docs/reference-edr-events#httpresponseheaders) |  |  |  | ☑️ |  |
| [INGEST](/v2/docs/reference-edr-events#ingest) | ☑️ | ☑️ | ☑️ |  |  |
| [LOG\_GET\_REP](/v2/docs/reference-edr-events#logget) |  |  |  |  |  |
| [LOG\_LIST\_REP](/v2/docs/reference-edr-events#loglist) |  |  |  |  |  |
| [MEM\_FIND\_HANDLES\_REP](/v2/docs/reference-edr-events#memfindhandle) |  | ☑️ |  |  |  |
| [MEM\_FIND\_STRING\_REP](/v2/docs/reference-edr-events#memfindstring) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_HANDLES\_REP](/v2/docs/reference-edr-events#memhandles) |  | ☑️ |  |  |  |
| [MEM\_MAP\_REP](/v2/docs/reference-edr-events#memmap) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_READ\_REP](/v2/docs/reference-edr-events#memread) | ☑️ | ☑️ | ☑️ |  |  |
| [MEM\_STRINGS\_REP](/v2/docs/reference-edr-events#memstrings) | ☑️ | ☑️ | ☑️ |  |  |
| [MODULE\_LOAD](/v2/docs/reference-edr-events#moduleload) |  | ☑️ | ☑️ |  |  |
| [MODULE\_MEM\_DISK\_MISMATCH](/v2/docs/reference-edr-events#modulememdiskmismatch) | ☑️ | ☑️ | ☑️ |  |  |
| [NETSTAT\_REP](/v2/docs/reference-edr-events#netstat) | ☑️ | ☑️ | ☑️ |  |  |
| [NETWORK\_CONNECTIONS](/v2/docs/reference-edr-events#networkconnections) | ☑️ | ☑️ | ☑️ |  |  |
| [NETWORK\_SUMMARY](/v2/docs/reference-edr-events#networksummary) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_DOCUMENT](/v2/docs/reference-edr-events#newdocument) | ☑️ | ☑️ |  |  |  |
| [NEW\_NAMED\_PIPE](/v2/docs/reference-edr-events#newnamedpipe) |  | ☑️ |  |  |  |
| [NEW\_PROCESS](/v2/docs/reference-edr-events#newprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_REMOTE\_THREAD](/v2/docs/reference-edr-events#newremotethread) |  | ☑️ |  |  |  |
| [NEW\_TCP4\_CONNECTION](/v2/docs/reference-edr-events#newtcp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_TCP6\_CONNECTION](/v2/docs/reference-edr-events#newtcp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_UDP4\_CONNECTION](/v2/docs/reference-edr-events#newudp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [NEW\_UDP6\_CONNECTION](/v2/docs/reference-edr-events#newudp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [OPEN\_NAMED\_PIPE](/v2/docs/reference-edr-events#opennamedpipe) |  | ☑️ |  |  |  |
| [OS\_AUTORUNS\_REP](/v2/docs/reference-edr-events#osautoruns) | ☑️ | ☑️ |  |  |  |
| [OS\_DRIVERS\_REP](/v2/docs/reference-edr-events#osdrivers) |  | ☑️ |  |  |  |
| [OS\_KILL\_PROCESS\_REP](/v2/docs/reference-edr-events#oskillprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_PACKAGES\_REP](/v2/docs/reference-edr-events#ospackages) |  | ☑️ |  |  |  |
| [OS\_PROCESSES\_REP](/v2/docs/reference-edr-events#osprocesses) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_RESUME\_REP](/v2/docs/reference-edr-events#osresume) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_SERVICES\_REP](/v2/docs/reference-edr-events#osservices) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_SUSPEND\_REP](/v2/docs/reference-edr-events#ossuspend) | ☑️ | ☑️ | ☑️ |  |  |
| [OS\_USERS\_REP](/v2/docs/reference-edr-events#osusers) |  | ☑️ |  |  |  |
| [OS\_VERSION\_REP](/v2/docs/reference-edr-events#osversion) | ☑️ | ☑️ | ☑️ |  |  |
| [PCAP\_LIST\_INTERFACES\_REP](/v2/docs/reference-edr-events#pcapifaces) |  |  | ☑️ |  |  |
| [PROCESS\_ENVIRONMENT](/v2/docs/reference-edr-events#processenvironment) |  | ☑️ | ☑️ |  |  |
| [RECEIPT](/v2/docs/reference-edr-events#receipt) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [REGISTRY\_CREATE](/v2/docs/reference-edr-events#registrycreate) |  | ☑️ |  |  |  |
| [REGISTRY\_DELETE](/v2/docs/reference-edr-events#registrydelete) |  | ☑️ |  |  |  |
| [REGISTRY\_LIST\_REP](/v2/docs/reference-edr-events#reglist) |  | ☑️ |  |  |  |
| [REGISTRY\_WRITE](/v2/docs/reference-edr-events#registrywrite) |  | ☑️ |  |  |  |
| [REJOIN\_NETWORK](/v2/docs/reference-edr-events#rejoinnetwork) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [REMOTE\_PROCESS\_HANDLE](/v2/docs/reference-edr-events#remoteprocesshandle) |  | ☑️ |  |  |  |
| [SEGREGATE\_NETWORK](/v2/docs/reference-edr-events#segregatenetwork) | ☑️ | ☑️ | ☑️ | ☑️ |  |
| [SENSITIVE\_PROCESS\_ACCESS](/v2/docs/reference-edr-events#sensitiveprocessaccess) |  | ☑️ |  |  |  |
| [SERVICE\_CHANGE](/v2/docs/reference-edr-events#servicechange) | ☑️ | ☑️ | ☑️ |  |  |
| [SHUTTING\_DOWN](/v2/docs/reference-edr-events#shuttingdown) | ☑️ | ☑️ | ☑️ |  |  |
| [SSH\_LOGIN](/v2/docs/reference-edr-events#sshlogin) | ☑️ |  |  |  |  |
| [SSH\_LOGOUT](/v2/docs/reference-edr-events#sshlogout) | ☑️ |  |  |  |  |
| [STARTING\_UP](/v2/docs/reference-edr-events#startingup) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_PROCESS](/v2/docs/reference-edr-events#terminateprocess) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_TCP4\_CONNECTION](/v2/docs/reference-edr-events#terminatetcp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_TCP6\_CONNECTION](/v2/docs/reference-edr-events#terminatetcp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_UDP4\_CONNECTION](/v2/docs/reference-edr-events#terminateudp4connection) | ☑️ | ☑️ | ☑️ |  |  |
| [TERMINATE\_UDP6\_CONNECTION](/v2/docs/reference-edr-events#terminateudp6connection) | ☑️ | ☑️ | ☑️ |  |  |
| [THREAD\_INJECTION](/v2/docs/reference-edr-events#threadinjection) |  | ☑️ |  |  |  |
| [USER\_LOGIN](/v2/docs/reference-edr-events#userlogin) | ☑️ |  |  |  |  |
| [USER\_LOGOUT](/v2/docs/reference-edr-events#userlogout) | ☑️ |  |  |  |  |
| [USER\_OBSERVED](/v2/docs/reference-edr-events#userobserved) | ☑️ | ☑️ | ☑️ |  |  |
| [VOLUME\_MOUNT](/v2/docs/reference-edr-events#volumemount) | ☑️ | ☑️ |  |  |  |
| [VOLUME\_UNMOUNT](/v2/docs/reference-edr-events#volumeunmount) | ☑️ | ☑️ |  |  |  |
| [WEL](/v2/docs/reference-edr-events#wel) |  | ☑️ |  |  |  |
| [YARA\_DETECTION](/v2/docs/reference-edr-events#yaradetection) | ☑️ | ☑️ | ☑️ |  |  |

---

## Event Descriptions

### AUTORUN\_CHANGE

Generated when an Autorun is changed.

**Platforms:**

```
{
  "REGISTRY_KEY": "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
  "TIMESTAMP": 1627497894000
}

```

---

### CLOUD\_NOTIFICATION

This event is a receipt from the agent that it has received the task sent to it, and includes high-level errors (if any).

**Platforms:**

```
{
  "NOTIFICATION_ID": "ADD_EXFIL_EVENT_REQ",
  "NOTIFICATION": {
    "INVESTIGATION_ID": "digger-4afdeb2b-a0d8-4a37-83b5-48996117998e"
  },
  "HCP_IDENT": {
    "HCP_ORG_ID": "c82e5c17d5194ef5a4acc454a95d31db",
    "HCP_SENSOR_ID": "8fc370e6699a49858e75c1316b725570",
    "HCP_INSTALLER_ID": "00000000000000000000000000000000",
    "HCP_ARCHITECTURE": 0,
    "HCP_PLATFORM": 0
  },
  "EXPIRY": 0
}

```

---

### CODE\_IDENTITY

Unique combinations of file hash and file path. This event is emitted the first time the combination is seen, typically when the binary is executed or loaded. Therefore it's a great event to look for hashes without being overwhelmed by process execution or module loads.

ONGOING\_IDENTITY

The `ONGOING_IDENTITY` event emits code signature information even if not newly seen, however this data can become duplicative and verbose.

**Platforms:**

```
{
  "MEMORY_SIZE": 0,
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\B1B207E5-300E-434F-B4FE-A4816E6551BE\\dismhost.exe",
  "TIMESTAMP": 1456285265,
  "SIGNATURE": {
    "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Code Signing PCA",
    "CERT_CHAIN_STATUS": 124,
    "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\B1B207E5-300E-434F-B4FE-A4816E6551BE\\dismhost.exe",
    "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, OU=MOPR, CN=Microsoft Corporation"
  },
  "HASH": "4ab4024eb555b2e4c54d378a846a847bd02f66ac54849bbce5a1c8b787f1d26c"
}

```

---

### CONNECTED

This event is generated when a Sensor connects to the cloud.

**Platforms:**

```
{
    "HOST_NAME" : "demo-win-2016",
    "IS_SEGREGATED" : 0,
    "KERNEL_ACQ_AVAILABLE" : 1,
    "MAC_ADDRESS" : "42-01-0A-80-00-02"
}

```

---

### DEBUG\_DATA\_REP

Response from a `get_debug_data` request.

### DIR\_FINDHASH\_REP

Response event for the `dir_find_hash` sensor command.

**Platforms:**

**Sample Event:**

```
{
    "DIRECTORY_LIST": [
        {
            "HASH": "f11dda931637a1a1bc614fc2f320326b24336c5155679aa062acae7c79f33d67",
            "ACCESS_TIME": 1535994794247,
            "FILE_SIZE": 113664,
            "CREATION_TIME": 1467173189067,
            "MODIFICATION_TIME": 1467173190171,
            "FILE_NAME": "MALWARE_DEMO_WINDOWS_1.exe",
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\MALWARE_DEMO_WINDOWS_1.exe"
        },
        {
            "HASH": "e37726feee8e72f3ab006e023cb9d6fa1a4087274b47217d2462325fa8008515",
            "ACCESS_TIME": 1535989041078,
            "FILE_SIZE": 1016320,
            "CREATION_TIME": 1522507344821,
            "MODIFICATION_TIME": 1522507355732,
            "FILE_NAME": "lc_win_64.exe",
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\lc_win_64.exe"
        }
    ],
    "HASH": [
        "f11dda931637a1a1bc614fc2f320326b24336c5155679aa062acae7c79f33d67",
        "e37726feee8e72f3ab006e023cb9d6fa1a4087274b47217d2462325fa8008515"
    ],
    "FILE_PATH": "*.exe",
    "DIRECTORY_LIST_DEPTH": 0,
    "DIRECTORY_PATH": "c:\\users\\dev\\desktop\\"
}

```

### DIR\_LIST\_REP

Response event for the `dir_list` sensor command. Includes Alternate Data Streams on Windows.

**Platforms:**

**Sample Event:**

```
{
    "DIRECTORY_LIST": [
        {
            "FILE_NAME": "vssdk_full.exe",
            "CREATION_TIME": 1553437930012,
            "MODIFICATION_TIME": 1553437937000,
            "STREAMS": [
                {
                    "FILE_NAME": "::$DATA",
                    "SIZE": 13782032
                }
            ],
            "ACCESS_TIME": 1567868284440,
            "FILE_SIZE": 13782032,
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\vssdk_full.exe"
        },
        {
            "FILE_NAME": "UniversalLog.txt",
            "CREATION_TIME": 1553028205525,
            "MODIFICATION_TIME": 1553028206289,
            "STREAMS": [
                {
                    "FILE_NAME": "::$DATA",
                    "SIZE": 125
                },
                {
                    "FILE_NAME": ":Zone.Identifier:$DATA",
                    "SIZE": 377
                }
            ],
            "ACCESS_TIME": 1567868284158,
            "FILE_SIZE": 125,
            "ATTRIBUTES": 32,
            "FILE_PATH": "c:\\users\\dev\\desktop\\UniversalLog.txt"
        }
    ]
}

```

---

### DISCONNECTED

This event is generated when a Sensor disconnects from the cloud.

**Platforms:**

```
{
  "DISCONNECTED": {},
  "ts": 1455674775
}

```

---

### DNS\_REQUEST

Generated from DNS responses and therefore includes both the requested domain and the response from the server. If the server responds with multiple responses (as allowed by the DNS protocol) the N answers will become N DNS\_REQUEST events, so you can always assume one DNS\_REQUEST event means one answer.

**Platforms:**

```
{
  "DNS_TYPE": 1,
  "TIMESTAMP": 1456285240,
  "DNS_FLAGS": 0,
  "DOMAIN_NAME": "time.windows.com"
}

```

---

### DRIVER\_CHANGE

Generated when a driver is changed.

**Platforms:**

```
{
  "PROCESS_ID": 0,
  "SVC_DISPLAY_NAME": "HbsAcq",
  "SVC_NAME": "HbsAcq",
  "SVC_STATE": 1,
  "SVC_TYPE": 1,
  "TIMESTAMP": 1517377895873
}

```

---

### EXISTING\_PROCESS

This event is similar to the NEW\_PROCESS event.  It gets emitted when a process existed prior to the LimaCharlie sensor loading.

**Platforms:**

---

### FILE\_CREATE

Generated when a file is created.

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Microsoft\\Windows\\WebCache\\V01tmp.log",
  "TIMESTAMP": 1468335271948
}

```

---

### FILE\_DEL\_REP

Response event for the `file_del` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_PATH": "C:\\test\\test.txt"
}

```

---

### FILE\_DELETE

Generated when a file is deleted.

> Be Aware:
>
> When adding this event to an event collection rule, you will be monitoring system-wide. This could result in a large number of events.

> Best Practices:
>
> * Utilize this selectively (ex. deploy on only suspect systems)
> * Use Exfil watch rules to specify paths that are of high interest
> * Consider using File Integrity Monitoring (FIM)
> * Look for this on an ad-hoc basis from the Sensor Console. ex.
>
>   ```
>   history_dump -e FILE_DELETE
>   ```

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Temp\\EBA4E4F0-3020-459E-9E34-D5336E244F05\\api-ms-win-core-processthreads-l1-1-2.dll",
  "TIMESTAMP": 1468335611906
}

```

---

### FILE\_GET\_REP

Response event for the `file_get` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_CONTENT": "$BASE64_ENCODED_FILE_CONTENTS",
  "FILE_PATH": "C:\\windows\\system32\\svchost.exe",
  "FILE_SIZE": 78880
}

```

### FILE\_HASH\_REP

Response event for the `file_hash` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "FILE_IS_SIGNED": 1,
  "FILE_PATH": "C:\\Windows\\System32\\svchost.exe",
  "HASH": "31780ff2aaf7bc71f755ba0e4fef1d61b060d1d2741eafb33cbab44d889595a0",
  "SIGNATURE": {
    "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Production PCA 2011",
    "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Publisher",
    "FILE_CERT_IS_VERIFIED_LOCAL": 1,
    "FILE_IS_SIGNED": 1,
    "FILE_PATH": "C:\\Windows\\System32\\svchost.exe"
  }
}

```

### FILE\_INFO\_REP

Response event for the `file_info` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "ACCESS_TIME": 1686685723546,
  "ATTRIBUTES": 0,
  "CREATION_TIME": 1686685723546,
  "FILE_IS_SIGNED": 1,
  "FILE_PATH": "C:\\Windows\\System32\\svchost.exe",
  "FILE_SIZE": 78880,
  "MODIFICATION_TIME": 1686685723546
}

```

---

### FILE\_MODIFIED

Generated when a file is modified.

> Be Aware:
>
> When adding this event to an event collection rule, you will be monitoring system-wide. This could result in a large number of events.

> Best Practices:
>
> * Utilize this selectively (ex. deploy on only suspect systems)
> * Use Exfil watch rules to specify paths that are of high interest
> * Consider using File Integrity Monitoring (FIM)
> * Look for this on an ad-hoc basis from the Sensor Console. ex.
>
>   ```
>   history_dump -e FILE_MODIFIED
>   ```

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\AppData\\Local\\Microsoft\\Windows\\WebCache\\V01.log",
  "TIMESTAMP": 1468335272949
}

```

---

### FILE\_MOV\_REP

Response event for the `file_mov` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "DESTINATION": "C:\\test\\test.txt.bak",
  "SOURCE": "C:\\test\\test.txt"
}

```

---

### FILE\_TYPE\_ACCESSED

Generated when a new process is observed interacting with certain file types.

The `RULE_NAME` component is the class of file extension involved:

* Rule 1: `.doc`, `.docm`, `.docx`
* Rule 2: `.xlt`, `.xlsm`, `.xlsx`
* Rule 3: `.ppt`, `.pptm`, `.pptx`, `.ppts`
* Rule 4: `.pdf`
* Rule 5: `.rtf`
* Rule 50: `.zip`
* Rule 51: `.rar`
* Rule 64: `.locky`, `.aesir`

**Platforms:**

```
{
  "PROCESS_ID": 2048,
  "RULE_NAME": 50,
  "FILE_PATH": "C:\\Program Files\\7-Zip\\7zG.exe"
}

```

---

### FIM\_ADD

Response event for the `fim_add` sensor command. An `ERROR: 0` implies the path was successfully added.

**Platforms:**

**Output:**

```
"event": {
  "ERROR":0
}

```

### FIM\_DEL

Response event for the `fim_del` sensor command. An `ERROR: 0` implies the path was successfully removed.

An `ERROR: 3` response implies the provided path was not found in the list of FIM patterns.

**Platforms:**

**Output:**

```
"event": {
  "ERROR":0
}

```

---

### FIM\_HIT

A file, directory, or registry key being monitored by File & Registry Integrity Monitoring has been modified.

**Platforms:**

```
{
  "PROCESS": {
    "MEMORY_USAGE": 25808896,
    "TIMESTAMP": 1541348299886,
    "COMMAND_LINE": "\"C:\\WINDOWS\\regedit.exe\" ",
    "PROCESS_ID": 4340,
    "THREADS": 3,
    "USER_NAME": "BUILTIN\\Administrators",
    "FILE_PATH": "C:\\WINDOWS\\regedit.exe",
    "PARENT_PROCESS_ID": 6260
  },
  "REGISTRY_KEY": "\\REGISTRY\\MACHINE\\SOFTWARE\\ActiveState\\New Value #1",
  "PROCESS_ID": 4340
}

```

---

### FIM\_LIST\_REP

Response event for the `fim_get` sensor command. The response will be a JSON list of FIM patterns.

**Platforms:**

**Output:**

```
{
  "PATTERNS": [
    0: "/home/*",
    1: "/home/*/.ssh/*",
    2: "/root/.ssh/authorized_keys"
  ]
}

```

---

### GET\_DOCUMENT\_REP

Generated when a `doc_cache_get` task requests a cached document.

**Platforms:**

### GET\_EXFIL\_EVENT\_REP

Response from an `exfil_get` sensor command.

**Platforms:**

### HIDDEN\_MODULE\_DETECTED

Generated when a `hidden_module_scan` command is issued.

Note that the name of the event does not confirm the presence of a hidden module. Please check the output to

confirm whether a hidden module was detected.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0,
  "ERROR_MESSAGE": "done"
}

```

### HISTORY\_DUMP\_REP

Response from `history_dump` sensor command. Does not itself contain the historic events but will be generated along them.

**Platforms:**

---

### HTTP\_REQUEST

This event is emitted whenever an HTTP request is made.

**Platforms:**

**Sample Event:**

```
{
  "URL": "https://play.google.com/log?authuser=0",
  "IP_ADDRESS": "172.217.2.142",
  "RESULT": 200,
  "PARENT": {
    "URL": "https://console.cloud.google.com"
  }
}

```

---

### HTTP\_REQUEST\_HEADERS

Provides HTTP Request headers.

**Platforms:**

**Sample Event:**

```
{
  "HEADERS": [
    {
      "NAME": "User-Agent",
      "VALUE": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    },
    {
      "NAME": "Accept",
      "VALUE": "*/*"
    }
  ]
}

```

---

### HTTP\_RESPONSE\_HEADERS

Provides HTTP Response headers.

**Platforms:**

**Sample Event:**

```
{
  "HEADERS": [
    {
      "NAME": "content-length",
      "VALUE": "859"
    },
    {
      "NAME": "cache-control",
      "VALUE": "max-age=3600"
    },
    {
      "NAME": "content-encoding",
      "VALUE": "br"
    },
    {
      "NAME": "content-type",
      "VALUE": "text/html; charset=utf-8"
    },
    {
      "NAME": "etag",
      "VALUE": "\"1540d7725dd15680377d45886baba56f620f7692faa530bc3597226ffadd77d1-br\""
    },
    {
      "NAME": "last-modified",
      "VALUE": "Thu, 21 Dec 2023 23:59:32 GMT"
    },
    {
      "NAME": "referrer-policy",
      "VALUE": "sameorigin"
    },
    {
      "NAME": "strict-transport-security",
      "VALUE": "max-age=3600 ; includeSubDomains"
    },
    {
      "NAME": "x-content-type-options",
      "VALUE": "nosniff"
    },
    {
      "NAME": "x-frame-options",
      "VALUE": "sameorigin"
    },
    {
      "NAME": "accept-ranges",
      "VALUE": "bytes"
    },
    {
      "NAME": "date",
      "VALUE": "Fri, 22 Dec 2023 19:10:58 GMT"
    },
    {
      "NAME": "x-served-by",
      "VALUE": "cache-dub4332-DUB"
    },
    {
      "NAME": "x-cache",
      "VALUE": "HIT"
    },
    {
      "NAME": "x-cache-hits",
      "VALUE": "1"
    },
    {
      "NAME": "x-timer",
      "VALUE": "S1703272259.579745,VS0,VE1"
    },
    {
      "NAME": "vary",
      "VALUE": "x-fh-requested-host, accept-encoding"
    },
    {
      "NAME": "alt-svc",
      "VALUE": "h3=\":443\";ma=86400,h3-29=\":443\";ma=86400,h3-27=\":443\";ma=86400"
    }
  ]
}

```

---

### LOG\_GET\_REP

Response from a `log_get` request.

### LOG\_LIST\_REP

Response from a `log_list` request.

### MEM\_FIND\_HANDLES\_REP

Response event for the `mem_find_handle` sensor command.

**Platforms:**

### MEM\_FIND\_STRING\_REP

Response event for the `mem_find_string` sensor command.

**Platforms:**

### MEM\_HANDLES\_REP

Response event for the `mem_handles` sensor command. This event will contain an array of handles identified in memory.

**Platforms:**

**Sample Event:**

```
{
    "HANDLES": [
      {
        "HANDLE_NAME": "\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options",
        "HANDLE_TYPE": "Key",
        "HANDLE_VALUE": 4,
        "PROCESS_ID": 908
      },
      {
        "HANDLE_NAME": "\\KnownDlls",
        "HANDLE_TYPE": "Directory",
        "HANDLE_VALUE": 48,
        "PROCESS_ID": 908
      },
      "..."]
}

```

### MEM\_MAP\_REP

Response event for the `mem_map` sensor command. This event will contain an array of arrays, representing processes and their associated memory data.

**Platforms:**

Sample Event:

```
{
    "MEMORY_MAP": [
      {
        "BASE_ADDRESS": 94100802174976,
        "MEMORY_ACCESS": 6,
        "MEMORY_SIZE": 4096,
        "MEMORY_TYPE": 3
      }
    ]
}

```

### MEM\_READ\_REP

Response event for the `mem_read` sensor command.

**Platforms:**

**Sample Event:**

```
{
  "MEMORY_DUMP": "TGltYU...",
  "PROCESS_ID": 745
}

```

### MEM\_STRINGS\_REP

Response event for the `mem_strings` sensor command. The response will contain two arrays of arrays, `STRINGSA` and `STRINGSW`.

**Platforms:**

**Sample Event:**

```
{
    "PROCESS_ID" : 745,
    "STRINGSA" : [
        [
            0 : "/lib64/ld-linux-x86-64.so.2",
            1 : "__gmon_start__"
        ]
    ]
}

```

---

### MODULE\_LOAD

Generated when a module (like DLL on Windows) is loaded in a process.

**Platforms:**

```
{
  "MEMORY_SIZE": 241664,
  "PROCESS_ID": 2904,
  "FILE_PATH": "C:\\Windows\\System32\\imm32.dll",
  "MODULE_NAME": "imm32.dll",
  "TIMESTAMP": 1468335264989,
  "BASE_ADDRESS": 140715814092800
}

```

---

### NETSTAT\_REP

Response from a  `netstat` command to list active network sockets.

**Platforms:**

**Sample Event:**

```
{
  "FRIENDLY": 0,
  "NETWORK_ACTIVITY": [
    {
      "DESTINATION": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 0
      },
      "PROCESS_ID": 856,
      "PROTOCOL": "tcp4",
      "SOURCE": {
        "IP_ADDRESS": "0.0.0.0",
        "PORT": 135
      }
    }
  ]
}

```

---

### NETWORK\_CONNECTIONS

List of recent network connections performed by a process.

**Platforms:**

```
{
  "NETWORK_ACTIVITY": [
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50396
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.214.49.56",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50397
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "189.247.166.18",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50398
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.217.70.67",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50399
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "104.110.238.53",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50400
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "23.214.49.56",
        "PORT": 80
      }
    },
    {
      "SOURCE": {
        "IP_ADDRESS": "172.16.223.138",
        "PORT": 50401
      },
      "IS_OUTGOING": 1,
      "DESTINATION": {
        "IP_ADDRESS": "204.79.197.203",
        "PORT": 80
      }
    }
  ],
  "HASH": "2de228cad2e542b2af2554d61fab5463ecbba3ff8349ba88c3e48637ed8086e9",
  "COMMAND_LINE": "C:\\WINDOWS\\system32\\msfeedssync.exe sync",
  "PROCESS_ID": 6968,
  "FILE_IS_SIGNED": 1,
  "USER_NAME": "WIN-5KC7E0NG1OD\\dev",
  "FILE_PATH": "C:\\WINDOWS\\system32\\msfeedssync.exe",
  "PARENT_PROCESS_ID": 1892
}

```

---

### NEW\_DOCUMENT

Generated when a file is created that matches a set list of locations and extensions. It indicates the file has been cached in memory and can be retrieved using the `doc_cache_get` task.

The following file patterns are considered "documents":

* `.bat`
* `.js`
* `.ps1`
* `.sh`
* `.py`
* `.exe`
* `.scr`
* `.pdf`
* `.doc`
* `.docm`
* `.docx`
* `.ppt`
* `.pptm`
* `.pptx`
* `.xlt`
* `.xlsm`
* `.xlsx`
* `.vbs`
* `.rtf`
* `.hta`
* `.lnk`
* `.xsl`
* `.com`
* `.png`
* `.jpg`
* `.asp`
* `.aspx`
* `.php`
* `\windows\system32\`

**Platforms:**

```
{
  "FILE_PATH": "C:\\Users\\dev\\Desktop\\evil.exe",
  "TIMESTAMP": 1468335816308,
  "HASH": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}

```

---

### NEW\_NAMED\_PIPE

This event is emitted when a new Named Pipe is created by a process.

**Platforms:**

```
{
  "FILE_PATH": "\\Device\\NamedPipe\\LOCAL\\mojo.6380.1072.2134013463507075011",
  "PROCESS_ID": 6380
}

```

---

### NEW\_PROCESS

Generated when a new process starts.

**Platforms:**

```
{
  "PARENT": {
    "PARENT_PROCESS_ID": 7076,
    "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\Common7\\IDE\\devenv.exe\"  ",
    "MEMORY_USAGE": 438730752,
    "PROCESS_ID": 5820,
    "THREADS": 39,
    "FILE_PATH": "C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\Common7\\IDE\\devenv.exe",
    "BASE_ADDRESS": 798949376
  },
  "PARENT_PROCESS_ID": 5820,
  "COMMAND_LINE": "-q  -s {0257E42D-7F05-42C4-B402-34C1CC2F2EAD} -p 5820",
  "FILE_PATH": "C:\\Program Files (x86)\\Microsoft Visual Studio 12.0\\VC\\vcpackages\\VCPkgSrv.exe",
  "PROCESS_ID": 1080,
  "THREADS": 9,
  "MEMORY_USAGE": 8282112,
  "TIMESTAMP": 1456285660,
  "BASE_ADDRESS": 4194304
}

```

---

### NEW\_REMOTE\_THREAD

Generated when a thread is created by a process in another process. This is often used by malware during various forms of code injection.

In this case, the process id `492` created a thread (with id `9012`) in the process id `7944`. The parent process is also globally uniquely identified by the `routing/parent` and the process where the thread was started is globally uniquely identified by the `routing/target` (not visible here).

**Platforms:**

```
{
  "THREAD_ID": 9012,
  "PROCESS_ID": 7944,
  "PARENT_PROCESS_ID": 492
}

```

---

### NEW\_TCP4\_CONNECTION

Generated when a new TCPv4 connection is established, either inbound or outbound.

**Platforms:**

```
{
  "PROCESS_ID": 6788,
  "DESTINATION": {
    "IP_ADDRESS": "172.16.223.219",
    "PORT": 80
  },
  "STATE": 5,
  "TIMESTAMP": 1468335512047,
  "SOURCE": {
    "IP_ADDRESS": "172.16.223.163",
    "PORT": 63581
  }
}

```

---

### NEW\_TCP6\_CONNECTION

Generated when a new TCPv6 connection is established, either inbound or outbound.

**Platforms:**

---

### NEW\_UDP4\_CONNECTION

Generated when a new UDPv4 socket "connection" is established, either inbound or outbound.

**Platforms:**

```
{
  "TIMESTAMP": 1468335452828,
  "PROCESS_ID": 924,
  "IP_ADDRESS": "172.16.223.163",
  "PORT": 63057
}

```

---

### NEW\_UDP6\_CONNECTION

Generated when a new UDPv6 socket "connection" is established, either inbound or outbound.

**Platforms:**

---

### OPEN\_NAMED\_PIPE

This event is emitted when an existing Named Pipe is opened by a process.

**Platforms:**

```
{
  "FILE_PATH": "\\Device\\NamedPipe\\lsass",
  "PROCESS_ID": 2232
}

```

---

### OS\_AUTORUNS\_REP

Response from an `os_autoruns` request.

**Platforms:**

**Sample Event:**

```
{
  "TIMESTAMP": 1456194620,
  "AUTORUNS": [
    {
      "REGISTRY_KEY": "Software\\Microsoft\\Windows\\CurrentVersion\\Run\\VMware User Process",
      "FILE_PATH": "\"C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe\" -n vmusr",
      "HASH": "036608644e3c282efaac49792a2bb2534df95e859e2ddc727cd5d2e764133d14"
    }
  ]
}

```

### OS\_DRIVERS\_REP

Response from an `os_drivers` request.

**Platforms:**

**Sample Event:**

```
{
  "SVCS": [
    {
      "PROCESS_ID": 0,
      "SVC_TYPE": 1,
      "SVC_NAME": "1394ohci",
      "SVC_STATE": 1,
      "HASH": "9ecf6211ccd30273a23247e87c31b3a2acda623133cef6e9b3243463c0609c5f",
      "SVC_DISPLAY_NAME": "1394 OHCI Compliant Host Controller",
      "EXECUTABLE": "\\SystemRoot\\System32\\drivers\\1394ohci.sys"
    }
  ]
}

```

### OS\_KILL\_PROCESS\_REP

Response from an `os_kill_process` request.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0,
  "PROCESS_ID": 579
}

```

### OS\_PACKAGES\_REP

List of packages installed on the system. This is currently Windows only but will be expanded to MacOS and Linux in the future.

**Platforms:**

**Sample Event:**

```
"PACKAGES": [
  {
    "PACKAGE_NAME": "Microsoft Windows Driver Development Kit Uninstall"
  }
]

```

### OS\_PROCESSES\_REP

Response from an `os_process` request.

**Platforms:**

**Sample Event:**

```
{
  "PROCESSES": [
    {
      "COMMAND_LINE": "/sbin/init",
      "FILE_PATH": "/usr/lib/systemd/systemd",
      "HASH": "477209848fabcaf52c060d98287f880845cb07fc9696216dbcfe9b6ea8e72bcd"
    }
  ]
}

```

### OS\_RESUME\_REP

Response from an `os_resume` request.

**Platforms:**

### OS\_SERVICES\_REP

Response from an `os_services` request.

**Platforms:**

**Sample Event:**

```
{
  "SVCS": [
    {
      "PROCESS_ID": 0,
      "SVC_TYPE": 32,
      "DLL": "%SystemRoot%\\System32\\AJRouter.dll",
      "SVC_NAME": "AJRouter"
    }
  ]
}

```

### OS\_SUSPEND\_REP

Response from an `os_suspend` request.

**Platforms:**

### OS\_USERS\_REP

Response from an `os_users` request.

**Platforms:**

**Sample Event:**

```
{
  "USERS": [
    {
      "USER_NAME": "Administrator"
    }
  ]
}

```

### OS\_VERSION\_REP

Response from an `os_version` request.

**Platforms:**

**Sample Event:**

```
{
  "BUILD_NUMBER": 20348
}

```

---

### PCAP\_LIST

\_INTERFACES\_REP
 Response from a `pcap_ifaces` request.

**Platforms:**

**Sample Event:**

```
{
  "INTERFACE": [
    {
      "NAME": "ens4",
      "IPV4": ["10.128.15.198"]
    }
  ]
}

```

---

### PROCESS\_ENVIRONMENT

Generated when a process starts. It lists all environment variables associated with that new process.

**Platforms:**

```
{
  "ENVIRONMENT_VARIABLES": [
    "LANG=en_US.UTF-8",
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "NOTIFY_SOCKET=/run/systemd/notify",
    "LISTEN_PID=18950",
    "LISTEN_FDS=2"
  ],
  "PROCESS_ID": 13463
}

```

---

### RECEIPT

This event is used as a generic response to some commands. The contents of a `RECEIPT` event usually contain an `ERROR` code that you can use to determine if the command was successful (`ERROR` codes can be explored [here](/v2/docs/reference-error-codes)). It's often a good idea to issue the original command with an `investigation_id` which will get echoed in the `RECEIPT` related to that command to make it easier to track.

**Platforms:**

---

### REGISTRY\_CREATE

This event is generated whenever a registry key / value is created on a Windows OS.

**Platforms:**

```
{
  "PROCESS_ID":  764,
  "REGISTRY_KEY":   "\\REGISTRY\\A\\{fddf4643-a007-4086-903e-be998801d0f7}\\Events\\{8fb5d848-23dc-498f-ac61-84b93aac1c33}"
}

```

---

### REGISTRY\_DELETE

This event is generated whenever a registry key / value is deleted on a Windows OS.

**Platforms:**

```
{
  "PROCESS_ID":  764,
  "REGISTRY_KEY":   "\\REGISTRY\\A\\{fddf4643-a007-4086-903e-be998801d0f7}\\Events\\{8fb5d848-23dc-498f-ac61-84b93aac1c33}"
}

```

---

### REGISTRY\_LIST\_REP

This event is generated in response to the `reg_list` command to list keys and values in a registry key.

**Platforms:**

**Sample Event:**

```
{
    "REGISTRY_KEY": [
      "ActiveState"
    ],
    "ROOT": "hklm\\software",
    "REGISTRY_VALUE": [
      {
        "TYPE": 4,
        "NAME": "Order"
      }
    ],
    "ERROR": 0
}

```

---

### REGISTRY\_WRITE

This event is generated whenever a registry value is written to on a Windows OS.

The `REGISTRY_VALUE` contains the first 16 bytes of the value written to the registry. If this value is a valid ASCII or Unicode string, the value will be as-is. On the other hand if the value is binary data, it will be a base64 encoded string, see examples below.

The `SIZE` is the size value used in the original registry write call. The `TYPE` is the Windows data type of the entry written as per [Microsoft's definition](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/25cce700-7fcf-4bb6-a2f3-0f6d08430a55).

**Platforms:**

Valid string payload:

```
{
  "PROCESS_ID":1820,
  "REGISTRY_KEY":"\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows Defender\\Diagnostics\\LastKnownGoodPlatformLocation",
  "REGISTRY_VALUE":"C:\\Progr",
  "SIZE":1,
  "TYPE":1,
}

```

Binary payload:

```
{
  "PROCESS_ID": 1700,
  "REGISTRY_KEY": "\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Diagnostics\\DiagTrack\\HeartBeats\\Default\\LastHeartBeatTime",
  "REGISTRY_VALUE": "bMPGjjDM1wE=","SIZE": 11,
  "TYPE": 11
}

```

---

### REJOIN\_NETWORK

Emitted after a sensor is allowed network connectivity again (after it was previously segregated). An error code of 0 indicates success.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0
}

```

---

### REMOTE\_PROCESS\_HANDLE

Generated whenever a process opens a handle to another process with access flags like `VM_READ`, `VM_WRITE`, or `PROCESS_CREATE_THREAD`.

The `ACCESS_FLAGS` is the access mask as defined [here](https://docs.microsoft.com/en-us/windows/desktop/procthread/process-security-and-access-rights).

**Platforms:**

```
{
  "ACCESS_FLAGS": 136208,
  "PARENT_PROCESS_ID": 6492,
  "PROCESS_ID": 2516
}

```

---

### SEGREGATE\_NETWORK

Emitted when a sensor is segregated (isolated) from the network using the `segregate_network` command. An error code of 0 indicates success.

**Platforms:**

**Sample Event:**

```
{
  "ERROR": 0
}

```

---

### SENSITIVE\_PROCESS\_ACCESS

Generated when a process gains sensitive access to operating system processes like `lsass.exe` on Windows.

Note

SENSITIVE\_PROCESS\_ACCESS currently is only emitted for processes accessing `lsass.exe` on Windows.

**Platforms:**

```
{
  "EVENTS": [
    {
      "event": {
        "COMMAND_LINE": "C:\\WINDOWS\\system32\\lsass.exe",
        "FILE_PATH": "C:\\WINDOWS\\system32\\lsass.exe",
        "PARENT_PROCESS_ID": 484,
        "PROCESS_ID": 636,
        "THREADS": 12,
        "USER_NAME": "BUILTIN\\Administrators"
      }
    }
  ]
}

```

---

### SERVICE\_CHANGE

Generated when a Service is changed.

**Platforms:**

```
{
  "PROCESS_ID": 0,
  "SVC_TYPE": 32,
  "DLL": "%SystemRoot%\\system32\\wlidsvc.dll",
  "SVC_NAME": "wlidsvc",
  "SVC_STATE": 1,
  "HASH": "b37199495115ed423ba99b7317377ce865bb482d4e847861e871480ac49d4a84",
  "SVC_DISPLAY_NAME": "Microsoft Account Sign-in Assistant",
  "TIMESTAMP": 1467942600540,
  "EXECUTABLE": "%SystemRoot%\\system32\\svchost.exe -k netsvcs"
}

```

---

### SEGREGATE\_NETWORK

Emitted when a sensor is segregated (isolated) from the network using the `segregate_network` command.

**Platforms:**

---

### SSH\_LOGIN

Generated when a user logs in via SSH.

**Platforms:**

```
{
  "USER_NAME": "root",
  "TIMESTAMP": 1468335816308
}

```

---

### SELF\_TEST

Internal event to manually request a power-on-self-test (POST) from the sensor.

---

### SHUTTING\_DOWN

Event generated when the sensor shuts down. Note: this event may not be observed if the host shuts down abruptly or too quickly.

**Platforms:**

**Event Data**

| Field | Type | Notes |
| --- | --- | --- |
| ts | Epoch timestamp |  |

**Sample Event:**

```
{
  "SHUTTING_DOWN": {
    "ts": 1455674775
  }
}

```

---

### SSH\_LOGOUT

Generated when a user logs out via SSH.

**Platforms:**

```
{
  "USER_NAME": "root",
  "TIMESTAMP": 1468335916308
}

```

---

### STARTING\_UP

Event generated when the sensor starts.

**Platforms:**

**Event Data**

| Field | Type | Notes |
| --- | --- | --- |
| ts | Epoch timestamp |  |

**Sample Event:**

```
{
  "STARTING_UP": {
    "ts": 1455674775
  }
}

```

---

### TERMINATE\_PROCESS

Generated when a process exits.

**Platforms:**

```
{
  "PARENT_PROCESS_ID": 5820,
  "TIMESTAMP": 1456285661,
  "PROCESS_ID": 6072
}

```

---

### TERMINATE\_TCP4\_CONNECTION

Generated when a TCPv4 connection terminates.

```
{
  "DESTINATION": {
    "IP_ADDRESS": "61.55.252.93",
    "PORT": 443
  },
  "PROCESS_ID": 4784,
  "SOURCE": {
    "IP_ADDRESS": "172.16.223.138",
    "PORT": 50145
  }
}

```

---

### TERMINATE\_TCP6\_CONNECTION

Generated when a TCPv6 connection terminates.

---

### TERMINATE\_UDP4\_CONNECTION

Generated when a UDPv4 socket terminates.

---

### TERMINATE\_UDP6\_CONNECTION

Generated when a UDPv6 socket terminates.

---

### THREAD\_INJECTION

This event is generated when the sensor detects what looks like a thread injection into a remote process.

**Platforms:**

```
{
  "event": {
    "EVENTS": [
      {
        "event": {
          "ACCESS_FLAGS": 2097151,
          "PARENT_PROCESS_ID": 5380,
          "PROCESS_ID": 4276,
          "SOURCE": {
            "BASE_ADDRESS": 140701160243200,
            "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --continue-active-setup",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "HASH": "c47fc20231ffc1e3befef952478363bff96cf3af1f36da4bd1129c8ed0e17fdb",
            "MEMORY_USAGE": 5881856,
            "PARENT_ATOM": "df4e951a09e365cb46c36c11659ee556",
            "PARENT_PROCESS_ID": 5972,
            "PROCESS_ID": 5380,
            "THIS_ATOM": "37b57d228af708b25d097f32659ee557",
            "THREADS": 3,
            "TIMESTAMP": 1704912214704,
            "USER_NAME": "WINDOWS-SERVER-\\whitney"
          },
          "TARGET": {
            "COMMAND_LINE": "C:\\Windows\\system32\\sppsvc.exe",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Windows\\system32\\sppsvc.exe",
            "HASH": "1ca5b9745872748575c452e456966b8ed1c4153757e9f4faf6f86c78c53d4ae8",
            "MEMORY_USAGE": 6156288,
            "PARENT_ATOM": "74be005ef68f6edb8682d972659ee024",
            "PARENT_PROCESS_ID": 628,
            "PROCESS_ID": 4276,
            "THIS_ATOM": "fe1dee93442392ea97becdad659ee516",
            "THREADS": 3,
            "TIMESTAMP": 1704912150174,
            "USER_NAME": "NT AUTHORITY\\NETWORK SERVICE"
          }
        },
        "routing": {
          "arch": 2,
          "did": "",
          "event_id": "d61caa47-225a-4f6a-9f3a-6094cdb3c383",
          "event_time": 1704912219717,
          "event_type": "REMOTE_PROCESS_HANDLE",
          "ext_ip": "104.198.223.172",
          "hostname": "windows-server-2022-bc76d608-9d83-4c6c-bdd5-f86bbd385a94-0.c.lc-demo-infra.internal.",
          "iid": "3c5c33e6-daaf-4029-be0b-94f50b86777e",
          "int_ip": "10.128.15.197",
          "moduleid": 2,
          "oid": "bc76d608-9d83-4c6c-bdd5-f86bbd385a94",
          "parent": "37b57d228af708b25d097f32659ee557",
          "plat": 268435456,
          "sid": "ccd0c386-88c1-4f8d-954c-581a95a1cc34",
          "tags": [
            "windows"
          ],
          "target": "fe1dee93442392ea97becdad659ee516",
          "this": "87509849fc608bce8a236f49659ee55b"
        }
      },
      {
        "event": {
          "PARENT_PROCESS_ID": 5380,
          "PROCESS_ID": 4276,
          "SOURCE": {
            "BASE_ADDRESS": 140701160243200,
            "COMMAND_LINE": "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --continue-active-setup",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "HASH": "c47fc20231ffc1e3befef952478363bff96cf3af1f36da4bd1129c8ed0e17fdb",
            "MEMORY_USAGE": 5881856,
            "PARENT_ATOM": "df4e951a09e365cb46c36c11659ee556",
            "PARENT_PROCESS_ID": 5972,
            "PROCESS_ID": 5380,
            "THIS_ATOM": "37b57d228af708b25d097f32659ee557",
            "THREADS": 3,
            "TIMESTAMP": 1704912214704,
            "USER_NAME": "WINDOWS-SERVER-\\whitney"
          },
          "TARGET": {
            "COMMAND_LINE": "C:\\Windows\\system32\\sppsvc.exe",
            "FILE_IS_SIGNED": 1,
            "FILE_PATH": "C:\\Windows\\system32\\sppsvc.exe",
            "HASH": "1ca5b9745872748575c452e456966b8ed1c4153757e9f4faf6f86c78c53d4ae8",
            "MEMORY_USAGE": 6156288,
            "PARENT_ATOM": "74be005ef68f6edb8682d972659ee024",
            "PARENT_PROCESS_ID": 628,
            "PROCESS_ID": 4276,
            "THIS_ATOM": "fe1dee93442392ea97becdad659ee516",
            "THREADS": 3,
            "TIMESTAMP": 1704912150174,
            "USER_NAME": "NT AUTHORITY\\NETWORK SERVICE"
          },
          "THREAD_ID": 3672
        },
        "routing": {
          "arch": 2,
          "did": "",
          "event_id": "ece7d85e-a43c-49d3-bc9a-28ace6dc1b02",
          "event_time": 1704912219967,
          "event_type": "NEW_REMOTE_THREAD",
          "ext_ip": "104.198.223.172",
          "hostname": "windows-server-2022-bc76d608-9d83-4c6c-bdd5-f86bbd385a94-0.c.lc-demo-infra.internal.",
          "iid": "3c5c33e6-daaf-4029-be0b-94f50b86777e",
          "int_ip": "10.128.15.197",
          "moduleid": 2,
          "oid": "bc76d608-9d83-4c6c-bdd5-f86bbd385a94",
          "parent": "37b57d228af708b25d097f32659ee557",
          "plat": 268435456,
          "sid": "ccd0c386-88c1-4f8d-954c-581a95a1cc34",
          "tags": [
            "windows"
          ],
          "target": "fe1dee93442392ea97becdad659ee516",
          "this": "b30a499edf9ec2e424b07d20659ee55b"
        }
      }
    ]
  }
  "ts": "2024-01-10 18:43:39"
}

```

---

### USER\_LOGIN

Generated when a user logs in to the operating system.

**Platforms:**

---

### USER\_LOGOUT

Generated when a user logs out of the operating system.

**Platforms:**

---

### USER\_OBSERVED

Generated the first time a user is observed on a host.

**Platforms:**

```
{
  "TIMESTAMP": 1479241363009,
  "USER_NAME": "root"
}

```

---

### VOLUME\_MOUNT

This event is generated when a volume is mounted.

**Platforms:**

```
{
  "VOLUME_PATH": "E:",
  "DEVICE_NAME": "\\Device\\HarddiskVolume3"
}

```

---

### VOLUME\_UNMOUNT

This event is generated when a volume is unmounted.

**Platforms:**

```
{
  "VOLUME_PATH": "/Volumes/RECOVERY",
  "VOLUME_NAME": "/dev/disk2s1"
}

```

---

### YARA\_DETECTION

Generated when a YARA scan finds a match.

**Platforms:**

```
{
  "RULE_NAME": "malware_detection_rule",
  "FILE_PATH": "C:\\malicious.exe",
  "HASH": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}

```

---

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Endpoint Detection & Response

---

# Query Console

# LCQL Examples
LimaCharlie Query Language (LCQL) lets you write well-structured queries to search across telemetry within LimaCharlie. The following examples can help you perform targeted searches or hunts across your telemetry, as well as modify them to build your own. Example queries are sorted by *source*, however can be adjusted for your environment.

Got a Unique Query?

If you've written a unique query or have one you'd like to share with the community, please join us in the [LimaCharlie Community Slack](https://slack.limacharlie.io)!

## General Queries

Search *all* event types across *all* Windows sytems for a particular string showing up in *any* field.
`-24h | plat == windows | * | event/* contains 'psexec'`

## GitHub Telemetry

GitHub logs can be an excellent source of telemetry to identify potential repository or account abuse or misuse. When ingested properly, GitHub log data can be observed via `plat == github`.

### GitHub Protected Branch Override

Show me all the GitHub branch protection override (force pushing to repo without all approvals) in the past 12h that came from a user outside the United States, with the repo, user and number of infractions.

`-12h | plat == github | protected_branch.policy_override | event/public_repo is false and event/actor_location/country_code is not "us" | event/repo as repo event/actor as actor COUNT(event) as count GROUP BY(repo actor)`

which could result in:

```
| actor    |   count | repo                               |
|----------|---------|------------------------------------|
| mXXXXXXa |      11 | acmeCorpCodeRep/customers          |
| aXXXXXXb |      11 | acmeCorpCodeRep/analysis           |
| cXXXXXXd |       3 | acmeCorpCodeRep/devops             |

```

## Network Telemetry

Network details recorded on endpoints, such as new connections or DNS requests, allow for combined insight. We can also query this data for aggregate details, and display data in an easily-consumed manner.

### Domain Count

Show me all domains resolved by Windows hosts that contain "google" in the last 10 minutes and the number of times each was resolved.

`-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)`

which could result in:

```
|   count | domain                     |
|---------|----------------------------|
|      14 | logging.googleapis.com     |
|      36 | logging-alv.googleapis.com |

```

### Domain Prevalence

Show me all domains resolved by Windows hosts that contain "google" in the last 10 minutes and the number of unique Sensors that have resolved them.

`-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

which could result in:

```
|   count | domain                     |
|---------|----------------------------|
|       4 | logging.googleapis.com     |
|       3 | logging-alv.googleapis.com |

```

## Process Activity

### Unsigned Binaries

Grouped and counted.
`-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash event/ORIGINAL_FILE_NAME as OriginalFileName COUNT_UNIQUE(Hash) as Count GROUP BY(Path Hash OriginalFileName)`

### Process Command Line Args

`-1h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "psexec" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host`

### Stack Children by Parent

`-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT_UNIQUE(event) as count GROUP BY(parent child)`

## Windows Event Log (WEL)

When ingested with EDR telemetry, or as a separate Adapter, `WEL` type events are easily searchable via LimaCharlie. Sample queries are organized alphabetically, with threat/technique details provided where applicable.

### %COMSPEC% in Service Path

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath contains "COMSPEC"`

### Overpass-the-Hash

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" and event/EVENT/EventData/LogonProcess == "seclogo"`

### Taskkill from a Non-System Account

*Requires process auditing to be enabled*

`-12h | plat == windows | WEL | event/EVENT/System/EventID == "4688" and event/EVENT/EventData/NewProcessName contains "taskkill" and event/EVENT/EventData/SubjectUserName not ends with "!"`

### Logons by Specific LogonType

`-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "10"`

### Stack/Count All LogonTypes by User

`-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/LogonType AS LogonType event/EVENT/EventData/TargetUserName as UserName COUNT_UNIQUE(event) as Count GROUP BY(UserName LogonType)`

### Failed Logons

`-1h | plat==windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SrcIP event/EVENT/EventData/LogonType as LogonType event/EVENT/EventData/TargetUserName as Username event/EVENT/EventData/WorkstationName as SrcHostname`

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Detection & Response

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

# LimaCharlie Query Language
Beta Feature

LCQL is currently in Beta, and features may change in the future.

LimaCharlie Query Language (LCQL) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie. Telemetry ingested via EDR sensors or adapters are searchable via LCQL, and can be searched en masse. Sample use cases for LCQL include:

* Analyze your entire, multi-platform fleet for network connections of interest.
* Search across all Windows Event Logs for unique user activity.
* Look at all Linux systems for specific package installation events.
* Analyze all volume mounts and unmounts on macOS devices
* And many more!!!

Querying the past 30 days within LimaCharlie is free.

Queries can also be saved by clicking the `Save` button. To save, view, or edit saved queries, users will need to be granted appropriate permissions:

* `query.del` - Delete saved queries
* `query.get` - Get saved queries
* `query.get.mtd` - Get saved queries metadata
* `query.set` - Set saved queries
* `query.set.mtd`- Set saved queries metadata

The steps below walk you through creating your own LCQL queries. If you're looking for samples or LCQL inspiration, check out our [LCQL Examples](/v2/docs/lcql-examples) page.

## Building LimaCharlie Queries

LCQL queries contain 4 components with a 5th optional one, each component is separated by a pipe (`|`):

1. **Timeframe**: the time range the query applies to. This can be either a single offset in the past like `-1h` or `-30m`. Or it can be a date time range like `2022-01-22 10:00:00 to 2022-01-25 14:00:00`.
2. **Sensors**: the set of sensors to query. This can be either `*` for all sensors, a list of space separated SIDs like `111-... 222-... 333-...`, or it can be a [sensor selector](/v2/docs/reference-sensor-selector-expressions) like `plat == windows`.  (Note: a full list of platform types can be found in the [ID Schema Reference](/v2/docs/reference-id-schema))
3. **Events**: the list of events to include in the query, space separated like `NEW_PROCESS DNS_REQUEST`, or a `*` to go over all event types.
4. **Filter**: the actual query filter. The filters are a series of statements combined with " and " and " or " that can be associated with parenthesis (`()`). String literals, when used, can be double-quoted to be case insensitive or single-quoted to be case sensitive. Selectors behave like  rules, for example: `event/FILE_PATH`.

The currently supported filter operators are listed below:

| operator | example |
| --- | --- |
| `is` or `==` | `event/FILE_PATH is "c:\windows\calc.exe"` |
| `is not` or `!=` | `event/FILE_IS_SIGNED != 0` |
| `contains` | `event/FILE_PATH contains 'evil'` |
| `not contains` | `event/FILE_PATH not contains 'system32'` |
| `matches` | `event/FILE_PATH matches ".*system[0-9a-z].*"` |
| `not matches` |  |
| `starts with` | `event/FILE_PATH starts with "c:\windows"` |
| `not starts with` |  |
| `ends with` | `event/FILE_PATH ends with '.eXe'` |
| `not ends with` |  |
| `cidr` | `event/NETWORK_CONNECTIONS/IP_ADDRESS cidr "10.1.0.0/16"` |
| `is lower than` | `event/NETWORK_CONNECTIONS/PORT is lower than 1024` |
| `is greater than` |  |
| `is platform` | `is platform "windows"` |
| `is not platform` | `is not platform "linux"` |
| `is tagged` | `is tagged "vip"` |
| `is not tagged` |  |
| `is public address` | `event/NETWORK_CONNECTIONS/IP_ADDRESS is public address` |
| `is private address` |  |
| `scope` | `event/NETWORK_CONNECTIONS scope (event/IP_ADDRESS is public address and event/PORT is 443)` |
| `with child` / `with descendant` / `with events` | `event/FILE_PATH contains "evil" with child (event/COMMAND_LINE contains "powershell")` |

5. Projection (optional): a list of fields you would like to extract from the results with a possible alias, like: `event/FILE_PATH as path event/USER_NAME AS user_name event/COMMAND_LINE`. The Projection can also support a grouping functionality by adding `GROUP BY(field1 field2 ...)` at the end of the projection statement.

When grouping, all fields being projected must either be in the `GROUP BY` statement, or have an aggregator modifier. An aggregator modifer is, for example, `COUNT( host )` or `COUNT_UNIQUE( host )` instead of just `host`.

A full example with grouping is:

`-1h | * | DNS_REQUEST | event/DOMAIN_NAME contains "apple" | event/DOMAIN_NAME as dns COUNT_UNIQUE(routing/hostname) as hostcount GROUP BY(dns host)`

which would give you the number of hosts having resolved a domain containing `apple`, grouped by domain.

All of this can result in a query like:

`-30m | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell" | event/COMMAND_LINE as cli event/FILE_PATH as path routing/hostname as host`

OR

`-30m | plat == windows | * | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`

Projection Syntax

Note: There is no space between `BY` and the `(` opening of the parentheses in a projection.

Example: `GROUP BY(dns host)` or `COUNT_UNIQUE(routing/hostname)`

## Using the CLI

The command line interface found in the Python CLI/SDK can be invoked like `limacharlie query` once installed (`pip install limacharlie`).

### Context

To streamline day to day usage, the first 3 components of the query are set seperatly and remain between queries.
 These 3 component can be set through the following commands:

1. `set_time` to set the timeframe of the query, like `set_time -3h` based on the [ParseDuration()](https://pkg.go.dev/time#ParseDuration) strings.
2. `set_sensors` to set the sensors who's data is queried, like `set_sensors plat == windows`, based on the [sensor selector](/v2/docs/reference-sensor-selector-expressions) grammar.
3. `set_events` to set the events that should be queried, space separated like `NEW_PROCESS DNS_REQUEST`. This command supports tab completion.

Once set, you can specify the last component(s): the Filter, and the Projection.

Several other commands are avaible to make your job easier:

* `set_limit_event` to set a maximum number of events to scan during the query.
* `set_output` to mirror the queries and their results to a file.
* `set_format` to display results either in `json` or `table`.
* `stats` to display the total costs incurred from the queries during this session.

### Querying

#### Paged Mode

The main method of running a query as described above (in paged mode) is to use the `q` (for "query") command.

Paged mode means that an initial subset of the results will be returned (usually in the 1000s of elements) and if you want to fetch more of the results, you can use the `n` (for "next") command to fetch the next page.

Some queries cannot be done in paged mode, like queries that do aggregation or queries that use a stateful filter (like `with child`). In those cases, all results over the entire timeline are computed.

For example:
`q event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

This command supports tab completion for elements of the query, like `event/DO` + "tab" will suggest `event/DOMAIN_NAME` or other relevant elements that exist as part of the schema.

#### Non Paged Mode

You can also force a full query over all the data (no paging) by using the "query all" (`qa`) command like:

`qa event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

#### Dry Run

To simulate running a query, use the `dryrun` command. This will query the LimaCharlie API and return to you an aproximate worst case cost for the query (assuming you fetch all pages over its entire time range).

For example:
`dryrun event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`

Endpoint Detection & Response

Command-line Interface

---

# Query Console
The **LimaCharlie Query Console** is a powerful feature within the LimaCharlie web application that enables users to interactively execute queries across their collected telemetry data using the [**LimaCharlie Query Language (LCQL)**](/v2/docs/lcql). The Query Console provides a streamlined interface to search, filter, and analyze events from multiple sources, such as EDR Sensors or telemetry from other integrated platforms. This allows security teams to easily perform targeted hunts, incident investigations, and data analysis across their fleet of devices.

Through the Query Console, users can write, execute, and save LCQL queries to explore various event types, such as network activity, process execution, and system changes. Queries can be customized for specific environments and saved for future use, offering a flexible solution for recurring investigations. Additionally, queries can be made programmatically via the REST API, allowing for automation and integration with other security workflows or platforms. Users can also leverage predefined examples or create unique queries to share with the LimaCharlie community, enhancing collaborative threat hunting and data exploration. The Query Console helps organizations gain deeper insights into their telemetry, simplifying large-scale data searches and empowering proactive security operations.

For examples and inspiration, see [LCQL Examples](/v2/docs/lcql-examples).

Endpoint Detection & Response

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Detection & Response

# Detection and Response
Detection & Response rules automate actions based on the real-time events streaming into LimaCharlie. Each rule has two YAML descriptors: one that describes what to detect, and another that describes how to respond.

Note

It's recommended to read about [Events](/v2/docs/events) before diving into  rules.

## A Basic Rule

Here's a rule that detects DNS requests to `example.com` and responds by reporting them within the Organization with a category name `DNS Hit example.com`.

```
# Detection
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
value: example.com

# Response
- action: report
  name: DNS Hit example.com

```

This rule will detect and respond to requests to `example.com` within 100ms of the `DNS_REQUEST` event occurring. It uses the `is` operator to assess if the given `value` can be found inside the `event` at the given `path`.

Want more detection examples?

For examples, check out the [Detection and Response Examples](/v2/docs/detection-and-response-examples).

## Detection

### Targets and events

Detections must specify an `event` (or `events`), and may optionally specify a `target`. Each target offers different event types. Here are the 5 possible rule targets:

* `edr` (default): telemetry events from LimaCharlie sensors
* `detection`: detections generated by other rules
* `deployment`: lifecycle events around deployment & enrollment of sensors
* `artifact`: artifacts collected via REST API or via `artifact_get` Sensor command
* `artifact_event`: lifecycle events around artifacts such as ingestion

For a full list of events with examples, see [Events Reference](/v2/docs/events).

Most of this page focuses on `edr` events. For information about other targets, see [Detection on Alternate Targets](/v2/docs/detection-on-alternate-targets).

#### Detections against Adapter events

Similar to EDR telemetry, data received via Adapters are observable via Detection & Response rules. D&R rules that action on Adapter-based data are written the same way, with event and operator qualifiers and response actions based on successful detections.

Depending on the type of adapter, you can reference adapter data directly via the `platform` [sensor selector](/v2/docs/reference-sensor-selector-expressions) (e.g. `aws`, `msdefender`, `crowdstrike`, etc.)

### Operators

Detections must specify an `op` (logical operator). The types of operators used are a good indicator for how complex the rule will be.

Here's a simple detection that uses a single `is windows` operator to detect a Windows sensor connecting to the Internet:

```
event: CONNECTED
op: is windows

```

And here's a more complex detection that uses the `and` operator to detect a non-Windows sensor that's making a DNS request to example.com.

```
event: DNS_REQUEST
op: and
rules:
- op: is windows
  not: true
- op: is
  path: event/DOMAIN_NAME
  value: example.com

```

There are 3 operators here:

1. The `and` operator evaluates nested `rules` and will only itself be `true` if both of the rules inside it are `true`
2. The `is windows` operator is accompanied by the `not` parameter, reversing the matching outcome and effectively saying "anything but windows"
3. The `is` operator is comparing the `value` 'example.com' to the content of the event at the given `path`

Each operator may have parameters alongside it. Some parameters, such as `not`, are useable on all operators. Most operators have required parameters specific to them.

> For a full list of operators and their usage, see [Reference: Operators](/v2/docs/detection-logic-operators).

### Paths

The `path` parameter is used commonly in several operators to specify which part of the event should be evaluated.

Here's an example of a standard JSON `DNS_REQUEST` event from a sensor:

```
{
  "event": {
    "DNS_TYPE": 1,
    "TIMESTAMP": 1456285240,
    "DNS_FLAGS": 0,
    "DOMAIN_NAME": "example.com"
  },
  "routing": {
    "event_type": "DNS_REQUEST",
    "oid": "8cbe27f4-agh1-4afb-ba19-138cd51389cd",
    "sid": "d3d17f12-eecf-5287-b3a1-bf267aabb3cf",
    "hostname": "test-host-123"
    // ...and other standardized routing data
  }
}

```

This detection will match the above event's hostname:

```
event: DNS_REQUEST
op: is
path: routing/hostname # where the value lives
value: test-host-123   # the expected value at that path

```

This works a lot like file paths in a directory system. Since LimaCharlie events are always formatted with separate `event` and `routing` data, almost all paths start with either `event/` or `routing/`.

> Tip: you can visit the Timeline view of any Sensor to browse historical events and bring them directly into the D&R rule editor.

Paths may also employ the use of wildcards `*` to represent 0 or more directory levels, or `?` to represent exactly 1 directory level. This can be useful when working with events like `NETWORK_CONNECTIONS`:

```
{
  "event": {
    "NETWORK_ACTIVITY": [
      {
        "SOURCE": {
          "IP_ADDRESS": "172.16.223.138",
          "PORT": 50396
        },
        "IS_OUTGOING": 1,
        "DESTINATION": {
          "IP_ADDRESS": "23.214.49.56",
          "PORT": 80
        }
      },
      {
        "SOURCE": {
          "IP_ADDRESS": "172.16.223.138",
          "PORT": 50397
        },
        "IS_OUTGOING": 1,
        "DESTINATION": {
          "IP_ADDRESS": "189.247.166.18",
          "PORT": 80
        }
      },
      // ...there could be several connections
    ],
    "HASH": "2de228cad2e542b2af2554d61fab5463ecbba3ff8349ba88c3e48637ed8086e9",
    "COMMAND_LINE": "C:\\WINDOWS\\system32\\msfeedssync.exe sync",
    "PROCESS_ID": 6968,
    "FILE_IS_SIGNED": 1,
    "USER_NAME": "WIN-5KC7E0NG1OD\\dev",
    "FILE_PATH": "C:\\WINDOWS\\system32\\msfeedssync.exe",
    "PARENT_PROCESS_ID": 1892
  },
  "routing": { ... } // Omitted for brevity
}

```

Notice that the `NETWORK_ACTIVITY` inside this event is a list.

Here's a rule that would match a known destination IP in any of the entries within `NETWORK_ACTIVITY`:

```
event: NETWORK_CONNECTIONS
op: is
path: event/NETWORK_ACTIVITY/?/DESTINATION/IP_ADDRESS # <---
value: 189.247.166.18

```

The `?` saves us from enumerating each index within the list and instead evaluates *all* values at the indicated level. This can be very powerful when used in combination with lookups: lists of threat indicators such as known bad IPs or domains.

> To learn more about using lookups in detections, see the `lookup` [operator](/v2/docs/detection-logic-operators#lookup).

### Values

The `value` parameter is commonly used by several detection operations but can also be used by some response actions as well.

In most detections `value` will be used to specify a known value like all the previous examples on this page have done. They're also capable of referencing previously set sensor variables using `value: [[var-name]]` double square bracket syntax.

Values from events can also be forwarded in response actions using `value: <<event/FILE_PATH>>` double angle bracket syntax.

> To see how sensor variables and lookback values are used, see the `add var / del var` action in [Reference: Response Actions](/v2/docs/response-actions).

## Response

Responses are much simpler than Detections. They're a list of actions to perform upon a matching detection.

### Actions

The most common action is the `report` action, which creates a Detection that shows up in the LimaCharlie web app and passes it along to the `detections` output stream in real-time.

```
- action: report
  name: detected-something

# Example of accessing map values
- action: report
  name: Event detected by {{ .event.USER_NAME }} from {{ index (index .event.NETWORK_ACTIVITY 0) "SOURCE" "IP_ADDRESS" }}

```

Each item in the response specifies an `action` and any accompanying parameters for that `action`.

A more complex response action could include running an [endpoint agent command](/v2/docs/endpoint-agent-commands) such as `yara_scan` using a field from within the detected event. The following example looks for `NEW_DOCUMENT` events that meet certain criteria, then initiates a YARA scan against the offending file path.

Detect

```
event: NEW_DOCUMENT
op: and
rules:
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .\:\\(users|windows\\temp)\\.*
  - case sensitive: false
    op: matches
    path: event/FILE_PATH
    re: .*\.(exe|dll)

```

Respond

```
# Report is optional, but informative
- action: report
  name: Executable written to Users or Temp (yara scan)

# Initiate a sensor command to yara scan the FILE_PATH
- action: task
  command: yara_scan hive://yara/malware-rule -f "{{ .event.FILE_PATH }}"
  investigation: Yara Scan Executable
  suppression:
    is_global: false
    keys:
      - '{{ .event.FILE_PATH }}'
      - Yara Scan Executable
    max_count: 1
    period: 1m

```

Notice the use of `suppression` to prevent the same `FILE_PATH` from being scanned more than once per minute to prevent a resource runaway situation.

Which D&R Rule Triggered a Command?

To determine which D&R rule triggered a command on an endpoint, navigate to the `Platform Logs` section. If a command was triggered by a D&R rule, the audit log will show the associate rule. If the command was sent via the API, the audit logs will show the API key name.

> To learn about all possible actions, see [Reference: Response Actions](/v2/docs/response-actions).

## Putting It All Together

Let's take this knowledge and write a rule to detect something a little more interesting.

On Windows there's a command called `icacls` which can be used to modify access control lists. Let's write a rule which detects any tampering via that command.

The first thing we can do is detect any new `icacls` processes:

```
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: icacls.exe

```

And we'll set a basic response action to report the detection, too:

```
- action: report
  name: win-acl-tampering

```

If we save that, we'll start to see detections for any `icacls` processes spawning. However, not all of them will be particularly interesting from a security perspective. In this case, we only really care about invocations of `icacls` where the `grant` parameter is specified.

Let's make this rule more specific. We can do this by using the `and` operator to match multiple operators. We'll check for the string `"grant"` in the `COMMAND_LINE`, and while we're at it we'll make sure we don't bother evaluating other platforms by using the `is windows` operator.

```
event: NEW_PROCESS
op: and
rules:
- op: is windows
- op: ends with
	path: event/FILE_PATH
	value: icacls.exe
- op: contains
  path: event/COMMAND_LINE
  value: grant

```

This more specific rule means we'll see fewer false positives to look at or exclude later.

However, we still might miss some invocations of `icacls` with this detection if they use any capital letters — our operators are being evaluated with an implicit `case sensitive: true` by default. Let's turn case sensitivity off and observe the final rule:

```
# Detection
event: NEW_PROCESS
op: and
rules:
- op: is windows
- op: ends with
	case sensitive: false
	path: event/FILE_PATH
	value: icacls.exe
- op: contains
	case sensitive: false
  path: event/COMMAND_LINE
  value: grant

# Response
- action: report
  name: win-acl-tampering

```

This rule combines multiple operators to specify the exact conditions which might make an `icacls` process interesting. If it sees one, it'll report it as a `win-acl-tampering` detection which will be forwarded to Outputs and become viewable in the Detections page.

> Tip: test your rules without waiting for events! We recommend enabling the replay add-on for a better D&R rule writing experience.
>
> * Visit Timeline of a sensor and `Build D&R Rule` directly from real events
> * While drafting a rule, `Replay` an event against the rule to see if it would match
> * Replay a rule over historical events to see if any detections would have occurred

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Endpoint Detection & Response

---

# Replay
Replay allows you to run [Detection & Response (D&R) rules](/v2/docs/detection-and-response) against historical traffic.
 This can be done in a few combinations of sources:

Rule Source:

* Existing rule in the organization, by name.
* Rule in the replay request.

Traffic:

* Sensor historical traffic.
* Local events provided during request.

## Using

Using the Replay API requires the [API key](/v2/docs/api-keys) to have the following permissions:

* `insight.evt.get`

The returned data from the API contains the following:

* `responses`: a list of the actions that would have been taken by the rule (like `report`, `task`, etc).
* `num_evals`: a number of evaluation operations performed by the rule. This is a rough estimate of the performance of the rule.
* `num_events`: the number of events that were replayed.
* `eval_time`: the number of seconds it took to replay the data.

```
{
  "error": "",        // if an error occured.
  "stats": {
    "n_proc": 0,      // the number of events processed
    "n_shard": 0,     // the number of chunks the replay job was broken into
    "n_eval": 0,      // the number of operator evaluations performed
    "wall_time": 0    // the number of real-world seconds the job took
  },
  "did_match": false, // indicates if the rule matched any event at all
  "results": [],      // a list of dictionaries containing the details of actions the engine would have taken
  "traces": []        // a list of trace items to help you troubleshoot where a rule failed
}

```

### Query Language

To use Replay in [LCQL Mode](/v2/docs/lcql) (LimaCharlie Query Language), you can specify your query in the `query` parameter of the Replay Request (defined below) when using the REST interface, or you can use the LimaCharlie Python SDK/CLI's [query interface](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Query.py): `limacharlie query --help`.

### Python CLI

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a friendly way to replay data, and to do so across larger datasets by automatically splitting up your query into multiple queries that can run in parallel.

Sample command line to query one sensor:

```
limacharlie-replay --sid 9cbed57a-6d6a-4af0-b881-803a99b177d9 --start 1556568500 --end 1556568600 --rule-content ./test_rule.txt

```

Sample command line to query an entire organization:

```
limacharlie-replay --entire-org --start 1555359000 --end 1556568600 --rule-name my-rule-name

```

If specifying a rule as content with the `--rule-content`, the format should be
 in `JSON` or `YAML` like:

```
detect:
  event: DNS_REQUEST
  op: is
  path: event/DOMAIN_NAME
  value: www.dilbert.com
respond:
  - action: report
    name: dilbert-is-here

```

Instead of specifying the `--entire-org` or `--sid` flags, you may use events from a local file via the `--events` flag.

We invite you to look at the command line usage itself, as the tool evolves.

### REST API

The Replay API is available to all DataCenter locations using a per-location URL.
 To get the appropriate URL for your organization, use the REST endpoint to retrieve the URLs found [here](https://api.limacharlie.io/static/swagger/#/Organizations/getOrgURLs) named `replay`.

Having per-location URLs will allow us to guarantee that processing occurs within the geographical area you chose. Currently, some locations are NOT guaranteed to be in the same area due to the fact we are using the Google Cloud Run product which is not available globally. For these cases, processing is currently done in the United States, but as soon as it becomes available in your area, the processing will be moved transparently.

Authentication to this API works with the same JWTs as the main limacharlie.io API.

For this example, we will use the experimental datacenter's URL:

```
https://0651b4f82df0a29c.replay.limacharlie.io/

```

The API mainly works on a per-sensor basis, on a limited amount of time. Replaying for multiple sensors (or entire org), or longer time period is done through multiple parallel API calls. This multiplexing is taken care of by the Python CLI above.

To query Replay, do a `POST` with a `Content-Type` header of `application-json` and with a JSON body like:

```
{
  "oid": "",             // OID this query relates to
  "rule_source": {       // rule source information (use one of "rule_name" or "rule")
    "rule_name": "",     // pre-existing rule name to run
    "namespace": "", // default: general namespace, can also be "managed" and "service"
    "rule": {            // literal rule to run
      "detect": {},
      "respond": []
    }
  },
  "event_source": {      // event source information (use one of "sensor_events" or "events")
    "sensor_events": {   // use historical events from sensors
      "sid": "",         // sensor id to replay from, or entire org if empty
      "start_time": 0,   // start second epoch time to replay from
      "end_time": 0      // end second epoch time to replay to
    },
    "events": [{}]       // literal list of events to replay
    "stream": "" // defaults to events, can also be "audit" or "detection"
  },
  "limit_event": 0,      // optional approximate number of events to process
  "limit_eval": 0,       // optional approximate number of operator evaluations to perform
  "trace": false,        // optional, if true add trace information to response, VERY VERBOSE
  "is_dry_run": false,   // optional, if true, an estimate of the total cost of the query will be returned
  "query": ""            // optional alternative way to describe a replay query as a LimaCharlie Query Language (LCQL) query.
}

```

Like the other endpoints you can also submit a `rule_name` in the URL query if you want
 to use an existing organization rule.

You may also specify a `limit_event` and `limit_eval` parameter as integers. They will limit the number of events evaluated and the number of rule evaluations performed (approximately). If the limits are reached, the response will contain an item named `limit_eval_reached: true` and `limit_event_reached: true`.

Finally, you may also set `trace` to `true` in the request to receive a detailed trace of the rule evaluation. This is useful in the development of new rules to find where rules are failing.

## Billing

The Replay service is billed on a per event evaluated.

---

# Writing and Testing Rules
Detection & Response () Rules are similar to Google Cloud Functions or AWS Lambda.
They allow you to push D&R rules to the LimaCharlie cloud where the rules will be applied
in real-time to data coming from the sensors.

D&R rules can also be applied to [Artifact Collection](/v2/docs/artifacts), but for now we will focus
on the simple case where it is applied to Sensor events.

For a full list of all rule operators and detailed documentation see the [Detection and Response](/v2/docs/detection-and-response) section.

### Life of a Rule

D&R rules are generally applied on a per-event basis. When the rule is applied, the "detection"
component of the rule is processed to determine if it matches. If there is a match, the "response"
component is applied.

The detection is processed one step at a time, starting at the root of the detection. If the
root matches, the rule is considered to be matching.

The detection component is composed of "nodes", where each node has an operator describing the
logical evaluation. Most operators are simple, like `is`, `starts with` etc. These simple nodes
can be combined with Boolean (true/false) logic using the `and` and `or` operators, which
themselves reference a series of nodes. The `and` node matches if all the sub-nodes match, while
the `or` node matches if any one of the sub-nodes matches.

When evaluating an `or`, as soon as the first matching sub-node is found, the rest of the sub-nodes
are skipped since they will have no impact on the final matching state of the "or". Similarly, failure of a sub-node in an "and" node will immediately terminate its evaluation.

If the "detection" component is matched, then the "response" evaluation begins.

The "response" component is a list of actions that should be taken. When an action refers to a
sensor, that sensor is assumed to be the sensor the event being evaluated is coming from.

The best general strategy for D&R rules is to put the parts of the rule most likely
to eliminate the event at the beginning of the rule, so that LC may move on to the next event
as quickly as possible.

## Introduction

### Goal

The goal of is code lab will be to create a D&R rule to detect the MITRE ATT&CK framework
[Control Panel Items](https://attack.mitre.org/techniques/T1196/) execution.

### Services Used

This code lab will use the Replay service to validate and test the rule prior to pushing it to production.

## Setup and Requirements

This code lab assumes you have access to a Linux host (MacOS terminal with `brew`). This
code lab also assumes you have "owner" access to an LC Organization. If you don't have
one already, create one, this code lab is compatible with the free tier that comes with
all organizations.

### Install CLI

Interacting with LC can always be done via the [web app](https://app.limacharlie.io) but
day to day operations and automation can be done via the Command Line Interface (CLI). This
will make following this code lab easier.

Install the CLI: `pip install limacharlie --user`. If you don't have `pip` installed, install
it, the exact instructions will depend on your Linux distribution.

### Create REST API Key

We need to create an API key we can use in the CLI to authenticate with LC. To do so, go
to the REST API section of the web app.

1. In the REST API section, click the "+" button in the top right of the page.
2. Give your key a name.
3. For simplicity, click the "Select All" button to enable all permissions. Obviously this would not be a recommended in a production environment,
4. Click the copy-to-clipboard button for the new key and take note of it (pasting it in a temporary text note for example).
5. Back on the REST API page, copy the "Organization ID" at the top of the page and keep note of it like the API key in the previous step.

The Organization ID (OID) identifies uniquely your organization while the API key grants specific permissions to this organization.

### Login to the CLI

Back in your terminal, log in with your credentials: `limacharlie login`.

1. When asked for the Organization ID, paste your OID from the previous step.
2. When asked for a name for this access, you can leave it blank to set the default credentials.
3. When asked for the secret API key, enter the key you got from the previous step.

You're done! If you issue a `limacharlie dr list` you should not get any errors.

## Draft Rule

To draft our rule, open your preferred text editor and save the rule to a file, we'll call it `T1196.rule`.
The format of a rule is [YAML](https://en.wikipedia.org/wiki/YAML), if you are unfamiliar with it, there is benefit to spending a few minutes getting familiar. It won't take long as it is not overly complex.

For our rules based on the [T1196](https://attack.mitre.org/techniques/T1196/) technique, we need
to apply the following constraints:

1. It only applies to Windows.
2. The event is a module (DLL for example on Windows) loading.
3. The module loading ends with `.cpl` (control panel extension).
4. The module is loading from outside of the `C:\windows\` directory.

LC supports a lot of different event types, this means that the first thing we should strive to
do to try to make the rule fail as quickly as possible is to filter all events we don't care about.

In this case, we only care about [CODE\_IDENTITY](/v2/docs/reference-edr-events#codeidentity) events. We also know that
our rule will use more than one criteria, and those criteria will be AND-ed together because we only
want to match when they all match.

```
op: and
event: CODE_IDENTITY
rules:
  -

```

The above sets up the criteria #2 preceding it, with the AND-ing that will follow. Since the AND is at the
top of our rule, and it has an `event:` clause, it will ensure that any event processed by this rule
but is NOT a `CODE_IDENTITY` event will be skipped over right away.

Next, we should look at the other criteria, and add them to the `rules:` list, which are all the sub-nodes
that will be AND-ed together.

Criteria #1 was to limit to Windows, that's easy:

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  -

```

Next up is criteria #3 and #4. Both of those can be determined using the `FILE_PATH` component of the
`CODE_IDENTITY` event. If you are unure what those events look like, the best way to get a positive confirmation
of the structure is simply to open the Historic View, start a new process on that specific host and look for
the relevant event. If we were to do this on a Windows host, we'd get an example like this one:

```
{
    "routing": {
        "parent": "...",
        "this": "...",
        "hostname": "WIN-...",
        "event_type": "CODE_IDENTITY",
        "event_time": 1567438408423,
        "ext_ip": "XXX.176.XX.148",
        "event_id": "11111111-1111-1111-1111-111111111111",
        "oid": "11111111-1111-1111-1111-111111111111",
        "plat": 268435456,
        "iid": "11111111-1111-1111-1111-111111111111",
        "sid": "11111111-1111-1111-1111-111111111111",
        "int_ip": "172.XX.223.XXX",
        "arch": 2,
        "tags": [
            "..."
        ],
        "moduleid": 2
    },
    "ts": "2019-09-02 15:33:28",
    "event": {
        "HASH_MD5": "7812c2c0a46d1f0a1cf8f2b23cd67341",
        "HASH": "d1d59eefe1aeea20d25a848c2c4ee4ffa93becaa3089745253f9131aedc48515",
        "ERROR": 0,
        "FILE_INFO": "10.0.17134.1",
        "HASH_SHA1": "000067ac70f0e38f46ce7f93923c6f5f06ecef7b",
        "SIGNATURE": {
            "FILE_CERT_IS_VERIFIED_LOCAL": 1,
            "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows",
            "FILE_PATH": "C:\\Windows\\System32\\setupcln.dll",
            "FILE_IS_SIGNED": 1,
            "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Production PCA 2011"
        },
        "FILE_PATH": "C:\\Windows\\System32\\setupcln.dll"
    }
}

```

This means what we want is to apply rules to the `event/FILE_PATH`. First part, #3 is easy, we just want
to test for the `event/FILE_PATH` ends in `.cpl`, we can do this using the `ends with` operator.

Most operators will use a `path` and a `value`. General convention is the `path` describes
how to get to a value we want to compare within the event. So `event/FILE_PATH` says "starting in the `event`
then get the `FILE_PATH`. The `value` generally represents a value we want to compare to the element found
in the `path`. How it is compared depends on the operator.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl

```

That was easy, but we're missing a critical component! By default, D&R rules operate in a case sensitive mode.
This means that the above node we added will match `.cpl` but will NOT match `.cPl`. To fix this, we just add
the `case sensitive: false` statement.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
    case sensitive: false
  -

```

Finally, we want to make sure the `event/FILE_PATH` is NOT in the `windows` directory. To do this, we will use
a regular expression with a `matches` operator. But in this case, we want to EXCLUDE the paths that include
the `windows` directory, so we want to "invert" the match. We can do this with the `not: true` statement.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
    case sensitive: false
  - op: matches
    path: event/FILE_PATH
    re: ^.\:\\windows\\
    case sensitive: false
    not: true

```

Here we go, we're done drafting our first rule.

## Validate Rule

What we want to do now is validate the rule. If the rule validates, it doesn't mean it's correct, it
just means that the structure is correct, the operators we use are known, etc. It's the first pass at
detecting possible formatting issues or typos.

To validate, we will simply leverage the Replay service. This service can be used to test rules or replay
historical events against a rule. In this case however, we just want to start by validating.

Up until now we focused on the "detection" part of the rule. But a full rule also contains a "response"
component. So before we proceed, we'll add this structure. For a response, we will use a
simple `action: report`. The `report` creates a "detection" (alert).

```
detect:
  op: and
  event: CODE_IDENTITY
  rules:
    - op: is windows
    - op: ends with
      path: event/FILE_PATH
      value: .cpl
      case sensitive: false
    - op: matches
      path: event/FILE_PATH
      re: ^.\:\\windows\\
      case sensitive: false
      not: true
respond:
  - action: report
    name: T1196

```

Now validate: `limacharlie replay --validate --rule-content T1196.rule`

After a few seconds, you should see a response with `success: true` if the rule
validates properly.

## Test rule

### Test Plan

Now that we know our rule is generally sound, we need to test it against some events.

Our test plan will take the following approach:

1. Test a positive (a `.cpl` loading outside of `windows`).
2. Test a negative for the major criteria:

   1. Test a non-`.cpl` loading outside of `windows` does not match.
   2. Test a `.cpl` loading within `windows` does not match.
3. Test on historical data.

With this plan, #1 and #2 lend themselves well to [unit tests](https://en.wikipedia.org/wiki/Unit_testing)
while #3 can be done more holistically by using Replay to run historical events
through the rule and evaluate if there are any [false positives](https://en.wikipedia.org/wiki/False_positives_and_false_negatives).

This may be excessive for you, or for certain rules which are very simple, we leave that
evaluation to you. For the sake of this code lab, we will do a light version to demonstrate
how to do tests.

### Testing a Single Event

To test #1 and #2, let's just create some synthetic events. It's always better to use
real-world samples, but we'll leave that up to you.

Take the event sample we had in the "Draft Rule" section and copy it to two new files
we will name `positive.json`, `negative-1.json` and `negative-2.json`.

Modify the `positive.json` file by renaming the `FILE_PATH` at the bottom from
`"C:\\Windows\\System32\\setupcln.dll"` to `"C:\\temp\\System32\\setupcln.cpl"` so that
the event now describes a `.cpl` loading in the `temp` directory, which we should detect.

Then modify the `negative-1.json` file by changing the same `.dll` to `.cpl`. This should NOT
match because the path is still in the `windows` directory.

Then modify the `negative-2.json` file by changing the `windows` directory to `temp`. This
should still NOT match because it's not a `.cpl`.

Now we can run our 3 samples against the rule using Replay,

`limacharlie replay --rule-content T1196.rule --events positive.json` should output a result
indicating the event matched (by actioning the `report`) like:

```
{
  "num_evals": 4,
  "eval_time": 0.00020599365234375,
  "num_events": 1,
  "responses": [
    {
      "report": {
        "source": "11111111-1111-1111-1111-111111111111.11111111-1111-1111-1111-111111111111.11111111-1111-1111-1111-111111111111.10000000.2",
        "routing": {
...

```

`limacharlie replay --rule-content T1196.rule --events negative-1.json` should output a result
indicating the event did NOT match like:

```
{
  "num_evals": 4,
  "eval_time": 0.00011777877807617188,
  "num_events": 1,
  "responses": [],
  "errors": []
}

```

`limacharlie replay --rule-content T1196.rule --events negative-2.json` be the same as `negative-1.json`.

### Testing Historical Data

The final test is to run the rule against historical data. If you are not using an
organization on the free tier, note that the Replay API is billed on usage. In the
following step we will run against all historical data from the organization, so if
your organization is not on the free tier and it is large, there may be non-trivial
costs associated.

Running our rule against the last week of data is simple:

`limacharlie replay --rule-content T1196.rule --entire-org --last-seconds 604800`

No matches should look like that:

```
{
  "num_evals": 67354,
  "eval_time": 1107.2150619029999,
  "num_events": 222938,
  "responses": [],
  "errors": []
}
```

### Moving to Unit Tests

Once your rule is done and you’ve evaluated various events for matches, you can move these to [D&R Rules Unit Tests](/v2/docs/unit-tests) so that the tests are run during rule update.

## Publish Rule

Now is the time to push the new rule to production, the easy part.

Simply run `limacharlie dr add --rule-name T1196 --rule-file T1196.rule`
and confirm it is operational by running `limacharlie dr list`.

Amazon Web Services

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Command-line Interface

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

---

# Platform Management

# Adapters as a Service
In some cases, users may need to install the LimaCharlie Adapter with persistence, to ensure that data collection survives a reboot and/or other disruptions.

To accommodate this need, the LimaCharlie adapter can be installed as a service.

## Service Installation

### Windows

To install the Windows LimaCharlie adapter as a service, insert the `-install:<service_name>` flag in the command line, following the adapter executable name.

For example:

`./lc_adapter.exe azure_event_hub client_options.identity.installation_key=...`

would be replaced with

`./lc_adapter.exe -install:azure_collection azure_event_hub client_options.identity.installation_key=...`

This would create a service named `azure_collection` with the adapter config.

Remember, adapter configurations can be provided via two methods:

* In the command line, as part of a list of flags
* Via a YAML config file

**Note:** The service will point to `lc_adapter.exe` based on its path at the creation of the service. If you wish to move the adapter to a permanent location, please do so before creating the service.

### Linux / systemd

To install a LimaCharlie adapter as a service on a Linux system with systemd, you will need a service file, the adapter binary, and your adapter command.

#### Adapter Binary

Download one of the [adapter binaries](/v2/docs/adapter-deployment) and apply the necessary permissions:

```
wget -O /path/to/adapter-directory/lc-adapter $ADAPTER_BINARY_URL
chmod +x /path/to/adapter-directory/lc-adapter
```

#### Service File - /etc/systemd/system/limacharlie-adapter-name.service

You will replace `$ADAPTER_COMMAND` in the service file with your actual adapter command below.

```
[Unit]
Description=LC Adapter Name
After=network.target

[Service]
Type=simple
ExecStart=$ADAPTER_COMMAND
WorkingDirectory=/path/to/adapter-directory
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lc-adapter-name

[Install]
WantedBy=multi-user.target
```

#### Adapter Command

Your adapter command may differ depending on your use case--this is an example of a [file](/v2/docs/adapter-types-file) adapter to ingest logs from a JSON file.

```
/path/to/adapter-directory/lc-adapter file file_path=/path/to/logs.json client_options.identity.installation_key=<INSTALLATION KEY> client_options.identity.oid=<ORG ID> client_options.platform=json client_options.sensor_seed_key=<SENSOR SEED KEY> client_options.mapping.event_type_path=<EVENT TYPE FIELD> client_options.hostname=<HOSTNAME>
```

#### Enable and Start the Service

```
sudo systemctl enable lc-adapter-name
sudo systemctl start lc-adapter-name
sudo systemctl status lc-adapter-name
```

## Service Uninstallation

### Windows

To remove a Windows LimaCharlie Adapter service, use the `-remove:<service_name>` flag.

### Linux

If your service is running with a systemd script, you can disable and remove it with the following:

```
sudo systemctl stop lc-adapter-name
sudo systemctl disable lc-adapter-name
sudo rm /etc/systemd/system/lc-adapter-name.service
sudo rm /path/to/adapter-directory/lc-adapter
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

# LimaCharlie SDK & CLI
## Go

The Go library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

* Repo - <https://github.com/refractionPOINT/go-limacharlie>

### Getting Started

#### Authentication

You can use Client Options to declare your client/org, or you can use environment variables.

**Using Environment Variables:**

* `LC_OID`: Organization ID
* `LC_API_KEY`: your LC API KEY
* `LC_UID`: optional, your user ID

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)
    fmt.Printf("Hello, this is %s", org.GetOID())
}

```

**Using Client Options:**

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    clientOptions = limacharlie.ClientOptions{
        OID: "MY_OID",
        APIKey: "MY_API_KEY",
        UID: "MY_UID",
    }
    org, _ := limacharlie.NewOrganizationFromClientOptions(clientOptions, nil)
    fmt.Printf("Hello, this is %s", org.GetOID())
}

```

### SDK

#### Examples

```
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)

    // List all sensors
    sensors, err := org.ListSensors()
    if err != nil {
        fmt.Println(err)
    }
    for sid, sensor := range sensors {
        fmt.Printf("%s - %s", sid, sensor.Hostname)
    }

    // List D&R rules from Hive
    hiveClient := limacharlie.NewHiveClient(org)
    rules, _ := hiveClient.List(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey:  org.GetOID(),
    })
    for rule_name, _ := range rules {
        fmt.Println(rule_name)
    }

    // Add D&R rule to Hive
    enabled := true
    case_sensitive := false
    if _, err := hiveClient.Add(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "test_rule_name",
        Enabled:      &enabled,
        Data: limacharlie.Dict{
            "detect": limacharlie.Dict{
                "event":            "NEW_PROCESS",
                "op":               "is",
                "path":             "event/COMMAND_LINE",
                "value":            "whoami",
                "case sensitive":   &case_sensitive,
            },
            "respond": []limacharlie.Dict{{
                "action": "report",
                "name":   "whoami detection",
            }},
        },
    }); err != nil {
        fmt.Println(err)
    }

    // List extensions
    extensions, _ := org.Extensions()
    for _, extension_name := range extensions {
        fmt.Println(extension_name)
    }

    // Subscribe to extension
    subscription_request := org.SubscribeToExtension("binlib")
    if subscription_request != nil {
        fmt.Println(subscription_request)
    }

    // List payloads
    payloads, _ := org.Payloads()
    for payload, _ := range payloads {
        fmt.Println(payload)
    }

    // List installation keys
    installation_keys, _ := org.InstallationKeys()
    for _, key := range installation_keys {
        fmt.Println(key.Description)
    }

    // Create installation key
    key_request, _ := org.AddInstallationKey(InstallationKey{
		Description: "my-test-key",
		Tags:        []string{"tag", "another-tag"},
	})

}

```

## Python

The Python library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

* Repo - <https://github.com/refractionpoint/python-limacharlie>

### Getting Started

#### Installing

##### PyPi (pip)

The library and the CLI is available as a Python package on PyPi (<https://pypi.org/project/limacharlie/>). It can be installed using pip as shown below.

```
pip install limacharlie
```

##### Docker Image

In addition to the PyPi distribution we also offer a pre-built Docker image on DockerHub (<https://hub.docker.com/r/refractionpoint/limacharlie>).

```
docker run refractionpoint/limacharlie:latest whoami

# Using a specific version (Docker image tag matches the library version)
docker run refractionpoint/limacharlie:4.9.13 whoami

# If you already have a credential file locally, you can mount it inside the Docker container
docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami
```

#### Credentials

Authenticating to use the SDK / CLI can be done in a few ways.

**Option 1 - Logging In**
 The simplest is to login to an Organization using an [API key](https://doc.limacharlie.io/docs/documentation/docs/api_keys.md).

Use `limacharlie login` to store credentials locally. You will need an `OID` (Organization ID) and an API key, and (optionally) a `UID` (User ID), all of which you can get from the Access Management --> REST API section of the web interface.

The login interface supports named environments, or a default one used when no environment is selected.

To list available environments:

```
limacharlie use
```

Setting a given environment in the current shell session can be done like this:

```
limacharlie use my-dev-org
```

You can also specify a `UID` (User ID) during login to use a *user* API key representing
 the total set of permissions that user has (see User Profile in the web interface).

**Option 2 - Environment Variables**
 You can use the `LC_OID` and `LC_API_KEY` and `LC_UID` environment variables to replace the values used logging in. The environment variables will be used if no other credentials are specified.

### SDK

The root of the functionality in the SDK is from the `Manager` object. It holds the credentials and is tied to a specific LimaCharlie Organization.

You can authenticate the `Manager` using an `oid` (and optionally a `uid`), along with either a `secret_api_key` or `jwt` directly. Alternatively you can just use an environment name (as specified in `limacharlie login`). If no creds are provided, the `Manager` will try to use the default environment and credentials.

#### Importing

```
import limacharlie

YARA_SIG = 'https://raw.githubusercontent.com/Yara-Rules/rules/master/Malicious_Documents/Maldoc_PDF.yar'

# Create an instance of the SDK.
mgr = limacharlie.Manager()

# Get a list of all the sensors in the current Organization.
all_sensors = mgr.sensors()

# Select the first sensor in the list.
sensor = all_sensors[0]

# Tag this sensor with a tag for 10 minutes.
sensor.tag( 'suspicious', ttl = 60 * 10 )

# Send a task to the sensor (unidirectionally, not expecting a response).
sensor.task( 'os_processes' )

# Send a yara scan to that sensor for processes "evil.exe".
sensor.task( 'yara_scan -e *evil.exe ' + YARA_SIG )

```

#### Use of gevent

Note that the SDK uses the `gevent` package which sometimes has issues with other
 packages that operate at a low level in python. For example, Jupyter notebooks
 may see freezing on importing `limacharlie` and require a tweak to load:

```
{
 "display_name": "IPython 2 w/gevent",
 "language": "python",
 "argv": [
  "python",
  "-c", "from gevent.monkey import patch_all; patch_all(thread=False); from ipykernel.kernelapp import main; main()",
  "-f",
  "{connection_file}"
 ]
}

```

### Components

#### Manager

This is a the general component that provides access to the managing functions of the API like querying sensors online, creating and removing Outputs etc.

#### Firehose

The `Firehose` is a simple object that listens on a port for LimaCharlie.io data. Under the hood it creates a Syslog Output on limacharlie.io pointing to itself and removes it on shutdown. Data from limacharlie.io is added to `firehose.queue` (a `gevent Queue`) as it is received.

It is a basic building block of automation for limacharlie.io.

#### Spout

Much like the `Firehose`, the Spout receives data from LimaCharlie.io, the difference
 is that the `Spout` does not require opening a local port to listen actively on. Instead
 it leverages `stream.limacharlie.io` to receive the data stream over HTTPS.

A `Spout` is automatically created when you instantiate a `Manager` with the
`is_interactive = True` and `inv_id = XXXX` arguments in order to provide real-time
 feedback from tasking sensors.

#### Sensor

This is the object returned by `manager.sensor( sensor_id )`.

It supports a `task`, `hostname`, `tag`, `untag`, `getTags` and more functions. This
 is the main way to interact with a specific sensor.

The `task` function sends a task to the sensor unidirectionally, meaning it does not
 receive the response from the sensor (if any). If you want to interact with a sensor
 in real-time, use the interactive mode (as mentioned in the `Spout`) and use either
 the `request` function to receive replies through a `FutureResults` object or the
`simpleRequest` to wait for the response and receive it as a return value.

#### Artifacts

The `Artifacts` is a helpful class to upload [artifacts](/v2/docs/artifacts) to LimaCharlie without going through a sensor.

#### Extensions

The `Extensions` can be used to subscribe to and manage extensions within your org.

```
import limacharlie
from limacharlie import Extension

mgr = limacharlie.Manager()
ext = Extension(mgr)
ext.subscribe('binlib')

```

#### Payloads

The `Payloads` can be used to manage various executable [payloads](/v2/docs/payloads) accessible to sensors.

#### Replay

The `Replay` object allows you to interact with [Replay](/v2/docs/replay) jobs managed by LimaCharlie. These allow you to re-run [D&R Rules](/v2/docs/detection-and-response) on historical data.

Sample command line to query one sensor:

```
limacharlie-replay --sid 9cbed57a-6d6a-4af0-b881-803a99b177d9 --start 1556568500 --end 1556568600 --rule-content ./test_rule.txt

```

Sample command line to query an entire organization:

```
limacharlie-replay --entire-org --start 1555359000 --end 1556568600 --rule-name my-rule-name

```

#### Search

The `Search` object allows you to perform an IOC search across multiple organizations.

#### SpotCheck

The `SpotCheck` object (sometimes called Fleet Check) allows you to manage an active (query sensors directly as opposed to searching on indexed historical data) search for various IOCs on an organization's sensors.

#### Configs

The `Configs` is used to retrieve an organization's configuration as a config file, or apply
 an existing config file to an organization. This is the concept of Infrastructure as Code.

#### Webhook

The `Webhook` object demonstrates handling [webhooks emitted by the LimaCharlie cloud](/v2/docs/tutorial-creating-a-webhook-adapter), including verifying the shared-secret signing of the webhooks.

### Examples:

* [Basic Manager Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_manager.py)
* [Basic Firehose Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_firehose.py)
* [Basic Spout Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_spout.py)
* [Basic Integrated Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_interactive_sensor.py)
* [Sample Configs](https://github.com/refractionPOINT/python-limacharlie/tree/master/limacharlie/sample_configs)

### Command Line Interface

Many of the objects available as part of the LimaCharlie Python SDK also support various command line interfaces.

#### Query

[LimaCharlie Query Language (LCQL)](/v2/docs/lcql) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie.

```
limacharlie query --help
```

#### ARLs

[Authenticated Resource Locators (ARLs)](/v2/docs/reference-authentication-resource-locator) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

ARLs can be used in the [YARA manager](/v2/docs/ext-yara-manager) to import rules from GitHub repositories and other locations.

Testing an ARL before applying it somewhere can be helpful to shake out access or authentication errors beforehand. You can test an ARL and see what files are fetched, and their contents, by running the following command:

```
limacharlie get-arl -a [github,Yara-Rules/rules/email]
```

#### Firehose

Listens on interface `1.2.3.4`, port `9424` for incoming connections from LimaCharlie.io.
 Receives only events from hosts tagged with `fh_test`.

```
python -m limacharlie.Firehose 1.2.3.4:9424 event -n firehose_test -t fh_test --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

#### Spout

Behaves similarly to the Firehose, but instead of listening from an internet accessible port, it connects to the `stream.limacharlie.io` service to stream the output over HTTPS. This means the Spout allows you to get ad-hoc output like the Firehose, but it also works through NATs and proxies.

It is MUCH more convenient for short term ad-hoc outputs, but it is less reliable than a Firehose for very large amounts of data.

```
python -m limacharlie.Spout event --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

#### Configs

The `fetch` command will get a list of the Detection & Response rules in your
 organization and will write them to the config file specified or the default
 config file `lc_conf.yaml` in YAML format.

```
limacharlie configs fetch --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca`
```

Then `push` can upload the rules specified in the config file (or the default one)
 to your organization. The optional `--force` argument will remove active rules not
 found in the config file. The `--dry-run` simulates the sync and displays the changes
 that would occur.

The `--config` allows you to specify an alternate config file and the `--api-key` allows
 you to specify a file on disk where the API should be read from (otherwise, of if `-` is
 specified as a file, the API Key is read from STDIN).

```
limacharlie configs push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca --config /path/to/template.yaml --all --ignore-inaccessible
```

All these capabilities are also supported directly by the `limacharlie.Configs` object.

The Sync functionality currently supports all common useful configurations. The `--no-rules` and `--no-outputs` flags can be used to ignore one or the other in config files and sync. Additional flags are also supported, see `limacharlie configs --help`.

To understand better the config format, do a `fetch` from your organization. Notice the use of the `include`
 statement. Using this statement you can combine multiple config files together, making
 it ideal for the management of complex rule sets and their versioning.

#### Spot Checks

Used to perform Organization-wide checks for specific indicators of compromise. Available as a custom API `SpotCheck` object or as a module from the command line. Supports many types of IoCs like file names, directories, registry keys, file hashes and YARA signatures.

```
python -m limacharlie.SpotCheck --no-macos --no-linux --tags vip --file c:\\evil.exe`
```

For detailed usage:

```
python -m limacharlie.SpotCheck --help
```

#### Search

Shortcut utility to perform IOC searches across all locally configured organizations.

```
limacharlie search --help
```

#### Extensions

Shortcut utility to manage extensions.

```
limacharlie extension --help
```

#### Artifact Upload

Shortcut utility to upload and retrieve [Artifacts](/v2/docs/artifacts) within LimaCharlie with just the CLI (no agent).

```
limacharlie artifacts --help
```

#### Artifact Download

Shortcut utility to download [Artifact Collection](/v2/docs/artifacts) in LimaCharlie locally.

```
limacharlie artifacts get_original --help
```

#### Replay

Shortcut utility to perform [Replay](/v2/docs/replay) jobs from the CLI.

```
limacharlie replay --help
```

#### Detection & Response

Shortcut utility to manage Detection and Response rules over the CLI.

```
limacharlie dr --help
```

#### Events & Detections

Print out to STDOUT events or detections matching the parameter.

```
limacharlie events --help
limacharlie detections --help
```

#### List Sensors

Print out all basic sensor information for all sensors matching the [selector](/v2/docs/reference-sensor-selector-expressions).

```
limacharlie sensors --selector 'plat == windows'
```

#### Invite Users

Invite single or multiple users to LimaCharlie. Invited users will be sent an email to confirm their address, enable the account and create a new password.

Keep in mind that this actions operates in the user context which means you need to use user scoped API key. For more information on how to obtain one, see <https://docs.limacharlie.io/apidocs/introduction#getting-a-jwt>

Invite a single user:

```
limacharlie users invite --email=user1@example.com
```

Invite multiple users:

```
limacharlie users invite --email=user1@example.com,user2@example.com,user3@example.com
```

Invite multiple users from new line delimited entries in a text file:

```
cat users_to_invite.txt
user1@example.com
user2@example.com
user3@example.com
```

```
limacharlie users invite --file=users_to_invite.txt
```

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

Command-line Interface

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

# Platform Management
## Overview

The Platform Management section covers essential tools and settings that help you control and configure your LimaCharlie environment. Whether you're managing user permissions, handling billing, or customizing your Cloud Sensors and overall platform configuration, these guides will ensure you can efficiently oversee and fine-tune every aspect of your deployment. Dive into the following topics to streamline management and maximize control of your infrastructure.

---

# Outputs

# Cost Effective SIEM Alternative
LimaCharlie's SecOps Cloud Platform provides a cost-effective and flexible alternative or supplement to traditional Security Information and Event Management (SIEM) offering essential capabilities while addressing the challenges of high costs, vendor lock-in, and complexity. By leveraging LimaCharlie's interoperability, automation, and detection and response () capabilities, security teams can optimize their operations and maintain a robust posture without the high costs and limitations of legacy SIEM solutions.

#### SIEM problems

The capabilities of SIEM solutions are essential for managing logs, correlating events, monitoring and alerting, and storing telemetry data. However, traditional SIEMs often present several challenges for organizations:

* **High costs:** SIEMs are typically very expensive to implement and maintain, with costs escalating as data volumes grow and additional features are required.
* **Vendor lock-in:** Many SIEMs are proprietary, closed systems that make it difficult for organizations to switch providers or integrate with other security tools.
* **Complexity:** SIEMs can be complex to set up and manage, requiring specialized skills and resources that may strain already overburdened security teams.

#### LimaCharlie’s solution

LimaCharlie's SecOps Cloud Platform offers a cost-effective alternative to traditional SIEMs, providing essential capabilities while addressing the challenges of high costs, vendor lock-in, and complexity:

* **Cost savings through flexible data management:** LimaCharlie provides one year of free telemetry storage in a fully searchable format, reducing the need to store all data in expensive SIEMs. The platform's ability to classify, filter, and route telemetry data intelligently allows organizations to send only critical data to their SIEM, further reducing costs.
* **Interoperability and customization:** Built with interoperability in mind, LimaCharlie seamlessly integrates with a wide range of security tools and platforms, enabling organizations to create custom workflows and avoid vendor lock-in. The platform's open architecture and extensive API support make it easy to integrate with existing security infrastructure.
* **Automation and ease of use:** LimaCharlie's Detection, Automation, and Response Engine enables security teams to create sophisticated detection rulesets and automate response actions, reducing alert fatigue and simplifying security operations. The SecOps Cloud Platform's powerful query language (LCQL) makes it easy for security professionals to access and analyze telemetry data without the complexity of traditional SIEMs.
* **Advanced capabilities:** LimaCharlie offers advanced threat hunting and integration with third-party threat intelligence platforms, providing security teams with the context and insights they need to identify and respond to threats effectively.

---

# Adding Outputs to an Allow List
At LimaCharlie, we rely on infrastructure with auto-scalers, and thus do not have static IPs nor a CIDR that you can rely on for an allow list (or "whitelisting").

Typically, the concern around adding IPs to an allow list for Outputs is based on wanting to limit abuse and ensure that data from webhooks is truly coming from LimaCharlie and not other sources. To address this, we provide a `secret_key` parameter that can be used as a *shared secret* between LimaCharlie and your webhook receiver. When we issue a webhook, we include a `lc-signature` header that is an HMAC of the content of the webhook using the shared `secret_key`.

---

# Add-ons

# API Integrations
## Mechanics

Functionally, API-based lookups operate exactly the same as using the normal `lookup` [operator](/v2/docs/detection-logic-operators#lookup), with one addition: `metadata_rules`. The rule will pass a value to the lookup, wait for a response, and then evaluate the response using `metadata_rules`.

The operators within `metadata_rules` are evaluated exactly the same as any other rule, except they additionally evaluate the lookup's response. The response actions will only run if the `metadata_rules` criteria are met.

## Configuration

When subscribed, API keys can be managed within the `Integrations` menu, available under `Organization Settings` in the web app:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28116%29.png)

Users who wish to view and/or edit API keys will need to have the following permissions:

* `org.conf.get`
* `org.conf.set`

## Available Lookups

LimaCharlie offers multiple API lookups for telemetry and [D&R rule](/v2/docs/detection-and-response) enrichment, allowing you to make higher fidelity detections that rely on API-based metadata. The list of available API-based integrations are under this page in the left-side navigation menu. Don't see an integration that you want? [Let us know!](https://www.limacharlie.io/contact)

---

# Add-Ons
LimaCharlie allows you to extend the capability of the platform via various add-ons. These can be enabled via the [add-ons marketplace](https://app.limacharlie.io/add-ons).

## Types of Add-Ons

We categorize our add-ons into three different categories, depending on the functionality or method in which the add-on augments the LimaCharlie platform.

* `api` add-ons are tightly integrated add-ons that enable LimaCharlie's core features
* `extension` add-ons are cloud services that can perform jobs on behalf of or add new capabilities to an Organization.
* `lookup` add-ons maintain reference to dynamic lists for use within D&R rules.
* `ruleset` add-ons provide managed sets of rules to use within D&R rules.

## Subscribing to Add-ons

Add-ons can be found and added to organizations through the [add-ons marketplace](https://app.limacharlie.io/add-ons) or by searching from within the Add-ons view in an organization (see below). The description of the add-on may include usage information about how to use it once it's installed.

![Untitled.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Untitled.png)

The following add-ons enable additional functionality in the web application:

* `atomic-red-team` - scan Windows sensors right from their `Overview` page
* `exfil` - enables `Exfil Control` to configure which events should be collected per platform
* `infrastructure-service` - enable `Templates` in the UI to manage org config in `yaml`
* `insight` - enables retention & browsing events and detections via `Timeline` and `Detections`
* `logging` - enables `Artifact Collection` to configure which paths to collect from
* `replay` - adds a component next to  rules for testing them against known / historical events
* `responder` - sweep sensors right from their `Overview` page to find preliminary IoCs
* `yara` - enables `YARA Scanners` view to pull in sources of YARA rules and automate scans with them

## Creating Add-ons

Users can create their own add-ons and optionally share them in the marketplace. Add-ons are your property, but may be evaluated and approved / dismissed due to quality or performance concerns. If you are not sure, [contact us](https://limacharlie.io/contact).

Got an idea?

Are you interested in creating an add-on or developing another project for LimaCharlie? Check out our [Developer Grant Program](/v2/docs/developer-grant-program).

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

# Developer Grant Program
The Developer Grant Program is designed to help fuel the growth of LimaCharlie add-ons and other projects that utilize the LimaCharlie platform. To help developers with their projects, we offer a $1,000 credit that can be applied towards using LimaCharlie to develop any kind of project you want.

If you are looking to commercialize an idea we can help you get it into our marketplace and if there is traction there, we can further support you in growing.

Interested parties can apply for the grant program [here](https://limacharlie.io/grant-program).

---

# OTX
AlienVault’s Open Threat Exchange (OTX) is the “neighborhood watch of the global intelligence community.” It enables private companies, independent security researchers, and government agencies to openly collaborate and share the latest information about emerging threats, attack methods, and malicious actors, promoting greater security across the entire community.

More information about OTX can be found [here](https://otx.alienvault.com/).

## Enabling the OTX Extension

Before utilizing the OTX extension, you will need an AlienVault OTX API Key. This can be found in your AlienVault OTX account [here](https://otx.alienvault.com/).

To enable the OTX extension, navigate to the [OTX extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-otx). Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(236).png "image(236).png")

Once the extension is enabled, navigate to Extensions > OTX. You will need to provide your OTX API Key, which can be done directly in the form or via LimaCharlie’s [Secrets Manager](/v2/docs/config-hive-secrets). Click Save.

Pulses will be synced to rules and lookups automatically every 3 hours.

## Using the OTX Extension

After providing a valid API key, the Extension will automatically create [Detection & Response rules](/v2/docs/detection-and-response) for your organization. The OTX  rules make use of the following events:

* Process Events

  + [CODE\_IDENTITY](/v2/docs/reference-edr-events#codeidentity)
  + [EXISTING\_PROCESS](/v2/docs/reference-edr-events#existingprocess)
  + [MEM\_HANDLES\_REP](/v2/docs/reference-edr-events#memhandlesrep) (response to the [mem\_handles](/v2/docs/endpoint-agent-commands#memhandles) Sensor command)
  + [NEW\_PROCESS](/v2/docs/reference-edr-events#newprocess)
* Network Events

  + [DNS\_REQUEST](/v2/docs/reference-edr-events#dnsrequest)
  + [HTTP\_REQUEST](/v2/docs/reference-edr-events#httprequest)
  + [NETWORK\_CONNECTIONS](/v2/docs/reference-edr-events#networkconnections)
  + [NEW\_TCP4\_CONNECTION](/v2/docs/reference-edr-events#newtcp4connection)
  + [NEW\_TCP6\_CONNECTION](/v2/docs/reference-edr-events#newtcp6connection)
  + [NEW\_UDP4\_CONNECTION](/v2/docs/reference-edr-events#newudp4connection)
  + [NEW\_UDP6\_CONNECTION](/v2/docs/reference-edr-events#newudp6connection)

Please ensure that the events you are interested in using with OTX lookups are enabled in the **Sensors >** Event Collection menu.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, Exfil (Event Collection) is a configuration extension that determines which types of events are collected and sent from endpoint agents to the cloud. It controls the data flow, ensuring only specified events are transmitted for monitoring and analysis. To capture specific events, they must be enabled within the Exfil or Event Collection settings.

---

# Plaso
Plaso Extension Pricing

While it is free to enable the Plaso extension, pricing is applied to both the original downloaded artifact and the processed (Plaso) artifacts -- $0.02/GB for the original downloaded artifact, and $1.0/GB for the generation of the processed artifacts.

## About

[Plaso](https://plaso.readthedocs.io/) is a Python-based suite of tools used for creation of analysis timelines from forensic artifacts acquired from an endpoint.

These timelines are invaluable tools for digital forensic investigators and analysts, enabling them to effectively correlate the vast quantities of information encountered in logs and various forensic artifacts encountered in an intrusion investigation.

The primary tools in the Plaso suite used for this process are [log2timeline](https://plaso.readthedocs.io/en/latest/sources/user/Using-log2timeline.html), [psort](https://plaso.readthedocs.io/en/latest/sources/user/Using-psort.html), and [psteal](https://plaso.readthedocs.io/en/latest/sources/user/Using-psteal.html).

* `log2timeline` - bulk forensic artifact parser
* `psort` - builds timelines based on output from `log2timeline`
* `psteal` - Simply a wrapper for `log2timeline` and `psort`

The `ext-plaso` extension within LimaCharlie allows you to run `log2timeline` and `psort` (using the `psteal` wrapper) against artifacts obtained from an endpoint, such as event logs, registry hives, and various other forensic artifacts. When executed, Plaso will parse and extract information from all acquired evidence artifacts that it has support for. Supported parsers are found [here](https://plaso.readthedocs.io/en/latest/sources/user/Parsers-and-plugins.html).

## Extension Configuration

Long Execution Times

Note that it can take **several minutes** for the plaso generation to complete for larger triage collections, but once it finishes you will see the results in the `ext-plaso` Sensor timeline, as well as the uploaded artifacts on the Artifacts page.

The `ext-plaso` extension runs `psteal` (`log2timeline` + `psort`) against the acquired evidence using the following commands:

1. ```
   psteal.py --source /path/to/artifact -o dynamic --storage-file $artifact_id.plaso -w $artifact_id.csv

   ```

Upon running `psteal.py`, a `.plaso` file and a `.csv` file are generated. They will be uploaded as LimaCharlie artifacts.

* Resulting `.plaso` file contains the raw output of `log2timeline.py`
* Resulting `.csv` file contains the CSV formatted version of the `.plaso` file contents

2. ```
   pinfo.py $artifact_id.plaso -w $artifact_id_pinfo.json --output_format json

   ```

After `psteal.py` runs, information is gathered from the resulting `.plaso` file using the `pinfo.py` utility and pushed into the `ext-plaso` sensor timeline as a `pinfo` event. This event provides a detailed summary with metrics of the processing that occurred, as well as any relevant errors you should be aware of.

The following events will be pushed to the `ext-plaso` sensor timeline:

* `job_queued`: indicates that `ext-plaso` has received and queued a request to process data
* `job_started`: indicates that `ext-plaso` has started processing the data
* `pinfo`: contains the `pinfo.py` output summarizing the results of the plaso file generation
* `plaso`: contains the `artifact_id` of the plaso file that was uploaded to LimaCharlie
* `csv`: contains the `artifact_id` of the CSV file that was uploaded to LimaCharlie

## Usage & Automation

LimaCharlie can automatically kick off evidence processing with Plaso based off of the artifact ID provided in a  rule action, or you can run it manually via the extension.

### Velociraptor Triage Acquisition Processing

If you use the LimaCharlie [Velociraptor](/v2/docs/ext-velociraptor) extension, a good use case of `ext-plaso` would be to trigger Plaso evidence processing upon ingestion of a Velociraptor KAPE files artifact collection.

1. Configure a D&R rule to watch for Velociraptor collection events upon ingestion, and then trigger the Plaso extension:

   **Detect:**

   ```
   op: and
   target: artifact_event
   rules:
       - op: is
         path: routing/log_type
         value: velociraptor
       - op: is
         not: true
         path: routing/event_type
         value: export_complete

   ```

   **Respond:**

   ```
   - action: extension request
     extension action: generate
     extension name: ext-plaso
     extension request:
         artifact_id: '{{ .routing.log_id }}'

   ```
2. Launch a `Windows.KapeFiles.Targets` artifact collection in the LimaCharlie Velociraptor extension. This instructs Velociraptor to gather all endpoint artifacts defined in [this KAPE Target file](https://github.com/EricZimmerman/KapeFiles/blob/master/Targets/Compound/KapeTriage.tkape).

   **Argument options:**

   * `EventLogs=Y` - EventLogs only, quicker processing time for proof of concept
   * `KapeTriage=Y` - full [KapeTriage](https://github.com/EricZimmerman/KapeFiles/blob/master/Targets/Compound/KapeTriage.tkape) files collection
      ![Screenshot 2024-01-22 at 2.57.34 PM.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot%202024-01-22%20at%202.57.34%20PM.png)
3. Once Velociraptor collects, zips, and uploads the evidence, the previously created D&R rule will send the triage `.zip` to `ext-plaso` for processing. Watch the `ext-plaso` sensor timeline for status and the Artifacts page for the resulting `.plaso` & `.csv` output files. See [Working with the Output](/v2/docs/ext-plaso#working-with-the-output).

### MFT Processing

If you use the LimaCharlie [Dumper](/v2/docs/ext-dumper) extension, a good use case of `ext-plaso` would be to trigger Plaso evidence processing upon ingestion of a MFT CSV artifact.

1. Configure a D&R rule to watch for MFT collection events upon ingestion, and then trigger the Plaso extension:

   **Detect:**

   ```
   op: and
   target: artifact_event
   rules:
       - op: is
         path: routing/log_type
         value: mftcsv
       - op: is
         not: true
         path: routing/event_type
         value: export_complete

   ```

   **Respond:**

   ```
   - action: extension request
     extension action: generate
     extension name: ext-plaso
     extension request:
         artifact_id: '{{ .routing.log_id }}'

   ```
2. Launch an MFT dump in the LimaCharlie Dumper extension.
   ![Screenshot 2024-04-04 at 9.49.11 AM.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot%202024-04-04%20at%209.49.11%E2%80%AFAM.png)
3. Once dumper is complete and uploads the evidence, the previously created D&R rule will send the zipped MFT CSV to `ext-plaso` for processing. Watch the `ext-plaso` sensor timeline for status and the Artifacts page for the resulting `.plaso` & `.csv` output files. See [Working with the Output](/v2/docs/ext-plaso#working-with-the-output).

## Working with the Output

Running the extension generates the following useful outputs:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28254%29.png)

* `pinfo` on `ext-plaso` sensor timeline
   First and foremost, after the completion of a processing job by `ext-plaso`, it is highly encouraged to analyze the resulting `pinfo` event on the `ext-plaso` sensor timeline. This event provides a detailed summary with metrics of the processing that occurred, as well as any relevant errors you should be aware of.

  + Pay close attention to fields such as `warnings_by_parser` or `warnings_by_path_spec` which may reveal parser errors that were encountered.
  + Sample output of `pinfo` showing counts of parsed artifacts nested under `storage_counters` -- this provides insight as to which, and how many events will be present in your CSV timeline.

```
"amcache": 986,
"appcompatcache": 4096,
"bagmru": 29,
"chrome_27_history": 29,
"chrome_66_cookies": 246,
"explorer_mountpoints2": 2,
"explorer_programscache": 1,
"filestat": 3495,
"lnk": 160,
"mft": 4790977,
"mrulist_string": 2,
"mrulistex_shell_item_list": 3,
"mrulistex_string": 5,
"mrulistex_string_and_shell_item": 5,
"mrulistex_string_and_shell_item_list": 1,
"msie_webcache": 143,
"msie_zone": 60,
"networks": 4,
"olecf_automatic_destinations": 37,
"olecf_default": 5,
"recycle_bin": 3,
"shell_items": 297,
"total": 5840430,
"user_access_logging": 34,
"userassist": 44,
"utmp": 13,
"windows_boot_execute": 8,
"windows_run": 10,
"windows_sam_users": 16,
"windows_services": 2004,
"windows_shutdown": 8,
"windows_task_cache": 835,
"windows_timezone": 4,
"windows_typed_urls": 3,
"windows_version": 6,
"winevtx": 382674,
"winlogon": 8,
"winreg_default": 654177

```

### Downloadable Artifacts

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28253%29.png)

* `plaso` artifact
   The downloadable `.plaso` file contains the raw output of `log2timeline.py` and can be [imported into Timesketch](https://timesketch.org/guides/user/upload-data/) as a timeline.
* `csv` artifact
   The downloadable `.csv` file can be easily viewed in any CSV viewer, but a highly recommended tool for this is [Timeline Explorer](https://ericzimmerman.github.io/) from Eric Zimmerman.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# Tutorials

# Reporting
1 Article  in this category

* Share
* Dark

  Light

---

[## Building Reports with BigQuery + Looker Studio

LimaCharlie does not include reporting by default, however our granular and customizable Output options allow you to push data to any source and use third-party tools for reporting. In this tutorial, we'll push a subset of LimaCharlie EDR telemetr...](/docs/tutorials-reporting-building-reports-with-bigquery-looker-studio)

Updated on : 06 May 2025

---

# Building Reports with BigQuery + Looker Studio
LimaCharlie does not include reporting by default, however our granular and customizable [Output](/v2/docs/outputs) options allow you to push data to any source and use third-party tools for reporting. In this tutorial, we'll push a subset of LimaCharlie EDR telemetry to [BigQuery](https://cloud.google.com/bigquery) and analyze our data using Google's [Looker Studio](https://lookerstudio.google.com/). We'll be doing the work in the web UI, however this could also be done via the API.

For this example, we will aggregate and analyze Windows processes making network connections.

## Preparing BigQuery

Within your project of choice, begin by creating a new dataset. For the purposes of this tutorial, I'm going to create a dataset named `windows_process_details`. Within this dataset, I'll create a table named `network_connections`.

Let's examine this hierarchy for a moment:

```
├── limacharlie-bq-testing    # project
│   ├── windows_process_details    # dataset
│   │   ├── network_connections    # table

```

The nice part about this type of hierarchy is that I can build out multiple tables of process details within the same dataset, and then link/analyze them as needed. We'll focus on the `network_connections` data for now, but we could also look at exporting other process details into the same dataset.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2897%29.png)

Within the Google Cloud Console, we also want to create a Service Account and gather an API key. More details on that can be found [here](https://cloud.google.com/iam/docs/service-accounts-create).

Copy the API key and keep it somewhere safe, we'll need to configure it in the output.

## Creating the BigQuery Output

Creating an Output within LimaCharlie is straightforward. Navigate to `Outputs` in the web UI, select `+ Add Output`, and select `Events`.

Note:

We want to export raw events in this case - however, we'll use filters to export only the events of interest to BigQuery.

Within the Output Destination menu, select `Google Cloud BigQuery`. You'll be prompted with a configuration menu; expand the `Advanced Options`, as we'll need those too.

The following values must be provided in order for the Output to work:

* Name (choose your own name)
* Dataset (from the previous section)
* Table (from the previous section)
* Project (from the previous section)
* Secret Key (the API key from the GCP service account)

Where to Store the Secret?

The secret key for this output can be inserted directly in the web app helper, however we recommend keeping secrets in the [Secret hive](/v2/docs/config-hive-secrets) for centralized management.

Within the `Advanced Options`, we'll need to provide the following details:

* Custom Transform - we don't want to include *all* the details from the `NETWORK_CONNECTIONS` event. For this output, we are interested in processes making network connections and the users associated with them. Thus, we'll apply the following transform to pare this down:

```
{
  "hostname": "routing.hostname",
  "command_line": "event.COMMAND_LINE",
  "user": "event.USER_NAME"
}

```

Within the `Specific Event Types` field, we'll specify only `NETWORK_CONNECTIONS`. This is another way to pare down the number of events processed and exported.

Finally, we'll also specify a tag of `windows`, ensuring we only capture Windows systems (per our tagging - your tags may differ). Based on the values provided and discussed, here's a screenshot of the Output configuration (minus the API key):

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28100%29.png)

Save the output details, and then check `View Samples` in the Outputs menu to see if you're successfully seeing events.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28101%29.png)

## Analyzing Events in BigQuery + Looker Studio

Navigating back to BigQuery, we can see some initial events flowing in:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28102%29.png)

Let's hop over to Looker Studio. Create a Blank Report, and select `BigQuery` in the `Connect to Data` menu.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28103%29.png)

Select the Project, Dataset, and Table of interest, and click `Add`.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28104%29.png)

Looker Studio may prompt you about permissions of connected data. However, once connected, we'll be able to see a starter table with aggregate details from our `network_connections` table.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28105%29.png)

And that's it! From here, you can manipulate and move around the data as needed. You can also blend with another table, allowing you to combine multiple data points.

Reports can also be styled, additional statistics generated, etc. The following example continues to pull on the basic data we exported to provide some unique insights:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28106%29.png)

---

# FAQ

# FAQ - General
## Is my data secure with LimaCharlie?

LimaCharlie data is secured starting at the endpoint all the way to your infrastructure. The LimaCharlie platform is hosted on the Google Cloud Platform, leveraging multiple capabilities from credentials management to compute isolation in order to limit the attack surface.

Data access is managed through Google Cloud IAM which is used to isolate various components and customer data. Processing is done in Google Kubernetes Engine which provides an additional layer of container isolation.

Each LimaCharlie data center uses independent cryptographic keys at all layers. Key management uses industry best practices such as key encryption at rest.

LimaCharlie is SOC 2 Type 2 and PCI-DSS compliant. Our infrastructure is housed in ISO 27001 compliant data centres.

## Where will my data be processed and stored?

The LimaCharlie global infrastructure is built on the Google Cloud Platform (GCP). Currently, computing resources are available in the USA, Canada, Europe, India, and the United Kingdom. New data centers can be spun up anywhere GCP is available upon request.

When you set up an Organization for the first time, you can select the Data Residency Region of your choice:

![Data Residency Region Picker](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot%202023-02-09%20at%204.16.05%20PM.png)

This provides you with the benefit of being able to select which GCP region you want your data in, and have assurance that it will always be processed in this location and never moved outside. This can be important for data residency requirements as it relates to regulatory compliance. For example, if you want to keep all of your information in the US, you can simply select the US region and know that your data will be both processed and stored there.

Need to change the Data Residency Region?

Please note that once a region has been selected for an organization, it cannot be changed later.

## Can LimaCharlie staff access my data?

LimaCharlie staff only access your private data when you contact us and give us permission to do so. We will always ask for your permission before we access your private telemetry data.

We consider your sensors and telemetry data to be private and confidential. We understand the tremendous power that is being entrusted to us while we have access to this data. We promise to only access your organization for the exclusive purpose of providing you with the assistance you request from us. We treat your private and confidential information with at least the same due care as we do with our own confidential information, as outlined in our privacy policy.

## Will third parties get access to my data?

The only time we provide your data to a third party is with your explicit consent. (e.g. when you set up an Output in LimaCharlie, you're explicitly telling us to send your data to a 3rd party).

## What control measures do you have in place to ensure that my data won't be accessed without proper authorizations?

We use transparency as a mitigating control against insider threats. In particular, when we access your organization data, an entry is made to the Audit Log in your organization. You can access the audit log in the web interface and via the API. We also provide the ability for you to send audit log data out of LimaCharlie immediately to a write-only bucket that you control in your own environment.

We use a break-glass system, meaning that LimaCharlie personnel do not have access to customer data by default. This requires an explicit programmatic action (internal to LimaCharlie) that includes its own audit trail that cannot be modified by LimaCharlie staff. This audit trail is regularly reviewed.

LimaCharlie staff access to customer data is restricted to only those who need it to perform their official duties.

LimaCharlie staff must explicitly request permission from the customer before granting access to any data or systems (other than in emergency cases where infrastructure is at risk).

We use role-based access control systems to provide granular control over the type of data access granted.

Access to customer organizations is granted programmatically as to provide a security control.

We require that our staff undergo a background check and take training, including privacy training, prior to being allowed to access customer data.

We are SOC 2 (Type 2) compliant and a copy of our audit report can be provided upon request.

## What is detected by LimaCharlie after it's initially installed?

When the Sensor is installed, LimaCharlie will start recording the telemetry. It will not, however, generate detections or take actions to protect the endpoints automatically. As an infrastructure company, we recognize that each environment is different, and one size fits all approach rarely works well. By default, we take the AWS approach - any new organization starts empty, without any pre-configured settings, add-ons, or  rules.

## Can LimaCharlie be deployed on-premises?

LimaCharlie is a cloud-based solution. The LimaCharlie platform is hosted on the Google Cloud Platform (GCP). There are no limits between AWS & GCP but LimaCharlie is not available on premises; if you configure the sensor on the endpoint, it will connect to the cloud.

## Does LimaCharlie detect variants of the latest malware?

When the sensor is installed, LimaCharlie will start recording telemetry. It will not, however, generate detections or take actions to protect the endpoints automatically. As an infrastructure company, we recognize that each environment is different, and one size fits all approach rarely works well. By default, any new organization starts empty, without any pre-configured settings, add-ons, or D&R rules.

LimaCharlie makes it easy to add a detection & response rule as soon as new variants of malware are discovered. This way, you are in a full control of your coverage and there is no need to wait for a vendor to come up with a new detection rule.

## What latency can I expect in LimaCharlie?

LimaCharlie Detection & Response (D&R) engine has very low latency and you can expect that responses are almost instantaneous (e.g. 100ms).

You may notice some latency as it relates to outputs. Some of our outputs are done in batches, such as Amazon S3, SFTP, Google Cloud Storage. You can configure the maximum size and maximum time for these outputs. We also offer live outputs, such as Syslog.

## How can I integrate LimaCharlie with my existing SIEM?

The most common use case we see is sending detections and events data from LimaCharlie into the SIEM.

To do it, you will need to configure outputs. Here are some examples for configuring outputs to go to an email or to Chronicle.

Remember to select the type of data forwarded by this configuration (stream). The available options are as follows:

* **event**: Contains all events coming back from sensors (not cloud detections). It is very verbose.
* **detect**: Contains all detections reported from D&R rules or subscriptions. This is the option you would choose if you want detections to generate emails (you would also need to ensure that D&R rules are configured to generate detections).
* **audit**: Contains auditing events about activity around the management of the platform in the cloud.
* **deployment**: Contains all "deployment" events like sensor enrollment, cloned sensors etc.
* **artifact**: Contains all "artifact" events of files collected through the Artifact Collection mechanism.

While sending detections and events data from LimaCharlie into the SIEM is the most common way we see our users set up the integration between these two systems, you can also bring in the data into LimaCharlie from SIEM or build other custom workflows. Contact our support team if you need help with your use case or if you have further questions.

## What is the retention policy for management/audit logs?

LimaCharlie stores management/audit logs for one year.

We suggest you set up an [Output](/v2/docs/outputs) to send logs to an external destination if you are looking to have your logs stored for over one year.

## Does LimaCharlie offer reporting capabilities?

It is very common for users to bring different log, network and endpoint data into the LimaCharlie to leverage our detection and response, advanced correlation and storage. If you wish to leverage data visualization capabilities, we make it easy to send the data you need to Splunk, Tableau or any other solution of your choice via public API.

In LimaCharlie web app, you can track information such as detections and events over time and number of sensors online.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2831%29.png)

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

# FAQ - Sensor Installation
## How can I add LimaCharlie traffic to an allow list?

The tables below show the hostnames and IPs used to connect to LimaCharlie. All connections use TCP port 443 and TLS 1.2+

## What Hostnames and IPs does LimaCharlie use for each region?

### Canada (Quebec)

| Hostname | IP | Use |
| --- | --- | --- |
| aae67d7e76570ec1.lc.limacharlie.io | 35.203.33.203 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| aae67d7e76570ec1.edr.limacharlie.io | 35.201.82.57 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| aae67d7e76570ec1.wss.limacharlie.io | 35.201.96.199 | Chrome, Edge and Adapters |
| aae67d7e76570ec1.ingest.limacharlie.io | 34.149.216.238 | Logs and Artifacts |
| aae67d7e76570ec1.replay.limacharlie.io | 142.250.115.121 | Replay |
| aae67d7e76570ec1.live.limacharlie.io | 34.120.175.14 | Live feed |
| aae67d7e76570ec1.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### US (Iowa)

| Hostname | IP | Use |
| --- | --- | --- |
| 9157798c50af372c.lc.limacharlie.io | 35.194.62.236 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 9157798c50af372c.edr.limacharlie.io | 34.149.165.165 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 9157798c50af372c.wss.limacharlie.io | 34.102.223.182 | Chrome, Edge and Adapters |
| 9157798c50af372c.ingest.limacharlie.io | 34.120.157.194 | Logs and Artifacts |
| 9157798c50af372c.replay.limacharlie.io | 142.250.115.121 | Replay |
| 9157798c50af372c.live.limacharlie.io | 34.120.123.4 | Live feed |
| 9157798c50af372c.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### India (Mumbai)

| Hostname | IP | Use |
| --- | --- | --- |
| 4d897015b0815621.lc.limacharlie.io | 35.200.151.24 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 4d897015b0815621.edr.limacharlie.io | 34.102.207.18 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 4d897015b0815621.wss.limacharlie.io | 34.98.108.101 | Chrome, Edge and Adapters |
| 4d897015b0815621.ingest.limacharlie.io | 34.149.161.19 | Logs and Artifacts |
| 4d897015b0815621.replay.limacharlie.io | 142.250.115.121 | Replay |
| 4d897015b0815621.live.limacharlie.io | 35.244.221.119 | Live feed |
| 4d897015b0815621.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### UK (London)

| Hostname | IP | Use |
| --- | --- | --- |
| 70182cf634c346bd.lc.limacharlie.io | 35.242.152.114 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 70182cf634c346bd.edr.limacharlie.io | 34.107.134.233 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 70182cf634c346bd.wss.limacharlie.io | 35.244.147.201 | Chrome, Edge and Adapters |
| 70182cf634c346bd.ingest.limacharlie.io | 34.149.56.238 | Logs and Artifacts |
| 70182cf634c346bd.replay.limacharlie.io | 142.250.115.121 | Replay |
| 70182cf634c346bd.live.limacharlie.io | 35.244.146.102 | Live feed |
| 70182cf634c346bd.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Europe (Emshaven)

| Hostname | IP | Use |
| --- | --- | --- |
| b76093c3662d5b4f.lc.limacharlie.io | 35.204.142.125 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| b76093c3662d5b4f.edr.limacharlie.io | 34.111.194.87 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| b76093c3662d5b4f.wss.limacharlie.io | 130.211.22.248 | Chrome, Edge and Adapters |
| b76093c3662d5b4f.ingest.limacharlie.io | 34.120.5.160 | Logs and Artifacts |
| b76093c3662d5b4f.replay.limacharlie.io | 142.250.115.121 | Replay |
| b76093c3662d5b4f.live.limacharlie.io | 34.120.64.23 | Live feed |
| b76093c3662d5b4f.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Australia (Sydney)

| Hostname | IP | Use |
| --- | --- | --- |
| abc32764762fce67.lc.limacharlie.io | 34.151.84.52 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| abc32764762fce67.edr.limacharlie.io | 34.54.253.51 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| abc32764762fce67.wss.limacharlie.io | 34.96.104.54 | Chrome, Edge and Adapters |
| abc32764762fce67.ingest.limacharlie.io | 35.241.63.128 | Logs and Artifacts |
| abc32764762fce67.replay.limacharlie.io | 34.49.249.16 | Replay |
| abc32764762fce67.live.limacharlie.io | 34.8.102.215 | Live feed |
| abc32764762fce67.hook.limacharlie.io | 34.49.185.177 | Webhooks |

## How much data does the LimaCharlie Sensor produce per day?

The amount of data that is produced by the sensor is dependent on how much, and what kind of activity is taking place on the endpoint. That being said, the average data produced per endpoint across thousands of deployments is approximately 1MB per day.

## How much resources does the LimaCharlie agent consume?

The total footprint of the agent on disk combined with what is in memory is approximately 50MB. The agent typically runs under 1% CPU.

Depending on what actions you may be performing it may increase (e.g. if you’re doing a full YARA scan it’s expected that the CPU usage will increase). When you use our YARA trickle scan, that also keeps CPU usage within reasonable bounds. You’ll only see YARA scans spike CPU when you do a full manual scan.

Depending on the configuration of the agent (it’s fully customizable), the network bandwidth will vary, but we typically see aproximately 2MB per day on Windows hosts.

## Why does my sensor initially connect successfully but then disappears?

Sometimes we see the agent connect to the LimaCharlie cloud, enrolls, then disconnects (which is normal the first time after enrollment) and never connects again, or it doesn't show that kernel has been acquired.

This behavior is typical with SSL interception. Sometimes it's a network device, but at other times some security products on the host can do that without being very obvious.

You can confirm if there is SSL interception by performing the following steps to check the SSL fingerprint of the LimaCharlie cloud from the host.

**Confirm the region of your** Organization

If you already know where your organization's region is located, you can move to the next step. To verify the organization's region where the data is processed and stored, click `Add Sensor` from the `Sensors` view. You will then see the region listed under `Sensor Connectivity`.
![Sensor - Region](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Sensor%20-%20Region.png)

**Open the test URL**
Via web browser, navigate to one of the below test URLs that corresponds to the correct region:

[Test URL - US Region](https://9157798c50af372c.lc.limacharlie.io/)
[Test URL - UK Region](https://70182cf634c346bd.lc.limacharlie.io/)
[Test URL - India Region](https://4d897015b0815621.lc.limacharlie.io/)
[Test URL - Europe Region](https://b76093c3662d5b4f.lc.limacharlie.io/)
[Test URL - Canada Region](https://aae67d7e76570ec1.lc.limacharlie.io/)

No website will open; you should get a "Your connection is not private" type of message instead.

**Display the SSL Certificate**

By clicking near the URL bar on the exclamation mark, you will open a small menu and you can click "Certificate status"/"Certificate validity"/"Certificate is not valid" which will display the certificate information.

![certifricate](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certifricate.png)

![certificate-1](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certificate-1.png)

**Confirm the SHA-1 and SHA-256 fingerprints**

The SHA-1 and SHA-256 fingerprints should match the values below that correspond to the region your organization is in.

If the SHA-1 and SHA-256 fingerprints you are seeing do not match what's listed below, that's an indicator of the SSL interception.

| Region | SHA-256 Fingerprint | SHA-1 Fingerprint |
| --- | --- | --- |
| US | 14 44 8C B6 A1 19 A5 BE 18 AE 28 07 E3 D6 BD 55 B8 7A 5E 0C 3F 2D 78 03 6E 7C 6A 2A AA 45 8F 60 | 1A 72 67 08 D0 83 7D A9 62 85 39 55 A1 12 1B 10 B0 F4 56 1A |
| UK | 49 49 B0 41 D6 14 F3 3B 86 BF DF 14 24 F8 BD 2F E1 98 39 41 5A 99 E6 F1 C7 A2 C8 AB 34 0C FE 1D | 2E 49 00 DB F8 3A 2A 88 E0 15 76 D5 C5 4F 8F F3 7D 27 77 DD |
| India | 68 6F 08 3D 53 3F 08 E0 22 EB F6 67 0C 3C 41 08 75 D6 0E 67 03 88 D9 B6 E1 F8 19 6B DA 54 5A A3 | 37 57 DD 4E CF 2B 25 0B CA EA E2 E6 E3 B2 98 48 29 19 F3 6B |
| Europe | EF B3 FA A7 78 AB F0 B0 41 00 CF A3 5F 44 3F 9A 4D 16 28 B9 83 22 85 E3 36 44 D5 DC F9 5C 78 5B | 07 72 B3 31 1A 89 D6 54 1D 71 C3 07 AD B5 8A 26 FD 30 7E 5D |
| Canada | D3 40 8B 59 AE 5A 28 75 D1 65 71 50 52 2E 6F 45 26 EE E8 19 3A 9A 74 39 C1 64 60 B8 6A 92 15 47 | E3 EF AE 6A 0E 7F 18 83 15 FE F2 02 6C F3 2D 4E 59 95 4D 0A |

## What happens if a host is offline?

When the host is offline, the Sensor will keep collecting telemetry and store it locally in a "ring buffer" (which limits the total possible size). The buffer is ~60mb, so the amount of time it will cover will vary based on how much telemetry the individual endpoint generates. e.g. A domain controller will likely be generating many more events than a regular end user workstation.

When the host is back online, the content of this buffer will be flushed to the cloud where [detection and response](/v2/docs/detection-and-response) () rules will apply as usual.

The same ring buffer is used when the Sensor runs normally, even if data is not sent to the cloud in real-time. The cloud can then retroactively request the full or partial content of the ring buffer, bringing your telemetry current.

## How can I tell which Installation Key was used to enroll a sensor?

On occasion you may need to check which installation key was used to enroll a sensor. You can do so by comparing the sensors `Installer ID` with the Installation Key's `Adapter Key` value.

1. Go to the Sensors section and click into the sensor in question to view its details page. Take note of the `Installer ID`.
2. Go to the Install Sensors section.  Click the copy icon under the `Adapter Key`.
3. Compare these two values; the Installer ID on a sensor should be the same as the Adapter Key of the installation key used.

If you need to check a large list of sensors, you can perform an export of all sensors from the main sensors list page, or use the LimaCharlie API.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

---

# Release Notes

# Release Notes
## 2025-08-08

Endpoint Agent 4.33.13 and 4.33.10.3

* Fix a Windows 2016 compatibility issue in the kernel driver for both `lc:stable`  (4.33.10.3) and `lc:latest` (4.33.13) versions.

## 2025-07-18

Endpoint Agent 4.33.11

* Bug Fixes

  + Resolved event loss on high-traffic Windows systems
  + Fixed kernel upgrade failures that could occur during system updates
  + Addressed code signing compatibility issues on macOS
* Breaking Changes

  + Console logging is now opt-in via `-v` or `--verbose` flags **Note:** The previous `-v` flag for displaying installer version has been changed to `-V`.  This improves default output cleanliness while maintaining debugging capabilities
* New `stable` version is now `4.33.10`

Web App 4.4.4

* A patch release with minor bug fixes

## 2025-07-10

Web App 4.4.3: fixed regression with sensor timeline view.

lc adapters v1.30.11:  integration with Cylance, Proofpoint Tap, and Wiz. Big and special thanks for the community contributors <https://github.com/shortstack>  and [RagingRedRiot](https://github.com/RagingRedRiot).

* *Note: these adapters are supported in the downloadable Adapter, but not yet rolled out to the webapp as "cloud adapter"*

## 2025-06-27

Endpoint Agent 4.33.9 - important fixes for Windows 7 and Windows 8 support

Web App 4.1.2 - bug fixes for customers and community

Also, last week we introduced two new rule sets from our community partners to LimaCharlie Add Ons collection:

* [SoteriaSec](https://soteriasec.io/) Commercial Ruleset: Google Workspace Rules
* [BLOKWORX](https://blokworx.com/) Detection & Response rules set covering detection of a collection of remote access services usage

## 2025-06-17

Web App 4.4.0

* AI powered community rules in “Beta”. Easy way to turn thousands of community rules to LimaCharlie detection & response. [See the docs](https://docs.limacharlie.io/docs/community-rules)
* New and improve Extensions page
* Bug fixes, including a few around auto-generated Extensions UI for extension builders

## 2025-05-30

Endpoint Agent 4.33.8 (now `latest`)

* Fix a potential deadlock on upgrade in the HBS component
* Fix a reverse logic issue processing the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variables - the possible / accepted values are `1`, `true`, `0`, `false` ( case insensitive )

Web App 4.3.3

* AI assisted detection read-out; navigation improvements, showing org selector consistently, and a number of bug fixes.

## 2025-05-22

Endpoint Agent 4.33.7 (now `latest` )

* Linux

  + Fix some Linux GLIBC compatibility issues. The minimum GLIBC supported version is now 2.16 ( released 2012 ) for all 3 supported architectures ( x86, x86\_64 and arm64 )
  + Fix the Linux alpine / musl libc binaries
* macOS:

  + standalone installer is now a universal binary (FAT) to prevent users from installing on the wrong architecture
  + Fix an issue where the host isolation command wouldn't terminate existing connections
* Windows:

  + Added an environment variable ( `LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK` ) to prevent the Windows' WinTrust code signing library from it's revocation cache from the internet. The default and *recommended* setting is to let WinTrust update its cache but the sensor may connect to content delivery networks ( CDNs ) on port 80 to do so
* General

  + The sensor troubleshooting tool ( `rphcp -H` ) was missing in the .deb, .msi or .pkg installers

Web App 4.3.2

* Fixes few edge-case crashes and recently reported bugs

## 2025-05-20

Releasing LimaCharlie Endpoint Protection integrates with third-party EDR solutions to provide a better view of security operations and extend agent’s capabilities. This functionality comprises the EPP Extension, Web App, and a previously released Endpoint Agent v4.33.6. For detailed documentation, see [Endpoint Protection](/v2/docs/ext-epp)

**Web App 4.3.1:**  UI support for Endpont Protection solution, bug fixes

**Extensions:** `Endpoint Protection` extension, a component of the EPP solution that codifies key configurations for Microsoft Defender.

## 2025-05-08

LC adapter v1.30.1

* Adding Sublime adapter - Audit logs from Sublime can be ingested cloud-to-cloud via the API, see [Docs](https://docs.limacharlie.io/docs/adapter-types-sublime-security) for details.

Web App  4.2.8

* A number of UI bug fixes.

## 2025-04-18

Endpoint agent 4.33.6

* Allow the sensor to drop the VDI file (delayed start) during the installation procedure via `-t`
* Added a sensor troubleshooting utility - a standalone command and a command line option for the sensor (`-H`) to help diagnose common misconfigurations and connectivity problems.

WebApp 4.2.3

* Fixing the artifact download broken in some cases, and other small bug fixes.

## 2025-04-11

Web App 4.2.1

* AI co-writer for D&R: use “ask AI” when creating the rule and it helps you write a detection and response based on your prompt.

  + We currently use Google’s  `gemini-2-flash` [model](https://deepmind.google/technologies/gemini/flash/)  that we tuned to do a good job building Detections and Responses in LimaCharlie, while the standard AI disclaimer applies: “trust but verify”.
* Event Tree updated for usability and performance on giant trees: enjoy collapsing and expanding groups of events, and traverse the tree with no strain on your browser.
* Other performance optimizations and bug fixes

Endpoint Agent 4.33.5

* Performance improvements for macOS
* Infrastructure work to support Endpoint Protection Platforms (EPP),  and added support for Microsoft Windows Defender

> Note of change
>
> LC Detection Events are now immutable. One can no longer remove the past events, or modify them in any way, as the detection events are factual historic record, and it’s prudent to keep them as such.

## 2025-03-28

* Web app 4.1.4

  + UI betterment: quick filters for common platforms on Sensor list, reliable navigation from/to Detections, other small improvements and bug fixes.
* [Adapter for SentinelOne](https://docs.limacharlie.io/docs/sentinelone):  connects to SentinelOne MGMT API and send to LC alerts, threats, and other events of interest.

## 2025-03-28

* Endpoint agent v4.33.4

  + Fix missing pipe event for Windows
  + Fix the kernel acquisition module for Linux arm64 builds
* Extensions and adapters:

  + Git-Sync - take the best from LimaCharlie Infra as Code by connecting with Git and syncing the desired sections of your configurations in easy to use UI. [Documentation](https://refractionpoint.slack.com/archives/C058QHECQC8/p1743177137477489)
  + ext-renigma v1.0.0 - initial release of integration with [REnigma](https://dtrsec.com/) - an advanced malware analysis platform leveraging its unique Record and Replay technology - read more in the [Docs](https://docs.limacharlie.io/docs/ext-renigma).
  + MIMECAST adapter - connect to the Mimecast API to stream audit events as they happen Read more in the [Docs](https://docs.limacharlie.io/docs/adapter-types-mimecast).
* Web app 4.1.1

  + Usability improvements on Detection page, ability to re-run command in sensor/console,  fix “copy array index”, and numerous bug fixes.

## 2025-03-14

Web App `v4.0.2`

* A long-awaited modernized UI is available (in preview). More work in on the way to further improve user experience.
* In-product dashboards available (in preview) - a bird’s eye view on key detections and the flow of data.

This is not just a paint job: we made substantial internal changes and will continue to improve quality. Learn more on what has changed in our blog: [**Announcing Our UI Update and In-product Dashboards**](https://limacharlie.io/blog/announcing-improved-ui-experience-and-in-product-dashboard)**.**

> Notes
>
> * On large orgs, the dashboards can take up to 15 sec to load the very first time, and normalize after the first load. Optimizations on the way.
> * The Query Console is not available in the Modern UI yet. We will bring it there,  in a much better shape. Meantime you’ll have to switch back to the Old Theme to access to it.

Add-Ons & Adapters:

* New: [PandaDoc adapter](/v2/docs/adapter-types-pandadoc) to connect and fetch PandaDoc API logs
* New:  [CrowdStrike Falcon Cloud adapter](/v2/docs/adapter-types-crowdstrike-falcon-cloud) - allows you to connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console.
* Update: Cloud-CLI v1.4.8 Extension - We have improved observability in the CLI extensions such as `ext-cloud-cli` which allows us to support users better. Additionally, we have improved error handling and reporting around long running CLI commands which may have got stuck or timed out.

## 2025-03-06

EDR Agent: `v4.33.2`

* Fixed a path expansion issues that would cause the cleanup command on Windows to leave configuration files after the uninstallation procedure.

Adapter: `v1.27.2`

* Added support for ZenDesk, read more in our docs: <https://docs.limacharlie.io/docs/adapter-types-zendesk>

## 2025-02-28

Introducing LimaCharlie Labs, where we share with you brave experiments and early prototypes of features and extensions that may or may not become production, based on your input and feedback. Check the `LABS` badge on the Web App.

* Playbook Extension is now available in the Labs - see [documentation here](/v2/docs/playbook)

Web App `v3.10.1`

* Introduce Event Latency ( `routing/latency` ), and add latency metrics to the Sensor Analytics, to help identify and troubleshoot any event latency issues.
* Add “Search by Description” to the org list.
* Bug fixes.
* “Report a Bug”: integrated tool to report bugs easily so that we do more bug fixes for y’all.

## 2025-02-21

Web App `v3.9.3`

* Bug fixes: handling edge-cases of org creation and adding users flows, fixing MS 365 sensor false status in certain rare conditions, other small fixes and internal instrumentation improvements.

CLI `4.9.12`

* Add users, simplified. Wrapping the [new API](https://api.limacharlie.io/static/swagger/#/Users/addOrgUser), a new command `limacharlie users invite` makes it easy to add a user, or a batch of users, to the org - without requesting them to create LimaCharlie account. See [Invite users section in LimaCharlie SDK](/v2/docs/limacharlie-sdk#invite-users) for usage.

EDR Endpoint Agent `v4.33.1`

* Fix various directory and file permissions on macOS
* Added a status file to help troubleshooting

  + The status file contains the sensor id, organization id, version and the agent's service uptime
  + File locations are platform specific:

    - Linux: `/opt/limacharlie/hcp_hbs_status.json`
    - macOS: `/Library/Application Support/limacharlie/hcp_hbs_status.json`
    - Windows: `c:\\programdata\\limacharlie\\hcp_hbs_status.json`
* Fix a missing package name for `Microsoft Edge Update` on Windows
* Fix a pattern matching issues that what affecting file integrity notifications
* Added the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variable support for customers wanting to use the local hostname instead of resolving it

## 2025-01-24

Web App `v3.8.12`

* New Features:

  + New Australia Datacenter: We have added a new datacenter in Australia to enhance the performance and availability of our services for users in the region.
  + Secrets Manager Integration: The SMTP password field now allows for integration with our secrets manager, providing a more secure way to handle authentication credentials.
  + New Extension: `ext-nims` allows you to send detections from LimaCharlie to NIMS via the Notion API. Read more [here](https://docs.limacharlie.io/docs/ext-nims).
* Bug Fixes & Enhancements:

  + Autofill OTP: The one-time password (OTP) field now properly auto-fills from password managers.
  + User Permissions Warning: A warning message has been implemented to notify users when revoking permissions to a user.

## 2025-01-09

Web App `v3.8.10`

* Bug Fixes and Improvements

  + Fixed a bug where creating a new secret in a secret manager and changing cloud adapter configuration at the same time would not update the cloud configuration with the new secret. This fix prevents the bug by stopping a certain event from being propagated.

ext-usage-alerts `v1.0.0`

* Newly released extension which allows you to create, maintain, & automatically refresh usage alert conditions for an Organization. Read more [here](https://docs.limacharlie.io/docs/ext-usage-alerts).

## 2024-12-12

Web App `v3.8.8`

* New features

  + Introduced user-level saved queries for improved data management.
* Bug Fixes and Improvements

  + Fixed the alignment of the ‘skip for now’ text on the initial sensor onboarding screen during organization creation.
  + Resolved an error related to empty extension configurations, enhancing user experience.
  + Fixed a minor scroll issue on the sensors page where there was a slight horizontal scroll possible on the page.
  + Implemented a fix for an issue where the organization creation waiting room would display “missing permission errors” when opening the app.
  + Minor enhancement on the input field for adding a user to your organization, where it will now show an error if the 'add user' button is clicked without a user's email filled in.
  + Updating various mentions of "Yara" to be all caps to reflect it being an acronym

## 2024-10-28

New MITRE Report API In this release, we've added a new REST API and CLI for producing a MITRE report for a given Organization based on the D&R rules in place (using their tags like `attack..t1000.xxx`).

* API: <https://api.limacharlie.io/static/swagger/#/Rules/getOrgMITREReport>
* CLI: `limacharlie mitre-report`

The resulting JSON report can be used with the attack-navigator: <https://mitre-attack.github.io/attack-navigator/>.This capability makes it easier to track security coverage against MITRE ATT&CK framework.

## 2024-10-19

EDR Sensor `v4.31.1`

* Network connection stability enhancements on all platforms.
* The enhancements are both in the cloud-triggered upgrade version of the sensor AND in the on-disk installation, but there is no requirement to deploy both simultaneously.

## 2024-10-17

New sort and bulk actions functionality for tables

In this release, we are adding the ability to sort columns in the LimaCharlie web app. In addition, tables now support bulk actions (Enable/Disable and Delete). This applies to the following sections of the web app: Adapters, Yara Rules, Secrets, Lookups, False Positive Rules and Detection and Response Rules.

## Prior Release Notes

All prior date release notes are located here: <https://limacharlie.io/release-notes>

---

