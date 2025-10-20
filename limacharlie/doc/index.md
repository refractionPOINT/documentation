# LimaCharlie Documentation Index

**For AI Agents**: This index is designed to help you quickly navigate LimaCharlie documentation based on user queries and tasks. Use the topic-based organization below to find relevant documentation.

---

## Quick Start & Overview

**Use when**: User wants to understand what LimaCharlie is or get started quickly.

- [What is LimaCharlie?](Getting_Started/what-is-limacharlie.md) - Platform overview and value proposition
- [Core Concepts](Getting_Started/limacharlie-core-concepts.md) - Fundamental concepts: sensors, adapters, installation keys, tags, D&R rules, Insight, outputs, API keys
- [Quickstart Guide](Getting_Started/quickstart.md) - Step-by-step guide: create org, deploy sensor, add Sigma rules, configure outputs

### Use Cases
- [Endpoint Detection and Response (EDR)](Getting_Started/Use_Cases/endpoint-detection-and-response-edr.md)
- [Cost-Effective SIEM](Getting_Started/Use_Cases/cost-effective-siem.md)
- [Cloud Security](Getting_Started/Use_Cases/cloud-security.md)
- [Building Products](Getting_Started/Use_Cases/building-products.md)
- [Build CTI Capabilities](Getting_Started/Use_Cases/build-cti-capabilities.md)
- [ChromeOS Support](Getting_Started/Use_Cases/chromeos-support.md)
- [Enterprises](Getting_Started/Use_Cases/enerprises.md)

---

## Sensors & Telemetry Collection

**Use when**: User needs to deploy sensors, collect telemetry, or ingest data.

### Endpoint Agent (EDR Sensor)
- [Installation Keys](Sensors/installation-keys.md) - Creating and managing installation keys
- [Sensor Tags](Sensors/sensor-tags.md) - Tagging sensors for organization and targeting
- [Sensor Connectivity](Sensors/sensor-connectivity.md) - Network requirements and connectivity

#### Installation & Deployment
- **Endpoint Agent Installation**: `Sensors/Endpoint_Agent/Endpoint_Agent_Installation/`
- **Enterprise Deployment**: `Telemetry/Sensors/Enterprise_Sensor_Deployment/`
  - [Chrome Enterprise](Telemetry/Sensors/Enterprise_Sensor_Deployment/chrome-enterprise.md)
- **Windows Specific**:
  - [Building Custom MSI Installer](Telemetry/Sensors/Operating_Systems/Windows/building-a-custom-msi-installer-for-windows.md)

#### Endpoint Agent Commands
- **Command Reference**: `Sensors/Endpoint_Agent/Endpoint_Agent_Commands/`
- **Sensor Commands**: `Telemetry/Sensors/Sensor_Commands/`

### Adapters (Log & Telemetry Ingestion)
**Use when**: User needs to ingest logs from cloud services, applications, or other sources.

#### Adapter Types & Examples
- **Adapter Types Directory**: `Sensors/Adapters/Adapter_Types/`
  - [1Password](Sensors/Adapters/Adapter_Types/1password.md)
  - **Azure**: `Sensors/Adapters/Adapter_Types/Azure_Logs/` (Azure Monitor, Key Vault, AKS)
  - **AWS**, **Google Cloud**, **Office 365**, and many more

#### Adapter Tutorials
- [Creating a Webhook Adapter](Sensors/Adapters/Adapter_Tutorials/tutorial-creating-a-webhook-adapter.md)
- [Ingesting Google Cloud Logs](Sensors/Adapters/Adapter_Tutorials/tutorial-ingesting-google-cloud-logs.md)
- [Ingesting from Cloud-Based External Sources](Sensors/Adapters/Adapter_Tutorials/tutorial-ingesting-telemetry-from-cloud-based-external-sources.md)

#### Adapter Examples
- [STDIN Adapter](Sensors/Adapters/Adapter_Examples/adapter-examples-stdin.md)
- [STDIN JSON Adapter](Sensors/Adapters/Adapter_Examples/adapter-examples-stdin-json.md)
- [Windows Event Logs](Sensors/Adapters/Adapter_Examples/adapter-examples-windows-event-logs.md)

