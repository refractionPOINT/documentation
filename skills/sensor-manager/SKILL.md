---
name: sensor-manager
description: Help users deploy, configure, manage, troubleshoot, and perform operations on LimaCharlie endpoint sensors across Windows, macOS, Linux, Chrome, and Edge platforms.
---

# LimaCharlie Sensor Manager

This skill provides comprehensive guidance for deploying, configuring, managing, and troubleshooting LimaCharlie endpoint sensors (also called endpoint agents). Use this skill when users need help with sensor installation, sensor commands, sensor management, tagging, versioning, or any sensor-related operations.

## Table of Contents

1. [Sensor Overview](#sensor-overview)
2. [Installation Keys](#installation-keys)
3. [Deployment Methods](#deployment-methods)
4. [Sensor Commands](#sensor-commands)
5. [Sensor Management](#sensor-management)
6. [Versioning and Upgrades](#versioning-and-upgrades)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Sensor Overview

### What are LimaCharlie Sensors?

LimaCharlie sensors (also called endpoint agents) are lightweight agents that run on endpoints to collect EDR (Endpoint Detection and Response) telemetry and forward it to the LimaCharlie cloud platform. Sensors provide deep visibility into endpoint activity while maintaining minimal performance impact.

**Key Characteristics:**
- Serverless, scalable solution for endpoint monitoring
- Support for Windows, macOS, Linux, Chrome, and Edge platforms
- Over 60 commands for file operations, memory operations, process operations, and more
- Single TCP connection over port 443 with pinned SSL certificates
- Two-component architecture: on-disk agent and over-the-air core

### Sensor Architecture

The LimaCharlie endpoint agent consists of two independently versioned components:

1. **On-disk agent**: Implements core identity, cryptography, and transport mechanisms. Rarely requires updates and typically remains static.
2. **Over-the-air core**: The main component that receives frequent updates (every few weeks) and delivers advanced functionality. Can be easily updated via the LimaCharlie cloud. Update size is generally 3-5 MB.

---

## Installation Keys

### What are Installation Keys?

Installation keys are Base64-encoded strings that associate sensors with the correct Organization. They provide a way to label and control your deployment population.

**Four Components of an Installation Key:**
1. **Organization ID (OID)**: The Organization ID that this key should enroll into
2. **Installer ID (IID)**: Generated and associated with every installation key
3. **Tags**: A list of tags automatically applied to sensors enrolling with the key
4. **Description**: Helps differentiate uses of various keys

### Managing Installation Keys

Installation keys can be managed on the **Sensors > Installation Keys** page in the web app.

### Use of Installation Keys for Classification

Use different installation keys to classify and organize your sensor deployments:

**Examples:**
- Key with "server" tag for server installations
- Key with "vip" tag for executive machines
- Key with "sales" tag for sales department
- Key with "production" tag for production environments
- Key with "staging" tag for staging environments

This enables you to:
- Write different detection and response rules for different host types
- Apply different security policies based on tags
- Organize and filter sensors effectively

### Pinned Certificates

By default, sensors use pinned SSL certificates and do not support traffic interception. To create installation keys without pinned certificates (allowing proxy inspection), you must use the REST API and set the `use_public_root_ca` flag to `true`.

### Proxy Support

The LimaCharlie sensor supports unauthenticated proxy tunneling through HTTP CONNECT.

**Configuration:**
Set the `LC_PROXY` environment variable to the DNS or hostname of the proxy:
```
LC_PROXY=proxy.corp.com:8080
```

**Windows-specific:**
- Use `LC_PROXY=-` for auto-detection of globally-configured, unauthenticated proxy
- The sensor will query: `HKLM\Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer`
- Use `LC_PROXY=!` to explicitly disable proxy

---

## Deployment Methods

### Windows Deployment

#### Standard Installation

1. Download the installer: `https://downloads.limacharlie.io/sensor/windows/64`
2. Run with `-i` flag and installation key:
```
hcp_win_x64_release.exe -i YOUR_INSTALLATION_KEY
```

#### Unattended Installation
```
hcp_win_x64_release.exe -i YOUR_INSTALLATION_KEY -q
```

#### Custom MSI Installer

For enterprise deployments, create a custom MSI installer:

**Prerequisites:**
- MSI wrapper application (e.g., exemsi)
- Digital code signing certificate (optional but recommended)

**Steps:**
1. Download LimaCharlie sensor EXE
2. Use MSI wrapper (like exemsi) to create MSI package
3. Set install arguments: `-i YOUR_INSTALLATION_KEY`
4. Set uninstall arguments: `-c`
5. Customize branding (product name, manufacturer, icon)
6. Sign the MSI with your digital certificate

**Benefits:**
- White-label the installer with your branding
- Easier deployment via enterprise tools (Intune, SCCM, GPO)
- Professional appearance in Windows Apps & Features

#### Enterprise Deployment via Microsoft Intune

See the Enterprise-Wide Agent Deployment documentation for Intune-specific instructions.

#### Uninstallation

**Via sensor command:**
```
uninstall --is-confirmed
```

**For MSI installations:**
```
uninstall --msi --is-confirmed
```

**Manual uninstallation:**
- Use Windows Add/Remove Programs
- Or run installer with `-c` flag

---

### macOS Deployment

#### macOS 10.15 Catalina to macOS 14 Sonoma

**Installation:**

1. Download the installer:
   - Intel Mac: `https://downloads.limacharlie.io/sensor/mac/64`
   - Apple Silicon: `https://downloads.limacharlie.io/sensor/mac/arm64`

2. Add execute permission:
```bash
chmod +x lc_sensor
```

3. Run installer with installation key:
```bash
sudo ./lc_sensor -i YOUR_INSTALLATION_KEY
```

4. Grant required permissions:
   - System Extensions: Allow RPHCP system extensions
   - Network Filter: Allow network content filtering
   - Full Disk Access: Enable in System Preferences > Privacy > Full Disk Access

**Note:** The RPHCP.app will be installed in /Applications and must remain there for proper operation.

**Verification:**
```bash
sudo launchctl list | grep com.refractionpoint.rphcp
```

#### macOS 15 Sequoia and Newer

See the macOS Agent Installation documentation for the latest macOS versions.

#### MDM Deployment

For large-scale macOS deployments, use Apple-approved MDM solutions:
- Configuration profiles can automate permission grants
- Extensions can be added to allow lists organization-wide
- See vendor documentation for extension approval

**Supported MDM Solutions:**
- Jamf Now
- Microsoft Intune
- Other Apple-approved MDM solutions

#### Uninstallation

**Via sensor command:**
```
uninstall --is-confirmed
```

**Manual uninstallation:**
```bash
sudo ./lc_sensor -c
```

This removes:
- System extensions
- RPHCP.app from /Applications
- Service configuration

---

### Linux Deployment

**System Requirements:**
- Linux kernel 4.4 or above (for eBPF support)
- Use `uname -r` to check kernel version
- Supports all distributions including ARM and MIPS

#### Debian Package Installation

**Architectures:**
- x64: `https://downloads.limacharlie.io/sensor/linux/deb64`
- arm64: `https://downloads.limacharlie.io/sensor/linux/debarm64`

**Interactive Installation:**
```bash
sudo dpkg -i limacharlie.deb
# or
sudo apt install ./limacharlie.deb
```

**Programmatic Installation with dpkg:**
```bash
echo "limacharlie limacharlie/installation_key string YOUR_KEY" | sudo debconf-set-selections && sudo dpkg -i limacharlie.deb
```

**Programmatic Installation with apt:**
```bash
echo "limacharlie limacharlie/installation_key string YOUR_KEY" | sudo debconf-set-selections && sudo apt install ./limacharlie.deb -y
```

**Uninstallation:**
```bash
sudo dpkg -r limacharlie
# or
sudo apt remove limacharlie
```

#### Custom Installation (Non-Debian)

**Download installer:**
```bash
wget https://downloads.limacharlie.io/sensor/linux/64 -O /tmp/lc_sensor
```

**For ARM64 or Alpine64:**
- Replace URL with the respective URL from installation wizard

**Execute installer:**
```bash
chmod +x /tmp/lc_sensor
sudo /tmp/lc_sensor -d YOUR_INSTALLATION_KEY
```

**Alternative: Use environment variable or file:**
```bash
# Option 1: Environment variable
export LC_INSTALLATION_KEY=YOUR_KEY
sudo /tmp/lc_sensor -d -

# Option 2: Text file
echo "YOUR_KEY" > lc_installation_key.txt
sudo /tmp/lc_sensor -d -
```

**Service Installation:**
Linux supports multiple service frameworks. Use init.d, systemd, or your preferred service manager. Example install script: https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh

**Usage:**
```bash
sudo chmod +x ./lc_linux_installer.sh
sudo ./lc_linux_installer.sh <PATH_TO_LC_SENSOR> <YOUR_INSTALLATION_KEY>
```

#### Disabling Netlink

In rare configurations, disable Netlink by setting environment variable:
```bash
export DISABLE_NETLINK=1
```

#### Uninstallation

**For Debian packages:**
```bash
apt remove limacharlie
```

**For custom installations (SystemV):**
See the script at: https://github.com/refractionPOINT/lce_doc/blob/master/docs/lc_linux_installer.sh#L97

**Remote uninstallation via sensor command:**
```bash
run --shell-command "service limacharlie stop; rm /bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp ; rm /etc/hcp_conf; rm /etc/hcp_hbs"
```

---

### Docker Deployment

#### Host Visibility Requirements

For full visibility, the container requires:
- **Privileged mode** for host-level resource access
- **Host networking** for network activity observation
- **Host PID mode** for process tracking
- **Host-level directory mounts**:
  - Root filesystem (rootfs)
  - Docker network namespaces (netns)
  - Kernel modules and debug symbols

#### Docker CLI Deployment

```bash
docker run --privileged --net=host \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:ro \
  -v /sys/kernel/btf:/sys/kernel/btf:ro \
  -v /lib/modules:/lib/modules:ro \
  --env LC_INSTALLATION_KEY=<your_key> \
  --env HOST_FS=/rootfs \
  --env NET_NS=/netns \
  refractionpoint/limacharlie_sensor:latest
```

#### Docker Compose Deployment

```yaml
services:
  lc-sensor:
    image: refractionpoint/limacharlie_sensor:latest
    restart: unless-stopped
    network_mode: "host"
    pid: "host"
    privileged: true
    environment:
      - HOST_FS=/rootfs
      - NET_NS=/netns
      - LC_INSTALLATION_KEY=<your key>
    deploy:
      resources:
        limits:
          cpus: "0.9"
          memory: "256M"
        reservations:
          cpus: "0.01"
          memory: "128M"
    cap_add:
      - SYS_ADMIN
    volumes:
      - /:/rootfs
      - /var/run/docker/netns:/netns
      - /sys/kernel/debug:/sys/kernel/debug
      - /sys/kernel/btf:/sys/kernel/btf
      - /lib/modules:/lib/modules
```

Start with:
```bash
docker-compose up -d
```

#### Image Flavors

- `latest`: Default (CentOS Linux)
- `alpine`: Alpine Linux (smaller size)
- `centos`: CentOS Linux

#### Environment Variables

- `LC_INSTALLATION_KEY`: Installation key for authentication
- `HOST_FS`: Path to host's root filesystem (e.g., `/rootfs`)
- `NET_NS`: Path to host's network namespace directory (e.g., `/netns`)

---

### Chrome Extension Deployment

The LimaCharlie Chrome Sensor is a browser extension providing visibility for browser activity.

**Installation:**

1. In LimaCharlie web app, go to "Installation Keys"
2. Copy the "Chrome Key" to clipboard
3. Install sensor from: `https://downloads.limacharlie.io/sensor/chrome`
4. A new tab will open - enter your installation key
5. Or configure via chrome://extensions/ > LimaCharlie Sensor > Extension options

**Enterprise Deployment:**

Use Managed Storage feature (key named `installation_key`) for managed Chrome deployments.

**Troubleshooting:**

1. Try uninstalling/re-installing the extension
2. If issues persist:
   - Go to chrome://extensions/
   - Enable "Developer Mode"
   - Click `background.html` link in LimaCharlie Sensor entry
   - Check Console for errors
   - Provide screenshot to LimaCharlie support with your OID

---

### Edge Extension Deployment

Similar to Chrome deployment. See Edge Agent Installation documentation for specific instructions.

---

### Container Clusters (Kubernetes)

For Kubernetes deployments, see the Container Clusters documentation.

---

### VDI and Virtual Machine Templates

**Important:** When creating VM templates with LimaCharlie sensors installed, special considerations apply. See the VDI Virtual Machine Templates documentation for proper template creation to avoid sensor ID conflicts.

---

## Sensor Commands

LimaCharlie sensors support over 60 commands for remote operations. Commands are executed via the sensor console or programmatically via API/SDK.

### Command Categories

#### File Operations
- `file_get`: Retrieve a file from the sensor
- `file_del`: Delete a file
- `file_hash`: Get file hash
- `file_info`: Get file metadata
- `file_mov`: Move/rename a file
- `dir_list`: List directory contents
- `dir_find_hash`: Find files by hash

#### Memory Operations
- `mem_map`: Get process memory map
- `mem_read`: Read process memory
- `mem_strings`: Extract strings from process memory
- `mem_find_string`: Search for string in process memory
- `mem_handles`: List process handles (Windows)
- `mem_find_handle`: Find specific handles (Windows)

#### Process Operations
- `os_processes`: List running processes
- `os_kill_process`: Terminate a process
- `os_suspend`: Suspend a process
- `os_resume`: Resume a suspended process

#### System Information
- `os_version`: Get OS version information
- `os_services`: List system services
- `os_autoruns`: List autorun entries
- `os_drivers`: List loaded drivers (Windows)
- `os_packages`: List installed packages
- `os_users`: List system users (Windows)
- `netstat`: Get network connections

#### Network Operations
- `dns_resolve`: Resolve DNS name
- `segregate_network`: Isolate sensor from network
- `rejoin_network`: Restore network connectivity

#### File Integrity Monitoring (FIM)
- `fim_add`: Add path to FIM monitoring
- `fim_del`: Remove path from FIM monitoring
- `fim_get`: List FIM rules

#### Exfiltration Rules
- `exfil_add`: Add exfiltration rule
- `exfil_del`: Delete exfiltration rule
- `exfil_get`: List exfiltration rules

#### YARA Scanning
- `yara_scan`: Scan with YARA rules
- `yara_update`: Update YARA rules

#### Artifacts and Logs
- `artifact_get`: Retrieve an artifact
- `log_get`: Get Windows event logs
- `history_dump`: Dump historical events

#### Management Operations
- `restart`: Restart the sensor
- `uninstall`: Uninstall the sensor
- `shutdown`: Shutdown the sensor
- `set_performance_mode`: Adjust performance settings
- `run`: Execute a command on the endpoint
- `put`: Upload a file to the endpoint
- `logoff`: Log off current user

#### macOS-Specific EPP Commands
- `epp_status`: Get EPP status
- `epp_scan`: Trigger EPP scan
- `epp_list_exclusions`: List EPP exclusions
- `epp_add_exclusion`: Add EPP exclusion
- `epp_rem_exclusion`: Remove EPP exclusion
- `epp_list_quarantine`: List quarantined items

### Platform Support Matrix

Commands have different support across platforms:

| Platform | Command Count | Notes |
|----------|--------------|-------|
| Windows | 60+ | Full feature set |
| macOS | 55+ | Includes EPP commands |
| Linux | 50+ | No Windows-specific commands |
| Chrome | ~10 | Browser-focused commands |
| Edge | ~10 | Browser-focused commands |

### Example Command Usage

**Get running processes:**
```
os_processes
```

**Retrieve a file:**
```
file_get --path "C:\Windows\System32\malware.exe"
```

**Kill a process:**
```
os_kill_process --pid 1234
```

**Network isolate sensor:**
```
segregate_network
```

**Restore network:**
```
rejoin_network
```

**YARA scan a directory:**
```
yara_scan --path "C:\Users" --rule-name "malware_signatures"
```

**Execute command on endpoint (use with caution):**
```
run --command "ipconfig /all"
```

---

## Sensor Management

### Listing Sensors

**In Web App:**
- Navigate to Sensors section
- View all enrolled sensors with metadata

**Via API/SDK (Python):**
```python
import limacharlie
lc = limacharlie.Manager()
for sensor in lc.sensors():
    print(sensor.sid, sensor.hostname)
```

### Filtering Sensors

Use **Sensor Selector Expressions** to filter sensors based on characteristics.

#### Available Fields

- `sid`: Sensor ID
- `oid`: Organization ID
- `iid`: Installation Key ID
- `plat`: Platform name (windows, linux, macos, chrome, etc.)
- `ext_plat`: Extended platform name
- `arch`: Architecture (x86, x64, arm, arm64)
- `enroll`: Enrollment timestamp (epoch seconds)
- `hostname`: Hostname
- `mac_addr`: Latest MAC address
- `alive`: Last connection timestamp (epoch seconds)
- `ext_ip`: Last external IP
- `int_ip`: Last internal IP
- `isolated`: Boolean - network isolated
- `should_isolate`: Boolean - marked for isolation
- `kernel`: Boolean - has kernel-level visibility
- `did`: Device ID
- `tags`: List of tags

#### Operators

- `==`: Equals
- `!=`: Not equal
- `in`: Element in list, or substring in string
- `not in`: Element not in list, or substring not in string
- `matches`: Matches regular expression
- `not matches`: Does not match regular expression
- `contains`: String contained within element

#### Example Selector Expressions

**All sensors with "test" tag:**
```
test in tags
```

**All Windows boxes with internal IP starting with 10.3.x.x:**
```
plat == windows and int_ip matches ^10\.3\..*
```

**All Linux sensors with network isolation or "evil" tag:**
```
plat == linux or (isolated == true or evil in tags)
```

**All Azure-related platforms:**
```
plat contains "azure"
```

**All sensors with platform starting with a number (use backticks):**
```
plat == `1password`
```

### Tagging Sensors

#### Tag Use Cases

**Classification:**
- Departments: sales, finance, operations, development
- Usage type: workstation, server, production, staging
- Importance: vip, critical, standard

**Automation:**
- Trigger different detection rules based on tags
- Apply different response actions
- Route detections to different outputs (Slack, email, SIEM)

**Workflow Creation:**
- Forward VIP detections to Slack
- Send standard detections to email
- Apply stricter monitoring to critical servers

#### Adding Tags

**1. Via Installation Key:**
Tags specified in installation key are automatically applied during enrollment.

**2. Via API:**
```
POST /{sid}/tags
```

**3. Via Detection & Response Rule:**
```yaml
# Response section
- action: add tag
  tag: DESKTOP
```

**4. Via Web App:**
Click on sensor to expand, then add/edit/remove tags.

#### Removing Tags

**Via API:**
```
DELETE /{sid}/tags
```

**Via Detection & Response Rule:**
Include remove tag action in response.

**Via Web App:**
Click sensor to expand, then remove tag.

#### System Tags

Special tags that control sensor behavior:

- `lc:latest`: Use latest sensor version (for testing)
- `lc:stable`: Use stable sensor version
- `lc:experimental`: Use experimental sensor version
- `lc:no_kernel`: Disable kernel component
- `lc:debug`: Use debug version of sensor
- `lc:limit-update`: Only update version at startup/reboot
- `lc:sleeper`: Enter sleeper mode (minimal activity)
- `lc:usage`: Usage-based billing mode

### Network Isolation

**Isolate sensor:**
```
segregate_network
```

**Restore network:**
```
rejoin_network
```

**Check isolation status:**
Use sensor selector: `isolated == true`

### Deleting Sensors

**Via Web App:**
Navigate to sensor, click delete.

**Via API/SDK:**
```python
import limacharlie
lc = limacharlie.Manager()
sensor = lc.sensor('SENSOR_ID')
sensor.delete()
```

**Note:** Deleting a sensor from the platform does not uninstall it from the endpoint. Use the `uninstall` command to remove the agent from the endpoint.

---

## Versioning and Upgrades

### Version Labels

LimaCharlie provides three version labels:

1. **Latest**: Most recent release with new fixes and features
2. **Stable**: Less frequently updated, ideal for slower update cadences
3. **Experimental**: Beta version of next "Latest" release

### Managing Sensor Versions

**Organization-Level:**
Set the default sensor version for your organization via web interface or API.

**Individual Sensor-Level:**
Use system tags to override organization default:
- `lc:latest`: Receive latest version
- `lc:stable`: Receive stable version
- `lc:experimental`: Receive experimental version

### Update Mechanisms

**Manual Update:**
Click button in web interface to update all sensors in organization. Updates take effect within 20 minutes.

**Auto-Update:**
Apply `lc:stable` tag to automatically update to latest stable version upon release.

**Staged Deployment:**
1. Tag representative sensors with `lc:latest`
2. Monitor for issues (stability, performance, telemetry quality)
3. If successful, update organization-level version
4. Remove `lc:latest` tag from test sensors

### Best Practices for Updates

1. **Test First**: Apply `lc:latest` to small subset of representative systems
2. **Monitor**: Evaluate stability, performance, telemetry quality
3. **Diverse Testing**: Test across different OS versions and workloads
4. **Gradual Rollout**: Update organization-wide only after successful testing
5. **Rollback Plan**: Keep `lc:stable` tag ready for quick rollback
6. **Update Timing**: Schedule updates during maintenance windows

### Update Constraints

Use `lc:limit-update` tag to prevent runtime updates. Sensor will only update at startup/reboot.

---

## Troubleshooting

### Non-Responding Sensors

#### Detection Method

Create a scheduled Detection & Response rule to check for sensors not sending data:

```python
import limacharlie
import time

SENSOR_SELECTOR = "plat == windows and `server` in tags"
DATA_WITHIN = 10 * 60 * 1000  # 10 minutes

def playbook(sdk: limacharlie.Limacharlie, data: dict) -> dict | None:
    relevant_sensors = sdk.sensors(selector=SENSOR_SELECTOR)
    stopped_sensors = []

    for sensor in relevant_sensors:
        data_overview = sensor.getHistoricOverview(
            int(time.time() - DATA_WITHIN),
            int(time.time())
        )
        after = int(time.time() * 1000) - DATA_WITHIN
        for timestamp in data_overview:
            if timestamp > after:
                break
        else:
            stopped_sensors.append(sensor)

    if stopped_sensors:
        return {
            "detection": {
                "stopped_sensors": [s.sid for s in stopped_sensors]
            }
        }
    return None
```

#### Common Causes

1. **Endpoint offline**: Machine is powered off or disconnected
2. **Network issues**: Firewall blocking port 443 or sensor domain
3. **Sensor service stopped**: Service crashed or was stopped
4. **Resource constraints**: Endpoint running out of resources
5. **Sensor uninstalled**: Agent was removed

#### Resolution Steps

1. **Verify endpoint is online**: Ping or connect to machine
2. **Check network connectivity**: Ensure port 443 access to sensor domain
3. **Verify service status**:
   - Windows: Check service in Services panel
   - macOS: `sudo launchctl list | grep com.refractionpoint.rphcp`
   - Linux: Check systemd/init.d service status
4. **Review endpoint logs**: Check for errors or crashes
5. **Restart service**: Restart the LimaCharlie service
6. **Reinstall sensor**: If necessary, reinstall the agent

### Connectivity Issues

#### Symptoms
- Sensor fails to enroll
- Sensor appears offline
- Intermittent disconnections

#### Network Requirements

- **Port**: 443 (TCP)
- **Protocol**: HTTPS with pinned SSL certificates
- **Domain**: Specific to your datacenter (check Installation Keys page)

#### Proxy Configuration

If using a proxy, set `LC_PROXY` environment variable:
```
LC_PROXY=proxy.corp.com:8080
```

For Windows auto-detection:
```
LC_PROXY=-
```

#### Firewall Rules

Allow outbound connections to:
- Primary sensor domain (check Installation Keys page)
- Artifact Collection service domain (optional, check Installation Keys page)

### Permission Issues (macOS)

#### Required Permissions
- System Extensions
- Network Filter
- Full Disk Access

#### Verification

Launch RPHCP.app from /Applications to check permission status.

#### Re-granting Permissions

1. Remove existing permissions from System Preferences
2. Run `sudo ./lc_sensor -c` to uninstall
3. Run `sudo ./lc_sensor -i YOUR_KEY` to reinstall
4. Follow permission prompts

### Performance Issues

#### Symptoms
- High CPU usage
- High memory usage
- Endpoint slowdown

#### Resolution

**Adjust performance mode:**
```
set_performance_mode --mode low
```

**Available modes:**
- `low`: Minimal resource usage
- `normal`: Default balanced mode
- `high`: Maximum visibility, higher resource usage

**Check sensor version:**
Ensure running latest stable version for performance improvements.

**Review exfiltration rules:**
Excessive exfiltration can impact performance.

**Review FIM rules:**
Monitoring too many paths can increase resource usage.

### Installation Failures

#### Windows

**UAC Issues:**
- Run installer as Administrator
- Ensure digital signature is valid

**Service Installation Failure:**
- Check Windows Event Logs
- Verify sufficient permissions
- Ensure no conflicting security software

#### macOS

**Permission Denial:**
- Complete all permission prompts
- Grant Full Disk Access
- Allow System Extensions

**MDM Conflicts:**
- Check MDM policies
- Add extension to allow list

#### Linux

**Kernel Version:**
- Verify kernel 4.4+ for eBPF support
- Use `uname -r` to check

**Dependency Issues:**
- Ensure required libraries are available
- Check service manager compatibility

**Permission Issues:**
- Run installer as root/sudo
- Verify file permissions

### Chrome/Edge Extension Issues

**Connectivity Failures:**
1. Uninstall and reinstall extension
2. Check chrome://extensions/ console for errors
3. Verify installation key is correct
4. Check network connectivity to LimaCharlie domain

**Permission Issues:**
Ensure extension has required permissions granted.

---

## Best Practices

### Installation Key Strategy

1. **Create multiple keys** for different use cases
2. **Use descriptive names** for easy identification
3. **Apply tags automatically** via installation keys
4. **Document key usage** for team reference

**Example Key Structure:**
- `prod-servers`: Production servers with tags `production`, `server`
- `prod-workstations`: Production workstations with tags `production`, `workstation`
- `dev-servers`: Development servers with tags `development`, `server`
- `vip-users`: Executive machines with tags `vip`, `workstation`

### Tagging Strategy

1. **Multi-dimensional tagging**: Use multiple tag categories
   - Environment: production, staging, development
   - Type: server, workstation, laptop
   - Department: sales, finance, engineering
   - Importance: vip, critical, standard

2. **Consistent naming**: Use consistent tag naming conventions
   - Use lowercase
   - Use hyphens for multi-word tags
   - Be descriptive but concise

3. **Document tags**: Maintain documentation of tag meanings and usage

### Deployment Best Practices

1. **Test deployments**: Always test on representative systems first
2. **Staged rollout**: Deploy in phases (dev → staging → production)
3. **Monitor initially**: Watch for issues during initial deployment
4. **Use automation**: Leverage MDM, package managers, deployment tools
5. **Document process**: Maintain runbooks for installation procedures

### Version Management

1. **Stay current**: Keep sensors updated for latest features and fixes
2. **Test before org-wide updates**: Use `lc:latest` tag on test systems
3. **Maintenance windows**: Schedule updates during low-activity periods
4. **Monitor after updates**: Watch for issues post-update
5. **Rollback plan**: Have plan to revert if issues arise

### Security Best Practices

1. **Protect installation keys**: Treat as sensitive credentials
2. **Rotate keys periodically**: Create new keys, deprecate old ones
3. **Monitor sensor inventory**: Track which sensors are deployed
4. **Network segmentation**: Consider sensor network requirements in network design
5. **Principle of least privilege**: Use appropriate permissions for sensor operations

### Performance Optimization

1. **Right-size exfiltration**: Only exfiltrate necessary data
2. **Targeted FIM**: Monitor only critical paths
3. **Performance modes**: Adjust based on endpoint role and resources
4. **Regular cleanup**: Remove sensors from decommissioned endpoints

### Operational Best Practices

1. **Alert on sensor loss**: Detect sensors that stop reporting
2. **Regular health checks**: Monitor sensor connectivity and health
3. **Inventory management**: Maintain accurate sensor inventory
4. **Incident response preparation**: Have runbooks for common sensor operations
5. **Team training**: Ensure team knows how to use sensor commands effectively

### Sleeper Mode Deployments

For incident response or pre-deployment scenarios:

1. Create organization with quota ≥ 3 (enables billing)
2. Create installation key with `lc:sleeper` tag
3. Deploy sensors across fleet
4. Billing: $0.10 per sensor per 30 days (100 sensors = $10/month)
5. When needed, apply `lc:usage` tag or remove `lc:sleeper` tag
6. Return to sleeper mode when incident response complete

**Benefits:**
- Pre-deployed agents ready for rapid activation
- Minimal cost during dormant period
- Competitive SLAs for incident response
- No reboot required to activate

### High-Scale Deployments

For deployments with thousands of sensors:

1. **Use automation**: Leverage API/SDK for programmatic management
2. **Batch operations**: Group sensors for bulk operations
3. **Selector expressions**: Use advanced selectors for precise targeting
4. **Tag hierarchy**: Implement comprehensive tagging structure
5. **Monitoring dashboards**: Create dashboards for fleet health
6. **Capacity planning**: Monitor event rates and adjust accordingly

---

## Additional Resources

### Documentation References
- Installation Keys: `/limacharlie/doc/Sensors/installation-keys.md`
- Sensor Tags: `/limacharlie/doc/Sensors/sensor-tags.md`
- Sensor Commands: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Commands/reference-endpoint-agent-commands.md`
- Sensor Connectivity: `/limacharlie/doc/Sensors/sensor-connectivity.md`
- Versioning: `/limacharlie/doc/Sensors/Endpoint_Agent/endpoint-agent-versioning-and-upgrades.md`
- Uninstallation: `/limacharlie/doc/Sensors/Endpoint_Agent/endpoint-agent-uninstallation.md`
- Sleeper Mode: `/limacharlie/doc/Sensors/Endpoint_Agent/sleeper.md`

### Platform-Specific Guides
- Windows: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/Windows_Agent_Installation/`
- macOS: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/macOS_Agent_Installation/`
- Linux: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/linux-agent-installation.md`
- Docker: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/docker-agent-installation.md`
- Chrome: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/chrome-agent-installation.md`

### API/SDK Resources
- REST API: https://api.limacharlie.io/static/swagger/
- Python SDK: https://github.com/refractionPOINT/python-limacharlie
- Go SDK: https://github.com/refractionPOINT/go-limacharlie

### Support
- Email: answers@limacharlie.io
- Community Slack: https://limacharlie.io/slack
- Documentation: https://doc.limacharlie.io

---

## Quick Reference

### Common Commands

```bash
# List processes
os_processes

# Get file
file_get --path "/path/to/file"

# Kill process
os_kill_process --pid 1234

# Network isolate
segregate_network

# Restore network
rejoin_network

# YARA scan
yara_scan --path "/path" --rule-name "signatures"

# Uninstall sensor
uninstall --is-confirmed

# Get system info
os_version
```

### Sensor Selector Examples

```
# All Windows servers
plat == windows and server in tags

# All isolated sensors
isolated == true

# All sensors in production
production in tags

# All sensors not seen in 24 hours
alive < {timestamp_24h_ago}

# All VIP workstations
vip in tags and workstation in tags
```

### System Tags

```
lc:latest       - Use latest version
lc:stable       - Use stable version
lc:experimental - Use experimental version
lc:no_kernel    - Disable kernel component
lc:debug        - Use debug version
lc:limit-update - Only update at startup
lc:sleeper      - Enter sleeper mode
lc:usage        - Usage-based billing
```

### Installation Key Planning Template

| Key Name | Description | Tags | Use Case |
|----------|-------------|------|----------|
| prod-servers | Production servers | production, server | Server deployments |
| prod-workstations | Production workstations | production, workstation | Employee machines |
| dev-env | Development environment | development | Dev systems |
| vip-users | Executive machines | vip, workstation | C-suite devices |
| staging | Staging environment | staging | Pre-prod testing |

---

## When to Use This Skill

Use the sensor-manager skill when users ask about:

- Installing or deploying LimaCharlie sensors
- Sensor commands and capabilities
- Managing sensors (listing, filtering, tagging)
- Troubleshooting sensor issues
- Sensor versioning and updates
- Network isolation
- Platform-specific installation (Windows, macOS, Linux, Chrome, Edge)
- Enterprise deployment (MDM, Intune, custom installers)
- Installation keys and sensor enrollment
- Uninstalling sensors
- Performance optimization
- Sleeper mode deployments
- Containerized deployments (Docker, Kubernetes)
- Proxy configuration
- Permission issues (especially macOS)
- Sensor connectivity
- Sensor health monitoring

This skill provides comprehensive, authoritative guidance for all sensor-related operations in LimaCharlie.
