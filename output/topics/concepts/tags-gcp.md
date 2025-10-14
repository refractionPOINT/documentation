# LimaCharlie GCP Integration

LimaCharlie provides comprehensive integration with Google Cloud Platform (GCP) services, enabling bidirectional data flow for security monitoring, analysis, and compliance. This documentation covers data ingestion from GCP services, data export to GCP destinations, and specialized analytics pipelines.

## Data Ingestion from GCP

### Google Cloud Platform Logs

Ingest logs from Google Cloud Platform services into LimaCharlie for centralized monitoring and detection.

**Tutorial: Ingesting Google Cloud Logs**
- Step-by-step guide to configure GCP log ingestion
- Covers authentication and service account setup
- Integration with Cloud Logging
- Real-time log streaming configuration

[Read more: Tutorial: Ingesting Google Cloud Logs](/docs/en/tutorial-ingesting-google-cloud-logs)

### Google Workspace

Monitor security events and user activity across Google Workspace applications including Gmail, Drive, Calendar, Admin console, and more.

**Capabilities:**
- User activity monitoring
- Security event detection
- Compliance and audit logging
- Integration with Google Workspace Alert Center

[Read more: Google Workspace](/docs/en/adapter-types-google-workspace)

### Google Cloud Pub/Sub Adapter

Receive data from Google Cloud Pub/Sub topics into LimaCharlie for processing and analysis.

**Configuration:**
- Subscribe to Pub/Sub topics
- Authenticate using service accounts
- Handle message formats and schemas
- Configure message acknowledgment

[Read more: Google Cloud Pubsub Adapter](/docs/en/adapter-types-google-cloud-pubsub)

### Google Cloud Storage Adapter

Ingest data from Google Cloud Storage buckets into LimaCharlie.

**Features:**
- Monitor buckets for new objects
- Process batch uploads
- Support for multiple file formats
- Automated data parsing and normalization

[Read more: Google Cloud Storage Adapter](/docs/en/adapter-types-google-cloud-storage)

## Data Export to GCP

### Google Cloud BigQuery

Send LimaCharlie telemetry, detection data, and security events to BigQuery for SQL-based analysis and long-term storage.

**Use Cases:**
- Security data lake creation
- Historical analysis and trending
- Compliance reporting
- Integration with BI tools

**Configuration:**
- Dataset and table management
- Schema customization
- Streaming vs. batch ingestion
- Authentication and permissions

[Read more: Google Cloud BigQuery Output](/docs/en/outputs-destinations-google-cloud-bigquery)

### Google Cloud Storage

Archive LimaCharlie data to Google Cloud Storage buckets for long-term retention and compliance.

**Features:**
- Configurable retention policies
- Multiple storage classes (Standard, Nearline, Coldline, Archive)
- Compressed output formats
- Partitioning strategies

[Read more: Google Cloud Storage Output](/docs/en/outputs-destinations-google-cloud-storage)

### Google Cloud Pub/Sub

Stream real-time data from LimaCharlie to Pub/Sub topics for event-driven architectures and downstream processing.

**Capabilities:**
- Real-time event streaming
- Topic-based routing
- Integration with Cloud Functions, Dataflow, and other GCP services
- Message ordering and delivery guarantees

[Read more: Google Cloud Pubsub Output](/docs/en/outputs-destinations-google-cloud-pubsub)

## Specialized Analytics Pipelines

### Velociraptor to BigQuery

Stream Velociraptor endpoint telemetry and hunt results to BigQuery for centralized analysis.

**Pipeline Components:**
- Velociraptor server integration
- Data transformation and normalization
- BigQuery schema mapping
- Query optimization for security analytics

**Benefits:**
- Centralized endpoint data repository
- Cross-organizational hunting
- Long-term telemetry retention
- Integration with threat intelligence

[Read more: Velociraptor to BigQuery](/docs/en/velociraptor-to-bigquery)

### Hayabusa to BigQuery

Pipeline Hayabusa Windows event log analysis results to BigQuery for threat hunting and incident response.

**Workflow:**
- Hayabusa EVTX parsing and analysis
- Detection rule matching
- BigQuery data loading
- Timeline analysis in SQL

**Use Cases:**
- Windows threat hunting at scale
- EVTX analysis automation
- Detection engineering
- Incident investigation and forensics

[Read more: Hayabusa to BigQuery](/docs/en/hayabusa-to-bigquery)

### Building Reports with BigQuery + Looker Studio

Create comprehensive security reports and interactive dashboards using BigQuery as the data source and Google Looker Studio for visualization.

**Capabilities:**
- Custom security dashboards
- Automated reporting workflows
- KPI and metrics tracking
- Executive and technical reporting

**Topics Covered:**
- BigQuery data preparation
- Looker Studio connector configuration
- Dashboard design best practices
- Scheduled report delivery

[Read more: Building Reports with BigQuery + Looker Studio](/docs/en/tutorials-reporting-building-reports-with-bigquery-looker-studio)

## CLI Extensions

### Google Cloud CLI Extension

Extend the LimaCharlie CLI with Google Cloud-specific commands and integrations.

**Features:**
- GCP service management from LimaCharlie CLI
- Automated configuration deployment
- Integration testing and validation
- Scripting and automation support

[Read more: Google Cloud CLI Extension](/docs/en/ext-cloud-cli-google-cloud)

## Related Documentation

- [LimaCharlie Outputs Overview](/docs/en/outputs)
- [Adapter Configuration](/docs/en/adapters)
- [Data Retention and Compliance](/docs/en/retention)
- [Query Language and Analytics](/docs/en/query-language)