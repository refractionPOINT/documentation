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
or the Windows service environment) so the running service inherits them.

### Enrollment

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_INSTALLATION_KEY` | All | Installation key used when enrolling with `-d -` (or via packaged installers). Takes priority over the local key file. |

### Logging & Troubleshooting

| Variable | Platforms | Description |
|----------|-----------|-------------|
| `LC_VERBOSE` | All | Set to `1`/`true` to enable verbose logging (same effect as the `-v` flag). |
| `RPAL_LOG_LEVEL` | All | Sets the log verbosity. Accepted values: `off`, `error` (alias `critical`), `warning` (alias `warn`), `info`, `debug`. Defaults to `warning` in release builds. |
| `RPAL_LOG_FILE` | All | Path to a file to write logs to. Setting this is the opt-in for logging on a release sensor — output is written to the file at `RPAL_LOG_LEVEL` (default `warning`). Without it, a release sensor stays silent unless `LC_VERBOSE` is set. |

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
