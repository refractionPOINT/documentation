# Using LimaCharlie

## Required Tool

**ALWAYS use the `limacharlie` CLI via Bash** for all LimaCharlie API operations. The CLI is automatically installed on session start and handles authentication. Never call MCP tools directly.

If auto-install failed, install manually:

```bash
pipx install limacharlie   # preferred (isolated environment)
uv tool install limacharlie # alternative
pip install --user limacharlie # fallback
```

On first use, verify authentication with `limacharlie auth whoami --output yaml`; if not authenticated, guide the user through `limacharlie auth login`.

## Critical Rules

### 1. Use the CLI Directly

- **WRONG**: `mcp__plugin_lc-essentials_limacharlie__lc_call_tool(...)` or spawning an api-executor agent
- **CORRECT**: `Bash("limacharlie <noun> <verb> --oid <oid> --output yaml")`

Always pass `--output yaml` for token-efficient, machine-readable output. Use `limacharlie <command> --ai-help` to discover a command's flags. Use `limacharlie api <endpoint>` only as an escape hatch for endpoints with no dedicated CLI command.

### 2. Never Write LCQL Queries Manually

LCQL uses unique pipe-based syntax validated against org-specific schemas. Manual queries WILL fail or produce incorrect results.

1. `limacharlie ai generate-query --prompt "..." --oid <oid> --output yaml` — convert natural language to LCQL
2. `limacharlie search validate --query "..." --oid <oid> --output yaml` — mandatory for ALL queries before execution
3. `limacharlie search run --query "..." --start <ts> --end <ts> --oid <oid> --output yaml` — execute only after validation passes

On validation failure, re-run the generate command with the error message — never fix queries manually.

### 3. Never Generate D&R Rules Manually

Use AI generation commands:

1. `limacharlie ai generate-detection --description "..." --oid <oid> --output yaml` — generate detection YAML
2. `limacharlie ai generate-response --description "..." --oid <oid> --output yaml` — generate response YAML
3. `limacharlie dr validate --detect detect.yaml --respond respond.yaml --oid <oid>` — validate before deploy

### 4. Never Calculate Timestamps Manually

LLMs consistently produce incorrect timestamp values.

**ALWAYS use bash:**

```bash
date +%s                           # Current time (seconds)
date -d '1 hour ago' +%s           # 1 hour ago
date -d '7 days ago' +%s           # 7 days ago
date -d '2025-01-15 00:00:00 UTC' +%s  # Specific date
```

### 5. OID is UUID, NOT Organization Name

- **WRONG**: `--oid "my-org-name"`
- **CORRECT**: `--oid "c1ffedc0-ffee-4a1e-b1a5-abc123def456"`
- Use `limacharlie org list --output yaml` to map org names to UUIDs

### 6. Timestamp Milliseconds vs Seconds

- Detection/event data: **milliseconds** (13 digits)
- API parameters: **seconds** (10 digits)
- **ALWAYS** divide by 1000 when using detection timestamps for API queries

### 7. Never Fabricate Data

- Only report what APIs return
- Never estimate, infer, or extrapolate data
- Show "N/A" or "Data unavailable" for missing fields
- Never calculate costs (no pricing data in API)

### 8. Spawn Agents in Parallel

When processing multiple organizations or items:

- Use a SINGLE message with multiple Task calls
- Do NOT spawn agents sequentially
- Each agent handles ONE item, parent aggregates results

## Standard Operating Procedures (SOPs)

Organizations can define SOPs (Standard Operating Procedures) in LimaCharlie that guide how tasks are performed. SOPs can be large documents, so they are loaded lazily (similar to Claude Code Skills).

### On Conversation Start (Load Index Only)

At the beginning of every conversation involving LimaCharlie operations:

1. **List all SOPs** using `limacharlie sop list --oid <oid> --output yaml` for each organization in scope
2. **Store ONLY the name and description** of each SOP (ignore the `text` field - it may be truncated or large)
3. Use this index to identify when an SOP might apply to current work

**Important:** Do NOT read or use the full SOP content at this stage. The `sop list` response may include a `text` field, but ignore it - always call `limacharlie sop get` when you need the actual procedure.

