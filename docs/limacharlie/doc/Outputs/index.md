# Outputs

Stream your security telemetry to SIEM platforms, webhooks, cloud services, and more.

## Overview

Outputs allow you to forward LimaCharlie telemetry to external destinations for:

- Long-term storage and compliance
- SIEM integration and correlation
- Custom analysis pipelines
- Alerting and notification systems

## Supported Output Types

### Cloud Platforms
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage
- Kafka

### SIEM & Analytics
- Splunk
- Elasticsearch
- Humio
- Sumo Logic

### Communication & Alerting
- Slack
- Microsoft Teams
- PagerDuty
- Email

### Generic Integrations
- Webhooks (HTTP/HTTPS)
- Syslog

## Output Configuration

Outputs are configured per organization and can include filters to control which events are forwarded:

- Event type filtering
- Tag-based filtering
- Detection-only outputs
- Custom JSON transformations

## Getting Started

1. Choose your destination platform
2. Configure credentials and endpoints
3. Set up event filters (optional)
4. Test the output
5. Monitor delivery metrics

## Best Practices

- Use event filtering to reduce noise and costs
- Configure multiple outputs for redundancy
- Monitor output health and delivery rates
- Secure credentials using organization secrets
