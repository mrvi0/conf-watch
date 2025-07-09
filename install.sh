#!/usr/bin/env bash

# ConfWatch Installer
# Uses bash-lib for colored output, logging, and validation

# Load bash-lib library
source <(curl -fsSL https://raw.githubusercontent.com/mrvi0/bash-lib/main/bash-lib-standalone.sh)

# Configuration
CONFWATCH_HOME="$HOME/.confwatch"
PYTHON_VERSION="python"
BASH_VERSION="bash"

print_header "ConfWatch Installer"

# Check if already installed
if [[ -d "$CONFWATCH_HOME" ]]; then
    colors::warning "ConfWatch already installed in $CONFWATCH_HOME"
    if confirm "Do you want to reinstall?"; then
        rm -rf "$CONFWATCH_HOME"
        colors::info "Removed existing installation"
    else
        colors::info "Installation cancelled"
        exit 0
    fi
fi

# Create installation directory
mkdir -p "$CONFWATCH_HOME"
logging::info "Created installation directory: $CONFWATCH_HOME"

# Check Python availability
if command -v python3 &> /dev/null; then
    PYTHON_VERSION_NUM=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    colors::success "Python $PYTHON_VERSION_NUM found"
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        colors::success "pip3 found"
        VERSION_TO_INSTALL="$PYTHON_VERSION"
    else
        colors::warning "pip3 not found, falling back to bash version"
        VERSION_TO_INSTALL="$BASH_VERSION"
    fi
else
    colors::warning "Python3 not found, installing bash version"
    VERSION_TO_INSTALL="$BASH_VERSION"
fi

# Install selected version
if [[ "$VERSION_TO_INSTALL" == "$PYTHON_VERSION" ]]; then
    colors::info "Installing Python version..."
    
    # Install Python dependencies
    pip3 install flask pyyaml requests cryptography
    
    # Copy Python files
    cp -r python/confwatch "$CONFWATCH_HOME/"
    cp python/requirements.txt "$CONFWATCH_HOME/"
    
    # Create Python entry point
    cat > "$CONFWATCH_HOME/confwatch" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from confwatch.cli.main import main
if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$CONFWATCH_HOME/confwatch"
    colors::success "Python version installed successfully!"
    
else
    colors::info "Installing Bash version..."
    
    # Copy bash files
    cp bash/confwatch "$CONFWATCH_HOME/"
    cp bash/confwatchd "$CONFWATCH_HOME/"
    cp -r bash/web "$CONFWATCH_HOME/"
    
    chmod +x "$CONFWATCH_HOME/confwatch"
    chmod +x "$CONFWATCH_HOME/confwatchd"
    
    colors::success "Bash version installed successfully!"
fi

# Create configuration directory
mkdir -p "$CONFWATCH_HOME/config"
logging::info "Created config directory"

# Create default configuration
cat > "$CONFWATCH_HOME/config/config.yml" << 'EOF'
# ConfWatch Configuration

# Files to monitor
watch:
  - ~/.bashrc
  - ~/.zshrc
  - ~/.config/nvim/init.vim
  - /etc/nginx/nginx.conf
  - ~/projects/.env

# Storage settings
storage:
  type: "git"  # or "sqlite"
  path: "~/.confwatch/repo"

# Notification settings
notifications:
  telegram:
    enabled: false
    bot_token: ""
    chat_id: ""
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: ""
    password: ""

# Monitoring settings
monitoring:
  interval: 300  # seconds
  auto_test:
    nginx: "nginx -t"
    apache: "apache2ctl configtest"
EOF

colors::success "Default configuration created"

# Initialize git repository for version storage
mkdir -p "$CONFWATCH_HOME/repo"
cd "$CONFWATCH_HOME/repo"
git init --quiet
git config user.name "ConfWatch"
git config user.email "confwatch@localhost"
colors::success "Git repository initialized"

# Add to PATH
if [[ ":$PATH:" != *":$CONFWATCH_HOME:"* ]]; then
    echo "export PATH=\"$CONFWATCH_HOME:\$PATH\"" >> "$HOME/.bashrc"
    colors::success "Added to PATH in .bashrc"
fi

# Create aliases
echo "alias confwatch='$CONFWATCH_HOME/confwatch'" >> "$HOME/.bashrc"
echo "alias confwatchd='$CONFWATCH_HOME/confwatchd'" >> "$HOME/.bashrc"

# Final success message
print_header "Installation Complete!"
colors::success "ConfWatch has been installed successfully!"
colors::info "Version: $VERSION_TO_INSTALL"
colors::info "Location: $CONFWATCH_HOME"
colors::info "Configuration: $CONFWATCH_HOME/config/config.yml"

echo ""
colors::info "Next steps:"
echo "1. Edit configuration: $CONFWATCH_HOME/config/config.yml"
echo "2. Create first snapshot: confwatch snapshot"
echo "3. View differences: confwatch diff ~/.bashrc"
echo "4. Start monitoring: confwatchd"

echo ""
colors::info "To start using ConfWatch, run:"
echo "source ~/.bashrc"
echo "confwatch --help"

logging::info "Installation completed successfully" 