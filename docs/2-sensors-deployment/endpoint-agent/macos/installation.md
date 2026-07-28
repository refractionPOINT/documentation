# macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma)

This document explains how to install, check, and uninstall the LimaCharlie Endpoint Agent on macOS (version 10.15 Catalina through macOS 14 Sonoma). There is also documentation for [macOS 10.14 and prior](installation-older.md), and [macOS 10.15 and newer](sequoia.md).

## Installer Options

When you run the installer from the command line, you can pass these arguments:

```text
-v: verbose logging output.
-V: display the sensor build version.
-d <INSTALLATION_KEY>: the installation key to use to enroll, no permanent installation.
-i <INSTALLATION_KEY>: install executable as a service with deployment key.
-r: uninstall executable as a service.
-c: uninstall executable as a service and delete identity files.
-H: verify sensor health and write a diagnostic report.
-w: executable is running as a macOS service.
-h: displays the list of accepted arguments.
```

For the complete list of options, environment variables, and local files, see the [Agent CLI & Environment Reference](../cli-reference.md).

## Installation Flow

1. Download the Sensor installer file. Installer for: [Intel Mac](https://downloads.limacharlie.io/sensor/mac/64) -or- [Apple Silicon Mac](https://downloads.limacharlie.io/sensor/mac/arm64).

2. Add execute permission to the installer file from the command line.

    > chmod +x lc\_sensor

3. Run the installer from the command line. Pass the -i argument and your Installation Key.

    > sudo ./lc\_sensor -i YOUR\_INSTALLATION\_KEY\_GOES\_HERE

    ![Basic installation](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/01-Basic_installation.png)

    Get the installation key from the [Installation Keys](../../installation-keys.md) section of the LimaCharlie web app.

    The installer installs the sensor as a launchctl service. The installation starts the enrollment of the sensor with the LimaCharlie cloud.

    ![Installation success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/02-Installation_success.png)

4. Answer the prompt that asks for permission to install system extensions. The installer puts an application (`RPHCP.app`) in the /Applications folder and starts it.

    ![Permissions required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/03-Permissions_Required.png)

5. Click the "Open System Preferences" button.

    ![System Extensions Required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/04-System_Extension_Required.png)

6. Unlock the preference pane with the padlock in the bottom left corner.

7. Click the Allow button next to `System software from application "RPHCP" was blocked from loading.`

    ![Unlocked](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/06-Allow_System_Software_Unlocked.png)

8. Click the Allow button when the prompt asks you to let the application Filter Network Content.

    ![Network filter](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/07--Network_Filter.png)

9. Select the checkbox next to the RPHCP app in System Preferences -> Privacy -> Full Disk Access when the prompt asks you to grant Full Disk Access.

    ![Full disk access](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/08-Full_Disk_Access.png)

The installation is now complete. A message shows that the installation was successful.

![Success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/09-Success.png)

## Verifying Installation

To check that the installation was successful, log in to the LimaCharlie web app and look for the device in the Sensors section. You can also do these checks on the device:

In a Terminal, run the command:

> sudo launchctl list | grep com.refractionpoint.rphcp

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Verification/Verification-installation-successful.png)

If the sensor runs, this command returns records as shown above.

You can also open the /Applications folder and start the RPHCP.app.

![Applications folder](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/10-Applications.png)

The application shows a message that tells you if the necessary permissions are granted.

![App installed correctly](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/11-App_Installed_Correctly.png)

Keep the RPHCP.app application in the /Applications folder, as the dialog says. If you move it, the application does not continue to operate correctly.

### A note on permissions

Apple deliberately makes the installation of extensions on macOS a process that needs several clicks. LimaCharlie uses such extensions. Thus, the first time that you install the sensor on a macOS system, you must grant permissions in System Preferences.

At present, the only way to automate the installation is an MDM solution that Apple approves. Large organizations often use these solutions to manage their macOS computers. If you use such a solution, see the documentation of your vendor. It explains how to add extensions to an allow list that applies to all your computers.

LimaCharlie knows that this is an inconvenience and hopes that Apple gives better solutions to security vendors in the future.

## Uninstallation Flow

To uninstall the sensor:

1. Run the installer from the command line. Pass the -c argument.

    > sudo ./hcp\_osx\_x64\_release\_4.23.0 -c

    ![Uninstall progress](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/1-Uninstall_Progress.png)

2. Enter your password at the prompt for credentials to change system extensions. Then press OK.

    ![Uninstall permissions](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/2-Uninstaller_Permissions.png)

    The uninstaller removes the related system extension. It also removes the `RPHCP.app` from the /Applications folder.

3. Look for the message that shows that the uninstallation was successful.

    ![Uninstall success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/3-Uninstall_Success.png)

## Install Using MDM Solutions

For the Mobile Device Management (MDM) Configuration Profile that deploys the LimaCharlie agent to an enterprise fleet, see [macOS Agent Installation with MDM Solutions](mdm-profiles.md).
