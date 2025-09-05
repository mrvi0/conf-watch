"""
Flask web application for ConfWatch.
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from ..core.scanner import FileScanner
from ..core.storage import GitStorage
from ..core.auth import AuthManager
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import confwatch

app = Flask(__name__)

# Configuration
CONFWATCH_HOME = os.path.expanduser("~/.confwatch")
CONFIG_FILE = os.path.join(CONFWATCH_HOME, "config", "config.yml")
REPO_DIR = os.path.join(CONFWATCH_HOME, "repo")
WEB_DIR = os.path.join(CONFWATCH_HOME, "web")

# Session configuration
app.secret_key = os.urandom(24)

# Initialize auth manager
auth_manager = AuthManager(CONFIG_FILE)

def require_auth(f):
    """Decorator to require authentication for routes."""
    def decorated_function(*args, **kwargs):
        # Check if authentication is enabled
        if not auth_manager.is_authenticated():
            return send_from_directory(WEB_DIR, 'index.html')
        
        # Check if user is authenticated
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
@require_auth
def index():
    """Serve the main web interface."""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/login')
def login():
    """Serve the login page."""
    if session.get('authenticated'):
        return redirect(url_for('index'))
    return send_from_directory(WEB_DIR, 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(WEB_DIR, filename)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for login."""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'})
        
        if auth_manager.verify_password(password):
            session['authenticated'] = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid password'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout."""
    session.pop('authenticated', None)
    return jsonify({'success': True})

@app.route('/api/auth/status')
def api_auth_status():
    """API endpoint to check authentication status."""
    return jsonify({
        'authenticated': session.get('authenticated', False),
        'auth_enabled': auth_manager.is_authenticated()
    })

@app.route('/api/rollback', methods=['POST'])
@require_auth
def api_rollback():
    """API endpoint for rollback."""
    try:
        data = request.get_json()
        file_path = data.get('file')
        commit_hash = data.get('commit_hash')
        
        if not file_path or not commit_hash:
            return jsonify({'success': False, 'error': 'Missing file path or commit hash'})
        
        # Валидация пути - проверяем, что файл находится в разрешенных директориях
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        
        # Проверяем, что файл существует и находится в разрешенных директориях
        if not os.path.exists(expanded_path):
            return jsonify({'success': False, 'error': f'File not found: {file_path}'})
        
        # Получаем абсолютный путь для корректной работы с storage
        abs_path = str(Path(file_path).expanduser().resolve())
        
        # Выполняем rollback
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(abs_path)
        
        if not history:
            return jsonify({'success': False, 'error': f'No history found for {file_path}'})
        
        # Проверяем, что коммит существует в истории
        commit_exists = any(entry['hash'] == commit_hash for entry in history)
        if not commit_exists:
            # Попробуем найти по короткому хешу
            matching_commits = [entry for entry in history if entry['hash'].startswith(commit_hash)]
            if len(matching_commits) == 1:
                commit_hash = matching_commits[0]['hash']
            elif len(matching_commits) > 1:
                return jsonify({'success': False, 'error': f'Multiple commits found for prefix {commit_hash[:8]}. Please use full commit hash.'})
            else:
                return jsonify({'success': False, 'error': f'Commit {commit_hash[:8]} not found in history'})
        
        # Получаем safe_name для файла используя абсолютный путь
        safe_name = storage._safe_name(abs_path)
        
        try:
            # Получаем содержимое файла из git по нужному коммиту
            file_content = storage.repo.git.show(f"{commit_hash}:{safe_name}")
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to retrieve file content from commit {commit_hash[:8]}: {str(e)}'})
        
        # Перезаписываем отслеживаемый файл этим содержимым с правильной кодировкой
        try:
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to write file {file_path}: {str(e)}'})
        
        # Создаём снапшот с комментарием используя абсолютный путь
        rollback_comment = f"Rollback from commit {commit_hash[:8]}"
        if not storage.save_file(abs_path, file_content, comment=rollback_comment, force=True):
            return jsonify({'success': False, 'error': 'Failed to create rollback snapshot'})
        
        return jsonify({
            'success': True, 
            'message': f'Successfully rolled back {file_path} to commit {commit_hash[:8]}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files')
@require_auth
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
@require_auth
def get_diff():
    try:
        file_path = request.args.get('file')  # оригинальный путь
        if not file_path:
            return jsonify({'error': 'File parameter required'}), 400
        
        scanner = FileScanner(CONFIG_FILE)
        expanded_path = scanner.expand_path(file_path)
        
        if not os.path.exists(expanded_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Получаем абсолютный путь для корректной работы с storage
        abs_path = str(Path(file_path).expanduser().resolve())
        
        # Читаем текущее содержимое файла с правильной кодировкой
        try:
            with open(expanded_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception as e:
            return jsonify({'error': f'Failed to read file: {str(e)}'}), 500
        
        storage = GitStorage(REPO_DIR)
        # История по абсолютному пути
        history = storage.get_file_history(abs_path)
        
        if not history:
            return jsonify({'error': 'No history found'}), 404
        
        if len(history) < 2:
            return jsonify({'error': 'No previous version found'}), 404
        
        prev_commit = history[1]['hash']
        curr_commit = history[0]['hash']
        
        try:
            diff = storage.get_file_diff(abs_path, prev_commit, curr_commit)
            return diff, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except Exception as e:
            return jsonify({'error': f'Failed to generate diff: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
@require_auth
def get_history():
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'error': 'File parameter required'}), 400
        
        # Получаем абсолютный путь для корректной работы с storage
        abs_path = str(Path(file_path).expanduser().resolve())
        
        storage = GitStorage(REPO_DIR)
        history = storage.get_file_history(abs_path)
        
        if not history:
            return jsonify({'error': 'No history found'}), 404
        
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshot', methods=['POST'])
@require_auth
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
        
        # Читаем файл с правильной кодировкой
        try:
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to read file: {str(e)}'}), 500
        
        storage = GitStorage(REPO_DIR)
        if storage.save_file(abs_path, content, comment=comment, force=force):
            return jsonify({'success': True, 'message': f'Snapshot created for {abs_path}'})
        else:
            return jsonify({'success': True, 'message': f'No changes detected in {abs_path}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/diff_between')
@require_auth
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

@app.route('/api/version')
def api_version():
    return jsonify({"version": confwatch.__version__})

def run_web_server(host='0.0.0.0', port=5000, debug=False):
    """Run the web server."""
    print(f"Starting ConfWatch web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_server() 