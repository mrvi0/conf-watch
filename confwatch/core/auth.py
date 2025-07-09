"""
Authentication module for ConfWatch.
Provides simple password-based authentication with unique passwords per installation.
"""

import os
import secrets
import hashlib
import yaml
from pathlib import Path


class AuthManager:
    """Manages authentication for ConfWatch web interface."""
    
    def __init__(self, config_file):
        """Initialize AuthManager with config file path."""
        self.config_file = config_file
        self.auth_file = os.path.join(os.path.dirname(config_file), "auth.yml")
    
    def generate_password(self):
        """Generate a random password for this installation."""
        # Generate a 12-character password with mixed case and numbers
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        return password
    
    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_password(self, password):
        """Save hashed password to auth file."""
        auth_data = {
            'password_hash': self.hash_password(password),
            'created_at': str(Path().cwd())
        }
        
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        with open(self.auth_file, 'w') as f:
            yaml.dump(auth_data, f, default_flow_style=False)
    
    def get_stored_password_hash(self):
        """Get stored password hash from auth file."""
        if not os.path.exists(self.auth_file):
            return None
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = yaml.safe_load(f)
                return auth_data.get('password_hash')
        except Exception:
            return None
    
    def verify_password(self, password):
        """Verify if provided password matches stored hash."""
        stored_hash = self.get_stored_password_hash()
        if not stored_hash:
            return False
        
        return self.hash_password(password) == stored_hash
    
    def is_authenticated(self):
        """Check if authentication is set up."""
        return self.get_stored_password_hash() is not None
    
    def get_password_info(self):
        """Get information about stored password."""
        if not os.path.exists(self.auth_file):
            return None
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = yaml.safe_load(f)
                return {
                    'created_at': auth_data.get('created_at', 'Unknown'),
                    'has_password': bool(auth_data.get('password_hash'))
                }
        except Exception:
            return None 