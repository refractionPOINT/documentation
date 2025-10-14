# SecOps Development

LimaCharlie provides a comprehensive development environment for security operations teams to build, test, and deploy detection and response capabilities.

## Development Workflow

The typical SecOps development workflow in LimaCharlie follows these stages:

1. **Local Development**: Write and test detection rules, response actions, and automation logic locally
2. **Testing**: Validate rules against sample data, test events, or test environments
3. **Staging**: Deploy to a staging organization for integration testing
4. **Production**: Push verified rules to production organizations
5. **Monitoring**: Track rule performance and tune as needed

## Detection & Response (D&R) Rules

D&R rules are the foundation of automated security operations in LimaCharlie. They define:

- **Detect**: What events or conditions to look for
- **Respond**: What actions to take when conditions are met

### Rule Structure

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: cmd.exe
    - op: contains
      path: event/COMMAND_LINE
      value: "/c"

respond:
  - action: report
    name: suspicious_cmd_execution
```

More complex example with multiple response actions:

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

Use the LimaCharlie CLI or API to test rules against historical data:

```bash
limacharlie dr test --rule my_rule.yaml --events sample_events.json
```

Or test against specific events:

```bash
limacharlie dr test --rule suspicious_powershell --event test_event.json
```

#### Web Interface Testing

Use the web interface to test rules interactively:

1. Navigate to D&R Rules
2. Click "Test Rule"
3. Paste sample event data
4. View match results and responses

Test rules against:
- Historical event data
- Synthetic test events
- Live event streams in test mode

## Version Control Integration

LimaCharlie supports infrastructure-as-code approaches for managing security operations:

- Store D&R rules in Git repositories
- Use CI/CD pipelines to deploy changes
- Track changes and roll back when needed

### Infrastructure as Code

Export and version control:
- D&R rules
- Output configurations
- Organization settings
- Service extensions

### Example CI/CD Workflows

**GitHub Actions:**

```yaml
# .github/workflows/deploy-rules.yml
name: Deploy D&R Rules

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to LimaCharlie
        run: |
          limacharlie dr import --file rules/*.yaml
        env:
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
```

**Python-based deployment:**

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

LimaCharlie integrates with:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

## Development Best Practices

### 1. Test Before Deploying

Always validate rules in a test environment before production deployment. Test rules against diverse event datasets and validate both positive and negative test cases.

### 2. Use Descriptive Names

Name rules clearly to indicate their purpose:
- `lateral_movement_psexec`
- `credential_dump_lsass`
- `webshell_detection_aspx`

### 3. Add Metadata

Include metadata in rules for documentation and tracking:

```yaml
metadata:
  author: security-team
  severity: high
  mitre: T1021.002
  description: Detects PsExec lateral movement
```

### 4. Version Your Rules

Use semantic versioning for rule sets to track changes over time. Document rule changes in commit messages and maintain clear version control history.

### 5. Monitor Performance

Track rule performance metrics:
- False positive rate
- Detection coverage
- Response time
- Resource usage

Optimize rule efficiency to minimize sensor impact:
- Use appropriate event types for detections
- Leverage caching for repeated lookups
- Monitor rule execution metrics
- Monitor performance impact of complex rules

### 6. Rule Development Process

- Start with broad detection logic, then refine based on false positives
- Use meaningful rule names and descriptions
- Document expected behavior and test cases
- Version control all rule changes

### 7. Security Best Practices

- Rotate API keys regularly
- Use least-privilege access controls
- Audit configuration changes
- Encrypt sensitive data in transit and at rest

## Development Tools

### LimaCharlie CLI

The command-line interface for managing LimaCharlie resources:

```bash
# Install
pip install limacharlie

# Authenticate
limacharlie login

# List rules
limacharlie dr list

# Import rules
limacharlie dr import --file rule.yaml

# Export rules
limacharlie dr export --output rules/

# Deploy rules
limacharlie dr push ./rules/

# Test detections
limacharlie dr test --rule suspicious_powershell --event test_event.json
```

### API Access

Programmatic access via REST API:

**Python:**

```python
from limacharlie import Manager

# Initialize
lc = Manager(api_key="your-api-key", oid="your-org-id")

# List D&R rules
rules = lc.rules()

# Add new rule
lc.add_rule({
    "name": "my_rule",
    "detect": {...},
    "respond": [...]
})
```

**REST API:**

```bash
curl -X POST https://api.limacharlie.io/v1/org/YOUR_OID/sensors \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### SDK Libraries

Official SDKs available for:
- Python
- JavaScript/Node.js
- Go

**Python SDK Examples:**

```python
from limacharlie import Manager

lc = Manager(oid="your-org-id", secret_api_key="your-api-key")

# Query sensors
sensors = lc.sensors()

# Execute commands
sensor = lc.sensor("sensor-id")
sensor.task("os_processes")
```

### VS Code Extension

LimaCharlie provides VS Code integration for:
- Syntax highlighting for D&R rules
- Rule validation and linting
- Integrated testing
- Deployment shortcuts

## Testing Strategies

### Unit Testing

Test individual rule components:

```python
def test_process_detection():
    rule = load_rule("detect_malicious_process.yaml")
    event = create_test_event(process="evil.exe")
    assert rule.matches(event)
```

### Integration Testing

Test rules against realistic data sets:

1. Collect sample events from test environment
2. Run rules against sample data
3. Validate expected detections and responses

### Performance Testing

Ensure rules scale appropriately:

- Test with high event volumes
- Monitor resource consumption
- Optimize expensive operations

## Debugging

### Logging

Enable verbose logging for troubleshooting:

```yaml
detect:
  # ... detection logic
  
respond:
  - action: report
    name: my_detection
    metadata:
      debug: true  # Enable debug logging
```

### Event Replay

Replay historical events to test rule changes:

```bash
limacharlie replay --start "2025-01-01" --end "2025-01-02" --rule new_rule.yaml
```

## Deployment Strategies

### Blue/Green Deployment

1. Deploy new rules to test organization
2. Validate performance and accuracy
3. Switch production to new rule set
4. Keep old rules as backup

### Canary Deployment

1. Deploy new rules to subset of sensors
2. Monitor for issues
3. Gradually increase coverage
4. Full rollout once validated

### Feature Flags

Use rule tags to enable/disable rules dynamically:

```yaml
detect:
  # ... detection logic

metadata:
  enabled: true
  tags: [experimental, canary]
```

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

## Collaboration

### Team Development

- Use separate organizations for dev/staging/prod
- Share rule templates via version control
- Document rule changes in commit messages
- Review rules before merging to main branch
- Use staging environments before production deployment

### Knowledge Sharing

- Document detection logic and rationale
- Share threat intelligence context
- Maintain playbooks for response actions
- Create rule libraries for common scenarios

## Resources

- [API Documentation](https://api.limacharlie.io/static/swagger/)
- [Python SDK Reference](https://github.com/refractionPOINT/python-limacharlie)
- [D&R Rule Examples](https://github.com/refractionPOINT/rules)
- [Community Resources](https://community.limacharlie.io)