"""
File watcher module for automatic change detection.
"""

import os
import time
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from ..core.scanner import FileScanner
from ..core.storage import GitStorage


class ConfigFileHandler(FileSystemEventHandler):
    """Handle file system events for monitored configuration files."""
    
    def __init__(self, watcher):
        self.watcher = watcher
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        if self.watcher.should_monitor_file(file_path):
            self.watcher.schedule_snapshot(file_path, "File modified")


class FileWatcher:
    """Watches configuration files for changes and creates automatic snapshots."""
    
    def __init__(self, config_file: str, repo_dir: str):
        self.config_file = config_file
        self.repo_dir = repo_dir
        self.scanner = FileScanner(config_file)
        self.storage = GitStorage(repo_dir)
        
        # Monitoring state
        self.is_running = False
        self.observer = None
        self.polling_thread = None
        self.stop_event = threading.Event()
        
        # Debouncing
        self.pending_snapshots: Dict[str, threading.Timer] = {}
        self.debounce_delay = 5  # seconds
        
        # File hashes for polling mode
        self.file_hashes: Dict[str, str] = {}
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load monitoring configuration."""
        # For now, use simple defaults
        # TODO: Load from config file
        self.auto_monitoring_enabled = True
        self.polling_interval = 30  # seconds
        self.ignore_patterns = [
            r'.*\.swp$',      # Vim swap files
            r'.*\.tmp$',      # Temporary files
            r'.*~$',          # Backup files
            r'.*\.bak$',      # Backup files
        ]
    
    def should_monitor_file(self, file_path: str) -> bool:
        """Check if file should be monitored."""
        # Get absolute path
        abs_path = str(Path(file_path).resolve())
        
        # Check if file is in our monitored list
        watched_files = self.scanner.get_watched_files()
        monitored_paths = {str(Path(f['original_path']).expanduser().resolve()) 
                          for f in watched_files if f.get('exists', False)}
        
        return abs_path in monitored_paths
    
    def schedule_snapshot(self, file_path: str, reason: str = "Auto-detected change"):
        """Schedule a debounced snapshot creation."""
        abs_path = str(Path(file_path).resolve())
        
        # Cancel existing timer for this file
        if abs_path in self.pending_snapshots:
            self.pending_snapshots[abs_path].cancel()
        
        # Schedule new snapshot
        timer = threading.Timer(
            self.debounce_delay,
            self.create_auto_snapshot,
            [abs_path, reason]
        )
        self.pending_snapshots[abs_path] = timer
        timer.start()
        
        print(f"[WATCHER] Scheduled snapshot for {abs_path} (reason: {reason})")
    
    def create_auto_snapshot(self, file_path: str, reason: str):
        """Create an automatic snapshot."""
        try:
            # Remove from pending
            if file_path in self.pending_snapshots:
                del self.pending_snapshots[file_path]
            
            # Check if file still exists and has actually changed
            if not os.path.exists(file_path):
                print(f"[WATCHER] File no longer exists: {file_path}")
                return
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"[WATCHER] Failed to read file {file_path}: {e}")
                return
            
            # Create snapshot with auto comment
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            comment = f"[AUTO] {reason} at {timestamp}"
            
            # Find original path (the path as configured by user)
            original_path = self.get_original_path(file_path)
            if not original_path:
                print(f"[WATCHER] Could not determine original path for {file_path}")
                return
            
            # Create snapshot
            if self.storage.save_file(file_path, content, comment=comment, force=False):
                print(f"[WATCHER] Created auto snapshot for {original_path}")
            else:
                print(f"[WATCHER] No changes detected in {original_path}")
                
        except Exception as e:
            print(f"[WATCHER] Error creating snapshot for {file_path}: {e}")
    
    def get_original_path(self, abs_path: str) -> Optional[str]:
        """Get the original configured path for an absolute path."""
        watched_files = self.scanner.get_watched_files()
        for file_info in watched_files:
            if file_info.get('exists', False):
                file_abs_path = str(Path(file_info['original_path']).expanduser().resolve())
                if file_abs_path == abs_path:
                    return file_info['original_path']
        return None
    
    def start_watchdog_monitoring(self):
        """Start file monitoring using watchdog."""
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError("Watchdog library not available. Install with: pip install watchdog")
        
        self.observer = Observer()
        handler = ConfigFileHandler(self)
        
        # Watch directories containing our monitored files
        watched_dirs = set()
        watched_files = self.scanner.get_watched_files()
        
        for file_info in watched_files:
            if file_info.get('exists', False):
                file_path = Path(file_info['path']).parent
                watched_dirs.add(str(file_path))
        
        # Schedule watchers for each directory
        for dir_path in watched_dirs:
            if os.path.exists(dir_path):
                self.observer.schedule(handler, dir_path, recursive=False)
                print(f"[WATCHER] Watching directory: {dir_path}")
        
        self.observer.start()
        print("[WATCHER] File monitoring started (watchdog mode)")
    
    def start_polling_monitoring(self):
        """Start file monitoring using polling."""
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        print("[WATCHER] File monitoring started (polling mode)")
    
    def _polling_loop(self):
        """Polling loop for file monitoring."""
        while not self.stop_event.is_set():
            try:
                watched_files = self.scanner.get_watched_files()
                
                for file_info in watched_files:
                    if not file_info.get('exists', False):
                        continue
                    
                    file_path = file_info['path']
                    abs_path = str(Path(file_path).resolve())
                    
                    try:
                        # Calculate current hash
                        with open(file_path, 'rb') as f:
                            current_hash = hashlib.sha256(f.read()).hexdigest()
                        
                        # Check if hash changed
                        if abs_path in self.file_hashes:
                            if self.file_hashes[abs_path] != current_hash:
                                self.schedule_snapshot(abs_path, "File content changed")
                        
                        # Update stored hash
                        self.file_hashes[abs_path] = current_hash
                        
                    except Exception as e:
                        print(f"[WATCHER] Error checking file {file_path}: {e}")
                
                # Wait for next check
                self.stop_event.wait(self.polling_interval)
                
            except Exception as e:
                print(f"[WATCHER] Error in polling loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start(self, use_watchdog: bool = True):
        """Start file monitoring."""
        if self.is_running:
            print("[WATCHER] Already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        try:
            if use_watchdog and WATCHDOG_AVAILABLE:
                self.start_watchdog_monitoring()
            else:
                if use_watchdog:
                    print("[WATCHER] Watchdog not available, falling back to polling")
                self.start_polling_monitoring()
        except Exception as e:
            print(f"[WATCHER] Failed to start monitoring: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop file monitoring."""
        if not self.is_running:
            print("[WATCHER] Not running")
            return
        
        print("[WATCHER] Stopping file monitoring...")
        
        # Stop observer
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        # Stop polling thread
        self.stop_event.set()
        if self.polling_thread:
            self.polling_thread.join(timeout=5)
            self.polling_thread = None
        
        # Cancel pending snapshots
        for timer in self.pending_snapshots.values():
            timer.cancel()
        self.pending_snapshots.clear()
        
        self.is_running = False
        print("[WATCHER] File monitoring stopped")
    
    def status(self) -> dict:
        """Get monitoring status."""
        watched_files = self.scanner.get_watched_files()
        monitored_count = sum(1 for f in watched_files if f.get('exists', False))
        
        return {
            'running': self.is_running,
            'mode': 'watchdog' if (self.observer and WATCHDOG_AVAILABLE) else 'polling',
            'monitored_files': monitored_count,
            'pending_snapshots': len(self.pending_snapshots),
            'watchdog_available': WATCHDOG_AVAILABLE,
        } 