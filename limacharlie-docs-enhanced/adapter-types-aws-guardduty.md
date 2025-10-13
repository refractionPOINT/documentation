## Overview

This Adapter allows you to ingest AWS GuardDuty events via either an [S3 bucket](https://aws.amazon.com/s3/) or [SQS message queue](https://aws.amazon.com/sqs/).

[AWS GuardDuty](https://aws.amazon.com/guardduty/) helps you protect your AWS accounts with intelligent threat detection.

Telemetry Platform: `guard_duty`

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

#### Collecting AWS GuardDuty Logs via an S3 Bucket

If collecting GuardDuty logs via an S3 bucket, you will need the following parameters:

* `bucket_name` - The name of the S3 bucket holding the data)
* `secret_key` - The API key for AWS that has access to the respective bucket.
* `access_key` - The AWS access key for the API key

The following command will create an Adapter using the (1) Adapter binary and (2) logs stored in an S3 bucket:

```
./lc_adapter s3 client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=guard_duty \
bucket_name=lc-ct-test \
access_key=YYYYYYYYYY \
secret_key=XXXXXXXX \
client_options.hostname=guardduty-logs
```

#### Collecting AWS GuardDuty Logs via an SQS Queue

If collecting GuardDuty logs via an SQS queue, you will need the following parameters:

* `secret_key` - The API key for AWS that has access to the respective bucket.
* `access_key` - The AWS access key for the API key
* `region` - The AWS region where the SQS instance lives
* `queue_url` - The URL to the SQS instance

The following command will create an Adapter using the (1) Adapter binary and (2) logs stored in an SQS queue:

```
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

Within the LimaCharlie web application, you can create an AWS GuardDuty Cloud Connector using the `+ Add Sensor` option.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(304).png)

[AWS CloudTrail](https://docs.aws.amazon.com/cloudtrail/) logs allow you to monitor AWS deployments. CloudTrail logs can provide granular visibility into AWS instances and can be used within [D&R rules](/v2/docs/detection-and-response) to identify AWS abuse.

This adapter allows you to ingest AWS CloudTrail events via either an [S3 bucket](https://aws.amazon.com/s3/) or [SQS message queue](https://aws.amazon.com/sqs/).

CloudTrail events can be addressed in LimaCharlie as the `aws` platform.

## Adapter Deployment

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

### Adapter-specific Options

CloudTrail logs can be collected via a cloud-to-cloud Adapter, or via the CLI Adapter. Furthermore, within each option, there is a choice of collecting logs from an S3 bucket or an SQS message queue.

## Cloud-to-Cloud Adapter

Within the LimaCharlie web application, you can create an AWS CloudTrail Cloud Connector using the `+ Add Sensor` option.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(306).png)

After providing an Installation Key, you will be guided through connecting either an S3 bucket or SQS queue to ingest AWS CloudTrail events.

#### Collecting AWS CloudTrail Logs via an S3 Bucket

If collecting CloudTrail logs via an S3 bucket, you will need the following parameters:

* `bucket_name` - The name of the S3 bucket holding the data)
* `secret_key` - The API key for AWS that has access to the respective bucket.
* `access_key` - The AWS access key for the API key

The following sample configuration can be used to create an S3 CLI Adapter for AWS CloudTrail events:

```
s3:
  client_options:
    hostname: aws-cloudtrail-logs
    identity:
      installation_key: <INSTALLATION_KEY>
      oid: <OID>
    platform: aws
    sensor_seed_key: super-special-seed-key
  bucket_name: <S3_BUCKET_NAME>
  secret_key: <S3_SECRET_KEY>
  access_key: <S3_ACCESS_KEY>
```

#### Collecting AWS CloudTrail Logs via an SQS Queue

If collecting CloudTrail logs via an SQS queue, you will need the following parameters:

* `secret_key` - The API key for AWS that has access to the respective bucket.
* `access_key` - The AWS access key for the API key
* `region` - The AWS region where the SQS instance lives
* `queue_url` - The URL to the SQS instance

The following sample configuration can be used to create an SQS CLI Adapter for AWS CloudTrail events:

```
sqs:
  client_options:
    hostname: aws-cloudtrail-logs
    identity:
      installation_key: <INSTALLATION_KEY>
      oid: <OID>
    platform: aws
    sensor_seed_key: super-special-seed-key
  region: <SQS_REGION>
  secret_key: <SQS_SECRET_KEY>
  access_key: <SQS_ACCESS_KEY>
  queue_url: <SQS_QUEUE_URL>
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Amazon Web Services

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
