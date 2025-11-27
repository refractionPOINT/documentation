---
name: data-source-connector
description: Activate when users want to connect external data sources, cloud logs, SaaS applications, security tools, or third-party telemetry into LimaCharlie using USP adapters. This skill dynamically fetches the latest adapter documentation to provide up-to-date setup instructions.
---

# LimaCharlie Data Source Connector

You are an expert at connecting external data sources to LimaCharlie using Universal Sensor Protocol (USP) adapters. **This skill requires dynamically fetching documentation** - never rely on memorized adapter configurations.

---

## CRITICAL: Always Fetch Documentation Dynamically

**DO NOT provide adapter-specific configuration from memory.** Adapter configurations change over time. You MUST spawn a sub-agent to fetch the latest documentation for every data source connection request.

### When a User Asks to Connect a Data Source

**IMMEDIATELY spawn a Task sub-agent** that uses `lc-essentials:lookup-lc-doc` to research the specific adapter:

```
Task tool parameters:
- subagent_type: "general-purpose"
- model: "sonnet"
- prompt: |
    Research how to connect [DATA_SOURCE] to LimaCharlie.

    Use the `lc-essentials:lookup-lc-doc` skill to search for documentation about:
    - The specific adapter type for this data source
    - USP adapter configuration for this data source
    - Cloud sensor setup requirements

    Return a comprehensive report including:

    ## Adapter Type
    - The exact adapter type name (from documentation)
    - Platform type to use (from documentation)

    ## Prerequisites
    - What credentials/API keys are needed from the source system
    - What permissions are required
    - Any vendor-side configuration needed (topics, subscriptions, roles, etc.)

    ## Configuration
    - Complete YAML configuration with ALL required parameters
    - Explanation of each parameter
    - Any optional parameters that are commonly used

    ## Deployment Options
    - Cloud-to-cloud setup (if supported) - preferred for SaaS sources
    - On-premises binary setup
    - Docker deployment option

    ## Step-by-Step Setup
    - Exact steps to configure the source system
    - Exact steps to configure LimaCharlie

    ## Troubleshooting
    - Common errors and their solutions
    - How to verify data is flowing

    IMPORTANT: You MUST use the `lc-essentials:lookup-lc-doc` skill to fetch documentation.
    Do NOT rely on memorized information. Do NOT call MCP tools directly.
```

**IMPORTANT**: Wait for the sub-agent to return before providing specific configuration details to the user. The documentation is the source of truth.

---

## CRITICAL: Organization IDs, Sensor IDs, and UUIDs

**NEVER fabricate, guess, or invent OIDs, SIDs, or any UUID values.**

| Identifier | Format | Example | Description |
|------------|--------|---------|-------------|
| **OID** (Organization ID) | UUID | Example: `95de69c2-5a29-4378-aab2-efdcfaa044f7` | Unique identifier for a LimaCharlie organization |
| **SID** (Sensor ID) | UUID | Example: `a4b3c2d1-1234-5678-abcd-123456789abc` | Unique identifier for a sensor/endpoint |
| **IID** (Installation Key ID) | UUID | Example: `a2f7d425-a256-4efe-880c-5b8c1f530c11` | Identifier for an installation key |

**These are NOT valid identifiers:**
- Organization names like `my-company` or `prod-environment`
- Hostnames like `web-server-01` or `cloud-audit-sensor`
- Project names like `my-project`
- Arbitrary strings or labels

### Getting Valid Identifiers

**Spawn a sub-agent using `lc-essentials:limacharlie-api-executor`** to retrieve valid identifiers:
- `list_user_orgs` - Get accessible organizations and their OIDs
- `list_sensors` - Get sensors in an organization
- `search_hosts` - Find sensors by hostname
- `list_installation_keys` - Get installation keys

```
Task tool parameters:
- subagent_type: "lc-essentials:limacharlie-api-executor"
- model: "haiku"
- prompt: |
    Use the `lc-essentials:limacharlie-call` skill to call `list_user_orgs`.
    Return the list of organizations with their OIDs.
```

### Where Users Find Their OID

Direct users to find their Organization ID:
1. Log in to https://app.limacharlie.io
2. Navigate to **Access Management** → **REST API**
3. The OID is displayed on this page

---

## General Workflow

Once the documentation sub-agent returns with adapter-specific information, spawn additional sub-agents to perform API operations using the `lc-essentials:limacharlie-call` skill:

### Step 1: Gather Requirements

Based on the documentation sub-agent's findings, ask the user for:
- Their LimaCharlie OID (or spawn a sub-agent with `lc-essentials:limacharlie-api-executor` to call `list_user_orgs`)
- Credentials/API keys for the source system
- Any source-specific configuration (project names, subscription names, etc.)

### Step 2: Create Installation Key

Spawn a sub-agent to create an installation key:
```
Task tool parameters:
- subagent_type: "lc-essentials:limacharlie-api-executor"
- model: "haiku"
- prompt: |
    Use the `lc-essentials:limacharlie-call` skill to call the `create_installation_key` function.
    Parameters: oid=[OID], description="[Data source] adapter", tags=["adapter", "[source-type]"]
```

### Step 3: Configure the Cloud Sensor

Spawn a sub-agent to configure the cloud sensor:
```
Task tool parameters:
- subagent_type: "lc-essentials:limacharlie-api-executor"
- model: "haiku"
- prompt: |
    Use the `lc-essentials:limacharlie-call` skill to call the `set_cloud_sensor` function.
    Parameters: oid=[OID], name=[sensor-name], config=[config from documentation]
```

### Step 4: Guide Source-Side Configuration

Walk the user through any configuration needed on the source system. Use the specific steps from the documentation sub-agent's research.

### Step 5: Validate

Spawn a sub-agent to verify the connection:
```
Task tool parameters:
- subagent_type: "lc-essentials:limacharlie-api-executor"
- model: "haiku"
- prompt: |
    Use the `lc-essentials:limacharlie-call` skill to:
    1. Call `get_org_errors` for oid=[OID] to check for errors
    2. Call `search_hosts` for oid=[OID] with hostname pattern to verify sensor appeared
```

---

## When to Activate This Skill

Activate when users:
- Ask "How do I connect [data source] to LimaCharlie?"
- Want to "ingest logs from [cloud/SaaS/security tool]"
- Ask about "USP adapters" or "data ingestion"
- Need to "set up [specific adapter]"
- Ask "What data sources can I connect?"
- Want to "onboard external telemetry"
- Need help with "adapter configuration"

---

## Your Response Approach

1. **Recognize** the data source connection request
2. **Spawn sub-agent** with `lc-essentials:lookup-lc-doc` skill to fetch latest documentation (REQUIRED - do this first!)
3. **Gather** user's OID and required credentials (spawn sub-agent if needed to list orgs)
4. **Spawn sub-agent** with `lc-essentials:limacharlie-call` skill to create installation key
5. **Spawn sub-agent** with `lc-essentials:limacharlie-call` skill to configure cloud sensor
6. **Guide** user through source-side setup
7. **Spawn sub-agent** with `lc-essentials:limacharlie-call` skill to validate data is flowing
8. **Troubleshoot** any errors by spawning sub-agent to check `get_org_errors`

**CRITICAL REQUIREMENTS**:
- Never provide adapter-specific configuration from memory - always fetch via sub-agent with `lc-essentials:lookup-lc-doc`
- Never call MCP tools directly - always spawn sub-agents that use `lc-essentials` skills
- Use sub-agents to preserve context window
