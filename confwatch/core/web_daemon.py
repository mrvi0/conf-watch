"""
Web daemon manager for ConfWatch.
Manages persistent web server with custom configuration.
"""

import os
import sys
import signal
import time
import atexit
import argparse
from pathlib import Path
from typing import Optional


class WebDaemonManager:
    """Manages the ConfWatch web daemon process."""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        
        # Daemon state
        confwatch_home = os.path.dirname(os.path.dirname(config_file))
        self.pid_file = os.path.join(confwatch_home, "web_daemon.pid")
        self.log_file = os.path.join(confwatch_home, "web_daemon.log")
        self.config_file_path = os.path.join(confwatch_home, "web_daemon.conf")
        
        self.running = False
        self.web_process = None
    
    def is_running(self) -> bool:
        """Check if web daemon is already running."""
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
        """Get web daemon PID if running."""
        if not os.path.exists(self.pid_file):
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    
    def save_config(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """Save web daemon configuration."""
        config = {
            'host': host,
            'port': port,
            'debug': debug
        }
        
        config_content = f"""# ConfWatch Web Daemon Configuration
HOST={host}
PORT={port}
DEBUG={str(debug).lower()}
"""
        
        with open(self.config_file_path, 'w') as f:
            f.write(config_content)
        
        print(f"Configuration saved to: {self.config_file_path}")
    
    def load_config(self) -> dict:
        """Load web daemon configuration."""
        config = {
            'host': '0.0.0.0',
            'port': 8080,
            'debug': False
        }
        
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip().lower()
                                value = value.strip()
                                
                                if key == 'host':
                                    config['host'] = value
                                elif key == 'port':
                                    config['port'] = int(value)
                                elif key == 'debug':
                                    config['debug'] = value.lower() in ('true', '1', 'yes')
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        return config
    
    def start(self, background: bool = True, host: str = None, port: int = None, debug: bool = None) -> bool:
        """Start the web daemon."""
        if self.is_running():
            print(f"[WEB DAEMON] Already running (PID: {self.get_pid()})")
            return False
        
        # Load existing config or use provided values
        config = self.load_config()
        if host is not None:
            config['host'] = host
        if port is not None:
            config['port'] = port
        if debug is not None:
            config['debug'] = debug
        
        # Save updated config
        self.save_config(config['host'], config['port'], config['debug'])
        
        if background:
            return self._start_background(config)
        else:
            return self._start_foreground(config)
    
    def _start_foreground(self, config: dict) -> bool:
        """Start web daemon in foreground."""
        print(f"[WEB DAEMON] Starting ConfWatch web server in foreground...")
        print(f"[WEB DAEMON] Host: {config['host']}, Port: {config['port']}, Debug: {config['debug']}")
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Setup cleanup
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            # Start web server
            from confwatch.web.app import run_web_server
            self.running = True
            
            print(f"[WEB DAEMON] Started successfully (PID: {os.getpid()})")
            print(f"[WEB DAEMON] Web interface available at: http://{config['host']}:{config['port']}")
            
            run_web_server(
                host=config['host'],
                port=config['port'],
                debug=config['debug']
            )
            
            return True
            
        except Exception as e:
            print(f"[WEB DAEMON] Failed to start: {e}")
            self._cleanup()
            return False
    
    def _start_background(self, config: dict) -> bool:
        """Start web daemon in background."""
        print("[WEB DAEMON] Starting ConfWatch web server in background...")
        print(f"[WEB DAEMON] Host: {config['host']}, Port: {config['port']}, Debug: {config['debug']}")
        
        # Fork process
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                print(f"[WEB DAEMON] Started successfully (PID: {pid})")
                print(f"[WEB DAEMON] Web interface available at: http://{config['host']}:{config['port']}")
                print(f"[WEB DAEMON] Logs: {self.log_file}")
                return True
        except OSError as e:
            print(f"[WEB DAEMON] Failed to fork: {e}")
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
            
            # Start web server
            from confwatch.web.app import run_web_server
            self.running = True
            
            print(f"[WEB DAEMON] Background daemon started (PID: {os.getpid()})")
            print(f"[WEB DAEMON] Web interface available at: http://{config['host']}:{config['port']}")
            
            run_web_server(
                host=config['host'],
                port=config['port'],
                debug=config['debug']
            )
            
            return True
            
        except Exception as e:
            print(f"[WEB DAEMON] Failed to start background daemon: {e}")
            self._cleanup()
            sys.exit(1)
    
    def stop(self) -> bool:
        """Stop the web daemon."""
        if not self.is_running():
            print("[WEB DAEMON] Not running")
            return False
        
        pid = self.get_pid()
        if pid is None:
            print("[WEB DAEMON] Could not determine PID")
            return False
        
        try:
            print(f"[WEB DAEMON] Stopping web daemon (PID: {pid})")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):  # Wait up to 10 seconds
                if not self.is_running():
                    print("[WEB DAEMON] Stopped successfully")
                    return True
                time.sleep(1)
            
            # Force kill if still running
            print("[WEB DAEMON] Force stopping web daemon")
            os.kill(pid, signal.SIGKILL)
            
            # Clean up pid file
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            
            return True
            
        except OSError as e:
            print(f"[WEB DAEMON] Failed to stop: {e}")
            return False
    
    def restart(self, host: str = None, port: int = None, debug: bool = None) -> bool:
        """Restart the web daemon."""
        print("[WEB DAEMON] Restarting...")
        if self.is_running():
            if not self.stop():
                return False
            
            # Wait a moment
            time.sleep(2)
        
        return self.start(background=True, host=host, port=port, debug=debug)
    
    def status(self) -> dict:
        """Get web daemon status."""
        running = self.is_running()
        pid = self.get_pid() if running else None
        config = self.load_config()
        
        status_info = {
            'running': running,
            'pid': pid,
            'pid_file': self.pid_file,
            'log_file': self.log_file,
            'config_file': self.config_file_path,
            'host': config['host'],
            'port': config['port'],
            'debug': config['debug'],
        }
        
        return status_info
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        print(f"[WEB DAEMON] Received signal {signum}")
        self.running = False
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup daemon resources."""
        if os.path.exists(self.pid_file):
            try:
                os.unlink(self.pid_file)
            except OSError:
                pass 