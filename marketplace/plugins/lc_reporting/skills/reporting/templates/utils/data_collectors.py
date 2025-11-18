"""
Data Collectors for LimaCharlie Reporting
Specialized collectors for each data type with caching and error handling
"""

from limacharlie import Manager
from datetime import datetime, timezone
from collections import defaultdict
from .report_helpers import normalize_sensor_data, format_timestamp


class DataCollector:
    """Base class for data collection with caching"""

    def __init__(self, oid, cache=True):
        """
        Initialize data collector

        Args:
            oid: Organization ID
            cache: Enable caching (default: True)
        """
        self.manager = Manager(oid=oid)
        self.oid = oid
        self.cache_enabled = cache
        self._cache = {}

    def _get_cached(self, key, fetch_func):
        """
        Get data from cache or fetch if not cached

        Args:
            key: Cache key
            fetch_func: Function to call if not cached

        Returns:
            Cached or freshly fetched data
        """
        if self.cache_enabled and key in self._cache:
            return self._cache[key]

        data = fetch_func()

        if self.cache_enabled:
            self._cache[key] = data

        return data


def collect_org_info(oid):
    """
    Collect organization information

    Args:
        oid: Organization ID

    Returns:
        Dictionary with organization metadata
    """
    try:
        m = Manager(oid=oid)
        org_info = m.getOrgInfo()

        return {
            'oid': oid,
            'name': org_info.get('name', 'Unknown'),
            'created': org_info.get('created', 0),
            'tier': org_info.get('tier', 'unknown'),
            'raw': org_info
        }
    except Exception as e:
        print(f"Error collecting org info: {e}")
        return {
            'oid': oid,
            'name': 'Unknown',
            'error': str(e)
        }


def collect_detections(oid, start_time, end_time, limit=5000, sensor_id=None, category=None):
    """
    Collect historic detections with optional filtering

    Args:
        oid: Organization ID
        start_time: Start timestamp
        end_time: End timestamp
        limit: Maximum number of detections (default: 5000)
        sensor_id: Filter by specific sensor (optional)
        category: Filter by detection category (optional)

    Returns:
        Dictionary with detection data and metadata
    """
    try:
        m = Manager(oid=oid)
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=limit)

        detection_list = []
        detection_timeline = defaultdict(int)
        detection_by_category = defaultdict(int)
        detection_by_severity = defaultdict(int)
        affected_sensors = set()

        for det in detections:
            # Apply filters
            det_sensor_id = det.get('routing', {}).get('sid', 'unknown')
            if sensor_id and det_sensor_id != sensor_id:
                continue

            det_category = det.get('cat', 'unknown')
            if category and det_category != category:
                continue

            # Process detection
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

            # Aggregate by category
            detection_by_category[det_category] += 1

            # Aggregate by severity
            severity = det.get('severity', 0)
            detection_by_severity[severity] += 1

            # Track affected sensors
            affected_sensors.add(det_sensor_id)

            # Store detection details
            detection_list.append({
                'timestamp': ts if ts else 0,
                'timestamp_str': format_timestamp(ts),
                'category': det_category,
                'rule': det.get('source_rule', 'unknown'),
                'sensor_id': det_sensor_id,
                'severity': severity,
                'summary': det.get('summary', 'No summary available'),
                'raw': det
            })

        # Sort by timestamp (most recent first)
        detection_list.sort(key=lambda x: x['timestamp'], reverse=True)

        # Check if limit was hit
        hit_limit = len(detection_list) >= limit

        return {
            'total': len(detection_list),
            'list': detection_list,
            'timeline': dict(sorted(detection_timeline.items())),
            'by_category': dict(sorted(detection_by_category.items(), key=lambda x: x[1], reverse=True)),
            'by_severity': dict(detection_by_severity),
            'affected_sensor_count': len(affected_sensors),
            'affected_sensors': list(affected_sensors),
            'hit_limit': hit_limit,
            'limit': limit
        }

    except Exception as e:
        print(f"Error collecting detections: {e}")
        return {
            'total': 0,
            'list': [],
            'timeline': {},
            'by_category': {},
            'by_severity': {},
            'affected_sensor_count': 0,
            'affected_sensors': [],
            'error': str(e)
        }


