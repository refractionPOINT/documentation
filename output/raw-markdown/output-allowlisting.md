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

Adding Outputs to an Allow List

* 06 Jun 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Adding Outputs to an Allow List

* Updated on 06 Jun 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

At LimaCharlie, we rely on infrastructure with auto-scalers, and thus do not have static IPs nor a CIDR that you can rely on for an allow list (or "whitelisting").

Typically, the concern around adding IPs to an allow list for Outputs is based on wanting to limit abuse and ensure that data from webhooks is truly coming from LimaCharlie and not other sources. To address this, we provide a `secret_key` parameter that can be used as a *shared secret* between LimaCharlie and your webhook receiver. When we issue a webhook, we include a `lc-signature` header that is an HMAC of the content of the webhook using the shared `secret_key`.

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

* [Output Billing](/docs/output-billing)

Tags

* [outputs](/docs/en/tags/outputs)
