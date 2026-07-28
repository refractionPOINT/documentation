# Linux Agent Installation

The LimaCharlie Linux Sensor runs on every mainstream Linux distribution and architecture (x86_64, i386, ARM64, Alpine/musl). LimaCharlie ships it as one binary. The binary adapts at run time to the kernel features that the host supplies, so there is no separate build or installer for each mode. On modern kernels, the sensor uses eBPF for in-kernel telemetry. On older kernels, it falls back to lighter mechanisms.

## Linux Distribution Support

LimaCharlie tests the sensor against current Debian, Ubuntu, CentOS/RHEL/Rocky/Alma, Amazon Linux, and Alpine releases on x86_64 and ARM64. Linux distributions differ, but the sensor usually runs on other distributions without changes. To validate a specific platform, contact LimaCharlie.

### Kernel Feature Tiers

The sensor picks the best acquisition mode that the host kernel supports. If newer features are not available, the sensor uses a lower mode. All tiers run **the same binary**. The sensor makes the selection at startup.

| Tier | Minimum kernel | Acquisition path | What you get |
|------|----------------|------------------|--------------|
| User-mode only | any (incl. 2.4 / 2.6 era) | `/proc` polling | Inventory of running processes, host metadata, live response, file integrity, USB monitoring, YARA scans, network isolation, and all detection-and-response features that work from user space. **No real-time process / file / network / DNS kernel events.** |
| User-mode + netlink connector | 2.6.15 | `/proc` polling + netlink `CN_PROC` connector | Adds real-time process create / exit notifications from the kernel. The sensor still reads the process command line and executable path from `/proc` after the event, so a process with a very short life can be missed. |
| User-mode + eBPF (default when available) | 5.7+ recommended | eBPF programs (CO-RE / BTF) attached for processes, files, network, DNS | Full in-kernel telemetry: process exec with reliable cmdline capture, file I/O, TCP / UDP connections, and DNS queries. The sensor collects these synchronously and attributes them to the task that caused them. Modern supported systems use this mode. |

The sensor does **not** need eBPF, kernel headers, or `bpftool` on the target host. The eBPF programs are pre-compiled into the binary. libbpf loads them with BTF when the kernel exposes it (`/sys/kernel/btf/vmlinux`). On kernels without BTF / CO-RE, the sensor stays in the netlink or user-mode tier.

Use `uname -r` to check the host kernel version. If the version is below 5.4, the sensor runs in the netlink tier (2.6.15+) or in the user-mode-only tier (older kernels). These tiers give less kernel telemetry, but the full control plane of the sensor still works.

### Forcing a lower tier

The sensor has one run-time override for compatibility. The eBPF tier has no opt-out, because the sensor selects it only when the kernel supports it.

- `DISABLE_NETLINK` — set this to any value in the environment of the sensor process to skip the netlink connector. Use it when another component on the host already consumes netlink proc events, or when the connector does not behave correctly. It has no effect when the sensor uses eBPF.

## Installation Instructions

### System Requirements

The sensor runs on glibc distributions back to glibc 2.17 (RHEL 7 / CentOS 7 / Debian 8 and newer). For older systems, or for systems without glibc, use the **Alpine / musl** build. This build is statically linked and does not depend on the host libc. The standard glibc build does not support older distributions such as RHEL 5 / 6, because of the libc baseline. You can evaluate the musl build for those systems, but the kernel telemetry is limited to what the host kernel exposes. See the tier table above.

### Deb Package

On a Debian Linux system, use the `.deb` package. [Downloading the Agent](../../index.md) gives a link to the Debian package for each architecture.

The deb package installs the LimaCharlie sensor as a `systemd` service. If `systemd` is not available, it installs a `system V` service.

The installer needs the Installation Key through the `debconf` configuration mechanism. By default, an interactive install requests the installation key through a local command or GUI interface. For large installations, set the installation key programmatically.

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

LimaCharlie supplies Debian packages for the architectures that the Linux sensor supports, like:

- **x64**: <https://downloads.limacharlie.io/sensor/linux/deb64>
- **arm64**: <https://downloads.limacharlie.io/sensor/linux/debarm64>

### RPM Package

On an RPM-based Linux distribution (RHEL, CentOS, Rocky, AlmaLinux, Fedora, openSUSE, Amazon Linux), use the `.rpm` package.

The rpm package installs the LimaCharlie sensor as a `systemd` service.

RPM has no interactive prompt mechanism, unlike the `.deb` package, and cannot request the installation key at install time. The post-install scriptlet looks for the key in two locations, in this order:

1. The `LC_INSTALLATION_KEY` environment variable.
2. The file `/etc/limacharlie/installation_key`.

If the key is in neither location, the package install stops with an error that explains the cause. The install changes no system state before it stops, so a missing key never leaves the host partly configured.

**Installing with the environment variable:**

```bash
sudo LC_INSTALLATION_KEY=INSTALLATION_KEY_HERE rpm -i limacharlie.rpm
```

