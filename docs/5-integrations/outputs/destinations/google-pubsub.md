# Google Cloud Pubsub

Output events and detections to a Pubsub topic.

- `secret_key`: the secret json key that identifies a service account.
- `project`: the name of the GCP Project that contains the Topic.
- `topic`: the specific value to use as a topic.

Example:

```text
project: my-project
topic: telemetry
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
```
