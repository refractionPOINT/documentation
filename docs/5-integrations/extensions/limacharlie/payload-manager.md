# Payload Manager

You can deploy [Payloads](../../../2-sensors-deployment/endpoint-agent/payloads.md) to LimaCharlie sensors for any purpose. A payload is a script, a pre-built binary, or another file.

One method to add payloads to an Organization is the payloads screen in the web app. This method is suitable for ad-hoc payloads. It does not scale past a few payloads, or to many organizations that need the same payload(s).

The payload manager lets you create and maintain payloads in your organization(s). It also creates and updates payloads automatically. You can save payload configurations and use them across many organizations with the Infrastructure as Code capabilities of LimaCharlie.

LimaCharlie syncs the payloads that you add in the payload manager one time every 24 hours for each org.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs. This structure gives you full control of security operations. It also supports multi-tenant setups for managed security providers, or for enterprises that manage many departments or clients.

Infrastructure as Code (IaC) uses code to automate the management and provisioning of IT infrastructure. With IaC, you scale, maintain, and deploy resources consistently. In LimaCharlie, IaC lets security teams deploy and manage sensors, rules, and other security infrastructure programmatically. The result is repeatable configurations and faster response times. IaC also keeps the best practices of infrastructure-as-code in cybersecurity operations.
