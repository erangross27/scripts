#!/bin/bash
# Claude Code Pre-Compaction Hook (SAVE SESSION BEFORE COMPACTION)
# Runs on: PreCompact event (before conversation compaction)
# Purpose: Update current session with latest progress before compaction

cat <<'EOF'
BEFORE COMPACTION: Call update_session with current progress to preserve context.

Required actions:
1. Call mcp__mongodb-memory__get_current_session
2. Call mcp__mongodb-memory__update_session with workingOn, decisions, progress, nextSteps

CRITICAL: CONVERSATION IS ABOUT TO BE COMPACTED

The conversation context is full and will be compacted. You MUST update the current session NOW.

REQUIRED ACTIONS (Execute IMMEDIATELY):

1. MANDATORY: Get current session state
   mcp__mongodb-memory__get_current_session (no parameters)

2. MANDATORY: Update session with COMPLETE current state
   mcp__mongodb-memory__update_session with ALL recent context:

   {
     "workingOn": "[What you're CURRENTLY working on - be specific]",
     "decisions": ["[ALL decisions made since last update]"],
     "progress": "[DETAILED summary of what was accomplished in recent messages]",
     "nextSteps": ["[What needs to happen next]"]
   }

WHAT TO INCLUDE:

workingOn: Current focus (be SPECIFIC)
decisions: ALL decisions made recently
progress: DETAILED summary of recent work
nextSteps: What's next (actionable items)

WHY THIS IS CRITICAL:

- Compaction DELETES conversation history
- Without this update, the last 10-50 messages will be LOST
- Session updates are the ONLY persistent memory
- This is your LAST CHANCE to save recent context

TRIAL-AND-ERROR CLEANUP:

After updating session, detect and clean up failed solution attempts:
- If user confirmed a solution worked AND you tried other approaches that failed
- Search for related memories, delete failed attempt memories
- Update correct solution memory with list of wrong approaches
- Only delete memories from THIS SESSION (check timestamps)
- If uncertain, keep all memories
EOF

exit 0
