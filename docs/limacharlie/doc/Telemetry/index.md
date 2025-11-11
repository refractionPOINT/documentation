# Telemetry

Detailed event schemas and data formats for LimaCharlie telemetry.

## Overview

This section provides comprehensive documentation of event schemas, data types, and telemetry formats used throughout the LimaCharlie platform.

## Event Schemas

Each event type has a defined schema with specific fields. Understanding these schemas is crucial for:

- Building accurate detection rules
- Parsing telemetry in SIEM platforms
- Querying data with LCQL
- Developing custom integrations

## Common Fields

All events include standard routing and metadata fields:

- `routing.sid`: Sensor ID
- `routing.oid`: Organization ID
- `routing.event_type`: Type of event
- `routing.event_time`: Timestamp (epoch milliseconds)
- `routing.tags`: Sensor tags

## Platform-Specific Schemas

Schemas vary by operating system and event type. Refer to specific event documentation for detailed field definitions.

## Resources

- View event schemas in the [web console](https://app.limacharlie.io)
- Query historical events to explore schema structure
- Use the API for programmatic schema access
