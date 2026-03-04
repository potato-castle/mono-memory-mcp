#!/usr/bin/env bash
set -euo pipefail

echo "==================================="
echo "  Mono Memory MCP — Setup"
echo "==================================="
echo ""

# Server URL
read -rp "Server URL (e.g. http://192.168.0.10:8765/mcp): " SERVER_URL
if [ -z "$SERVER_URL" ]; then
  echo "Error: server URL is required."
  exit 1
fi

# Ping server
echo ""
echo "Checking connection..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "000" ]; then
  echo "Error: cannot reach $SERVER_URL"
  exit 1
fi
echo "Connected! (HTTP $HTTP_CODE)"
echo ""

# Author name
read -rp "Your name (author): " AUTHOR_NAME
if [ -z "$AUTHOR_NAME" ]; then
  echo "Error: author name is required."
  exit 1
fi

# Write to ~/.mcp.json
MCP_CONFIG="$HOME/.mcp.json"

if [ -f "$MCP_CONFIG" ]; then
  python3 -c "
import json
with open('$MCP_CONFIG') as f:
    config = json.load(f)
config.setdefault('mcpServers', {})
config['mcpServers']['mono-memory'] = {
    'type': 'streamable-http',
    'url': '$SERVER_URL'
}
with open('$MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
else
  cat > "$MCP_CONFIG" << MCPEOF
{
  "mcpServers": {
    "mono-memory": {
      "type": "streamable-http",
      "url": "$SERVER_URL"
    }
  }
}
MCPEOF
fi

echo ""
echo "==================================="
echo "  Setup complete!"
echo "==================================="
echo ""
echo "  Server:  $SERVER_URL"
echo "  Author:  $AUTHOR_NAME"
echo "  Config:  $MCP_CONFIG"
echo ""
echo "Restart Claude Code to connect."
