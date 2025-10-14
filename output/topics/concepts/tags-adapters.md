# Adapter

The adapter service is a core component of LimaCharlie that allows you to ingest data from various external sources and transform it into telemetry that can be processed by the platform. Adapters act as data connectors that can pull from or listen to different services, normalize the data, and forward it to your LimaCharlie organization.

## Overview

Adapters provide a flexible way to integrate third-party services, cloud platforms, and custom data sources into LimaCharlie. Each adapter type is designed to handle specific data sources and protocols, making it easy to centralize security telemetry from across your infrastructure.

## Supported Adapter Types

LimaCharlie supports a wide variety of adapter types for different data sources:

### Cloud & Infrastructure
- **AWS S3** - Ingest data from S3 buckets
- **AWS SQS** - Consume messages from SQS queues
- **Google Cloud Storage** - Pull data from GCS buckets
- **Google Cloud Pub/Sub** - Subscribe to Pub/Sub topics

### Email & Communication
- **IMAP** - Monitor email accounts via IMAP
- **Mimecast** - Ingest Mimecast email security logs
- **Sublime Security** - Integrate Sublime email detection platform

### Identity & Access Management
- **Okta** - Collect Okta system logs and events
- **1Password** - Monitor 1Password events
- **Microsoft 365** - Ingest M365 audit logs

### Security Tools
- **Microsoft Defender** - Collect Defender alerts and events
- **Sophos** - Ingest Sophos endpoint and firewall logs
- **PandaDoc** - Monitor document activity

### IT Management
- **IT Glue** - Sync IT documentation and asset data

### Generic Ingestion
- **File** - Monitor and ingest from file sources
- **Syslog** - Receive syslog messages
- **Stdin** - Ingest data from standard input
- **Stdin JSON** - Ingest JSON-formatted data from standard input
- **EVTX** - Parse Windows Event Log files

## Key Concepts

### Data Transformation
Adapters normalize data from various sources into LimaCharlie's standardized telemetry format, making it easier to write detection rules and perform analysis across different data sources.

### Flexible Deployment
Adapters can run in different environments:
- Cloud-hosted by LimaCharlie
- Self-hosted on your infrastructure
- As containerized services

### Configuration
Each adapter type has its own configuration schema that defines:
- Authentication credentials
- Data source location
- Transformation rules
- Output destinations
- Filtering and sampling options

## Getting Started

To start using adapters:

1. Choose the appropriate adapter type for your data source
2. Configure the adapter with necessary credentials and settings
3. Deploy the adapter (cloud or self-hosted)
4. Verify data is flowing into your LimaCharlie organization

## Related Documentation

- [Adapter Usage](/docs/en/adapter-usage) - How to configure and deploy adapters
- Individual adapter type documentation (see links above for specific adapters)