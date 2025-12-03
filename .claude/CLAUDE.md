# LimaCharlie SecOps Workspace

This workspace provides agentic security operations capabilities through the LimaCharlie platform.

## Session Memory

The session memory system tracks context between sessions. When you see "PREVIOUS SESSION DETECTED", review the context below and ask the user if they want to continue.

**If user says "yes" to continue**: Use the session context to resume work seamlessly.

**If user says "no" or "start fresh"**: Clear the session log by replacing its contents with a fresh template, then begin a new session.

### Current Session Log

@session-memory/session.md

## Session Logging Instructions

Throughout each session, you MUST actively maintain the session log at `.claude/session-memory/session.md`. Update it when:

1. **Organizations accessed**: Add to the Organizations table with name, OID, and role
2. **Sensors investigated**: Add to the Sensors table with hostname, SID, platform, notes
3. **Detections found**: Add to the Detections table with ID, rule, sensor, status
4. **API keys used**: Record key names (never values) and their purpose
5. **LCQL queries run**: Record queries, their purpose, and time ranges used
6. **Time ranges**: Track investigation time windows
7. **Major actions**: Add timestamped entries to Actions Taken section
8. **Decisions made**: Document significant choices and reasoning
9. **Pending items**: Keep Next Steps updated with remaining work

### Log Update Format

When updating the session log, use this format:

**For timestamps**: Use ISO format like `2025-12-01T14:30:00`

**For actions**: `1. **HH:MM** - Description of action taken`

**For tables**: Append new rows, don't replace existing data

**Session start**: Always update "Session Started" and "Last Updated" timestamps

## Clearing a Session

When the user wants to start fresh, replace the session.md contents with this template:

```markdown
# Session Log

## Session Started: [CURRENT_TIMESTAMP]
## Last Updated: [CURRENT_TIMESTAMP]

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

```
