# Observability Pipeline

The Observability Pipeline in LimaCharlie allows you to process, transform, and route telemetry data in real-time. This powerful feature enables you to normalize data from multiple sources, enrich events, filter noise, and send processed data to various destinations.

## Overview

The pipeline operates on streaming telemetry data before it's stored or forwarded. You can chain multiple processing steps to transform data as it flows through the system.

## Key Capabilities

- **Data Transformation**: Modify event structure, add/remove fields, normalize formats
- **Enrichment**: Add context from external sources or internal lookups
- **Filtering**: Drop unwanted events or sample high-volume data
- **Routing**: Send specific events to different outputs based on conditions
- **Aggregation**: Combine multiple events into summaries
- **Parsing**: Extract structured data from unstructured logs

## Pipeline Components

### Processors

Processors are the building blocks of your pipeline. Each processor performs a specific transformation:

- **Filter**: Include/exclude events based on criteria
- **Parse**: Extract fields using regex, JSON parsing, or other methods
- **Enrich**: Add fields from lookups or external APIs
- **Transform**: Modify field values or event structure
- **Aggregate**: Combine events over time windows
- **Sample**: Reduce event volume by sampling

### Outputs

Define where processed events should be sent:

- LimaCharlie storage
- External SIEMs
- Data lakes
- Custom webhooks
- Other cloud services

## Configuration

Pipelines are configured using YAML or through the web interface. Example pipeline configuration:

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

## Best Practices

1. **Start Simple**: Begin with basic filtering and gradually add complexity
2. **Test Thoroughly**: Use pipeline testing tools before deploying to production
3. **Monitor Performance**: Watch for pipeline latency and processing errors
4. **Document Logic**: Comment complex transformations for maintainability
5. **Handle Errors**: Include error handling for parsing and enrichment failures

## Performance Considerations

- Keep pipelines efficient to avoid latency
- Use sampling for high-volume event types
- Cache enrichment lookups when possible
- Monitor pipeline metrics and alerts

## Related Documentation

- Output destinations and integrations
- Detection & Response rules
- Artifact collection
- Data retention policies