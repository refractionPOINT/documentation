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

IP Geolocation

* 29 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# IP Geolocation

* Updated on 29 Aug 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

> No Subscription Required
>
> LimaCharlie provides access to this integration free of charge for all users, so no additional subscription is required.

With the `ip-geo` [add-on](https://app.limacharlie.io/add-ons/detail/ip-geo) subscribed, it can be used as an API-based lookup.

```
event: CONNECTED
op: lookup
resource: hive://lookup/ip-geo
path: routing/ext_ip
metadata_rules:
  op: is
  value: true
  path: country/is_in_european_union
```

Step-by-step, this rule will do the following:

* Upon seeing a `CONNECTED` event, retrieve the `routing/ext_ip` value and send it to MaxMind via the `api/ip-geo` resource
* Upon receiving a response from `api/ip-geo`, evaluate it using `metadata_rules` to see if the country associated with the IP is located in the EU

The format of the metadata returned is documented [here](https://github.com/maxmind/MaxMind-DB-Reader-python) and looks like this:

```
{
  "country": {
    "geoname_id": 2750405,
    "iso_code": "NL",
    "is_in_european_union": true,
    "names": {
      "ru": "\u041d\u0438\u0434\u0435\u0440\u043b\u0430\u043d\u0434\u044b",
      "fr": "Pays-Bas",
      "en": "Netherlands",
      "de": "Niederlande",
      "zh-CN": "\u8377\u5170",
      "pt-BR": "Holanda",
      "ja": "\u30aa\u30e9\u30f3\u30c0\u738b\u56fd",
      "es": "Holanda"
    }
  },
  "location": {
    "latitude": 52.3824,
    "accuracy_radius": 100,
    "time_zone": "Europe/Amsterdam",
    "longitude": 4.8995
  },
  "continent": {
    "geoname_id": 6255148,
    "code": "EU",
    "names": {
      "ru": "\u0415\u0432\u0440\u043e\u043f\u0430",
      "fr": "Europe",
      "en": "Europe",
      "de": "Europa",
      "zh-CN": "\u6b27\u6d32",
      "pt-BR": "Europa",
      "ja": "\u30e8\u30fc\u30ed\u30c3\u30d1",
      "es": "Europa"
    }
  },
  "registered_country": {
    "geoname_id": 2750405,
    "iso_code": "NL",
    "is_in_european_union": true,
    "names": {
      "ru": "\u041d\u0438\u0434\u0435\u0440\u043b\u0430\u043d\u0434\u044b",
      "fr": "Pays-Bas",
      "en": "Netherlands",
      "de": "Niederlande",
      "zh-CN": "\u8377\u5170",
      "pt-BR": "Holanda",
      "ja": "\u30aa\u30e9\u30f3\u30c0\u738b\u56fd",
      "es": "Holanda"
    }
  }
}
```

The geolocation data comes from GeoLite2 data created by [MaxMind](http://www.maxmind.com).

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

* [Pangea](/docs/api-integrations-pangea)

Tags

* [add-ons](/docs/en/tags/add-ons)
