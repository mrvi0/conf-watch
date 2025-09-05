#!/usr/bin/env python3
"""
Emergency fix script for broken ConfWatch installation after update.
This script fixes the module path issue when update goes wrong.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def fix_confwatch_installation():
    """Fix broken ConfWatch installation."""
    print("🔧 ConfWatch Installation Fix")
    print("=" * 40)
    
    # Detect ConfWatch home
    confwatch_home = os.path.expanduser("~/.confwatch")
    if not os.path.exists(confwatch_home):
        print("❌ ConfWatch installation directory not found!")
        return False
    
    print(f"📁 Found ConfWatch at: {confwatch_home}")
    
    confwatch_module_dir = os.path.join(confwatch_home, "confwatch-module")
    confwatch_module_path = os.path.join(confwatch_module_dir, "confwatch")
    
    # Check if module is in wrong location
    if os.path.exists(confwatch_module_dir) and not os.path.exists(confwatch_module_path):
        print("🔍 Detected module structure issue...")
        
        # Look for confwatch module files directly in confwatch-module
        init_file = os.path.join(confwatch_module_dir, "__init__.py")
        if os.path.exists(init_file):
            print("✅ Found module files in wrong location, fixing...")
            
            # Create temporary backup
            temp_backup = confwatch_module_dir + ".temp"
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
            
            shutil.move(confwatch_module_dir, temp_backup)
            
            # Recreate proper structure
            os.makedirs(confwatch_module_dir, exist_ok=True)
            shutil.move(temp_backup, confwatch_module_path)
            
            print("✅ Fixed module structure")
        else:
            print("❌ Module files not found, need to re-download...")
            return download_and_fix(confwatch_home)
    
    elif not os.path.exists(confwatch_module_path):
        print("❌ ConfWatch module missing, re-downloading...")
        return download_and_fix(confwatch_home)
    
    else:
        print("✅ Module structure looks correct")
    
    # Test the installation
    print("🧪 Testing installation...")
    launcher = os.path.join(confwatch_home, "confwatch")
    
    if not os.path.exists(launcher):
        print("❌ Launcher script missing, recreating...")
        create_launcher(confwatch_home)
    
    # Test if it works
    try:
        result = subprocess.run([launcher, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Installation fixed successfully!")
            print(f"🎉 ConfWatch version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Still having issues: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing installation: {e}")
        return False

def download_and_fix(confwatch_home):
    """Download fresh ConfWatch and fix installation."""
    print("📥 Downloading fresh ConfWatch...")
    
    confwatch_module_dir = os.path.join(confwatch_home, "confwatch-module")
    confwatch_module_path = os.path.join(confwatch_module_dir, "confwatch")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Try to download using curl/wget
        archive_url = "https://github.com/mrvi0/conf-watch/archive/refs/heads/main.tar.gz"
        archive_path = os.path.join(temp_dir, "confwatch.tar.gz")
        
        # Try curl first
        result = subprocess.run([
            "curl", "-fsSL", "-o", archive_path, archive_url
        ], capture_output=True)
        
        if result.returncode != 0:
            # Try wget
            result = subprocess.run([
                "wget", "-q", "-O", archive_path, archive_url
            ], capture_output=True)
            
            if result.returncode != 0:
                print("❌ Could not download ConfWatch archive")
                return False
        
        print("✅ Downloaded ConfWatch archive")
        
        # Extract
        result = subprocess.run([
            "tar", "-xzf", archive_path, "-C", temp_dir
        ], capture_output=True)
        
        if result.returncode != 0:
            print("❌ Could not extract archive")
            return False
        
        print("✅ Extracted archive")
        
        # Find the extracted directory
        extracted_dir = None
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and item.startswith("conf-watch"):
                extracted_dir = item_path
                break
        
        if not extracted_dir:
            print("❌ Could not find extracted ConfWatch directory")
            return False
        
        # Copy module
        source_module = os.path.join(extracted_dir, "confwatch")
        if not os.path.exists(source_module):
            print("❌ ConfWatch module not found in archive")
            return False
        
        # Remove old module if exists
        if os.path.exists(confwatch_module_path):
            shutil.rmtree(confwatch_module_path)
        
        # Create confwatch-module directory
        os.makedirs(confwatch_module_dir, exist_ok=True)
        
        # Copy new module
        shutil.copytree(source_module, confwatch_module_path)
        print("✅ Copied fresh ConfWatch module")
        
        # Update launcher
        create_launcher(confwatch_home)
        
        return True

def create_launcher(confwatch_home):
    """Create/update launcher script."""
    launcher_content = f"""#!/usr/bin/env bash
# ConfWatch Launcher Script (Fixed)
CONFWATCH_HOME="{confwatch_home}"
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
    
    launcher_file = os.path.join(confwatch_home, "confwatch")
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    
    os.chmod(launcher_file, 0o755)
    print("✅ Created/updated launcher script")

if __name__ == "__main__":
    success = fix_confwatch_installation()
    sys.exit(0 if success else 1) 