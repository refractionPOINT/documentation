# SESSION CONTINUATION PROTOCOL

The banner prompts users to type "continue" or "fresh" when a previous session exists.

**Handle these responses:**

- **User says "continue" (or similar):** Load the context from the session log below and summarize what was being worked on. Then proceed with the task.

- **User says "fresh" or "start fresh":** Clear session.md using the template at the bottom of this file. Confirm the reset.

- **User ignores the prompt and asks something else:** That's fine - proceed normally. The session context is available if needed.

**Key point:** Don't gate-keep. If they want to work, let them work. The session log is there for context, not as a barrier.

---

## Session Log (Auto-Imported)

@.claude/session-memory/session.md

---

# LimaCharlie SecOps Workspace

This workspace provides agentic security operations capabilities through the LimaCharlie platform.

---

## Session Behavior

**Throughout the session:**
- The PostToolUse hook automatically logs actions to session.md
- You should also update these manually when relevant:
  - Organizations accessed (name, OID, role)
  - Sensors investigated (hostname, SID, platform)
  - Detections found (ID, rule, sensor, status)
  - LCQL queries run (query, purpose, time range)
  - Important decisions and reasoning
  - Pending/next steps

**When user says "start fresh":** Clear session.md with the template below.

---

## Session Template

When clearing a session, replace session.md with:

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
