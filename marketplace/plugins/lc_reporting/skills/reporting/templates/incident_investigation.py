#!/usr/bin/env python3
"""
Incident Investigation Report Template
Provides detailed forensic analysis for security incident investigation
"""

from limacharlie import Manager
import time
import json
import os
from datetime import datetime, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader


def generate_incident_investigation_report(oid, sensor_id=None, start_time=None, end_time=None,
                                           iocs=None, detection_category=None, output_format='html'):
    """
    Generate an incident investigation report for a LimaCharlie organization

    Args:
        oid: Organization ID
        sensor_id: Specific sensor ID to investigate (optional)
        start_time: Investigation start timestamp (optional, defaults to 24h ago)
        end_time: Investigation end timestamp (optional, defaults to now)
        iocs: List of IOCs to search for (optional)
        detection_category: Specific detection category to focus on (optional)
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    m = Manager(oid=oid)

    # Set default time range (last 24 hours)
    if end_time is None:
        end_time = int(time.time())
    if start_time is None:
        start_time = end_time - (24 * 3600)  # 24 hours ago

    print(f"Generating incident investigation report...")
    print(f"  Time range: {datetime.fromtimestamp(start_time, tz=timezone.utc)} to {datetime.fromtimestamp(end_time, tz=timezone.utc)}")
    if sensor_id:
        print(f"  Focused on sensor: {sensor_id}")
    if detection_category:
        print(f"  Detection category: {detection_category}")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Investigation scope
    data['investigation_scope'] = {
        'sensor_id': sensor_id,
        'start_time': start_time,
        'end_time': end_time,
        'start_date': datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
        'end_date': datetime.fromtimestamp(end_time, tz=timezone.utc).isoformat(),
        'duration_hours': round((end_time - start_time) / 3600, 1),
        'iocs': iocs if iocs else [],
        'detection_category': detection_category
    }

    # 3. Sensor information (if specific sensor provided)
    if sensor_id:
        print(f"Collecting sensor information for {sensor_id}...")
        try:
            sensor = m.sensor(sensor_id)
            sensor_info = sensor.getInfo()

            data['sensor_info'] = {
                'sid': sensor_id,
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
            data['sensor_info'] = {
                'sid': sensor_id,
                'error': str(e)
            }
    else:
        data['sensor_info'] = None

    # 4. Related Detections
    print("Collecting related detections...")
    try:
        # Use higher limit for investigation reports
        detection_limit = 5000
        detections = m.getHistoricDetections(start=start_time, end=end_time, limit=detection_limit)

        detection_list = []
        detection_timeline = defaultdict(int)
        detection_by_category = defaultdict(int)
        affected_sensors = set()

        for det in detections:
            # Filter by sensor if specified
            det_sensor_id = det.get('routing', {}).get('sid', 'unknown')
            if sensor_id and det_sensor_id != sensor_id:
                continue

            # Filter by category if specified
            det_category = det.get('cat', 'unknown')
            if detection_category and det_category != detection_category:
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

            # Count by category
            detection_by_category[det_category] += 1

            # Track affected sensors
            affected_sensors.add(det_sensor_id)

            # Store detection details
            detection_list.append({
                'timestamp': ts if ts else 0,
                'timestamp_str': datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else 'unknown',
                'category': det_category,
                'rule': det.get('source_rule', 'unknown'),
                'sensor_id': det_sensor_id,
                'severity': det.get('severity', 0),
                'summary': det.get('summary', 'No summary available')
            })

        # Sort detections by timestamp (most recent first)
        detection_list.sort(key=lambda x: x['timestamp'], reverse=True)

        # Check if we hit the limit (might have more detections)
        hit_limit = len(detection_list) >= detection_limit
        limit_warning = f"Showing first {detection_limit} detections (limit reached, more may exist)" if hit_limit else None

        data['detections'] = {
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
        data['detections'] = {
            'total': 0,
            'list': [],
            'timeline': {},
            'by_category': {},
            'affected_sensor_count': 0,
            'affected_sensors': []
        }

    # 5. IOC Search (if IOCs provided)
    if iocs and len(iocs) > 0:
        print(f"Searching for {len(iocs)} IOCs...")
        ioc_results = []

        for ioc in iocs:
            try:
                # Search for IOC in detection data
                # Note: Full IOC search would require Insight/historic events
                # For now, search in detection summaries
                matches = []
                for det in data['detections']['list']:
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
                    'error': str(e)
                })

        data['ioc_search'] = {
            'total_iocs': len(iocs),
            'results': ioc_results
        }
    else:
        data['ioc_search'] = None

    # Note: Additional telemetry like network connections, process trees, etc.
    # would require querying historic events which may have org-specific retention policies

    # 8. Recommendations
    print("Generating recommendations...")
    recommendations = []

    # Based on detection count
    if data['detections']['total'] > 50:
        recommendations.append({
            'priority': 'high',
            'category': 'Volume',
            'recommendation': f"High detection volume ({data['detections']['total']} detections). Review for potential compromise or misconfiguration."
        })

    # Based on affected sensors
    if data['detections']['affected_sensor_count'] > 5:
        recommendations.append({
            'priority': 'high',
            'category': 'Lateral Movement',
            'recommendation': f"Multiple sensors affected ({data['detections']['affected_sensor_count']}). Investigate for lateral movement."
        })

    # Based on categories
    high_risk_categories = ['ransomware', 'malware', 'trojan', 'backdoor', 'exploit']
    for category in data['detections']['by_category'].keys():
        if any(risk in category.lower() for risk in high_risk_categories):
            recommendations.append({
                'priority': 'critical',
                'category': 'Threat Type',
                'recommendation': f"High-risk detection category detected: {category}. Immediate investigation required."
            })

    # General recommendations
    if data['detections']['total'] > 0:
        recommendations.append({
            'priority': 'medium',
            'category': 'Investigation',
            'recommendation': 'Review detection timeline for patterns and correlation with known security events.'
        })
        recommendations.append({
            'priority': 'medium',
            'category': 'Containment',
            'recommendation': 'Consider isolating affected sensors if malicious activity is confirmed.'
        })

    data['recommendations'] = recommendations

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'report_type': 'Incident Investigation'
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
    md.append("# LimaCharlie Incident Investigation Report\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")

    # Organization
    org = data['org_info']
    md.append(f"**Organization**: {org.get('name', 'N/A')} ({org.get('oid', 'N/A')})\n")

    # Investigation Scope
    scope = data['investigation_scope']
    md.append("## Investigation Scope")
    md.append(f"- **Time Range**: {scope['start_date']} to {scope['end_date']}")
    md.append(f"- **Duration**: {scope['duration_hours']} hours")
    if scope['sensor_id']:
        md.append(f"- **Target Sensor**: {scope['sensor_id']}")
    if scope['detection_category']:
        md.append(f"- **Detection Category**: {scope['detection_category']}")
    md.append("")

    # Detections Summary
    det = data['detections']
    md.append("## Detections Summary")
    md.append(f"- **Total Detections**: {det['total']}")
    md.append(f"- **Affected Sensors**: {det['affected_sensor_count']}")
    md.append("")

    # Recommendations
    if data['recommendations']:
        md.append("## Recommendations")
        for rec in data['recommendations']:
            md.append(f"- **[{rec['priority'].upper()}]** {rec['category']}: {rec['recommendation']}")
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
    template = env.get_template('incident_investigation.j2')
    return template.render(**data)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python incident_investigation.py <OID> [sensor_id] [hours_back] [format]")
        print("Example: python incident_investigation.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd bb4b30af-ff11-4ff4-836f-f014ada33345 24 html")
        print("\nOptional: Specify detection category with --category=<category>")
        print("Optional: Specify IOCs with --ioc=<ioc1,ioc2,...>")
        sys.exit(1)

    oid = sys.argv[1]

    # Parse arguments more carefully
    sensor_id = None
    hours_back = 24
    fmt = 'html'

    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg.startswith('--'):
            continue  # Skip option flags
        elif arg.isdigit():
            hours_back = int(arg)
        elif arg in ['html', 'markdown', 'json']:
            fmt = arg
        elif len(arg) > 16 and '-' in arg:  # Looks like a UUID
            sensor_id = arg
        elif i == 2:  # First positional arg could be sensor_id
            sensor_id = arg

    # Parse optional parameters
    detection_category = None
    iocs = None
    for arg in sys.argv:
        if arg.startswith('--category='):
            detection_category = arg.split('=')[1]
        elif arg.startswith('--ioc='):
            iocs = arg.split('=')[1].split(',')

    # Calculate time range
    end_time = int(time.time())
    start_time = end_time - (hours_back * 3600)

    report = generate_incident_investigation_report(
        oid=oid,
        sensor_id=sensor_id,
        start_time=start_time,
        end_time=end_time,
        iocs=iocs,
        detection_category=detection_category,
        output_format=fmt
    )

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sensor_suffix = f"_{sensor_id[:8]}" if sensor_id else ""
    filename = f'incident_investigation{sensor_suffix}_{timestamp}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
