# Custom Report Creation Guide

This guide shows you how to create custom LimaCharlie reports using the reporting utilities framework.

## Overview

The reporting framework provides reusable utilities for:
- **Data Collection**: Pre-built collectors for detections, sensors, rules, org info
- **Data Processing**: Time range parsing, aggregation, filtering
- **Rendering**: HTML (Jinja2), Markdown, and JSON output formats
- **Standardization**: Base classes for consistent report structure

## Quick Start: Three Ways to Build Reports

### Method 1: Simple Function-Based Report

For quick, one-off reports:

```python
from utils.data_collectors import collect_org_info, collect_detections
from utils.report_helpers import parse_time_range
from utils.formatters import render_json_report

def my_simple_report(oid, hours_back=24):
    """Quick custom report"""

    # Collect data
    data = {}
    data['org_info'] = collect_org_info(oid)

    start_time, end_time = parse_time_range(hours_back=hours_back)
    data['detections'] = collect_detections(oid, start_time, end_time)

    # Render as JSON
    return render_json_report(data)
```

### Method 2: Using SimpleReport Builder

For reports with templates:

```python
from utils.base_report import SimpleReport

def collect_my_data(oid, **params):
    """Data collection function"""
    from utils.data_collectors import collect_org_info, collect_sensors

    data = {}
    data['org_info'] = collect_org_info(oid)
    data['sensors'] = collect_sensors(oid)
    return data

# Create report
report = SimpleReport(
    oid='my-org-id',
    report_type='My Custom Report',
    data_collector_func=collect_my_data,
    template_name='my_template.j2',
    output_format='html'
)

# Generate and save
report.save()
```

### Method 3: Subclassing BaseReport (Recommended)

For production reports:

```python
from utils.base_report import BaseReport
from utils.data_collectors import collect_detections, collect_sensors
from utils.report_helpers import parse_time_range

class MyCustomReport(BaseReport):

    def get_template_name(self):
        return 'my_custom_report.j2'

    def get_report_type(self):
        return 'Custom Security Analysis'

    def collect_data(self):
        """Collect all needed data"""
        data = {}

        # Parse parameters
        hours_back = self.params.get('hours_back', 24)
        start_time, end_time = parse_time_range(hours_back=hours_back)

        # Collect data
        data['detections'] = collect_detections(
            self.oid, start_time, end_time
        )
        data['sensors'] = collect_sensors(self.oid)

        # Add custom analysis
        data['analysis'] = self._custom_analysis(data)

        return data

    def _custom_analysis(self, data):
        """Custom analysis logic"""
        return {
            'high_risk_count': sum(
                1 for d in data['detections']['list']
                if d['severity'] >= 3
            )
        }

# Usage
report = MyCustomReport(oid='my-org-id', hours_back=48)
report.save()
```

## Available Utilities

### Data Collectors (`utils/data_collectors.py`)

#### `collect_org_info(oid)`
Collects organization metadata.

**Returns:**
```python
{
    'oid': 'org-id',
    'name': 'Organization Name',
    'created': timestamp,
    'tier': 'enterprise',
    'raw': {...}  # Full org info
}
```

#### `collect_detections(oid, start_time, end_time, limit=5000, sensor_id=None, category=None)`
Collects historic detections with filtering and aggregation.

**Returns:**
```python
{
    'total': 1532,
    'list': [...],  # List of detection dicts
    'timeline': {'2025-11-17 08:00': 45, ...},
    'by_category': {'malware': 100, ...},
    'by_severity': {0: 50, 1: 100, ...},
    'affected_sensor_count': 12,
    'affected_sensors': ['sid1', 'sid2', ...],
    'hit_limit': False,
    'limit': 5000
}
```

#### `collect_sensors(oid, tags=None, platform=None)`
Collects sensor information with optional filtering.

**Returns:**
```python
{
    'total': 150,
    'list': [...],  # List of sensor dicts
    'by_platform': {'windows': 100, 'linux': 50},
    'online_count': 145,
    'offline_count': 5
}
```

#### `collect_sensor_info(oid, sensor_id)`
Detailed info for a specific sensor.

#### `collect_rules(oid, namespace=None, enabled_only=False)`
Collects D&R rules.

