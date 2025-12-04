#!/bin/bash

# PostToolUse Hook: Session Activity Logger
# WRITES actions directly to session.md - no reminders, actual logging
#
# This hook fires after tool calls and appends significant actions
# directly to the session file to maintain session continuity.
#
# Hook input schema:
#   { session_id, transcript_path, cwd, hook_event_name,
#     tool_name, tool_input, tool_response, tool_use_id }

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SESSION_FILE="$PROJECT_ROOT/.claude/session-memory/session.md"

# Read the tool use data from stdin
INPUT=$(cat)

# Check if jq is available for reliable JSON parsing
if command -v jq &> /dev/null; then
    USE_JQ=true
    TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
else
    USE_JQ=false
    TOOL_NAME=$(echo "$INPUT" | grep -oP '"tool_name"\s*:\s*"\K[^"]+' | head -1)
fi

# Exit silently if we couldn't determine the tool
if [ -z "$TOOL_NAME" ]; then
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Extract field from tool_input (uses jq if available, falls back to grep)
# ═══════════════════════════════════════════════════════════════════════════════
extract_input() {
    local field="$1"
    if [ "$USE_JQ" = true ]; then
        echo "$INPUT" | jq -r ".tool_input.$field // empty" 2>/dev/null
    else
        echo "$INPUT" | grep -oP "\"$field\"\s*:\s*\"\K[^\"]*" | head -1
    fi
}

# Helper to truncate strings
truncate() {
    local str="$1"
    local max="${2:-40}"
    if [ ${#str} -gt $max ]; then
        echo "${str:0:$max}..."
    else
        echo "$str"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# FILTER: Which tools warrant logging?
# ═══════════════════════════════════════════════════════════════════════════════

SHOULD_LOG=false
LOG_CATEGORY=""
EXTRA_INFO=""

case "$TOOL_NAME" in
    # LimaCharlie MCP calls - always log with rich context
    mcp__limacharlie__*|mcp__plugin_lc-essentials_limacharlie__*)
        SHOULD_LOG=true
        LOG_CATEGORY="LC"

        # Extract function name
        FUNC=$(echo "$TOOL_NAME" | sed 's/mcp__limacharlie__//' | sed 's/mcp__plugin_lc-essentials_limacharlie__//')

        # Always extract OID and SID if present (truncated for readability)
        OID=$(extract_input "oid")
        OID_SHORT="${OID:0:8}"
        SID=$(extract_input "sid")
        SID_SHORT="${SID:0:8}"

        # Build context string
        CTX=""
        [ -n "$OID_SHORT" ] && CTX="org:$OID_SHORT"
        [ -n "$SID_SHORT" ] && CTX="${CTX}${CTX:+ | }sid:$SID_SHORT"

        # Function-specific context for high-value operations
        case "$FUNC" in
            run_lcql_query|run_saved_query)
                QUERY=$(extract_input "query")
                QUERY_NAME=$(extract_input "query_name")
                if [ -n "$QUERY" ]; then
                    CTX="${CTX}${CTX:+ | }\"$(truncate "$QUERY" 50)\""
                elif [ -n "$QUERY_NAME" ]; then
                    CTX="${CTX}${CTX:+ | }saved:$QUERY_NAME"
                fi
                ;;
            search_iocs|batch_search_iocs)
                IOC_TYPE=$(extract_input "ioc_type")
                IOC_VAL=$(extract_input "ioc_value")
                [ -n "$IOC_TYPE" ] && CTX="${CTX}${CTX:+ | }$IOC_TYPE:$(truncate "$IOC_VAL" 30)"
                ;;
            *_dr_*_rule|get_rule|set_rule|delete_rule)
                RULE=$(extract_input "rule_name")
                [ -n "$RULE" ] && CTX="${CTX}${CTX:+ | }rule:$RULE"
                ;;
            search_hosts)
                HOST=$(extract_input "hostname_expr")
                [ -n "$HOST" ] && CTX="${CTX}${CTX:+ | }host:$HOST"
                ;;
            get_historic_detections|get_historic_events)
                START=$(extract_input "start")
                END=$(extract_input "end")
                if [ -n "$START" ] && [ -n "$END" ]; then
                    # Convert epoch to readable if possible
                    if command -v date &> /dev/null; then
                        START_FMT=$(date -d "@$START" '+%m/%d %H:%M' 2>/dev/null || echo "$START")
                        END_FMT=$(date -d "@$END" '+%m/%d %H:%M' 2>/dev/null || echo "$END")
                        CTX="${CTX}${CTX:+ | }range:$START_FMT→$END_FMT"
                    fi
                fi
                ;;
            get_detection)
                DET_ID=$(extract_input "detection_id")
                [ -n "$DET_ID" ] && CTX="${CTX}${CTX:+ | }det:${DET_ID:0:12}"
                ;;
            get_sensor_info|is_online|isolate_network|rejoin_network)
                # SID already captured above, maybe add action context
                ;;
        esac

        # Build final EXTRA_INFO
        if [ -n "$CTX" ]; then
            EXTRA_INFO="$FUNC | $CTX"
        else
            EXTRA_INFO="$FUNC"
        fi
        ;;

    # File modifications - log these
    Edit)
        SHOULD_LOG=true
        LOG_CATEGORY="Edit"
        FILE_PATH=$(extract_input "file_path")
        FILE_NAME=$(basename "$FILE_PATH" 2>/dev/null)
        # Get relative path for context
        REL_PATH=$(echo "$FILE_PATH" | sed "s|$PROJECT_ROOT/||" 2>/dev/null)
        if [ -n "$REL_PATH" ] && [ "$REL_PATH" != "$FILE_NAME" ]; then
            EXTRA_INFO="$REL_PATH"
        else
            EXTRA_INFO="$FILE_NAME"
        fi
        ;;
    Write)
        SHOULD_LOG=true
        LOG_CATEGORY="Write"
        FILE_PATH=$(extract_input "file_path")
        FILE_NAME=$(basename "$FILE_PATH" 2>/dev/null)
        REL_PATH=$(echo "$FILE_PATH" | sed "s|$PROJECT_ROOT/||" 2>/dev/null)
        if [ -n "$REL_PATH" ] && [ "$REL_PATH" != "$FILE_NAME" ]; then
            EXTRA_INFO="$REL_PATH"
        else
            EXTRA_INFO="$FILE_NAME"
        fi
        ;;
    NotebookEdit)
        SHOULD_LOG=true
        LOG_CATEGORY="Notebook"
        NB_PATH=$(extract_input "notebook_path")
        EXTRA_INFO=$(basename "$NB_PATH" 2>/dev/null)
        ;;

    # Task/Agent spawning - log these
    Task)
        SHOULD_LOG=true
        LOG_CATEGORY="Agent"
        DESC=$(extract_input "description")
        AGENT_TYPE=$(extract_input "subagent_type")
        if [ -n "$AGENT_TYPE" ]; then
            EXTRA_INFO="[$AGENT_TYPE] $(truncate "$DESC" 40)"
        else
            EXTRA_INFO="$(truncate "$DESC" 50)"
        fi
        ;;

    # Skill invocations - log these
    Skill)
        SHOULD_LOG=true
        LOG_CATEGORY="Skill"
        EXTRA_INFO=$(extract_input "skill")
        ;;

    # Bash commands - selective logging
    Bash)
        COMMAND=$(extract_input "command")

        # Log state-changing commands, skip reads
        case "$COMMAND" in
            git\ commit*)
                SHOULD_LOG=true
                LOG_CATEGORY="Git"
                # Extract commit message if present
                MSG=$(echo "$COMMAND" | grep -oP '\-m\s*"?\K[^"]+' | head -1)
                EXTRA_INFO="commit: $(truncate "$MSG" 50)"
                ;;
            git\ push*)
                SHOULD_LOG=true
                LOG_CATEGORY="Git"
                EXTRA_INFO="push"
                ;;
            git\ merge*|git\ rebase*)
                SHOULD_LOG=true
                LOG_CATEGORY="Git"
                EXTRA_INFO="$(echo "$COMMAND" | cut -d' ' -f1-3)"
                ;;
            gh\ pr\ create*)
                SHOULD_LOG=true
                LOG_CATEGORY="GitHub"
                # Try to extract title
                TITLE=$(echo "$COMMAND" | grep -oP '\-\-title\s*"?\K[^"]+' | head -1)
                EXTRA_INFO="PR created: $(truncate "$TITLE" 40)"
                ;;
            npm\ install*|pip\ install*|yarn\ add*)
                SHOULD_LOG=true
                LOG_CATEGORY="Package"
                EXTRA_INFO="$(truncate "$COMMAND" 50)"
                ;;
            rm\ *|mv\ *)
                SHOULD_LOG=true
                LOG_CATEGORY="Files"
                EXTRA_INFO="$(truncate "$COMMAND" 50)"
                ;;
            docker\ *|kubectl\ *)
                SHOULD_LOG=true
                LOG_CATEGORY="Container"
                EXTRA_INFO="$(truncate "$COMMAND" 50)"
                ;;
        esac
        ;;

    # Read-only tools - skip
    Read|Glob|Grep|WebFetch|WebSearch|BashOutput|TodoWrite)
        SHOULD_LOG=false
        ;;
