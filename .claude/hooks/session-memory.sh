#!/bin/bash

# SessionStart Hook: Display Banner
# Context injection is handled by @import in CLAUDE.md - this just shows the welcome banner

PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
SESSION_FILE="$PROJECT_ROOT/.claude/session-memory/session.md"

# ═══════════════════════════════════════════════════════════════════════════════
# DETECT ENVIRONMENT STATUS
# ═══════════════════════════════════════════════════════════════════════════════

STATUS_LINES=""

# Check MCP servers from installed plugin
PLUGIN_MCP="$PROJECT_ROOT/marketplace/plugins/lc-essentials/.mcp.json"
if [ -f "$PLUGIN_MCP" ]; then
    # Extract only top-level keys under mcpServers (not nested objects like "headers")
    MCP_SERVERS=$(python3 -c "
import json, sys
try:
    with open('$PLUGIN_MCP') as f:
        data = json.load(f)
    servers = data.get('mcpServers', {})
    for name in servers.keys():
        print(name)
except: pass
" 2>/dev/null)
    if [ -n "$MCP_SERVERS" ]; then
        STATUS_LINES="${STATUS_LINES}\u001b[32m    ✓ MCP Servers:\u001b[0m\n"
        while IFS= read -r server; do
            STATUS_LINES="${STATUS_LINES}\u001b[32m       • $server\u001b[0m\n"
        done <<< "$MCP_SERVERS"
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
# DETECT SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

HAS_ACTIVE_SESSION=false
SESSION_SUMMARY=""

if [ -f "$SESSION_FILE" ]; then
    # Extract session data - use grep with proper pattern matching
    # Session start: extract value after "## Session Started: " (must have content after colon+space)
    SESSION_START=$(grep "^## Session Started: ." "$SESSION_FILE" | head -1 | sed 's/^## Session Started: //')
    LAST_UPDATED=$(grep "^## Last Updated: ." "$SESSION_FILE" | head -1 | sed 's/^## Last Updated: //')
    ORG_COUNT=$(grep -A 100 "^### Organizations" "$SESSION_FILE" | grep -E "^\| [a-zA-Z0-9]" | grep -v "^\| Name" | wc -l)
    SENSOR_COUNT=$(grep -A 100 "^### Sensors" "$SESSION_FILE" | grep -E "^\| [a-zA-Z0-9]" | grep -v "^\| Hostname" | wc -l)
    # Objective: must have actual content after the colon (not just the markdown formatting)
    OBJECTIVE=$(grep "^\- \*\*Primary objective\*\*: ." "$SESSION_FILE" | head -1 | sed 's/^- \*\*Primary objective\*\*: //')
    ACTION_COUNT=$(grep -E "^\- \*\*[0-9]{2}:[0-9]{2}" "$SESSION_FILE" | wc -l)
    LAST_ACTIONS=$(grep -E "^\- \*\*[0-9]{2}:[0-9]{2}" "$SESSION_FILE" | tail -3)
    PENDING=$(grep -E "^- \[ \]" "$SESSION_FILE" | head -3)

    # Determine if we have an active session (only if there's actual content)
    if [ -n "$OBJECTIVE" ] || [ "$ACTION_COUNT" -gt 0 ] || [ "$ORG_COUNT" -gt 0 ]; then
        HAS_ACTIVE_SESSION=true

        # Build session summary for display
        if [ -n "$SESSION_START" ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[90m  Session started: $SESSION_START\u001b[0m\n"
        fi
        if [ -n "$LAST_UPDATED" ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[90m  Last updated: $LAST_UPDATED\u001b[0m\n"
        fi
        SESSION_SUMMARY="${SESSION_SUMMARY}\n"

        if [ "$ORG_COUNT" -gt 0 ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[97m  Organizations: $ORG_COUNT tracked\u001b[0m\n"
        fi
        if [ "$SENSOR_COUNT" -gt 0 ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[97m  Sensors: $SENSOR_COUNT tracked\u001b[0m\n"
        fi
        if [ -n "$OBJECTIVE" ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\n\u001b[97m  Objective: $OBJECTIVE\u001b[0m\n"
        fi
        if [ -n "$LAST_ACTIONS" ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\n\u001b[36m  Recent actions:\u001b[0m\n"
            while IFS= read -r action; do
                SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[90m  $action\u001b[0m\n"
            done <<< "$LAST_ACTIONS"
        fi
        if [ -n "$PENDING" ]; then
            SESSION_SUMMARY="${SESSION_SUMMARY}\n\u001b[36m  Pending:\u001b[0m\n"
            while IFS= read -r item; do
                SESSION_SUMMARY="${SESSION_SUMMARY}\u001b[90m  $item\u001b[0m\n"
            done <<< "$PENDING"
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD BANNER
# ═══════════════════════════════════════════════════════════════════════════════

BANNER='\u001b[34m╔════════════════════════════════════════════════════════════════════════════════════════════════════╗\u001b[0m\n\n'
BANNER="${BANNER}\u001b[34m  ██╗         ██████╗       ███████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██╔════╝       ██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██║            ███████╗█████╗  ██║     ██║   ██║██████╔╝███████╗\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ██║        ██║            ╚════██║██╔══╝  ██║     ██║   ██║██╔═══╝ ╚════██║\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ███████╗   ╚██████╗       ███████║███████╗╚██████╗╚██████╔╝██║     ███████║\u001b[0m\n"
BANNER="${BANNER}\u001b[34m  ╚══════╝    ╚═════╝       ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝\u001b[0m\n\n"

# Add environment status if available
if [ -n "$STATUS_LINES" ]; then
    BANNER="${BANNER}\u001b[34m  Your environment:\u001b[0m\n${STATUS_LINES}\n"
fi

if [ "$HAS_ACTIVE_SESSION" = true ]; then
    BANNER="${BANNER}\u001b[33m  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m\n"
    BANNER="${BANNER}\u001b[33m  📋 PREVIOUS SESSION DETECTED\u001b[0m\n"
    BANNER="${BANNER}\u001b[33m  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m\n\n"
    BANNER="${BANNER}${SESSION_SUMMARY}\n"
    BANNER="${BANNER}\u001b[33m  ──────────────────────────────────────────────────────────────────────────────────────────────────\u001b[0m\n\n"
    BANNER="${BANNER}\u001b[32m  Type \"continue\" to resume or \"fresh\" to start over\u001b[0m\n\n"
else
    BANNER="${BANNER}\u001b[35m  Welcome to the Agentic SecOps Workspace.\u001b[0m\n\n"
    BANNER="${BANNER}\u001b[36m  Session logging is active.\u001b[0m\n\n"
fi

BOTTOM_BORDER='\u001b[34m╚════════════════════════════════════════════════════════════════════════════════════════════════════╝\u001b[0m'
FULL_MESSAGE="${BANNER}${BOTTOM_BORDER}"

# Print banner directly to terminal
echo -e "\n${FULL_MESSAGE}\n" > /dev/tty 2>/dev/null || echo -e "\n${FULL_MESSAGE}\n"

# Simple success output - context is loaded via @import in CLAUDE.md
echo '{"continue": true}'

exit 0
