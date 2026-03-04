# Mono Memory Setup

Set up the Mono Memory MCP server connection.

## Steps

1. Ask: "What is your memory server URL? (e.g. http://192.168.0.10:8765/mcp)"
2. Ask: "What name should be used as your author? (e.g. alice, bob)"
3. Read `~/.mcp.json` (create if not exists)
4. Add or update the `mono-memory` server entry:
   ```json
   {
     "mcpServers": {
       "mono-memory": {
         "type": "streamable-http",
         "url": "<user's server URL>"
       }
     }
   }
   ```
5. Save the file
6. Tell the user to restart Claude Code to apply the change
