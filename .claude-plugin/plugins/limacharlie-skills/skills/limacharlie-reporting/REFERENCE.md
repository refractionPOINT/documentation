# Reference Guide

Advanced techniques and tips for creating effective HTML reports.

## Chart.js Quick Reference

### Chart Types

**Line Charts** - Trends over time:
```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Revenue',
      data: [100, 150, 120],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1  // Curve smoothness (0 = straight, 1 = very curved)
    }]
  }
});
```

**Bar Charts** - Comparing categories:
```javascript
new Chart(ctx, {
  type: 'bar',  // or 'horizontalBar'
  data: {
    labels: ['Product A', 'Product B', 'Product C'],
    datasets: [{
      label: 'Sales',
      data: [12, 19, 3],
      backgroundColor: 'rgba(54, 162, 235, 0.6)'
    }]
  }
});
```

**Pie/Doughnut Charts** - Proportions:
```javascript
new Chart(ctx, {
  type: 'pie',  // or 'doughnut'
  data: {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{
      data: [300, 50, 100],
      backgroundColor: [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)'
      ]
    }]
  }
});
```

### Common Options

```javascript
{
  responsive: true,  // Resize with container
  maintainAspectRatio: true,  // Keep aspect ratio

  plugins: {
    title: {
      display: true,
      text: 'My Chart Title'
    },
    legend: {
      display: true,
      position: 'top'  // 'top', 'bottom', 'left', 'right'
    }
  },

  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Y Axis Label'
      }
    }
  }
}
```

## HTML/CSS Tips

### Responsive Grid Layouts

```python
html = """
<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }
</style>

<div class="grid">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
"""
```

### Metric Cards

```python
html = """
<style>
  .metric {
    padding: 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    text-align: center;
  }
  .value { font-size: 2.5em; font-weight: bold; }
  .label { font-size: 1.1em; margin-top: 10px; }
</style>

<div class="metric">
  <div class="value">$1,234</div>
  <div class="label">Total Cost</div>
</div>
"""
```

### Conditional Row Highlighting

```python
for item in data:
    bg = '#ffdddd' if item['error'] else 'white'
    html += f"<tr style='background: {bg};'><td>{item['name']}</td></tr>"
```

### Table Styling

```python
html = """
<style>
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    background: #f0f0f0;
    padding: 12px;
    text-align: left;
    font-weight: 600;
  }
  td {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
  }
  tr:hover {
    background: #f8f9fa;
  }
</style>
"""
```

## Alternative Visualization Libraries

### ApexCharts (Modern, Interactive)

```python
html = """
<div id="chart"></div>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script>
var options = {
  chart: { type: 'line' },
  series: [{
    name: 'sales',
    data: [30, 40, 45, 50, 49, 60, 70, 91]
  }],
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
  }
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();
</script>
"""
```

### Plotly (Statistical/Scientific)

```python
html = """
<div id="plot"></div>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script>
var data = [{
  x: [1, 2, 3, 4, 5],
  y: [1, 2, 4, 8, 16],
  mode: 'lines+markers',
  type: 'scatter'
}];

var layout = {
  title: 'Exponential Growth'
};

Plotly.newPlot('plot', data, layout);
</script>
"""
```

## Performance Tips

### Large Tables

For tables with 1000+ rows, add pagination:

```python
html = """
<div style="max-height: 600px; overflow-y: auto;">
  <table>
    <!-- Many rows -->
  </table>
</div>
"""
```

Or use DataTables for automatic pagination:

```python
html = """
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>

<table id="myTable">
  <!-- table content -->
</table>

<script>
  $(document).ready(function() {
    $('#myTable').DataTable({
      pageLength: 25,
      order: [[0, 'asc']]
    });
  });
</script>
"""
```

### Many Charts

Load Chart.js once, create many charts:

```python
html = """
<canvas id="chart1"></canvas>
<canvas id="chart2"></canvas>
<canvas id="chart3"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
  new Chart(document.getElementById('chart1'), {...});
  new Chart(document.getElementById('chart2'), {...});
  new Chart(document.getElementById('chart3'), {...});
</script>
"""
```

## Styling Best Practices

### Use CSS Variables for Consistency

```python
html = """
<style>
  :root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --danger-color: #f5576c;
    --success-color: #4caf50;
  }

  .card { background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); }
  .error { color: var(--danger-color); }
  .success { color: var(--success-color); }
</style>
"""
```

### Mobile-Friendly Design

```python
html = """
<style>
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }

  @media (max-width: 768px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
"""
```

## Data Formatting Helpers

### Python Format Strings

