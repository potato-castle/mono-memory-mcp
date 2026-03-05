#!/bin/bash
cd "$(dirname "$0")/.."

if lsof -ti:8765 > /dev/null 2>&1; then
    echo "Server is already running (PID: $(lsof -ti:8765))"
    exit 1
fi

nohup uv run python server.py > /tmp/mono-memory.log 2>&1 &
sleep 2

if lsof -ti:8765 > /dev/null 2>&1; then
    echo "Server started (PID: $(lsof -ti:8765))"
else
    echo "Failed to start server. Check /tmp/mono-memory.log"
    exit 1
fi
