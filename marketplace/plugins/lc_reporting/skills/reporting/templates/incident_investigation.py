#!/usr/bin/env python3
"""
Incident Investigation Report Template
Provides detailed forensic analysis for security incident investigation
"""

from limacharlie import Manager
from datetime import datetime, timezone
from collections import defaultdict
from utils.base_report import BaseReport
from utils.report_helpers import parse_time_range, calculate_duration
from utils.constants import INCIDENT_INVESTIGATION_LIMIT
from utils.cli import parse_common_args, execute_report


class IncidentInvestigationReport(BaseReport):
    """
    Incident investigation report for forensic analysis.

    Provides detailed investigation of:
    - Specific sensor activity (optional)
    - Detection timeline and patterns
    - IOC matching (optional)
    - Category-specific investigations
    - Affected sensors and scope
    """

    def __init__(self, oid, sensor_id=None, iocs=None, detection_category=None, **kwargs):
        """
        Initialize incident investigation report.

        Args:
            oid: Organization ID
            sensor_id: Specific sensor to investigate (optional)
            iocs: List of IOCs to search for (optional)
            detection_category: Specific category to focus on (optional)
            **kwargs: Additional arguments passed to BaseReport
        """
        super().__init__(oid, **kwargs)
        self.sensor_id = sensor_id
        self.iocs = iocs if iocs else []
        self.detection_category = detection_category

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'incident_investigation.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'Incident Investigation Report'

    def collect_data(self):
        """
        Collect incident investigation data.

        Returns:
            Dictionary with investigation scope, sensor info, detections, and IOC results
        """
        m = Manager(oid=self.oid)

        # Calculate time range
        start, end = parse_time_range(
            time_range_days=self.time_range_days,
            hours_back=self.hours_back
        )

        print("Generating incident investigation report...")
        print(f"  Time range: {self._format_timestamp(start)} to {self._format_timestamp(end)}")
        if self.sensor_id:
            print(f"  Focused on sensor: {self.sensor_id}")
        if self.detection_category:
            print(f"  Detection category: {self.detection_category}")

        data = {}

        # 1. Organization metadata
        print("Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. Investigation scope
        data['investigation_scope'] = {
            'sensor_id': self.sensor_id,
            'start_time': start,
            'end_time': end,
            'start_date': self._format_timestamp(start),
            'end_date': self._format_timestamp(end),
            'duration_hours': calculate_duration(start, end, 'hours'),
            'iocs': self.iocs,
            'detection_category': self.detection_category
        }

        # 3. Sensor information (if specific sensor provided)
        if self.sensor_id:
            print(f"Collecting sensor information for {self.sensor_id}...")
            data['sensor_info'] = self._collect_sensor_info(m)
        else:
            data['sensor_info'] = None

        # 4. Related Detections
        print("Collecting related detections...")
        data['detections'] = self._collect_detections(m, start, end)

        # 5. IOC Search (if IOCs provided)
        if self.iocs:
            print(f"Searching for {len(self.iocs)} IOCs...")
            data['ioc_results'] = self._search_iocs(data['detections']['list'])
        else:
            data['ioc_results'] = []

        # 6. Recommendations
        data['recommendations'] = self._generate_recommendations(data)

        return data

    def _collect_sensor_info(self, manager):
        """Collect information about specific sensor."""
        try:
            sensor = manager.sensor(self.sensor_id)
            sensor_info = sensor.getInfo()

            return {
                'sid': self.sensor_id,
                'hostname': sensor_info.get('hostname', 'unknown'),
                'platform': sensor_info.get('plat', 'unknown'),
                'ext_ip': sensor_info.get('ext_ip', 'unknown'),
                'int_ip': sensor_info.get('int_ip', 'unknown'),
                'tags': sensor.getTags(),
                'is_online': sensor.isOnline(),
                'last_seen': sensor_info.get('last_seen', 0)
            }
        except Exception as e:
            print(f"  Error collecting sensor info: {e}")
            return {
                'sid': self.sensor_id,
                'error': str(e)
            }

    def _collect_detections(self, manager, start, end):
        """Collect and analyze detections for investigation."""
        try:
            detections = manager.getHistoricDetections(
                start=start,
                end=end,
                limit=INCIDENT_INVESTIGATION_LIMIT
            )

            detection_list = []
            detection_timeline = defaultdict(int)
            detection_by_category = defaultdict(int)
            affected_sensors = set()

            for det in detections:
                # Filter by sensor if specified
                det_sensor_id = det.get('routing', {}).get('sid', 'unknown')
                if self.sensor_id and det_sensor_id != self.sensor_id:
                    continue

                # Filter by category if specified
                det_category = det.get('cat', 'unknown')
                if self.detection_category and det_category != self.detection_category:
                    continue

                # Process detection timestamp
                ts = det.get('ts', det.get('timestamp', 0))
                if ts:
                    try:
                        if ts > 10000000000:
                            ts = ts / 1000

                        # Timeline by hour
                        hour_key = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:00')
                        detection_timeline[hour_key] += 1
                    except (ValueError, OSError):
                        pass

                # Count by category
                detection_by_category[det_category] += 1

                # Track affected sensors
                affected_sensors.add(det_sensor_id)

                # Store detection details
                detection_list.append({
                    'timestamp': ts if ts else 0,
                    'timestamp_str': self._format_timestamp(ts) if ts else 'unknown',
                    'category': det_category,
                    'rule': det.get('source_rule', 'unknown'),
                    'sensor_id': det_sensor_id,
                    'severity': det.get('severity', 0),
                    'summary': det.get('summary', 'No summary available')
                })

            # Sort detections by timestamp (most recent first)
            detection_list.sort(key=lambda x: x['timestamp'], reverse=True)

            # Check if we hit the limit
            hit_limit = len(detection_list) >= INCIDENT_INVESTIGATION_LIMIT
            limit_warning = f"Showing first {INCIDENT_INVESTIGATION_LIMIT} detections (limit reached, more may exist)" if hit_limit else None

            return {
                'total': len(detection_list),
                'list': detection_list[:100],  # Limit to 100 most recent for display
                'timeline': dict(sorted(detection_timeline.items())),
                'by_category': dict(sorted(detection_by_category.items(), key=lambda x: x[1], reverse=True)),
                'affected_sensor_count': len(affected_sensors),
                'affected_sensors': list(affected_sensors),
                'limit_warning': limit_warning
            }
        except Exception as e:
            print(f"  Error collecting detections: {e}")
            return {
                'total': 0,
                'list': [],
                'timeline': {},
                'by_category': {},
                'affected_sensor_count': 0,
                'affected_sensors': [],
                'limit_warning': None
            }

    def _search_iocs(self, detection_list):
        """Search for IOCs in detection data."""
        ioc_results = []

        for ioc in self.iocs:
            try:
                # Search for IOC in detection summaries
                matches = []
                for det in detection_list:
                    if ioc.lower() in det['summary'].lower():
                        matches.append({
                            'detection': det,
                            'match_type': 'detection_summary'
                        })

                ioc_results.append({
                    'ioc': ioc,
                    'matches': len(matches),
                    'details': matches[:10]  # First 10 matches
                })
            except Exception as e:
                print(f"  Error searching for IOC {ioc}: {e}")
                ioc_results.append({
                    'ioc': ioc,
                    'matches': 0,
                    'details': [],
                    'error': str(e)
                })

        return ioc_results

    def _generate_recommendations(self, data):
        """Generate investigation recommendations based on findings."""
        recommendations = []

        # Check detection volume
        detection_count = data['detections']['total']
        if detection_count > 100:
            recommendations.append({
                'priority': 'high',
                'category': 'Detection Volume',
                'recommendation': f'{detection_count} detections found - review high-severity items first'
            })

        # Check for critical categories
        for category, count in data['detections']['by_category'].items():
            if any(crit in category.upper() for crit in ['EXFIL', 'RANSOMWARE', 'LATERAL']):
                recommendations.append({
                    'priority': 'critical',
                    'category': 'Critical Detection',
                    'recommendation': f'{count} {category} detections require immediate investigation'
                })

        # Check if multiple sensors affected
        sensor_count = data['detections']['affected_sensor_count']
        if sensor_count > 1:
            recommendations.append({
                'priority': 'medium',
                'category': 'Scope',
                'recommendation': f'{sensor_count} sensors affected - investigate for lateral movement'
            })

        # IOC match recommendations
        if data.get('ioc_results'):
            matches_found = sum(1 for ioc in data['ioc_results'] if ioc['matches'] > 0)
            if matches_found > 0:
                recommendations.append({
                    'priority': 'high',
                    'category': 'IOC Match',
                    'recommendation': f'{matches_found} IOCs matched - review context and containment actions'
                })

        return recommendations


# CLI Entry Point
if __name__ == '__main__':
    # Custom argument parsing for incident investigation specific options
    args = parse_common_args(
        description='Generate an incident investigation report for forensic analysis',
        default_hours=24,
        custom_args=[
            {'name': '--sensor', 'help': 'Specific sensor ID to investigate', 'type': str, 'default': None},
            {'name': '--category', 'help': 'Detection category to focus on', 'type': str, 'default': None},
            {'name': '--iocs', 'help': 'Comma-separated list of IOCs to search for', 'type': str, 'default': None}
        ]
    )

    # Parse IOCs if provided
    iocs = args.iocs.split(',') if hasattr(args, 'iocs') and args.iocs else None

    # Build custom parameters
    custom_params = {
        'sensor_id': args.sensor if hasattr(args, 'sensor') else None,
        'detection_category': args.category if hasattr(args, 'category') else None,
        'iocs': iocs
    }

    execute_report(IncidentInvestigationReport, args, custom_params)
