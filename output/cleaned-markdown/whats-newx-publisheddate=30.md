# Release Notes

## October 2025

### Extension: Yara

**New behavior added**
- Added ability to manage Yara signatures from the Extension management page

### Ingestion

**New behavior added**
- Added ability to specify a `batch_size` payload for the REST, GCS, and S3 Adapters.

### Platform

**New behavior added**
- Log message stating rate limiting is enabled now only shows up when rate limiting is happening.

### Sensor

**New sensor release: 5.46.0**
- Improved parsing and cleanup of macOS `es_file_t` structures to reduce memory usage.
- Added support for Windows 11 24H2 DnsQuery telemetry.
- Limited event types sent from macOS sensors are now properly set.
- Starting with this version, you will need to manually enable the "limited event type" function through the sensor_config.

## September 2025

### Sigma Rules

**New behavior added**
- Sigma Rules now support user-provided configuration yamls to configure Sigma pipelines

### Extension: VirusTotal

**New behavior added**
- All lookups now have the ability to ingest in the "VT" stream for retention

### Soteria Rules

**New rules deployed:**
- `rules-soteria/windows/ransomware/bitlocker_encryption_detected.yaml`
- `rules-soteria/windows/ransomware/windows_shadow_copy_delete.yaml`
- `rules-soteria/windows/persistence/windows_firewall_rule.yaml`

### Extension: Artifact Collection

**Bug fix**
- Fixed an issue preventing the use of compiled Velociraptor artifacts in artifact collection

### Extension: Chronicler

**Bug fix**
- Fixed an issue where Chronicler was sending incomplete Replicant artifact results

## August 2025

### Platform

**New behavior added**
- New `get_tags` function added to Detection & Response rules to help retrieve tags from the Insight Service

### Extension: Net Inspect

**Bug fix**
- Fixed an issue preventing HTTPS traffic inspection when using a custom certificate

### Sensor

**New sensor release: 5.45.0**
- Enhanced macOS ES client authorization check
- Windows process tracking bug fixes
- Improved sensor disconnection handling
- Added support for Google Cloud Storage (GCS) payloads
- Add optional parameters to SERVICE_CHANGE event
- Fix Registry value caching
- Improved performance when using `deny_tree` functionality
- Fixed issue where DNS lookups were not correctly parsed on newer Windows versions

## July 2025

### Extension: Artifact Collection

**New behavior added**
- Can now run multiple artifact collections in parallel with scheduling support
- Artifact Collection results now available in the Replicant section of sensor pages

### Platform

**New behavior added**
- New organizations now default to sensor version 5.44.0
- Improved REST Adapter error messages

### Sensor

**New sensor release: 5.44.0**
- Add Linux eBPF support (preview)
- Enhanced memory usage tracking
- Added ability to list loaded kernel modules (Linux)
- macOS file event improvements
- Added ability to set sensor group through installation key

## June 2025

### Extension: Managed Detection and Response (MDR)

**New behavior added**
- Reduced false positive rate with improved detection logic
- Added automated response actions for high-severity threats

### Platform

**New behavior added**
- New API endpoints for managing detection rules
- Added support for webhooks in automated responses
- Improved search performance in historical data

### Extension: Cloud Sensors (AWS, GCP, Azure)

**New behavior added**
- Added support for Azure VM metadata ingestion
- GCP Cloud Function logs now automatically ingested
- AWS CloudTrail improvements for S3 and IAM events

## May 2025

### Soteria Rules

**New rules deployed:**
- `rules-soteria/linux/privilege_escalation/sudo_privilege_escalation.yaml`
- `rules-soteria/cloud/aws/aws_iam_policy_changed.yaml`
- `rules-soteria/cloud/gcp/gcp_service_account_key_created.yaml`

### Platform

**New behavior added**
- Added ability to export detection alerts to CSV
- Improved timeline visualization in Investigation view
- New keyboard shortcuts for common actions

### Sensor

**New sensor release: 5.43.0**
- Reduced CPU usage during high-volume event periods
- Added support for monitoring Docker containers (Linux)
- Improved network connection tracking accuracy
- Fixed issue with process tree reconstruction on macOS

## April 2025

### Extension: Replay

**New behavior added**
- Added ability to replay historical events through D&R rules for testing
- Support for replay speed control (1x, 2x, 5x, 10x)

### Platform

**Bug fix**
- Fixed issue where large timeline queries could timeout
- Corrected organization quota calculations

### Extension: Integrity

**New behavior added**
- Added support for monitoring Windows registry keys
- Integrity checks can now be scheduled at custom intervals

## March 2025

### Platform

**New behavior added**
- New Insight Service tags available: `malicious_ip`, `tor_exit_node`, `known_miner`
- Added ability to create custom dashboards
- Organization settings now support 2FA enforcement

### Extension: VirusTotal Livehunt

**New behavior added**
- Livehunt rules now support Yara modules
- Added notification options for Livehunt matches

### Sensor

**New sensor release: 5.42.0**
- Added Chrome extension monitoring capability
- Improved file integrity monitoring performance
- Fixed issue with DNS event collection on Ubuntu 24.04
- Added support for detecting RunDLL32 process injection

## February 2025

### Soteria Rules

**New rules deployed:**
- `rules-soteria/windows/credential_access/lsass_memory_dump.yaml`
- `rules-soteria/linux/execution/suspicious_cron_job.yaml`
- `rules-soteria/macos/persistence/launch_agent_creation.yaml`

### Platform

**New behavior added**
- Added bulk sensor management capabilities
- Improved API rate limiting with more granular controls
- New retention policies for Artifact Collection results

### Extension: Carbon Black

**New behavior added**
- Added support for Carbon Black Cloud Enterprise EDR
- Automatic alert synchronization with LimaCharlie detections

## January 2025

### Platform

**New behavior added**
- New Data Residency options: EU-Central, Asia-Pacific
- Added support for custom SSL certificates in Adapters
- Improved error messages across all API endpoints

### Sensor

**New sensor release: 5.41.0**
- Added Apple Silicon native support (M1/M2/M3)
- Improved Windows kernel driver stability
- Added support for monitoring Kubernetes pods
- Fixed issue with network event deduplication

### Extension: SIEM Adapters

**New behavior added**
- Added native Splunk HEC adapter
- Google Chronicle adapter now supports custom parsers
- Improved performance for high-volume log forwarding