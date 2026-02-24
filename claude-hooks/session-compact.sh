#!/bin/bash
# Claude Code Session Compact Hook (RESTORE SESSION)
# Runs on: compact and resume events (after compaction)
# Purpose: FORCE context restoration after compaction

CLAUDE_PID=$PPID

echo "POST-COMPACTION CONTEXT RESTORATION - MANDATORY

YOUR CLAUDE PROCESS ID: ${CLAUDE_PID}

MANDATORY TOOL CALLS - EXECUTE THESE NOW:

1. FIRST - Restore your session:
   mcp__mongodb-memory__get_current_session (no parameters)

2. THEN - Load project knowledge (call in parallel):
   mcp__mongodb-memory__recall_memories({\"project\": \"scripts\", \"limit\": 10})
   mcp__mongodb-memory__search_memories({\"query\": \"[keywords from workingOn]\", \"limit\": 5})

DO NOT respond to user until you complete all tool calls above!

REQUIRED OUTPUT FORMAT - Your response MUST start with:

POST-COMPACTION CONTEXT RESTORED
Session Status: [ACTIVE: name | NO SESSION - starting fresh]
Session ID: [id or N/A]
Claude PID: ${CLAUDE_PID}
Working On: [COMPLETE text from session]
Decisions Made: [ALL decisions, not summarized]
Progress: [COMPLETE progress text]
Next Steps: [ALL steps, not summarized]
Memories Loaded: [X] memories found

SCENARIOS:

IF get_current_session returns session data:
   - Read ALL fields: workingOn, decisions[], progress, nextSteps[]
   - Load memories
   - Search for task-relevant memories using workingOn keywords
   - Show REQUIRED OUTPUT FORMAT with COMPLETE session data
   - Continue working on the task

IF get_current_session returns \"No active session\":
   - Check get_previous_session for context
   - Load memories
   - Ask user what they want to work on
   - Call start_session with claudePid=\"${CLAUDE_PID}\"

AUTOMATIC SESSION UPDATES (After restoration):

YOU MUST call update_session AUTOMATICALLY after:
- Edit, Write, NotebookEdit tool use
- Bash commands that modify files
- User provides feedback or makes a decision
- Discovering bugs, fixing issues, completing subtasks

NEVER batch updates at end of conversation
NEVER skip updates because change seems small
NEVER wait for user to say \"update the session\""

exit 0
