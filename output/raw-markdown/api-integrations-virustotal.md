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

VirusTotal

* 29 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# VirusTotal

* Updated on 29 Aug 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## API Keys

The VirusTotal API key is added via the [integrations](https://docs.limacharlie.io/v2/docs/add-ons-api-integrations#configuration) menu within LimaCharlie.

## Usage

With the `vt` [add-on](https://app.limacharlie.io/add-ons/detail/vt) subscribed and a VirusTotal API Key configured in the Integrations page, VirusTotal can be used as an API-based lookup.

```
event: CODE_IDENTITY
op: lookup
path: event/HASH
resource: hive://lookup/vt
metadata_rules:
  op: is greater than
  value: 1
  path: /
  length of: true
```

Step-by-step, this rule will do the following:

* Upon seeing a `CODE_IDENTITY` event, retrieve the `event/HASH` value and send it to VirusTotal via the `api/vt` resource.
* Upon receiving a response from `api/vt`, evaluate it using `metadata_rules` to see if the length of the response is greater than 1 (in this case meaning that more than 1 vendor reporting a hash is bad).

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

* [VirusTotal Integration](/docs/tutorials-integratons-virustotal-integration)

---

###### What's Next

* [Extensions](/docs/extensions)

Table of contents

+ [API Keys](#api-keys)
+ [Usage](#usage)

Tags

* [add-ons](/docs/en/tags/add-ons)
