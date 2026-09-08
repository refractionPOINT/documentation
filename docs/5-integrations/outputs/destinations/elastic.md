# Elastic

Output events and detections to [Elastic](https://www.elastic.co/).

- `addresses`: the IPs or DNS where to send the data to.
- `index`: the index name to send data to.
- `username`: user name if using username/password auth. (use either username/password -or- API key)
- `password`: password if using username/password auth.
- `cloud_id`: Cloud ID from Elastic.
- `api_key`: API key; if using it for auth. (use either username/password -or- API key)
- `is_create_action`: if `true`, the `_bulk` request uses the `create` action instead of `index`. Required when sending to a data stream.

Example:

```text
addresses: 11.10.10.11,11.10.11.11
username: some
password: pass1234
index: limacharlie
```

## Sending to a data stream

Elasticsearch [data streams](https://www.elastic.co/docs/manage-data/data-store/data-streams)
support only the `create` action in a
[`_bulk`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk)
request. By default this output uses the `index` action, which a data stream
rejects, so set `is_create_action` to `true` when the value of `index` names a
data stream:

```text
addresses: https://elastic.mydomain.com:9200
api_key: some-api-key
index: logs-limacharlie-default
is_create_action: true
```

The `index` value stays a plain name; Elastic resolves it to the data stream's
backing indices and applies the lifecycle policy configured on the Elastic side.

## Related articles

- [OpenSearch](opensearch.md)

## What's Next

- [Google Cloud BigQuery](bigquery.md)
