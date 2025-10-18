---
title: macOS Agent Installation - MDM Configuration Profiles
slug: macos-agent-installation-mdm-configuration-profiles
breadcrumb: Sensors > Endpoint Agent > Endpoint Agent Installation > macOS Agent Installation
source: https://docs.limacharlie.io/docs/macos-agent-installation-mdm-configuration-profiles
articleId: a9d9225c-a17f-4670-957d-3420449aaadd
---

* * *

macOS Agent Installation - MDM Configuration Profiles

  *  __16 Mar 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# macOS Agent Installation - MDM Configuration Profiles

  *  __Updated on 16 Mar 2025
  *  __ 2 Minutes to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

This document provides details of the Mobile Device Management (MDM) Configuration Profile that can be used to deploy the LimaCharlie agent to your enterprise fleet on macOS (versions 10.15 and newer).

## Affected Dialogs

Once the configuration profile is deployed using an approved MDM server, users will not need to provide approval to complete the agent installation. In particular, the following three system approval dialogs will no longer be presented:

System Extension  
![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/04-System_Extension_Required.png)

Network Filter  
![Network filter](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/07--Network_Filter.png)

Full Disk Access  
![Full disk access](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/08-Full_Disk_Access.png)

Application Installation  
![RPHCP application install](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/03-Permissions_Required.png)

## Configuration Profile Details

We have provided a sample configuration profile for reference: [![MobileConfig icon](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/mobileconfig-icon.png)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)  
  
  
[ Download LimaCharlie.mobileconfig sample configuration profile](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/LimaCharlie.mobileconfig.zip)

This profile includes the following permissions:

  * System Extension

  * Full Disk Access

  * Network Content Filter




## Silent Installation Preference

In addition to the MDM profile, you will also want to place the following preference file in the /Library/Preferences folder on the endpoint prior to installation. With this preference file in place the application will provide for a silent installation.

The required preference file can be downloaded here: [![Preference file icon](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/preference-icon.png)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/com.refractionpoint.rphcp.client.plist.zip)  
  
  
[ Download com.refractionpoint.rphcp.client.plist preference file (to be placed in the /Library/Preferences folder on the endpoint)](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/com.refractionpoint.rphcp.client.plist.zip)

## Installation Scripts

We have made a sample installation and uninstallation script available. You can use these with MDM providers to mass install/remove LimaCharlie. Note that the installation script should be edited prior to use as it requires your unique Installation Key to be entered.

These scripts will determine the machine architecture (Intel or Apple Silicon), download the appropriate installer, and then perform the installation or uninstallation. They also will automatically add (or remove, for uninstallations) the Silent Installation Preference File.

[Sample Installation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-install-limacharlie.sh)

[Sample Uninstallation Script](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/sample-uninstall-limacharlie.sh)

## Example Jamf Pro Setup

While any Apple / user approved MDM provider may be used, we have provided specific instructions for Jamf Pro as a matter of convenience.

  1. Log into Jamf Pro and go to Computers -> Configuration Profiles

  2. Add a new profile

  3. In the General section choose a name for the profile and set Level to "Computer Level"




![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-1-General.png)

  4. Add a Privacy Preferences Policy Control configuration and set the parameters as follows:




Identifier:  
com.refractionpoint.rphcp.extension

Identifier Type:  
Bundle ID

Code Requirement:  
anchor apple generic and identifier "com.refractionpoint.rphcp.extension" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)

App or Service:  
SystemPolicyAllFiles

Access:  
Allow

![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-PPPC.png)

  5. Add a System Extensions configuration and set the parameters as follows:




Enter your desired display name

System Extension Types: Allowed System Extensions

Team Identifier: N7N82884NH

Allowed System Extensions: com.refractionpoint.rphcp.extension

![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-2-SystemExtensions.png)

  6. Add a Content Filter configuration and set the parameters as follows:




Enter your desired filter name

Identifier: com.refractionpoint.rphcp.client

Filter Order: Firewall

Add a Socket Filter with the following details:  
Socket Filter Bundle Identifier:  
com.refractionpoint.rphcp.client

Socket Filter Designated Requirement  
anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)

Add a Network Filter with the following details:

Network Filter Bundle Identifier:  
com.refractionpoint.rphcp.client

Network Filter Designated Requirement:  
anchor apple generic and identifier "com.refractionpoint.rphcp.client" and (certificate leaf[field.1.2.840.113635.100.6.1.9] /* exists */ or certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = N7N82884NH)

![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/MDM_profiles/JamfPro-4-ContentFilter.png)

  7. Deploy the configuration profile to your devices.




Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ macOS Agent Installation via Jamf Now ](/docs/installing-macos-agents-via-jamf-now)
  * [ Enterprise-Wide Agent Deployment ](/docs/enterprise-wide-agent-deployment)
  * [ macOS Agent Installation ](/docs/macos-agent-installation)
  * [ macOS Agent Installation - Older Versions (macOS 10.14 and prior) ](/docs/macos-agent-installation-older-versions)
  * [ macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma) ](/docs/macos-agent-installation-latest-os-versions)



* * *

###### What's Next

  * [ macOS Agent Installation via Jamf Now ](/docs/installing-macos-agents-via-jamf-now) __



Table of contents

    * Affected Dialogs 
    * Configuration Profile Details 
    * Silent Installation Preference 
    * Installation Scripts 
    * Example Jamf Pro Setup 



Tags

  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ macos ](/docs/en/tags/macos)
  * [ sensors ](/docs/en/tags/sensors)


