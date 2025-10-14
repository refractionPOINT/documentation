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

Reference: Error Codes

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Reference: Error Codes

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

The follow error codes are found within various Report (`*_REP`) events found within the [EDR Events](/v2/docs/reference-edr-events), often in response to an [endpoint agent command](/v2/docs/endpoint-agent-commands).

| Error Code | Value |
| --- | --- |
| ERROR\_SUCCESS | 0, 200 |
| ERROR\_INVALID\_FUNCTION | 1 |
| ERROR\_FILE\_NOT\_FOUND | 2 |
| ERROR\_PATH\_NOT\_FOUND | 3 |
| ERROR\_ACCESS\_DENIED | 5 |
| ERROR\_INVALID\_HANDLE | 6 |
| ERROR\_NOT\_ENOUGH\_MEMORY | 8 |
| ERROR\_INVALID\_DRIVE | 15 |
| ERROR\_CURRENT\_DIRECTORY | 16 |
| ERROR\_WRITE\_PROTECT | 19 |
| ERROR\_CRC | 23 |
| ERROR\_SEEK | 25 |
| ERROR\_WRITE\_FAULT | 29 |
| ERROR\_READ\_FAULT | 30 |
| ERROR\_SHARING\_VIOLATION | 32 |
| ERROR\_LOCK\_VIOLATION | 33 |
| ERROR\_HANDLE\_EOF | 38 |
| ERROR\_HANDLE\_DISK\_FULL | 39 |
| ERROR\_NOT\_SUPPORTED | 50 |
| ERROR\_BAD\_NETPATH | 53 |
| ERROR\_NETWORK\_BUSY | 54 |
| ERROR\_NETWORK\_ACCESS\_DENIED | 65 |
| ERROR\_BAD\_NET\_NAME | 67 |
| ERROR\_FILE\_EXISTS | 80 |
| ERROR\_INVALID\_PASSWORD | 86 |
| ERROR\_INVALID\_PARAMETER | 87 |
| ERROR\_BROKEN\_PIPE | 109 |
| ERROR\_OPEN\_FAILED | 110 |
| ERROR\_BUFFER\_OVERFLOW | 111 |
| ERROR\_DISK\_FULL | 112 |
| ERROR\_INVALID\_NAME | 123 |
| ERROR\_NEGATIVE\_SEEK | 131 |
| ERROR\_DIR\_NOT\_EMPTY | 145 |
| ERROR\_BUSY | 170 |
| ERROR\_BAD\_EXE\_FORMAT | 193 |
| ERROR\_FILENAME\_EXCED\_RANGE | 206 |
| ERROR\_FILE\_TOO\_LARGE | 223 |
| ERROR\_DIRECTORY | 267 |
| ERROR\_INVALID\_ADDRESS | 487 |
| ERROR\_TIMEOUT | 1460 |

## Payload Specific

When dealing with Payloads or Artifact collection, you may receive HTTP specific error codes:
<https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>

## Yara Specific

When doing Yara scanning operations, you may receive Yara specific error codes.

These are documented here:
<https://github.com/VirusTotal/yara/blob/master/libyara/include/yara/error.h>

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

* [Endpoint Agent Commands](/docs/endpoint-agent-commands)
* [Endpoint Agent Events Overview](/docs/endpoint-agent-events-overview)
* [Reference: Endpoint Agent Commands](/docs/reference-endpoint-agent-commands)
* [Reference: EDR Events](/docs/reference-edr-events)

---

###### What's Next

* [Template Strings and Transforms](/docs/template-strings-and-transforms)

Table of contents

+ [Payload Specific](#payload-specific)
+ [Yara Specific](#yara-specific)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [events](/docs/en/tags/events)
* [reference](/docs/en/tags/reference)
