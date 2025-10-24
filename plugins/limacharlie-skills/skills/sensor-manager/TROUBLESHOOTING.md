# Sensor Troubleshooting Guide

Comprehensive troubleshooting guide for resolving LimaCharlie sensor issues.

## Table of Contents

- [Connectivity Issues](#connectivity-issues)
- [Non-Responding Sensors](#non-responding-sensors)
- [Installation Failures](#installation-failures)
- [Permission Issues (macOS)](#permission-issues-macos)
- [Performance Issues](#performance-issues)
- [Chrome/Edge Extension Issues](#chromeedge-extension-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Network Isolation Issues](#network-isolation-issues)
- [Update and Versioning Issues](#update-and-versioning-issues)

---

## Connectivity Issues

### Symptoms

- Sensor fails to enroll after installation
- Sensor appears offline in web console
- Intermittent disconnections
- Sensor shows "last seen" timestamp is old

### Network Requirements

**Required:**
- **Port**: 443 (TCP outbound)
- **Protocol**: HTTPS with TLS 1.2+
- **Domain**: Specific to your datacenter (check Installation Keys page)

**Optional (for artifact collection):**
- Artifact Collection service domain (check Installation Keys page)

### Diagnosis Steps

#### 1. Verify Network Connectivity

**Test basic connectivity:**
```bash
# Windows
ping downloads.limacharlie.io

# Linux/macOS
ping downloads.limacharlie.io
curl -v https://downloads.limacharlie.io
```

**Test sensor domain connectivity:**

Check your Installation Keys page in LimaCharlie web app for your specific sensor domain (e.g., `sensor-usw2.limacharlie.io`).

```bash
# Windows
Test-NetConnection sensor-usw2.limacharlie.io -Port 443

# Linux/macOS
telnet sensor-usw2.limacharlie.io 443
# OR
curl -v https://sensor-usw2.limacharlie.io
```

#### 2. Check Firewall Rules

**Verify outbound connections allowed to:**
- Primary sensor domain (from Installation Keys page)
- downloads.limacharlie.io (for updates)
- Artifact collection domain (optional, from Installation Keys page)

**Common firewall products:**
- Windows Defender Firewall
- iptables (Linux)
- Corporate firewalls (Palo Alto, Cisco ASA, etc.)

**Windows Defender Firewall check:**
```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*LimaCharlie*"}
```

**Linux iptables check:**
```bash
sudo iptables -L OUTPUT -v -n | grep 443
```

#### 3. Verify Sensor Service Status

**Windows:**
```powershell
Get-Service | Where-Object {$_.DisplayName -like "*LimaCharlie*"}
# OR
sc query rphcp
```

**macOS:**
```bash
sudo launchctl list | grep com.refractionpoint.rphcp
```

**Linux:**
```bash
# systemd
sudo systemctl status limacharlie

# init.d
sudo service limacharlie status
```

### Solutions

#### Configure Proxy Support

If your environment requires proxy:

**Set environment variable:**

**Windows (persistent):**
```powershell
[System.Environment]::SetEnvironmentVariable('LC_PROXY', 'proxy.corp.com:8080', [System.EnvironmentVariableTarget]::Machine)
Restart-Service rphcp
```

**Windows (auto-detection):**
```powershell
[System.Environment]::SetEnvironmentVariable('LC_PROXY', '-', [System.EnvironmentVariableTarget]::Machine)
Restart-Service rphcp
```

**Linux (systemd):**

Edit `/etc/systemd/system/limacharlie.service`:
```ini
[Service]
Environment="LC_PROXY=proxy.corp.com:8080"
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart limacharlie
```

**macOS:**

Edit launch daemon plist:
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>LC_PROXY</key>
    <string>proxy.corp.com:8080</string>
</dict>
```

#### Configure Firewall Rules

**Windows Defender Firewall:**
```powershell
New-NetFirewallRule -DisplayName "LimaCharlie Sensor" -Direction Outbound -Program "C:\Program Files\rphcp\rphcp.exe" -Action Allow
```

**Linux iptables:**
```bash
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

#### Restart Sensor Service

**Windows:**
```powershell
Restart-Service rphcp
```

**macOS:**
```bash
sudo launchctl unload /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl load /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
```

**Linux:**
```bash
sudo systemctl restart limacharlie
# OR
sudo service limacharlie restart
```

#### Reinstall Sensor

If connectivity issues persist after all troubleshooting:

1. Uninstall sensor (see [DEPLOYMENT.md](./DEPLOYMENT.md))
2. Verify network connectivity before reinstalling
3. Reinstall sensor with fresh installation key
4. Monitor enrollment in web console

---

## Non-Responding Sensors

### Symptoms

- Sensor shows as offline in web console
- No telemetry data being received
- Commands sent to sensor timeout or fail
- "Last seen" timestamp is hours or days old

### Detection Method

Create a scheduled Detection & Response rule to automatically detect non-responding sensors:

```python
import limacharlie
import time

SENSOR_SELECTOR = "plat == windows and `server` in tags"
DATA_WITHIN = 10 * 60 * 1000  # 10 minutes in milliseconds

def playbook(sdk: limacharlie.Limacharlie, data: dict) -> dict | None:
    relevant_sensors = sdk.sensors(selector=SENSOR_SELECTOR)
    stopped_sensors = []

    for sensor in relevant_sensors:
        data_overview = sensor.getHistoricOverview(
            int(time.time() - DATA_WITHIN / 1000),
            int(time.time())
        )
        after = int(time.time() * 1000) - DATA_WITHIN

        has_recent_data = False
        for timestamp in data_overview:
            if timestamp > after:
                has_recent_data = True
                break

        if not has_recent_data:
            stopped_sensors.append(sensor)

    if stopped_sensors:
        return {
            "detection": {
                "stopped_sensors": [s.sid for s in stopped_sensors],
                "sensor_count": len(stopped_sensors)
            }
        }
    return None
```

### Common Causes

1. **Endpoint offline**: Machine is powered off, sleeping, or disconnected from network
2. **Network issues**: Firewall blocking traffic, proxy authentication required
3. **Sensor service stopped**: Service crashed or was stopped manually
4. **Resource constraints**: Endpoint running out of memory or CPU
5. **Sensor uninstalled**: Agent was removed from endpoint
6. **Certificate issues**: SSL/TLS certificate validation failing
7. **Clock skew**: System time significantly out of sync

### Diagnosis Steps

#### 1. Verify Endpoint Status

**Check if endpoint is online:**
```bash
# Ping the endpoint
ping hostname.domain.com

# Windows
Test-Connection hostname.domain.com

# Try remote access (RDP, SSH, etc.)
```

#### 2. Check Service Status

**Windows (locally):**
```powershell
Get-Service rphcp
Get-Process rphcp -ErrorAction SilentlyContinue
```

**Windows (remotely via WMI):**
```powershell
Get-Service -ComputerName hostname rphcp
```

**macOS:**
```bash
sudo launchctl list | grep com.refractionpoint.rphcp
ps aux | grep rphcp
```

**Linux:**
```bash
sudo systemctl status limacharlie
ps aux | grep rphcp
```

#### 3. Check Logs

**Windows:**
- Check Windows Event Viewer → Application logs
- Look for LimaCharlie or RPHCP entries
- Check for errors or crashes

**macOS:**
```bash
log show --predicate 'process == "rphcp"' --last 1h
# OR
tail -f /var/log/system.log | grep rphcp
```

**Linux:**
```bash
# systemd
sudo journalctl -u limacharlie -n 100
sudo journalctl -u limacharlie --since "1 hour ago"

# syslog
tail -f /var/log/syslog | grep rphcp
```

#### 4. Check System Resources

**Windows:**
```powershell
Get-Counter '\Memory\Available MBytes'
Get-Counter '\Processor(_Total)\% Processor Time'
```

**macOS/Linux:**
```bash
top -l 1 | head -n 10
free -h
df -h
```

#### 5. Verify System Time

Clock skew can cause SSL/TLS issues:

**Windows:**
```powershell
w32tm /query /status
```

**macOS/Linux:**
```bash
date
timedatectl  # systemd systems
```

### Solutions

#### Restart Sensor Service

**Windows:**
```powershell
Restart-Service rphcp
```

**macOS:**
```bash
sudo launchctl kickstart -k system/com.refractionpoint.rphcp
```

**Linux:**
```bash
sudo systemctl restart limacharlie
```

#### Address Resource Constraints

If system is low on resources:

1. **Free up memory**: Close unnecessary applications
2. **Free up disk space**: Clean temporary files
3. **Reduce sensor resource usage**:
   ```
   set_performance_mode --mode low
   ```

#### Sync System Time

**Windows:**
```powershell
w32tm /resync /force
```

**macOS:**
```bash
sudo sntp -sS time.apple.com
```

**Linux:**
```bash
sudo ntpdate -s time.nist.gov
# OR (systemd)
sudo timedatectl set-ntp true
```

#### Reinstall Sensor

If service is missing or corrupted:

1. Uninstall sensor
2. Reboot endpoint
3. Reinstall sensor
4. Verify enrollment

---

## Installation Failures

### Windows Installation Failures

#### Symptoms
- Installer exits with error code
- Service fails to install
- Installation completes but sensor doesn't appear in web console

#### Common Causes and Solutions

**1. Insufficient Permissions**

**Error:** "Access denied" or "Administrator privileges required"

**Solution:**
- Right-click installer → "Run as Administrator"
- Or run from elevated command prompt:
  ```cmd
  runas /user:Administrator "hcp_win_x64_release.exe -i YOUR_KEY"
  ```

**2. Antivirus/EDR Interference**

**Error:** Installer blocked, files quarantined, or service fails to start

**Solution:**
- Temporarily disable antivirus/EDR
- Add LimaCharlie to exclusion list:
  - `C:\Program Files\rphcp\`
  - Process: `rphcp.exe`
- Reinstall sensor
- Re-enable antivirus/EDR

**3. Conflicting Security Software**

**Error:** Service fails to start, driver installation fails

**Solution:**
- Check for conflicts with other EDR/monitoring tools
- Uninstall conflicting software or install LimaCharlie first
- Some products that may conflict:
  - Other EDR solutions
  - System monitoring tools
  - Behavioral analysis tools

**4. Invalid Installation Key**

**Error:** "Invalid installation key" or "Authentication failed"

**Solution:**
- Verify installation key is correct (copy/paste carefully)
- Check key hasn't been disabled in LimaCharlie web console
- Generate new installation key and retry

**5. Network Issues During Installation**

**Error:** "Connection timeout" or "Unable to reach server"

**Solution:**
- Verify internet connectivity
- Check firewall allows outbound HTTPS (port 443)
- Configure proxy if needed (set `LC_PROXY` environment variable before installation)
- Verify system time is correct

**6. Service Installation Fails**

**Error:** "Service installation failed" or "Service failed to start"

**Check Windows Event Logs:**
```powershell
Get-EventLog -LogName System -Newest 50 | Where-Object {$_.Source -like "*rphcp*"}
Get-EventLog -LogName Application -Newest 50 | Where-Object {$_.Source -like "*LimaCharlie*"}
```

**Solution:**
- Ensure no other service is using the same name
- Check service dependencies are met
- Manually register service:
  ```cmd
  sc create rphcp binPath= "C:\Program Files\rphcp\rphcp.exe -d YOUR_KEY" start= auto
  sc start rphcp
  ```

---

### macOS Installation Failures

#### Symptoms
- Installation completes but sensor doesn't appear
- Permission prompts don't appear
- System extensions blocked

#### Common Causes and Solutions

**1. Permissions Not Granted**

**Error:** Sensor appears but doesn't send telemetry

**Solution:**
Grant all required permissions:

**System Extensions:**
- System Preferences → Security & Privacy → General
- Click "Allow" for RPHCP extensions

**Network Filter:**
- Approve network filter extension when prompted

**Full Disk Access:**
- System Preferences → Security & Privacy → Privacy → Full Disk Access
- Add RPHCP.app (click "+", navigate to /Applications/RPHCP.app)
- Ensure checkbox is enabled

**2. RPHCP.app Moved or Deleted**

**Error:** "RPHCP.app not found" or sensor stops working

**Solution:**
- RPHCP.app MUST remain in /Applications
- If moved or deleted, reinstall sensor:
  ```bash
  sudo ./lc_sensor -c  # Uninstall
  sudo ./lc_sensor -i YOUR_KEY  # Reinstall
  ```

**3. System Extension Approval Issues**

**Error:** "System extension blocked" persists after clicking "Allow"

**Solution for macOS 10.15-14:**
1. Open Terminal
2. Check system extension status:
   ```bash
   systemextensionsctl list
   ```
3. If RPHCP extensions show as "waiting for approval":
   ```bash
   sudo systemextensionsctl uninstall com.refractionpoint.rphcp
   sudo ./lc_sensor -c
   sudo ./lc_sensor -i YOUR_KEY
   ```
4. Grant permissions immediately when prompted

**Solution for macOS 15 Sequoia:**
- May need to allow in Background Items
- System Settings → General → Login Items & Extensions → Background Items
- Enable RPHCP

**4. SIP (System Integrity Protection) Issues**

**Error:** Installation fails with permission errors despite sudo

**Check SIP status:**
```bash
csrutil status
```

**Solution:**
- SIP should remain enabled for security
- LimaCharlie sensor is compatible with SIP
- If issues persist, try Safe Mode installation:
  1. Boot into Safe Mode (hold Shift during startup)
  2. Install sensor
  3. Reboot normally

**5. MDM Conflicts**

**Error:** Extensions blocked by MDM policy

**Solution:**
- Contact your IT administrator
- Add RPHCP to MDM allow list:
  - Team ID: [RPHCP_TEAM_ID]
  - Bundle IDs:
    - com.refractionpoint.rphcp
    - com.refractionpoint.rphcp.network

**6. Installation Key Issues**

**Error:** "Invalid installation key" or sensor doesn't enroll

**Solution:**
- Verify installation key is correct
- Ensure no extra spaces or line breaks in key
- Test with new installation key
- Check Organization ID is correct

---

### Linux Installation Failures

#### Symptoms
- Package installation fails
- Service fails to start
- Sensor doesn't appear in web console

#### Common Causes and Solutions

**1. Kernel Version Too Old**

**Error:** "Kernel version not supported" or "eBPF not available"

**Check kernel version:**
```bash
uname -r
```

**Required:** Linux kernel 4.4 or above

**Solution:**
- Update kernel to 4.4 or later:
  ```bash
  # Debian/Ubuntu
  sudo apt update
  sudo apt upgrade linux-image-generic

  # RHEL/CentOS
  sudo yum update kernel
  ```
- Reboot to new kernel

**2. Missing Dependencies**

**Error:** Package installation fails with dependency errors

**Solution:**

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install -f  # Fix broken dependencies
sudo apt install ./limacharlie.deb
```

**RHEL/CentOS:**
```bash
sudo yum install epel-release
sudo yum install <missing_package>
```

**3. Permission Issues**

**Error:** "Permission denied" during installation

**Solution:**
- Ensure running as root or with sudo
- Check file permissions on installer
- Verify SELinux isn't blocking (RHEL/CentOS):
  ```bash
  sudo setenforce 0  # Temporarily disable
  # Install sensor
  sudo setenforce 1  # Re-enable
  ```

**4. Service Manager Issues**

**Error:** Service fails to register or start

**For systemd systems:**
```bash
# Check systemd status
sudo systemctl status

# Reload systemd
sudo systemctl daemon-reload

# Try starting manually
sudo systemctl start limacharlie
sudo systemctl status limacharlie
```

**For init.d systems:**
```bash
# Check init script
ls -la /etc/init.d/limacharlie

# Make executable
sudo chmod +x /etc/init.d/limacharlie

# Start service
sudo /etc/init.d/limacharlie start
```

**5. Network/Firewall Issues**

**Error:** Sensor installs but doesn't connect

**Solution:**
- Check iptables rules:
  ```bash
  sudo iptables -L -n | grep 443
  ```
- Allow outbound HTTPS:
  ```bash
  sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
  sudo iptables-save > /etc/iptables/rules.v4
  ```
- Check SELinux (RHEL/CentOS):
  ```bash
  sudo setenforce 0  # Temporarily disable for testing
  # If sensor connects, configure SELinux policy properly
  sudo setenforce 1
  ```

**6. Netlink Issues**

**Error:** Sensor starts but crashes or fails to collect network data

**Solution:**
Disable Netlink if it's causing issues:
```bash
export DISABLE_NETLINK=1
sudo -E ./lc_sensor -d YOUR_KEY
```

To make permanent, add to service configuration:
```ini
[Service]
Environment="DISABLE_NETLINK=1"
```

---

## Permission Issues (macOS)

### Required Permissions

LimaCharlie sensor on macOS requires three types of permissions:

1. **System Extensions**: Allow RPHCP kernel extensions
2. **Network Filter**: Allow network content filtering
3. **Full Disk Access**: Allow reading files across the system

### Verification

**Launch RPHCP.app** from /Applications to check permission status:
- Green checkmarks = Permission granted
- Red X = Permission missing or denied

### Re-granting Permissions

If permissions are missing or revoked:

#### Complete Re-installation

1. **Uninstall sensor**:
```bash
sudo ./lc_sensor -c
```

2. **Remove from System Preferences**:
   - System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Remove RPHCP if present

3. **Reboot** (recommended for clean state)

4. **Reinstall sensor**:
```bash
sudo ./lc_sensor -i YOUR_INSTALLATION_KEY
```

5. **Grant all permissions when prompted**

#### Individual Permission Fixes

**System Extensions:**
1. System Preferences → Security & Privacy → General
2. Look for message about RPHCP
3. Click "Allow"
4. If no message appears, extension may already be approved

**Full Disk Access:**
1. System Preferences → Security & Privacy → Privacy
2. Select "Full Disk Access"
3. Click lock to make changes
4. If RPHCP is listed but unchecked, enable it
5. If RPHCP is not listed:
   - Click "+"
   - Navigate to /Applications
   - Select RPHCP.app
   - Ensure checkbox is enabled

**Network Filter:**
- Usually granted automatically during installation
- If prompted, click "Allow"

### macOS 15 Sequoia Specific

**Background Items:**
- System Settings → General → Login Items & Extensions
- Select "Background Items"
- Enable RPHCP

**App Verification:**
- If "unidentified developer" warning appears:
  1. Right-click RPHCP.app
  2. Select "Open"
  3. Click "Open" in confirmation dialog

### MDM Environment

If in MDM-managed environment:

1. **Check MDM profiles**:
```bash
profiles list
profiles show -type configuration
```

2. **Contact IT administrator** to:
   - Add RPHCP to system extension allow list
   - Add RPHCP to Full Disk Access policy
   - Add RPHCP to network filter allow list

3. **Required Team ID and Bundle IDs**:
   - Team ID: [Check with LimaCharlie support]
   - Bundle IDs:
     - com.refractionpoint.rphcp
     - com.refractionpoint.rphcp.network

---

## Performance Issues

### Symptoms

- High CPU usage by sensor process
- High memory consumption
- Endpoint slowdown or lag
- Disk I/O bottlenecks

### Diagnosis

#### Check Resource Usage

**Windows:**
```powershell
Get-Process rphcp | Select-Object CPU,WS
# Or use Task Manager and find rphcp.exe
```

**macOS:**
```bash
top -pid $(pgrep rphcp)
# Or use Activity Monitor and search for rphcp
```

**Linux:**
```bash
top -p $(pgrep rphcp)
# OR
ps aux | grep rphcp
```

#### Identify Cause

**High resource usage can be caused by:**

1. **Excessive exfiltration rules**: Too many event types being collected
2. **Intensive FIM rules**: Monitoring too many paths or busy directories
3. **YARA scanning**: Active scans consuming CPU/disk
4. **High endpoint activity**: Legitimate high activity on busy servers
5. **Performance mode setting**: Sensor in "high" performance mode
6. **Memory leaks**: Rare, but possible in older sensor versions

### Solutions

#### 1. Adjust Performance Mode

Set sensor to lower performance mode:

```
set_performance_mode --mode low
```

**Performance modes:**
- `low`: Minimal resource usage, reduced telemetry
- `normal`: Balanced (default)
- `high`: Maximum visibility, higher resources

#### 2. Review and Optimize Exfiltration Rules

**List current rules:**
```
exfil_get
```

**Remove unnecessary rules:**
```
exfil_del --event "EVENT_TYPE"
```

**Best practices:**
- Only exfiltrate events you actively use
- Use path filters to narrow scope
- Avoid exfiltrating high-frequency events on busy systems (e.g., FILE_OPEN on file servers)

**Common high-volume events to be selective about:**
- `FILE_OPEN`
- `FILE_READ`
- `DNS_REQUEST` (on DNS servers)
- `NEW_TCP4_CONNECTION` (on busy web servers)

#### 3. Optimize FIM Rules

**List current FIM rules:**
```
fim_get
```

**Remove or narrow FIM monitoring:**
```
fim_del --path "/very/busy/directory"
```

**Best practices:**
- Monitor only critical paths
- Avoid monitoring temporary directories
- Use specific file patterns when possible
- Don't monitor entire root filesystem

#### 4. Manage YARA Scans

**Stop active scan if running:**
- Wait for scan to complete (check web console)
- YARA scans are CPU and disk intensive

**Schedule scans during off-hours:**
- Use scheduled D&R rules to trigger scans at night or during maintenance windows

#### 5. Update Sensor Version

Newer sensor versions often include performance improvements:

**Check current version:**
- View in LimaCharlie web console (Sensors page)

**Update sensor:**
1. Tag sensor with `lc:latest` (for testing)
2. Wait ~20 minutes for update
3. Monitor performance
4. If improved, update organization-wide

#### 6. Investigate Specific Issues

**Memory leaks (gradual memory growth):**
- Update to latest sensor version
- Restart sensor to free memory:
  ```
  restart
  ```

**Disk I/O issues:**
- Check if antivirus is scanning sensor files
- Add sensor to AV exclusions
- Verify disk health (not a failing drive)

**Network bandwidth:**
- If sensor is consuming significant bandwidth:
  - Review exfiltration rules
  - Check for file upload operations (artifact_get, file_get)
  - Consider network constraints

#### 7. Adjust System Resources

If endpoint is underpowered for workload:

**Short-term:**
- Close unnecessary applications
- Free up disk space
- Use performance mode "low"

**Long-term:**
- Upgrade system RAM
- Upgrade to SSD storage
- Consider if workload is appropriate for hardware

---

## Chrome/Edge Extension Issues

### Connectivity Failures

#### Symptoms
- Extension installed but sensor doesn't appear in web console
- Extension shows "disconnected" or "offline"
- No telemetry data being collected

#### Solutions

**1. Verify Installation Key**

- Click extension icon
- Verify installation key is correct
- Re-enter key and save
- Refresh browser

**2. Check Extension Permissions**

- Navigate to `chrome://extensions/` (Chrome) or `edge://extensions/` (Edge)
- Find "LimaCharlie Sensor"
- Ensure extension is enabled
- Check that all required permissions are granted

**3. Reinstall Extension**

1. Navigate to extensions page
2. Remove LimaCharlie Sensor extension
3. Close all browser windows
4. Reopen browser
5. Reinstall extension
6. Configure with installation key

**4. Clear Extension Storage**

- Right-click extension icon → Options
- Clear any cached data
- Re-enter installation key
- Restart browser

**5. Check Network Connectivity**

- Ensure browser has internet access
- Verify firewall isn't blocking extension
- Check corporate proxy settings if applicable

### Debug Console Access

For deeper troubleshooting:

#### Chrome

1. Navigate to `chrome://extensions/`
2. Enable "Developer Mode" (toggle in top right)
3. Find "LimaCharlie Sensor" entry
4. Click "Inspect views: background page" or "service worker"
5. Check Console tab for errors
6. Look for network errors, authentication failures, or JavaScript errors

#### Edge

1. Navigate to `edge://extensions/`
2. Enable "Developer mode" (toggle in left sidebar)
3. Find "LimaCharlie Sensor" entry
4. Click "background.html" or "Inspect"
5. Check Console tab for errors

### Common Error Messages

**"Authentication failed"**
- Installation key is incorrect or expired
- Re-enter correct key

**"Network error"**
- Browser cannot reach LimaCharlie cloud
- Check internet connectivity
- Check firewall/proxy settings

**"Permission denied"**
- Extension missing required permissions
- Reinstall extension and grant all permissions

**"Extension context invalidated"**
- Extension was updated or reloaded
- Refresh browser or restart

### Enterprise Deployment Issues

#### Managed Storage Not Working

**Symptoms:**
- Extension installed via enterprise policy but not connecting
- Sensors not appearing despite mass deployment

**Solutions:**

1. **Verify managed storage configuration**:
   ```json
   {
     "installation_key": "YOUR_ACTUAL_KEY_HERE"
   }
   ```
   Ensure key is correct and properly formatted (no extra quotes, spaces, or line breaks)

2. **Check policy application**:
   - Chrome: `chrome://policy/`
   - Edge: `edge://policy/`
   - Look for LimaCharlie Sensor extension policies

3. **Force policy refresh**:
   - Chrome: `chrome://policy/` → "Reload policies"
   - Edge: `edge://policy/` → "Reload policies"
   - Or restart browser

4. **Verify extension installation method**:
   - Ensure extension ID matches official LimaCharlie extension
   - Verify extension is force-installed (not just "available")

---

## Platform-Specific Issues

### Windows-Specific Issues

#### Service Won't Start

**Check service status:**
```powershell
Get-Service rphcp
```

**Check for errors:**
```powershell
Get-EventLog -LogName Application -Source "rphcp" -Newest 20
Get-EventLog -LogName System -Source "Service Control Manager" | Where-Object {$_.Message -like "*rphcp*"}
```

**Common causes:**
- Missing dependencies
- Corrupted installation
- Conflicting software

**Solutions:**
```powershell
# Try manual start
Start-Service rphcp

# If fails, check dependencies
sc qc rphcp

# Reinstall service
sc delete rphcp
# Then reinstall sensor
```

#### Driver Issues

**Error:** "Driver failed to load"

**Check driver status:**
```powershell
fltmc instances
fltmc filters
```

**Solution:**
```powershell
# Reload filter driver
fltmc unload rphcp
fltmc load rphcp
```

#### Windows Defender Conflicts

**Error:** Sensor installation blocked or quarantined

**Solution:**
```powershell
# Add exclusions
Add-MpPreference -ExclusionPath "C:\Program Files\rphcp"
Add-MpPreference -ExclusionProcess "rphcp.exe"
```

---

### macOS-Specific Issues

#### RPHCP.app Missing

**Error:** "RPHCP.app not found in /Applications"

**Solution:**
```bash
# Check if present but hidden
ls -la /Applications/ | grep RPHCP

# If missing, reinstall
sudo ./lc_sensor -c
sudo ./lc_sensor -i YOUR_KEY
```

#### Launch Daemon Won't Load

**Check daemon status:**
```bash
sudo launchctl list | grep rphcp
```

**View daemon configuration:**
```bash
cat /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
```

**Reload daemon:**
```bash
sudo launchctl unload /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
sudo launchctl load /Library/LaunchDaemons/com.refractionpoint.rphcp.plist
```

#### System Extension Removal Issues

**Error:** "Failed to remove system extension"

**Solution:**
```bash
# Force remove extensions
sudo systemextensionsctl list
sudo systemextensionsctl uninstall com.refractionpoint.rphcp

# Reboot may be required
sudo reboot
```

---

### Linux-Specific Issues

#### eBPF Not Available

**Error:** "eBPF not supported" or "Kernel too old"

**Check kernel:**
```bash
uname -r
```

**Solution:**
- Upgrade to kernel 4.4 or later
- For older kernels, LimaCharlie may have limited functionality

#### systemd Service Issues

**Service won't start:**
```bash
# Check status
sudo systemctl status limacharlie

# View logs
sudo journalctl -u limacharlie -n 50

# Check service file
cat /etc/systemd/system/limacharlie.service
```

**Fix permissions:**
```bash
sudo chmod 644 /etc/systemd/system/limacharlie.service
sudo systemctl daemon-reload
sudo systemctl restart limacharlie
```

#### SELinux Issues (RHEL/CentOS)

**Error:** "Permission denied" despite root access

**Check SELinux:**
```bash
getenforce
```

**Temporarily disable for testing:**
```bash
sudo setenforce 0
# Test sensor
sudo setenforce 1
```

**Proper solution - create SELinux policy:**
```bash
# Generate policy from audit logs
sudo ausearch -m avc -ts recent | audit2allow -M limacharlie_policy
sudo semodule -i limacharlie_policy.pp
```

---

## Network Isolation Issues

### Cannot Isolate Sensor

**Symptoms:**
- `segregate_network` command fails
- Error message: "Network isolation not supported"
- Sensor doesn't appear isolated after command

**Causes:**
1. **Older sensor version**: Update to latest version
2. **Platform limitation**: Some platforms don't support isolation
3. **Permissions issue**: Sensor lacks required privileges
4. **Kernel component disabled**: `lc:no_kernel` tag applied

**Solutions:**

**1. Verify platform support:**
- Windows: Supported
- macOS: Supported
- Linux: Supported (requires kernel >= 4.4)
- Chrome/Edge: Not supported

**2. Update sensor:**
```
# Apply latest version tag
# Via API or web console
```

**3. Verify kernel component:**
- Ensure `lc:no_kernel` tag is NOT applied to sensor
- Check sensor details in web console

**4. Check permissions:**
- Windows: Ensure driver loaded (`fltmc filters | findstr rphcp`)
- macOS: Ensure network filter extension approved
- Linux: Ensure running as root, eBPF available

### Cannot Rejoin Network

**Symptoms:**
- `rejoin_network` command fails or times out
- Endpoint remains isolated
- Cannot communicate with endpoint except via LimaCharlie

**Solutions:**

**1. Retry command:**
```
rejoin_network
```

**2. Restart sensor:**
```
restart
```
Sensor will rejoin network on restart.

**3. Physical access:**
If commands fail, physical access to endpoint may be required:

**Windows:**
```cmd
# Stop service
net stop rphcp
# Restart service
net start rphcp
```

**macOS/Linux:**
```bash
# Restart service
sudo systemctl restart limacharlie
# OR
sudo service limacharlie restart
```

**4. Last resort - uninstall:**
```
uninstall --is-confirmed
```
This will remove sensor and restore network.

---

## Update and Versioning Issues

### Sensor Not Updating

**Symptoms:**
- Sensor remains on old version after organization update
- `lc:latest` tag applied but version doesn't change
- Update pushed hours ago but sensor still on old version

**Causes:**
1. Sensor offline or not checking in
2. Update constrained by `lc:limit-update` tag
3. Network issues preventing update download
4. Insufficient disk space
5. Sensor version conflict

**Solutions:**

**1. Verify sensor is online:**
- Check "last seen" timestamp in web console
- Ensure sensor is checking in regularly

**2. Check for limiting tags:**
```
# Via web console: View sensor tags
# Look for: lc:limit-update
```
If present, sensor only updates on restart:
```
restart
```

**3. Verify network connectivity:**
- Ensure sensor can reach downloads.limacharlie.io
- Check firewall rules
- Verify proxy configuration if applicable

**4. Check disk space:**

**Windows:**
```powershell
Get-PSDrive C
```

**macOS/Linux:**
```bash
df -h
```

Ensure at least 100MB free for update download.

**5. Force update:**
```
restart
```
Restarting sensor will trigger update check.

**6. Verify organization update version:**
- Web console: Organization settings
- Ensure correct version selected for rollout

### Sensor Stuck on Experimental Version

**Symptoms:**
- Sensor on experimental version but should be stable
- Behavior unexpected or unstable

**Solution:**

**1. Remove experimental tag:**
- Web console: Select sensor → Edit tags
- Remove `lc:experimental` tag

**2. Apply stable tag:**
- Add `lc:stable` tag

**3. Restart sensor:**
```
restart
```

**4. Verify version after 20 minutes:**
- Check sensor version in web console
- Should now show stable version

### Rollback to Previous Version

**Symptoms:**
- New version causing issues
- Need to revert to previous stable version

**Solution:**

**1. Apply stable tag:**
- Remove `lc:latest` tag
- Add `lc:stable` tag

**2. Restart sensor:**
```
restart
```

**3. Contact support:**
- If stable version also problematic
- LimaCharlie support can help specify exact version
- Email: answers@limacharlie.io

---

## General Troubleshooting Tips

### Gathering Diagnostic Information

When contacting support, provide:

1. **Organization ID (OID)**: Found in web console
2. **Sensor ID (SID)**: From sensor details page
3. **Platform and version**: OS and sensor version
4. **Error messages**: Exact error text
5. **Screenshots**: Of errors or unexpected behavior
6. **Logs**:
   - Windows: Event Viewer logs
   - macOS: Console.app logs
   - Linux: journalctl output
7. **Timeline**: When issue started, what changed

### Best Practices

1. **Test in non-production first**: Try solutions on test systems
2. **One change at a time**: Make changes incrementally to identify cause
3. **Document changes**: Keep notes on troubleshooting steps
4. **Check known issues**: Review LimaCharlie status page and community Slack
5. **Escalate when stuck**: Don't spend excessive time - contact support

### Getting Help

**LimaCharlie Support:**
- Email: answers@limacharlie.io
- Community Slack: https://limacharlie.io/slack
- Documentation: https://doc.limacharlie.io

**Include in Support Requests:**
- Organization ID (OID)
- Sensor ID (SID) if specific sensor
- Platform and sensor version
- Detailed description of issue
- Steps to reproduce
- Troubleshooting already attempted
- Relevant logs or screenshots

---

## Additional Resources

### Related Guides
- [Deployment Guide](./DEPLOYMENT.md): Installation instructions
- [Command Reference](./REFERENCE.md): All sensor commands
- [Main Skill Guide](./SKILL.md): Sensor management overview

### Documentation
- Sensor connectivity: `/limacharlie/doc/Sensors/sensor-connectivity.md`
- Versioning and upgrades: `/limacharlie/doc/Sensors/Endpoint_Agent/endpoint-agent-versioning-and-upgrades.md`
- Platform-specific guides: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/`

---

## Return to Main Guide

[← Back to Sensor Manager](./SKILL.md)
