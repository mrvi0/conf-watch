"""
ConfWatch updater module.
Handles automatic updates from GitHub using backup-reinstall-restore approach.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


class ConfWatchUpdater:
    """Handles ConfWatch updates using backup-reinstall-restore approach."""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.confwatch_home = os.path.dirname(os.path.dirname(config_file))
        self.config_dir = os.path.join(self.confwatch_home, "config")
        self.repo_dir = os.path.join(self.confwatch_home, "repo")
        self.web_dir = os.path.join(self.confwatch_home, "web")
        
        # Directories that contain user data and should be preserved
        self.user_data_dirs = [
            ("config", self.config_dir),
            ("repo", self.repo_dir),
            ("web", self.web_dir)  # Contains auth.yml
        ]
    
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
    
    def backup_user_data(self, backup_dir: str) -> bool:
        """Backup user data to temporary directory."""
        print("💾 Backing up user data...")
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for name, source_dir in self.user_data_dirs:
                if os.path.exists(source_dir):
                    target_dir = os.path.join(backup_dir, name)
                    print(f"  📁 Backing up {name}...")
                    shutil.copytree(source_dir, target_dir)
                    
                    # Count items for user info
                    if name == "repo" and os.path.exists(os.path.join(source_dir, ".git")):
                        try:
                            result = subprocess.run([
                                "git", "-C", source_dir, "log", "--oneline"
                            ], capture_output=True, text=True)
                            if result.returncode == 0:
                                snapshot_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                                print(f"    ✅ {snapshot_count} snapshots backed up")
                        except:
                            pass
                else:
                    print(f"  ⚠️  {name} directory not found, skipping...")
            
            print("✅ User data backed up successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to backup user data: {e}")
            return False
    
    def restore_user_data(self, backup_dir: str) -> bool:
        """Restore user data from temporary directory."""
        print("📥 Restoring user data...")
        
        try:
            for name, target_dir in self.user_data_dirs:
                source_dir = os.path.join(backup_dir, name)
                if os.path.exists(source_dir):
                    print(f"  📁 Restoring {name}...")
                    
                    # Remove existing directory if present
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    
                    # Copy back from backup
                    shutil.copytree(source_dir, target_dir)
                else:
                    print(f"  ⚠️  {name} backup not found, skipping...")
            
            print("✅ User data restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore user data: {e}")
            return False
    
    def run_fresh_installation(self, branch: str = "main") -> bool:
        """Run fresh installation script."""
        print("🔄 Running fresh installation...")
        
        # Remove existing installation (but user data is already backed up)
        if os.path.exists(self.confwatch_home):
            print("  🗑️  Removing old installation...")
            shutil.rmtree(self.confwatch_home)
        
        # Download and run install script
        install_script_url = f"https://raw.githubusercontent.com/mrvi0/conf-watch/{branch}/install.sh"
        
        try:
            # Download install script
            result = subprocess.run([
                "curl", "-fsSL", install_script_url
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                # Try wget as fallback
                result = subprocess.run([
                    "wget", "-q", "-O", "-", install_script_url
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print("❌ Could not download install script")
                    return False
            
            install_script = result.stdout
            
            # Run install script
            env = os.environ.copy()
            env['CONFWATCH_UPDATE_MODE'] = '1'  # Signal to install script that this is an update
            
            process = subprocess.Popen([
                "bash", "-c", install_script
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Show installation progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"  {output.strip()}")
            
            if process.returncode == 0:
                print("✅ Fresh installation completed")
                return True
            else:
                print("❌ Fresh installation failed")
                return False
                
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def restart_daemon(self):
        """Restart daemon if it was running."""
        try:
            from confwatch.daemon.daemon import DaemonManager
            daemon = DaemonManager(self.config_file, self.repo_dir)
            print("🔄 Restarting daemon...")
            if daemon.start():
                print("✅ Daemon restarted successfully")
            else:
                print("⚠️  Warning: Could not restart daemon")
        except Exception as e:
            print(f"⚠️  Warning: Could not restart daemon: {e}")
    
    def update(self, branch: str = "main", force: bool = False) -> bool:
        """Perform complete update process using backup-reinstall-restore."""
        print("ConfWatch Update")
        print("=" * 30)
        
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")
        
        if not force:
            print("This will update ConfWatch to the latest version from GitHub.")
            print("The update process will:")
            print("  1. Backup your user data (config, snapshots, auth)")
            print("  2. Remove current installation")
            print("  3. Install fresh version")
            print("  4. Restore your user data")
            print("  5. Restart daemon if it was running")
            print()
            print("✅ PRESERVED (will NOT be touched):")
            print("  • Your configuration files (~/.confwatch/config/)")
            print("  • All file history and snapshots (~/.confwatch/repo/)")
            print("  • Authentication settings (auth.yml)")
            print()
            
            # Show snapshot count if available
            if os.path.exists(self.repo_dir):
                try:
                    result = subprocess.run([
                        "git", "-C", self.repo_dir, "log", "--oneline"
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        snapshot_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                        print(f"✅ Found {snapshot_count} snapshots in history (will be preserved)")
                except:
                    print("✅ Configuration directory found: " + self.config_dir)
                    print("✅ Repository directory found: " + self.repo_dir)
            
            response = input("\nContinue with update? (y/N): ").strip().lower()
            if response != 'y':
                print("Update cancelled.")
                return False
        
        # Check daemon status
        daemon_was_running = self.check_daemon_status()
        
        # Create temporary backup directory
        with tempfile.TemporaryDirectory(prefix="confwatch-backup-") as backup_dir:
            try:
                # Step 1: Backup user data
                if not self.backup_user_data(backup_dir):
                    print("❌ Update failed: Could not backup user data")
                    return False
                
                # Step 2: Run fresh installation
                if not self.run_fresh_installation(branch):
                    print("❌ Update failed: Fresh installation failed")
                    print("⚠️  Your data is safe in backup, but update failed")
                    return False
                
                # Step 3: Restore user data
                if not self.restore_user_data(backup_dir):
                    print("❌ Update failed: Could not restore user data")
                    print("⚠️  Fresh installation completed but data restore failed")
                    return False
                
                # Step 4: Restart daemon if it was running
                if daemon_was_running:
                    self.restart_daemon()
                
                print("🎉 Update completed successfully!")
                
                # Show new version
                try:
                    new_version = self.get_current_version()
                    if new_version != "unknown":
                        print(f"✅ Updated to version: {new_version}")
                except:
                    pass
                
                print("You can now use the updated ConfWatch.")
                return True
                
            except Exception as e:
                print(f"❌ Update failed with error: {e}")
                print("⚠️  Your data is safe in temporary backup")
                return False 