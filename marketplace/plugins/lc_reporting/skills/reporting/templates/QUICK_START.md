# Quick Start: Custom LimaCharlie Reports

## 30-Second Start

```python
from utils.base_report import BaseReport
from utils.data_collectors import collect_detections, collect_org_info
from utils.report_helpers import parse_time_range

class MyReport(BaseReport):
    def get_template_name(self):
        return 'security_detections.j2'  # Reuse existing template

    def get_report_type(self):
        return 'My Custom Report'

    def collect_data(self):
        start, end = parse_time_range(hours_back=24)
        return {
            'org_info': collect_org_info(self.oid),
            'detection_summary': collect_detections(self.oid, start, end)
        }

# Generate report
MyReport(oid='your-org-id').save()
```

## Available Utilities

### Constants
```python
from utils.constants import (
    DEFAULT_DETECTION_LIMIT,   # 5000
    MAX_DETECTION_LIMIT,       # 50000
    INCIDENT_INVESTIGATION_LIMIT,  # 5000
    PROGRESS_REPORT_INTERVAL,  # 100
    SEVERITY_MAP,              # Severity number to name mapping
    CRITICAL_CATEGORIES,       # High-risk detection categories
    MITRE_CTI_URL,            # MITRE ATT&CK data source
    MAX_TAG_DISPLAY           # 30
)
```

### CLI Helpers
```python
from utils.cli import (
    simple_cli,               # One-liner CLI setup
    parse_common_args,        # Standard argument parsing
    execute_report            # Execute report with error handling
)
```

### Data Collectors
```python
from utils.data_collectors import (
    collect_org_info,          # Organization metadata
    collect_detections,        # Detections with aggregations
    collect_sensors,           # Sensor inventory
    collect_sensor_info,       # Single sensor details
    collect_rules,             # D&R rules
    collect_ioc_matches        # IOC search
)
```

### Report Helpers
```python
from utils.report_helpers import (
    parse_time_range,          # Time range parsing
    format_timestamp,          # Timestamp formatting
    aggregate_by_category,     # Category aggregation
    aggregate_by_timeline,     # Timeline aggregation
    filter_items,              # Item filtering
    calculate_duration,        # Duration calculation
    progress_reporter          # Progress reporting context manager
)
```

### Formatters
```python
from utils.formatters import (
    render_html_report,        # Jinja2 HTML rendering
    render_markdown_report,    # Auto Markdown
    render_json_report,        # JSON export
    save_report                # Save to file
)
```

## Common Patterns

### Pattern: High-Severity Detections Only

```python
detections = collect_detections(oid, start, end)
high_severity = [d for d in detections['list'] if d['severity'] >= 3]
```

### Pattern: Filter by Platform

```python
sensors = collect_sensors(oid, platform='windows')
```

### Pattern: Multi-Format Output

```python
# In your report class
def generate(self):
    data = self.collect_data()

    if self.output_format == 'json':
        return render_json_report(data)
    elif self.output_format == 'markdown':
        return render_markdown_report(data)
    else:
        return render_html_report(data, self.get_template_name())
```

### Pattern: Custom Time Range

```python
# Last 7 days
start, end = parse_time_range(time_range_days=7)

# Last 48 hours
start, end = parse_time_range(hours_back=48)

# Specific range
start, end = parse_time_range(start_time=123456, end_time=789012)
```

## Examples to Study

1. **custom_report_template.py** - Reference example showing best practices (120 lines)
2. **security_detections.py** - Comprehensive detection analysis (241 lines)
3. **executive_summary.py** - High-level organizational overview (204 lines)
4. **CUSTOM_REPORTS_GUIDE.md** - Full guide with patterns and examples

## Run Examples

```bash
# Security detections report
python3 security_detections.py YOUR_OID --days 7 --format html

# Executive summary
python3 executive_summary.py YOUR_OID --days 30 --format html

# Incident investigation with custom parameters
python3 incident_investigation.py YOUR_OID --hours 48 --sensor SENSOR_ID --category EXFIL

# MITRE ATT&CK coverage
python3 mitre_coverage.py YOUR_OID

# Configuration audit
python3 config_audit.py YOUR_OID

# Sensor health report
python3 sensor_health_report.py YOUR_OID
```

## Next Steps

1. Copy `custom_report_template.py` as starting point
2. Modify `collect_data()` method for your needs
3. Optionally create custom Jinja2 template in jinja2/html/
4. Use `simple_cli()` for instant CLI support
5. Run and iterate!

## Need Help?

- **Full guide**: See `CUSTOM_REPORTS_GUIDE.md`
- **Framework details**: See `FRAMEWORK_SUMMARY.md`
- **Existing reports**: Study other `.py` files in this directory
