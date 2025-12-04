#!/bin/bash

# PostToolUse Hook: Session Activity Logger
# WRITES actions directly to session.md - no reminders, actual logging
#
# This hook fires after tool calls and appends significant actions
# directly to the session file to maintain session continuity.

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SESSION_FILE="$PROJECT_ROOT/.claude/session-memory/session.md"

# Read the tool use data from stdin
INPUT=$(cat)

# Extract tool name from the JSON input
TOOL_NAME=$(echo "$INPUT" | grep -oP '"tool_name"\s*:\s*"\K[^"]+' | head -1)

# If tool_name not found, try alternate patterns
if [ -z "$TOOL_NAME" ]; then
    TOOL_NAME=$(echo "$INPUT" | grep -oP '"name"\s*:\s*"\K[^"]+' | head -1)
fi

# Exit silently if we couldn't determine the tool
if [ -z "$TOOL_NAME" ]; then
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# FILTER: Which tools warrant logging?
# ═══════════════════════════════════════════════════════════════════════════════

SHOULD_LOG=false
LOG_CATEGORY=""
EXTRA_INFO=""

case "$TOOL_NAME" in
    # LimaCharlie MCP calls - always log
    mcp__limacharlie__*)
        SHOULD_LOG=true
        LOG_CATEGORY="LimaCharlie API"
        # Extract the actual function name
        EXTRA_INFO=$(echo "$TOOL_NAME" | sed 's/mcp__limacharlie__//')
        ;;
    mcp__plugin_lc-essentials_limacharlie__*)
        SHOULD_LOG=true
        LOG_CATEGORY="LimaCharlie API"
        EXTRA_INFO=$(echo "$TOOL_NAME" | sed 's/mcp__plugin_lc-essentials_limacharlie__//')
        ;;

    # File modifications - log these
    Edit)
        SHOULD_LOG=true
        LOG_CATEGORY="File edit"
        EXTRA_INFO=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' | head -1 | xargs basename 2>/dev/null)
        ;;
    Write)
        SHOULD_LOG=true
        LOG_CATEGORY="File write"
        EXTRA_INFO=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' | head -1 | xargs basename 2>/dev/null)
        ;;
    NotebookEdit)
        SHOULD_LOG=true
        LOG_CATEGORY="Notebook edit"
        ;;

    # Task/Agent spawning - log these
    Task)
        SHOULD_LOG=true
        LOG_CATEGORY="Agent task"
        EXTRA_INFO=$(echo "$INPUT" | grep -oP '"description"\s*:\s*"\K[^"]+' | head -1)
        ;;

    # Skill invocations - log these
    Skill)
        SHOULD_LOG=true
        LOG_CATEGORY="Skill"
        EXTRA_INFO=$(echo "$INPUT" | grep -oP '"skill"\s*:\s*"\K[^"]+' | head -1)
        ;;

    # Bash commands - selective logging
    Bash)
        # Extract command from input
        COMMAND=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' | head -1)

        # Log state-changing commands, skip reads
        case "$COMMAND" in
            git\ commit*|git\ push*|git\ merge*|git\ rebase*)
                SHOULD_LOG=true
                LOG_CATEGORY="Git"
                EXTRA_INFO="$COMMAND"
                ;;
            npm\ install*|pip\ install*|yarn\ add*)
                SHOULD_LOG=true
                LOG_CATEGORY="Package install"
                EXTRA_INFO="$COMMAND"
                ;;
            rm\ *|mv\ *)
                SHOULD_LOG=true
                LOG_CATEGORY="File operation"
                EXTRA_INFO="$COMMAND"
                ;;
            docker\ *|kubectl\ *)
                SHOULD_LOG=true
                LOG_CATEGORY="Container/K8s"
                EXTRA_INFO="$COMMAND"
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
