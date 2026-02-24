#!/bin/bash
# Claude Code UserPromptSubmit Hook - MANDATORY Search-First Protocol
# Runs on: Every user message

echo "MANDATORY MEMORY SEARCH - EXECUTE BEFORE RESPONDING

YOUR FIRST ACTION must be these tool calls (extract keywords from user's message):

mcp__mongodb-memory__search_memories({\"query\": \"[keywords]\", \"limit\": 5})
mcp__mongodb-memory__search_sessions({\"query\": \"[keywords]\", \"limit\": 5})

DO NOT write any text response before executing these searches.
DO NOT skip searches because you \"think you know the answer\".

EXCEPTION: Skip searches ONLY if user is asking a simple greeting or about this hook itself.

SKILL CHECK - BEFORE ANY RESPONSE:

BEFORE responding, check if ANY installed skill applies to the user's message.
If a skill applies, invoke it BEFORE writing code.

REFERENCE INFORMATION:

MCP MONGODB TOOLS:
- Use MCP tools for MongoDB queries, not Bash mongosh
- Tools: find, aggregate, count, list-collections, collection-schema

AVAILABLE MCP MEMORY TOOLS:
- search_memories: Full-text search across all memories
- search_sessions: Search sessions by keyword
- recall_memories: Query by project/category/tags
- store_memory: Create NEW permanent memory
- update_memory: Modify EXISTING memory by ID"

exit 0
