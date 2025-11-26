# LimaCharlie Essentials Agents

This directory contains specialized agents for the lc-essentials plugin. These agents handle specific types of queries with optimized models and workflows.

## Available Agents

### sensor-health-reporter

**Model**: Claude Haiku (fast and cost-effective)

**Purpose**: Check sensor health for a **single** LimaCharlie organization. Designed to be spawned in parallel by the `sensor-health` skill.

**When to Use**:
This agent is **not invoked directly by users**. Instead, it's spawned in parallel (one instance per org) by the `sensor-health` skill when users ask about:
- Sensor connectivity status
- Data availability and reporting
- Offline or non-responsive sensors
- Sensor health across organizations

**Architecture Role**:
- **Parent Skill**: `sensor-health` (orchestrates parallel execution)
- **This Agent**: Checks ONE organization's sensors
- **Parallelization**: Multiple instances run simultaneously, one per org

**Expected Input**:
Receives a prompt specifying:
- Organization name
- Organization ID (UUID)
- Check type (e.g., "online but no data", "offline for X days")
- Time window (e.g., "last hour", "7 days")

**Output Format**:
Returns concise findings for its assigned org only:
```markdown
### {Org Name}

**Status**: Found N sensors | No issues found

Sensors with issues (N):
- sensor-id-1
- sensor-id-2
...
```

**Key Features**:
- **Single-Org Focus**: Only checks the one organization specified in its prompt
- **Fast Execution**: Uses Haiku model + parallel API calls within the org
- **Concise Output**: Returns findings only, no aggregation or analysis
- **Error Tolerance**: Handles API errors gracefully, reports partial results
- **Designed for Parallelism**: Optimized to run alongside other instances

**Skills Used**:
- `lc-essentials:limacharlie-call` - For API operations

**How It Works**:
1. Extracts org ID, check type, and time window from prompt
2. Calculates timestamps using bash date commands
3. Makes parallel API calls to gather sensor data for the org
4. Filters results based on check criteria
5. Returns concise findings for this org only (parent skill aggregates)

### dr-replay-tester

**Model**: Claude Haiku (fast and cost-effective)

**Purpose**: Test D&R rules via historical replay against a **single** LimaCharlie organization. Designed to be spawned in parallel by the `detection-engineering` skill for multi-org testing.

**When to Use**:
This agent is **not invoked directly by users**. Instead, it's spawned in parallel (one instance per org) by the `detection-engineering` skill when users want to:
- Test a D&R rule across multiple organizations
- Validate detection logic against real historical data
- Compare rule performance across different environments

**Architecture Role**:
- **Parent Skill**: `detection-engineering` (orchestrates parallel execution)
- **This Agent**: Tests rule against ONE organization's historical data
- **Parallelization**: Multiple instances run simultaneously, one per org

**Expected Input**:
Receives a prompt specifying:
- Organization name and ID (UUID)
- Detection rule (YAML/dict)
- Response rule (optional)
- Time window (e.g., "last 1 hour", "last 24 hours")
- Sensor selector (optional, e.g., `plat == "windows"`)

**Output Format**:
Returns **summarized** findings (not all matches):
```markdown
### {Org Name}

**Match Statistics**:
- Events processed: {N}
- Events matched: {M}
- Match rate: {X.X%}

**Sample Matches** (showing 5 of {total}):
1. {hostname}: {process} - {command_line_snippet}
...

**Common Patterns**:
- Top hostname: {hostname} ({N} matches)
- Top process: {process_name} ({N} matches)

**Assessment**: {Brief assessment}
```

**Key Features**:
- **Single-Org Focus**: Only tests against the one organization specified
- **Result Summarization**: Returns stats and top 5 samples, not all hits
- **Pattern Analysis**: Identifies common patterns in matches (hostnames, processes)
- **Fast Execution**: Uses Haiku model for quick turnaround
- **Designed for Parallelism**: Optimized to run alongside other instances

**Skills Used**:
- `lc-essentials:limacharlie-call` - For `replay_dr_rule` API calls

**How It Works**:
1. Extracts org ID, detection rule, time window, and selector from prompt
2. Converts time window to `last_seconds` parameter
3. Runs `replay_dr_rule` with extracted parameters
4. Analyzes results: calculates stats, extracts top samples, finds patterns
5. Returns concise summary for this org only (parent skill aggregates)

---

## Agent Architecture

All agents follow Claude Code best practices:
- Single responsibility per agent
- Clear frontmatter with name, description, model, and skills
- Structured system prompts with role, instructions, examples, and constraints
- Optimized model selection (Haiku for simple tasks, Sonnet for complex analysis)
- Efficient tool usage with parallel operations where possible

## Adding New Agents

To add a new agent to this plugin:

1. Create a new `.md` file in this directory
2. Add YAML frontmatter with required fields:
   ```yaml
   ---
   name: agent-name
   description: What it does and when to use it
   model: haiku|sonnet|opus
   skills:
     - lc-essentials:skill-name
   ---
   ```
3. Write a clear system prompt (2-4 paragraphs minimum)
4. Update this README with the new agent's details
5. Update the main plugin README with usage examples

## Best Practices

- **Model Selection**: Use Haiku for straightforward data gathering and reporting, Sonnet for complex analysis
- **Skill Access**: Only include skills the agent actually needs
- **Clear Descriptions**: The description field determines when Claude invokes the agent
- **Examples**: Include concrete examples of queries the agent handles
- **Progress Tracking**: Use TodoWrite for multi-step operations
- **Error Handling**: Handle API errors gracefully and continue with partial results
