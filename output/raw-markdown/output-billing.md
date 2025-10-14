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

Output Billing

* 07 Dec 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Output Billing

* Updated on 07 Dec 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie aims to bill outputs at cost. This means that as a default outputs are billed accordingly to the [published pricing](https://limacharlie.io/pricing).

An exception to this is outputs that use Google Cloud Platform mechanism where the destination region is the same as the one the relevant LimaCharlie datacenter lives in. In those cases, outputs are not billed.

Here is a list of the relevant regions for the various LimaCharlie datacenter.

* USA: `us-central1`
* Canada: `northamerica-northeast1`
* Europe: `europe-west4`
* UK: `europe-west2`
* India: `asia-south1`
* Australia: `australia-southeast1`

The supported GCP mechanism for free output are:

* `gcs`
* `pubsub`
* `bigquery`

Google Cloud Platform general region list: <https://cloud.google.com/about/locations>

IP ranges of GCP resources per region change over time. Google publishes these ranges as a JSON file here: <https://www.gstatic.com/ipranges/cloud.json>

Google Cloud Platform

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

* [Amazon S3](/docs/outputs-destinations-amazon-s3)
