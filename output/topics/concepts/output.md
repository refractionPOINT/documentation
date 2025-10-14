# Output Destinations and Billing

## Output Billing

LimaCharlie aims to bill outputs at cost. This means that as a default, outputs are billed according to the [published pricing](https://limacharlie.io/pricing).

An exception to this is outputs that use Google Cloud Platform mechanisms where the destination region is the same as the one the relevant LimaCharlie datacenter lives in. In those cases, outputs are not billed.

### LimaCharlie Datacenter Regions

Here is a list of the relevant regions for the various LimaCharlie datacenters:

* USA: `us-central1`
* Canada: `northamerica-northeast1`
* Europe: `europe-west4`
* UK: `europe-west2`
* India: `asia-south1`
* Australia: `australia-southeast1`

The supported GCP mechanisms for free output are:

* `gcs`
* `pubsub`
* `bigquery`

**Additional Resources:**
- Google Cloud Platform general region list: <https://cloud.google.com/about/locations>
- IP ranges of GCP resources per region change over time. Google publishes these ranges as a JSON file here: <https://www.gstatic.com/ipranges/cloud.json>

## Supported Output Destinations

### Amazon S3

Output events and detections to an Amazon S3 bucket. If you have your own visualization stack, or you just need the data archived, you can output directly to Amazon S3. This way you don't need any infrastructure.

**Parameters:**

- `bucket`: the path to the AWS S3 bucket
- `secret_key`: AWS secret access key
- `access_key`: AWS access key ID
- `region`: AWS region where the bucket is located

### Apache Kafka

Output events and detections to a Kafka target.

**Parameters:**

- `dest_host`: the IP or DNS and port to connect to, format `kafka.myorg.com`
- `is_tls`: if true will output over TCP/TLS
- `is_strict_tls`: if true will enforce validation of TLS certs

### Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

**Parameters:**

- `connection_string`: the connection string provided by Azure. Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the Azure portal

### Azure Storage Blob

Output events and detections to a Blob Container in Azure Storage Blobs.

**Parameters:**

- `secret_key`: the secret access key for the Blob Container
- `blob_container`: the name of the Blob Container to upload to
- `account_name`: the account name used to authenticate

### Elastic

Output events and detections to Elastic.

**Parameters:**

- `addresses`: the IPs or DNS where to send the data to
- `index`: the index name to send data to
- `username`: user name if using username/password auth (use either username/password -or- API key)
- `password`: password if using username/password auth
- `api_key`: API key if using API key auth

### Google Cloud BigQuery

Output events and detections to a Google Cloud BigQuery Table.

For a practical use case of this output, see this tutorial on pushing Velociraptor data to BigQuery.

**Parameters:**

- `schema`: describes the column names, data types, and other information; should be a JSON schema definition
- `secret_key`: the secret JSON key identifying a service account
- `project`: the GCP Project name where the dataset lives
- `dataset`: the BigQuery dataset name
- `table`: the BigQuery table name

### Google Cloud Pubsub

Output events and detections to a Pubsub topic.

**Parameters:**

- `secret_key`: the secret json key identifying a service account
- `project`: the GCP Project name where the Topic lives
- `topic`: use this specific value as a topic

**Example:**

```
project: my-project
topic: my-topic
```

### Google Cloud Storage

Output events and detections to a GCS bucket.

> **Looking for Google Chronicle?** If you already use Google Chronicle, we make it easy to send telemetry you've collected in LimaCharlie to Chronicle. You can get that set up by creating an Output in the LimaCharlie web app.

**Parameters:**

- `secret_key`: the secret JSON key identifying a service account
- `project`: the GCP Project name where the bucket lives
- `bucket`: the GCS bucket name to upload to

### Humio

Output events and detections to the Humio.com service.

**Parameters:**

- `humio_repo`: the name of the humio repo to upload to
- `humio_api_token`: the humio ingestion token
- `endpoint_url`: optionally specify a custom endpoint URL, if you have Humio deployed on-premises

### OpenSearch

Output events and detections to OpenSearch.

**Parameters:**

- `addresses`: the IPs or DNS where to send the data to
- `index`: the index name to send data to
- `username`: user name if using username/password auth
- `password`: password if using username/password auth

### SCP

Output events and detections over SCP (SSH file transfer).

**Parameters:**

- `dest_host`: the ip:port where to send the data to, like `1.2.3.4:22`
- `dir`: the directory where to output the files on the remote host
- `username`: the SSH username to log in with
- `password`: the SSH password (if using password auth)
- `private_key`: the SSH private key (if using key-based auth)

### SFTP

Output events and detections over SFTP.

**Parameters:**

- `dest_host`: the ip:port where to send the data to, like `1.2.3.4:22`
- `dir`: the directory where to output the files on the remote host
- `username`: the username to log in with
- `password`: optional password to log in with
- `private_key`: optional SSH private key for authentication

### Slack

Output detections and audit (only) to a Slack community and channel.

**Parameters:**

- `slack_api_token`: the Slack provided API token used to authenticate
- `slack_channel`: the channel to output to within the community

**Example:**

```
slack_api_token: sample_api_token
slack_channel: #security-alerts
```

### SMTP

One option to export data from LimaCharlie is via SMTP, allowing you to send emails directly to a ticketing inbox or send high-priority detections to an on-call, shared email.

To utilize SMTP output, you will need:

- An SMTP server that utilizes STARTTLS or SSL/TLS
- Valid SMTP credentials (username and password)
- Recipient email address(es)

**Parameters:**

- `smtp_server`: the SMTP server hostname
- `smtp_port`: the SMTP server port
- `username`: SMTP authentication username
- `password`: SMTP authentication password
- `from_email`: the email address to send from
- `to_email`: the recipient email address(es)
- `use_tls`: whether to use TLS encryption

### Splunk

To send data from LimaCharlie to Splunk, you will need to configure an output.

> **Want to reduce Splunk spend?** Watch the webinar recording to learn about using LimaCharlie to reduce spending on Splunk and other high-cost security data solutions.

**Parameters:**

- `hec_token`: Splunk HTTP Event Collector (HEC) token
- `hec_url`: Splunk HEC endpoint URL
- `index`: Splunk index to send data to
- `source`: source field value
- `sourcetype`: sourcetype field value

### Syslog

Syslog (TCP) - Output events and detections to a syslog target.

**Parameters:**

- `dest_host`: the IP or DNS and port to connect to, format `www.myorg.com:514`
- `is_tls`: if true will output over TCP/TLS
- `is_strict_tls`: if true will enforce validation of TLS certs

### Tines

Output events and detections to Tines.

**Parameters:**

- `dest_host`: the Tines-provided Webhook URL

**Example:**

```
dest_host: https://something.tines.com/webhook/de2314c5f6246d17e82bf7b5742c9eaf/2d2dbcd2ab3845e9592d33c0526bc123
```

Detections or events sent to Tines can be used to trigger automated workflows and response actions.

### Webhook

Output individually each event, detection, audit, deployment or artifact through a POST webhook.

**Parameters:**

- `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`
- `secret_key`: an arbitrary shared secret that will be included in the webhook POST for authentication
- `is_strict_tls`: if true will enforce validation of TLS certs

### Webhook (Bulk)

Output batches of events, detections, audits, deployments or artifacts through a POST webhook.

**Parameters:**

- `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`
- `secret_key`: an arbitrary shared secret that will be included in the webhook POST for authentication
- `is_strict_tls`: if true will enforce validation of TLS certs
- `batch_size`: number of items to batch before sending
- `batch_timeout`: maximum time to wait before sending a partial batch