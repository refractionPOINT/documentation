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

EVTX

* 07 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# EVTX

* Updated on 07 Aug 2025
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

This Adapter allows you to ingest and convert a `.evtx` file into LimaCharlie. The `.evtx` files are the binary format used by Microsoft for Windows Event Logs. This is useful to ingest historical Windows Event Logs, for example during an Incident Response (IR) engagement.

For real-time collection of Windows Event Logs, see the [Windows Event Logs](/v2/docs/ingesting-windows-event-logs) documentation.

## Configurations

Adapter Type: `evtx`

* `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).
* `file_path`: path to the `.evtx` file to ingest.

## API Doc

See the [unofficial documentation on EVTX](https://www.giac.org/paper/gcia/2999/evtx-windows-event-logging/115806).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

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
* [Artifact](/docs/ext-artifact)

---

###### What's Next

* [File](/docs/adapter-types-file)

Table of contents

+ [Overview](#overview)
+ [Configurations](#configurations)
+ [API Doc](#api-doc)

Tags

* [adapters](/docs/en/tags/adapters)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
