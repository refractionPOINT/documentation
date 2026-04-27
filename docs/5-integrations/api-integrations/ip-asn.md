# IP ASN

> No Subscription Required
>
> LimaCharlie provides access to this integration free of charge for all users, so no additional subscription is required.

With the `ip-geo` [add-on](https://app.limacharlie.io/add-ons/detail/ip-geo) subscribed, the `ip-asn` resource can be used as an API-based lookup to resolve IP addresses to their Autonomous System Number (ASN) and organization.

```yaml
event: USER_LOGIN
op: lookup
resource: lcr://api/ip-asn
path: event/SOURCE_IP
metadata_rules:
  op: is
  value: 13335
  path: autonomous_system_number
```

Step-by-step, this rule will do the following:

- Upon seeing a `USER_LOGIN` event, retrieve the `event/SOURCE_IP` value and look it up via the `api/ip-asn` resource
- Upon receiving a response from `api/ip-asn`, evaluate it using `metadata_rules` to see if the ASN matches 13335 (Cloudflare)

The format of the metadata returned looks like this:

```json
{
  "autonomous_system_number": 13335,
  "autonomous_system_organization": "Cloudflare, Inc."
}
```

The ASN data comes from the MaxMind GeoLite2-ASN database. For more information, visit [maxmind.com](http://www.maxmind.com).

## See Also

- [IP Geolocation](ip-geolocation.md) — country, city, and location data
- [Behavioral Detection — First-Seen with Lookup Metadata](../../3-detection-response/behavioral-detection.md#first-seen-with-lookup-metadata) — using ASN in suppression keys