or with `dnf` / `yum`:

```bash
sudo LC_INSTALLATION_KEY=INSTALLATION_KEY_HERE dnf install ./limacharlie.rpm
```

**Installing with the key file:**

```bash
sudo mkdir -p /etc/limacharlie
echo "INSTALLATION_KEY_HERE" | sudo tee /etc/limacharlie/installation_key >/dev/null
sudo chmod 600 /etc/limacharlie/installation_key
sudo rpm -i limacharlie.rpm
```

The install reads the key file one time. You can delete the file after the install to keep the key off the disk. The sensor then uses its own enrollment files.

**Uninstalling:**

```bash
sudo rpm -e limacharlie
```

or

```bash
sudo dnf remove limacharlie
```

The uninstall stops the service and removes the sensor binary, the identity files, and the package staging directory.

LimaCharlie supplies RPM packages for the architectures that the Linux sensor supports, like:

- **x64**: <https://downloads.limacharlie.io/sensor/linux/rpm64>
- **arm64**: <https://downloads.limacharlie.io/sensor/linux/rpmarm64>

### Custom Installation

Some systems cannot use the `.deb` package or the `.rpm` package. Examples are distributions without `dpkg` or `rpm`, and installs that need a non-standard layout. On these systems, download the installer directly with this command:

```python
wget https://downloads.limacharlie.io/sensor/linux/64 -O /tmp/lc_sensor
```

> Other Linux Versions
>
> To install on an ARM64 or Alpine64 system, replace the URL in the command above with the URL for that system from the installation wizard in LimaCharlie

When you run the installer from the command line, pass the `-d INSTALLATION_KEY` argument. `INSTALLATION_KEY` is the key above.

Linux has many frameworks that manage services. Because of this, the LC sensor does not install itself onto the system by default. It uses the current working directory as the installation directory and starts enrollment from there.

You can therefore wrap the executable with the service management technology of your Organization. Give the location of the installer and the `-d INSTALLATION_KEY` parameter. Make sure that the current working directory is the directory for the few sensor files that go to disk.

Many Linux systems use `init.d`. If `init.d` is enough for your needs, see the [sample install script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh).
Run it like this:

```bash
sudo chmod +x ./lc_linux_installer.sh
sudo ./lc_linux_installer.sh <PATH_TO_LC_SENSOR> <YOUR_INSTALLATION_KEY>
```

You can also pass the value `-` in place of the `INSTALLATION_KEY`, like this: `-d -`. The installer then looks for the installation key in these locations, in this order:

- Environment variable `LC_INSTALLATION_KEY`
- Text file in current working directory: `lc_installation_key.txt`

### Disabling Netlink

On a kernel without eBPF, the Linux sensor uses the netlink proc connector (`CN_PROC`) to receive real-time process events. A few configurations do not want this auto-detection. For example, another agent on the host can already consume the same connector. To disable netlink, set the environment variable `DISABLE_NETLINK` to any value on the sensor process. If netlink is disabled and eBPF is not available, the sensor falls back to user-mode `/proc` polling. This setting has no effect when eBPF is the active acquisition path.

### Custom Data Directory

By default, the sensor stores its data and status files under `/opt/limacharlie`. If that path is not writable on a non-standard or hardened distribution, point the sensor at a different directory. Set the `LC_DATA_DIRECTORY` environment variable on the sensor process to an absolute path. The directory must exist, and the sensor must be able to write to it.

### Restricting DNS Tracking to an Interface

By default, DNS tracking watches all network interfaces. To limit it to one interface, set the `LC_DNS_IFACE` environment variable on the sensor process to the interface name (for example `LC_DNS_IFACE=eth0`).

For the complete list of supported options, see the [Agent CLI & Environment Reference](../cli-reference.md).

## Uninstalling the Agent

For more uninstall options, see [Endpoint Agent Uninstallation](../uninstallation.md)

The uninstall method depends on how you installed the sensor. If you installed a Debian package (`dpkg` file) or an RPM package (`rpm` / `dnf` / `yum`), uninstall with the same package manager. If you used the SystemV installation method, use the bottom of the [SystemV install script](https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh#L97).

### Sensor Command

The `uninstall` command does not work for Linux systems. But you can run a chained command from the Sensor Console:

```powershell
 run --shell-command "service limacharlie stop; rm /bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp ; rm /etc/hcp_conf; rm /etc/hcp_hbs"
```

The command above removes LimaCharlie and its files from the system when you run it remotely. You can also join the command to a rule that uninstalls the sensor automatically.

### Debian Systems

If you installed the sensor with the .deb file, this option is the cleanest uninstall method.

```bash
apt remove limacharlie
```

### RPM-based Systems

If you installed the sensor with the .rpm file, use the matching package manager:

```bash
sudo dnf remove limacharlie
```

or

```bash
sudo rpm -e limacharlie
```
