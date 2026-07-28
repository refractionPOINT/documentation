# IP ASN

> No Subscription Required
>
> LimaCharlie gives all users access to this integration free of charge. You do not need a subscription.

If you subscribe to the `ip-geo` [add-on](https://app.limacharlie.io/add-ons/detail/ip-geo), you can use the `ip-asn` resource as an API-based lookup. The lookup resolves an IP address to its Autonomous System Number (ASN) and organization.

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

This rule does these steps:

- When a `USER_LOGIN` event occurs, the rule gets the `event/SOURCE_IP` value and looks it up with the `api/ip-asn` resource
- When `api/ip-asn` sends a response, the rule evaluates it with `metadata_rules` to see if the ASN matches 13335 (Cloudflare)

The metadata has this format:

```json
{
  "autonomous_system_number": 13335,
  "autonomous_system_organization": "Cloudflare, Inc."
}
```

The ASN data comes from the MaxMind GeoLite2-ASN database. For more information, see [maxmind.com](http://www.maxmind.com).

## See Also

- [IP Geolocation](ip-geolocation.md) — country, city, and location data
- [Behavioral Detection — First-Seen with Lookup Metadata](../../3-detection-response/behavioral-detection.md#first-seen-with-lookup-metadata) — how to use ASN in suppression keys
