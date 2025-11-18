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

## Available Collectors

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

## Available Helpers

```python
from utils.report_helpers import (
    parse_time_range,          # Time range parsing
    format_timestamp,          # Timestamp formatting
    aggregate_by_category,     # Category aggregation
    aggregate_by_timeline,     # Timeline aggregation
    filter_items,              # Item filtering
    calculate_duration         # Duration calculation
)
```

## Available Formatters

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

1. **incident_investigation_v2.py** - Complete refactored report (228 lines)
2. **CUSTOM_REPORTS_GUIDE.md** - Full guide with 3 patterns
3. **FRAMEWORK_SUMMARY.md** - Framework overview

## Run Examples

```bash
# Incident investigation (refactored version)
python3 incident_investigation_v2.py YOUR_OID 48 html

# Parameters:
#   YOUR_OID    - Organization ID
#   48          - Hours back (optional, default 24)
#   html        - Format: html, markdown, or json (optional)
```

## Next Steps

1. Copy `incident_investigation_v2.py` as template
2. Modify `collect_data()` method for your needs
3. Optionally create custom Jinja2 template
4. Run and iterate!

## Need Help?

- **Full guide**: See `CUSTOM_REPORTS_GUIDE.md`
- **Framework details**: See `FRAMEWORK_SUMMARY.md`
- **Existing reports**: Study other `.py` files in this directory
