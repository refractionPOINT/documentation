# Infrastructure as Code

## Overview

LimaCharlie leverages YAML templates to define and manage the configurations for an Organization, enabling a powerful infrastructure-as-code (IaC) approach. These templates capture all the essential security settings and features of an organization, such as:

* **Enabled Add-ons**: Any additional features or modules that have been activated, from advanced detection mechanisms to specialized data analysis tools.
* **Detection & Response Rules**: The automated rules that determine how the system responds to specific threats or events, ensuring immediate and appropriate action.
* **Event & Artifact Collection**: Specifications for what data is collected, how it's processed, and how long it's retained. This can include system logs, endpoint telemetry, or forensic data from incidents.
* **File Integrity Monitoring**: Rules that detect and alert on unauthorized file changes, helping to identify potential breaches or malicious activity.
* **Output Configurations**: Settings that determine how and where data is sent, such as forwarding alerts to SIEMs, sending notifications to Slack, or exporting logs to external storage.

These YAML-based configurations allow you to capture an organization's entire security setup in a standardized format. This not only provides clarity and visibility but also enables efficient scaling. When deploying a new organization, you can simply apply the existing YAML template to instantly replicate the security environment—no need for manual reconfiguration.

The infrastructure-as-code model promotes consistency, as every organization can be configured identically with minimal effort. Additionally, YAML templates can be version-controlled, allowing you to track changes, roll back updates, and ensure auditability over time. This approach is especially beneficial in multi-tenant environments or service providers managing security across multiple clients, as it facilitates rapid, scalable deployment with confidence that security postures remain aligned across organizations.

Another advantage is the flexibility to customize templates for specific use cases. You can create a base template for common settings and extend it with organization-specific rules or modules, giving you the ability to fine-tune security without sacrificing consistency.

Overall, LimaCharlie's YAML templates enable security teams to treat organizations like modular containers, allowing rapid, repeatable deployment and easy maintenance across a large number of environments while minimizing the risks of human error.

## Example

Here's a basic config for an organization in LimaCharlie:

```yaml
version: 3
resources:
  api:
  - insight
  replicant:
  - infrastructure-service
  - integrity
  - reliable-tasking
  - responder
  - sigma
  - soteria-rules
  - logging
  - yara
integrity:
  linux-key:
    patterns:
    - /home/*/.ssh/*
    tags: []
    platforms:
    - linux
artifact:
  linux-logs:
    is_ignore_cert: false
    is_delete_after: false
    days_retention: 30
    patterns:
    - /var/log/syslog.1
    - /var/log/auth.log.1
    tags: []
    platforms:
    - linux
  windows-logs:
    is_ignore_cert: false
    is_delete_after: false
    days_retention: 30
    patterns:
    - wel://system:*
    - wel://security:*
    - wel://application:*
    tags: []
    platforms:
    - windows
```

Applying this would get an org started with some basics:

* Add-ons that enable incident response (`insight`, `reliable-tasking`, `responder`)
* Managed detection & response rulesets (`sigma`, `soteria-rules`)
* Services that add Sensor capabilities (`integrity`, `logging`, `yara`)
* Some basic configurations to monitor file integrity of `*/.ssh` on Linux and collect syslog, auth logs, and Windows event logs

## Generating IaC Configs

There are many ways to produce an IaC config for reuse across multiple deployments. One option is to use our [IaC Generator](https://iac.limacharlie.io/).

![IaC Generator](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28263%29.png)

## Applying Configs

### Methods

* Via web application in 'Templates' (requires `infrastructure-service`)
* Via REST API requests to `infrastructure-service`
* Via CLI (`limacharlie config fetch` / `limacharlie config push`)

The web application offers two main modes of syncing:

* `Apply`: Add new config and apply changes additively
* `Modify`: Edit existing config and apply changes destructively

Apply mode can be especially useful for applying partial configs from online examples and community solutions. LimaCharlie has a [GitHub repository](https://github.com/refractionPOINT/templates) with some starter config templates.

For finer-grained control of config, or updating configs as part of a CI pipeline, we recommend reading the documentation for [infrastructure service](/v2/docs/ext-infrastructure).