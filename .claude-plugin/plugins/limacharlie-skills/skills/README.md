# LimaCharlie Skills

A comprehensive collection of specialized Skills for working with the LimaCharlie SecOps Cloud Platform.

## Overview

This directory contains **25 specialized skills** that provide Claude with expert-level knowledge for working with LimaCharlie's endpoint detection and response (EDR), cloud security monitoring, threat hunting, and incident response capabilities.

Each skill is a self-contained instruction set with comprehensive documentation, real-world examples, and best practices drawn from the official LimaCharlie documentation.

## Quick Start

### For Claude Code

When working in this repository, Claude Code will automatically discover and use these skills based on context.

### For Claude.ai

Upload individual skill folders through Settings → Skills.

## Available Skills

### Entry Point

| Skill | Description | Use When |
|-------|-------------|----------|
| [limacharlie-expert](./limacharlie-expert/) | High-level LimaCharlie component overview | Starting any LimaCharlie task, understanding component interconnections, or getting routed to specialized skills |

### Core Platform Operations

| Skill | Description | Use When |
|-------|-------------|----------|
| [dr-rule-builder](./dr-rule-builder/) | Detection & Response rule creation | Creating, testing, or validating D&R rules |
| [sensor-manager](./sensor-manager/) | Endpoint sensor deployment | Deploying or managing sensors on endpoints |
| [adapter-configurator](./adapter-configurator/) | Data source adapter setup | Ingesting logs from cloud services or SIEMs |
| [onboard-external-telemetry](./onboard-external-telemetry/) | Step-by-step external data source onboarding | Connecting new cloud/SaaS data sources for beginners |

### Data Operations

| Skill | Description | Use When |
|-------|-------------|----------|
| [lcql-query-builder](./lcql-query-builder/) | Query language for searching telemetry | Writing LCQL queries for investigations |
| [output-configurator](./output-configurator/) | Route data to external systems | Forwarding events to SIEMs or data lakes |
| [artifact-collector](./artifact-collector/) | Forensic artifact collection | Collecting files, memory dumps, or logs |

### Security Operations

| Skill | Description | Use When |
|-------|-------------|----------|
| [incident-responder](./incident-responder/) | Incident response workflows | Responding to security incidents |
| [threat-hunter](./threat-hunter/) | Proactive threat hunting | Hunting for threats or suspicious activity |
| [yara-manager](./yara-manager/) | YARA malware detection | Creating or managing YARA rules |

### Development & Integration

| Skill | Description | Use When |
|-------|-------------|----------|
| [extension-developer](./extension-developer/) | Custom extension development | Building custom integrations |
| [api-integrator](./api-integrator/) | LimaCharlie APIs and SDKs | Automating with Python/Go SDKs |
| [playbook-automator](./playbook-automator/) | Automated response workflows | Creating security automation |

### Advanced Features

| Skill | Description | Use When |
|-------|-------------|----------|
| [stateful-rule-designer](./stateful-rule-designer/) | Complex event correlation | Correlating multiple events over time |
| [cloud-security-monitor](./cloud-security-monitor/) | Cloud platform monitoring | Monitoring AWS, Azure, or GCP |
| [threat-intel-integrator](./threat-intel-integrator/) | Threat intelligence integration | Using VirusTotal, GreyNoise, etc. |

### Platform Management

| Skill | Description | Use When |
|-------|-------------|----------|
| [billing-reporter](./billing-reporter/) | Billing and usage analysis | Analyzing costs, investigating usage trends, or comparing billing across organizations |
| [limacharlie-reporting](./limacharlie-reporting/) | Rich HTML report generation | Creating interactive dashboards, charts, and visualizations for any LimaCharlie data |
| [config-hive-manager](./config-hive-manager/) | Configuration storage | Managing secrets, rules, and lookups |
| [sigma-rule-deployer](./sigma-rule-deployer/) | Managed ruleset deployment | Deploying Sigma, Soteria, or SOC Prime rules |
| [infrastructure-as-code](./infrastructure-as-code/) | Configuration as code | Managing LimaCharlie with IaC |

### Specialized Use Cases

| Skill | Description | Use When |
|-------|-------------|----------|
| [forensic-analyst](./forensic-analyst/) | Digital forensics analysis | Conducting forensic investigations |
| [performance-optimizer](./performance-optimizer/) | Performance and cost optimization | Optimizing performance or reducing costs |

## Skill Structure

Each skill follows a consistent structure:

```
skill-name/
└── SKILL.md          # Comprehensive documentation with YAML frontmatter
```

### SKILL.md Format

```yaml
---
name: skill-name
description: Clear one-sentence description of when to use this skill
---

# Skill Title

## Introduction
[What the skill covers]

## [Topic 1]
[Comprehensive guidance with examples]

## [Topic 2]
[More detailed instructions]

## Examples
[Real-world, working examples]

## Best Practices
[Expert recommendations]

## Troubleshooting
[Common issues and solutions]
```

