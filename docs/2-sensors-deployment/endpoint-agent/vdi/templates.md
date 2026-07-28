# VDI & Virtual Machine Templates

You can install the LimaCharlie Endpoint Agent in template-based environments, both VMs and VDIs.

The method is the same as the method described above. But you must stage the installation of the Endpoint Agent correctly in your templates.

The most common mistake is to install the Sensor directly in the template and then create the rest of the infrastructure from that template. The result is "cloned sensors": sensors that run with the same Sensor ID on different hosts, VMs, or containers.

If cloned sensors occur, LimaCharlie generates a [sensor\_clone](../../../8-reference/platform-events.md#sensor_clone) event and shows an error in your dashboard. You then have two choices:

1. Fix the installation process and re-deploy.
2. Run a de-duplication process with a [Detection & Response rule that de-duplicates cloned sensors](../../../3-detection-response/examples.md#de-duplicate-cloned-sensors).

To prepare sensors to run correctly from templates, create a special `hcp_vdi` (macOS and Linux) or `hcp_vdi.dat` (Windows) file in the applicable configuration directory:

- Windows: `%SYSTEMROOT%\system32\`
- macOS: `/usr/local/`
- Linux: usually `/etc/`, but it is the current working directory of the sensor process.

The content of the `hcp_vdi` file must be a string with the epoch timestamp in seconds when the sensors start to enroll. For example, if the current time is `1696876542`, a value of `1696882542` makes the sensor try to enroll 10 minutes later. You can then install the sensor without a risk that it enrolls before you create the base image.

To create this file quickly, run the LimaCharlie EDR binary (for example `lc_sensor.exe`) with the `-t` option. The option creates a `hcp_vdi.dat` file with a value of +1 day. This is usually enough time to create the base image and to submit it to a VDI platform, which often starts the image. The next day, each machine that comes from this base image starts to enroll.

Example `hcp_vdi.dat` file content:

```text
1696882542
```

If a sensor is already enrolled, the sensor ignores the `hcp_vdi` file completely.
