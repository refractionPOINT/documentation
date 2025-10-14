# macOS Agent Installation - Older Versions (macOS 10.14 and prior)

This document provides details of how to install, verify, and uninstall the LimaCharlie sensor on macOS (versions 10.14 and prior). We also offer documentation for macOS 10.15 and newer.

## macOS Sensor (macOS 10.14 and prior)

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

1. Download the [Sensor installer file](https://downloads.limacharlie.io/sensor/mac/64)

2. Add execute permission to the installer file via the command line

```bash
chmod +x hcp_osx_x64_release_4.23.0
```

3. Run the installer via the command line. You'll pass the argument -i and your Installation Key.

```bash
sudo ./hcp_osx_x64_release_4.23.0 -i YOUR_INSTALLATION_KEY_GOES_HERE
```

You can obtain the installation key from the Installation Keys section of the LimaCharlie web application.

The sensor will be installed as a launchctl service. Installation will trigger the sensors enrollment with the LimaCharlie cloud.

4. You will be prompted to grant permissions for system extensions to be installed.

5. Click the "Open System Preferences" button

6. Unlock the preference pane using the padlock in the bottom left corner, then click the Allow button next to `System software from developer "Refraction Point, Inc" was blocked from loading.`

The installation is now complete and you should see a message indicating that the installation was successful.

## Verifying Installation

To verify that the sensor was installed successfully, you can log into the LimaCharlie web application and see if the device has appeared in the Sensors section. Additionally, you can check the following on the device itself:

### Ensure the process is running

In a Terminal, run the command:

```bash
sudo launchctl list | grep com.refractionpoint.rphcp
```

If the agent is running, this command should return a record.

### Ensure the Kernel Extension is loaded

You can confirm that the kernel extension is loaded by running the command:

```bash
kextstat | grep com.refractionpoint.
```

If the extension is loaded, this command should return a record.

### A note on permissions

Apple has purposely made installing extensions (like the ones used by LimaCharlie) a process that requires several clicks on macOS. The net effect of this is that the first time the sensor is installed on a macOS system, permissions will need to be granted via System Preferences.

Currently, the only way to automate the installation is to use an Apple-approved MDM solution. These solutions are often used by large organizations to manage their Mac fleet. If you are using such a solution, see your vendor's documentation on how to add extensions to the allow list which can be applied to your entire fleet.

We're aware this is an inconvenience and hope Apple will provide better solutions for security vendors in future.

## Uninstallation Flow

To uninstall the sensor:

1. Run the installer via the command line. You'll pass the argument -c

```bash
sudo ./hcp_osx_x64_release_4.23.0 -c
```

2. You should see a message indicating that the uninstallation was successful.

---

**Note:** Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.