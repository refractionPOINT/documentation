# Extensions

Extensions enhance LimaCharlie's platform capabilities across security testing, threat detection, forensics, data collection, automation, and integrations. Each extension integrates seamlessly with the core platform to provide specialized functionality.

## Security Testing & Validation

### Atomic Red Team

Execute Atomic Red Team tests to validate detection rules and security controls. This extension enables security teams to simulate adversary techniques from the MITRE ATT&CK framework and verify that detection rules trigger as expected.

[View Full Documentation](/docs/ext-atomic-red-team)

### Integrity

Monitor and validate system integrity across endpoints. The Integrity extension provides continuous monitoring of critical system files, configurations, and binaries to detect unauthorized changes.

[View Full Documentation](/docs/ext-integrity)

## Threat Detection & Analysis

### YARA

Deploy and manage YARA rules for malware detection and threat hunting. The YARA extension enables real-time scanning of files, memory, and processes using custom or community YARA signatures.

[View Full Documentation](/docs/ext-yara)

### YARA Manager

Centralized management interface for YARA rules across your organization. YARA Manager simplifies rule deployment, versioning, and distribution to sensors at scale.

[View Full Documentation](/docs/ext-yara-manager)

### VirusTotal Integration

Integrate VirusTotal threat intelligence for file and URL analysis. This integration automatically enriches file hashes and URLs with VirusTotal reputation data and detection results.

[View Full Documentation](/docs/tutorials-integratons-virustotal-integration)

## Forensics & Incident Response

### Velociraptor

Deploy Velociraptor for endpoint visibility and forensic investigations. This extension brings Velociraptor's powerful artifact collection and query capabilities into the LimaCharlie platform.

[View Full Documentation](/docs/ext-velociraptor)

### Velociraptor to BigQuery

Stream Velociraptor artifacts directly to BigQuery for analysis. This extension enables long-term storage and large-scale analysis of Velociraptor collections using BigQuery's analytics capabilities.

[View Full Documentation](/docs/velociraptor-to-bigquery)

### Plaso

Process and analyze timeline data using the Plaso framework. The Plaso extension automates super timeline creation from disk images and file systems for forensic investigations.

[View Full Documentation](/docs/ext-plaso)

### Hayabusa

Fast Windows Event Log forensics with Hayabusa integration. Hayabusa provides rapid threat hunting and detection in Windows Event Logs using high-speed Sigma rule processing.

[View Full Documentation](/docs/ext-hayabusa)

### Zeek

Network security monitoring using Zeek (formerly Bro). This extension processes network traffic to generate detailed protocol logs and detect suspicious network activity.

[View Full Documentation](/docs/ext-zeek)

### Artifact

Collect and analyze forensic artifacts from endpoints. The Artifact extension provides pre-built and custom artifact collection capabilities for incident response and investigations.

[View Full Documentation](/docs/ext-artifact)

## Data Collection & Management

### Exfil (Event Collection)

Configure event exfiltration and collection workflows. The Exfil extension manages how events are collected, filtered, and forwarded to external systems or storage locations.

[View Full Documentation](/docs/ext-exfil)

### Lookup Manager

Manage threat intelligence lookups and enrichment data. Lookup Manager maintains watchlists, IOC feeds, and reference data for real-time event enrichment.

[View Full Documentation](/docs/ext-lookup-manager)

### BinLib

Binary library management for detection engineering. BinLib provides a repository of known-good and known-bad binaries to improve detection accuracy and reduce false positives.

[View Full Documentation](/docs/binlib)

## Automation & Operations

### Reliable Tasking

Ensure reliable task execution across distributed sensors. Reliable Tasking guarantees that commands reach sensors even when they're temporarily offline, with automatic retry and confirmation.

[View Full Documentation](/docs/ext-reliable-tasking)

### Sensor Cull

Automatically manage inactive or obsolete sensors. Sensor Cull identifies and removes sensors that haven't reported in, helping maintain a clean sensor inventory.

[View Full Documentation](/docs/ext-sensor-cull)

### Infrastructure

Manage infrastructure resources and configurations. The Infrastructure extension provides centralized management of cloud resources, network configurations, and deployment automation.

[View Full Documentation](/docs/ext-infrastructure)

## Integrations

### Twilio

SMS and voice notification integration via Twilio. This extension enables alert delivery through SMS messages and voice calls for critical security events.

[View Full Documentation](/docs/ext-twilio)

### Govee

IoT device integration for physical security indicators. The Govee extension controls smart lights and devices to provide visual indicators of security events and system status.

[View Full Documentation](/docs/ext-govee)

## Development

### Building the User Interface

Guidelines for building custom UI extensions. This documentation covers the framework, APIs, and best practices for developing custom user interface components and dashboards.

[View Full Documentation](/docs/building-the-user-interface)

---

## Extension Architecture

Extensions integrate with LimaCharlie through:
- **Detection & Response (D&R) Rules**: Trigger extension actions based on event patterns
- **REST APIs**: Programmatic access to extension functionality
- **Webhooks**: Receive notifications and data from external services
- **Custom Outputs**: Stream data to external systems and storage

## Getting Started

Most extensions can be deployed directly from the LimaCharlie Add-ons marketplace:

1. Navigate to Add-ons in the web interface
2. Browse available extensions
3. Click "Subscribe" on the desired extension
4. Configure extension-specific settings
5. Deploy to target sensors or organization-wide

For development and custom extensions, refer to the [Building the User Interface](/docs/building-the-user-interface) documentation.

---

**Note:** This documentation covers v2 of the extensions API. For legacy v1 documentation, see [v1 Deprecated](/v1/docs/tags/extensions).