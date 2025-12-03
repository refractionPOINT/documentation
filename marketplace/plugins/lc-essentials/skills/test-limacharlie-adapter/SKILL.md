---
name: test-limacharlie-adapter
description: Deploy a temporary LimaCharlie Adapter on the local Linux host for testing log ingestion. Downloads the adapter, auto-detects active logs in /var/log, and streams them to your LimaCharlie organization. Supports raw text or syslog parsing.
allowed-tools: mcp__plugin_lc-essentials_limacharlie__lc_call_tool, Bash, Read, AskUserQuestion, Skill
---

# Test LimaCharlie Adapter

Deploy a temporary LimaCharlie Adapter on the local Linux host for testing log ingestion. The adapter streams local log files to your LimaCharlie organization in real-time.

## When to Use

Use this skill when:

- **Testing log ingestion**: Validate that logs flow correctly into LimaCharlie
- **Testing D&R rules on logs**: Write and test detection rules against real syslog/auth logs
- **Exploring adapter behavior**: Understand how adapters parse and forward log data
- **Development and debugging**: Test log parsing configurations before production deployment
- **Learning**: Explore LimaCharlie's log ingestion capabilities hands-on

## What This Skill Does

This skill performs a multi-phase deployment:

1. **Phase 1 - Installation Key**: Creates or finds an existing "Test Adapter" installation key in your selected LimaCharlie organization
2. **Phase 2 - Log Detection**: Auto-detects the most active log file in `/var/log` based on recent modification time
3. **Phase 3 - Parsing Mode**: Lets you choose between raw text or structured syslog parsing
4. **Phase 4 - Adapter Deployment**: Downloads the Linux adapter binary to a temporary directory and runs it in the background

The adapter:
- Runs in the background (non-blocking)
- Uses a unique temp directory (avoids file conflicts)
- Streams logs in real-time (like `tail -f`)
- Cleans up automatically when stopped

## Required Information

Before starting, ensure you have:

- **LimaCharlie organization**: Select from your available orgs or create a new one
- **Linux 64-bit host**: This skill downloads the Linux x64 adapter
- **Internet access**: Required to download the adapter binary
- **Readable log files**: The adapter needs read access to log files in `/var/log`

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

**If "Test Adapter" key exists**: Extract the `key` value from the response.

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

Save the returned `key` value and `iid` for later phases.

### Phase 2: Auto-Detect Active Log File

Find the most recently modified log files in `/var/log`:

```bash
find /var/log -maxdepth 1 -type f \( -name "*.log" -o -name "syslog" -o -name "messages" -o -name "auth.log" \) -readable -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -5
```

This shows the 5 most recently modified log files. Pick the most active one (typically `/var/log/syslog` or `/var/log/messages` on Linux systems).

Confirm the selected log file with the user before proceeding.

### Phase 3: Choose Parsing Mode

Ask the user to select a parsing mode using AskUserQuestion:

**Option 1: Raw Text** - Simple, no parsing
- Events appear as raw log lines
- Good for quick testing or when you'll parse later with D&R rules

**Option 2: Syslog Parsed** - Structured parsing with grok patterns
- Extracts timestamp, hostname, program, pid, and message
- Events are structured JSON with named fields
- Good for writing specific detections

### Phase 4: Download and Run the Adapter

**Step 1**: Create a temp directory and download the adapter:

```bash
TEMP_DIR=$(mktemp -d -t lc-adapter-test-XXXXXX)
curl -sSL https://downloads.limacharlie.io/adapter/linux/64 -o "$TEMP_DIR/lc_adapter"
chmod +x "$TEMP_DIR/lc_adapter"
echo "Adapter downloaded to: $TEMP_DIR"
```

**Step 2**: Run the adapter in background.

**For Raw Text mode:**

```bash
sudo setsid "$TEMP_DIR/lc_adapter" file \
  file_path=<LOG_FILE_PATH> \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=text \
  client_options.sensor_seed_key=test-adapter \
  client_options.hostname=$(hostname) > /dev/null 2>&1 &
echo "Adapter started in $TEMP_DIR"
```

**For Syslog Parsed mode:**

```bash
sudo setsid "$TEMP_DIR/lc_adapter" file \
  file_path=<LOG_FILE_PATH> \
  client_options.identity.installation_key=<INSTALLATION_KEY> \
  client_options.identity.oid=<OID> \
  client_options.platform=text \
  client_options.sensor_seed_key=test-adapter \
  client_options.hostname=$(hostname) \
  'client_options.mapping.parsing_grok=message: %{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:source_host} %{PROG:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:log_message}' \
  client_options.mapping.event_type_path=program > /dev/null 2>&1 &
echo "Adapter started in $TEMP_DIR"
```

