# Platform and Use Cases

## Overview

LimaCharlie is a Security Infrastructure as a Service (SIaaS) platform providing comprehensive capabilities for endpoint detection and response (EDR), security operations, and threat management across diverse environments. The platform supports deployment across multiple use cases and organizational types, from enterprise security operations centers (SOCs) to managed security service providers (MSSPs) and security product developers.

## Platform Categories

### Endpoint Detection and Response (EDR)

LimaCharlie provides enterprise-grade EDR capabilities that enable real-time visibility and response across all endpoints in your environment.

**Core Capabilities:**
- Real-time monitoring of endpoint activities including processes, network connections, file operations, and registry changes
- Behavioral detection through Detection & Response (D&R) rules
- Automated response actions: kill processes, isolate hosts, delete files, execute custom commands
- Historical forensic data for incident investigation
- Cross-platform support: Windows, macOS, Linux, Chrome OS, and browser agents

**Deployment Scenarios:**
- Traditional enterprise endpoints (workstations, servers)
- Cloud workloads (AWS, Azure, GCP)
- Container environments and Kubernetes
- IoT and specialized systems
- Remote and distributed workforces

### Security Operations Center (SOC) Infrastructure

Build complete SOC infrastructure using LimaCharlie as your foundation, providing centralized visibility and orchestrated response capabilities.

**Infrastructure Components:**
- Centralized telemetry aggregation from endpoints, cloud services, and network devices
- Detection and response rule engine for custom security logic
- Integration with case management systems
- Orchestrated response across your security stack
- Real-time alerting and notification systems

**Data Sources:**
- Endpoint telemetry (EDR events)
- Cloud audit logs (AWS CloudTrail, Azure Activity Logs, GCP Audit Logs)
- Network traffic metadata
- Windows Event Logs and Sysmon
- Application logs
- Third-party security tool outputs

### Enterprise SOC

Organizations deploying LimaCharlie at enterprise scale benefit from centralized management, visibility, and control across multiple business units or environments.

**Enterprise Architecture:**
- Hierarchical organization structure (parent and child organizations)
- Consistent security policy application across all managed organizations
- Aggregated telemetry and detections for enterprise-wide visibility
- Delegated administration and access control
- Shared threat intelligence and detection rules
- Consolidated reporting and analytics

**Multi-Organization Management:**
- Parent organization manages multiple child organizations
- Individual organizations maintain their own sensors, detection rules, data retention, and access controls
- Centralized console for switching between organizations
- Unified billing and resource management
- Cross-organization threat hunting and investigation

**Use Cases:**
- Multi-national corporations with regional divisions
- Enterprises with separate business units requiring data isolation
- Organizations managing both corporate IT and operational technology (OT) environments
- Holding companies overseeing multiple subsidiaries

### Security Service Providers (MSSP, MSP, MDR)

LimaCharlie's multi-tenant architecture enables service providers to deliver security services at scale with complete customer isolation.

**Multi-Tenancy Architecture:**
- Parent organizations can create and manage multiple child organizations
- Complete data and operational isolation between customers
- Configuration inheritance from parent to child organizations
- Cross-organization management from a single interface
- Consolidated reporting across the customer base

**Service Provider Features:**

**Customer Onboarding:**
- API-driven organization creation
- Automated sensor deployment
- Template-based configuration deployment
- Bulk user provisioning

**Centralized Monitoring:**
- Unified dashboard viewing security events across all customers
- Alert aggregation from all managed organizations
- Cross-tenant search for IOCs and threats
- Consolidated threat intelligence sharing

**White-Label Capabilities:**
- Custom branding for customer-facing interfaces
- Branded email notifications
- Custom domain support
- Reseller pricing models

**Operational Efficiency:**
- Playbook-driven consistent incident response
- Rule templates deployable to multiple organizations
- Configuration management as code (Infrastructure as Code)
- Comprehensive API for automation

**Financial Management:**
- Usage-based billing with customer chargeback capabilities
- Detailed usage reporting per customer organization
- Volume discounts based on total sensor count
- Flexible licensing per customer

**Service Types:**

**Managed Security Service Provider (MSSP):**
- 24/7 security monitoring
- Threat detection and response
- Proactive threat hunting
- Vulnerability management
- Compliance reporting

**Managed Service Provider (MSP):**
- Endpoint protection
- Security monitoring
- Incident response
- Security awareness training
- Compliance assistance

**Managed Detection and Response (MDR):**
- Continuous monitoring
- Advanced threat detection
- Incident investigation
- Response orchestration
- Threat intelligence integration

### Cyber Threat Intelligence (CTI)

LimaCharlie provides comprehensive capabilities for building and operationalizing threat intelligence across your security operations.

**Intelligence Capabilities:**
- Ingest threat intelligence from various sources
- Create custom intelligence feeds
- Correlate telemetry with threat indicators
- Automate response actions based on threat intelligence
- Share intelligence across organizations

