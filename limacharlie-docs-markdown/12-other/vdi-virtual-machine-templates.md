# VDI & Virtual Machine Templates
The LimaCharlie Endpoint Agent can be installed in template-based environments whether they're VMs or VDIs.

The methodology is the same as described above, but you need to be careful to stage the Endpoint Agent install properly in your templates.

The most common mistake is to install the Sensor directly in the template, and then instantiate the rest of the infrastructure from this template. This will result in "cloned sensors", sensors running using the same Sensor ID on different hosts/VMs/Containers.

If these occur, a [sensor\_clone](/v2/docs/reference-platform-events#sensorclone) event will be generated as well as an error in your dashboard. If this happens you have two choices:

1. Fix the installation process and re-deploy.
2. Run a de-duplication process with a Detection & Response rule [like this](/v2/docs/detection-and-response-examples#deduplicate-cloned-sensors).

Preparing sensors to run properly from templates can be done by creating a special `hcp_vdi` (macOS and Linux) or `hcp_vdi.dat` (Windows) file in the relevant configuration directory:

* Windows: `%SYSTEMROOT%\system32\`
* macOS: `/usr/local/`
* Linux: usually `/etc/` but fundamentally the current working directory of the sensor execution.

The contents of the `hcp_vdi` file should be a string representation of the second-based epoch timestamp when you want the sensors to begin enrolling. For example if the current time is `1696876542`, setting a value of `1696882542` will mean the sensor will only attempt to enroll in 10 minutes in the future. This allows you to install the sensor without risking it enrolling right away before the base image is created.

A shortcut for creating this file is to invoke the LimaCharlie EDR binary (like `lc_sensor.exe`) with the `-t` option, which will create a `hcp_vdi.dat` file with a value +1 day. This is usually plenty of time to finish the creation of the base image, submit it to a VDI platform (which often boots up the image) etc. The next day, any machine generated from this base image will start enrolling.

Example `hcp_vdi.dat` file content:

```
1696882542
```

Note that if a sensor is already enrolled, the presence of the `hcp_vdi` file will be completely ignored.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

Endpoint Detection & Response

---

## Related articles

* [Endpoint Agent Installation](/docs/endpoint-agent-installation)
* [Windows Agent Installation](/docs/windows-agent-installation)
* [Building a custom MSI installer for Windows](/docs/building-a-custom-msi-installer-for-windows)

---

### What's Next

* [Windows Agent Installation](/docs/windows-agent-installation)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)