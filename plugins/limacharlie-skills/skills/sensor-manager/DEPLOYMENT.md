# Sensor Deployment Guide

Complete deployment instructions for LimaCharlie sensors across all supported platforms.

## Table of Contents

- [Windows Deployment](#windows-deployment)
- [macOS Deployment](#macos-deployment)
- [Linux Deployment](#linux-deployment)
- [Docker Deployment](#docker-deployment)
- [Chrome Extension Deployment](#chrome-extension-deployment)
- [Edge Extension Deployment](#edge-extension-deployment)
- [Container Clusters (Kubernetes)](#container-clusters-kubernetes)
- [VDI and Virtual Machine Templates](#vdi-and-virtual-machine-templates)

---

## Windows Deployment

### Standard Installation

#### Prerequisites
- Windows 7 or later (Server 2008 R2 or later for servers)
- Administrator privileges
- Internet connectivity to LimaCharlie cloud (port 443)

#### Download
```
https://downloads.limacharlie.io/sensor/windows/64
```

#### Installation Steps

1. **Download the installer** to the target system

2. **Run with installation key**:
```cmd
hcp_win_x64_release.exe -i YOUR_INSTALLATION_KEY
```

3. **Verify installation**:
   - Check Services panel for "LimaCharlie" service (running)
   - Check LimaCharlie web app Sensors page (sensor should appear within 1-2 minutes)

#### Unattended Installation

For silent installation without user prompts:

```cmd
hcp_win_x64_release.exe -i YOUR_INSTALLATION_KEY -q
```

The `-q` flag suppresses all UI elements and confirmation dialogs.

---

### Custom MSI Installer

Create a custom MSI installer for enterprise deployments with your own branding.

#### Why Use MSI?

- Professional appearance in Windows Apps & Features
- Easier deployment via enterprise tools (Intune, SCCM, GPO)
- White-label with your company branding
- Signed with your code signing certificate
- Better control over installation process

#### Prerequisites

- MSI wrapper application (e.g., [exemsi](https://www.exemsi.com/))
- Digital code signing certificate (optional but recommended)
- LimaCharlie sensor EXE file

#### Steps to Create MSI

1. **Download LimaCharlie sensor EXE**
   ```
   https://downloads.limacharlie.io/sensor/windows/64
   ```

2. **Launch your MSI wrapper tool** (e.g., exemsi)

3. **Configure MSI settings**:
   - **Product Name**: Your company name or "Security Agent"
   - **Manufacturer**: Your company name
   - **Version**: Match sensor version or use your own versioning
   - **Icon**: Your company icon (optional)
   - **Executable**: Select the LimaCharlie sensor EXE
   - **Install Arguments**: `-i YOUR_INSTALLATION_KEY`
   - **Uninstall Arguments**: `-c`

4. **Build the MSI package**

5. **Sign the MSI** (recommended):
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com installer.msi
   ```

6. **Test the MSI**:
   ```cmd
   msiexec /i installer.msi /qn
   ```

#### MSI Deployment via GPO

1. Copy MSI to network share accessible by all computers
2. Open Group Policy Management Console
3. Create or edit a GPO
4. Navigate to: Computer Configuration → Policies → Software Settings → Software Installation
5. Right-click → New → Package
6. Select your MSI file
7. Choose "Assigned" deployment method
8. Link GPO to appropriate Organizational Unit (OU)

---

### Enterprise Deployment via Microsoft Intune

Deploy LimaCharlie sensors across your organization using Microsoft Intune.

#### Preparation

1. **Create custom MSI** (see Custom MSI Installer section above)
2. **Prepare installation key** specific to this deployment
3. **Test MSI** on representative systems

#### Deployment Steps

1. **Sign in to Microsoft Endpoint Manager** admin center

2. **Navigate to Apps**:
   - Apps → All apps → Add

3. **Select app type**:
   - Choose "Line-of-business app"
   - Click "Select"

4. **Upload MSI**:
   - Click "Select app package file"
   - Upload your custom MSI
   - Click "OK"

5. **Configure app information**:
   - **Name**: LimaCharlie Security Agent (or your custom name)
   - **Description**: EDR sensor for endpoint security monitoring
   - **Publisher**: Your company name
   - **Category**: Security (optional)
   - Click "Next"

6. **Configure assignments**:
   - **Required**: Select groups for mandatory installation
   - **Available for enrolled devices**: Select groups for optional installation
   - Click "Next"

7. **Review and create**:
   - Review settings
   - Click "Create"

#### Monitor Deployment

- Navigate to: Apps → All apps → [Your App] → Device install status
- View installation status across enrolled devices
- Review any failures and troubleshoot

#### Troubleshooting Intune Deployment

**Installation fails:**
- Check device has internet connectivity
- Verify installation key is valid
- Review Intune logs: `C:\ProgramData\Microsoft\IntuneManagementExtension\Logs\`
- Check Windows Event Viewer for errors

**Sensor not appearing in LimaCharlie:**
- Verify network connectivity to LimaCharlie cloud (port 443)
- Check installation key is correct
- Verify no proxy/firewall blocking connection

---

### Deployment via SCCM/ConfigMgr

Deploy using Microsoft System Center Configuration Manager.

#### Preparation

1. Create custom MSI installer
2. Copy MSI to SCCM content library share

#### Deployment Steps

1. **Create Application**:
   - Software Library → Application Management → Applications
   - Right-click → Create Application

2. **Specify Application Information**:
   - Type: Windows Installer (*.msi file)
   - Select your MSI file
   - Follow wizard to completion

3. **Create Deployment**:
   - Right-click application → Deploy
   - Select target collection
   - Set deployment purpose (Required or Available)
   - Configure schedule

4. **Monitor Deployment**:
   - Monitoring → Deployments
   - View status and resolve issues

---

### Uninstallation

#### Via Sensor Command

From LimaCharlie web console:
```
uninstall --is-confirmed
```

For MSI installations:
```
uninstall --is-confirmed --msi
```

#### Via Windows Add/Remove Programs

1. Open Settings → Apps → Apps & features
2. Find "LimaCharlie" or your custom product name
3. Click Uninstall

#### Via Command Line

For standard installation:
```cmd
hcp_win_x64_release.exe -c
```

For MSI installation:
```cmd
msiexec /x {PRODUCT_CODE} /qn
```

Or:
```cmd
msiexec /x installer.msi /qn
```

---

## macOS Deployment

### macOS 10.15 Catalina to macOS 14 Sonoma

#### Prerequisites

- macOS 10.15 (Catalina) or later
- Administrator (sudo) access
- Internet connectivity to LimaCharlie cloud (port 443)

#### Download

**Intel Mac:**
```
https://downloads.limacharlie.io/sensor/mac/64
```

**Apple Silicon (M1/M2/M3):**
```
https://downloads.limacharlie.io/sensor/mac/arm64
```

#### Installation Steps

1. **Download the installer** to the target system

2. **Add execute permission**:
```bash
chmod +x lc_sensor
```

3. **Run installer with installation key**:
```bash
sudo ./lc_sensor -i YOUR_INSTALLATION_KEY
```

4. **Grant required permissions**:

   **System Extensions:**
   - A dialog will appear: "System Extension Blocked"
   - Click "Open Security Preferences"
   - Click "Allow" next to RPHCP extensions
   - Close System Preferences

   **Network Filter:**
   - A dialog will appear requesting network content filtering
   - Click "Allow"

   **Full Disk Access:**
   - Open System Preferences → Security & Privacy → Privacy
   - Select "Full Disk Access"
   - Click the lock to make changes (enter password)
   - Find and enable "RPHCP" in the list
   - If not present, click "+", navigate to /Applications/RPHCP.app, and add it

5. **Verify installation**:
```bash
sudo launchctl list | grep com.refractionpoint.rphcp
```

You should see the LimaCharlie service running.

**Important:** The RPHCP.app will be installed in /Applications and must remain there for proper operation. Do not move or delete this application.

#### Verification

- Check LimaCharlie web app Sensors page (sensor should appear within 1-2 minutes)
- Verify RPHCP.app is present in /Applications
- Launch RPHCP.app to view sensor status and permissions

---

### macOS 15 Sequoia and Newer

macOS 15 Sequoia introduces new security requirements and changes to system extensions.

#### Important Changes

- Enhanced privacy protections
- New permission requirements
- Updated system extension approval process

#### Installation

Follow the same installation steps as macOS 10.15-14, with these additional considerations:

1. **Additional Permission Prompts**: Sequoia may show additional permission requests. Approve all LimaCharlie/RPHCP-related requests.

2. **App Verification**: macOS may show "unidentified developer" warnings. Right-click RPHCP.app and select "Open" to bypass.

3. **Background Items**: May need to allow RPHCP in System Settings → General → Login Items & Extensions → Background Items

For the latest macOS Sequoia-specific instructions, see: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/macOS_Agent_Installation/`

---

### MDM Deployment for macOS

For large-scale macOS deployments, use Apple-approved Mobile Device Management (MDM) solutions.

#### Benefits of MDM Deployment

- Automated permission grants
- Pre-approved system extensions
- Organization-wide allow lists
- Reduced user interaction
- Centralized management

#### Supported MDM Solutions

- **Jamf Pro / Jamf Now**
- **Microsoft Intune**
- **VMware Workspace ONE**
- **Kandji**
- **Mosyle**
- Other Apple-approved MDM solutions

#### MDM Configuration Steps (General)

1. **Create Configuration Profile**:
   - System Extensions policy
   - Network Filter policy
   - Privacy Preferences Policy Control (PPPC)

2. **System Extensions Configuration**:
   - Team ID: `RPHCP_TEAM_ID` (check with LimaCharlie support)
   - Bundle IDs:
     - `com.refractionpoint.rphcp`
     - `com.refractionpoint.rphcp.network`

3. **Network Filter Configuration**:
   - Allow network content filtering for RPHCP

4. **Privacy Configuration (PPPC)**:
   - Grant Full Disk Access to `/Applications/RPHCP.app`
   - Grant other necessary permissions

5. **Deploy Sensor Package**:
   - Create PKG installer with installation key embedded
   - Deploy via MDM

#### Jamf Pro Specific Steps

1. **Upload Sensor PKG**:
   - Settings → Computer Management → Packages
   - Upload LimaCharlie sensor package

2. **Create Configuration Profile**:
   - Computers → Configuration Profiles → New
   - Add System Extensions payload
   - Add Privacy Preferences Policy Control payload
   - Add Network Filter payload

3. **Create Policy**:
   - Computers → Policies → New
   - Add sensor package to policy
   - Set trigger (enrollment, check-in, recurring)
   - Scope to target computers

4. **Deploy**:
   - Save policy
   - Sensors will deploy on next check-in

#### Microsoft Intune Specific Steps

1. **Create Configuration Profile**:
   - Devices → macOS → Configuration profiles → Create profile
   - Profile type: Templates → Extensions

2. **Configure System Extensions**:
   - Add RPHCP team ID and bundle IDs

3. **Create Privacy Profile**:
   - Create new profile
   - Add Privacy preferences for Full Disk Access

4. **Upload Sensor Package**:
   - Apps → macOS → Add → Line-of-business app
   - Upload sensor PKG file

5. **Assign Profiles and App**:
   - Assign configuration profiles to device groups
   - Assign sensor app to same groups

---

### Uninstallation (macOS)

#### Via Sensor Command

From LimaCharlie web console:
```
uninstall --is-confirmed
```

#### Manual Uninstallation

Run the uninstaller:
```bash
sudo ./lc_sensor -c
```

This removes:
- System extensions
- RPHCP.app from /Applications
- Launch daemon configuration
- All sensor components

---

## Linux Deployment

### System Requirements

- Linux kernel 4.4 or above (for eBPF support)
- Check kernel version: `uname -r`
- Supports all distributions including ARM and MIPS
- Root/sudo access required

---

### Debian/Ubuntu Package Installation

#### Download

**x86_64 (amd64):**
```
https://downloads.limacharlie.io/sensor/linux/deb64
```

**ARM64:**
```
https://downloads.limacharlie.io/sensor/linux/debarm64
```

#### Interactive Installation

Using dpkg:
```bash
sudo dpkg -i limacharlie.deb
```

Using apt:
```bash
sudo apt install ./limacharlie.deb
```

The installer will prompt for the installation key interactively.

#### Programmatic Installation with dpkg

For automated deployments without interactive prompts:

```bash
echo "limacharlie limacharlie/installation_key string YOUR_INSTALLATION_KEY" | sudo debconf-set-selections && sudo dpkg -i limacharlie.deb
```

#### Programmatic Installation with apt

```bash
echo "limacharlie limacharlie/installation_key string YOUR_INSTALLATION_KEY" | sudo debconf-set-selections && sudo apt install ./limacharlie.deb -y
```

#### Verification

Check service status:
```bash
sudo systemctl status limacharlie
```

Verify sensor appears in LimaCharlie web app within 1-2 minutes.

#### Uninstallation

Using dpkg:
```bash
sudo dpkg -r limacharlie
```

Using apt:
```bash
sudo apt remove limacharlie
```

---

### Custom Installation (Non-Debian Distributions)

For RHEL, CentOS, Fedora, Alpine, Arch, and other distributions.

#### Download

**x86_64:**
```bash
wget https://downloads.limacharlie.io/sensor/linux/64 -O /tmp/lc_sensor
```

**ARM64:**
```
https://downloads.limacharlie.io/sensor/linux/arm64
```

**Alpine (musl-based):**
```
https://downloads.limacharlie.io/sensor/linux/alpine64
```

**MIPS:**
```
https://downloads.limacharlie.io/sensor/linux/mips
```

#### Installation

1. **Add execute permission**:
```bash
chmod +x /tmp/lc_sensor
```

2. **Run installer with installation key**:
```bash
sudo /tmp/lc_sensor -d YOUR_INSTALLATION_KEY
```

#### Alternative: Use Environment Variable

**Option 1: Environment variable**
```bash
export LC_INSTALLATION_KEY=YOUR_INSTALLATION_KEY
sudo /tmp/lc_sensor -d -
```

**Option 2: Text file**
```bash
echo "YOUR_INSTALLATION_KEY" > lc_installation_key.txt
export LC_INSTALLATION_KEY=$(cat lc_installation_key.txt)
sudo /tmp/lc_sensor -d -
```

---

### Service Installation

Linux supports multiple service frameworks. Use the appropriate method for your distribution.

#### Automated Service Installation Script

LimaCharlie provides a helper script for service installation:

**Download:**
```bash
wget https://raw.githubusercontent.com/refractionPOINT/lce_doc/master/docs/lc_linux_installer.sh
chmod +x lc_linux_installer.sh
```

**Usage:**
```bash
sudo ./lc_linux_installer.sh <PATH_TO_LC_SENSOR> <YOUR_INSTALLATION_KEY>
```

**Example:**
```bash
sudo ./lc_linux_installer.sh /tmp/lc_sensor "YOUR_INSTALLATION_KEY"
```

This script:
- Installs the sensor binary to `/usr/local/bin/rphcp`
- Creates service configuration (systemd or init.d)
- Starts the service
- Enables automatic startup on boot

#### Manual systemd Installation

For systemd-based distributions (most modern Linux):

1. **Copy sensor binary**:
```bash
sudo cp lc_sensor /usr/local/bin/rphcp
sudo chmod +x /usr/local/bin/rphcp
```

2. **Create systemd service file** `/etc/systemd/system/limacharlie.service`:
```ini
[Unit]
Description=LimaCharlie Sensor
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/rphcp -d YOUR_INSTALLATION_KEY
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable limacharlie
sudo systemctl start limacharlie
```

4. **Verify service**:
```bash
sudo systemctl status limacharlie
```

#### Manual init.d Installation

For older distributions using SysV init:

1. **Copy sensor binary**:
```bash
sudo cp lc_sensor /usr/local/bin/rphcp
sudo chmod +x /usr/local/bin/rphcp
```

2. **Create init script** `/etc/init.d/limacharlie`:
```bash
#!/bin/bash
# chkconfig: 2345 90 10
# description: LimaCharlie Sensor

case "$1" in
  start)
    /usr/local/bin/rphcp -d YOUR_INSTALLATION_KEY &
    ;;
  stop)
    killall rphcp
    ;;
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac
exit 0
```

3. **Make executable and enable**:
```bash
sudo chmod +x /etc/init.d/limacharlie
sudo update-rc.d limacharlie defaults  # Debian/Ubuntu
# OR
sudo chkconfig --add limacharlie  # RHEL/CentOS
```

4. **Start service**:
```bash
sudo service limacharlie start
```

---

### Configuration Options

#### Disable Netlink

In rare configurations where Netlink causes issues:

```bash
export DISABLE_NETLINK=1
sudo ./lc_sensor -d YOUR_INSTALLATION_KEY
```

#### Proxy Configuration

Set the `LC_PROXY` environment variable:

```bash
export LC_PROXY=proxy.corp.com:8080
sudo -E ./lc_sensor -d YOUR_INSTALLATION_KEY
```

To make permanent, add to service configuration:
```ini
[Service]
Environment="LC_PROXY=proxy.corp.com:8080"
```

---

### Uninstallation (Linux)

#### Debian Package

```bash
sudo apt remove limacharlie
# OR
sudo dpkg -r limacharlie
```

#### Custom Installation with systemd

```bash
sudo systemctl stop limacharlie
sudo systemctl disable limacharlie
sudo rm /etc/systemd/system/limacharlie.service
sudo systemctl daemon-reload
sudo rm /usr/local/bin/rphcp
```

#### Custom Installation with init.d

```bash
sudo service limacharlie stop
sudo update-rc.d limacharlie remove  # Debian/Ubuntu
# OR
sudo chkconfig --del limacharlie  # RHEL/CentOS
sudo rm /etc/init.d/limacharlie
sudo rm /usr/local/bin/rphcp
```

#### Remote Uninstallation via Sensor Command

Execute from LimaCharlie console:
```bash
run --shell-command "service limacharlie stop; rm /usr/local/bin/rphcp; update-rc.d limacharlie remove -f; rm -rf /etc/init.d/limacharlie; rm /etc/hcp*"
```

---

## Docker Deployment

Deploy LimaCharlie sensor as a Docker container to monitor the host system.

### Host Visibility Requirements

For full host visibility, the container requires:

- **Privileged mode**: For host-level resource access
- **Host networking**: For network activity observation
- **Host PID mode**: For process tracking
- **Host-level directory mounts**:
  - Root filesystem (`/` → `/rootfs`)
  - Docker network namespaces (`/var/run/docker/netns` → `/netns`)
  - Kernel modules (`/lib/modules`)
  - Kernel debug symbols (`/sys/kernel/debug`, `/sys/kernel/btf`)

### Docker CLI Deployment

```bash
docker run -d \
  --name limacharlie-sensor \
  --privileged \
  --net=host \
  --pid=host \
  --restart=unless-stopped \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:ro \
  -v /sys/kernel/btf:/sys/kernel/btf:ro \
  -v /lib/modules:/lib/modules:ro \
  -e LC_INSTALLATION_KEY=YOUR_INSTALLATION_KEY \
  -e HOST_FS=/rootfs \
  -e NET_NS=/netns \
  refractionpoint/limacharlie_sensor:latest
```

### Docker Compose Deployment

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  lc-sensor:
    image: refractionpoint/limacharlie_sensor:latest
    container_name: limacharlie-sensor
    restart: unless-stopped
    network_mode: "host"
    pid: "host"
    privileged: true

    environment:
      - LC_INSTALLATION_KEY=YOUR_INSTALLATION_KEY
      - HOST_FS=/rootfs
      - NET_NS=/netns

    volumes:
      - /:/rootfs:ro
      - /var/run/docker/netns:/netns:ro
      - /sys/kernel/debug:/sys/kernel/debug:ro
      - /sys/kernel/btf:/sys/kernel/btf:ro
      - /lib/modules:/lib/modules:ro

    cap_add:
      - SYS_ADMIN

    deploy:
      resources:
        limits:
          cpus: "0.9"
          memory: "256M"
        reservations:
          cpus: "0.01"
          memory: "128M"
```

**Deploy:**
```bash
docker-compose up -d
```

**Verify:**
```bash
docker-compose ps
docker-compose logs lc-sensor
```

### Image Flavors

LimaCharlie provides multiple image variants:

- `refractionpoint/limacharlie_sensor:latest` - Default (CentOS Linux)
- `refractionpoint/limacharlie_sensor:alpine` - Alpine Linux (smaller size)
- `refractionpoint/limacharlie_sensor:centos` - CentOS Linux (explicit)

**Use Alpine for minimal size:**
```bash
docker run ... refractionpoint/limacharlie_sensor:alpine
```

### Environment Variables

- **`LC_INSTALLATION_KEY`** (required): Installation key for sensor enrollment
- **`HOST_FS`** (required): Path to host's root filesystem mount (typically `/rootfs`)
- **`NET_NS`** (required): Path to host's network namespace directory (typically `/netns`)
- **`LC_PROXY`** (optional): Proxy server (e.g., `proxy.corp.com:8080`)

### Resource Limits

Adjust resource limits based on your requirements:

```yaml
deploy:
  resources:
    limits:
      cpus: "1.0"      # Maximum CPU usage
      memory: "512M"   # Maximum memory
    reservations:
      cpus: "0.1"      # Minimum guaranteed CPU
      memory: "128M"   # Minimum guaranteed memory
```

### Verification

1. **Check container status**:
```bash
docker ps | grep limacharlie
```

2. **View logs**:
```bash
docker logs limacharlie-sensor
```

3. **Check LimaCharlie web app**: Sensor should appear within 1-2 minutes

### Uninstallation

**Docker CLI:**
```bash
docker stop limacharlie-sensor
docker rm limacharlie-sensor
```

**Docker Compose:**
```bash
docker-compose down
```

---

## Chrome Extension Deployment

The LimaCharlie Chrome Sensor is a browser extension providing visibility for browser activity.

### Manual Installation

1. **Get installation key**:
   - Navigate to LimaCharlie web app
   - Go to **Sensors > Installation Keys**
   - Copy the "Chrome Key" to clipboard

2. **Install extension**:
   - Visit: `https://downloads.limacharlie.io/sensor/chrome`
   - Or search Chrome Web Store for "LimaCharlie Sensor"
   - Click "Add to Chrome"

3. **Configure extension**:
   - A new tab will open automatically
   - Paste your installation key
   - Click "Save"

   **Alternative configuration:**
   - Navigate to `chrome://extensions/`
   - Find "LimaCharlie Sensor"
   - Click "Details"
   - Click "Extension options"
   - Enter installation key
   - Click "Save"

4. **Verify enrollment**:
   - Check LimaCharlie web app Sensors page
   - Sensor should appear within 1-2 minutes

### Enterprise Deployment (Managed Chrome)

For organization-wide deployment using Chrome Enterprise/Google Workspace.

#### Prerequisites

- Google Workspace or Chrome Enterprise enrollment
- Admin access to Google Admin Console

#### Deployment Steps

1. **Sign in to Google Admin Console**: admin.google.com

2. **Navigate to Chrome Management**:
   - Devices → Chrome → Apps & extensions

3. **Add Chrome extension**:
   - Click the "+" button (Add app or extension)
   - Search for "LimaCharlie Sensor" or enter extension ID
   - Click "Select"

4. **Configure installation key via Managed Storage**:
   - Select the LimaCharlie Sensor extension
   - Click "User Settings" or "Device Settings"
   - Add policy configuration:
   ```json
   {
     "installation_key": "YOUR_INSTALLATION_KEY"
   }
   ```

5. **Set installation policy**:
   - **Force install**: Extension installs automatically, users cannot remove
   - **Force install + pin**: Extension installs and is pinned to toolbar
   - **Normal install**: Available in Chrome Web Store for users

6. **Apply to organizational units**:
   - Select target OUs (organizational units)
   - Click "Save"

7. **Verify deployment**:
   - Check user devices
   - Verify sensors appear in LimaCharlie web app

### Troubleshooting

#### Extension not connecting

1. Try uninstalling and reinstalling the extension
2. Verify installation key is correct
3. Check network connectivity to LimaCharlie domain

#### Debug console access

1. Navigate to `chrome://extensions/`
2. Enable "Developer Mode" (top right toggle)
3. Find "LimaCharlie Sensor" entry
4. Click `background.html` or "Inspect views: service worker"
5. Check Console tab for errors
6. Take screenshot and send to LimaCharlie support with your Organization ID

---

## Edge Extension Deployment

Deployment process is similar to Chrome extension.

### Manual Installation

1. **Get installation key**:
   - Navigate to LimaCharlie web app
   - Go to **Sensors > Installation Keys**
   - Copy the "Edge Key" to clipboard

2. **Install extension**:
   - Visit Microsoft Edge Add-ons store
   - Search for "LimaCharlie Sensor"
   - Click "Get"

3. **Configure extension**:
   - Click extension icon
   - Enter installation key
   - Click "Save"

4. **Verify enrollment**:
   - Check LimaCharlie web app Sensors page
   - Sensor should appear within 1-2 minutes

### Enterprise Deployment

Deploy via Microsoft Endpoint Manager (Intune) or Microsoft 365 Admin Center.

For detailed Edge-specific deployment instructions, see: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/edge-agent-installation.md`

---

## Container Clusters (Kubernetes)

Deploy LimaCharlie sensors to Kubernetes clusters for container and host monitoring.

### Kubernetes DaemonSet Deployment

Deploy sensor as a DaemonSet to run on every node.

#### Create Secret

Store installation key as a Kubernetes secret:

```bash
kubectl create secret generic limacharlie-key \
  --from-literal=installation-key='YOUR_INSTALLATION_KEY'
```

#### Create DaemonSet

Create `limacharlie-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: limacharlie-sensor
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: limacharlie-sensor
  template:
    metadata:
      labels:
        app: limacharlie-sensor
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: sensor
        image: refractionpoint/limacharlie_sensor:latest
        securityContext:
          privileged: true
        env:
        - name: LC_INSTALLATION_KEY
          valueFrom:
            secretKeyRef:
              name: limacharlie-key
              key: installation-key
        - name: HOST_FS
          value: /rootfs
        - name: NET_NS
          value: /netns
        volumeMounts:
        - name: root
          mountPath: /rootfs
          readOnly: true
        - name: netns
          mountPath: /netns
          readOnly: true
        - name: kernel-debug
          mountPath: /sys/kernel/debug
          readOnly: true
        - name: kernel-btf
          mountPath: /sys/kernel/btf
          readOnly: true
        - name: lib-modules
          mountPath: /lib/modules
          readOnly: true
        resources:
          limits:
            cpu: "1"
            memory: 512Mi
          requests:
            cpu: "0.1"
            memory: 128Mi
      volumes:
      - name: root
        hostPath:
          path: /
      - name: netns
        hostPath:
          path: /var/run/docker/netns
      - name: kernel-debug
        hostPath:
          path: /sys/kernel/debug
      - name: kernel-btf
        hostPath:
          path: /sys/kernel/btf
      - name: lib-modules
        hostPath:
          path: /lib/modules
```

**Deploy:**
```bash
kubectl apply -f limacharlie-daemonset.yaml
```

**Verify:**
```bash
kubectl get daemonset -n kube-system limacharlie-sensor
kubectl get pods -n kube-system -l app=limacharlie-sensor
```

### Helm Chart Deployment

LimaCharlie provides Helm charts for easier deployment.

For detailed Kubernetes deployment instructions, see: `/limacharlie/doc/Sensors/container-clusters.md`

---

## VDI and Virtual Machine Templates

Special considerations when creating VM templates with LimaCharlie sensors installed.

### The Challenge

Each LimaCharlie sensor has a unique Sensor ID (SID). When creating VM templates:
- Cloning a VM with sensor installed duplicates the SID
- Multiple VMs with same SID cause conflicts
- Sensors may fail to enroll or show incorrect data

### Solutions

#### Option 1: Install Sensor AFTER Cloning (Recommended)

1. Create VM template WITHOUT LimaCharlie sensor
2. Clone VMs from template
3. Install sensor on each VM individually
4. Each VM gets unique SID

**Pros:**
- Simple and reliable
- No SID conflicts
- Each sensor properly identified

**Cons:**
- Manual installation step for each VM
- Requires post-deployment automation

#### Option 2: Use Sysprep (Windows) or Cloud-Init (Linux)

**Windows with Sysprep:**

1. Install sensor on template VM
2. Configure Sysprep to run cleanup script on first boot:
   - Delete sensor ID file: `C:\Windows\System32\drivers\hcp*`
   - Restart sensor service
3. Run Sysprep
4. Clone VM

**Linux with Cloud-Init:**

1. Install sensor on template VM
2. Configure cloud-init to run on first boot:
```bash
#!/bin/bash
rm -f /etc/hcp*
systemctl restart limacharlie
```
3. Clone VM

#### Option 3: Sleeper Mode Sensors

Deploy sensors in "sleeper mode" with minimal activity:

1. Create installation key with `lc:sleeper` tag
2. Install sensor on template VM using this key
3. Clone VMs
4. Sensors remain in low-activity sleeper mode
5. Activate specific sensors when needed by removing `lc:sleeper` tag or adding `lc:usage` tag

**Billing:** Sleeper mode costs $0.10 per sensor per 30 days (versus full usage-based pricing).

### Best Practices

1. **Document your approach**: Clearly document whether sensors are pre-installed or post-installed
2. **Test thoroughly**: Verify sensors enroll correctly after cloning
3. **Automation**: Use automation tools (Ansible, PowerShell, Terraform) to install sensors post-clone
4. **Tagging**: Use different installation keys/tags for template-based deployments
5. **Monitor enrollment**: Watch for duplicate SIDs or enrollment failures

### Resources

For detailed VDI/VM template instructions, see: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/vdi-virtual-machine-templates.md`

---

## General Deployment Best Practices

### Pre-Deployment

1. **Plan installation key strategy**: Create keys with appropriate tags for organization
2. **Test on representative systems**: Test across different OS versions and configurations
3. **Document deployment process**: Create runbooks for your team
4. **Prepare network**: Ensure port 443 access to LimaCharlie cloud
5. **Review proxy requirements**: Configure `LC_PROXY` if needed

### During Deployment

1. **Staged rollout**: Deploy to small groups first (dev → staging → production)
2. **Monitor enrollment**: Watch sensors appear in web app
3. **Verify connectivity**: Confirm sensors check in regularly
4. **Tag appropriately**: Apply tags during or immediately after enrollment
5. **Document issues**: Track and resolve any enrollment or connectivity issues

### Post-Deployment

1. **Verify telemetry**: Confirm sensors are sending expected events
2. **Configure D&R rules**: Set up detection and response rules
3. **Set up alerts**: Configure alerts for sensor offline/connectivity issues
4. **Monitor performance**: Watch for resource usage issues
5. **Plan updates**: Establish sensor versioning and update process

### Security Considerations

1. **Protect installation keys**: Treat as sensitive credentials, rotate periodically
2. **Use signed installers**: Sign MSI packages with your code signing certificate
3. **Implement least privilege**: Run deployments with appropriate, limited permissions
4. **Audit deployments**: Maintain records of sensor deployments
5. **Network segmentation**: Consider sensor network requirements in network design

---

## Additional Resources

### Documentation
- Platform-specific guides: `/limacharlie/doc/Sensors/Endpoint_Agent/Endpoint_Agent_Installation/`
- Installation keys: `/limacharlie/doc/Sensors/installation-keys.md`
- Sensor connectivity: `/limacharlie/doc/Sensors/sensor-connectivity.md`

### Related Guides
- [Command Reference](./REFERENCE.md): All sensor commands
- [Troubleshooting Guide](./TROUBLESHOOTING.md): Resolve deployment and connectivity issues
- [Main Skill Guide](./SKILL.md): Sensor management overview

### Support
- Email: answers@limacharlie.io
- Community Slack: https://limacharlie.io/slack
- Documentation: https://doc.limacharlie.io

---

## Return to Main Guide

[← Back to Sensor Manager](./SKILL.md)
