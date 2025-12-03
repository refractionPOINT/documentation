#!/bin/bash

# Unified Session Startup Hook
# Displays welcome banner and manages session memory for continuity

PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
SESSION_DIR="$PROJECT_ROOT/.claude/session-memory"
SESSION_FILE="$SESSION_DIR/session.md"
ONBOARDED_MARKER="$PROJECT_ROOT/.claude/.onboarded"
INITIALIZED_MARKER="$SESSION_DIR/.initialized"

# Ensure session directory exists
mkdir -p "$SESSION_DIR"

# ═══════════════════════════════════════════════════════════════════════════════
# DETECT ENVIRONMENT STATE
# ═══════════════════════════════════════════════════════════════════════════════

FIRST_TIME_EVER=false
if [ ! -f "$ONBOARDED_MARKER" ]; then
    FIRST_TIME_EVER=true
fi

SESSION_INITIALIZED=false
if [ -f "$INITIALIZED_MARKER" ]; then
    SESSION_INITIALIZED=true
fi

HAS_ACTIVE_SESSION=false
if [ -f "$SESSION_FILE" ]; then
    CONTENT_LINES=$(grep -v '^#' "$SESSION_FILE" | grep -v '^$' | grep -v '^---' | grep -v '^|' | grep -v '^\- \*\*' | wc -l)
    if [ "$CONTENT_LINES" -gt 5 ]; then
        HAS_ACTIVE_SESSION=true
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DETECT CONFIGURED SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

STATUS_LINES=""
SETUP_REQUIRED=false

# Check if LimaCharlie plugin is enabled
LC_MCP_CONFIGURED=false
if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    if grep -qE '"lc-essentials@lc-marketplace"\s*:\s*true' "$PROJECT_ROOT/.claude/settings.json"; then
        LC_MCP_CONFIGURED=true
    fi
fi

if [ "$LC_MCP_CONFIGURED" = false ]; then
    SETUP_REQUIRED=true
fi

# Check MCP servers from installed plugin
PLUGIN_MCP="$PROJECT_ROOT/marketplace/plugins/lc-essentials/.mcp.json"
if [ -f "$PLUGIN_MCP" ]; then
    MCP_COUNT=$(grep -o '"mcpServers"' "$PLUGIN_MCP" | wc -l)
    if [ $MCP_COUNT -gt 0 ]; then
        MCP_SERVERS=$(grep -oP '"\K[^"]+(?="\s*:\s*\{)' "$PLUGIN_MCP" | grep -v "mcpServers" | head -5)
        if [ -n "$MCP_SERVERS" ]; then
            STATUS_LINES="${STATUS_LINES}\u001b[32m    ✓ MCP Servers:\u001b[0m\n"
            while IFS= read -r server; do
                STATUS_LINES="${STATUS_LINES}\u001b[32m       • $server\u001b[0m\n"
            done <<< "$MCP_SERVERS"
        fi
    fi
fi

