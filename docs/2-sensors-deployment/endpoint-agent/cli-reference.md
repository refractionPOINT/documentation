# Agent CLI & Environment Reference

This page is the single reference for the command-line options, environment
variables, and local files supported by the LimaCharlie endpoint agent (the
on-disk sensor binary, named `rphcp` once installed). The platform-specific
installation pages link here for the full list.

All options below are available in the released sensor. Internal/debug-only
flags are intentionally not documented.

## Command-Line Options

The same binary is used both to install/manage the service and to run it. When
run from the command line you can pass the following options. Most management
actions require **root** (Linux/macOS) or **Administrator** (Windows).

| Option | Long form | Description |
|--------|-----------|-------------|
| `-i <KEY>` | `--install` | Install as a service using the specified installation key, then enroll. |
| `-d <KEY>` | `--deployment` | Run with the installation key without performing a permanent installation (temporary/foreground enrollment). Pass `-d -` to read the key from the environment or a local file (see [Installation key sources](#installation-key-sources)). |
| `-u` | `--upgrade` | Upgrade the installed service in place using this binary. Requires sensor **4.33.28+**. See [Service Upgrades](service-upgrades.md). |
| `-r` | `--uninstall` | Uninstall the service, leaving the identity files on disk. |
| `-c` | `--uninstall-clean` | Uninstall the service and delete the identity/config files (`hcp`, `hcp_hbs`, `hcp_conf`). |
| `-t` | `--vdi` | Write the VDI delay file to postpone enrollment by 24 hours, for use when baking golden images. See [VDI Templates](vdi/templates.md). |
| `-H` | `--health` | Run the sensor health check and write a diagnostic report. See [Sensor Troubleshooting Utility](../../8-reference/faq/troubleshooting.md#sensor-troubleshooting-utility). Requires sensor **4.33.6+**. |
| `-v` | `--verbose` | Enable verbose logging output (equivalent to setting `LC_VERBOSE=1`). |
| `-V` | `--version` | Print the sensor build version and exit. |
| `-w` | `--service` | Run as a service. This is the form used by the OS service manager (SCM, launchd, systemd); you normally do not invoke it directly. |
| `-h` | `--help` | Print the list of accepted options. |

## Environment Variables

These environment variables are read by the sensor process. For installed
services, set them through your service manager (systemd unit, launchd plist,
or the Windows service environment) so the running service inherits them — see
[Setting Environment Variables for an Installed Service](#setting-environment-variables-for-an-installed-service)
below for the per-platform procedure.

### Enrollment

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_INSTALLATION_KEY` | All | Installation key used when enrolling with `-d -` (or via packaged installers). Takes priority over the local key file. |

### Logging & Troubleshooting

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_VERBOSE` | All | Set to `1`/`true` to enable verbose logging (same effect as the `-v` flag). |
| `RPAL_LOG_LEVEL` | All | Sets the log verbosity. Accepted values: `off`, `error` (alias `critical`), `warning` (alias `warn`), `info`, `debug`. Defaults to `warning` in release builds. **In released sensors `warning` is the most verbose level that produces output — `info` and `debug` log statements are compiled out, so those values have no additional effect.** |
| `RPAL_LOG_FILE` | All | Path to a file to write logs to. Setting this is the opt-in for logging on a release sensor — output is written to the file at `RPAL_LOG_LEVEL` (`warning` and above). Without it, a release sensor stays silent unless `LC_VERBOSE` is set. The log can contain operational details about the host; treat it as potentially sensitive and remove it once you are done troubleshooting. |

See [Enabling Verbose and File Logging](../../8-reference/faq/troubleshooting.md#enabling-verbose-and-file-logging)
for usage examples.

### Connectivity

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_PROXY` | All | Route the cloud connection through an HTTP CONNECT proxy (e.g. `proxy.corp.com:8080`). Special values: `-` (Windows registry auto-detect) and `!` (disable). See [Sensor Connectivity](../connectivity.md#proxy-tunneling). |
| `LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK` | Windows | Set to `1`/`true` to make code-signature revocation checks (CRL/OCSP) use only the local cache and never reach out to the network. Useful on air-gapped or tightly restricted networks. |
| `LC_DISABLE_REVERSE_DNS_HOSTNAME` | All | Set to `1`/`true` to skip reverse-DNS hostname resolution. See [Hostname Resolution](hostname-resolution.md). |

### Data & Collection

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_DATA_DIRECTORY` | All | Override the directory where the sensor stores its data and status files (default `/opt/limacharlie` on Linux, `/Library/Application Support/limacharlie` on macOS, `C:\ProgramData\limacharlie` on Windows). Useful on non-standard or hardened distributions where the default path is not writable. |
| `LC_DNS_IFACE` | Linux | Restrict DNS tracking to a single named network interface (e.g. `eth0`). When unset, all interfaces are watched. |
| `DISABLE_NETLINK` | Linux | Set to any value to skip the netlink (`CN_PROC`) process connector and fall back to `/proc` polling. No effect when eBPF is in use. See [Disabling Netlink](linux/installation.md#disabling-netlink). |
| `LC_MOD_LOAD_LOC` | Linux/macOS | Alternate directory for the sensor's temporary module-loading files, for hosts where the default location is restricted (e.g. SELinux). |
| `HOST_FS` | Linux/macOS | Path to the host root filesystem when the sensor runs inside a container. See [Docker installation](docker/installation.md). |
| `NET_NS` | Linux/macOS | Directory containing network namespaces (default `/var/run/docker/netns`) for namespace-aware network collection in containerized hosts. |

### Upgrades

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_UPGRADE_SKIP_VERSION_CHECK` | All | **Advanced.** Set to `1`/`true` to skip the version comparison during an in-place upgrade (`-u`), forcing the binary to replace the installed service even when it is not newer. Use only when deliberately re-applying or downgrading a known-good build. |

## Setting Environment Variables for an Installed Service

The variables above are read by the sensor process when it starts. When the
sensor runs as a managed service it inherits its environment from the service
manager, not from your interactive shell, so `export`-ing a variable in a
terminal has no effect on the running service. To make a variable take effect
you set it in the service manager and then restart the service so it is
re-spawned with the new environment. The procedure below is the same for any
variable in the tables above — substitute the variable name and value you need.

### macOS (launchd)

The installed sensor runs as the launchd daemon `com.refractionpoint.rphcp`,
defined by `/Library/LaunchDaemons/com.refractionpoint.rphcp.plist`. Add an
`EnvironmentVariables` dictionary to that plist (launchd values are always
strings):

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>LC_DISABLE_REVERSE_DNS_HOSTNAME</key>
    <string>1</string>
</dict>
```

Add more `<key>`/`<string>` pairs to the same `<dict>` to set additional
variables. Validate the edited file, then reload the daemon so launchd
re-reads it — the environment is applied only when the process is spawned, so a
running daemon will not pick up the change until it is restarted:

```bash
sudo plutil -lint /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl bootout system /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
```

Confirm the running service picked up the variable:

```bash
sudo launchctl print system/com.refractionpoint.rphcp | grep -A 5 environment
```

Notes:

- **Test without editing the plist.** To apply a variable for the *next* launch
  only, use `sudo launchctl debug system/com.refractionpoint.rphcp --environment LC_DISABLE_REVERSE_DNS_HOSTNAME=1`
  followed by `sudo launchctl kickstart -k system/com.refractionpoint.rphcp`.
  The setting is consumed on that single launch and is not persistent — useful
  for confirming a variable's effect before committing it to the plist.
- **Managed fleets.** Reinstalling the sensor recreates the plist, so re-apply
  the variable after a reinstall. On hosts managed by an MDM, set the variable
  through the management channel so it is not reverted when the configuration
  profile is re-applied. See [MDM Profiles](macos/mdm-profiles.md).

### Linux (systemd)

The installed sensor runs as the `limacharlie` systemd unit. Add an environment
drop-in rather than editing the packaged unit file:

```bash
sudo systemctl edit limacharlie
```

In the editor that opens, add:

```ini
[Service]
Environment=LC_DISABLE_REVERSE_DNS_HOSTNAME=1
```

This writes `/etc/systemd/system/limacharlie.service.d/override.conf`. Apply it
by restarting the service:

```bash
sudo systemctl restart limacharlie
```

`systemctl edit` reloads the systemd daemon for you; if you create or edit the
drop-in file by hand, run `sudo systemctl daemon-reload` first. On hosts that
use a System V init service instead of systemd, export the variable from the
init script's environment. Verify the running process:

```bash
sudo cat /proc/"$(pgrep -x rphcp)"/environ | tr '\0' '\n' | grep '^LC_'
```

### Windows (service)

The installed sensor runs as the `rphcpsvc` service. Set the variable in one of
two ways, then restart the service:

- **Machine-wide (simplest):** `setx /M LC_DISABLE_REVERSE_DNS_HOSTNAME 1` (run
  from an elevated prompt). This adds the variable to the system environment
  that every service and new process inherits.
- **Scoped to the sensor service:** add a `REG_MULTI_SZ` value named
  `Environment` under
  `HKLM\SYSTEM\CurrentControlSet\Services\rphcpsvc`, with one `NAME=value`
  entry per line. The Service Control Manager merges these into the service's
  environment only, leaving the rest of the host untouched.

Restart the service so it is re-spawned with the new environment:

```powershell
Restart-Service rphcpsvc
```

## Local Files

| File | Default location | Purpose |
|------|------------------|---------|
| `lc_installation_key.txt` | Current working directory | Optional source of the installation key when using `-d -`. |
| `hcp`, `hcp_hbs`, `hcp_conf` | `/etc` (Linux), `/usr/local` (macOS), `C:\Windows\System32` (Windows) | Identity and configuration files written at install time. Removed by `-c`; left in place by `-r`. |
| `hcp_vdi` / `hcp_vdi.dat` | `/etc` or CWD (Linux), `/usr/local` (macOS), `C:\Windows\System32` (Windows) | VDI delay file holding the epoch timestamp until which enrollment is postponed. See [VDI Templates](vdi/templates.md). |
| `hcp.log` | `./hcp.log` (Linux), `/usr/local/hcp.log` (macOS), `C:\Windows\System32\hcp.log` (Windows) | First-connection connectivity log. See [Sensor Not Connecting](../../8-reference/faq/troubleshooting.md#sensor-not-connecting). |
| `hcp_hbs_status.json` | Sensor data directory (see `LC_DATA_DIRECTORY`) | Local status file with sensor ID, org ID, version, and uptime. |
| `sensor_health_YYYY_MM_DD_HH_MM.json` | Sensor data directory (see `LC_DATA_DIRECTORY`) | Output of the `-H` health check. |

## Installation Key Sources

When `-i`/`-d` is given `-` instead of a literal key, the sensor looks for the
installation key in this order:

1. The `LC_INSTALLATION_KEY` environment variable.
2. The `lc_installation_key.txt` file in the current working directory.
