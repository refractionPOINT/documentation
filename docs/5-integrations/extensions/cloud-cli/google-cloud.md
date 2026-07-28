# Google Cloud

The Google Cloud command line interface, or gcloud CLI, lets you create and manage Google Cloud resources and services on the command line. This component of the Cloud CLI Extension lets you interact with Google Cloud directly from LimaCharlie.

This extension uses [Google Cloud's native CLI tool](https://cloud.google.com/cli).

## Example

This example stops the specified GCP compute instance.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "gcloud" }}'
    command_tokens:
      - compute
      - instances
      - stop
      - '{{ .routing.hostname }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the Google Cloud CLI capabilities, you need:

- A GCP service account JSON key. See the [service account keys guide](https://cloud.google.com/iam/docs/keys-create-delete) from Google Cloud.
- Create a secret in the secrets manager in this format:

  ```json
  {
      "type": "",
      "project_id": "",
      "private_key_id": "",
      "private_key": "",
      "client_email": "",
      "client_id": "",
      "auth_uri": "",
      "token_uri": "",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "",
      "universe_domain": "googleapis.com"
  }
  ```
