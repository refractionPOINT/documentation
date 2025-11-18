# Reporting Framework Approach

**Last Updated**: 2025-11-14
**Status**: Active Development - Chart Migration Phase

## Core Philosophy

This reporting framework is designed to be **AI-agent-driven**. AI agents (like Claude) will read this framework, understand the patterns, and generate both:
1. **Canned reports** - Pre-built templates that work out-of-the-box
2. **Custom reports** - New reports built by AI agents following established patterns

## Design Principles for AI-Driven Development

### 1. **Clear Examples > Complex Abstractions**
- AI learns by reading existing templates and adapting them
- Simple, repeatable patterns are easier for AI to understand than complex macro systems
- Prefer explicit, inline code over DRY abstractions
- Copy-paste-modify is acceptable and encouraged for AI

### 2. **Transparent, Readable Code**
- AI can understand explicit Chart.js configurations better than nested Jinja2 macros
- Each chart should be self-contained and clearly documented
- Comment the WHY, not just the WHAT

### 3. **Well-Documented Data Sources**
- `data-catalog.yaml` is the source of truth for available data
- AI reads this to know what data can be fetched
- Keep it updated with all available LimaCharlie data sources

### 4. **Pattern-Based Learning**
- AI learns from examples in existing templates
- Each report template should demonstrate clear patterns
- SKILL.md guides AI on when and how to use the framework

## Technology Stack

### Current (Phase 1 - Completed)
- ✅ **Python**: Data collection using LimaCharlie SDK
- ✅ **Jinja2**: Template rendering for HTML/Markdown/JSON
- ✅ **Mermaid.js**: Basic visualizations (DEPRECATED - being replaced)

### Target (Phase 2 - In Progress)
- ✅ **Python**: Data collection using LimaCharlie SDK
- ✅ **Jinja2**: Template rendering for HTML/Markdown/JSON
- 🚧 **Chart.js**: Interactive, beautiful charts (MIGRATION IN PROGRESS)
- 🚧 **Inline chart definitions**: Clear, explicit JavaScript in templates

### Why Chart.js + Jinja2?

**Perfect for AI because:**
1. **Declarative Configuration** - Chart.js uses clear JSON-like configs
2. **No Build Process** - Just template data into JavaScript
3. **Well-Documented** - AI can reference Chart.js docs
4. **Visible Patterns** - AI can see exactly how data flows: Python → Jinja2 → Chart.js
5. **Easy to Modify** - AI can read a chart and generate variations

**Example Pattern:**
```python
# Python: Prepare data
chart_data = {
    'labels': ['Mon', 'Tue', 'Wed'],
    'values': [120, 150, 180]
}
```

```jinja2
<!-- Jinja2: Template into JavaScript -->
<canvas id="myChart"></canvas>
<script>
new Chart(document.getElementById('myChart'), {
    type: 'line',
    data: {
        labels: {{ chart_data.labels|tojson }},
        datasets: [{
            label: 'Detections',
            data: {{ chart_data.values|tojson }}
        }]
    }
});
</script>
```

AI can clearly see: Python dict → Jinja2 |tojson filter → JavaScript Chart.js config

## Framework Structure

```
reporting/
├── FRAMEWORK_APPROACH.md          # This file - AI reads this first
├── SKILL.md                       # AI agent instructions
├── data-catalog.yaml              # What data is available
├── ROADMAP.md                     # Development status
├── templates/
│   ├── mssp_comprehensive_report.py    # Example: Full MSSP report
│   ├── sensor_health_report.py         # Example: Sensor monitoring
│   ├── multi_tenant_billing_report.py  # Example: Cross-org billing
│   ├── executive_summary.py            # Example: Executive summary
│   ├── chart_utils.py                  # Optional: Chart data helpers
│   └── jinja2/
│       ├── html/
│       │   ├── mssp_comprehensive.j2   # REFERENCE TEMPLATE
│       │   └── sensor_health.j2
│       └── markdown/
│           └── *.j2
└── utils/
    ├── branding.py                     # Dynamic company branding
    └── README.md
```

## How AI Agents Should Use This Framework

