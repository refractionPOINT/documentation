# macOS Agent Installation - MDM Configuration Profiles

This document provides comprehensive details for deploying the LimaCharlie agent to macOS enterprise fleets (versions 10.15 and newer) using Mobile Device Management (MDM) Configuration Profiles.

## Affected Dialogs

Once the configuration profile is deployed using an approved MDM server, users will not need to provide approval to complete the agent installation. The following system approval dialogs will no longer be presented:

### System Extension
![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/04-System_Extension_Required.png)

### Network Filter
![Network filter](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/07--Network_Filter.png)

### Full Disk Access
![Full disk access](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/08-Full_Disk_Access.png)

### Application Installation
![RPHCP application install](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/03-Permissions_Required.png)

## Configuration Profile Details

A sample configuration profile is provided for reference:

[Download LimaCharlie.mobileconfig sample configuration profile](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)

This profile includes the following permissions:

* System Extension
* Full Disk Access
* Network Content Filter

## Silent Installation Preference

In addition to the MDM profile, place the following preference file in the `/Library/Preferences` folder on the endpoint prior to installation. With this preference file in place, the application will provide a silent installation.

[Download com.refractionpoint.rphcp.client.plist preference file](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/com.refractionpoint.rphcp.client.plist.zip)

## Installation Scripts

Sample installation and uninstallation scripts are available for use with MDM providers to mass install/remove LimaCharlie. **Note:** The installation script must be edited prior to use as it requires your unique Installation Key.

These scripts will:
- Determine the machine architecture (Intel or Apple Silicon)
- Download the appropriate installer
- Perform the installation or uninstallation
- Automatically add (or remove, for uninstallations) the Silent Installation Preference File

[Sample Installation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-install-limacharlie.sh)

[Sample Uninstallation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-uninstall-limacharlie.sh)

## MDM Provider Examples

### Jamf Pro Setup

While any Apple/user approved MDM provider may be used, specific instructions for Jamf Pro are provided below:

1. Log into Jamf Pro and go to **Computers → Configuration Profiles**

2. Add a new profile

3. In the **General** section, choose a name for the profile and set Level to "Computer Level"

![Jamf Pro General Settings](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-1-General.png)

4. Add a **Privacy Preferences Policy Control** configuration with the following parameters:

   - **Identifier:** `com.refractionpoint.rphcp.extension`
   - **Identifier Type:** Bundle ID
   - **Code Requirement:** `anchor apple generic and identifier "com.refractionpoint.rphcp.extension" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)`
   - **App or Service:** SystemPolicyAllFiles
   - **Access:** Allow

![Jamf Pro PPPC Settings](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-PPPC.png)

5. Add a **System Extensions** configuration with the following parameters:

   - Enter your desired display name
   - **System Extension Types:** Allowed System Extensions
   - **Team Identifier:** N7N82884NH
   - **Allowed System Extensions:** `com.refractionpoint.rphcp.extension`

![Jamf Pro System Extensions](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-SystemExtensions.png)

6. Add a **Content Filter** configuration with the following parameters:

   - Enter your desired filter name
   - **Identifier:** `com.refractionpoint.rphcp.client`
   - **Filter Order:** Firewall

   **Add a Socket Filter:**
   - **Socket Filter Bundle Identifier:** `com.refractionpoint.rphcp.client`
   - **Socket Filter Designated Requirement:** `anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)`

   **Add a Network Filter:**
   - **Network Filter Bundle Identifier:** `com.refractionpoint.rphcp.client`
   - **Network Filter Designated Requirement:** `anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)`

![Jamf Pro Content Filter](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-4-ContentFilter.png)

7. Deploy the configuration profile to your devices

### Microsoft Intune Setup

You can deploy the LimaCharlie Sensor for macOS using Microsoft Intune by following these instructions:

#### MDM Profile Configuration

1. In the [Microsoft Intune admin center](https://intune.microsoft.com/), go to **Devices → Manage Devices → Configuration**

![MS Intune Configurations](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Configurations.png)

2. Choose [Policies](https://intune.microsoft.com/?ref=AdminCenter#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/configuration), click **Create** and choose **New Policy**

   - Set **Platform** to macOS
   - Set **Profile Type** to Templates, then choose the template name "Custom"
   - Click **Create**

3. Enter the custom policy details:

   - **Name:** LimaCharlie
   - **Custom configuration profile name:** LimaCharlie
   - **Deployment channel:** Device channel
   - **Configuration profile file:** [Download and use the LimaCharlie MDM profile](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)

4. Set the **Assignments** to include all users who need the profile installed

![MS Intune Configuration Details](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Configuration-details.png)

#### Installation Script Configuration

1. In the [Microsoft Intune admin center](https://intune.microsoft.com/), go to **Devices → Manage Devices → Scripts and remediations**

![MS Intune Scripts](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Scripts.png)

2. Choose [Platform scripts](https://intune.microsoft.com/?ref=AdminCenter#view/Microsoft_Intune_DeviceSettings/DevicesMenu/~/scripts), click **Add** and choose macOS

3. Configure the script with the following parameters:

   - **Name:** Install LimaCharlie
   - **Shell script:** [Download this template shell script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-install-limacharlie.sh) (edit to include your Installation Key before uploading)
   - **Run script as signed-in user:** No
   - **Hide script notifications on devices:** Yes
   - **Script frequency:** Not configured
   - **Max number of times to retry if script fails:** 3
   - **Assignments:** Set the `Included groups` to `All Users` to install for all users, or select the specific group for LimaCharlie installation

![MS Intune Script Details](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Script-details.png)

## Installation Keys

Installation keys are Base64-encoded strings provided to Sensors and Adapters to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.