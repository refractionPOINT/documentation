---
name: reporting
description: Generate comprehensive security and operational reports from LimaCharlie data including sensor health, detections, usage statistics, billing, and configuration audits. Use when users need MSSP reports, executive summaries, compliance reports, or multi-tenant billing analysis.
allowed-tools:
  - Read
  - Write
  - Bash
  - mcp__limacharlie__get_org_info
  - mcp__limacharlie__list_sensors
  - mcp__limacharlie__get_sensor_info
  - mcp__limacharlie__get_historic_detections
  - mcp__limacharlie__list_rules
  - mcp__limacharlie__list_outputs
  - mcp__limacharlie__list_tags
  - mcp__limacharlie__list_users
---

# LimaCharlie Reporting Skill

## Overview
This skill enables AI agents to generate comprehensive security and operational reports from LimaCharlie organization data. It provides structured access to telemetry, detections, sensors, usage statistics, and more.

**Quick Links**:
- 📋 **[ROADMAP.md](ROADMAP.md)** - Complete list of planned templates with development status
- 📊 **[data-catalog.yaml](data-catalog.yaml)** - Full catalog of available data sources
- 🎨 **[utils/branding.py](utils/branding.py)** - Dynamic branding utility

## Purpose
- Generate standardized reports for LimaCharlie SecOps data
- Provide reusable templates for common reporting scenarios
- Ensure consistency across multiple report generation sessions
- Document available data sources and access methods

**Current Status**: 3 of 9 templates completed (33% complete)

## When to Use This Skill
Use this skill when you need to:
- Create reports on sensor health and status
- Analyze security detections over time periods
- Generate usage and billing reports
- Audit organizational configuration (rules, outputs, users)
- Investigate security incidents
- Monitor operational metrics
- Create executive summaries
- Export data for compliance purposes

## Prerequisites

### Authentication
Ensure LimaCharlie CLI is authenticated:
```bash
limacharlie who  # Check authentication status
limacharlie set-oid <OID>  # Set active organization
```

### Required Files
- `data-catalog.yaml` - Complete reference of available data types
- `utils/report_helpers.py` - Python utilities for data collection
- `templates/` - Pre-built report templates

## Available Data Sources

Refer to `data-catalog.yaml` for the complete list of 23 data categories including:

1. **Organization Metadata** - Basic org info, quotas, versions
2. **Sensors** (646 total) - Endpoints, status, capabilities
3. **D&R Rules** (606 total) - Detection and response logic
4. **Events** - Historical telemetry (Insight enabled)
5. **Detections** - Security alerts and findings
6. **Usage Statistics** - Daily operational metrics
7. **Outputs** (68 total) - Data export configurations
8. **Tags** (53 total) - Sensor organization
9. **Extensions** (4 active) - Subscribed services
10. **API Keys** (89 total) - Programmatic access
11. **Users** (26 total) - Access control
12. **YARA Rules** - Malware detection
13. **False Positive Rules** - Alert suppression
14. **Installation Keys** (45 total) - Sensor deployment
15. **Audit Logs** - Change history
16. **MITRE ATT&CK** - Coverage mapping
17. **Lookup Tables** - Data enrichment
18. **IOC Search** - Threat hunting
19. **Artifacts** - Collected forensic data
20. **Event Schemas** - Event definitions
21. **Jobs** - Background tasks
22. **Secrets** - Stored credentials
23. **LCQL Queries** - Advanced querying

## Report Types

### 1. Comprehensive MSSP Report ✅ IMPLEMENTED
**Purpose**: Complete operational and security report for MSSP clients

**Includes**:
- Organization metadata with current sensor version
- Detailed sensor health by platform with human-readable names
  - Traditional OS: Windows, Linux, macOS
  - Extensions: LimaCharlie Extensions, Test Systems
  - Integrations: Slack, Office365, Defender
- Security detection analysis (10,000 limit)
  - Detection categories with counts
  - Top triggered rules (with actual rule names)
  - Detection timeline by day
- Usage statistics over time period
  - Event volume trends
  - D&R rule evaluations
  - Data output metrics
- Configuration overview
  - D&R rules, outputs, tags, users, API keys
- Interactive HTML with Chart.js graphs

