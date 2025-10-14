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

Ingesting MacOS Unified Logs

* 07 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# Ingesting MacOS Unified Logs

* Updated on 07 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

You can enable real-time MacOS Unified Logs (MUL) ingestion using the LimaCharlie EDR Sensor.

First, navigate to the Exfil Control section of LimaCharlie and ensure that `MUL` events are enabled for your Windows rules.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28258%29.png)

Next, navigate to the `Artifact Collection` section and set up an artifact collection rule for the MacOS Unified Log(s) of interest. To ingest MUL real-time events in the timeline, use the `mul://[Predicate]` format, where the predicate is a standard [MacOS MUL predicate](https://www.macminivault.com/faq/introduction-to-macos-unified-logs/). For example, to ingest the Safari logs, you'd use the following pattern:

`mul://process == "Safari"`

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28259%29.png)

If you ingest MacOS Unified Logs with a `mul://` pattern, they are streamed in real-time as first-class telemetry alongside the native EDR events, and are included in the flat rate price of the sensor.
 :::

After you apply those, you should start seeing your MacOS Unified Logs data coming through for your endpoints within 10 minutes. You can verify this by going into the Timeline view and choosing `MUL` event type.

Also see: [Artifacts](/v1/docs/telemetry-artifacts)

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

* [LimaCharlie Core Concepts](/v1/docs/limacharlie-core-concepts)
