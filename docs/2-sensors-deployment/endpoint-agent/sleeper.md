# Sleeper Deployment

The usage-based billing of LimaCharlie lets incident responders offer pre-deployments to their customers at almost no cost. Responders can deploy across the full fleet of an Organization. The sensors stay dormant in 'sleeper mode' at a cost of $0.10 per 30 days. Agents that are deployed before an incident let responders offer competitive SLAs.

> More questions?
>
> For more details about sleeper mode deployments, contact LimaCharlie at [answers@limacharlie.io](mailto:answers@limacharlie.io). You can also book a call with the engineering team to discuss your use case.

Sleeper billing uses these metrics:

| Connected Time | Events Processed | Events Retained |
| --- | --- | --- |
| $0.10 per 30 days | $0.67 per 100,000 events | $0.17 per 100,000 events |

You control sleeper deployments with Sensor tags. The `lc:sleeper` Tag on a Sensor stops the collection of LimaCharlie telemetry on the host. The sensor enters sleeper mode in 10 minutes or less after you apply the tag. LimaCharlie then bills only the "Connected Time" shown above. If you remove the tag, normal operation returns in 10 minutes or less.

Sleeper mode needs the organization to have billing enabled. The quota must be at least 3 to be outside the free tier.

An example of a pre-deployment in an enterprise can be:

1. Create a new Organization in LimaCharlie.
2. Set the Quota to 3 to enable billing.
3. Create a new Installation Key, and set the `lc:sleeper` tag on the key.
4. Enroll any number of EDR sensors. The charges above apply. For example, 100 Sensors in sleeper mode cost $10 each month.
5. Set the Quota to the number of Sensors that you need to "wake up". For example, to wake up 5 sensors, set the quota to at least 5. Remove the `lc:sleeper` tag from those Sensors. The Sensors come online in 10 minutes or less, and LimaCharlie bills them against the quota.
6. Add the `lc:sleeper` tag again when you finish, then lower the Quota.

A change to sleeper mode does not change the binary on disk, but the code in memory does change. The binary on disk stays the same when you put an org into sleeper mode and when you change versions.

The changes to sleeper mode take effect without a reboot. In sleeper mode, operations that read the memory of other processes stop. A [YARA](../../5-integrations/extensions/third-party/yara.md) scan is an example of such an operation.
