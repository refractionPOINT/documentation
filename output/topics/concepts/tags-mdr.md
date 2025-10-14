# Security Service Providers (MSSP, MSP, MDR)

LimaCharlie was purpose-built for Security Service Providers like MSSPs, MSPs, and MDR providers. The platform's multi-tenant architecture, flexible pricing, and automation capabilities make it an ideal foundation for building and scaling security services.

## Key Capabilities for Service Providers

### Multi-Tenant Architecture

- **Organization Hierarchy**: Manage multiple client organizations from a single interface
- **Cross-Organization Views**: Monitor and manage security across all clients
- **Isolated Environments**: Each client organization maintains complete data isolation
- **Granular Access Control**: Define precise permissions for team members across organizations

### Flexible Business Models

LimaCharlie supports various service provider business models:

- **Reseller Model**: Purchase capacity and resell to clients with your own markup
- **White-Label**: Brand the platform as your own service
- **Hybrid Approach**: Combine multiple models based on client needs

### Automation at Scale

- **Infrastructure as Code**: Define security policies, detection rules, and configurations as code
- **Replicator**: Deploy configurations across multiple organizations with a single command
- **CI/CD Integration**: Automate deployment and updates through your existing pipelines
- **API-First Design**: Programmatically manage all aspects of the platform

### Cost-Effective Pricing

- **Usage-Based**: Only pay for what you use - no per-seat or per-sensor licensing
- **Predictable Margins**: Transparent pricing helps you forecast costs and margins
- **Volume Discounts**: Benefit from economies of scale as you grow

## Getting Started as a Service Provider

### 1. Account Structure

Create a hierarchical organization structure:

```
Your Company (Root Org)
├── Client A
│   ├── Production Environment
│   └── Development Environment
├── Client B
│   └── Production Environment
└── Internal/Demo
    └── Testing Environment
```

### 2. Define Your Service Offering

Determine what capabilities you'll provide:

- **EDR/XDR**: Endpoint detection and response
- **SIEM**: Log collection and analysis
- **Threat Hunting**: Proactive threat detection
- **Incident Response**: Automated response actions
- **Compliance Monitoring**: Continuous compliance validation
- **Custom Integrations**: Connect to client-specific tools

### 3. Create Standard Configurations

Build reusable templates for:

- Detection & Response rules
- Output destinations (SIEM, ticketing, etc.)
- Sensor configurations
- Retention policies
- Alert routing

### 4. Implement Automation

Use the Replicator to deploy your standard configurations:

```yaml
# replicator.yaml
organizations:
  - name: client-a-prod
    detection_rules:
      - ./rules/standard-edr.yaml
      - ./rules/ransomware-detection.yaml
    outputs:
      - ./outputs/client-siem.yaml
    retention:
      events: 90d
      detections: 365d
```

Deploy across clients:

```bash
python -m limacharlie replicator apply -f replicator.yaml
```

### 5. Set Up Monitoring and Alerting

Configure centralized monitoring:

- **Outputs**: Route detections to your SOC tools
- **Webhooks**: Integrate with your ticketing system
- **Slack/Teams**: Real-time notifications
- **Custom Dashboards**: Build views for your analysts

## Best Practices

### Security Isolation

- Never share API keys between client organizations
- Use service accounts with least privilege access
- Enable audit logging for all administrative actions
- Implement multi-factor authentication for all users

### Configuration Management

- Store all configurations in version control
- Use CI/CD to deploy changes consistently
- Test changes in a dev/staging organization first
- Document your standard operating procedures

### Client Onboarding

Create a standardized onboarding process:

1. Create client organization
2. Deploy sensors to endpoints
3. Apply standard detection rules
4. Configure outputs and integrations
5. Set up custom rules (if needed)
6. Validate monitoring coverage
7. Provide client access (if applicable)

### Performance Optimization

- Use appropriate retention periods for each data type
- Leverage sampling for high-volume events
- Implement efficient detection rules
- Monitor your usage and costs regularly

## Advanced Features for Service Providers

### Custom Integrations

Build integrations using:

- **REST API**: Programmatic access to all platform features
- **Webhooks**: Real-time event notifications
- **Outputs**: Stream data to any destination
- **Extensions**: Custom capabilities using serverless functions

### Threat Intelligence

- **Built-in Feeds**: Access to LimaCharlie's threat intelligence
- **Custom Feeds**: Import your own threat intelligence
- **Sharing**: Share indicators across client organizations (with permission)

### Hunting and Investigation

- **Cross-Organization Queries**: Hunt across multiple clients
- **Historical Search**: Query retained telemetry
- **Live Terminal**: Interactive access to endpoints
- **Artifacts**: Collect forensic evidence

### Compliance and Reporting

- **Audit Logs**: Complete audit trail of all actions
- **Compliance Rules**: Automated compliance validation
- **Custom Reports**: Generate client-specific reports
- **Data Retention**: Configure retention per compliance requirements

## Pricing for Service Providers

LimaCharlie offers flexible pricing for service providers:

- **Volume Discounts**: Lower per-unit costs as you scale
- **Commit Discounts**: Save by committing to usage levels
- **Custom Agreements**: Tailored pricing for large deployments

Contact the sales team for service provider pricing: [https://limacharlie.io/contact](https://limacharlie.io/contact)

## Support and Resources

### Documentation

- [Getting Started Guide](/docs/getting-started)
- [API Reference](/docs/api)
- [Detection & Response Rules](/docs/detection-and-response)
- [Replicator Documentation](/docs/replicator)

### Community

- [Slack Community](https://slack.limacharlie.io): Connect with other service providers
- [GitHub](https://github.com/refractionpoint): Open-source tools and examples
- [Blog](https://limacharlie.io/blog): Best practices and updates

### Professional Services

LimaCharlie offers professional services for service providers:

- **Onboarding Assistance**: Get help setting up your practice
- **Custom Development**: Build custom integrations and features
- **Training**: Train your team on the platform
- **Architecture Review**: Optimize your deployment

## Example Use Cases

### MSSP: 24/7 Monitoring

An MSSP uses LimaCharlie to provide 24/7 security monitoring:

- Deploy EDR sensors to client endpoints
- Implement standard detection rules across all clients
- Route alerts to SOC's ticketing system
- Provide custom dashboards for each client
- Bill clients based on endpoint count

### MSP: Security Add-On

An MSP adds security to their service offering:

- Integrate LimaCharlie with RMM tools
- Provide ransomware protection to clients
- Monitor for software vulnerabilities
- Include security in existing monthly fees
- Scale offering as client base grows

### MDR: Managed Detection and Response

An MDR provider builds their service on LimaCharlie:

- Use advanced detection rules and threat intelligence
- Leverage artifact collection for investigations
- Implement automated response actions
- Provide 24/7 incident response
- Offer tiered service levels

## Next Steps

1. [Sign up for a LimaCharlie account](https://app.limacharlie.io/signup)
2. Review the [Getting Started Guide](/docs/getting-started)
3. Explore the [API Documentation](/docs/api)
4. Join the [Slack Community](https://slack.limacharlie.io)
5. Contact sales to discuss service provider pricing