**Returns:**
```python
{
    'total': 250,
    'list': [...],
    'by_namespace': {'general': 100, 'managed': 150},
    'enabled_count': 240,
    'disabled_count': 10
}
```

#### `collect_ioc_matches(oid, iocs, detections_data)`
Search for IOCs in detection data.

### Report Helpers (`utils/report_helpers.py`)

#### `parse_time_range(time_range_days=None, start_time=None, end_time=None, hours_back=None)`
Parse time ranges from various input formats.

```python
# Various ways to specify time range
start, end = parse_time_range(hours_back=24)
start, end = parse_time_range(time_range_days=7)
start, end = parse_time_range(start_time=123456, end_time=789012)
```

#### `format_timestamp(ts, fmt='iso')`
Format timestamps in various formats.

```python
format_timestamp(ts, 'iso')       # 2025-11-17T14:30:00+00:00
format_timestamp(ts, 'datetime')  # 2025-11-17 14:30:00
format_timestamp(ts, 'date')      # 2025-11-17
```

#### `aggregate_by_category(items, category_key='cat', count=True)`
Aggregate items by category.

#### `aggregate_by_timeline(items, timestamp_key='ts', interval='hour')`
Aggregate items into time buckets.

#### `aggregate_by_field(items, field_key, count=True, top_n=None)`
Generic aggregation by any field.

#### `filter_items(items, filters)`
Filter items by multiple criteria.

#### `calculate_severity_distribution(items, severity_key='severity')`
Calculate severity distribution with percentages.

### Formatters (`utils/formatters.py`)

#### `render_html_report(data, template_name, template_dir=None)`
Render using Jinja2 template.

#### `render_markdown_report(data, title='Report')`
Auto-generate Markdown report.

#### `render_json_report(data, indent=2)`
Render as JSON.

#### `save_report(content, output_format='html', prefix='report', output_dir=None)`
Save report to file with timestamp.

#### `add_report_metadata(data, report_type='Generic Report')`
Add standard metadata to report data.

## Complete Example: Threat Hunter Report

Here's a complete example creating a custom threat hunting report:

```python
#!/usr/bin/env python3
"""
Threat Hunter Report - Custom report example
Focuses on high-severity detections and lateral movement indicators
"""

import sys
from utils.base_report import BaseReport
from utils.data_collectors import (
    collect_org_info,
    collect_detections,
    collect_sensors
)
from utils.report_helpers import (
    parse_time_range,
    filter_items,
    aggregate_by_field
)


class ThreatHunterReport(BaseReport):
    """Threat hunting focused report"""

    def get_template_name(self):
        # Use existing security_detections template or create custom
        return 'security_detections.j2'

    def get_report_type(self):
        return 'Threat Hunter Analysis'

    def collect_data(self):
        """Collect threat hunting data"""
        data = {}

        # Parameters
        hours_back = self.params.get('hours_back', 48)
        min_severity = self.params.get('min_severity', 3)  # High+ only

        # Time range
        start_time, end_time = parse_time_range(hours_back=hours_back)

        print(f"Hunting threats from last {hours_back} hours...")

        # 1. Org info
        data['org_info'] = collect_org_info(self.oid)

        # 2. All detections
        all_detections = collect_detections(
            self.oid, start_time, end_time, limit=5000
        )

        # 3. Filter high-severity only
        high_severity_detections = filter_items(
            all_detections['list'],
            {'severity': lambda s: s >= min_severity}
        )

        print(f"  Found {len(high_severity_detections)} high-severity detections")

        # 4. Analyze affected sensors
        affected_sensor_ids = set(d['sensor_id'] for d in high_severity_detections)

        # 5. Lateral movement detection
        # Sensors with multiple high-severity alerts
        sensors_by_detection_count = aggregate_by_field(
            high_severity_detections,
            'sensor_id',
            count=True
        )

        lateral_movement_suspects = {
            sid: count for sid, count in sensors_by_detection_count.items()
            if count >= 3  # 3+ high-severity detections
        }

        # 6. Build report data
        data['detection_summary'] = {
            'total': all_detections['total'],
            'high_severity': len(high_severity_detections),
            'by_category': aggregate_by_field(
                high_severity_detections, 'category', count=True
            ),
            'timeline': aggregate_by_timeline(
                high_severity_detections, interval='hour'
            )
        }

        data['lateral_movement'] = {
            'suspect_count': len(lateral_movement_suspects),
            'suspects': lateral_movement_suspects
        }

        data['affected_sensors'] = list(affected_sensor_ids)

        # 7. Recommendations
        data['recommendations'] = self._generate_recommendations(data)

        return data

    def _generate_recommendations(self, data):
        """Generate threat hunting recommendations"""
        recs = []

        if data['lateral_movement']['suspect_count'] > 0:
            recs.append({
                'priority': 'critical',
                'category': 'Lateral Movement',
                'recommendation': f"Investigate {data['lateral_movement']['suspect_count']} sensors with multiple high-severity alerts for lateral movement."
            })

        if data['detection_summary']['high_severity'] > 10:
            recs.append({
                'priority': 'high',
                'category': 'Investigation',
                'recommendation': 'High volume of critical detections. Prioritize investigation by affected sensor.'
            })

        return recs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python threat_hunter_report.py <OID> [hours_back]")
        sys.exit(1)

    oid = sys.argv[1]
    hours_back = int(sys.argv[2]) if len(sys.argv) > 2 else 48

    report = ThreatHunterReport(
        oid=oid,
        hours_back=hours_back,
        min_severity=3,
        output_format='html'
    )

    report.save()
```

