#!/usr/bin/env python3
"""
Comprehensive Organization Report Template
Generates detailed operational and security reports for organizations
"""

from limacharlie import Manager
import time
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from jinja2 import Environment, FileSystemLoader


def generate_mssp_report(oid, time_range_days=7, output_format='html'):
    """
    Generate a comprehensive organization report

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

    print(f"Generating comprehensive organization report for {time_range_days} days...")
    print(f"Time range: {datetime.fromtimestamp(start_time, tz=timezone.utc)} to {datetime.fromtimestamp(end_time, tz=timezone.utc)}")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("\n[1/9] Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Detailed sensor statistics
    print("[2/9] Collecting detailed sensor statistics...")
    all_sensors = list(m.sensors())
    online_sensors = m.getAllOnlineSensors()
    # online_sensors is a list of SIDs (strings), not dicts
    online_sids = set(online_sensors) if isinstance(online_sensors, list) else set()

    # Get platform breakdown properly - TWO PASS approach
    # Pass 1: Collect all hostnames for each platform code
    platform_hostnames = defaultdict(list)
    sensor_list = []

    for i, sensor in enumerate(all_sensors):
        if i % 100 == 0:
            print(f"  Processing sensor {i}/{len(all_sensors)}...")

        try:
            info = sensor.getInfo()
            platform_raw = info.get('plat', info.get('ext_plat', 'unknown'))
            hostname = info.get('hostname', 'N/A')
            is_online = sensor.sid in online_sids

            platform_hostnames[str(platform_raw)].append(hostname)
            sensor_list.append({
                'sid': sensor.sid,
                'hostname': hostname,
                'platform_raw': platform_raw,
                'online': is_online,
                'ext_ip': info.get('ext_ip', 'N/A'),
                'last_seen': info.get('last_seen', 0)
            })
        except Exception as e:
            platform_hostnames['error'].append('error')

    # Generate descriptive names for each platform code
    def get_platform_display_name(platform_raw, hostnames):
        """Generate human-readable name based on platform and hostname patterns"""
        platform_str = str(platform_raw)

        # Known string platforms
        if platform_str in ['windows', 'linux', 'macos', 'chrome']:
            return platform_str

        # Numeric platforms - analyze hostname patterns
        if isinstance(platform_raw, int) or platform_str.isdigit():
            # Count hostname patterns
            patterns = {
                'ext': sum(1 for h in hostnames if 'ext-' in h.lower()),
                'test': sum(1 for h in hostnames if 'test' in h.lower()),
                'slack': sum(1 for h in hostnames if 'slack' in h.lower()),
                'office': sum(1 for h in hostnames if 'office' in h.lower()),
                'defender': sum(1 for h in hostnames if 'defender' in h.lower()),
                'demo': sum(1 for h in hostnames if 'demo' in h.lower()),
            }

            # Determine primary category
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
            elif patterns['demo'] > total * 0.5:
                return 'Demo Systems'
            else:
                # Generic adapter name with primary hostname hint
                primary = hostnames[0] if hostnames else 'unknown'
                return f'Adapter ({primary})'

        return platform_str

    # Pass 2: Assign display names and aggregate
    platform_code_to_name = {}
    for platform_raw, hostnames in platform_hostnames.items():
        display_name = get_platform_display_name(platform_raw, hostnames)
        platform_code_to_name[str(platform_raw)] = display_name

    # Build final aggregations
    platforms = defaultdict(int)
    online_platforms = defaultdict(int)
    sensor_details = []
    numeric_platform_samples = defaultdict(list)

    for sensor_info in sensor_list:
        platform_raw = sensor_info['platform_raw']
        platform_display = platform_code_to_name.get(str(platform_raw), str(platform_raw))

        platforms[platform_display] += 1
        if sensor_info['online']:
            online_platforms[platform_display] += 1

        # Track samples for numeric platforms
        if isinstance(platform_raw, int) or str(platform_raw).isdigit():
            if len(numeric_platform_samples[platform_raw]) < 5:
                numeric_platform_samples[platform_raw].append(sensor_info['hostname'])

        sensor_info['platform'] = platform_display
        sensor_details.append(sensor_info)

    data['sensor_stats'] = {
        'total': len(all_sensors),
        'online': len(online_sensors),
        'offline': len(all_sensors) - len(online_sensors),
        'online_percentage': round((len(online_sensors) / len(all_sensors) * 100) if all_sensors else 0, 1),
        'by_platform': dict(platforms),
        'online_by_platform': dict(online_platforms),
        'sensor_details': sensor_details[:20],  # Top 20 for report
        'numeric_platform_info': dict(numeric_platform_samples)  # For reference in report
    }

    # 3. Detection analysis
    print("[3/9] Analyzing detections...")
    try:
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=10000)

        detection_categories = defaultdict(int)
        detection_by_day = defaultdict(int)
        detection_by_rule = defaultdict(int)
        detection_by_sensor = defaultdict(int)
        detection_timeline = []
        detection_count = 0

        for det in detections:
            detection_count += 1
            # Category
            cat = det.get('cat', 'unknown')
            detection_categories[cat] += 1

            # Rule name - use 'source_rule' field which contains the actual rule name
            rule = det.get('source_rule', det.get('cat', 'unknown'))
            detection_by_rule[rule] += 1

            # Sensor
            sid = det.get('sid', 'unknown')
            detection_by_sensor[sid] += 1

            # Timeline
            ts = det.get('timestamp', det.get('ts', 0))
            if ts:
                try:
                    # Handle millisecond timestamps
                    if ts > 1000000000000:  # Milliseconds
                        ts = ts / 1000
                    day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')
                    detection_by_day[day] += 1
                    detection_timeline.append({
                        'timestamp': ts,
                        'date': day,
                        'category': cat,
                        'rule': rule,
                        'sid': sid
                    })
                except (ValueError, OSError) as e:
                    # Skip malformed timestamps
                    pass

        # Get top rules
        top_rules = sorted(detection_by_rule.items(), key=lambda x: x[1], reverse=True)[:10]
        top_sensors = sorted(detection_by_sensor.items(), key=lambda x: x[1], reverse=True)[:10]

        data['detection_summary'] = {
            'total': detection_count,
            'by_category': dict(detection_categories),
            'by_day': dict(sorted(detection_by_day.items())),
            'top_rules': top_rules,
            'top_sensors': top_sensors,
            'avg_per_day': round(detection_count / time_range_days, 1) if time_range_days > 0 else 0,
            'timeline': detection_timeline[:100]  # Last 100
        }
    except Exception as e:
        print(f"  Error collecting detections: {e}")
        data['detection_summary'] = {'error': str(e), 'total': 0}

    # 4. Usage statistics with time series
    print("[4/9] Collecting usage statistics...")
    try:
        usage = m.getUsageStats()
        if 'usage' in usage:
            # Filter to our date range
            start_date = datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%d')
            end_date = datetime.fromtimestamp(end_time, tz=timezone.utc).strftime('%Y-%m-%d')

            filtered_usage = {}
            for date, stats in usage['usage'].items():
                if start_date <= date <= end_date:
                    filtered_usage[date] = stats

            # Calculate trends - combined timeline for Mermaid charts
            event_timeline = []

            for date in sorted(filtered_usage.keys()):
                stats = filtered_usage[date]
                event_timeline.append({
                    'date': date,
                    'events': stats.get('sensor_events', 0),
                    'evaluations': stats.get('replay_num_evals', 0),
                    'output_gb': round(stats.get('output_bytes_tx', 0) / (1024**3), 3)
                })

            # Latest day stats
            if filtered_usage:
                latest_date = max(filtered_usage.keys())
                latest_stats = filtered_usage[latest_date]
            else:
                latest_date = 'N/A'
                latest_stats = {}

            data['usage_summary'] = {
                'date_range': f"{start_date} to {end_date}",
                'latest_date': latest_date,
                'latest_stats': {
                    'sensor_events': latest_stats.get('sensor_events', 0),
                    'detections_generated': latest_stats.get('replay_num_evals', 0),
                    'output_bytes_gb': round(latest_stats.get('output_bytes_tx', 0) / (1024**3), 2),
                    'peak_sensors': latest_stats.get('sensor_watermark', 0)
                },
                'timeline': {
                    'events': event_timeline  # Combined timeline with all metrics
                },
                'totals': {
                    'total_events': sum(s.get('sensor_events', 0) for s in filtered_usage.values()),
                    'total_output_gb': round(sum(s.get('output_bytes_tx', 0) for s in filtered_usage.values()) / (1024**3), 2),
                    'total_evaluations': sum(s.get('replay_num_evals', 0) for s in filtered_usage.values())
                }
            }
    except Exception as e:
        print(f"  Error collecting usage: {e}")
        data['usage_summary'] = {'error': str(e)}

    # 5. D&R Rule effectiveness
    print("[5/9] Analyzing D&R rules...")
    try:
        rules = m.rules()
        namespace_counts = defaultdict(int)

        for rule_path in rules.keys():
            # Extract namespace from rule path (e.g., "namespace/rule_name")
            if '/' in rule_path:
                namespace = rule_path.split('/')[0]
            else:
                namespace = 'general'
            namespace_counts[namespace] += 1

        data['dr_rules'] = {
            'total': len(rules),
            'by_namespace': dict(namespace_counts),
            'sample_rules': list(rules.keys())[:10]
        }
    except Exception as e:
        data['dr_rules'] = {'error': str(e), 'total': 0}

    # 6. False positive analysis
    print("[6/9] Checking false positive rules...")
    try:
        fps = m.fps()
        data['false_positives'] = {
            'total': len(fps),
            'rules': list(fps.keys())[:20]
        }
    except Exception as e:
        data['false_positives'] = {'error': str(e), 'note': 'Requires fp.ctrl permission'}

    # 7. Output health
    print("[7/9] Checking outputs...")
    try:
        outputs = m.outputs()
        output_types = defaultdict(int)

        for output_name, output_config in outputs.items():
            output_type = output_config.get('module', 'unknown') if isinstance(output_config, dict) else 'unknown'
            output_types[output_type] += 1

        data['outputs'] = {
            'total': len(outputs),
            'by_type': dict(output_types),
            'output_names': list(outputs.keys())[:10]
        }
    except Exception as e:
        data['outputs'] = {'error': str(e), 'total': 0}

    # 8. Tags analysis
    print("[8/9] Analyzing tags...")
    try:
        all_tags = m.getAllTags()
        # Count sensors per tag
        tag_usage = {}
        for tag in all_tags[:20]:  # Top 20 tags
            try:
                sensors_with_tag = list(m.sensorsWithTag(tag))
                tag_usage[tag] = len(sensors_with_tag)
            except:
                pass

        data['tags'] = {
            'total': len(all_tags),
            'top_tags': sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    except Exception as e:
        data['tags'] = {'error': str(e), 'total': 0}

    # 9. Configuration summary
    print("[9/9] Collecting configuration summary...")
    try:
        data['config_summary'] = {
            'users': len(m.getUsers()),
            'api_keys': len(m.getApiKeys())
        }
    except Exception as e:
        data['config_summary'] = {'error': str(e)}

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'time_range_days': time_range_days,
        'start_date': datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'end_date': datetime.fromtimestamp(end_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    }

    print("\n✓ Data collection complete. Formatting report...")

    # Format output
    if output_format == 'json':
        return json.dumps(data, indent=2)
    else:
        return render_report(data, output_format)


def render_report(data, output_format='html'):
    """
    Render report using Jinja2 templates with Mermaid charts

    Args:
        data: Dictionary of report data
        output_format: 'html', 'markdown', or 'pdf'

    Returns:
        Rendered report as string (or bytes for PDF)
    """
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

    # Load and render template
    template = env.get_template('mssp_comprehensive.j2')
    rendered_content = template.render(**data)

    # Convert to PDF if requested
    if output_format == 'pdf':
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=rendered_content).write_pdf()
            return pdf_bytes
        except ImportError:
            print("⚠️  Warning: weasyprint not installed. Install with: pip3 install weasyprint")
            print("Returning HTML instead...")
            return rendered_content

    return rendered_content


# Legacy function stubs removed - now using Jinja2 templates
# The old format_markdown and format_html functions have been replaced
# with the render_report function above using Mermaid for all visualizations
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mssp_comprehensive_report.py <OID> [days] [format]")
        print("  format: html (default), markdown, pdf, or json")
        print("Example: python mssp_comprehensive_report.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 html")
        sys.exit(1)

    oid = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    fmt = sys.argv[3] if len(sys.argv) > 3 else 'html'

    # Validate format
    if fmt not in ['html', 'markdown', 'pdf', 'json']:
        print(f"Error: Invalid format '{fmt}'. Must be html, markdown, pdf, or json")
        sys.exit(1)

    # Generate report (PDF conversion handled by render_report function)
    report = generate_mssp_report(oid, days, fmt)

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'pdf' if fmt == 'pdf' else 'json'
    filename = f'mssp_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    # Write binary for PDF, text for others
    mode = 'wb' if isinstance(report, bytes) else 'w'
    with open(filepath, mode) as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
