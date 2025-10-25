# Usage Examples

Real-world examples showing how to generate HTML reports for different scenarios.

## Example 1: Simple Billing Report

**User Request:** "Show me my LimaCharlie billing for this month"

**Implementation:**

```python
import sys
sys.path.insert(0, '/full/path/to/.claude-plugin/plugins/limacharlie-skills/skills/limacharlie-reporting')

from lib import create_and_serve_report

# Assume we fetched this data from LimaCharlie MCP tools
org_name = "Production Org"
total_cost = 1234.56
services = [
    {'service': 'Detection & Response', 'cost': 500.00, 'usage': '1.2M events'},
    {'service': 'Artifact Collection', 'cost': 300.00, 'usage': '45 artifacts'},
    {'service': 'Output Data', 'cost': 434.56, 'usage': '125 GB'}
]

# Generate HTML
html = f"""
<h1>Billing Report: {org_name}</h1>
<h2>Total: ${total_cost:,.2f}</h2>

<table border="1" style="width:100%; border-collapse: collapse; margin-top: 20px;">
  <thead>
    <tr style="background: #f0f0f0;">
      <th style="padding: 10px;">Service</th>
      <th style="padding: 10px;">Usage</th>
      <th style="padding: 10px;">Cost</th>
    </tr>
  </thead>
  <tbody>
"""

for s in services:
    html += f"""
    <tr>
      <td style="padding: 10px;">{s['service']}</td>
      <td style="padding: 10px;">{s['usage']}</td>
      <td style="padding: 10px;">${s['cost']:,.2f}</td>
    </tr>
"""

html += """
  </tbody>
</table>
"""

url = create_and_serve_report(html, title="Billing Report")
print(f"\n✅ Billing report ready: {url}")
```

---

## Example 2: Billing with Chart

**User Request:** "Show me a chart of my monthly costs"

```python
from lib import create_and_serve_report

# Monthly cost data
months = ['January', 'February', 'March', 'April']
costs = [800, 950, 1100, 1234]

# Generate HTML with Chart.js
html = f"""
<h1>Monthly Billing Trend</h1>
<canvas id="trendChart" style="max-width: 800px; margin: 20px auto;"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: {months},
    datasets: [{{
      label: 'Monthly Cost ($)',
      data: {costs},
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.1)',
      tension: 0.4,
      fill: true
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{
        display: true,
        text: 'Cost Trend (Last 4 Months)',
        font: {{ size: 18 }}
      }}
    }},
    scales: {{
      y: {{
        beginAtZero: true,
        ticks: {{
          callback: function(value) {{
            return '$' + value;
          }}
        }}
      }}
    }}
  }}
}});
</script>
"""

url = create_and_serve_report(html, title="Cost Trend")
print(f"\n✅ Cost trend report: {url}")
```

---

## Example 3: Sensor Health Dashboard

**User Request:** "Show me a dashboard of my sensor health"

```python
from lib import create_and_serve_report

# Sensor data from LimaCharlie
sensors = [
    {'hostname': 'web-01', 'platform': 'linux', 'status': 'online', 'last_seen': '2 min ago'},
    {'hostname': 'web-02', 'platform': 'linux', 'status': 'online', 'last_seen': '1 min ago'},
    {'hostname': 'db-01', 'platform': 'linux', 'status': 'online', 'last_seen': '5 min ago'},
    {'hostname': 'win-dc01', 'platform': 'windows', 'status': 'online', 'last_seen': '1 min ago'},
    {'hostname': 'win-ws01', 'platform': 'windows', 'status': 'offline', 'last_seen': '2 hours ago'}
]

online_count = sum(1 for s in sensors if s['status'] == 'online')
offline_count = len(sensors) - online_count

html = f"""
<style>
  .metric-card {{
    display: inline-block;
    padding: 30px;
    margin: 15px;
    border-radius: 8px;
    color: white;
    text-align: center;
    min-width: 150px;
  }}
  .metric-value {{ font-size: 2.5em; font-weight: bold; }}
  .metric-label {{ font-size: 1.1em; margin-top: 5px; }}
  .online {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
  .offline {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
  .status-online {{ color: green; font-weight: bold; }}
  .status-offline {{ color: red; font-weight: bold; }}
</style>

<h1>Sensor Health Dashboard</h1>

<div style="margin: 30px 0;">
  <div class="metric-card online">
    <div class="metric-value">{online_count}</div>
    <div class="metric-label">Online</div>
  </div>
  <div class="metric-card offline">
    <div class="metric-value">{offline_count}</div>
    <div class="metric-label">Offline</div>
  </div>
</div>

<h2>Sensor Details</h2>
<table border="1" style="width:100%; border-collapse: collapse;">
  <thead>
    <tr style="background: #f0f0f0;">
      <th style="padding: 12px;">Hostname</th>
      <th style="padding: 12px;">Platform</th>
      <th style="padding: 12px;">Status</th>
      <th style="padding: 12px;">Last Seen</th>
    </tr>
  </thead>
  <tbody>
"""

for s in sensors:
    status_class = 'status-online' if s['status'] == 'online' else 'status-offline'
    row_bg = 'rgba(255, 99, 132, 0.1)' if s['status'] == 'offline' else 'white'
    html += f"""
    <tr style="background: {row_bg};">
      <td style="padding: 12px;">{s['hostname']}</td>
      <td style="padding: 12px;">{s['platform']}</td>
      <td style="padding: 12px;" class="{status_class}">{s['status']}</td>
      <td style="padding: 12px;">{s['last_seen']}</td>
    </tr>
"""

html += """
  </tbody>
</table>
"""

url = create_and_serve_report(html, title="Sensor Health")
print(f"\n✅ Sensor health dashboard: {url}")
```

