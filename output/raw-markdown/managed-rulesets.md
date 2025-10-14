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

Managed Rulesets

* 13 Nov 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Managed Rulesets

* Updated on 13 Nov 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

In addition to LimaCharlie's powerful custom detection & response capabilities, we also offer native integration with several managed rulesets. LimaCharlie currently offers:

* [Sigma Rules](/v2/docs/sigma-rules)
* SnapAttack Community Edition
* [SOC Prime](/v2/docs/soc-prime-rules)
* [Soteria](/v2/docs/soteria-rules)

  + AWS
  + EDR
  + Microsoft/Office 365

A Word on Managed Rulesets

While managed rulesets can help your organizations achieve detection and response capabilities quickly, not all detections are suitable for every environment.

Ensure that you are fine-tuning managed rulesets within your environment via enabling/disabling rules or via [False Positive](/v2/docs/false-positive-rules) controls.

Managed rulesets offer several advantages, such as:

* Providing out-of-the-box coverage for common threats, reducing the time and effort to develop in-house rules.
* Curated rulesets are maintained and updated by their respective parties, often covering the latest threats.
* A foundation for building complex detection logic utilizing managed rulesets as inspiration.

Every environment is unique, and we recommend choosing rulesets that benefit your need(s) and/or use case(s).

What's the difference between Sigma and Soteria rules?

[Sigma](https://github.com/SigmaHQ/sigma) is an open source project that aims at creating a generic query language for security and  rules. It looks up known anomalies and Common Vulnerabilities and Exposures (CVEs).

As Sigma is an open source project,

* applying the Sigma ruleset is free
* there will be a higher rate of false positives

[Soteria](https://soteria.io/) is a US-based MSSP that has been using LimaCharlie for a long time. They developed a corpus of hundreds of behavioral signatures for Windows / Mac / Linux (signature not in terms of a hash, but in terms of a rule that describes a behavior). With one click, you can apply their rules in a managed way. When Soteria updates the rules for their customers, you will get those updates in real time as well.

As Soteria is a managed ruleset,

* applying the Soteria ruleset costs $0.5 per endpoint per month
* the rate of false positives is much lower

Amazon Web Services

Endpoint Detection & Response

Managed Security Services Provider

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

* [Detection and Response Examples](/docs/detection-and-response-examples)
* [Detection and Response](/docs/detection-and-response)
* [Soteria M365 Rules](/docs/soteria-m365-rules)
* [Soteria AWS Rules](/docs/soteria-aws-rules)
* [Stateful Rules](/docs/stateful-rules)
* [Detection on Alternate Targets](/docs/detection-on-alternate-targets)
* [Soteria Rules](/docs/soteria-rules)
* [Soteria EDR Rules](/docs/soteria-edr-rules)
* [Sigma Rules](/docs/sigma-rules)
* [Sigma Converter](/docs/sigma-converter)
* [Quickstart](/docs/quickstart)
* [SOC Prime Rules](/docs/soc-prime-rules)

---

###### What's Next

* [Sigma Rules](/docs/sigma-rules)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
