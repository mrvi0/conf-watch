"""
ConfWatch updater module.
Handles automatic updates from GitHub.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


class ConfWatchUpdater:
    """Handles ConfWatch updates."""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.confwatch_home = os.path.dirname(os.path.dirname(config_file))
        self.confwatch_module_dir = os.path.join(self.confwatch_home, "confwatch-module")
        self.web_dir = os.path.join(self.confwatch_home, "web")
        self.venv_dir = os.path.join(self.confwatch_home, "venv")
        self.launcher_file = os.path.join(self.confwatch_home, "confwatch")
        self.repo_dir = os.path.join(self.confwatch_home, "repo")
    
    def get_current_version(self) -> str:
        """Get current ConfWatch version."""
        try:
            import confwatch
            return confwatch.__version__
        except Exception:
            return "unknown"
    
    def check_daemon_status(self) -> bool:
        """Check if daemon is running and stop it if needed."""
        try:
            from confwatch.daemon.daemon import DaemonManager
            daemon = DaemonManager(self.config_file, self.repo_dir)
            if daemon.is_running():
                print("🔄 Stopping daemon...")
                daemon.stop()
                return True
            return False
        except Exception as e:
            print(f"Warning: Could not check daemon status: {e}")
            return False
    
    def restart_daemon(self):
        """Restart daemon if it was running."""
        try:
            from confwatch.daemon.daemon import DaemonManager
            daemon = DaemonManager(self.config_file, self.repo_dir)
            if daemon.start():
                print("✅ Daemon restarted successfully")
            else:
                print("⚠️  Warning: Could not restart daemon")
        except Exception as e:
            print(f"⚠️  Warning: Could not restart daemon: {e}")
    
    def download_update(self, temp_dir: str, branch: str = "main") -> bool:
        """Download latest version from GitHub."""
        download_url = f"https://github.com/mrvi0/conf-watch/archive/refs/heads/{branch}.tar.gz"
        archive_path = os.path.join(temp_dir, "update.tar.gz")
        
        if shutil.which("curl"):
            result = subprocess.run([
                "curl", "-fsSL", download_url, "-o", archive_path
            ], capture_output=True, text=True)
        elif shutil.which("wget"):
            result = subprocess.run([
                "wget", "-q", download_url, "-O", archive_path
            ], capture_output=True, text=True)
        else:
            print("❌ Error: curl or wget required for update")
            return False
        
        if result.returncode != 0:
            print(f"❌ Error downloading update: {result.stderr}")
            return False
        
        return True
    
    def extract_update(self, temp_dir: str) -> bool:
        """Extract downloaded archive."""
        archive_path = os.path.join(temp_dir, "update.tar.gz")
        
        result = subprocess.run([
            "tar", "-xzf", archive_path,
            "-C", temp_dir, "--strip-components=1"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error extracting update: {result.stderr}")
            return False
        
        return True
    
    def backup_current_installation(self) -> tuple:
        """Create backups of current installation."""
        # Backup Python module
        module_backup_dir = self.confwatch_module_dir + ".backup"
        if os.path.exists(module_backup_dir):
            shutil.rmtree(module_backup_dir)
        
        if os.path.exists(self.confwatch_module_dir):
            shutil.move(self.confwatch_module_dir, module_backup_dir)
        
        # Backup web files
        web_backup_dir = self.web_dir + ".backup"
        if os.path.exists(web_backup_dir):
            shutil.rmtree(web_backup_dir)
        
        if os.path.exists(self.web_dir):
            shutil.move(self.web_dir, web_backup_dir)
        
        return module_backup_dir, web_backup_dir
    
    def restore_backups(self, module_backup_dir: str, web_backup_dir: str):
        """Restore backups on update failure."""
        print("🔄 Restoring backup...")
        
        # Restore module
        if os.path.exists(module_backup_dir):
            if os.path.exists(self.confwatch_module_dir):
                shutil.rmtree(self.confwatch_module_dir)
            shutil.move(module_backup_dir, self.confwatch_module_dir)
        
        # Restore web files
        if os.path.exists(web_backup_dir):
            if os.path.exists(self.web_dir):
                shutil.rmtree(self.web_dir)
            shutil.move(web_backup_dir, self.web_dir)
    
    def update_python_module(self, temp_dir: str):
        """Update Python module."""
        new_module_dir = os.path.join(temp_dir, "confwatch")
        shutil.copytree(new_module_dir, self.confwatch_module_dir)
    
    def update_web_interface(self, temp_dir: str):
        """Update web interface files."""
        new_web_dir = os.path.join(temp_dir, "confwatch", "web", "static")
        
        if os.path.exists(new_web_dir):
            shutil.copytree(new_web_dir, self.web_dir)
    
    def update_dependencies(self, temp_dir: str):
        """Update Python dependencies."""
        requirements_file = os.path.join(temp_dir, "requirements.txt")
        if not os.path.exists(requirements_file):
            return
        
        pip_cmd = os.path.join(self.venv_dir, "bin", "pip")
        if not os.path.exists(pip_cmd):
            print("⚠️  Warning: pip not found in virtual environment")
            return
        
        result = subprocess.run([
            pip_cmd, "install", "--upgrade", "-r", requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  Warning: Could not update dependencies: {result.stderr}")
        else:
            print("✅ Dependencies updated successfully")
    
    def update_launcher(self):
        """Update launcher script."""
        new_launcher_content = f"""#!/usr/bin/env bash
