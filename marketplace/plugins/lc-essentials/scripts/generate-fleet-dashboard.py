import json
import sys

# Get paths from arguments or use defaults
data_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/fleet-dashboard-data.json'
output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/fleet-dashboard-2025-12-05.html'

# Read the data
with open(data_file, 'r') as f:
    data = json.load(f)

# Aggregate platform data
platform_totals = {}
for org in data['organizations']:
    for platform, count in org['sensors']['platforms'].items():
        # Skip non-numeric counts (e.g., notes about missing data)
        if isinstance(count, (int, float)) and count > 0:
            platform_totals[platform] = platform_totals.get(platform, 0) + count

# Get orgs with detections
orgs_with_detections = [(org['name'], org['detections']['total']) 
                        for org in data['organizations'] 
                        if org['detections']['total'] > 0]

# HTML Template (truncated from full version for brevity - same as before)
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LimaCharlie Fleet Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0a0f1e;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ 
            background: linear-gradient(135deg, #1a2332 0%, #2a3547 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border-left: 4px solid #00a8e8;
        }}
        h1 {{ color: #00a8e8; font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ color: #9aa5b1; font-size: 1.1em; }}
        .metrics-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #1e2836 0%, #2a3547 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid #00a8e8;
        }}
        .metric-label {{ color: #9aa5b1; font-size: 0.9em; margin-bottom: 8px; }}
        .metric-value {{ 
            font-size: 2.5em;
            font-weight: bold;
            color: #00a8e8;
            margin-bottom: 5px;
        }}
        .metric-detail {{ color: #7a8a99; font-size: 0.85em; }}
        .chart-container {{
            background: #1e2836;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 1.3em;
            color: #e0e0e0;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        table {{
            width: 100%;
            background: #1e2836;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 30px;
        }}
        thead {{
            background: #2a3547;
        }}
        th {{
            padding: 15px;
            text-align: left;
            color: #00a8e8;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ background: #354457; }}
        td {{
            padding: 15px;
            border-top: 1px solid #2a3547;
        }}
        tr:hover {{ background: #252f3f; }}
        .health-score {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: bold;
        }}
        .health-high {{ background: #00a86b; color: white; }}
        .health-medium {{ background: #ffa500; color: white; }}
        .health-low {{ background: #e63946; color: white; }}
        .alert-section {{
            background: #1e2836;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .alert-box {{
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid;
        }}
        .alert-critical {{
            background: rgba(230, 57, 70, 0.1);
            border-color: #e63946;
        }}
        .alert-warning {{
            background: rgba(255, 165, 0, 0.1);
            border-color: #ffa500;
        }}
        .alert-title {{
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.05em;
        }}
        .alert-message {{ color: #9aa5b1; margin-bottom: 5px; }}
        .alert-recommendation {{ color: #7a8a99; font-size: 0.9em; font-style: italic; }}
        footer {{
            background: #1e2836;
            padding: 25px;
            border-radius: 12px;
            color: #7a8a99;
            font-size: 0.9em;
        }}
        .provenance-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .prov-item {{ display: flex; flex-direction: column; }}
        .prov-label {{ color: #9aa5b1; font-size: 0.85em; margin-bottom: 4px; }}
        .prov-value {{ color: #e0e0e0; }}
        .accuracy-note {{
            background: rgba(0, 168, 232, 0.1);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #00a8e8;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ LimaCharlie Fleet Dashboard</h1>
            <div class="subtitle">Multi-Organization Security Monitoring Overview</div>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Organizations</div>
                <div class="metric-value">{data['metadata']['total_orgs']}</div>
                <div class="metric-detail">{data['metadata']['successful_collections']} successful, {data['metadata']['failed_collections']} failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Sensors</div>
                <div class="metric-value">{data['summary']['total_sensors']}</div>
                <div class="metric-detail">{data['summary']['online_sensors']} online ({data['summary']['fleet_online_percentage']}%)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Detections (24h)</div>
                <div class="metric-value">{data['summary']['total_detections']:,}</div>
                <div class="metric-detail">Last 24 hours</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Average Health Score</div>
                <div class="metric-value">{data['summary']['average_health_score']}</div>
                <div class="metric-detail">{data['summary']['critical_anomalies']} critical, {data['summary']['warning_anomalies']} warnings</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Platform Distribution</div>
            <svg id="platform-chart" width="800" height="400"></svg>
        </div>

        <div class="chart-container">
            <div class="chart-title">Organization Health Scores</div>
            <svg id="health-chart" width="1200" height="600"></svg>
        </div>

        <div class="chart-container">
            <div class="chart-title">Organization Details</div>
            <table id="org-table">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Organization</th>
                        <th onclick="sortTable(1)">Sensors</th>
                        <th onclick="sortTable(2)">Online %</th>
                        <th onclick="sortTable(3)">Detections</th>
                        <th onclick="sortTable(4)">Rules</th>
                        <th onclick="sortTable(5)">Outputs</th>
                        <th onclick="sortTable(6)">Health Score</th>
                        <th onclick="sortTable(7)">Anomalies</th>
                    </tr>
                </thead>
                <tbody>
'''

# Add table rows
for org in sorted(data['organizations'], key=lambda x: x['health_score'], reverse=True):
    sensors_total = org['sensors']['total'] if org['sensors']['total'] != -1 else 'N/A'
    online_pct = org['sensors']['online_percentage'] if org['sensors']['online_percentage'] != -1 else 'N/A'
    detections = org['detections']['total'] if org['detections']['total'] != -1 else 'N/A'
    rules = org['configuration']['rules'] if org['configuration']['rules'] != -1 else 'N/A'
    outputs = org['configuration']['outputs'] if org['configuration']['outputs'] != -1 else 'N/A'
    
    health_class = 'health-high' if org['health_score'] > 60 else ('health-medium' if org['health_score'] > 40 else 'health-low')
    
    html += f'''
                    <tr>
                        <td>{org['name']}</td>
                        <td>{sensors_total}</td>
                        <td>{online_pct}{'%' if online_pct != 'N/A' else ''}</td>
                        <td>{detections if detections == 'N/A' else f'{detections:,}'}</td>
                        <td>{rules}</td>
                        <td>{outputs}</td>
                        <td><span class="health-score {health_class}">{org['health_score']}</span></td>
                        <td>{len(org['anomalies'])}</td>
                    </tr>
'''

html += '''
                </tbody>
            </table>
        </div>

        <div class="alert-section">
            <div class="chart-title">Critical Anomalies</div>
'''

# Add critical anomalies
critical = [a for a in data['anomalies'] if a['severity'] == 'critical']
for anomaly in critical:
    html += f'''
            <div class="alert-box alert-critical">
                <div class="alert-title">🔴 {anomaly['org_name']}: {anomaly['message']}</div>
                <div class="alert-recommendation">→ {anomaly['recommendation']}</div>
            </div>
'''

html += '''
        </div>

        <div class="alert-section">
            <div class="chart-title">Warning Anomalies</div>
'''

# Add warning anomalies (limit to first 10)
warnings = [a for a in data['anomalies'] if a['severity'] == 'warning'][:10]
for anomaly in warnings:
    html += f'''
            <div class="alert-box alert-warning">
                <div class="alert-title">🟡 {anomaly['org_name']}: {anomaly['message']}</div>
                <div class="alert-recommendation">→ {anomaly['recommendation']}</div>
            </div>
'''

if len([a for a in data['anomalies'] if a['severity'] == 'warning']) > 10:
    html += f'''
            <div style="color: #9aa5b1; text-align: center; padding: 10px;">
                ... and {len([a for a in data['anomalies'] if a['severity'] == 'warning']) - 10} more warnings
            </div>
'''

html += f'''
        </div>

        <footer>
            <h3 style="color: #00a8e8; margin-bottom: 15px;">Data Provenance</h3>
            <div class="provenance-grid">
                <div class="prov-item">
                    <div class="prov-label">Generated</div>
                    <div class="prov-value">{data['metadata']['generated_at']}</div>
                </div>
                <div class="prov-item">
                    <div class="prov-label">Time Window</div>
                    <div class="prov-value">Last {data['metadata']['time_window_hours']} hours</div>
                </div>
                <div class="prov-item">
                    <div class="prov-label">Organizations</div>
                    <div class="prov-value">{data['metadata']['total_orgs']} total ({data['metadata']['successful_collections']} successful, {data['metadata']['failed_collections']} failed)</div>
                </div>
                <div class="prov-item">
                    <div class="prov-label">Data Source</div>
                    <div class="prov-value">LimaCharlie API via fleet-dashboard-collector agents</div>
                </div>
            </div>
            <div class="accuracy-note">
                <strong>Data Accuracy:</strong> All values shown are from actual API responses. No data has been estimated, interpolated, or fabricated. Missing or unavailable data is marked as "N/A".
            </div>
        </footer>
    </div>

    <script>
        // Platform distribution pie chart
        const platformData = {json.dumps(list(platform_totals.items()))};
        const width = 800;
        const height = 400;
        const radius = Math.min(width, height) / 2 - 40;

        const svg = d3.select("#platform-chart")
            .attr("viewBox", `0 0 ${{width}} ${{height}}`);

        const g = svg.append("g")
            .attr("transform", `translate(${{width / 2}}, ${{height / 2}})`);

        const color = d3.scaleOrdinal()
            .domain(platformData.map(d => d[0]))
            .range(["#00a8e8", "#00d9ff", "#0077b6", "#48cae4", "#90e0ef", "#ade8f4", "#caf0f8"]);

        const pie = d3.pie()
            .value(d => d[1])
            .sort(null);

        const arc = d3.arc()
            .innerRadius(radius * 0.5)
            .outerRadius(radius);

        const arcs = g.selectAll(".arc")
            .data(pie(platformData))
            .enter()
            .append("g")
            .attr("class", "arc");

        arcs.append("path")
            .attr("d", arc)
            .attr("fill", d => color(d.data[0]))
            .attr("stroke", "#0a0f1e")
            .attr("stroke-width", 2)
            .on("mouseover", function(event, d) {{
                d3.select(this).style("opacity", 0.7);
            }})
            .on("mouseout", function(event, d) {{
                d3.select(this).style("opacity", 1);
            }});

        // Legend
        const legend = svg.append("g")
            .attr("transform", `translate(${{width - 200}}, 20)`);

        platformData.forEach((d, i) => {{
            const legendRow = legend.append("g")
                .attr("transform", `translate(0, ${{i * 25}})`);

            legendRow.append("rect")
                .attr("width", 15)
                .attr("height", 15)
                .attr("fill", color(d[0]));

            legendRow.append("text")
                .attr("x", 20)
                .attr("y", 12)
                .attr("fill", "#e0e0e0")
                .style("font-size", "12px")
                .text(`${{d[0]}} (${{d[1]}})`);
        }});

        // Health scores bar chart
        const orgData = {json.dumps([[org['name'], org['health_score']] for org in sorted(data['organizations'], key=lambda x: x['health_score'], reverse=True) if org['health_score'] > 0])};
        
        const healthSvg = d3.select("#health-chart");
        const margin = {{top: 20, right: 30, bottom: 120, left: 150}};
        const chartWidth = 1200 - margin.left - margin.right;
        const chartHeight = 600 - margin.top - margin.bottom;

        const x = d3.scaleBand()
            .range([0, chartWidth])
            .domain(orgData.map(d => d[0]))
            .padding(0.2);

        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([chartHeight, 0]);

        const chart = healthSvg.append("g")
            .attr("transform", `translate(${{margin.left}}, ${{margin.top}})`);

        chart.selectAll(".bar")
            .data(orgData)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d[0]))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d[1]))
            .attr("height", d => chartHeight - y(d[1]))
            .attr("fill", d => d[1] > 60 ? "#00a86b" : (d[1] > 40 ? "#ffa500" : "#e63946"));

        chart.append("g")
            .attr("transform", `translate(0, ${{chartHeight}})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end")
            .style("fill", "#e0e0e0");

        chart.append("g")
            .call(d3.axisLeft(y))
            .selectAll("text")
            .style("fill", "#e0e0e0");

        // Table sorting
        function sortTable(n) {{
            const table = document.getElementById("org-table");
            let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            switching = true;
            dir = "desc";
            
            while (switching) {{
                switching = false;
                rows = table.rows;
                
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    
                    let xVal = x.textContent || x.innerText;
                    let yVal = y.textContent || y.innerText;
                    
                    // Remove commas and % for numeric comparison
                    xVal = xVal.replace(/,/g, '').replace(/%/g, '');
                    yVal = yVal.replace(/,/g, '').replace(/%/g, '');
                    
                    // Try numeric comparison
                    if (!isNaN(xVal) && !isNaN(yVal)) {{
                        xVal = parseFloat(xVal);
                        yVal = parseFloat(yVal);
                    }}
                    
                    if (dir == "desc") {{
                        if (xVal < yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else if (dir == "asc") {{
                        if (xVal > yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else {{
                    if (switchcount == 0 && dir == "desc") {{
                        dir = "asc";
                        switching = true;
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>
'''

with open(output_file, 'w') as f:
    f.write(html)

print(f"SUCCESS: {output_file}")
