# Google Cloud Storage

## Overview

This Adapter ingests files and blobs that are stored in Google Cloud Storage (GCS).

By default, this adapter operates as a sink: it "consumes" the files in the GCS bucket. It deletes each file after it ingests the file.

## Configurations

Adapter Type: `gcs`

- `client_options`: see [common adapter configuration](../usage.md).
- `bucket_name`: the name of the bucket to ingest from.
- `service_account_creds`: the string version of the JSON credentials for a (Google) Service Account that accesses the bucket.
- `prefix`: only ingest files that have this path prefix.
- `single_load`: if `true`, the adapter does not operate as a sink. It ingests all files in the bucket one time and then exits.

### Infrastructure as Code Deployment

```python
sensor_type: "gcs"
gcs:
  bucket_name: "your-gcs-bucket-for-limacharlie-logs"
  service_account_creds: "hive://secret/gcs-service-account"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GCS"
    platform: "json"
    sensor_seed_key: "gcs-log-processor"
    mapping:
      sensor_hostname_path: "resource.labels.instance_id"
      event_type_path: "logName"
      event_time_path: "timestamp"
    indexing: []
  # Optional configuration
  prefix: "security_logs/firewall/"  # Filter by path prefix
  parallel_fetch: 5                  # Parallel downloads
  single_load: false                 # Continuous processing
```

## API Doc

See the [official documentation](https://cloud.google.com/storage).