**Intelligence Sources:**

**Built-in Feeds:**
Curated threat intelligence feeds enabled with a single click.

**Custom Feeds:**
- Third-party threat intelligence providers
- Internal research and analysis
- Industry sharing groups (ISACs)
- Open source intelligence (OSINT)

**API Integration:**
```python
# Adding indicators via API
import requests

api_key = "your_api_key"
oid = "your_organization_id"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

indicator = {
    "indicator": "malicious-domain.com",
    "type": "domain",
    "tags": ["malware", "phishing"],
    "metadata": {
        "source": "internal_research",
        "confidence": "high"
    }
}

response = requests.post(
    f"https://api.limacharlie.io/v1/{oid}/indicators",
    headers=headers,
    json=indicator
)
```

**Detection & Response:**

**Automated Matching:**
LimaCharlie automatically correlates telemetry against intelligence feeds:
- Network connections to known malicious IPs/domains
- File hashes matching known malware
- Process executions matching threat patterns

**Detection Rules:**
```yaml
# Alert on connection to known C2 server
detect:
  event: NETWORK_CONNECTIONS
  op: exists
  path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
  
match:
  op: in_feed
  path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
  feed: c2_servers

respond:
  - action: report
    name: connection_to_c2
  - action: task
    command: deny_tree
```

**Intelligence Management:**

**Tagging & Categorization:**
- Threat actor names
- Campaign identifiers
- Attack techniques (MITRE ATT&CK)
- Industry sectors
- Confidence levels

**Lifecycle Management:**
- Set expiration dates for indicators
- Archive old intelligence
- Update confidence scores over time
- Track first/last seen timestamps

**Sharing & Collaboration:**
```bash
# Export indicators in STIX format
curl -X GET \
  "https://api.limacharlie.io/v1/{oid}/indicators/export?format=stix" \
  -H "Authorization: Bearer {api_key}"

# Import STIX bundle
curl -X POST \
  "https://api.limacharlie.io/v1/{oid}/indicators/import" \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json" \
  -d @stix_bundle.json
```

### Security Monitoring for DevOps

LimaCharlie provides security monitoring capabilities designed for DevOps environments, enabling security without compromising development velocity.

**DevOps Security Capabilities:**
- Monitor CI/CD pipeline for security issues
- Detect anomalous behavior in containerized environments
- Track infrastructure changes
- Identify security misconfigurations
- Maintain compliance while moving fast

**CI/CD Pipeline Security:**
Monitor build and deployment pipelines for:
- Unauthorized code changes
- Suspicious build processes
- Credential exposure in logs
- Malicious dependencies
- Container image vulnerabilities

**Container Monitoring:**
Track security events in containerized environments:
- Container escape attempts
- Privilege escalation
- Network anomalies
- File system changes
- Process execution

**Infrastructure as Code (IaC) Monitoring:**
- Unauthorized terraform/CloudFormation changes
- Configuration drift
- Privilege escalation in infrastructure
- Exposed secrets in code repositories

**Implementation Steps:**

**Step 1: Deploy Sensors**
```bash
# Install on Linux hosts
curl https://downloads.limacharlie.io/sensor/linux | sudo bash -s -- -i YOUR_INSTALLATION_KEY

# For Kubernetes environments
kubectl apply -f https://downloads.limacharlie.io/sensor/k8s/YOUR_INSTALLATION_KEY
```

**Step 2: Configure Detection Rules**
```yaml
# Detect unauthorized docker socket access
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: /var/run/docker.sock
    - op: exists
      path: event/PROCESS/COMMAND_LINE
      
respond:
  - action: report
    name: unauthorized_docker_access
```

**Step 3: Monitor CI/CD Events**
```bash
# Send CI/CD events via REST API
curl -X POST https://api.limacharlie.io/v1/YOUR_OID/insight \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "jenkins",
    "type": "build_started",
    "metadata": {
      "job": "production-deploy",
      "user": "jenkins-bot"
    }
  }'
```

**Common Detection Patterns:**

**Cryptocurrency Mining Detection:**
```yaml
detect:
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: ["xmrig", "minergate", "stratum+tcp"]
    - op: is
      path: event/PARENT/FILE_PATH
      value: /usr/bin/docker
respond:
  - action: report
    name: crypto_mining_in_container
  - action: task
    command: deny_tree
```

**Kubernetes API Access Monitoring:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: contains
      path: event/NETWORK_ACTIVITY/DESTINATION/IP_ADDRESS
      value: KUBERNETES_API_IP
    - op: is
      path: event/NETWORK_ACTIVITY/DESTINATION/PORT
      value: 443
    - not:
        op: contains
        path: event/PROCESS/FILE_PATH
        value: ["/usr/bin/kubectl", "/usr/local/bin/kubectl"]
