#!/bin/bash
# PostToolUse Hook - Runs AFTER every tool execution
# Purpose: Enforcement after code modifications and automatic session updates

TOOL_NAME="$1"
TOOL_STATUS="$2"

# Only process successful tool executions
if [[ "$TOOL_STATUS" != "success" ]]; then
  exit 0
fi

# IMMEDIATE Session Update After Code Modifications
if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "NotebookEdit" ]]; then
  cat <<'EOF'
MANDATORY SESSION UPDATE AFTER CODE MODIFICATION

You just modified code. This MUST be recorded in the session NOW.

THE GAP PROBLEM: Compaction can happen at ANY moment without warning.
Any work not recorded in the session will be PERMANENTLY LOST.

REQUIRED: Call mcp__mongodb-memory__update_session with:

{
  "progress": "Modified [EXACT FILE NAME] - [WHAT YOU CHANGED]",
  "decisions": ["Any architectural decisions made (if applicable)"],
  "nextSteps": ["What needs to happen next"]
}

You CANNOT continue responding without calling update_session.
EOF
  exit 0
fi

# Git Operations Completed
if [[ "$TOOL_NAME" == "Bash" ]]; then
  BASH_COMMAND="${@:3}"

  if echo "$BASH_COMMAND" | grep -q "git commit"; then
    cat <<'EOF'
GIT COMMIT COMPLETED

Recommended actions:
- Verify session was updated before commit
- Consider storing critical patterns in MCP memory
EOF
    exit 0
  fi
fi

# Memory Storage Confirmation
if [[ "$TOOL_NAME" == "mcp__mongodb-memory__store_memory" ]]; then
  cat <<'EOF'
MEMORY STORED SUCCESSFULLY

Consider:
- Update current session to reference this decision
- Verify memory has appropriate tags and category
EOF
  exit 0
fi

# Session Update Confirmation
if [[ "$TOOL_NAME" == "mcp__mongodb-memory__update_session" ]]; then
  echo "SESSION UPDATED SUCCESSFULLY - Continue with your current task."
  exit 0
fi

# Silent pass-through for other tools
exit 0
