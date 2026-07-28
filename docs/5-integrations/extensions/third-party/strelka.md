# Strelka

## Strelka Extension Pricing

Use of ext-strelka also uses Artifact Exporting, at a rate of $0.02/GB for the processed artifacts. It also causes webhook data to arrive in LimaCharlie. These related costs are added to the specific price of ext-strelka.

[Strelka](https://github.com/target/strelka) is a real-time file scanning system used for threat hunting, threat detection, and incident response.

The Strelka extension receives files as Artifacts. Give an `artifact_id` in the `run_on` request. The extension then processes the file and returns the results to the caller. It also sends the results to its related Sensor.

## Configuration

Example rule that processes all Artifacts ingested with the type `zeek-extract`:

**Detect:**

```yaml
event: ingest
op: is
path: routing/log_type
target: artifact_event
value: zeek-extract
```

**Respond:**

```yaml
- action: extension request
  extension action: run_on
  extension name: ext-strelka
  extension request:
    artifact_id: '{{ .routing.log_id }}'
```

## Usage

If you use the LimaCharlie [Zeek](zeek.md) extension, you can start a Zeek analysis when LimaCharlie ingests a PCAP artifact. The analysis generates the Zeek artifacts that trigger the Strelka extension in the example above.

**Detect:**

```yaml
op: exists
event: ingest
artifact type: pcap
path: /
target: artifact_event
```

**Respond:**

```yaml
- action: extension request
  extension action: run_on
  extension name: ext-zeek
  extension request:
    artifact_id: '{{ .routing.log_id }}'
    retention: 30
```
