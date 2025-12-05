---
name: add-new-skill
description: Create a new skill for the lc-essentials plugin following best practices and framework conventions. Use when adding LimaCharlie API operations, orchestration workflows, or specialized capabilities to the plugin.
allowed-tools: Task, Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, TodoWrite
argument-hint: "description of what the skill should do"
---

# Add New Skill to lc-essentials Plugin

You are creating a new skill for the **lc-essentials** Claude Code plugin based on the user's description below.

## User's Skill Description

**The user wants a skill that:** $ARGUMENTS

Your job is to create a skill that fulfills this description while conforming to the established framework patterns and conventions.

## Step 1: Research Claude Code Skills Best Practices

First, use the Task tool with `subagent_type="claude-code-guide"` to look up:
- Official Claude Code documentation on creating skills (SKILL.md format)
- Best practices for skill descriptions and discovery optimization
- How skills interact with sub-agents and the Task tool

## Step 2: Review Plugin Framework Documentation

Read these files to understand the lc-essentials framework:
- `marketplace/plugins/lc-essentials/CALLING_API.md` - API execution architecture
- `marketplace/plugins/lc-essentials/SKILL_TEMPLATE.md` - Template structure
- `marketplace/plugins/lc-essentials/agents/README.md` - Sub-agent patterns
- `marketplace/plugins/lc-essentials/skills/limacharlie-call/SKILL.md` - Core API skill reference

## Step 3: CRITICAL FRAMEWORK RULES

**Every skill in lc-essentials MUST follow these rules. Violations will break the plugin.**

### Rule 1: NEVER Call MCP Server Directly (CRITICAL)

**WRONG - Do not include this pattern:**
```
mcp__plugin_lc-essentials_limacharlie__lc_call_tool(
  tool_name="function_name",
  parameters={...}
)
```

**CORRECT - Always delegate via Task tool:**
```
Task(
  subagent_type="lc-essentials:limacharlie-api-executor",
  model="haiku",
  prompt="Execute LimaCharlie API call:
    - Function: function_name
    - Parameters: {\"oid\": \"...\", ...}
    - Return: RAW"
)
```

**Why**: Direct MCP calls create bottlenecks, prevent parallel execution, lose cost optimization.

### Rule 2: NEVER Generate LCQL Queries Manually (CRITICAL)

**WRONG:**
```
run_lcql_query(query="-24h | * | NEW_PROCESS | ...")
```

**CORRECT - Always use two-step workflow:**
```
1. generate_lcql_query(oid="...", query="Natural language description")
2. run_lcql_query(oid="...", query=<generated_query>)
```

**Why**: LCQL uses unique pipe-based syntax validated against org-specific schemas. Manual queries WILL fail.

### Rule 3: NEVER Generate D&R Rules Manually (CRITICAL)

**WRONG:**
```yaml
detection:
  op: is
  event: NEW_PROCESS
  ...
```

**CORRECT - Use AI generation tools:**
```
1. generate_dr_rule_detection() → Generate detection YAML
2. generate_dr_rule_respond() → Generate response YAML
3. validate_dr_rule_components() → Validate before deploying
4. set_dr_general_rule() → Deploy validated rules
```

**Why**: D&R rule YAML syntax is complex and validated against org schemas. Manual syntax produces errors.

### Rule 4: NEVER Calculate Timestamps Manually (CRITICAL)

**WRONG:**
```
timestamp = 1699574400  # LLMs get this wrong
```

**CORRECT - Use bash date commands:**
```bash
date +%s                    # Current time (seconds)
date -d '1 hour ago' +%s    # 1 hour ago
date -d '7 days ago' +%s    # 7 days ago
date -d '2025-01-15 00:00:00 UTC' +%s  # Specific date
```

**Why**: LLMs consistently produce incorrect timestamp values.

### Rule 5: Organization ID (OID) is UUID, NOT Name

**WRONG:**
```
oid: "my-org-name"
```

**CORRECT:**
```
oid: "c1ffedc0-ffee-4a1e-b1a5-abc123def456"
```

