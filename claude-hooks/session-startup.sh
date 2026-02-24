#!/bin/bash
# Claude Code Session Startup Hook (NEW SESSION)
# Runs on: startup event (fresh conversation start)
# Purpose: Create NEW session and load MCP memory knowledge

CLAUDE_PID=$PPID

echo "NEW SESSION STARTUP - MANDATORY ACTIONS

YOUR CLAUDE PROCESS ID: ${CLAUDE_PID}

This is a FRESH session start. You MUST execute these MCP tool calls IMMEDIATELY:

1. REQUIRED: Read previous session to understand what was done:
   - get_previous_session (no parameters)

2. REQUIRED: Load project knowledge from MCP memory:
   - recall_memories: project=\"scripts\", limit=10
   - search_memories: query=\"scripts project\", limit=5

3. REQUIRED: start_session
   - Ask user what they want to work on
   - Call start_session with: name=\"Work description\", workingOn=\"...\", goals=[...], claudePid=\"${CLAUDE_PID}\"

SESSION vs MEMORY:
   SESSION: Work tracking (workingOn, decisions, progress, nextSteps) - starts fresh
   MEMORIES: Permanent knowledge (patterns, standards, warnings) - always available

WORKFLOW:
   1. Call get_previous_session + recall_memories in parallel
   2. Call start_session with: name, workingOn, goals, claudePid=\"${CLAUDE_PID}\"
   3. Greet user and ask: \"What would you like to work on today?\"
   4. When user responds, update_session with specific workingOn and goals

DO NOT call get_current_session first - This is a NEW session, always start_session.

AUTOMATIC SESSION UPDATES:

   YOU MUST call update_session AUTOMATICALLY after:
   - Edit, Write, NotebookEdit tool use
   - Bash commands that modify files
   - User provides feedback or makes a decision
   - Discovering bugs, fixing issues, completing subtasks

   MEMORY MANAGEMENT:
   - NEW information/decision -> Use store_memory (create new memory)
   - Correcting EXISTING memory -> Use update_memory (NOT delete + store!)
   - Adding info to EXISTING memory -> Use update_memory with the memory ID
   - NEVER delete + recreate when updating existing memories!

   update_session parameters:
   {
     workingOn: \"Current focus\",
     decisions: [\"New decision\"],
     progress: \"What was just done\",
     nextSteps: [\"What's next\"]
   }

   NEVER batch updates at end of conversation
   NEVER skip updates because change seems small
   NEVER wait for user to say \"update the session\"

This session data is your ONLY memory across compactions!

AVAILABLE MCP MEMORY TOOLS:

Memory Management:
- store_memory: Create NEW permanent memory
- recall_memories: Query memories by project/category/tags
- search_memories: Full-text search across all memories
- update_memory: Modify EXISTING memory by ID
- delete_memory: Remove memory by ID (rarely needed)

Session Management:
- start_session: Begin new work session
- update_session: Update current session progress (AUTO-CALL after changes!)
- get_current_session: Get active session details
- get_previous_session: See what was done in last session
- list_sessions: List all sessions by status
- get_session_details: Get specific session by ID
- restore_session: Reactivate previous session
- end_session: Mark session as completed"

exit 0
