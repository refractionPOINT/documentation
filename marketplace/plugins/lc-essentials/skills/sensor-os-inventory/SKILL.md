---
name: sensor-os-inventory
description: Get operating system versions for all online sensors in LimaCharlie organizations. Sends os_version tasks to live agents and collects OS details (name, version, build, architecture). Use for fleet inventory, compliance auditing, vulnerability management, OS patching priority, or asset discovery (e.g., "what OS versions are running across my fleet", "show me all Windows 10 sensors", "inventory all sensor operating systems").
allowed-tools: Task, Read, Bash
---

# Sensor OS Inventory Skill

> **IMPORTANT**: Never call `mcp__plugin_lc-essentials_limacharlie__lc_call_tool` directly.
> Always use the Task tool with `subagent_type="lc-essentials:limacharlie-api-executor"`.

This skill collects operating system version information from all online sensors across one or more LimaCharlie organizations by sending live `os_version` tasks to each sensor.

## When to Use

Use this skill when the user asks about:
- **OS Inventory**: "What operating systems are running across my fleet?"
- **Version Discovery**: "Show me all Windows versions in my organizations"
- **Compliance Auditing**: "List all sensors with their OS versions for compliance"
- **Vulnerability Management**: "Which sensors are running outdated OS versions?"
- **Asset Discovery**: "Get OS details for all my sensors"
- **Cross-Org Reports**: "Show me OS distribution across all my orgs"

## What This Skill Does

This skill orchestrates OS version collection by:
1. Getting the list of user's organizations (or using specified orgs)
2. Spawning parallel `lc-essentials:sensor-os-collector` agents (one per org)
3. Each agent gets online sensors and sends `os_version` tasks to them
4. Aggregating results from all agents
5. Presenting a unified inventory report

**Key Advantage**: By running one agent per organization in parallel, this skill can inventory dozens of organizations simultaneously.

**Note**: The `os_version` command only works on **online sensors**. Offline sensors will be reported separately but won't have OS version data.

## How to Use

### Step 1: Parse User Query

Identify the key parameters:
- **Scope**: All orgs (default) or specific orgs by name
- **Platform filter**: Optional filter (windows, linux, macos)
- **Report format**: Summary (default) or detailed list

### Step 2: Get Organizations

Use the LimaCharlie API to get the user's organizations:

```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_user_orgs
    - Parameters: {}
    - Return: RAW"
)
```

If the user specified specific organizations, filter the list to only those.

### Step 3: Spawn Parallel Agents

For each organization, spawn a `lc-essentials:sensor-os-collector` agent in parallel:

```
Task(
  subagent_type="lc-essentials:sensor-os-collector",
  model="haiku",
  prompt="Collect OS versions for all online sensors in organization '{org_name}' (OID: {oid}).
    Optional platform filter: {platform or 'none'}
    Return: OS version details for each sensor."
)
```

**CRITICAL**: Spawn ALL agents in a SINGLE message with multiple Task tool calls to run them in parallel:

```
<message with multiple Task blocks>
  Task 1: Collect from org 1
  Task 2: Collect from org 2
  Task 3: Collect from org 3
  ...
</message>
```

Do NOT spawn them sequentially - that defeats the purpose of parallelization.

### Step 4: Aggregate Results

Once all agents return:
1. Parse each agent's findings
2. Count total sensors inventoried
3. Group by organization and platform
4. Create OS version distribution summary

### Step 5: Generate Report

Present a unified report with:
- **Executive Summary**: Total sensors, OS distribution
- **Per-Org Breakdown**: Sensors and OS versions by org
- **Platform Summary**: Breakdown by Windows/Linux/macOS
- **Version Details**: Specific versions found

## Example Workflow

**User Query**: "Show me what operating systems are running across my fleet"

**Step 1**: Get org list
```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: list_user_orgs
    - Parameters: {}
    - Return: RAW"
)
```

