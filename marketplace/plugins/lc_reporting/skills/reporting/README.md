# LimaCharlie Reporting Skill

## Quick Start

This skill enables AI agents to generate comprehensive security and operational reports from LimaCharlie organization data.

### Test the Skill

```bash
cd .claude/skills/limacharlie-reporting/templates
python3 executive_summary.py YOUR_ORG_ID 7 html
```

## File Structure

```
.claude/skills/limacharlie-reporting/
├── README.md                      # This file - overview and quick start
├── skill.md                       # Complete skill documentation
├── data-catalog.yaml              # Reference of all available data types
├── templates/                     # Report templates
│   ├── README.md                  # Template documentation
│   └── executive_summary.py       # Executive summary report (working)
└── utils/                         # Utility functions (planned)
    └── README.md                  # Utilities documentation
```

## Key Files

### 1. skill.md
Complete documentation for using this skill:
- When to use the skill
- Available data sources
- Report types
- Usage instructions
- Best practices
- Common scenarios
- Troubleshooting

### 2. data-catalog.yaml
Comprehensive reference of all 23 data categories available in LimaCharlie:
- Organization metadata
- Sensors (646 total)
- D&R Rules (606 total)
- Events & Detections (Insight enabled)
- Usage statistics
- And 18 more categories...

Each entry includes:
- Description
- Access methods (SDK & MCP tools)
- Required permissions
- Available fields
- Example code

### 3. templates/executive_summary.py
Working report template that generates:
- Organizational overview
- Sensor health metrics
- Detection summary
- Usage statistics
- Configuration audit

Supports HTML, Markdown, and JSON output.

## For Future Agents

When a user requests a report:

1. **Read `skill.md`** - Understand the skill capabilities
2. **Consult `data-catalog.yaml`** - Check what data is available
3. **Choose a template** - Use existing template or create custom
4. **Verify access** - Check authentication and permissions
5. **Generate report** - Collect data and format output

## Available Report Templates

Currently implemented:
- ✅ **Executive Summary** - High-level organizational overview

Planned:
- Sensor Health Report
- Security Detections Report
- Usage & Billing Report
- Configuration Audit Report
- Incident Investigation Report
- MITRE ATT&CK Coverage Report

## Example Usage

### Using Python Template Directly

```bash
# Generate 7-day executive summary as HTML
python3 templates/executive_summary.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 html

# Generate 30-day report as Markdown
python3 templates/executive_summary.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 30 markdown

# Generate JSON export
python3 templates/executive_summary.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd 7 json
```

### Using in AI Agent Context

When an agent needs to generate a report:

```
User: "Generate an executive summary for the last 7 days"

Agent:
1. Reviews skill.md to understand requirements
2. Checks data-catalog.yaml for data availability
3. Runs: python3 templates/executive_summary.py <OID> 7 html
4. Reads the generated HTML file
5. Presents summary to user with file location
```

## Data Categories

The skill provides access to 23 data categories (see `data-catalog.yaml` for complete details):

1. Organization Metadata
2. Sensors (646 total)
3. D&R Rules (606 total)
4. Events (Historical)
5. Detections (Historical)
6. Usage Statistics (Daily breakdowns)
7. Outputs (68 total)
8. Tags (53 total)
9. Extensions (4 active)
10. API Keys (89 total)
11. Users (26 total)
12. YARA Rules
13. False Positive Rules
14. Installation Keys (45 total)
15. Audit Logs
16. MITRE ATT&CK Coverage
17. Lookup Tables
18. IOC Search
19. Artifacts
20. Event Schemas
21. Jobs
22. Secrets
23. LCQL Queries

## Authentication

Ensure LimaCharlie CLI is authenticated before using:

```bash
limacharlie who                     # Check auth status
limacharlie set-oid YOUR_ORG_ID     # Set active org
```

## Output Formats

Reports can be generated in:
- **HTML** - Professional, styled reports with tables and visualizations
- **Markdown** - Clean, documentation-friendly format
- **JSON** - Machine-readable data export

## Best Practices

1. **Always specify time ranges** - Prevents overwhelming data returns
2. **Use limits on queries** - Start small, increase if needed
3. **Cache static data** - Org info doesn't change frequently
4. **Check permissions first** - Verify before attempting access
5. **Include metadata** - Date, time range, org info in reports
6. **Handle errors gracefully** - Not all data may be available

## Extending the Skill

To add a new report template:

1. Copy `templates/executive_summary.py` as starting point
2. Modify data collection for your needs
3. Reference `data-catalog.yaml` for available data
4. Implement formatting functions
5. Test with your organization
6. Update template README

## Testing

The skill has been tested with:
- Organization: lc_demo (8cbe27f4-bfa1-4afb-ba19-138cd51389cd)
- Report Type: Executive Summary
- Output Format: HTML
- Result: ✅ Success (6.1KB report generated)

## Maintenance

Update this skill when:
- New data sources become available in LimaCharlie
- API changes affect access methods
- New report types are requested
- Organization configuration changes significantly

Last updated: 2025-11-12

## Support

For issues or questions:
1. Review `skill.md` for complete documentation
2. Check `data-catalog.yaml` for data availability
3. Verify authentication: `limacharlie who`
4. Test with small queries first
5. Check permissions for required data sources

---

**Status**: Active and tested
**Version**: 1.0
**Organization**: lc_demo (8cbe27f4-bfa1-4afb-ba19-138cd51389cd)
