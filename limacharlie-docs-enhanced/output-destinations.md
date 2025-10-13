[## Amazon S3

Output events and detections to an Amazon S3 bucket. If you have your own visualization stack, or you just need the data archived, you can output directly to Amazon S3. This way you don't need any infrastructure. bucket : the path to the AWS S3...](/docs/outputs-destinations-amazon-s3)

Updated on : 07 Oct 2025

[## Apache Kafka

Output events and detections to a Kafka target. dest\_host : the IP or DNS and port to connect to, format kafka.myorg.com . is\_tls : if true will output over TCP/TLS. is\_strict\_tls : if true will enforce validation of TLS certs. ...](/docs/outputs-destinations-apache-kafka)

Updated on : 05 Oct 2024

[## Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka). connection\_string : the connection string provided by Azure. Note that the connection string should end with ;EntityPath=your-hub-name which is sometimes miss...](/docs/outputs-destinations-azure-event-hub)

Updated on : 05 Oct 2024

[## Azure Storage Blob

Output events and detections to a Blob Container in Azure Storage Blobs. secret\_key : the secret access key for the Blob Container. blob\_container : the name of the Blob Container to upload to. account\_name : the account name used to aut...](/docs/outputs-destinations-azure-storage-blob)

Updated on : 05 Oct 2024

[## Elastic

Output events and detections to Elastic . addresses : the IPs or DNS where to send the data to. index : the index name to send data to. username : user name if using username/password auth. (use either username/password -or- API key) ...](/docs/outputs-destinations-elastic)

Updated on : 05 Oct 2024

[## Google Cloud BigQuery

Output events and detections to a Google Cloud BigQuery Table. For a practical use case of this output, see this tutorial on pushing Velociraptor data to BigQuery . schema : describes the column names, data types, and other information; should...](/docs/outputs-destinations-google-cloud-bigquery)

Updated on : 10 Dec 2024

[## Google Cloud Pubsub

Output events and detections to a Pubsub topic. secret\_key : the secret json key identifying a service account. project : the GCP Project name where the Topic lives. topic : use this specific value as a topic. Example: project: my-p...](/docs/outputs-destinations-google-cloud-pubsub)

Updated on : 05 Oct 2024

[## Google Cloud Storage

Output events and detections to a GCS bucket. Looking for Google Chronicle? If you already use Google Chronicle, we make it easy to send telemetry you've collected in LimaCharlie to Chronicle. You can get that set up by creating an Output in ...](/docs/outputs-destinations-google-cloud-storage)

Updated on : 05 Oct 2024

[## Humio

Output events and detections to the Humio.com service. humio\_repo : the name of the humio repo to upload to. humio\_api\_token : the humio ingestion token. endpoint\_url : optionally specify a custom endpoint URL, if you have Humio deploy...](/docs/outputs-destinations-humio)

Updated on : 05 Oct 2024

[## OpenSearch

Output events and detections to OpenSearch . addresses : the IPs or DNS where to send the data to index : the index name to send data to username : user name if using username/password auth password : password if using username/pass...](/docs/outputs-destinations-opensearch)

Updated on : 05 Oct 2024

[## SCP

Output events and detections over SCP (SSH file transfer). dest\_host : the ip:port where to send the data to, like 1.2.3.4:22 . dir : the directory where to output the files on the remote host. username : the SSH username to log in with...](/docs/outputs-destinations-scp)

Updated on : 05 Oct 2024

[## SFTP

Output events and detections over SFTP. dest\_host : the ip:port where to send the data to, like 1.2.3.4:22 . dir : the directory where to output the files on the remote host. username : the username to log in with. password : option...](/docs/outputs-destinations-sftp)

Updated on : 05 Oct 2024

[## Slack

Output detections and audit (only) to a Slack community and channel. slack\_api\_token : the Slack provided API token used to authenticate. slack\_channel : the channel to output to within the community. Example: slack\_api\_token: sample\_ap...](/docs/outputs-destinations-slack)

Updated on : 05 Oct 2024

[## SMTP

One option to export data from LimaCharlie is via SMTP, allowing you to send emails directly to a ticketing inbox or send high-priority detections to an on-call, shared email. To utilize SMTP output, you will need: An SMTP server that utilizes S...](/docs/outputs-destinations-smtp)

Updated on : 08 Oct 2025

[## Splunk

To send data from LimaCharlie to Splunk, you will need to configure an output. Want to reduce Splunk spend? Watch the webinar recording to learn about using LimaCharlie to reduce spending on Splunk and other high-cost security data solution...](/docs/outputs-destinations-splunk)

Updated on : 08 Oct 2025

[## Syslog

Syslog (TCP) Output events and detections to a syslog target. dest\_host : the IP or DNS and port to connect to, format www.myorg.com:514 . is\_tls : if true will output over TCP/TLS. is\_strict\_tls : if true will enforce validation o...](/docs/outputs-destinations-syslog)

Updated on : 05 Oct 2024

[## Tines

Output events and detections to Tines . dest\_host : the Tines-provided Webhook URL Example: dest\_host: https://something.tines.com/webhook/de2314c5f6246d17e82bf7b5742c9eaf/2d2dbcd2ab3845e9592d33c0526bc123 Detections or events sent to ...](/docs/output-destinations-tines)

Updated on : 05 Oct 2024

[## Webhook

Output individually each event, detection, audit, deployment or artifact through a POST webhook. dest\_host : the IP or DNS, port and page to HTTP(S) POST to, format https://www.myorg.com:514/whatever . secret\_key : an arbitrary shared secre...](/docs/outputs-destinations-webhook)

Updated on : 05 Oct 2024

[## Webhook (Bulk)

Output batches of events, detections, audits, deployments or artifacts through a POST webhook. dest\_host : the IP or DNS, port and page to HTTP(S) POST to, format https://www.myorg.com:514/whatever . secret\_key : an arbitrary shared secret ...](/docs/outputs-destinations-webhook-bulk)

Updated on : 05 Oct 2024
