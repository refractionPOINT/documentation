Prior to rolling out a new Sensor version, we recommend testing to ensure everything works as intended within your environment. While we test Sensors before releasing them, we cannot predict every niche use case. We also recommend testing on `dev` or `test` systems prior to deployment in production, again, to eliminate any concerns of resource utilization or Sensor operations.

Sensor version testing is done via LimaCharlie's tagging functionality.

When you tag a Sensor with `lc:latest`, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the latest version of the sensor will be used instead. You can apply this tag to a handful of systems to test-deploy the latest version.

Alternatively, you can tag a sensor with `lc:stable`. Similarly, the sensor version currently assigned to the Organization will be ignored for that specific sensor, and the stable version of the sensor will be used instead.

You can tag a Sensor by opening the sensors list, selecting a sensor you would like to test, and navigating to the `tags` field on the sensor `Overview`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(314).png)

Simply type `lc:stable` and click `Update Tags`.

Note: It can take up to 10 minutes to update the sensor to the tagged version.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
