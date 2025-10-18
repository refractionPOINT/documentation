# Create a D&R Rule Using a Threat Feed

A common use case for rules is to use them to compare telemetry against known malicious IPs, domain names, or file hashes via threat feeds. With LimaCharlie, it is easy to leverage public threat feeds or create your own.

To configure a threat feed, it must first be enabled within the Add-ons Marketplace. First, select a threat feed from the plethora available for free. In the following example, we will enable `crimeware-ips`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/crimeware-ips\(1\).png)

Select `Subscribe`, which will make the feed available to the respective Organization.

Once subscribed, you can write a D&R rule to detect whenever there is a match to an IP within the threat feed. Navigate to `D&R Rules` within the web application main page, and select `+ New Rule`. Begin your rule with the following template:


    event: NETWORK_CONNECTIONS
    op: lookup
    path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
    resource: hive://lookup/crimeware-ips


## Additional Telemetry Points

Configure a lookup based on file hash:


    op: lookup
    event: CODE_IDENTITY
    path: event/HASH
    resource: hive://lookup/my-hash-lookup


Configure a lookup based on domain name(s):


    op: lookup
    event: DNS_REQUEST
    path: event/DOMAIN_NAME
    resource: hive://lookup/my-dns-lookup