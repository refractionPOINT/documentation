# Google Cloud Storage

Output events and detections to a GCS bucket.

You can also use this output with Google Chronicle.

If you use Google Chronicle, you can send the telemetry that you collect in LimaCharlie to Chronicle. To set this up, create an output in LimaCharlie to a GCS bucket.

- `bucket`: the path to the GCS bucket.
- `secret_key`: the secret json key that identifies a service account.
- `sec_per_file`: the number of seconds after which a file is cut and uploaded (default 120, maximum 3600).
- `is_compression`: if set to "true", the data is gzipped before upload.
- `is_indexing`: if set to "true", files are written under a time-based directory structure (`year/month/day/hour/`) instead of flat files with random names. See [File organization](#file-organization) below.
- `dir`: the directory prefix for the files on the remote host.
- `is_no_sharding`: do not add a shard directory at the root of the generated files.

Example:

```text
bucket: my-bucket-name
secret_key: {
  "type": "service_account",
  "project_id": "my-lc-data",
  "private_key_id": "EXAMPLE_KEY_ID_REPLACE_WITH_YOURS",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...(your actual private key here)...\n-----END PRIVATE KEY-----\n",
  "client_email": "my-service-writer@my-lc-data.iam.gserviceaccount.com",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-service-writer%40my-lc-data.iam.gserviceaccount.com"
}
is_indexing: "true"
is_no_sharding: "true"
is_compression: "true"
```

## File Organization

By default, each batch of data is uploaded as a flat file with a random (UUID) name at the root of the bucket, or under `dir` if you set it. The file names have no order. Use this mode for pipelines that list and consume all new objects, and that ignore the names.

To organize files by date and time, set `is_indexing` to `"true"`. Files are then written under a time-based directory structure:

```text
[dir/][shard/]year/month/day/hour/d{stream-id}_{counter}[.gz]
```

For example: `logs/1/2026/7/7/13/d1b2c3d4-e5f6-7890-abcd-ef1234567890_12.gz`

- The timestamp components are in **UTC**. They show when the batch was uploaded.
- Data files begin with a `d` prefix.
- `shard` is a single hexadecimal character that spreads the write load across key prefixes. To make the paths start at the year, set `is_no_sharding` to `"true"`.
- Directory components are not zero-padded (July is `7`, not `07`). A plain lexical sort of the object keys is thus not strictly chronological. If the order is important, parse the path components as numbers.
- The `sec_per_file` value controls how often a new file is created.

## Related articles

- [Building Reports with BigQuery + Looker Studio](../../../4-data-queries/tutorials/bigquery-looker-studio.md)
- [Google Cloud Pubsub](google-pubsub.md)
- [Google Cloud BigQuery](bigquery.md)
- [Google Workspace](../../../2-sensors-deployment/adapters/types/google-workspace.md)
- [Google Cloud Storage](../../../2-sensors-deployment/adapters/types/google-cloud-storage.md)
- [Google Cloud Pubsub](../../../2-sensors-deployment/adapters/types/google-cloud-pubsub.md)
- [Tutorial: Ingesting Google Cloud Logs](../../../2-sensors-deployment/adapters/tutorials/google-cloud-logs.md)
- [Google Cloud](../../extensions/cloud-cli/google-cloud.md)

## What's Next

- [Humio](humio.md)
