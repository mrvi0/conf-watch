"""
Flask web application for ConfWatch.
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from ..core.scanner import FileScanner
from ..core.storage import GitStorage

app = Flask(__name__)

# Configuration
CONFWATCH_HOME = os.path.expanduser("~/.confwatch")
CONFIG_FILE = os.path.join(CONFWATCH_HOME, "config", "config.yml")
REPO_DIR = os.path.join(CONFWATCH_HOME, "repo")
WEB_DIR = os.path.join(CONFWATCH_HOME, "web")

@app.route('/')
def index():
    """Serve the main web interface."""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/api/files')
def get_files():
    """Get list of monitored files."""
    try:
        scanner = FileScanner(CONFIG_FILE)
        files = scanner.get_watched_files()
        
        result = []
        for file_info in files:
            # Check if file has history
            has_history = False
            if file_info['exists']:
                storage = GitStorage(REPO_DIR)
                history = storage.get_file_history(file_info['path'])
                has_history = len(history) > 0
            
            result.append({
                'name': file_info['path'],
                'exists': file_info['exists'],
                'has_history': has_history
            })
        
        return jsonify({'files': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diff')
def get_diff():
    """Get diff for a file."""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return "File parameter required", 400
        
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        
        if not os.path.exists(expanded_path):
            return "File not found", 404
        
        # Get current content
        with open(expanded_path, 'r') as f:
            current_content = f.read()
        
        # Get last version from storage
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(file_path)
        
        if not history:
            return "No history found", 404
        
        # Get previous version content
        file_name = Path(file_path).name
        storage_file = Path(REPO_DIR) / file_name
        
        if storage_file.exists():
            with open(storage_file, 'r') as f:
                previous_content = f.read()
            
            # Generate diff
            from ..core.diff import DiffViewer
            diff_output = DiffViewer.unified_diff(
                previous_content, current_content,
                f"{file_path} (previous)", f"{file_path} (current)"
            )
            return diff_output
        else:
            return "No previous version found", 404
    
    except Exception as e:
        return str(e), 500

@app.route('/api/history')
def get_history():
    """Get history for a file."""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return "File parameter required", 400
        
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(file_path)
        
        if not history:
            return "No history found", 404
        
        # Format history
        result = []
        for entry in history:
            result.append(f"[{entry['date']}] {entry['hash'][:8]} - {entry['message']}")
        
        return "\n".join(result)
    
    except Exception as e:
        return str(e), 500

@app.route('/api/snapshot', methods=['POST'])
def create_snapshot():
    """Create snapshot for a file."""
    try:
        data = request.get_json()
        file_path = data.get('file')
        
        if not file_path:
            return jsonify({'success': False, 'error': 'File parameter required'}), 400
        
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        
        if not os.path.exists(expanded_path):
            return jsonify({'success': False, 'error': f'File not found: {file_path}'}), 400
        
        # Read file content
        with open(expanded_path, 'r') as f:
            content = f.read()
        
        # Save to storage
        storage = GitStorage(REPO_DIR)
        if storage.save_file(file_path, content):
            return jsonify({'success': True, 'message': f'Snapshot created for {file_path}'})
        else:
            return jsonify({'success': True, 'message': f'No changes detected in {file_path}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def run_web_server(host='localhost', port=5000, debug=False):
    """Run the web server."""
    print(f"Starting ConfWatch web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_server() 