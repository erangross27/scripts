#!/bin/bash
# Claude Code UserPromptSubmit Hook - AUTOMATIC TOPIC-BASED SESSION MANAGEMENT
# Runs on: UserPromptSubmit event (every time user sends a message)
# Purpose: ENFORCE automatic session end/start when topic changes

echo "AUTOMATIC SESSION MANAGEMENT - TOPIC CHANGE DETECTION

REQUIRED ACTIONS (Execute BEFORE responding to user):

1. CHECK CURRENT SESSION:
   mcp__mongodb-memory__get_current_session (no parameters)

2. ANALYZE TOPIC CHANGE:
   Compare user's CURRENT message with session's 'workingOn' field:

   TOPIC CHANGE INDICATORS (NEW topic detected):
   - User asks about DIFFERENT task than current workingOn
   - User switches from one script/feature to another
   - User asks \"now let's work on...\" or \"switch to...\" or \"next task...\"
   - User's message is about UNRELATED topic to current workingOn

   NOT A TOPIC CHANGE (SAME topic, continue session):
   - Follow-up questions about SAME task/feature
   - Clarifications about CURRENT work
   - \"Also add...\" or \"Also fix...\" referring to CURRENT work
   - Debugging/testing CURRENT implementation

3. IF TOPIC CHANGED - Execute these steps IN ORDER:

   STEP 1: End current session
   mcp__mongodb-memory__end_session({
       \"summary\": \"Completed work on [previous topic]: [brief summary]\"
     })

   STEP 2: Start new session for new topic
   mcp__mongodb-memory__start_session({
       \"name\": \"[Extract topic from user's message]\",
       \"workingOn\": \"[User's new request]\",
       \"goals\": [\"[Primary goal from user's message]\"]
     })

   STEP 3: Load relevant memories for new topic
   mcp__mongodb-memory__search_memories({
       \"query\": \"[keywords from new topic]\",
       \"limit\": 5
     })

4. IF NO TOPIC CHANGE - Continue with current session:
   Update session with progress as normal

BEHAVIORAL REQUIREMENTS:

- ALWAYS detect topic changes BEFORE responding
- ALWAYS end session when topic changes
- ALWAYS start new session with descriptive name
- ALWAYS acknowledge session switches to user
- NEVER ask user \"should I start a new session?\" - DO IT AUTOMATICALLY
- NEVER continue old session when topic clearly changed"

exit 0
