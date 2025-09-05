#!/usr/bin/env bash

# ConfWatch Installer for Users
# Downloads and installs ConfWatch from GitHub

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Configuration
CONFWATCH_HOME="$HOME/.confwatch"
VENV_DIR="$CONFWATCH_HOME/venv"
CONFIG_DIR="$CONFWATCH_HOME/config"
REPO_DIR="$CONFWATCH_HOME/repo"
WEB_DIR="$CONFWATCH_HOME/web"
TEMP_DIR="/tmp/confwatch-install"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "           ConfWatch Installer"
    echo "=================================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Progress indicator with limited log output
show_progress() {
    local message="$1"
    local command="$2"
    local start_time=$(date +%s)
    
    echo -ne "${YELLOW}ℹ $message${NC}"
    
    # Create temporary files for output
    local temp_log=$(mktemp)
    local temp_err=$(mktemp)
    
    # Run command in background and capture output
    if eval "$command" > "$temp_log" 2> "$temp_err"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "\r${GREEN}✓ $message (${duration}s)${NC}"
        
        # Show last 5 lines if there's output and it's substantial
        if [[ -s "$temp_log" ]] && [[ $(wc -l < "$temp_log") -gt 5 ]]; then
            echo -e "${GRAY}$(tail -n 5 "$temp_log")${NC}"
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "\r${RED}✗ $message (${duration}s)${NC}"
        
        # Show last 10 lines of error output
        if [[ -s "$temp_err" ]]; then
            echo -e "${RED}Error output:${NC}"
            echo -e "${GRAY}$(tail -n 10 "$temp_err")${NC}"
        fi
        
        # Clean up and exit
        rm -f "$temp_log" "$temp_err"
        return 1
    fi
    
    # Clean up temp files
    rm -f "$temp_log" "$temp_err"
    return 0
}

# Check if Python 3 is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Found Python 3: $(python3 --version)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        print_success "Found Python: $(python --version)"
    else
        print_error "Python 3 is required but not installed."
        print_info "Please install Python 3 and try again."
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_success "Found pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_success "Found pip"
    else
        print_info "pip not found, attempting to install..."
        
        # Try to install pip using different methods
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            print_info "Installing pip using apt-get..."
            show_progress "Updating package lists..." "apt-get update -qq"
            show_progress "Installing python3-pip and python3-venv..." "apt-get install -y python3-pip python3-venv"
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            print_info "Installing pip using yum..."
            show_progress "Installing python3-pip and python3-venv..." "yum install -y python3-pip python3-venv"
        elif command -v dnf &> /dev/null; then
            # Fedora
            print_info "Installing pip using dnf..."
            show_progress "Installing python3-pip and python3-venv..." "dnf install -y python3-pip python3-venv"
        elif command -v pacman &> /dev/null; then
            # Arch Linux
            print_info "Installing pip using pacman..."
            show_progress "Installing python-pip..." "pacman -S --noconfirm python-pip"
        elif command -v zypper &> /dev/null; then
            # openSUSE
            print_info "Installing pip using zypper..."
            show_progress "Installing python3-pip and python3-venv..." "zypper install -y python3-pip python3-venv"
        elif command -v apk &> /dev/null; then
            # Alpine Linux
            print_info "Installing pip using apk..."
            show_progress "Installing python3-dev, py3-pip and py3-virtualenv..." "apk add --no-cache python3-dev py3-pip py3-virtualenv"
        else
            # Try get-pip.py as fallback
            print_info "Trying to install pip using get-pip.py..."
            if command -v curl &> /dev/null; then
                curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3
            elif command -v wget &> /dev/null; then
                wget -qO- https://bootstrap.pypa.io/get-pip.py | python3
            else
                print_error "Could not install pip automatically."
                print_info "Please install pip manually and try again:"
                print_info "  Ubuntu/Debian: apt-get install python3-pip python3-venv"
                print_info "  CentOS/RHEL: yum install python3-pip python3-venv"
                print_info "  Fedora: dnf install python3-pip python3-venv"
                exit 1
            fi
        fi
        
        # Verify pip installation
        if command -v pip3 &> /dev/null; then
            PIP_CMD="pip3"
            print_success "Successfully installed pip3"
        elif command -v pip &> /dev/null; then
            PIP_CMD="pip"
            print_success "Successfully installed pip"
        else
            print_error "Failed to install pip."
            print_info "Please install pip manually and try again."
            exit 1
        fi
    fi
}