**Step 2**: Spawn parallel agents (example with 3 orgs)
```
# Single message with 3 Task calls
Task(subagent_type="lc-essentials:sensor-os-collector", prompt="Collect OS versions for org1 (OID: uuid1)...")
Task(subagent_type="lc-essentials:sensor-os-collector", prompt="Collect OS versions for org2 (OID: uuid2)...")
Task(subagent_type="lc-essentials:sensor-os-collector", prompt="Collect OS versions for org3 (OID: uuid3)...")
```

**Step 3**: Aggregate results
```
org1: 15 sensors inventoried
  - Windows 10 (10.0.19045): 8 sensors
  - Windows 11 (10.0.22631): 5 sensors
  - Linux (Ubuntu 22.04): 2 sensors
org2: 8 sensors inventoried
  - macOS 14.0: 6 sensors
  - Windows 11: 2 sensors
org3: 3 sensors offline, 0 inventoried
```

**Step 4**: Present report
```markdown
## Sensor OS Inventory

**Total: 23 sensors inventoried across 3 organizations**
**3 sensors offline (not inventoried)**

### OS Distribution Summary
| OS | Version | Count |
|----|---------|-------|
| Windows 10 | 10.0.19045 | 8 |
| Windows 11 | 10.0.22631 | 7 |
| macOS | 14.0 | 6 |
| Linux (Ubuntu) | 22.04 | 2 |

### Per-Organization Breakdown

#### org1 (15 sensors online)
- Windows 10 (10.0.19045): 8 sensors
- Windows 11 (10.0.22631): 5 sensors
- Linux (Ubuntu 22.04): 2 sensors

#### org2 (8 sensors online)
- macOS 14.0: 6 sensors
- Windows 11 (10.0.22631): 2 sensors

#### org3 (0 sensors online)
- 3 sensors offline - unable to collect OS version

### Notes
- OS version data requires sensors to be online
- 3 offline sensors were not inventoried
```

## Handling Large Result Sets

When `list_user_orgs` returns a `resource_link`:

```bash
bash ./marketplace/plugins/lc-essentials/scripts/analyze-lc-result.sh "<resource_link>"
jq -r '.orgs[] | "\(.oid)|\(.name)"' /tmp/lc-result-*.json
```

## Performance Tips

1. **Always spawn agents in parallel** - Use a single message with multiple Task calls
2. **Limit scope if needed** - For quick checks, allow user to specify specific orgs
3. **Use Haiku model** - OS collection is straightforward data gathering
4. **Handle errors gracefully** - If one org fails, continue with others
5. **Report offline sensors** - Make it clear which sensors couldn't be inventoried

## Error Handling

If an agent fails:
- Log the error for that organization
- Continue processing other organizations
- Include error summary in final report
- Don't let one org failure block the entire report

Common errors:
- **Sensor offline**: Cannot collect OS version from offline sensors
- **Timeout**: Live commands have 30s timeout - some sensors may not respond
- **Permission denied**: API key may lack required permissions

## Report Format Template

```markdown
## Sensor OS Inventory

**Summary**: {Total} sensors inventoried across {N} organizations
**Offline**: {M} sensors offline (not inventoried)

### OS Distribution Summary
| OS | Version | Count |
|----|---------|-------|
| {os_name} | {version} | {count} |
...

### Per-Organization Breakdown

#### {Org Name 1} ({count} sensors online)
{OS breakdown for this org}

#### {Org Name 2} ({count} sensors online)
{OS breakdown for this org}

### Organizations with No Online Sensors
- {Org Name X}: {N} sensors offline

### Notes
- {Any relevant context}
```

## Important Constraints

- **Parallel Execution**: ALWAYS spawn agents in parallel (single message, multiple Tasks)
- **OID Format**: Organization ID is a UUID, not the org name
- **Online Only**: `os_version` command only works on online sensors
- **Timeout**: Live commands timeout after 30 seconds
- **Model**: Always use "haiku" for the sub-agents
- **Error Tolerance**: Continue with partial results if some orgs or sensors fail

## Related Functions

From `limacharlie-call` skill:
- `list_user_orgs` - Get organizations
- `list_sensors` - Get all sensors (with online_only filter)
- `get_online_sensors` - Get online sensors
- `get_os_version` - Send os_version task to sensor (used by sub-agent)
