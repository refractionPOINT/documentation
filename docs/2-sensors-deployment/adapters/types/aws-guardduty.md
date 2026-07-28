# AWS GuardDuty

## Overview

This adapter ingests AWS GuardDuty events from an [S3 bucket](https://aws.amazon.com/s3/) or from an [SQS message queue](https://aws.amazon.com/sqs/).

[AWS GuardDuty](https://aws.amazon.com/guardduty/) helps you protect your AWS accounts with intelligent threat detection.

Telemetry Platform: `guard_duty`

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter uses.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

#### Collecting AWS GuardDuty Logs via an S3 Bucket

To collect GuardDuty logs from an S3 bucket, you need these parameters:

- `bucket_name` - The name of the S3 bucket holding the data)
- `secret_key` - The API key for AWS that has access to the respective bucket.
- `access_key` - The AWS access key for the API key

This command creates an adapter that uses the adapter binary and reads logs from an S3 bucket:

```bash
./lc_adapter s3 client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=guard_duty \
bucket_name=lc-ct-test \
access_key=YYYYYYYYYY \
secret_key=XXXXXXXX \
client_options.hostname=guardduty-logs
```

#### Collecting AWS GuardDuty Logs via an SQS Queue

To collect GuardDuty logs from an SQS queue, you need these parameters:

- `secret_key` - The API key for AWS that has access to the respective bucket.
- `access_key` - The AWS access key for the API key
- `region` - The AWS region that contains the SQS instance
- `queue_url` - The URL to the SQS instance

This command creates an adapter that uses the adapter binary and reads logs from an SQS queue:

```bash
./lc_adapter sqs client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=guard_duty \
client_options.sensor_seed_key=<SENSOR_SEED_KEY> \
client_options.hostname=guardduty-logs \
access_key=YYYYYYYYYY \
secret_key=XXXXXXXX \
queue_url=<QUEUE_URL> \
region=<AWS-REGION>
```

## Guided Deployment

In the LimaCharlie web app, create an AWS GuardDuty cloud connector with the `+ Add Sensor` option.

![Add Sensor option for AWS GuardDuty Cloud Connector in the LimaCharlie web application](../../../assets/images/image(304).png)
