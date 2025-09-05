"""
Daemon manager for ConfWatch file monitoring.
"""

import os
import sys
import signal
import time
import json
import atexit
from pathlib import Path
from typing import Optional

from .watcher import FileWatcher


class DaemonManager:
    """Manages the ConfWatch daemon process."""
    
    def __init__(self, config_file: str, repo_dir: str):
        self.config_file = config_file
        self.repo_dir = repo_dir
        
        # Daemon state
        confwatch_home = os.path.dirname(os.path.dirname(config_file))
        self.pid_file = os.path.join(confwatch_home, "daemon.pid")
        self.log_file = os.path.join(confwatch_home, "daemon.log")
        
        self.watcher: Optional[FileWatcher] = None
        self.running = False
    
    def is_running(self) -> bool:
        """Check if daemon is already running."""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            try:
                os.kill(pid, 0)  # Send signal 0 to check if process exists
                return True
            except OSError:
                # Process doesn't exist, remove stale pid file
                os.unlink(self.pid_file)
                return False
                
        except (ValueError, FileNotFoundError):
            return False
    
    def get_pid(self) -> Optional[int]:
        """Get daemon PID if running."""
        if not os.path.exists(self.pid_file):
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    
    def start(self, background: bool = True, use_watchdog: bool = True) -> bool:
        """Start the daemon."""
        if self.is_running():
            print(f"[DAEMON] Already running (PID: {self.get_pid()})")
            return False
        
        if background:
            return self._start_background(use_watchdog)
        else:
            return self._start_foreground(use_watchdog)
    
    def _start_foreground(self, use_watchdog: bool = True) -> bool:
        """Start daemon in foreground."""
        print("[DAEMON] Starting ConfWatch daemon in foreground...")
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Setup cleanup
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            # Start file watcher
            self.watcher = FileWatcher(self.config_file, self.repo_dir)
            self.watcher.start(use_watchdog=use_watchdog)
            self.running = True
            
            print(f"[DAEMON] Started successfully (PID: {os.getpid()})")
            
            # Keep daemon running
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[DAEMON] Received interrupt signal")
            
            return True
            
        except Exception as e:
            print(f"[DAEMON] Failed to start: {e}")
            self._cleanup()
            return False
    
    def _start_background(self, use_watchdog: bool = True) -> bool:
        """Start daemon in background."""
        print("[DAEMON] Starting ConfWatch daemon in background...")
        
        # Fork process
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                print(f"[DAEMON] Started successfully (PID: {pid})")
                return True
        except OSError as e:
            print(f"[DAEMON] Failed to fork: {e}")
            return False
        
        # Child process continues here
        try:
            # Detach from parent
            os.setsid()
            
            # Fork again to prevent zombie
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
            
            # Change working directory
            os.chdir("/")
            
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            
            # Redirect to log file
            with open(self.log_file, 'a') as log:
                os.dup2(log.fileno(), sys.stdout.fileno())
                os.dup2(log.fileno(), sys.stderr.fileno())
            
            # Close stdin
            sys.stdin.close()
            
            # Write PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Setup cleanup
            atexit.register(self._cleanup)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start file watcher
            self.watcher = FileWatcher(self.config_file, self.repo_dir)
            self.watcher.start(use_watchdog=use_watchdog)
            self.running = True
            
            print(f"[DAEMON] Background daemon started (PID: {os.getpid()})")
            
            # Keep daemon running
            while self.running:
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"[DAEMON] Failed to start background daemon: {e}")
            self._cleanup()
            sys.exit(1)
    
    def stop(self) -> bool:
        """Stop the daemon."""
        if not self.is_running():
            print("[DAEMON] Not running")
            return False
        
        pid = self.get_pid()
        if pid is None:
            print("[DAEMON] Could not determine PID")
            return False
        
        try:
            print(f"[DAEMON] Stopping daemon (PID: {pid})")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):  # Wait up to 10 seconds
                if not self.is_running():
                    print("[DAEMON] Stopped successfully")
                    return True
                time.sleep(1)
            
            # Force kill if still running
            print("[DAEMON] Force stopping daemon")
            os.kill(pid, signal.SIGKILL)
            
            # Clean up pid file
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            
            return True
            
        except OSError as e:
            print(f"[DAEMON] Failed to stop: {e}")
            return False
    
    def restart(self, use_watchdog: bool = True) -> bool:
        """Restart the daemon."""
        print("[DAEMON] Restarting...")
        if self.is_running():
            if not self.stop():
                return False
            
            # Wait a moment
            time.sleep(2)
        
        return self.start(use_watchdog=use_watchdog)
    
    def status(self) -> dict:
        """Get daemon status."""
        running = self.is_running()
        pid = self.get_pid() if running else None
        
        status_info = {
            'running': running,
            'pid': pid,
            'pid_file': self.pid_file,
            'log_file': self.log_file,
        }
        
        # If running, try to get watcher status
        if running and self.watcher:
            try:
                watcher_status = self.watcher.status()
                status_info.update(watcher_status)
            except Exception as e:
                status_info['watcher_error'] = str(e)
        
        return status_info
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        print(f"[DAEMON] Received signal {signum}")
        self.running = False
        
        if self.watcher:
            self.watcher.stop()
        
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup daemon resources."""
        if self.watcher:
            self.watcher.stop()
        
        if os.path.exists(self.pid_file):
            try:
                os.unlink(self.pid_file)
            except OSError:
                pass 