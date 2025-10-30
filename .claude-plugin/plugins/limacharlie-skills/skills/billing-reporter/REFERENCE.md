# Billing Reporter Reference Guide

This document provides detailed reference information about LimaCharlie billing concepts, SKUs, and technical details.

---

## Understanding Billing Components

### Billing Models

**Quota-Based (vSensors)**
- Fixed monthly fee per vSensor quota
- Includes 1 year of full telemetry storage
- Sensors can go over quota (causes degraded service/spotty connectivity, no overage charges)
- Optimal utilization: 75-95% of quota
- Best for: Stable, predictable deployments

**Usage-Based**
- Pay for actual sensor connection time + events processed
- No quota limits or over-quota penalties
- Billed on: sensor time, events processed, events stored
- Best for: Variable workloads, seasonal usage

**Sleeper Mode**
- $0.10 per sensor per 30 days
- Minimal telemetry until activated
- Best for: Incident response readiness, pre-deployments

**Unified Billing**
- Single invoice for all organizations under a billing domain
- Consolidated billing cycle
- Centralized payment
- Best for: MSPs, MSSPs, enterprises with multiple departments

### Key Billing SKUs

| SKU | Description | Typical Cost Driver |
|-----|-------------|---------------------|
| `sensor_quota` | vSensor quota (quota-based model) | Number of concurrent sensors |
| `sensor_events` | Events processed by platform | Event volume from sensors |
| `sensor_retained` | Events stored (retention) | Event volume × retention period |
| `output_data` | Data egress to external systems | Output volume × destinations |
| `query_events` | Events evaluated during searches | Query frequency × time range |
| `artifact_quota` | Artifact storage | Number and size of collected files |
| `payload_data` | Data sent to endpoints | Payload deployments (Dumper, ART, etc.) |
| `extension_*` | Extension-specific costs | Varies by extension |

### Cost Components Breakdown

**Sensors (Typically 40-60% of costs)**
- Per-endpoint quota or usage-based pricing
- Includes: agent connection, telemetry ingestion, 1yr storage
- Optimization: Sensor culling, sleeper mode, performance modes

**Output Data (Typically 20-40% of costs)**
- Billed per GB transmitted to external systems
- Free: GCP same-region (GCS, Pub/Sub, BigQuery)
- Optimization: Send detections only, same-region outputs, compression

**Event Processing & Storage (Typically 10-20% of costs)**
- Processing: Events evaluated by D&R rules
- Storage: Events retained beyond 1 year (Insight extension)
- Optimization: Event filters, retention policies, performance modes

**Queries (Typically 5-15% of costs)**
- Events evaluated during LCQL searches
- Billed per million events scanned
- Optimization: Narrow time ranges, platform filters, saved queries

**Extensions (Variable)**
- Additional services and integrations
- Examples: Artifact, VirusTotal, Zeek, Plaso
- Optimization: Disable unused extensions, throttle usage

**Artifacts & Payloads (Variable)**
- Artifacts: Files collected from endpoints
- Payloads: Data sent to endpoints (Dumper, ART)
- Optimization: Retention policies, selective collection

---

## Complete SKU Catalog

The following SKUs are available in LimaCharlie. Use `limacharlie:get_sku_definitions` to retrieve current pricing.

### Extension SKUs

**Binary Library Analysis** (`extension_binlib:files_scanned`)
- Scans executable files and binaries to extract metadata
- Identifies libraries, analyzes imports/exports
- Detects potential security issues
- Unit: per file scanned

**AI Agent Engine** (`extension_ext-ai-agent-engine:tokens`)
- LLM-powered security automation and analysis
- Intelligent threat analysis and investigation
- Response recommendations and security operations
- Unit: per token consumed

**Plaso Timeline Analysis** (`extension_ext-plaso:bytes_scanned`)
- Forensic timeline analysis using Plaso (log2timeline)
- Processes disk images, log files, and artifacts
- Builds detailed chronological event sequences
- Unit: per GB scanned

**Playbook Execution** (`extension_ext-playbook:exec_time`)
- Automated workflow orchestration
- Multiple actions, integrations, and decision logic
- Responds to security events and performs investigations
- Unit: per second of execution time

**Strelka File Analysis** (`extension_ext-strelka:bytes_scanned`)
- Deep file analysis and metadata extraction
- Recursively extracts and analyzes files
- Identifies file types and embedded content
- Unit: per GB scanned

