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

Syslog

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Syslog

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

## Syslog (TCP)

Output events and detections to a syslog target.

* `dest_host`: the IP or DNS and port to connect to, format `www.myorg.com:514`.
* `is_tls`: if `true` will output over TCP/TLS.
* `is_strict_tls`: if `true` will enforce validation of TLS certs.
* `is_no_header`: if `true` will not emit a Syslog header before every message. This effectively turns it into a TCP output.
* `structured_data`: arbitrary field to include in syslog "Structured Data" headers. Sometimes useful for cloud SIEMs integration.

Example:

```
dest_host: storage.corp.com
is_tls: "true"
is_strict_tls: "true"
is_no_header: "false"
```

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

* [Syslog](/docs/adapter-types-syslog)

---

###### What's Next

* [Tines](/docs/output-destinations-tines)

Table of contents

+ [Syslog (TCP)](#syslog-tcp-)

Tags

* [outputs](/docs/en/tags/outputs)
