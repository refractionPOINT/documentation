# Amazon S3

Output events and detections to an Amazon S3 bucket.

If you have your own visualization stack, or if you only need an archive of the data, output directly to Amazon S3. You then do not need your own infrastructure.

- `bucket`: the path to the AWS S3 bucket.
- `key_id`:  the id of the AWS auth key.
- `secret_key`: the AWS secret key to auth with.
- `sec_per_file`: the number of seconds after which a file is cut and uploaded (default 120, maximum 3600).
- `is_compression`: if set to "true", LimaCharlie gzips the data before upload.
- `is_indexing`: if set to "true", files are written under a time-based directory structure (`year/month/day/hour/`) instead of flat files with random names. See [File organization](#file-organization) below.
- `region_name`: the region name of the bucket. Set this parameter, although it is not always needed.
- `endpoint_url`: an optional custom endpoint URL. Use it with region\_name to output to third-party services that are compatible with S3.
- `dir`: the directory prefix
- `is_no_sharding`: do not add a shard directory at the root of the files generated.

Example:

```text
bucket: my-bucket-name
key_id: AKIAABCDEHPUXHHHHSSQ
secret_key: fonsjifnidn8anf4fh74y3yr34gf3hrhgh8er
is_indexing: "true"
is_no_sharding: "true"
is_compression: "true"
```

![aws](../../../assets/images/aws.png)

## File Organization

By default, LimaCharlie uploads each batch of data as a flat file with a random (UUID) name. The file goes to the root of the bucket, or under `dir` if you set it. File names have no order. Use this mode for pipelines that list and consume all new objects without regard to the name.

To organize files by date and time, set `is_indexing` to `"true"`. Files are then written under a time-based directory structure:

```text
[dir/][shard/]year/month/day/hour/d{stream-id}_{counter}[.gz]
```

For example: `logs/1/2026/7/7/13/d1b2c3d4-e5f6-7890-abcd-ef1234567890_12.gz`

- The timestamp components are in **UTC**. They show when LimaCharlie uploaded the batch.
- Data files begin with a `d` prefix.
- `shard` is a single hexadecimal character that spreads the write load across key prefixes. To make paths start at the year, set `is_no_sharding` to `"true"`.
- Directory components have no zero padding (July is `7`, not `07`). A lexical sort of object keys is therefore not chronological. If the order is important, parse the path components as numbers.
- The `sec_per_file` parameter controls how often LimaCharlie creates a new file.

If you enable the `is_compression` flag, LimaCharlie compresses each file as a GZIP at upload and adds a `.gz` extension. LimaCharlie recommends that you enable `is_compression`.

## AWS IAM Configuration

1. Log in to AWS console and go to the IAM service.
2. Click on `Users` from the menu.
3. Click `Create User`, give it a name, and click `Next`.
4. Click `Next`, then `Create User`
5. Click on the user you just created and click on the `Security Credentials` tab
6. Click `Create access key`
7. Select `Other` and click `Next`
8. Give a description (optional) and click `Create access key`
9. Take note of the "Access key", "Secret access key" and ARN name for the user (starts with "arn:", shown on the user summary screen).

## AWS S3 Configuration

1. Go to the S3 service.
2. Click `Create bucket`, enter a name and select a region.
3. Click `Create bucket`
4. Click on your newly created bucket and click on the `Permissions` tab
5. Select `Bucket policy` and click `Edit`
6. Enter the policy from the [Policy Sample](#policy-sample) section. Replace `<<USER_ARN>>` with the ARN name of the user that you created. Replace `<<BUCKET_NAME>>` with the name of the bucket that you created.
7. Click `Save Changes`

### Policy Sample

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Sid": "PermissionForObjectOperations",
         "Effect": "Allow",
         "Principal": {
            "AWS": "<<USER_ARN>>"
         },
         "Action": "s3:PutObject",
         "Resource": "arn:aws:s3:::<<BUCKET_NAME>>/*"
      }
   ]
}
```

## LimaCharlie Configuration

1. In the LimaCharlie web app, in your organization view, click `Outputs` and then `Add Output`
2. Select the stream that you want to send (events, detections, etc)
3. Select the `Amazon S3` destination
4. Give the output a name. Enter the bucket name, key\_id, and secret\_key that you noted from AWS. Enter any other parameters that you want to configure
5. Click `Save Output`
6. After about a minute, LimaCharlie starts to write the data to your bucket

## Related articles

- [AWS CloudTrail](../../../2-sensors-deployment/adapters/types/aws-cloudtrail.md)
- [S3](../../../2-sensors-deployment/adapters/types/s3.md)
- [AWS](../../extensions/cloud-cli/aws.md)
- [AWS GuardDuty](../../../2-sensors-deployment/adapters/types/aws-guardduty.md)

## What's Next

- [Apache Kafka](apache-kafka.md)
