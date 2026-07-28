# Syslog

## Syslog (TCP)

Output events and detections to a syslog target.

- `dest_host`: the IP or DNS and port to connect to, format `www.myorg.com:514`.
- `is_tls`: if `true`, the output sends data over TCP/TLS.
- `is_strict_tls`: if `true`, the output validates TLS certs.
- `is_no_header`: if `true`, the output does not send a Syslog header before each message. This makes it a TCP output.
- `structured_data`: a field of your choice to include in syslog "Structured Data" headers. This field can help with integration into cloud SIEMs.

Example:

```text
dest_host: storage.corp.com
is_tls: "true"
is_strict_tls: "true"
is_no_header: "false"
```

## Related articles

- [Syslog](../../../2-sensors-deployment/adapters/types/syslog.md)

## What's Next

- [Tines](tines.md)
