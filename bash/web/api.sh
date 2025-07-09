#!/usr/bin/env bash

# ConfWatch Web API
# Simple HTTP server for web interface

# Load bash-lib library
source <(curl -fsSL https://raw.githubusercontent.com/mrvi0/bash-lib/main/bash-lib-standalone.sh)

# Configuration
CONFWATCH_HOME="$HOME/.confwatch"
CONFIG_FILE="$CONFWATCH_HOME/config/config.yml"
REPO_DIR="$CONFWATCH_HOME/repo"
WEB_DIR="$(dirname "$0")"
PORT=8080

# HTTP response headers
HTTP_200="HTTP/1.1 200 OK\r\nContent-Type: %s\r\nAccess-Control-Allow-Origin: *\r\n\r\n"
HTTP_404="HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n"
HTTP_500="HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\n"

# Send HTTP response
send_response() {
    local status="$1"
    local content_type="$2"
    local body="$3"
    
    printf "$status" "$content_type"
    echo -n "$body"
}

# Send JSON response
send_json() {
    local body="$1"
    send_response "$HTTP_200" "application/json" "$body"
}

# Send text response
send_text() {
    local body="$1"
    send_response "$HTTP_200" "text/plain" "$body"
}

# Send error response
send_error() {
    local message="$1"
    echo -e "$HTTP_500$message"
}

# Parse HTTP request
parse_request() {
    local request="$1"
    local method=$(echo "$request" | head -n1 | cut -d' ' -f1)
    local path=$(echo "$request" | head -n1 | cut -d' ' -f2)
    local query=$(echo "$path" | cut -d'?' -f2)
    local path=$(echo "$path" | cut -d'?' -f1)
    
    echo "$method|$path|$query"
}

# Get list of monitored files
handle_files_api() {
    logging::info "Handling /api/files request"
    
    # Read config file and extract watch list
    local files=$(grep "^- " "$CONFIG_FILE" | sed 's/^- //' | sed 's/^[[:space:]]*//')
    local json_files="["
    local first=true
    
    for file in $files; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_files="$json_files,"
        fi
        
        # Expand tilde in path
        local expanded_file=$(eval echo "$file")
        local exists="false"
        local has_history="false"
        
        # Check if file exists
        if [[ -f "$expanded_file" ]]; then
            exists="true"
        fi
        
        # Check if file has history
        local basename=$(basename "$expanded_file")
        if [[ -f "$REPO_DIR/$basename" ]]; then
            has_history="true"
        fi
        
        json_files="$json_files{\"name\":\"$file\",\"exists\":$exists,\"has_history\":$has_history}"
    done
    
    json_files="$json_files]"
    send_json "$json_files"
}

# Get diff for a file
handle_diff_api() {
    local query="$1"
    local file=$(echo "$query" | sed 's/.*file=\([^&]*\).*/\1/' | sed 's/%20/ /g')
    
    logging::info "Handling /api/diff request for: $file"
    
    if [[ -z "$file" ]]; then
        send_error "File parameter required"
        return
    fi
    
    # Expand tilde in path
    file=$(eval echo "$file")
    
    # Get absolute path
    file=$(realpath "$file")
    local basename=$(basename "$file")
    
    cd "$REPO_DIR"
    
    # Check if file exists in repo
    if [[ ! -f "$basename" ]]; then
        send_text "No history found for: $file"
        return
    fi
    
    # Get last commit
    local last_commit=$(git log --oneline -1 "$basename" 2>/dev/null | cut -d' ' -f1)
    
    if [[ -z "$last_commit" ]]; then
        send_text "No previous version found for: $file"
        return
    fi
    
    # Get diff
    local diff=$(git diff "$last_commit" "$basename" 2>/dev/null)
    send_text "$diff"
}

# Get history for a file
handle_history_api() {
    local query="$1"
    local file=$(echo "$query" | sed 's/.*file=\([^&]*\).*/\1/' | sed 's/%20/ /g')
    
    logging::info "Handling /api/history request for: $file"
    
    if [[ -z "$file" ]]; then
        send_error "File parameter required"
        return
    fi
    
    # Expand tilde in path
    file=$(eval echo "$file")
    
    # Get absolute path
    file=$(realpath "$file")
    local basename=$(basename "$file")
    
    cd "$REPO_DIR"
    
    # Check if file exists in repo
    if [[ ! -f "$basename" ]]; then
        send_text "No history found for: $file"
        return
    fi
    
    # Get history
    local history=$(git log --oneline --follow "$basename" 2>/dev/null)
    send_text "$history"
}

# Create snapshot for a file
handle_snapshot_api() {
    local body="$1"
    local file=$(echo "$body" | sed 's/.*"file":"\([^"]*\)".*/\1/')
    
    logging::info "Handling /api/snapshot request for: $file"
    
    if [[ -z "$file" ]]; then
        send_json '{"success":false,"error":"File parameter required"}'
        return
    fi
    
    # Expand tilde in path
    file=$(eval echo "$file")
    
    # Check if file exists
    if [[ ! -f "$file" ]]; then
        send_json "{\"success\":false,\"error\":\"File not found: $file\"}"
        return
    fi
    
    # Get absolute path
    file=$(realpath "$file")
    local basename=$(basename "$file")
    local repo_file="$REPO_DIR/$basename"
    
    # Copy file to repo
    cp "$file" "$repo_file"
    
    # Add to git
    cd "$REPO_DIR"
    git add "$basename" > /dev/null 2>&1
    
    # Check if there are changes
    if git diff --cached --quiet; then
        send_json '{"success":true,"message":"No changes detected"}'
        return
    fi
    
    # Commit changes
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Web-snapshot: $file at $timestamp" > /dev/null 2>&1
    
    send_json "{\"success\":true,\"message\":\"Snapshot created for $file\"}"
}

# Handle static files
handle_static_file() {
    local path="$1"
    local file="$WEB_DIR$path"
    
    if [[ -f "$file" ]]; then
        local content_type="text/plain"
        
        # Determine content type
        case "$file" in
            *.html) content_type="text/html" ;;
            *.css) content_type="text/css" ;;
            *.js) content_type="application/javascript" ;;
            *.json) content_type="application/json" ;;
        esac
        
        send_response "$HTTP_200" "$content_type" "$(cat "$file")"
    else
        echo -e "$HTTP_404File not found"
    fi
}