#### Adapter Deployment
- **Deployment Guide**: `Telemetry/Adapters/Adapter_Deployment/`

### Reference
- [Sensor Selector Expressions](Telemetry/Sensors/Reference/reference-sensor-selector-expressions.md) - Targeting specific sensors

---

## Detection & Response (D&R)

**Use when**: User wants to create detection rules, automate responses, or use managed rulesets.

### Core Concepts & Guides
- [Writing and Testing Rules](Detection_and_Response/writing-and-testing-rules.md) - Comprehensive guide to creating D&R rules
- [Detection and Response Examples](Detection_and_Response/detection-and-response-examples.md) - Real-world examples
- [Detection Logic Operators](Detection_and_Response/Reference/detection-logic-operators.md) - Reference for rule logic
- [Response Actions](Detection_and_Response/Reference/response-actions.md) - Available automated responses

### Advanced Detection Features
- [Stateful Rules](Detection_and_Response/stateful-rules.md) - Rules that maintain state across events
- [False Positive Rules](Detection_and_Response/false-positive-rules.md) - Managing false positives
- [Detection on Alternate Targets](Detection_and_Response/detection-on-alternate-targets.md) - Beyond endpoint events
- [Unit Tests](Detection_and_Response/unit-tests.md) - Testing D&R rules
- [Replay](Detection_and_Response/replay.md) - Replaying events for testing

### Managed Rulesets
**Use when**: User wants pre-built detection rules.

- [Community Rules](Detection_and_Response/Managed_Rulesets/community-rules.md) - Open-source community rules
- [SOC Prime Rules](Detection_and_Response/Managed_Rulesets/soc-prime-rules.md) - SOC Prime threat detection content
- **Sigma Rules**: `Detection_and_Response/Managed_Rulesets/Sigma_Rules/`
  - [Sigma Converter](Detection_and_Response/Managed_Rulesets/Sigma_Rules/sigma-converter.md)
- **Soteria Rules**: `Detection_and_Response/Managed_Rulesets/Soteria_Rules/`
  - [Soteria EDR Rules](Detection_and_Response/Managed_Rulesets/Soteria_Rules/soteria-edr-rules.md)
  - [Soteria AWS Rules](Detection_and_Response/Managed_Rulesets/Soteria_Rules/soteria-aws-rules.md)
  - [Soteria M365 Rules](Detection_and_Response/Managed_Rulesets/Soteria_Rules/soteria-m365-rules.md)

### Tutorials
- [Writing and Testing Rules Tutorial](Detection_and_Response/Tutorials/writing-and-testing-rules.md)
- [Create D&R Rule Using Threat Feed](Detection_and_Response/Tutorials/create-a-dr-rule-using-a-threat-feed.md)

### Reference
- [Error Codes](Detection_and_Response/Reference/reference-error-codes.md)

---

## Events & Event Data

**Use when**: User needs to understand event structures, schemas, or event types.

### Event Documentation
- [Event Schemas](Events/event-schemas.md) - Dynamic schema API and event structure
- [Template Strings and Transforms](Events/template-strings-and-transforms.md) - Manipulating event data

### Endpoint Agent Events (EDR)
- [EDR Events Reference](Events/Endpoint_Agent_Events_Overview/reference-edr-events.md) - Complete list of endpoint events
- [Sysmon Comparison](Events/Endpoint_Agent_Events_Overview/sysmon-comparison.md) - Mapping to Sysmon events
- [Error Codes](Events/Endpoint_Agent_Events_Overview/reference-error-codes.md)

### Platform Events
- [Platform Events Overview](Events/Platform_Events_Overview/reference-platform-events.md) - Platform-level events
- [Schedule Events](Events/Platform_Events_Overview/reference-schedule-events.md) - Scheduled/cron events

---

## Query & Analysis

**Use when**: User wants to query data, search events, or analyze telemetry.

