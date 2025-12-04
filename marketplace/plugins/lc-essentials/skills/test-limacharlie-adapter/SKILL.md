---
name: test-limacharlie-adapter
description: Deploy a temporary LimaCharlie Adapter on the local Linux or Mac OS host for testing log ingestion. Downloads the adapter, auto-detects log sources, and streams them to your LimaCharlie organization.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_call_tool, Bash, Read, AskUserQuestion, Skill
---

# Test LimaCharlie Adapter

Deploy a temporary LimaCharlie Adapter on the local Linux or Mac OS host for testing log ingestion. The adapter streams local logs to your LimaCharlie organization in real-time.

## When to Use

Use this skill when:

- **Testing log ingestion**: Validate that logs flow correctly into LimaCharlie
- **Testing D&R rules on logs**: Write and test detection rules against real log data
- **Exploring adapter behavior**: Understand how adapters forward log data
- **Development and debugging**: Test adapter configurations before production deployment
- **Learning**: Explore LimaCharlie's log ingestion capabilities hands-on

## What This Skill Does

This skill performs a multi-phase deployment:

1. **Phase 1 - Installation Key**: Creates or finds an existing "Test Adapter" installation key in your selected LimaCharlie organization
2. **Phase 2 - Log Source Detection**: Auto-detects log sources (files on Linux, unified logging on Mac OS)
3. **Phase 3 - Adapter Deployment**: Downloads the appropriate adapter binary for your platform and runs it with logs piped to stdin

The adapter:
- Runs in the background (non-blocking)
- Uses a unique temp directory (avoids file conflicts)
- Streams logs in real-time (`tail -f` on Linux, `log stream` on Mac OS)
- Does NOT require root/sudo
- Cleans up automatically when stopped

## Required Information

Before starting, ensure you have:

- **LimaCharlie organization**: Select from your available orgs or create a new one
- **Linux or Mac OS host**: Supports Linux x64, Mac Intel (x64), and Mac Apple Silicon (arm64)
- **Internet access**: Required to download the adapter binary
- **Log access**: On Linux, needs read access to log files in `/var/log`. On Mac OS, uses the unified logging system via `log stream`

## How to Use

### Pre-requisite: Select an Organization

First, get the list of available organizations:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_user_orgs",
  parameters={}
)
```

This returns your available organizations. Use AskUserQuestion to let the user select one, or if they need a new org, use the `limacharlie-call` skill to create one with `create_org`.

### Phase 1: Get or Create Installation Key

Check for existing "Test Adapter" installation key:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_installation_keys",
  parameters={"oid": "<SELECTED_ORG_ID>"}
)
```

**If "Test Adapter" key exists**: Extract the `iid` value from the response.

**If not exists**: Create one:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "<SELECTED_ORG_ID>",
    "description": "Test Adapter",
    "tags": ["test-adapter", "temporary"]
  }
)
```

Save the returned `iid` for later phases.

> **IMPORTANT**: For adapters, the `installation_key` parameter is the **IID (UUID format)**, NOT the full base64-encoded key used by EDR sensors.

### Phase 2: Detect Log Source

First, detect the platform:

```bash
OS_TYPE=$(uname -s)
echo "Platform: $OS_TYPE"
```

**For Linux**: Find the most recently modified log files in `/var/log`:

```bash
find /var/log -maxdepth 1 -type f \( -name "*.log" -o -name "syslog" -o -name "messages" -o -name "auth.log" \) -readable -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -5
```

This shows the 5 most recently modified log files. Pick the most active one (typically `/var/log/syslog` or `/var/log/messages`). Confirm the selected log file with the user before proceeding.

**For Mac OS**: No file detection needed - uses the unified logging system via `log stream`. The adapter will receive logs directly from macOS's unified logging system.

### Phase 3: Download and Run the Adapter

**Step 1**: Detect platform and create temp directory:

```bash
OS_TYPE=$(uname -s)
ARCH=$(uname -m)
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/lc-adapter-test-XXXXXX")
HOSTNAME=$(hostname)
echo "Platform: $OS_TYPE ($ARCH), Temp dir: $TEMP_DIR"
```

**Step 2**: Download the appropriate adapter binary:

```bash
if [ "$OS_TYPE" = "Darwin" ]; then
  if [ "$ARCH" = "arm64" ]; then
    DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/mac/arm64"
  else
    DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/mac/64"
  fi
