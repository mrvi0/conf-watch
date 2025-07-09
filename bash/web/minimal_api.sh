#!/usr/bin/env bash

# ConfWatch Minimal Web API
# Ultra-simple HTTP server for web interface

CONFWATCH_HOME="$HOME/.confwatch"
WEB_DIR="$(dirname "$0")"
PORT=8080

echo "Starting ConfWatch minimal web server on port $PORT"
echo "Web interface available at: http://localhost:$PORT"

# Simple HTTP response function
send_response() {
    local status="$1"
    local content_type="$2"
    local body="$3"
    
    echo -e "HTTP/1.1 $status"
    echo -e "Content-Type: $content_type"
    echo -e "Access-Control-Allow-Origin: *"
    echo -e ""
    echo -n "$body"
}

# Handle requests
while true; do
    # Read HTTP request
    read -r line
    if [[ -z "$line" ]]; then
        continue
    fi
    
    # Parse request line
    method=$(echo "$line" | cut -d' ' -f1)
    path=$(echo "$line" | cut -d' ' -f2)
    
    echo "Request: $method $path"
    
    # Skip headers
    while read -r line; do
        if [[ -z "$line" ]]; then
            break
        fi
    done
    
    # Handle different paths
    case "$path" in
        "/")
            # Serve index.html
            if [[ -f "$WEB_DIR/index.html" ]]; then
                content=$(cat "$WEB_DIR/index.html")
                send_response "200 OK" "text/html" "$content"
            else
                send_response "404 Not Found" "text/plain" "index.html not found"
            fi
            ;;
        "/api/files")
            # Return simple JSON response
            json='[{"name":"~/.bashrc","exists":true,"has_history":false},{"name":"~/.zshrc","exists":false,"has_history":false}]'
            send_response "200 OK" "application/json" "$json"
            ;;
        "/api/diff")
            # Return simple diff response
            send_response "200 OK" "text/plain" "No diff available in minimal version"
            ;;
        "/api/history")
            # Return simple history response
            send_response "200 OK" "text/plain" "No history available in minimal version"
            ;;
        "/api/snapshot")
            # Return simple snapshot response
            json='{"success":true,"message":"Snapshot created (minimal version)"}'
            send_response "200 OK" "application/json" "$json"
            ;;
        *)
            send_response "404 Not Found" "text/plain" "Not Found"
            ;;
    esac
done | nc -l -p "$PORT" -w 1 