**Important**:
- Uses `setsid` to create a new session and fully detach from the terminal (prevents Claude Code from hanging)
- Store the `TEMP_DIR` path for cleanup later
- The adapter process name is `lc_adapter` - use this for stopping

### Verify Adapter Connection

After starting, the adapter should appear in your LimaCharlie organization within a few seconds as a sensor. Verify by listing sensors with a selector that matches the installation key's `iid`:

```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "<SELECTED_ORG_ID>",
    "selector": "iid == `<INSTALLATION_KEY_IID>`"
  }
)
```

Replace `<INSTALLATION_KEY_IID>` with the `iid` UUID from the installation key used.

### Stopping and Cleanup

When the user wants to stop the test adapter:

**Step 1**: Kill the adapter process by name:

```bash
sudo pkill -f lc_adapter
```

**Step 2**: Clean up the temp directory:

```bash
sudo rm -rf <TEMP_DIR>
```

**Important**: Do NOT use `KillShell` to stop the adapter - this can kill the parent shell process unexpectedly. Always use `pkill` to terminate the adapter process directly.

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

Returns: `{"iid": "test-adapter-iid", "key": "abc123:def456:..."}`

5. Find most active log:
```bash
find /var/log -maxdepth 1 -type f \( -name "*.log" -o -name "syslog" -o -name "messages" -o -name "auth.log" \) -readable -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -5
```

Shows `/var/log/syslog` is most active.

6. Ask user for parsing mode (via AskUserQuestion) - user selects "Syslog Parsed"

7. Download and run adapter:
```bash
TEMP_DIR=$(mktemp -d -t lc-adapter-test-XXXXXX)
curl -sSL https://downloads.limacharlie.io/adapter/linux/64 -o "$TEMP_DIR/lc_adapter"
chmod +x "$TEMP_DIR/lc_adapter"
sudo setsid "$TEMP_DIR/lc_adapter" file \
  file_path=/var/log/syslog \
  client_options.identity.installation_key="abc123:def456:..." \
  client_options.identity.oid="abc123-def456-..." \
  client_options.platform=text \
  client_options.sensor_seed_key=test-adapter \
  client_options.hostname=$(hostname) \
  'client_options.mapping.parsing_grok=message: %{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:source_host} %{PROG:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:log_message}' \
  client_options.mapping.event_type_path=program > /dev/null 2>&1 &
echo "Adapter started in $TEMP_DIR"
```

8. Verify adapter connection:
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="list_sensors",
  parameters={
    "oid": "abc123-def456-...",
    "selector": "iid == `test-adapter-iid`"
  }
)
```

9. Inform user the adapter is running and how to stop it.

### Example 2: Stopping the Test Adapter

**User**: "Stop the test adapter"

**Steps**:

1. Kill the adapter process:
```bash
sudo pkill -f lc_adapter
```

2. Clean up:
```bash
sudo rm -rf /tmp/lc-adapter-test-XXXXXX
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

- **Read access required**: The adapter needs to be able to read the log files. If running without sudo, ensure the log files are readable by the current user.
- **Temp directory**: The adapter may create working files, so we use a dedicated temp directory to keep things clean
- **Automatic tags**: Sensors enrolled with this key get `test-adapter` and `temporary` tags for easy identification
- **Console visibility**: The adapter appears as a sensor in your LimaCharlie web console at https://app.limacharlie.io
- **Background execution**: The adapter runs in background, so you can continue working while it streams logs
- **Reusable key**: The "Test Adapter" installation key is reused if it already exists, avoiding duplicate keys
- **Real-time streaming**: The adapter follows the log file and streams new entries as they're written
- **Cleanup**: Always clean up when done to avoid orphaned processes and files

## Parsing Options Explained

### Raw Text Mode
- `platform=text`
- Events appear with the full log line in a `TEXT` event type
- Simple and fast, good for quick testing

### Syslog Parsed Mode
- Uses grok pattern: `%{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:source_host} %{PROG:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:log_message}`
- Extracts structured fields:
  - `timestamp`: The syslog timestamp
  - `source_host`: The hostname from the log
  - `program`: The program/daemon name (used as event type)
  - `pid`: Process ID (if present)
  - `log_message`: The actual log message
- Events are typed by program name (e.g., `sshd`, `systemd`, `cron`)

## Related Skills

- `limacharlie-call`: For creating organizations or other API operations
- `detection-engineering`: For creating D&R rules to test with the adapter
- `sensor-health`: To check if your test adapter is reporting properly
- `timeline-creation`: To investigate events from your test adapter
- `test-limacharlie-edr`: For testing the EDR sensor instead of log adapters
