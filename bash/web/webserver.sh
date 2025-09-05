#!/usr/bin/env bash

# ConfWatch Web API - Python HTTP Server
CONFWATCH_HOME="$HOME/.confwatch"
CONFIG_FILE="$CONFWATCH_HOME/config/config.yml"
REPO_DIR="$CONFWATCH_HOME/repo"
WEB_DIR="$(dirname "$0")"
PORT="${PORT:-8080}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        return 1
    fi
}

# Create Python HTTP server
create_python_server() {
    local python_cmd="$1"
    cat > "$WEB_DIR/server.py" << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import sys
import subprocess
import urllib.parse
from pathlib import Path

# Configuration
CONFWATCH_HOME = os.path.expanduser("~/.confwatch")
CONFIG_FILE = os.path.join(CONFWATCH_HOME, "config/config.yml")
REPO_DIR = os.path.join(CONFWATCH_HOME, "repo")
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class ConfWatchHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return super().do_GET()
        elif self.path.startswith('/api/'):
            self.handle_api()
        else:
            return super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_error(404)
    
    def handle_api(self):
        if self.path == '/api/files':
            self.handle_files_api()
        elif self.path.startswith('/api/diff'):
            self.handle_diff_api()
        elif self.path.startswith('/api/history'):
            self.handle_history_api()
        elif self.path == '/api/snapshot':
            self.handle_snapshot_api()
        else:
            self.send_error(404)
    
    def handle_files_api(self):
        try:
            files = []
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    for line in f:
                        if line.strip().startswith('- '):
                            file_path = line.strip()[2:].strip()
                            expanded_path = os.path.expanduser(file_path)
                            exists = os.path.exists(expanded_path)
                            
                            # Check if file has history
                            safe_filename = expanded_path.replace('/', '_').replace('~', 'home')
                            if safe_filename.startswith('_'):
                                safe_filename = safe_filename[1:]
                            has_history = os.path.exists(os.path.join(REPO_DIR, safe_filename))
                            
                            files.append({
                                'name': file_path,
                                'exists': exists,
                                'has_history': has_history
                            })
            
            self.send_json_response({'files': files})
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_diff_api(self):
        try:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_path = query.get('file', [''])[0]
            
            if not file_path:
                self.send_error(400, 'File parameter required')
                return
            
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                self.send_error(404, 'File not found')
                return
            
            safe_filename = expanded_path.replace('/', '_').replace('~', 'home')
            if safe_filename.startswith('_'):
                safe_filename = safe_filename[1:]
            
            repo_file = os.path.join(REPO_DIR, safe_filename)
            if not os.path.exists(repo_file):
                self.send_text_response('No history found for: ' + file_path)
                return
            
            # Get diff using git
            result = subprocess.run(
                ['git', 'diff', 'HEAD~1', safe_filename],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.send_text_response(result.stdout)
            else:
                self.send_text_response('No previous version found')
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_history_api(self):
        try:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_path = query.get('file', [''])[0]
            
            if not file_path:
                self.send_error(400, 'File parameter required')
                return
            
            expanded_path = os.path.expanduser(file_path)
            safe_filename = expanded_path.replace('/', '_').replace('~', 'home')
            if safe_filename.startswith('_'):
                safe_filename = safe_filename[1:]
            
            repo_file = os.path.join(REPO_DIR, safe_filename)
            if not os.path.exists(repo_file):
                self.send_text_response('No history found for: ' + file_path)
                return
            
            # Get history using git
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', safe_filename],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.send_text_response(result.stdout)
            else:
                self.send_text_response('No history found')
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_snapshot_api(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            file_path = data.get('file', '')
            
            if not file_path:
                self.send_json_response({'success': False, 'error': 'File parameter required'})
                return
            
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                self.send_json_response({'success': False, 'error': 'File not found'})
                return
            
            safe_filename = expanded_path.replace('/', '_').replace('~', 'home')
            if safe_filename.startswith('_'):
                safe_filename = safe_filename[1:]
            
            repo_file = os.path.join(REPO_DIR, safe_filename)
            
            # Copy file to repo
            import shutil
            shutil.copy2(expanded_path, repo_file)
            
            # Add to git
            result = subprocess.run(['git', 'add', safe_filename], cwd=REPO_DIR)
            if result.returncode != 0:
                self.send_json_response({'success': False, 'error': 'Failed to add to git'})
                return
            
            # Check if there are changes
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=REPO_DIR)
            if result.returncode == 0:
                self.send_json_response({'success': True, 'message': 'No changes detected'})
                return
            
            # Commit changes
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = subprocess.run(
                ['git', 'commit', '-m', f'Web-snapshot: {file_path} at {timestamp}'],
                cwd=REPO_DIR
            )
            
            if result.returncode == 0:
                self.send_json_response({'success': True, 'message': f'Snapshot created for {file_path}'})
            else:
                self.send_json_response({'success': False, 'error': 'Failed to commit'})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_text_response(self, text):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode())

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    os.chdir(WEB_DIR)
    
    with socketserver.TCPServer(("", port), ConfWatchHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{port}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()
EOF
}

# Start HTTP server
start_server() {
    log_info "Starting ConfWatch Python web server on port $PORT"
    echo -e "${GREEN}Web interface available at: http://0.0.0.0:$PORT${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    
    # Create Python server
    create_python_server
    
    # Start server
    cd "$WEB_DIR"
    python3 server.py "$PORT"
}

# Show help
show_help() {
    echo -e "${GREEN}ConfWatch Python Web API${NC}"
    echo "=================================================="
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -p, --port PORT     Port to listen on (default: 8080)"
    echo "  -h, --help          Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0"
    echo "  $0 -p 9000"
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
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if ConfWatch is installed
if [[ ! -d "$CONFWATCH_HOME" ]]; then
    log_error "ConfWatch is not installed. Run ./install.sh first."
    exit 1
fi

# Check if Python is available
PYTHON_CMD=$(check_python)
if [[ $? -ne 0 ]]; then
    log_error "Python 3 is required but not installed."
    exit 1
fi

log_info "Using Python: $PYTHON_CMD"

# Start server
start_server 