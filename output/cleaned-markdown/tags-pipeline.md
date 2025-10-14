# Observability Pipeline

The Observability Pipeline is a feature that allows you to ingest, transform, and route observability data (logs, metrics, traces) through LimaCharlie.

## Overview

The Observability Pipeline enables you to:

- Ingest data from various sources
- Transform and enrich data in flight
- Route data to multiple destinations
- Apply filtering and sampling rules
- Normalize data formats

## Key Concepts

### Data Sources

The pipeline can accept data from multiple sources including:

- Syslog
- HTTP/HTTPS endpoints
- Cloud provider logs (AWS, Azure, GCP)
- Application logs
- Infrastructure metrics

### Transformations

Data can be transformed using:

- Field extraction and parsing
- Data enrichment
- Format conversion
- Filtering and sampling
- Aggregation

### Destinations

Processed data can be routed to:

- SIEM systems
- Log management platforms
- Data lakes
- Analytics tools
- Custom endpoints

## Configuration

Configure your pipeline through the LimaCharlie web interface or API. Define:

1. **Input sources** - where data comes from
2. **Processing rules** - how to transform data
3. **Output destinations** - where to send processed data

## Benefits

- **Cost Optimization**: Filter and sample data before sending to expensive destinations
- **Data Normalization**: Convert data to consistent formats
- **Enrichment**: Add context and metadata to raw events
- **Flexibility**: Route different data types to appropriate destinations
- **Scalability**: Handle high-volume data streams efficiently