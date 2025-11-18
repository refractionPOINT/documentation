"""
Report Helper Utilities
Common functions for time range handling, aggregation, and data processing
"""

import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict


def parse_time_range(time_range_days=None, start_time=None, end_time=None, hours_back=None):
    """
    Parse time range from various input formats

    Args:
        time_range_days: Number of days to look back (optional)
        start_time: Explicit start timestamp (optional)
        end_time: Explicit end timestamp (optional)
        hours_back: Number of hours to look back (optional)

    Returns:
        Tuple of (start_time, end_time) as Unix timestamps
    """
    # End time defaults to now
    if end_time is None:
        end_time = int(time.time())

    # Calculate start time from various inputs
    if start_time is not None:
        # Explicit start time provided
        pass
    elif hours_back is not None:
        start_time = end_time - (hours_back * 3600)
    elif time_range_days is not None:
        start_time = end_time - (time_range_days * 86400)
    else:
        # Default to 24 hours
        start_time = end_time - 86400

    return start_time, end_time


def format_timestamp(ts, fmt='iso'):
    """
    Format a Unix timestamp in various formats

    Args:
        ts: Unix timestamp (seconds or milliseconds)
        fmt: Output format ('iso', 'datetime', 'date', 'time')

    Returns:
        Formatted timestamp string
    """
    if ts is None or ts == 0:
        return 'unknown'

    # Handle millisecond timestamps
    if ts > 10000000000:
        ts = ts / 1000

    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)

        if fmt == 'iso':
            return dt.isoformat()
        elif fmt == 'datetime':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif fmt == 'date':
            return dt.strftime('%Y-%m-%d')
        elif fmt == 'time':
            return dt.strftime('%H:%M:%S')
        else:
            return dt.isoformat()
    except (ValueError, OSError):
        return 'unknown'


def calculate_duration(start_time, end_time, unit='hours'):
    """
    Calculate duration between two timestamps

    Args:
        start_time: Start Unix timestamp
        end_time: End Unix timestamp
        unit: Output unit ('seconds', 'minutes', 'hours', 'days')

    Returns:
        Duration as float in specified unit
    """
    duration_seconds = end_time - start_time

    if unit == 'seconds':
        return duration_seconds
    elif unit == 'minutes':
        return round(duration_seconds / 60, 1)
    elif unit == 'hours':
        return round(duration_seconds / 3600, 1)
    elif unit == 'days':
        return round(duration_seconds / 86400, 1)
    else:
        return duration_seconds


def aggregate_by_category(items, category_key='cat', count=True):
    """
    Aggregate items by category

    Args:
        items: List of dictionaries containing category data
        category_key: Key to use for category (default: 'cat')
        count: If True, count occurrences; if False, collect items

    Returns:
        Dictionary mapping categories to counts or lists
    """
    result = defaultdict(int if count else list)

    for item in items:
        category = item.get(category_key, 'unknown')
        if count:
            result[category] += 1
        else:
            result[category].append(item)

    return dict(result)


def aggregate_by_timeline(items, timestamp_key='ts', interval='hour'):
    """
    Aggregate items into time buckets

    Args:
        items: List of dictionaries containing timestamp data
        timestamp_key: Key to use for timestamp (default: 'ts')
        interval: Time bucket interval ('hour', 'day', 'week')

    Returns:
        Dictionary mapping time buckets to counts
    """
    timeline = defaultdict(int)

    for item in items:
        ts = item.get(timestamp_key, item.get('timestamp', 0))
        if not ts:
            continue

        try:
            # Handle millisecond timestamps
            if ts > 10000000000:
                ts = ts / 1000

            dt = datetime.fromtimestamp(ts, tz=timezone.utc)

            if interval == 'hour':
                bucket = dt.strftime('%Y-%m-%d %H:00')
            elif interval == 'day':
                bucket = dt.strftime('%Y-%m-%d')
            elif interval == 'week':
                # ISO week format
                bucket = dt.strftime('%Y-W%U')
            else:
                bucket = dt.strftime('%Y-%m-%d %H:00')

            timeline[bucket] += 1
        except (ValueError, OSError):
            continue

    return dict(sorted(timeline.items()))


def aggregate_by_field(items, field_key, count=True, top_n=None):
    """
    Generic aggregation by any field

    Args:
        items: List of dictionaries
        field_key: Key to aggregate by
        count: If True, count occurrences; if False, collect items
        top_n: If specified, return only top N results by count

    Returns:
        Dictionary mapping field values to counts or lists
    """
    result = defaultdict(int if count else list)

    for item in items:
        value = item.get(field_key, 'unknown')
        if count:
            result[value] += 1
        else:
            result[value].append(item)

    result_dict = dict(result)

    if top_n and count:
        # Sort by count and take top N
        sorted_items = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:top_n])

    return result_dict


def normalize_sensor_data(sensor_info):
    """
    Normalize sensor information to a standard format

    Args:
        sensor_info: Raw sensor info from LimaCharlie SDK

    Returns:
        Normalized sensor data dictionary
    """
    return {
        'sid': sensor_info.get('sid', 'unknown'),
        'hostname': sensor_info.get('hostname', 'unknown'),
        'platform': sensor_info.get('plat', sensor_info.get('platform', 'unknown')),
        'ext_ip': sensor_info.get('ext_ip', 'unknown'),
        'int_ip': sensor_info.get('int_ip', 'unknown'),
        'last_seen': sensor_info.get('last_seen', 0),
        'is_online': sensor_info.get('is_online', False),
        'tags': sensor_info.get('tags', [])
    }


def filter_items(items, filters):
    """
    Filter items based on multiple criteria

    Args:
        items: List of dictionaries to filter
        filters: Dictionary of field->value filters

    Returns:
        Filtered list of items
    """
    filtered = items

    for field, value in filters.items():
        if value is not None:
            filtered = [item for item in filtered if item.get(field) == value]

    return filtered


def calculate_severity_distribution(items, severity_key='severity'):
    """
    Calculate distribution of items by severity

    Args:
        items: List of dictionaries containing severity data
        severity_key: Key to use for severity (default: 'severity')

    Returns:
        Dictionary with severity counts and percentages
    """
    severity_map = {
        0: 'info',
        1: 'low',
        2: 'medium',
        3: 'high',
        4: 'critical'
    }

    counts = defaultdict(int)
    total = len(items)

    for item in items:
        severity_num = item.get(severity_key, 0)
        severity_name = severity_map.get(severity_num, 'unknown')
        counts[severity_name] += 1

    # Calculate percentages
    distribution = {}
    for severity, count in counts.items():
        distribution[severity] = {
            'count': count,
            'percentage': round((count / total * 100) if total > 0 else 0, 1)
        }

    return distribution


__all__ = [
    'parse_time_range',
    'format_timestamp',
    'calculate_duration',
    'aggregate_by_category',
    'aggregate_by_timeline',
    'aggregate_by_field',
    'normalize_sensor_data',
    'filter_items',
    'calculate_severity_distribution'
]
