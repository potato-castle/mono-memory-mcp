---
name: setup
description: Set up Mono Memory MCP server connection and author
---

# Mono Memory Setup

Set up the Mono Memory MCP server connection.

## Important

- Do NOT use AskUserQuestion tool. Do NOT present selection options or default values.
- Instead, output a plain text question and wait for the user to type their answer.

## Steps

1. Print this message and wait for the user's reply:
   ```
   Enter your memory server URL (e.g. http://192.168.0.10:8765/mcp):
   ```
2. After receiving the server URL, print this message and wait for the user's reply:
   ```
   Enter your author name:
   ```
3. Read `~/.mcp.json` (create if not exists)
4. Add or update the `mono-memory` server entry using the URL the user typed:
   ```json
   {
     "mcpServers": {
       "mono-memory": {
         "type": "streamable-http",
         "url": "<the URL user typed>"
       }
     }
   }
   ```
5. Save the file
6. Tell the user to restart Claude Code to apply the change
