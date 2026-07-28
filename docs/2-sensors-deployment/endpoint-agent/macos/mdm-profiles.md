# macOS Agent Installation - MDM Configuration Profiles

This document describes the Mobile Device Management (MDM) Configuration Profile. Use the profile to deploy the LimaCharlie agent to a macOS fleet (versions 10.15 and newer).

## Affected Dialogs

After you deploy the configuration profile with an approved MDM server, users do not need to approve the agent installation. macOS no longer shows these three system approval dialogs:

System Extension
![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/04-System_Extension_Required.png)

Network Filter
![Network filter](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/07--Network_Filter.png)

Full Disk Access
![Full disk access](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/08-Full_Disk_Access.png)

Application Installation
![RPHCP application install](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/03-Permissions_Required.png)

## Configuration Profile Details

A sample configuration profile is available for reference: [![MobileConfig icon](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/mobileconfig-icon.png)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)

[Download LimaCharlie.mobileconfig sample configuration profile](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)

The profile includes these permissions:

- System Extension
- Full Disk Access
- Network Content Filter

## Silent Installation Preference

Put the preference file below in the /Library/Preferences folder on the endpoint before you install the agent. The preference file makes the installation silent. Use the preference file with the MDM profile.

Download the preference file: [![Preference file icon](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/preference-icon.png)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/com.refractionpoint.rphcp.client.plist.zip)

[Download com.refractionpoint.rphcp.client.plist preference file (to be placed in the /Library/Preferences folder on the endpoint)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/com.refractionpoint.rphcp.client.plist.zip)

## Installation Scripts

A sample installation script and a sample uninstallation script are available. Use them with MDM providers to install or remove LimaCharlie on many machines. Edit the installation script before you use it, because it needs your unique Installation Key.

The scripts find the machine architecture (Intel or Apple Silicon), download the correct installer, and then install or uninstall the agent. The scripts also add the Silent Installation Preference File, or remove it for an uninstallation.

[Sample Installation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-install-limacharlie.sh)

[Sample Uninstallation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-uninstall-limacharlie.sh)

## Example Jamf Pro Setup

You can use any Apple-approved or user-approved MDM provider. These instructions are for Jamf Pro.

1. Log in to Jamf Pro and go to Computers -> Configuration Profiles.
2. Add a new profile.
3. In the General section, enter a name for the profile and set Level to "Computer Level".

    ![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-1-General.png)

4. Add a Privacy Preferences Policy Control configuration and set these parameters:

    Identifier:
    com.refractionpoint.rphcp.extension

    Identifier Type:
    Bundle ID

    Code Requirement:
    anchor apple generic and identifier "com.refractionpoint.rphcp.extension" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /\* exists \*/ or certificate 1[field.1.2.840.113635.100.6.2.6] /\* exists \*/ and certificate leaf[field.1.2.840.113635.100.6.1.13] /\* exists \*/ and certificate leaf[subject.OU] = N7N82884NH)

    App or Service:
    SystemPolicyAllFiles

    Access:
    Allow

    ![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-PPPC.png)

5. Add a System Extensions configuration and set these parameters:

    Enter your display name

    System Extension Types: Allowed System Extensions

    Team Identifier: N7N82884NH

    Allowed System Extensions: com.refractionpoint.rphcp.extension

    ![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-SystemExtensions.png)

6. Add a Content Filter configuration and set these parameters:

    Enter your filter name

    Identifier: com.refractionpoint.rphcp.client

    Filter Order: Firewall

    Add a Socket Filter with these details:
    Socket Filter Bundle Identifier:
    com.refractionpoint.rphcp.client

    Socket Filter Designated Requirement
    anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /\* exists \*/ or certificate 1[field.1.2.840.113635.100.6.2.6] /\* exists \*/ and certificate leaf[field.1.2.840.113635.100.6.1.13] /\* exists \*/ and certificate leaf[subject.OU] = N7N82884NH)

    Add a Network Filter with these details:

    Network Filter Bundle Identifier:
    com.refractionpoint.rphcp.client

    Network Filter Designated Requirement:
    anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /\* exists \*/ or certificate 1[field.1.2.840.113635.100.6.2.6] /\* exists \*/ and certificate leaf[field.1.2.840.113635.100.6.1.13] /\* exists \*/ and certificate leaf[subject.OU] = N7N82884NH)

    ![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-4-ContentFilter.png)

7. Deploy the configuration profile to your devices.
