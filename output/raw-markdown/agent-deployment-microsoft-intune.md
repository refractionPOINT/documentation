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

Agent Deployment via Microsoft Intune

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Agent Deployment via Microsoft Intune

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

[Microsoft Intune](https://learn.microsoft.com/en-us/mem/) is a cloud-based endpoint management solution that integrates with Microsoft Azure. It allows for simplified app and device management across a wide range of devices, including mobile devices, desktop computers, and virtual endpoints.

Intune can be used to simplify LimaCharlie Sensor deployment within enterprise environments. To add a custom App to Intune, select the `+ Add` button within the Intune admin center:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2861%29.png)

InTune supports Windows and macOS package deployment.

### Windows Deployment via Intune

Deploying Windows applications via Intune requires creating an Intune application package (`.intunewin` file extension). To do this, please utilize Microsoft's IntuneWinAppUtil.exe file. Usage and documentation on creating an `.intunewin` file can be found [here](https://learn.microsoft.com/en-us/mem/intune/apps/apps-win32-prepare).

Intune Package Contents

Intune packages may need to be created for each Organization, as the Installation Key must be provided at the time of installation.

We recommend first creating a [custom MSI installer](/v2/docs/building-a-custom-msi-installer-for-windows), bundled with the appropriate installation key, and then including that in your `.intunewin` file.

After clicking `+ Add`, choose `Windows app (Win32)`:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2863%29.png)

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

* [Windows Agent Installation](/docs/windows-agent-installation)
* [Building a custom MSI installer for Windows](/docs/building-a-custom-msi-installer-for-windows)

---

###### What's Next

* [ChromeOS with Google Chrome Enterprise](/docs/chrome-enterprise)

Table of contents

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