**Template**: `templates/mssp_comprehensive_report.py`
**Status**: Fully functional and tested
**Output formats**: HTML (with charts), Markdown, JSON

**Usage**:
```bash
python3 templates/mssp_comprehensive_report.py <OID> [days] [format]
# Example: 30-day HTML report
python3 templates/mssp_comprehensive_report.py 8cbe27f4-... 30 html
```

### 2. Executive Summary Report
**Purpose**: High-level organizational overview for management

**Includes**:
- Organization metadata and sensor count
- Online vs offline sensor ratio
- Detection summary (last 7/30 days)
- Top detection categories
- Usage trend highlights
- Critical alerts or issues

**Template**: `templates/executive_summary.py`
**Status**: Basic implementation, can be enhanced

### 3. Sensor Health Report ✅ IMPLEMENTED
**Purpose**: Comprehensive operational health monitoring for sensor fleet

**Includes**:
- Executive summary with key metrics
  - Total sensors, online/offline counts
  - Overall availability percentage
  - Platform and tag counts
- Platform distribution analysis
  - Sensors by platform with human-readable names
  - Online/offline status per platform
  - Availability percentage per platform
  - Sample hostnames for each platform type
- Tag-based sensor grouping
  - Sensors per tag with status
  - Identification of untagged sensors
- Stale sensor detection
  - Offline 1-7 days
  - Offline 7-30 days
  - Offline >30 days
  - Last seen timestamps
- Sensor version distribution
  - Top 10 versions in use
  - Version standardization insights
- Actionable recommendations
  - Sensors requiring attention
  - Tag management suggestions
  - Availability improvement tips
- Interactive HTML with stacked bar charts

**Template**: `templates/sensor_health_report.py`
**Status**: Fully functional and tested
**Output formats**: HTML (with charts), Markdown, JSON

**Usage**:
```bash
python3 templates/sensor_health_report.py <OID> [format]
# Example: HTML health report
python3 templates/sensor_health_report.py 8cbe27f4-... html
```

**Key Features**:
- Two-pass platform naming for human-readable categories
- Automatic stale sensor categorization by offline duration
- Version distribution analysis for compliance checking
- Comprehensive tagging analysis and recommendations
- Real-time online/offline status tracking

### 4. Security Detections Report
**Purpose**: Analysis of security alerts over time

**Includes**:
- Total detections by time period
- Detections by category
- Detections by sensor
- Top triggered rules
- Trends and patterns
- Unresolved high-severity detections

**Template**: `templates/security_detections.py`

### 5. Multi-Tenant Billing Report ✅ IMPLEMENTED
**Purpose**: Comprehensive billing overview across all accessible organizations

**Includes**:
- Cross-tenant summary dashboard
  - Total sensors across all orgs
  - Total events, data output, rule evaluations
  - Aggregated estimated monthly costs
- Organization overview table
  - Sensor count vs quota per org
  - Activity metrics per org
  - Cost comparison across tenants
- Detailed per-organization breakdown
  - Key metrics (events, output GB, evaluations)
  - Sensor utilization (active vs quota)
  - Last 7 days daily activity
  - Cost estimation with transparent formulas
- Interactive HTML with Chart.js cost visualization
- Multi-format output (HTML, Markdown, JSON)

**Template**: `templates/multi_tenant_billing_report.py`
**Status**: Fully functional and tested
**Output formats**: HTML (with charts), Markdown, JSON

**Usage**:
```bash
python3 templates/multi_tenant_billing_report.py [days]
# Example: 30-day billing report across all accessible orgs
python3 templates/multi_tenant_billing_report.py 30
```

**Cost Estimation Formula**:
```
Estimated Monthly Cost =
  (Sensor Count × $5) +           # Base sensor cost
  (Output GB × $0.20) +            # Data egress
  (Evaluations ÷ 1000 × $0.001)   # Rule evaluations
```

**Note**: Uses `Manager.userAccessibleOrgs()` to automatically discover all organizations the authenticated user can access.

### 6. Configuration Audit Report
**Purpose**: Document current organizational configuration

**Includes**:
- D&R rules summary
- Output configurations
- YARA rules
- Tags in use
- Installation keys
- API keys
- Users and permissions

**Template**: `templates/config_audit.py`

### 7. Incident Investigation Report
**Purpose**: Deep-dive analysis for specific security incidents