**How to Get**: Call `list_user_orgs` to map org names to UUIDs.

**Exception** - User-level operations that DON'T need OID:
- `list_user_orgs` - Lists all accessible organizations
- `create_org` - Creates new organization
- `get_platform_names` - Gets global platform list

### Rule 6: Always Specify Return Field for API Executor

When delegating to `limacharlie-api-executor`, you MUST specify what data to return:

```
- Return: RAW              # Full API response
- Return: Count of sensors  # Extract/summarize specific data
- Return: Only hostnames   # Filter response
```

### Rule 7: Use Sub-Agents for Parallel Operations

When processing multiple items (organizations, detection layers, etc.):
- Spawn ONE agent per item in PARALLEL
- Each agent focuses on ONE item
- Parent skill aggregates results

**Example pattern:**
```
Task 1 → Check Org A (parallel)
Task 2 → Check Org B (parallel)
Task 3 → Check Org C (parallel)
...then aggregate all results
```

### Rule 8: Use Server-Side Filtering (selector & online_only)

For sensor queries, use `selector` parameter with bexpr syntax:
```
selector="plat == `windows` and hostname matches `^prod-`"
online_only=true
```

Both are evaluated server-side BEFORE results are returned.

## Step 4: Skill Structure

Create the skill in: `marketplace/plugins/lc-essentials/skills/{skill-name}/SKILL.md`

Required YAML frontmatter:
```yaml
---
name: skill-name-in-kebab-case
description: Clear description with keywords, use cases, and trigger words. Include action verbs (list, get, create, delete) and domain keywords (sensor, rule, detection). Maximum 1024 characters.
allowed-tools: Task, Read, Bash
---
```

**Model Selection** (specified at agent level, not skill level):
- **Haiku**: Fast, cost-effective for straightforward operations (data gathering, API calls, simple analysis)
- **Sonnet**: Complex analysis, entity extraction, multi-step reasoning
- **Opus**: Rarely needed (only for extremely complex tasks)

## Step 5: Skill Categories

Determine which category your skill falls into:

### Category A: API Wrapper Skill
Simple skills that wrap a single API operation.
- Validate parameters
- Delegate to `limacharlie-api-executor`
- Format and return results

### Category B: Orchestration Skill
Complex skills that coordinate multiple operations.
- Parse user queries
- Fetch required data (e.g., org list)
- Spawn parallel sub-agents (one per item)
- Aggregate and format results

### Category C: Research Skill
Skills that search and combine information.
- Search multiple sources with various keywords
- Read multiple files to gather complete info
- Combine information from multiple sources

## Step 6: Create Supporting Files (if needed)

If your skill needs a dedicated sub-agent, create it in:
`marketplace/plugins/lc-essentials/agents/{agent-name}.md`

Agent frontmatter:
```yaml
---
name: agent-name
description: What it does and when to use (determines when Claude invokes it)
model: haiku|sonnet|opus
skills:
  - lc-essentials:skill-name
---
```

## Step 7: Update Documentation

After creating the skill:
1. Add entry to `marketplace/plugins/lc-essentials/SKILLS_SUMMARY.md`
2. If creating an agent, update `marketplace/plugins/lc-essentials/agents/README.md`

## Your Task

Based on the user's description above, create a skill that fulfills their requirements.

**Workflow:**
1. Research Claude Code skills documentation using the `claude-code-guide` agent
2. Read the plugin framework files listed in Step 2
3. Analyze the user's description to determine:
   - What LimaCharlie API functions are needed
   - Which skill category applies (API Wrapper, Orchestration, or Research)
   - Whether a dedicated sub-agent is needed
   - An appropriate skill name (kebab-case)
4. Ask clarifying questions if the description is ambiguous
5. Create the skill following ALL rules in Step 3
6. Create any supporting agents if needed
7. Update documentation files (SKILLS_SUMMARY.md, agents/README.md if applicable)
8. Report what was created with a summary of the skill's capabilities

**Remember:** Every rule in Step 3 is CRITICAL. If the skill violates any of these rules, it WILL break the plugin or produce incorrect results.
