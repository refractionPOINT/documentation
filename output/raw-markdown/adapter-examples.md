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

Adapter Examples

3 Articles  in this category

Share this

* Print
* Share
* Dark

  Light

Contents

# Adapter Examples

3 Articles  in this category

* Share
* Dark

  Light

---

[## Stdin

This example is similar to the Syslog example above, except it uses the CLI Adapter and receives the data from the CLI's STDIN interface. This method is perfect for ingesting arbitrary logs on disk or from other applications locally. ./lc\_adapte...](/docs/adapter-examples-stdin)

Updated on : 10 Oct 2025

[## Stdin JSON

This example is similar to the Stdin example above, except it assumes the data being read is JSON, not just text. If your data source is already JSON, it's much simpler to let LimaCharlie do the JSON parsing directly. ./lc\_adapter stdin client\_opt...](/docs/adapter-examples-stdin-json)

Updated on : 15 Aug 2025

[## Windows Event Logs

This example shows collecting Windows Event Logs ( wel ) from a Windows box natively (and therefore is only available using the Windows Adapter ). This is useful for cases where you'd like to collect WEL without running the LimaCharlie Windows Agen...](/docs/adapter-examples-windows-event-logs)

Updated on : 28 May 2025
