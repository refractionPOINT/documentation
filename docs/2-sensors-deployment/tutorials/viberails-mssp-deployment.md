# Deploying Viberails at Scale via Payloads (MSSP Guide)

[Viberails](https://viberails.io) is a control plane for AI coding assistants (Claude Code, Cursor, Gemini CLI, GitHub Copilot CLI, Codex, OpenCode, OpenClaw). It installs lightweight hooks into each tool so every prompt and tool call is audited and authorized through LimaCharlie.

For MSSPs, MSPs, and MDR providers who already manage developer endpoints in LimaCharlie, the existing endpoint agent and its [Payloads](../endpoint-agent/payloads.md) feature can be used to deliver and configure Viberails across every customer's developer workstations without touching their endpoints by hand.

This tutorial walks through that workflow end to end.

## Why this works well for MSSPs

- **Reuses your existing fleet.** Anywhere the LimaCharlie agent is already deployed, you can ship and execute a payload — no new MDM, no new VPN, no installer to email developers.
- **Fits IaC.** Payloads, installation rules, and D&R rules can all be templated and pushed to many customer organizations through the [Payload Manager](../../5-integrations/extensions/limacharlie/payload-manager.md) extension or [Git-Sync](../../5-integrations/extensions/limacharlie/git-sync.md).
- **Targeted, not fleet-wide.** Sensor tags let you scope the rollout to developer machines only, and the [sensor selector](../../1-getting-started/use-cases/investigation-guide.md) syntax keeps that targeting consistent across customers.
- **Auditable.** Every payload `run` produces a `RECEIPT` event in the sensor timeline, so you can prove that Viberails was installed on a given host at a given time.

## How it works

```mermaid
flowchart LR
    subgraph MSSP[MSSP Org]
        BIN[Viberails binaries<br/>linux/macos/windows]
        TPL[D&R rule template]
    end
    subgraph PM[Payload Manager]
        SYNC[Sync every 24h]
    end
    subgraph CUST[Customer Orgs]
        P1[Payloads]
        R1[D&R Rules]
        S1[Tagged sensors<br/>developer workstations]
    end
    BIN --> PM
    TPL --> PM
    PM --> P1
    PM --> R1
    P1 --> S1
    R1 --> S1
    S1 -.RECEIPT.-> Audit[LimaCharlie<br/>audit timeline]
```

1. The MSSP uploads the Viberails binaries (one per OS/architecture) as Payloads in each customer organization, normally via the Payload Manager so they stay in sync.
2. Each customer organization holds a D&R rule that fires on `CONNECTED` for sensors tagged as developer workstations (`viberails-deploy`).
3. The rule `put`s the right binary onto disk, then `run`s it with `join-team` and `install --providers all`, scoped to the active console user so hooks land in that user's home directory.
4. Once installed, Viberails reports every AI tool prompt and tool call back to that same LimaCharlie organization (or any Viberails team the MSSP designates).

## Prerequisites

- A Viberails team already created. See [Quick Start](https://github.com/refractionPOINT/viberails#quick-start). Note the **team URL** produced by `viberails init-team` — you will reuse it for every customer endpoint that should report to the same team. MSSPs typically create one Viberails team per customer (so audit data stays in the customer's tenant) or one shared team (so the MSSP SOC sees everything).
- The LimaCharlie endpoint agent installed on the developer workstations you want to cover.
- API permissions to manage payloads and D&R rules in each customer org:
  - `payload.ctrl`, `payload.use`
  - `dr.list`, `dr.set`, `dr.del`
- The [Payload Manager](../../5-integrations/extensions/limacharlie/payload-manager.md) extension installed in each target org if you want centralized syncing of payloads.

## Step 1 — Tag developer workstations

Pick a tag that identifies machines where AI coding assistants are used. We will use `viberails-deploy` throughout this guide.

You can tag manually from the Sensors view, with the CLI, or automatically based on installed software. A common pattern is to add the tag at install time via the [installation key](../installation-keys.md), so any new developer workstation enrolling under that key inherits the tag.

```bash
# Example: tag an existing sensor
limacharlie sensors tag --sid <SENSOR_ID> --tag viberails-deploy --oid <OID>
```

See [Sensor Tags](../sensor-tags.md) for the full mechanics.

## Step 2 — Upload the Viberails binaries as payloads

Viberails publishes signed binaries for every supported OS/architecture at `get.viberails.io`. Download them once on a trusted host and verify checksums against [release.json](https://get.viberails.io/release.json), then upload each one as a [payload](../endpoint-agent/payloads.md).

```bash
# Download
curl -fsSL -o viberails-linux-x64       https://get.viberails.io/viberails-linux-x64
curl -fsSL -o viberails-linux-arm64     https://get.viberails.io/viberails-linux-arm64
curl -fsSL -o viberails-macos-x64       https://get.viberails.io/viberails-macos-x64
curl -fsSL -o viberails-macos-arm64     https://get.viberails.io/viberails-macos-arm64
curl -fsSL -o viberails-windows-x64.exe https://get.viberails.io/viberails-windows-x64.exe

# Upload to a single org via the CLI
for f in viberails-linux-x64 viberails-linux-arm64 \
         viberails-macos-x64 viberails-macos-arm64 \
         viberails-windows-x64.exe; do
  limacharlie payload create --name "$f" --file "./$f" --oid <OID>
done
```

!!! tip "Naming"
    The payload **name** is also the on-disk file name when it lands on the endpoint, and it determines the file extension that the OS uses to decide how to execute it. Keep the `.exe` suffix for Windows so it runs as a native executable.

### Distributing payloads across many customer orgs

For more than a handful of organizations, do not upload payloads one by one. Instead, drive the upload through the [Payload Manager](../../5-integrations/extensions/limacharlie/payload-manager.md):

- Store the binaries in an object store (GCS, S3, an internal artifact registry) keyed by version.
- Configure Payload Manager in each customer org to pull the same set of named payloads from that source.
- Payload Manager re-syncs payloads every 24 hours, so refreshing a Viberails release across the fleet is a single upload at the source.

When you ship a new Viberails release, replace the artifacts at the source URL and the change propagates everywhere.

## Step 3 — Create the deployment D&R rule

The rule below fires when a tagged sensor connects, drops the right binary onto disk, runs Viberails as the **active console user** (so hooks install in that user's home directory rather than `root`/`SYSTEM`), then removes the tag so the rule only fires once per workstation.

Replace `<YOUR_TEAM_URL>` with the URL produced by `viberails init-team`. If you maintain one Viberails team per customer, parameterize this per-org when you sync the rule.

### Windows

```yaml
detect:
  event: CONNECTED
  op: and
  rules:
    - op: is platform
      name: windows
    - op: is tagged
      tag: viberails-deploy
respond:
  - action: task
    command: put --payload-name viberails-windows-x64.exe --payload-path "C:\Windows\Temp\viberails.exe"
  - action: wait
    duration: 10s
  # Run as the interactively logged-on user. PsExec/RunAs-equivalent behavior
  # is needed because hooks must land in the developer's profile, not SYSTEM's.
  # The scheduled task approach below uses the Interactive group token of
  # whoever is currently signed in.
  - action: task
    command: >
      run --shell-command
      "schtasks /Create /F /SC ONCE /ST 00:00 /TN VRInstall
       /TR \"cmd /c C:\\Windows\\Temp\\viberails.exe join-team <YOUR_TEAM_URL>
       && C:\\Windows\\Temp\\viberails.exe install --providers all\"
       /RU INTERACTIVE && schtasks /Run /TN VRInstall"
  - action: wait
    duration: 60s
  - action: task
    command: run --shell-command "schtasks /Delete /F /TN VRInstall"
  - action: task
    command: file_del "C:\Windows\Temp\viberails.exe"
  - action: remove tag
    tag: viberails-deploy
  - action: add tag
    tag: viberails-installed
```

### macOS

```yaml
detect:
  event: CONNECTED
  op: and
  rules:
    - op: is platform
      name: macos
    - op: is tagged
      tag: viberails-deploy
respond:
  - action: task
    command: put --payload-name viberails-macos-arm64 --payload-path "/var/tmp/viberails"
  - action: wait
    duration: 10s
  - action: task
    command: run --shell-command "chmod +x /var/tmp/viberails"
  - action: task
    command: >
      run --shell-command
      "USER=$(stat -f%Su /dev/console);
       UID=$(id -u $USER);
       launchctl asuser $UID sudo -u $USER -H /var/tmp/viberails join-team <YOUR_TEAM_URL>;
       launchctl asuser $UID sudo -u $USER -H /var/tmp/viberails install --providers all"
  - action: wait
    duration: 30s
  - action: task
    command: file_del "/var/tmp/viberails"
  - action: remove tag
    tag: viberails-deploy
  - action: add tag
    tag: viberails-installed
```

For Intel hardware, swap `viberails-macos-arm64` for `viberails-macos-x64`. If you have a mixed fleet, split the rule by architecture using `op: is arch`.

### Linux

```yaml
detect:
  event: CONNECTED
  op: and
  rules:
    - op: is platform
      name: linux
    - op: is tagged
      tag: viberails-deploy
respond:
  - action: task
    command: put --payload-name viberails-linux-x64 --payload-path "/tmp/viberails"
  - action: wait
    duration: 10s
  - action: task
    command: run --shell-command "chmod +x /tmp/viberails"
  - action: task
    command: >
      run --shell-command
      "USER=$(who | awk 'NR==1{print $1}');
       sudo -u $USER -H /tmp/viberails join-team <YOUR_TEAM_URL>;
       sudo -u $USER -H /tmp/viberails install --providers all"
  - action: wait
    duration: 30s
  - action: task
    command: file_del "/tmp/viberails"
  - action: remove tag
    tag: viberails-deploy
  - action: add tag
    tag: viberails-installed
```

!!! warning "User-context matters"
    Viberails stores its configuration under the **developer's** home directory (`~/.config/viberails/`) and installs hooks into per-tool config files there (`~/.claude/`, `~/.cursor/`, etc.). The endpoint agent runs payloads as `root`/`SYSTEM`, so the rules above explicitly drop privileges to the interactively signed-in user. Running Viberails as `root`/`SYSTEM` would install hooks for that account and leave the developer untouched.

    If no user is signed in when the rule fires, the install will fail. The simplest workaround is to fire on a different trigger that implies a user is present, or to leave the `viberails-deploy` tag in place until the rule sees a logged-in user and successfully completes.

## Step 4 — Distribute the rule to every customer org

Manage the rule the same way you manage every other MSSP-wide D&R rule. The two common patterns:

- **Git-Sync.** Commit the rule (and the payload manifest) to your shared infrastructure repo and let [Git-Sync](../../5-integrations/extensions/limacharlie/git-sync.md) push it to each customer org. Parameterize `<YOUR_TEAM_URL>` per-org through the templating mechanism your repo uses.
- **Organization Groups + IaC CLI.** Define the rule once and apply it to every organization in your "developer-coverage" Organization Group via `limacharlie configs push`.

See [Designing Access for MSSPs](../../7-administration/access/designing-access.md) for the recommended Organization Group layout.

## Step 5 — Verify

For each newly tagged endpoint, confirm the install succeeded:

1. **Receipt in the sensor timeline.** Look for `RECEIPT` events corresponding to each `run` task. The exit code should be 0 and STDOUT should contain `Joined team successfully!` followed by `Hooks installed`.
2. **Tag rotation.** The sensor should now carry `viberails-installed` and no longer carry `viberails-deploy`.
3. **Viberails events flowing.** In the Viberails team's LimaCharlie organization, watch for the first audit events from that machine the next time a developer uses one of the supported AI coding tools.

If verification fails, enable Viberails debug logging on the affected machine and inspect `~/.local/share/viberails/debug/` (Linux/macOS) or `%LOCALAPPDATA%\viberails\debug\` (Windows). See [Viberails Troubleshooting](https://github.com/refractionPOINT/viberails#troubleshooting).

## Updating Viberails on the fleet

Viberails auto-upgrades itself by default whenever any hooked tool runs, so a one-shot install is normally enough. If you have disabled `auto_upgrade` per the [Viberails configuration](https://github.com/refractionPOINT/viberails#configuration), or you want to force-roll a version across all customer endpoints, add a second tag (e.g. `viberails-upgrade`) and a companion D&R rule that runs `viberails upgrade` instead of `install`.

## Removing Viberails

Use the same pattern in reverse: tag the targets `viberails-uninstall`, drop the binary as a payload, and run `viberails uninstall-all --yes` in the user's context. The `--yes` flag suppresses the interactive confirmation, which is essential under a non-interactive payload `run`.

---

## See Also

- [Payloads](../endpoint-agent/payloads.md)
- [Payload Manager](../../5-integrations/extensions/limacharlie/payload-manager.md)
- [Git-Sync](../../5-integrations/extensions/limacharlie/git-sync.md)
- [Sensor Tags](../sensor-tags.md)
- [Security Service Providers (MSSP, MSP, MDR)](../../1-getting-started/use-cases/mssp-msp-mdr.md)
- [Designing Access for MSSPs](../../7-administration/access/designing-access.md)
