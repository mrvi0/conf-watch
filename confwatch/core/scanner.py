"""
File scanner module for monitoring configuration files.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import yaml


class FileScanner:
    """Scans and monitors configuration files for changes."""
    
    def __init__(self, config_path: str):
        """Initialize scanner with configuration file path."""
        self.config_path = config_path
        self.config = self._load_config()
        # Handle both list format and dict format
        if isinstance(self.config, list):
            self.watched_files = self.config
        else:
            self.watched_files = self.config.get('watch', []) if self.config else []
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {'watch': []}
                return yaml.safe_load(content) or {'watch': []}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def expand_path(self, path: str) -> str:
        """Expand tilde and resolve absolute path."""
        return str(Path(path).expanduser().resolve())
    
    def get_watched_files(self) -> List[Dict]:
        """Get list of watched files with their status."""
        files = []
        for file_path in self.watched_files:
            expanded_path = self.expand_path(file_path)
            exists = os.path.exists(expanded_path)
            files.append({
                'original_path': file_path,
                'path': expanded_path,
                'expanded_path': expanded_path,
                'exists': exists,
                'hash': self.get_file_hash(expanded_path) if exists else None
            })
        return files
    
    def has_changes(self, file_path: str, previous_hash: str) -> bool:
        """Check if file has changed since last snapshot."""
        if not os.path.exists(file_path):
            return False
        current_hash = self.get_file_hash(file_path)
        return current_hash != previous_hash 