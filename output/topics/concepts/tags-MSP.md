# Security Service Providers (MSSP, MSP, MDR)

LimaCharlie is designed to support security service providers, including MSSPs (Managed Security Service Providers), MSPs (Managed Service Providers), and MDR (Managed Detection and Response) providers. The platform provides comprehensive multi-tenancy capabilities and automation features that enable service providers to efficiently manage security operations for multiple clients.

## Multi-Tenancy Architecture

LimaCharlie's architecture is built from the ground up to support multi-tenancy, allowing service providers to manage multiple customer organizations from a single interface while maintaining strict data isolation and security boundaries.

### Organization Management

Service providers can create and manage multiple organizations (tenants), each representing a different customer or business unit. Each organization maintains:

- Separate data storage and processing
- Independent billing and resource tracking
- Isolated security policies and configurations
- Dedicated API keys and access controls

### Hierarchical Access Control

The platform supports hierarchical access control, enabling service providers to:

- Grant different permission levels to different team members
- Provide customers with limited access to their own data
- Maintain administrative control across all managed organizations
- Delegate specific responsibilities without compromising security

## Automation and Orchestration

LimaCharlie provides extensive automation capabilities that enable service providers to scale their operations efficiently.

### Detection & Response Rules

Create and deploy detection and response rules across multiple customer organizations:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: "powershell.exe"
respond:
  - action: report
    name: suspicious_powershell
```

### Infrastructure as Code

Manage your security infrastructure as code using LimaCharlie's REST API and CLI tools. This enables:

- Version-controlled security configurations
- Automated deployment across customer environments
- Consistent policy enforcement
- Rapid onboarding of new customers

## Resource Management

### Resource Limits and Quotas

Set resource limits and quotas for each customer organization to ensure fair usage and predictable costs:

- Event ingestion limits
- Storage quotas
- API rate limits
- Retention policies

### Billing and Cost Tracking

Track resource consumption and costs on a per-organization basis:

- Detailed usage reports
- Cost attribution to specific customers
- Flexible billing models
- Budget alerts and notifications

## Customer Portal and Self-Service

Enable customers to access their own security data and insights through a dedicated portal:

- Read-only or limited-write access to their organization
- Custom dashboards and reports
- Alert notifications and incident management
- Service request workflows

## API and Integration

LimaCharlie's comprehensive REST API enables deep integration with service provider tools and workflows:

- Automated customer provisioning
- Integration with ticketing systems
- SIEM and SOAR connectivity
- Custom reporting and analytics

Example API call to create a new organization:

```bash
curl -X POST "https://api.limacharlie.io/v1/orgs" \
  -H "Authorization: bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer-org",
    "template": "base-security-template"
  }'
```

## Best Practices for Service Providers

### Standardization

- Develop standard security baselines for different customer profiles
- Use templates for consistent deployment
- Maintain a library of reusable detection and response rules

### Segregation

- Maintain strict data segregation between customers
- Use dedicated API keys for each customer organization
- Implement role-based access control (RBAC) for your team

### Automation

- Automate repetitive tasks wherever possible
- Use Infrastructure as Code for configuration management
- Implement automated testing for security rules

### Monitoring and Reporting

- Set up centralized monitoring across all customer organizations
- Create standardized reports for different stakeholder levels
- Implement proactive alerting for critical issues

### Scalability

- Design processes that scale as you add customers
- Use automation to reduce per-customer operational overhead
- Leverage LimaCharlie's cloud-native architecture for elastic scaling

## Support and Resources

LimaCharlie provides dedicated support for service providers:

- Technical account management
- Architecture consulting
- Custom training and onboarding
- Priority support channels

For more information on how LimaCharlie can support your service provider business, contact the sales team or consult the documentation.