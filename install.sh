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

# Выбор версии
while true; do
    echo "Which version do you want to install?"
    echo "  1) Bash (no dependencies, minimal features)"
    echo "  2) Python (full features, requires Python 3 + pip + Flask, PyYAML, etc)"
    read -p "Enter 1 or 2 [1]: " version_choice
    version_choice=${version_choice:-1}
    if [[ "$version_choice" == "1" ]]; then
        VERSION_TO_INSTALL="$BASH_VERSION"
        break
    elif [[ "$version_choice" == "2" ]]; then
        VERSION_TO_INSTALL="$PYTHON_VERSION"
        break
    else
        echo "Please enter 1 or 2."
    fi
done

if [[ "$VERSION_TO_INSTALL" == "$PYTHON_VERSION" ]]; then
    colors::warning "Python version requires system dependencies: python3, pip3, Flask, PyYAML, requests, cryptography, watchdog, gitpython."
    echo "If you are not sure, install the Bash version."
    if ! confirm "Continue with Python version installation?"; then
        echo "Installation cancelled."
        exit 0
    fi
    # Проверка наличия python3 и pip3
    if ! command -v python3 &> /dev/null; then
        colors::error "Python3 not found! Aborting."
        exit 1
    fi
    if ! command -v pip3 &> /dev/null; then
        colors::error "pip3 not found! Aborting."
        exit 1
    fi
    # Копирование Python файлов
    mkdir -p "$CONFWATCH_HOME"
    cp -r python/confwatch "$CONFWATCH_HOME/"
    cp python/requirements.txt "$CONFWATCH_HOME/"
    mkdir -p "$CONFWATCH_HOME/web"
    cp bash/web/webserver.sh "$CONFWATCH_HOME/web/"
    cp bash/web/index.html "$CONFWATCH_HOME/web/"
    # Создание исполняемого файла
    cat > "$CONFWATCH_HOME/confwatch" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'confwatch'))
from cli.main import main
if __name__ == "__main__":
    main()
EOF
    chmod +x "$CONFWATCH_HOME/confwatch"
    # Создание web server entry point
    cat > "$CONFWATCH_HOME/confwatch-web" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'confwatch'))
from cli.web import main
if __name__ == "__main__":
    main()
EOF
    chmod +x "$CONFWATCH_HOME/confwatch-web"
    colors::success "Python version installed!"
else
    # Bash версия
    mkdir -p "$CONFWATCH_HOME"
    cp bash/confwatch "$CONFWATCH_HOME/"
    cp bash/confwatchd "$CONFWATCH_HOME/"
    mkdir -p "$CONFWATCH_HOME/web"
    cp bash/web/webserver.sh "$CONFWATCH_HOME/web/"
    cp bash/web/index.html "$CONFWATCH_HOME/web/"
    chmod +x "$CONFWATCH_HOME/confwatch"
    chmod +x "$CONFWATCH_HOME/confwatchd"
    colors::success "Bash version installed!"
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
sed -i '/confwatch/d' "$HOME/.bashrc" 2>/dev/null
sed -i '/confwatchd/d' "$HOME/.bashrc" 2>/dev/null

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