---

## Example 4: Detection Coverage with Pie Chart

**User Request:** "Show me my detection coverage across platforms"

```python
from lib import create_and_serve_report

# Detection rule data
platforms = ['Windows', 'Linux', 'macOS', 'Cloud']
rule_counts = [45, 23, 18, 32]

html = f"""
<h1>Detection Coverage Report</h1>

<div style="max-width: 600px; margin: 40px auto;">
  <canvas id="coverageChart"></canvas>
</div>

<h2>Rules by Platform</h2>
<table border="1" style="width:100%; max-width: 600px; margin: 20px auto; border-collapse: collapse;">
  <thead>
    <tr style="background: #f0f0f0;">
      <th style="padding: 12px;">Platform</th>
      <th style="padding: 12px;">Active Rules</th>
    </tr>
  </thead>
  <tbody>
"""

for platform, count in zip(platforms, rule_counts):
    html += f"""
    <tr>
      <td style="padding: 12px;">{platform}</td>
      <td style="padding: 12px; text-align: center;">{count}</td>
    </tr>
"""

html += f"""
  </tbody>
  <tfoot>
    <tr style="background: #f8f9fa; font-weight: bold;">
      <td style="padding: 12px;">Total</td>
      <td style="padding: 12px; text-align: center;">{sum(rule_counts)}</td>
    </tr>
  </tfoot>
</table>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('coverageChart'), {{
  type: 'doughnut',
  data: {{
    labels: {platforms},
    datasets: [{{
      data: {rule_counts},
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)'
      ],
      borderWidth: 2
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{
        display: true,
        text: 'Detection Rules by Platform',
        font: {{ size: 18 }}
      }},
      legend: {{
        position: 'bottom'
      }}
    }}
  }}
}});
</script>
"""

url = create_and_serve_report(html, title="Detection Coverage")
print(f"\n✅ Detection coverage report: {url}")
```

---

## Example 5: Multi-Chart Dashboard

**User Request:** "Create a comprehensive dashboard with multiple charts"

```python
from lib import create_and_serve_report

# Sample data
monthly_costs = [800, 950, 1100, 1234]
service_costs = [500, 300, 434.56]
service_names = ['Detection', 'Artifacts', 'Outputs']

html = f"""
<style>
  .dashboard-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin: 30px 0;
  }}
  .chart-container {{
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
  }}
  @media (max-width: 768px) {{
    .dashboard-grid {{
      grid-template-columns: 1fr;
    }}
  }}
</style>

<h1>Comprehensive Billing Dashboard</h1>

<div class="dashboard-grid">
  <div class="chart-container">
    <h3>Monthly Trend</h3>
    <canvas id="trendChart"></canvas>
  </div>

  <div class="chart-container">
    <h3>Cost Distribution</h3>
    <canvas id="pieChart"></canvas>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
// Trend chart
new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [{{
      label: 'Monthly Cost ($)',
      data: {monthly_costs},
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.4
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true
  }}
}});

// Pie chart
new Chart(document.getElementById('pieChart'), {{
  type: 'pie',
  data: {{
    labels: {service_names},
    datasets: [{{
      data: {service_costs},
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)'
      ]
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true
  }}
}});
</script>
"""

url = create_and_serve_report(html, title="Dashboard")
print(f"\n✅ Comprehensive dashboard: {url}")
```

---

## Tips for Effective Reports

### 1. Start Simple, Add Complexity

Begin with basic HTML tables, then add charts if visualization helps:

```python
# Start here
html = "<h1>Data</h1><table>...</table>"

# Add charts if it helps
html += "<canvas id='chart'></canvas><script>...</script>"
```

### 2. Use Inline Styles

Keep reports self-contained with inline CSS:

```python
html = """
<style>
  .highlight { background: yellow; }
</style>
<div class="highlight">Important data</div>
"""
```

### 3. Format Numbers for Readability

Use Python's formatting:

```python
cost = 1234.56
html = f"<h2>Total: ${cost:,.2f}</h2>"  # → "Total: $1,234.56"
```

### 4. Conditional Formatting

Highlight issues:

```python
for sensor in sensors:
    bg_color = '#ffdddd' if sensor['status'] == 'offline' else 'white'
    html += f"<tr style='background: {bg_color};'>..."
```

### 5. Keep JavaScript Simple

Use Chart.js defaults, don't over-configure:

```python
# Good: simple and clear
new Chart(ctx, {
  type: 'bar',
  data: {...}
});

# Overkill: too much configuration
new Chart(ctx, {
  type: 'bar',
  data: {...},
  options: { /* 50 lines of config */ }
});
```

---

## Using with LimaCharlie MCP Tools

Combine this skill with LimaCharlie MCP tools to create real reports:

```python
# 1. Fetch data with MCP tools
usage = limacharlie.get_usage_stats(oid="...")
org_info = limacharlie.get_org_info(oid="...")

# 2. Generate HTML from the data
html = f"""
<h1>Usage Report: {org_info['name']}</h1>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Sensors</td><td>{usage['sensors']['online']}</td></tr>
  <tr><td>Events</td><td>{usage['events']['processed']:,}</td></tr>
</table>
"""

# 3. Serve it
url = create_and_serve_report(html, title="Usage Report")
print(f"Report: {url}")
```
