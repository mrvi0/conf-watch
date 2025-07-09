"""
Flask web application for ConfWatch.
"""

import os
import json
import yaml
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from ..core.scanner import FileScanner, update_config_with_password
from ..core.storage import GitStorage

app = Flask(__name__)

# Configuration
CONFWATCH_HOME = os.path.expanduser("~/.confwatch")
CONFIG_FILE = os.path.join(CONFWATCH_HOME, "config", "config.yml")
REPO_DIR = os.path.join(CONFWATCH_HOME, "repo")
WEB_DIR = os.path.join(CONFWATCH_HOME, "web")

def load_auth_config():
    """Load authentication configuration."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('web_auth', {})
    except Exception as e:
        print(f"Error loading auth config: {e}")
        return {'enabled': False}

def check_auth(username, password):
    """Check if username and password are correct."""
    auth_config = load_auth_config()
    if not auth_config.get('enabled', False):
        return True
    
    return (username == auth_config.get('username', 'admin') and 
            password == auth_config.get('password', ''))

def authenticate():
    """Send 401 response that enables basic auth."""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="ConfWatch Web Interface"'})

@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors with styled auth page."""
    return send_from_directory(WEB_DIR, 'auth.html'), 401

def requires_auth(f):
    """Decorator to require basic auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_config = load_auth_config()
        if not auth_config.get('enabled', False):
            return f(*args, **kwargs)
        
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    """Serve the main web interface."""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/<path:filename>')
@requires_auth
def static_files(filename):
    return send_from_directory(WEB_DIR, filename)

@app.route('/api/rollback', methods=['POST'])
@requires_auth
def api_rollback():
    """API endpoint for rollback."""
    try:
        data = request.get_json()
        file_path = data.get('file')
        commit_hash = data.get('commit_hash')
        
        if not file_path or not commit_hash:
            return jsonify({'success': False, 'error': 'Missing file path or commit hash'})
        
        # Выполняем rollback
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(file_path)
        
        if not history:
            return jsonify({'success': False, 'error': f'No history found for {file_path}'})
        
        # Проверяем, что коммит существует в истории
        commit_exists = any(entry['hash'] == commit_hash for entry in history)
        if not commit_exists:
            # Попробуем найти по короткому хешу
            commit_exists = any(entry['hash'].startswith(commit_hash) for entry in history)
            if commit_exists:
                # Найдём полный хеш
                for entry in history:
                    if entry['hash'].startswith(commit_hash):
                        commit_hash = entry['hash']
                        break
            else:
                return jsonify({'success': False, 'error': f'Commit {commit_hash[:8]} not found in history'})
        
        # Получаем safe_name для файла
        safe_name = storage._safe_name(file_path)
        # Получаем содержимое файла из git по нужному коммиту
        file_content = storage.repo.git.show(f"{commit_hash}:{safe_name}")
        
        # Перезаписываем отслеживаемый файл этим содержимым
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        with open(expanded_path, 'w') as f:
            f.write(file_content)
        
        # Создаём снапшот с комментарием
        rollback_comment = f"Rollback from commit {commit_hash[:8]}"
        storage.save_file(file_path, file_content, comment=rollback_comment, force=True)
        
        return jsonify({
            'success': True, 
            'message': f'Successfully rolled back {file_path} to commit {commit_hash[:8]}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files')
@requires_auth
def get_files():
    """Get list of monitored files."""
    try:
        scanner = FileScanner(CONFIG_FILE)
        files = scanner.get_watched_files()
        
        result = []
        for file_info in files:
            # Check if file has history
            has_history = False
            history_count = 0
            abs_path = str(Path(file_info['original_path']).expanduser().resolve())
            if file_info['exists']:
                storage = GitStorage(REPO_DIR)
                history = storage.get_file_history(abs_path)
                history_count = len(history)
                has_history = history_count > 0
            
            result.append({
                'name': file_info['original_path'],
                'abs_path': abs_path,
                'exists': file_info['exists'],
                'has_history': has_history,
                'history_count': history_count
            })
        
        return jsonify({'files': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diff')
@requires_auth
def get_diff():
    try:
        file_path = request.args.get('file')  # оригинальный путь
        if not file_path:
            return jsonify({'error': 'File parameter required'}), 400
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        if not os.path.exists(expanded_path):
            return jsonify({'error': 'File not found'}), 404
        # Читаем текущее содержимое файла (expanded_path)
        with open(expanded_path, 'r') as f:
            current_content = f.read()
        storage = GitStorage(REPO_DIR)
        # История по оригинальному пути
        history = storage.get_file_history(file_path)
        if not history:
            return jsonify({'error': 'No history found'}), 404
        if len(history) < 2:
            return jsonify({'error': 'No previous version found'}), 404
        prev_commit = history[1]['hash']
        curr_commit = history[0]['hash']
        diff = storage.get_file_diff(file_path, prev_commit, curr_commit)
        return diff, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
@requires_auth
def get_history():
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'error': 'File parameter required'}), 400
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(file_path)
        if not history:
            return jsonify({'error': 'No history found'}), 404
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshot', methods=['POST'])
@requires_auth
def create_snapshot():
    try:
        data = request.get_json()
        file_path = data.get('file')
        comment = data.get('comment', '').strip()
        force = bool(data.get('force', False))
        if not file_path:
            return jsonify({'success': False, 'error': 'File parameter required'}), 400
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        abs_path = str(Path(file_path).expanduser().resolve())
        if not os.path.exists(expanded_path):
            return jsonify({'success': False, 'error': f'File not found: {file_path}'}), 400
        with open(expanded_path, 'r') as f:
            content = f.read()
        storage = GitStorage(REPO_DIR)
        if storage.save_file(abs_path, content, comment=comment, force=force):
            return jsonify({'success': True, 'message': f'Snapshot created for {abs_path}'})
        else:
            return jsonify({'success': True, 'message': f'No changes detected in {abs_path}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/diff_between')
@requires_auth
def get_diff_between():
    try:
        file_path = request.args.get('file')
        from_hash = request.args.get('from')
        to_hash = request.args.get('to')
        if not file_path or not from_hash or not to_hash:
            return jsonify({'error': 'file, from, to parameters required'}), 400
        storage = GitStorage(REPO_DIR)
        diff = storage.get_file_diff(file_path, from_hash, to_hash)
        return diff, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_web_server(host='localhost', port=5000, debug=False):
    """Run the web server."""
    print(f"Starting ConfWatch web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_server() 