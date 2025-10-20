# VirusTotal Integration

You can easily integrate LimaCharlie with VirusTotal to enhance your data enrichment and detections. You will need a VirusTotal API key in order to utilize this add-on.

VirusTotal Data Caching

The free tier of VirusTotal allows four lookups per minute via the API. LimaCharlie employs a global cache of VirusTotal requests which should significantly reduce costs if you are using VirusTotal at scale. VirusTotal requests are cached for 3 days.

Once you have your VirusTotal API key, you can add it in the Organization integrations section of the LimaCharlie web app.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/vt-key.png)

Once you have entered your API key, you can then create a rule to perform a lookup of a hash. For example, the following rule will let you know if there is a hit from VirusTotal on a hash with at least two different engines.

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
