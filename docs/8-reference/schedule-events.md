# Reference: Schedule Events

Schedule events trigger automatically at different intervals for each Organization or for each Sensor. Rules see these events through the `schedule` target.

Per-sensor and per-org scheduling events have a similar structure.

The `event` component contains one key, `frequency`. It is the frequency of this scheduling event, in seconds. The event type also contains the human readable version of the frequency.

These frequencies are emitted:

- `30m`: `30m_per_org` and `30m_per_sensor`
- `1h`: `1h_per_org` and `1h_per_sensor`
- `3h`: `3h_per_org` and `3h_per_sensor`
- `6h`: `6h_per_org` and `6h_per_sensor`
- `12h`: `12h_per_org` and `12h_per_sensor`
- `24h`: `24h_per_org` and `24h_per_sensor`
- `168h` (7 days): `168h_per_org` and `168h_per_sensor`

Scheduling events are generated for each org that meets these criteria:

- Had a minimum of 1 sensor online in the last 7 days.

Scheduling events are generated for each sensor that meets these criteria:

- Was online a minimum of one time in the last 30 days.

LimaCharlie does not keep scheduling events as part of the year retention. To use them, create D&R rules that use the `schedule` target and do the relevant `action` on a match. For example, to issue an `os_packages` one time each week on Windows hosts:

```yaml
detect:
  target: schedule
  event: 168h_per_sensor
  op: is platform
  name: windows
respond:
  - action: task
    command: os_packages
    investigation: weekly-package-list
```

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives complete control over security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

## Related articles

- [Detection on Alternate Targets](../3-detection-response/alternate-targets.md)
- [Detection and Response Examples](../3-detection-response/examples.md)
- [Reference: Platform Events](platform-events.md)
