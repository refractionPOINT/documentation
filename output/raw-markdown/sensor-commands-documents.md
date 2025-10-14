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

Documents

* 10 May 2023
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# Documents

* Updated on 10 May 2023
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

### doc\_cache\_get

Retrieve a document / file that was cached on the sensor.

**Platforms:**

**Response Event:**
 [GET\_DOCUMENT\_REP](/v1/docs/reference-events-responses-documents)

This command is currently listed to the following document types:

* .bat
* .js
* .ps1
* .sh
* .py
* .exe
* .scr
* .pdf
* .doc
* .docm
* .docx
* .ppt
* .pptm
* .pptx
* .xlt
* .xlsm
* .xlsx
* .vbs
* .rtf
* .hta
* .lnk
* Any files created in `system32` on Windows.

**Usage:**

```
usage: doc_cache_get [-h] [-f FILE_PATTERN] [-s HASHSTR]

optional arguments:
  -f FILE_PATTERN, --file_pattern FILE_PATTERN
                        a pattern to match on the file path and name of the
                        document, simple wildcards ? and * are supported
  -s HASHSTR, --hash HASHSTR
                        hash of the document to get
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

###### What's Next

* [File and Registry Integrity Monitoring](/v1/docs/sensor-commands-fim)

Table of contents
