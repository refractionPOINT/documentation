#!/usr/bin/env python3
"""
Sensor Health Report Template
Generates comprehensive operational health report for LimaCharlie sensors
"""

from limacharlie import Manager
import time
import json
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter


def generate_sensor_health_report(oid, output_format='html'):
    """
    Generate a comprehensive sensor health report

    Args:
        oid: Organization ID
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    m = Manager(oid=oid)

    print(f"Generating sensor health report...")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("\n[1/6] Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Collect all sensor data with caching
    print("[2/6] Collecting sensor data...")
    all_sensors = list(m.sensors())
    online_sensors = m.getAllOnlineSensors()
    online_sids = set(online_sensors) if isinstance(online_sensors, list) else set()

    # Pass 1: Collect sensor info and hostname patterns
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

            # Calculate offline duration - check 'alive' field first (datetime string), then 'last_seen' (timestamp)
            offline_hours = 0
            last_seen_timestamp = 0
            last_seen_str = 'Never'

            if not is_online:
                # Try 'alive' field first (datetime string format: "2025-10-01 17:08:10")
                alive_str = info.get('alive', '')
                if alive_str:
                    try:
                        # Parse datetime string (format: "YYYY-MM-DD HH:MM:SS")
                        alive_dt = datetime.strptime(alive_str, '%Y-%m-%d %H:%M:%S')
                        # Make timezone-aware (assume UTC)
                        alive_dt = alive_dt.replace(tzinfo=timezone.utc)
                        last_seen_timestamp = alive_dt.timestamp()
                        offline_hours = (current_time - last_seen_timestamp) / 3600
                        last_seen_str = alive_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except Exception as e:
                        # Fall back to last_seen field
                        last_seen = info.get('last_seen', 0)
                        if last_seen > 0:
                            # Normalize timestamp (could be seconds or milliseconds)
                            if last_seen > 10000000000:  # Milliseconds
                                last_seen = last_seen / 1000
                            last_seen_timestamp = last_seen
                            offline_hours = (current_time - last_seen) / 3600
                            last_seen_str = datetime.fromtimestamp(last_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                else:
                    # Try last_seen as fallback
                    last_seen = info.get('last_seen', 0)
                    if last_seen > 0:
                        # Normalize timestamp (could be seconds or milliseconds)
                        if last_seen > 10000000000:  # Milliseconds
                            last_seen = last_seen / 1000
                        last_seen_timestamp = last_seen
                        offline_hours = (current_time - last_seen) / 3600
                        last_seen_str = datetime.fromtimestamp(last_seen, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            # Extract version info
            agent_version = info.get('sensor_seed_key', 'unknown')
            if agent_version != 'unknown':
                # Extract version number from seed key if possible
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
                'ext_ip': info.get('ext_ip', 'N/A'),
                'int_ip': info.get('int_ip', 'N/A'),
                'last_seen_timestamp': last_seen_timestamp,
                'last_seen_str': last_seen_str,
                'offline_hours': offline_hours,
                'tags': tags,
                'version': agent_version,
                'os_version': info.get('os_version', 'N/A'),
                'architecture': info.get('architecture', 'N/A'),
            })
        except Exception as e:
            print(f"  Error processing sensor {i}: {e}")
            platform_hostnames['error'].append('error')

    print(f"  Processed {len(sensor_data)} sensors")

    # Pass 2: Generate descriptive platform names
    print("[3/6] Analyzing platform distribution...")
    def get_platform_display_name(platform_raw, hostnames):
        """Generate human-readable name based on platform and hostname patterns"""
        platform_str = str(platform_raw)

        # Known string platforms
        if platform_str in ['windows', 'linux', 'macos', 'chrome']:
            return platform_str.capitalize()

        # Numeric platforms - analyze hostname patterns
        if isinstance(platform_raw, int) or platform_str.isdigit():
            patterns = {
                'ext': sum(1 for h in hostnames if 'ext-' in h.lower()),
                'test': sum(1 for h in hostnames if 'test' in h.lower() or 'parser' in h.lower()),
                'slack': sum(1 for h in hostnames if 'slack' in h.lower()),
                'office': sum(1 for h in hostnames if 'office' in h.lower()),
                'defender': sum(1 for h in hostnames if 'defender' in h.lower()),
                'github': sum(1 for h in hostnames if 'github' in h.lower()),
                'gcp': sum(1 for h in hostnames if 'gcp' in h.lower()),
                'aws': sum(1 for h in hostnames if 'aws' in h.lower()),
            }

            total = len(hostnames)
            if patterns['ext'] > total * 0.5:
                return 'LimaCharlie Extensions'
            elif patterns['test'] > total * 0.5:
                return 'Test/Parser Systems'
            elif patterns['slack'] > 0:
                return 'Slack Integration'
            elif patterns['office'] > 0:
                return 'Office365 Integration'
            elif patterns['defender'] > 0:
                return 'Defender Integration'
            elif patterns['github'] > 0:
                return 'GitHub Integration'
            elif patterns['gcp'] > 0:
                return 'GCP Integration'
            elif patterns['aws'] > 0:
                return 'AWS Integration'

        return f"Platform {platform_str}"

    # Build platform statistics
    platform_stats = {}
    for platform_raw, hostnames in platform_hostnames.items():
        platform_name = get_platform_display_name(platform_raw, hostnames)
        platform_sensors = [s for s in sensor_data if str(s['platform_raw']) == platform_raw]
        online_count = sum(1 for s in platform_sensors if s['online'])

        platform_stats[platform_name] = {
            'total': len(platform_sensors),
            'online': online_count,
            'offline': len(platform_sensors) - online_count,
            'availability': (online_count / len(platform_sensors) * 100) if len(platform_sensors) > 0 else 0,
            'sample_hostnames': hostnames[:3]
        }

    data['platform_stats'] = dict(sorted(platform_stats.items(), key=lambda x: x[1]['total'], reverse=True))

    # 3. Tag analysis
    print("[4/6] Analyzing tags...")
    tag_stats = {}
    for tag, hostnames in tag_sensor_map.items():
        tag_sensors = [s for s in sensor_data if tag in s['tags']]
        online_count = sum(1 for s in tag_sensors if s['online'])

        tag_stats[tag] = {
            'total': len(tag_sensors),
            'online': online_count,
            'offline': len(tag_sensors) - online_count,
            'sample_hostnames': hostnames[:3]
        }

    data['tag_stats'] = dict(sorted(tag_stats.items(), key=lambda x: x[1]['total'], reverse=True))

    # Sensors without tags
    untagged_sensors = [s for s in sensor_data if not s['tags']]
    data['untagged_count'] = len(untagged_sensors)
    data['untagged_sample'] = [s['hostname'] for s in untagged_sensors[:5]]

    # 4. Stale sensor detection
    print("[5/6] Identifying stale sensors...")
    stale_categories = {
        'offline_24h': [],  # Offline 1-7 days
        'offline_7d': [],   # Offline 7-30 days
        'offline_30d': []   # Offline >30 days
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

            if hours > 30 * 24:  # >30 days
                stale_categories['offline_30d'].append(sensor_info)
            elif hours > 7 * 24:  # 7-30 days
                stale_categories['offline_7d'].append(sensor_info)
            elif hours > 24:  # 1-7 days
                stale_categories['offline_24h'].append(sensor_info)

    data['stale_sensors'] = stale_categories

    # 5. Version distribution
    print("[6/6] Analyzing version distribution...")
    data['version_distribution'] = dict(version_counts.most_common(10))

    # Summary statistics
    data['summary'] = {
        'total_sensors': len(sensor_data),
        'online_sensors': len([s for s in sensor_data if s['online']]),
        'offline_sensors': len([s for s in sensor_data if not s['online']]),
        'availability_percentage': (len([s for s in sensor_data if s['online']]) / len(sensor_data) * 100) if len(sensor_data) > 0 else 0,
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

    # Generate output in requested format
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    elif output_format == 'markdown':
        return generate_markdown_report(data)
    else:  # html
        return generate_html_report(data)


def generate_markdown_report(data):
    """Generate markdown formatted report"""
    md = []
    summary = data['summary']

    md.append(f"# Sensor Health Report")
    md.append(f"")
    md.append(f"**Organization**: {summary['org_name']}")
    md.append(f"**Generated**: {summary['report_generated']}")
    md.append(f"")

    # Executive Summary
    md.append(f"## 📊 Executive Summary")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Sensors | {summary['total_sensors']:,} |")
    md.append(f"| Online | {summary['online_sensors']:,} ({summary['availability_percentage']:.1f}%) |")
    md.append(f"| Offline | {summary['offline_sensors']:,} |")
    md.append(f"| Platforms | {summary['platform_count']} |")
    md.append(f"| Tags | {summary['tag_count']} |")
    md.append(f"| Untagged Sensors | {summary['untagged_count']} |")
    md.append(f"")

    # Platform Distribution
    md.append(f"## 🖥️ Platform Distribution")
    md.append(f"")
    md.append(f"| Platform | Total | Online | Offline | Availability |")
    md.append(f"|----------|-------|--------|---------|--------------|")
    for platform, stats in data['platform_stats'].items():
        md.append(f"| {platform} | {stats['total']} | {stats['online']} | {stats['offline']} | {stats['availability']:.1f}% |")
    md.append(f"")

    # Stale Sensors
    md.append(f"## ⚠️ Stale Sensors")
    md.append(f"")
    md.append(f"| Category | Count |")
    md.append(f"|----------|-------|")
    md.append(f"| Offline 1-7 days | {summary['stale_24h_count']} |")
    md.append(f"| Offline 7-30 days | {summary['stale_7d_count']} |")
    md.append(f"| Offline >30 days | {summary['stale_30d_count']} |")
    md.append(f"")

    # Show stale sensors by category
    for category_name, category_label in [('offline_30d', 'Offline >30 Days'), ('offline_7d', 'Offline 7-30 Days'), ('offline_24h', 'Offline 1-7 Days')]:
        sensors = data['stale_sensors'][category_name]
        if sensors:
            md.append(f"### {category_label} ({len(sensors)} sensors)")
            md.append(f"")
            md.append(f"| Hostname | Offline Duration | Last Seen | Tags |")
            md.append(f"|----------|------------------|-----------|------|")
            for sensor in sensors[:10]:  # Limit to top 10
                md.append(f"| {sensor['hostname']} | {sensor['offline_days']:.1f} days | {sensor['last_seen']} | {sensor['tags']} |")
            if len(sensors) > 10:
                md.append(f"")
                md.append(f"*...and {len(sensors) - 10} more*")
            md.append(f"")

    # Tag Distribution
    if data['tag_stats']:
        md.append(f"## 🏷️ Tag Distribution (Top 10)")
        md.append(f"")
        md.append(f"| Tag | Sensors | Online | Offline |")
        md.append(f"|-----|---------|--------|---------|")
        for tag, stats in list(data['tag_stats'].items())[:10]:
            md.append(f"| {tag} | {stats['total']} | {stats['online']} | {stats['offline']} |")
        md.append(f"")

    # Untagged Sensors
    if data['untagged_count'] > 0:
        md.append(f"## 📝 Untagged Sensors")
        md.append(f"")
        md.append(f"**Total untagged**: {data['untagged_count']}")
        md.append(f"")
        md.append(f"**Sample hostnames**: {', '.join(data['untagged_sample'])}")
        md.append(f"")

    # Version Distribution
    if data['version_distribution']:
        md.append(f"## 📦 Version Distribution (Top 10)")
        md.append(f"")
        md.append(f"| Version | Count |")
        md.append(f"|---------|-------|")
        for version, count in data['version_distribution'].items():
            md.append(f"| {version} | {count} |")
        md.append(f"")

    # Recommendations
    md.append(f"## 💡 Recommendations")
    md.append(f"")
    recommendations = []

    if summary['stale_30d_count'] > 0:
        recommendations.append(f"- **{summary['stale_30d_count']} sensors offline >30 days**: Consider removing or investigating these sensors")

    if summary['stale_7d_count'] > 0:
        recommendations.append(f"- **{summary['stale_7d_count']} sensors offline 7-30 days**: Review and potentially restart or reinstall")

    if summary['untagged_count'] > 10:
        recommendations.append(f"- **{summary['untagged_count']} untagged sensors**: Apply organizational tags for better management")

    if summary['availability_percentage'] < 90:
        recommendations.append(f"- **Availability at {summary['availability_percentage']:.1f}%**: Target 95%+ sensor uptime for optimal coverage")

    if len(data['version_distribution']) > 5:
        recommendations.append(f"- **Multiple versions detected**: Consider standardizing sensor versions for consistency")

    if not recommendations:
        recommendations.append("- ✅ Sensor fleet is healthy! No immediate actions required.")

    md.extend(recommendations)
    md.append(f"")

    md.append(f"---")
    md.append(f"*Generated by LimaCharlie Sensor Health Report*")

    return '\n'.join(md)


def generate_html_report(data):
    """Generate HTML formatted report with charts"""
    summary = data['summary']

    # Prepare chart data
    platform_labels = list(data['platform_stats'].keys())
    platform_totals = [data['platform_stats'][p]['total'] for p in platform_labels]
    platform_online = [data['platform_stats'][p]['online'] for p in platform_labels]
    platform_offline = [data['platform_stats'][p]['offline'] for p in platform_labels]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Health Report - {summary['org_name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #667eea;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: white;
            margin: 0 0 10px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .summary-card .subtitle {{
            font-size: 14px;
            color: #999;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .availability-good {{ color: #28a745; }}
        .availability-warning {{ color: #ffc107; }}
        .availability-critical {{ color: #dc3545; }}
        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-online {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-offline {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Sensor Health Report</h1>
        <p><strong>Organization:</strong> {summary['org_name']}</p>
        <p><strong>Generated:</strong> {summary['report_generated']}</p>
        <p><strong>Total Sensors:</strong> {summary['total_sensors']:,}</p>
    </div>

    <div class="summary-grid">
        <div class="summary-card">
            <h3>Online Sensors</h3>
            <div class="value">{summary['online_sensors']:,}</div>
            <div class="subtitle">{summary['availability_percentage']:.1f}% availability</div>
        </div>
        <div class="summary-card">
            <h3>Offline Sensors</h3>
            <div class="value">{summary['offline_sensors']:,}</div>
            <div class="subtitle">Need attention</div>
        </div>
        <div class="summary-card">
            <h3>Platforms</h3>
            <div class="value">{summary['platform_count']}</div>
            <div class="subtitle">Different types</div>
        </div>
        <div class="summary-card">
            <h3>Stale Sensors</h3>
            <div class="value">{summary['stale_30d_count']}</div>
            <div class="subtitle">Offline >30 days</div>
        </div>
        <div class="summary-card">
            <h3>Tags</h3>
            <div class="value">{summary['tag_count']}</div>
            <div class="subtitle">{summary['untagged_count']} untagged</div>
        </div>
    </div>

    <div class="section">
        <h2>🖥️ Platform Distribution</h2>
        <div class="chart-container">
            <canvas id="platformChart"></canvas>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Platform</th>
                    <th>Total</th>
                    <th>Online</th>
                    <th>Offline</th>
                    <th>Availability</th>
                    <th>Sample Hostnames</th>
                </tr>
            </thead>
            <tbody>
"""

    for platform, stats in data['platform_stats'].items():
        avail_class = 'availability-good' if stats['availability'] >= 90 else ('availability-warning' if stats['availability'] >= 70 else 'availability-critical')
        sample_hosts = ', '.join(stats['sample_hostnames'])
        html += f"""                <tr>
                    <td><strong>{platform}</strong></td>
                    <td>{stats['total']}</td>
                    <td><span class="badge badge-online">{stats['online']}</span></td>
                    <td><span class="badge badge-offline">{stats['offline']}</span></td>
                    <td class="{avail_class}"><strong>{stats['availability']:.1f}%</strong></td>
                    <td><small>{sample_hosts}</small></td>
                </tr>
"""

    html += """            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>⚠️ Stale Sensors</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Offline 1-7 Days</h3>
                <div class="value" style="color: #ffc107;">{stale_24h_count}</div>
            </div>
            <div class="summary-card">
                <h3>Offline 7-30 Days</h3>
                <div class="value" style="color: #ff9800;">{stale_7d_count}</div>
            </div>
            <div class="summary-card">
                <h3>Offline >30 Days</h3>
                <div class="value" style="color: #dc3545;">{stale_30d_count}</div>
            </div>
        </div>
""".format(
        stale_24h_count=summary['stale_24h_count'],
        stale_7d_count=summary['stale_7d_count'],
        stale_30d_count=summary['stale_30d_count']
    )

    # Add stale sensor tables
    for category_name, category_label in [('offline_30d', 'Offline >30 Days'), ('offline_7d', 'Offline 7-30 Days'), ('offline_24h', 'Offline 1-7 Days')]:
        sensors = data['stale_sensors'][category_name]
        if sensors:
            html += f"""
        <h3>{category_label} ({len(sensors)} sensors)</h3>
        <table>
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>Offline Duration</th>
                    <th>Last Seen</th>
                    <th>Tags</th>
                </tr>
            </thead>
            <tbody>
"""
            for sensor in sensors[:20]:  # Limit to top 20
                html += f"""                <tr>
                    <td>{sensor['hostname']}</td>
                    <td>{sensor['offline_days']:.1f} days ({sensor['offline_hours']:.0f} hours)</td>
                    <td><small>{sensor['last_seen']}</small></td>
                    <td><small>{sensor['tags']}</small></td>
                </tr>
"""
            if len(sensors) > 20:
                html += f"""                <tr>
                    <td colspan="4"><em>...and {len(sensors) - 20} more sensors</em></td>
                </tr>
"""
            html += """            </tbody>
        </table>
"""

    html += """    </div>
"""

    # Tag distribution
    if data['tag_stats']:
        html += """
    <div class="section">
        <h2>🏷️ Tag Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Tag</th>
                    <th>Sensors</th>
                    <th>Online</th>
                    <th>Offline</th>
                    <th>Sample Hostnames</th>
                </tr>
            </thead>
            <tbody>
"""
        for tag, stats in list(data['tag_stats'].items())[:15]:
            sample_hosts = ', '.join(stats['sample_hostnames'])
            html += f"""                <tr>
                    <td><strong>{tag}</strong></td>
                    <td>{stats['total']}</td>
                    <td><span class="badge badge-online">{stats['online']}</span></td>
                    <td><span class="badge badge-offline">{stats['offline']}</span></td>
                    <td><small>{sample_hosts}</small></td>
                </tr>
"""
        html += """            </tbody>
        </table>
    </div>
"""

    # Untagged sensors
    if data['untagged_count'] > 0:
        html += f"""
    <div class="section">
        <h2>📝 Untagged Sensors</h2>
        <p><strong>Total untagged:</strong> {data['untagged_count']}</p>
        <p><strong>Sample hostnames:</strong> {', '.join(data['untagged_sample'])}</p>
    </div>
"""

    # Version distribution
    if data['version_distribution']:
        html += """
    <div class="section">
        <h2>📦 Version Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Version</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
"""
        for version, count in data['version_distribution'].items():
            html += f"""                <tr>
                    <td><code>{version}</code></td>
                    <td>{count}</td>
                </tr>
"""
        html += """            </tbody>
        </table>
    </div>
"""

    # Recommendations
    html += """
    <div class="section">
        <h2>💡 Recommendations</h2>
        <div class="recommendations">
            <ul>
"""

    recommendations = []
    if summary['stale_30d_count'] > 0:
        recommendations.append(f"<strong>{summary['stale_30d_count']} sensors offline >30 days:</strong> Consider removing or investigating these sensors")

    if summary['stale_7d_count'] > 0:
        recommendations.append(f"<strong>{summary['stale_7d_count']} sensors offline 7-30 days:</strong> Review and potentially restart or reinstall")

    if summary['untagged_count'] > 10:
        recommendations.append(f"<strong>{summary['untagged_count']} untagged sensors:</strong> Apply organizational tags for better management")

    if summary['availability_percentage'] < 90:
        recommendations.append(f"<strong>Availability at {summary['availability_percentage']:.1f}%:</strong> Target 95%+ sensor uptime for optimal coverage")

    if len(data['version_distribution']) > 5:
        recommendations.append(f"<strong>Multiple versions detected:</strong> Consider standardizing sensor versions for consistency")

    if not recommendations:
        recommendations.append("✅ <strong>Sensor fleet is healthy!</strong> No immediate actions required.")

    for rec in recommendations:
        html += f"                <li>{rec}</li>\n"

    html += """            </ul>
        </div>
    </div>

    <script>
        // Platform distribution chart
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        new Chart(platformCtx, {
            type: 'bar',
            data: {
                labels: """ + json.dumps(platform_labels) + """,
                datasets: [
                    {
                        label: 'Online',
                        data: """ + json.dumps(platform_online) + """,
                        backgroundColor: 'rgba(40, 167, 69, 0.7)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Offline',
                        data: """ + json.dumps(platform_offline) + """,
                        backgroundColor: 'rgba(220, 53, 69, 0.7)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Sensor Status by Platform'
                    }
                }
            }
        });
    </script>

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
        <p>Generated by LimaCharlie Sensor Health Report</p>
    </footer>
</body>
</html>
"""

    return html


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 sensor_health_report.py <OID> [format]")
        print("  format: 'html' (default), 'markdown', or 'json'")
        sys.exit(1)

    oid = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'html'

    report = generate_sensor_health_report(oid, output_format=output_format)

    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if output_format == 'json':
        filename = f'sensor_health_{timestamp}.json'
    elif output_format == 'markdown':
        filename = f'sensor_health_{timestamp}.md'
    else:
        filename = f'sensor_health_{timestamp}.html'

    with open(filename, 'w') as f:
        f.write(report)

    print(f"\n✅ Report generated: {filename}")
