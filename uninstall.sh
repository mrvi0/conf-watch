#!/usr/bin/env bash

# ConfWatch Python Uninstaller

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CONFWATCH_HOME="$HOME/.confwatch"

print_header() {
    echo -e "${YELLOW}"
    echo "=================================================="
    echo "           ConfWatch Uninstaller"
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

# Remove from PATH
remove_from_path() {
    print_info "Removing ConfWatch from PATH..."
    
    # Remove from .bashrc
    if [[ -f "$HOME/.bashrc" ]]; then
        if grep -q "ConfWatch" "$HOME/.bashrc"; then
            # Remove ConfWatch lines from .bashrc
            sed -i '/^# ConfWatch$/,/^export PATH.*confwatch/d' "$HOME/.bashrc"
            print_success "Removed from .bashrc"
        fi
    fi
    
    # Remove from .zshrc
    if [[ -f "$HOME/.zshrc" ]]; then
        if grep -q "ConfWatch" "$HOME/.zshrc"; then
            # Remove ConfWatch lines from .zshrc
            sed -i '/^# ConfWatch$/,/^export PATH.*confwatch/d' "$HOME/.zshrc"
            print_success "Removed from .zshrc"
        fi
    fi
}

# Main uninstallation
main() {
    print_header
    
    if [[ ! -d "$CONFWATCH_HOME" ]]; then
        print_info "ConfWatch is not installed."
        exit 0
    fi
    
    echo -e "${YELLOW}This will completely remove ConfWatch and all its data.${NC}"
    echo -e "${YELLOW}This action cannot be undone.${NC}"
    echo ""
    read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled."
        exit 0
    fi
    
    print_info "Removing ConfWatch..."
    
    # Remove from PATH
    remove_from_path
    
    # Remove ConfWatch directory
    if [[ -d "$CONFWATCH_HOME" ]]; then
        rm -rf "$CONFWATCH_HOME"
        print_success "Removed ConfWatch directory: $CONFWATCH_HOME"
    fi
    
    print_success "Uninstallation completed!"
    echo ""
    echo -e "${GREEN}ConfWatch has been completely removed.${NC}"
    echo ""
    echo -e "${YELLOW}To complete the cleanup:${NC}"
    echo "1. Restart your terminal or run: source ~/.bashrc"
    echo "2. If you want to reinstall, run: ./install.sh"
}

# Run uninstallation
main "$@" 