else
  DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/linux/64"
fi
curl -sSL "$DOWNLOAD_URL" -o "$TEMP_DIR/lc_adapter"
chmod +x "$TEMP_DIR/lc_adapter"
echo "Adapter downloaded to: $TEMP_DIR"
```

**Step 3**: Run the adapter with logs piped to stdin:

```bash
if [ "$OS_TYPE" = "Darwin" ]; then
  # Mac: pipe from log stream (unified logging)
  nohup bash -c "log stream --style syslog | $TEMP_DIR/lc_adapter stdin \
    client_options.identity.installation_key=<IID> \
    client_options.identity.oid=<OID> \
    client_options.platform=text \
    client_options.sensor_seed_key=test-adapter \
    client_options.hostname=$HOSTNAME \
    > $TEMP_DIR/adapter.log 2>&1" > /dev/null 2>&1 &
else
  # Linux: pipe from tail -f on log file
  setsid bash -c "tail -f <LOG_FILE_PATH> | $TEMP_DIR/lc_adapter stdin \
    client_options.identity.installation_key=<IID> \
    client_options.identity.oid=<OID> \
    client_options.platform=text \
    client_options.sensor_seed_key=test-adapter \
    client_options.hostname=$HOSTNAME \
    > $TEMP_DIR/adapter.log 2>&1" > /dev/null 2>&1 &
fi
echo "Adapter started in $TEMP_DIR"
```

**Important**:
- **Linux** uses `setsid` to create a new session and `tail -f` to stream log files
- **Mac OS** uses `nohup` for detachment and `log stream` for unified logging
- Both approaches prevent Claude Code from hanging while waiting for the process
- Does NOT require sudo - the adapter runs as regular user
- Logs output to `$TEMP_DIR/adapter.log` for debugging
- Store the `TEMP_DIR` path for cleanup later
- The adapter process name is `lc_adapter` - use this for stopping

### Verify Adapter Connection

After starting, the adapter should appear in your LimaCharlie organization within a few seconds as a sensor. Verify by listing sensors with a selector that matches the installation key's `iid`:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "<SELECTED_ORG_ID>",
    "selector": "iid == `<IID>`"
  }
)
```

You can also check the adapter log for connection status:

```bash
cat "$TEMP_DIR/adapter.log"
```

Look for `usp-client connected` to confirm successful connection.

### Stopping and Cleanup

When the user wants to stop the test adapter:

**Single command to stop and clean up** (recommended):

```bash
pkill -9 -f lc_adapter; pkill -9 -f "tail -f.*log"; pkill -9 -f "log stream"; rm -rf <TEMP_DIR>; echo "Cleanup complete"
```

**Important notes**:
- Use `-9` (SIGKILL) for reliable termination of detached processes
- Use `;` instead of `&&` - pkill returns non-zero exit codes even on success (e.g., 144 when the signal is delivered)
- Kill `lc_adapter` AND the log source process (`tail -f` on Linux, `log stream` on Mac)
- Do NOT use `KillShell` to stop the adapter - always use `pkill`

**Verify cleanup succeeded**:

```bash
ps aux | grep "[l]c_adapter" || echo "Adapter stopped"
```

The `[l]` bracket trick prevents grep from matching itself in the output.

## Example Usage

### Example 1: Full Deployment Workflow

**User**: "I want to test log ingestion with LimaCharlie"

**Steps**:

1. List organizations:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_user_orgs",
  parameters={}
)
```

Response shows: `[{"name": "My Test Org", "oid": "abc123-def456-..."}]`

2. Ask user to select org (via AskUserQuestion)

3. Check for existing installation key:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_installation_keys",
  parameters={"oid": "abc123-def456-..."}
)
```

4. Create installation key if needed:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "abc123-def456-...",
    "description": "Test Adapter",
    "tags": ["test-adapter", "temporary"]
  }
)
```

Returns: `{"iid": "729b2770-9ae6-4e14-beea-5e42b854adf5", ...}`

5. Detect platform and find log source (Linux only):
```bash
OS_TYPE=$(uname -s)
ARCH=$(uname -m)
# On Linux, find most active log file:
if [ "$OS_TYPE" = "Linux" ]; then
  find /var/log -maxdepth 1 -type f \( -name "*.log" -o -name "syslog" -o -name "messages" -o -name "auth.log" \) -readable -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -5
