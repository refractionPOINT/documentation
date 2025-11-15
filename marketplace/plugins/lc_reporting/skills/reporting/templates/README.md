# Report Templates

This directory contains pre-built report templates for common LimaCharlie reporting scenarios.

## Available Templates

### executive_summary.py ✅
**Status**: Complete
**Purpose**: High-level organizational overview for management
**Usage**:
```bash
python executive_summary.py <OID> [days] [format]
# Example:
python executive_summary.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 html
```
**Outputs**: HTML, Markdown, or JSON report

### Coming Soon

The following templates will be added as needed:

- **sensor_health.py** - Detailed sensor status and health metrics
- **security_detections.py** - Security alerts and detection analysis
- **usage_billing.py** - Usage statistics and billing breakdown
- **config_audit.py** - Configuration audit and documentation
- **incident_investigation.py** - Incident investigation workflow
- **mitre_coverage.py** - MITRE ATT&CK coverage analysis

## Creating Custom Templates

To create a new template:

1. Copy `executive_summary.py` as a starting point
2. Modify the data collection section for your needs
3. Reference `../data-catalog.yaml` for available data sources
4. Implement your formatting functions
5. Test with your organization
6. Document usage in this README

## Template Structure

All templates should follow this structure:

```python
#!/usr/bin/env python3
"""
Template Name
Brief description
"""

from limacharlie import Manager
import time

def generate_report(oid, **kwargs):
    """
    Generate the report

    Args:
        oid: Organization ID
        **kwargs: Template-specific parameters

    Returns:
        Formatted report string
    """
    # 1. Initialize Manager
    m = Manager(oid=oid)

    # 2. Collect data
    data = {}

    # 3. Process data
    # ... processing logic ...

    # 4. Format output
    return format_output(data)

def format_output(data):
    """Format data as report"""
    # Formatting logic
    pass

if __name__ == '__main__':
    # CLI interface
    pass
```

## Best Practices

1. **Error Handling**: Wrap data collection in try/except blocks
2. **Progress Indicators**: Print progress for long-running operations
3. **Flexible Output**: Support multiple output formats (HTML, MD, JSON)
4. **CLI Interface**: Make templates runnable from command line
5. **Documentation**: Include docstrings and usage examples
6. **Validation**: Check authentication before starting
7. **Metadata**: Include generation time and parameters in reports
