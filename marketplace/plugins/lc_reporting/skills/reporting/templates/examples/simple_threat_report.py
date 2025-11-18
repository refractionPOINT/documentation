#!/usr/bin/env python3
"""
Simple Threat Report - Example Custom Report
Demonstrates how easy it is to create reports with the framework

This report focuses on high-severity detections in the last 48 hours
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_report import BaseReport
from utils.data_collectors import collect_org_info, collect_detections, collect_sensors
from utils.report_helpers import parse_time_range, aggregate_by_field, aggregate_by_timeline


class SimpleThreatReport(BaseReport):
    """Simple threat report focusing on high-severity detections"""

    def get_template_name(self):
        # Reuse existing security_detections template
        return 'security_detections.j2'

    def get_report_type(self):
        return 'Simple Threat Report'

    def collect_data(self):
        """Collect threat data - only ~30 lines of code!"""

        # Parse time range (default: 48 hours)
        hours_back = self.params.get('hours_back', 48)
        min_severity = self.params.get('min_severity', 3)

        start_time, end_time = parse_time_range(hours_back=hours_back)

        print(f"Analyzing threats from last {hours_back} hours...")
        print(f"Minimum severity: {min_severity} (high+)")

        # Collect organization info
        org_info = collect_org_info(self.oid)

        # Collect all detections
        all_detections = collect_detections(self.oid, start_time, end_time)

        # Filter to high-severity only
        high_severity = [
            d for d in all_detections['list']
            if d['severity'] >= min_severity
        ]

        print(f"  Found {len(high_severity)}/{all_detections['total']} high-severity detections")

        # Find sensors with most high-severity detections
        sensor_threat_counts = aggregate_by_field(
            high_severity,
            'sensor_id',
            count=True,
            top_n=10
        )

        # Analyze threat categories
        threat_categories = aggregate_by_field(
            high_severity,
            'category',
            count=True,
            top_n=10
        )

        # Build report data
        data = {
            'org_info': org_info,
            'detection_summary': {
                'total': len(high_severity),
                'list': high_severity[:100],  # Top 100
                'by_category': threat_categories,
                'timeline': aggregate_by_timeline(high_severity),
                'severity_threshold': min_severity
            },
            'top_threatened_sensors': sensor_threat_counts,
            'time_range': {
                'hours': hours_back,
                'start': start_time,
                'end': end_time
            }
        }

        return data


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python simple_threat_report.py <OID> [hours_back] [format]")
        print("Example: python simple_threat_report.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 48 html")
        print("")
        print("Parameters:")
        print("  OID         : Organization ID (required)")
        print("  hours_back  : Hours to look back (default: 48)")
        print("  format      : html, markdown, or json (default: html)")
        sys.exit(1)

    oid = sys.argv[1]
    hours_back = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'html'

    # Create and generate report
    report = SimpleThreatReport(
        oid=oid,
        output_format=output_format,
        hours_back=hours_back,
        min_severity=3
    )

    # Save to file
    filepath = report.save()

    print(f"\\nReport type: {report.get_report_type()}")
    print(f"Format: {output_format}")
    print(f"Time range: {hours_back} hours")