**Includes**:
- Timeline of relevant events
- Affected sensors
- Related detections
- IOC search results
- Lateral movement analysis
- Remediation actions taken

**Template**: `templates/incident_investigation.py`

### 8. MITRE ATT&CK Coverage Report
**Purpose**: Assess detection capability against MITRE framework

**Includes**:
- Tactics coverage percentage
- Techniques coverage by tactic
- Coverage gaps
- Recommended improvements

**Template**: `templates/mitre_coverage.py`

### 9. Custom Report
**Purpose**: Ad-hoc reports based on specific user requirements

**Approach**:
1. Consult `data-catalog.yaml` for available data
2. Determine required data sources
3. Use `utils/report_helpers.py` for data collection
4. Format output as requested (HTML, Markdown, JSON, CSV)

## Usage Instructions

### Step 1: Understand the Request
- What is the report purpose?
- What time range is needed?
- What format is requested?
- Are there specific filters or criteria?

### Step 2: Consult Data Catalog
- Review `data-catalog.yaml` for available data
- Identify required data sources
- Check permissions needed
- Note access methods (SDK or MCP tools)

### Step 3: Verify Access
- Confirm authentication: `limacharlie who`
- Verify organization is set: check OID in output
- Check if Insight is enabled (for historical data)
- Verify permissions for required data sources

### Step 4: Collect Data
Use appropriate methods:

**Python SDK Approach**:
```python
from limacharlie import Manager
import time

m = Manager(oid='YOUR_OID')

# Example: Get detections for last 7 days
end = int(time.time())
start = end - (7 * 24 * 3600)
detections = m.getHistoricDetections(start=start, end=end, limit=1000)
```

**MCP Tool Approach**:
```python
# Use mcp__limacharlie__* tools directly
# Example available in tool descriptions
```

**Utility Functions**:
```python
from utils.report_helpers import (
    get_org_summary,
    get_sensor_statistics,
    get_detection_summary,
    get_usage_summary
)
```

### Step 5: Process and Format
- Aggregate data as needed
- Calculate statistics and trends
- Apply filters and sorting
- Format for output (HTML/Markdown/JSON)

### Step 6: Generate Report
- Include metadata (date, time range, org)
- Add executive summary
- Present data with visualizations
- Provide actionable insights
- Include methodology notes

## Best Practices

### Data Collection
1. **Always specify time ranges** - Prevents overwhelming data returns
2. **Use limits on queries** - Start with small limits, increase if needed
3. **Cache static data** - Org info, schemas don't change frequently
4. **Handle pagination** - Large datasets may require multiple queries
5. **Check permissions first** - Verify before attempting data access

### Report Quality
1. **Include context** - Date generated, time period, organization
2. **Provide summaries** - Don't just dump raw data
3. **Highlight insights** - What do the numbers mean?
4. **Show trends** - Compare to previous periods when possible
5. **Make it actionable** - Include recommendations

### Performance
1. **Query efficiently** - Use filters to reduce data volume
2. **Parallel data collection** - Fetch independent data sources concurrently
3. **Stream large datasets** - Don't load everything into memory
4. **Use appropriate tools** - MCP tools have built-in optimizations
5. **Cache sensor lists** - For multi-tenant reports, iterate once and store
6. **Batch organization queries** - Collect all org OIDs first, then process in batches
7. **Pre-aggregate data** - Calculate totals during collection, not after
8. **Limit detection queries** - Use reasonable limits (1000-10000) to avoid timeouts

### Error Handling
1. **Verify authentication** before starting
2. **Handle permission errors** gracefully
3. **Provide fallbacks** if data unavailable
4. **Log errors** for debugging
5. **Validate data** before processing
6. **Handle empty organizations** - Some orgs may have 0 sensors or activity
7. **Graceful degradation** - If one org fails, continue with others in multi-tenant reports

### Working with Sensors
1. **Sensor iteration** - Use `m.sensors()` generator for large sensor lists
2. **Online status** - `m.getAllOnlineSensors()` returns list of SID strings
3. **Sensor info caching** - Call `sensor.getInfo()` once and cache the result
4. **Platform codes** - Use two-pass pattern analysis for descriptive names
5. **Hostname patterns** - Group sensors by hostname prefixes (ext-, test-, etc.)
6. **Tag filtering** - Filter sensors by tags before processing to reduce volume

