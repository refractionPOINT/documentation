#!/usr/bin/env python3
"""
Executive Summary Report Template
Generates a high-level organizational overview for management
"""

from limacharlie import Manager
import time
import json
import os
from datetime import datetime, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader


def generate_executive_summary(oid, time_range_days=7, output_format='html'):
    """
    Generate an executive summary report for a LimaCharlie organization

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

    print(f"Generating executive summary for {time_range_days} days...")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Sensor statistics
    print("Collecting sensor statistics...")
    all_sensors = list(m.sensors())
    online_sensors = m.getAllOnlineSensors()

    data['sensor_stats'] = {
        'total': len(all_sensors),
        'online': len(online_sensors),
        'offline': len(all_sensors) - len(online_sensors),
        'online_percentage': round((len(online_sensors) / len(all_sensors) * 100) if all_sensors else 0, 1)
    }

    # Platform breakdown - properly get platform from sensor info
    print(f"  Analyzing {len(all_sensors)} sensors...")
    platforms = defaultdict(int)
    for i, sensor in enumerate(all_sensors):
        if i % 100 == 0 and i > 0:
            print(f"  Processed {i}/{len(all_sensors)} sensors...")
        try:
            info = sensor.getInfo()
            # Get platform - try 'plat' first, then 'ext_plat', default to 'unknown'
            platform = info.get('plat', info.get('ext_plat', 'unknown'))
            platforms[str(platform)] += 1
        except Exception as e:
            platforms['unknown'] += 1
    data['sensor_stats']['by_platform'] = dict(platforms)

    # 3. Detection summary
    print("Collecting detection data...")
    try:
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=10000)

        detection_categories = defaultdict(int)
        detection_by_day = defaultdict(int)
        detection_count = 0  # Count detections as we iterate (can't use len() on generator)

        for det in detections:
            detection_count += 1

            # Count by category
            cat = det.get('cat', 'unknown')
            detection_categories[cat] += 1

            # Count by day - handle timestamp safely
            ts = det.get('timestamp', det.get('ts', 0))
            if ts:
                try:
                    # Convert milliseconds to seconds if needed
                    if ts > 10000000000:  # Likely milliseconds
                        ts = ts / 1000
                    day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')
                    detection_by_day[day] += 1
                except (ValueError, OSError) as e:
                    # Skip invalid timestamps
                    pass

        data['detection_summary'] = {
            'total': detection_count,
            'by_category': dict(detection_categories),
            'by_day': dict(sorted(detection_by_day.items())),
            'avg_per_day': round(detection_count / time_range_days, 1) if time_range_days > 0 else 0
        }
    except Exception as e:
        print(f"  Error collecting detections: {e}")
        data['detection_summary'] = {'error': str(e), 'total': 0, 'by_category': {}, 'by_day': {}, 'avg_per_day': 0}

    # 4. Usage summary (last full day)
    print("Collecting usage statistics...")
    try:
        usage = m.getUsageStats()
        if 'usage' in usage:
            # Get most recent day's stats
            latest_date = max(usage['usage'].keys())
            latest_stats = usage['usage'][latest_date]

            data['usage_summary'] = {
                'date': latest_date,
                'sensor_events': latest_stats.get('sensor_events', 0),
                'detections_generated': latest_stats.get('replay_num_evals', 0),
                'output_bytes_gb': round(latest_stats.get('output_bytes_tx', 0) / (1024**3), 2),
                'peak_sensors': latest_stats.get('sensor_watermark', 0)
            }
    except Exception as e:
        data['usage_summary'] = {'error': str(e)}

    # 5. Configuration summary
    print("Collecting configuration data...")
    data['config_summary'] = {
        'dr_rules': len(m.rules()),
        'outputs': len(m.outputs()),
        'tags': len(m.getAllTags()),
        'users': len(m.getUsers()),
        'api_keys': len(m.getApiKeys())
    }

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'time_range_days': time_range_days,
        'start_date': datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%d'),
        'end_date': datetime.fromtimestamp(end_time, tz=timezone.utc).strftime('%Y-%m-%d')
    }

    # Format output
    if output_format == 'json':
        return json.dumps(data, indent=2)
    elif output_format == 'markdown':
        return format_markdown(data)
    else:  # html
        return render_report(data)


def format_markdown(data):
    """Format data as Markdown report"""
    md = []
    md.append("# LimaCharlie Executive Summary Report\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")
    md.append(f"**Time Range**: {meta['start_date']} to {meta['end_date']} ({meta['time_range_days']} days)\n")

    # Organization
    org = data['org_info']
    md.append("## Organization")
    md.append(f"- **Name**: {org.get('name', 'N/A')}")
    md.append(f"- **Organization ID**: {org.get('oid', 'N/A')}")
    md.append(f"- **Sensor Quota**: {org.get('sensor_quota', 'N/A')}")
    md.append(f"- **Current Sensor Version**: {org.get('sensor_version', 'N/A')}\n")

    # Sensors
    sensors = data['sensor_stats']
    md.append("## Sensor Health")
    md.append(f"- **Total Sensors**: {sensors['total']}")
    md.append(f"- **Online**: {sensors['online']} ({sensors['online_percentage']}%)")
    md.append(f"- **Offline**: {sensors['offline']}\n")

    if sensors.get('by_platform'):
        md.append("### By Platform")
        for platform, count in sorted(sensors['by_platform'].items()):
            md.append(f"- **{platform}**: {count}")
        md.append("")

    # Detections
    det = data['detection_summary']
    md.append("## Security Detections")
    md.append(f"- **Total Detections**: {det.get('total', 0)}")
    md.append(f"- **Average per Day**: {det.get('avg_per_day', 0)}\n")

    if det.get('by_category'):
        md.append("### Top Detection Categories")
        sorted_cats = sorted(det['by_category'].items(), key=lambda x: x[1], reverse=True)[:5]
        for cat, count in sorted_cats:
            md.append(f"- **{cat}**: {count}")
        md.append("")

    # Usage
    if 'usage_summary' in data and 'error' not in data['usage_summary']:
        usage = data['usage_summary']
        md.append("## Usage Statistics (Most Recent Day)")
        md.append(f"- **Date**: {usage.get('date', 'N/A')}")
        md.append(f"- **Sensor Events**: {usage.get('sensor_events', 0):,}")
        md.append(f"- **D&R Evaluations**: {usage.get('detections_generated', 0):,}")
        md.append(f"- **Output Data**: {usage.get('output_bytes_gb', 0)} GB")
        md.append(f"- **Peak Concurrent Sensors**: {usage.get('peak_sensors', 0)}\n")

    # Configuration
    config = data['config_summary']
    md.append("## Configuration")
    md.append(f"- **D&R Rules**: {config.get('dr_rules', 0)}")
    md.append(f"- **Outputs**: {config.get('outputs', 0)}")
    md.append(f"- **Tags**: {config.get('tags', 0)}")
    md.append(f"- **Users**: {config.get('users', 0)}")
    md.append(f"- **API Keys**: {config.get('api_keys', 0)}\n")

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
    template = env.get_template('executive_summary.j2')
    return template.render(**data)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python executive_summary.py <OID> [days] [format]")
        print("Example: python executive_summary.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 html")
        sys.exit(1)

    oid = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    fmt = sys.argv[3] if len(sys.argv) > 3 else 'html'

    report = generate_executive_summary(oid, days, fmt)

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    filename = f'executive_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
