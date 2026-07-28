# macOS Agent Installation - Older Versions (macOS 10.14 and prior)

This document explains how to install, check, and uninstall the LimaCharlie sensor on macOS (version 10.14 and earlier). There is also [documentation for macOS 10.15 and newer](installation.md).

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

1. Download the [Sensor installer file](https://downloads.limacharlie.io/sensor/mac/64)

2. Add execute permission to the installer file from the command line.

    > chmod +x hcp\_osx\_x64\_release\_4.23.0

3. Run the installer from the command line. Pass the -i argument and your Installation Key.

    > sudo ./hcp\_osx\_x64\_release\_4.23.0 -i YOUR\_INSTALLATION\_KEY\_GOES\_HERE

    ![Basic installation](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/01-Basic_installation.png)

    Get the installation key from the Installation Keys section of the LimaCharlie web app. [More information about installation keys](../../installation-keys.md).

    The installer installs the sensor as a launchctl service. The installation starts the enrollment of the sensor with the LimaCharlie cloud.

    ![Installation success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Installation/02-Installation_success.png)

4. Answer the prompt that asks for permission to install system extensions.

    ![Permissions required](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/03_Older_Systems-System_Extension_Notice.png)

5. Click the "Open System Preferences" button.

6. Unlock the preference pane with the padlock in the bottom left corner.

7. Click the Allow button next to `System software from developer "Refraction Point, Inc" was blocked from loading.`

    ![Unlocked](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/04-Older_Systems-System_Software_Approval.png)

The installation is now complete. A message shows that the installation was successful.

## Verifying Installation

To check that the installation was successful, log in to the LimaCharlie web app and look for the device in the Sensors section. You can also do these checks on the device:

### Ensure the process is running

In a Terminal, run the command:

> sudo launchctl list | grep com.refractionpoint.rphcp

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/Installed_correctly.png)

If the sensor runs, this command returns a record as shown above.

### Ensure the Kernel Extension is loaded

To confirm that the kernel extension is loaded, run the command:

> kextstat | grep com.refractionpoint.

![Successful installation verification](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/verifying-extension.png)

If the extension is loaded, this command returns a record as shown above.

### A note on permissions

Apple deliberately makes the installation of extensions on macOS a process that needs several clicks. LimaCharlie uses such extensions. Thus, the first time that you install the sensor on a macOS system, you must grant permissions in System Preferences.

At present, the only way to automate the installation is an MDM solution that Apple approves. Large organizations often use these solutions to manage their macOS computers. If you use such a solution, see the documentation of your vendor. It explains how to add extensions to an allow list that applies to all your computers.

LimaCharlie knows that this is an inconvenience and hopes that Apple gives better solutions to security vendors in the future.

## Uninstallation Flow

To uninstall the sensor:

1. Run the installer from the command line. Pass the -c argument.

    > sudo ./hcp\_osx\_x64\_release\_4.23.0 -c

    ![Uninstall progress](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/macOS_10.14/Installed_correctly.png)

2. Look for the message that shows that the uninstallation was successful.

    ![Uninstall success](https://storage.googleapis.com/limacharlie-io/doc/sensor-installation/macOS/images/Uninstallation/3-Uninstall_Success.png)
