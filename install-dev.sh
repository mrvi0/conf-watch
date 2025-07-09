#!/usr/bin/env bash

# ConfWatch Python Installer
# Installs ConfWatch with virtual environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFWATCH_HOME="$HOME/.confwatch"
VENV_DIR="$CONFWATCH_HOME/venv"
CONFIG_DIR="$CONFWATCH_HOME/config"
REPO_DIR="$CONFWATCH_HOME/repo"
WEB_DIR="$CONFWATCH_HOME/web"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "           ConfWatch Python Installer"
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
        print_error "pip is required but not installed."
        print_info "Please install pip and try again."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        print_info "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Create configuration
create_config() {
    print_info "Creating configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    # Copy default config from project
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp "$PROJECT_DIR/confwatch/default_config.yml" "$CONFIG_DIR/config.yml"
    print_success "Configuration created at $CONFIG_DIR/config.yml"
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

    # Определяем корень проекта (используем текущую рабочую директорию)
    PROJECT_DIR="$(pwd)"
    print_info "Project directory: $PROJECT_DIR"
    print_info "Looking for: $PROJECT_DIR/confwatch/web/static/index.html"
    
    # Отладочная информация
    print_info "Checking if directory exists: $PROJECT_DIR/confwatch/web/static"
    if [[ -d "$PROJECT_DIR/confwatch/web/static" ]]; then
        print_info "✓ Directory exists"
        ls -la "$PROJECT_DIR/confwatch/web/static/"
    else
        print_info "✗ Directory does not exist"
    fi
    
    print_info "Checking if file exists: $PROJECT_DIR/confwatch/web/static/index.html"
    if [[ -f "$PROJECT_DIR/confwatch/web/static/index.html" ]]; then
        print_info "✓ File exists"
    else
        print_info "✗ File does not exist"
    fi

    if [[ -d "$PROJECT_DIR/confwatch/web/static" ]] && [[ -f "$PROJECT_DIR/confwatch/web/static/index.html" ]]; then
        print_info "Copying web files from project..."
        cp -r "$PROJECT_DIR/confwatch/web/static"/* "$WEB_DIR/"
        print_success "Web files copied from project"
    else
        print_error "Project web files not found: $PROJECT_DIR/confwatch/web/static/index.html"
        print_info "Please ensure the project contains web interface files"
        exit 1
    fi

    print_success "Web interface created"
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

# Copy Python module to runtime directory
copy_python_module() {
    print_info "Copying Python module..."
    
    # Ensure target directory exists
    mkdir -p "$CONFWATCH_HOME/confwatch-module"
    # Remove existing module if exists
    if [[ -d "$CONFWATCH_HOME/confwatch-module/confwatch" ]]; then
        rm -rf "$CONFWATCH_HOME/confwatch-module/confwatch"
    fi
    
    # Copy Python module (копируем саму папку confwatch внутрь confwatch-module)
    cp -r "$PROJECT_DIR/confwatch" "$CONFWATCH_HOME/confwatch-module/"
    print_success "Python module copied to $CONFWATCH_HOME/confwatch-module/confwatch"
}

# Main installation
main() {
    print_header
    
    print_info "Installing ConfWatch Python version..."
    print_info "Installation directory: $CONFWATCH_HOME"
    
    # Check prerequisites
    check_python
    check_pip
    
    # Create directories
    mkdir -p "$CONFWATCH_HOME"
    
    # Install
    create_venv
    install_dependencies
    create_config
    init_repo
    cd "$PROJECT_DIR"
    setup_web
    create_launcher
    copy_python_module
    add_to_path
    
    print_success "Installation completed successfully!"
    echo ""
    echo -e "${GREEN}ConfWatch has been installed successfully!${NC}"
    echo -e "${YELLOW}Location:${NC} $CONFWATCH_HOME"
    echo -e "${YELLOW}Virtual Environment:${NC} $VENV_DIR"
    echo -e "${YELLOW}Configuration:${NC} $CONFIG_DIR/config.yml"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Restart your terminal or run: source ~/.bashrc"
    echo "2. Edit configuration: $CONFIG_DIR/config.yml"
    echo "3. Create first snapshot: confwatch snapshot"
    echo "4. Start web interface: confwatch web"
    echo ""
    echo -e "${YELLOW}To start using ConfWatch:${NC}"
    echo "confwatch --help"
}

# Run installation
main "$@" 