# Check if git is available
check_git() {
    if command -v git &> /dev/null; then
        print_success "Found git: $(git --version)"
    else
        print_info "git not found, attempting to install..."
        
        # Try to install git using different methods
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            print_info "Installing git using apt-get..."
            show_progress "Updating package lists..." "apt-get update -qq"
            show_progress "Installing git..." "apt-get install -y git"
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            print_info "Installing git using yum..."
            show_progress "Installing git..." "yum install -y git"
        elif command -v dnf &> /dev/null; then
            # Fedora
            print_info "Installing git using dnf..."
            show_progress "Installing git..." "dnf install -y git"
        elif command -v pacman &> /dev/null; then
            # Arch Linux
            print_info "Installing git using pacman..."
            show_progress "Installing git..." "pacman -S --noconfirm git"
        elif command -v zypper &> /dev/null; then
            # openSUSE
            print_info "Installing git using zypper..."
            show_progress "Installing git..." "zypper install -y git"
        elif command -v apk &> /dev/null; then
            # Alpine Linux
            print_info "Installing git using apk..."
            show_progress "Installing git..." "apk add --no-cache git"
        else
            print_error "Could not install git automatically."
            print_info "Please install git manually and try again:"
            print_info "  Ubuntu/Debian: apt-get install git"
            print_info "  CentOS/RHEL: yum install git"
            print_info "  Fedora: dnf install git"
            exit 1
        fi
        
        # Verify git installation
        if command -v git &> /dev/null; then
            print_success "Successfully installed git: $(git --version)"
        else
            print_error "Failed to install git."
            print_info "Please install git manually and try again."
            exit 1
        fi
    fi
}

# Download and extract project
download_project() {
    print_info "Downloading ConfWatch from GitHub..."
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    
    # Clone repository without authentication prompts
    if ! GIT_TERMINAL_PROMPT=0 git clone https://github.com/mrvi0/conf-watch.git "$TEMP_DIR" > /dev/null 2>&1; then
        # Try with curl/wget fallback if git clone fails
        print_info "Git clone failed, trying direct download..."
        if command -v curl &> /dev/null; then
            curl -fsSL https://github.com/mrvi0/conf-watch/archive/refs/heads/main.tar.gz | tar -xz -C "$TEMP_DIR" --strip-components=1
        elif command -v wget &> /dev/null; then
            wget -qO- https://github.com/mrvi0/conf-watch/archive/refs/heads/main.tar.gz | tar -xz -C "$TEMP_DIR" --strip-components=1
        else
            print_error "Failed to download ConfWatch from GitHub."
            print_info "Please check your internet connection and try again."
            print_info "Or install git, curl, or wget and try again."
            exit 1
        fi
    fi
    
    if [[ ! -d "$TEMP_DIR/confwatch" ]]; then
        print_error "Failed to download ConfWatch project"
        exit 1
    fi
    
    print_success "Project downloaded successfully"
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        print_info "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    show_progress "Creating virtual environment..." "$PYTHON_CMD -m venv \"$VENV_DIR\""
    print_success "Virtual environment created at $VENV_DIR"
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    show_progress "Upgrading pip..." "pip install --upgrade pip"
    
    # Install requirements
    show_progress "Installing Python dependencies..." "pip install -r \"$TEMP_DIR/requirements.txt\""
    
    print_success "Dependencies installed successfully"
}

# Create configuration
create_config() {
    print_info "Creating configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    # Copy default config from downloaded project
    cp "$TEMP_DIR/confwatch/default_config.yml" "$CONFIG_DIR/config.yml"
    print_success "Configuration created at $CONFIG_DIR/config.yml"
}