```python
# Currency
cost = 1234.56
f"${cost:,.2f}"  # → "$1,234.56"

# Large numbers
events = 1234567
f"{events:,}"  # → "1,234,567"

# Percentages
pct = 0.8567
f"{pct:.1%}"  # → "85.7%"

# Bytes to human readable
bytes_val = 1234567890
for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
    if bytes_val < 1024:
        size_str = f"{bytes_val:.1f} {unit}"
        break
    bytes_val /= 1024
```

### HTML Escaping

Always escape user data to prevent XSS:

```python
from html import escape

user_input = "<script>alert('xss')</script>"
html = f"<p>{escape(user_input)}</p>"
# → <p>&lt;script&gt;alert('xss')&lt;/script&gt;</p>
```

## Common Patterns

### Loading Multiple Reports

```python
from lib import create_and_serve_report

# Generate multiple reports
urls = []
for org in organizations:
    html = generate_org_report(org)
    url = create_and_serve_report(html, filename=f"org-{org['id']}")
    urls.append(url)

# Create index page
index_html = "<h1>Reports</h1><ul>"
for url in urls:
    filename = url.split('/')[-1]
    index_html += f"<li><a href='{filename}'>{filename}</a></li>"
index_html += "</ul>"

index_url = create_and_serve_report(index_html, filename="index")
print(f"Index: {index_url}")
```

### Exporting Report Data

Users can save reports:
- **Print to PDF**: Browser → Print → Save as PDF
- **Save HTML**: Browser → Right-click → Save Page As
- **Copy Data**: Select table → Ctrl+C → Paste to Excel

### Auto-Refresh

For live dashboards:

```python
html = """
<meta http-equiv="refresh" content="30">
<h1>Live Dashboard</h1>
<p>Auto-refreshes every 30 seconds</p>
<!-- Report content -->
"""
```

## Troubleshooting

### Charts Not Rendering

1. Check browser console for errors
2. Verify Chart.js loaded: `typeof Chart !== 'undefined'`
3. Ensure canvas has ID: `<canvas id="myChart"></canvas>`
4. Confirm script runs after Chart.js loads

### Large Reports Slow

1. Paginate large tables (see DataTables above)
2. Limit charts to visible data ranges
3. Use CSS `display: none` for hidden sections
4. Consider splitting into multiple reports

### Styling Not Applied

1. Check CSS syntax (missing semicolons, braces)
2. Use browser dev tools to inspect styles
3. Ensure selectors match HTML elements
4. Check for typos in class/ID names

## Security Notes

### XSS Prevention

Always escape user data:

```python
from html import escape

# BAD (vulnerable to XSS)
html = f"<p>{user_input}</p>"

# GOOD (safe)
html = f"<p>{escape(user_input)}</p>"
```

### Localhost Only

Reports are only accessible on localhost - they're not exposed to the network. The server binds to `127.0.0.1`, making them only viewable on your machine.

## Advanced Techniques

### Custom Tooltips (Chart.js)

```javascript
{
  plugins: {
    tooltip: {
      callbacks: {
        label: function(context) {
          return '$' + context.parsed.y.toLocaleString();
        }
      }
    }
  }
}
```

### Drill-Down Reports

Link from summary to detail:

```python
# Summary report
summary_html = """
<h1>Summary</h1>
<ul>
  <li><a href="detail-windows.html">Windows Details</a></li>
  <li><a href="detail-linux.html">Linux Details</a></li>
</ul>
"""

summary_url = create_and_serve_report(summary_html, filename="summary")

# Detail reports
windows_html = "<h1>Windows Details</h1>..."
create_and_serve_report(windows_html, filename="detail-windows")

linux_html = "<h1>Linux Details</h1>..."
create_and_serve_report(linux_html, filename="detail-linux")
```

### Interactive Filters (JavaScript)

```python
html = """
<input type="text" id="filter" placeholder="Filter table...">
<table id="dataTable">
  <!-- table rows -->
</table>

<script>
  document.getElementById('filter').addEventListener('input', function(e) {
    const filter = e.target.value.toLowerCase();
    const rows = document.querySelectorAll('#dataTable tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(filter) ? '' : 'none';
    });
  });
</script>
"""
```

## Further Reading

- **Chart.js Docs**: https://www.chartjs.org/docs/latest/
- **ApexCharts Docs**: https://apexcharts.com/docs/
- **MDN HTML**: https://developer.mozilla.org/en-US/docs/Web/HTML
- **MDN CSS**: https://developer.mozilla.org/en-US/docs/Web/CSS
- **CSS Grid Guide**: https://css-tricks.com/snippets/css/complete-guide-grid/
