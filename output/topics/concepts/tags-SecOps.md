# SecOps Development

**LimaCharlie's SecOps capabilities allow security teams to build, deploy, and operate custom security tooling at scale.**

## Overview

SecOps Development in LimaCharlie enables you to create custom detection and response (D&R) rules, automate security operations, integrate with third-party tools, and build tailored security workflows.

## Core Components

### Detection & Response (D&R) Rules

D&R rules are the foundation of SecOps development in LimaCharlie. They allow you to:

- Define custom detection logic using event matching
- Trigger automated responses when threats are detected
- Chain multiple actions together for complex workflows
- Test rules in isolation before deploying to production

**Basic D&R Rule Structure:**

```yaml
detect:
  event: NEW_PROCESS
  op: starts with
  path: /tmp/
  
respond:
  - action: report
    name: suspicious_process_execution
  - action: task
    command: deny_tree
    investigation: true
```

### Event Types

LimaCharlie sensors generate dozens of event types that can be used in detection logic:

- Process events (NEW_PROCESS, TERMINATE_PROCESS)
- Network events (NEW_CONNECTION, DNS_REQUEST)
- File events (FILE_CREATE, FILE_MODIFIED, FILE_DELETE)
- Registry events (REGISTRY_CREATE, REGISTRY_WRITE) [Windows]
- User events (USER_LOGIN, USER_LOGOFF)
- And many more...

### Response Actions

When detections trigger, you can execute various response actions:

- **report**: Generate a detection report
- **task**: Execute sensor commands (isolate, deny_tree, etc.)
- **action**: Trigger automation or integrations
- **add_tag**: Apply tags to endpoints
- **service_request**: Call external webhooks or services

### Automation & Integrations

LimaCharlie supports multiple automation methods:

1. **Outputs**: Stream detections to external systems (SIEM, SOAR, ticketing)
2. **Actions**: HTTP callbacks and webhooks
3. **Service Requests**: Call external APIs from D&R rules
4. **FP&A (False Positive & Absence)**: Automated alert enrichment and filtering

## Development Workflow

### 1. Rule Development

- Start with the web interface rule builder
- Test against historical data using replay
- Validate logic with known true/false positives
- Export rules as YAML for version control

### 2. Testing

```bash
# Test a rule against historical events
limacharlie rules test --rule-file my_rule.yaml --org my-org
```

### 3. Deployment

- Deploy individually via UI or CLI
- Bulk deploy using infrastructure-as-code
- Use staging organizations for pre-production testing
- Apply rules selectively using tags and filters

### 4. Monitoring

- Review detection rates and false positives
- Monitor performance impact on endpoints
- Adjust thresholds and tune logic
- Archive or deprecate ineffective rules

## Best Practices

### Rule Development

1. **Be specific**: Narrow detection scope to reduce false positives
2. **Use filters**: Apply rules only to relevant endpoints using tags
3. **Test thoroughly**: Validate against known good and bad activity
4. **Document intent**: Add clear descriptions explaining rule purpose
5. **Version control**: Store rules in git for change tracking

### Performance Optimization

- Avoid overly broad event matching
- Use efficient operators (equals over contains when possible)
- Limit expensive operations (hashing, external lookups)
- Monitor sensor performance metrics

### Security Considerations

- Follow least privilege for API keys and permissions
- Audit rule changes and access logs
- Encrypt sensitive data in transit and at rest
- Test destructive actions in non-production first

## Advanced Topics

### Custom Event Generation

Create synthetic events for tracking custom metrics:

```yaml
respond:
  - action: report
    name: custom_metric
    metadata:
      metric_name: login_count
      value: "{{ .event.user }}"
```

### Multi-Stage Detection

Chain multiple events together for behavioral detection:

```yaml
detect:
  op: and
  rules:
    - event: NEW_PROCESS
      path: cmd.exe
    - event: NEW_CONNECTION
      after: 5s
      
respond:
  - action: report
    name: suspicious_command_with_network
```

### Integration Patterns

Common integration scenarios:

- **Enrichment**: Query threat intelligence APIs during detection
- **Ticketing**: Auto-create tickets in Jira/ServiceNow
- **SOAR**: Trigger playbooks in Cortex XSOAR, Tines, etc.
- **SIEM**: Forward events to Splunk, Sentinel, Chronicle

## Resources

- [D&R Rule Syntax Reference](/docs/detection-and-response)
- [Event Type Documentation](events.md)
- [Sensor Commands Reference](/docs/sensor-commands)
- [API Documentation](/docs/api)
- [Community Rules Repository](https://github.com/refractionPOINT/rules)

## Support

For questions or assistance with SecOps development:

- Community Slack: [limacharlie.slack.com](https://limacharlie.slack.com)
- GitHub Issues: [github.com/refractionPOINT/lc-public](https://github.com/refractionPOINT/lc-public)
- Email: support@limacharlie.io