## Output Formats

### HTML Report
- Professional styling
- Interactive tables
- Charts and graphs
- Exportable
- **Template**: `templates/html_template.html`

### Markdown Report
- Clean, readable format
- Tables and lists
- Code blocks for technical details
- Compatible with documentation systems
- **Template**: `templates/markdown_template.md`

### JSON Export
- Machine-readable
- Complete data structure
- For further processing
- API integration

### CSV Export
- Spreadsheet compatible
- Simple data tables
- For analysis in Excel/Sheets

## Example Workflow

```python
# 1. Load utilities
from utils.report_helpers import ReportGenerator
import time

# 2. Initialize report generator
rg = ReportGenerator(oid='8cbe27f4-bfa1-4afb-ba19-138cd51389cd')

# 3. Define time range
end = int(time.time())
start = end - (7 * 24 * 3600)  # Last 7 days

# 4. Collect data
org_info = rg.get_org_info()
sensor_stats = rg.get_sensor_stats()
detection_summary = rg.get_detection_summary(start, end)
usage_stats = rg.get_usage_summary(start, end)

# 5. Generate report
report = rg.generate_executive_summary(
    org_info=org_info,
    sensor_stats=sensor_stats,
    detection_summary=detection_summary,
    usage_stats=usage_stats,
    time_range=(start, end)
)

# 6. Output
with open('exec_summary.html', 'w') as f:
    f.write(report)
```

## Common Scenarios

### Scenario 1: "Generate a weekly security report"
1. Use **Security Detections Report** template
2. Time range: Last 7 days
3. Include: Detection counts, categories, top rules, trends
4. Format: HTML with charts

### Scenario 2: "How many sensors are online?"
1. Quick query using `Manager.getAllOnlineSensors()`
2. Compare to total sensor count
3. Break down by platform
4. List recently offline sensors

### Scenario 3: "What's our MITRE coverage?"
1. Use **MITRE ATT&CK Coverage Report** template
2. Fetch MITRE report data
3. Visualize tactics and techniques
4. Identify gaps
5. Recommend rule additions

### Scenario 4: "Monthly billing report"
1. Use **Usage & Billing Report** template
2. Time range: Current month
3. Aggregate daily stats by week
4. Highlight cost drivers
5. Provide optimization recommendations

### Scenario 5: "Investigate IOC across fleet"
1. Use IOC search functionality
2. Search by hash/domain/IP
3. Identify affected sensors
4. Check related detections
5. Generate incident report

## Troubleshooting

### "Unauthorized" errors
- Check authentication: `limacharlie who`
- Verify OID is set correctly
- Check required permissions in data catalog
- Some data requires specific permissions

### "Insight not enabled"
- Historical events/detections require Insight
- Verify: `m.isInsightEnabled()`
- Use alternative data sources if disabled

### Large data volumes
- Add limits to queries
- Narrow time ranges
- Use pagination
- Filter by specific criteria

### Missing data
- Verify data actually exists for time range
- Check if sensors were active during period
- Confirm data retention settings
- Review org configuration

## File Structure
```
.claude/skills/limacharlie-reporting/
├── skill.md (this file - comprehensive documentation)
├── ROADMAP.md (development roadmap and template progress)
├── README.md (quick reference)
├── data-catalog.yaml (23 data categories documented)
├── templates/
│   ├── mssp_comprehensive_report.py ✅ (fully functional)
│   ├── multi_tenant_billing_report.py ✅ (fully functional)
│   ├── sensor_health_report.py ✅ (fully functional)
│   ├── executive_summary.py (basic implementation)
│   ├── security_detections.py (planned)
│   ├── config_audit.py (planned)
│   ├── incident_investigation.py (planned)
│   └── mitre_coverage.py (planned)
└── utils/
    ├── branding.py ✅ (dynamic brand extraction)
    ├── report_helpers.py (planned)
    ├── data_collectors.py (planned)
    ├── formatters.py (planned)
    └── visualizations.py (planned)
```

