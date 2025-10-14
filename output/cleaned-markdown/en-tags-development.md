# SecOps Development

LimaCharlie provides a comprehensive development environment for security operations teams to build, test, and deploy detection and response capabilities.

## Development Workflow

The typical SecOps development workflow in LimaCharlie follows these stages:

1. **Local Development**: Write and test detection rules locally
2. **Testing**: Validate rules against sample data or test environments
3. **Deployment**: Push rules to production organizations
4. **Monitoring**: Track rule performance and tune as needed

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

### Testing Rules

Use the LimaCharlie CLI or API to test rules against historical data:

```bash
limacharlie dr test --rule my_rule.yaml --events sample_events.json
```

## Version Control Integration

LimaCharlie supports infrastructure-as-code approaches for managing security operations:

- Store D&R rules in Git repositories
- Use CI/CD pipelines to deploy changes
- Track changes and roll back when needed

### Example CI/CD Workflow

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

## Development Best Practices

### 1. Test Before Deploying

Always validate rules in a test environment before production deployment.

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

Use semantic versioning for rule sets to track changes over time.

### 5. Monitor Performance

Track rule performance metrics:
- False positive rate
- Detection coverage
- Response time
- Resource usage

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
```

### API Access

Programmatic access via REST API:

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

### SDK Libraries

Official SDKs available for:
- Python
- JavaScript/Node.js
- Go

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

### Rule Testing Interface

Use the web interface to test rules interactively:

1. Navigate to D&R Rules
2. Click "Test Rule"
3. Paste sample event data
4. View match results and responses

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

## Collaboration

### Team Development

- Use separate organizations for dev/staging/prod
- Share rule templates via version control
- Document rule changes in commit messages
- Review rules before merging to main branch

### Knowledge Sharing

- Document detection logic and rationale
- Share threat intelligence context
- Maintain playbooks for response actions
- Create rule libraries for common scenarios