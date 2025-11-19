#!/usr/bin/env python3
"""
Security Detections Report Template
Provides comprehensive analysis of security detections and threat patterns
"""

from limacharlie import Manager
from datetime import datetime, timezone
from collections import defaultdict
from utils.base_report import BaseReport
from utils.report_helpers import parse_time_range
from utils.constants import (
    MAX_DETECTION_LIMIT,
    CRITICAL_CATEGORIES
)
from utils.cli import simple_cli


class SecurityDetectionsReport(BaseReport):
    """
    Comprehensive security detections analysis report.

    Provides detailed detection analytics including:
    - Detection volume and trends
    - Category and rule breakdowns
    - Top affected hostnames/sensors
    - Hourly distribution patterns
    - Critical detection counts
    """

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'security_detections.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'Security Detections Report'

    def collect_data(self):
        """
        Collect comprehensive detection data.

        Returns:
            Dictionary with org_info, detection_summary, and dr_rules
        """
        m = Manager(oid=self.oid)

        # Calculate time range
        start, end = parse_time_range(
            time_range_days=self.time_range_days,
            hours_back=self.hours_back
        )

        # Determine actual days for averages
        time_range_days = self.time_range_days or (self.hours_back / 24 if self.hours_back else 1)

        print(f"Generating security detections report for {time_range_days} days...")

        data = {}

        # 1. Organization metadata
        print("Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. Collect all detections
        print("Collecting detection data...")
        data['detection_summary'] = self._collect_detections(m, start, end, time_range_days)

        # 3. Get D&R Rules for context
        print("Collecting D&R rule information...")
        data['dr_rules'] = self._collect_rules(m)

        # Add metadata
        data['report_metadata'] = {
            'time_range_days': time_range_days,
            'start_date': self._format_timestamp(start, 'date'),
            'end_date': self._format_timestamp(end, 'date')
        }

        return data

    def _collect_detections(self, manager, start, end, time_range_days):
        """Collect and analyze all detection data."""
        try:
            detections = manager.getHistoricDetections(
                start=start,
                end=end,
                limit=MAX_DETECTION_LIMIT
            )

            # Initialize tracking structures
            detection_count = 0
            detection_by_category = defaultdict(int)
            detection_by_day = defaultdict(int)
            detection_by_hour = defaultdict(int)
            detection_by_rule = defaultdict(int)
            detection_by_sensor = defaultdict(int)
            detection_by_hostname = defaultdict(int)
            hourly_distribution = defaultdict(int)
            limit_reached = False

            print("  Processing detections...")
            for det in detections:
                detection_count += 1

                # Check if we hit the limit
                if detection_count >= MAX_DETECTION_LIMIT:
                    limit_reached = True

                # Count by category
                cat = det.get('cat', 'unknown')
                detection_by_category[cat] += 1

                # Count by day/hour for timeline
                ts = det.get('ts', det.get('timestamp', 0))
                if ts:
                    try:
                        # Convert milliseconds to seconds if needed
                        if ts > 10000000000:
                            ts = ts / 1000

                        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                        day = dt.strftime('%Y-%m-%d')
                        detection_by_day[day] += 1

                        # For 24-hour reports, track by hour
                        if time_range_days <= 1:
                            hour_label = dt.strftime('%Y-%m-%d %H:00')
                            detection_by_hour[hour_label] += 1

                        # Collect hourly distribution (0-23 for heatmap)
                        hourly_distribution[dt.hour] += 1
                    except (ValueError, OSError):
                        pass

                # Count by rule name
                rule_name = det.get('source_rule', 'unknown')
                if isinstance(rule_name, str):
                    detection_by_rule[rule_name] += 1

                # Count by sensor
                sensor_id = det.get('routing', {}).get('sid', 'unknown')
                detection_by_sensor[sensor_id] += 1

                # Count by hostname (clean up for readability)
                hostname = det.get('routing', {}).get('hostname', sensor_id)
                if hostname and hostname != 'unknown':
                    hostname = hostname.rstrip('.')
                    if '.internal' in hostname:
                        hostname = hostname.split('.')[0]
                detection_by_hostname[hostname] += 1

            print(f"  Processed {detection_count} detections")
            if limit_reached:
                print(f"  ⚠️  WARNING: Detection limit of {MAX_DETECTION_LIMIT} reached - results may be incomplete!")

            # Calculate detection velocity (day-over-day changes)
            sorted_days = sorted(detection_by_day.items())
            detection_velocity = []
            if len(sorted_days) >= 2:
                for i in range(1, len(sorted_days)):
                    prev_count = sorted_days[i-1][1]
                    curr_count = sorted_days[i][1]
                    change = curr_count - prev_count
                    pct_change = ((change / prev_count) * 100) if prev_count > 0 else 0
                    detection_velocity.append({
                        'day': sorted_days[i][0],
                        'count': curr_count,
                        'change': change,
                        'pct_change': round(pct_change, 1)
                    })

            # Get top items
            top_rules = sorted(detection_by_rule.items(), key=lambda x: x[1], reverse=True)[:10]
            top_sensors = sorted(detection_by_sensor.items(), key=lambda x: x[1], reverse=True)[:10]
            top_hostnames = sorted(detection_by_hostname.items(), key=lambda x: x[1], reverse=True)[:10]

            # Count critical category detections
            critical_detections_count = sum(
                count for cat, count in detection_by_category.items()
                if any(crit.lower() in cat.lower() for crit in CRITICAL_CATEGORIES)
            )

            return {
                'total': detection_count,
                'by_category': dict(sorted(detection_by_category.items(), key=lambda x: x[1], reverse=True)),
                'by_day': dict(sorted(detection_by_day.items())),
                'by_hour': dict(sorted(detection_by_hour.items())) if time_range_days <= 1 else {},
                'is_24h_or_less': time_range_days <= 1,
                'avg_per_day': round(detection_count / time_range_days, 1) if time_range_days > 0 else 0,
                'top_rules': [{'rule': rule, 'count': count} for rule, count in top_rules],
                'top_sensors': [{'sensor_id': sid, 'count': count} for sid, count in top_sensors],
                'top_hostnames': [{'hostname': hostname, 'count': count} for hostname, count in top_hostnames],
                'critical_detections_count': critical_detections_count,
                'detection_velocity': detection_velocity[-7:] if detection_velocity else [],
                'hourly_distribution': dict(sorted(hourly_distribution.items())),
                'limit_reached': limit_reached,
                'detection_limit': MAX_DETECTION_LIMIT
            }

        except Exception as e:
            print(f"  Error collecting detections: {e}")
            return {
                'error': str(e),
                'total': 0,
                'by_category': {},
                'by_day': {},
                'by_hour': {},
                'is_24h_or_less': False,
                'avg_per_day': 0,
                'top_rules': [],
                'top_sensors': [],
                'top_hostnames': [],
                'critical_detections_count': 0,
                'detection_velocity': [],
                'hourly_distribution': {},
                'limit_reached': False,
                'detection_limit': 0
            }

    def _collect_rules(self, manager):
        """Collect D&R rules information."""
        try:
            rules = list(manager.rules())
            return {
                'total': len(rules),
                'rules': rules
            }
        except Exception as e:
            print(f"  Error collecting rules: {e}")
            return {'total': 0, 'rules': []}


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        SecurityDetectionsReport,
        description='Generate a comprehensive security detections report',
        default_days=7
    )