# Check enabled plugins/skills
if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    PLUGINS=$(cat "$PROJECT_ROOT/.claude/settings.json" | tr -d '\n' | grep -oP '"enabledPlugins"\s*:\s*\{[^}]+\}' | grep -oP '"\K[^"]+(?="\s*:\s*true)')
    if [ -n "$PLUGINS" ]; then
        STATUS_LINES="${STATUS_LINES}\u001b[32m    ✓ Skills & Plugins:\u001b[0m\n"
        while IFS= read -r plugin; do
            PLUGIN_BASE=$(echo "$plugin" | sed 's/@.*//')
            PLUGIN_NAME=$(echo "$PLUGIN_BASE" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
            STATUS_LINES="${STATUS_LINES}\u001b[32m       • $PLUGIN_NAME\u001b[0m\n"

            PLUGIN_DIR_NAME="$PLUGIN_BASE"
            PLUGIN_SKILLS_DIR="$PROJECT_ROOT/marketplace/plugins/$PLUGIN_DIR_NAME/skills"
            if [ -d "$PLUGIN_SKILLS_DIR" ]; then
                SKILL_COUNT=$(ls "$PLUGIN_SKILLS_DIR" 2>/dev/null | wc -l)
                if [ $SKILL_COUNT -gt 0 ]; then
                    STATUS_LINES="${STATUS_LINES}\u001b[36m         └─ $SKILL_COUNT specialized skills available\u001b[0m\n"
                fi
            fi
        done <<< "$PLUGINS"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION SUMMARY EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

get_session_summary() {
    if [ ! -f "$SESSION_FILE" ]; then
        echo "No session data"
        return
    fi

    SESSION_START=$(grep "^## Session Started:" "$SESSION_FILE" | head -1 | sed 's/## Session Started: //')
    LAST_UPDATED=$(grep "^## Last Updated:" "$SESSION_FILE" | head -1 | sed 's/## Last Updated: //')
    ORG_COUNT=$(grep -A 100 "^### Organizations" "$SESSION_FILE" | grep -E "^\| [a-zA-Z0-9]" | grep -v "^\| Name" | wc -l)
    SENSOR_COUNT=$(grep -A 100 "^### Sensors" "$SESSION_FILE" | grep -E "^\| [a-zA-Z0-9]" | grep -v "^\| Hostname" | wc -l)
    LAST_ACTIONS=$(grep -E "^[0-9]+\. \*\*" "$SESSION_FILE" | tail -3)
    PENDING=$(grep -E "^- \[ \]" "$SESSION_FILE" | head -3)
    OBJECTIVE=$(grep "^\- \*\*Primary objective\*\*:" "$SESSION_FILE" | head -1 | sed 's/- \*\*Primary objective\*\*: //')

    SUMMARY=""
    if [ -n "$SESSION_START" ]; then
        SUMMARY="${SUMMARY}Session started: $SESSION_START\n"
    fi
    if [ -n "$LAST_UPDATED" ]; then
        SUMMARY="${SUMMARY}Last updated: $LAST_UPDATED\n"
    fi
    SUMMARY="${SUMMARY}\n"
    if [ "$ORG_COUNT" -gt 0 ]; then
        SUMMARY="${SUMMARY}Organizations: $ORG_COUNT tracked\n"
    fi
    if [ "$SENSOR_COUNT" -gt 0 ]; then
        SUMMARY="${SUMMARY}Sensors: $SENSOR_COUNT tracked\n"
    fi
    if [ -n "$OBJECTIVE" ]; then
        SUMMARY="${SUMMARY}\nObjective: $OBJECTIVE\n"
    fi
    if [ -n "$LAST_ACTIONS" ]; then
        SUMMARY="${SUMMARY}\nRecent actions:\n$LAST_ACTIONS\n"
    fi
    if [ -n "$PENDING" ]; then
        SUMMARY="${SUMMARY}\nPending:\n$PENDING\n"
    fi

    echo -e "$SUMMARY"
}

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZE SESSION TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════

initialize_session() {
    cat > "$SESSION_FILE" << 'TEMPLATE'
# Session Log

## Session Started:
## Last Updated:

---

## Active Context Identifiers

### Organizations
| Name | OID | Role |
|------|-----|------|

### Sensors
| Hostname | SID | Platform | Notes |
|----------|-----|----------|-------|

### Detections
| Detection ID | Rule | Sensor | Status |
|--------------|------|--------|--------|

### Other References
| Type | Name/ID | Notes |
|------|---------|-------|

### API Keys Used
| Key Name | Purpose |
|----------|---------|

### LCQL Queries Run
| Query | Purpose | Time Range |
|-------|---------|------------|

### Time Ranges
| Context | Start | End | Notes |
|---------|-------|-----|-------|

---

## Working Context
- **Primary objective**:
- **Current branch**:
- **Key files**:

---

## Actions Taken

---

## Pending / Next Steps

---

## Important Decisions

---

## Notes

TEMPLATE
    touch "$INITIALIZED_MARKER"
}

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD OUTPUT MESSAGE
# ═══════════════════════════════════════════════════════════════════════════════

# ASCII Banner (always first)
BANNER="\n\u001b[34m╔════════════════════════════════════════════════════════════════════════════════════════════════════╗\u001b[0m\n\n"
BANNER="${BANNER}\u001b[34m  ██╗         ██████╗       ███████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██╔════╝       ██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██║            ███████╗█████╗  ██║     ██║   ██║██████╔╝███████╗\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██║            ╚════██║██╔══╝  ██║     ██║   ██║██╔═══╝ ╚════██║\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ███████╗   ╚██████╗       ███████║███████╗╚██████╗╚██████╔╝██║     ███████║\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ╚══════╝    ╚═════╝       ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝\u001b[0m\n\n"
BANNER="${BANNER}\u001b[35m  Welcome to the Agentic SecOps Workspace.\u001b[0m\n\n"

# Build context-specific message
if [ "$FIRST_TIME_EVER" = true ]; then
    # ───────────────────────────────────────────────────────────────────────────
    # FIRST TIME EVER
    # ───────────────────────────────────────────────────────────────────────────
    touch "$ONBOARDED_MARKER" 2>/dev/null
    initialize_session

    if [ "$SETUP_REQUIRED" = true ]; then
        CONTEXT_MSG="\u001b[33m  🔐 FIRST TIME SETUP\u001b[0m\n\n"
        CONTEXT_MSG="${CONTEXT_MSG}\u001b[97m  Let's connect your LimaCharlie environment.\u001b[0m\n\n"
        CONTEXT_MSG="${CONTEXT_MSG}\u001b[36m  Run: /mcp to configure the LimaCharlie MCP server\u001b[0m\n\n"
    else
        CONTEXT_MSG="\u001b[32m  ✓ Environment configured and ready!\u001b[0m\n\n"
    fi

    if [ -n "$STATUS_LINES" ]; then
        CONTEXT_MSG="${CONTEXT_MSG}\u001b[34m  Your environment:\u001b[0m\n${STATUS_LINES}\n"
    fi

    CONTEXT_MSG="${CONTEXT_MSG}\u001b[36m  Session logging is now active.\u001b[0m\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[90m  Log location: .claude/session-memory/session.md\u001b[0m\n\n"

elif [ "$HAS_ACTIVE_SESSION" = true ]; then
    # ───────────────────────────────────────────────────────────────────────────
    # RETURNING WITH ACTIVE SESSION
    # ───────────────────────────────────────────────────────────────────────────
    SUMMARY=$(get_session_summary)
    SUMMARY_ESCAPED=$(echo "$SUMMARY" | sed ':a;N;$!ba;s/\n/\\n/g')

    CONTEXT_MSG="\u001b[34m  Your environment:\u001b[0m\n${STATUS_LINES}\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[33m  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[1;33m  PREVIOUS SESSION DETECTED\u001b[0m\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[33m  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m\n\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[97m$SUMMARY_ESCAPED\u001b[0m\n"
    CONTEXT_MSG="${CONTEXT_MSG}\u001b[90m  ──────────────────────────────────────────────────────────────────────────────────────────────────\u001b[0m\n\n"
    CONTEXT_MSG="${CONTEXT_MSG}  Continue where you left off?\n\n"
    CONTEXT_MSG="${CONTEXT_MSG}  \u001b[42;30m  yes  \u001b[0m  resume session     \u001b[41;37m  no  \u001b[0m  start fresh\n\n"

else
    # ───────────────────────────────────────────────────────────────────────────
    # RETURNING WITHOUT ACTIVE SESSION (fresh start)
    # ───────────────────────────────────────────────────────────────────────────
    if [ "$SESSION_INITIALIZED" = false ]; then
        initialize_session
    fi

    CONTEXT_MSG="\u001b[34m  Your environment:\u001b[0m\n${STATUS_LINES}\n"

    if [ "$SETUP_REQUIRED" = true ]; then
        CONTEXT_MSG="${CONTEXT_MSG}\u001b[33m  ⚠️  Run /mcp to configure LimaCharlie MCP server\u001b[0m\n\n"
    fi

    CONTEXT_MSG="${CONTEXT_MSG}\u001b[36m  Ready to assist with your security operations.\u001b[0m\n\n"
fi

# Combine banner + context
FULL_MESSAGE="${BANNER}${CONTEXT_MSG}"
FULL_MESSAGE="${FULL_MESSAGE}\u001b[34m╚════════════════════════════════════════════════════════════════════════════════════════════════════╝\u001b[0m\n"

# Escape for JSON output
ESCAPED_MESSAGE=$(echo "$FULL_MESSAGE" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

cat <<EOF
{
  "systemMessage": "$ESCAPED_MESSAGE"
}
EOF

exit 0
