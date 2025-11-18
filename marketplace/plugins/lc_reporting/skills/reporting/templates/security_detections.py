#!/usr/bin/env python3
"""
Security Detections Report Template
Provides comprehensive analysis of security detections and threat patterns
"""

from limacharlie import Manager
import time
import json
import os
from datetime import datetime, timezone
from collections import defaultdict, Counter
from jinja2 import Environment, FileSystemLoader


def generate_security_detections_report(oid, time_range_days=7, output_format='html'):
    """
    Generate a comprehensive security detections report for a LimaCharlie organization

    Args:
        oid: Organization ID
        time_range_days: Number of days to analyze (default: 7)
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    m = Manager(oid=oid)

    # Calculate time range
    end_time = int(time.time())
    start_time = end_time - (time_range_days * 24 * 3600)

    print(f"Generating security detections report for {time_range_days} days...")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Collect all detections
    print("Collecting detection data...")
    try:
        # Use higher limit and track if we hit it
        DETECTION_LIMIT = 50000
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=DETECTION_LIMIT)

        # Initialize tracking structures
        detection_count = 0
        detection_by_category = defaultdict(int)
        detection_by_day = defaultdict(int)
        detection_by_hour = defaultdict(int)  # For 24-hour timeline
        detection_by_rule = defaultdict(int)
        detection_by_sensor = defaultdict(int)
        detection_by_hostname = defaultdict(int)
        hourly_distribution = defaultdict(int)  # Hour of day distribution (0-23)
        all_detections_list = []
        limit_reached = False

        print("  Processing detections...")
        for det in detections:
            detection_count += 1

            # Check if we hit the limit
            if detection_count >= DETECTION_LIMIT:
                limit_reached = True

            # Store full detection for later analysis
            all_detections_list.append(det)

            # Count by category
            cat = det.get('cat', 'unknown')
            detection_by_category[cat] += 1

            # Count by day/hour for timeline AND hourly distribution
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
                    hour = dt.hour
                    hourly_distribution[hour] += 1
                except (ValueError, OSError):
                    pass

            # Count by rule name (use source_rule field)
            rule_name = det.get('source_rule', 'unknown')
            if isinstance(rule_name, str):
                detection_by_rule[rule_name] += 1

            # Count by sensor (use routing.sid field)
            sensor_id = det.get('routing', {}).get('sid', 'unknown')
            detection_by_sensor[sensor_id] += 1

            # Count by hostname (use routing.hostname field, fallback to sid)
            hostname = det.get('routing', {}).get('hostname', sensor_id)
            # Clean up hostname - remove trailing dot and long domain suffixes
            if hostname and hostname != 'unknown':
                hostname = hostname.rstrip('.')
                # Shorten long internal domain names for readability
                if '.internal' in hostname:
                    hostname = hostname.split('.')[0]
            detection_by_hostname[hostname] += 1

        print(f"  Processed {detection_count} detections")
        if limit_reached:
            print(f"  ⚠️  WARNING: Detection limit of {DETECTION_LIMIT} reached - results may be incomplete!")

        # Calculate detection velocity (detections per day trend)
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

        # Get top triggered rules (top 10)
        top_rules = sorted(detection_by_rule.items(), key=lambda x: x[1], reverse=True)[:10]

        # Get top sensors by detection count (top 10)
        top_sensors = sorted(detection_by_sensor.items(), key=lambda x: x[1], reverse=True)[:10]

        # Get top hostnames by detection count (top 10) - more human readable than SIDs
        top_hostnames = sorted(detection_by_hostname.items(), key=lambda x: x[1], reverse=True)[:10]

        # Identify potentially critical categories (common high-priority detection types)
        critical_categories = [
            'EXFIL', 'RANSOMWARE', 'CRYPTOMINER', 'EXPLOIT',
            'CREDENTIAL_ACCESS', 'PRIVILEGE_ESCALATION', 'LATERAL_MOVEMENT'
        ]
        critical_detections_count = sum(
            count for cat, count in detection_by_category.items()
            if any(crit.lower() in cat.lower() for crit in critical_categories)
        )

        # Build final detection summary
        data['detection_summary'] = {
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
            'detection_velocity': detection_velocity[-7:] if detection_velocity else [],  # Last 7 days
            'hourly_distribution': dict(sorted(hourly_distribution.items())),
            'limit_reached': limit_reached,
            'detection_limit': DETECTION_LIMIT
        }

    except Exception as e:
        print(f"  Error collecting detections: {e}")
        data['detection_summary'] = {
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

    # 3. Get D&R Rules for context
    print("Collecting D&R rule information...")
    try:
        rules = list(m.rules())
        data['dr_rules'] = {
            'total': len(rules),
            'rules': rules
        }
    except Exception as e:
        print(f"  Error collecting rules: {e}")
        data['dr_rules'] = {'total': 0, 'rules': []}

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'time_range_days': time_range_days,
        'start_date': datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%d'),
        'end_date': datetime.fromtimestamp(end_time, tz=timezone.utc).strftime('%Y-%m-%d')
    }

    # Format output
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    elif output_format == 'markdown':
        return format_markdown(data)
    else:  # html
        return render_report(data)


def format_markdown(data):
    """Format data as Markdown report"""
    md = []
    md.append("# LimaCharlie Security Detections Report\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")
    md.append(f"**Time Range**: {meta['start_date']} to {meta['end_date']} ({meta['time_range_days']} days)\n")

    # Organization
    org = data['org_info']
    md.append(f"**Organization**: {org.get('name', 'N/A')} ({org.get('oid', 'N/A')})\n")

    # Detection Overview
    det = data['detection_summary']
    md.append("## Detection Overview")
    md.append(f"- **Total Detections**: {det.get('total', 0):,}")
    md.append(f"- **Average per Day**: {det.get('avg_per_day', 0)}")
    md.append(f"- **Critical Category Detections**: {det.get('critical_detections_count', 0)}")
    if det.get('limit_reached'):
        md.append(f"- ⚠️  **WARNING**: Detection limit of {det.get('detection_limit', 0):,} reached - data may be incomplete")
    md.append("")

    # Top Categories
    if det.get('by_category'):
        md.append("## Top Detection Categories")
        for cat, count in list(det['by_category'].items())[:10]:
            md.append(f"- **{cat}**: {count:,}")
        md.append("")

    # Top Rules
    if det.get('top_rules'):
        md.append("## Top Triggered Rules")
        for rule_data in det['top_rules'][:10]:
            md.append(f"- **{rule_data['rule']}**: {rule_data['count']:,}")
        md.append("")

    # Top Hostnames
    if det.get('top_hostnames'):
        md.append("## Top Hostnames by Detection Count")
        for hostname_data in det['top_hostnames'][:10]:
            md.append(f"- **{hostname_data['hostname']}**: {hostname_data['count']:,}")
        md.append("")

    md.append("---")
    md.append("*Generated by LimaCharlie Reporting Skill*")

    return '\n'.join(md)


def render_report(data):
    """Render report using Jinja2 template with Chart.js"""

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'jinja2', 'html')

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load and render template
    template = env.get_template('security_detections.j2')
    return template.render(**data)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python security_detections.py <OID> [days] [format]")
        print("Example: python security_detections.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 html")
        sys.exit(1)

    oid = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    fmt = sys.argv[3] if len(sys.argv) > 3 else 'html'

    report = generate_security_detections_report(oid, days, fmt)

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    filename = f'security_detections_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
