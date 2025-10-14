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

Windows Event Logs

* 28 May 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Windows Event Logs

* Updated on 28 May 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

This example shows collecting Windows Event Logs (`wel`) from a Windows box natively (and therefore is only available using the Windows Adapter). This is useful for cases where you'd like to collect WEL without running the LimaCharlie Windows Agent.

```
./lc_adapter wel client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d `
    client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd `
    client_options.sensor_seed_key=domain-controller1 `
    client_options.platform=wel `
    evt_sources=security:*,application:*,system:*,Microsoft-Windows-Windows Defender/Operational:*
```

Here's a breakdown of the above example:

* `lc_adapter`: simply the CLI Adapter.
* `wel`: the method the Adapter should use to collect data locally. The `wel` value will use a native local Windows Event Logs subscription.
* `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
* `client_options.identity.oid=....`: the Organization ID from LimaCharlie the installation key above belongs to.
* `client_options.platform=wel`: this indicates the type of data that will be received from this adapter. In this case it's `wel` events.
* `client_options.sensor_seed_key=....`: this is the value that identifies this instance of the Adapter. Record it to re-use the Sensor ID generated for this Adapter later if you have to re-install the Adapter.
* `evt_sources=....`: a comma separated list of event channel to collect along with a XPath filter expression for each. The format is `CHANNEL_NAME:FILTER_EXPRESSION` where a filter of `*` means all events. Common channels: `security`, `system` and `application`.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

* [Microsoft Defender](/docs/adapter-types-microsoft-defender)
* [Windows Event Log](/docs/adapter-types-windows-event-log)
* [EVTX](/docs/adapter-types-evtx)
* [Ingesting Windows Event Logs](/docs/ingesting-windows-event-logs)
* [Hayabusa](/docs/ext-hayabusa)

---

###### What's Next

* [HubSpot](/docs/adapter-types-hubspot)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