**Zeek Extension** (`extension_ext-zeek:bytes_scanned`)
- Processes PCAP files and network traffic
- Generates network metadata and security insights
- On-demand processing of uploaded PCAPs
- Unit: per GB analyzed

### Storage and Data SKUs

**Artifact Storage** (`log_bytes`)
- Storage of logs and artifacts on daily basis
- Includes PCAP files, text logs, Windows Event Logs
- Measured per GB-day (each GB stored for full day = 1 unit)
- Part of core telemetry retention capability

**Artifacts Exported** (`log_bytes_exported`)
- Data egress for artifacts exported to external systems
- Separate from Output module
- Tracks artifact data being exported
- Unit: per GB exported

**Output Storage** (`output_bytes_tx`)
- Data sent to configured outputs (SIEM, logging platforms, S3, etc.)
- Forwards detections, events, and telemetry
- Measures total volume to all configured outputs
- Unit: per GB sent

**Payload Data Sent** (`payload_bytes`)
- Data volume for payloads deployed to endpoints
- Files, scripts, or executables sent to sensors
- Includes Atomic Red Team and Dumper services
- Unit: per GB sent

### Platform Services

**Replay Events** (`replay_num_events`)
- Retroactively apply new detection rules to historical data
- Useful for threat hunting and testing new detections
- Investigate incidents by replaying events through updated logic
- Unit: per event replayed

**Zeek Network Analysis Service** (`service_zeek`)
- Zeek (formerly Bro) network analysis service
- Processes network traffic and generates metadata
- Analyzes PCAP data for connection logs, DNS, HTTP, file transfers
- Unit: per request or operation

**USP Telemetry Processed** (`usp_telemetry_bytes`)
- Universal Security Platform telemetry ingestion
- Ingests security telemetry from non-endpoint sources
- Cloud logs, network devices, applications, third-party tools
- Unit: per GB processed

---

## Cost Optimization Best Practices

### Quick Wins (High Impact, Low Effort)

1. **Use GCP Same-Region Outputs** (FREE)
   - USA datacenter → us-central1
   - Europe → europe-west4
   - Canada → northamerica-northeast1
   - Savings: 100% of output costs for same-region

2. **Switch Event Stream to Detection Stream**
   - Change outputs from `stream: event` to `stream: detection`
   - Savings: 90-99% output volume reduction

3. **Enable Sensor Culling**
   - Remove stale sensors that haven't connected
   - Savings: 10-20% quota costs

4. **Add Query Filters**
   - Narrow time ranges (-4h instead of -7d)
   - Add platform filters early
   - Savings: 10-100x query cost reduction

### Medium-Term Optimizations

1. **Performance Mode Tuning**
   - Low mode for low-risk endpoints
   - High mode only for critical systems
   - Savings: 20-40% event volume

2. **Output Architecture Review**
   - Consolidate redundant outputs
   - Use bulk webhooks instead of individual
   - Enable compression
   - Savings: 30-50% output costs

3. **Extension Audit**
   - Disable unused extensions
   - Throttle high-volume extensions
   - Savings: Variable, often $50-200/month

4. **Detection Suppression**
   - Add suppression to noisy rules
   - Use false positive rules
   - Savings: 50-95% detection volume

### Long-Term Strategies

1. **Billing Model Optimization**
   - Evaluate quota-based vs usage-based
   - Consider sleeper mode for IR readiness
   - Move to unified billing for multi-org
   - Savings: Variable, can be significant

2. **Retention Policy Review**
   - Adjust retention periods
   - Archive to cheaper storage (S3 Glacier)
   - Savings: 50-80% storage costs

3. **Deployment Architecture**
   - Consolidate small organizations
   - Separate prod/dev/test appropriately
   - Use tags for logical separation instead of orgs
   - Savings: Reduced overhead, easier management

4. **Proactive Monitoring**
   - Usage Alerts extension
   - Weekly billing reviews
   - Automated reports to stakeholders
   - Savings: Prevents cost creep

---

## Setting Up Cost Monitoring

### Usage Alerts Extension

**Guide the user through setup**:

1. **Navigate to Extensions**
   "Go to Add-ons → Extensions → 'Usage Alerts'"

2. **Create Alert Rules**
   "Create alerts for your key cost drivers. For example:
   - Output data: 100GB per 30 days
   - Query events: 50M per 7 days
   - Sensor quota: 90% utilization"

3. **Configure Notifications**
   "Route these alerts to your team:
   - Create an output to Slack/email
   - Set up a webhook for your monitoring system
   - Configure the detection stream to forward usage alerts"

