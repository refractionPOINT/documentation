# Utility Functions

This directory will contain reusable utility functions for report generation.

## Planned Utilities

### report_helpers.py
- `ReportGenerator` class - Main report generation interface
- Helper functions for common data collection patterns
- Caching mechanisms for frequently accessed data

### data_collectors.py
- Standardized data collection functions
- Error handling wrappers
- Retry logic for API calls

### formatters.py
- HTML formatting utilities
- Markdown formatting utilities
- JSON/CSV export functions
- Chart/visualization helpers

### visualizations.py
- Chart generation functions
- Graph utilities
- Data visualization helpers

## Usage

```python
from utils.report_helpers import ReportGenerator

rg = ReportGenerator(oid='YOUR_OID')
data = rg.get_org_summary()
report = rg.format_as_html(data)
```

## Note

These utilities will be built out as templates require them. For now, templates contain their own utility functions. As patterns emerge, common code will be refactored into these modules.
