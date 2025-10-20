# macOS Agent Installation - Latest Versions (macOS 15 Sequoia and newer)

## macOS Sensor (macOS 15 Sequoia)

This document provides details of how to install, verify, and uninstall the LimaCharlie Endpoint Agent on macOS (versions 15 Sonoma). We also offer separate documentation for older versions.

### Installer Options

When running the installer from the command line, you can pass the following arguments:

```
-v: display build version.
-q: quiet; do not display banner.
-d <INSTALLATION_KEY>: the installation key to use to enroll, no permanent installation.
-i <INSTALLATION_KEY>: install executable as a service with deployment key.
-r: uninstall executable as a service.
-c: uninstall executable as a service and delete identity files.
-w: executable is running as a macOS service.
-h: displays the list of accepted arguments.
```

### Installation Flow

1. Download the Sensor installer file. Installer for: [Intel Mac](https://downloads.limacharlie.io/sensor/mac/64) -or- [Apple Silicon Mac](https://downloads.limacharlie.io/sensor/mac/arm64).
2. Add execute permission to the installer file via the command line

> chmod +x lc_sensor

3. Run the installer via the command line. You'll pass the argument -i and your Installation Key.

> sudo ./lc_sensor -i YOUR_INSTALLATION_KEY_GOES_HERE

You can obtain the installation key from the [Installation Keys](../../../../installation-keys.md) section of the LimaCharlie web application.

The sensor will be installed as a launchctl service. Installation will trigger the sensors enrollment with the LimaCharlie cloud

![macOS Terminal application showing LimaCharlie installation](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/1-Terminal_install.png)

4. An application (`RPHCP.app`) will be installed in the /Applications folder and will automatically launch. Note that it may take a few minutes before you see this happened after installation.

   You will be prompted to grant permissions for system extensions to be installed. Click the "**Open System Settings**" button

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/2-Endpoint_Extension_Installation_Dialog.png)

6. Ensure the toggle for "Allow in the Background" next to "Refraction Point, Inc." is toggled On.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/2.5-Login_Items_and_Extensions.png)

7. Click the "i" info icon next to "Endpoint Security Extensions", then ensure the toggle next to "RPHCP" is on.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/3-Endpoint_Extension_Enablement.png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/EndpointSecurityExtension-Enabled.png)

8. After enabling that toggle you'll need to click the "Allow" button to allow RPHCP to filter network content.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/4-Network_Filter_Enablement.png)

8. You'll be prompted to grant Full Disk Access. Check the checkbox next to the RPHCP app in System Preferences -> Privacy -> Full Disk Access

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/5-Full_Disk_Access_Permission_Dialog.png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/6-Full_Disk-Access_Enablement.png)

The installation is now complete and you should see a message indicating that the installation was successful.

![Success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/09-Success.png)

### Verifying Installation

To verify that the sensor was installed successfully, you can log into the LimaCharlie web application and see if the device has appeared in the Sensors section. Additionally, you can check the following on the device itself:

In a Terminal, run the command:

> sudo launchctl list | grep com.refractionpoint.rphcp

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Verification/Verification-installation-successful.png)

If the agent is running, this command should return records as shown above.

You can also check the /Applications folder and launch the RPHCP.app.

![Applications folder](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/10-Applications.png)

You can confirm the network filter was properly installed and enabled by going to System Settings → Network → VPN & Filters. You should expect to see "RPHCP" in the list with the status showing as Enabled.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/7-Network_Filter_Confirmation(1).png)

The application will show a message to indicate if the required permissions have been granted.

![App installed correctly](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/11-App_Installed_Correctly.png)

As described in the dialog, the RPHCP.app application must be left in the /Applications folder in order for it to continue operating properly.

#### A note on permissions

Apple has purposely made installing extensions (like the ones used by LimaCharlie) a process that requires several clicks on macOS. The net effect of this is that the first time the sensor is installed on a macOS system, permissions will need to be granted via System Preferences

Currently, the only way to automate the installation is to use an Apple-approved MDM solution. These solutions are often used by large organizations to manage their Mac fleet. If you are using such a solution, see your vendor's documentation on how to add extensions to the allow list which can be applied to your entire fleet.

We're aware this is an inconvenience and hope Apple will provide better solutions for security vendors in future.

### Uninstallation Flow

To uninstall the sensor:

1. Run the installer via the command line. You'll pass the argument -c

> sudo ./hcp_osx_x64_release_4.23.0 -c

![Uninstall progress](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/1-Uninstall_Progress.png)

2. You will be prompted for credentials to modify system extensions. Enteryour password and press OK.

![Uninstall permissions](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/2-Uninstaller_Permissions.png)

The related system extension will be removed and the `RPHCP.app` will be removed from the /Applications folder.

3. You should see a message indicating that the uninstallation was successful.

![Uninstall success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/3-Uninstall_Success.png)

Note: After uninstallation the LimaCharlie sensor along with the related extensions will be removed. macOS requires a reboot to fully unload and remove extensions.

### Install Using MDM Solutions

See our document [macOS Agent Installation with MDM Solutions](macos-agent-installation-mdm-configuration-profiles.md) for the Mobile Device Management (MDM) Configuration Profile that can be used to deploy the LimaCharlie agent to an enterprise fleet.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