4. **Set Appropriate Thresholds**
   "Based on your current usage:
   - Current output: 85GB/month → Alert at 100GB
   - Current queries: 30M events/week → Alert at 50M
   - Current sensors: 80/100 quota → Alert at 90"

### Regular Billing Reviews

**Recommend a cadence**:

**Weekly** (Quick checks):
- Review usage alerts
- Check sensor count vs quota
- Monitor output volume trends

**Monthly** (Detailed review):
- Full billing analysis
- Cost optimization opportunities
- Budget vs actual comparison
- Trend analysis

**Quarterly** (Strategic):
- Billing model assessment
- Architecture review
- Multi-org optimization
- Vendor relationship (custom plans)

---

## Exporting Data for External Analysis

### Using MCP Tools for Current Data

**Current billing cycle data** is available through the MCP server tools:
- `limacharlie:get_org_info` - Organization details, quota settings, billing model
- `limacharlie:get_usage_stats` - Current cycle usage by SKU, event counts, costs
- `limacharlie:get_billing_details` - Stripe billing data, subscriptions, payment methods
- `limacharlie:get_sku_definitions` - Complete SKU catalog with pricing

I can fetch this data for you and format it for export to spreadsheets or other analysis tools.

### BigQuery Export for Historical Analysis

**For historical analysis**:

"For comprehensive historical billing analysis, I recommend:

1. Set up billing record output to BigQuery:
   - Stream: `audit` or create custom billing export
   - Destination: Google Cloud BigQuery
   - Region: Same as LC datacenter (free)

2. Build custom reports in Looker Studio:
   - Time-series cost analysis
   - SKU breakdown over time
   - Multi-org comparisons
   - Forecasting and budgeting

3. Set up automated reporting:
   - Daily/weekly cost summaries
   - Anomaly detection
   - Budget alerts"

### CSV/Spreadsheet Export

**For spreadsheet analysis**:

"I can help you export current usage data for Excel/Google Sheets:
1. I'll fetch the data using MCP tools
2. Format it as a table or CSV structure
3. You can copy/paste into your spreadsheet
4. Add your own calculations, pivot tables, and charts

This is perfect for:
- Custom cost analysis and forecasting
- Presenting to stakeholders
- Comparing against budgets
- Building your own reporting dashboards"

---

## Troubleshooting Common Issues

### "Usage data seems incorrect"

**Check**:
1. Billing cycle timing (data is per current cycle)
2. Organization ID (are you looking at the right org?)
3. Recent changes (quota adjustments, new outputs)
4. API permissions (can you access billing data?)

### "Can't access billing data for some orgs"

**Likely causes**:
- Insufficient API permissions
- Not a member of the organization
- Organization in different billing domain
- Custom billing plan restrictions

**Solution**:
"You need the appropriate API permissions to access billing data. Check your user role in each organization, or ask an admin to grant you access."

### "MCP tool returns empty data"

**Check**:
1. Organization is active (not deleted)
2. Billing cycle has data (not brand new org)
3. MCP server configuration (credentials valid)
4. API endpoint access (network, firewall)

### "Estimated costs don't match invoice"

**Remember**:
- Usage stats show current cycle (incomplete)
- Invoices include proration for quota changes
- Some SKUs are post-paid (previous month)
- Others are pre-paid (next month)
- Unified billing aggregates differently

**Explain**:
"The usage stats show your current billing cycle data, which is incomplete. Your invoice includes:
- Pre-paid items (sensor quota for next month)
- Post-paid items (usage from last month)
- Prorations for any quota changes
- Previous balance or credits"

---

## Additional Resources

### Documentation
- Billing Options: `/limacharlie/doc/Platform_Management/Billing/billing-options.md`
- FAQ Billing: `/limacharlie/doc/FAQ/faq-billing.md`
- FAQ Invoices: `/limacharlie/doc/FAQ/faq-invoices.md`
- Output Billing: `/limacharlie/doc/Outputs/output-billing.md`
- Usage Alerts Extension: `/limacharlie/doc/Add-Ons/Extensions/LimaCharlie_Extensions/ext-usage-alerts.md`

### Related Skills
- **performance-optimizer**: For detailed cost optimization strategies
- **output-configurator**: For optimizing output costs
- **sensor-manager**: For sensor quota and culling
- **api-integrator**: For programmatic billing access

### External Links
- Pricing: https://limacharlie.io/pricing
- MCP Server Documentation: https://docs.limacharlie.io/docs/mcp-server
- Support: support@limacharlie.io
- Community: https://community.limacharlie.com