### LimaCharlie Query Language (LCQL)
- [LCQL Examples](Query_Console/lcql-examples.md) - Query language examples
- [Query Console UI](Query_Console/query-console-ui.md) - Using the web interface
- [Query with CLI](Query_Console/query-with-cli.md) - Command-line querying

---

## Outputs & Data Export

**Use when**: User wants to forward data to external systems (SIEM, storage, etc.).

### Output Configuration
- [Output Allowlisting](Outputs/output-allowlisting.md) - Filtering output data
- [Output Billing](Outputs/output-billing.md) - Cost implications
- [Testing Outputs](Outputs/testing-outputs.md) - Validating output configurations

### Output Destinations
**Directory**: `Outputs/Destinations/` and `Outputs/Output_Destinations/`

Popular destinations:
- [Amazon S3](Outputs/Destinations/outputs-destinations-amazon-s3.md)
- [Google Cloud BigQuery](Outputs/Destinations/outputs-destinations-google-cloud-bigquery.md)
- [Google Cloud Pub/Sub](Outputs/Destinations/outputs-destinations-google-cloud-pubsub.md)
- [Google Cloud Storage](Outputs/Destinations/outputs-destinations-google-cloud-storage.md)
- [Azure Event Hub](Outputs/Destinations/outputs-destinations-azure-event-hub.md)
- [Azure Storage Blob](Outputs/Destinations/outputs-destinations-azure-storage-blob.md)
- [Elastic](Outputs/Destinations/outputs-destinations-elastic.md)
- [OpenSearch](Outputs/Destinations/outputs-destinations-opensearch.md)
- [Apache Kafka](Outputs/Destinations/outputs-destinations-apache-kafka.md)
- [Tines](Outputs/Destinations/output-destinations-tines.md)

---

## Add-Ons & Extensions

**Use when**: User wants to extend platform functionality or integrate with third-party tools.

### Using Extensions
- [Using Extensions](Add-Ons/Extensions/using-extensions.md) - How to install and use extensions

### Building Extensions
- [Building Extensions Guide](Add-Ons/Extensions/Building/building-extensions.md)
- [Building the User Interface](Add-Ons/Extensions/Building/building-the-user-interface.md)
- [Schema Data Types](Add-Ons/Extensions/Building/schema-data-types.md)

### LimaCharlie Official Extensions
**Directory**: `Add-Ons/Extensions/LimaCharlie_Extensions/`

- [LimaCharlie CLI](Add-Ons/Extensions/LimaCharlie_Extensions/limacharlie-cli.md)
- [YARA Manager](Add-Ons/Extensions/LimaCharlie_Extensions/ext-yara-manager.md)
- [Payload Manager](Add-Ons/Extensions/LimaCharlie_Extensions/payload-manager.md)
- [Git Sync](Add-Ons/Extensions/LimaCharlie_Extensions/ext-git-sync.md)
- [Reliable Tasking](Add-Ons/Extensions/LimaCharlie_Extensions/ext-reliable-tasking.md)
- [Infrastructure](Add-Ons/Extensions/LimaCharlie_Extensions/ext-infrastructure.md)
- [Usage Alerts](Add-Ons/Extensions/LimaCharlie_Extensions/ext-usage-alerts.md)
- [Exfil Detection](Add-Ons/Extensions/LimaCharlie_Extensions/ext-exfil.md)
- [Integrity Monitoring](Add-Ons/Extensions/LimaCharlie_Extensions/ext-integrity.md)
- [EPP (Endpoint Protection)](Add-Ons/Extensions/LimaCharlie_Extensions/ext-epp.md)
- [Artifact Collection](Add-Ons/Extensions/LimaCharlie_Extensions/ext-artifact.md)
- [Dumper](Add-Ons/Extensions/LimaCharlie_Extensions/ext-dumper.md)
- [Sensor Cull](Add-Ons/Extensions/LimaCharlie_Extensions/ext-sensor-cull.md)
- [Lookup Manager](Add-Ons/Extensions/LimaCharlie_Extensions/ext-lookup-manager.md)
- [Binary Library (binlib)](Add-Ons/Extensions/LimaCharlie_Extensions/binlib.md)

