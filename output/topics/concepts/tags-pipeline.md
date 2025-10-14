Looking at these two documents, they are both about the **same topic** - the Observability Pipeline in LimaCharlie. They cover overlapping concepts but with different levels of detail. I'll merge them into a single, comprehensive document that preserves all technical details and code examples.

```markdown
# Observability Pipeline

The Observability Pipeline in LimaCharlie allows you to ingest, process, transform, and route observability data (logs, metrics, traces, and telemetry) in real-time through the platform.

## Overview

The Observability Pipeline operates on streaming telemetry data before it's stored or forwarded, enabling you to chain multiple processing steps to transform data as it flows through the system. This powerful feature allows you to normalize data from multiple sources, enrich events, filter noise, and send processed data to various destinations.

## Key Capabilities

- **Data Transformation**: Modify event structure, add/remove fields, normalize formats, and convert data to consistent formats
- **Enrichment**: Add context from external sources, internal lookups, or metadata to raw events
- **Filtering**: Drop unwanted events or sample high-volume data
- **Routing**: Send specific events to different outputs based on conditions
- **Aggregation**: Combine multiple events into summaries or aggregate over time windows
- **Parsing**: Extract structured data from unstructured logs using regex, JSON parsing, or other methods

## Pipeline Components

### Data Sources

The pipeline can accept data from multiple sources including:

- Syslog
- HTTP/HTTPS endpoints
- Cloud provider logs (AWS, Azure, GCP)
- Application logs
- Infrastructure metrics
- LimaCharlie sensors and agents

### Processors

Processors are the building blocks of your pipeline. Each processor performs a specific transformation:

- **Filter**: Include/exclude events based on criteria
- **Parse**: Extract fields using regex, JSON parsing, or other methods
- **Enrich**: Add fields from lookups or external APIs
- **Transform**: Modify field values or event structure
- **Aggregate**: Combine events over time windows
- **Sample**: Reduce event volume by sampling

### Destinations (Outputs)

Define where processed events should be sent. Processed data can be routed to:

- LimaCharlie storage
- SIEM systems (Splunk, Sentinel, etc.)
- Log management platforms
- Data lakes
- Analytics tools
- Custom webhooks
- Other cloud services
- Custom endpoints

## Configuration

Pipelines are configured using YAML or through the LimaCharlie web interface or API. Define:

1. **Input sources** - where data comes from
2. **Processing rules** - how to transform data (processors)
3. **Output destinations** - where to send processed data

### Example Pipeline Configuration

```yaml
pipeline:
  - processor: filter
    config:
      include:
        event_type: NETWORK_CONNECTIONS
  
  - processor: parse
    config:
      field: event.COMMAND_LINE
      pattern: '(?P<command>\w+)\s+(?P<args>.*)'
  
  - processor: enrich
    config:
      lookup: threat_intel
      field: event.IP_ADDRESS
      output_field: threat_info
  
  - processor: output
    config:
      destination: splunk
      format: cef
```

## Benefits

- **Cost Optimization**: Filter and sample data before sending to expensive destinations
- **Data Normalization**: Convert data to consistent formats across multiple sources
- **Enrichment**: Add context and metadata to raw events
- **Flexibility**: Route different data types to appropriate destinations based on conditions
- **Scalability**: Handle high-volume data streams efficiently
- **Real-time Processing**: Transform and route data as it flows through the system

## Best Practices

1. **Start Simple**: Begin with basic filtering and gradually add complexity
2. **Test Thoroughly**: Use pipeline testing tools before deploying to production
3. **Monitor Performance**: Watch for pipeline latency and processing errors
4. **Document Logic**: Comment complex transformations for maintainability
5. **Handle Errors**: Include error handling for parsing and enrichment failures

## Performance Considerations

- Keep pipelines efficient to avoid latency in data processing
- Use sampling for high-volume event types to reduce processing load
- Cache enrichment lookups when possible to improve performance
- Monitor pipeline metrics and alerts to identify bottlenecks
- Consider the cost and performance impact of each processing step

## Related Documentation

- Output destinations and integrations
- Detection & Response rules
- Artifact collection
- Data retention policies
```