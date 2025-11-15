#!/usr/bin/env python3
"""
Multi-Tenant Billing Report
Generates billing overview across all accessible organizations
"""

from limacharlie import Manager
import time
import json
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from chart_utils import generate_static_chart, should_use_static_charts


def generate_billing_report(time_range_days=30, output_format='html'):
    """
    Generate a multi-tenant billing report

    Args:
        time_range_days: Number of days to analyze (default: 30)
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    print(f"Generating multi-tenant billing report for {time_range_days} days...")

    # Get all accessible organizations
    m = Manager()
    orgs_data = m.userAccessibleOrgs()
    org_oids = orgs_data.get('orgs', [])
    org_names = orgs_data.get('names', {})

    print(f"Found {len(org_oids)} organizations to analyze\n")

    # Calculate time range
    end_time = int(time.time())
    start_time = end_time - (time_range_days * 24 * 3600)
    start_date = datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%d')
    end_date = datetime.fromtimestamp(end_time, tz=timezone.utc).strftime('%Y-%m-%d')

    # Collect data for all orgs
    all_orgs_data = []
    totals = {
        'total_events': 0,
        'total_output_gb': 0,
        'total_evaluations': 0,
        'total_sensors': 0,
        'total_estimated_cost': 0
    }

    for i, oid in enumerate(org_oids, 1):
        org_name = org_names.get(oid, 'Unknown')
        print(f"[{i}/{len(org_oids)}] Processing {org_name}...")

        try:
            m_org = Manager(oid=oid)

            # Get org info
            org_info = m_org.getOrgInfo()
            sensor_count = len(list(m_org.sensors()))

            # Get usage stats
            usage = m_org.getUsageStats()

            # Aggregate usage for the time period
            org_usage = {
                'events': 0,
                'output_bytes': 0,
                'evaluations': 0,
                'peak_sensors': 0,
                'daily_breakdown': []
            }

            if 'usage' in usage:
                for date_str, stats in sorted(usage['usage'].items()):
                    if start_date <= date_str <= end_date:
                        org_usage['events'] += stats.get('sensor_events', 0)
                        org_usage['output_bytes'] += stats.get('output_bytes_tx', 0)
                        org_usage['evaluations'] += stats.get('replay_num_evals', 0)
                        org_usage['peak_sensors'] = max(org_usage['peak_sensors'], stats.get('sensor_watermark', 0))

                        org_usage['daily_breakdown'].append({
                            'date': date_str,
                            'events': stats.get('sensor_events', 0),
                            'output_gb': round(stats.get('output_bytes_tx', 0) / (1024**3), 3),
                            'evaluations': stats.get('replay_num_evals', 0)
                        })

            # Convert bytes to GB
            output_gb = org_usage['output_bytes'] / (1024**3)

            # Estimate costs (approximate LimaCharlie pricing)
            # Note: Actual pricing varies by plan and should be confirmed with billing
            estimated_cost = (
                (sensor_count * 5) +  # $5/sensor/month (approximate)
                (output_gb * 0.20) +  # $0.20/GB (approximate)
                (org_usage['evaluations'] / 1000 * 0.001)  # $0.001 per 1k evals (approximate)
            )

            org_data = {
                'oid': oid,
                'name': org_name,
                'sensor_quota': org_info.get('sensor_quota', 0),
                'sensor_count': sensor_count,
                'peak_sensors': org_usage['peak_sensors'],
                'total_events': org_usage['events'],
                'total_output_gb': round(output_gb, 2),
                'total_evaluations': org_usage['evaluations'],
                'estimated_cost': round(estimated_cost, 2),
                'daily_breakdown': org_usage['daily_breakdown'][-7:]  # Last 7 days
            }

            all_orgs_data.append(org_data)

            # Add to totals
            totals['total_events'] += org_usage['events']
            totals['total_output_gb'] += output_gb
            totals['total_evaluations'] += org_usage['evaluations']
            totals['total_sensors'] += sensor_count
            totals['total_estimated_cost'] += estimated_cost

        except Exception as e:
            print(f"  Error processing {org_name}: {e}")
            all_orgs_data.append({
                'oid': oid,
                'name': org_name,
                'error': str(e)
            })

    # Prepare final data structure
    data = {
        'report_metadata': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'time_range_days': time_range_days,
            'start_date': start_date,
            'end_date': end_date,
            'org_count': len(org_oids)
        },
        'totals': {
            'total_events': totals['total_events'],
            'total_output_gb': round(totals['total_output_gb'], 2),
            'total_evaluations': totals['total_evaluations'],
            'total_sensors': totals['total_sensors'],
            'estimated_monthly_cost': round(totals['total_estimated_cost'], 2)
        },
        'organizations': all_orgs_data
    }

    print("\n✓ Data collection complete. Formatting report...")

    # Format output
    if output_format == 'json':
        return json.dumps(data, indent=2)
    elif output_format == 'markdown':
        return format_markdown(data)
    else:  # html
        return format_html(data, output_format)


def format_markdown(data):
    """Format data as Markdown report"""
    md = []
    md.append("# Multi-Tenant Billing Report\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")
    md.append(f"**Period**: {meta['start_date']} to {meta['end_date']} ({meta['time_range_days']} days)")
    md.append(f"**Organizations**: {meta['org_count']}\n")

    # Totals Overview
    totals = data['totals']
    md.append("## 📊 Cross-Tenant Summary\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| Total Sensors | {totals['total_sensors']} |")
    md.append(f"| Total Events | {totals['total_events']:,} |")
    md.append(f"| Total Data Output | {totals['total_output_gb']:.2f} GB |")
    md.append(f"| Total Evaluations | {totals['total_evaluations']:,} |")
    md.append(f"| **Estimated Monthly Cost** | **${totals['estimated_monthly_cost']:.2f}** |")
    md.append("")

    # Organization Overview
    md.append("## 🏢 Organization Overview\n")
    md.append("| Organization | Sensors | Events | Output (GB) | Est. Cost |")
    md.append("|-------------|---------|--------|-------------|-----------|")

    for org in sorted(data['organizations'], key=lambda x: x.get('estimated_cost', 0), reverse=True):
        if 'error' in org:
            md.append(f"| {org['name']} | - | - | - | Error |")
        else:
            md.append(f"| {org['name']} | {org['sensor_count']}/{org['sensor_quota']} | {org['total_events']:,} | {org['total_output_gb']:.2f} | ${org['estimated_cost']:.2f} |")
    md.append("")

    # Detailed breakdown for each org
    md.append("## 📈 Detailed Organization Breakdown\n")

    for org in data['organizations']:
        if 'error' in org:
            md.append(f"### {org['name']}")
            md.append(f"**Error**: {org['error']}\n")
            continue

        md.append(f"### {org['name']}\n")
        md.append(f"**Organization ID**: `{org['oid']}`\n")

        md.append("#### Key Metrics")
        md.append(f"- **Sensors**: {org['sensor_count']} / {org['sensor_quota']} quota")
        md.append(f"- **Peak Sensors**: {org['peak_sensors']}")
        md.append(f"- **Total Events**: {org['total_events']:,}")
        md.append(f"- **Data Output**: {org['total_output_gb']:.2f} GB")
        md.append(f"- **Rule Evaluations**: {org['total_evaluations']:,}")
        md.append(f"- **Estimated Cost**: ${org['estimated_cost']:.2f}\n")

        if org.get('daily_breakdown'):
            md.append("#### Last 7 Days Activity")
            md.append("| Date | Events | Output (GB) | Evaluations |")
            md.append("|------|--------|-------------|-------------|")
            for day in org['daily_breakdown']:
                md.append(f"| {day['date']} | {day['events']:,} | {day['output_gb']:.3f} | {day['evaluations']:,} |")
            md.append("")

    md.append("---")
    md.append("*Generated by LimaCharlie Multi-Tenant Billing Report*")
    md.append("\n**Note**: Estimated costs are approximate and based on standard pricing. Actual costs may vary based on your specific plan and commitments.")

    return '\n'.join(md)


def format_html(data, output_format='html'):
    """Format data as HTML report with charts"""

    meta = data['report_metadata']
    totals = data['totals']
    orgs = data['organizations']

    # Determine if we should use static charts
    use_static_charts = should_use_static_charts(output_format)

    # Prepare chart data
    org_labels = [org['name'] for org in orgs if 'error' not in org]
    org_costs = [org['estimated_cost'] for org in orgs if 'error' not in org]
    org_events = [org['total_events'] for org in orgs if 'error' not in org]
    org_output = [org['total_output_gb'] for org in orgs if 'error' not in org]

    # Generate static chart for PDF if needed
    cost_chart_static = None
    if use_static_charts:
        cost_chart_static = generate_static_chart(
            {'labels': org_labels, 'data': org_costs},
            'bar',
            'Cost Distribution by Organization',
            color='#667eea'
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Multi-Tenant Billing Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1400px;
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
        .cost-highlight {{
            border-left-color: #28a745;
        }}
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
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        .org-section {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Multi-Tenant Billing Report</h1>
        <div class="metadata">
            Generated: {meta['generated_at']}<br>
            Period: {meta['start_date']} to {meta['end_date']} ({meta['time_range_days']} days)<br>
            Organizations: {meta['org_count']}
        </div>
    </div>

    <div class="card">
        <h2>📊 Cross-Tenant Summary</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">Total Sensors</div>
                <div class="stat-value">{totals['total_sensors']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Events</div>
                <div class="stat-value">{totals['total_events']:,}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Output</div>
                <div class="stat-value">{totals['total_output_gb']:.2f} GB</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Evaluations</div>
                <div class="stat-value">{totals['total_evaluations']:,}</div>
            </div>
            <div class="stat-box cost-highlight">
                <div class="stat-label">Estimated Monthly Cost</div>
                <div class="stat-value">${totals['estimated_monthly_cost']:.2f}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>📈 Cost Distribution by Organization</h2>"""

    # Conditional chart rendering
    if use_static_charts and cost_chart_static:
        html += f"""
        <div style="text-align: center; padding: 20px;">
            <img src="{cost_chart_static}" style="max-width: 100%; height: auto;" alt="Cost Distribution Chart">
        </div>"""
    else:
        html += """
        <div class="chart-container">
            <canvas id="costChart"></canvas>
        </div>"""

    html += """
    </div>

    <div class="card">
        <h2>🏢 Organization Overview</h2>
        <table>
            <tr>
                <th>Organization</th>
                <th>Sensors</th>
                <th>Events</th>
                <th>Output (GB)</th>
                <th>Estimated Cost</th>
            </tr>
"""

    for org in sorted(orgs, key=lambda x: x.get('estimated_cost', 0), reverse=True):
        if 'error' in org:
            html += f"""            <tr>
                <td><strong>{org['name']}</strong></td>
                <td colspan="4" style="color: #dc3545;">Error: {org['error']}</td>
            </tr>
"""
        else:
            html += f"""            <tr>
                <td><strong>{org['name']}</strong></td>
                <td>{org['sensor_count']}/{org['sensor_quota']}</td>
                <td>{org['total_events']:,}</td>
                <td>{org['total_output_gb']:.2f}</td>
                <td><strong>${org['estimated_cost']:.2f}</strong></td>
            </tr>
"""

    html += """        </table>
    </div>

    <div class="card">
        <h2>📋 Detailed Organization Breakdown</h2>
"""

    for org in orgs:
        if 'error' in org:
            html += f"""        <div class="org-section">
            <h3>{org['name']}</h3>
            <p style="color: #dc3545;"><strong>Error:</strong> {org['error']}</p>
        </div>
"""
            continue

        html += f"""        <div class="org-section">
            <h3>{org['name']}</h3>
            <p><strong>Organization ID:</strong> <code>{org['oid']}</code></p>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Sensors</div>
                    <div class="stat-value" style="font-size: 1.4em;">{org['sensor_count']}/{org['sensor_quota']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Peak Sensors</div>
                    <div class="stat-value" style="font-size: 1.4em;">{org['peak_sensors']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Events</div>
                    <div class="stat-value" style="font-size: 1.4em;">{org['total_events']:,}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Data Output</div>
                    <div class="stat-value" style="font-size: 1.4em;">{org['total_output_gb']:.2f} GB</div>
                </div>
                <div class="stat-box cost-highlight">
                    <div class="stat-label">Estimated Cost</div>
                    <div class="stat-value" style="font-size: 1.4em;">${org['estimated_cost']:.2f}</div>
                </div>
            </div>
"""

        if org.get('daily_breakdown'):
            html += """            <h4>Last 7 Days Activity</h4>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Events</th>
                    <th>Output (GB)</th>
                    <th>Evaluations</th>
                </tr>
"""
            for day in org['daily_breakdown']:
                html += f"""                <tr>
                    <td>{day['date']}</td>
                    <td>{day['events']:,}</td>
                    <td>{day['output_gb']:.3f}</td>
                    <td>{day['evaluations']:,}</td>
                </tr>
"""
            html += """            </table>
"""

        html += """        </div>
"""

    html += """    </div>

    <div class="note">
        <strong>Note:</strong> Estimated costs are approximate and based on standard LimaCharlie pricing ($5/sensor/month + $0.20/GB + $0.001 per 1k evaluations).
        Actual costs may vary based on your specific plan, commitments, and current pricing. Please refer to your LimaCharlie billing dashboard for actual charges.
    </div>

    <div class="footer">
        Generated by LimaCharlie Multi-Tenant Billing Report
    </div>
"""

    # Add Chart.js script only for HTML output
    if not use_static_charts:
        html += """
    <script>
        // Cost Distribution Chart
        const costCtx = document.getElementById('costChart');
        if (costCtx) {
            new Chart(costCtx, {
                type: 'bar',
                data: {
                    labels: """ + json.dumps(org_labels) + """,
                    datasets: [{
                        label: 'Estimated Cost ($)',
                        data: """ + json.dumps(org_costs) + """,
                        backgroundColor: '#667eea',
                        borderColor: '#764ba2',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
    </script>
"""

    html += """</body>
</html>
"""

    return html


if __name__ == '__main__':
    import sys

    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'html'

    # Validate format
    if fmt not in ['html', 'markdown', 'pdf', 'json']:
        print(f"Error: Invalid format '{fmt}'. Must be html, markdown, pdf, or json")
        sys.exit(1)

    # For PDF, generate HTML first then convert
    report_format = 'html' if fmt == 'pdf' else fmt
    report = generate_billing_report(days, report_format)

    # Convert to PDF if requested
    if fmt == 'pdf':
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=report).write_pdf()
            report = pdf_bytes
        except ImportError:
            print("⚠️  Warning: weasyprint not installed. Install with: pip3 install weasyprint")
            print("Falling back to HTML output...")
            fmt = 'html'

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'pdf' if fmt == 'pdf' else 'json'
    filename = f'billing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    # Write binary for PDF, text for others
    mode = 'wb' if isinstance(report, bytes) else 'w'
    with open(filepath, mode) as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