def collect_sensors(oid, tags=None, platform=None):
    """
    Collect sensor information with optional filtering

    Args:
        oid: Organization ID
        tags: Filter by tags (optional)
        platform: Filter by platform (optional)

    Returns:
        Dictionary with sensor data
    """
    try:
        m = Manager(oid=oid)
        sensors = m.sensors()

        sensor_list = []
        platform_counts = defaultdict(int)
        online_count = 0
        offline_count = 0

        for sensor in sensors:
            sensor_info = sensor.getInfo()
            sensor_platform = sensor_info.get('plat', 'unknown')
            is_online = sensor.isOnline()

            # Apply filters
            if platform and sensor_platform != platform:
                continue

            sensor_tags = sensor.getTags()
            if tags and not any(tag in sensor_tags for tag in tags):
                continue

            # Aggregate stats
            platform_counts[sensor_platform] += 1
            if is_online:
                online_count += 1
            else:
                offline_count += 1

            # Normalize and store
            normalized = normalize_sensor_data(sensor_info)
            normalized['is_online'] = is_online
            normalized['tags'] = sensor_tags

            sensor_list.append(normalized)

        return {
            'total': len(sensor_list),
            'list': sensor_list,
            'by_platform': dict(platform_counts),
            'online_count': online_count,
            'offline_count': offline_count
        }

    except Exception as e:
        print(f"Error collecting sensors: {e}")
        return {
            'total': 0,
            'list': [],
            'by_platform': {},
            'online_count': 0,
            'offline_count': 0,
            'error': str(e)
        }


def collect_sensor_info(oid, sensor_id):
    """
    Collect detailed information for a specific sensor

    Args:
        oid: Organization ID
        sensor_id: Sensor ID

    Returns:
        Dictionary with sensor details
    """
    try:
        m = Manager(oid=oid)
        sensor = m.sensor(sensor_id)
        sensor_info = sensor.getInfo()

        normalized = normalize_sensor_data(sensor_info)
        normalized['is_online'] = sensor.isOnline()
        normalized['tags'] = sensor.getTags()

        return normalized

    except Exception as e:
        print(f"Error collecting sensor info for {sensor_id}: {e}")
        return {
            'sid': sensor_id,
            'error': str(e)
        }


def collect_rules(oid, namespace=None, enabled_only=False):
    """
    Collect D&R rules with optional filtering

    Args:
        oid: Organization ID
        namespace: Filter by namespace (optional)
        enabled_only: Only include enabled rules (default: False)

    Returns:
        Dictionary with rules data
    """
    try:
        m = Manager(oid=oid)
        rules = m.rules()

        rule_list = []
        by_namespace = defaultdict(int)
        enabled_count = 0
        disabled_count = 0

        for rule in rules:
            rule_namespace = rule.get('namespace', 'default')
            is_enabled = rule.get('isEnabled', True)

            # Apply filters
            if namespace and rule_namespace != namespace:
                continue

            if enabled_only and not is_enabled:
                continue

            # Aggregate stats
            by_namespace[rule_namespace] += 1
            if is_enabled:
                enabled_count += 1
            else:
                disabled_count += 1

            rule_list.append(rule)

        return {
            'total': len(rule_list),
            'list': rule_list,
            'by_namespace': dict(by_namespace),
            'enabled_count': enabled_count,
            'disabled_count': disabled_count
        }

    except Exception as e:
        print(f"Error collecting rules: {e}")
        return {
            'total': 0,
            'list': [],
            'by_namespace': {},
            'enabled_count': 0,
            'disabled_count': 0,
            'error': str(e)
        }


def collect_ioc_matches(oid, iocs, detections_data):
    """
    Search for IOC matches in detection data

    Args:
        oid: Organization ID
        iocs: List of IOCs to search for
        detections_data: Detection data from collect_detections()

    Returns:
        Dictionary with IOC search results
    """
    ioc_results = []

    for ioc in iocs:
        matches = []
        for det in detections_data.get('list', []):
            # Search in summary
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

    return {
        'total_iocs': len(iocs),
        'results': ioc_results
    }


__all__ = [
    'DataCollector',
    'collect_org_info',
    'collect_detections',
    'collect_sensors',
    'collect_sensor_info',
    'collect_rules',
    'collect_ioc_matches'
]
