# Security Service Providers (MSSP, MSP, MDR)

The LimaCharlie Agentic SecOps Workspace (ASW) is a single platform for cybersecurity operations.

The ASW supplies cybersecurity capabilities and infrastructure through a public cloud model. The model is on-demand, pay-per-use, and API-first. For the cybersecurity industry, this change is comparable to the effect of the public cloud on IT.

Managed security services providers (MSSPs), managed detection and response (MDR) firms, and digital forensics and incident response (DFIR) teams use the Agentic SecOps Workspace. It improves their security operations and helps them to compete. With the ASW, a service provider can deliver security services at scale and control costs. The provider can also consolidate and customize security tools, and take on new clients with confidence.

The delivery model of the ASW is similar to a public cloud. This model lets a service provider integrate the ASW into its operations one step at a time and with low risk. With pay-as-you-go pricing, you pay only for the capabilities that you need, and only while you use them. There are no long-term contracts, no complex licensing, no capacity planning, no price modeling, and no termination fees.

## Implementation strategies for quick wins

The Agentic SecOps Workspace has many capabilities and is flexible and customizable. MSSP users report that some strategies are good start points with the platform. This section describes three ways that the ASW helps a service provider to improve security operations and grow its business immediately:

### Gain greater visibility into client environments

The ASW gives a service provider more visibility into client environments. It also brings telemetry data under a single plane for one view. This is one of the first benefits for a service provider that uses the ASW. The following paragraphs give an outline:

**Decide what telemetry data you need to support security operations.** You have many options. The ASW has two primary sources of telemetry:

The first source is the endpoint detection and response (EDR) sensors of the platform. You can deploy these sensors on Windows, Mac, and Linux endpoints, with the same features on each operating system. The sensors capture system events and other telemetry data. Browser-based sensors are also available for Chrome and Edge. The sensors stream telemetry data and artifacts into the ASW in real time, and you can also use them to do response actions on endpoints. You can also import event data from third-party EDR tools such as VMWare Carbon Black, CrowdStrike, and Microsoft Defender.

The second source is log data. Adapters or a webhook bring this data into the ASW. The supported log data sources include O365, 1Password, AWS CloudTrail, Google Cloud Platform (GCP), and Slack Audit logs. There are more sources than this text can list. For the full list, see the ASW documentation.

**Configure client organizations to provide the required visibility.** In the ASW web interface, a few clicks set up the necessary installation keys. A REST API and a command-line interface (CLI) give more advanced control of the configuration. After setup, the ASW stores the configuration of each client organization as YAML files. The configuration includes the telemetry that you bring into the Agentic SecOps Workspace. The multitenancy and organization management features of the ASW change the configuration of many organizations at the same time. For a more detailed example, see the demo MSSP setup.

**Bring your data under a single plane.** The ASW normalizes all telemetry data to a common JSON format. You explore the data through one interface. Many service providers no longer need to use separate web interfaces or different data formats to see and act on their telemetry data.

**Operationalize your telemetry data.** Visibility into client environments is an essential first step, but the Agentic SecOps Workspace can do more. The detection and response engine of the ASW acts on each event that enters the platform. You can apply detection and response (D&R) logic to telemetry data. Write your own custom detections, use curated rulesets such as Sigma, Soteria, or SOC Prime rules, or use both methods.

You cannot protect what you cannot see. With the ASW, you get full visibility into a client environment. You see that telemetry in one interface and one data format. You act on the telemetry data with the detection, automation, and response engine.

### Implement scalable SecOps and simplified client management

The Agentic SecOps Workspace is multitenant by design. It has fine-grained role-based access control (RBAC). It also supports an Infrastructure-as-Code (IaC) approach to configuration management. These features let a service provider do cybersecurity operations at scale.

**Separate client environments intelligently.** The multitenancy of the ASW puts a logical boundary between the data of each client organization. You still see and manage all organizations from one platform. Multitenancy helps you keep client data separate and obey regional regulations such as data residency rules.

**Manage access and permissions more effectively.** RBAC lets you give each user the access to organizations and the permissions that the user needs. You can give permissions to one user for each organization. For more efficient management of access, use Organization Groups. An Organization Group is a set of client organizations, permissions, and users.

An Organization Group gives the same permissions and the same access to each user that you add to the group. Most Organization Groups are set up by job function. For example, create one Organization Group for security engineers. Its members can edit the configuration for telemetry ingestion in all of your client organizations. Create a second Organization Group for non-technical roles with read-only access, or with access to general information about the organization.

**Build SecOps workflows that scale.** The Agentic SecOps Workspace lets a service provider use an infrastructure-as-code approach to security operations. You store and manage the security configuration of each client organization as YAML files. The configuration includes D&R rules, data forwarding, and output settings.

To create a new organization quickly, clone the configuration of an existing organization or use a configuration template. Keep one global set of configuration settings for all client organizations. Add a configuration file for each client when it is necessary. To change many client organizations, edit the global configuration file with the CLI or the web app. Then push the change to all of your organizations at scale.

The Agentic SecOps Workspace helps a service provider use a scalable approach to cybersecurity operations. For a more detailed example of these ASW concepts, watch Setting Up an MSSP with LimaCharlie.

### Improve incident response times and offer unbeatable service-level agreements

The Agentic SecOps Workspace is valuable for a service provider that does incident response (IR) work. The primary capabilities for IR teams are as follows:

**Begin IR engagements without delay.** The Agentic SecOps Workspace is on-demand. You do not need to speak to a vendor sales representative or change a contract before you start an IR engagement. With the ASW, log in to your account, use a credit card or increase your sensor quota, and start.

You can also configure tenants before an IR engagement. Set up your IR configuration in the ASW with custom D&R rulesets, curated rulesets, memory dumps, YARA scans, and other capabilities. Then export the configuration files for your IR tenant. Reuse the files at the start of each new IR engagement.

**Take the fight to the adversary.** During an IR engagement with an active attacker, the Agentic SecOps Workspace gives you a response capability on the endpoints of your client.

Deploy ASW sensors in bulk with an enterprise deployment tool. Then use those sensors to collect event data in real time. You can also run shell commands and executables on endpoints, deploy security tools and remediation packages at scale, or isolate compromised machines from the network. These actions have little effect on the operations and the mission-critical IT infrastructure of the client.

**Use security intelligence as soon as you have it.** The ASW uses an IaC approach. In an emergency, you do not depend on a vendor to update a tool or to publish an indicator of compromise (IoC). For example, a 0-day compromise occurs, and you get early access to an IoC through an information-sharing network or a colleague. Copy the IoC data from a Slack message into a new ASW D&R rule. Update the configuration file, and push the change to the environment of your client. Service providers that depend on a vendor must wait for that vendor to act.

**Build a true rapid-response capability.** Deploy LimaCharlie sensors to client environments in "sleeper" mode before an incident. In this mode, the settings for telemetry collection are at a minimum, and the cost is a few cents each month. If an incident occurs, the sensors are already on the endpoints. Turn the sensors on for an immediate response. Service provider partners that use this method offer service-level agreements of as little as 20 minutes. This is a considerable advantage when they sell to new MDR or MSSP clients.

IR work has high stakes and high pressure. The slow sales processes and the technical limits of legacy cybersecurity vendors often make the work more difficult. The ASW lets an incident responder act quickly and independently during an incident. It also lets a cybersecurity service provider improve its response capabilities and offer attractive service-level agreements to prospective clients.
