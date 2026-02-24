#!/bin/bash
# PreToolUse Hook - Runs BEFORE every tool execution
# Purpose: Validation before code modifications and git operations

TOOL_NAME="$1"

# Code Modification Tools
if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "NotebookEdit" ]]; then
  cat <<'EOF'
PRE-TOOL VALIDATION - CODE MODIFICATION DETECTED

Before proceeding with code modification, verify you have:

- Searched MCP memories for relevant patterns/standards
- Checked existing implementation patterns
- Validated this change follows project standards

PRE-MODIFICATION GATE CHECK:
Did you search MCP memories before this code modification?
EOF
  exit 0
fi

# Git Commit Operations
if [[ "$TOOL_NAME" == "Bash" ]]; then
  BASH_COMMAND="${@:2}"

  if echo "$BASH_COMMAND" | grep -q "git commit"; then
    cat <<'EOF'
PRE-COMMIT VALIDATION - GIT COMMIT DETECTED

Before committing, verify you have:

- Updated the current session with update_session
  (progress, decisions, nextSteps)
- Stored important decisions in MCP memory (if applicable)
  (New patterns -> store_memory category: "pattern")
  (Bugs fixed -> store_memory category: "bug")
  (Standards established -> store_memory category: "standard")
EOF
    exit 0
  fi
fi

# Silent pass-through for all other tools
exit 0
