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

Chrome Agent Installation

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Chrome Agent Installation

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

* [ChromeOS with Google Chrome Enterprise](/docs/chrome-enterprise)
* [Edge Agent Installation](/docs/edge-agent-installation)

---

###### What's Next

* [Container Clusters](/docs/container-clusters)

Table of contents

+ [Installation Instructions](#installation-instructions)
+ [Troubleshooting the Chrome Sensor](#troubleshooting-the-chrome-sensor)

Tags

* [browser agent](/docs/en/tags/browser%20agent)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [sensors](/docs/en/tags/sensors)
