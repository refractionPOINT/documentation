# Google Cloud Storage

Output events and detections to a GCS bucket.

Looking for Google Chronicle?

If you already use Google Chronicle, we make it easy to send telemetry you've collected in LimaCharlie to Chronicle. You can get that set up by creating an Output in LimaCharlie to a GCS bucket.

  * `bucket`: the path to the GCS bucket.

  * `secret_key`: the secret json key identifying a service account.

  * `sec_per_file`: the number of seconds after which a file is cut and uploaded.

  * `is_compression`: if set to "true", data will be gzipped before upload.

  * `is_indexing`: if set to "true", data is uploaded in a way that makes it searchable.

  * `dir`: the directory prefix where to output the files on the remote host.




Example:


    bucket: my-bucket-name
    secret_key: {
      "type": "service_account",
      "project_id": "my-lc-data",
      "private_key_id": "11b6f4173dedabcdefb779e4afae6d88ddce3cc1",
      "private_key": "-----BEGIN PRIVATE KEY-----\n.....\n-----END PRIVATE KEY-----\n",
      "client_email": "my-service-writer@my-lc-data.iam.gserviceaccount.com",
      "client_id": "102526666608388828174",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-service-writer%40my-lc-data.iam.gserviceaccount.com"
    }
    is_indexing: "true"
    is_compression: "true"
