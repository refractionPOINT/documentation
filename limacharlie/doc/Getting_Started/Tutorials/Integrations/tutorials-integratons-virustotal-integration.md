---

VirusTotal Integration

* 07 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# VirusTotal Integration

* Updated on 07 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

You can easily integrate LimaCharlie with VirusTotal to enhance your data enrichment and detections. You will need a VirusTotal API key in order to utilize this add-on.

VirusTotal Data Caching

The free tier of VirusTotal allows four lookups per minute via the API. LimaCharlie employs a global cache of VirusTotal requests which should significantly reduce costs if you are using VirusTotal at scale. VirusTotal requests are cached for 3 days.

Once you have your VirusTotal API key, you can add it in the Organization integrations section of the LimaCharlie web app.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/vt-key.png)

Once you have entered your API key, you can then create a  rule to perform a lookup of a hash. For example, the following rule will let you know if there is a hit from VirusTotal on a hash with at least two different engines.

```
path: event/HASH
op: lookup
resource: hives://lookup/vt
event: CODE_IDENTITY
metadata_rules:
  path: /
  value: 2
  length of: true
  op: is greater than
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

* [VirusTotal](/docs/api-integrations-virustotal)
* [Detection and Response Examples](/docs/detection-and-response-examples)

---

###### What's Next

* [Building Reports with BigQuery + Looker Studio](/docs/tutorials-reporting-building-reports-with-bigquery-looker-studio)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
* [tutorial](/docs/en/tags/tutorial "Tutorial")