fi
# On Mac: uses log stream, no file detection needed
```

On Linux, shows `/var/log/syslog` is most active. On Mac, skip this step.

6. Download and run adapter:
```bash
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/lc-adapter-test-XXXXXX")
HOSTNAME=$(hostname)

if [ "$OS_TYPE" = "Darwin" ]; then
  if [ "$ARCH" = "arm64" ]; then
    DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/mac/arm64"
  else
    DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/mac/64"
  fi
else
  DOWNLOAD_URL="https://downloads.limacharlie.io/adapter/linux/64"
fi
curl -sSL "$DOWNLOAD_URL" -o "$TEMP_DIR/lc_adapter"
chmod +x "$TEMP_DIR/lc_adapter"

if [ "$OS_TYPE" = "Darwin" ]; then
  nohup bash -c "log stream --style syslog | $TEMP_DIR/lc_adapter stdin \
    client_options.identity.installation_key=729b2770-9ae6-4e14-beea-5e42b854adf5 \
    client_options.identity.oid=abc123-def456-... \
    client_options.platform=text \
    client_options.sensor_seed_key=test-adapter \
    client_options.hostname=$HOSTNAME \
    > $TEMP_DIR/adapter.log 2>&1" > /dev/null 2>&1 &
else
  setsid bash -c "tail -f /var/log/syslog | $TEMP_DIR/lc_adapter stdin \
    client_options.identity.installation_key=729b2770-9ae6-4e14-beea-5e42b854adf5 \
    client_options.identity.oid=abc123-def456-... \
    client_options.platform=text \
    client_options.sensor_seed_key=test-adapter \
    client_options.hostname=$HOSTNAME \
    > $TEMP_DIR/adapter.log 2>&1" > /dev/null 2>&1 &
fi
echo "Adapter started in $TEMP_DIR"
```

7. Verify adapter connection:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "abc123-def456-...",
    "selector": "iid == `729b2770-9ae6-4e14-beea-5e42b854adf5`"
  }
)
```

8. Inform user the adapter is running and how to stop it.

### Example 2: Stopping the Test Adapter

**User**: "Stop the test adapter"

**Steps**:

1. Stop adapter and clean up (single command):
```bash
pkill -9 -f lc_adapter; pkill -9 -f "tail -f.*log"; pkill -9 -f "log stream"; rm -rf /tmp/lc-adapter-test-XXXXXX; echo "Cleanup complete"
```

2. Verify cleanup:
```bash
ps aux | grep "[l]c_adapter" || echo "Adapter stopped"
```

3. Optionally, delete the sensor from LimaCharlie:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="delete_sensor",
  parameters={
    "oid": "abc123-def456-...",
    "sid": "<SENSOR_ID>"
  }
)
```

## Additional Notes

- **Cross-platform support**: Works on Linux (x64), Mac OS Intel (x64), and Mac OS Apple Silicon (arm64)
- **No root required**: The adapter runs as a regular user
- **Log sources differ by platform**:
  - **Linux**: Uses `tail -f` to stream log files from `/var/log`
  - **Mac OS**: Uses `log stream` to access macOS unified logging (no file selection needed)
- **Temp directory**: The adapter may create working files, so we use a dedicated temp directory to keep things clean
- **Automatic tags**: Sensors enrolled with this key get `test-adapter` and `temporary` tags for easy identification
- **Console visibility**: The adapter appears as a sensor in your LimaCharlie web console at https://app.limacharlie.io
- **Background execution**: The adapter runs in background, so you can continue working while it streams logs
- **Reusable key**: The "Test Adapter" installation key is reused if it already exists, avoiding duplicate keys
- **Real-time streaming**: Uses `tail -f` (Linux) or `log stream` (Mac) for reliable streaming
- **Cleanup**: Always clean up when done to avoid orphaned processes and files. Use `;` not `&&` when chaining cleanup commands since pkill returns non-zero exit codes even on success
- **Debugging**: Check `$TEMP_DIR/adapter.log` if the adapter isn't connecting

## Related Skills

- `limacharlie-call`: For creating organizations or other API operations
- `detection-engineering`: For creating D&R rules to test with the adapter
- `sensor-health`: To check if your test adapter is reporting properly
- `timeline-creation`: To investigate events from your test adapter
- `test-limacharlie-edr`: For testing the EDR sensor instead of log adapters
