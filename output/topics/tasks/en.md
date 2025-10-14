# Sleeper Deployment

LimaCharlie's usage-based billing enables incident responders to offer pre-deployments to their customers at almost zero cost. That is, they can deploy across an Organization's entire fleet and lay dormant in 'sleeper mode' at a cost of just $0.10 per 30 days. With agents deployed ahead of an incident, responders can offer competitive SLAs.

> Have more questions?
>
> For more details on sleeper mode deployments, feel free to contact us at answers@limacharlie.io or book a quick call with the engineering team to discuss your use case.

Sleeper and Usage billing use the following metrics:

| Connected Time | Events Processed | Events Retained |
| --- | --- | --- |
| $0.10 per 30 days | $0.67 per 100,000 events | $0.17 per 100,000 events |

Using sleeper and usage deployments is done via Sensor tagging. Applying the `lc:sleeper` Tag to a Sensor will stop LimaCharlie telemetry collection activity on the host. Within 10 minutes of the tag being applied, the sensor will enter sleeper mode and will be billed only for its "Connected Time" as outlined above. If the tag is removed, normal operations resume within 10 minutes.

Applying the `lc:usage` tag will make the sensor operate normally as usual, but its connection will not count against the normal Sensor Quota. Instead it will be billed per time spend connected and number of events process/retained as outlined above.

Using the "usage" and "sleeper" mode requires the organization in question to have billing enabled (a quota of at least 3 to be outside of the free tier).

This means a sample scenario around pre-deploying in an enterprise could look something like this:

1. Create a new Organization in LimaCharlie.
2. Set the Quota to 3 to enable billing.
3. Create a new Installation Key, and set the `lc:sleeper` tag on the key.
4. Enroll any number of EDR sensors. Charges will apply as specified above. For example, if you deploy 100 Sensors in sleeper mode, total monthly costs will be $10.
5. Whenever you need to "wake up" and use some of the EDRs, you have 2 options:

   1. Set the `lc:usage` tag on the Sensor(s) you need. Within 10 minutes, telemetry collection will resume and billed on direct usage.
   2. Set the quota to the number of Sensor(s) you need, remove the `lc:sleeper` tag from the specific Sensors, and within 10 minutes they will be online, billed according to the quota.
6. When you're done, just re-add the `lc:sleeper` tag.

Switching to sleeper mode does not change the binary on disk, however, the code running in memory does change. Whether putting an org into sleeper mode or changing versions, the binary on disk remains as-is.

The changes to sleeper mode go into effect without the need for a reboot. In sleeper mode, activities such as read other process' memory (e.g. [YARA](/v2/docs/ext-yara)) will stop.

## Related Concepts

### Organizations

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

### Tags

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.

### Sensors

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

### Installation Keys

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.