respond:
  - action: report
    name: unauthorized_k8s_api_access
```

**Secrets Exposure Tracking:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: ["AWS_SECRET", "PRIVATE_KEY", "password="]
    - op: contains
      path: event/PARENT/COMMAND_LINE
      value: ["jenkins", "gitlab-runner", "circleci"]
respond:
  - action: report
    name: potential_secrets_in_logs
  - action: webhook
    url: YOUR_INCIDENT_RESPONSE_WEBHOOK
```

### File Integrity Monitoring (FIM)

File Integrity Monitoring tracks changes to files and registry keys on your systems, enabling detection of unauthorized modifications and compliance verification.

**FIM Capabilities:**
- File creation, modification, deletion detection
- Permission and ownership changes
- Registry key monitoring (Windows)
- Recursive directory monitoring
- Pattern-based exclusions

**Configuration:**
FIM is configured through sensor-specific rules defining which resources to monitor. The sensor continuously monitors these resources and reports changes to LimaCharlie cloud.

**Monitored Changes:**

**File System:**
- File creation
- File modification
- File deletion
- Permission changes
- Ownership changes

**Registry (Windows):**
- Key creation
- Key deletion
- Value changes
- Permission modifications

**Use Cases:**
- **Compliance**: Meet regulatory requirements for file integrity monitoring
- **Incident Detection**: Identify unauthorized system modifications
- **Malware Detection**: Detect malicious file changes
- **Configuration Management**: Track configuration drift
- **Forensics**: Maintain audit trails for investigation

**Best Practices:**
- Start focused with critical system files and configuration files
- Tune for your environment to reduce noise while maintaining visibility
- Review FIM alerts regularly to identify patterns
- Document baseline file states
- Coordinate with change management processes

### SOAR / Automation

LimaCharlie provides Security Orchestration, Automation and Response (SOAR) capabilities enabling automated detection, investigation, and response workflows.

**Automation Capabilities:**
- Automate repetitive security tasks
- Orchestrate complex multi-step workflows
- Integrate with external tools and services
- Respond to threats in real-time
- Reduce mean time to respond (MTTR)

**Automation Components:**

**Detection & Response Rules:**
D&R rules are the foundation of automation, allowing you to:
- Detect security events based on telemetry
- Automatically trigger responses when threats are detected
- Chain multiple actions together
- Integrate with external systems

**Automation Actions:**
- Isolate endpoints from the network
- Kill malicious processes
- Delete files
- Execute custom commands
- Send notifications
- Trigger external webhooks
- Create tickets in incident management systems

**Orchestration:**
Build complex workflows by:
- Chaining multiple D&R rules together
- Using outputs from one action as inputs to another
- Implementing conditional logic
- Integrating with third-party tools via APIs

**Integration Ecosystem:**
- SIEM platforms
- Ticketing systems
- Communication tools (Slack, Teams)
- Threat intelligence feeds
- Cloud platforms
- Custom APIs and webhooks

## Specialized Use Cases

### Threat Hunting

Use LimaCharlie's telemetry collection and historical search capabilities to proactively hunt for threats.

**Hunting Capabilities:**
- Query historical data to identify indicators of compromise
- Analyze patterns of behavior
- Investigate suspicious activities across infrastructure
- Pivot from one indicator to related activity
- Identify patterns and trends

### Incident Response

Rapidly investigate and respond to security incidents with real-time capabilities.

**Response Capabilities:**
- Execute commands remotely on endpoints
- Collect forensic artifacts
- Isolate compromised systems
- Remediate threats
- Reconstruct attack timelines
- Maintain evidence chains

### Compliance and Auditing

Collect detailed telemetry for compliance requirements including PCI DSS, HIPAA, SOC 2, and other frameworks.

**Compliance Features:**
- File integrity monitoring
- Privileged user activity tracking
- Comprehensive audit logs
- Compliance report generation
- Evidence collection and retention

### Cloud Security

Extend monitoring and protection to cloud workloads across AWS, Azure, and GCP.

**Cloud Capabilities:**
- Monitor container environments
- Secure serverless functions
- Protect cloud-native applications
- Ingest cloud audit logs
- Monitor cloud configurations

### Network Security Monitoring

Collect and analyze network traffic metadata to identify threats.

**Network Monitoring:**
- Anomalous communications detection
- Data exfiltration attempt identification
- Lateral movement detection
- DNS query monitoring
- Connection tracking

### User and Entity Behavior Analytics (UEBA)

Collect user activity data and analyze patterns to identify threats.

**UEBA Capabilities:**
- Compromised account detection
- Insider threat identification
- Privilege abuse detection
- Behavioral anomaly detection
- User activity baseline establishment

### Purple Teaming

LimaCharlie supports purple teaming exercises combining offensive and defensive tactics to improve security posture.

