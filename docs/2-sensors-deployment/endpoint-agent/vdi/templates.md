# VDI & Virtual Machine Templates

The LimaCharlie Endpoint Agent can be installed in template-based environments whether they're VMs or VDIs.

The methodology is the same as described above, but you need to be careful to stage the Endpoint Agent install properly in your templates.

The most common mistake is to install the Sensor directly in the template, and then instantiate the rest of the infrastructure from this template. This will result in "cloned sensors", sensors running using the same Sensor ID on different hosts/VMs/Containers.

If these occur, a [sensor\_clone](../../../8-reference/platform-events.md#sensorclone) event will be generated as well as an error in your dashboard. If this happens you have two choices:

1. Fix the installation process and re-deploy.
2. Run a de-duplication process with a Detection & Response rule [like this](../../../3-detection-response/examples.md#deduplicate-cloned-sensors).

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
