# Agent CLI & Environment Reference

This page is the one reference for the command-line options, the environment
variables, and the local files that the LimaCharlie endpoint agent supports.
The agent is the on-disk sensor binary, named `rphcp` after installation. The
installation page for each platform links to this page for the full list.

All options below are available in the released sensor. This page does not
document internal flags or debug-only flags.

## Command-Line Options

The same binary installs the service, manages the service, and runs it. When
you start the binary from the command line, you can give the options below.
Most management actions need **root** (Linux/macOS) or **Administrator**
(Windows).

| Option | Long form | Description |
|--------|-----------|-------------|
| `-i <KEY>` | `--install` | Install as a service with the given installation key, then enroll. |
| `-d <KEY>` | `--deployment` | Run with the installation key, but do not install permanently (temporary or foreground enrollment). Give `-d -` to read the key from the environment or from a local file (see [Installation key sources](#installation-key-sources)). |
| `-u` | `--upgrade` | Upgrade the installed service in place with this binary. Needs sensor **4.33.28+**. See [Service Upgrades](service-upgrades.md). |
| `-r` | `--uninstall` | Uninstall the service. The identity files stay on disk. |
| `-c` | `--uninstall-clean` | Uninstall the service and delete the identity and configuration files (`hcp`, `hcp_hbs`, `hcp_conf`). |
| `-t` | `--vdi` | Write the VDI delay file to delay enrollment by 24 hours. Use this option when you build golden images. See [VDI Templates](vdi/templates.md). |
| `-H` | `--health` | Run the sensor health check and write a diagnostic report. See [Sensor Troubleshooting Utility](../../8-reference/faq/troubleshooting.md#sensor-troubleshooting-utility). Needs sensor **4.33.6+**. |
| `-v` | `--verbose` | Enable verbose logging output. This is the same as `LC_VERBOSE=1`. |
| `-V` | `--version` | Print the sensor build version and exit. |
| `-w` | `--service` | Run as a service. The OS service manager (SCM, launchd, systemd) uses this form. You do not usually start it directly. |
| `-h` | `--help` | Print the list of accepted options. |

## Environment Variables

The sensor process reads these environment variables. For installed services,
set the variables in your service manager (systemd unit, launchd plist, or the
Windows service environment). The running service then inherits them. For the
procedure for each platform, see
[Setting Environment Variables for an Installed Service](#setting-environment-variables-for-an-installed-service)
below.

### Enrollment

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_INSTALLATION_KEY` | All | Installation key that the sensor uses when it enrolls with `-d -` or with a packaged installer. This variable has priority over the local key file. |

### Logging & Troubleshooting

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_VERBOSE` | All | Set to `1`/`true` to enable verbose logging. This has the same effect as the `-v` flag. |
| `RPAL_LOG_LEVEL` | All | Sets the log verbosity. Accepted values: `off`, `error` (alias `critical`), `warning` (alias `warn`), `info`, `debug`. The default in release builds is `warning`. **In released sensors, `warning` is the most verbose level that gives output. The `info` and `debug` log statements are compiled out, so those values have no more effect.** |
| `RPAL_LOG_FILE` | All | Path of a file for the logs. This variable is the opt-in for logging on a release sensor. The sensor writes to the file at `RPAL_LOG_LEVEL` (`warning` and above). Without it, a release sensor writes nothing unless you set `LC_VERBOSE`. The log can contain operational details about the host. Treat the log as sensitive and delete it after you complete the troubleshooting. |

See [Enabling Verbose and File Logging](../../8-reference/faq/troubleshooting.md#enabling-verbose-and-file-logging)
for examples.

### Connectivity

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_PROXY` | All | Send the cloud connection through an HTTP CONNECT proxy (for example `proxy.corp.com:8080`). Special values: `-` (Windows registry auto-detect) and `!` (disable). See [Sensor Connectivity](../connectivity.md#proxy-tunneling). |
| `LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK` | Windows | Set to `1`/`true` to make the code-signature revocation checks (CRL/OCSP) use only the local cache and never use the network. This is useful on air-gapped networks and on networks with strict restrictions. |
| `LC_DISABLE_REVERSE_DNS_HOSTNAME` | All | Set to `1`/`true` to skip reverse-DNS hostname resolution. See [Hostname Resolution](hostname-resolution.md). |

### Data & Collection

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_DATA_DIRECTORY` | All | Change the directory where the sensor keeps its data files and status files (default `/opt/limacharlie` on Linux, `/Library/Application Support/limacharlie` on macOS, `C:\ProgramData\limacharlie` on Windows). This is useful on non-standard or hardened distributions where the sensor cannot write to the default path. |
| `LC_DNS_IFACE` | Linux | Limit DNS tracking to one named network interface (for example `eth0`). If you do not set this variable, the sensor watches all interfaces. |
| `DISABLE_NETLINK` | Linux | Set to any value to skip the netlink (`CN_PROC`) process connector and use `/proc` polling instead. It has no effect when the sensor uses eBPF. See [Disabling Netlink](linux/installation.md#disabling-netlink). |
| `LC_MOD_LOAD_LOC` | Linux/macOS | Different directory for the temporary module files of the sensor. Use it on hosts where the default location is restricted (for example by SELinux). |
| `HOST_FS` | Linux/macOS | Path of the host root filesystem when the sensor runs in a container. See [Docker installation](docker/installation.md). |
| `NET_NS` | Linux/macOS | Directory that contains the network namespaces (default `/var/run/docker/netns`). The sensor uses it for network collection with namespaces on hosts that run containers. |

### Upgrades

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_UPGRADE_SKIP_VERSION_CHECK` | All | **Advanced.** Set to `1`/`true` to skip the version comparison during an in-place upgrade (`-u`). The binary then replaces the installed service even when the binary is not newer. Use it only when you apply a known-good build again, or downgrade to one, on purpose. |

## Setting Environment Variables for an Installed Service

The sensor process reads the variables above when it starts. When the sensor
runs as a managed service, it inherits its environment from the service
manager, not from your interactive shell. An `export` command in a terminal has
no effect on the running service.

To apply a variable, set it in the service manager and then restart the
service. The service manager then starts the service again with the new
environment. The procedure below is the same for each variable in the tables
above. Use the variable name and the value that you need.

### macOS (launchd)

The installed sensor runs as the launchd daemon `com.refractionpoint.rphcp`.
The file `/Library/LaunchDaemons/com.refractionpoint.rphcp.plist` defines the
daemon. Add an `EnvironmentVariables` dictionary to that plist (launchd values
are always strings):

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>LC_DISABLE_REVERSE_DNS_HOSTNAME</key>
    <string>1</string>
</dict>
```

To set more variables, add more `<key>`/`<string>` pairs to the same `<dict>`.
launchd applies the environment only when it starts the process, so a daemon
that runs does not get the change before a restart. Check the edited file, then
load the daemon again:

```bash
sudo plutil -lint /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl bootout system /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
```

Confirm that the running service has the variable:

```bash
sudo launchctl print system/com.refractionpoint.rphcp | grep -A 5 environment
```

Notes:

- **Test without an edit to the plist.** To apply a variable for the *next*
  launch only, use `sudo launchctl debug system/com.refractionpoint.rphcp --environment LC_DISABLE_REVERSE_DNS_HOSTNAME=1`
  and then `sudo launchctl kickstart -k system/com.refractionpoint.rphcp`.
  The setting applies to that one launch and is not persistent. Use it to
  confirm the effect of a variable before you write it to the plist.
- **Managed fleets.** A new installation of the sensor creates the plist again,
  so set the variable again after each reinstallation. On hosts that an MDM
  manages, set the variable through the management channel. The variable then
  stays when the MDM applies the configuration profile again. See
  [MDM Profiles](macos/mdm-profiles.md).

### Linux (systemd)

The installed sensor runs as the `limacharlie` systemd unit. Do not edit the
packaged unit file. Add an environment drop-in:

```bash
sudo systemctl edit limacharlie
```

In the editor that opens, add:

```ini
[Service]
Environment=LC_DISABLE_REVERSE_DNS_HOSTNAME=1
```

This writes `/etc/systemd/system/limacharlie.service.d/override.conf`. To apply
it, restart the service:

```bash
sudo systemctl restart limacharlie
```

`systemctl edit` reloads the systemd daemon for you. If you create or edit the
drop-in file manually, run `sudo systemctl daemon-reload` first. On hosts that
use a System V init service instead of systemd, export the variable from the
environment of the init script. Check the running process:

```bash
sudo cat /proc/"$(pgrep -x rphcp)"/environ | tr '\0' '\n' | grep '^LC_'
```

### Windows (service)

The installed sensor runs as the `rphcpsvc` service. Set the variable in one of
two ways, then restart the service:

- **Machine-wide (simplest):** run `setx /M LC_DISABLE_REVERSE_DNS_HOSTNAME 1`
  from an elevated prompt. This adds the variable to the system environment
  that every service and every new process inherits.
- **Scoped to the sensor service:** add a `REG_MULTI_SZ` value named
  `Environment` under
  `HKLM\SYSTEM\CurrentControlSet\Services\rphcpsvc`, with one `NAME=value`
  entry for each line. The Service Control Manager merges these entries into
  the environment of the service only. The rest of the host does not change.

Restart the service. It then starts with the new environment:

```powershell
Restart-Service rphcpsvc
```

## Local Files

| File | Default location | Purpose |
|------|------------------|---------|
| `lc_installation_key.txt` | Current working directory | Optional source of the installation key when you use `-d -`. |
| `hcp`, `hcp_hbs`, `hcp_conf` | `/etc` (Linux), `/usr/local` (macOS), `C:\Windows\System32` (Windows) | Identity and configuration files that the installer writes. `-c` deletes them; `-r` keeps them. |
| `hcp_vdi` / `hcp_vdi.dat` | `/etc` or CWD (Linux), `/usr/local` (macOS), `C:\Windows\System32` (Windows) | VDI delay file. It holds the epoch timestamp until which the sensor delays enrollment. See [VDI Templates](vdi/templates.md). |
| `hcp.log` | `./hcp.log` (Linux), `/usr/local/hcp.log` (macOS), `C:\Windows\System32\hcp.log` (Windows) | First-connection connectivity log. See [Sensor Not Connecting](../../8-reference/faq/troubleshooting.md#sensor-not-connecting). |
| `hcp_hbs_status.json` | Sensor data directory (see `LC_DATA_DIRECTORY`) | Local status file with the sensor ID, the org ID, the version, and the uptime. |
| `sensor_health_YYYY_MM_DD_HH_MM.json` | Sensor data directory (see `LC_DATA_DIRECTORY`) | Output of the `-H` health check. |

## Installation Key Sources

If you give `-` to `-i`/`-d` instead of a literal key, the sensor looks for the
installation key in this order:

1. The `LC_INSTALLATION_KEY` environment variable.
2. The `lc_installation_key.txt` file in the current working directory.
