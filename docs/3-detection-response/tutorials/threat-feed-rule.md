# Create a D&R Rule Using a Threat Feed

Rules often compare telemetry against known malicious IP addresses, domain names, or file hashes. A threat feed supplies these values. In LimaCharlie, you can use a public threat feed or create your own.

Before you configure a threat feed, enable it in the Add-ons Marketplace. Select one of the many threat feeds that are free. The example that follows enables `crimeware-ips`.

![crimeware ips](../../assets/images/crimeware-ips(1).png)

Select `Subscribe`. The feed then becomes available to the organization.

After you subscribe, write a D&R rule that detects a match to an IP address in the threat feed.

1. On the main page of the web app, go to `D&R Rules`.
2. Select `+ New Rule`.
3. Start the rule with this template:

    ```yaml
    event: NETWORK_CONNECTIONS
    op: lookup
    path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
    resource: hive://lookup/crimeware-ips
    ```

## Additional Telemetry Points

Configure a lookup that uses a file hash:

```yaml
op: lookup
event: CODE_IDENTITY
path: event/HASH
resource: hive://lookup/my-hash-lookup
```

Configure a lookup that uses domain names:

```yaml
op: lookup
event: DNS_REQUEST
path: event/DOMAIN_NAME
resource: hive://lookup/my-dns-lookup
```
