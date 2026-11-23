# Output Delivery Guarantees

Outputs are best-effort. LimaCharlie keeps no durable queue between the platform and your destination. When a destination is down or too slow, data can be lost. A record can also arrive more than once, and records can arrive out of order.

This page describes what happens when a delivery fails, how to find out, and how to build a pipeline that loses as little as possible.

## Streaming and batch outputs

Outputs fall into two groups, and they fail differently.

| Group | Outputs | How records are sent |
|-------|---------|----------------------|
| Streaming | Syslog, Webhook, Kafka, Google Pub/Sub, Azure Event Hub, Slack, Microsoft Teams, Telegram, SMTP and similar | One record at a time, as it arrives |
| Batch | Amazon S3, Google Cloud Storage, Azure Storage Blob, SFTP, SCP, BigQuery, Elastic, OpenSearch, Humio and Webhook Bulk | Records pile up in a local file that is uploaded as a whole |

## Streaming outputs

Each record gets up to 3 attempts, and the whole delivery of one record has a hard limit of about 5 seconds. The wait before the second attempt is 200 ms and the wait before the third is 400 ms. When the 5 seconds run out, LimaCharlie stops retrying even if attempts are left. If every attempt fails, LimaCharlie drops the record and [disables the output](#after-a-failure).

### Webhook

Each request times out after 2 seconds, and any response outside the 2xx range counts as a failure. Inside each attempt, LimaCharlie retries a failed request up to 3 times. The 5-second limit above still applies to all of it, so a record whose receiver keeps timing out gets at most two or three requests before it is dropped. A slow receiver can still see the same record more than once, so make the receiver idempotent and keep it fast. A receiver that needs more than 2 seconds to answer is treated as down.

### Syslog

Syslog outputs use TCP, optionally with TLS (`is_tls`). UDP is not supported. A record counts as delivered once LimaCharlie has written it to the connection. The protocol has no acknowledgement, so a record that the receiver never processed can still count as delivered.

### Falling behind

Each output holds up to 100,000 records in flight. When a destination is so slow that the limit is reached, LimaCharlie drops new records until there is room again and logs an `output cannot keep up` error.

## Batch outputs

LimaCharlie buffers records locally and cuts a file when either of these happens first:

- `sec_per_file` seconds have passed. The default is 120 and the maximum is 3600.
- The file reaches about 10 MB.

Each file is uploaded with up to 50 attempts, 2 seconds apart, which is about 100 seconds in total. If the last attempt fails, LimaCharlie discards the whole file and [disables the output](#after-a-failure).

A retried upload to Amazon S3 or Google Cloud Storage rewrites the same object name, so it does not leave a duplicate. A retried Webhook Bulk upload can deliver the same batch twice.

## After a failure

When an output gives up on a record or a file, LimaCharlie disables it for a while:

- Records that arrive while the output is disabled are dropped.
- The output comes back on its own within about an hour.
- Editing the output's configuration brings it back immediately. Any change works, including saving it unchanged.

The `is_delete_on_failure` option changes this. When it is `true`, a failure deletes the output configuration for good instead of disabling it. It suits a temporary output you do not want to clean up later. The web app shows it as Delete on Failure. Do not set it on an output you depend on.

## Finding out about failures

- **Platform logs.** Each failure is logged in Platform Logs under Errors with the key `output/OUTPUT_NAME`, at most once a minute per output.
- **`output_drop` events.** LimaCharlie sends a summary event to the `deployment` stream for each output that dropped data, about once a minute. See [`output_drop` events](stream-structures.md#output_drop-events) for the fields.

The `count` in an `output_drop` event is a lower bound. A failed batch counts as one drop however many records it held, and records skipped while the output is disabled are not counted.

You can alert on these events with a [D&R rule on the `deployment` target](../../3-detection-response/alternate-targets.md#target-deployment):

```yaml
detect:
  target: deployment
  event: output_drop
  op: is
  path: routing/event_type
  value: output_drop

respond:
  - action: report
    name: output-dropping-data
    priority: 3
```

If the rule gets noisy, add a [suppression](../../8-reference/response-actions.md#suppression) to the action.

## Building a reliable pipeline

If you need every record:

1. Send to a destination that is highly available and absorbs bursts, such as a cloud storage bucket, Google Pub/Sub or Kafka. Run any slower system behind it.
2. Alert on `output_drop` so you notice a gap.
3. Keep Webhook receivers under 2 seconds and idempotent.
4. Test the output after any change. See [Testing Outputs](testing.md).

## Related

- [Output Stream Structures](stream-structures.md)
- [Testing Outputs](testing.md)
- [Output Allowlisting](allowlisting.md)
