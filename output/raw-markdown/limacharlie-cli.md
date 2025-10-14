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

LimaCharlie CLI

* 15 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# LimaCharlie CLI

* Updated on 15 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie CLI Extension allows you to issue [LimaCharlie CLI commands](/v2/docs/limacharlie-sdk) using extension requests.

Repo - <https://github.com/refractionPOINT/python-limacharlie>

You may use a  rule to trigger a LimaCharlie CLI event. For example the following rule response actions:

```
- action: extension request
  extension action: run
  extension name: limacharlie-cli
  extension request:
    command_line: '{{ "limacharlie configs push --dry-run --oid" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

* [LimaCharlie SDK & CLI](/docs/limacharlie-sdk)

---

###### What's Next

* [BinLib](/docs/binlib)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