## Creating Custom Jinja2 Templates

For HTML output, create a Jinja2 template in `jinja2/html/`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ report_metadata.report_type }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* Your custom styles */
    </style>
</head>
<body>
    <h1>{{ report_metadata.report_type }}</h1>

    <h2>Organization: {{ org_info.name }}</h2>

    <!-- Use your custom data -->
    <div class="stats">
        <p>Total Detections: {{ detection_summary.total }}</p>
    </div>

    <!-- Chart.js visualization -->
    <canvas id="myChart"></canvas>
    <script>
        {% set categories = (detection_summary.by_category.items()|sort(attribute='1', reverse=True)|list)[:10] %}
        new Chart(document.getElementById('myChart'), {
            type: 'bar',
            data: {
                labels: {{ categories|map(attribute='0')|list|tojson }},
                data: {{ categories|map(attribute='1')|list|tojson }}
            }
        });
    </script>
</body>
</html>
```

## Best Practices

1. **Always use data collectors** instead of calling SDK directly
2. **Parse time ranges** with `parse_time_range()` for consistency
3. **Add metadata** with `add_report_metadata()` before rendering
4. **Handle errors gracefully** - all collectors return error info on failure
5. **Use aggregation helpers** instead of manual loops
6. **Follow naming conventions**: `my_report_name.py` → `my_report_name.j2`

## Testing Your Report

```bash
# Test with JSON output first (fastest)
python my_custom_report.py <OID> --format=json

# Then Markdown
python my_custom_report.py <OID> --format=markdown

# Finally HTML (requires template)
python my_custom_report.py <OID> --format=html
```

## Common Patterns

### Pattern: Multi-Tenant Report

```python
from utils.base_report import SimpleReport

def collect_multi_tenant_data(oid, **params):
    # Collect data from multiple orgs
    all_orgs = params.get('orgs', [])
    data = {'orgs': []}

    for org_id in all_orgs:
        org_data = collect_org_info(org_id)
        # ... collect more data per org
        data['orgs'].append(org_data)

    return data
```

### Pattern: Compliance Report

```python
def collect_compliance_data(oid, **params):
    data = {}

    # Rules compliance
    rules = collect_rules(oid)
    data['rules_with_tags'] = filter_items(
        rules['list'],
        filters={'tags': lambda t: len(t) > 0}
    )

    # Sensor coverage
    sensors = collect_sensors(oid)
    data['coverage_percentage'] = (
        sensors['online_count'] / sensors['total'] * 100
    )

    return data
```

## Next Steps

1. Study existing reports: `incident_investigation_v2.py`, `security_detections.py`
2. Copy and modify an existing report for your use case
3. Create custom Jinja2 templates for unique visualizations
4. Share your custom reports with the community!
