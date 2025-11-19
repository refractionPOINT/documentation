#!/usr/bin/env python3
"""
Executive Summary Report Template
Generates a high-level organizational overview for management
"""

from limacharlie import Manager
from collections import defaultdict
from utils.base_report import BaseReport
from utils.report_helpers import parse_time_range, progress_reporter
from utils.constants import DEFAULT_DETECTION_LIMIT, PROGRESS_REPORT_INTERVAL
from utils.cli import simple_cli


class ExecutiveSummary(BaseReport):
    """
    Executive summary report for organizational overview.

    Provides high-level metrics for management including:
    - Sensor health and platform distribution
    - Detection trends and categories
    - Usage statistics (most recent day)
    - Configuration summary (rules, outputs, users)
    """

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'executive_summary.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'Executive Summary Report'

    def collect_data(self):
        """
        Collect executive summary data.

        Returns:
            Dictionary with org_info, sensor_stats, detection_summary,
            usage_summary, and config_summary
        """
        m = Manager(oid=self.oid)

        # Calculate time range
        start, end = parse_time_range(
            time_range_days=self.time_range_days,
            hours_back=self.hours_back
        )

        print(f"Generating executive summary for {self.time_range_days or self.hours_back or 24} {'days' if self.time_range_days else 'hours'}...")

        # Collect data
        data = {}

        # 1. Organization metadata
        print("Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. Sensor statistics
        print("Collecting sensor statistics...")
        data['sensor_stats'] = self._collect_sensor_stats(m)

        # 3. Detection summary
        print("Collecting detection data...")
        data['detection_summary'] = self._collect_detection_summary(m, start, end)

        # 4. Usage summary (last full day)
        print("Collecting usage statistics...")
        data['usage_summary'] = self._collect_usage_stats(m)

        # 5. Configuration summary
        print("Collecting configuration data...")
        data['config_summary'] = self._collect_config_summary(m)

        # Add time range metadata
        data['report_metadata'] = {
            'time_range_days': self.time_range_days or (self.hours_back // 24 if self.hours_back else 1),
            'start_date': self._format_timestamp(start, 'date'),
            'end_date': self._format_timestamp(end, 'date')
        }

        return data

    def _collect_sensor_stats(self, manager):
        """Collect sensor statistics with platform breakdown."""
        all_sensors = list(manager.sensors())
        online_sensors = manager.getAllOnlineSensors()

        sensor_stats = {
            'total': len(all_sensors),
            'online': len(online_sensors),
            'offline': len(all_sensors) - len(online_sensors),
            'online_percentage': round(
                (len(online_sensors) / len(all_sensors) * 100) if all_sensors else 0, 1
            )
        }

        # Platform breakdown with progress reporting
        platforms = defaultdict(int)
        print(f"  Analyzing {len(all_sensors)} sensors...")

        with progress_reporter(len(all_sensors), '  Analyzing sensors') as progress:
            for i, sensor in enumerate(all_sensors):
                progress.update(i + 1)
                try:
                    info = sensor.getInfo()
                    platform = info.get('plat', info.get('ext_plat', 'unknown'))
                    platforms[str(platform)] += 1
                except Exception:
                    platforms['unknown'] += 1

        sensor_stats['by_platform'] = dict(platforms)
        return sensor_stats

    def _collect_detection_summary(self, manager, start, end):
        """Collect detection summary with aggregations."""
        try:
            detections = manager.getHistoricDetections(
                start=start,
                end=end,
                limit=DEFAULT_DETECTION_LIMIT
            )

            detection_categories = defaultdict(int)
            detection_by_day = defaultdict(int)
            detection_count = 0

            for det in detections:
                detection_count += 1

                # Count by category
                cat = det.get('cat', 'unknown')
                detection_categories[cat] += 1

                # Count by day
                ts = det.get('timestamp', det.get('ts', 0))
                if ts:
                    try:
                        # Convert milliseconds to seconds if needed
                        if ts > 10000000000:
                            ts = ts / 1000
                        day = self._format_timestamp(ts, 'date')
                        detection_by_day[day] += 1
                    except (ValueError, OSError):
                        pass

            # Calculate time range in days for average
            time_range_days = self.time_range_days or (self.hours_back / 24 if self.hours_back else 1)

            return {
                'total': detection_count,
                'by_category': dict(detection_categories),
                'by_day': dict(sorted(detection_by_day.items())),
                'avg_per_day': round(detection_count / time_range_days, 1) if time_range_days > 0 else 0
            }

        except Exception as e:
            print(f"  Error collecting detections: {e}")
            return {
                'error': str(e),
                'total': 0,
                'by_category': {},
                'by_day': {},
                'avg_per_day': 0
            }

    def _collect_usage_stats(self, manager):
        """Collect usage statistics for most recent day."""
        try:
            usage = manager.getUsageStats()
            if 'usage' in usage:
                # Get most recent day's stats
                latest_date = max(usage['usage'].keys())
                latest_stats = usage['usage'][latest_date]

                return {
                    'date': latest_date,
                    'sensor_events': latest_stats.get('sensor_events', 0),
                    'detections_generated': latest_stats.get('replay_num_evals', 0),
                    'output_bytes_gb': round(latest_stats.get('output_bytes_tx', 0) / (1024**3), 2),
                    'peak_sensors': latest_stats.get('sensor_watermark', 0)
                }
        except Exception as e:
            return {'error': str(e)}

    def _collect_config_summary(self, manager):
        """Collect configuration summary."""
        return {
            'dr_rules': len(manager.rules()),
            'outputs': len(manager.outputs()),
            'tags': len(manager.getAllTags()),
            'users': len(manager.getUsers()),
            'api_keys': len(manager.getApiKeys())
        }


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        ExecutiveSummary,
        description='Generate an executive summary report for a LimaCharlie organization',
        default_days=7
    )
