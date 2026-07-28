# OpenSearch

Output events and detections to [OpenSearch](https://opensearch.org/).

- `addresses`: the IPs or DNS names to send the data to
- `index`: the index name to send the data to
- `username`: the user name, if you authenticate with a user name and a password
- `password`: the password, if you authenticate with a user name and a password

Example:

```text
addresses: https://1.2.3.4:9200, https://elastic.mydomain.com:9200
username: some
password: pass1234
index: limacharlie-events
```

## Related articles

- [Elastic](elastic.md)
- [ASW](scp.md)