esac

# ═══════════════════════════════════════════════════════════════════════════════
# WRITE: Append action directly to session file
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$SHOULD_LOG" = true ]; then
    # Create session file if it doesn't exist
    if [ ! -f "$SESSION_FILE" ]; then
        mkdir -p "$(dirname "$SESSION_FILE")"
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
    fi

    # Get timestamp
    TIMESTAMP=$(date '+%H:%M:%S')

    # Format the log entry
    if [ -n "$EXTRA_INFO" ]; then
        LOG_ENTRY="- **$TIMESTAMP** [$LOG_CATEGORY] $EXTRA_INFO"
    else
        LOG_ENTRY="- **$TIMESTAMP** [$LOG_CATEGORY] $TOOL_NAME"
    fi

    # Find the "## Actions Taken" section and append after it
    # Using a temp file for safety
    TEMP_FILE=$(mktemp)

    # Check if "## Actions Taken" exists in the file
    if grep -q "## Actions Taken" "$SESSION_FILE"; then
        # Insert the log entry after "## Actions Taken" line
        awk -v entry="$LOG_ENTRY" '
            /^## Actions Taken/ {
                print
                getline
                # Skip any existing empty line right after the header
                if ($0 == "") {
                    print ""
                    print entry
                } else {
                    print entry
                    print
                }
                next
            }
            { print }
        ' "$SESSION_FILE" > "$TEMP_FILE"
        mv "$TEMP_FILE" "$SESSION_FILE"
    else
        # Fallback: just append to end of file
        echo "$LOG_ENTRY" >> "$SESSION_FILE"
    fi

    # Update "Last Updated" timestamp
    sed -i "s/## Last Updated:.*/## Last Updated: $(date '+%Y-%m-%dT%H:%M:%S')/" "$SESSION_FILE"
fi

exit 0
