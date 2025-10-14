# SecOps Development

LimaCharlie provides a comprehensive development environment for building, testing, and deploying security operations workflows and detection logic.

## Development Workflow

The typical SecOps development workflow in LimaCharlie follows these stages:

1. **Local Development**: Write and test detection rules, response actions, and automation logic
2. **Testing**: Validate rules against test data and simulated events
3. **Staging**: Deploy to a staging organization for integration testing
4. **Production**: Roll out verified logic to production environments

## Detection & Response (D&R) Rules

D&R rules are the core of LimaCharlie's detection capabilities. They combine detection logic with automated response actions.

### Rule Structure

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: "powershell.exe"
    - op: contains
      path: event/COMMAND_LINE
      value: "-encodedcommand"

respond:
  - action: report
    name: suspicious_powershell
  - action: task
    command: deny_tree
```

### Testing Rules

Use the LimaCharlie CLI or web interface to test rules against:

- Historical event data
- Synthetic test events
- Live event streams in test mode

## Automation & Orchestration

LimaCharlie supports multiple automation approaches:

### Output Streams

Forward detections and events to external systems:

- SIEM platforms
- SOAR tools
- Custom webhooks
- Message queues

### Service Extensions

Extend LimaCharlie functionality with custom code:

- Python-based extensions
- Serverless function integrations
- Custom API endpoints

## API & SDK Development

Build custom integrations and tools using LimaCharlie's REST API:

### Python SDK

```python
from limacharlie import Manager

lc = Manager(oid="your-org-id", secret_api_key="your-api-key")

# Query sensors
sensors = lc.sensors()

# Execute commands
sensor = lc.sensor("sensor-id")
sensor.task("os_processes")
```

### REST API

```bash
curl -X POST https://api.limacharlie.io/v1/org/YOUR_OID/sensors \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

## Version Control & CI/CD

Manage LimaCharlie configurations as code:

### Infrastructure as Code

Export and version control:

- D&R rules
- Output configurations
- Organization settings
- Service extensions

### CI/CD Integration

Automate deployment using:

- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

Example GitHub Actions workflow:

```yaml
name: Deploy LimaCharlie Rules

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy rules
        env:
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
          LC_OID: ${{ secrets.LC_OID }}
        run: |
          python deploy_rules.py
```

## Best Practices

### Rule Development

- Start with broad detection logic, then refine based on false positives
- Use meaningful rule names and descriptions
- Document expected behavior and test cases
- Version control all rule changes

### Testing

- Test rules against diverse event datasets
- Validate both positive and negative test cases
- Monitor performance impact of complex rules
- Use staging environments before production deployment

### Performance

- Optimize rule efficiency to minimize sensor impact
- Use appropriate event types for detections
- Leverage caching for repeated lookups
- Monitor rule execution metrics

### Security

- Rotate API keys regularly
- Use least-privilege access controls
- Audit configuration changes
- Encrypt sensitive data in transit and at rest

## Development Tools

### LimaCharlie CLI

Command-line tool for managing LimaCharlie resources:

```bash
# Install
pip install limacharlie

# Configure
limacharlie login

# Deploy rules
limacharlie dr push ./rules/

# Test detections
limacharlie dr test --rule suspicious_powershell --event test_event.json
```

### VS Code Extension

LimaCharlie provides VS Code integration for:

- Syntax highlighting for D&R rules
- Rule validation and linting
- Integrated testing
- Deployment shortcuts

## Resources

- [API Documentation](https://api.limacharlie.io/static/swagger/)
- [Python SDK Reference](https://github.com/refractionPOINT/python-limacharlie)
- [D&R Rule Examples](https://github.com/refractionPOINT/rules)
- [Community Resources](https://community.limacharlie.io)