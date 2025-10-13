To install sensors en masse, you can simply navigate to the `Installation Keys` section under **Sensors**, grab the Sensor download package and installation keys. You can then use a `cURL` command with a download link and Installation Key, or use any kind of enterprise deployment tool to install en masse.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/installation.png)

Documentation on installing sensors can be found [here](/v2/docs/endpoint-agent-installation). Of course, mass deployments can be done using RMM, SCCM, MDM, and other tools.

We have provided [sample MDM profiles](/v2/docs/macos-agent-installation-mdm-configuration-profiles) for mass deployments on macOS.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
