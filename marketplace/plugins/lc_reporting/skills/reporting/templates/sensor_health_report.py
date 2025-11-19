#!/usr/bin/env python3
"""
Sensor Health Report Template
Generates comprehensive operational health report for LimaCharlie sensors
"""

from limacharlie import Manager
import time
from datetime import datetime, timezone
from collections import defaultdict, Counter
from utils.base_report import BaseReport
from utils.report_helpers import progress_reporter
from utils.cli import simple_cli


class SensorHealthReport(BaseReport):
    """
    Sensor health and operational status report.

    Provides comprehensive sensor analysis including:
    - Online/offline status and counts
    - Platform distribution
    - Tag coverage and usage
    - Sensor version distribution
    - Offline duration analysis
    - Long-offline sensor identification
    """

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'sensor_health.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'Sensor Health Report'

    def collect_data(self):
        """
        Collect sensor health and status data.

        Returns:
            Dictionary with sensor stats, platform distribution, tags, and versions
        """
        print("Generating sensor health report...")

        m = Manager(oid=self.oid)

        data = {}

        # 1. Organization metadata
        print("\n[1/5] Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. Collect all sensor data
        print("[2/5] Collecting sensor data...")
        sensor_data, online_sids = self._collect_all_sensors(m)

        # 3. Calculate sensor statistics
        print("[3/5] Calculating sensor statistics...")
        data['sensor_stats'] = self._calculate_stats(sensor_data, online_sids)

        # 4. Platform distribution
        print("[4/5] Analyzing platform distribution...")
        data['platform_stats'] = self._analyze_platforms(sensor_data)

        # 5. Tag analysis
        print("[5/5] Analyzing tag coverage...")
        data['tag_stats'] = self._analyze_tags(sensor_data)

        # 6. Version distribution
        data['version_stats'] = self._analyze_versions(sensor_data)

        return data

    def _collect_all_sensors(self, manager):
        """Collect all sensor information."""
        all_sensors = list(manager.sensors())
        online_sensors = manager.getAllOnlineSensors()
        online_sids = set(online_sensors) if isinstance(online_sensors, list) else set()

        sensor_data = []
        current_time = int(time.time())

        with progress_reporter(len(all_sensors), '  Processing sensors') as progress:
            for i, sensor in enumerate(all_sensors):
                progress.update(i + 1)

                try:
                    info = sensor.getInfo()
                    platform_raw = info.get('plat', info.get('ext_plat', 'unknown'))
                    hostname = info.get('hostname', 'N/A')
                    is_online = sensor.sid in online_sids

                    # Calculate offline duration
                    offline_hours, last_seen_str = self._calculate_offline_duration(
                        is_online, info, current_time
                    )

                    # Extract version
                    agent_version = info.get('sensor_seed_key', 'unknown')

                    # Collect tags
                    tags = info.get('tags', [])

                    sensor_data.append({
                        'sid': sensor.sid,
                        'hostname': hostname,
                        'platform_raw': platform_raw,
                        'online': is_online,
                        'offline_hours': offline_hours,
                        'last_seen_str': last_seen_str,
                        'tags': tags,
                        'version': agent_version
                    })
                except Exception as e:
                    print(f"  Error processing sensor {i}: {e}")

        print(f"  Processed {len(sensor_data)} sensors")
        return sensor_data, online_sids

    def _calculate_offline_duration(self, is_online, info, current_time):
        """Calculate how long a sensor has been offline."""
        if is_online:
            return 0, 'Online'

        offline_hours = 0
        last_seen_str = 'Never'

        # Try alive field first
        alive_str = info.get('alive', '')
        if alive_str:
            try:
                alive_dt = datetime.strptime(alive_str, '%Y-%m-%d %H:%M:%S')
                alive_dt = alive_dt.replace(tzinfo=timezone.utc)
                offline_hours = (current_time - alive_dt.timestamp()) / 3600
                last_seen_str = alive_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                return offline_hours, last_seen_str
            except:
                pass

        # Fallback to last_seen
        last_seen = info.get('last_seen', 0)
        if last_seen > 0:
            if last_seen > 10000000000:
                last_seen = last_seen / 1000
            offline_hours = (current_time - last_seen) / 3600
            last_seen_str = datetime.fromtimestamp(last_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        return offline_hours, last_seen_str

    def _calculate_stats(self, sensor_data, online_sids):
        """Calculate overall sensor statistics."""
        total = len(sensor_data)
        online = len(online_sids)
        offline = total - online

        # Find sensors offline > 24 hours
        long_offline = [
            s for s in sensor_data
            if not s['online'] and s['offline_hours'] > 24
        ]

        # Find sensors offline > 7 days
        very_long_offline = [
            s for s in sensor_data
            if not s['online'] and s['offline_hours'] > 168  # 7 days
        ]

        return {
            'total': total,
            'online': online,
            'offline': offline,
            'online_percentage': round((online / total * 100) if total > 0 else 0, 1),
            'offline_24h_count': len(long_offline),
            'offline_7d_count': len(very_long_offline),
            'offline_24h_list': sorted(long_offline, key=lambda x: x['offline_hours'], reverse=True)[:20],
            'offline_7d_list': sorted(very_long_offline, key=lambda x: x['offline_hours'], reverse=True)[:20]
        }

    def _analyze_platforms(self, sensor_data):
        """Analyze platform distribution."""
        platform_hostnames = defaultdict(list)

        for sensor in sensor_data:
            platform_hostnames[str(sensor['platform_raw'])].append(sensor['hostname'])

        platform_stats = {}
        for platform_raw, hostnames in platform_hostnames.items():
            platform_sensors = [s for s in sensor_data if str(s['platform_raw']) == platform_raw]
            online_count = sum(1 for s in platform_sensors if s['online'])

            platform_stats[platform_raw] = {
                'total': len(platform_sensors),
                'online': online_count,
                'offline': len(platform_sensors) - online_count,
                'hostnames': hostnames[:10]  # Sample of hostnames
            }

        return dict(sorted(platform_stats.items(), key=lambda x: x[1]['total'], reverse=True))

    def _analyze_tags(self, sensor_data):
        """Analyze tag coverage."""
        tag_sensor_map = defaultdict(list)

        for sensor in sensor_data:
            for tag in sensor['tags']:
                tag_sensor_map[tag].append(sensor['hostname'])

        # Convert to list format sorted by sensor count
        tag_list = [
            {
                'name': tag,
                'sensor_count': len(hostnames),
                'sample_hostnames': hostnames[:5]
            }
            for tag, hostnames in tag_sensor_map.items()
        ]

        tag_list.sort(key=lambda x: x['sensor_count'], reverse=True)

        # Count sensors with/without tags
        sensors_with_tags = sum(1 for s in sensor_data if len(s['tags']) > 0)
        sensors_without_tags = len(sensor_data) - sensors_with_tags

        return {
            'total_tags': len(tag_sensor_map),
            'sensors_with_tags': sensors_with_tags,
            'sensors_without_tags': sensors_without_tags,
            'tag_list': tag_list[:30]  # Top 30 tags
        }

    def _analyze_versions(self, sensor_data):
        """Analyze sensor version distribution."""
        version_counts = Counter()

        for sensor in sensor_data:
            agent_version = sensor['version']
            if agent_version != 'unknown':
                # Extract version prefix
                version = agent_version.split('-')[0] if '-' in agent_version else agent_version[:10]
                version_counts[version] += 1

        # Convert to sorted list
        version_list = [
            {'version': version, 'count': count}
            for version, count in version_counts.most_common(10)
        ]

        return {
            'total_versions': len(version_counts),
            'version_list': version_list
        }


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        SensorHealthReport,
        description='Generate a comprehensive sensor health and operational status report',
        require_oid=True
    )
