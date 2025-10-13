You can deploy the LimaCharlie Sensor for macOS using the MDM provider of your choice. Below are instructions for deploying the LimaCharlie Sensor for macOS using Microsoft Intune.

## **MDM Profile**

Set up the installation script by following these steps:

1. In the [Microsoft Intune admin center](https://intune.microsoft.com/), go to Devices → Manage Devices → Configuration.

![Screenshot of MS Intune -> Devices | Configuration](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Configurations.png)

2. Choose [Policies](https://intune.microsoft.com/?ref=AdminCenter#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/configuration), click the Create button and choose New Policy

   1. Set the Platform to be macOS

   2. Set the Profile Type to be Templates, then choose the template name “Custom”

   3. Click Create

3. Enter the custom policy details as follows:

   1. Name:  LimaCharlie

   2. Custom configuration profile name:  LimaCharlie

   3. Deployment channel: Device channel

   4. Configuration profile file: Download and use the [LimaCharlie MDM profile](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip).

Set the Assignments to include all users who need the profile installed.

![Screenshot of MS Intune -> Devices | Configuration | Details](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Configuration-details.png)

## Installation Script

Set up the installation script by following these steps:

1. In the [Microsoft Intune admin center](https://intune.microsoft.com/), go to Devices → Manage Devices → Scripts and remediations.

![Screenshot of MS Intune -> Devices | Scripts](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Scripts.png)

2. Choose [Platform scripts](https://intune.microsoft.com/?ref=AdminCenter#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/scripts), click the Add button and choose macOS

3. Set up the script with the following parameters:

Name: Install LimaCharlie

Shell script:  [Download this template shell script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-install-limacharlie.sh); be sure to edit it to include your Installation Key before uploading it in MS Intune.

Run script as signed-in user:  No

Hide script notifications on devices:  Yes

Script frequency:  Not configured

Max number of times to retry if script fails:  3

Assignments:  Set the `Included groups` to be `All Users` if you wish all users to get the application to be installed, or simply select the correct group to whom you wish to have LimaCharlie be installed for.

![Screenshot of MS Intune -> Devices | Scripts | Details](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Script-details.png)

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
