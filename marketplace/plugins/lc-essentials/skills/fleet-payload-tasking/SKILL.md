---
name: fleet-payload-tasking
description: Deploy payloads and shell commands fleet-wide using reliable tasking. Execute scripts, collect data, or run commands across all endpoints with automatic handling of offline sensors. Use for vulnerability scanning, data collection, software inventory, compliance checks, or any fleet-wide operation.
allowed-tools:
  - Task
  - Read
  - Bash
  - Write
  - AskUserQuestion
  - mcp__plugin_lc-essentials_limacharlie__lc_call_tool
  - mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_detection
  - mcp__plugin_lc-essentials_limacharlie__generate_dr_rule_respond
  - mcp__plugin_lc-essentials_limacharlie__validate_dr_rule_components
---

# Fleet Payload Tasking Skill

Deploy payloads (scripts) or shell commands to all endpoints in an organization using reliable tasking. Handles offline sensors automatically - tasks queue and execute when sensors come online.

> **TODO**: Move payload generation, D&R rule creation, and result collection logic into sub-agents for better parallelization and reduced context usage. The main skill should orchestrate sub-agents rather than executing all steps directly.

## When to Use

Use this skill when the user needs to:
- **Run commands fleet-wide**: "Run this script on all Linux servers", "Execute a command across all endpoints"
- **Collect data from endpoints**: "Get OS version from all machines", "Collect installed packages"
- **Vulnerability scanning**: "Find all endpoints with log4j", "Check for vulnerable OpenSSL versions"
- **Software inventory**: "What versions of Chrome are installed?", "Find all Java installations"
- **Compliance checks**: "Verify security configurations across the fleet"
- **Custom data collection**: "Run this custom script and collect results"

## Two Deployment Approaches

### Approach 1: Shell Commands (Simple, Quick)

For simple data collection, use `os_shell` directly in the task - no payload upload needed:

```
reliable_tasking(
  task="os_shell echo '{\"hostname\":\"'$(hostname)'\",\"os\":\"'$(uname -s)'\",\"bash\":\"'$(/bin/bash --version | head -1)'\"}'",
  selector="plat == macos",
  context="shell-scan-001",
  ttl=3600
)
```

**Pros:**
- No payload upload step
- JSON output comes directly in STDOUT
- Simpler workflow

**Cons:**
- Command line length limits
- Complex logic is harder to express
- Less reusable

### Approach 2: Payload Scripts (Complex, Reusable)

For complex operations, upload a payload script first:

1. Create and upload payload
2. Create D&R rule to collect results
3. Deploy via reliable tasking
4. Collect artifacts

**Pros:**
- Handles complex logic
- Reusable across scans
- Can write large result files

**Cons:**
- More setup steps
- Requires payload management

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FLEET PAYLOAD TASKING                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  OPTION A: Shell Command (Simple)                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │ Build os_shell  │───▶│ Deploy via      │───▶│ D&R rule        │     │
│  │ command with    │    │ reliable_tasking│    │ captures STDOUT │     │
│  │ inline JSON     │    │                 │    │ as detection    │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
│  OPTION B: Payload Script (Complex)                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │ Generate & Upload│───▶│ Create D&R rule │───▶│ Deploy via      │     │
│  │ payload script  │    │ to file_get     │    │ reliable_tasking│     │
│  │                 │    │ result file     │    │                 │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                    │                                    │
│                                    ▼                                    │
│                          ┌─────────────────┐                            │
│                          │ Results stored  │                            │
│                          │ as artifacts    │                            │
│                          └─────────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Benefits

| Feature | Benefit |
|---------|---------|
| **Reliable Tasking** | Handles offline sensors - task executes when they come online |
| **Flexible Targeting** | Use sensor selectors (tags, platform, hostname patterns) |
| **Shell or Payload** | Choose simple commands or complex scripts |
| **Async Workflow** | Deploy now, collect results later |
| **Cross-Platform** | Linux, macOS, Windows support |
| **Scalable** | Works across thousands of endpoints |

## Shell Command Workflow (Recommended for Simple Tasks)

### Step 1: Select Organization

```
lc_call_tool(
  tool_name="list_user_orgs",
  parameters={}
)
```

### Step 2: Build Shell Command

Create a command that outputs JSON to STDOUT:

```bash
# Example: Collect bash/zsh versions
os_shell echo '{"scan_id":"scan-001","hostname":"'$(hostname)'","results":[' && \
  for p in /bin/bash /usr/bin/bash /bin/zsh; do \
    [ -x "$p" ] && echo '{"path":"'$p'","version":"'$($p --version 2>/dev/null | head -1)'"},' ; \
  done && \
  echo ']}'
```

### Step 3: Deploy via Reliable Tasking

```
lc_call_tool(
  tool_name="reliable_tasking",
  parameters={
    "oid": "[org-id]",
    "task": "os_shell echo '{\"scan_id\":\"scan-001\",\"hostname\":\"'$(hostname)'\",\"bash\":\"'$(/bin/bash --version | head -1)'\"}'",
    "selector": "plat == macos",
    "context": "bash-scan-001",
    "ttl": 3600
  }
)
```

### Step 4: Create D&R Rule to Capture Results

```
lc_call_tool(
  tool_name="set_dr_general_rule",
  parameters={
    "oid": "[org-id]",
    "rule_name": "shell-scan-collector",
    "rule_content": {
      "detect": {
        "event": "RECEIPT",
        "op": "contains",
        "path": "event/STDOUT",
        "value": "scan-001"
      },
      "respond": [
        {
          "action": "report",
          "name": "shell-scan-result"
        }
      ]
    }
  }
)
```