# Main request handler
handle_request() {
    local request="$1"
    local parsed=$(parse_request "$request")
    local method=$(echo "$parsed" | cut -d'|' -f1)
    local path=$(echo "$parsed" | cut -d'|' -f2)
    local query=$(echo "$parsed" | cut -d'|' -f3)
    
    logging::info "Request: $method $path"
    
    case "$path" in
        "/")
            handle_static_file "/index.html"
            ;;
        "/api/files")
            handle_files_api
            ;;
        "/api/diff")
            handle_diff_api "$query"
            ;;
        "/api/history")
            handle_history_api "$query"
            ;;
        "/api/snapshot")
            if [[ "$method" == "POST" ]]; then
                # Read request body
                local body=""
                while IFS= read -r line; do
                    if [[ -z "$line" ]]; then
                        break
                    fi
                done
                IFS= read -r body
                handle_snapshot_api "$body"
            else
                send_error "Method not allowed"
            fi
            ;;
        *)
            handle_static_file "$path"
            ;;
    esac
}

# Start HTTP server
start_server() {
    logging::info "Starting ConfWatch web server on port $PORT"
    colors::success "Web interface available at: http://localhost:$PORT"
    
    # Create named pipe for communication
    local pipe="/tmp/confwatch_api_$$"
    mkfifo "$pipe"
    
    # Start netcat server
    while true; do
        # Read HTTP request
        local request=""
        while IFS= read -r line; do
            request="$request$line"$'\n'
            if [[ -z "$line" ]]; then
                break
            fi
        done < "$pipe"
        
        # Handle request
        handle_request "$request" > "$pipe"
    done | nc -l -p "$PORT" -w 1
    
    # Cleanup
    rm -f "$pipe"
}

# Show help
show_help() {
    print_header "ConfWatch Web API"
    
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [options]"
    echo ""
    
    echo -e "${CYAN}Options:${NC}"
    echo "  -p, --port PORT     Port to listen on (default: 8080)"
    echo "  -h, --help          Show this help"
    echo ""
    
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0"
    echo "  $0 -p 9000"
    echo ""
    
    echo -e "${CYAN}API Endpoints:${NC}"
    echo "  GET  /              Web interface"
    echo "  GET  /api/files     List monitored files"
    echo "  GET  /api/diff      Get file diff"
    echo "  GET  /api/history   Get file history"
    echo "  POST /api/snapshot  Create snapshot"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            colors::error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if ConfWatch is installed
if [[ ! -d "$CONFWATCH_HOME" ]]; then
    colors::error "ConfWatch is not installed. Run ./install.sh first."
    exit 1
fi

# Check if netcat is available
if ! command -v nc &> /dev/null; then
    colors::error "netcat (nc) is required but not installed."
    exit 1
fi

# Start server
start_server 