## Usage Examples

### Detection & Response
```
"Help me create a rule to detect PowerShell execution from Office documents"
→ Activates: dr-rule-builder
```

### Incident Response
```
"I have an alert for suspicious process execution, how do I investigate?"
→ Activates: incident-responder, threat-hunter
```

### Cloud Security
```
"Set up monitoring for AWS CloudTrail and GuardDuty"
→ Activates: cloud-security-monitor, onboard-external-telemetry
```

### Forensics
```
"I need to collect a memory dump and analyze it for malware"
→ Activates: artifact-collector, forensic-analyst
```

## Key Features

✅ **Comprehensive Coverage** - All major LimaCharlie components and workflows
✅ **Real-World Examples** - Working code and configurations from official docs
✅ **Best Practices** - Expert guidance and proven patterns
✅ **Cross-Referenced** - Skills reference each other for complex workflows
✅ **Production-Ready** - Examples tested against LimaCharlie documentation
✅ **Regularly Updated** - Maintained alongside LimaCharlie documentation

## Documentation Sources

All skills are created from authoritative LimaCharlie documentation:

- **Official Docs**: 281 markdown files covering the entire platform
- **SDK Documentation**: Complete Python and Go SDK references
- **Use Cases**: Real-world deployment scenarios
- **Best Practices**: Official recommendations and patterns

## Contributing

### Adding New Skills

1. Create a new directory with a descriptive name (lowercase, hyphenated)
2. Add a `SKILL.md` file following the format above
3. Include comprehensive examples from LimaCharlie documentation
4. Update `../.claude-plugin/marketplace.json`
5. Update this README with the new skill

### Updating Existing Skills

1. Edit the relevant `SKILL.md` file
2. Ensure examples are up-to-date with current LimaCharlie features
3. Test changes with Claude Code
4. Document significant changes in version history

### Quality Guidelines

- ✅ Include working examples that can be copy-pasted
- ✅ Reference official documentation and command syntax
- ✅ Provide troubleshooting guidance
- ✅ Use consistent formatting and structure
- ✅ Keep descriptions concise but comprehensive
- ✅ Include both simple and advanced use cases

## Resources

- **LimaCharlie Documentation**: https://docs.limacharlie.io
- **LimaCharlie Platform**: https://app.limacharlie.io
- **Community Slack**: https://slack.limacharlie.io
- **GitHub**: https://github.com/refractionPOINT
- **Support**: support@limacharlie.io

## Skills Documentation

For more information about Claude Skills:
- **Skills Overview**: https://docs.anthropic.com/en/docs/build-with-claude/skills
- **Creating Skills**: https://github.com/anthropics/skills
- **Skills API**: https://docs.anthropic.com/en/api/skills

## License

These skills are provided as part of the LimaCharlie documentation repository.

## Version History

### 1.4.0 (2025-10-25)
- Added `limacharlie-reporting` skill for rich HTML report generation
- Now includes 25 comprehensive skills
- New skill provides infrastructure for creating interactive dashboards with charts, tables, and visualizations
- Includes background HTTP server with automatic lifecycle management
- Free-form report generation using programmatic HTML composition
- Supports Chart.js, Plotly.js, and DataTables for rich visualizations
- Designed for container/WSL environments with localhost-only server
- No predefined templates - fully dynamic report generation based on user requests

### 1.3.0 (2025-10-24)
- Added `billing-reporter` skill for billing and usage analysis
- Now includes 23 comprehensive skills
- New skill enables investigation of costs across single or multiple organizations
- Supports usage trend analysis, cost driver identification, and optimization recommendations
- Leverages MCP server tools (`get_org_info`, `get_usage_stats`) for live data analysis

### 1.2.0 (2025-10-24)
- Added `limacharlie-expert` entry point skill
- Now includes 22 comprehensive skills
- Entry point skill provides high-level component overview and interconnections
- Focus on component mechanics and how LimaCharlie components connect together
- Routes users to appropriate specialized skills based on task requirements

### 1.1.0 (2025-10-24)
- Added `onboard-external-telemetry` skill for beginner-friendly data source onboarding
- Now includes 21 comprehensive skills
- New skill includes 6 detailed walkthroughs (AWS, M365, Okta, Azure, CrowdStrike, Syslog)
- Complete reference for 50+ adapter types
- Extensive troubleshooting guide for common onboarding issues

### 1.0.0 (2025-10-22)
- Initial release with 20 comprehensive skills
- Covers all major LimaCharlie platform components
- Based on 281 documentation files and complete SDK references
- Includes 200+ working examples and 100+ best practices

---

**Note**: These skills are designed to work with Claude Code, Claude.ai (paid plans), and the Claude API. They provide specialized knowledge for security operations, detection engineering, incident response, and platform management using LimaCharlie.