**Purple Teaming Features:**
- Attack simulation and adversary emulation
- Detection rule testing and validation
- Real-time telemetry analysis
- Response automation testing
- Detection-as-Code capabilities

**Exercise Benefits:**
- Improved detection capabilities
- Better incident response
- Knowledge transfer between teams
- Security control validation
- Cost-effective testing

### Building Security Products

LimaCharlie provides a platform for building custom security solutions.

**Development Capabilities:**
- Custom detection rule engine
- Rich telemetry from multiple sources
- Automation and orchestration
- Multi-tenancy support
- Flexible APIs and SDKs

**Development Workflow:**
1. Design your security product
2. Configure detection rules
3. Build automation workflows
4. Test and validate
5. Deploy using multi-tenant capabilities

### Mergers and Acquisitions Cyber Due Diligence

Use LimaCharlie for cybersecurity due diligence during M&A activities.

**Assessment Areas:**
- Infrastructure security evaluation
- Data security assessment
- Threat landscape understanding
- Compliance and governance review
- Security team capability assessment

**Due Diligence Process:**
1. Initial assessment through questionnaires
2. Technical review and analysis
3. Risk quantification
4. Comprehensive reporting
5. Post-acquisition integration planning

## Platform Support

### Platform Coverage

**Operating Systems:**
- Windows (7, 8, 10, 11, Server 2008+)
- Linux (most distributions)
- macOS (10.12+)
- Chrome OS

**Cloud Platforms:**
- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCP)

**Specialized Environments:**
- Kubernetes and container platforms
- IoT devices
- Point-of-sale systems
- Industrial control systems

### ChromeOS Support

LimaCharlie provides sensor support for ChromeOS devices enrolled in enterprise management.

**ChromeOS Capabilities:**
- System event monitoring
- Telemetry data collection
- Detection and response rules
- Incident investigation
- Compliance monitoring

**Deployment:**
Deploy sensors through enterprise management console to enrolled ChromeOS devices for unified fleet management.

## Additional Capabilities

### Observability Pipeline

The Observability Pipeline provides flexible data ingestion, processing, and routing for logs, metrics, and traces.

**Pipeline Components:**

**Sources:**
- File monitoring
- HTTP endpoints
- Cloud services (AWS CloudWatch, GCP Logging, Azure Monitor)
- Syslog
- Kafka

**Processors:**
- Parse JSON/CSV
- Add fields and enrich data
- Filter events
- Sample data
- Aggregate events

**Destinations:**
- LimaCharlie platform
- Amazon S3
- Elasticsearch
- Splunk
- Custom HTTP endpoints

### Adapters

Adapters enable ingestion of data from various sources beyond native EDR telemetry:

**Input Methods:**
- Standard input (stdin, stdin JSON)
- File monitoring
- Syslog
- Windows Event Logs (EVTX)

**Cloud Storage:**
- Amazon S3
- Google Cloud Storage
- Google Cloud Pub/Sub
- Azure Storage Blob

**Message Queues:**
- Amazon SQS
- Azure Event Hub

**Security Platforms:**
- Microsoft Defender
- Microsoft 365
- Sophos
- Sublime Security

**Identity & Access:**
- Okta
- Microsoft Entra ID
- 1Password

**Email Security:**
- IMAP
- Mimecast

**Business Applications:**
- IT Glue
- PandaDoc
- Google Workspace

### Outputs

Configure destinations for events, alerts, and telemetry:

**Output Destinations:**
- SMTP (email)
- Splunk
- Amazon S3
- Google Cloud BigQuery
- Google Cloud Storage
- Webhook (individual and bulk)
- Tines
- Syslog
- Slack
- SFTP/SCP
- OpenSearch
- Humio
- Azure Storage Blob
- Azure Event Hub

## Best Practices

### Architecture
- Use separate environments for staging and production
- Implement configuration version control
- Maintain documentation for custom rules and playbooks
- Regular backup of critical configurations

### Operations
- Establish clear SLAs
- Implement tiered alerting and escalation procedures
- Conduct regular threat hunting exercises
- Continuous rule tuning and optimization

### Security
- Enable MFA for all accounts
- Implement least privilege access
- Conduct regular access reviews
- Maintain comprehensive audit logging

### Growth
- Start with core capabilities and expand gradually
- Gather feedback regularly
- Track key performance metrics
- Invest in automation early

## Getting Started

Organizations can begin using LimaCharlie by:

1. **Account Setup**: Create an organization and configure initial settings
2. **Sensor Deployment**: Deploy sensors to endpoints across your environment
3. **Detection Configuration**: Set up detection rules tailored to your needs
4. **Integration**: Connect to existing security tools and workflows
5. **Operationalization**: Implement monitoring, detection, and response workflows

For service providers and enterprise deployments, contact LimaCharlie sales to discuss advanced features, multi-tenancy, and professional services.