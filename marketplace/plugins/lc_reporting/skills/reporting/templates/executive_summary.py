#!/usr/bin/env python3
"""
Executive Summary Report Template
Generates a high-level organizational overview for management
"""

from limacharlie import Manager
import time
import json
from datetime import datetime, timezone
from collections import defaultdict


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

    # Platform breakdown
    platforms = defaultdict(int)
    for sensor in all_sensors:
        try:
            # Get platform from sensor object
            platform = sensor._platform if hasattr(sensor, '_platform') else 'unknown'
            platforms[platform] += 1
        except:
            platforms['unknown'] += 1
    data['sensor_stats']['by_platform'] = dict(platforms)

    # 3. Detection summary
    print("Collecting detection data...")
    try:
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=10000)

        detection_categories = defaultdict(int)
        detection_by_day = defaultdict(int)

        for det in detections:
            # Count by category
            cat = det.get('cat', 'unknown')
            detection_categories[cat] += 1

            # Count by day
            ts = det.get('timestamp', det.get('ts', 0))
            if ts:
                day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')
                detection_by_day[day] += 1

        data['detection_summary'] = {
            'total': len(detections),
            'by_category': dict(detection_categories),
            'by_day': dict(sorted(detection_by_day.items())),
            'avg_per_day': round(len(detections) / time_range_days, 1) if time_range_days > 0 else 0
        }
    except Exception as e:
        data['detection_summary'] = {'error': str(e), 'total': 0}

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
        return format_html(data)


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


def format_html(data):
    """Format data as HTML report"""

    meta = data['report_metadata']
    org = data['org_info']
    sensors = data['sensor_stats']
    det = data['detection_summary']
    config = data['config_summary']

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LimaCharlie Executive Summary - {org.get('name', 'N/A')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .metadata {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .status-good {{ border-left-color: #28a745; }}
        .status-warning {{ border-left-color: #ffc107; }}
        .status-danger {{ border-left-color: #dc3545; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Executive Summary Report</h1>
        <div class="metadata">
            <strong>{org.get('name', 'N/A')}</strong> |
            Generated: {meta['generated_at']} |
            Time Range: {meta['start_date']} to {meta['end_date']} ({meta['time_range_days']} days)
        </div>
    </div>

    <div class="card">
        <h2>📊 Key Metrics</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">Total Sensors</div>
                <div class="stat-value">{sensors['total']}</div>
            </div>
            <div class="stat-box status-good">
                <div class="stat-label">Online Sensors</div>
                <div class="stat-value">{sensors['online']} <span style="font-size:0.5em">({sensors['online_percentage']}%)</span></div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Detections</div>
                <div class="stat-value">{det.get('total', 0)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Avg Detections/Day</div>
                <div class="stat-value">{det.get('avg_per_day', 0)}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>💻 Sensor Health</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Sensors</td>
                <td>{sensors['total']}</td>
            </tr>
            <tr>
                <td>Online</td>
                <td>{sensors['online']} ({sensors['online_percentage']}%)</td>
            </tr>
            <tr>
                <td>Offline</td>
                <td>{sensors['offline']}</td>
            </tr>
        </table>

        <h3>Platform Distribution</h3>
        <table>
            <tr>
                <th>Platform</th>
                <th>Count</th>
            </tr>
"""

    for platform, count in sorted(sensors.get('by_platform', {}).items()):
        html += f"            <tr><td>{platform}</td><td>{count}</td></tr>\n"

    html += """        </table>
    </div>

    <div class="card">
        <h2>🔒 Security Detections</h2>
        <p>Detection activity over the reporting period.</p>
"""

    if det.get('by_category'):
        html += """        <h3>Top Detection Categories</h3>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
            </tr>
"""
        sorted_cats = sorted(det['by_category'].items(), key=lambda x: x[1], reverse=True)[:10]
        for cat, count in sorted_cats:
            html += f"            <tr><td>{cat}</td><td>{count}</td></tr>\n"
        html += "        </table>\n"

    html += "    </div>\n"

    # Usage stats
    if 'usage_summary' in data and 'error' not in data['usage_summary']:
        usage = data['usage_summary']
        html += f"""    <div class="card">
        <h2>📈 Usage Statistics</h2>
        <p>Most recent day's activity: <strong>{usage.get('date', 'N/A')}</strong></p>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Sensor Events</td>
                <td>{usage.get('sensor_events', 0):,}</td>
            </tr>
            <tr>
                <td>D&R Evaluations</td>
                <td>{usage.get('detections_generated', 0):,}</td>
            </tr>
            <tr>
                <td>Output Data</td>
                <td>{usage.get('output_bytes_gb', 0)} GB</td>
            </tr>
            <tr>
                <td>Peak Concurrent Sensors</td>
                <td>{usage.get('peak_sensors', 0)}</td>
            </tr>
        </table>
    </div>
"""

    # Configuration
    html += f"""    <div class="card">
        <h2>⚙️ Configuration Summary</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">D&R Rules</div>
                <div class="stat-value">{config.get('dr_rules', 0)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Outputs</div>
                <div class="stat-value">{config.get('outputs', 0)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Tags</div>
                <div class="stat-value">{config.get('tags', 0)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Users</div>
                <div class="stat-value">{config.get('users', 0)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">API Keys</div>
                <div class="stat-value">{config.get('api_keys', 0)}</div>
            </div>
        </div>
    </div>

    <div class="footer">
        Generated by LimaCharlie Reporting Skill
    </div>
</body>
</html>
"""

    return html


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

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    filename = f'executive_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'

    with open(filename, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {filename}")
