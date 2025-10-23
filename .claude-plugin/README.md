# LimaCharlie Skills for Claude

This directory contains the marketplace definition for the LimaCharlie Skills collection.

## What are Skills?

Skills are specialized instruction sets that Claude loads to enhance performance on specific tasks. Each skill contains comprehensive documentation, examples, and best practices for working with different aspects of the LimaCharlie SecOps Cloud Platform.

## Available Skills

This collection includes **20 specialized skills** organized into 6 categories:

### Core Platform Operations
- **dr-rule-builder** - Create Detection & Response rules
- **sensor-manager** - Deploy and manage endpoint sensors
- **adapter-configurator** - Configure data source adapters

### Data Operations
- **lcql-query-builder** - Write and optimize queries
- **output-configurator** - Route telemetry to SIEMs and data lakes
- **artifact-collector** - Collect forensic artifacts

### Security Operations
- **incident-responder** - Execute incident response workflows
- **threat-hunter** - Conduct proactive threat hunting
- **yara-manager** - Manage YARA malware detection rules

### Development & Integration
- **extension-developer** - Build custom extensions
- **api-integrator** - Use LimaCharlie APIs and SDKs
- **playbook-automator** - Create automated workflows

### Advanced Features
- **stateful-rule-designer** - Create complex event correlation rules
- **cloud-security-monitor** - Monitor AWS, Azure, and GCP
- **threat-intel-integrator** - Integrate threat intelligence feeds

### Platform Management
- **config-hive-manager** - Manage configuration storage
- **sigma-rule-deployer** - Deploy managed rulesets
- **infrastructure-as-code** - Manage config as code

### Specialized Use Cases
- **forensic-analyst** - Conduct digital forensics
- **performance-optimizer** - Optimize performance and costs

## Installation

### For Claude Code Users

These skills are located in the `skills/` directory and will be automatically discovered by Claude Code when working in this repository.

### For Claude.ai Users

1. Navigate to Settings → Skills
2. Upload individual skill folders from the `../skills/` directory
3. Skills will activate automatically based on context

### For API Users

Skills can be referenced via the Claude Skills API. See the [Skills API documentation](https://docs.anthropic.com/en/docs/build-with-claude/skills) for details.

## Usage

Skills activate automatically when Claude detects you're working on related tasks. They can also be manually invoked:

- "Help me create a D&R rule..." → activates **dr-rule-builder**
- "How do I deploy sensors?" → activates **sensor-manager**
- "I need to investigate this alert" → activates **incident-responder** or **threat-hunter**
- "Set up AWS monitoring" → activates **cloud-security-monitor**

## Skill Structure

Each skill follows this structure:

```
skills/
└── skill-name/
    └── SKILL.md          # Main skill definition with YAML frontmatter
```

The `SKILL.md` file contains:
- YAML frontmatter with name and description
- Comprehensive instructions and examples
- Best practices and troubleshooting
- Command references and code samples

## Development

### Creating New Skills

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: my-skill-name
description: Clear description of when to use this skill
---

# Skill Title

[Your comprehensive instructions here]
```

3. Update `marketplace.json` to include the new skill

### Updating Skills

1. Edit the relevant `SKILL.md` file
2. Test the skill with Claude Code
3. Update version in `marketplace.json` if needed

## Resources

- **LimaCharlie Documentation**: https://docs.limacharlie.io
- **Skills Documentation**: https://docs.anthropic.com/en/docs/build-with-claude/skills
- **LimaCharlie Community**: https://slack.limacharlie.io
- **Support**: support@limacharlie.io

## License

These skills are provided as part of the LimaCharlie documentation repository. See the main repository LICENSE for details.

## Contributing

Contributions are welcome! Please:

1. Follow the existing skill structure and format
2. Include comprehensive examples and documentation
3. Test skills thoroughly before submitting
4. Update the marketplace.json file

## Version History

- **1.0.0** (2025-10-22) - Initial release with 20 comprehensive skills
