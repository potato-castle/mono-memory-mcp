#!/bin/bash
if lsof -ti:8765 > /dev/null 2>&1; then
    lsof -ti:8765 | xargs kill
    echo "Server stopped"
else
    echo "Server is not running"
fi
