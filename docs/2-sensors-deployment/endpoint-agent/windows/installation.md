# Windows Agent Installation

This guide explains how to install the LimaCharlie Endpoint Detection and Response (EDR) sensor on Windows systems. The sensor gives visibility into your Windows endpoints for threat detection and response in real time.

## Supported Windows Versions

**Desktop:**

- Windows 7, 8, 8.1, 10, 11

**Server:**

- Windows Server 2008 R2, 2012, 2012 R2, 2016, 2019, 2022

**Architectures:**

- x64 (64-bit) - Most common
- x86 (32-bit) - Legacy systems
- ARM64 - Windows on ARM devices

## Prerequisites

Before you install the LimaCharlie sensor, make sure that you have:

1. **Administrator privileges** on the Windows system
2. **An Installation Key** from your LimaCharlie organization
3. **Network access** to LimaCharlie cloud services (outbound HTTPS on port 443)

## Getting Your Installation Key

You need an Installation Key to enroll your sensor with the LimaCharlie cloud. To get your key:

1. Log in to the [LimaCharlie web application](https://app.limacharlie.io)
2. Select your organization
3. Go to **Sensors** > **Installation Keys** in the left sidebar
4. Copy an existing key, or click **Create Installation Key** to make a new key
5. Keep this key ready. You need it during the installation

For more information about how to manage keys, see [Installation Keys](../../installation-keys.md).

> **Tip:** An installation key can have tags. When a sensor enrolls with a key that has tags, the cloud applies those tags to the sensor.

## Downloading the Sensor

Choose the correct download for your system architecture:

### Executable (EXE) Downloads

| Architecture | Download Link |
|--------------|---------------|
| 64-bit (x64) | [https://downloads.limacharlie.io/sensor/windows/64](https://downloads.limacharlie.io/sensor/windows/64) |
| 32-bit (x86) | [https://downloads.limacharlie.io/sensor/windows/32](https://downloads.limacharlie.io/sensor/windows/32) |
| ARM64 | [https://downloads.limacharlie.io/sensor/windows/arm64](https://downloads.limacharlie.io/sensor/windows/arm64) |

> **Note:** A native ARM64 build is available for Windows on ARM devices (sensor 4.33.26 or later). Earlier sensor versions ran under x64 emulation. Emulation is no longer necessary.

### MSI Installer Downloads

| Architecture | Download Link |
|--------------|---------------|
| 64-bit (x64) | [https://downloads.limacharlie.io/sensor/windows/msi64](https://downloads.limacharlie.io/sensor/windows/msi64) |
| 32-bit (x86) | [https://downloads.limacharlie.io/sensor/windows/msi32](https://downloads.limacharlie.io/sensor/windows/msi32) |
| ARM64 | [https://downloads.limacharlie.io/sensor/windows/msiarm64](https://downloads.limacharlie.io/sensor/windows/msiarm64) |

> **Note about downloaded filenames:** The downloaded file has a versioned name such as `hcp_win_x64_release_4.33.23.exe`. You can rename it to `rphcp.exe`, or use the original filename in commands.
>
> **How to find the architecture that you need**
>
> On Windows 10/11: Go to **Settings** > **System** > **About** and look at **System type**.
>
> On older Windows: Right-click **Computer** > **Properties** and check the **System type**.

## Command-Line Options

When you run the installer from the command line, you can use these options:

| Option | Description |
|--------|-------------|
| `-i <KEY>` | Install as a Windows service with the specified installation key |
| `-d <KEY>` | Run with installation key (temporary, no permanent installation) |
| `-r` | Uninstall the service |
| `-c` | Uninstall the service and delete identity files (clean uninstall) |
| `-V` | Show the sensor version |
| `-v` | Enable verbose logging output |
| `-H` | Check sensor health and installation |
| `-h` | Show the help message |

For the complete list of options, environment variables, and local files, see the [Agent CLI & Environment Reference](../cli-reference.md).

## Installation Methods

### Method 1: Executable (EXE) Installation

This method is recommended for the installation on individual systems.

**Step 1:** Download the appropriate EXE for your architecture (see download links above).

**Step 2:** Open **Command Prompt** or **PowerShell** as Administrator.

> To run as Administrator: Right-click Command Prompt or PowerShell and select **Run as administrator**.

**Step 3:** Go to the folder where you downloaded the installer:

```bash
cd C:\Users\YourUsername\Downloads
```

**Step 4:** Run the installer with your Installation Key:

```batch
rphcp.exe -i YOUR_INSTALLATION_KEY_GOES_HERE
```

Replace `YOUR_INSTALLATION_KEY_GOES_HERE` with the key that you copied from the LimaCharlie web application.

**Step 5:** Wait for the installation to complete. The output shows that the installation is successful and that the service started.

The sensor is now installed and runs as a Windows service. It starts automatically when Windows boots.

### Method 2: MSI Installation

MSI installers are best for enterprise deployment with tools such as Group Policy, SCCM, or Intune.

#### Interactive Installation

1. Download the correct MSI for your architecture
2. Double-click the MSI file to start the installer
3. Obey the installation prompts

> **Note:** The MSI installation asks you for the Installation Key. Make sure that you have it ready.

#### Silent Installation (Command Line)

For automated deployments, use this command in an elevated Command Prompt or PowerShell:

```batch
msiexec /i "path\to\installer.msi" /qn INSTALLATIONKEY="YOUR_INSTALLATION_KEY_GOES_HERE"
```

Example with a specific MSI:

```batch
msiexec /i "C:\Downloads\hcp_win_x64.msi" /qn INSTALLATIONKEY="YOUR_INSTALLATION_KEY_GOES_HERE"
```

Options explained:

- `/i` - Install the package
- `/qn` - Quiet mode with no user interface
- `INSTALLATIONKEY` - The LimaCharlie installation key for enrollment

### Method 3: PowerShell Script (Automated)

This script does the download and the installation automatically. It detects your system architecture and downloads the correct installer.

> **Note:** This script needs PowerShell 3.0 or later. Windows 7 and Server 2008 R2 include PowerShell 2.0 by default. On these systems, it is possible that you must first install [Windows Management Framework 3.0+](https://www.microsoft.com/en-us/download/details.aspx?id=34595).

Save this script as `Install-LimaCharlie.ps1`:

```powershell
#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Downloads and installs the LimaCharlie sensor.
.DESCRIPTION
    This script detects the system architecture, downloads the appropriate
    LimaCharlie sensor installer, and installs it as a Windows service.
.PARAMETER InstallationKey
    The LimaCharlie installation key for enrollment.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallationKey
)

# Determine system architecture using WMI for accurate detection
$CpuArch = (Get-CimInstance -ClassName Win32_Processor).Architecture
# Architecture values: 0 = x86, 9 = x64, 12 = ARM64
$Arch = switch ($CpuArch) {
    0  { "32" }
    9  { "64" }
    12 { "arm64" }
    default { if ([Environment]::Is64BitOperatingSystem) { "64" } else { "32" } }
}

Write-Host "Detected architecture: $Arch" -ForegroundColor Cyan

# Set download URL and local path
$InstallerUrl = "https://downloads.limacharlie.io/sensor/windows/$Arch"
$TempDownload = Join-Path $env:TEMP "lc_sensor_download.exe"
$InstallerPath = Join-Path $env:TEMP "rphcp.exe"

# Download the installer (filename from server varies, so we normalize it)
Write-Host "Downloading LimaCharlie sensor..." -ForegroundColor Cyan
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $InstallerUrl -OutFile $TempDownload -UseBasicParsing
    # Rename to consistent filename
    Move-Item -Path $TempDownload -Destination $InstallerPath -Force
    Write-Host "Download complete." -ForegroundColor Green
} catch {
    Write-Host "Error downloading installer: $_" -ForegroundColor Red
    Remove-Item $TempDownload -Force -ErrorAction SilentlyContinue
    exit 1
}

# Install the sensor
Write-Host "Installing LimaCharlie sensor..." -ForegroundColor Cyan
try {
    $process = Start-Process -FilePath $InstallerPath -ArgumentList "-i", $InstallationKey -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -eq 0) {
        Write-Host "Installation successful!" -ForegroundColor Green
    } else {
        Write-Host "Installation may have encountered issues. Exit code: $($process.ExitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error during installation: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
$service = Get-Service -Name "rphcpsvc" -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host "LimaCharlie sensor is installed and running." -ForegroundColor Green
} else {
    Write-Host "Warning: Service may not be running. Please check manually." -ForegroundColor Yellow
}

# Clean up
Remove-Item $InstallerPath -Force -ErrorAction SilentlyContinue
```

**To run the script:**

1. Open PowerShell as Administrator
2. If script execution is not yet allowed, allow it:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. Run the script with your Installation Key:

   ```powershell
   .\Install-LimaCharlie.ps1 -InstallationKey "YOUR_INSTALLATION_KEY_GOES_HERE"
   ```

## Verifying Installation

After the installation, check that the sensor runs correctly. Use any of these methods:

### Windows Services GUI

1. Press `Win + R`, type `services.msc`, and press Enter
2. Scroll down to find **LimaCharlie** in the list
3. Check that the **Status** is **Running** and the **Startup Type** is **Automatic**

### PowerShell

Run this command to check the service status:

```powershell
Get-Service rphcpsvc | Select-Object Name, Status, StartType
```

Expected output:

```text
Name     Status StartType
----     ------ ---------
rphcpsvc Running Automatic
```

### Command Prompt

Run this command:

```text
sc query rphcpsvc
```

Look for `STATE : 4  RUNNING` in the output.

### Verification Script

Save and run this PowerShell script to check the status:

```powershell
# Verify LimaCharlie installation
$service = Get-Service -Name "rphcpsvc" -ErrorAction SilentlyContinue
if ($null -eq $service) {
    Write-Host "LimaCharlie sensor is NOT installed." -ForegroundColor Red
} elseif ($service.Status -eq "Running") {
    Write-Host "LimaCharlie sensor is installed and running." -ForegroundColor Green
    Write-Host "  Service Name: $($service.Name)"
    Write-Host "  Display Name: $($service.DisplayName)"
    Write-Host "  Start Type:   $($service.StartType)"
} else {
    Write-Host "LimaCharlie sensor is installed but NOT running." -ForegroundColor Yellow
    Write-Host "  Current Status: $($service.Status)"
}
```python

### LimaCharlie Web Application

1. Log in to [app.limacharlie.io](https://app.limacharlie.io)
2. Go to **Sensors** in the left sidebar
3. The new sensor shows in the list after a few minutes

## Troubleshooting

### "Access Denied" Error

**Cause:** You must run the installer with Administrator privileges.

**Solution:** Right-click Command Prompt or PowerShell and select **Run as administrator**. Then run the installer.

### Architecture Mismatch Error

**Cause:** You used a 32-bit installer on a 64-bit system, or a 64-bit installer on a 32-bit system.

**Solution:** Download and use the correct installer for your system architecture. The sensor shows an error message about the mismatch.

### Antivirus Blocking Installation

**Cause:** Some antivirus software can flag the sensor installer.

**Solution:**
1. Disable your antivirus for the time of the installation, OR
2. Add an exclusion for `rphcp.exe` and `C:\Windows\System32\rphcp.exe`
3. If the problem continues, contact your antivirus vendor

### Firewall Blocking Connection

**Cause:** The sensor cannot reach LimaCharlie cloud services.

**Solution:** Allow outbound HTTPS traffic on port 443 to:
- `*.limacharlie.io`

### Installation Key Errors

**Cause:** The installation key is invalid, expired, or copied incorrectly.

**Solution:**
1. Check the key in the LimaCharlie web application
2. Make sure that you copied the full key with no extra spaces
3. Check that the key is not revoked and not expired

### Service Won't Start

**Cause:** Different problems, such as file permissions or the system configuration.

**Solution:**
1. Check Windows Event Viewer (Application and System logs) for errors
2. Make sure that the system meets the minimum requirements
3. Run the installer with the `-c` flag to clean up, then install again

## Uninstallation

### Using the Executable

Run the installer with the clean uninstall flag:

```

rphcp.exe -c

```text

This removes the service and deletes all identity files.

To uninstall but keep the identity files for a later installation:

```

rphcp.exe -r

```text

### Using the MSI

1. Open **Control Panel** > **Programs** > **Programs and Features**
2. Find **LimaCharlie** in the list
3. Click **Uninstall**

Or use the command line:

```

msiexec /x "path\to\installer.msi" /qn

```text

### Using LimaCharlie Console

You can uninstall the sensor remotely from the LimaCharlie web application:

1. Go to the sensor in the Sensors list
2. Open the **Console** tab
3. Run the command: `uninstall`

For MSI installations, use: `uninstall --msi`

For more uninstallation options, see [Endpoint Agent Uninstallation](../uninstallation.md).

## Next Steps

After the sensor is installed, you can:

- [Configure Detection & Response rules](../../../3-detection-response/index.md) to detect threats
- [Explore Sensor Commands](../../../8-reference/endpoint-commands.md) to interact with your endpoints
- [Build a Custom MSI](custom-msi.md) with your branding for enterprise deployment
- [Deploy via Microsoft Intune](../../enterprise-deployment/intune.md) for large-scale rollout
