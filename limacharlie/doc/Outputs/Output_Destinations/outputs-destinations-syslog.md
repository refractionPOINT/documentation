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

Thank you for your feedback! Our team will get back to you

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change

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
