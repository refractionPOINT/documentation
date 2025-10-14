# Network Monitoring

Network monitoring in LimaCharlie provides visibility into network traffic, connections, and communications across your infrastructure. This enables detection of malicious network activity, unauthorized connections, and data exfiltration attempts.

## Overview

LimaCharlie's network monitoring capabilities allow you to:

- Monitor network connections in real-time
- Detect suspicious network patterns
- Track data flows and communications
- Identify unauthorized network access
- Monitor DNS queries and responses
- Analyze network protocols and traffic

## Configuration

Network monitoring can be configured through Detection & Response (D&R) rules and collection policies to capture relevant network events from your sensors.

## Key Network Events

LimaCharlie captures various network-related events including:

- **NEW_CONNECTION**: New network connections established
- **DNS_REQUEST**: DNS query requests
- **HTTP_REQUEST**: HTTP/HTTPS requests
- **NETWORK_SUMMARY**: Periodic network activity summaries
- **CONNECTION_CLOSED**: Network connections terminated

## Detection Capabilities

Network monitoring enables detection of:

- Command and control (C2) communications
- Data exfiltration attempts
- Lateral movement
- Suspicious DNS queries
- Unauthorized outbound connections
- Port scanning and reconnaissance
- Protocol anomalies

## Best Practices

1. **Focus on anomalies**: Monitor for unusual network patterns rather than all traffic
2. **Baseline normal behavior**: Understand typical network activity before alerting on deviations
3. **Correlate events**: Combine network events with process and file events for context
4. **Use allowlists**: Reduce noise by allowlisting known-good connections
5. **Monitor DNS**: DNS is often an early indicator of compromise

---

# Security Monitoring for DevOps

Security monitoring for DevOps integrates security practices into the continuous integration and continuous deployment (CI/CD) pipeline, enabling teams to identify and respond to security issues throughout the software development lifecycle.

## Overview

LimaCharlie provides security monitoring capabilities that integrate seamlessly into DevOps workflows:

- Runtime security monitoring for containers and cloud workloads
- CI/CD pipeline security
- Infrastructure as code (IaC) security scanning
- Continuous compliance monitoring
- API and webhook integrations for automation

## DevOps Integration

### CI/CD Pipeline Integration

LimaCharlie can be integrated into CI/CD pipelines to:

- Scan container images for vulnerabilities
- Monitor build processes for suspicious activity
- Validate security configurations
- Enforce security policies before deployment
- Generate security attestations

### Container Security

Monitor containerized environments with:

- Runtime container monitoring
- Image vulnerability scanning
- Container escape detection
- Kubernetes security monitoring
- Docker security monitoring

### Cloud Security

Monitor cloud infrastructure including:

- EC2 instances
- Lambda functions
- Cloud storage access
- API gateway activity
- Cloud configuration compliance

## Automation

LimaCharlie's API and webhook capabilities enable:

- Automated incident response
- Security orchestration
- Custom integrations with DevOps tools
- Automated remediation workflows
- Security metrics and reporting

## Best Practices

1. **Shift left**: Integrate security early in the development process
2. **Automate security checks**: Build security into CI/CD pipelines
3. **Monitor runtime behavior**: Don't rely solely on static analysis
4. **Use infrastructure as code**: Version control and audit security configurations
5. **Implement least privilege**: Limit access and permissions by default
6. **Continuous monitoring**: Monitor applications and infrastructure continuously, not just at deployment

## Key Capabilities

- **Real-time monitoring**: Detect threats as they occur in production
- **Automated response**: Configure automated responses to security events
- **Compliance**: Maintain continuous compliance with security standards
- **Visibility**: Gain comprehensive visibility across development and production environments
- **Scalability**: Monitor security across distributed, cloud-native architectures