### LimaCharlie Labs (Experimental)
- [Playbook](Add-Ons/Extensions/LimaCharlie_Labs/playbook.md)
- [AI Agent Engine](Add-Ons/Extensions/LimaCharlie_Labs/ai-agent-engine.md)

### Third-Party Extensions
**Directory**: `Add-Ons/Extensions/Third-Party_Extensions/`

Popular integrations:
- [Velociraptor](Add-Ons/Extensions/Third-Party_Extensions/ext-velociraptor.md)
- [YARA](Add-Ons/Extensions/Third-Party_Extensions/ext-yara.md)
- [Zeek](Add-Ons/Extensions/Third-Party_Extensions/ext-zeek.md)
- [Strelka](Add-Ons/Extensions/Third-Party_Extensions/ext-strelka.md)
- [Hayabusa](Add-Ons/Extensions/Third-Party_Extensions/ext-hayabusa.md)
- [Plaso](Add-Ons/Extensions/Third-Party_Extensions/ext-plaso.md)
- [Atomic Red Team](Add-Ons/Extensions/Third-Party_Extensions/ext-atomic-red-team.md)
- [OTX (AlienVault)](Add-Ons/Extensions/Third-Party_Extensions/ext-otx.md)
- [PagerDuty](Add-Ons/Extensions/Third-Party_Extensions/ext-pagerduty.md)
- [Twilio](Add-Ons/Extensions/Third-Party_Extensions/ext-twilio.md)
- [NIMS](Add-Ons/Extensions/Third-Party_Extensions/ext-nims.md)
- [Renigma](Add-Ons/Extensions/Third-Party_Extensions/ext-renigma.md)
- [SecureAnnex](Add-Ons/Extensions/Third-Party_Extensions/ext-secureannex.md)
- [Govee](Add-Ons/Extensions/Third-Party_Extensions/ext-govee.md)

### Cloud CLI Extensions
**Directory**: `Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/`

- [AWS](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-aws.md)
- [Azure](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-azure.md)
- [Google Cloud](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-google-cloud.md)
- [Microsoft 365](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-microsoft365.md)
- [Okta](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-okta.md)
- [GitHub](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-github.md)
- [Tailscale](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-tailscale.md)
- [1Password](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-1password.md)
- [DigitalOcean](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-digitalocean.md)
- [Vultr](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-vultr.md)
- [SDM (StrongDM)](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-sdm.md)
- [Sublime](Add-Ons/Extensions/Third-Party_Extensions/Cloud_CLI/ext-cloud-cli-sublime.md)

### Extension Tutorials
- [Velociraptor to BigQuery](Add-Ons/Extensions/Tutorials/velociraptor-to-bigquery.md)
- [Hayabusa to BigQuery](Add-Ons/Extensions/Tutorials/hayabusa-to-bigquery.md)

### API Integrations
**Directory**: `Add-Ons/API_Integrations/`

- [VirusTotal](Add-Ons/API_Integrations/api-integrations-virustotal.md)
- [GreyNoise](Add-Ons/API_Integrations/api-integrations-greynoise.md)
- [AlphaMountain](Add-Ons/API_Integrations/api-integrations-alphamountain.md)
- [EchoTrail](Add-Ons/API_Integrations/api-integrations-echotrail.md)
- [Pangea](Add-Ons/API_Integrations/api-integrations-pangea.md)
- [Hybrid Analysis](Add-Ons/API_Integrations/api-integrations-hybrid-analysis.md)
- [IP Geolocation](Add-Ons/API_Integrations/api-integrations-ip-geolocation.md)

### Services
- [Replay Service](Add-Ons/Services/replay.md)
- [Dumper Service](Add-Ons/Services/addons-services-dumper.md)

### Developer Resources
- [Developer Grant Program](Add-Ons/developer-grant-program.md)