**Current Status**:
- ✅ **mssp_comprehensive_report.py**: Production-ready, handles 7-30+ day reports
- ✅ **multi_tenant_billing_report.py**: Production-ready, cross-tenant billing overview
- ✅ **sensor_health_report.py**: Production-ready, comprehensive sensor fleet health monitoring
- ✅ **branding.py**: Extracts company branding from domains
- 📝 Data catalog fully documented with all access methods
- 📝 Known issues and solutions documented
- 📝 Best practices and gotchas section complete

## Known Issues and Gotchas

### Detection Data

**Issue**: Detection rule names showing as "unknown"
**Cause**: The detection data structure uses `source_rule` field, not `rule_name`
**Solution**: Always extract rule names using `det.get('source_rule', det.get('cat', 'unknown'))`

**Example**:
```python
# WRONG - will show "unknown"
rule = det.get('rule_name', 'unknown')

# CORRECT - extracts actual rule name
rule = det.get('source_rule', det.get('cat', 'unknown'))
```

**Detection Data Structure**:
```python
{
    'cat': 'unique-google-domain',           # Category name
    'source_rule': 'general.test-goog',      # Actual rule name (namespace.rule)
    'namespace': 'general',                   # Rule namespace
    'detect_id': '...',                       # Unique detection ID
    'ts': 1234567890,                         # Timestamp (may be ms or seconds)
    'sid': '...',                             # Sensor ID (may be 'N/A')
}
```

**Important Notes**:
- Multiple rules can trigger on the same event (e.g., production + testing rules)
- Rules with identical counts are usually related but serve different purposes
- `source_rule` format is typically "namespace.rule-name"
- Timestamps can be in seconds OR milliseconds - normalize before processing

### Sensor Last Seen Timestamps

**Issue**: Stale sensor detection showing 0 offline sensors when many are actually offline
**Cause**: The `last_seen` field doesn't exist or is 0 for most sensors - must use `alive` field instead
**Solution**: Parse the `alive` field (datetime string) for offline duration calculation

**Field Structure**:
```python
sensor_info = sensor.getInfo()

# WRONG - this field often doesn't exist or is 0
last_seen = info.get('last_seen', 0)  # Returns 0 for most sensors

# CORRECT - use 'alive' field (datetime string)
alive_str = info.get('alive', '')  # "2025-10-01 17:08:10"
```

**Parsing alive field**:
```python
from datetime import datetime, timezone

alive_str = info.get('alive', '')
if alive_str:
    # Parse datetime string (format: "YYYY-MM-DD HH:MM:SS")
    alive_dt = datetime.strptime(alive_str, '%Y-%m-%d %H:%M:%S')
    alive_dt = alive_dt.replace(tzinfo=timezone.utc)
    last_seen_timestamp = alive_dt.timestamp()
    offline_hours = (current_time - last_seen_timestamp) / 3600
```

**Important Notes**:
- Use built-in `datetime.strptime()` - no external dependencies needed
- `alive` field is consistently populated for offline sensors
- `last_seen` field should only be used as fallback
- Always check `alive` first for accurate offline duration

### Sensor Platform Data

**Issue**: Numeric platform codes (e.g., 2415919104) instead of OS names
**Cause**: These are extension sensors, not traditional endpoints
**Solution**: Categorize by hostname pattern and provide mapping

**Platform Types**:

1. **Traditional OS Platforms**:
   - String values: "windows", "linux", "macos", "chrome"
   - Access via: `sensor.getInfo()['plat']`

2. **Extension/Adapter Sensors** (numeric codes):
   - Cloud integrations: Slack, Office365, Defender, etc.
   - Extensions: Strelka, SecureAnnex, Hayabusa, AI agents
   - Adapters: Test systems, parsers, data processors
   - Hostname pattern indicates type (e.g., "ext-", "slack-", "office365")

**Platform Categorization Logic**:
```python
def get_platform_display_name(platform, hostname):
    """Convert platform to human-readable name"""
    if platform in ['windows', 'linux', 'macos', 'chrome']:
        return platform

    # Numeric = extension/adapter
    if isinstance(platform, int) or str(platform).isdigit():
        hostname_lower = str(hostname).lower()
        if 'ext-' in hostname_lower:
            return f'extension/{platform}'
        elif any(svc in hostname_lower for svc in ['slack', 'office365', 'defender']):
            return f'cloud-integration/{platform}'
        else:
            return f'adapter/{platform}'

    return str(platform)
```

