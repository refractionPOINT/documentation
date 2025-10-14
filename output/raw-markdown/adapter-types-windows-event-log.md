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

Windows Event Log

* 30 Jul 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Windows Event Log

* Updated on 30 Jul 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## Overview

This Adapter allows you to connect to the local Windows Event Logs API on Windows. This means this Adapter is only available from Windows builds and only works locally (will not connect to remote Windows instances).

## Configurations

Adapter Type: `wel`

* `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).
* `evt_sources`: a comma separated list of elements in the format `SOURCE:FILTER`, where `SOURCE` is an Event Source name like `Application`, `System` or `Security` and `FILTER` is an `XPath` filter value as described in the documentation linked below.

### Infrastructure as Code Deployment

```
# Windows Event Log (WEL) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-windows-event-log

# Basic Event Sources:
# evt_sources: "Security,System,Application"

# With XPath Filters:
# evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System:'*[System[Provider[@Name=\"Microsoft-Windows-Kernel-General\"]]]'"

# File-Based Sources:
# evt_sources: "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx:'*[System[(EventID=4624)]]'"

  wel:
    evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System,Application"
    client_options:
      identity:
        oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        installation_key: "YOUR_LC_INSTALLATION_KEY_WEL"
      hostname: "prod-dc01.example.local"
      platform: "windows"
      sensor_seed_key: "wel-collector"
    write_timeout_sec: 30
```

### XPath Filter Examples

Security Events (High Priority):

```
  Security:'*[System[(Level=1 or Level=2 or Level=3)]]'
```

Logon Events Only:

```
  Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'
```

System Errors:

```
  System:'*[System[(Level=1 or Level=2)]]'
```

Specific Provider:

```
  Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'
```

## API Doc

See the [official documentation](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

* [Windows Event Logs](/docs/adapter-examples-windows-event-logs)
* [Ingesting Windows Event Logs](/docs/ingesting-windows-event-logs)
* [Hayabusa](/docs/ext-hayabusa)

---

###### What's Next

* [Zendesk](/docs/adapter-types-zendesk)

Table of contents

+ [Overview](#overview)
+ [Configurations](#configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
