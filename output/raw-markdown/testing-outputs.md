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

Testing Outputs

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Testing Outputs

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

The easiest way to test if the outputs are configured correctly is to set the stream to `Audit` which will send auditing events about activity around the management of the platform in the cloud. You can then edit the same output or make any other change on the platform, which will trigger an audit event to be sent.

After you have confirmed that the output configurations works, you can switch the data stream from `Audit` to the one you are looking to use.

If you are running into an error configuring an output, the error details will be listed in the Platform Logs section under Errors, with the key that looks like `outputs/OUTPUT_NAME`.

If an output fails, it gets disabled temporarily to avoid spam. It will be re-enabled automatically after a while, or you can force it to be re-enabled by updating the configuration.

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

* [Template Strings and Transforms](/docs/template-strings-and-transforms)

---

###### What's Next

* [Template Strings and Transforms](/docs/template-strings-and-transforms-3)

Tags

* [outputs](/docs/en/tags/outputs)
