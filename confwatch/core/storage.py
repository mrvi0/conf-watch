"""
Storage modules for version control of configuration files.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import git
import hashlib


class BaseStorage:
    """Base class for storage backends."""
    
    def __init__(self, storage_path: str):
        """Initialize storage with path."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save file content to storage."""
        raise NotImplementedError
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """Get file version history."""
        raise NotImplementedError
    
    def get_file_diff(self, file_path: str, version1: str, version2: str) -> str:
        """Get diff between two versions."""
        raise NotImplementedError


class GitStorage(BaseStorage):
    """Git-based storage backend."""
    
    def __init__(self, storage_path: str):
        """Initialize Git storage."""
        super().__init__(storage_path)
        self._init_repo()
    
    def _init_repo(self):
        """Initialize Git repository."""
        try:
            self.repo = git.Repo(self.storage_path)
        except git.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.storage_path)
            # Configure Git user
            self.repo.config_writer().set_value("user", "name", "ConfWatch").release()
            self.repo.config_writer().set_value("user", "email", "confwatch@localhost").release()
    
    def _safe_name(self, file_path: str) -> str:
        abs_path = str(Path(file_path).expanduser().resolve())
        h = hashlib.sha256(abs_path.encode()).hexdigest()
        return f"{h}_{Path(file_path).name}"

    def save_file(self, file_path: str, content: str, comment: str = '', force: bool = False) -> bool:
        try:
            abs_path = str(Path(file_path).expanduser().resolve())
            safe_name = self._safe_name(abs_path)
            storage_file = self.storage_path / safe_name
            with open(storage_file, 'w') as f:
                f.write(content)
            self.repo.index.add([safe_name])
            try:
                has_changes = self.repo.index.diff('HEAD') or len(list(self.repo.iter_commits())) == 0
                if has_changes or force:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = f"Snapshot: {abs_path} at {timestamp}"
                    if comment:
                        msg += f"\n{comment}"
                    self.repo.index.commit(msg)
                    return True
            except git.BadName:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg = f"Snapshot: {abs_path} at {timestamp}"
                if comment:
                    msg += f"\n{comment}"
                self.repo.index.commit(msg)
                return True
            return False
        except Exception as e:
            print(f"Error saving file to Git: {e}")
            return False
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """Get Git history for file."""
        try:
            safe_name = self._safe_name(file_path)
            
            # Проверяем, что файл существует в репозитории
            if not (self.storage_path / safe_name).exists():
                return []
            
            commits = list(self.repo.iter_commits(paths=safe_name))
            
            history = []
            for commit in commits:
                history.append({
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                    'author': commit.author.name
                })
            
            return history
        except Exception as e:
            print(f"Error getting file history: {e}")
            return []
    
    def get_file_diff(self, file_path: str, version1: str, version2: str) -> str:
        """Get Git diff between versions."""
        try:
            safe_name = self._safe_name(file_path)
            
            # Проверяем, что файл существует в репозитории
            if not (self.storage_path / safe_name).exists():
                return ""
            
            # Проверяем, что коммиты существуют
            try:
                self.repo.commit(version1)
                self.repo.commit(version2)
            except Exception as e:
                print(f"Error: Invalid commit hash: {e}")
                return ""
            
            diff = self.repo.git.diff(version1, version2, '--', safe_name)
            return diff
        except Exception as e:
            print(f"Error getting diff: {e}")
            return ""


class SQLiteStorage(BaseStorage):
    """SQLite-based storage backend."""
    
    def __init__(self, storage_path: str):
        """Initialize SQLite storage."""
        super().__init__(storage_path)
        self.db_path = self.storage_path / "confwatch.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                content TEXT NOT NULL,
                hash TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save file to SQLite database."""
        try:
            import sqlite3
            import hashlib
            
            file_name = Path(file_path).name
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if content has changed
            cursor.execute(
                "SELECT hash FROM files WHERE file_name = ? ORDER BY timestamp DESC LIMIT 1",
                (file_name,)
            )
            result = cursor.fetchone()
            
            if result and result[0] == file_hash:
                # No changes
                conn.close()
                return False
            
            # Save new version
            cursor.execute(
                "INSERT INTO files (file_path, file_name, content, hash) VALUES (?, ?, ?, ?)",
                (file_path, file_name, content, file_hash)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving file to SQLite: {e}")
            return False
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """Get SQLite history for file."""
        try:
            import sqlite3
            
            file_name = Path(file_path).name
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, file_path, content, hash, timestamp FROM files WHERE file_name = ? ORDER BY timestamp DESC",
                (file_name,)
            )
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'file_path': row[1],
                    'hash': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"Error getting file history: {e}")
            return []
    
    def get_file_diff(self, file_path: str, version1: str, version2: str) -> str:
        """Get diff between SQLite versions."""
        try:
            import sqlite3
            import difflib
            
            file_name = Path(file_path).name
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get content for both versions
            cursor.execute("SELECT content FROM files WHERE id = ?", (version1,))
            content1 = cursor.fetchone()[0]
            
            cursor.execute("SELECT content FROM files WHERE id = ?", (version2,))
            content2 = cursor.fetchone()[0]
            
            conn.close()
            
            # Generate diff
            diff = difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"{file_path} (v{version1})",
                tofile=f"{file_path} (v{version2})"
            )
            
            return ''.join(diff)
            
        except Exception as e:
            print(f"Error getting diff: {e}")
            return "" 