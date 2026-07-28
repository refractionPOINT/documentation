# Quickstart

LimaCharlie is infrastructure that connects sources of security data, automates actions on the data that it sees, and sends the data where you need it. There is no *correct* way to use it, because every environment is different.

Most LimaCharlie users need basic endpoint detection and response (EDR) capabilities. This guide covers these tasks:

1. Create a new [Organization](#creating-an-organization)
2. Deploy a [Sensor](#deploying-a-sensor) to the Organization
3. Add [Sigma rules](#adding-sigma-rules) to detect suspicious activity
4. Forward detections to an external destination as an [Output](#output)

You can do all of these tasks in the free tier. The free tier gives full platform functionality for a maximum of two (2) sensors. If you do not have a free account, sign up at [app.limacharlie.io](https://app.limacharlie.io).

## Creating an Organization

LimaCharlie organizations are isolated tenants in the cloud. They are equivalent to "projects". You can configure each organization for the needs of its deployment.

After you accept the initial Terms of Service, a prompt asks you to create an organization. Select a `Region` and give a globally unique `Name`.

Region Selection

The region that you select for an organization is permanent. Also consider the regulatory requirements for your data and for the data of your customers.

After LimaCharlie creates the organization, it shows the initial dashboard and the Sensor list. The list is empty and ready for the next step.

## Deploying a Sensor

On the Sensors page of your new organization, click `Add Sensor`. This opens the setup flow for new sensors. Sensors are executables that install on hosts. They connect the hosts to the LimaCharlie cloud to send telemetry, receive commands, and give other capabilities.

Sensors Overview

For a full overview of the types of sensors and their capabilities, see Sensors.

This example installs a sensor on a Windows 10 (64 bit) machine.

1. Choose the Windows sensor type.
2. Create an Installation Key. The key registers the executable to communicate securely with your organization.
3. Choose the `64 bit (.exe)` installer.
4. Obey the on-screen instructions to run the installer correctly.
5. See the immediate feedback when the sensor registers with the cloud.

Potential Issues

Sensors are executables that communicate with the cloud. Antivirus software and network layers can interfere with the installation. If you get an issue, see troubleshooting.

A Windows sensor that is connected to the cloud gives you much visibility into the endpoint. When you open the new sensor in the web app, you get views such as:

- `Timeline`: the viewer for the telemetry events that LimaCharlie collects from the endpoint
- `Processes`: the list of processes that run on the endpoint, their level of network activity, and commands to control processes (i.e. kill / pause / resume process, or view modules)
- `File System`: an explorer for the file system of the endpoint, in the browser
- `Console`: a safe shell-like environment to send commands
- `Live Feed`: a live view of all the events of the sensor

Telemetry now comes in through the cloud. The next step adds rules to detect possible malicious activity.

## Adding Sigma Rules

It takes much work to write security rules and automations from the start. LimaCharlie maintains a `sigma` add-on to give an open baseline of coverage. You can enable the add-on for free. LimaCharlie keeps it up to date with the [openly maintained threat signatures](https://github.com/SigmaHQ/sigma).

When you enable the Sigma add-on, LimaCharlie applies rules to your organization automatically. These rules match the threat signatures, and they make Detections on the endpoint telemetry that comes in.

Writing Detection and Response rules

This guide does not explain how to write your own rules. After you finish this guide, read [Detection & Response](../3-detection-response/tutorials/writing-testing-rules.md).

## Output

The security data from your sensors is yours, and you can do what you want with it. This example sends detections to an [Amazon S3 bucket](https://aws.amazon.com/s3/) for longer storage of detections.

On the Outputs page of your organization, click `Add Output`. This opens the setup flow for new outputs.

1. Choose the Detections stream.
2. Choose the Amazon S3 destination.
3. Configure the Output. Make sure that it connects securely to the correct bucket:
   - Output Name
   - Bucket Name
   - Key ID
   - Secret Key
   - Region
4. Optionally, look at samples of the data in the detection stream. Samples are available only if there are recent detections.

With this output in place, you can keep your detections for more than the 1 year that LimaCharlie retains them. You can also stage them for any tool that can pull from S3.

---

## See Also

- [Core Concepts](core-concepts.md)
- [Installation Keys](../2-sensors-deployment/installation-keys.md)
- [Your First Detection Rule](../3-detection-response/index.md)
