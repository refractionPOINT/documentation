# Output Delivery Guarantees

Outputs are best-effort. LimaCharlie keeps no durable queue between the platform and your destination. When a destination is down or too slow, data can be lost. A record can also arrive more than once, and records can arrive out of order.

This page describes what happens when a delivery fails, how to find out, and how to set up a pipeline that reduces the risk of loss.

## Streaming and batch outputs

Outputs fall into two groups, and they fail differently.

| Group | Outputs | How records are sent |
|-------|---------|----------------------|
| Streaming | Syslog, Webhook, Kafka, Google Pub/Sub, Azure Event Hub, Slack, Microsoft Teams, Telegram, SMTP and similar | The output accepts records one at a time. Some destinations, such as Google Pub/Sub, group them for transmission. |
| Batch | Amazon S3, Google Cloud Storage, Azure Storage Blob, SFTP, SCP, BigQuery, Elastic, OpenSearch, Humio and Webhook Bulk | Records are buffered locally and uploaded together as a batch. |

## Streaming outputs

A failed send is retried up to 3 attempts in total. The wait before the second attempt is 200 ms and the wait before the third is 400 ms. Retries for one record stop once about 5 seconds have passed, even if attempts are left. A single send can take longer than that for some destinations: Azure Event Hub, for example, has its own 10-second timeout. Some destinations, such as Google Pub/Sub, report a failure only after the send has returned.

If every attempt fails, LimaCharlie drops the record and [disables the output](#after-a-failure).

### Webhook

A request times out after 2 seconds for a payload under 1 MiB, plus 1 second for each whole MiB. Only a final `2xx` response counts as delivered. Redirects are followed. Each send attempt makes up to 3 HTTP requests, and all of them share the 5-second limit above.

So a receiver can see the same record more than once. Make it idempotent and have it answer within 2 seconds.

### Syslog

Syslog outputs use TCP, optionally with TLS (`is_tls`). UDP is not supported. A record counts as delivered once LimaCharlie has written it to the connection. The protocol has no acknowledgement, so a record that the receiver never processed can still count as delivered.

### Falling behind

By default an output processes up to 100,000 records at the same time. When the destination is so slow that this limit is reached, LimaCharlie drops new records until there is room again and can log an `output cannot keep up, data dropped` error.

## Batch outputs

LimaCharlie buffers records locally and sends a batch when either of these happens first:

- `sec_per_file` seconds have passed. The default is 120 and the maximum is 3600.
- The batch holds about 10 MiB of records, measured before compression.

Each batch gets up to 50 upload attempts, 2 seconds apart. Counting the uploads themselves, that is about 100 seconds or more. An error that a retry cannot fix stops the retries earlier. After the last failed attempt, LimaCharlie discards the batch. Part of it may already have reached the destination.

The output itself is [disabled](#after-a-failure) when the next record arrives after the failed upload.

A retried upload to Amazon S3 or Google Cloud Storage reuses the same object name. Webhook Bulk can deliver the same batch more than once.

## After a failure

When an output gives up on a record or a batch, LimaCharlie disables it for a while:

- Records that arrive while the output is disabled are dropped.
- LimaCharlie retries the output at the next configuration refresh, normally within about an hour.
- Changing the output's configuration can bring it back sooner, once the change takes effect. Saving it without changes may not.

The `is_delete_on_failure` option changes this. When it is `true`, LimaCharlie tries to delete the output configuration for good on a delivery failure instead of disabling it. Records dropped because the output is falling behind do not trigger the deletion on their own. The option suits a temporary output you do not want to clean up later. The web app shows it as Delete on Failure. Do not set it on an output you depend on.

## Finding out about failures

- **Platform logs.** Errors appear in Platform Logs under Errors with the key `output/OUTPUT_NAME`. This is best-effort, and normally at most once a minute per output.
- **`output_drop` events.** LimaCharlie sends a summary event to the `deployment` stream for each output that dropped data. It is best-effort, normally about once a minute while drops continue, and can come sooner when an output stops. Outputs of the `deployment` stream and temporary live outputs produce no `output_drop` events. See [`output_drop` events](stream-structures.md#output_drop-events) for the fields.

The `count` in an `output_drop` event counts the drops LimaCharlie observed, not every record lost. A failed batch upload can show up as one drop or none, and records skipped while the output is disabled are not counted.

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

## Reducing the risk of loss

1. Send to a destination that is highly available and absorbs bursts, such as a cloud storage bucket, Google Pub/Sub or Kafka. Run any slower system behind it.
2. Alert on `output_drop` to detect delivery gaps. It does not catch every loss.
3. Keep Webhook receivers idempotent and have them answer within 2 seconds.
4. Test the output after any change. See [Testing Outputs](testing.md).

## Related

- [Output Stream Structures](stream-structures.md)
- [Testing Outputs](testing.md)
- [Output Allowlisting](allowlisting.md)