# Generate authentication password
generate_auth_password() {
    print_info "Generating authentication password..."
    
    # Activate virtual environment to use Python modules
    source "$VENV_DIR/bin/activate"
    export PYTHONPATH="$CONFWATCH_HOME/confwatch-module:$PYTHONPATH"
    
    # Generate password using Python
    PASSWORD=$(python3 -c "
import sys
import os

# Add the confwatch module to Python path
confwatch_module_path = '$CONFWATCH_HOME/confwatch-module'
if confwatch_module_path not in sys.path:
    sys.path.insert(0, confwatch_module_path)

try:
    from confwatch.core.auth import AuthManager
    
    auth = AuthManager('$CONFIG_DIR/config.yml')
    password = auth.generate_password()
    auth.save_password(password)
    print(password)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    exit(1)
")
    
    if [[ -n "$PASSWORD" ]]; then
        print_success "Authentication password generated"
        # Store password for later display
        WEB_PASSWORD="$PASSWORD"
    else
        print_error "Failed to generate authentication password"
        exit 1
    fi
}

# Initialize Git repository
init_repo() {
    print_info "Initializing Git repository..."
    
    mkdir -p "$REPO_DIR"
    cd "$REPO_DIR"
    
    if [[ ! -d ".git" ]]; then
        git init > /dev/null 2>&1
        git config user.name "ConfWatch"
        git config user.email "confwatch@localhost"
        print_success "Git repository initialized"
    else
        print_info "Git repository already exists"
    fi
}

# Create web directory and copy files
setup_web() {
    print_info "Setting up web interface..."
    
    mkdir -p "$WEB_DIR"
    
    # Copy web files from downloaded project
    if [[ -d "$TEMP_DIR/confwatch/web/static" ]] && [[ -f "$TEMP_DIR/confwatch/web/static/index.html" ]]; then
        print_info "Copying web files from project..."
        cp -r "$TEMP_DIR/confwatch/web/static"/* "$WEB_DIR/"
        print_success "Web files copied from project"
    else
        print_error "Project web files not found: $TEMP_DIR/confwatch/web/static/index.html"
        print_info "Please ensure the project contains web interface files"
        exit 1
    fi
    
    print_success "Web interface created"
}

# Copy Python module to runtime directory
copy_python_module() {
    print_info "Copying Python module..."
    mkdir -p "$CONFWATCH_HOME/confwatch-module"
    if [[ -d "$CONFWATCH_HOME/confwatch-module/confwatch" ]]; then
        rm -rf "$CONFWATCH_HOME/confwatch-module/confwatch"
    fi
    cp -r "$TEMP_DIR/confwatch" "$CONFWATCH_HOME/confwatch-module/"
    print_success "Python module copied to $CONFWATCH_HOME/confwatch-module/confwatch"
}

# Create launcher script
create_launcher() {
    print_info "Creating launcher script..."
    cat > "$CONFWATCH_HOME/confwatch" << EOF
#!/usr/bin/env bash

# ConfWatch Launcher
# Activates virtual environment and runs ConfWatch

CONFWATCH_HOME="$CONFWATCH_HOME"
VENV_DIR="$VENV_DIR"

# Activate virtual environment
source "\$VENV_DIR/bin/activate"

# Add runtime directory to Python path
export PYTHONPATH="$CONFWATCH_HOME/confwatch-module:\$PYTHONPATH"

# Run ConfWatch
python -m confwatch.cli.main "\$@"
EOF
    chmod +x "$CONFWATCH_HOME/confwatch"
    print_success "Launcher script created"
}

# Add to PATH
add_to_path() {
    print_info "Adding ConfWatch to PATH..."
    
    # Check if already in PATH
    if [[ ":$PATH:" == *":$CONFWATCH_HOME:"* ]]; then
        print_info "ConfWatch is already in PATH"
        return
    fi
    
    # Add to .bashrc
    if [[ -f "$HOME/.bashrc" ]]; then
        echo "" >> "$HOME/.bashrc"
        echo "# ConfWatch" >> "$HOME/.bashrc"
        echo "export PATH=\"$CONFWATCH_HOME:\$PATH\"" >> "$HOME/.bashrc"
        print_success "Added to .bashrc"
    fi
    
    # Add to .zshrc if exists
    if [[ -f "$HOME/.zshrc" ]]; then
        echo "" >> "$HOME/.zshrc"
        echo "# ConfWatch" >> "$HOME/.zshrc"
        echo "export PATH=\"$CONFWATCH_HOME:\$PATH\"" >> "$HOME/.zshrc"
        print_success "Added to .zshrc"
    fi
}

# Cleanup
cleanup() {
    print_info "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    print_success "Cleanup completed"
}

# Main installation
main() {
    print_header
    
    print_info "Installing ConfWatch..."
    print_info "Installation directory: $CONFWATCH_HOME"
    
    # Check prerequisites
    check_python
    check_pip
    check_git
    
    # Create directories
    mkdir -p "$CONFWATCH_HOME"
    
    # Install
    download_project
    create_venv
    install_dependencies
    create_config
    copy_python_module
    init_repo
    setup_web
    generate_auth_password
    create_launcher
    add_to_path
    cleanup
    
    print_success "Installation completed successfully!"
    echo ""
    echo -e "${GREEN}ConfWatch has been installed successfully!${NC}"
    echo -e "${YELLOW}Location:${NC} $CONFWATCH_HOME"
    echo -e "${YELLOW}Virtual Environment:${NC} $VENV_DIR"
    echo -e "${YELLOW}Configuration:${NC} $CONFIG_DIR/config.yml"
    echo -e "${YELLOW}Authentication:${NC} Web interface is protected with a unique password"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Restart your terminal or run: source ~/.bashrc"
    echo "2. Edit configuration: $CONFIG_DIR/config.yml"
    echo "3. Create first snapshot: confwatch snapshot"
    echo "4. Start web interface: confwatch web"
    echo "5. Use the generated password to access the web interface"
    echo ""
    echo -e "${YELLOW}To start using ConfWatch:${NC}"
    echo "confwatch --help"
    echo ""
    echo -e "${YELLOW}To reset web interface password:${NC}"
    echo "confwatch reset-password"
    echo ""
    echo -e "${GREEN}Web Interface Password:${NC} $WEB_PASSWORD"
    echo -e "${YELLOW}⚠  IMPORTANT: Save this password! It won't be shown again.${NC}"
}

# Run installation
main "$@" 