---
name: mono-update
description: Update the mono-memory plugin to the latest version
---

# Mono Update

## Steps

1. Print:
   ```
   Updating mono-memory plugin...
   ```

2. Run update via Bash (downloads latest from GitHub, no git required):
   ```bash
   curl -sL https://github.com/potato-castle/mono-memory-mcp/archive/main.tar.gz | tar xz -C /tmp && cp -r /tmp/mono-memory-mcp-main/* ~/.claude/plugins/mono-memory-mcp/ && rm -rf /tmp/mono-memory-mcp-main && echo "Updated successfully"
   ```

3. If success:
   ```
   Plugin updated!

   > Restart Claude Code to apply changes.
   ```

4. If curl/tar fails:
   ```
   Auto-update failed. Run these commands manually in Claude Code:

   /plugin uninstall mono-memory-mcp@mono-memory-mcp
   /plugin install mono-memory-mcp@mono-memory-mcp

   Then restart Claude Code.
   ```