# ConfWatch Launcher Script (Updated)
CONFWATCH_HOME="{self.confwatch_home}"
VENV_DIR="$CONFWATCH_HOME/venv"
export PYTHONPATH="$CONFWATCH_HOME/confwatch-module:$PYTHONPATH"

if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
    python -m confwatch.cli.main "$@"
else
    echo "Error: ConfWatch virtual environment not found at $VENV_DIR"
    exit 1
fi
"""
        
        with open(self.launcher_file, 'w') as f:
            f.write(new_launcher_content)
        
        os.chmod(self.launcher_file, 0o755)
    
    def get_new_version(self) -> str:
        """Get version of newly installed ConfWatch."""
        try:
            # Temporarily add new module to path
            sys.path.insert(0, self.confwatch_module_dir)
            import importlib
            import confwatch as new_confwatch
            importlib.reload(new_confwatch)
            return new_confwatch.__version__
        except Exception:
            return "unknown"
    
    def cleanup_backups(self, module_backup_dir: str, web_backup_dir: str):
        """Clean up backup directories after successful update."""
        if os.path.exists(module_backup_dir):
            shutil.rmtree(module_backup_dir)
        
        if os.path.exists(web_backup_dir):
            shutil.rmtree(web_backup_dir)
    
    def update(self, branch: str = "main", force: bool = False) -> bool:
        """Perform complete update process."""
        print("ConfWatch Update")
        print("=" * 30)
        
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")
        
        if not force:
            print("This will update ConfWatch to the latest version from GitHub.")
            print("The update process will:")
            print("  1. Download the latest version")
            print("  2. Stop any running daemon")
            print("  3. Update Python modules and dependencies")
            print("  4. Preserve your configuration and data")
            print("  5. Restart daemon if it was running")
            response = input("Continue with update? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Update cancelled.")
                return False
        
        # Stop daemon if running
        daemon_was_running = self.check_daemon_status()
        
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Download and extract
                print("📥 Downloading latest version from GitHub...")
                if not self.download_update(temp_dir, branch):
                    return False
                
                print("📦 Extracting update...")
                if not self.extract_update(temp_dir):
                    return False
                
                # Create backups
                module_backup_dir, web_backup_dir = self.backup_current_installation()
                
                # Update components
                print("🔄 Updating ConfWatch module...")
                self.update_python_module(temp_dir)
                
                print("🌐 Updating web interface...")
                self.update_web_interface(temp_dir)
                
                print("📚 Updating dependencies...")
                self.update_dependencies(temp_dir)
                
                print("🔧 Updating launcher...")
                self.update_launcher()
                
                # Check new version
                new_version = self.get_new_version()
                if new_version != "unknown":
                    print(f"✅ Updated to version: {new_version}")
                else:
                    print("✅ Update completed")
                
                # Restart daemon if it was running
                if daemon_was_running:
                    print("🔄 Restarting daemon...")
                    self.restart_daemon()
                
                # Clean up backups on success
                self.cleanup_backups(module_backup_dir, web_backup_dir)
                
                print("🎉 Update completed successfully!")
                print("You can now use the updated ConfWatch.")
                
                return True
                
            except Exception as e:
                print(f"❌ Error during update: {e}")
                
                # Restore backups on error
                self.restore_backups(module_backup_dir, web_backup_dir)
                
                print("❌ Update failed. Previous version restored.")
                return False 