### Reference
- [Authentication Resource Locator](Add-Ons/Reference/reference-authentication-resource-locator.md)

---

## Platform Management

**Use when**: User needs to manage organizations, users, access control, billing, or configuration.

### Access & Permissions
- [User Access](Platform_Management/Access_and_Permissions/user-access.md)
- [API Keys](Platform_Management/Access_and_Permissions/api-keys.md)
- [Single Sign-On (SSO)](Platform_Management/Access_and_Permissions/single-sign-on.md)
- [Permissions Reference](Platform_Management/Access_and_Permissions/reference-permissions.md)

### Billing
- [Billing Options](Platform_Management/Billing/billing-options.md)
- [Using Custom Billing Plans](Platform_Management/Billing/using-custom-billing-plans.md)

### Configuration Hive
- [Config Hive for Cloud Sensors](Platform_Management/Config_Hive/config-hive-cloud-sensors.md)
- [Config Hive for D&R Rules](Platform_Management/Config_Hive/config-hive-dr-rules.md)
- [Config Hive for Lookups](Platform_Management/Config_Hive/config-hive-lookups.md)

### SDK & Automation
- [LimaCharlie SDK](Platform_Management/limacharlie-sdk.md)

---

## API Reference

**Use when**: User needs to interact with LimaCharlie programmatically via REST API.

**Full API Documentation**: `LimaCharlie.io_REST_API/`

### Key API Sections
- **API Keys**: `LimaCharlie.io_REST_API/API_Keys/`
- **Sensors**: `LimaCharlie.io_REST_API/Sensors/`
- **Organizations**: `LimaCharlie.io_REST_API/Organizations/`
- **Rules (D&R)**: `LimaCharlie.io_REST_API/Rules/`
- **Outputs**: `LimaCharlie.io_REST_API/Outputs/`
- **Extensions**: `LimaCharlie.io_REST_API/Extension/`, `Extension-Request/`, `Extension-Schema/`, `Extension-Subscription/`
- **Artifacts**: `LimaCharlie.io_REST_API/Artifacts/`
- **False Positives**: `LimaCharlie.io_REST_API/False_Positives/`
- **Hive**: `LimaCharlie.io_REST_API/Hive/`
- **Installation Keys**: `LimaCharlie.io_REST_API/Installation_Keys/`
- **Jobs**: `LimaCharlie.io_REST_API/Jobs/`
- **Modules**: `LimaCharlie.io_REST_API/Modules/`
- **Payload**: `LimaCharlie.io_REST_API/Payload/`
- **Resources**: `LimaCharlie.io_REST_API/Resources/`
- **Retention**: `LimaCharlie.io_REST_API/Retention/`
- **Schema**: `LimaCharlie.io_REST_API/Schema/`
- **Service**: `LimaCharlie.io_REST_API/Service/`
- **Tags**: `LimaCharlie.io_REST_API/Tags/`
- **Users**: `LimaCharlie.io_REST_API/Users/`
- **Billing**: `LimaCharlie.io_REST_API/Billing/`
- **Groups**: `LimaCharlie.io_REST_API/Groups/`
- **Errors**: `LimaCharlie.io_REST_API/Errors/`
- **General**: `LimaCharlie.io_REST_API/General/`
- **Model-Request**: `LimaCharlie.io_REST_API/Model-Request/`

---

## Connecting to LimaCharlie

**Use when**: User wants to integrate LimaCharlie with AI tools or development environments.

- [MCP Server](Connecting/mcp-server.md) - Model Context Protocol server for AI integration

---

## FAQ & Troubleshooting

**Use when**: User encounters issues or has common questions.

### General FAQ
- [General FAQ](FAQ/faq-general.md)
- [Privacy FAQ](FAQ/faq-privacy.md)
- [Account Management FAQ](FAQ/faq-account-management.md)

### Technical FAQ
- [Sensor Installation FAQ](FAQ/faq-sensor-installation.md)
- [Sensor Removal](FAQ/sensor-removal.md)
- [Troubleshooting FAQ](FAQ/faq-troubleshooting.md)