### For Generating Canned Reports:
1. Read `SKILL.md` to understand when to use this framework
2. Check `data-catalog.yaml` to see what data is available
3. Run existing Python scripts (e.g., `mssp_comprehensive_report.py`)
4. Customize parameters (OID, time range, output format)

### For Generating Custom Reports:
1. Read `SKILL.md` to understand the framework
2. Review `data-catalog.yaml` to identify required data sources
3. Study existing templates (e.g., `mssp_comprehensive_report.py`) to learn patterns
4. Copy and adapt the closest existing template
5. Modify data collection logic
6. Modify Jinja2 template for custom layout/charts
7. Follow established patterns for consistency

## Chart Migration Strategy (Current Phase)

### FROM: Mermaid.js (Deprecated)
```jinja2
<!-- OLD APPROACH - Limited, static -->
<pre class="mermaid">
pie title "Platform Distribution"
    "Windows" : 45
    "Linux" : 30
</pre>
```

**Problems:**
- No real line charts for time series
- Limited interactivity
- Poor support for trends over time
- AI generates summary boxes instead of actual visualizations

### TO: Chart.js (Target)
```jinja2
<!-- NEW APPROACH - Interactive, powerful -->
<canvas id="platformChart"></canvas>
<script>
new Chart(document.getElementById('platformChart'), {
    type: 'pie',
    data: {
        labels: {{ platform_labels|tojson }},
        datasets: [{
            data: {{ platform_values|tojson }},
            backgroundColor: ['#667eea', '#764ba2', '#4F9EEE']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Platform Distribution' }
        }
    }
});
</script>
```

**Benefits:**
- Proper line charts for detections over time
- Interactive tooltips and legends
- Area charts for event volume trends
- Multi-line charts for usage metrics
- Beautiful, professional appearance
- AI can clearly see data → chart config pattern

## Chart Types to Implement

### Priority 1 (Critical for MSSP Report):
- [x] **Line Chart** - Detections over time, event volume trends
- [x] **Area Chart** - Event volume with filled area
- [x] **Bar Chart** - Daily comparisons, top rules
- [ ] **Pie Chart** - Platform distribution, detection categories
- [ ] **Multi-line Chart** - Events + Evaluations + Output on same graph

### Priority 2 (Nice to Have):
- [ ] **Stacked Bar Chart** - Online/offline sensors by platform
- [ ] **Horizontal Bar Chart** - Top detection rules (better for long names)
- [ ] **Doughnut Chart** - Alternative to pie charts

## Reference Template Pattern

Each report should follow this pattern:

```python
#!/usr/bin/env python3
"""
Report Template Name
Clear description of what this report does
"""

from limacharlie import Manager
import time
import json
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

def generate_report(oid, days=7, format='html'):
    """
    Generate [report type]

    Args:
        oid: Organization ID
        days: Time range in days
        format: 'html', 'markdown', or 'json'

    Returns:
        Formatted report string
    """
    # 1. Initialize
    m = Manager(oid=oid)

    # 2. Collect data (with progress indicators)
    print("[1/5] Collecting organization info...")
    org_info = m.getOrgInfo()

    print("[2/5] Collecting sensor data...")
    sensors = list(m.sensors())

    # 3. Process data for charts
    chart_data = {
        'labels': [...],
        'datasets': [...]
    }

    # 4. Render template
    env = Environment(loader=FileSystemLoader('templates/jinja2/html'))
    template = env.get_template('report_name.j2')
    return template.render(
        org_info=org_info,
        chart_data=chart_data,
        # ... other data
    )

if __name__ == '__main__':
    # CLI interface
    # Always include usage example
    pass
```

## Inline Chart Example Pattern

```jinja2
<!-- PATTERN: Line Chart for Time Series -->
<div class="card">
    <h2>📈 Detections Over Time</h2>
    <canvas id="detectionsChart" height="80"></canvas>
</div>

<script>
// Chart: Detections timeline
// Shows daily detection counts with trend line
new Chart(document.getElementById('detectionsChart'), {
    type: 'line',
    data: {
        labels: {{ detection_timeline.dates|tojson }},
        datasets: [{
            label: 'Daily Detections',
            data: {{ detection_timeline.counts|tojson }},
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            fill: true,
            tension: 0.4  // Smooth curves
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: 'Detection Volume - Last {{ time_range_days }} Days'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Detections' }
            }
        }
    }
});
</script>
```

