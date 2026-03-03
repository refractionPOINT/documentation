# Service Upgrades

The LimaCharlie endpoint agent consists of two components that are versioned independently:

- **On-disk agent** — the service binary installed on the host. It handles core identity, cryptography, and transport. This component rarely changes and is what gets replaced during a service upgrade.
- **Over-the-air core** — the main functional component that delivers detection and response capabilities. It is downloaded from the LimaCharlie cloud and updated frequently. See [Versioning & Upgrades](versioning-upgrades.md) for managing over-the-air updates.

The procedures on this page upgrade the **on-disk agent** only. This is useful when a new service binary is needed for bug fixes, platform compatibility, or to gain support for new on-disk features. Over-the-air core updates happen separately through the LimaCharlie cloud and do not require a service upgrade.

The upgrade process stops the running service, replaces the binary with the new version, and restarts the service. If the new version fails to start, an automatic rollback to the previous version occurs.

!!! note "Prerequisites" - The command must be run with **root** (Linux/macOS) or **Administrator** (Windows) privileges. - No installation key is required for upgrades.

## Upgrade to Latest Version

=== "Linux / macOS"

    ```bash
    curl -L --proto '=https' --tlsv1.2 -sSf https://downloads.limacharlie.io/sensor/posix/install | sudo sh -s -- --upgrade
    ```

=== "Windows (PowerShell)"

    ```powershell
    irm https://downloads.limacharlie.io/sensor/windows/install.ps1 | iex; Upgrade-LCSensor
    ```

## Upgrade or Downgrade to a Specific Version

The `--version` flag can be used to move to any available sensor version, whether newer or older than the currently installed version. This is useful for rolling back to a known-good version or pinning to a specific release.

!!! note
The `--version` flag requires sensor version **4.33.28 or later**.

=== "Linux / macOS"

    ```bash
    curl -L --proto '=https' --tlsv1.2 -sSf https://downloads.limacharlie.io/sensor/posix/install | sudo sh -s -- --upgrade --version 4.33.28
    ```

=== "Windows (PowerShell)"

    ```powershell
    irm https://downloads.limacharlie.io/sensor/windows/install.ps1 | iex; Upgrade-LCSensor -Version "4.33.28"
    ```

## Upgrade Using a Downloaded Sensor Binary

If you have already downloaded a sensor binary, you can upgrade the installed service directly by running it with the `-u` flag. This performs the same in-place upgrade without needing the shell installer.

!!! note
The `-u` flag requires sensor version **4.33.28 or later**.

=== "Linux / macOS"

    ```bash
    sudo ./hcp_linux_x64_release_4.33.28 -u
    ```

=== "Windows"

    ```bat
    hcp_win_x64_release_4.33.28.exe -u
    ```