**Reporting Best Practice**:
- Always include hostname samples for numeric platforms
- Categorize extensions separately from OS sensors
- Provide reference mapping in reports

**SOLUTION - Two-Pass Platform Naming (Implemented)**:

Use a two-pass approach to generate descriptive platform names:

```python
# Pass 1: Collect all hostnames per platform code
platform_hostnames = defaultdict(list)
for sensor in all_sensors:
    platform_raw = sensor.getInfo().get('plat')
    hostname = sensor.getInfo().get('hostname')
    platform_hostnames[str(platform_raw)].append(hostname)

# Pass 2: Analyze patterns and assign descriptive names
def get_platform_display_name(platform_raw, hostnames):
    patterns = {
        'ext': sum(1 for h in hostnames if 'ext-' in h.lower()),
        'test': sum(1 for h in hostnames if 'test' in h.lower()),
        'slack': sum(1 for h in hostnames if 'slack' in h.lower()),
        'office': sum(1 for h in hostnames if 'office' in h.lower()),
        'defender': sum(1 for h in hostnames if 'defender' in h.lower()),
    }

    total = len(hostnames)
    if patterns['ext'] > total * 0.5:
        return 'LimaCharlie Extensions'
    elif patterns['test'] > total * 0.5:
        return 'Test/Parser Systems'
    elif patterns['slack'] > 0:
        return 'Slack Integration'
    elif patterns['office'] > 0:
        return 'Office365 Integration'
    elif patterns['defender'] > 0:
        return 'Defender Integration'
    else:
        return f'Adapter ({hostnames[0]})'
```

**Result**: Transforms confusing codes into readable names:
- `2415919104` → "LimaCharlie Extensions" (30 sensors)
- `2147483648` → "Test/Parser Systems" (7 sensors)
- `67108864` → "Defender Integration" (3 sensors)
- `3758096384` → "Office365 Integration" (1 sensor)
- `150994944` → "Slack Integration" (1 sensor)

### Data Type Issues

**Issue**: Type mismatches causing errors
**Common Problems**:
1. `getAllOnlineSensors()` returns list of SID strings, not dicts
2. Platform field can be string OR integer
3. Timestamps may be seconds or milliseconds
4. `getHistoricDetections()` returns generator, not list (no `len()`)

**Solutions**:
```python
# Online sensors
online_sids = set(online_sensors) if isinstance(online_sensors, list) else set()

# Platform sorting (mixed types)
for platform in sorted(platforms.keys(), key=str):
    # ...

# Timestamp normalization
if ts > 1000000000000:  # Milliseconds
    ts = ts / 1000

# Generator counting
count = 0
for item in generator:
    count += 1
# Use count, not len(generator)
```

### Multi-Tenant Access

**Issue**: Accessing multiple organizations for cross-tenant reporting
**Solution**: Use `Manager.userAccessibleOrgs()` to enumerate accessible organizations

**Data Structure**:
```python
from limacharlie import Manager

# Get list of accessible organizations
m = Manager()
orgs_data = m.userAccessibleOrgs()

# Returns dict with two keys:
# 'orgs': list of OID strings (UUIDs)
# 'names': dict mapping OID -> organization name
org_oids = orgs_data.get('orgs', [])
org_names = orgs_data.get('names', {})

# Iterate over organizations
for oid in org_oids:
    m_org = Manager(oid=oid)
    org_name = org_names.get(oid, 'Unknown')
    # Access org-specific data
    info = m_org.getOrgInfo()
    usage = m_org.getUsageStats()
```

**Common Errors**:
- ❌ `m.getOrgs()` - Method doesn't exist
- ❌ `m.getBillingInfo()` - Method doesn't exist (use `getUsageStats()` instead)
- ❌ Iterating directly over return value - Must extract 'orgs' list first

**Usage Stats for Billing**:
```python
usage = m.getUsageStats()
for date_str, stats in usage['usage'].items():
    events = stats.get('sensor_events', 0)
    output_bytes = stats.get('output_bytes_tx', 0)
    evaluations = stats.get('replay_num_evals', 0)

# Cost estimation (approximate):
# - $5/sensor/month
# - $0.20/GB output
# - $0.001 per 1000 rule evaluations
```

