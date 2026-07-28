# Service Upgrades

The LimaCharlie endpoint agent has two components with independent version numbers:

- **On-disk agent** — the service binary on the host. It does core identity, cryptography, and transport. This component changes rarely, and a service upgrade replaces it.
- **Over-the-air core** — the main component that supplies detection and response functions. It is downloaded from the LimaCharlie cloud and updated often. To manage over-the-air updates, see [Versioning & Upgrades](versioning-upgrades.md).

The procedures on this page upgrade the **on-disk agent** only. Use them when you need a new service binary for bug fixes, platform compatibility, or support for new on-disk features. The LimaCharlie cloud updates the over-the-air core separately, and that update does not need a service upgrade.

The upgrade stops the service, replaces the binary with the new version, and starts the service again. If the new version does not start, the upgrade rolls back to the previous version automatically.

!!! note "Prerequisites" - Run the command with **root** (Linux/macOS) or **Administrator** (Windows) privileges. - Upgrades do not need an installation key.

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

Use the `--version` flag to move to any available sensor version, newer or older than the installed version. Use the flag to roll back to a known-good version or to pin a specific release.

!!! note
The `--version` flag needs sensor version **4.33.28 or later**.

=== "Linux / macOS"

    ```bash
    curl -L --proto '=https' --tlsv1.2 -sSf https://downloads.limacharlie.io/sensor/posix/install | sudo sh -s -- --upgrade --version 4.33.28
    ```

=== "Windows (PowerShell)"

    ```powershell
    irm https://downloads.limacharlie.io/sensor/windows/install.ps1 | iex; Upgrade-LCSensor -Version "4.33.28"
    ```

## Upgrade Using a Downloaded Sensor Binary

If you already downloaded a sensor binary, run it with the `-u` flag to upgrade the installed service. This does the same in-place upgrade, but it does not need the shell installer.

!!! note
The `-u` flag needs sensor version **4.33.28 or later**.

=== "Linux / macOS"

    ```bash
    sudo ./hcp_linux_x64_release_4.33.28 -u
    ```

=== "Windows"

    ```bat
    hcp_win_x64_release_4.33.28.exe -u
    ```

## Upgrade from the Cloud with the `upgrade_core` Command (Beta)

You can task a sensor to upgrade its own on-disk agent with the `upgrade_core` sensor command, instead of running an installer on the host. The sensor downloads, checks, and installs the requested release. Local shell access and an installer download are not necessary. The automatic rollback on a failed start also applies here.

The native upgrade procedure is in beta, so you must give the `--beta` flag. Without the flag, the command is rejected.

```bash
limacharlie sensor task <SID> upgrade_core --beta
```

Optional flags:

- `--force`: upgrade even if the sensor already reports the latest available release.
- `--version`: pin the exact release to install (e.g. `5.3.3`) instead of the latest. Downgrades are allowed.

!!! note
The `upgrade_core` command needs sensor version **5.3.3 or later**. A sensor with an older version drops the request without a message, and no upgrade occurs.

See the [endpoint commands reference](../../8-reference/endpoint-commands.md#upgrade_core) for more detail.

## Advanced: Forcing an Upgrade

By default, an in-place upgrade (`-u`) replaces the installed service only when the supplied binary is newer than the installed binary. To re-apply a build, or to move to a build that is not newer, set the `LC_UPGRADE_SKIP_VERSION_CHECK` environment variable to `1` (or `true`) on the upgrade process. For example, use the variable to deploy a known-good version again. The variable skips the version comparison and always replaces the installed service.

!!! warning
Set this variable only when you want to override the version check. The automatic rollback on a failed start still applies. But without the version check, you can downgrade the on-disk agent deliberately.
