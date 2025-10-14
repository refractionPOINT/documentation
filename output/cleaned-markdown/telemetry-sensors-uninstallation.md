# Sensor Uninstallation

There are multiple options available to uninstall the LimaCharlie sensor, depending on the operating system and/or method of installation. macOS and Windows systems allow for easy uninstallation via sensor commands or D&R rules. Linux systems may require additional steps, as detailed below.

## macOS and Windows

When uninstalling macOS and Windows Sensors, please attempt to utilize a method similar to sensor deployment. For example, if sensors were deployed via a package manager, then the same package manager may have uninstall options as well. This will help keep software inventories up to date.

### Manual Uninstallation

#### Windows EXE

On Windows, the LimaCharlie sensor can be uninstalled on individual endpoints by running the installer EXE with the `-c` argument, which will remove the Sensor and its service entirely.

Example:

```
C:\Windows\System32\rphcp.exe -c
del C:\Windows\System32\rphcp.exe
```

#### Windows MSI

If uninstalling via the Windows MSI installer, the `/x` switch can be used to uninstall.

Example:

```
msiexec /x lc_sensor.msi /qn
```

If you run into issues where the service is still present (`sc.exe query rphcpsvc`) or the exe is still left behind (`C:\Windows\System32\rphcp.exe`), you can remove them with the following:

```
C:\Windows\System32\rphcp.exe -c       # If this throws an error about the service, it's safe to ignore
del C:\Windows\System32\rphcp.exe
```

#### macOS

Manual installation of macOS Sensors is detailed [here](/v1/docs/macos-sensor-installation-latest-os-versions#uninstallation-flow).

### Sensor Commands

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. More information on that can be found [here](/v1/docs/sensor-commands-management#uninstall).

On Windows, the command defaults to uninstalling the sensor as if installed from the direct installer exe. If an MSI was used for installation, you can add a `--msi` flag to the `uninstall` command to trigger an uninstallation that is compatible with MSI.

### SDK

To run the uninstall command against *all* Sensors, a simple loop with the SDK in Python would work:

```python
import limacharlie
lc = limacharlie.Manager()
for sensor in lc.sensors():
  sensor.task( 'uninstall' )
```

### Using a D&R Rule

As an alternative approach, you can also use a Detection & Response (D&R) rule to automatically trigger an uninstall of the LimaCharlie sensor when a sensor connects to the LimaCharlie cloud. Below is an example of the rule you can use for this purpose. This example is specific to Windows-based endpoints, but can be modified based on your needs:

```yaml
# Detect
event: SYNC
op: is windows

# Respond
- action: task
  command: uninstall --is-confirmed
- action: add tag
  tag: uninstalled
```

### Package Management Tools

For Package Management tools, and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than installing from LimaCharlie. This will help keep software inventories up to date.

## Linux

Linux Sensor uninstallation depends on how the sensor was installed. For example, if installed via a Debian package (`dpkg` file), you should uninstall via the same mechanism. If you installed via the SystemV installation method, please utilize the bottom of [this script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh#L97).

### Sensor Command

The `uninstall` command does not work for Linux systems. However, there is a chained command that can be run from the Sensor Console:

```bash
run --shell-command "service limacharlie stop; rm /bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp ; rm /etc/hcp_conf; rm /etc/hcp_hbs"
```

The above command removes LimaCharlie and associated files from the system when run remotely. Note that the above command could also be coupled with a D&R rule for automated sensor uninstallation, if necessary.

### Debian Systems

If the sensor was originally installed with the .deb file, this option is the cleanest uninstall method.

```bash
apt remove limacharlie
```