### Step 5: Query Results

Use LCQL or check detections:

```
lc_call_tool(
  tool_name="run_lcql_query",
  parameters={
    "oid": "[org-id]",
    "query": "event_type = 'RECEIPT' AND event/STDOUT contains 'scan-001'",
    "limit": 100
  }
)
```

Or check generated detections:

```
lc_call_tool(
  tool_name="get_historic_detections",
  parameters={
    "oid": "[org-id]",
    "start": [timestamp],
    "end": [timestamp],
    "limit": 100
  }
)
```

## Payload Script Workflow (For Complex Operations)

### Step 1: Generate Payload Script

Create a script that:
1. Performs the desired operation
2. Writes JSON results to a temp file
3. Outputs ONLY the file path to STDOUT

**Example: Cross-platform mktemp handling**

```bash
#!/bin/bash
SCAN_ID="$1"

# Cross-platform mktemp (macOS requires different syntax)
if [ "$(uname)" = "Darwin" ]; then
    OUTPUT_FILE=$(mktemp /tmp/lc-fleet-scan.XXXXXX)
    mv "$OUTPUT_FILE" "${OUTPUT_FILE}.json"
    OUTPUT_FILE="${OUTPUT_FILE}.json"
else
    OUTPUT_FILE=$(mktemp /tmp/lc-fleet-scan-XXXXXX.json)
fi

# Write results to file
echo '{"scan_id":"'$SCAN_ID'","hostname":"'$(hostname)'","results":[]}' > "$OUTPUT_FILE"

# CRITICAL: Output ONLY the file path
echo "$OUTPUT_FILE"
```

### Step 2: Upload Payload

Use `file_content` with base64-encoded script:

```bash
# Encode the script
base64 -w0 /tmp/my-payload.sh
```

```
lc_call_tool(
  tool_name="create_payload",
  parameters={
    "oid": "[org-id]",
    "name": "my-payload.sh",
    "file_content": "[base64-encoded-content]"
  }
)
```

### Step 3: Create D&R Rule for File Collection

```
lc_call_tool(
  tool_name="set_dr_general_rule",
  parameters={
    "oid": "[org-id]",
    "rule_name": "payload-collector",
    "rule_content": {
      "detect": {
        "event": "RECEIPT",
        "op": "matches",
        "path": "event/STDOUT",
        "re": "/tmp/lc-fleet-scan[.-][A-Za-z0-9]+\\.json"
      },
      "respond": [
        {
          "action": "task",
          "command": "file_get {{ .event.STDOUT | trim }}",
          "investigation": "scan-001"
        },
        {
          "action": "report",
          "name": "payload-result"
        }
      ]
    }
  }
)
```

### Step 4: Deploy Task

```
lc_call_tool(
  tool_name="reliable_tasking",
  parameters={
    "oid": "[org-id]",
    "task": "run --payload-name my-payload.sh --arguments 'scan-001'",
    "selector": "plat == linux",
    "context": "scan-001",
    "ttl": 604800
  }
)
```

### Step 5: Collect Artifacts

```
lc_call_tool(
  tool_name="list_artifacts",
  parameters={
    "oid": "[org-id]",
    "start": [scan-start-timestamp],
    "end": [now-timestamp]
  }
)
```

## Sensor Selectors

| Selector | Example | Description |
|----------|---------|-------------|
| All sensors | (empty) | Every sensor in org |
| By platform | `plat == windows` | Only Windows sensors |
| By tag | `tag == production` | Sensors with specific tag |
| Combined | `plat == linux AND tag == webserver` | Multiple criteria |
| By hostname | `hostname == server1.example.com` | Specific host |

## Monitoring Task Progress

```
lc_call_tool(
  tool_name="list_reliable_tasks",
  parameters={"oid": "[org-id]"}
)
```

Shows:
- Which sensors have acknowledged/executed
- Which sensors are still pending (offline)
- Task expiration time

## Error Handling

| Issue | Cause | Resolution |
|-------|-------|------------|
| No results | Sensors offline | Wait for TTL period |
| Partial results | Some sensors offline | Check `list_reliable_tasks` for pending |
| D&R not matching | Wrong STDOUT pattern | Verify regex matches actual output |
| Payload failed | Script error | Check RECEIPT events for STDERR |

## Cleanup

After operation completion:

```
# Delete D&R rule
lc_call_tool(
  tool_name="delete_dr_general_rule",
  parameters={"oid": "[org-id]", "rule_name": "shell-scan-collector"}
)

# Delete payload (if used)
lc_call_tool(
  tool_name="delete_payload",
  parameters={"oid": "[org-id]", "name": "my-payload.sh"}
)

# Delete reliable task
lc_call_tool(
  tool_name="delete_reliable_task",
  parameters={"oid": "[org-id]", "task_id": "[task-id]", "selector": "*"}
)
```

## Security Considerations

- **Approval Workflow**: Consider requiring user confirmation before fleet-wide operations
- **Input Validation**: Sanitize parameters to prevent command injection
- **Audit Logging**: All operations logged in LimaCharlie audit trail
- **Least Privilege**: Use sensor selectors to limit scope when possible
- **Payload Review**: Review payload scripts before deployment

## Related Skills

- `sensor-coverage` - Fleet inventory and health
- `sensor-tasking` - Direct sensor commands
- `detection-engineering` - Create D&R rules
- `limacharlie-call` - Low-level API access
