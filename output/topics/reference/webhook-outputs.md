# Webhook Output Destinations

LimaCharlie supports two webhook output destination types: individual event webhooks and bulk batch webhooks. Both send data via HTTP(S) POST requests with optional authentication and signature verification.

## Webhook (Individual Events)

Output individually each event, detection, audit, deployment or artifact through a POST webhook.

### Configuration Parameters

* `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`.
* `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the webhook to verify authenticity. [See "Webhook Details" section.](https://doc.limacharlie.io/docs/documentation/ZG9jOjE5MzExMTY-outputs#webhook-details)
* `auth_header_name` and `auth_header_value`: set a specific value to a specific HTTP header name in the outgoing webhooks.

### Examples

#### Basic Webhook Configuration

```yaml
dest_host: https://webhooks.corp.com/new_detection
secret_key: this-is-my-secret-shared-key
auth_header_name: x-my-special-auth
auth_header_value: 4756345846583498
```

#### Google Chat Webhook

Example [hook to Google Chat](https://developers.google.com/chat/how-tos/webhooks):

```yaml
dest_host: https://chat.googleapis.com/v1/spaces/AAAA4-AAAB/messages?key=afsdfgfdgfE6vySjMm-dfdssss&token=pBh2oZWr7NTSj9jisenfijsnvfisnvijnfsdivndfgyOYQ%3D
secret_key: gchat-hook-sig42
custom_transform: |
   {
      "text": "Detection {{ .cat }} on {{ .routing.hostname }}: {{ .link }}"
   }
```

## Webhook (Bulk)

Output batches of events, detections, audits, deployments or artifacts through a POST webhook.

### Configuration Parameters

* `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`.
* `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the webhook to verify authenticity. This is a required field. [See "Webhook Details" section.](https://doc.limacharlie.io/docs/documentation/ZG9jOjE5MzExMTY-outputs#webhook-details)
* `auth_header_name` and `auth_header_value`: set a specific value to a specific HTTP header name in the outgoing webhooks.
* `sec_per_file`: the number of seconds after which a file is cut and uploaded.
* `is_no_sharding`: do not add a shard directory at the root of the files generated.

### Example

```yaml
dest_host: https://webhooks.corp.com/new_detection
secret_key: this-is-my-secret-shared-key
auth_header_name: x-my-special-auth
auth_header_value: 4756345846583498
```

## Choosing Between Webhook Types

- **Individual Webhook**: Use when you need real-time, per-event delivery to external systems. Each event triggers a separate HTTP POST request immediately.
- **Bulk Webhook**: Use when you need to send batched data at intervals. Events are accumulated and sent together based on the `sec_per_file` parameter, reducing the number of HTTP requests and improving efficiency for high-volume scenarios.

Both webhook types support the same authentication mechanisms (shared secret HMAC signatures and custom HTTP headers) and use the same `dest_host` format for specifying the target endpoint.