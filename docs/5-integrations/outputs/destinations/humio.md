# Humio

Output events and detections to the [Humio.com](https://humio.com) service.

- `humio_repo`: the name of the humio repo to upload to.
- `humio_api_token`: the humio ingestion token.
- `endpoint_url`: an optional custom endpoint URL. If you deploy Humio on-prem, set this value to the address of that deployment. The default is the Humio cloud.

Example:

```text
humio_repo: sandbox
humio_api_token: fdkoefj0erigjre8iANUDBFyfjfoerjfi9erge
```

Note: To [parse timestamps](https://docs.humio.com/reference/query-functions/functions/parsetimestamp/) correctly, it can be necessary to [create a new parser in Humio](https://docs.humio.com/docs/parsers/creating-a-parser/). You can use this JSON parser:

```text
parseJson() | parseTimestamp(field=@timestamp,format="unixTimeMillis",timezone="Etc/UTC")
```

For the Community Edition of Humio, the `endpoint_url` is: `https://cloud.community.humio.com`.