### When Performing Tasks (Load Full Content)

Before executing any significant operation:

1. **Check SOP relevance**: Compare the current task against stored SOP descriptions
2. **If a match is found**:
   - Announce: "Following SOP: [sop-name] - [description]"
   - **MUST call `limacharlie sop get --key <name> --oid <oid> --output yaml`** to retrieve the full SOP content (do not skip this step)
   - Follow the procedure defined in the SOP
3. **If multiple SOPs match**: Announce all matching SOPs, fetch each with `limacharlie sop get`, and follow all applicable procedures

### Example Workflow

1. User asks to investigate a malware alert
2. LLM checks stored SOP index: "malware-response" matches (description: "Standard procedure for malware incidents")
3. LLM announces: "Following SOP: malware-response - Standard procedure for malware incidents"
4. LLM calls `limacharlie sop get --key malware-response --oid <oid> --output yaml` to load the full procedure
5. LLM follows the documented steps from the loaded SOP content

## Sensor Selector Reference

Sensor selectors use [bexpr](https://github.com/hashicorp/go-bexpr) syntax to filter sensors. Use `*` to match all sensors.

### Available Fields

| Field | Type | Description |
|-------|------|-------------|
| `sid` | string | Sensor ID (UUID) |
| `oid` | string | Organization ID (UUID) |
| `iid` | string | Installation Key ID (UUID) |
| `plat` | string | Platform name (see values below) |
| `ext_plat` | string | Extended platform (for multi-platform adapters like Carbon Black) |
| `arch` | string | Architecture (see values below) |
| `hostname` | string | Sensor hostname |
| `ext_ip` | string | External IP address |
| `int_ip` | string | Internal IP address |
| `mac_addr` | string | MAC address |
| `did` | string | Device ID |
| `enroll` | int | Enrollment timestamp |
| `alive` | int | Last seen timestamp |
| `is_del` | bool | Sensor is deleted |
| `isolated` | bool | Sensor is network isolated |
| `should_isolate` | bool | Sensor should be isolated |
| `kernel` | bool | Kernel mode enabled |
| `sealed` | bool | Sensor is sealed |
| `should_seal` | bool | Sensor should be sealed |
| `tags` | string[] | Sensor tags (use `in` operator) |

### Platform Values (`plat`, `ext_plat`)

**EDR Platforms:** `windows`, `linux`, `macos`, `ios`, `android`, `chrome`, `vpn`

**Adapter/USP Platforms:** `text`, `json`, `gcp`, `aws`, `carbon_black`, `1password`, `office365`, `sophos`, `crowdstrike`, `msdefender`, `sentinel_one`, `okta`, `duo`, `github`, `slack`, `azure_ad`, `azure_monitor`, `entraid`, `zeek`, `cef`, `wel`, `xml`, `guard_duty`, `k8s_pods`, `wiz`, `proofpoint`, `box`, `cylance`, `fortigate`, `netscaler`, `paloalto_fw`, `iis`, `trend_micro`, `trend_worryfree`, `bitwarden`, `mimecast`, `hubspot`, `zendesk`, `pandadoc`, `falconcloud`, `sublime`, `itglue`, `canary_token`, `lc_event`, `email`, `mac_unified_logging`, `azure_event_hub_namespace`, `azure_key_vault`, `azure_kubernetes_service`, `azure_network_security_group`, `azure_sql_audit`, `otel`, `cortex_xdr`, `harmony`, `threatlocker`, `halopsa`, `cato`, `gmail`

### Architecture Values (`arch`)

`x86`, `x64`, `arm`, `arm64`, `alpine64`, `chromium`, `wireguard`, `arml`, `usp_adapter`

### Example Selectors

```text
plat == windows                           # All Windows sensors
plat == windows and arch == x64           # 64-bit Windows only
plat == linux and hostname contains "web" # Linux with "web" in hostname
"prod" in tags                            # Sensors tagged "prod"
plat == windows and not isolated          # Non-isolated Windows
ext_plat == windows                       # Carbon Black/Crowdstrike reporting Windows endpoints
```
