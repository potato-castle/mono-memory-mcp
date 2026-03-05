---
name: mono-update
description: Update the mono-memory plugin to the latest version
---

# Mono Update

Update the mono-memory MCP plugin to the latest version from GitHub.

## Steps

1. Run the update using Bash:
   ```bash
   cd ~/.claude/plugins/mono-memory-mcp && git pull origin main
   ```

2. Print the result:
   - If updated:
     ```
     Plugin updated!

     > Restart Claude Code to apply changes.
     ```
   - If already up to date:
     ```
     Already up to date.
     ```
   - If error (e.g. directory not found):
     ```
     Plugin not found at ~/.claude/plugins/mono-memory-mcp.
     Reinstall with: /plugin marketplace add potato-castle/mono-memory-mcp
     ```
