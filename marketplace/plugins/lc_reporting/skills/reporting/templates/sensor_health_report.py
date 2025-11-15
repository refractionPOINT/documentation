#!/usr/bin/env python3
"""
Sensor Health Report Template (Refactored with Jinja2)
Generates comprehensive operational health report for LimaCharlie sensors
"""

from limacharlie import Manager
import time
import json
from datetime import datetime, timezone
from collections import defaultdict, Counter
from jinja2 import Environment, FileSystemLoader
import os
import sys
from chart_utils import generate_static_chart, should_use_static_charts


def collect_sensor_data(oid):
    """
    Collect all sensor health data from LimaCharlie

    Args:
        oid: Organization ID

    Returns:
        Dictionary containing all sensor health metrics
    """
    m = Manager(oid=oid)

    print(f"Generating sensor health report...")

    data = {}

    # 1. Organization metadata
    print("\n[1/6] Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Collect all sensor data
    print("[2/6] Collecting sensor data...")
    all_sensors = list(m.sensors())
    online_sensors = m.getAllOnlineSensors()
    online_sids = set(online_sensors) if isinstance(online_sensors, list) else set()

    platform_hostnames = defaultdict(list)
    sensor_data = []
    tag_sensor_map = defaultdict(list)
    version_counts = Counter()

    current_time = int(time.time())

    for i, sensor in enumerate(all_sensors):
        if i % 100 == 0:
            print(f"  Processing sensor {i+1}/{len(all_sensors)}...")

        try:
            info = sensor.getInfo()
            platform_raw = info.get('plat', info.get('ext_plat', 'unknown'))
            hostname = info.get('hostname', 'N/A')
            is_online = sensor.sid in online_sids

            # Calculate offline duration
            offline_hours = 0
            last_seen_str = 'Never'

            if not is_online:
                alive_str = info.get('alive', '')
                if alive_str:
                    try:
                        alive_dt = datetime.strptime(alive_str, '%Y-%m-%d %H:%M:%S')
                        alive_dt = alive_dt.replace(tzinfo=timezone.utc)
                        offline_hours = (current_time - alive_dt.timestamp()) / 3600
                        last_seen_str = alive_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except:
                        last_seen = info.get('last_seen', 0)
                        if last_seen > 0:
                            if last_seen > 10000000000:
                                last_seen = last_seen / 1000
                            offline_hours = (current_time - last_seen) / 3600
                            last_seen_str = datetime.fromtimestamp(last_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                else:
                    last_seen = info.get('last_seen', 0)
                    if last_seen > 0:
                        if last_seen > 10000000000:
                            last_seen = last_seen / 1000
                        offline_hours = (current_time - last_seen) / 3600
                        last_seen_str = datetime.fromtimestamp(last_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            # Extract version
            agent_version = info.get('sensor_seed_key', 'unknown')
            if agent_version != 'unknown':
                version = agent_version.split('-')[0] if '-' in agent_version else agent_version[:10]
                version_counts[version] += 1

            # Collect tags
            tags = info.get('tags', [])
            for tag in tags:
                tag_sensor_map[tag].append(hostname)

            platform_hostnames[str(platform_raw)].append(hostname)
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

    # 3. Platform distribution
    print("[3/6] Analyzing platform distribution...")
    platform_stats = {}

    for platform_raw, hostnames in platform_hostnames.items():
        platform_sensors = [s for s in sensor_data if str(s['platform_raw']) == platform_raw]
        online_count = sum(1 for s in platform_sensors if s['online'])

        # Generate display name
        display_name = str(platform_raw).capitalize() if platform_raw in ['windows', 'linux', 'macos'] else f"Platform {platform_raw}"

        platform_stats[display_name] = {
            'total': len(platform_sensors),
            'online': online_count,
            'offline': len(platform_sensors) - online_count,
            'availability': (online_count / len(platform_sensors) * 100) if len(platform_sensors) > 0 else 0
        }

    data['platform_stats'] = dict(sorted(platform_stats.items(), key=lambda x: x[1]['total'], reverse=True))

    # 4. Tag analysis
    print("[4/6] Analyzing tags...")
    tag_stats = {}

    for tag, hostnames in tag_sensor_map.items():
        tag_sensors = [s for s in sensor_data if tag in s['tags']]
        online_count = sum(1 for s in tag_sensors if s['online'])

        tag_stats[tag] = {
            'total': len(tag_sensors),
            'online': online_count,
            'offline': len(tag_sensors) - online_count
        }

    data['tag_stats'] = dict(sorted(tag_stats.items(), key=lambda x: x[1]['total'], reverse=True))

    untagged_sensors = [s for s in sensor_data if not s['tags']]
    data['untagged_count'] = len(untagged_sensors)

    # 5. Stale sensor detection
    print("[5/6] Identifying stale sensors...")
    stale_categories = {
        'offline_24h': [],
        'offline_7d': [],
        'offline_30d': []
    }

    for sensor in sensor_data:
        if not sensor['online'] and sensor['offline_hours'] > 0:
            hours = sensor['offline_hours']
            sensor_info = {
                'hostname': sensor['hostname'],
                'offline_hours': hours,
                'offline_days': hours / 24,
                'last_seen': sensor['last_seen_str'],
                'tags': ', '.join(sensor['tags']) if sensor['tags'] else 'No tags'
            }

            if hours > 30 * 24:
                stale_categories['offline_30d'].append(sensor_info)
            elif hours > 7 * 24:
                stale_categories['offline_7d'].append(sensor_info)
            elif hours > 24:
                stale_categories['offline_24h'].append(sensor_info)

    data['stale_sensors'] = stale_categories

    # 6. Version distribution
    print("[6/6] Analyzing version distribution...")
    data['version_distribution'] = dict(version_counts.most_common(10))

    # Summary statistics
    online_count = len([s for s in sensor_data if s['online']])
    data['summary'] = {
        'total_sensors': len(sensor_data),
        'online_sensors': online_count,
        'offline_sensors': len(sensor_data) - online_count,
        'availability_percentage': (online_count / len(sensor_data) * 100) if len(sensor_data) > 0 else 0,
        'platform_count': len(platform_stats),
        'tag_count': len(tag_stats),
        'untagged_count': len(untagged_sensors),
        'stale_24h_count': len(stale_categories['offline_24h']),
        'stale_7d_count': len(stale_categories['offline_7d']),
        'stale_30d_count': len(stale_categories['offline_30d']),
        'report_generated': datetime.now(timezone.utc).isoformat(),
        'org_name': data['org_info'].get('name', 'Unknown'),
        'org_id': oid
    }

    return data


def _generate_static_charts_for_data(data):
    """
    Generate static charts for PDF output

    Args:
        data: Sensor health data dictionary

    Returns:
        Dictionary of chart names to base64-encoded images
    """
    charts = {}

    # Platform distribution pie chart
    if data.get('platform_stats'):
        platform_labels = list(data['platform_stats'].keys())
        platform_data = [stats['total'] for stats in data['platform_stats'].values()]

        chart = generate_static_chart(
            {'labels': platform_labels, 'data': platform_data},
            'pie',
            'Sensor Distribution by Platform'
        )
        if chart:
            charts['platform_distribution'] = chart

    # Tag distribution pie chart (top 10)
    if data.get('tag_stats'):
        tag_items = sorted(data['tag_stats'].items(), key=lambda x: x[1]['total'], reverse=True)[:10]
        tag_labels = [item[0] for item in tag_items]
        tag_data = [item[1]['total'] for item in tag_items]

        chart = generate_static_chart(
            {'labels': tag_labels, 'data': tag_data},
            'pie',
            'Top 10 Tags by Sensor Count'
        )
        if chart:
            charts['tag_distribution'] = chart

    # Stale sensors pie chart
    stale = data.get('stale_sensors', {})
    stale_counts = {
        '1-7 days': len(stale.get('offline_24h', [])),
        '7-30 days': len(stale.get('offline_7d', [])),
        '>30 days': len(stale.get('offline_30d', []))
    }

    if sum(stale_counts.values()) > 0:
        chart = generate_static_chart(
            {'labels': list(stale_counts.keys()), 'data': list(stale_counts.values())},
            'pie',
            'Offline Sensor Age Distribution'
        )
        if chart:
            charts['stale_sensors'] = chart

    # Version distribution bar chart (top 10)
    if data.get('version_distribution'):
        version_items = list(data['version_distribution'].items())[:10]
        version_labels = [v[:15] + '...' if len(v) > 15 else v for v, _ in version_items]
        version_data = [count for _, count in version_items]

        chart = generate_static_chart(
            {'labels': version_labels, 'data': version_data},
            'bar',
            'Top 10 Agent Versions'
        )
        if chart:
            charts['version_distribution'] = chart

    return charts


def render_report(data, output_format='html'):
    """
    Render report using Jinja2 templates

    Args:
        data: Dictionary of sensor health data
        output_format: 'html', 'markdown', or 'pdf'

    Returns:
        Rendered report as string (or bytes for PDF)
    """
    # Generate static charts for PDF/non-interactive formats
    if should_use_static_charts(output_format):
        data['static_charts'] = _generate_static_charts_for_data(data)
        data['use_static_charts'] = True
    else:
        data['use_static_charts'] = False

    # For PDF, first render as HTML then convert
    template_format = 'html' if output_format == 'pdf' else output_format

    # Get template directory
    template_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'jinja2',
        template_format
    )

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Add custom filters
    env.filters['round'] = lambda x, decimals=1: round(x, decimals)
    env.filters['percent'] = lambda x: f"{x:.1f}%"

    # Load and render template
    template = env.get_template('sensor_health.j2')
    html_content = template.render(**data)

    # Convert to PDF if requested
    if output_format == 'pdf':
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            print("⚠️  Warning: weasyprint not installed. Install with: pip3 install weasyprint")
            print("Falling back to HTML output...")
            return html_content

    return html_content


def main():
    if len(sys.argv) < 2:
        print("Usage: sensor_health_report.py <oid> [format]")
        print("  format: html (default), markdown, or pdf")
        sys.exit(1)

    oid = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'html'

    # Validate format
    if output_format not in ['html', 'markdown', 'pdf']:
        print(f"Error: Invalid format '{output_format}'. Must be html, markdown, or pdf")
        sys.exit(1)

    # Collect data
    data = collect_sensor_data(oid)

    # Render report
    report = render_report(data, output_format)

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = 'html' if output_format == 'html' else 'md' if output_format == 'markdown' else 'pdf'
    filename = f"sensor_health_{timestamp}.{ext}"
    filepath = os.path.join(reports_dir, filename)

    # Write binary for PDF, text for others
    mode = 'wb' if isinstance(report, bytes) else 'w'
    with open(filepath, mode) as f:
        f.write(report)

    print(f"\n✅ Report generated: {filepath}")


if __name__ == '__main__':
    main()
