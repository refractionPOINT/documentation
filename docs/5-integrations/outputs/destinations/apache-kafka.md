# Apache Kafka

Output events and detections to a Kafka target.

- `dest_host`: the IP or DNS and port to connect to, format `kafka.myorg.com`.
- `is_tls`: if `true`, the output uses TCP/TLS.
- `is_strict_tls`: if `true`, the output validates TLS certs.
- `username`: if you set this with `password`, LimaCharlie uses Basic authentication.
- `password`: if you set this with `username`, LimaCharlie uses Basic authentication.
- `routing_topic`: use the element with this name from the `routing` of the event as the Kafka topic name.
- `literal_topic`: use this specific value as a topic.

**Note on authentication:** if you set `username` and `password`, LimaCharlie assumes the authentication mechanism SASL_SSL + SCRAM-SHA-512. This mechanism can work with services such as [AWS Manages Streaming Kafka](https://aws.amazon.com/msk/). If you need different authentication parameters, contact [support@limacharlie.io](mailto:support@limacharlie.io).

Example:

```text
dest_host: kafka.corp.com
is_tls: "true"
is_strict_tls: "true"
username: lc
password: letmein
literal_topic: telemetry
```
