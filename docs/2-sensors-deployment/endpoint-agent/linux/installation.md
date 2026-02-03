# Linux Agent Installation

The LimaCharlie Linux Sensor interfaces with the kernel to acquire deep visibility into the host's activity while taking measures to preserve the host's performance. We make full use of eBPF, which **requires Linux 4.4 or above**.

The Sensor current supports all Linux distributions (including ARM and MIPS).

**Linux Distribution Support**

Our Linux Sensor fully utilizes eBPF, which requires at least Linux 4.4 or above. Use the command `uname -r` to check your kernel version to determine support.

## Installation Instructions

### System Requirements

All versions of Debian and CentOS starting around Debian 5 should be supported. Due to the high diversity of the ecosystem it's also likely to be working on other distributions. If you need a specific platform, contact us.

### Deb Package

If you are deploying on a Debian Linux system, we recommend using the `.deb` package. You can find a link to the Debian package for various architectures at [Downloading the Agent](../../index.md#downloading-the-agents).

The deb package will install the LimaCharlie sensor using a `systemd` service, or if unavailable a `system V` service.

The Installation Key is required by the installer via the `debconf` configuration mechanism. By default, installing the package interactively will request the installation key via a local command/GUI interface. To perform large scale installations, we recommend setting the installation key programmatically.

**Installing interactively:**

```python
sudo dpkg -i limacharlie.deb
```

or

```python
sudo apt install ./limacharlie.deb
```

**Uninstalling interactively:**

```bash
sudo dpkg -r limacharlie
```

or

```bash
sudo apt remove limacharlie
```

**Installing and setting the installation key programmatically with dpkg:**

```powershell
echo "limacharlie limacharlie/installation_key string INSTALLATION_KEY_HERE" | sudo debconf-set-selections && sudo dpkg -i limacharlie.deb
```

**Installing and setting the installation key programmatically with apt:**

```powershell
echo "limacharlie limacharlie/installation_key string INSTALLATION_KEY_HERE" | sudo debconf-set-selections && sudo apt install ./limacharlie.deb -y
```

Debian packages are offered for the various architectures the Linux sensor supports, like:

* **x64**: <https://downloads.limacharlie.io/sensor/linux/deb64>
* **arm64**: <https://downloads.limacharlie.io/sensor/linux/debarm64>

### Custom Installation

For non-Debian systems, download the installer using the following command:

```python
wget https://downloads.limacharlie.io/sensor/linux/64 -O /tmp/lc_sensor
```

> Other Linux Versions
>
> If installing on an ARM64 or Alpine64 system, replace the URL in the command above with the respective URL from the installation wizard within LimaCharlie

Executing the installer via the command line, pass the `-d INSTALLATION_KEY` argument where `INSTALLATION_KEY` is the key mentioned above.

Because Linux supports a plethora of service management frameworks, by default the LC sensor does not install itself onto the system. Rather it assumes the "current working directory" is the installation directory and immediately begins enrollment from there.

This means you can wrap the executable using the specific service management technology used within your Organization by simply specifying the location of the installer, the `-d INSTALLATION_KEY` parameter and making sure the current working directory is the directory where you want the few sensor-related files written to disk to reside.

A common methodology for Linux is to use `init.d`, if this is sufficient for your needs, see this [sample install script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh).
You can invoke it like this:

```bash
sudo chmod +x ./lc_linux_installer.sh
sudo ./lc_linux_installer.sh <PATH_TO_LC_SENSOR> <YOUR_INSTALLATION_KEY>
```

You may also pass the value `-` instead of the `INSTALLATION_KEY` like: `-d -`. This will make the installer look for the installation key in an alternate place in the following order:

* Environment variable `LC_INSTALLATION_KEY`
* Text file in current working directory: `lc_installation_key.txt`

### Disabling Netlink

By default, the Linux sensor makes use of Netlink if available. In some rare configurations this auto-detection may be unwanted and Netlink usage can be disabled by setting the environment variable `DISABLE_NETLINK` to any value on the sensor process.

## Uninstalling the Agent

For additional agent uninstall options, see [Endpoint Agent Uninstallation](../uninstallation.md)

Linux agent uninstallation depends on how the sensor was installed. For example, if installed via a Debian package (`dpkg` file), you should uninstall via the same mechanism. If you installed via the SystemV installation method, please utilize the bottom of [this script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh#L97).

### Sensor Command

The `uninstall` command does not work for Linux systems. However, there is a chained command that can be run from the Sensor Console:

```powershell
 run --shell-command "service limacharlie stop; rm /bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp ; rm /etc/hcp_conf; rm /etc/hcp_hbs"
```

The above command removes LimaCharlie and associated files from the system when run remotely. Note that the above command could also be coupled with a rule for automated sensor uninstallation, if necessary.

### Debian Systems

If the sensor was originally installed with the .deb file, this option is the cleanest uninstall method.

```bash
apt remove limacharlie
```
