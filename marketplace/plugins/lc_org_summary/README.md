# LimaCharlie Organization Summary Plugin

A Claude Code plugin that provides intelligent organization health summaries for LimaCharlie deployments.

## Overview

The Organization Summary plugin helps you quickly understand the health and status of your LimaCharlie organizations by analyzing sensor deployment, platform coverage, and data recency. It generates comprehensive reports that highlight operational status, active platforms, and potential issues.

## Features

- **Single Organization Summaries**: Get detailed health reports for a specific organization
- **Multi-Organization Overview**: Compare and analyze all accessible organizations at once
- **Active Platform Detection**: Identifies platforms with recent telemetry data (last 30 days)
- **Sensor Status Monitoring**: Tracks online vs. total sensor counts
- **Health Assessment**: Provides quick visual indicators of organization health
- **Optimized Performance**: Uses Claude 3.5 Haiku for fast, cost-effective analysis

## Installation

### Via Marketplace

If this plugin is available in a Claude Code marketplace:

```bash
/plugin marketplace add <marketplace-url>
/plugin install lc-org-summary
```

### Manual Installation

1. Copy the `lc_org_summary` directory to your Claude Code plugins folder
2. Ensure the LimaCharlie MCP server is configured
3. Restart Claude Code or reload plugins

## Usage

### Summarize All Organizations

```
Use the org_summary agent to summarize all my organizations
```

The agent will:
1. List all organizations you have access to
2. Analyze sensor status for each
3. Check platform activity and data recency
4. Generate a comparative summary table

### Summarize Specific Organization

```
Use the org_summary agent to summarize organization <OID>
```

Replace `<OID>` with your organization ID. The agent will provide:
- Organization name and description
- Online and total sensor counts
- List of active platforms (with recent data)
- Health assessment and recommendations

## Output Format

### Single Organization Summary

```
# Organization Summary: Production Environment

**Organization ID**: 8e2f5a3b-1234-5678-90ab-cdef12345678
**Description**: Main production deployment

## Sensor Status
- **Online Sensors**: 142 currently online
- **Total Sensors**: 150
- **Online Percentage**: 94.7%

## Active Platforms (Last 30 Days)
- **windows**: 85 sensors
- **linux**: 45 sensors
- **macos**: 12 sensors

## Health Assessment
✅ Healthy: Strong sensor coverage across all platforms with 95% online rate
```

### Multi-Organization Summary

```
# LimaCharlie Organizations Summary

Total Organizations: 3

| Organization | OID | Online Sensors | Total Sensors | Active Platforms | Status |
|--------------|-----|----------------|---------------|------------------|--------|
| Production   | 8e2f... | 142 | 150 | windows, linux, macos | ✅ |
| Staging      | 9a3c... | 23  | 25  | windows, linux        | ✅ |
| Development  | 7b1d... | 5   | 8   | windows              | ⚠️ |
```

## Agent Details

### Tools Used

The org_summary agent uses these LimaCharlie MCP tools:

- `list_user_orgs` - Discover accessible organizations
- `get_org_info` - Fetch organization metadata
- `get_online_sensors` - Count and list online sensors
- `list_sensors` - Enumerate all sensors
- `get_sensor_info` - Get sensor details
- `list_with_platform` - List sensors by platform
- `get_platform_names` - Discover available platforms
- `get_time_when_sensor_has_data` - Verify data recency

### Performance Characteristics

- **Model**: Claude 3.5 Haiku (fast and cost-effective)
- **Average Runtime**:
  - Single org: 5-10 seconds
  - Multiple orgs: 10-30 seconds (depending on count)
- **Optimization**: Checks 1-2 sensors per platform for data recency

### Data Recency Definition

A platform is considered "active" only if it has sensors that reported data within the **last 30 days**. This ensures summaries reflect current operational status, not historical deployments.

## Use Cases

### Daily Operations Review

Quickly check the health of all your LimaCharlie deployments:
```
Show me a summary of all my organizations
```

### Incident Response Preparation

Before investigating an incident, verify the organization's sensor coverage:
```
Summarize organization <incident-org-id>
```

### Deployment Verification

After deploying new sensors, confirm they're online and reporting:
```
Give me a summary of the staging organization
```

### Executive Reporting

Generate quick health snapshots for stakeholder updates:
```
Summarize all organizations with health status
```

## Health Status Indicators

The agent uses visual indicators for quick assessment:

- ✅ **Healthy**: >80% sensors online with recent data on all platforms
- ⚠️ **Attention Needed**: 50-80% sensors online or some platforms with stale data
- ❌ **Critical**: <50% sensors online or no recent data from any platform

## Troubleshooting

### No Organizations Found

**Symptom**: Agent reports no accessible organizations

**Solution**:
- Verify your LimaCharlie API credentials are configured
- Check that your user account has organization access
- Ensure the MCP server connection is working

### Platform Data Shows as Stale

**Symptom**: All platforms show no recent data despite active sensors

**Solution**:
- Verify sensors are actually sending telemetry (check Timeline in UI)
- Confirm the time range calculation is correct (last 30 days)
- Check if there are API rate limiting issues

### Slow Performance

**Symptom**: Summaries take a long time to generate

**Solution**:
- Reduce the number of organizations being checked
- The agent is optimized with Haiku model - slow performance might indicate network issues
- Check MCP server response times

## Requirements

- Claude Code with plugin support
- LimaCharlie MCP server configured and accessible
- Valid LimaCharlie user credentials with organization access
- Network connectivity to LimaCharlie API endpoints

## Configuration

### MCP Server Configuration

The plugin requires the LimaCharlie MCP server. Configuration is in `.mcp.json`:

```json
{
  "mcpServers": {
    "limacharlie": {
      "type": "http",
      "url": "https://mcp.limacharlie.io/mcp"
    }
  }
}
```

### Customization

To modify the agent's behavior, edit `agents/org_summary/AGENT.md`:

- Adjust data recency threshold (currently 30 days)
- Change health status thresholds
- Modify output format
- Add additional metrics

## Examples

### Example 1: Quick Health Check

**Request**: "Give me a quick summary of all my orgs"

**Response**: Generates a table comparing all organizations with key metrics and health indicators

### Example 2: Detailed Analysis

**Request**: "I need a detailed summary of organization abc-123-def including platform breakdown"

**Response**: Provides comprehensive single-organization report with sensor counts, platform distribution, and health assessment

### Example 3: Platform Investigation

**Request**: "Which of my organizations have Windows sensors with recent data?"

**Response**: Analyzes all organizations and highlights those with active Windows platform coverage

## Contributing

To improve this plugin:

1. Fork the documentation repository
2. Make your changes to the plugin files
3. Test thoroughly with various organization configurations
4. Submit a pull request with clear description of improvements

## Support

For issues, questions, or feature requests:

- GitHub Issues: [refractionPOINT/documentation](https://github.com/refractionPOINT/documentation/issues)
- LimaCharlie Support: support@limacharlie.io
- Community Slack: [LimaCharlie Slack](https://slack.limacharlie.io)

## License

This plugin is part of the LimaCharlie documentation repository and follows the same license terms.

## Version History

### 1.0.0 (Initial Release)
- Single organization summary generation
- Multi-organization comparative analysis
- Active platform detection with 30-day recency check
- Health status indicators
- Optimized with Claude 3.5 Haiku model
