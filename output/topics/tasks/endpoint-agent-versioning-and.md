# Endpoint Agent Versioning and Upgrades

## Endpoint Agent Versioning and Upgrades

LimaCharlie frequently releases new versions of the endpoint agent (typically every few weeks), giving you full control over which version runs in your Organization. Sensors are not updated by default, allowing you to manage versioning and deployment as needed.

### Endpoint Agent Components

The LimaCharlie endpoint agent consists of two main components, each versioned independently:

1. **On-disk agent**: Implements core identity, cryptography, and transport mechanisms. This component rarely requires updates and typically remains static.
2. **Over-the-air core**: The main component that receives frequent updates and delivers advanced functionality. It can be easily updated via the LimaCharlie cloud.

When updates occur, they impact the over-the-air component, as it's the easiest to modify, with the update size generally being around 3-5 MB.

### Version Labels

LimaCharlie provides three version labels to simplify version management:

1. **Latest**: The most recent release with new fixes and features.
2. **Stable**: A less frequently updated version, ideal for maintaining slower update cadences.
3. **Experimental**: The beta version of the next "Latest" release.

You can upgrade to any of these versions for your organization by using the LimaCharlie web interface or the [API](https://api.limacharlie.io/static/swagger/#/Modules/upgradeOrg).

### Managing Versioning for Sensors

To manage the versioning of sensors, you can leverage LimaCharlie's **System** Tags:

* `lc:latest`: Tags the Sensor to receive the most recent version.
  + This tag is primarily intended for testing `latest` sensor version against a small set of representative sensors before org-wide upgrades to `latest`.
* `lc:stable`: Tags the sensor to receive a stable version.
* `lc:experimental`: Tags the sensor to receive the experimental version.

These tags can be applied to individual sensors to alter version behavior, and updates take effect within 10 minutes. This method also enables staging deployments to test updates on a small group of sensors before organization-wide rollouts.

### Updating Endpoint Agents

#### Best Practices

When deploying new sensor versions, follow a controlled testing approach by first applying the `lc:latest` tag to a small subset of representative systems across different operating systems and workloads. Monitor these test systems for a period of time, evaluating stability, performance, and telemetry quality. If testing is successful, update the organization-level sensor version and remove the `lc:latest` tag from test systems, while maintaining a rollback plan and monitoring system health during the deployment. Note that the `lc:latest` sensor tag should primarily be used for upgrade testing purposes, as it automatically updates sensors to new versions as they are released.

#### Manual Update

You can manually trigger an update for all endpoint agents in your organization by simply clicking a button in the web interface. This action updates the over-the-air component of the sensors within 20 minutes, with no need to re-download installers, as the installer remains unchanged.

#### Auto-Update

To automate updates, apply the `lc:stable` tag to your sensors. This will ensure that sensors automatically update to the latest stable version upon release.

#### Staged Deployment

For testing new versions, tag specific sensors with `lc:latest` to run the latest version without affecting the rest of your organization. This allows you to test new releases on selected hosts before proceeding with a full rollout.

## Glossary

**Endpoint Agents** are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

**Organization**: In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

**Tags** in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.

**Sensors**: Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.