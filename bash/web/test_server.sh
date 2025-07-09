#!/usr/bin/env bash

# ConfWatch Test Web Server
# Uses Python3's built-in HTTP server

CONFWATCH_HOME="$HOME/.confwatch"
WEB_DIR="$(dirname "$0")"
PORT=8080

echo "Starting ConfWatch test web server on port $PORT"
echo "Web interface available at: http://localhost:$PORT"

# Check if Python3 is available
if command -v python3 &> /dev/null; then
    echo "Using Python3 HTTP server..."
    cd "$WEB_DIR"
    python3 -m http.server "$PORT"
elif command -v python &> /dev/null; then
    echo "Using Python HTTP server..."
    cd "$WEB_DIR"
    python -m http.server "$PORT"
else
    echo "Error: Python3 or Python not found"
    exit 1
fi 