---
name: test-limacharlie-edr
description: Deploy a temporary LimaCharlie EDR agent on the local Linux host for testing. Downloads and runs the LC sensor in a temp directory with automatic cleanup. Use for testing detection rules, investigating sensor behavior, or development. Requires selecting or creating a LimaCharlie organization first.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_call_tool, Bash, Read, AskUserQuestion, Skill
---

# Test LimaCharlie EDR

Deploy a temporary LimaCharlie EDR sensor on the local Linux host for testing purposes. The sensor runs in the background with automatic cleanup when stopped.

## When to Use

Use this skill when:

- **Testing D&R rules**: Validate detection rules against live sensor data from your own machine
- **Investigating sensor behavior**: Understand what events the sensor generates for specific actions
- **Development and debugging**: Test detections in a controlled environment
- **Quick validation**: Verify your LimaCharlie setup is working correctly
- **Learning**: Explore LimaCharlie capabilities hands-on

## What This Skill Does

This skill performs a two-phase deployment:

1. **Phase 1 - Installation Key**: Creates or finds an existing "Test EDR" installation key in your selected LimaCharlie organization
2. **Phase 2 - Sensor Deployment**: Downloads the Linux EDR agent to a temporary directory and runs it in the background as root

The sensor:
- Runs in the background (non-blocking)
- Uses a unique temp directory (avoids file conflicts)
- Requires root/sudo for full system monitoring
- Cleans up automatically when stopped

## Required Information

Before starting, ensure you have:

- **LimaCharlie organization**: Select from your available orgs or create a new one
- **Linux 64-bit host**: This skill downloads the Linux x64 sensor
- **Internet access**: Required to download the sensor binary
- **Root/sudo access**: The sensor needs elevated privileges for proper monitoring

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

Check for existing "Test EDR" installation key:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_installation_keys",
  parameters={"oid": "<SELECTED_ORG_ID>"}
)
```

**If "Test EDR" key exists**: Extract the `key` value from the response.

**If not exists**: Create one:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="create_installation_key",
  parameters={
    "oid": "<SELECTED_ORG_ID>",
    "description": "Test EDR",
    "tags": ["test-edr", "temporary"]
  }
)
```

Save the returned `key` value for the next phase.

### Phase 2: Download and Run the EDR

**Step 1**: Create a temp directory and download the sensor:

```bash
TEMP_DIR=$(mktemp -d -t lc-edr-test-XXXXXX)
curl -sSL https://downloads.limacharlie.io/sensor/linux/64 -o "$TEMP_DIR/lc_sensor"
chmod +x "$TEMP_DIR/lc_sensor"
echo "Sensor downloaded to: $TEMP_DIR"
```

**Step 2**: Run the sensor in background (as root):

```bash
sudo setsid "$TEMP_DIR/lc_sensor" -d <INSTALLATION_KEY> > /dev/null 2>&1 &
echo "Sensor started in $TEMP_DIR"
```

**Important**:
- Uses `setsid` to create a new session and fully detach from the terminal (prevents Claude Code from hanging)
- Store the `TEMP_DIR` path for cleanup later
- The sensor process name is `lc_sensor` - use this for stopping

### Verify Sensor Connection

After starting, the sensor should appear in your LimaCharlie organization within a few seconds. Verify by listing sensors with a selector that matches the installation key's `iid` (Installation ID, a UUID):

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "<SELECTED_ORG_ID>",
    "selector": "iid == `<INSTALLATION_KEY_IID>`"
  }
)
```

Replace `<INSTALLATION_KEY_IID>` with the `iid` UUID from the installation key used. This selector fetches only the sensor enrolled with that specific installation key, rather than listing all sensors in the organization.

### Stopping and Cleanup

When the user wants to stop the test EDR:

**Step 1**: Kill the sensor process by name:

```bash
sudo pkill -f lc_sensor
```

**Step 2**: Clean up the temp directory:

```bash
sudo rm -rf <TEMP_DIR>
```

**Important**: Do NOT use `KillShell` to stop the sensor - this can kill the parent shell process unexpectedly. Always use `pkill` to terminate the sensor process directly.

## Example Usage

### Example 1: Full Deployment Workflow

**User**: "I want to test the LimaCharlie EDR on my machine"

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
    "description": "Test EDR",
    "tags": ["test-edr", "temporary"]
  }
)
```

Returns: `{"iid": "test-edr", "key": "abc123:def456:..."}`

5. Download and run sensor:
```bash
TEMP_DIR=$(mktemp -d -t lc-edr-test-XXXXXX)
curl -sSL https://downloads.limacharlie.io/sensor/linux/64 -o "$TEMP_DIR/lc_sensor"
chmod +x "$TEMP_DIR/lc_sensor"
sudo setsid "$TEMP_DIR/lc_sensor" -d "abc123:def456:..." > /dev/null 2>&1 &
echo "Sensor started in $TEMP_DIR"
```

6. Verify sensor connection using a selector with the installation key's `iid`:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "abc123-def456-...",
    "selector": "iid == `<IID_FROM_INSTALLATION_KEY>`"
  }
)
```

7. Inform user the sensor is running and how to stop it (using `sudo pkill -f lc_sensor`).

### Example 2: Stopping the Test EDR

**User**: "Stop the test EDR"

**Steps**:

1. Kill the sensor process:
```bash
sudo pkill -f lc_sensor
```

2. Clean up:
```bash
sudo rm -rf /tmp/lc-edr-test-XXXXXX
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

- **Root privileges required**: The sensor needs sudo/root to properly monitor system calls, processes, files, and network activity
- **Temp directory**: The sensor creates working files, so we use a dedicated temp directory to keep things clean
- **Automatic tags**: Sensors enrolled with this key get `test-edr` and `temporary` tags for easy identification
- **Console visibility**: The sensor appears in your LimaCharlie web console at https://app.limacharlie.io
- **Background execution**: The sensor runs in background, so you can continue working while it monitors
- **Reusable key**: The "Test EDR" installation key is reused if it already exists, avoiding duplicate keys
- **Cleanup**: Always clean up when done to avoid orphaned processes and files

## Related Skills

- `limacharlie-call`: For creating organizations or other API operations
- `detection-engineering`: For creating D&R rules to test with the sensor
- `sensor-health`: To check if your test sensor is reporting properly
- `timeline-creation`: To investigate events from your test sensor
