# Elastic

Output events and detections to [Elastic](https://www.elastic.co/).

- `addresses`: the IPs or DNS names to send the data to.
- `index`: the index name to send the data to.
- `username`: the user name, if you authenticate with a user name and a password. (Use either a user name and a password, or an API key.)
- `password`: the password, if you authenticate with a user name and a password.
- `cloud_id`: the Cloud ID from Elastic.
- `api_key`: the API key, if you authenticate with an API key. (Use either a user name and a password, or an API key.)

Example:

```text
addresses: 11.10.10.11,11.10.11.11
username: some
password: pass1234
index: limacharlie
```

## Related articles

- [OpenSearch](opensearch.md)

## What's Next

- [Google Cloud BigQuery](bigquery.md)
