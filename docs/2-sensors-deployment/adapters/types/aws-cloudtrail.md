# AWS CloudTrail

[AWS CloudTrail](https://docs.aws.amazon.com/cloudtrail/) logs let you monitor AWS deployments. CloudTrail logs give detailed visibility into AWS instances. You can use them in D&R rules to find abuse of AWS.

This adapter ingests AWS CloudTrail events from an [S3 bucket](https://aws.amazon.com/s3/) or from an [SQS message queue](https://aws.amazon.com/sqs/).

You address CloudTrail events in LimaCharlie with the `aws` platform.

## Adapter Deployment

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter uses.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

### Adapter-specific Options

A cloud-to-cloud adapter or a CLI adapter collects CloudTrail logs. With each option, you can collect the logs from an S3 bucket or from an SQS message queue.

## Cloud-to-Cloud Adapter

In the LimaCharlie web app, create an AWS CloudTrail cloud connector with the `+ Add Sensor` option.

![image.png](../../../assets/images/image(160).png)

After you give an Installation Key, the web app guides you to connect an S3 bucket or an SQS queue that ingests AWS CloudTrail events.

### Collecting AWS CloudTrail Logs via an S3 Bucket

To collect CloudTrail logs from an S3 bucket, you need these parameters:

- `bucket_name` - The name of the S3 bucket holding the data)
- `secret_key` - The API key for AWS that has access to the respective bucket.
- `access_key` - The AWS access key for the API key

This sample configuration creates an S3 CLI adapter for AWS CloudTrail events:

```yaml
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

To collect CloudTrail logs from an SQS queue, you need these parameters:

- `secret_key` - The API key for AWS that has access to the respective bucket.
- `access_key` - The AWS access key for the API key
- `region` - The AWS region that contains the SQS instance
- `queue_url` - The URL to the SQS instance

This sample configuration creates an SQS CLI adapter for AWS CloudTrail events:

```yaml
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