### Billing FAQ
- [Billing FAQ](FAQ/faq-billing.md)
- [Invoices FAQ](FAQ/faq-invoices.md)

---

## Tutorials

**Use when**: User wants step-by-step guidance on specific tasks.

### Detection & Response Tutorials
**Directory**: `Getting_Started/Tutorials/Detection_&_Response/`

### Extension Tutorials
**Directory**: `Getting_Started/Tutorials/Extensions/`

### Integration Tutorials
**Directory**: `Getting_Started/Tutorials/Integrations/`
- [VirusTotal Integration](Getting_Started/Tutorials/Integrations/tutorials-integratons-virustotal-integration.md)

### Reporting Tutorials
**Directory**: `Getting_Started/Tutorials/Reporting/`
- [Building Reports with BigQuery & Looker Studio](Getting_Started/Tutorials/Reporting/tutorials-reporting-building-reports-with-bigquery-looker-studio.md)

### Sensor Management Tutorials
**Directory**: `Getting_Started/Tutorials/Sensor_Management/`

### Telemetry Tutorials
**Directory**: `Getting_Started/Tutorials/Telemetry/`
- [Ingesting macOS Unified Logs](Getting_Started/Tutorials/Telemetry/ingesting-macos-unified-logs.md)

---

## Common Query Patterns for AI Agents

### "How do I deploy a sensor?"
→ [Quickstart: Deploying a Sensor](Getting_Started/quickstart.md#deploying-a-sensor)
→ [Installation Keys](Sensors/installation-keys.md)
→ `Sensors/Endpoint_Agent/Endpoint_Agent_Installation/`

### "How do I ingest logs from [cloud service]?"
→ [Adapter Types](Sensors/Adapters/Adapter_Types/)
→ [Creating a Webhook Adapter](Sensors/Adapters/Adapter_Tutorials/tutorial-creating-a-webhook-adapter.md)

### "How do I create detection rules?"
→ [Writing and Testing Rules](Detection_and_Response/writing-and-testing-rules.md)
→ [Detection Logic Operators](Detection_and_Response/Reference/detection-logic-operators.md)
→ [Response Actions](Detection_and_Response/Reference/response-actions.md)

### "How do I export data to [destination]?"
→ [Outputs Documentation](Outputs/)
→ [Output Destinations](Outputs/Destinations/)

### "What events does the sensor collect?"
→ [EDR Events Reference](Events/Endpoint_Agent_Events_Overview/reference-edr-events.md)
→ [Event Schemas](Events/event-schemas.md)

### "How do I query my data?"
→ [LCQL Examples](Query_Console/lcql-examples.md)
→ [Query Console UI](Query_Console/query-console-ui.md)

### "How do I use the API?"
→ [API Keys](Platform_Management/Access_and_Permissions/api-keys.md)
→ [LimaCharlie SDK](Platform_Management/limacharlie-sdk.md)
→ `LimaCharlie.io_REST_API/`

### "How do I integrate with [tool]?"
→ [Extensions Directory](Add-Ons/Extensions/)
→ [API Integrations](Add-Ons/API_Integrations/)

### "Sensor won't install / connect"
→ [Sensor Installation FAQ](FAQ/faq-sensor-installation.md)
→ [Troubleshooting FAQ](FAQ/faq-troubleshooting.md)
→ [Sensor Connectivity](Sensors/sensor-connectivity.md)

---

## Documentation Statistics

- **Total Documentation Files**: 275+ markdown files
- **Major Sections**: 13 top-level categories
- **Largest Sections**:
  - Sensors & Telemetry: ~88 files
  - Add-Ons & Extensions: ~63 files
  - Detection & Response: ~19 files

---

**For AI Agents**: When responding to user queries, use this index to:
1. Identify the primary topic area
2. Navigate to specific documentation using relative paths
3. Cross-reference related topics (e.g., adapters + outputs, sensors + D&R rules)
4. Provide complete file paths when referencing documentation
