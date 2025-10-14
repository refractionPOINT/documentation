# Managed Rulesets

In addition to LimaCharlie's powerful custom detection & response capabilities, we also offer native integration with several managed rulesets. LimaCharlie currently offers:

* Sigma Rules
* SnapAttack Community Edition
* SOC Prime
* Soteria
  + AWS
  + EDR
  + Microsoft/Office 365

## A Word on Managed Rulesets

While managed rulesets can help your organizations achieve detection and response capabilities quickly, not all detections are suitable for every environment.

Ensure that you are fine-tuning managed rulesets within your environment via enabling/disabling rules or via False Positive controls.

Managed rulesets offer several advantages, such as:

* Providing out-of-the-box coverage for common threats, reducing the time and effort to develop in-house rules.
* Curated rulesets are maintained and updated by their respective parties, often covering the latest threats.
* A foundation for building complex detection logic utilizing managed rulesets as inspiration.

Every environment is unique, and we recommend choosing rulesets that benefit your need(s) and/or use case(s).

## What's the difference between Sigma and Soteria rules?

[Sigma](https://github.com/SigmaHQ/sigma) is an open source project that aims at creating a generic query language for security and rules. It looks up known anomalies and Common Vulnerabilities and Exposures (CVEs).

As Sigma is an open source project,

* applying the Sigma ruleset is free
* there will be a higher rate of false positives

[Soteria](https://soteria.io/) is a US-based MSSP that has been using LimaCharlie for a long time. They developed a corpus of hundreds of behavioral signatures for Windows / Mac / Linux (signature not in terms of a hash, but in terms of a rule that describes a behavior). With one click, you can apply their rules in a managed way. When Soteria updates the rules for their customers, you will get those updates in real time as well.

As Soteria is a managed ruleset,

* applying the Soteria ruleset costs $0.5 per endpoint per month
* the rate of false positives is much lower