### Usage Statistics Data Structure

**Important**: Usage stats are the primary source for billing and operational metrics.

**Structure**:
```python
usage = m.getUsageStats()
# Returns: {
#   'usage': {
#     '2025-11-06': {
#       'sensor_events': 131206,        # Total events ingested
#       'output_bytes_tx': 500123456,   # Bytes transmitted (data egress)
#       'replay_num_evals': 435847,     # D&R rule evaluations
#       'peak_sensors': 4,              # Peak concurrent sensors
#       # ... other metrics
#     },
#     '2025-11-07': { ... },
#     # ... more dates
#   }
# }
```

**Key Metrics**:
- `sensor_events` - Total events ingested for the day
- `output_bytes_tx` - Data output in bytes (divide by 1024³ for GB)
- `replay_num_evals` - Number of D&R rule evaluations
- `peak_sensors` - Peak number of concurrent sensors

**Date Range**: Typically returns ~90 days of daily metrics

**Aggregation Example**:
```python
total_events = sum(day.get('sensor_events', 0)
                   for day in usage['usage'].values())
total_gb = sum(day.get('output_bytes_tx', 0)
               for day in usage['usage'].values()) / (1024**3)
```

### Report Quality Tips

1. **Always verify field names** - Use sample data inspection before full processing
2. **Handle mixed data types** - Platform, timestamps, IDs can have multiple formats
3. **Provide context** - Include hostname samples, rule namespaces, categories
4. **Normalize timestamps** - Check magnitude before datetime conversion
5. **Count generators properly** - Iterate and count, don't use len()
6. **Group related data** - Extension sensors, rule families, detection categories
7. **Use descriptive platform names** - Apply two-pass pattern analysis for numeric platforms
8. **Test with sample data first** - Run on small datasets before full production reports
9. **Filter date ranges properly** - Usage stats contain ~90 days, filter to your desired period
10. **Handle missing data gracefully** - Use `.get()` with defaults for all dict access

### Dynamic Branding Support

The skill includes a branding utility (`utils/branding.py`) that automatically styles reports:

**Features**:
- **Default**: LimaCharlie branding (purple gradient, Syne/Rubik fonts)
- **Auto-detect business domains**: Extracts colors/fonts from company websites
- **Generic email fallback**: Uses LC branding for gmail.com, hotmail.com, etc.

**Usage**:
```python
from utils.branding import get_brand_for_user, generate_css_from_brand

# Auto-detect branding from user email
brand = get_brand_for_user('user@company.com')

# Generate CSS variables
css = generate_css_from_brand(brand)
```

**Example Output**:
- `user@gmail.com` → LimaCharlie branding (purple gradient)
- `user@anthropic.com` → Anthropic colors (#d97757 primary)
- `user@microsoft.com` → Microsoft colors (extracted from microsoft.com)

**Integration**: Can be added to report templates to automatically match company branding

## Updates and Maintenance

This skill should be updated when:
- New data sources become available
- API changes affect access methods
- New report templates are requested
- Organization configuration changes significantly

**Recent Updates**:
- 2025-11-12: Fixed sensor health report - use `alive` field instead of `last_seen` for offline duration
- 2025-11-12: Sensor health report template completed and tested (532 stale sensors detected!)
- 2025-11-12: Added stale sensor detection with three severity levels (>24h, >7d, >30d)
- 2025-11-12: Implemented tag-based sensor grouping and analysis
- 2025-11-12: Added version distribution tracking for compliance
- 2025-11-12: Multi-tenant billing report template completed and tested
- 2025-11-12: Added `Manager.userAccessibleOrgs()` support for cross-tenant reporting
- 2025-11-12: Implemented cost estimation formulas with transparent breakdown
- 2025-11-12: Added two-pass platform naming for human-readable sensor categories
- 2025-11-12: Fixed detection rule name extraction (use `source_rule` field)
- 2025-11-12: Added dynamic branding utility for company-specific styling
- 2025-11-12: Comprehensive MSSP report template completed and tested

Last updated: 2025-11-12

## Support

For questions or issues with this skill:
1. Review the data catalog for available data
2. Check the LimaCharlie documentation
3. Test data access methods with small queries
4. Verify authentication and permissions
5. Consult example templates for guidance
