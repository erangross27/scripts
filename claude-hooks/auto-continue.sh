#!/bin/bash
# Claude Code Auto-Continue Hook
# Runs on: Stop event (when Claude finishes responding)
# Purpose: Force Claude to continue until task is 100% complete

cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "AUTO-CONTINUE CHECK

INTERNAL CHECK (DO NOT OUTPUT TO USER):

Q1: What was the original task the user requested?
Q2: Have you completed ALL parts of that task?
Q3: Are there any remaining items, files, or steps left to do?

IF WORK REMAINS:
- IMMEDIATELY continue with the next item WITHOUT ANY SUMMARY
- Do NOT output a completion check or summary
- Do NOT ask 'would you like me to continue?'
- Do NOT wait for user input
- Just SILENTLY start working on the next item

IF ALL WORK IS DONE:
- You can stop and provide a brief completion message

DO NOT STOP FOR:
- Completing one file when user asked for multiple files
- Finishing one step when the task has multiple steps
- Doing part of the request when user asked for everything
- Asking permission for obvious next steps

ONLY STOP IF:
1. You did EVERYTHING user asked (nothing remains)
2. You hit a blocking error that requires user input
3. You need a user decision on HOW to proceed
4. You need clarification on WHAT user wants"
  }
}
EOF

exit 0