**Why this pattern works for AI:**
1. Clear comments explain purpose
2. Inline configuration - AI sees everything in one place
3. Jinja2 `|tojson` filter is explicit and visible
4. Options are documented (e.g., `tension: 0.4 // Smooth curves`)
5. AI can copy this entire block and modify data/labels

## Branding Integration

The framework supports dynamic branding via `utils/branding.py`:

```python
from utils.branding import get_brand_for_user, generate_css_from_brand

# Extract company colors from email domain
brand = get_brand_for_user('user@company.com')

# Pass to template
template.render(
    brand_colors=brand,
    # ...
)
```

```jinja2
<!-- In template: Use brand colors -->
<script>
new Chart(ctx, {
    data: {
        datasets: [{
            backgroundColor: '{{ brand_colors.primary_color }}',
            borderColor: '{{ brand_colors.secondary_color }}'
        }]
    }
});
</script>
```

## Best Practices for AI-Generated Reports

### DO:
- ✅ Read existing templates to learn patterns
- ✅ Copy and modify existing chart configurations
- ✅ Add clear comments explaining chart purpose
- ✅ Use consistent naming (e.g., `chart_data`, `timeline_data`)
- ✅ Include progress indicators during data collection
- ✅ Provide usage examples in docstrings
- ✅ Use `|tojson` filter for passing Python data to JavaScript

### DON'T:
- ❌ Create complex macro systems (AI prefers explicit code)
- ❌ Over-abstract chart creation (inline is clearer)
- ❌ Hide data transformations (make them visible)
- ❌ Assume data availability (check data-catalog.yaml first)
- ❌ Skip comments (AI and humans both benefit)

## Current Status

### Completed:
- ✅ Framework structure established
- ✅ Data catalog documented (23 data sources)
- ✅ 4 canned report templates with Mermaid charts
- ✅ Dynamic branding utility
- ✅ Jinja2 template system
- ✅ Plugin structure following marketplace conventions

### In Progress:
- 🚧 Migrating from Mermaid.js to Chart.js
- 🚧 Creating reference Chart.js examples
- 🚧 Updating MSSP comprehensive template

### Next Steps:
1. Create Chart.js line chart example for detections timeline
2. Create Chart.js area chart for event volume
3. Create Chart.js multi-line chart for usage metrics
4. Update MSSP template with all new charts
5. Document chart patterns for AI reference
6. Test report generation with new charts
7. Update other templates (sensor health, billing) with Chart.js

## Future Considerations

### When to Create New Templates:
- User requests a specific report type not covered
- Common use case emerges from multiple custom requests
- New LimaCharlie data sources become available

### When to Update Framework:
- Chart.js version updates with breaking changes
- New visualization types needed (e.g., heatmaps, sankey diagrams)
- Performance issues with large datasets
- Branding requirements change

### When to Refactor:
- **Only when patterns become unclear to AI**
- If multiple templates have identical chart code (extract to utility)
- If data collection is duplicated (create shared helpers)
- But: Keep it explicit and readable for AI

## For Future AI Agents

If you're an AI agent working on this framework in a future session:

1. **Read this file first** to understand the approach
2. **Check ROADMAP.md** for current development status
3. **Review data-catalog.yaml** to see available data
4. **Study existing templates** to learn established patterns
5. **Follow the inline chart pattern** when creating new visualizations
6. **Prioritize clarity over cleverness** - other AI agents will read your code

Remember: This framework is designed for AI agents to use and extend. Keep patterns clear, explicit, and well-documented.

---

**Project**: LimaCharlie Reporting Framework
**Plugin**: `lc_reporting`
**Skill**: `reporting`
**Author**: Christopher Luft (christopher.luft@gmail.com)
**AI Assistant**: Claude (Anthropic)
