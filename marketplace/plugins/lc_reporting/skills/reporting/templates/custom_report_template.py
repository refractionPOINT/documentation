"""
Custom Report Template

This is a reference example showing best practices for creating custom reports
using the LimaCharlie reporting framework.

Copy this file and modify the following:
1. Class name and docstring
2. get_template_name() - return your Jinja2 template filename
3. get_report_type() - return your report name
4. collect_data() - implement your data collection logic

Usage:
    python3 custom_report_template.py <OID> [--hours 24] [--format html]
"""

from utils.base_report import BaseReport
from utils.data_collectors import (
    collect_org_info,
    collect_detections,
    collect_sensors
)
from utils.report_helpers import (
    parse_time_range,
    aggregate_by_category,
    calculate_severity_distribution
)
from utils.cli import simple_cli


class CustomReport(BaseReport):
    """
    Example custom report demonstrating the framework pattern.

    This report collects:
    - Organization information
    - Detection summary with aggregations
    - Sensor inventory by platform

    Customize this to build your own reports!
    """

    def get_template_name(self):
        """
        Return the name of the Jinja2 template to use.

        Options:
        - Create your own template in templates/jinja2/html/
        - Reuse an existing template:
          - 'security_detections.j2'
          - 'sensor_health.j2'
          - 'config_audit.j2'
          - 'executive_summary.j2'
        """
        return 'security_detections.j2'  # Using existing template as example

    def get_report_type(self):
        """Return the human-readable report type name."""
        return 'Custom Example Report'

    def collect_data(self):
        """
        Collect and process all data needed for the report.

        This is the main method you'll customize for your report.
        Use utilities from utils/ to:
        - Collect data: data_collectors.py
        - Process time ranges: report_helpers.parse_time_range()
        - Aggregate data: report_helpers.aggregate_by_*()
        - Format data: report_helpers.format_timestamp(), etc.

        Returns:
            Dictionary of data to pass to the template
        """
        # 1. Parse time range from constructor arguments
        start, end = parse_time_range(
            time_range_days=self.time_range_days,
            hours_back=self.hours_back
        )

        # 2. Collect raw data using utilities
        org_info = collect_org_info(self.oid)

        detection_summary = collect_detections(
            self.oid,
            start,
            end,
            limit=5000  # Use constants.DEFAULT_DETECTION_LIMIT in production
        )

        sensor_summary = collect_sensors(self.oid)

        # 3. Process and aggregate data
        # Example: Get high-severity detections only
        high_severity_detections = [
            d for d in detection_summary['list']
            if d.get('severity', 0) >= 3
        ]

        # Example: Category aggregation
        detections_by_category = aggregate_by_category(
            detection_summary['list'],
            category_key='cat'
        )

        # Example: Severity distribution
        severity_dist = calculate_severity_distribution(
            detection_summary['list']
        )

        # 4. Build data structure for template
        return {
            'org_info': org_info,
            'time_range': {
                'start': start,
                'end': end,
                'start_date': self._format_timestamp(start),
                'end_date': self._format_timestamp(end)
            },
            'detection_summary': {
                'total': detection_summary['total'],
                'list': detection_summary['list'][:100],  # Limit for display
                'by_category': detections_by_category,
                'severity_distribution': severity_dist,
                'high_severity_count': len(high_severity_detections)
            },
            'sensor_summary': sensor_summary
        }


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        CustomReport,
        description='Generate a custom example report',
        default_hours=24
    )
