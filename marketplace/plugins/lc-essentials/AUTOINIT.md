# Using LimaCharlie

## Required Skill

**ALWAYS load the `lc-essentials:limacharlie-call` skill** before any LimaCharlie API operation. Never call LimaCharlie MCP tools directly.

## Critical Rules

### 1. Never Call MCP Tools Directly

- **WRONG**: `mcp__plugin_lc-essentials_limacharlie__lc_call_tool(...)`
- **CORRECT**: Use Task tool with `subagent_type="lc-essentials:limacharlie-api-executor"`

### 2. Never Write LCQL Queries Manually

LCQL uses unique pipe-based syntax validated against org-specific schemas.

- **ALWAYS**: `generate_lcql_query()` first, then `run_lcql_query()` with the generated query
- Manual queries WILL fail or produce incorrect results

### 3. Never Generate D&R Rules Manually

Use AI generation tools:
1. `generate_dr_rule_detection()` - Generate detection YAML
2. `generate_dr_rule_respond()` - Generate response YAML
3. `validate_dr_rule_components()` - Validate before deploy

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

- **WRONG**: `oid: "my-org-name"`
- **CORRECT**: `oid: "c1ffedc0-ffee-4a1e-b1a5-abc123def456"`
- Use `list_user_orgs` to map org names to UUIDs

### 6. Timestamp Milliseconds vs Seconds

- Detection/event data: **milliseconds** (13 digits)
- API parameters (`get_historic_events`, `get_historic_detections`): **seconds** (10 digits)
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

Organizations can define SOPs (Standard Operating Procedures) in LimaCharlie that guide how tasks are performed.

### On Conversation Start

At the beginning of every conversation involving LimaCharlie operations:

1. **List all SOPs** using `list_sops` for each organization in scope
2. **Store in context** the name and description of each SOP
3. Use this list to identify when an SOP applies to current work

### When Performing Tasks

Before executing any significant operation:

1. **Check SOP relevance**: Compare the current task against stored SOP descriptions
2. **If a match is found**:
   - Announce: "Following SOP: [sop-name] - [description]"
   - Call `get_sop` to retrieve the full SOP content
   - Follow the procedure defined in the SOP
3. **If multiple SOPs match**: Announce all matching SOPs and follow each applicable procedure

### Example Workflow

1. User asks to investigate a malware alert
2. LLM checks stored SOPs: "malware-response" matches (description: "Standard procedure for malware incidents")
3. LLM announces: "Following SOP: malware-response - Standard procedure for malware incidents"
4. LLM calls `get_sop` to read the full procedure
5. LLM follows the documented steps in the SOP

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

**Adapter/USP Platforms:** `text`, `json`, `gcp`, `aws`, `carbon_black`, `1password`, `office365`, `sophos`, `crowdstrike`, `msdefender`, `sentinel_one`, `okta`, `duo`, `github`, `slack`, `azure_ad`, `azure_monitor`, `entraid`, `zeek`, `cef`, `wel`, `xml`, `guard_duty`, `k8s_pods`, `wiz`, `proofpoint`, `box`, `cylance`, `fortigate`, `netscaler`, `paloalto_fw`, `iis`, `trend_micro`, `trend_worryfree`, `bitwarden`, `mimecast`, `hubspot`, `zendesk`, `pandadoc`, `falconcloud`, `sublime`, `itglue`, `canary_token`, `lc_event`, `email`, `mac_unified_logging`, `azure_event_hub_namespace`, `azure_key_vault`, `azure_kubernetes_service`, `azure_network_security_group`, `azure_sql_audit`

### Architecture Values (`arch`)

`x86`, `x64`, `arm`, `arm64`, `alpine64`, `chromium`, `wireguard`, `arml`, `usp_adapter`

### Example Selectors

```
plat == windows                           # All Windows sensors
plat == windows and arch == x64           # 64-bit Windows only
plat == linux and hostname contains "web" # Linux with "web" in hostname
"prod" in tags                            # Sensors tagged "prod"
plat == windows and not isolated          # Non-isolated Windows
ext_plat == windows                       # Carbon Black/Crowdstrike reporting Windows endpoints
```
